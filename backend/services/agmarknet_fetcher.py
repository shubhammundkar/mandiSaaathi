"""Agmarknet Data Fetcher Service.

Fetches, normalizes, cleans, and dedupes mandi commodity price data using the
official/unofficial `agmarknet` package, with graceful fallback to local
verified historical snapshot data when the remote API enforces CAPTCHA or times out.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.config import BASE_DIR, DATA_DIR

logger = logging.getLogger(__name__)

# Exact commodity names matching package filter tables (agmarknet.filters)
COMMODITY_MAP: Dict[str, str] = {
    "Tomato": "Tomato",
    "Onion": "Onion",
    "Soybean": "Soyabean",
    "Soyabean": "Soyabean",
    "Tur": "Red gram/Arhar/Tur(whole)",
    "Arhar": "Red gram/Arhar/Tur(whole)",
    "Red gram/Arhar/Tur(whole)": "Red gram/Arhar/Tur(whole)",
    "Cotton": "Cotton",
    "Potato": "Potato",
    "Wheat": "Wheat",
}

DEFAULT_STATE = "Maharashtra"
SNAPSHOT_PATH = DATA_DIR / "agmarknet_maharashtra_snapshot.csv"


def get_canonical_commodity_name(commodity: str) -> str:
    """Resolves commodity input to exact agmarknet filter name."""
    clean = commodity.strip()
    return COMMODITY_MAP.get(clean, clean)


def chunk_date_range(from_date: str, to_date: str, chunk_days: int = 30) -> List[tuple[str, str]]:
    """Splits date range into chunks of up to `chunk_days` days."""
    start = datetime.strptime(from_date, "%Y-%m-%d").date()
    end = datetime.strptime(to_date, "%Y-%m-%d").date()
    
    chunks = []
    current_start = start
    while current_start <= end:
        current_end = min(current_start + timedelta(days=chunk_days - 1), end)
        chunks.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
        current_start = current_end + timedelta(days=1)
    return chunks


def fetch_from_snapshot(commodity_name: str, from_date: str, to_date: str) -> pd.DataFrame:
    """Fallback reader from verified offline snapshot.
    
    Strictly accepts only real records where is_sample == 0 and source != 'sample'.
    """
    if not SNAPSHOT_PATH.exists():
        logger.warning(f"Snapshot file not found at {SNAPSHOT_PATH}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(SNAPSHOT_PATH)
    except Exception as exc:
        logger.warning(f"Failed to read snapshot file at {SNAPSHOT_PATH}: {exc}")
        return pd.DataFrame()

    if df.empty:
        return df

    # Strictly filter for real rows (is_sample == 0)
    if "is_sample" in df.columns:
        df = df[df["is_sample"] == 0]
    if "source" in df.columns:
        df = df[df["source"] != "sample"]

    if df.empty:
        logger.warning("Snapshot file contains no verified real rows (is_sample=0)")
        return pd.DataFrame()

    # Filter commodity and date range
    mask = (df["commodity"] == commodity_name) & (df["arrival_date"] >= from_date) & (df["arrival_date"] <= to_date)
    filtered = df.loc[mask].copy()
    if not filtered.empty:
        filtered["source"] = "snapshot"
        filtered["is_sample"] = 0
    return filtered


def clean_and_normalize(df: pd.DataFrame, commodity_name: str, source: str = "live") -> pd.DataFrame:
    """Normalizes DataFrame columns to database schema, drops invalid prices,

    removes IQR outliers per crop & market, and dedupes.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "state", "district", "market", "commodity", "variety", "grade",
            "arrival_date", "min_price", "max_price", "modal_price",
            "arrival_quantity", "source", "is_sample", "fetched_at"
        ])

    # Standardize column naming if coming raw from package
    col_mapping = {
        "State": "state",
        "District": "district",
        "Market": "market",
        "Commodity": "commodity",
        "Variety": "variety",
        "Grade": "grade",
        "Arrival_Date": "arrival_date",
        "Min_x0020_Price": "min_price",
        "Max_x0020_Price": "max_price",
        "Modal_x0020_Price": "modal_price",
        "Min Price": "min_price",
        "Max Price": "max_price",
        "Modal Price": "modal_price",
        "Arrivals": "arrival_quantity",
        "arrival_qty": "arrival_quantity",
    }
    df = df.rename(columns=col_mapping)

    # Ensure required columns exist
    if "state" not in df.columns:
        df["state"] = DEFAULT_STATE
    if "commodity" not in df.columns:
        df["commodity"] = commodity_name
    if "variety" not in df.columns:
        df["variety"] = "FAQ"
    if "grade" not in df.columns:
        df["grade"] = "FAQ"
    if "arrival_quantity" not in df.columns:
        df["arrival_quantity"] = 0.0

    # Convert prices to numeric
    for price_col in ["min_price", "max_price", "modal_price", "arrival_quantity"]:
        if price_col in df.columns:
            df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    # Drop zero, negative, or missing prices
    df = df.dropna(subset=["modal_price", "arrival_date", "market"])
    df = df[df["modal_price"] > 0]
    
    # Fill min and max if missing
    df["min_price"] = df["min_price"].fillna(df["modal_price"])
    df["max_price"] = df["max_price"].fillna(df["modal_price"])

    # Ensure min <= modal <= max
    df["min_price"] = df[["min_price", "modal_price"]].min(axis=1)
    df["max_price"] = df[["max_price", "modal_price"]].max(axis=1)

    # Remove IQR Outliers per (commodity, market)
    filtered_groups = []
    for _, group in df.groupby(["commodity", "market"], as_index=False):
        if len(group) >= 4:
            q1 = group["modal_price"].quantile(0.25)
            q3 = group["modal_price"].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                group = group[(group["modal_price"] >= lower_bound) & (group["modal_price"] <= upper_bound)]
        filtered_groups.append(group)
    if filtered_groups:
        df = pd.concat(filtered_groups, ignore_index=True)

    # Deduplicate on (market, commodity, variety, arrival_date)
    df = df.sort_values(by="modal_price", ascending=False)
    df = df.drop_duplicates(subset=["market", "commodity", "variety", "arrival_date"], keep="first")

    # Final metadata fields
    if "source" not in df.columns:
        df["source"] = source
    if "is_sample" not in df.columns:
        df["is_sample"] = 0
    df["fetched_at"] = datetime.now().isoformat()

    cols = [
        "state", "district", "market", "commodity", "variety", "grade",
        "arrival_date", "min_price", "max_price", "modal_price",
        "arrival_quantity", "source", "is_sample", "fetched_at"
    ]
    return df[cols].reset_index(drop=True)


