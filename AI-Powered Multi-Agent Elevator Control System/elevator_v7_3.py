import tkinter as tk
import time
from collections import deque

class Elevator:
    def __init__(self, id, canvas, x_pos):
        self.id = id
        self.logical_floor = 0      
        self.display_floor = 0     
        self.pixel_y = 450.0
        self.direction = 0         
        self.up_stops = []
        self.down_stops = []
        self.total_dist = 0.0
        self.served_count = 0
        self.capacity = 8

        self.canvas = canvas
        self.rect = canvas.create_rectangle(x_pos, 450, x_pos+50, 500, fill="#34495e", outline="#ecf0f1", width=2)
        self.text = canvas.create_text(x_pos+25, 475, text=f"E{id}", fill="white", font=("Arial", 10, "bold"))
        self.status_ui = canvas.create_text(x_pos+25, 515, text="IDLE", fill="#2ecc71", font=("Arial", 8))
        self.path_line = canvas.create_line(x_pos+25, 450, x_pos+25, 450, fill="#e94560", dash=(4, 2))

    def get_load(self):
        return len(self.up_stops) + len(self.down_stops)

    def has_destination(self, floor):
        return floor in self.up_stops or floor in self.down_stops

    def estimated_travel_distance(self, new_floor):
        """Heuristic"""
        if self.get_load() == 0:
            return abs(self.logical_floor - new_floor)

        if self.direction == 1:  
            if new_floor >= self.logical_floor:
                return new_floor - self.logical_floor
            farthest = max(self.up_stops) if self.up_stops else self.logical_floor
            return (farthest - self.logical_floor) + (farthest - new_floor)
        
        elif self.direction == -1: 
            if new_floor <= self.logical_floor:
                return self.logical_floor - new_floor
            farthest = min(self.down_stops) if self.down_stops else self.logical_floor
            return (self.logical_floor - farthest) + (new_floor - farthest)
        
        return abs(self.logical_floor - new_floor)

    def add_destination(self, floor):
        if floor == self.logical_floor:
            if self.direction == 0:
                self.served_count += 1
                self.canvas.itemconfig(self.rect, fill="#2ecc71")
                self.canvas.after(280, lambda: self.canvas.itemconfig(self.rect, fill="#34495e"))
            return True

        if self.has_destination(floor): return True

        added = False
        if floor > self.logical_floor:
            if floor not in self.up_stops:
                self.up_stops.append(floor)
                self.up_stops.sort()
                added = True
        elif floor < self.logical_floor:
            if floor not in self.down_stops:
                self.down_stops.append(floor)
                self.down_stops.sort(reverse=True)
                added = True

        if self.direction == 0 and added:
            self.direction = 1 if self.up_stops else -1
        return added

    def step(self):
        # LOOK Algorithm State Machine
        if self.direction == 1 and not self.up_stops:
            self.direction = -1 if self.down_stops else 0
        elif self.direction == -1 and not self.down_stops:
            self.direction = 1 if self.up_stops else 0
        elif self.direction == 0:
            if self.up_stops: self.direction = 1
            elif self.down_stops: self.direction = -1

        target = self.up_stops[0] if self.direction == 1 else (self.down_stops[0] if self.direction == -1 else None)
        
        arrival = False
        if target is not None:
            target_y = 450 - (target * 45)
            if abs(self.pixel_y - target_y) > 2:
                move = -4 if self.direction == 1 else 4
                self.pixel_y += move
                self.total_dist += abs(move) / 45
                self.canvas.move(self.rect, 0, move)
                self.canvas.move(self.text, 0, move)
                self.display_floor = int(round((450 - self.pixel_y) / 45))
                # تحديث خط المسار
                tx = self.canvas.coords(self.text)[0]
                self.canvas.coords(self.path_line, tx, self.pixel_y + 25, tx, target_y + 25)
            else:
                self.pixel_y = target_y
                self.logical_floor = target
                self.display_floor = target
                if self.direction == 1: self.up_stops.pop(0)
                else: self.down_stops.pop(0)
                self.served_count += 1
                arrival = True
                self.canvas.itemconfig(self.rect, fill="#2ecc71")
                self.canvas.after(280, lambda: self.canvas.itemconfig(self.rect, fill="#34495e"))
        else:
            self.canvas.coords(self.path_line, 0, 0, 0, 0)

        self.update_ui()
        return arrival

    def update_ui(self):
        icon = "IDLE" if self.direction == 0 else ("↑" if self.direction == 1 else "↓")
        color = "#2ecc71" if self.direction == 0 else "#f1c40f"
        load = self.get_load()
        self.canvas.itemconfig(self.status_ui, text=f"L{self.display_floor} {icon} [{load}]", fill=color)


