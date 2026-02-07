from collections import deque
from django.http import JsonResponse
from django.shortcuts import render
import json
import heapq


# =========================
# FCFS SCHEDULER
# =========================
def fcfs_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []

    # NEW queue (sorted by arrival time)
    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,                # current burst index
        "burst_time": 0,           # total CPU time used
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = deque()               # READY queue
    blocked = []                  # (unblock_time, process)
    completed = []

    while new or ready or blocked:

        # NEW → READY
        for p in new[:]:
            if p["arrival"] <= time:
                ready.append(p)
                new.remove(p)

        # BLOCKED → READY
        for unblock_time, p in blocked[:]:
            if unblock_time <= time:
                ready.append(p)
                blocked.remove((unblock_time, p))

        if ready:
            p = ready.popleft()

            cpu_time = p["bursts"][p["index"]]
            start = time
            end = start + cpu_time

            # Response time only once
            if p["response_time"] is None:
                p["response_time"] = start - p["arrival"]

            gantt.append({"pid": p["pid"], "start": start, "end": end})

            p["burst_time"] += cpu_time
            p["index"] += 1

            # If IO burst exists → BLOCKED
            if p["index"] < len(p["bursts"]):
                io_time = p["bursts"][p["index"]]
                blocked.append((end + io_time, p))
                p["index"] += 1
            else:
                p["completion_time"] = end
                completed.append(p)

            time = end + context_switch if (new or ready or blocked) else end

        else:
            # CPU IDLE handling
            next_times = []
            if new:
                next_times.append(new[0]["arrival"])
            if blocked:
                next_times.append(min(t for t, _ in blocked))

            if next_times:
                next_time = min(next_times)
                gantt.append({"pid": "IDLE", "start": time, "end": next_time})
                time = next_time

    return build_response(gantt, completed, time)


# =========================
# SJF SCHEDULER (NON-PREEMPTIVE)
# =========================
def sjf_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0                     # tie-breaker for heap

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []                  # min-heap (cpu_time, tie, process)
    blocked = []
    completed = []

    while new or ready or blocked:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (p["bursts"][p["index"]], tie, p))
                tie += 1
                new.remove(p)

        for unblock_time, p in blocked[:]:
            if unblock_time <= time:
                heapq.heappush(ready, (p["bursts"][p["index"]], tie, p))
                tie += 1
                blocked.remove((unblock_time, p))

        if ready:
            _, _, p = heapq.heappop(ready)

            cpu_time = p["bursts"][p["index"]]
            start = time
            end = start + cpu_time

            if p["response_time"] is None:
                p["response_time"] = start - p["arrival"]

            gantt.append({"pid": p["pid"], "start": start, "end": end})

            p["burst_time"] += cpu_time
            p["index"] += 1

            if p["index"] < len(p["bursts"]):
                io_time = p["bursts"][p["index"]]
                blocked.append((end + io_time, p))
                p["index"] += 1
            else:
                p["completion_time"] = end
                completed.append(p)

            time = end + context_switch if (new or ready or blocked) else end

        else:
            next_times = []
            if new:
                next_times.append(new[0]["arrival"])
            if blocked:
                next_times.append(min(t for t, _ in blocked))

            if next_times:
                next_time = min(next_times)
                gantt.append({"pid": "IDLE", "start": time, "end": next_time})
                time = next_time

    return build_response(gantt, completed, time)


