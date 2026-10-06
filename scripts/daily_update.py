"""Daily automated update script to pull the latest 3 days of mandi prices,

upsert into SQLite, and export a refreshed snapshot CSV.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import fetch_all, get_db_connection, init_db
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

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SNAPSHOT_PATH = DATA_DIR / "agmarknet_maharashtra_snapshot.csv"


def run_daily_update(days_back: int = 3):
    print("=" * 60)
    print("Mandi Saathi — Daily Ingestion & Snapshot Refresh Pipeline")
    print("=" * 60)
    
    init_db()
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    from_date_str = start_date.strftime("%Y-%m-%d")
    to_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Syncing window: {from_date_str} to {to_date_str} ({days_back} days)")
    
    new_records = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for crop in CROPS:
            df = fetch_prices(crop, from_date_str, to_date_str)
            if df.empty:
                continue
                
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
                new_records += 1
                
        conn.commit()
    
    print(f"Upserted {new_records} daily records to SQLite.")
    
    # Export full 90-day refreshed dataset to snapshot CSV
    all_rows = fetch_all("""
        SELECT 
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price,
            arrival_quantity, source, is_sample, fetched_at
        FROM mandi_prices
        ORDER BY arrival_date DESC, commodity, market
    """)
    
    if all_rows:
        export_df = pd.DataFrame(all_rows)
        export_df.to_csv(SNAPSHOT_PATH, index=False)
        print(f"Refreshed snapshot exported to {SNAPSHOT_PATH} ({len(export_df)} total records).")
        
    print("=" * 60)
    print("Daily update completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_daily_update()
