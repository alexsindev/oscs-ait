from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Location:
    lat: float
    lng: float


@dataclass
class Attraction:
    id: int
    name: str
    location: Location
    open_time: int   # minutes from midnight
    close_time: int
    duration: int
    fee: float
    preference: float  # [0, 1]
    category: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": {"lat": self.location.lat, "lng": self.location.lng},
            "open_time": self.open_time,
            "close_time": self.close_time,
            "duration": self.duration,
            "fee": self.fee,
            "preference": self.preference,
            "category": self.category,
        }

    @staticmethod
    def from_dict(d):
        return Attraction(
            id=d["id"],
            name=d["name"],
            location=Location(d["location"]["lat"], d["location"]["lng"]),
            open_time=d["open_time"],
            close_time=d["close_time"],
            duration=d["duration"],
            fee=d["fee"],
            preference=d["preference"],
            category=d["category"],
        )


@dataclass
class Visit:
    attraction_id: int
    name: str
    arrival_time: int
    departure_time: int
    fee: float
    preference: float
    category: str


@dataclass
class DayPlan:
    day: int
    visits: list[Visit] = field(default_factory=list)
    total_satisfaction: float = 0.0
    total_cost: float = 0.0
    total_travel_time: int = 0


@dataclass
class ConvergencePoint:
    iteration: int
    satisfaction: float
    temperature: float


@dataclass
class Itinerary:
    days: list[DayPlan]
    total_satisfaction: float
    total_cost: float
    total_attractions: int
    algorithm: str
    computation_ms: float
    convergence: Optional[list[ConvergencePoint]] = None


@dataclass
class SolveParams:
    num_days: int = 2
    daily_time_budget: int = 600  # minutes
    total_budget: float = 100.0
    start_time: int = 540         # 9:00 AM
    hotel_lat: float = 13.7563
    hotel_lng: float = 100.5018