# =========================
# LJF SCHEDULER
# =========================
def ljf_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []                  # max-heap using negative burst
    blocked = []
    completed = []

    while new or ready or blocked:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (-p["bursts"][p["index"]], tie, p))
                tie += 1
                new.remove(p)

        for unblock_time, p in blocked[:]:
            if unblock_time <= time:
                heapq.heappush(ready, (-p["bursts"][p["index"]], tie, p))
                tie += 1
                blocked.remove((unblock_time, p))

        if ready:
            _, _, p = heapq.heappop(ready)

            cpu_time = p["bursts"][p["index"]]
            start = time
            end = start + cpu_time

            if p["response_time"] is None:
                p["response_time"] = start - p["arrival"]

            gantt.append({"pid": p["pid"], "start": start, "end": end})

            p["burst_time"] += cpu_time
            p["index"] += 1

            if p["index"] < len(p["bursts"]):
                io_time = p["bursts"][p["index"]]
                blocked.append((end + io_time, p))
                p["index"] += 1
            else:
                p["completion_time"] = end
                completed.append(p)

            time = end + context_switch if (new or ready or blocked) else end

        else:
            next_times = []
            if new:
                next_times.append(new[0]["arrival"])
            if blocked:
                next_times.append(min(t for t, _ in blocked))

            if next_times:
                next_time = min(next_times)
                gantt.append({"pid": "IDLE", "start": time, "end": next_time})
                time = next_time

    return build_response(gantt, completed, time)


# =========================
# PRIORITY SCHEDULER
# lower value = higher priority
# =========================
def priority_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "priority": p["priority"],   # lower number = higher priority
        "index": 0,
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []                  # (priority, tie, process)
    blocked = []
    completed = []

    while new or ready or blocked:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                new.remove(p)

        for unblock_time, p in blocked[:]:
            if unblock_time <= time:
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                blocked.remove((unblock_time, p))

        if ready:
            _, _, p = heapq.heappop(ready)

            cpu_time = p["bursts"][p["index"]]
            start = time
            end = start + cpu_time

            if p["response_time"] is None:
                p["response_time"] = start - p["arrival"]

            gantt.append({"pid": p["pid"], "start": start, "end": end})

            p["burst_time"] += cpu_time
            p["index"] += 1

            if p["index"] < len(p["bursts"]):
                io_time = p["bursts"][p["index"]]
                blocked.append((end + io_time, p))
                p["index"] += 1
            else:
                p["completion_time"] = end
                completed.append(p)

            time = end + context_switch if (new or ready or blocked) else end

        else:
            next_times = []
            if new:
                next_times.append(new[0]["arrival"])
            if blocked:
                next_times.append(min(t for t, _ in blocked))

            if next_times:
                next_time = min(next_times)
                gantt.append({"pid": "IDLE", "start": time, "end": next_time})
                time = next_time

    return build_response(gantt, completed, time)


# =========================
# COMMON RESPONSE BUILDER
# =========================
def build_response(gantt, completed, total_time):
    n = len(completed)
    total_tat = total_wt = total_rt = 0
    result = []

    for p in completed:
        tat = p["completion_time"] - p["arrival"]
        wt = tat - p["burst_time"]
        rt = p["response_time"]

        total_tat += tat
        total_wt += wt
        total_rt += rt

        result.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst_time": p["burst_time"],
            "completion_time": p["completion_time"],
            "tat": tat,
            "wt": wt,
            "rt": rt
        })

    return JsonResponse({
        "gantt": gantt,
        "processes": result,
        "average": {
            "tat": total_tat / n if n else 0,
            "wt": total_wt / n if n else 0,
            "rt": total_rt / n if n else 0
        },
        "system": {
            "total_time": total_time,
            "throughput": n / total_time if total_time > 0 else 0
        }
    }, safe=False)


def template(request):
    return render(request, "template.html")


def srtf_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "remaining": sum(p["bursts"][::2]),
        "bursts": p["bursts"],
        "index": 0,
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])
    ready = []
    completed = []

    current = None

    while new or ready or current:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (p["remaining"], tie, p))
                tie += 1
                new.remove(p)

        if current:
            heapq.heappush(ready, (current["remaining"], tie, current))
            tie += 1
            current = None

        if ready:
            _, _, p = heapq.heappop(ready)

            if p["response_time"] is None:
                p["response_time"] = time - p["arrival"]

            start = time
            p["remaining"] -= 1
            p["burst_time"] += 1
            time += 1

            gantt.append({"pid": p["pid"], "start": start, "end": time})

            if p["remaining"] == 0:
                p["completion_time"] = time
                completed.append(p)
            else:
                current = p
        else:
            time += 1

    return build_response(gantt, completed, time)


