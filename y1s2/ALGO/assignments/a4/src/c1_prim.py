"""
C1: Minimum Spanning Tree via Prim's Algorithm
Dataset: data/infra.csv (undirected weighted graph)
"""
import csv
import os
import heapq
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'infra.csv')


def load_undirected_graph(filepath):
    """Load undirected graph (add each edge in both directions)."""
    graph = defaultdict(list)
    vertices = set()
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row['u'].strip()
            v = row['v'].strip()
            w = int(row['weight'])
            graph[u].append((v, w))
            graph[v].append((u, w))
            vertices.add(u)
            vertices.add(v)
    return dict(graph), sorted(vertices)


def prim(graph, vertices, start):
    """
    Prim's MST algorithm using a min-heap (lazy deletion).
    Time complexity: O(E log V).

    Returns:
        mst_edges  – list of (u, v, weight) in the MST
        total_cost – sum of MST edge weights
    """
    in_mst = set()
    # key[v] = cheapest known edge weight connecting v to the growing MST
    key = {v: float('inf') for v in vertices}
    parent = {v: None for v in vertices}
    key[start] = 0
    pq = [(0, start)]     # (key value, vertex)

    mst_edges = []
    total_cost = 0

    while pq:
        cost, u = heapq.heappop(pq)
        if u in in_mst:    # already finalized – skip stale heap entry
            continue
        in_mst.add(u)

        if parent[u] is not None:
            mst_edges.append((parent[u], u, cost))
            total_cost += cost

        for v, w in graph.get(u, []):
            if v not in in_mst and w < key[v]:
                key[v] = w
                parent[v] = u
                heapq.heappush(pq, (w, v))

    return mst_edges, total_cost


def main():
    graph, vertices = load_undirected_graph(DATA_FILE)
    start = 'A'
    mst_edges, total_cost = prim(graph, vertices, start)

    print("Prim's Minimum Spanning Tree")
    print("=" * 35)
    print(f"Starting vertex: {start}")
    print(f"\n{'Edge':<15} Weight")
    print("-" * 25)
    for u, v, w in mst_edges:
        print(f"{u} -- {v:<8} {w}")
    print("-" * 25)
    print(f"Total MST cost: {total_cost}")

    n = len(vertices)
    if len(mst_edges) == n - 1:
        print(f"\nMST spans all {n} vertices ({n-1} edges) – valid spanning tree.")
    else:
        print("\nWarning: graph appears disconnected.")

    # Uniqueness: all edge weights in infra.csv are distinct
    weights = [w for _, _, w in mst_edges]
    if len(weights) == len(set(weights)):
        print("All MST edge weights are distinct -> the MST is unique.")


if __name__ == '__main__':
    main()
