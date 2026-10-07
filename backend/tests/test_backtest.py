"""Unit tests for the 90-Day Backtest Simulation Engine."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.backtest_engine import run_90_day_backtest


def test_backtest_tomato_90_days():
    """Verifies that 90-day backtest runs leak-free and generates required metrics."""
    result = run_90_day_backtest(crop="Tomato", district="Pune")
    assert result["status"] == "OK"
    assert result["crop"] == "Tomato"
    assert result["district"] == "Pune"
    assert result["nearest_mandi"] == "Pune"
    assert result["days_tested"] >= 50

    # Rates and returns
    assert 0.0 <= result["percent_days_better"] <= 100.0
    assert 0.0 <= result["percent_days_better_or_equal"] <= 100.0
    assert isinstance(result["average_extra_rs_per_quintal"], float)
    assert isinstance(result["total_extra_rs_per_quintal"], float)

    # Cumulative series
    series = result["cumulative_series"]
    assert len(series) == result["days_tested"]
    assert "date" in series[0]
    assert "mandi_saathi_cumulative" in series[0]
    assert "nearest_cumulative" in series[0]
    assert "cumulative_gain" in series[0]

    # Worse days transparency
    worse = result["worse_days"]
    assert isinstance(worse, list)
    for w in worse:
        assert w["diff_rs"] < 0
        assert "reason" in w
        assert len(w["reason"]) > 10

    # Honest assessment
    assert len(result["honest_assessment"]) > 20


def test_backtest_thin_data_handling():
    """Verifies that thin or missing data returns honest warning rather than simulated numbers."""
    result = run_90_day_backtest(crop="RareDragonFruit")
    assert result["status"] == "THIN_DATA"
    assert result["days_tested"] == 0
    assert result["percent_days_better"] == 0.0
    assert result["average_extra_rs_per_quintal"] == 0.0
    assert len(result["cumulative_series"]) == 0
    assert len(result["worse_days"]) == 0
    assert "thin" in result["honest_assessment"].lower()


def test_backtest_api_endpoint():
    """Verifies GET /api/backtest endpoint."""
    client = TestClient(app)

    # Valid commodity test
    resp = client.get("/api/backtest?crop=Soybean")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "OK"
    assert data["days_tested"] > 0
    assert "cumulative_series" in data
    assert "worse_days" in data
    assert "honest_assessment" in data

    # Thin commodity endpoint test
    resp_thin = client.get("/api/backtest?crop=NonExistentCrop")
    assert resp_thin.status_code == 200
    data_thin = resp_thin.json()
    assert data_thin["status"] == "THIN_DATA"
    assert data_thin["days_tested"] == 0
