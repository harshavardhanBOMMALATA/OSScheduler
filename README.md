# OSScheduler Visualizer

🔗 Live Demo: https://osschedulevisualizer.onrender.com

---

## Introduction

OSScheduler is a Django-based web visualization project that helps users understand operating system scheduling algorithms through beautiful and interactive visualizations.

Many students and learners struggle to understand scheduling concepts when they are limited to Gantt charts and static graphs. This project makes learning easier by visually showing how scheduling algorithms work step by step.

OSScheduler is helpful for students and anyone who wants to learn or revise OS scheduling algorithms in a more intuitive and practical way.

---

## Problem Statement

Many students and learners try to understand CPU scheduling algorithms by reading theory and looking at Gantt charts, but still end up feeling confused. It is hard to imagine how processes actually move and change during execution just from diagrams. This website helps solve that problem by visually showing process flow and scheduling in a clear and easy-to-understand way.

---

## Description and About the Project

Imagine a CPU as a single service counter and processes as people waiting in a queue to get their work done. Most students learn scheduling by reading rules and drawing Gantt charts, but it is still hard to picture what is really happening at that counter. OSScheduler is built to solve this exact problem by visually showing how processes move, wait, and execute inside the CPU.

The frontend of OSScheduler is designed like a guided walkthrough. As soon as processes are added, users can see them entering the system, waiting in line, and getting picked by the CPU based on the selected scheduling algorithm. Colors, smooth transitions, and clear layouts help users understand why one process runs before another, just like watching people move forward in a real queue.

Visualization is the key part of the project. JavaScript handles how processes shift between states, pause, resume, or finish execution. The frontend behaves like a screen showing live activity, while all decision-making happens in the backend. This makes the learning experience feel more like watching a real system in action rather than reading static diagrams.

Behind the scenes, the backend is implemented using Python and acts as the “brain” of the scheduler. It applies the rules of each scheduling algorithm using efficient logic and data structures like heaps and priority queues. Once the decisions are made, the backend sends only the final scheduling steps to the frontend, which then brings them to life through visualization.

---

## Scheduling Algorithms Implemented

CPU scheduling can be compared to different ways a manager decides who gets served next. Each algorithm follows a different idea, and this project helps users see how those ideas play out in real time.

### First Come First Serve (FCFS) — O(n)

Think of a simple line at a ticket counter.

- Whoever comes first gets served first.
- No one is allowed to interrupt once service starts.
- Since the scheduler just moves forward through the queue once, the complexity is linear.
- If a very slow customer comes first, everyone else has to wait longer.

### Shortest Job First (SJF) — O(n log n)

This is like a counter that prefers people with quick tasks.

- The process with the smallest burst time is selected first.
- To always find the shortest job, the scheduler keeps processes sorted or in a min-heap.
- Maintaining this order adds the log n cost.
- If sorting is ignored, the scheduler may pick the wrong process.

### Longest Job First (LJF) — O(n log n)

Here, longer tasks are given priority.

- The process with the longest burst time runs first.
- Selection logic is similar to SJF but reversed.
- Sorting or heap management is still required.
- Without burst-time comparison, the algorithm loses its meaning.

### Shortest Remaining Time First (SRTF) — O(n log n)

This works like a service counter that constantly rechecks the queue.

- A running process can be stopped if a shorter job arrives.
- Remaining time changes as execution progresses.
- The scheduler frequently updates and reselects processes using a heap.
- Skipping these checks would make the scheduling inaccurate.

### Longest Remaining Time First (LRTF) — O(n log n)

Opposite of SRTF, focusing on longer remaining work.

- The process with the most remaining time is chosen.
- Remaining time updates after each execution step.
- A max-heap ensures correct selection.
- Ignoring updates would lead to wrong execution order.

### Priority Scheduling (Non-Preemptive) — O(n log n)

Imagine an office where VIPs are served first.

- Each process has a priority level.
- The highest-priority process runs when the CPU becomes free.
- A priority queue helps in fast selection.
- Low-priority processes may wait longer.

### Priority Scheduling (Preemptive) — O(n log n)

This is a stricter VIP system.

- A higher-priority process can interrupt the one currently running.
- The scheduler checks priorities whenever a new process arrives.
- Frequent checking increases computational cost.
- Without interruption, it behaves like the non-preemptive version.

### Round Robin — O(n × k)

This is like giving everyone a fixed time at the counter.

- Each process gets a small time slice.
- If unfinished, it goes back to the queue.
- Processes repeat multiple rounds before completion.
- The number of rounds depends on burst time and time quantum.

---

## Conclusion

OSScheduler Visualizer was built with a simple idea in mind: scheduling makes more sense when you can actually see it happening. While learning operating systems, many of us understand the definitions but still feel confused when it comes to visualizing process execution. This project tries to bridge that gap by showing how scheduling decisions affect processes in real time.

By combining clear visuals with correct scheduling logic, OSScheduler helps learners move beyond theory and gain practical understanding. It is especially useful for students who want to build intuition about scheduling algorithms rather than just memorizing them.

---

## Connect with Me

If you’d like to connect, collaborate, or discuss this project, feel free to reach out through any of the platforms below:

- LinkedIn: https://www.linkedin.com/in/harshavardhan-bommalata-7bb9442b0
- GitHub: https://github.com/harshavardhanBOMMALATA
- Instagram: https://www.instagram.com/always_harsha_royal/?hl=en
- Email: hbommalata@gmail.com
