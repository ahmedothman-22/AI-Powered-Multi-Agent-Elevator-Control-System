"""
Elevator Dispatch System - A* Edition v8.0
===========================================
    Initial State : (current_floor, frozenset(all_requested_floors))
    Actions : move to any floor in the unvisited set
    Transition : (floor, remaining) -> (next_floor, remaining - {next_floor})
    Step Cost : |current_floor - next_floor| (floors travelled)
    Goal Test : remaining == ∅
    Path Cost : total floors travelled to serve all requests
Optimal search : A* with admissible heuristic h(n) = span + nearest_extreme
"""
import tkinter as tk
import time, heapq, itertools, random
from collections import deque

# ╔══════════════════════════════════════════════════════════╗
# ║ SEARCH FORMULATION ║
# ╚══════════════════════════════════════════════════════════╝
class ElevatorProblem:
    """
    Problem formulation for a single elevator car.
    State
    -----
    A 2-tuple (current_floor : int, unvisited : frozenset[int])
    representing where the car is and which requested floors
    have not yet been visited.
    Initial State
    -------------
    Set at construction time from the car's current position
    and the full set of pending requests.
    Actions
    -------
    For each floor f in unvisited, the car may move directly to f.
    (We model non-stop movement; intermediate floors are not modelled
    as separate actions because the cost function captures distance.)
    Transition Model
    ----------------
    RESULT( (cur, unvisited), f ) = (f, unvisited - {f})
    Step Cost
    ---------
    |cur - f| (number of floors traversed)
    Goal Test
    ---------
    unvisited == ∅
    Heuristic h(n) — admissible & consistent
    -------------------------------------------
    Lower-bound on remaining travel:
        span = max(unvisited) - min(unvisited)
        nearest_edge = min( |cur - min|, |cur - max| )
        h = span + nearest_edge
    Proof of admissibility: the car must cover the full span of
    outstanding floors at least once, and must first travel to
    the nearer extreme — so h never over-estimates true cost.
    """
    def __init__(self, initial_floor: int, requested: set):
        self.initial_state = (initial_floor, frozenset(requested))
    def is_goal(self, state: tuple) -> bool:
        _, unvisited = state
        return len(unvisited) == 0
    def successors(self, state: tuple):
        cur, unvisited = state
        result = []
        for nf in unvisited:
            new_state = (nf, frozenset(f for f in unvisited if f != nf))
            step_cost = abs(cur - nf)
            result.append((new_state, step_cost))
        return result
    def h(self, state: tuple) -> float:
        cur, unvisited = state
        if not unvisited:
            return 0.0
        lo, hi = min(unvisited), max(unvisited)
        span = hi - lo
        nearest = min(abs(cur - lo), abs(cur - hi))
        return float(span + nearest)

# ╔══════════════════════════════════════════════════════════╗
# ║ A* SEARCH ║
# ╚══════════════════════════════════════════════════════════╝
def astar(problem: ElevatorProblem):
    """A* Tree Search with duplicate-state pruning via a reached table."""
    start = problem.initial_state
    if problem.is_goal(start):
        return [], 0.0
    tie = itertools.count()
    reached = {start: 0.0}
    frontier = []
    heapq.heappush(frontier, (problem.h(start), next(tie), 0.0, start, []))
    while frontier:
        _, _, g, state, path = heapq.heappop(frontier)
        if g > reached.get(state, float('inf')):
            continue
        if problem.is_goal(state):
            return path, g
        for child, cost in problem.successors(state):
            new_g = g + cost
            if new_g < reached.get(child, float('inf')):
                reached[child] = new_g
                new_f = new_g + problem.h(child)
                heapq.heappush(frontier, (new_f, next(tie), new_g, child, path + [child[0]]))
    return [], float('inf')

