import pytest
from src.models import Attraction, Location, SolveParams
from src.data_structures import IntervalTree, BinaryMaxHeap
from src import greedy, simulated_annealing
from src.verifier import verify


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_attraction(id, lat=13.756, lng=100.502, open_t=540, close_t=1020,
                    dur=60, fee=5.0, pref=0.8, cat="Museum"):
    return Attraction(id, f"Attr{id}", Location(lat, lng), open_t, close_t, dur, fee, pref, cat)


def small_set():
    return [
        make_attraction(1, 13.756, 100.502, 540, 1020, 60, 10.0, 0.9),
        make_attraction(2, 13.760, 100.505, 660, 1320, 45, 15.0, 0.8, "Restaurant"),
        make_attraction(3, 13.765, 100.510, 360, 1080, 90, 0.0, 0.7, "Park"),
        make_attraction(4, 13.770, 100.515, 480, 1140, 45, 5.0, 0.85, "Landmark"),
        make_attraction(5, 13.755, 100.508, 600, 1260, 120, 20.0, 0.75, "Shopping"),
    ]


def default_params():
    return SolveParams(num_days=2, daily_time_budget=600, total_budget=100.0,
                       start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)


# ── IntervalTree ──────────────────────────────────────────────────────────────

class TestIntervalTree:
    def test_single_interval_queried_inside(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)
        assert 1 in t.query_open_at(600)

    def test_single_interval_before_open(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)
        assert 1 not in t.query_open_at(500)

    def test_single_interval_at_open_boundary(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)
        assert 1 in t.query_open_at(540)

    def test_single_interval_at_close_boundary(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)
        assert 1 not in t.query_open_at(1020)  # [open, close) — must depart by close

    def test_multiple_intervals_partial_overlap(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)   # museum
        t.insert(660, 1320, 2)   # restaurant
        t.insert(360, 1080, 3)   # park
        result = t.query_open_at(700)
        assert set(result) == {1, 2, 3}

    def test_only_one_open(self):
        t = IntervalTree()
        t.insert(540, 1020, 1)
        t.insert(1100, 1380, 2)
        assert t.query_open_at(1050) == []

    def test_empty_tree(self):
        t = IntervalTree()
        assert t.query_open_at(600) == []

    def test_many_intervals(self):
        t = IntervalTree()
        for i in range(50):
            t.insert(i * 10, i * 10 + 100, i)
        result = t.query_open_at(500)
        assert len(result) > 0


# ── BinaryMaxHeap ─────────────────────────────────────────────────────────────

class TestBinaryMaxHeap:
    def test_single_element(self):
        h = BinaryMaxHeap()
        h.push(0.9, "a")
        assert h.pop() == "a"

    def test_max_returned_first(self):
        h = BinaryMaxHeap()
        h.push(0.5, "low")
        h.push(0.9, "high")
        h.push(0.7, "mid")
        assert h.pop() == "high"

    def test_order_of_pops(self):
        h = BinaryMaxHeap()
        scores = [0.3, 0.9, 0.1, 0.7, 0.5]
        for s in scores:
            h.push(s, s)
        extracted = []
        while len(h) > 0:
            extracted.append(h.pop())
        assert extracted == sorted(scores, reverse=True)

    def test_empty_pop_returns_none(self):
        h = BinaryMaxHeap()
        assert h.pop() is None

    def test_peek_does_not_remove(self):
        h = BinaryMaxHeap()
        h.push(0.8, "x")
        assert h.peek() == "x"
        assert len(h) == 1

    def test_len_tracks_correctly(self):
        h = BinaryMaxHeap()
        for i in range(10):
            h.push(float(i), i)
        assert len(h) == 10
        h.pop()
        assert len(h) == 9

    def test_heap_property_after_many_pushes(self):
        import random
        random.seed(0)
        h = BinaryMaxHeap()
        vals = [random.random() for _ in range(100)]
        for v in vals:
            h.push(v, v)
        prev = float("inf")
        while len(h):
            curr = h.pop()
            assert curr <= prev
            prev = curr


# ── Greedy Correctness ────────────────────────────────────────────────────────

