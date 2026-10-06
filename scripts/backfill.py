"""Backfill script to populate SQLite database with 90 days of Maharashtra mandi prices."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import get_db_connection, init_db
from backend.services.agmarknet_fetcher import COMMODITY_MAP, fetch_prices

CROPS = [
    "Tomato",
    "Onion",
    "Soybean",
    "Tur",
    "Cotton",
    "Potato",
    "Wheat"
]

def run_backfill(days: int = 90):
    print("=" * 60)
    print("Mandi Saathi — Database Backfill Pipeline")
    print("=" * 60)
    
    init_db()
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    from_date_str = start_date.strftime("%Y-%m-%d")
    to_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Target Date Range: {from_date_str} to {to_date_str} ({days} days)")
    
    total_inserted = 0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for crop in CROPS:
            print(f"\nProcessing {crop}...")
            df = fetch_prices(crop, from_date_str, to_date_str)
            if df.empty:
                print(f"  Warning: No records found for {crop}")
                continue
                
            records_count = 0
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO mandi_prices (
                        state, district, market, commodity, variety, grade,
                        arrival_date, min_price, max_price, modal_price,
                        arrival_quantity, source, is_sample
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["state"],
                    row["district"],
                    row["market"],
                    row["commodity"],
                    row["variety"],
                    row["grade"],
                    row["arrival_date"],
                    float(row["min_price"]),
                    float(row["max_price"]),
                    float(row["modal_price"]),
                    float(row["arrival_quantity"]),
                    row["source"],
                    int(row["is_sample"])
                ))
                records_count += 1
            
            conn.commit()
            print(f"  Inserted/Updated {records_count} records for {crop}")
            total_inserted += records_count

        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT market), COUNT(DISTINCT commodity) FROM mandi_prices")
        total_in_db, unique_markets, unique_commodities = cursor.fetchone()

    print("\n" + "=" * 60)
    print("Backfill Complete!")
    print(f"Total rows currently in mandi_prices: {total_in_db}")
    print(f"Unique APMC markets: {unique_markets}")
    print(f"Unique commodities: {unique_commodities}")
    print("=" * 60)

if __name__ == "__main__":
    run_backfill()
