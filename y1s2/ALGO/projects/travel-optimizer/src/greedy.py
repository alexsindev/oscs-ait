import time
from src.models import Attraction, SolveParams, Itinerary, DayPlan, Visit
from src.data_structures import IntervalTree, BinaryMaxHeap
from src.generator import build_travel_matrix


def solve(attractions: list[Attraction], params: SolveParams, seed=None) -> Itinerary:
    t0 = time.perf_counter()

    travel, idx = build_travel_matrix(attractions, params.hotel_lat, params.hotel_lng)
    hotel_idx = len(attractions)

    tree = IntervalTree()
    for a in attractions:
        tree.insert(a.open_time, a.close_time, a.id)

    attr_map = {a.id: a for a in attractions}
    visited = set()
    days = []
    total_cost = 0.0

    for day_num in range(1, params.num_days + 1):
        current_time = params.start_time
        current_node = hotel_idx
        day_cost = 0.0
        day_sat = 0.0
        day_travel = 0
        visits = []

        while True:
            open_ids = tree.query_open_at(current_time)
            heap = BinaryMaxHeap()

            for aid in open_ids:
                if aid in visited:
                    continue
                a = attr_map[aid]
                if total_cost + a.fee > params.total_budget:
                    continue
                a_idx = idx[aid]
                travel_t = travel[current_node][a_idx]
                arrival = current_time + travel_t
                departure = arrival + a.duration
                if arrival < a.open_time or departure > a.close_time:
                    continue
                return_t = travel[a_idx][hotel_idx]
                if (departure + return_t - params.start_time) > params.daily_time_budget:
                    continue
                score = a.preference / (travel_t + a.duration + 1)
                heap.push(score, aid)

            best_id = heap.pop()
            if best_id is None:
                break

            a = attr_map[best_id]
            a_idx = idx[best_id]
            travel_t = travel[current_node][a_idx]
            arrival = current_time + travel_t
            departure = arrival + a.duration

            visits.append(Visit(a.id, a.name, arrival, departure, a.fee, a.preference, a.category))
            visited.add(best_id)
            total_cost += a.fee
            day_cost += a.fee
            day_sat += a.preference
            day_travel += travel_t
            current_time = departure
            current_node = a_idx

        days.append(DayPlan(day_num, visits, day_sat, day_cost, day_travel))

    total_sat = sum(d.total_satisfaction for d in days)
    total_attr = sum(len(d.visits) for d in days)
    ms = (time.perf_counter() - t0) * 1000

    return Itinerary(days, total_sat, total_cost, total_attr, "greedy", ms)
