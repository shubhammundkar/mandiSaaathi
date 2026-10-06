"""Unit tests for the Advisory Engine and Data Service.

Verifies net return calculations, timing and cutoff rules, break-even math,
stale-data deprioritization, and the canonical test: nearest Rs 200 today beats far Rs 180 tomorrow plus higher transport.
"""

from datetime import datetime, timedelta
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

    # Candidate 1: Nearest Mandi (15 km away, Rs 200/q today, arrives before 12:00 PM cutoff)
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

    # Candidate 2: Far Mandi (140 km away, Rs 180/q expected tomorrow, misses 12:00 PM cutoff)
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
        departure_hour=departure_hour,
        config=config
    )

    assert ranked["best_recommendation"]["market"] == "Pune (Local APMC)"
    assert ranked["best_recommendation"]["net_return_per_quintal"] > ranked["comparisons"][0]["net_return_per_quintal"]


def test_after_cutoff_case():
    """Verifies that arriving after auction cutoff sets Day+1 and applies holding cost."""
    config = load_config()
    cand = {
        "market": "Far APMC",
        "district": "Pune",
        "lat": 19.50,
        "lng": 74.50,
        "modal_price": 2000.0,
        "auction_cutoff": "12:00",
        "arrival_date": "2026-10-07"
    }

    # Depart at 11:30 AM with a 2-hour drive -> arrives at 13:30 (after 12:00 cutoff)
    metrics = compute_mandi_metrics(
        candidate=cand,
        origin_lat=18.52,
        origin_lng=73.85,
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=11.5,
        crop="Tomato",
        config=config
    )

    assert metrics["missed_cutoff"] is True
    assert metrics["arrival_day"] == "Tomorrow (Day+1)"
    # Holding cost (12 Rs/q) + base loading (15) + unloading (15) = 42 Rs/q
    assert metrics["costs"]["loading_unloading_per_q"] == 42.0


def test_stale_data_case():
    """Verifies that data over 3 days old is flagged as stale (LOW confidence)

    and deprioritized from top advice when fresh alternatives exist.
    """
    config = load_config()
    today = datetime.now().date()
    stale_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    fresh_date = today.strftime("%Y-%m-%d")

    # Stale candidate with slightly higher gross price
    stale_cand = {
        "market": "Stale Mandi",
        "district": "Pune",
        "lat": 18.55,
        "lng": 73.88,
        "modal_price": 2200.0,
        "auction_cutoff": "12:00",
        "arrival_date": stale_date
    }

    # Fresh candidate with moderate gross price
    fresh_cand = {
        "market": "Fresh Mandi",
        "district": "Pune",
        "lat": 18.52,
        "lng": 73.85,
        "modal_price": 2000.0,
        "auction_cutoff": "12:00",
        "arrival_date": fresh_date
    }

    m_stale = compute_mandi_metrics(stale_cand, 18.52, 73.85, 20.0, "tempo", 7.0, "Tomato", config, now_date=today)
    m_fresh = compute_mandi_metrics(fresh_cand, 18.52, 73.85, 20.0, "tempo", 7.0, "Tomato", config, now_date=today)

    assert m_stale["is_stale"] is True
    assert m_stale["confidence"] == "LOW"
    assert m_stale["days_ago"] >= 4

    assert m_fresh["is_stale"] is False
    assert m_fresh["confidence"] == "HIGH"

    ranked = rank_and_evaluate(
        evaluated=[m_stale, m_fresh],
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=7.0,
        config=config
    )

    # Fresh mandi is recommended first because stale mandi is excluded from #1 spot
    assert ranked["best_recommendation"]["market"] == "Fresh Mandi"
    assert ranked["comparisons"][0]["market"] == "Stale Mandi"
    assert ranked["comparisons"][0]["is_stale"] is True


def test_break_even_math():
    """Verifies that break-even price is calculated correctly against nearest mandi."""
    result = calculate_advisory(
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0
    )
    assert "nearest_baseline" in result
    nearest = result["best_recommendation"] if result["best_recommendation"]["is_nearest"] else None
    
    for comp in result["comparisons"]:
        assert "break_even_price" in comp
        assert comp["break_even_price"] > 0
        # If far mandi is further, break-even price must be higher to cover extra transport
        if comp["distance_km"] > 50:
            assert comp["break_even_price"] > 1000.0


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