# ╔══════════════════════════════════════════════════════════╗
# ║ ELEVATOR CAR ║
# ╚══════════════════════════════════════════════════════════╝
class Elevator:
    FH = 48
    BASE_Y = 530
    SPEED = 4
    MAX_PENDING = 8
    def __init__(self, cid: int, canvas: tk.Canvas, x: int):
        self.cid = cid
        self.canvas = canvas
        self.x = x
        self.floor = 0
        self.disp_floor = 0
        self.py = float(self.BASE_Y)
        self.pending = set()
        self.path = []
        self.path_cost = 0.0
        self.dist = 0.0
        self.served = 0
        self._cache = None
        colors = [("#1e88e5", "#64b5f6"), ("#43a047", "#81c784"), ("#8e24aa", "#ba68c8")]
        self.body_c, self.accent = colors[(cid-1) % 3]
        self.body = canvas.create_rectangle(x, self.BASE_Y, x+54, self.BASE_Y+54,
                                           fill=self.body_c, outline=self.accent, width=3)
        self.label = canvas.create_text(x+27, self.BASE_Y+27, text=str(cid),
                                       fill="white", font=("Arial", 16, "bold"))
        self.floor_label = canvas.create_text(x+27, self.BASE_Y-12, text="0",
                                             fill="white", font=("Arial", 10, "bold"))
        self.arrow = canvas.create_text(x+27, self.BASE_Y+68, text="·",
                                       fill=self.accent, font=("Arial", 14, "bold"))
        self.path_line = canvas.create_line(x+27, self.BASE_Y+27, x+27, self.BASE_Y+27,
                                           fill="#ff5252", dash=(4, 2), width=2)
    def _fy(self, f):
        return self.BASE_Y - f * self.FH
    def add(self, floor: int):
        if len(self.pending) >= self.MAX_PENDING:
            return False
        if floor in self.pending:
            return True
        self.pending.add(floor)
        self._replan()
        return True
    def _replan(self):
        if not self.pending:
            self.path = []
            self.path_cost = 0.0
            self._cache = None
            return
        key = (self.floor, frozenset(self.pending))
        if key == self._cache:
            return
        self.path, self.path_cost = astar(ElevatorProblem(self.floor, self.pending))
        self._cache = key
    def load(self):
        return len(self.pending)
    def step(self):
        if not self.path:
            cx = self.x + 27
            self.canvas.coords(self.path_line, cx, self.py+27, cx, self.py+27)
            self.canvas.itemconfig(self.arrow, text="·")
            return False
        tgt = self.path[0]
        tgt_py = self._fy(tgt)
        delta = tgt_py - self.py
        if abs(delta) > 3:
            move = 4 if delta > 0 else -4
            self.py += move
            self.dist += abs(move) / self.FH
            self.disp_floor = int(round((self.BASE_Y - self.py) / self.FH))
            self._update_graphics(tgt_py)
        else:
            self.py = tgt_py
            self.floor = self.disp_floor = tgt
            self.path.pop(0)
            self.pending.discard(tgt)
            self.served += 1
            self._cache = None
            self._update_graphics(None)
            self.canvas.itemconfig(self.body, fill="#facc15")
            self.canvas.after(280, lambda: self.canvas.itemconfig(self.body, fill=self.body_c))
        return True
    def _update_graphics(self, tgt_py):
        cx = self.x + 27
        self.canvas.coords(self.body, self.x, self.py, self.x+54, self.py+54)
        self.canvas.coords(self.label, cx, self.py + 27)
        self.canvas.coords(self.floor_label, cx, self.py - 12)
        self.canvas.itemconfig(self.floor_label, text=str(self.disp_floor))
        if tgt_py is not None:
            self.canvas.coords(self.path_line, cx, self.py+27, cx, tgt_py+27)
        else:
            self.canvas.coords(self.path_line, cx, self.py+27, cx, self.py+27)
        arrow = "▲" if self.path and self.path[0] > self.disp_floor else "▼" if self.path else "·"
        self.canvas.itemconfig(self.arrow, text=arrow)
    def reset(self):
        self.pending.clear()
        self.path.clear()
        self.floor = self.disp_floor = 0
        self.py = float(self.BASE_Y)
        self.dist = self.served = 0.0
        self._cache = None
        self._update_graphics(None)

