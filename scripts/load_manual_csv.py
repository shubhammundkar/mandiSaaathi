"""Manual CSV Ingestion Tool for Mandi Saathi.

Loads CSV files downloaded directly from agmarknet.gov.in into the SQLite database
(mandi_prices table) with is_sample=0 and source='manual_csv'.

Also updates data/agmarknet_maharashtra_snapshot.csv with verified real records.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import get_db_connection, init_db, fetch_one
from backend.services.agmarknet_fetcher import COMMODITY_MAP

DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_PATH = DATA_DIR / "agmarknet_maharashtra_snapshot.csv"

# Known header patterns in Agmarknet exports
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "state": ["state", "state name", "statename"],
    "district": ["district", "district name", "districtname"],
    "market": ["market", "market name", "marketname", "mandi", "apmc", "centre", "center"],
    "commodity": ["commodity", "crop", "commodity name", "commodityname"],
    "variety": ["variety", "variety name", "varietyname"],
    "grade": ["grade"],
    "arrival_date": ["arrival_date", "arrival date", "date", "report date", "report_date", "price date", "price_date"],
    "min_price": ["min_price", "min price", "min_x0020_price", "minimum price", "min price (rs./quintal)", "min price (rs/q)", "min"],
    "max_price": ["max_price", "max price", "max_x0020_price", "maximum price", "max price (rs./quintal)", "max price (rs/q)", "max"],
    "modal_price": ["modal_price", "modal price", "modal_x0020_price", "modal", "modal price (rs./quintal)", "modal price (rs/q)"],
    "arrival_quantity": ["arrival_quantity", "arrivals", "arrival", "arrival (tonnes)", "arrivals (tonnes)", "arrivals (qtl)", "arrival_qty"]
}


def find_header_row(file_path: Path) -> int:
    """Finds the 0-indexed row number containing the column headers."""
    header_keywords = {"market", "commodity", "price", "arrival", "mandi", "state", "district"}
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f):
            if idx > 25:
                break
            line_lower = line.lower()
            matches = sum(1 for kw in header_keywords if kw in line_lower)
            if matches >= 2:
                return idx
    return 0


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Maps varied column names from agmarknet CSV downloads to canonical names."""
    rename_dict = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace("_x0020_", " ").replace("  ", " ")
        for canonical, syns in COLUMN_SYNONYMS.items():
            if norm in syns or any(norm.startswith(s) for s in syns):
                rename_dict[col] = canonical
                break
    return df.rename(columns=rename_dict)


