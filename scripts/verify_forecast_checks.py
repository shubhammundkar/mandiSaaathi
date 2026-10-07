import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

def main():
    client = TestClient(app)

    print("=== CHECK 1: /api/forecast returns 5 days of low <= likely <= high with confidence label ===")
    r = client.get("/api/forecast?crop=Tomato&market=Pune")
    data = r.json()
    print(f"Status Code: {r.status_code}")
    print(f"Crop: {data['crop']} | Market: {data['market']}")
    print(f"Confidence Label: {data['confidence']}")
    print(f"Forecast length: {len(data['forecast'])}")

    all_valid = True
    for f in data["forecast"]:
        ordered = f["low"] <= f["likely"] <= f["high"]
        strict = f["low"] < f["high"]
        day_str = f"{f['day']} ({f['date']}, {f['weekday']}): Low=Rs{f['low']} <= Likely=Rs{f['likely']} <= High=Rs{f['high']} -> Valid: {ordered and strict}"
        print(f"  {day_str}")
        if not (ordered and strict):
            all_valid = False

    check1_passed = all_valid and data["confidence"] in ["HIGH", "MEDIUM", "LOW"] and len(data["forecast"]) == 5
    print(f"-> CHECK 1 PASSED: {check1_passed}\n")

    print("=== CHECK 2: Crop with thin / absent data returns LOW confidence or 'Not enough data', not made-up forecast ===")
    # 2a. Missing crop (0 records)
    r_thin = client.get("/api/forecast?crop=Dragonfruit&market=Pune")
    d_thin = r_thin.json()
    print(f"Crop: Dragonfruit in Pune")
    print(f"  Status: {d_thin.get('status')}")
    print(f"  Confidence: {d_thin.get('confidence')}")
    print(f"  Message: {d_thin.get('message')}")
    print(f"  Forecast items: {len(d_thin.get('forecast', []))} (No made-up numbers)")
    check_2a = d_thin.get("status") == "NOT_ENOUGH_DATA" and d_thin.get("confidence") == "LOW" and len(d_thin.get("forecast", [])) == 0

    # 2b. Crop not traded in that mandi (e.g. Cotton in Pune)
    r_cotton = client.get("/api/forecast?crop=Cotton&market=Pune")
    d_cotton = r_cotton.json()
    print(f"\nCrop: Cotton in Pune (0 records)")
    print(f"  Status: {d_cotton.get('status')}")
    print(f"  Confidence: {d_cotton.get('confidence')}")
    print(f"  Message: {d_cotton.get('message')}")
    print(f"  Forecast items: {len(d_cotton.get('forecast', []))} (No made-up numbers)")
    check_2b = d_cotton.get("status") == "NOT_ENOUGH_DATA" and d_cotton.get("confidence") == "LOW" and len(d_cotton.get("forecast", [])) == 0

    # 2c. Storage advice on thin crop
    r_store = client.get("/api/storage-advice?crop=Dragonfruit&market=Pune")
    d_store = r_store.json()
    print(f"\nStorage advice for Dragonfruit:")
    print(f"  Recommendation: {d_store.get('recommendation')}")
    check_2c = d_store.get("recommendation") in ["Not enough data", "Sell now"]

    check2_passed = check_2a and check_2b and check_2c
    print(f"-> CHECK 2 PASSED: {check2_passed}\n")

if __name__ == "__main__":
    main()
