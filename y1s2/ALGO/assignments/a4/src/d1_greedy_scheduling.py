"""
D1: Greedy Interval Scheduling – maximise the NUMBER of non-overlapping jobs.
Dataset: data/jobs.csv
Strategy: sort by finish time (earliest-deadline-first), greedily accept
a job whenever it does not overlap with the last accepted job.
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


def greedy_interval_scheduling(jobs):
    """
    Classic earliest-finish-time greedy for interval scheduling.
    Two jobs i, j are compatible if start_j >= finish_i.
    Returns the selected jobs in finish-time order.
    """
    sorted_jobs = sorted(jobs, key=lambda j: j['finish'])
    selected = []
    last_finish = -1    # sentinel: no job selected yet

    for job in sorted_jobs:
        if job['start'] >= last_finish:
            selected.append(job)
            last_finish = job['finish']

    return selected


def main():
    jobs = load_jobs(DATA_FILE)

    sorted_jobs = sorted(jobs, key=lambda j: j['finish'])
    print("Greedy Interval Scheduling  (maximize job count)")
    print("=" * 52)
    print("\nAll jobs sorted by finish time:")
    print(f"  {'Job':<8} {'Start':<8} {'Finish':<8} {'Reward'}")
    print("  " + "-" * 36)
    for j in sorted_jobs:
        print(f"  {j['id']:<8} {j['start']:<8} {j['finish']:<8} {j['reward']}")

    selected = greedy_interval_scheduling(jobs)
    total_reward = sum(j['reward'] for j in selected)

    print(f"\nSelected jobs ({len(selected)} non-overlapping):")
    print(f"  {'Job':<8} {'Start':<8} {'Finish':<8} {'Reward'}")
    print("  " + "-" * 36)
    for j in selected:
        print(f"  {j['id']:<8} {j['start']:<8} {j['finish']:<8} {j['reward']}")
    print(f"\n  Jobs selected : {len(selected)}")
    print(f"  Total reward  : {total_reward}  (not the optimisation objective here)")


if __name__ == '__main__':
    main()
