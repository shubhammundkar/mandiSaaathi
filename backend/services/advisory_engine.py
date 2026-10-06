"""Core Advisory & Recommendation Engine.

Calculates Net Return per quintal after deducting transport, handling labor,
APMC market fee, and crop-specific transit spoilage. Implements arrival-day
and morning auction cutoff logic, break-even price thresholds, and confidence scoring.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from backend.config import BASE_DIR
from backend.services.data_service import get_latest_prices_for_crop, load_mandi_matrix

CONFIG_PATH = BASE_DIR / "backend" / "config.yaml"


def load_config() -> Dict[str, Any]:
    """Loads economic parameters from config.yaml."""
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates road-estimated distance (km) using Haversine with a 1.25 winding factor."""
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    direct_km = R * c
    # Indian rural road winding factor ~1.25
    return round(direct_km * 1.25, 1)


DISTRICT_COORDS: Dict[str, tuple[float, float]] = {
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Ahilyanagar": (19.0948, 74.7480),
    "Ahmednagar": (19.0948, 74.7480),
    "Solapur": (17.6599, 75.9064),
    "Latur": (18.4088, 76.5604),
    "Jalgaon": (21.0077, 75.5626),
    "Akola": (20.7002, 77.0082),
    "Amravati": (20.9374, 77.7796),
    "Kolhapur": (16.7050, 74.2433),
    "Nagpur": (21.1458, 79.0882),
    "Mumbai": (19.0760, 72.8777),
}


def get_origin_coords(district: str) -> tuple[float, float]:
    """Resolves origin coordinates from district name."""
    clean = district.strip().title()
    for d_name, coords in DISTRICT_COORDS.items():
        if d_name.lower() in clean.lower():
            return coords
    return (18.5204, 73.8567)


def parse_time_str(time_str: str) -> float:
    """Converts 'HH:MM' string to decimal hours (e.g. '11:30' -> 11.5)."""
    try:
        parts = time_str.split(":")
        return float(parts[0]) + float(parts[1]) / 60.0
    except Exception:
        return 12.0


