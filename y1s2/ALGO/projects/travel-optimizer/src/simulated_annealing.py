import copy
import math
import time
import numpy as np
from src.models import Attraction, SolveParams, Itinerary, DayPlan, Visit, ConvergencePoint
from src import greedy
from src.generator import build_travel_matrix

T0 = 100.0
ALPHA = 0.9992      # ~11 500 effective iterations before T < T_MIN
T_MIN = 0.01
MAX_ITER = 15_000
WAIT_LIMIT = 45     # max minutes tourist will wait for an attraction to open

Chromosome = list[list[int]]  # day -> [attraction_ids]


def solve(attractions: list[Attraction], params: SolveParams, seed: int = 42) -> Itinerary:
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)

    travel, idx = build_travel_matrix(attractions, params.hotel_lat, params.hotel_lng)
    attr_map = {a.id: a for a in attractions}
    all_ids = [a.id for a in attractions]

    greedy_sol = greedy.solve(attractions, params)
    current = _to_chromosome(greedy_sol)
    best = copy.deepcopy(current)
    best_fit = _fitness(best, attr_map, idx, travel, params)
    current_fit = best_fit

    T = T0
    convergence = []

    for i in range(MAX_ITER):
        if T < T_MIN:
            break

        neighbor = _mutate(current, all_ids, attr_map, params, rng)
        n_fit = _fitness(neighbor, attr_map, idx, travel, params)
        dE = n_fit - current_fit

        if dE > 0 or rng.random() < math.exp(dE / T):
            current = neighbor
            current_fit = n_fit
            if current_fit > best_fit:
                best = copy.deepcopy(current)
                best_fit = current_fit

        if i % 50 == 0:
            convergence.append(ConvergencePoint(i, best_fit, T))

        T *= ALPHA

    itinerary = _build_itinerary(best, attr_map, idx, travel, params)
    itinerary.algorithm = "simulated_annealing"
    itinerary.computation_ms = (time.perf_counter() - t0) * 1000
    itinerary.convergence = convergence
    return itinerary


def _to_chromosome(itinerary: Itinerary) -> Chromosome:
    return [[v.attraction_id for v in d.visits] for d in itinerary.days]


def _fitness(chrom: Chromosome, attr_map, idx, travel, params: SolveParams) -> float:
    hotel = len(idx)
    seen = set()
    fitness = 0.0
    total_cost = 0.0

    for day_ids in chrom:
        cur_time = params.start_time
        cur_node = hotel
        for aid in day_ids:
            if aid in seen:
                continue
            a = attr_map[aid]
            travel_t = travel[cur_node][idx[aid]]
            arrival = cur_time + travel_t
            if arrival < a.open_time:
                if a.open_time - arrival > WAIT_LIMIT:
                    continue
                arrival = a.open_time
            departure = arrival + a.duration
            if departure > a.close_time:
                continue
            if total_cost + a.fee > params.total_budget:
                continue
            if (departure - params.start_time) > params.daily_time_budget:
                continue
            fitness += a.preference
            total_cost += a.fee
            seen.add(aid)
            cur_time = departure
            cur_node = idx[aid]

    return fitness


def _mutate(chrom: Chromosome, all_ids: list[int], attr_map, params, rng) -> Chromosome:
    new = copy.deepcopy(chrom)
    op = int(rng.integers(0, 6))
    if op == 0:
        _swap_within_day(new, rng)
    elif op == 1:
        _move_between_days(new, rng)
    elif op == 2:
        _insert_unvisited(new, all_ids, rng)
    elif op == 3:
        _remove_one(new, rng)
    elif op == 4:
        _replace_visit(new, all_ids, rng)
    else:
        _upgrade_visit(new, all_ids, attr_map, params, rng)
    return new


def _swap_within_day(chrom: Chromosome, rng):
    days_with_2 = [i for i, d in enumerate(chrom) if len(d) >= 2]
    if not days_with_2:
        return
    di = int(rng.choice(days_with_2))
    day = chrom[di]
    i, j = rng.choice(len(day), size=2, replace=False)
    day[i], day[j] = day[j], day[i]


def _move_between_days(chrom: Chromosome, rng):
    if len(chrom) < 2:
        return
    non_empty = [i for i, d in enumerate(chrom) if d]
    if not non_empty:
        return
    from_d = int(rng.choice(non_empty))
    to_d = int(rng.integers(0, len(chrom)))
    while to_d == from_d and len(chrom) > 1:
        to_d = int(rng.integers(0, len(chrom)))
    src_pos = int(rng.integers(0, len(chrom[from_d])))
    aid = chrom[from_d].pop(src_pos)
    ins_pos = int(rng.integers(0, len(chrom[to_d]) + 1))
    chrom[to_d].insert(ins_pos, aid)


