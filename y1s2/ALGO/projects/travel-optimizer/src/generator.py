import json
import math
import numpy as np
from scipy.stats import truncnorm, beta as beta_dist
from src.models import Attraction, Location

CATEGORY_WEIGHTS = {
    "Restaurant":     0.25,
    "Landmark":       0.20,
    "Museum":         0.15,
    "Park":           0.15,
    "Shopping":       0.15,
    "Entertainment":  0.10,
}

BANGKOK_CLUSTERS = [
    (13.7500, 100.4913, 0.012),  # Old City
    (13.7398, 100.5688, 0.015),  # Sukhumvit
    (13.7222, 100.5271, 0.012),  # Silom/Sathorn
    (13.7997, 100.5500, 0.015),  # Chatuchak
    (13.7390, 100.5148, 0.010),  # Chinatown
]

# Per-neighbourhood category skews for Bangkok Real dataset (weights, unnormalised)
NEIGHBOURHOOD_SKEWS = {
    0: {"Museum": 3, "Landmark": 4, "Restaurant": 1, "Park": 1, "Shopping": 1, "Entertainment": 1},  # Old City
    1: {"Museum": 1, "Landmark": 1, "Restaurant": 4, "Park": 1, "Shopping": 4, "Entertainment": 3},  # Sukhumvit
    2: {"Museum": 1, "Landmark": 3, "Restaurant": 4, "Park": 1, "Shopping": 2, "Entertainment": 2},  # Silom
    3: {"Museum": 1, "Landmark": 1, "Restaurant": 2, "Park": 4, "Shopping": 4, "Entertainment": 1},  # Chatuchak
    4: {"Museum": 1, "Landmark": 3, "Restaurant": 4, "Park": 1, "Shopping": 2, "Entertainment": 1},  # Chinatown
}

CATEGORY_PARAMS = {
    "Museum":        {"open_mean": 540,  "open_std": 15,  "close_mean": 1020, "close_std": 15,
                      "dur_mean": 90,   "dur_std": 25,  "dur_min": 45,  "dur_max": 180,
                      "fee_free_p": 0.20, "fee_mean": 10, "fee_std": 5,   "fee_min": 2,  "fee_max": 25,
                      "pref_a": 3, "pref_b": 2},
    "Restaurant":    {"open_mean": 660,  "open_std": 30,  "close_mean": 1320, "close_std": 30,
                      "dur_mean": 50,   "dur_std": 15,  "dur_min": 30,  "dur_max": 90,
                      "fee_free_p": 0.00, "fee_mean": 20, "fee_std": 8,   "fee_min": 5,  "fee_max": 40,
                      "pref_a": 2, "pref_b": 2},
    "Landmark":      {"open_mean": 360,  "open_std": 30,  "close_mean": 1080, "close_std": 30,
                      "dur_mean": 45,   "dur_std": 20,  "dur_min": 20,  "dur_max": 90,
                      "fee_free_p": 0.50, "fee_mean": 6,  "fee_std": 4,   "fee_min": 0,  "fee_max": 15,
                      "pref_a": 3, "pref_b": 2},
    "Park":          {"open_mean": 360,  "open_std": 30,  "close_mean": 1080, "close_std": 30,
                      "dur_mean": 60,   "dur_std": 20,  "dur_min": 30,  "dur_max": 120,
                      "fee_free_p": 0.90, "fee_mean": 3,  "fee_std": 2,   "fee_min": 0,  "fee_max": 5,
                      "pref_a": 2, "pref_b": 3},
    "Shopping":      {"open_mean": 600,  "open_std": 30,  "close_mean": 1260, "close_std": 30,
                      "dur_mean": 80,   "dur_std": 30,  "dur_min": 30,  "dur_max": 180,
                      "fee_free_p": 0.00, "fee_mean": 25, "fee_std": 15,  "fee_min": 5,  "fee_max": 60,
                      "pref_a": 2, "pref_b": 2},
    "Entertainment": {"open_mean": 720,  "open_std": 30,  "close_mean": 1380, "close_std": 30,
                      "dur_mean": 120,  "dur_std": 40,  "dur_min": 60,  "dur_max": 240,
                      "fee_free_p": 0.05, "fee_mean": 25, "fee_std": 10,  "fee_min": 10, "fee_max": 55,
                      "pref_a": 2, "pref_b": 3},
}

