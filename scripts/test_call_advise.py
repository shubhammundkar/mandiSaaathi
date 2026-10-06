import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

def main():
    client = TestClient(app)
    resp = client.post('/api/advise', json={
        'crop': 'Tomato',
        'district': 'Pune',
        'quantity': 20.0,
        'vehicle': 'tempo',
        'departure_hour': 7.0
    })

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()

    print("=== REAL POST /api/advise CALL RESULT ===")
    print("Query:", data["query"])
    best = data["best_recommendation"]
    print(f"#1 BEST MANDI: {best['market']} ({best['district']})")
    print(f"   Gross Modal Price: Rs {best['gross_modal_price']}/q (Min: {best['price_range']['min']}, Max: {best['price_range']['max']})")
    print(f"   Distance: {best['distance_km']} km | Travel Time: {best['travel_hours']} hrs | Arrival: {best['arrival_time']}")
    print(f"   Net Return: Rs {best['net_return_per_quintal']}/q | Total Net: Rs {best['total_net_earnings']}")
    print(f"   Confidence: {best['confidence']} (Reported: {best['arrival_date']})")
    reason_safe = best['verdict_reason'].replace('\u20b9', 'Rs ')
    print(f"   One-line Reason: {reason_safe}")

    print(f"\nRANKED COMPARISONS ({len(data['comparisons'])} alternative mandis):")
    for i, comp in enumerate(data['comparisons'][:6], 2):
        print(f"#{i} {comp['market']} ({comp['district']})")
        print(f"   Gross: Rs {comp['gross_modal_price']}/q | Net Return: Rs {comp['net_return_per_quintal']}/q | Distance: {comp['distance_km']} km")
        print(f"   Break-Even Price: Rs {comp['break_even_price']}/q")

if __name__ == "__main__":
    main()
