given array A

partitioning process 
----

p = start idx of a side
r = high idx of a side

A 
=> A[p, q-1] # low side
=> pivot A[q] # pivot
=> A[q+1, r] # high side

QS(A, p, r):
	if p < r:
		q = PART(A, p, r)
		QS(A, p, q-1)
 		QS(A, q+1, r)

PART(A, p, r):
	
	x = A[r] # the pivot is the last element
	i = p-1 # start from the left end of the subarray
	for j = p to r-1: # iterate from left end to except the pivot
		if A[j] <= x # does A[j] belong to the low side
			i = i+1
			A[i] = A[j]
	A[i+1] = A[r]
	return i+1


BEST CASE -> pivot is always at middle
			





