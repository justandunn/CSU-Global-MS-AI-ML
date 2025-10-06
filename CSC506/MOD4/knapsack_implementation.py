# knapsack_implementation.py
# Author: Justan Dunn
# Date: October 13, 2025
# Purpose: Implement and compare recursive and dynamic-programming
#          0-1 Knapsack algorithms in a fleet-operations context.

import random
import time

# -----------------------------
# Generate test dataset
# -----------------------------
def generate_dataset(num_items, seed=42):
    random.seed(seed)
    items = []
    for i in range(num_items):
        # Simulate fleet repair tasks or cargo shipments
        value = random.randint(10, 100)    # readiness/profit benefit
        weight = random.randint(5, 30)     # time or capacity cost
        items.append((value, weight))
    return items

# -----------------------------
# Recursive Backtracking
# -----------------------------
def knapsack_recursive(items, capacity, n):
    # Base case: no items or zero capacity
    if n == 0 or capacity == 0:
        return 0
    value, weight = items[n - 1]

    # If weight exceeds capacity, skip the item
    if weight > capacity:
        return knapsack_recursive(items, capacity, n - 1)
    else:
        # Include or exclude the item and take max
        include = value + knapsack_recursive(items, capacity - weight, n - 1)
        exclude = knapsack_recursive(items, capacity, n - 1)
        return max(include, exclude)

# -----------------------------
# Dynamic Programming (Bottom-Up)
# -----------------------------
def knapsack_dp(items, capacity):
    n = len(items)
    table = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build DP table iteratively
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            value, weight = items[i - 1]
            if weight <= w:
                table[i][w] = max(value + table[i - 1][w - weight], table[i - 1][w])
            else:
                table[i][w] = table[i - 1][w]

    return table[n][capacity], table

# -----------------------------
# Helper: print table subset for visualization
# -----------------------------
def print_table(table, items, capacity):
    n = len(items)
    print("\nPartial DP Table (top-left 6x6 section):")
    for i in range(min(6, n + 1)):
        print(table[i][:min(6, capacity + 1)])

# -----------------------------
# Main Execution Block
# -----------------------------
if __name__ == "__main__":
    # Generate sample dataset
    num_items = 10
    capacity = 50
    items = generate_dataset(num_items)

    print("=== Figure 1: Initial Dataset and Capacity Constraints ===")
    for i, (v, w) in enumerate(items, start=1):
        print(f"Item {i}: Value={v}, Weight={w}")
    print(f"Capacity Limit: {capacity}\n")

    # --- Recursive Backtracking Test ---
    print("=== Figure 2: Recursive Backtracking Results ===")
    start_time = time.time()
    best_value_recursive = knapsack_recursive(items, capacity, len(items))
    recursive_time = time.time() - start_time
    print(f"Optimal value (Recursive): {best_value_recursive}")
    print(f"Execution time: {recursive_time:.4f} seconds\n")

    # --- Dynamic Programming Test ---
    print("=== Figure 3: Dynamic-Programming Results ===")
    start_time = time.time()
    best_value_dp, dp_table = knapsack_dp(items, capacity)
    dp_time = time.time() - start_time
    print(f"Optimal value (DP): {best_value_dp}")
    print(f"Execution time: {dp_time:.4f} seconds")
    print_table(dp_table, items, capacity)

    # Comparative Summary
    print("\n--- Summary ---")
    print(f"Recursive Time: {recursive_time:.4f}s")
    print(f"Dynamic Programming Time: {dp_time:.4f}s")
    print("DP algorithm is significantly faster and scalable for larger inputs.")
