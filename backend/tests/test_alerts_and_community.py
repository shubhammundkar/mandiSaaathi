"""Unit tests for Step 11: Alerts, Farmer Reports, and Data Quality.

Verifies:
1. Alert Subscriptions (subscribe, list, delete) and WhatsApp morning preview built from real data.
2. "I sold today" Farmer Reports saving to farmer_reports with strict sanity checks,
   and displaying with a "Farmer reported" badge (never mixed into Agmarknet mandi_prices).
3. Data quality endpoint reporting per-mandi last reported date, 30-day coverage, and confidence badge.
"""

from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import execute_query, fetch_all, fetch_one
from backend.services.alerts_service import (
    delete_alert,
    generate_morning_alert_preview,
    get_active_alerts,
    get_data_quality,
    get_farmer_reports,
    save_farmer_report,
    subscribe_alert,
)

client = TestClient(app)


def test_alert_subscribe_list_delete_flow():
    """Verifies subscribing, listing, and deleting alert subscriptions."""
    # 1. Subscribe
    sub_res = client.post("/api/alerts/subscribe", json={
        "crop": "Tomato",
        "district": "Pune",
        "language": "mr",
        "nickname": "रामभाऊ"
    })
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["crop"] == "Tomato"
    assert sub_data["district"] == "Pune"
    assert sub_data["language"] == "mr"
    assert sub_data["nickname"] == "रामभाऊ"
    assert "id" in sub_data
    sub_id = sub_data["id"]

    try:
        # 2. List
        list_res = client.get("/api/alerts")
        assert list_res.status_code == 200
        subs = list_res.json().get("subscriptions", [])
        assert any(s["id"] == sub_id for s in subs)

        # 3. Delete
        del_res = client.delete(f"/api/alerts/{sub_id}")
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "success"

        # 4. Verify no longer active
        list_after = client.get("/api/alerts").json().get("subscriptions", [])
        assert not any(s["id"] == sub_id for s in list_after)
    finally:
        # Cleanup
        execute_query("DELETE FROM alert_subscriptions WHERE id = ?", (sub_id,))


def test_whatsapp_morning_preview_real_data():
    """Verifies that WhatsApp-style morning preview is constructed from real advisory and forecast figures."""
    # Test Marathi preview
    res_mr = client.post("/api/alerts/preview", json={
        "crop": "Tomato",
        "district": "Pune",
        "language": "mr",
        "nickname": "बाळू शिंदे"
    })
    assert res_mr.status_code == 200
    data_mr = res_mr.json()
    preview_mr = data_mr["preview_text"]

    assert "बाळू शिंदे" in preview_mr
    assert "₹" in preview_mr
    assert "पुणे" in preview_mr or "Pune" in preview_mr or "दैनिक" in preview_mr
    assert "बाजार समिती" in preview_mr or "सर्वोत्तम" in preview_mr
    # WhatsApp formatting check (*bold*)
    assert "*" in preview_mr

    # Test English preview
    res_en = client.post("/api/alerts/preview", json={
        "crop": "Tomato",
        "district": "Pune",
        "language": "en",
        "nickname": "Kisan Friend"
    })
    assert res_en.status_code == 200
    data_en = res_en.json()
    preview_en = data_en["preview_text"]

    assert "Kisan Friend" in preview_en
    assert "Modal Price" in preview_en
    assert "Net Return" in preview_en
    assert "Distance" in preview_en
    assert "₹" in preview_en


def test_farmer_report_sanity_checks():
    """Verifies that farmer report submissions reject invalid prices, quantities, and dates."""
    today = datetime.now().date()
    future_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

    # 1. Price <= 0 rejected
    res_neg_price = client.post("/api/farmer-reports", json={
        "crop": "Tomato", "market": "Pune", "price": -50.0, "quantity": 10.0
    })
    assert res_neg_price.status_code in (400, 422)

    # 2. Absurdly high price (> 50,000) rejected
    res_high_price = client.post("/api/farmer-reports", json={
        "crop": "Tomato", "market": "Pune", "price": 999999.0, "quantity": 10.0
    })
    assert res_high_price.status_code in (400, 422)

    # 3. Quantity <= 0 rejected
    res_neg_qty = client.post("/api/farmer-reports", json={
        "crop": "Tomato", "market": "Pune", "price": 2000.0, "quantity": 0.0
    })
    assert res_neg_qty.status_code in (400, 422)

    # 4. Future date rejected
    res_future = client.post("/api/farmer-reports", json={
        "crop": "Tomato", "market": "Pune", "price": 2000.0, "quantity": 10.0,
        "report_date": future_date
    })
    assert res_future.status_code in (400, 422)


def test_farmer_report_saving_and_separation_from_agmarknet():
    """Verifies saving to farmer_reports, 'Farmer reported' badge, and isolation from mandi_prices."""
    test_market = "Pimpalgaon"
    test_price = 2350.0
    test_qty = 40.0
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. Submit valid farmer report
    sub_res = client.post("/api/farmer-reports", json={
        "crop": "Tomato",
        "market": test_market,
        "price": test_price,
        "quantity": test_qty,
        "report_date": today_str
    })
    assert sub_res.status_code == 200
    report_data = sub_res.json()
    assert report_data["badge"] == "Farmer reported"
    assert report_data["source"] == "farmer_reported"
    assert report_data["is_farmer_reported"] is True
    report_id = report_data["id"]

    try:
        # 2. Verify returned in GET /api/farmer-reports with 'Farmer reported' badge
        get_res = client.get(f"/api/farmer-reports?market={test_market}")
        assert get_res.status_code == 200
        feed = get_res.json()
        assert feed["badge"] == "Farmer reported"
        assert feed["source"] == "farmer_reported"
        reports = feed["reports"]
        assert any(r["id"] == report_id and r["badge"] == "Farmer reported" for r in reports)

        # 3. Critical Requirement: NEVER mixed into Agmarknet mandi_prices table!
        mandi_prices_check = fetch_all("""
            SELECT * FROM mandi_prices 
            WHERE source = 'farmer_reported' OR source = 'farmer'
        """)
        assert len(mandi_prices_check) == 0, "Farmer reports must NEVER be mixed into mandi_prices!"

        mandi_prices_market_check = fetch_one("""
            SELECT COUNT(*) as cnt FROM mandi_prices
            WHERE market = ? AND modal_price = ? AND arrival_date = ? AND source = 'farmer_reported'
        """, (test_market, test_price, today_str))
        assert mandi_prices_market_check["cnt"] == 0
    finally:
        # Cleanup
        execute_query("DELETE FROM farmer_reports WHERE id = ?", (report_id,))


def test_data_quality_endpoint():
    """Verifies data quality per mandi: last reported date, 30-day coverage, and confidence badge."""
    res = client.get("/api/data-quality")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "ready"
    assert "total_monitored_mandis" in data
    assert data["total_monitored_mandis"] >= 15
    assert "high_confidence_mandis" in data
    assert "medium_confidence_mandis" in data
    assert "low_confidence_mandis" in data

    mandis = data.get("mandis", [])
    assert len(mandis) == data["total_monitored_mandis"]

    # Check structure of each mandi entry
    for m in mandis:
        assert "market" in m
        assert "district" in m
        assert "latest_reported_date" in m
        assert "coverage_pct_30d" in m
        assert 0.0 <= m["coverage_pct_30d"] <= 100.0
        assert "confidence" in m
        assert m["confidence"] in ("HIGH", "MEDIUM", "LOW")
        assert "confidence_badge" in m
        assert m["confidence_badge"] in ("green", "yellow", "red")
        assert "coordinates_present" in m
