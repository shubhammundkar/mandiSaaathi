"""Price Forecasting & Sell-or-Store Decision Engine.

Generates 5-day price corridors (Low, Likely, High) using rolling moving average,
linear momentum trend, and weekday seasonality adjustments. Implements economic
sell-or-store optimization for non-perishable commodities (Onion, Soybean, Tur, Potato, Wheat).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from backend.database import fetch_all
from backend.services.advisory_engine import load_config
from backend.services.agmarknet_fetcher import get_canonical_commodity_name

STORAGE_ELIGIBLE_CROPS = {
    "Onion",
    "Soybean",
    "Soyabean",
    "Tur",
    "Red gram/Arhar/Tur(whole)",
    "Potato",
    "Wheat"
}


def get_mandi_price_history(crop: str, market: str) -> pd.DataFrame:
    """Fetches chronological price history for given crop and mandi."""
    canonical_crop = get_canonical_commodity_name(crop)
    rows = fetch_all("""
        SELECT arrival_date, min_price, max_price, modal_price, arrival_quantity
        FROM mandi_prices
        WHERE (commodity = ? OR commodity = ?) AND market = ?
        ORDER BY arrival_date ASC
    """, (crop, canonical_crop, market))

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["arrival_date"] = pd.to_datetime(df["arrival_date"])
    df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")
    df = df.dropna(subset=["modal_price", "arrival_date"])
    df = df.sort_values(by="arrival_date").reset_index(drop=True)
    return df


def forecast_5_days(crop: str, market: str) -> Dict[str, Any]:
    """Generates 5-day Low, Likely, and High price outlook using moving averages,

    trend extrapolation, and weekday seasonality. Never returns a single deterministic number.
    """
    df = get_mandi_price_history(crop, market)
    canonical_crop = get_canonical_commodity_name(crop)

    if df.empty or len(df) < 7:
        return {
            "crop": crop,
            "market": market,
            "status": "NOT_ENOUGH_DATA",
            "confidence": "LOW",
            "message": f"Insufficient historical records for {crop} in {market} (need >= 7 days).",
            "forecast": []
        }

    prices = df["modal_price"].values
    n = len(prices)
    latest_date = df["arrival_date"].iloc[-1].date()
    current_price = float(prices[-1])

    # 1. 7-day Moving Average baseline
    ma_window = min(7, n)
    ma_current = float(np.mean(prices[-ma_window:]))

    # 2. Linear Trend Estimation (Slope over last 14 days)
    trend_window = min(14, n)
    recent_x = np.arange(trend_window)
    recent_y = prices[-trend_window:]
    if len(recent_x) > 1:
        slope, _ = np.polyfit(recent_x, recent_y, 1)
    else:
        slope = 0.0

    # Cap daily slope at +/- 2.5% of current price to avoid runaway extrapolation
    max_drift = current_price * 0.025
    clamped_slope = max(-max_drift, min(max_drift, slope))

    if clamped_slope > current_price * 0.005:
        trend_label = "BULLISH"
    elif clamped_slope < -current_price * 0.005:
        trend_label = "BEARISH"
    else:
        trend_label = "STABLE"

    # 3. Day-of-week Seasonality Index
    df["weekday"] = df["arrival_date"].dt.weekday  # 0=Mon, 6=Sun
    weekday_means = df.groupby("weekday")["modal_price"].mean().to_dict()
    overall_mean = float(np.mean(prices))

    # 4. Residual Volatility for Forecast Range Bands
    residuals = []
    for i in range(1, n):
        pred_i = prices[i - 1] + clamped_slope
        residuals.append(prices[i] - pred_i)
    sigma = float(np.std(residuals)) if len(residuals) > 2 else (current_price * 0.03)
    sigma = max(current_price * 0.02, sigma)  # Floor at 2% price spread

    # 5. Build 5-Day Forward Corridor (Skipping Sundays)
    forecast_points = []
    curr_date = latest_date

    step = 1
    while len(forecast_points) < 5:
        curr_date += timedelta(days=1)
        # APMC mandis are closed on Sunday (weekday == 6)
        if curr_date.weekday() == 6:
            continue

        weekday_idx = curr_date.weekday()
        # Seasonal multiplier
        w_factor = 1.0
        if overall_mean > 0 and weekday_idx in weekday_means:
            w_factor = float(weekday_means[weekday_idx] / overall_mean)
            # Damping seasonality extremes
            w_factor = 1.0 + (w_factor - 1.0) * 0.5

        # Base likely price projection
        projected_likely = (current_price + clamped_slope * step) * w_factor
        projected_likely = round(max(current_price * 0.5, projected_likely), 2)

        # Corridor widens with square root of time
        spread = 1.645 * sigma * math.sqrt(1.0 + 0.15 * step)
        low_price = round(max(current_price * 0.4, projected_likely - spread), 2)
        high_price = round(projected_likely + spread, 2)

        # Ensure low < likely < high strictly holds
        if low_price >= projected_likely:
            low_price = round(projected_likely * 0.96, 2)
        if high_price <= projected_likely:
            high_price = round(projected_likely * 1.04, 2)

        weekday_name = curr_date.strftime("%A")
        forecast_points.append({
            "day": f"Day {len(forecast_points) + 1}",
            "day_offset": step,
            "date": curr_date.strftime("%Y-%m-%d"),
            "weekday": weekday_name,
            "low": low_price,
            "likely": projected_likely,
            "high": high_price
        })
        step += 1

    # Confidence label based on sample size and volatility
    rel_volatility = sigma / current_price
    days_since_latest = (datetime.now().date() - latest_date).days

    if days_since_latest <= 1 and n >= 25 and rel_volatility <= 0.08:
        confidence = "HIGH"
    elif days_since_latest <= 3 and n >= 12:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "crop": crop,
        "canonical_crop": canonical_crop,
        "market": market,
        "status": "OK",
        "current_price": current_price,
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "trend": trend_label,
        "confidence": confidence,
        "volatility_percentage": round(rel_volatility * 100, 1),
        "forecast": forecast_points
    }


def get_storage_advice(crop: str, market: Optional[str] = None) -> Dict[str, Any]:
    """Evaluates whether to sell today versus hold/store for 1 to 5 days,

    deducting warehouse costs and moisture/quality shrinkage.
    """
    config = load_config()
    storage_cfg = config.get("storage", {})
    daily_cost_map = storage_cfg.get("daily_cost_per_quintal", {})
    daily_loss_map = storage_cfg.get("daily_quality_loss_rate", {})
    min_gain_threshold = float(storage_cfg.get("min_gain_threshold_per_quintal", 25.0))

    canonical_crop = get_canonical_commodity_name(crop)

    # 1. Non-storage eligible crops (e.g. Tomato)
    if crop not in STORAGE_ELIGIBLE_CROPS and canonical_crop not in STORAGE_ELIGIBLE_CROPS:
        return {
            "crop": crop,
            "market": market or "All Mandis",
            "is_storage_viable": False,
            "recommendation": "Sell now",
            "best_wait_days": 0,
            "net_benefit_per_quintal": 0.0,
            "rationale": f"{crop} is perishable and cannot be stored on farm. Selling immediately avoids severe transit and holding spoilage."
        }

    # 2. Resolve default market if not provided
    if not market:
        # Find market with highest recent record density
        best_mkt_row = fetch_all("""
            SELECT market, COUNT(*) as cnt
            FROM mandi_prices
            WHERE commodity = ? OR commodity = ?
            GROUP BY market
            ORDER BY cnt DESC
            LIMIT 1
        """, (crop, canonical_crop))
        if best_mkt_row:
            market = best_mkt_row[0]["market"]
        else:
            market = "Pune"

    # 3. Fetch 5-day forecast
    fc = forecast_5_days(crop, market)
    if fc.get("status") == "NOT_ENOUGH_DATA" or not fc.get("forecast"):
        return {
            "crop": crop,
            "market": market,
            "is_storage_viable": True,
            "recommendation": "Not enough data",
            "best_wait_days": 0,
            "net_benefit_per_quintal": 0.0,
            "rationale": f"Insufficient historical data in {market} to calculate reliable storage return."
        }

    current_price = fc["current_price"]
    daily_storage_rate = float(daily_cost_map.get(crop, daily_cost_map.get(canonical_crop, 0.40)))
    daily_loss_rate = float(daily_loss_map.get(crop, daily_loss_map.get(canonical_crop, 0.0005)))

    best_wait_days = 0
    max_net_gain = 0.0
    best_step_metrics = None

    steps_evaluation = []

    for item in fc["forecast"]:
        n_days = item["day_offset"]
        likely_future_price = item["likely"]
        gross_gain = likely_future_price - current_price

        # Storage costs over n days
        storage_cost = round(n_days * daily_storage_rate, 2)
        # Quality & moisture shrinkage deduction
        quality_loss = round(current_price * (n_days * daily_loss_rate), 2)

        net_gain = round(gross_gain - storage_cost - quality_loss, 2)

        step_record = {
            "wait_days": n_days,
            "forecasted_likely": likely_future_price,
            "gross_gain_per_q": round(gross_gain, 2),
            "storage_cost_per_q": storage_cost,
            "quality_loss_per_q": quality_loss,
            "net_benefit_per_q": net_gain
        }
        steps_evaluation.append(step_record)

        if net_gain > max_net_gain:
            max_net_gain = net_gain
            best_wait_days = n_days
            best_step_metrics = step_record

    # 4. Formulate Decision
    if max_net_gain >= min_gain_threshold and best_wait_days > 0 and best_step_metrics is not None:
        rec = f"Wait {best_wait_days} days"
        rationale = (
            f"Holding for {best_wait_days} days nets +₹{max_net_gain}/q extra profit. "
            f"Expected price rise (+₹{best_step_metrics['gross_gain_per_q']}/q) significantly covers "
            f"storage charges (₹{best_step_metrics['storage_cost_per_q']}/q) and shrinkage."
        )
    else:
        rec = "Sell now"
        if max_net_gain <= 0:
            rationale = "Projected market trend does not cover storage and quality shrinkage costs. Selling today maximizes return."
        else:
            rationale = f"Holding yields only marginal net gain (+₹{max_net_gain}/q), which does not justify price volatility risk. Selling today is recommended."

    return {
        "crop": crop,
        "market": market,
        "is_storage_viable": True,
        "recommendation": rec,
        "current_price": current_price,
        "best_wait_days": best_wait_days,
        "net_benefit_per_quintal": max_net_gain,
        "confidence": fc["confidence"],
        "rationale": rationale,
        "evaluation_steps": steps_evaluation
    }


def get_forecast_lower_bound(crop: str, market: str, day_offset: int = 1) -> Optional[float]:
    """Provides conservative lower-bound forecast price for arrival day.

    Wired directly into advisory engine for next-day and far mandi evaluations.
    """
    fc = forecast_5_days(crop, market)
    if fc.get("status") == "OK" and fc.get("forecast"):
        # Match day_offset or take first item
        for item in fc["forecast"]:
            if item["day_offset"] >= day_offset:
                return float(item["low"])
        return float(fc["forecast"][0]["low"])
    return None