def lrtf_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "remaining": sum(p["bursts"][::2]),
        "bursts": p["bursts"],
        "index": 0,
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])
    ready = []
    completed = []
    current = None

    while new or ready or current:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (-p["remaining"], tie, p))
                tie += 1
                new.remove(p)

        if current:
            heapq.heappush(ready, (-current["remaining"], tie, current))
            tie += 1
            current = None

        if ready:
            _, _, p = heapq.heappop(ready)

            if p["response_time"] is None:
                p["response_time"] = time - p["arrival"]

            start = time
            p["remaining"] -= 1
            p["burst_time"] += 1
            time += 1

            gantt.append({"pid": p["pid"], "start": start, "end": time})

            if p["remaining"] == 0:
                p["completion_time"] = time
                completed.append(p)
            else:
                current = p
        else:
            time += 1

    return build_response(gantt, completed, time)


def preemptive_priority_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]
    context_switch = data.get("context_switch", 0)

    time = 0
    gantt = []
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "priority": p["priority"],
        "remaining": sum(p["bursts"][::2]),
        "burst_time": 0,
        "completion_time": None,
        "response_time": None
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])
    ready = []
    completed = []
    current = None

    while new or ready or current:

        for p in new[:]:
            if p["arrival"] <= time:
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                new.remove(p)

        if current:
            heapq.heappush(ready, (current["priority"], tie, current))
            tie += 1
            current = None

        if ready:
            _, _, p = heapq.heappop(ready)

            if p["response_time"] is None:
                p["response_time"] = time - p["arrival"]

            start = time
            p["remaining"] -= 1
            p["burst_time"] += 1
            time += 1

            gantt.append({"pid": p["pid"], "start": start, "end": time})

            if p["remaining"] == 0:
                p["completion_time"] = time
                completed.append(p)
            else:
                current = p
        else:
            time += 1

    return build_response(gantt, completed, time)

from collections import deque
from django.http import JsonResponse
import json

def fcfs_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}          # timeline[time] = [events]

    # -------------------------
    # INITIAL QUEUES
    # -------------------------
    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": 0
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = deque()
    blocked = []           # (unblock_time, process)
    running = None

    # -------------------------
    # MAIN LOOP (NO TIME SKIP)
    # -------------------------
    while new or ready or blocked or running:

        timeline[time] = []

        # ✅ INITIAL NEW STATE (ONLY ADDITION)
        if time == 0:
            for p in new:
                timeline[time].append({
                    "pid": p["pid"],
                    "from": None,
                    "to": "NEW"
                })

        # -------------------------
        # BLOCKED → READY
        # -------------------------
        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                ready.append(p)
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "BLOCKED",
                    "to": "READY"
                })

        # -------------------------
        # NEW → READY
        # -------------------------
        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                ready.append(p)
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "NEW",
                    "to": "READY"
                })

        # -------------------------
        # READY → RUNNING
        # -------------------------
        if running is None and ready:
            running = ready.popleft()
            running["remaining"] = running["bursts"][running["index"]]
            timeline[time].append({
                "pid": running["pid"],
                "from": "READY",
                "to": "RUNNING"
            })

        # -------------------------
        # EXECUTE 1 SECOND
        # -------------------------
        if running:
            running["remaining"] -= 1

            if running["remaining"] == 0:
                running["index"] += 1

                # RUNNING → BLOCKED
                if running["index"] < len(running["bursts"]):
                    io_time = running["bursts"][running["index"]]
                    blocked.append((time + io_time + 1, running))
                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "BLOCKED"
                    })
                    running["index"] += 1

                # RUNNING → COMPLETED
                else:
                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "COMPLETED"
                    })

                running = None

        time += 1

    return JsonResponse({"timeline": timeline}, safe=False)


