# Sorting Algorithms

## Comparison-Based Lower Bound

Any comparison-based sorting algorithm requires **Ω(n log n)** comparisons in the worst case.
Proof: Decision tree has n! leaves; tree of height h has at most 2^h leaves → h ≥ log₂(n!) = Ω(n log n).

---

## O(n²) Algorithms

### Insertion Sort

```python
def insertion_sort(A):
    for i in range(1, len(A)):
        key = A[i]
        j = i - 1
        while j >= 0 and A[j] > key:
            A[j+1] = A[j]
            j -= 1
        A[j+1] = key
```

- **Best case:** O(n) — already sorted
- **Worst case:** O(n²) — reverse sorted
- **In-place, stable**
- Efficient for small n or nearly-sorted arrays

---

## O(n log n) Algorithms

### Merge Sort

```python
def merge_sort(A):
    if len(A) <= 1:
        return A
    mid = len(A) // 2
    L = merge_sort(A[:mid])
    R = merge_sort(A[mid:])
    return merge(L, R)

def merge(L, R):
    result, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            result.append(L[i]); i += 1
        else:
            result.append(R[j]); j += 1
    return result + L[i:] + R[j:]
```

**Recurrence:** T(n) = 2T(n/2) + Θ(n) → T(n) = Θ(n log n) (Master Theorem Case 2)

- **All cases:** Θ(n log n)
- **Stable, not in-place** (O(n) auxiliary space)

### Heap Sort

1. Build a max-heap: O(n)
2. Repeatedly extract max and place at end: n × O(log n) = O(n log n)

```python
def heapify(A, n, i):
    largest = i
    l, r = 2*i+1, 2*i+2
    if l < n and A[l] > A[largest]: largest = l
    if r < n and A[r] > A[largest]: largest = r
    if largest != i:
        A[i], A[largest] = A[largest], A[i]
        heapify(A, n, largest)

def heap_sort(A):
    n = len(A)
    for i in range(n//2 - 1, -1, -1):
        heapify(A, n, i)
    for i in range(n-1, 0, -1):
        A[0], A[i] = A[i], A[0]
        heapify(A, i, 0)
```

- **All cases:** Θ(n log n)
- **In-place, not stable**

### Quicksort

```python
def quicksort(A, p, r):
    if p < r:
        q = partition(A, p, r)
        quicksort(A, p, q-1)
        quicksort(A, q+1, r)

def partition(A, p, r):
    pivot = A[r]            # last element as pivot
    i = p - 1
    for j in range(p, r):
        if A[j] <= pivot:
            i += 1
            A[i], A[j] = A[j], A[i]
    A[i+1], A[r] = A[r], A[i+1]
    return i + 1
```

**Recurrences:**
- **Best / Average:** T(n) = 2T(n/2) + Θ(n) → Θ(n log n)
- **Worst case** (already sorted, last-element pivot): T(n) = T(n-1) + Θ(n) → Θ(n²)

**Mitigations:** Random pivot selection; median-of-three pivot.

- **In-place, not stable** (standard version)
- Average performance is excellent in practice (small constants)

---

## Linear-Time Sorting (Non-Comparison)

These algorithms beat the Ω(n log n) barrier by exploiting structure in the keys.

### Counting Sort

**Assumption:** Keys are integers in range [0, k].

```python
def counting_sort(A, k):
    C = [0] * (k+1)
    for x in A: C[x] += 1
    for i in range(1, k+1): C[i] += C[i-1]  # cumulative
    B = [0] * len(A)
    for x in reversed(A):
        B[C[x]-1] = x
        C[x] -= 1
    return B
```

**Complexity:** Θ(n + k). **Stable.** Use when k = O(n).

### Radix Sort

Sort by least significant digit first, using a stable sort (counting sort) at each pass.

**Complexity:** Θ(d(n + k)) where d = number of digits, k = radix.

For n numbers each with at most b bits: use r-bit digits → d = b/r passes, k = 2^r.
Optimal r = log₂ n gives Θ(bn / log n).

### Bucket Sort

**Assumption:** Input is uniformly distributed in [0, 1).

1. Create n buckets for subranges of [0,1).
2. Scatter each element into its bucket.
3. Sort each bucket (insertion sort).
4. Concatenate buckets.

**Expected complexity:** Θ(n) when input is uniform.

---

## Master Theorem

For recurrences of the form T(n) = aT(n/b) + f(n):

Let `p = log_b(a)`:

| Case | Condition | Solution |
|------|-----------|---------|
| 1 | f(n) = O(n^(p−ε)) | T(n) = Θ(n^p) |
| 2 | f(n) = Θ(n^p) | T(n) = Θ(n^p log n) |
| 3 | f(n) = Ω(n^(p+ε)) and regularity holds | T(n) = Θ(f(n)) |

**Examples:**
- Merge sort: a=2, b=2, p=1, f=Θ(n) → Case 2 → Θ(n log n)
- Binary search: a=1, b=2, p=0, f=Θ(1) → Case 2 → Θ(log n)
- Strassen's matrix multiply: a=7, b=2, p=log₂7≈2.81, f=Θ(n²) → Case 1 → Θ(n^2.81)
