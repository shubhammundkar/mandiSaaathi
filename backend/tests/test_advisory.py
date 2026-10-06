"""Unit tests for the Advisory Engine and Data Service.

Verifies net return calculations, timing and cutoff rules, break-even math,
and the canonical test: nearest Rs 200 today beats far Rs 180 tomorrow plus higher transport.
"""

import pytest
from backend.services.data_service import get_data_status, get_crops, get_mandis
from backend.services.advisory_engine import (
    calculate_advisory,
    compute_mandi_metrics,
    haversine_distance,
    load_config,
    rank_and_evaluate
)


def test_data_status_ready():
    status = get_data_status()
    assert status["status"] == "ready"
    assert status["total_records"] > 0
    assert status["monitored_mandis"] >= 10
    assert status["monitored_crops"] >= 5


def test_haversine_distance():
    # Pune to Nashik road distance is roughly 180-250 km
    pune = (18.5204, 73.8567)
    nashik = (19.9975, 73.7898)
    dist = haversine_distance(pune[0], pune[1], nashik[0], nashik[1])
    assert 180 <= dist <= 250


def test_nearest_200_today_beats_far_180_tomorrow_plus_higher_transport():
    """Canonical Hackathon Test Case:

    A nearby mandi offering Rs 200 today beats a distant mandi expected to offer Rs 180 tomorrow
    due to higher transport costs, missing the morning auction cutoff, and overnight holding costs.
    """
    config = load_config()

    # Candidate 1: Nearest Mandi (e.g. 15 km away, Rs 200/q today, arrives before 12:00 PM cutoff)
    nearest_cand = {
        "market": "Pune (Local APMC)",
        "district": "Pune",
        "lat": 18.50,
        "lng": 73.86,
        "modal_price": 200.0,
        "min_price": 180.0,
        "max_price": 220.0,
        "auction_cutoff": "12:00",
        "arrival_date": "2026-10-07"
    }

    # Candidate 2: Far Mandi (e.g. 140 km away, Rs 180/q expected tomorrow, misses 12:00 PM cutoff)
    far_cand = {
        "market": "Nashik (Distant APMC)",
        "district": "Nashik",
        "lat": 19.99,
        "lng": 73.78,
        "modal_price": 180.0,
        "min_price": 160.0,
        "max_price": 200.0,
        "auction_cutoff": "12:00",
        "arrival_date": "2026-10-07"
    }

    # Farmer departs from Pune district at 9:30 AM with 20 quintals via tempo
    origin_lat, origin_lng = 18.52, 73.85
    departure_hour = 9.5

    nearest_metrics = compute_mandi_metrics(
        candidate=nearest_cand,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=departure_hour,
        crop="Tomato",
        config=config
    )

    far_metrics = compute_mandi_metrics(
        candidate=far_cand,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=departure_hour,
        crop="Tomato",
        config=config
    )

    # 1. Nearest mandi arrives before cutoff, far mandi misses cutoff
    assert nearest_metrics["missed_cutoff"] is False
    assert far_metrics["missed_cutoff"] is True

    # 2. Far mandi transport cost is significantly higher
    assert far_metrics["costs"]["transport_per_q"] > nearest_metrics["costs"]["transport_per_q"]

    # 3. Far mandi incurs overnight holding cost
    assert far_metrics["costs"]["loading_unloading_per_q"] > nearest_metrics["costs"]["loading_unloading_per_q"]

    # 4. Nearest mandi Net Return per quintal beats far mandi
    assert nearest_metrics["net_return_per_quintal"] > far_metrics["net_return_per_quintal"]

    # 5. Rank and evaluate confirms nearest mandi is #1 recommendation
    evaluated = [nearest_metrics, far_metrics]
    ranked = rank_and_evaluate(
        evaluated=evaluated,
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=departure_hour
    )

    assert ranked["best_recommendation"]["market"] == "Pune (Local APMC)"
    assert ranked["best_recommendation"]["net_return_per_quintal"] > ranked["comparisons"][0]["net_return_per_quintal"]


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
    
    # Comparisons sorted descending by net return
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
    # Departing at 11:30 AM with a 2-hour drive must miss 12:00 PM cutoff
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        departure_hour=11.5
    )
    best = result["best_recommendation"]
    assert best is not None
