def QS(A, p, r):

	if p >= r: 
		return

	q = PART(A, p, r)
	QS(A, p, q-1)
	QS(A, q+1, r)

def PART(A, p, r):

	piv = A[r]
	i = p-1

	for j in range(p, r):
		if A[j] <= piv:
			i=i+1
			A[i] = A[j]

	A[i+1] = A[r]
	return i+1

A = [4,1,2,34,5,6]

QS(A, 0, len(A))

print(A)