CATEGORY_NAMES = {
    "Museum":        ["National Museum", "Art Gallery", "History Museum", "Science Museum",
                      "Cultural Center", "Heritage House", "Contemporary Art Museum", "City Museum"],
    "Restaurant":    ["Thai Kitchen", "Riverside Cafe", "Night Market Grill", "Rooftop Restaurant",
                      "Street Food Hall", "Garden Bistro", "Seafood House", "Noodle Bar"],
    "Landmark":      ["Grand Palace", "Wat Pho", "Golden Mount", "Democracy Monument",
                      "Erawan Shrine", "Victory Monument", "Vimanmek Mansion", "Wat Arun"],
    "Park":          ["Lumpini Park", "Chatuchak Park", "Benjakitti Park", "Santiphap Park",
                      "Rama IX Park", "Queen Sirikit Garden", "Suan Rot Fai", "Bang Krachao"],
    "Shopping":      ["MBK Center", "Chatuchak Market", "Siam Paragon", "Terminal 21",
                      "Icon Siam", "Asiatique", "Platinum Mall", "JJ Market"],
    "Entertainment": ["Muay Thai Stadium", "Escape Room Bangkok", "Laser Tag Arena",
                      "Rooftop Bar", "Jazz Club", "Comedy Club", "Bowling Alley", "Sky Deck"],
}


def _sample_truncated_normal(rng, mean, std, lo, hi):
    a, b = (lo - mean) / std, (hi - mean) / std
    return float(truncnorm.rvs(a, b, loc=mean, scale=std, random_state=rng))


def _sample_category_params(rng, category):
    p = CATEGORY_PARAMS[category]

    open_time = int(round(_sample_truncated_normal(rng, p["open_mean"], p["open_std"],
                                                    p["open_mean"] - 60, p["open_mean"] + 60)))
    close_time = int(round(_sample_truncated_normal(rng, p["close_mean"], p["close_std"],
                                                     p["close_mean"] - 60, p["close_mean"] + 60)))
    close_time = max(close_time, open_time + 60)

    duration = int(round(_sample_truncated_normal(rng, p["dur_mean"], p["dur_std"],
                                                   p["dur_min"], p["dur_max"])))

    if rng.random() < p["fee_free_p"]:
        fee = 0.0
    else:
        fee = round(_sample_truncated_normal(rng, p["fee_mean"], p["fee_std"],
                                              p["fee_min"], p["fee_max"]), 2)

    preference = round(float(beta_dist.rvs(p["pref_a"], p["pref_b"], random_state=rng)), 4)

    return open_time, close_time, duration, fee, preference


def _sample_location(rng, cluster_idx=None):
    if cluster_idx is None:
        cluster_idx = rng.integers(0, len(BANGKOK_CLUSTERS))
    lat_c, lng_c, sigma = BANGKOK_CLUSTERS[cluster_idx]
    lat = float(rng.normal(lat_c, sigma))
    lng = float(rng.normal(lng_c, sigma))
    return lat, lng


def _category_name(rng, category, existing_names):
    bank = CATEGORY_NAMES[category]
    name = rng.choice(bank)
    suffix = 1
    candidate = name
    while candidate in existing_names:
        candidate = f"{name} {suffix}"
        suffix += 1
    return candidate


def generate_dataset(n: int, seed: int, name: str) -> list[Attraction]:
    rng = np.random.default_rng(seed)
    categories = list(CATEGORY_WEIGHTS.keys())
    weights = np.array([CATEGORY_WEIGHTS[c] for c in categories])
    weights /= weights.sum()

    attractions = []
    used_names = set()
    for i in range(n):
        category = rng.choice(categories, p=weights)
        lat, lng = _sample_location(rng)
        open_t, close_t, dur, fee, pref = _sample_category_params(rng, category)
        aname = _category_name(rng, category, used_names)
        used_names.add(aname)
        attractions.append(Attraction(
            id=i + 1,
            name=aname,
            location=Location(lat, lng),
            open_time=open_t,
            close_time=close_t,
            duration=dur,
            fee=fee,
            preference=pref,
            category=category,
        ))
    return attractions


def generate_bangkok_real(n: int, seed: int) -> list[Attraction]:
    rng = np.random.default_rng(seed)
    attractions = []
    used_names = set()
    for i in range(n):
        cluster_idx = int(rng.integers(0, len(BANGKOK_CLUSTERS)))
        skew = NEIGHBOURHOOD_SKEWS[cluster_idx]
        cats = list(skew.keys())
        w = np.array([skew[c] for c in cats], dtype=float)
        w /= w.sum()
        category = rng.choice(cats, p=w)
        lat, lng = _sample_location(rng, cluster_idx)
        open_t, close_t, dur, fee, pref = _sample_category_params(rng, category)
        aname = _category_name(rng, category, used_names)
        used_names.add(aname)
        attractions.append(Attraction(
            id=i + 1,
            name=aname,
            location=Location(lat, lng),
            open_time=open_t,
            close_time=close_t,
            duration=dur,
            fee=fee,
            preference=pref,
            category=category,
        ))
    return attractions


