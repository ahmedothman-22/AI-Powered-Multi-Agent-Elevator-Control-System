# 🏢 AI Elevator Dispatch System (A*)

## 📌 Overview
This project is a simulation of a smart multi-elevator dispatch system using Artificial Intelligence (A* Search Algorithm).

The system simulates real-world elevator behavior inside a building and intelligently assigns requests to the best elevator based on:
- Current position
- Pending requests
- Travel cost
- Waiting time priority
- Load balancing between elevators

It also provides a real-time GUI simulation using Tkinter with animations, analytics, and heatmap visualization.

---

## 🧠 AI Concept Used

### 🔎 A* Search Algorithm
Each elevator uses A* search to compute the optimal path for serving requests.

### State Representation:
(current_floor, unvisited_requests)

### Actions:
Move directly to any requested floor.

### Transition:
(current_floor, remaining) → (next_floor, remaining - {next_floor})

### Step Cost:
|current_floor - next_floor|

### Goal Test:
All requested floors are served (remaining == empty)

---

## 🎯 Heuristic Function

The heuristic is designed to be admissible and consistent:

h(n) = (max(unvisited) - min(unvisited)) + distance_to_nearest_extreme

Where:
- span = max - min (minimum required travel range)
- nearest_extreme = distance from current floor to closest boundary

✔ Ensures A* finds optimal solution  
✔ Never overestimates cost  
✔ Guarantees optimal path planning  

---

## ⚙️ Features

### 🚀 Smart Dispatching System
- Assigns each request to the best elevator dynamically
- Uses A* cost estimation for decision making
- Considers:
  - Elevator load
  - Travel cost
  - Waiting time priority
  - System efficiency

---

### 🧭 Path Optimization
- Each elevator computes optimal route using A*
- Avoids unnecessary movement
- Dynamically replans when new requests arrive

---

### 🎮 GUI Simulation (Tkinter)
- Animated elevator movement
- Building floor grid (0–10)
- Direction indicators (▲ ▼)
- Path visualization line
- Real-time updates

---

### 📊 Analytics Dashboard
- Total served requests
- Total distance traveled
- Efficiency (requests per floor traveled)
- System uptime
- Queue size monitoring

---

### 🔥 Floor Heatmap
- Tracks frequency of requests per floor
- Displays demand intensity visually
- Helps identify high-traffic floors

---

### 🎛️ Controls
- Random Traffic Generator
- Emergency Stop (clears all requests)
- Full System Reset
- Manual floor request buttons (0–10)

---

## 🏗️ System Architecture

User Request → Queue → Dispatcher → A* Planner → Elevator Selection → Execution

---

## 🧩 Project Components

### 1. ElevatorProblem Class
Handles:
- State representation
- Successor generation
- Goal test
- Heuristic calculation

---

### 2. A* Search Engine
Implements:
- Priority queue (heapq)
- Path cost tracking
- State pruning (reached table)
- Optimal path selection

---

### 3. Elevator Class
Responsible for:
- Movement animation
- Request handling
- Path execution
- Real-time GUI updates
- Floor transitions

---

### 4. App Controller
Manages:
- Dispatching logic
- Request queue
- UI updates loop
- System monitoring
- Performance metrics

---

## 📈 Performance Metrics
The system tracks in real time:
- Total served requests
- Total distance traveled
- Efficiency ratio (requests/floor)
- Queue size
- Floor heatmap intensity
- System uptime
-
-

---

## 🧪 How to Run

### Requirements:
- Python 3.8+
- Tkinter (built-in with Python)

### Run the project:
git clone https://github.com/ahmedothman-22/AI-Powered-Multi-Agent-Elevator-Control-System.git
