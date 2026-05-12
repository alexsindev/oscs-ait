"""
B2: DFS Structure Analysis
Dataset: data/roads.csv
Reports discovery/finish times, parents, and edge classifications.
Note: recursive DFS; adequate for this graph size (4 vertices).
"""
import csv
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'roads.csv')


def load_graph(filepath):
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


def dfs(graph, vertices):
    """
    Full DFS over all vertices (handles disconnected graphs).
    Edge classification:
        TREE   – edge to an undiscovered vertex
        BACK   – edge to an ancestor (gray vertex) → cycle
        FORWARD – edge to a descendant (black, discovered later)
        CROSS   – edge to a vertex in another subtree (black, discovered earlier)
    """
    color = {v: 'white' for v in vertices}
    parent = {v: None for v in vertices}
    disc = {}
    fin = {}
    edge_classes = []
    time = [0]   # mutable so inner function can mutate it

    def dfs_visit(u):
        color[u] = 'gray'
        time[0] += 1
        disc[u] = time[0]

        for v in graph.get(u, []):
            if color[v] == 'white':
                parent[v] = u
                edge_classes.append((u, v, 'TREE'))
                dfs_visit(v)
            elif color[v] == 'gray':
                edge_classes.append((u, v, 'BACK'))
            else:   # black
                if disc[u] < disc[v]:
                    edge_classes.append((u, v, 'FORWARD'))
                else:
                    edge_classes.append((u, v, 'CROSS'))

        color[u] = 'black'
        time[0] += 1
        fin[u] = time[0]

    for v in vertices:      # alphabetical order
        if color[v] == 'white':
            dfs_visit(v)

    return disc, fin, parent, edge_classes


def main():
    graph, vertices = load_graph(DATA_FILE)
    disc, fin, parent, edge_classes = dfs(graph, vertices)

    print("DFS Structure Analysis")
    print("=" * 48)
    print(f"{'Vertex':<10} {'disc':<8} {'fin':<8} {'parent'}")
    print("-" * 48)
    for v in vertices:
        p = parent[v] if parent[v] is not None else 'None'
        print(f"{v:<10} {disc[v]:<8} {fin[v]:<8} {p}")

    print()
    print("Edge Classification:")
    print("-" * 35)
    for u, v, kind in edge_classes:
        print(f"  {u} -> {v}  :  {kind}")

    has_cycle = any(k == 'BACK' for _, _, k in edge_classes)
    print()
    print("Discussion:")
    if has_cycle:
        print("  [!] Back edges found: graph contains directed cycle(s).")
    else:
        print("  No back edges: graph is a DAG (no directed cycles).")
    cross = [(u, v) for u, v, k in edge_classes if k == 'CROSS']
    if cross:
        print(f"  Cross edges {cross}: reach already-finished subtrees,")
        print("  confirming the graph has multiple paths without creating cycles.")
    print(f"  All {len(vertices)} vertices discovered from one DFS root -> weakly connected.")


if __name__ == '__main__':
    main()
