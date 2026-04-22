# AI-Powered Multi-Agent Elevator Control System

## 📌 Project Overview
This project is an intelligent elevator simulation and dispatch system built in Python. It applies core concepts from the **"Artificial Intelligence: A Modern Approach" (AIMA)** textbook to solve the classic multi-elevator scheduling problem. The goal is to minimize passenger wait times and optimize elevator travel distances using Heuristic Search algorithms.

## 🚀 Phases of Development

### Phase 1: Environment & Naive Agent (GUI + Problem Solving)
- **Interactive GUI:** Built using `Tkinter`, simulating an 11-floor building with 3 elevators.
- **System Monitoring:** Features a live Event Log, a Floor Heatmap to track high-demand areas, and real-time efficiency statistics.
- **Naive Solution:** Implemented basic movement rules using the **LOOK Algorithm** (State Machine) without advanced AI, acting as the baseline performance metric (First-Come, First-Serve approach).

### Phase 2: AI Integration & Refactoring (Problem Formulation)
Refactored the codebase to clearly define the problem space according to AIMA standards:
- **State Space:** The current floor of each elevator, its direction, load, and pending requests.
- **Initial State:** All elevators at Floor 0, IDLE, with 0 load.
- **Actions:** `MOVE_UP`, `MOVE_DOWN`, `STOP_AND_SERVE`.
- **Goal Test:** All requests in the queue are served, and elevators return to IDLE.
- **Path Cost:** A custom Heuristic Function to calculate the optimal assignment.

## 🧠 The AI Component: Heuristic Search
Instead of naive dispatching, the system evaluates the best elevator for an incoming request using a **Heuristic Cost Function**. 

The cost is calculated based on:
1. **Estimated Distance:** Distance between the elevator and the requested floor.
2. **Load Penalty:** Heavily loaded elevators receive higher costs.
3. **Alignment Bonus:** Elevators already moving in the direction of the requested floor receive a cost reduction.
4. **Aging / Wait Time:** To prevent starvation, the cost decreases dynamically the longer a request sits in the queue.

## 🛠️ Technologies Used
- **Language:** Python 3.x
- **Libraries:** `Tkinter` (GUI), `time`, `collections.deque`
- **Algorithms:** LOOK Scheduling, Heuristic Search

## 🏃‍♂️ How to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/ahmedothman-22/AI-Powered-Multi-Agent-Elevator-Control-System.git
