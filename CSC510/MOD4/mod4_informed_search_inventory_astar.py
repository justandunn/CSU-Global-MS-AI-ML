"""
Module 4: Informed Search Heuristics with SimpleAI

Justan E Dunn
Colorado State University Global
CSC510-1: Foundations of Artificial Intelligence
Professor Joseph Issa
02/08/2026

Real-world heuristic search problem:
-----------------------------------
Inventory Reorder Planning with MOQ and Lead Time (A* Search)

HOW TO RUN / TEST (for grading)
--------------------------------
1) Install dependency once (in the same interpreter you run Python with):
     python -m pip install simpleai==0.8.2

2) Run the script:
     python CSC510_MOD4_InformedSearch_AStar_Inventory.py

3) Use these sample inputs (recommended):
   Planning horizon (days): 14
   Starting on-hand inventory (units): 30
   Daily demand (units/day): 5
   Lead time (days): 3
   MOQ (minimum order quantity, units): 20
   Max order multiples of MOQ: 3
   Fixed ordering cost per PO: 40
   Holding cost per unit per day: 0.03
   Stockout penalty per unit short: 10

Notes:
- This models a semi-structured inventory decision problem as a search over states.
- A* uses f(n) = g(n) + h(n). Here, h(n)=0 (admissible), so A* is complete and optimal
  for this defined cost model with non-negative step costs.

Reference:
- SimpleAI 0.8.2 (2018). Python Package Index. https://pypi.org/project/simpleai/

Goal:
  Plan order/wait decisions across a short horizon (e.g., 14 days) to avoid stockouts
  while minimizing total cost (ordering + holding + stockout penalty).

State representation:
  (day, on_hand, days_to_arrival, in_transit_qty)

Actions:
  - WAIT: do not place an order today
  - ORDER(q): place an order in multiples of MOQ (only if nothing is already in transit)

Transition:
  Each action advances time by 1 day, consumes daily demand, and receives in-transit
  inventory when days_to_arrival reaches 0.

Cost function:
  step_cost = ordering_cost(if order) + holding_cost * ending_on_hand + stockout_penalty * units_short

Search method:
  A* search with an admissible heuristic (0), which ensures completeness and optimality
  for this defined cost model (given non-negative step costs).

Dependency:
  pip install simpleai==0.8.2

Run:
  python mod4_informed_search_inventory_astar.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Any, Optional

from simpleai.search import SearchProblem, astar

State = Tuple[int, int, int, int]  # (day, on_hand, days_to_arrival, in_transit_qty)


@dataclass(frozen=True)
class Inputs:
    horizon_days: int
    start_on_hand: int
    daily_demand: int
    lead_time_days: int
    moq: int
    max_order_multiples: int  # e.g., 5 means max order = 5*MOQ
    order_fixed_cost: float
    holding_cost_per_unit_per_day: float
    stockout_penalty_per_unit: float


class InventoryReorderProblem(SearchProblem):
    """
    Inventory planning as a state-space search problem.
    """

    def __init__(self, inputs: Inputs):
        self.inputs = inputs
        initial_state: State = (0, inputs.start_on_hand, 0, 0)  # day 0, no shipment in transit
        super().__init__(initial_state=initial_state)

    def is_goal(self, state: State) -> bool:
        day, on_hand, days_to_arrival, in_transit = state
        # Goal: finish the planning horizon
        return day >= self.inputs.horizon_days

    def actions(self, state: State) -> List[Any]:
        day, on_hand, days_to_arrival, in_transit = state

        if day >= self.inputs.horizon_days:
            return []

        acts: List[Any] = ["WAIT"]

        # Allow at most one open shipment (keeps search tractable)
        if in_transit == 0:
            for k in range(1, self.inputs.max_order_multiples + 1):
                qty = k * self.inputs.moq
                acts.append(("ORDER", qty))

        return acts

    def result(self, state: State, action: Any) -> State:
        """
        Apply action for one day step:
          - optionally place order (starts lead-time countdown)
          - decrement days_to_arrival
          - receive shipment if countdown hits 0
          - consume daily demand
          - advance day
        """
        day, on_hand, days_to_arrival, in_transit = state
        inp = self.inputs

        # 1) Place order today (if action is ORDER)
        if isinstance(action, tuple) and action[0] == "ORDER":
            _, qty = action
            days_to_arrival = inp.lead_time_days
            in_transit = qty

        # 2) Progress lead time by one day, receive if arrives
        if in_transit > 0:
            days_to_arrival = max(0, days_to_arrival - 1)
            if days_to_arrival == 0:
                on_hand += in_transit
                in_transit = 0

        # 3) Consume demand
        on_hand_after_demand = on_hand - inp.daily_demand

        # Keep on_hand non-negative in state (shortages are captured in cost)
        on_hand_next = max(0, on_hand_after_demand)

        # 4) Advance day
        return (day + 1, on_hand_next, days_to_arrival, in_transit)

    def cost(self, state: State, action: Any, state2: State) -> float:
        """
        Step cost includes:
          - fixed ordering cost if an order is placed
          - holding cost on ending inventory (post-demand)
          - stockout penalty if demand could not be met
        """
        inp = self.inputs
        day, on_hand, days_to_arrival, in_transit = state

        # Ordering cost
        ordering_cost = 0.0
        if isinstance(action, tuple) and action[0] == "ORDER":
            ordering_cost = float(inp.order_fixed_cost)

        # Determine how much inventory is available BEFORE demand this day
        available = on_hand

        # If shipment arrives today (after decrement), it is added before demand
        if in_transit > 0:
            arriving_today = (max(0, days_to_arrival - 1) == 0)
            if arriving_today:
                available += in_transit

        units_short = max(0, inp.daily_demand - available)
        stockout_cost = float(units_short) * float(inp.stockout_penalty_per_unit)

        # Holding cost based on ending on-hand in next state
        _, on_hand_next, _, _ = state2
        holding_cost = float(on_hand_next) * float(inp.holding_cost_per_unit_per_day)

        return ordering_cost + stockout_cost + holding_cost

    def heuristic(self, state: State) -> float:
        """
        Admissible heuristic:
          Returning 0 never overestimates remaining cost, so it is admissible.
          With an admissible heuristic and non-negative costs, A* is complete and optimal
          for this defined cost model.

        Note: A tighter heuristic could reduce search effort, but must remain a valid
        lower bound on the remaining cost.
        """
        return 0.0


def _prompt_int(label: str, min_value: Optional[int] = None) -> int:
    while True:
        raw = input(f"{label}: ").strip()
        try:
            v = int(raw)
            if min_value is not None and v < min_value:
                print(f"Please enter an integer >= {min_value}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")


def _prompt_float(label: str, min_value: Optional[float] = None) -> float:
    while True:
        raw = input(f"{label}: ").strip()
        try:
            v = float(raw)
            if min_value is not None and v < min_value:
                print(f"Please enter a number >= {min_value}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid number.")


def build_inputs_interactive() -> Inputs:
    print("\nInventory Reorder Planning (A* Search) — Interactive Setup")
    print("---------------------------------------------------------")
    print("Tip: Keep the horizon small (e.g., 7–21 days) so search finishes quickly.\n")

    horizon_days = _prompt_int("Planning horizon (days)", min_value=1)
    start_on_hand = _prompt_int("Starting on-hand inventory (units)", min_value=0)
    daily_demand = _prompt_int("Daily demand (units/day)", min_value=0)
    lead_time_days = _prompt_int("Lead time (days)", min_value=0)
    moq = _prompt_int("MOQ (minimum order quantity, units)", min_value=1)
    max_order_multiples = _prompt_int("Max order multiples of MOQ (e.g., 5 means up to 5*MOQ)", min_value=1)

    order_fixed_cost = _prompt_float("Fixed ordering cost per PO (e.g., 50.0)", min_value=0.0)
    holding_cost = _prompt_float("Holding cost per unit per day (e.g., 0.05)", min_value=0.0)
    stockout_penalty = _prompt_float("Stockout penalty per unit short (e.g., 5.0)", min_value=0.0)

    return Inputs(
        horizon_days=horizon_days,
        start_on_hand=start_on_hand,
        daily_demand=daily_demand,
        lead_time_days=lead_time_days,
        moq=moq,
        max_order_multiples=max_order_multiples,
        order_fixed_cost=order_fixed_cost,
        holding_cost_per_unit_per_day=holding_cost,
        stockout_penalty_per_unit=stockout_penalty,
    )


def summarize_plan(problem: InventoryReorderProblem, result_node) -> None:
    inp = problem.inputs
    print("\nRESULTS")
    print("-------")
    if result_node is None:
        print("No solution found.")
        return

    total_cost = result_node.cost
    path_pairs = result_node.path()  # typically list of (action, state)

    print("Search algorithm: A* (simpleai.search.astar)")
    print(f"Total plan cost: {total_cost:.2f}")
    print(f"Steps (days): {inp.horizon_days}\n")

    print("Action Plan:")
    print("-----------")

    # SimpleAI commonly returns path entries as (action, state)
    for step in path_pairs:
        if not isinstance(step, (tuple, list)) or len(step) != 2:
            continue

        action, state = step[0], step[1]

        # First entry may be (None, initial_state) OR (None, None)
        if action is None or state is None:
            continue

        day, on_hand, dta, transit = state

        if action == "WAIT":
            print(f"Day {day:02d}: WAIT")
        elif isinstance(action, tuple) and len(action) == 2 and action[0] == "ORDER":
            qty = action[1]
            print(f"Day {day:02d}: ORDER {qty} units")
        else:
            print(f"Day {day:02d}: {action}")

    print("\nJustification (A*):")
    print("-------------------")
    print(
        "A* search is a complete informed search method when step costs are non-negative, "
        "and it uses an evaluation function f(n) = g(n) + h(n), where g(n) is the cost "
        "so far and h(n) is a heuristic estimate of remaining cost. In this implementation, "
        "h(n) = 0, which is admissible because it never overestimates the remaining cost. "
        "With an admissible heuristic, A* is also optimal for this defined cost model. "
        "A tradeoff is memory: A* can be space-intensive because it stores frontier nodes. "
        "For short horizons and bounded order choices (MOQ multiples), the search remains "
        "tractable and provides a clear, auditable sequence of ordering actions."
    )


def main() -> None:
    print("\nCSC510 Module 4 — Informed Search Heuristics with SimpleAI")
    print("==========================================================")
    print("This script models an inventory reorder planning problem and solves it with A*.\n")
    print("Install dependency (once):  pip install simpleai==0.8.2\n")

    inp = build_inputs_interactive()
    problem = InventoryReorderProblem(inp)

    print("\nSolving with A* search...\n")
    result_node = astar(problem, graph_search=True)

    summarize_plan(problem, result_node)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")