def generate_hard_dataset(n: int, seed: int) -> list[Attraction]:
    """Adversarial dataset that exposes greedy's myopic failure.

    Structure:
    - 40% 'far cluster' attractions: HIGH preference (Beta(5,2)≈0.71 mean),
      short morning windows (close 1pm–3pm), located 22–30 travel-minutes from
      hotel in 3 geographic clusters.
    - 60% 'near trap' attractions: MEDIUM preference (Beta(4,3)≈0.57 mean),
      all-day windows, very close to hotel (2–4 min travel).

    Greedy scoring = pref/(travel+dur+1):
      Near: ~0.57/(3+60+1) = 0.0089  ← slightly higher → greedy picks near first
      Far:  ~0.71/(28+65+1) = 0.0076

    Greedy visits many near traps, exhausting the morning. Far windows close
    before greedy can reach them. SA discovers that visiting far clusters first
    maximises total satisfaction — classic global-vs-local optimisation failure.
    """
    rng = np.random.default_rng(seed)

    HOTEL_LAT, HOTEL_LNG = 13.7563, 100.5018

    # Three far clusters, each ~24–28 travel-minutes from hotel at 30 km/h
    FAR_CLUSTER_CENTERS = [
        (13.880, 100.500),  # North:  ~13.5 km → 27 min
        (13.740, 100.635),  # East:   ~11.8 km → 24 min
        (13.645, 100.510),  # South:  ~12.5 km → 25 min
    ]

    attractions = []
    used_names = set()
    n_far = n * 2 // 5       # 40% far cluster (high pref, tight window)
    n_near = n - n_far        # 60% near hotel  (medium pref, all day)

    # ── Far cluster attractions ──────────────────────────────────────────────
    for i in range(n_far):
        ci = i % len(FAR_CLUSTER_CENTERS)
        clat, clng = FAR_CLUSTER_CENTERS[ci]
        lat = float(rng.normal(clat, 0.006))
        lng = float(rng.normal(clng, 0.006))

        open_time = int(rng.integers(480, 541))         # 8:00–9:00 am
        window = int(rng.integers(210, 301))            # 3.5–5 h window
        close_time = open_time + window                 # closes ~1pm–2pm

        duration = int(round(float(rng.normal(65, 12))))
        duration = max(45, min(100, duration))
        close_time = max(close_time, open_time + duration + 20)

        if rng.random() < 0.30:
            fee = 0.0
        else:
            fee = round(float(rng.uniform(3, 20)), 2)

        preference = round(float(beta_dist.rvs(5, 2, random_state=rng)), 4)

        category = str(rng.choice(["Museum", "Landmark"]))
        aname = _category_name(rng, category, used_names)
        used_names.add(aname)
        attractions.append(Attraction(
            id=i + 1, name=aname,
            location=Location(lat, lng),
            open_time=open_time, close_time=close_time,
            duration=duration, fee=fee, preference=preference,
            category=category,
        ))

    # ── Near-hotel trap attractions ──────────────────────────────────────────
    near_cats = ["Restaurant", "Shopping", "Park", "Entertainment"]
    near_weights = np.array([0.30, 0.30, 0.20, 0.20])

    for i in range(n_near):
        lat = float(rng.normal(HOTEL_LAT, 0.010))
        lng = float(rng.normal(HOTEL_LNG, 0.010))

        open_time = 480    # 8 am
        close_time = 1200  # 8 pm

        duration = int(round(float(rng.normal(60, 10))))
        duration = max(30, min(90, duration))

        if rng.random() < 0.20:
            fee = 0.0
        else:
            fee = round(float(rng.uniform(2, 18)), 2)

        preference = round(float(beta_dist.rvs(4, 3, random_state=rng)), 4)

        category = str(rng.choice(near_cats, p=near_weights))
        aname = _category_name(rng, category, used_names)
        used_names.add(aname)
        attractions.append(Attraction(
            id=n_far + i + 1, name=aname,
            location=Location(lat, lng),
            open_time=open_time, close_time=close_time,
            duration=duration, fee=fee, preference=preference,
            category=category,
        ))

    return attractions


def save_dataset(attractions: list[Attraction], path: str):
    with open(path, "w") as f:
        json.dump([a.to_dict() for a in attractions], f, indent=2)


def load_dataset(path: str) -> list[Attraction]:
    with open(path) as f:
        return [Attraction.from_dict(d) for d in json.load(f)]


def haversine_minutes(lat1, lng1, lat2, lng2, speed_kmh=30.0) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    dist_km = 2 * R * math.asin(math.sqrt(a))
    return math.ceil((dist_km / speed_kmh) * 60)


def build_travel_matrix(attractions: list[Attraction], hotel_lat: float, hotel_lng: float):
    n = len(attractions)
    ids = [a.id for a in attractions]
    idx = {aid: i for i, aid in enumerate(ids)}
    matrix = [[0] * (n + 1) for _ in range(n + 1)]  # indices 0..n-1 = attractions, n = hotel
    for i, a in enumerate(attractions):
        t = haversine_minutes(hotel_lat, hotel_lng, a.location.lat, a.location.lng)
        matrix[n][i] = t
        matrix[i][n] = t
        for j, b in enumerate(attractions):
            if i != j:
                matrix[i][j] = haversine_minutes(a.location.lat, a.location.lng,
                                                   b.location.lat, b.location.lng)
    return matrix, idx
