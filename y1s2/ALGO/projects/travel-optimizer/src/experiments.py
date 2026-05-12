from dataclasses import dataclass
import numpy as np
from src.models import Attraction, SolveParams, Itinerary
from src.verifier import verify

SA_SEEDS = [42, 123, 7, 99, 314, 271, 1001, 555, 888, 2024]


@dataclass
class RunResult:
    satisfaction: float
    cost: float
    attractions: int
    computation_ms: float
    valid: bool
    convergence: list = None


@dataclass
class Stats:
    mean: float
    std: float
    min: float
    max: float
    valid_count: int
    mean_ms: float
    mean_attractions: float
    mean_cost: float
    raw: list[float] = None


def run_single(attractions: list[Attraction], params: SolveParams,
               algorithm_fn, seed: int = 42) -> RunResult:
    result = algorithm_fn(attractions, params, seed)
    ok, _ = verify(result, params, attractions)
    return RunResult(
        satisfaction=result.total_satisfaction,
        cost=result.total_cost,
        attractions=result.total_attractions,
        computation_ms=result.computation_ms,
        valid=ok,
        convergence=result.convergence,
    )


def run_multiple(attractions: list[Attraction], params: SolveParams,
                 algorithm_fn, seeds: list[int] = None) -> Stats:
    if seeds is None:
        seeds = SA_SEEDS
    results = [run_single(attractions, params, algorithm_fn, s) for s in seeds]
    valid = [r for r in results if r.valid]
    sats = [r.satisfaction for r in valid]
    return Stats(
        mean=float(np.mean(sats)) if sats else 0.0,
        std=float(np.std(sats, ddof=1)) if len(sats) > 1 else 0.0,
        min=float(np.min(sats)) if sats else 0.0,
        max=float(np.max(sats)) if sats else 0.0,
        valid_count=len(valid),
        mean_ms=float(np.mean([r.computation_ms for r in valid])) if valid else 0.0,
        mean_attractions=float(np.mean([r.attractions for r in valid])) if valid else 0.0,
        mean_cost=float(np.mean([r.cost for r in valid])) if valid else 0.0,
        raw=sats,
    )


def run_algorithm_comparison(datasets: dict[str, list[Attraction]],
                              params: SolveParams,
                              greedy_fn, sa_fn) -> dict:
    rows = {}
    for name, attractions in datasets.items():
        g = run_single(attractions, params, greedy_fn)
        s = run_multiple(attractions, params, sa_fn)
        improvement = ((s.mean - g.satisfaction) / g.satisfaction * 100) if g.satisfaction > 0 else 0.0
        rows[name] = {"greedy": g, "sa": s, "improvement_pct": improvement}
    return rows


def run_scalability(datasets: dict[str, list[Attraction]],
                    params: SolveParams,
                    greedy_fn, sa_fn) -> dict:
    rows = {}
    for name, attractions in datasets.items():
        g = run_single(attractions, params, greedy_fn)
        s = run_multiple(attractions, params, sa_fn)
        rows[name] = {"n": len(attractions), "greedy_ms": g.computation_ms, "sa_mean_ms": s.mean_ms}
    return rows


def run_param_sweep(attractions: list[Attraction],
                    param_name: str, param_values: list,
                    base_params: SolveParams,
                    greedy_fn, sa_fn) -> dict:
    rows = {}
    for val in param_values:
        p = SolveParams(
            num_days=val if param_name == "num_days" else base_params.num_days,
            daily_time_budget=val if param_name == "daily_time_budget" else base_params.daily_time_budget,
            total_budget=val if param_name == "total_budget" else base_params.total_budget,
            start_time=base_params.start_time,
            hotel_lat=base_params.hotel_lat,
            hotel_lng=base_params.hotel_lng,
        )
        g = run_single(attractions, p, greedy_fn)
        s = run_multiple(attractions, p, sa_fn)
        rows[val] = {"greedy": g, "sa": s}
    return rows


def run_convergence(attractions: list[Attraction], params: SolveParams,
                    sa_fn, n_seeds: int = 5) -> list:
    curves = []
    for seed in SA_SEEDS[:n_seeds]:
        r = run_single(attractions, params, sa_fn, seed)
        curves.append({"seed": seed, "convergence": r.convergence})
    return curves
