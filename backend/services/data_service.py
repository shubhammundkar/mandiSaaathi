import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.config import DATA_DIR
from backend.database import fetch_all, fetch_one, get_db_connection

logger = logging.getLogger(__name__)

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


def _insert_dataframe_to_mandi_prices(df: pd.DataFrame, default_source: str = "snapshot", default_is_sample: int = 0) -> int:
    """Inserts records from a pandas DataFrame into mandi_prices."""
    rows = []
    now_iso = datetime.now().isoformat()
    for _, row in df.iterrows():
        market = str(row.get("market", "")).strip()
        commodity = str(row.get("commodity", "")).strip()
        if not market or not commodity:
            continue
        state = str(row.get("state", "Maharashtra")).strip() or "Maharashtra"
        district = str(row.get("district", market)).strip() or market
        variety = str(row.get("variety", "FAQ")).strip() or "FAQ"
        grade = str(row.get("grade", "FAQ")).strip() or "FAQ"
        arrival_date = str(row.get("arrival_date", "")).strip()
        if not arrival_date:
            continue
        try:
            modal_price = float(row.get("modal_price", 0.0))
            if modal_price <= 0:
                continue
            min_price = float(row.get("min_price", modal_price))
            max_price = float(row.get("max_price", modal_price))
            qty = float(row.get("arrival_quantity", 0.0))
        except (ValueError, TypeError):
            continue
        source = str(row.get("source", default_source)).strip() or default_source
        is_sample = int(row.get("is_sample", default_is_sample))
        fetched_at = str(row.get("fetched_at", now_iso)).strip() or now_iso

        rows.append((
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price, qty,
            source, is_sample, fetched_at
        ))

    if not rows:
        return 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO mandi_prices (
                state, district, market, commodity, variety, grade,
                arrival_date, min_price, max_price, modal_price,
                arrival_quantity, source, is_sample, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
    return len(rows)


def load_initial_data_if_empty() -> Dict[str, Any]:
    """On startup, if mandi_prices is empty:
    1. Loads data/agmarknet_maharashtra_snapshot.csv (real rows) automatically with is_sample=0.
    2. If real snapshot doesn't exist or is empty, loads data/sample_history.csv with is_sample=1.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM mandi_prices")
        count = cursor.fetchone()[0]
        if count > 0:
            return {"status": "already_populated", "count": count}

    snapshot_path = DATA_DIR / "agmarknet_maharashtra_snapshot.csv"
    sample_path = DATA_DIR / "sample_history.csv"

    # 1. Try real snapshot (data/agmarknet_maharashtra_snapshot.csv)
    if snapshot_path.exists():
        try:
            df = pd.read_csv(snapshot_path)
            if not df.empty:
                if "is_sample" in df.columns:
                    df = df[df["is_sample"] == 0]
                else:
                    df["is_sample"] = 0
                
                if not df.empty:
                    inserted = _insert_dataframe_to_mandi_prices(df, default_source="snapshot", default_is_sample=0)
                    logger.info(f"Startup: Loaded {inserted} real records from {snapshot_path.name} into mandi_prices.")
                    return {"status": "loaded_real_snapshot", "count": inserted}
        except Exception as exc:
            logger.warning(f"Error loading real snapshot on startup: {exc}")

    # 2. If only sample data exists (data/sample_history.csv)
    if sample_path.exists():
        try:
            df = pd.read_csv(sample_path)
            if not df.empty:
                df["is_sample"] = 1
                df["source"] = "sample"
                inserted = _insert_dataframe_to_mandi_prices(df, default_source="sample", default_is_sample=1)
                logger.info(f"Startup: Loaded {inserted} sample records from {sample_path.name} into mandi_prices (is_sample=1).")
                return {"status": "loaded_sample_data", "count": inserted}
        except Exception as exc:
            logger.warning(f"Error loading sample data on startup: {exc}")

    return {"status": "no_data_found", "count": 0}


def get_prices(
    crop: Optional[str] = None,
    days: Optional[int] = 30
) -> List[Dict[str, Any]]:
    """Fetches market price records for a crop over past N days.
    
    Returns real rows (is_sample=0) when available, falling back to sample rows (is_sample=1)
    if only sample data exists. Always includes is_sample on every row.
    """
    days_val = int(days) if days and int(days) > 0 else 30

    # Build commodity filter
    params: List[Any] = []
    where_parts: List[str] = []

    if crop and crop.strip():
        canonical = get_canonical_commodity_name(crop.strip())
        where_parts.append("(commodity = ? OR commodity = ?)")
        params.extend([crop.strip(), canonical])

    crop_where = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    # Check if real records exist for this crop/filter
    real_check_query = f"""
        SELECT COUNT(*) as cnt 
        FROM mandi_prices 
        {crop_where + (' AND' if crop_where else 'WHERE')} is_sample = 0
    """
    real_check = fetch_one(real_check_query, tuple(params))
    has_real = bool(real_check and real_check["cnt"] > 0)

    # Determine latest date for cutoff calculation
    max_date_query = f"SELECT MAX(arrival_date) as max_date FROM mandi_prices {crop_where}"
    max_row = fetch_one(max_date_query, tuple(params))
    if max_row and max_row["max_date"]:
        base_dt = datetime.strptime(max_row["max_date"], "%Y-%m-%d").date()
    else:
        base_dt = datetime.now().date()
    cutoff_date = (base_dt - timedelta(days=days_val)).strftime("%Y-%m-%d")

    # Final query
    final_where: List[str] = []
    final_params: List[Any] = []

    if crop and crop.strip():
        canonical = get_canonical_commodity_name(crop.strip())
        final_where.append("(commodity = ? OR commodity = ?)")
        final_params.extend([crop.strip(), canonical])

    if has_real:
        final_where.append("is_sample = 0")

    final_where.append("arrival_date >= ?")
    final_params.append(cutoff_date)

    where_sql = "WHERE " + " AND ".join(final_where)
    sql = f"""
        SELECT 
            id, state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price,
            arrival_quantity, source, is_sample, fetched_at
        FROM mandi_prices
        {where_sql}
        ORDER BY arrival_date DESC, modal_price DESC
    """
    rows = fetch_all(sql, tuple(final_params))

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "state": r["state"],
            "district": r["district"],
            "market": r["market"],
            "commodity": r["commodity"],
            "variety": r["variety"],
            "grade": r["grade"],
            "arrival_date": r["arrival_date"],
            "min_price": float(r["min_price"]),
            "max_price": float(r["max_price"]),
            "modal_price": float(r["modal_price"]),
            "arrival_quantity": float(r["arrival_quantity"] or 0.0),
            "source": r["source"],
            "is_sample": int(r["is_sample"]),
            "fetched_at": r["fetched_at"]
        })
    return results

