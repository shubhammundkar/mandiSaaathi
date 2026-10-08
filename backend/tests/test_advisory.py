"""Unit tests for the Advisory Engine and Data Service.

Verifies net return calculations, timing and cutoff rules, break-even math,
stale-data deprioritization, and the canonical test: nearest Rs 200 today beats far Rs 180 tomorrow plus higher transport.
"""

from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.data_service import get_data_status, get_crops, get_mandis
from backend.services.advisory_engine import (
    calculate_advisory,
    compute_mandi_metrics,
    haversine_distance,
    load_config,
    rank_and_evaluate
)

client = TestClient(app)


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


def test_market_no_coordinates_never_recommended_and_pune_to_pimpalgaon_distance():
    """Test: a market with no coordinates is never recommended, and Pune to Pimpalgaon distance is not 8 km."""
    from backend.database import execute_query
    from backend.services.data_service import load_mandi_matrix
    from backend.services.advisory_engine import get_origin_coords

    # 1. Verify Pune to Pimpalgaon distance is NOT 8 km
    matrix = load_mandi_matrix()
    matrix_map = {m["market"]: m for m in matrix.get("mandis", [])}
    assert "Pimpalgaon" in matrix_map
    pimp = matrix_map["Pimpalgaon"]
    pune_lat, pune_lng = get_origin_coords("Pune")

    dist_pune_pimpalgaon = haversine_distance(pune_lat, pune_lng, pimp["lat"], pimp["lng"])
    # Real road distance between Pune and Pimpalgaon (Nashik) is ~230 km
    assert dist_pune_pimpalgaon != 8.0, "Pune to Pimpalgaon distance must not be the fallback 8.0 km!"
    assert 180.0 <= dist_pune_pimpalgaon <= 260.0, f"Expected distance ~230 km, got {dist_pune_pimpalgaon}"

    # Verify advisory engine calculates ~230 km and not 8 km when evaluating Pimpalgaon from Pune
    adv = calculate_advisory(crop="Tomato", district="Pune")
    all_recs = ([adv["best_recommendation"]] if adv.get("best_recommendation") else []) + adv.get("comparisons", [])
    pimp_adv = next((m for m in all_recs if m["market"] == "Pimpalgaon"), None)
    if pimp_adv:
        assert pimp_adv["distance_km"] != 8.0
        assert pimp_adv["distance_km"] > 150.0

    # 2. Verify a market with no coordinates is NEVER recommended
    ghost_market = "UnmappedGhostMandi"
    execute_query("""
        INSERT INTO mandi_prices (
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price,
            arrival_quantity, source, is_sample, fetched_at
        ) VALUES (
            'Maharashtra', 'UnknownDist', ?, 'Tomato', 'Hybrid', 'FAQ',
            '2026-10-08', 9500.0, 9900.0, 9800.0, 50.0, 'sample', 1, '2026-10-08T12:00:00'
        )
    """, (ghost_market,))

    try:
        res = calculate_advisory(crop="Tomato", district="Pune")
        best = res.get("best_recommendation")
        comparisons = res.get("comparisons", [])
        excluded = res.get("excluded_markets", [])

        # Market with no coordinates must NEVER be best recommendation
        assert best is not None
        assert best["market"] != ghost_market, "Market with no coordinates must NEVER be recommended!"

        # Must NOT appear in comparisons ranking
        assert not any(c["market"] == ghost_market for c in comparisons)

        # Must be in excluded_markets with flag 'location unknown'
        ghost_ex = [m for m in excluded if m["market"] == ghost_market]
        assert len(ghost_ex) == 1
        assert ghost_ex[0]["flag"] == "location unknown"
        assert ghost_ex[0]["distance_km"] is None  # Never invented!
        assert ghost_ex[0]["is_excluded"] is True
    finally:
        execute_query("DELETE FROM mandi_prices WHERE market = ?", (ghost_market,))


