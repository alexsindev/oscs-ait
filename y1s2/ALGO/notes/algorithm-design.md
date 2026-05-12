## Algorithm Design and Analysis

### FORMAL DEFINITION
- a procedure to accomplish a task
- an algorithm must solve a general, well-specified problem
- specified by defining the complete set of instances it must work on

### Problem vs. Instance of Problem

Problem: Sorting
Input: A sequence of n keys a1, ... an
Output: The permutation (reordering) of the input sequence such that a1' <= a2' <= ... <= an-1' <= an'

Insertion Sort Algorithm

insertion_sort(item s[], int n) 
{
    int i, j;
    for (i = 1; i < n; i++) {
        j = i
        while ((j > 0) && (s[j] < s[j-1])) {
            swap(&s[j], &s[j-1]);
            j = j-1
        }
    }
}

### Desirable Property of Algorithms
- correct
- efficient
- easy to implement

#### Correctness
Correct algorithms often come with a proof of correctness.
Explanations of why we know that the algorithm must take every instance
of the problem to the desired result.
"It's obvious init?" never suffices as a proof of correctness, and it is
usually flat out wrong

##### Robot Tour Optimization
- Gist: Robots that solder need to know how to proceed between the first contact point
to the last, then returns to the first contact point for the subsequent board. It is
its only job. We call this a tour.

- Goal: Robots are expensive, we want to find the tour that minimizes the time it takes
 to assemble the circuit board. A reasonable assumption is that the robot arm moves with
 fixed speed. So time to travel between two points is proportional to their distance
 > distance > time

Problem: Robot Tour Optimization
Input: A set S of n points in the plane
Output: What is the shortest cycle tour that visits each point in set S

