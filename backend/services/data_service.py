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
    """Returns data source status, row counts, latest update timestamp, and monitoring health.
    
    Strictly reports source 'sample' and is_sample=True whenever any sample rows exist.
    """
    sample_check = fetch_one("""
        SELECT COUNT(*) as sample_count
        FROM mandi_prices
        WHERE is_sample = 1 OR source = 'sample'
    """)
    has_sample = bool(sample_check and sample_check["sample_count"] > 0)

    summary = fetch_one("""
        SELECT 
            COUNT(*) as total_records,
            MAX(arrival_date) as latest_date,
            COUNT(DISTINCT market) as monitored_mandis,
            COUNT(DISTINCT commodity) as monitored_crops
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

    if has_sample:
        active_source = "sample"
        is_sample_flag = True
    else:
        source_row = fetch_one("""
            SELECT source FROM mandi_prices
            WHERE is_sample = 0
            ORDER BY CASE
                WHEN source = 'live' THEN 1
                WHEN source = 'manual_csv' THEN 2
                WHEN source = 'snapshot' THEN 3
                ELSE 4 END
            LIMIT 1
        """)
        active_source = source_row["source"] if source_row and source_row["source"] else "snapshot"
        is_sample_flag = False

    return {
        "status": "ready",
        "source": active_source,
        "total_records": summary["total_records"],
        "latest_date": summary["latest_date"],
        "monitored_mandis": summary["monitored_mandis"],
        "monitored_crops": summary["monitored_crops"],
        "is_sample": is_sample_flag
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


from backend.services.agmarknet_fetcher import get_canonical_commodity_name


def get_mandis(crop: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns metadata for all mandis, optionally filtered by commodity."""
    matrix = load_mandi_matrix()
    matrix_map = {m["market"]: m for m in matrix.get("mandis", [])}

    if crop:
        canonical = get_canonical_commodity_name(crop)
        rows = fetch_all("""
            SELECT DISTINCT market, district
            FROM mandi_prices
            WHERE commodity = ? OR commodity = ?
        """, (crop, canonical))
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
    canonical = get_canonical_commodity_name(crop)
    rows = fetch_all("""
        SELECT mp.*
        FROM mandi_prices mp
        INNER JOIN (
            SELECT market, MAX(arrival_date) as max_date
            FROM mandi_prices
            WHERE commodity = ? OR commodity = ?
            GROUP BY market
        ) latest ON mp.market = latest.market AND mp.arrival_date = latest.max_date
        WHERE mp.commodity = ? OR mp.commodity = ?
        ORDER BY mp.modal_price DESC
    """, (crop, canonical, crop, canonical))
    return rows

