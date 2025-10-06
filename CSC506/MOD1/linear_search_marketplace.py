# linear_search_marketplace.py
# Week 1 – Linear Search over a (simulated) online marketplace

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

@dataclass
class Item:
    id: int
    title: str
    category: str
    price: float

def linear_search(items: Iterable[Item], predicate: Callable[[Item], bool]) -> Optional[Item]:
    """
    Return the first Item for which predicate(item) is True, else None.
    Time complexity: O(n) in the number of items examined.
    Space complexity: O(1) auxiliary.
    """
    for item in items:
        if predicate(item):
            return item
    return None

# --- Optional: simulate a paginated marketplace API (realistic) ---
def paginate(items: List[Item], page_size: int) -> Iterable[List[Item]]:
    for i in range(0, len(items), page_size):
        yield items[i:i + page_size]

def linear_search_paginated(items: List[Item],
                            predicate: Callable[[Item], bool],
                            page_size: int = 5) -> Optional[Item]:
    """
    Linear search across a paginated dataset. We must visit pages in sequence
    and scan each element until we find a match, then stop.
    Still O(n) in the total number of items visited.
    """
    for page in paginate(items, page_size):
        for it in page:
            if predicate(it):
                return it
    return None

# --- Demo dataset + runs you can screenshot ---
def build_demo_data() -> List[Item]:
    return [
        Item(1, "Wireless Mouse", "Electronics", 19.99),
        Item(2, "Mechanical Keyboard", "Electronics", 79.99),
        Item(3, "Running Shoes", "Sports", 49.95),
        Item(4, "Coffee Beans 2lb", "Grocery", 16.50),
        Item(5, "USB-C Cable", "Electronics", 8.99),
        Item(6, "Yoga Mat", "Sports", 21.25),
        Item(7, "Noise-Cancelling Headphones", "Electronics", 129.00),
        Item(8, "LED Desk Lamp", "Home", 24.75),
        Item(9, "Chef Knife", "Home", 34.40),
        Item(10, "Insulated Bottle", "Outdoors", 17.49),
    ]

def pretty(item: Optional[Item]) -> str:
    return "None" if item is None else f"[id={item.id} | {item.title} | {item.category} | ${item.price:.2f}]"

if __name__ == "__main__":
    data = build_demo_data()

    print("\n=== Linear Search (simple list) ===")
    target_title = "USB-C Cable"
    result = linear_search(data, lambda it: it.title == target_title)
    print(f"Looking for exact title '{target_title}' -> {pretty(result)}")

    print("\n=== Linear Search (case-insensitive contains in title) ===")
    needle = "headphones"
    result = linear_search(data, lambda it: needle.lower() in it.title.lower())
    print(f"Looking for any title containing '{needle}' -> {pretty(result)}")

    print("\n=== Linear Search with a composite predicate ===")
    result = linear_search(
        data,
        lambda it: it.category == "Electronics" and it.price <= 25.00
    )
    print(f"Electronics item priced <= $25.00 -> {pretty(result)}")

    print("\n=== Linear Search over Paginated Dataset (page_size=4) ===")
    result = linear_search_paginated(
        data,
        predicate=lambda it: it.category == "Sports" and "Yoga" in it.title,
        page_size=4
    )
    print(f"Find 'Sports' with 'Yoga' in title -> {pretty(result)}")

    print("\nDone.")
# linear_search_marketplace.py
# Week 1 – Linear Search over a (simulated) online marketplace