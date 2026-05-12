class _ITNode:
    __slots__ = ("low", "high", "data", "max_high", "left", "right")

    def __init__(self, low, high, data):
        self.low = low
        self.high = high
        self.data = data
        self.max_high = high
        self.left = None
        self.right = None


class IntervalTree:
    """Augmented BST keyed on interval start. Supports point queries in O(log n + k)."""

    def __init__(self):
        self._root = None

    def insert(self, low: int, high: int, data):
        self._root = self._insert(self._root, low, high, data)

    def _insert(self, node, low, high, data):
        if node is None:
            return _ITNode(low, high, data)
        if low < node.low:
            node.left = self._insert(node.left, low, high, data)
        else:
            node.right = self._insert(node.right, low, high, data)
        node.max_high = max(node.high,
                            node.left.max_high if node.left else 0,
                            node.right.max_high if node.right else 0)
        return node

    def query_open_at(self, time: int) -> list:
        result = []
        self._query(self._root, time, result)
        return result

    def _query(self, node, time, result):
        if node is None:
            return
        if node.max_high <= time:
            return
        self._query(node.left, time, result)
        if node.low <= time < node.high:
            result.append(node.data)
        self._query(node.right, time, result)


class BinaryMaxHeap:
    """Array-based max-heap storing (score, data) pairs."""

    def __init__(self):
        self._heap: list[tuple[float, object]] = []

    def push(self, score: float, data):
        self._heap.append((score, data))
        self._bubble_up(len(self._heap) - 1)

    def pop(self):
        if not self._heap:
            return None
        self._heap[0], self._heap[-1] = self._heap[-1], self._heap[0]
        score, data = self._heap.pop()
        if self._heap:
            self._bubble_down(0)
        return data

    def peek(self):
        return self._heap[0][1] if self._heap else None

    def __len__(self):
        return len(self._heap)

    def _bubble_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._heap[i][0] > self._heap[parent][0]:
                self._heap[i], self._heap[parent] = self._heap[parent], self._heap[i]
                i = parent
            else:
                break

    def _bubble_down(self, i):
        n = len(self._heap)
        while True:
            left, right, largest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._heap[left][0] > self._heap[largest][0]:
                largest = left
            if right < n and self._heap[right][0] > self._heap[largest][0]:
                largest = right
            if largest == i:
                break
            self._heap[i], self._heap[largest] = self._heap[largest], self._heap[i]
            i = largest