def fetch_prices(
    commodity: str,
    from_date: str,
    to_date: str,
    state: str = DEFAULT_STATE,
    max_retries: int = 2,
    timeout_seconds: float = 8.0,
    chunk_days: int = 30
) -> pd.DataFrame:
    """Fetches commodity prices for Maharashtra across date range in 30-day chunks.
    
    If the package fails or returns nothing:
    - Does NOT silently fall back to generated data.
    - Only falls back to a real snapshot (is_sample=0 rows) if one exists.
    - Otherwise returns the real error.
    """
    target_commodity = get_canonical_commodity_name(commodity)
    date_chunks = chunk_date_range(from_date, to_date, chunk_days=chunk_days)
    
    collected_frames: List[pd.DataFrame] = []
    live_success = False
    last_error: Optional[Exception] = None

    # Attempt fetching using agmarknet package
    try:
        from agmarknet import Agmarknet
        client = Agmarknet()

        for chunk_start, chunk_end in date_chunks:
            chunk_df = None
            for attempt in range(max_retries):
                try:
                    time.sleep(0.3)  # Short delay between calls
                    chunk_df = client.report(
                        commodity=target_commodity,
                        state=state,
                        from_date=chunk_start,
                        to_date=chunk_end,
                        timeout=timeout_seconds
                    )
                    if chunk_df is not None and not chunk_df.empty:
                        collected_frames.append(chunk_df)
                        live_success = True
                    break
                except Exception as exc:
                    last_error = exc
                    logger.warning(f"Live agmarknet attempt {attempt + 1} failed for {chunk_start} to {chunk_end}: {exc}")
                    time.sleep(0.5)

    except Exception as exc:
        last_error = exc
        logger.warning(f"Live agmarknet client unavailable: {exc}")

    # If live returned data, clean and return
    if live_success and collected_frames:
        merged = pd.concat(collected_frames, ignore_index=True)
        return clean_and_normalize(merged, target_commodity, source="live")

    # Fallback route: ONLY fall back to a real snapshot (is_sample=0) if one exists
    snapshot_df = fetch_from_snapshot(target_commodity, from_date, to_date)
    if not snapshot_df.empty:
        logger.info(f"Falling back to verified real offline snapshot (is_sample=0) for {target_commodity} ({from_date} to {to_date})")
        return clean_and_normalize(snapshot_df, target_commodity, source="snapshot")

    # If agmarknet failed or returned nothing and NO real snapshot exists:
    # Do NOT silently fall back to generated data. Return/raise the real error!
    if last_error is not None:
        error_msg = f"Agmarknet package failed for {target_commodity} ({from_date} to {to_date}): {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_error
    else:
        error_msg = f"Agmarknet package returned no data for {target_commodity} ({from_date} to {to_date}), and no verified real snapshot (is_sample=0) exists."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
