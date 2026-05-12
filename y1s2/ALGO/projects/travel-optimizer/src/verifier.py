from src.models import Itinerary, SolveParams, Attraction


def verify(itinerary: Itinerary, params: SolveParams,
           attractions: list[Attraction] = None) -> tuple[bool, list[str]]:
    errors = []
    attr_map = {a.id: a for a in attractions} if attractions else {}

    seen = set()
    for day in itinerary.days:
        for v in day.visits:
            if v.attraction_id in seen:
                errors.append(f"Duplicate visit: attraction {v.attraction_id} ({v.name})")
            seen.add(v.attraction_id)

    for day in itinerary.days:
        for v in day.visits:
            a = attr_map.get(v.attraction_id)
            open_t = a.open_time if a else v.arrival_time
            close_t = a.close_time if a else v.departure_time
            if v.arrival_time < open_t:
                errors.append(f"Day {day.day}: {v.name} arrives before open ({v.arrival_time} < {open_t})")
            if v.departure_time > close_t:
                errors.append(f"Day {day.day}: {v.name} departs after close ({v.departure_time} > {close_t})")

    for day in itinerary.days:
        for i in range(1, len(day.visits)):
            prev, curr = day.visits[i - 1], day.visits[i]
            if curr.arrival_time < prev.departure_time:
                errors.append(f"Day {day.day}: overlap between visit {i-1} and {i}")

    for day in itinerary.days:
        if day.visits:
            elapsed = day.visits[-1].departure_time - params.start_time
            if elapsed > params.daily_time_budget:
                errors.append(f"Day {day.day}: daily time budget exceeded ({elapsed} > {params.daily_time_budget})")

    if itinerary.total_cost > params.total_budget + 1e-6:
        errors.append(f"Total cost {itinerary.total_cost:.2f} exceeds budget {params.total_budget:.2f}")

    return len(errors) == 0, errors