def parse_date_safely(val: Any) -> Optional[str]:
    """Parses various date formats from Agmarknet exports into YYYY-MM-DD."""
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None

    # Already YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", val_str):
        return val_str

    for fmt in (
        "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d/%b/%Y",
        "%d-%B-%Y", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%y", "%d/%m/%y"
    ):
        try:
            return datetime.strptime(val_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback to pandas flexible parser with dayfirst=True
    try:
        dt = pd.to_datetime(val_str, dayfirst=True, errors="coerce")
        if pd.notna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None


def clean_price(val: Any) -> Optional[float]:
    """Converts price strings (with commas/symbols) to float."""
    if pd.isna(val) or val is None:
        return None
    val_str = re.sub(r"[^\d\.]", "", str(val).strip())
    if not val_str:
        return None
    try:
        num = float(val_str)
        return num if num > 0 else None
    except ValueError:
        return None


def load_manual_csv(file_path: Path) -> Tuple[int, int]:
    """Parses and loads a single manual CSV file into SQLite mandi_prices with is_sample=0."""
    if not file_path.exists():
        print(f"Error: File does not exist at {file_path}")
        return 0, 0

    header_row = find_header_row(file_path)
    try:
        df = pd.read_csv(file_path, skiprows=header_row, encoding="utf-8", dtype=str)
    except Exception:
        df = pd.read_csv(file_path, skiprows=header_row, encoding="latin-1", dtype=str)

    df = map_columns(df)

    required_cols = ["market", "commodity", "modal_price", "arrival_date"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Error: Could not find required columns {missing} in {file_path.name}")
        print(f"Available columns: {list(df.columns)}")
        return 0, 0

    init_db()

    rows_to_insert = []
    skipped_count = 0

    for _, row in df.iterrows():
        market = str(row.get("market", "")).strip()
        commodity = str(row.get("commodity", "")).strip()
        raw_date = row.get("arrival_date")
        modal_p = clean_price(row.get("modal_price"))

        if not market or not commodity or not modal_p:
            skipped_count += 1
            continue

        parsed_date = parse_date_safely(raw_date)
        if not parsed_date:
            skipped_count += 1
            continue

        min_p = clean_price(row.get("min_price")) or modal_p
        max_p = clean_price(row.get("max_price")) or modal_p
        min_p = min(min_p, modal_p)
        max_p = max(max_p, modal_p)

        qty_val = clean_price(row.get("arrival_quantity")) or 0.0
        state = str(row.get("state", "Maharashtra")).strip() or "Maharashtra"
        district = str(row.get("district", market)).strip() or market
        variety = str(row.get("variety", "FAQ")).strip() or "FAQ"
        grade = str(row.get("grade", "FAQ")).strip() or "FAQ"

        rows_to_insert.append((
            state, district, market, commodity, variety, grade,
            parsed_date, min_p, max_p, modal_p, qty_val,
            "manual_csv", 0, datetime.now().isoformat()
        ))

    if not rows_to_insert:
        print(f"No valid rows found in {file_path.name} (skipped {skipped_count} rows).")
        return 0, skipped_count

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO mandi_prices (
                state, district, market, commodity, variety, grade,
                arrival_date, min_price, max_price, modal_price,
                arrival_quantity, source, is_sample, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(market, commodity, variety, arrival_date) DO UPDATE SET
                state = excluded.state,
                district = excluded.district,
                grade = excluded.grade,
                min_price = excluded.min_price,
                max_price = excluded.max_price,
                modal_price = excluded.modal_price,
                arrival_quantity = excluded.arrival_quantity,
                source = 'manual_csv',
                is_sample = 0,
                fetched_at = excluded.fetched_at;
        """, rows_to_insert)
        conn.commit()

    print(f"Successfully loaded {len(rows_to_insert)} real records (is_sample=0, source='manual_csv') from {file_path.name}.")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} invalid or incomplete rows.")

    # Refresh verified real snapshot file (is_sample = 0 only)
    refresh_real_snapshot()
    return len(rows_to_insert), skipped_count


def refresh_real_snapshot():
    """Exports all verified real records (is_sample=0) from SQLite to SNAPSHOT_PATH."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                state, district, market, commodity, variety, grade,
                arrival_date, min_price, max_price, modal_price,
                arrival_quantity, source, is_sample, fetched_at
            FROM mandi_prices
            WHERE is_sample = 0
            ORDER BY arrival_date DESC, commodity, market
        """)
        rows = cursor.fetchall()

    if rows:
        export_df = pd.DataFrame([dict(r) for r in rows])
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        export_df.to_csv(SNAPSHOT_PATH, index=False)
        print(f"Updated verified real snapshot at {SNAPSHOT_PATH} ({len(export_df)} real records).")
    else:
        if SNAPSHOT_PATH.exists():
            SNAPSHOT_PATH.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Load manual CSV files downloaded from agmarknet.gov.in into Mandi Saathi database."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=None,
        help="Path to CSV file or directory of CSV files downloaded from agmarknet.gov.in"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Mandi Saathi — Manual Agmarknet CSV Loader")
    print("=" * 70)

    target_paths: List[Path] = []
    if args.csv_path:
        p = Path(args.csv_path)
        if p.is_dir():
            target_paths.extend(list(p.glob("*.csv")))
        elif p.exists():
            target_paths.append(p)
        else:
            print(f"Error: Specified path not found: {args.csv_path}")
            sys.exit(1)
    else:
        # Default directory check: data/manual_downloads/
        manual_dir = DATA_DIR / "manual_downloads"
        manual_dir.mkdir(parents=True, exist_ok=True)
        target_paths = list(manual_dir.glob("*.csv"))
        if not target_paths:
            print(f"No CSV path specified and no files found in {manual_dir}.")
            print("Usage: python scripts/load_manual_csv.py <path_to_file.csv>")
            print(f"Or place your CSV downloads into: {manual_dir}")
            sys.exit(0)

    total_inserted = 0
    total_skipped = 0

    for path in target_paths:
        print(f"\nProcessing {path.name}...")
        ins, skip = load_manual_csv(path)
        total_inserted += ins
        total_skipped += skip

    # Print database status
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM mandi_prices WHERE is_sample = 0")
        real_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM mandi_prices WHERE is_sample = 1")
        sample_count = cursor.fetchone()[0]

    print("\n" + "=" * 70)
    print(f"Total rows inserted/updated this run: {total_inserted}")
    print(f"Total rows skipped this run: {total_skipped}")
    print(f"Current Database Composition:")
    print(f"  • Real Verified Records (is_sample=0): {real_count}")
    print(f"  • Sample Fallback Records (is_sample=1): {sample_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
