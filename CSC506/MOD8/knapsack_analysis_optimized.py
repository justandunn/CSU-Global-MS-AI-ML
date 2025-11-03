# knapsack_analysis_optimized.py
# Author: Justan E. Dunn
# Date: 2025-10-27
# Purpose: Empirically analyze & optimize 0-1 Knapsack implementations
#          (recursive, recursive+memo, DP 2D, DP 1D) with timing & memory.

import random
import time
import tracemalloc
import sys
from statistics import mean

# -----------------------------
# Dataset generation utilities
# -----------------------------
def generate_dataset(num_items: int, seed: int = 42):
    """
    Create a deterministic dataset of (value, weight) pairs.
    Weights/values sized to keep capacities realistic.
    """
    rng = random.Random(seed + num_items)  # vary per n, but deterministic
    items = []
    for _ in range(num_items):
        value = rng.randint(10, 100)     # benefit (profit/readiness)
        weight = rng.randint(5, 30)      # cost (capacity/time)
        items.append((value, weight))
    # Capacity ~ about one-third of total weight to keep interesting
    capacity = max(30, sum(w for _, w in items) // 3)
    return items, capacity

# -----------------------------
# Algorithms
# -----------------------------
def knapsack_recursive(items, capacity):
    """
    Plain recursive backtracking (exponential).
    Returns (best_value, max_depth_seen)
    """
    sys.setrecursionlimit(10000)
    max_depth = [0]

    def rec(i, remaining, depth):
        if depth > max_depth[0]:
            max_depth[0] = depth
        if i == len(items) or remaining == 0:
            return 0
        v, w = items[i]
        # skip if too heavy
        best = rec(i + 1, remaining, depth + 1)
        if w <= remaining:
            best = max(best, v + rec(i + 1, remaining - w, depth + 1))
        return best

    best_val = rec(0, capacity, 1)
    return best_val, max_depth[0]


def knapsack_recursive_memo(items, capacity):
    """
    Top-down DP with memoization.
    Returns (best_value, max_depth_seen)
    """
    sys.setrecursionlimit(10000)
    memo = {}
    max_depth = [0]

    def rec(i, remaining, depth):
        if depth > max_depth[0]:
            max_depth[0] = depth
        if i == len(items) or remaining == 0:
            return 0
        key = (i, remaining)
        if key in memo:
            return memo[key]
        v, w = items[i]
        best = rec(i + 1, remaining, depth + 1)
        if w <= remaining:
            best = max(best, v + rec(i + 1, remaining - w, depth + 1))
        memo[key] = best
        return best

    best_val = rec(0, capacity, 1)
    return best_val, max_depth[0]


def knapsack_dp_2d(items, capacity):
    """
    Bottom-up DP with 2D table. Returns (best_value, peak_table_bytes_est)
    """
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        v, w = items[i - 1]
        for cap in range(1, capacity + 1):
            if w <= cap:
                table[i][cap] = max(v + table[i - 1][cap - w], table[i - 1][cap])
            else:
                table[i][cap] = table[i - 1][cap]
    best_val = table[n][capacity]
    # rough memory estimate: number of cells * ~28 bytes per Python int (illustrative)
    table_cells = (n + 1) * (capacity + 1)
    approx_bytes = table_cells * 28
    return best_val, approx_bytes


def knapsack_dp_1d(items, capacity):
    """
    Bottom-up DP optimized with 1D rolling array. Returns best_value.
    """
    dp = [0] * (capacity + 1)
    for v, w in items:
        # iterate backwards to avoid reusing same item
        for cap in range(capacity, w - 1, -1):
            cand = v + dp[cap - w]
            if cand > dp[cap]:
                dp[cap] = cand
    return dp[capacity]

# -----------------------------
# Benchmark helpers
# -----------------------------
def time_and_peak_memory(func, *args, repeats=5):
    """
    Run func(*args) multiple times; return (avg_seconds, peak_kb, extra_info)
    Uses tracemalloc for peak memory during one representative run.
    """
    # time
    times = []
    ret_last = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        ret_last = func(*args)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    # peak memory on a fresh run
    tracemalloc.start()
    _ = func(*args)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak / 1024.0
    avg_s = mean(times)
    return avg_s, peak_kb, ret_last

# -----------------------------
# Reporting
# -----------------------------
def print_divider(title):
    print("\\n" + "=" * 14, title, "=" * 14)

def human_bytes(nbytes):
    units = ["B", "KB", "MB", "GB"]
    s = 0
    v = float(nbytes)
    while v >= 1024 and s < len(units) - 1:
        v /= 1024
        s += 1
    return f"{v:.1f} {units[s]}"

# -----------------------------
# Main experiment
# -----------------------------
if __name__ == "__main__":
    # Choose problem sizes
    sizes = [5, 10, 15, 20]

    # ===== Figure 1: Runtime comparison table =====
    print_divider("FIGURE 1: Runtime Comparison (avg seconds over 3 runs)")
    header = f"{'n':>3} | {'Cap':>5} | {'Rec':>8} | {'Rec+Memo':>9} | {'DP 2D':>8} | {'DP 1D':>8}"
    print(header)
    print("-" * len(header))

    runtime_rows = []

    # We’ll also collect memory & recursion for Figure 2
    mem_rows = []

    for n in sizes:
        items, capacity = generate_dataset(n)
        # Recursive (plain)
        rec_time, rec_peak_kb, (rec_val, rec_max_depth) = time_and_peak_memory(knapsack_recursive, items, capacity, repeats=3)
        # Recursive + memo
        memo_time, memo_peak_kb, (memo_val, memo_max_depth) = time_and_peak_memory(knapsack_recursive_memo, items, capacity, repeats=3)
        # DP 2D
        dp2d_time, dp2d_peak_kb, (dp2d_val, dp2d_bytes) = time_and_peak_memory(knapsack_dp_2d, items, capacity, repeats=3)
        # DP 1D
        dp1d_time, dp1d_peak_kb, dp1d_val = time_and_peak_memory(knapsack_dp_1d, items, capacity, repeats=3)

        # Sanity check: all best values should match
        assert rec_val == memo_val == dp2d_val == dp1d_val, "Mismatch in optimal values!"

        print(f"{n:>3} | {capacity:>5} | {rec_time:>8.4f} | {memo_time:>9.4f} | {dp2d_time:>8.4f} | {dp1d_time:>8.4f}")
        runtime_rows.append((n, capacity, rec_time, memo_time, dp2d_time, dp1d_time))

        mem_rows.append({
            "n": n,
            "capacity": capacity,
            "rec_peak_kb": rec_peak_kb,
            "rec_max_depth": rec_max_depth,
            "memo_peak_kb": memo_peak_kb,
            "memo_max_depth": memo_max_depth,
            "dp2d_peak_kb": dp2d_peak_kb,
            "dp2d_approx_bytes": dp2d_bytes,
            "dp1d_peak_kb": dp1d_peak_kb
        })

    # ===== Figure 2: Memory & Recursion Depth =====
    print_divider("FIGURE 2: Memory & Recursion Depth")
    print(f"{'n':>3} | {'Rec Peak (KB)':>13} | {'Rec Depth':>9} | {'Memo Peak (KB)':>14} | {'Memo Depth':>10} | {'DP2D Peak (KB)':>14} | {'DP1D Peak (KB)':>14}")
    print("-" * 100)
    for r in mem_rows:
        print(f"{r['n']:>3} | {r['rec_peak_kb']:>13.1f} | {r['rec_max_depth']:>9} | "
              f"{r['memo_peak_kb']:>14.1f} | {r['memo_max_depth']:>10} | "
              f"{r['dp2d_peak_kb']:>14.1f} | {r['dp1d_peak_kb']:>14.1f}")

    # Optional: show rough DP 2D table memory footprint estimate for largest n
    largest = max(mem_rows, key=lambda x: x["n"])
    print("\\nApprox DP 2D table memory for largest case "
          f"(lower-bound object estimate): {human_bytes(largest['dp2d_approx_bytes'])}")

    # ===== Figure 3: Optimized DP 1D on largest dataset =====
    n = max(sizes)
    items, capacity = generate_dataset(n)
    print_divider("FIGURE 3: Optimized DP 1D Detailed Run")
    print("Items (value, weight):")
    for i, (v, w) in enumerate(items, 1):
        print(f"  {i:>2}: v={v}, w={w}")
    print(f"Capacity: {capacity}\\n")

    tracemalloc.start()
    t0 = time.perf_counter()
    best_val = knapsack_dp_1d(items, capacity)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Optimal value (DP 1D): {best_val}")
    print(f"Execution time: {t1 - t0:.4f} seconds")
    print(f"Peak memory (DP 1D): {peak/1024:.1f} KB")
    print("\\nSummary: 1D DP achieves the same optimal value as other methods while using significantly less memory than 2D DP.")
