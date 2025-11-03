# dijkstra_delivery.py
# Author: Justan E. Dunn
# Date: 2025-10-19
# Purpose: Dijkstra shortest-path routing for food delivery with simulated traffic updates.

import heapq
from collections import defaultdict

class CityGraph:
    def __init__(self):
        # adjacency list: node -> list[(neighbor, weight)]
        self.adj = defaultdict(list)
        # store edges for easy updates (u, v) -> weight
        self.edge_w = {}

    def add_edge(self, u, v, w, bidirectional=True):
        # non-negative weights (travel time in minutes)
        if w < 0:
            raise ValueError("Edge weight must be non-negative for Dijkstra.")
        self.adj[u].append((v, w))
        self.edge_w[(u, v)] = w
        if bidirectional:
            self.adj[v].append((u, w))
            self.edge_w[(v, u)] = w

    def update_edge(self, u, v, new_w):
        """Update edge weight to simulate traffic (idempotent: set, not multiply)."""
        if (u, v) not in self.edge_w:
            raise KeyError(f"Edge {(u, v)} not found")
        if new_w < 0:
            raise ValueError("Edge weight must be non-negative.")
        # Write to map
        self.edge_w[(u, v)] = new_w
        # Write to adjacency list
        nbrs = self.adj[u]
        for i, (nbr, w) in enumerate(nbrs):
            if nbr == v:
                nbrs[i] = (v, new_w)
                break

    def dijkstra(self, source, target=None):
        """Return (dist, prev) where dist[x] is min distance. If target, early stop."""
        dist = {node: float("inf") for node in self.adj.keys()}
        prev = {}
        dist[source] = 0.0
        pq = [(0.0, source)]
        visited = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if target is not None and u == target:
                break  # early stop once target finalized

            for v, w in self.adj[u]:
                alt = d + w
                if alt < dist.get(v, float("inf")):
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))
        return dist, prev

    @staticmethod
    def path(prev, source, target):
        if target not in prev and source != target:
            # no path discovered
            return []
        cur = target
        seq = [cur]
        while cur != source:
            if cur not in prev:
                return []
            cur = prev[cur]
            seq.append(cur)
        seq.reverse()
        return seq

def demo():
    g = CityGraph()
    # Graph: intersections A..G. Weights ~ minutes.
    edges = [
        ("A","B",4), ("A","C",2),
        ("B","D",5), ("C","D",1), ("C","E",7),
        ("D","F",3), ("E","F",2), ("F","G",4)
    ]
    for u, v, w in edges:
        g.add_edge(u, v, w, bidirectional=True)

    source, target = "A", "G"

    print("=== FIGURE 1: Baseline Graph & Shortest Path (No Congestion) ===")
    print("Edges (u -> v : weight):")
    for (u, v), w in sorted(g.edge_w.items()):
        if u < v:  # print each undirected edge once
            print(f"  {u} <-> {v} : {w}")
    dist, prev = g.dijkstra(source, target)
    path = g.path(prev, source, target)
    print(f"\nShortest path {source} -> {target}: {path} (cost: {dist[target]:.1f} min)")

    # Simulate traffic: congestion on C->D and D->F, detour encouraging A->B->D->F->G or A->C->E->F->G
    print("\n=== FIGURE 2: Apply Real-Time Traffic Updates (Higher Weights) ===")
    g.update_edge("C","D",6); g.update_edge("D","C",6)  # from 1 to 6
    g.update_edge("D","F",8); g.update_edge("F","D",8)  # from 3 to 8
    for (u, v), w in sorted(g.edge_w.items()):
        if u < v:
            print(f"  {u} <-> {v} : {w}")

    print("\n=== FIGURE 3: Recomputed Shortest Path Under Traffic ===")
    dist2, prev2 = g.dijkstra(source, target)
    path2 = g.path(prev2, source, target)
    print(f"Shortest path {source} -> {target}: {path2} (cost: {dist2[target]:.1f} min)")

if __name__ == "__main__":
    demo()