def sjf_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}              # timeline[time] = [events]
    tie = 0                    # tie breaker for heap

    # -------------------------
    # INITIAL QUEUES
    # -------------------------
    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": 0
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []                 # min-heap → (cpu_time, tie, process)
    blocked = []               # (unblock_time, process)
    running = None

    # -------------------------
    # MAIN LOOP (NO TIME SKIP)
    # -------------------------
    while new or ready or blocked or running:

        timeline[time] = []

        # -------------------------
        # BLOCKED → READY
        # -------------------------
        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                heapq.heappush(
                    ready,
                    (p["bursts"][p["index"]], tie, p)
                )
                tie += 1
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "BLOCKED",
                    "to": "READY"
                })

        # -------------------------
        # NEW → READY
        # -------------------------
        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(
                    ready,
                    (p["bursts"][p["index"]], tie, p)
                )
                tie += 1
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "NEW",
                    "to": "READY"
                })

        # -------------------------
        # READY → RUNNING (SJF)
        # -------------------------
        if running is None and ready:
            _, _, running = heapq.heappop(ready)
            running["remaining"] = running["bursts"][running["index"]]
            timeline[time].append({
                "pid": running["pid"],
                "from": "READY",
                "to": "RUNNING"
            })

        # -------------------------
        # EXECUTE 1 SECOND
        # -------------------------
        if running:
            running["remaining"] -= 1

            # CPU burst finished
            if running["remaining"] == 0:
                running["index"] += 1

                # RUNNING → BLOCKED
                if running["index"] < len(running["bursts"]):
                    io_time = running["bursts"][running["index"]]
                    blocked.append((time + io_time + 1, running))

                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "BLOCKED"
                    })

                    running["index"] += 1

                # RUNNING → COMPLETED
                else:
                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "COMPLETED"
                    })

                running = None

        # -------------------------
        # NEXT SECOND
        # -------------------------
        time += 1

    return JsonResponse({
        "timeline": timeline
    }, safe=False)


def ljf_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}              # timeline[time] = [events]
    tie = 0                    # tie breaker for heap

    # -------------------------
    # INITIAL QUEUES
    # -------------------------
    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": 0
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []                 # max-heap → (-cpu_time, tie, process)
    blocked = []               # (unblock_time, process)
    running = None

    # -------------------------
    # MAIN LOOP (NO TIME SKIP)
    # -------------------------
    while new or ready or blocked or running:

        timeline[time] = []

        # -------------------------
        # BLOCKED → READY
        # -------------------------
        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                heapq.heappush(
                    ready,
                    (-p["bursts"][p["index"]], tie, p)
                )
                tie += 1
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "BLOCKED",
                    "to": "READY"
                })

        # -------------------------
        # NEW → READY
        # -------------------------
        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(
                    ready,
                    (-p["bursts"][p["index"]], tie, p)
                )
                tie += 1
                timeline[time].append({
                    "pid": p["pid"],
                    "from": "NEW",
                    "to": "READY"
                })

        # -------------------------
        # READY → RUNNING (LJF)
        # -------------------------
        if running is None and ready:
            _, _, running = heapq.heappop(ready)
            running["remaining"] = running["bursts"][running["index"]]
            timeline[time].append({
                "pid": running["pid"],
                "from": "READY",
                "to": "RUNNING"
            })

        # -------------------------
        # EXECUTE 1 SECOND
        # -------------------------
        if running:
            running["remaining"] -= 1

            # CPU burst finished
            if running["remaining"] == 0:
                running["index"] += 1

                # RUNNING → BLOCKED
                if running["index"] < len(running["bursts"]):
                    io_time = running["bursts"][running["index"]]
                    blocked.append((time + io_time + 1, running))

                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "BLOCKED"
                    })

                    running["index"] += 1

                # RUNNING → COMPLETED
                else:
                    timeline[time].append({
                        "pid": running["pid"],
                        "from": "RUNNING",
                        "to": "COMPLETED"
                    })

                running = None

        # -------------------------
        # NEXT SECOND
        # -------------------------
        time += 1

    return JsonResponse({
        "timeline": timeline
    }, safe=False)


import heapq
from django.http import JsonResponse
import json


