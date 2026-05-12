"""
B4: All-Pairs Shortest Paths via Floyd-Warshall
Dataset: data/roads.csv
Computes the full distance matrix, detects negative cycles, and
demonstrates path reconstruction.
"""
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'roads.csv')

INF = float('inf')


def load_graph(filepath):
    edges = []
    vertices = set()
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row['source'].strip()
            v = row['destination'].strip()
            w = int(row['weight'])
            edges.append((u, v, w))
            vertices.add(u)
            vertices.add(v)
    return edges, sorted(vertices)


def floyd_warshall(vertices, edges):
    """
    Standard Floyd-Warshall O(V^3).

    dist[i][j]  – shortest path weight from vertices[i] to vertices[j].
    nxt[i][j]   – index of the next vertex on that shortest path
                  (used for path reconstruction); None if no path.

    Negative-cycle detection: if dist[i][i] < 0 after the algorithm,
    vertex i lies on a negative cycle.
    """
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    dist = [[INF] * n for _ in range(n)]
    nxt  = [[None] * n for _ in range(n)]

    # Base case: self-loops and direct edges
    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        i, j = idx[u], idx[v]
        if w < dist[i][j]:      # keep lightest parallel edge if any
            dist[i][j] = w
            nxt[i][j]  = j     # next-hop index toward destination

    # Relaxation through intermediate vertex k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                via = dist[i][k] + dist[k][j]
                if via < dist[i][j]:
                    dist[i][j] = via
                    nxt[i][j]  = nxt[i][k]

    has_neg_cycle = any(dist[i][i] < 0 for i in range(n))
    return dist, nxt, has_neg_cycle, idx


def reconstruct_path(vertices, nxt, idx, src, dst):
    """Follow nxt pointers from src to dst."""
    i, j = idx[src], idx[dst]
    if nxt[i][j] is None:
        return None
    path = [src]
    while i != j:
        i = nxt[i][j]
        path.append(vertices[i])
    return path


def main():
    edges, vertices = load_graph(DATA_FILE)
    dist, nxt, has_neg_cycle, idx = floyd_warshall(vertices, edges)
    n = len(vertices)

    print("Floyd-Warshall All-Pairs Shortest Paths")
    print("=" * 50)
    print(f"Negative cycle detected: {has_neg_cycle}")

    # ---- Distance matrix ----
    print("\nDistance matrix (INF = no path):")
    col_w = 8
    header = " " * 5 + "".join(f"{v:>{col_w}}" for v in vertices)
    print(header)
    for i, u in enumerate(vertices):
        row = f"{u:>4} "
        for j in range(n):
            cell = "INF" if dist[i][j] == INF else str(dist[i][j])
            row += f"{cell:>{col_w}}"
        print(row)

    # ---- Path reconstruction examples ----
    print("\nPath reconstruction (all reachable pairs):")
    print("-" * 48)
    for src in vertices:
        for dst in vertices:
            if src == dst:
                continue
            d = dist[idx[src]][idx[dst]]
            if d == INF:
                print(f"  {src} -> {dst}: unreachable")
            else:
                path = reconstruct_path(vertices, nxt, idx, src, dst)
                print(f"  {src} -> {dst}: dist={d}, path={' -> '.join(path)}")

    print("\nComparison with repeated single-source shortest paths:")
    print("  Floyd-Warshall O(V^3): best when V is small or the graph is dense.")
    print("  Repeated Dijkstra O(V*(V+E) log V): better for large sparse graphs")
    print("  with non-negative weights (run once per source vertex).")
    print(f"  Here V={n}, so Floyd-Warshall is equally practical.")


if __name__ == '__main__':
    main()