def compute_mandi_metrics(
    candidate: Dict[str, Any],
    origin_lat: float,
    origin_lng: float,
    quantity_quintals: float,
    vehicle_type: str,
    departure_hour: float,
    crop: str,
    config: Dict[str, Any],
    overrides: Optional[Dict[str, Any]] = None,
    now_date: Optional[Any] = None
) -> Dict[str, Any]:
    """Computes full distance, timing, deductions, and net return for a single mandi candidate."""
    overrides = overrides or {}
    now_date = now_date or datetime.now().date()

    # Normalize vehicle key
    v_key = vehicle_type.lower().replace(" ", "_")
    if v_key in ["own", "own_vehicle", "bike"]:
        v_key = "own_vehicle"
    elif "truck" in v_key:
        v_key = "truck"
    else:
        v_key = "tempo"

    vehicles_cfg = config.get("vehicles", {})
    vehicle_cfg = vehicles_cfg.get(v_key, {
        "rate_per_km": 18.0,
        "speed_kmh": 45.0
    })

    rate_per_km = float(overrides.get("rate_per_km", vehicle_cfg.get("rate_per_km", 18.0)))
    speed_kmh = float(overrides.get("speed_kmh", vehicle_cfg.get("speed_kmh", 45.0)))

    # Labor handling
    handling_cfg = config.get("handling", {})
    loading_rate = float(overrides.get("loading_per_quintal", handling_cfg.get("loading_per_quintal", 15.0)))
    unloading_rate = float(overrides.get("unloading_per_quintal", handling_cfg.get("unloading_per_quintal", 15.0)))
    overnight_rate = float(overrides.get("overnight_holding_per_quintal", handling_cfg.get("overnight_holding_per_quintal", 12.0)))

    # Market fee
    fee_pct = float(overrides.get("market_fee_percent", config.get("market_fee_percent", 1.5))) / 100.0

    # Spoilage
    spoilage_cfg = config.get("spoilage_per_day", {})
    daily_spoilage = float(overrides.get("spoilage_rate", spoilage_cfg.get(crop, 0.005)))

    # Distance & transit
    m_lat = candidate.get("lat", 18.5)
    m_lng = candidate.get("lng", 73.8)
    distance_km = haversine_distance(origin_lat, origin_lng, m_lat, m_lng)
    travel_hours = round(max(0.2, distance_km / max(10.0, speed_kmh)), 1)
    arrival_hour = departure_hour + travel_hours

    cutoff_str = candidate.get("auction_cutoff", config.get("operational", {}).get("auction_cutoff", "12:00"))
    cutoff_hour = parse_time_str(cutoff_str)

    # Arrival vs Auction Cutoff
    missed_cutoff = arrival_hour > cutoff_hour
    holding_cost = overnight_rate if missed_cutoff else 0.0
    effective_spoilage_hours = travel_hours + (16.0 if missed_cutoff else 0.0)

    # Price & far-mandi lower bound haircut
    gross_price = float(candidate.get("modal_price", candidate.get("price", 0.0)))
    is_far = distance_km > 60.0
    haircut = config.get("operational", {}).get("cautious_forecast_haircut", 0.04) if is_far else 0.0
    expected_price = round(gross_price * (1.0 - haircut), 2)

    # Deductions per quintal
    batch_qty = max(0.1, quantity_quintals)
    transport_cost = round((distance_km * rate_per_km * 2.0) / batch_qty, 2)
    loading_cost = round(loading_rate + unloading_rate + holding_cost, 2)
    fee_cost = round(expected_price * fee_pct, 2)
    spoilage_cost = round(expected_price * (effective_spoilage_hours / 24.0) * daily_spoilage, 2)

    total_deductions = round(transport_cost + loading_cost + fee_cost + spoilage_cost, 2)
    net_return = round(expected_price - total_deductions, 2)
    total_earnings = round(net_return * batch_qty, 2)

    # Days since last report
    arr_date_str = candidate.get("arrival_date", str(now_date))
    try:
        arr_date = datetime.strptime(arr_date_str, "%Y-%m-%d").date()
        days_ago = max(0, (now_date - arr_date).days)
    except Exception:
        days_ago = 0

    is_stale = days_ago > 3
    if days_ago <= 1:
        confidence = "HIGH"
    elif days_ago <= 3:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "market": candidate.get("market", "Unknown Mandi"),
        "district": candidate.get("district", "Unknown District"),
        "distance_km": distance_km,
        "travel_hours": travel_hours,
        "arrival_time": f"{int(arrival_hour):02d}:{int((arrival_hour % 1) * 60):02d}",
        "auction_cutoff": cutoff_str,
        "missed_cutoff": missed_cutoff,
        "arrival_day": "Tomorrow (Day+1)" if missed_cutoff else "Today (Day 0)",
        "gross_modal_price": gross_price,
        "expected_price": expected_price,
        "is_far_mandi": is_far,
        "lower_bound_haircut_applied": haircut > 0,
        "price_range": {
            "min": float(candidate.get("min_price", gross_price * 0.9)),
            "modal": gross_price,
            "max": float(candidate.get("max_price", gross_price * 1.1))
        },
        "costs": {
            "transport_per_q": transport_cost,
            "loading_unloading_per_q": loading_cost,
            "market_fee_per_q": fee_cost,
            "spoilage_per_q": spoilage_cost,
            "total_deductions_per_q": total_deductions
        },
        "net_return_per_quintal": net_return,
        "total_net_earnings": total_earnings,
        "days_ago": days_ago,
        "is_stale": is_stale,
        "confidence": confidence,
        "arrival_date": arr_date_str,
        "source": candidate.get("source", "snapshot"),
        "is_sample": bool(candidate.get("is_sample", 0))
    }


