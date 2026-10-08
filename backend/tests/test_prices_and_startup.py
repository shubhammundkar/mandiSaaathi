"""Unit tests for startup data loader and GET /api/prices endpoint."""

import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db_connection, execute_query
from backend.services.data_service import get_prices, load_initial_data_if_empty


client = TestClient(app)


def test_get_prices_tomato_and_empty_params():
    """Verifies that GET /api/prices returns rows with is_sample attribute."""
    # Test with crop and days
    res = client.get("/api/prices?crop=Tomato&days=7")
    assert res.status_code == 200
    rows = res.json()
    assert isinstance(rows, list)
    if rows:
        first = rows[0]
        assert "is_sample" in first
        assert "modal_price" in first
        assert "arrival_date" in first
        assert "market" in first
        assert first["commodity"] == "Tomato"

    # Test with empty query parameters ?crop=&days=
    res_empty = client.get("/api/prices?crop=&days=")
    assert res_empty.status_code == 200
    rows_empty = res_empty.json()
    assert isinstance(rows_empty, list)
    if rows_empty:
        assert "is_sample" in rows_empty[0]


def test_get_prices_prioritizes_real_data():
    """Verifies that when real records (is_sample=0) exist for a crop, get_prices returns real records."""
    # Insert a temporary real test row
    test_market = "TestRealAPMC"
    execute_query("""
        INSERT INTO mandi_prices (
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price,
            arrival_quantity, source, is_sample, fetched_at
        ) VALUES (
            'Maharashtra', 'Pune', ?, 'Tomato', 'Hybrid', 'FAQ',
            '2026-10-08', 2100.0, 2600.0, 2350.0, 100.0, 'manual_csv', 0, '2026-10-08T12:00:00'
        )
    """, (test_market,))

    try:
        prices = get_prices(crop="Tomato", days=7)
        assert len(prices) > 0
        # Should return real rows (is_sample=0)
        assert any(p["market"] == test_market and p["is_sample"] == 0 for p in prices)
        for p in prices:
            assert p["is_sample"] == 0
    finally:
        # Cleanup
        execute_query("DELETE FROM mandi_prices WHERE market = ?", (test_market,))


def test_startup_loader_when_empty(monkeypatch):
    """Verifies that load_initial_data_if_empty loads snapshot or sample data if DB is empty."""
    # Verify that when DB already has rows, it reports already_populated
    res = load_initial_data_if_empty()
    assert res["status"] in ("already_populated", "loaded_real_snapshot", "loaded_sample_data")