# ╔══════════════════════════════════════════════════════════╗
# ║ MAIN APPLICATION ║
# ╚══════════════════════════════════════════════════════════╝
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Elevator System v8.0")
        self.root.configure(bg="#0a0e1a")
        self.root.resizable(True, True)
        self.root.state('zoomed')
        self.queue = deque()
        self.heat = {i: 0 for i in range(11)}
        self.start_time = time.time()
        self.canvas = tk.Canvas(root, bg="#0a0e1a", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self._draw_building()
        self.cars = [Elevator(i+1, self.canvas, 140 + i * 170) for i in range(3)]
        self._create_sidebar()
        self._loop()
    def _draw_building(self):
        for i in range(11):
            y = 530 - i * 48
            self.canvas.create_line(90, y, 620, y, fill="#1e2a44", width=2)
            self.canvas.create_text(55, y, text=f"L{i}", fill="#8899bb", font=("Arial", 11, "bold"))
    def _create_sidebar(self):
        container = tk.Frame(self.root, bg="#111827", width=250)
        container.pack(side=tk.RIGHT, fill=tk.Y)
        canvas = tk.Canvas(container, bg="#111827", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#111827")
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        tk.Label(scroll_frame, text="AI ELEVATOR v8.0", fg="#60a5fa", bg="#111827",
                 font=("Arial", 16, "bold")).pack(pady=(0,15))
        self.stats_var = tk.StringVar()
        tk.Label(scroll_frame, textvariable=self.stats_var, fg="#34d399", bg="#1f2937",
                 font=("Courier", 9), justify="left", padx=12, pady=12).pack(fill=tk.X)
        tk.Label(scroll_frame, text="FLOOR HEATMAP", fg="#f472b6", bg="#111827",
                 font=("Arial", 10, "bold")).pack(pady=(25,8))
        self.heat_var = tk.StringVar()
        tk.Label(scroll_frame, textvariable=self.heat_var, fg="#67e8f9", bg="#1f2937",
                 font=("Courier", 9), justify="left").pack(fill=tk.X, pady=5)
        tk.Button(scroll_frame, text="Random Traffic", bg="#1e40af", fg="white",
                  command=self.random_calls).pack(fill=tk.X, pady=8)
        tk.Button(scroll_frame, text="Emergency Stop", bg="#b91c1c", fg="white",
                  command=self.emergency).pack(fill=tk.X, pady=5)
        tk.Button(scroll_frame, text="Full Reset", bg="#374151", fg="white",
                  command=self.full_reset).pack(fill=tk.X)
        tk.Label(scroll_frame, text="Call From Floor", fg="#94a3b8", bg="#111827",
                 font=("Arial", 10, "bold")).pack(pady=(30,10))
        for f in range(10, -1, -1):
            tk.Button(scroll_frame, text=f"Floor {f}", bg="#1e2937", fg="#cbd5e1",
                      command=lambda fl=f: self.call_floor(fl)).pack(pady=3, fill=tk.X)
    def call_floor(self, floor):
        if any(floor in c.pending for c in self.cars) or any(r['floor'] == floor for r in self.queue):
            return
        self.heat[floor] += 1
        self.queue.append({'floor': floor, 'time': time.time()})
    def random_calls(self):
        for _ in range(random.randint(4, 9)):
            self.call_floor(random.randint(0, 10))
    def emergency(self):
        for c in self.cars:
            c.pending.clear()
            c.path.clear()
        self.queue.clear()
    def full_reset(self):
        for c in self.cars:
            c.reset()
        self.queue.clear()
        self.heat = {i: 0 for i in range(11)}
        self.start_time = time.time()
    def _dispatch(self):
        if not self.queue:
            return
        req = self.queue[0]
        floor = req['floor']
        wait = time.time() - req['time']
        best_car = None
        best_cost = float('inf')
        for car in self.cars:
            if car.load() >= Elevator.MAX_PENDING:
                continue
            hypo = car.pending | {floor}
            _, cost = astar(ElevatorProblem(car.floor, hypo))
            marginal = cost - car.path_cost + (car.load() * 2.5) - min(wait * 1.3, 14)
            if marginal < best_cost:
                best_cost = marginal
                best_car = car
        if best_car:
            best_car.add(floor)
            self.queue.popleft()
    def _loop(self):
        for car in self.cars:
            car.step()
        if self.queue:
            self._dispatch()
        self._update_ui()
        self.root.after(40, self._loop)
    def _update_ui(self):
        served = sum(c.served for c in self.cars)
        dist = sum(c.dist for c in self.cars)
        eff = f"{served / dist:.2f}" if dist > 0 else "—"
        uptime = int(time.time() - self.start_time)
        stats = (f"Uptime : {uptime}s\n"
                 f"Served : {served}\n"
                 f"Distance : {dist:.1f} floors\n"
                 f"Efficiency : {eff} req/floor\n"
                 f"Queue : {len(self.queue)}")
        self.stats_var.set(stats)
        mx = max(self.heat.values()) or 1
        heat_text = ""
        for f in range(10, -1, -1):
            v = self.heat.get(f, 0)
            if v > 0:
                bar = "█" * int(v / mx * 14)
                heat_text += f"L{f:2d} {bar} {v}\n"
        self.heat_var.set(heat_text if heat_text else "No calls yet")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