class UltimateSystemV7_3:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Elevator - Ultimate Edition Final")
        self.root.configure(bg="#1a1a2e")
        
        self.request_queue = deque()
        self.floor_heatmap = {i: 0 for i in range(11)}
        self.start_time = time.time()
        self.log_messages = []

        self.canvas = tk.Canvas(root, width=530, height=560, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20)
        
        for i in range(11):
            y = 500 - (i * 45)
            self.canvas.create_line(70, y, 460, y, fill="#2c3e50")
            self.canvas.create_text(35, y-22, text=f"L{i}", fill="#ecf0f1")

        self.elevators = [Elevator(i+1, self.canvas, 120 + (i*125)) for i in range(3)]
        
        # Sidebar Panel
        self.sidebar = tk.Frame(root, bg="#16213e", padx=20, pady=10)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(self.sidebar, text="AI ELEVATOR v7.3 FINAL", fg="#e94560", bg="#16213e", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.stats_label = tk.Label(self.sidebar, text="", fg="#00ff00", bg="#0f1b2e", font=("Courier", 9), justify=tk.LEFT, padx=10, pady=10)
        self.stats_label.pack(fill=tk.X)

        tk.Label(self.sidebar, text="FLOOR HEATMAP", fg="#e94560", bg="#16213e", font=("Arial", 10, "bold")).pack(pady=(15,5))
        self.heatmap_label = tk.Label(self.sidebar, text="", fg="#00aaff", bg="#0f1b2e", font=("Courier", 8), justify=tk.LEFT, padx=10, pady=8)
        self.heatmap_label.pack(fill=tk.X)

        tk.Label(self.sidebar, text="EVENT LOG", fg="#e94560", bg="#16213e", font=("Arial", 10, "bold")).pack(pady=(15,5))
        self.log_frame = tk.Frame(self.sidebar, bg="#16213e")
        self.log_frame.pack(fill=tk.X)
        self.log_text = tk.Text(self.log_frame, height=10, width=32, bg="#0f1b2e", fg="#00ffaa", font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.X)

        tk.Button(self.sidebar, text="EMERGENCY STOP", bg="#c0392b", fg="white", command=self.emergency).pack(fill=tk.X, pady=8)
        tk.Button(self.sidebar, text="RESET ALL", bg="#7f8c8d", fg="white", command=self.reset_all).pack(fill=tk.X, pady=5)

        tk.Label(self.sidebar, text="CALL FROM FLOOR", fg="white", bg="#16213e", font=("Arial", 10, "bold")).pack(pady=(15,8))
        for i in range(10, -1, -1):
            tk.Button(self.sidebar, text=f"Floor {i}", width=18, bg="#0f3460", fg="white", 
                      command=lambda f=i: self.add_request(f)).pack(pady=2)

        self.master_loop()

    def add_log(self, message):
        ts = time.strftime("%H:%M:%S")
        self.log_messages.append(f"[{ts}] {message}")
        if len(self.log_messages) > 12: self.log_messages.pop(0)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "\n".join(self.log_messages))
        self.log_text.see(tk.END)

    def add_request(self, floor):
        already_assigned = any(ev.has_destination(floor) for ev in self.elevators)
        already_queued = any(r['floor'] == floor for r in self.request_queue)
        if not already_assigned and not already_queued:
            self.floor_heatmap[floor] += 1
            self.request_queue.append({'floor': floor, 'time': time.time()})
            self.add_log(f"New Call → Floor {floor}")

    def emergency(self):
        for ev in self.elevators:
            ev.up_stops.clear(); ev.down_stops.clear(); ev.direction = 0
        self.request_queue.clear()
        self.add_log("🚨 EMERGENCY STOP")

    def reset_all(self):
        for ev in self.elevators:
            ev.up_stops.clear(); ev.down_stops.clear(); ev.direction = 0
            ev.total_dist = 0.0; ev.served_count = 0; ev.logical_floor = 0
            ev.pixel_y = 450.0
            self.canvas.coords(ev.rect, 120 + ((ev.id-1)*125), 450, 120 + ((ev.id-1)*125)+50, 500)
            self.canvas.coords(ev.text, 120 + ((ev.id-1)*125)+25, 475)
        self.request_queue.clear()
        self.floor_heatmap = {i: 0 for i in range(11)}
        self.start_time = time.time()
        self.add_log("System Reset")

    def calculate_cost(self, ev, floor, wait_time):
        """Heuristic Cost Function"""
        if ev.get_load() >= ev.capacity: return float('inf')
        dist = ev.estimated_travel_distance(floor)
        load_penalty = ev.get_load() * 4.5
        alignment_bonus = 10 if (ev.direction == 1 and floor >= ev.logical_floor) or (ev.direction == -1 and floor <= ev.logical_floor) else 1
        aging = min(wait_time * 1.5, 15)
        dir_penalty = 8 if ev.direction == 0 and ev.get_load() > 0 else 0
        return dist + load_penalty - alignment_bonus + dir_penalty - aging

    def dispatch_logic(self):
        max_per_tick = max(2, min(len(self.request_queue), len(self.elevators) * 2))
        processed = 0
        while self.request_queue and processed < max_per_tick:
            req = self.request_queue[0]
            floor = req['floor']; wait_time = time.time() - req['time']
            best_ev = None; min_cost = float('inf')
            for ev in self.elevators:
                cost = self.calculate_cost(ev, floor, wait_time)
                if cost < min_cost: min_cost = cost; best_ev = ev
            if best_ev:
                best_ev.add_destination(floor)
                self.request_queue.popleft()
                self.add_log(f"F{floor} → E{best_ev.id} (Cost: {min_cost:.1f})")
                processed += 1
            else: break

    def update_heatmap_ui(self):
        max_val = max(self.floor_heatmap.values()) or 1
        lines = []
        for f in range(10, -1, -1):
            count = self.floor_heatmap[f]
            if count > 0:
                bar = "█" * int((count / max_val) * 12)
                lines.append(f"L{f:2d} {bar:<12} {count}")
        self.heatmap_label.config(text="\n".join(lines) if lines else "No calls yet")

    def master_loop(self):
        served = sum(e.served_count for e in self.elevators)
        dist = sum(e.total_dist for e in self.elevators)
        eff = (served / dist) if dist > 0 else 0.0
        stats = (f"Uptime: {int(time.time()-self.start_time)}s\n"
                 f"Served: {served}\n"
                 f"Total Dist: {dist:.1f}F\n"
                 f"Efficiency: {eff:.2f} R/F\n"
                 f"Pending: {len(self.request_queue)}")
        self.stats_label.config(text=stats)
        self.update_heatmap_ui()
        for ev in self.elevators: ev.step()
        if self.request_queue: self.dispatch_logic()
        self.root.after(40, self.master_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateSystemV7_3(root)
    root.mainloop()