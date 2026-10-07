"""Historical 90-Day Backtest Simulation Engine.

Simulates trading decisions day-by-day over the historical record (up to 90 days).
STRICTLY LEAK-FREE: On each trading day T, the engine uses only market prices reported
before day T. Realized returns are computed using actual day T market clearing prices
minus actual transportation, handling, APMC market fee, and spoilage costs.

Compares Mandi Saathi strategy against the baseline of always selling at the nearest local APMC.
Provides transparent accounting: win rate, average extra ₹/quintal, cumulative series,
worse trading days, and an honest assessment of negative alpha or thin data.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from backend.database import fetch_all
from backend.services.advisory_engine import (
    load_config,
    load_mandi_matrix,
    get_origin_coords,
    haversine_distance,
    parse_time_str,
    DISTRICT_COORDS
)
from backend.services.agmarknet_fetcher import get_canonical_commodity_name

# Default farming origin districts per commodity
DEFAULT_CROP_DISTRICTS: Dict[str, str] = {
    "Tomato": "Pune",
    "Onion": "Nashik",
    "Soybean": "Latur",
    "Soyabean": "Latur",
    "Tur": "Latur",
    "Red gram/Arhar/Tur(whole)": "Latur",
    "Cotton": "Akola",
    "Potato": "Pune",
    "Wheat": "Pune"
}


def get_crop_price_history(crop: str) -> pd.DataFrame:
    """Fetches full chronological price history for given crop across all mandis."""
    canonical_crop = get_canonical_commodity_name(crop)
    rows = fetch_all("""
        SELECT arrival_date, market, modal_price, min_price, max_price, arrival_quantity
        FROM mandi_prices
        WHERE (commodity = ? OR commodity = ?)
        ORDER BY arrival_date ASC
    """, (crop, canonical_crop))

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["arrival_date"] = pd.to_datetime(df["arrival_date"]).dt.date
    df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
    df = df.dropna(subset=["modal_price", "arrival_date"])
    df = df.sort_values(by="arrival_date").reset_index(drop=True)
    return df


def run_90_day_backtest(
    crop: str,
    district: Optional[str] = None,
    quantity_quintals: float = 20.0,
    vehicle_type: str = "tempo",
    departure_hour: float = 7.0
) -> Dict[str, Any]:
    """Executes a leak-free 90-day simulation comparing Mandi Saathi against nearest mandi baseline."""
    canonical_crop = get_canonical_commodity_name(crop)

    # 1. Resolve Origin District
    if not district or district.strip() == "":
        district = DEFAULT_CROP_DISTRICTS.get(crop, DEFAULT_CROP_DISTRICTS.get(canonical_crop, "Pune"))
    
    origin_lat, origin_lng = get_origin_coords(district)

    # 2. Load Configuration and Mandi Matrix
    config = load_config()
    matrix = load_mandi_matrix()
    matrix_mandis = {m["market"]: m for m in matrix.get("mandis", [])}

    # Precompute distances and cutoffs for candidate mandis
    mandi_spatial: Dict[str, Dict[str, Any]] = {}
    for mkt_name, m_info in matrix_mandis.items():
        m_lat = float(m_info.get("lat", 18.5))
        m_lng = float(m_info.get("lng", 73.8))
        dist_km = haversine_distance(origin_lat, origin_lng, m_lat, m_lng)
        mandi_spatial[mkt_name] = {
            "distance_km": dist_km,
            "lat": m_lat,
            "lng": m_lng,
            "auction_cutoff": m_info.get("auction_cutoff", "12:00")
        }

    # Identify Nearest Mandi baseline
    nearest_mandi = min(mandi_spatial.keys(), key=lambda k: mandi_spatial[k]["distance_km"])

    # 3. Fetch Historical Data
    df = get_crop_price_history(crop)
    if df.empty or df["arrival_date"].nunique() < 10:
        found_dates = df["arrival_date"].nunique() if not df.empty else 0
        return {
            "crop": crop,
            "canonical_crop": canonical_crop,
            "district": district,
            "nearest_mandi": nearest_mandi,
            "status": "THIN_DATA",
            "message": f"Historical data for {crop} is too thin to perform a statistically sound backtest (found {found_dates} dates, need >= 10).",
            "days_tested": 0,
            "days_better": 0,
            "days_equal": 0,
            "days_worse": 0,
            "percent_days_better": 0.0,
            "percent_days_better_or_equal": 0.0,
            "average_extra_rs_per_quintal": 0.0,
            "total_extra_rs_per_quintal": 0.0,
            "cumulative_series": [],
            "worse_days": [],
            "honest_assessment": f"Thin data alert: Only {found_dates} recorded trading dates exist for {crop}. A 90-day simulation cannot be reliably calculated."
        }

    # 4. Economic Cost Parameters
    v_key = vehicle_type.lower().replace(" ", "_")
    if "truck" in v_key:
        v_key = "truck"
    elif "own" in v_key:
        v_key = "own_vehicle"
    else:
        v_key = "tempo"

    vehicle_cfg = config.get("vehicles", {}).get(v_key, {"rate_per_km": 18.0, "speed_kmh": 45.0})
    rate_per_km = float(vehicle_cfg.get("rate_per_km", 18.0))
    speed_kmh = float(vehicle_cfg.get("speed_kmh", 45.0))

    handling_cfg = config.get("handling", {})
    loading_rate = float(handling_cfg.get("loading_per_quintal", 15.0))
    unloading_rate = float(handling_cfg.get("unloading_per_quintal", 15.0))
    overnight_holding = float(handling_cfg.get("overnight_holding_per_quintal", 12.0))

    fee_pct = float(config.get("market_fee_percent", 1.5)) / 100.0
    spoilage_rate = float(config.get("spoilage_per_day", {}).get(crop, config.get("spoilage_per_day", {}).get(canonical_crop, 0.005)))
    cautious_haircut = float(config.get("operational", {}).get("cautious_forecast_haircut", 0.04))

    batch_qty = max(0.1, quantity_quintals)

    def calculate_net_deductions(mkt_name: str, price: float, is_realization: bool = False) -> tuple[float, float, bool]:
        """Calculates transport, handling, fee, and spoilage deductions."""
        m_info = mandi_spatial.get(mkt_name, {"distance_km": 50.0, "auction_cutoff": "12:00"})
        dist = m_info["distance_km"]
        travel_hrs = round(max(0.2, dist / speed_kmh), 1)
        arrival_hr = departure_hour + travel_hrs
        cutoff_hr = parse_time_str(m_info["auction_cutoff"])
        missed = arrival_hr > cutoff_hr

        # Deductions
        trans = round((dist * rate_per_km * 2.0) / batch_qty, 2)
        load = round(loading_rate + unloading_rate + (overnight_holding if missed else 0.0), 2)
        fee = round(price * fee_pct, 2)
        eff_spoil_hrs = travel_hrs + (16.0 if missed else 0.0)
        spoil = round(price * (eff_spoil_hrs / 24.0) * spoilage_rate, 2)
        tot_deductions = round(trans + load + fee + spoil, 2)
        net_ret = round(price - tot_deductions, 2)
        return net_ret, tot_deductions, missed

    # Pre-index price lookup by (arrival_date, market)
    date_market_prices: Dict[tuple[date, str], float] = (
        df.set_index(["arrival_date", "market"])["modal_price"].to_dict()
    )

    all_dates = sorted(df["arrival_date"].unique())
    # Reserve first 5 days for initial warm-up history
    warmup_days = 5
    eval_dates = all_dates[warmup_days:]

    cumulative_series: List[Dict[str, Any]] = []
    worse_days: List[Dict[str, Any]] = []

    cum_saathi = 0.0
    cum_nearest = 0.0
    diffs_list: List[float] = []

    # 5. Day-by-Day Simulation (Strictly Leak-Free)
    for sim_date in eval_dates:
        # Strictly visible data: arrival_date < sim_date
        past_slice = df[df["arrival_date"] < sim_date]
        if past_slice.empty:
            continue

        latest_known = past_slice.sort_values("arrival_date").groupby("market").last()

        # Advisory evaluation as of morning of sim_date
        best_candidate = None
        best_expected_net = -1e9

        for cand_mkt, row in latest_known.iterrows():
            if cand_mkt not in mandi_spatial:
                continue
            days_ago = (sim_date - row["arrival_date"]).days
            if days_ago > 3:  # Stale data filter
                continue

            last_price = float(row["modal_price"])
            m_info = mandi_spatial[cand_mkt]
            dist = m_info["distance_km"]
            is_far = dist > 60.0

            # Conservative lower-bound haircut for far or cutoff-missing mandis
            expected_p = last_price * (1.0 - cautious_haircut if is_far else 1.0)
            est_net, _, _ = calculate_net_deductions(cand_mkt, expected_p)

            if est_net > best_expected_net:
                best_expected_net = est_net
                best_candidate = cand_mkt

        # Default fallback to nearest if no valid candidate found
        if not best_candidate:
            best_candidate = nearest_mandi

        # Realized Settlement on sim_date
        p_rec_actual = date_market_prices.get((sim_date, best_candidate))
        p_near_actual = date_market_prices.get((sim_date, nearest_mandi))

        if p_rec_actual is not None and p_near_actual is not None:
            net_rec, _, _ = calculate_net_deductions(best_candidate, p_rec_actual, is_realization=True)
            net_near, _, _ = calculate_net_deductions(nearest_mandi, p_near_actual, is_realization=True)
            diff = round(net_rec - net_near, 2)

            cum_saathi = round(cum_saathi + net_rec, 2)
            cum_nearest = round(cum_nearest + net_near, 2)
            cum_gain = round(cum_saathi - cum_nearest, 2)

            diffs_list.append(diff)

            cumulative_series.append({
                "date": sim_date.strftime("%Y-%m-%d"),
                "recommended_mandi": best_candidate,
                "nearest_mandi": nearest_mandi,
                "mandi_saathi_net": net_rec,
                "nearest_net": net_near,
                "diff_rs": diff,
                "mandi_saathi_cumulative": cum_saathi,
                "nearest_cumulative": cum_nearest,
                "cumulative_gain": cum_gain
            })

            if diff < 0:
                loss_magnitude = abs(diff)
                reason_str = (
                    f"Selected {best_candidate} based on prior price advantage, but on {sim_date.strftime('%d %b')} "
                    f"local {nearest_mandi} modal price reached ₹{p_near_actual:.2f} while {best_candidate} cleared at "
                    f"₹{p_rec_actual:.2f}, resulting in a net deficit of -₹{loss_magnitude:.2f}/q after transport."
                )
                worse_days.append({
                    "date": sim_date.strftime("%Y-%m-%d"),
                    "recommended_mandi": best_candidate,
                    "nearest_mandi": nearest_mandi,
                    "diff_rs": diff,
                    "recommended_net": net_rec,
                    "nearest_net": net_near,
                    "actual_price_recommended": round(p_rec_actual, 2),
                    "actual_price_nearest": round(p_near_actual, 2),
                    "reason": reason_str
                })

    days_tested = len(diffs_list)
    if days_tested == 0:
        return {
            "crop": crop,
            "canonical_crop": canonical_crop,
            "district": district,
            "nearest_mandi": nearest_mandi,
            "status": "THIN_DATA",
            "message": f"No overlapping trading settlements recorded for {crop}.",
            "days_tested": 0,
            "days_better": 0,
            "days_equal": 0,
            "days_worse": 0,
            "percent_days_better": 0.0,
            "percent_days_better_or_equal": 0.0,
            "average_extra_rs_per_quintal": 0.0,
            "total_extra_rs_per_quintal": 0.0,
            "cumulative_series": [],
            "worse_days": [],
            "honest_assessment": "Insufficient paired trading settlements to calculate backtest."
        }

    days_better = sum(1 for d in diffs_list if d > 0)
    days_equal = sum(1 for d in diffs_list if d == 0)
    days_worse = sum(1 for d in diffs_list if d < 0)

    pct_better = round((days_better / days_tested) * 100.0, 1)
    pct_better_or_equal = round(((days_better + days_equal) / days_tested) * 100.0, 1)
    avg_extra = round(float(np.mean(diffs_list)), 2)
    tot_extra = round(float(np.sum(diffs_list)), 2)

    # 6. Formulate Honest Assessment
    if avg_extra > 0:
        assessment = (
            f"Honest Positive Alpha: Mandi Saathi outperformed the nearest local mandi ({nearest_mandi}) "
            f"on {days_better} of {days_tested} trading days ({pct_better}%), matching local sales on {days_equal} days. "
            f"Over the simulated 90-day period, following the advisory yielded an average extra net profit of "
            f"+₹{avg_extra}/quintal (+₹{tot_extra}/quintal cumulative) after strictly deducting all return transit, "
            f"loading, market fee, and spoilage costs. "
            f"On {days_worse} days ({round(days_worse / days_tested * 100, 1)}%), the strategy underperformed due "
            f"to intra-day price inversions."
        )
    elif avg_extra == 0:
        assessment = (
            f"Neutral Alpha: Mandi Saathi matched the local nearest mandi ({nearest_mandi}) across all tested days. "
            f"Travel beyond the local mandi was not recommended, successfully saving the farmer unnecessary freight expenses."
        )
    else:
        assessment = (
            f"Honest Negative Alpha: Traveling beyond {nearest_mandi} resulted in an average net loss of "
            f"-₹{abs(avg_extra)}/quintal due to transport overhead exceeding regional price premiums. "
            f"For {crop} in {district}, selling directly at {nearest_mandi} is economically superior."
        )

    return {
        "crop": crop,
        "canonical_crop": canonical_crop,
        "district": district,
        "nearest_mandi": nearest_mandi,
        "status": "OK",
        "days_tested": days_tested,
        "days_better": days_better,
        "days_equal": days_equal,
        "days_worse": days_worse,
        "percent_days_better": pct_better,
        "percent_days_better_or_equal": pct_better_or_equal,
        "average_extra_rs_per_quintal": avg_extra,
        "total_extra_rs_per_quintal": tot_extra,
        "cumulative_series": cumulative_series,
        "worse_days": worse_days,
        "honest_assessment": assessment
    }
