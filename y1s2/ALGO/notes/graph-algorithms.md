# Graph Algorithms

## Graph Representations

**Adjacency List:** Array of lists. Space O(V + E). Good for sparse graphs.
**Adjacency Matrix:** V×V matrix. Space O(V²). O(1) edge lookup; good for dense graphs.

---

## BFS — Breadth-First Search

Explores vertices in layers (by hop distance from source).

```python
from collections import deque

def bfs(graph, source):
    dist = {v: -1 for v in graph}
    parent = {v: None for v in graph}
    dist[source] = 0
    queue = deque([source])

    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)

    return dist, parent
```

**Complexity:** O(V + E)

**Applications:**
- Shortest path in unweighted graph
- Level-order traversal
- Bipartite graph detection
- Connected components

---

## DFS — Depth-First Search

Explores as deep as possible before backtracking.

```python
def dfs(graph, source, visited=None, order=None):
    if visited is None: visited = set()
    if order is None: order = []
    visited.add(source)
    for v in graph[source]:
        if v not in visited:
            dfs(graph, v, visited, order)
    order.append(source)  # post-order = reverse topological sort
    return order
```

**Timestamps:** Discovery time `d[v]` and finish time `f[v]` allow classification
of edges:
- Tree edge: `d[u] < d[v] < f[v] < f[u]`
- Back edge: v is ancestor of u (indicates cycle in directed graph)
- Forward edge: u is ancestor of v but not tree edge (directed only)
- Cross edge: all other cases

**Applications:**
- Topological sort (reverse finish order in DAG)
- Strongly connected components (Kosaraju's / Tarjan's)
- Cycle detection
- Articulation points, bridges

---

## Single-Source Shortest Paths

### Dijkstra's Algorithm

**Assumption:** Non-negative edge weights.

```python
import heapq

def dijkstra(graph, source):
    dist = {v: float('inf') for v in graph}
    dist[source] = 0
    parent = {v: None for v in graph}
    pq = [(0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue  # stale entry
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    return dist, parent
```

**Complexity:** O((V + E) log V) with binary heap.

**Why it fails with negative edges:** A later-discovered shorter path via a negative
edge could improve already-settled vertices.

### Bellman-Ford

Handles negative edges; detects negative cycles.

```python
def bellman_ford(vertices, edges, source):
    dist = {v: float('inf') for v in vertices}
    dist[source] = 0

    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Detect negative cycle
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None  # negative cycle exists

    return dist
```

**Complexity:** O(VE)

---

## All-Pairs Shortest Paths

### Floyd-Warshall

Dynamic programming on intermediate vertices.

```python
def floyd_warshall(n, edges):
    INF = float('inf')
    dist = [[INF]*n for _ in range(n)]
    for i in range(n): dist[i][i] = 0
    for u, v, w in edges: dist[u][v] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist
```

**Recurrence:** `d[i][j][k] = min(d[i][j][k-1], d[i][k][k-1] + d[k][j][k-1])`

**Complexity:** O(V³). Detects negative cycles: if `dist[i][i] < 0` for any i.

---

## Minimum Spanning Tree

Given a connected undirected graph with edge weights, find a spanning tree
(connects all V vertices) with minimum total edge weight.

**Key property (Cut property):** For any cut (S, V−S), the minimum weight edge
crossing the cut belongs to some MST.

### Prim's Algorithm

Grows MST from a starting vertex, always adding the cheapest edge connecting
the tree to a non-tree vertex.

```python
import heapq

def prim(graph, source):
    in_mst = set()
    key = {v: float('inf') for v in graph}
    parent = {v: None for v in graph}
    key[source] = 0
    pq = [(0, source)]

    while pq:
        cost, u = heapq.heappop(pq)
        if u in in_mst: continue
        in_mst.add(u)
        for v, w in graph[u]:
            if v not in in_mst and w < key[v]:
                key[v] = w
                parent[v] = u
                heapq.heappush(pq, (w, v))

    return parent
```

**Complexity:** O(E log V) with binary heap.

### Kruskal's Algorithm

Sort all edges by weight; greedily add edges that don't form a cycle (union-find).

```python
def kruskal(vertices, edges):
    parent = {v: v for v in vertices}
    rank = {v: 0 for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry: return False
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    mst = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if union(u, v):
            mst.append((u, v, w))

    return mst
```

**Complexity:** O(E log E) = O(E log V).

---

## Dynamic Programming: Weighted Interval Scheduling

Given n jobs with start times sᵢ, finish times fᵢ, and weights wᵢ, find the
maximum-weight subset of non-overlapping jobs.

```python
def weighted_interval_scheduling(jobs):
    jobs.sort(key=lambda j: j.finish)
    n = len(jobs)

    # p[i] = latest job that finishes before job i starts
    p = [0] * n
    for i in range(n):
        for j in range(i-1, -1, -1):
            if jobs[j].finish <= jobs[i].start:
                p[i] = j + 1  # 1-indexed, 0 = no compatible job
                break

    # dp[i] = max weight using jobs 1..i
    dp = [0] * (n+1)
    for i in range(1, n+1):
        dp[i] = max(dp[i-1], jobs[i-1].weight + dp[p[i-1]])

    return dp[n]
```

**Complexity:** O(n log n) for sorting + O(n log n) for binary search in p computation.
