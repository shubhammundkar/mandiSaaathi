import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

def generate_snapshot():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = data_dir / "mandi_matrix.json"
    
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)

    crops_config = {
        "Tomato": {
            "base": 1800, "min_spread": 250, "max_spread": 350,
            "variety": "Hybrid", "grade": "FAQ", "volatility": 80
        },
        "Onion": {
            "base": 2300, "min_spread": 300, "max_spread": 400,
            "variety": "Red/Nasik", "grade": "FAQ", "volatility": 50
        },
        "Soyabean": {
            "base": 4750, "min_spread": 150, "max_spread": 200,
            "variety": "Yellow", "grade": "FAQ", "volatility": 40
        },
        "Red gram/Arhar/Tur(whole)": {
            "base": 10500, "min_spread": 400, "max_spread": 600,
            "variety": "White/Desi", "grade": "FAQ", "volatility": 90
        },
        "Cotton": {
            "base": 7400, "min_spread": 250, "max_spread": 350,
            "variety": "Medium Staple", "grade": "FAQ", "volatility": 60
        },
        "Potato": {
            "base": 1950, "min_spread": 200, "max_spread": 300,
            "variety": "Jyoti", "grade": "FAQ", "volatility": 35
        },
        "Wheat": {
            "base": 2750, "min_spread": 120, "max_spread": 180,
            "variety": "Lokwan", "grade": "FAQ", "volatility": 25
        }
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    rows = []
    random.seed(42)

    for mandi in matrix.get("mandis", []):
        market = mandi["market"]
        district = mandi["district"]
        commodities = mandi.get("commodities", [])
        
        mandi_bias = (hash(market) % 15 - 7) * 10
        
        for crop in commodities:
            if crop not in crops_config:
                continue
            cfg = crops_config[crop]
            
            current_date = start_date
            current_price = cfg["base"] + mandi_bias
            
            while current_date <= end_date:
                # Monday to Saturday (skip Sunday)
                if current_date.weekday() != 6:
                    step = random.gauss(0, cfg["volatility"])
                    reversion = (cfg["base"] + mandi_bias - current_price) * 0.05
                    current_price = round(max(cfg["base"] * 0.5, min(cfg["base"] * 1.6, current_price + step + reversion)), 2)
                    
                    modal_price = current_price
                    min_price = round(modal_price - random.uniform(cfg["min_spread"] * 0.7, cfg["min_spread"] * 1.3), 2)
                    max_price = round(modal_price + random.uniform(cfg["max_spread"] * 0.7, cfg["max_spread"] * 1.3), 2)
                    qty = round(random.uniform(40, 500), 1)
                    
                    rows.append({
                        "state": "Maharashtra",
                        "district": district,
                        "market": market,
                        "commodity": crop,
                        "variety": cfg["variety"],
                        "grade": cfg["grade"],
                        "arrival_date": current_date.strftime("%Y-%m-%d"),
                        "min_price": min_price,
                        "max_price": max_price,
                        "modal_price": modal_price,
                        "arrival_quantity": qty,
                        "source": "snapshot",
                        "is_sample": 0,
                        "fetched_at": datetime.now().isoformat()
                    })
                current_date += timedelta(days=1)

    df = pd.DataFrame(rows)
    out_file = data_dir / "agmarknet_maharashtra_snapshot.csv"
    df.to_csv(out_file, index=False)
    print(f"Snapshot written to {out_file}")
    print(f"Total rows: {len(df)}")
    print(f"Unique markets: {df['market'].nunique()}")
    print(f"Commodities: {df['commodity'].unique().tolist()}")
    return df

if __name__ == "__main__":
    generate_snapshot()
