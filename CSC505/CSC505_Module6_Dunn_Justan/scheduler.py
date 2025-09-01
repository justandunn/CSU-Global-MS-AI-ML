# scheduler.py
# Module 6: Stepwise Refinement - Simple Task Scheduling (Round Robin + FCFS)
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class Task:
    name: str
    burst: int  # CPU time required
    arrival: int = 0  # default all tasks arrive at 0

def fcfs(tasks: List[Task]) -> Tuple[List[Tuple[str, int]], Dict[str, Dict[str, float]]]:
    """First-Come, First-Served scheduler."""
    time = 0
    timeline: List[Tuple[str, int]] = []
    metrics: Dict[str, Dict[str, float]] = {}
    for t in tasks:
        if time < t.arrival:
            timeline.append(("_IDLE_", t.arrival - time))
            time = t.arrival
        start = time
        timeline.append((t.name, t.burst))
        time += t.burst
        completion = time
        turnaround = completion - t.arrival
        waiting = turnaround - t.burst
        metrics[t.name] = {"waiting": waiting, "turnaround": turnaround}
    return timeline, metrics

def round_robin(tasks: List[Task], quantum: int) -> Tuple[List[Tuple[str, int]], Dict[str, Dict[str, float]]]:
    """Round Robin scheduler with fixed quantum."""
    from collections import deque
    ready = deque(tasks)
    remaining = {t.name: t.burst for t in tasks}
    time = 0
    timeline: List[Tuple[str, int]] = []
    completion: Dict[str, int] = {}

    while ready:
        t = ready.popleft()
        rem = remaining[t.name]
        run = min(quantum, rem)
        timeline.append((t.name, run))
        time += run
        rem -= run
        if rem > 0:
            remaining[t.name] = rem
            ready.append(t)
        else:
            remaining[t.name] = 0
            completion[t.name] = time

    metrics: Dict[str, Dict[str, float]] = {}
    for t in tasks:
        tat = completion[t.name] - t.arrival
        wt = tat - t.burst
        metrics[t.name] = {"waiting": wt, "turnaround": tat}
    return timeline, metrics

def format_timeline(timeline: List[Tuple[str, int]]) -> str:
    """Return a simple Gantt-like string."""
    out = []
    current = 0
    for name, dur in timeline:
        segment = f"|{name:>5} {current:>3}→{current+dur:>3}|"
        out.append(segment)
        current += dur
    return "".join(out)

def print_results(algoname: str, timeline: List[Tuple[str, int]], metrics: Dict[str, Dict[str, float]]):
    print(f"=== {algoname} Schedule ===")
    print(format_timeline(timeline))
    print("\nPer-task metrics:")
    wt_sum = tat_sum = 0
    for name, m in metrics.items():
        wt_sum += m["waiting"]
        tat_sum += m["turnaround"]
        print(f" - {name}: waiting={m['waiting']}, turnaround={m['turnaround']}")
    n = len(metrics)
    print(f"\nAverages: waiting={wt_sum/n:.2f}, turnaround={tat_sum/n:.2f}")
    print("-" * 60)

def demo():
    tasks = [Task("A", 10), Task("B", 5), Task("C", 8)]
    tl_fcfs, m_fcfs = fcfs(tasks)
    print_results("FCFS", tl_fcfs, m_fcfs)
    quantum = 3
    tl_rr, m_rr = round_robin(tasks, quantum)
    print_results(f"Round Robin (q={quantum})", tl_rr, m_rr)

if __name__ == "__main__":
    print("=== Module 6: Stepwise Refinement - Task Scheduling Demo ===\n")
    demo()