def _insert_unvisited(chrom: Chromosome, all_ids: list[int], rng):
    visited = {aid for day in chrom for aid in day}
    unvisited = [aid for aid in all_ids if aid not in visited]
    if not unvisited or not chrom:
        return
    aid = int(rng.choice(unvisited))
    di = int(rng.integers(0, len(chrom)))
    ins_pos = int(rng.integers(0, len(chrom[di]) + 1))
    chrom[di].insert(ins_pos, aid)


def _remove_one(chrom: Chromosome, rng):
    non_empty = [i for i, d in enumerate(chrom) if d]
    if not non_empty:
        return
    di = int(rng.choice(non_empty))
    pos = int(rng.integers(0, len(chrom[di])))
    chrom[di].pop(pos)


def _replace_visit(chrom: Chromosome, all_ids: list[int], rng):
    """Replace a scheduled attraction with a random unvisited one (in-place swap)."""
    non_empty = [i for i, d in enumerate(chrom) if d]
    if not non_empty:
        return
    di = int(rng.choice(non_empty))
    pos = int(rng.integers(0, len(chrom[di])))
    visited = {aid for day in chrom for aid in day}
    unvisited = [aid for aid in all_ids if aid not in visited]
    if not unvisited:
        return
    chrom[di][pos] = int(rng.choice(unvisited))


def _upgrade_visit(chrom: Chromosome, all_ids: list[int], attr_map, params, rng):
    """Swap the lowest-preference scheduled attraction (in the first 2/3 of a day)
    with the highest-preference unvisited one that is likely open at that time.

    Prefers duration-similar replacements (within ±30 min) to avoid cascading
    budget overflows from inserting much-longer-duration attractions.
    """
    non_empty = [i for i, d in enumerate(chrom) if d]
    if not non_empty:
        return
    di = int(rng.choice(non_empty))
    day = chrom[di]
    n = len(day)
    if n == 0:
        return
    # Only consider early-to-middle positions; later positions are near day's end
    # where few new attractions are still open.
    max_pos = max(1, n * 2 // 3)
    worst_pos = min(range(max_pos), key=lambda p: attr_map[day[p]].preference)
    worst = attr_map[day[worst_pos]]
    # Estimate the clock time when the tourist reaches this position
    est_time = params.start_time + (worst_pos / n) * params.daily_time_budget
    visited = {aid for d in chrom for aid in d}
    # Candidate must have higher preference and plausibly be open at the estimated time
    candidates = [
        aid for aid in all_ids
        if aid not in visited
        and attr_map[aid].preference > worst.preference
        and attr_map[aid].open_time <= est_time + WAIT_LIMIT
        and attr_map[aid].close_time >= est_time + attr_map[aid].duration
    ]
    if not candidates:
        return
    # Prefer duration-similar candidates (±30 min) to avoid cascade budget overflows.
    # Fall back to any valid candidate if no similar-duration one exists.
    similar = [aid for aid in candidates
               if attr_map[aid].duration <= worst.duration + 30]
    pool = similar if similar else candidates
    best_id = max(pool, key=lambda aid: attr_map[aid].preference)
    chrom[di][worst_pos] = best_id


def _build_itinerary(chrom: Chromosome, attr_map, idx, travel, params: SolveParams) -> Itinerary:
    hotel = len(idx)
    days = []
    total_cost = 0.0
    seen = set()

    for day_num, day_ids in enumerate(chrom, 1):
        cur_time = params.start_time
        cur_node = hotel
        visits = []
        day_cost = 0.0
        day_sat = 0.0
        day_travel = 0

        for aid in day_ids:
            if aid in seen:
                continue
            a = attr_map[aid]
            travel_t = travel[cur_node][idx[aid]]
            arrival = cur_time + travel_t
            if arrival < a.open_time:
                if a.open_time - arrival > WAIT_LIMIT:
                    continue
                arrival = a.open_time
            departure = arrival + a.duration
            if departure > a.close_time:
                continue
            if total_cost + a.fee > params.total_budget:
                continue
            if (departure - params.start_time) > params.daily_time_budget:
                continue
            visits.append(Visit(a.id, a.name, arrival, departure, a.fee, a.preference, a.category))
            seen.add(aid)
            total_cost += a.fee
            day_cost += a.fee
            day_sat += a.preference
            day_travel += travel_t
            cur_time = departure
            cur_node = idx[aid]

        days.append(DayPlan(day_num, visits, day_sat, day_cost, day_travel))

    total_sat = sum(d.total_satisfaction for d in days)
    total_attr = sum(len(d.visits) for d in days)
    return Itinerary(days, total_sat, total_cost, total_attr, "simulated_annealing", 0.0)