def test_rank_and_evaluate_excludes_unknown_location():
    """Direct test that rank_and_evaluate excludes candidates with missing distance or flag 'location unknown'."""
    cand_unknown = {
        "market": "NoCoordMandi",
        "district": "Nowhere",
        "distance_km": None,
        "flag": "location unknown",
        "is_excluded": True,
        "net_return_per_quintal": 5000.0,
        "gross_modal_price": 5200.0
    }
    cand_valid = {
        "market": "ValidMandi",
        "district": "Pune",
        "distance_km": 20.0,
        "travel_hours": 0.5,
        "is_stale": False,
        "missed_cutoff": False,
        "gross_modal_price": 2000.0,
        "net_return_per_quintal": 1850.0,
        "costs": {"transport_per_q": 36.0, "loading_unloading_per_q": 30.0}
    }

    res = rank_and_evaluate(
        evaluated=[cand_unknown, cand_valid],
        crop="Tomato",
        district="Pune",
        quantity_quintals=20.0,
        vehicle_type="tempo",
        departure_hour=7.0
    )
    assert res["best_recommendation"]["market"] == "ValidMandi"
    assert not any(c["market"] == "NoCoordMandi" for c in res["comparisons"])
    assert any(ex["market"] == "NoCoordMandi" and ex["flag"] == "location unknown" for ex in res["excluded_markets"])


def test_advise_pune_sensible_distances():
    """Verifies that /api/advise for Pune lists sensible distances (tens or hundreds of km, not 8)."""
    res = client.post("/api/advise", json={"crop": "Tomato", "district": "Pune"})
    assert res.status_code == 200
    data = res.json()
    best = data.get("best_recommendation")
    assert best is not None
    assert "distance_km" in best
    # Pune local APMC is across town (~3.5 km)
    assert 1.0 <= best["distance_km"] <= 30.0

    comps = data.get("comparisons", [])
    assert len(comps) > 0
    for comp in comps:
        dist = comp["distance_km"]
        assert dist is not None
        # All non-local comparison mandis are tens or hundreds of km away (not 8.0 km)
        assert dist != 8.0, f"Mandi {comp['market']} must not have fallback 8.0 km distance!"
        # Distance should be sensible between 10 km and 1000 km
        assert 10.0 <= dist <= 1000.0, f"Mandi {comp['market']} has unexpected distance {dist}"

    # Specifically check Pimpalgaon Baswant in comparisons
    pimp = next((c for c in comps if "Pimpalgaon" in c["market"]), None)
    if pimp:
        assert pimp["distance_km"] > 200.0, f"Pimpalgaon should be ~230 km from Pune, got {pimp['distance_km']}"


def test_api_mandis_has_coordinates_or_visible_flag():
    """Verifies that every mandi in /api/mandis has coordinates or a visible flag."""
    from backend.database import execute_query

    res = client.get("/api/mandis")
    assert res.status_code == 200
    mandis = res.json().get("mandis", [])
    assert len(mandis) >= 15

    for m in mandis:
        assert "market" in m
        assert "district" in m
        if m.get("lat") is not None and m.get("lng") is not None:
            assert isinstance(m["lat"], (int, float))
            assert isinstance(m["lng"], (int, float))
            assert m["flag"] in ("approximate", "verified")
            assert m["location_status"] == "known"
        else:
            assert m["flag"] == "location unknown"
            assert m["location_status"] == "location unknown"

    # Insert an unmapped market to test visible flag when coordinates are missing
    unmapped_market = "UnmappedTestMandi"
    execute_query("""
        INSERT INTO mandi_prices (
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price,
            arrival_quantity, source, is_sample, fetched_at
        ) VALUES (
            'Maharashtra', 'MysteryDistrict', ?, 'Tomato', 'Hybrid', 'FAQ',
            '2026-10-08', 2000.0, 2500.0, 2200.0, 50.0, 'sample', 1, '2026-10-08T12:00:00'
        )
    """, (unmapped_market,))

    try:
        res2 = client.get("/api/mandis")
        assert res2.status_code == 200
        mandis2 = res2.json().get("mandis", [])
        unmapped_entry = next((m for m in mandis2 if m["market"] == unmapped_market), None)
        assert unmapped_entry is not None
        assert unmapped_entry["lat"] is None
        assert unmapped_entry["lng"] is None
        assert unmapped_entry["flag"] == "location unknown"
        assert unmapped_entry["location_status"] == "location unknown"
    finally:
        execute_query("DELETE FROM mandi_prices WHERE market = ?", (unmapped_market,))


