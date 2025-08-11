# prototype_flow.py

from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class Page:
    name: str

# Define pages in prototype
PAGES: List[Page] = [
    Page("Home"),
    Page("Lists View"),
    Page("Items View"),
    Page("Add/Edit Item"),
    Page("Settings"),
]

# Define directed transitions (source -> target)
FLOW: List[Tuple[str, str]] = [
    ("Home", "Lists View"),
    ("Home", "Settings"),
    ("Lists View", "Items View"),
    ("Items View", "Add/Edit Item"),
    ("Items View", "Settings"),
    ("Add/Edit Item", "Items View"),  # after save/cancel, return to list
    ("Items View", "Share/Export (OS Sheet)"),
]

def page_names() -> List[str]:
    return [p.name for p in PAGES]

def print_summary():
    names = page_names()
    print("=== Mobile App Paper Prototype ===\n")
    print(f"Total Pages in Prototype: {len(names)}\n")
    print("Pages:")
    for i, n in enumerate(names, 1):
        print(f"  {i}. {n}")

    print("\nNavigation Flow (edges):")
    for i, (src, dst) in enumerate(FLOW, 1):
        print(f"  {i}. {src} → {dst}")

    # Optional: linear “happy path”
    happy_path = ["Home", "Lists View", "Items View", "Add/Edit Item", "Items View"]
    print("\nHappy Path:")
    print("  " + " → ".join(happy_path))

if __name__ == "__main__":
    print_summary()
