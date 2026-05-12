"""
B3: Dijkstra's Algorithm and Bellman-Ford Comparison
Dataset: data/roads.csv (non-negative weights)
- Dijkstra: O((V+E) log V) with a binary min-heap
- Bellman-Ford: O(VE), handles negative weights, detects negative cycles
"""
import csv
import os
import heapq
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'roads.csv')


def load_graph(filepath):
    graph = defaultdict(list)
    edges = []
    vertices = set()
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row['source'].strip()
            v = row['destination'].strip()
            w = int(row['weight'])
            graph[u].append((v, w))
            edges.append((u, v, w))
            vertices.add(u)
            vertices.add(v)
    return dict(graph), edges, sorted(vertices)


# ---------------------------------------------------------------------------
# Dijkstra's algorithm
# Correctness assumption: all edge weights >= 0.
# ---------------------------------------------------------------------------
def dijkstra(graph, vertices, source):
    dist = {v: float('inf') for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0
    pq = [(0, source)]     # (tentative distance, vertex)

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:    # stale entry in the heap
            continue
        for v, w in graph.get(u, []):
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                parent[v] = u
                heapq.heappush(pq, (new_dist, v))

    return dist, parent


# ---------------------------------------------------------------------------
# Bellman-Ford algorithm
# Correctness: works with negative weights; detects negative-weight cycles.
# Runs |V|-1 relaxation passes; one extra pass to detect negative cycles.
# ---------------------------------------------------------------------------
def bellman_ford(edges, vertices, source):
    dist = {v: float('inf') for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0

    n = len(vertices)
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True
        if not updated:    # converged early
            break

    # Extra pass: any further relaxation implies a negative cycle.
    has_neg_cycle = False
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            has_neg_cycle = True
            break

    return dist, parent, has_neg_cycle


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------
def reconstruct_path(parent, source, target):
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path if (path and path[0] == source) else None


def print_results(label, dist, parent, vertices, source):
    print(f"\n{label} – shortest paths from '{source}':")
    print(f"  {'Target':<10} {'Distance':<12} Path")
    print("  " + "-" * 50)
    for v in vertices:
        d = dist[v]
        d_str = str(d) if d != float('inf') else 'inf'
        path = reconstruct_path(parent, source, v)
        path_str = " -> ".join(path) if path else "unreachable"
        print(f"  {v:<10} {d_str:<12} {path_str}")


def main():
    graph, edges, vertices = load_graph(DATA_FILE)
    source = 'A'

    dist_d, parent_d = dijkstra(graph, vertices, source)
    print_results("Dijkstra", dist_d, parent_d, vertices, source)

    dist_b, parent_b, neg_cycle = bellman_ford(edges, vertices, source)
    print_results("Bellman-Ford", dist_b, parent_b, vertices, source)
    print(f"\n  Negative cycle detected: {neg_cycle}")

    print("\n" + "=" * 55)
    print("Discussion:")
    print("  Both algorithms yield identical results (all weights >= 0).")
    print("  Dijkstra:     O((V+E) log V) – greedy, requires non-negative weights.")
    print("  Bellman-Ford: O(VE)          – handles negative weights and detects")
    print("                                 negative cycles via one extra relaxation pass.")
    print("  Prefer Dijkstra for large sparse graphs without negative weights.")
    print("  Prefer Bellman-Ford when negative weights or cycle detection is needed.")


if __name__ == '__main__':
    main()