class TestGreedy:
    def test_visits_at_least_one(self):
        result = greedy.solve(small_set(), default_params())
        assert result.total_attractions > 0

    def test_no_duplicate_visits(self):
        result = greedy.solve(small_set(), default_params())
        ids = [v.attraction_id for d in result.days for v in d.visits]
        assert len(ids) == len(set(ids))

    def test_respects_time_windows(self):
        attrs = small_set()
        attr_map = {a.id: a for a in attrs}
        result = greedy.solve(attrs, default_params())
        for day in result.days:
            for v in day.visits:
                a = attr_map[v.attraction_id]
                assert v.arrival_time >= a.open_time
                assert v.departure_time <= a.close_time

    def test_respects_total_budget(self):
        params = default_params()
        result = greedy.solve(small_set(), params)
        assert result.total_cost <= params.total_budget + 1e-6

    def test_respects_daily_time_budget(self):
        params = default_params()
        result = greedy.solve(small_set(), params)
        for day in result.days:
            if day.visits:
                elapsed = day.visits[-1].departure_time - params.start_time
                assert elapsed <= params.daily_time_budget

    def test_chronological_order(self):
        result = greedy.solve(small_set(), default_params())
        for day in result.days:
            for i in range(1, len(day.visits)):
                assert day.visits[i].arrival_time >= day.visits[i - 1].departure_time

    def test_deterministic(self):
        attrs = small_set()
        params = default_params()
        r1 = greedy.solve(attrs, params)
        r2 = greedy.solve(attrs, params)
        assert r1.total_satisfaction == r2.total_satisfaction
        assert r1.total_attractions == r2.total_attractions

    def test_zero_budget_visits_only_free(self):
        params = SolveParams(total_budget=0.0, num_days=2, daily_time_budget=600,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = greedy.solve(small_set(), params)
        for day in result.days:
            for v in day.visits:
                assert v.fee == 0.0

    def test_tight_budget(self):
        params = SolveParams(total_budget=5.0, num_days=1, daily_time_budget=600,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = greedy.solve(small_set(), params)
        assert result.total_cost <= 5.0 + 1e-6

    def test_single_day(self):
        params = SolveParams(num_days=1, daily_time_budget=600, total_budget=200.0,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = greedy.solve(small_set(), params)
        assert len(result.days) == 1

    def test_many_days(self):
        params = SolveParams(num_days=5, daily_time_budget=600, total_budget=500.0,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = greedy.solve(small_set(), params)
        assert len(result.days) == 5

    def test_passes_verifier(self):
        attrs = small_set()
        result = greedy.solve(attrs, default_params())
        ok, errors = verify(result, default_params(), attrs)
        assert ok, errors

    def test_empty_attractions(self):
        result = greedy.solve([], default_params())
        assert result.total_attractions == 0

    def test_satisfaction_sum_matches_visits(self):
        attrs = small_set()
        result = greedy.solve(attrs, default_params())
        manual = sum(v.preference for d in result.days for v in d.visits)
        assert abs(result.total_satisfaction - manual) < 1e-6


# ── SA Correctness ────────────────────────────────────────────────────────────

class TestSA:
    def test_produces_valid_itinerary(self):
        attrs = small_set()
        result = simulated_annealing.solve(attrs, default_params(), seed=42)
        ok, errors = verify(result, default_params(), attrs)
        assert ok, errors

    def test_no_duplicate_visits(self):
        result = simulated_annealing.solve(small_set(), default_params(), seed=42)
        ids = [v.attraction_id for d in result.days for v in d.visits]
        assert len(ids) == len(set(ids))

    def test_respects_total_budget(self):
        params = default_params()
        result = simulated_annealing.solve(small_set(), params, seed=42)
        assert result.total_cost <= params.total_budget + 1e-6

    def test_respects_time_windows(self):
        attrs = small_set()
        attr_map = {a.id: a for a in attrs}
        result = simulated_annealing.solve(attrs, default_params(), seed=42)
        for day in result.days:
            for v in day.visits:
                a = attr_map[v.attraction_id]
                assert v.arrival_time >= a.open_time
                assert v.departure_time <= a.close_time

    def test_sa_geq_greedy(self):
        attrs = small_set()
        params = default_params()
        g = greedy.solve(attrs, params)
        s = simulated_annealing.solve(attrs, params, seed=42)
        assert s.total_satisfaction >= g.total_satisfaction - 1e-6

    def test_seed_reproducibility(self):
        attrs = small_set()
        params = default_params()
        r1 = simulated_annealing.solve(attrs, params, seed=99)
        r2 = simulated_annealing.solve(attrs, params, seed=99)
        assert r1.total_satisfaction == r2.total_satisfaction

    def test_different_seeds_may_differ(self):
        attrs = small_set()
        params = default_params()
        r1 = simulated_annealing.solve(attrs, params, seed=1)
        r2 = simulated_annealing.solve(attrs, params, seed=9999)
        ok1, _ = verify(r1, params, attrs)
        ok2, _ = verify(r2, params, attrs)
        assert ok1 and ok2

    def test_has_convergence_data(self):
        result = simulated_annealing.solve(small_set(), default_params(), seed=42)
        assert result.convergence is not None and len(result.convergence) > 0

    def test_tight_budget(self):
        params = SolveParams(total_budget=5.0, num_days=1, daily_time_budget=600,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = simulated_annealing.solve(small_set(), params, seed=42)
        assert result.total_cost <= 5.0 + 1e-6

    def test_single_day(self):
        params = SolveParams(num_days=1, daily_time_budget=600, total_budget=200.0,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = simulated_annealing.solve(small_set(), params, seed=42)
        assert len(result.days) == 1

    def test_many_days(self):
        params = SolveParams(num_days=5, daily_time_budget=600, total_budget=500.0,
                             start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
        result = simulated_annealing.solve(small_set(), params, seed=42)
        assert len(result.days) == 5

    def test_chronological_order(self):
        result = simulated_annealing.solve(small_set(), default_params(), seed=42)
        for day in result.days:
            for i in range(1, len(day.visits)):
                assert day.visits[i].arrival_time >= day.visits[i - 1].departure_time

    def test_empty_attractions(self):
        result = simulated_annealing.solve([], default_params(), seed=42)
        assert result.total_attractions == 0
