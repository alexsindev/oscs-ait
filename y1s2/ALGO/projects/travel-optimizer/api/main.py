from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models import Attraction, Location, SolveParams, Visit, DayPlan, Itinerary
from src import greedy, simulated_annealing
from src.generator import (
    generate_dataset, generate_bangkok_real, generate_hard_dataset,
    save_dataset, load_dataset,
)

DATA_DIR = Path("assets/dataset")

app = FastAPI(title="Tourism Itinerary Optimizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class LocationSchema(BaseModel):
    lat: float
    lng: float


class AttractionSchema(BaseModel):
    id: int
    name: str
    location: LocationSchema
    open_time: int
    close_time: int
    duration: int
    fee: float
    preference: float
    category: str


class OptimizeRequest(BaseModel):
    attractions: Optional[list[AttractionSchema]] = None
    dataset_name: Optional[str] = None
    hotel_lat: float = 13.7563
    hotel_lng: float = 100.5018
    num_days: int = 2
    daily_time_budget: int = 600
    total_budget: float = 100.0
    start_time: int = 540
    algorithm: str = "sa"   # "greedy" | "sa"
    sa_seed: int = 42


class VisitOut(BaseModel):
    attraction_id: int
    name: str
    lat: float
    lng: float
    arrival_time: int
    departure_time: int
    fee: float
    preference: float
    category: str


class DayPlanOut(BaseModel):
    day: int
    visits: list[VisitOut]
    total_satisfaction: float
    total_cost: float
    total_travel_time: int


class ItineraryOut(BaseModel):
    days: list[DayPlanOut]
    total_satisfaction: float
    total_cost: float
    total_attractions: int
    algorithm: str
    computation_ms: float


# ── Helpers ───────────────────────────────────────────────────────────────────

def _schema_to_model(a: AttractionSchema) -> Attraction:
    return Attraction(
        id=a.id,
        name=a.name,
        location=Location(a.location.lat, a.location.lng),
        open_time=a.open_time,
        close_time=a.close_time,
        duration=a.duration,
        fee=a.fee,
        preference=a.preference,
        category=a.category,
    )


def _enrich_itinerary(itin: Itinerary, attr_map: dict[int, Attraction]) -> ItineraryOut:
    """Add lat/lng to each Visit so the frontend can place map pins."""
    days_out = []
    for d in itin.days:
        visits_out = []
        for v in d.visits:
            a = attr_map[v.attraction_id]
            visits_out.append(VisitOut(
                attraction_id=v.attraction_id,
                name=v.name,
                lat=a.location.lat,
                lng=a.location.lng,
                arrival_time=v.arrival_time,
                departure_time=v.departure_time,
                fee=v.fee,
                preference=v.preference,
                category=v.category,
            ))
        days_out.append(DayPlanOut(
            day=d.day,
            visits=visits_out,
            total_satisfaction=d.total_satisfaction,
            total_cost=d.total_cost,
            total_travel_time=d.total_travel_time,
        ))
    return ItineraryOut(
        days=days_out,
        total_satisfaction=itin.total_satisfaction,
        total_cost=itin.total_cost,
        total_attractions=itin.total_attractions,
        algorithm=itin.algorithm,
        computation_ms=itin.computation_ms,
    )


def _ensure_dataset(name: str) -> list[Attraction]:
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        return load_dataset(str(path))

    # Generate on demand if not present
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    generators = {
        "small": lambda: generate_dataset(15, 42, "small"),
        "medium": lambda: generate_dataset(75, 42, "medium"),
        "large": lambda: generate_dataset(300, 42, "large"),
        "bangkok_real": lambda: generate_bangkok_real(150, 42),
        "hard": lambda: generate_hard_dataset(100, 42),
    }
    if name not in generators:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    attrs = generators[name]()
    save_dataset(attrs, str(path))
    return attrs


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/datasets")
def list_datasets() -> list[str]:
    return ["small", "medium", "large", "bangkok_real", "hard"]


@app.get("/api/datasets/{name}")
def get_dataset(name: str) -> list[dict]:
    attrs = _ensure_dataset(name)
    return [a.to_dict() for a in attrs]


@app.post("/api/optimize", response_model=ItineraryOut)
def optimize(req: OptimizeRequest) -> ItineraryOut:
    # Resolve attractions
    if req.attractions:
        attractions = [_schema_to_model(a) for a in req.attractions]
    elif req.dataset_name:
        attractions = _ensure_dataset(req.dataset_name)
    else:
        raise HTTPException(status_code=422, detail="Provide 'attractions' or 'dataset_name'")

    attr_map = {a.id: a for a in attractions}

    params = SolveParams(
        num_days=req.num_days,
        daily_time_budget=req.daily_time_budget,
        total_budget=req.total_budget,
        start_time=req.start_time,
        hotel_lat=req.hotel_lat,
        hotel_lng=req.hotel_lng,
    )

    if req.algorithm == "greedy":
        itin = greedy.solve(attractions, params)
    elif req.algorithm == "sa":
        itin = simulated_annealing.solve(attractions, params, seed=req.sa_seed)
    else:
        raise HTTPException(status_code=422, detail=f"Unknown algorithm: {req.algorithm}")

    return _enrich_itinerary(itin, attr_map)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
