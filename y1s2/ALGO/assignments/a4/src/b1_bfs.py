"""
B1: Unweighted Reachability and Hop Distance via BFS
Dataset: data/roads.csv (edge weights ignored)
"""
import csv
import os
from collections import deque, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'roads.csv')


def load_unweighted_graph(filepath):
    """Load directed graph from CSV, ignoring edge weights."""
    graph = defaultdict(list)
    vertices = set()
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row['source'].strip()
            v = row['destination'].strip()
            graph[u].append(v)
            vertices.add(u)
            vertices.add(v)
    return dict(graph), sorted(vertices)


def bfs(graph, vertices, source):
    """
    Breadth-First Search from source.
    Returns:
        dist   – hop count from source (-1 = unreachable)
        parent – predecessor in BFS tree
    """
    dist = {v: -1 for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0
    queue = deque([source])

    while queue:
        u = queue.popleft()
        for v in graph.get(u, []):
            if dist[v] == -1:          # not yet visited
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)

    return dist, parent


def reconstruct_path(parent, source, target):
    """Walk parent pointers from target back to source."""
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path if (path and path[0] == source) else None


def main():
    graph, vertices = load_unweighted_graph(DATA_FILE)
    source = 'A'
    dist, parent = bfs(graph, vertices, source)

    print(f"BFS from source: {source}")
    print(f"{'Target':<10} {'Hops':<10} Path")
    print("-" * 45)
    for v in vertices:
        if dist[v] == -1:
            print(f"{v:<10} {'unreachable'}")
        else:
            path = reconstruct_path(parent, source, v)
            path_str = " -> ".join(path) if path else "N/A"
            print(f"{v:<10} {dist[v]:<10} {path_str}")


if __name__ == '__main__':
    main()
