import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import fetch_all

def main():
    rows = fetch_all("""
        SELECT 
            market, 
            district, 
            COUNT(*) as record_count, 
            COUNT(DISTINCT commodity) as crop_count,
            GROUP_CONCAT(DISTINCT commodity) as crops,
            MIN(arrival_date) as start_date, 
            MAX(arrival_date) as end_date
        FROM mandi_prices 
        GROUP BY market, district 
        ORDER BY record_count DESC
    """)
    print(f"Total monitored mandis: {len(rows)}")
    print("-" * 75)
    for i, r in enumerate(rows, 1):
        print(f"{i:2d}. {r['market']:<16} | District: {r['district']:<12} | Records: {r['record_count']:<4} | Crops: {r['crop_count']} ({r['crops']})")
    print("-" * 75)

if __name__ == "__main__":
    main()
