"""Data service layer providing unified query access to mandi prices, metadata, and data health."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config import DATA_DIR
from backend.database import fetch_all, fetch_one

MATRIX_PATH = DATA_DIR / "mandi_matrix.json"


def load_mandi_matrix() -> Dict[str, Any]:
    """Loads mandi matrix containing locations, cutoffs, and supported crops."""
    if not MATRIX_PATH.exists():
        return {"mandis": []}
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_data_status() -> Dict[str, Any]:
    """Returns data source status, row counts, latest update timestamp, and monitoring health."""
    summary = fetch_one("""
        SELECT 
            COUNT(*) as total_records,
            MAX(arrival_date) as latest_date,
            COUNT(DISTINCT market) as monitored_mandis,
            COUNT(DISTINCT commodity) as monitored_crops,
            source,
            is_sample
        FROM mandi_prices
    """)
    
    if not summary or summary["total_records"] == 0:
        return {
            "status": "empty",
            "source": "none",
            "total_records": 0,
            "latest_date": None,
            "monitored_mandis": 0,
            "monitored_crops": 0,
            "is_sample": False
        }

    return {
        "status": "ready",
        "source": summary["source"] or "snapshot",
        "total_records": summary["total_records"],
        "latest_date": summary["latest_date"],
        "monitored_mandis": summary["monitored_mandis"],
        "monitored_crops": summary["monitored_crops"],
        "is_sample": bool(summary["is_sample"])
    }


def get_crops() -> List[Dict[str, Any]]:
    """Returns list of distinct supported commodities and their market availability."""
    rows = fetch_all("""
        SELECT 
            commodity,
            COUNT(DISTINCT market) as mandi_count,
            MAX(arrival_date) as latest_date,
            ROUND(AVG(modal_price), 2) as avg_price
        FROM mandi_prices
        GROUP BY commodity
        ORDER BY mandi_count DESC
    """)
    return rows


def get_mandis(crop: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns metadata for all mandis, optionally filtered by commodity."""
    matrix = load_mandi_matrix()
    matrix_map = {m["market"]: m for m in matrix.get("mandis", [])}

    if crop:
        rows = fetch_all("""
            SELECT DISTINCT market, district
            FROM mandi_prices
            WHERE commodity = ?
        """, (crop,))
    else:
        rows = fetch_all("""
            SELECT DISTINCT market, district
            FROM mandi_prices
        """)

    results = []
    for row in rows:
        mkt = row["market"]
        info = matrix_map.get(mkt, {})
        results.append({
            "market": mkt,
            "district": row["district"],
            "lat": info.get("lat", 19.0),
            "lng": info.get("lng", 74.0),
            "auction_cutoff": info.get("auction_cutoff", "12:00")
        })
    return results


def get_latest_prices_for_crop(crop: str) -> List[Dict[str, Any]]:
    """Returns the most recent price record per mandi for a given crop."""
    rows = fetch_all("""
        SELECT mp.*
        FROM mandi_prices mp
        INNER JOIN (
            SELECT market, MAX(arrival_date) as max_date
            FROM mandi_prices
            WHERE commodity = ?
            GROUP BY market
        ) latest ON mp.market = latest.market AND mp.arrival_date = latest.max_date
        WHERE mp.commodity = ?
        ORDER BY mp.modal_price DESC
    """, (crop, crop))
    return rows
