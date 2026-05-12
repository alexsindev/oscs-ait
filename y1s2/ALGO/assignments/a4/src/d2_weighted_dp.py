"""
D2: Weighted Interval Scheduling – maximise total REWARD via Dynamic Programming.
Dataset: data/jobs.csv

Recurrence (Kleinberg & Tardos formulation):
    OPT(0) = 0
    OPT(j) = max( reward_j + OPT(p(j)),  OPT(j-1) )

where jobs are sorted by finish time (1-indexed), and p(j) is the index of
the latest job that finishes no later than job j starts (0 if none).
"""
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'jobs.csv')


def load_jobs(filepath):
    jobs = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append({
                'id':     row['job_id'].strip(),
                'start':  int(row['start']),
                'finish': int(row['finish']),
                'reward': int(row['reward']),
            })
    return jobs


def compute_predecessors(jobs):
    """
    For each job j (0-indexed in the sorted list), find the largest index i < j
    such that jobs[i]['finish'] <= jobs[j]['start'].
    Returns -1 when no such predecessor exists.
    """
    n = len(jobs)
    p = [-1] * n
    for j in range(n):
        for i in range(j - 1, -1, -1):
            if jobs[i]['finish'] <= jobs[j]['start']:
                p[j] = i
                break
    return p


def weighted_interval_scheduling(jobs):
    """
    Bottom-up DP for weighted interval scheduling.
    Returns (max_reward, selected_jobs, dp_table, sorted_jobs, predecessors).
    """
    jobs_sorted = sorted(jobs, key=lambda j: j['finish'])
    n = len(jobs_sorted)
    p = compute_predecessors(jobs_sorted)

    # dp[j]: maximum reward using jobs from the first j candidates (1-indexed).
    # dp[0] = 0 (base case: no jobs available).
    dp = [0] * (n + 1)
    for j in range(1, n + 1):
        job = jobs_sorted[j - 1]
        pred_dp_idx = p[j - 1] + 1    # p is 0-indexed; shift to 1-indexed dp table
        include_val = job['reward'] + dp[pred_dp_idx]
        exclude_val = dp[j - 1]
        dp[j] = max(include_val, exclude_val)

    # ---- Reconstruction ----
    selected = []
    j = n
    while j >= 1:
        job = jobs_sorted[j - 1]
        pred_dp_idx = p[j - 1] + 1
        include_val = job['reward'] + dp[pred_dp_idx]
        if include_val >= dp[j - 1]:
            selected.append(job)
            j = pred_dp_idx            # jump past the selected job's predecessor
        else:
            j -= 1
    selected.reverse()

    return dp[n], selected, dp, jobs_sorted, p


def main():
    jobs = load_jobs(DATA_FILE)
    max_reward, selected, dp, jobs_sorted, p = weighted_interval_scheduling(jobs)
    n = len(jobs_sorted)

    print("Weighted Interval Scheduling  (Dynamic Programming)")
    print("=" * 56)

    # ---- Job table with predecessor column ----
    print("\nJobs sorted by finish time (p uses 1-based indexing, 0 = none):")
    print(f"  {'j':<5} {'Job':<8} {'Start':<8} {'Finish':<8} {'Reward':<8} p(j)")
    print("  " + "-" * 48)
    for j in range(n):
        job = jobs_sorted[j]
        pred_display = p[j] + 1     # convert to 1-based for readability (0 = none)
        print(f"  {j+1:<5} {job['id']:<8} {job['start']:<8} {job['finish']:<8} {job['reward']:<8} {pred_display}")

    print("\nRecurrence:")
    print("  OPT(0) = 0")
    print("  OPT(j) = max( reward_j + OPT(p(j)),  OPT(j-1) )")

    # ---- DP table ----
    print("\nDP table:")
    print(f"  {'j':<6} OPT(j)")
    print("  " + "-" * 14)
    for j in range(n + 1):
        print(f"  {j:<6} {dp[j]}")

    # ---- Result ----
    print(f"\nMaximum total reward: {max_reward}")
    print(f"\nSelected jobs:")
    print(f"  {'Job':<8} {'Start':<8} {'Finish':<8} {'Reward'}")
    print("  " + "-" * 36)
    for job in selected:
        print(f"  {job['id']:<8} {job['start']:<8} {job['finish']:<8} {job['reward']}")
    print(f"\n  Total reward: {sum(j['reward'] for j in selected)}")


if __name__ == '__main__':
    main()