def rank_and_evaluate(
    evaluated: List[Dict[str, Any]],
    crop: str,
    district: str,
    quantity_quintals: float,
    vehicle_type: str,
    departure_hour: float,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Sorts evaluated mandis, calculates break-even against nearest, and formats verdict."""
    if not evaluated:
        return {
            "crop": crop,
            "district": district,
            "best_recommendation": None,
            "comparisons": []
        }

    config = config or load_config()
    fee_pct = float(config.get("market_fee_percent", 1.5)) / 100.0
    crop_spoil_rate = float(config.get("spoilage_per_day", {}).get(crop, 0.005))

    # Find nearest mandi to serve as baseline
    nearest_mandi = min(evaluated, key=lambda x: x["distance_km"])
    nearest_net = nearest_mandi["net_return_per_quintal"]

    # Calculate break-even price for all mandis against nearest
    for item in evaluated:
        if item["market"] == nearest_mandi["market"]:
            item["break_even_price"] = item["gross_modal_price"]
            item["is_nearest"] = True
        else:
            item["is_nearest"] = False
            # Price needed so that: Net_far = nearest_net
            # P_be * (1 - fee_rate - spoil_factor) = nearest_net + trans + load
            spoil_factor = (item["travel_hours"] / 24.0) * crop_spoil_rate
            denom = max(0.5, 1.0 - fee_pct - spoil_factor)
            be_price = (nearest_net + item["costs"]["transport_per_q"] + item["costs"]["loading_unloading_per_q"]) / denom
            item["break_even_price"] = round(be_price, 2)

    # Sort descending by net return
    # Prioritize non-stale mandis for top ranking
    fresh_mandis = [m for m in evaluated if not m["is_stale"]]
    stale_mandis = [m for m in evaluated if m["is_stale"]]

    fresh_mandis.sort(key=lambda x: x["net_return_per_quintal"], reverse=True)
    stale_mandis.sort(key=lambda x: x["net_return_per_quintal"], reverse=True)

    sorted_list = fresh_mandis + stale_mandis
    best = sorted_list[0]
    gain = round(best["net_return_per_quintal"] - nearest_net, 2)

    # Construct one-line rationale
    if best["market"] == nearest_mandi["market"]:
        reason = f"Sell locally at {best['market']}: Low transport and zero auction delay maximize net profit."
    elif gain > 0:
        reason = f"Travel to {best['market']}: Premium price nets +₹{gain}/q higher profit after covering all travel costs."
    else:
        reason = f"Sell at {best['market']}: Best available market for your volume and transport vehicle."

    best["verdict_reason"] = reason
    best["gain_vs_nearest_per_quintal"] = gain

    for item in sorted_list[1:]:
        diff = round(best["net_return_per_quintal"] - item["net_return_per_quintal"], 2)
        if item["is_stale"]:
            item["verdict_reason"] = f"Caution: Unreported for {item['days_ago']} days. Potential data lag."
        elif item["missed_cutoff"]:
            item["verdict_reason"] = f"Misses morning auction cutoff ({item['auction_cutoff']}). Adds overnight storage."
        else:
            item["verdict_reason"] = f"Yields ₹{diff}/q lower net return than {best['market']} due to transport/price difference."

    return {
        "query": {
            "crop": crop,
            "district": district,
            "quantity_quintals": quantity_quintals,
            "vehicle_type": vehicle_type,
            "departure_hour": f"{int(departure_hour):02d}:00"
        },
        "best_recommendation": best,
        "nearest_baseline": nearest_mandi["market"],
        "comparisons": sorted_list[1:] if len(sorted_list) > 1 else []
    }


def calculate_advisory(
    crop: str,
    district: Optional[str] = "Pune",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    quantity_quintals: float = 20.0,
    vehicle_type: str = "tempo",
    departure_hour: float = 7.0,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Entrypoint query fetching DB prices and evaluating all candidate mandis."""
    district = district or "Pune"
    if lat is not None and lng is not None:
        origin_lat, origin_lng = lat, lng
    else:
        origin_lat, origin_lng = get_origin_coords(district)

    config = load_config()
    prices = get_latest_prices_for_crop(crop)
    if not prices:
        return {
            "crop": crop,
            "district": district,
            "error": f"No recent market trading records found for {crop}.",
            "best_recommendation": None,
            "comparisons": []
        }

    matrix = load_mandi_matrix()
    matrix_map = {m["market"]: m for m in matrix.get("mandis", [])}

    evaluated = []
    for row in prices:
        mkt = row["market"]
        info = matrix_map.get(mkt, {})
        cand = dict(row)
        cand["lat"] = info.get("lat", 18.5)
        cand["lng"] = info.get("lng", 73.8)
        cand["auction_cutoff"] = info.get("auction_cutoff", "12:00")
        metrics = compute_mandi_metrics(
            candidate=cand,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            quantity_quintals=quantity_quintals,
            vehicle_type=vehicle_type,
            departure_hour=departure_hour,
            crop=crop,
            config=config,
            overrides=overrides
        )
        evaluated.append(metrics)

    return rank_and_evaluate(
        evaluated=evaluated,
        crop=crop,
        district=district,
        quantity_quintals=quantity_quintals,
        vehicle_type=vehicle_type,
        departure_hour=departure_hour,
        config=config
    )
