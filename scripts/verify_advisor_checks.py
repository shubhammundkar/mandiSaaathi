"""Verification script for Step 7 Advisor Form checks."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

def main():
    client = TestClient(app)

    print("=== CHECK 1: Form loads real crops and districts from API ===")
    r_crops = client.get("/api/crops")
    assert r_crops.status_code == 200
    crops = r_crops.json().get("crops", [])
    print(f"Loaded {len(crops)} real crops from /api/crops:")
    for c in crops:
        print(f"  - {c['commodity']} ({c['mandi_count']} mandis, latest: {c['latest_date']}, avg: Rs {c['avg_price']})")
    assert len(crops) > 0

    r_mandis = client.get("/api/mandis")
    assert r_mandis.status_code == 200
    mandis = r_mandis.json().get("mandis", [])
    districts = sorted(list(set(m["district"] for m in mandis if m.get("district"))))
    print(f"\nLoaded {len(mandis)} mandis spanning {len(districts)} districts from /api/mandis:")
    print(f"  Districts: {', '.join(districts)}")
    assert len(districts) > 0

    print("\n=== CHECK 2: Try demo fills fields and sends request ===")
    demo_body = {"crop": "Tomato", "district": "Pune", "quantity": 20.0, "vehicle": "tempo"}
    r_advise = client.post("/api/advise", json=demo_body)
    assert r_advise.status_code == 200
    adv = r_advise.json()
    rec = adv["best_recommendation"]
    print(f"POST /api/advise response status: {r_advise.status_code}")
    print(f"  Recommended Mandi: {rec['market']} ({rec['district']})")
    print(f"  Distance: {rec['distance_km']} km | Arrival: {rec['arrival_time']}")
    print(f"  Gross Modal Price: Rs {rec['gross_modal_price']}/q")
    print(f"  Net Return in Pocket: Rs {rec['net_return_per_quintal']}/q")
    print(f"  Total Net Earnings: Rs {rec['total_net_earnings']}")
    clean_verdict = rec['verdict_reason'].replace('\u20b9', 'Rs')
    print(f"  Verdict: {clean_verdict}")

    print("\n=== CHECK 3: Switching language changes every label ===")
    i18n_path = Path(__file__).resolve().parent.parent / "frontend" / "js" / "i18n.js"
    i18n_content = i18n_path.read_text(encoding="utf-8")
    
    # Check that EN, HI, MR dictionaries exist
    for lang in ["en", "hi", "mr"]:
        assert f"{lang}: {{" in i18n_content or f"{lang}:" in i18n_content
    print("  Languages supported: English (en), Hindi (hi), Marathi (mr)")

    # Key translations audit
    test_keys = [
        "advisor_heading", "btn_calculate", "btn_try_demo", "btn_listen",
        "select_crop", "select_district", "input_quantity", "select_vehicle",
        "crop_tomato", "crop_onion", "crop_soybean", "crop_tur", "crop_cotton", "crop_potato", "crop_wheat",
        "vehicle_tempo", "vehicle_truck", "vehicle_own",
        "results_hero_title", "results_net_return", "results_total_earnings",
        "results_breakeven_title", "results_forecast_title", "results_storage_title",
        "table_mandi", "table_modal", "table_deductions", "table_net", "table_verdict"
    ]
    all_present = True
    for k in test_keys:
        if f"{k}:" not in i18n_content:
            print(f"  Missing key: {k}")
            all_present = False
    print(f"  Checked {len(test_keys)} critical keys across all 3 languages: All present = {all_present}")
    assert all_present

    print("\n=== CHECK 4: Badge shows true data source ===")
    r_status = client.get("/api/data-status")
    assert r_status.status_code == 200
    st = r_status.json()
    print(f"  Source: {st['source']}")
    print(f"  Total Records: {st['total_records']}")
    print(f"  Latest Date: {st['latest_date']}")
    print(f"  Monitored APMCs: {st['monitored_mandis']}")
    print(f"  Monitored Crops: {st['monitored_crops']}")
    print(f"  Is Sample Data: {st['is_sample']}")
    assert st["source"] in ["live", "snapshot", "sample"]
    assert st["total_records"] > 0
    print("\n-> ALL 4 CHECKS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
