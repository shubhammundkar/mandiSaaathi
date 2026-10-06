"""Core Advisory & Recommendation Engine.

Calculates Net Return per quintal after deducting transport, handling labor,
APMC commission, and crop-specific transit spoilage. Implements arrival-day
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
    """Calculates road-estimated distance (km) between coordinates using Haversine with a 1.25 winding factor."""
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


# Reference district center coordinates in Maharashtra
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
    return (18.5204, 73.8567)  # Default Pune


def parse_time_str(time_str: str) -> float:
    """Converts 'HH:MM' string to decimal hours (e.g. '11:30' -> 11.5)."""
    try:
        parts = time_str.split(":")
        return float(parts[0]) + float(parts[1]) / 60.0
    except Exception:
        return 12.0


def calculate_advisory(
    crop: str,
    district: str,
    quantity_quintals: float = 20.0,
    vehicle_type: str = "tempo",
    departure_hour: float = 7.0,  # 7:00 AM default departure
    origin_lat: Optional[float] = None,
    origin_lng: Optional[float] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Evaluates candidate mandis for crop and ranks them by Net Return per quintal."""
    config = load_config()
    overrides = overrides or {}

    # 1. Resolve vehicle parameters
    vehicle_cfg = config.get("vehicles", {}).get(vehicle_type.lower(), {
        "rate_per_km": 18.0,
        "capacity_quintals": 25.0,
        "avg_speed_kmh": 45.0
    })
    rate_per_km = float(overrides.get("rate_per_km", vehicle_cfg["rate_per_km"]))
    avg_speed = float(overrides.get("avg_speed_kmh", vehicle_cfg["avg_speed_kmh"]))

    # 2. Handling costs
    handling_cfg = config.get("handling", {})
    loading_rate = float(overrides.get("loading_per_quintal", handling_cfg.get("loading_per_quintal", 15.0)))
    unloading_rate = float(overrides.get("unloading_per_quintal", handling_cfg.get("unloading_per_quintal", 15.0)))
    overnight_rate = float(handling_cfg.get("overnight_holding_per_quintal", 12.0))

    # 3. Market fee & perishability
    comm_rate = float(overrides.get("commission_rate", config.get("market_fees", {}).get("apmc_cess_percentage", 1.5))) / 100.0
    perishability_rates = config.get("crop_perishability_daily_rate", {})
    daily_spoilage = float(overrides.get("spoilage_rate", perishability_rates.get(crop, 0.005)))

    # 4. Resolve origin
    if origin_lat is None or origin_lng is None:
        origin_lat, origin_lng = get_origin_coords(district)

    # 5. Fetch candidate prices and mandi metadata
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

    now_date = datetime.now().date()
    evaluated: List[Dict[str, Any]] = []

    for row in prices:
        market = row["market"]
        m_info = matrix_map.get(market, {})
        m_lat = m_info.get("lat", 18.5)
        m_lng = m_info.get("lng", 73.8)
        cutoff_str = m_info.get("auction_cutoff", "12:00")
        cutoff_hour = parse_time_str(cutoff_str)

        # Distance & transit
        distance_km = haversine_distance(origin_lat, origin_lng, m_lat, m_lng)
        travel_hours = round(max(0.2, distance_km / max(10.0, avg_speed)), 1)
        arrival_hour = departure_hour + travel_hours

        # Cutoff check: if arrival is after auction cutoff, must sell Day+1
        missed_cutoff = arrival_hour > cutoff_hour
        extra_holding_cost = overnight_rate if missed_cutoff else 0.0
        effective_spoilage_hours = travel_hours + (16.0 if missed_cutoff else 0.0)

        # Base price (modal)
        gross_price = float(row["modal_price"])
        
        # Cautious haircut for far markets (> 60 km)
        is_far = distance_km > 60.0
        haircut = config.get("operational", {}).get("cautious_forecast_haircut", 0.04) if is_far else 0.0
        expected_price = round(gross_price * (1.0 - haircut), 2)

        # Cost deductions per quintal
        # Total roundtrip or hired transport distributed over batch quantity
        batch_qty = max(1.0, quantity_quintals)
        transport_cost = round((distance_km * rate_per_km * 2.0) / batch_qty, 2)
        handling_cost = round(loading_rate + unloading_rate + extra_holding_cost, 2)
        commission_cost = round(expected_price * comm_rate, 2)
        spoilage_cost = round(expected_price * (effective_spoilage_hours / 24.0) * daily_spoilage, 2)

        total_deductions = round(transport_cost + handling_cost + commission_cost + spoilage_cost, 2)
        net_return = round(expected_price - total_deductions, 2)
        total_earnings = round(net_return * batch_qty, 2)

        # Freshness & confidence score
        arr_date = datetime.strptime(row["arrival_date"], "%Y-%m-%d").date()
        days_ago = max(0, (now_date - arr_date).days)
        if days_ago <= 1:
            confidence = "HIGH"
        elif days_ago <= 3:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        evaluated.append({
            "market": market,
            "district": row["district"],
            "distance_km": distance_km,
            "travel_hours": travel_hours,
            "arrival_hour": f"{int(arrival_hour):02d}:{int((arrival_hour % 1) * 60):02d}",
            "auction_cutoff": cutoff_str,
            "missed_cutoff": missed_cutoff,
            "gross_modal_price": gross_price,
            "expected_price": expected_price,
            "price_range": {
                "min": float(row["min_price"]),
                "modal": gross_price,
                "max": float(row["max_price"])
            },
            "costs": {
                "transport_per_q": transport_cost,
                "handling_per_q": handling_cost,
                "commission_per_q": commission_cost,
                "spoilage_per_q": spoilage_cost,
                "total_deductions_per_q": total_deductions
            },
            "net_return_per_quintal": net_return,
            "total_net_earnings": total_earnings,
            "confidence": confidence,
            "days_ago": days_ago,
            "arrival_date": row["arrival_date"],
            "source": row["source"],
            "is_sample": bool(row["is_sample"])
        })

    # Sort descending by net return
    evaluated.sort(key=lambda x: x["net_return_per_quintal"], reverse=True)

    # Identify nearest mandi to calculate break-even for all others
    nearest_mandi = min(evaluated, key=lambda x: x["distance_km"])
    nearest_net = nearest_mandi["net_return_per_quintal"]

    for item in evaluated:
        if item["market"] == nearest_mandi["market"]:
            item["break_even_price"] = item["gross_modal_price"]
            item["is_nearest"] = True
        else:
            item["is_nearest"] = False
            # Price needed at this mandi to match the nearest mandi's net return:
            # P_be * (1 - comm_rate - spoilage_factor) = nearest_net + transport + handling
            spoil_factor = (parse_time_str(item["travel_hours"] if isinstance(item["travel_hours"], str) else f"{item['travel_hours']}:00") / 24.0) * daily_spoilage
            denom = max(0.5, 1.0 - comm_rate - spoil_factor)
            be_price = (nearest_net + item["costs"]["transport_per_q"] + item["costs"]["handling_per_q"]) / denom
            item["break_even_price"] = round(be_price, 2)

    best = evaluated[0]
    gain_vs_nearest = round(best["net_return_per_quintal"] - nearest_net, 2)
    
    if best["market"] == nearest_mandi["market"]:
        verdict = f"Sell at {best['market']}: Closest distance saves transport and avoids travel spoilage."
    else:
        verdict = f"Travel to {best['market']}: Premium price gains +₹{gain_vs_nearest}/q net profit above local market."

    best["verdict_reason"] = verdict
    best["gain_vs_nearest_per_quintal"] = gain_vs_nearest

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
        "comparisons": evaluated[1:] if len(evaluated) > 1 else []
    }
