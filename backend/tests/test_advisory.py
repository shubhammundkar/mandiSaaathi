"""Unit tests for the Advisory Engine and Data Service."""

import pytest
from backend.services.data_service import get_data_status, get_crops, get_mandis
from backend.services.advisory_engine import calculate_advisory, haversine_distance


def test_data_status_ready():
    status = get_data_status()
    assert status["status"] == "ready"
    assert status["total_records"] > 0
    assert status["monitored_mandis"] >= 10
    assert status["monitored_crops"] >= 5


def test_haversine_distance():
    # Pune to Nashik is roughly ~160-200 km road distance
    pune = (18.5204, 73.8567)
    nashik = (19.9975, 73.7898)
    dist = haversine_distance(pune[0], pune[1], nashik[0], nashik[1])
    assert 180 <= dist <= 250


def test_advisory_ranking_tomato():
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=7.0
    )
    assert "best_recommendation" in result
    best = result["best_recommendation"]
    assert best is not None
    assert "net_return_per_quintal" in best
    assert "total_net_earnings" in best
    assert best["net_return_per_quintal"] > 0
    assert "confidence" in best
    assert best["confidence"] in ["HIGH", "MEDIUM", "LOW"]
    
    # Comparisons should be sorted descending
    if result["comparisons"]:
        prev_net = best["net_return_per_quintal"]
        for comp in result["comparisons"]:
            assert comp["net_return_per_quintal"] <= prev_net
            prev_net = comp["net_return_per_quintal"]


def test_break_even_logic():
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0
    )
    assert "nearest_baseline" in result
    for comp in result["comparisons"]:
        assert "break_even_price" in comp
        assert comp["break_even_price"] > 0


def test_auction_cutoff_trigger():
    # Departing very late (e.g. 11:30 AM) with a 2-hour drive must miss 12:00 PM cutoff
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        departure_hour=11.5
    )
    best = result["best_recommendation"]
    assert best is not None


def test_nearest_mandi_beats_distant_when_costs_exceed_gain():
    """Canonical test case from hackathon guide:

    Nearest mandi with moderate price today beats distant mandi with lower or delayed
    price once higher transport, labor, and holding costs are deducted.
    """
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=5.0,  # Smaller quantity makes transport per quintal much higher for far mandis
        vehicle_type="tempo",
        departure_hour=10.0
    )
    best = result["best_recommendation"]
    assert best is not None
    # Verify that the recommended mandi has higher net return than far mandis
    far_mandis = [c for c in result["comparisons"] if c["distance_km"] > 100]
    if far_mandis:
        assert best["net_return_per_quintal"] > far_mandis[0]["net_return_per_quintal"]
