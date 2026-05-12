## Proof Techniques

### Proof by CounterExample

**Claim: In Greedy Approach, SD always provide the optimal solution**

Suppose SD always provide the optimal solution

Therefore, using SD yields a max subarray of non-overlapping intervals

Using this as an example:

## Proof Techniques

### Proof by CounterExample

**Claim: In Greedy Approach, SD always provide the optimal solution**

Suppose SD always provide the optimal solution

Therefore, using SD yields a max subarray of non-overlapping intervals

Using this as an example for intervals: <br>
<img src="./asset/intervals.png" width="300px">

~~Using EST: - A, G~~ # not necessary

Using EFT (the optimal solution): - B, E, H

Using SD: - C, H

By the counter example:

SD did not yield the max subarray

this is a contradiction, therefore, the claim is false

Note: EST - sort the intervals asc by the min start time EFT - sort the
intervals asc by the min finish time SD - sort the intervals asc by the (F - S)

### Proof By Induction

Idea:
base case: n
suppose (IH): it is true for n = k
then by IH: it must also be true for n = k+1

Example 1: Proof by induction that the sum of Natural Numbers
is n(n+1)/2
```
let n = 1, then by the given formula, n(n+1)/2 yields 1
suppose this is true for n=k where k >= n, therefore k(k+1)/2
S => 1 + 2 + ... + k = k(k+1)/2

then by inductive hypothesis, the statement must also be true for n = k+1

1 + 2 + ... + k + (k+1) = k(k+1)/2 + (k+1)

substituting S, we get;

k(k+1)/2 + (k+1) = (k+1+1)/2 + (k+1)
....
LHS = RHS

therefore, the statement holds for n=k+1
```
Example 2: Proof by induction the function for fibonacci number is
```
func Fib(n int) int {
if n == 0 { return 0 }
if n == 1 { return 1 }
return Fib(n-1) + Fib(n-2) }
```
Base Cases
Case n=0 => F(0)=0 by definition.

Case n=1 => F(1)=1 by definition.

IH:
Assume that for all k
... SOMETHING? FIGURE IT OUT ...


