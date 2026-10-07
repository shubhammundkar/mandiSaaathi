"""Unit tests for the Forecast Engine and Sell-or-Store Decision Advisory."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.forecast_engine import (
    forecast_5_days,
    get_forecast_lower_bound,
    get_storage_advice,
    STORAGE_ELIGIBLE_CROPS
)


def test_forecast_5_days_structure():
    """Verifies that 5-day forecast generates corridors with low < likely < high."""
    result = forecast_5_days(crop="Tomato", market="Pune")
    assert result["status"] == "OK"
    assert result["crop"] == "Tomato"
    assert result["market"] == "Pune"
    assert result["confidence"] in ["HIGH", "MEDIUM", "LOW"]
    assert result["trend"] in ["BULLISH", "BEARISH", "STABLE"]

    fc = result["forecast"]
    assert len(fc) == 5

    for day in fc:
        assert "date" in day
        assert "weekday" in day
        assert "low" in day
        assert "likely" in day
        assert "high" in day
        # Core rule: low < likely < high, never one single number
        assert day["low"] < day["likely"] < day["high"]
        assert day["low"] > 0


def test_forecast_insufficient_data():
    """Verifies graceful handling when data is absent or sparse."""
    result = forecast_5_days(crop="ExoticDragonFruit", market="NonExistentMandi")
    assert result["status"] == "NOT_ENOUGH_DATA"
    assert result["confidence"] == "LOW"
    assert len(result["forecast"]) == 0


def test_sell_or_store_non_perishables():
    """Verifies sell-or-store optimization on storage-eligible crops."""
    crops_to_test = ["Onion", "Soybean", "Tur", "Potato", "Wheat"]
    
    for crop in crops_to_test:
        advice = get_storage_advice(crop=crop)
        assert advice["crop"] == crop
        assert advice["is_storage_viable"] is True
        assert advice["recommendation"] in [
            "Sell now", "Wait 1 days", "Wait 2 days", "Wait 3 days", "Wait 4 days", "Wait 5 days", "Not enough data"
        ]
        assert "current_price" in advice
        assert "net_benefit_per_quintal" in advice
        assert "rationale" in advice
        assert len(advice["evaluation_steps"]) > 0
        
        # Verify economic step deductions
        step1 = advice["evaluation_steps"][0]
        assert step1["storage_cost_per_q"] > 0
        assert step1["quality_loss_per_q"] >= 0


def test_sell_or_store_perishable_tomato():
    """Verifies that perishable crops like Tomato always recommend immediate sale."""
    advice = get_storage_advice(crop="Tomato")
    assert advice["is_storage_viable"] is False
    assert advice["recommendation"] == "Sell now"
    assert "perishable" in advice["rationale"].lower()


def test_forecast_lower_bound_wired():
    """Verifies lower bound provider returns a conservative price and wires into advise."""
    low_val = get_forecast_lower_bound(crop="Tomato", market="Pune", day_offset=1)
    assert low_val is not None
    assert low_val > 0

    client = TestClient(app)
    resp = client.post("/api/advise", json={
        "crop": "Tomato",
        "district": "Pune",
        "quantity": 20.0,
        "vehicle": "tempo",
        "departure_hour": 7.0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "best_recommendation" in data
    assert data["best_recommendation"]["expected_price"] > 0


def test_api_forecast_and_storage_endpoints():
    """Verifies GET /api/forecast and GET /api/storage-advice endpoints."""
    client = TestClient(app)

    # 1. GET /api/forecast returns 5 days with low <= likely <= high and confidence label
    resp1 = client.get("/api/forecast?crop=Soybean&market=Latur")
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["status"] == "OK"
    assert d1["confidence"] in ["HIGH", "MEDIUM", "LOW"]
    assert len(d1["forecast"]) == 5
    for pt in d1["forecast"]:
        assert pt["low"] <= pt["likely"] <= pt["high"]
        assert pt["low"] < pt["high"]

    # 2. Thin/missing data endpoint check: returns low confidence / Not enough data, no made-up forecast
    resp_thin = client.get("/api/forecast?crop=Dragonfruit&market=Pune")
    assert resp_thin.status_code == 200
    d_thin = resp_thin.json()
    assert d_thin["status"] == "NOT_ENOUGH_DATA"
    assert d_thin["confidence"] == "LOW"
    assert len(d_thin["forecast"]) == 0  # No made-up numbers

    # 3. GET /api/storage-advice
    resp2 = client.get("/api/storage-advice?crop=Onion&market=Lasalgaon")
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["crop"] == "Onion"
    assert d2["is_storage_viable"] is True
    assert "recommendation" in d2

    # 4. Storage advice on thin data returns 'Not enough data'
    resp_store_thin = client.get("/api/storage-advice?crop=Dragonfruit&market=Pune")
    assert resp_store_thin.status_code == 200
    d_store_thin = resp_store_thin.json()
    assert d_store_thin["recommendation"] in ["Not enough data", "Sell now"]