def srtf_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": sum(p["bursts"][::2])
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []           # (remaining, tie, p)
    blocked = []
    running = None

    while new or ready or blocked or running:

        timeline[time] = []

        # BLOCKED → READY
        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                heapq.heappush(ready, (p["remaining"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "BLOCKED", "to": "READY"})

        # NEW → READY
        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(ready, (p["remaining"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "NEW", "to": "READY"})

        # PREEMPT
        if running:
            heapq.heappush(ready, (running["remaining"], tie, running))
            tie += 1
            running = None

        # READY → RUNNING
        if ready:
            _, _, running = heapq.heappop(ready)
            timeline[time].append({"pid": running["pid"], "from": "READY", "to": "RUNNING"})

        # EXECUTE 1 SECOND
        if running:
            running["remaining"] -= 1

            if running["remaining"] == 0:
                timeline[time].append({"pid": running["pid"], "from": "RUNNING", "to": "COMPLETED"})
                running = None

        time += 1

    return JsonResponse({"timeline": timeline}, safe=False)



def lrtf_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": sum(p["bursts"][::2])
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []           # (-remaining, tie, p)
    blocked = []
    running = None

    while new or ready or blocked or running:

        timeline[time] = []

        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                heapq.heappush(ready, (-p["remaining"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "BLOCKED", "to": "READY"})

        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(ready, (-p["remaining"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "NEW", "to": "READY"})

        if running:
            heapq.heappush(ready, (-running["remaining"], tie, running))
            tie += 1
            running = None

        if ready:
            _, _, running = heapq.heappop(ready)
            timeline[time].append({"pid": running["pid"], "from": "READY", "to": "RUNNING"})

        if running:
            running["remaining"] -= 1
            if running["remaining"] == 0:
                timeline[time].append({"pid": running["pid"], "from": "RUNNING", "to": "COMPLETED"})
                running = None

        time += 1

    return JsonResponse({"timeline": timeline}, safe=False)


def priority_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "priority": p["priority"],
        "bursts": p["bursts"],
        "index": 0,
        "remaining": 0
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []           # (priority, tie, p)
    blocked = []
    running = None

    while new or ready or blocked or running:

        timeline[time] = []

        for unblock_time, p in blocked[:]:
            if unblock_time == time:
                blocked.remove((unblock_time, p))
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "BLOCKED", "to": "READY"})

        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "NEW", "to": "READY"})

        if running is None and ready:
            _, _, running = heapq.heappop(ready)
            running["remaining"] = running["bursts"][running["index"]]
            timeline[time].append({"pid": running["pid"], "from": "READY", "to": "RUNNING"})

        if running:
            running["remaining"] -= 1
            if running["remaining"] == 0:
                timeline[time].append({"pid": running["pid"], "from": "RUNNING", "to": "COMPLETED"})
                running = None

        time += 1

    return JsonResponse({"timeline": timeline}, safe=False)


def prtf_visualization_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    processes = data["processes"]

    time = 0
    timeline = {}
    tie = 0

    new = [{
        "pid": p["pid"],
        "arrival": p["arrival"],
        "priority": p["priority"],
        "remaining": sum(p["bursts"][::2])
    } for p in processes]

    new.sort(key=lambda x: x["arrival"])

    ready = []           # (priority, tie, p)
    blocked = []
    running = None

    while new or ready or blocked or running:

        timeline[time] = []

        for p in new[:]:
            if p["arrival"] == time:
                new.remove(p)
                heapq.heappush(ready, (p["priority"], tie, p))
                tie += 1
                timeline[time].append({"pid": p["pid"], "from": "NEW", "to": "READY"})

        if running:
            heapq.heappush(ready, (running["priority"], tie, running))
            tie += 1
            running = None

        if ready:
            _, _, running = heapq.heappop(ready)
            timeline[time].append({"pid": running["pid"], "from": "READY", "to": "RUNNING"})

        if running:
            running["remaining"] -= 1
            if running["remaining"] == 0:
                timeline[time].append({"pid": running["pid"], "from": "RUNNING", "to": "COMPLETED"})
                running = None

        time += 1

    return JsonResponse({"timeline": timeline}, safe=False)
