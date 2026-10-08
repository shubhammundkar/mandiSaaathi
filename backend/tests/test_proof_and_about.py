"""Unit tests for Step 12: Proof and About pages.

Verifies:
1. Backtest API delivers stat cards metrics (average extra Rs per quintal, % days better,
   days tested), cumulative series for Chart.js, worse-days list, and honest assessment.
2. proof.js contains required frontend components (Chart.js integration, worse days, limits, formula breakdown).
3. about.js contains required sections (problem, 4-step architecture, limitations, and exact Agmarknet credit).
"""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def test_backtest_endpoint_payload_structure():
    """Verifies that /api/backtest delivers all data needed for proof.js stat cards and chart."""
    resp = client.get("/api/backtest?crop=Tomato&district=Pune&quantity=20&vehicle=tempo")
    assert resp.status_code == 200
    data = resp.json()

    # Stat cards metrics
    assert "average_extra_rs_per_quintal" in data
    assert isinstance(data["average_extra_rs_per_quintal"], (int, float))
    assert "percent_days_better" in data
    assert isinstance(data["percent_days_better"], (int, float))
    assert "days_tested" in data
    assert data["days_tested"] > 0

    # Chart.js series (cumulative Mandi Saathi vs nearest mandi)
    assert "cumulative_series" in data
    series = data["cumulative_series"]
    assert len(series) == data["days_tested"]
    first = series[0]
    assert "date" in first
    assert "mandi_saathi_cumulative" in first
    assert "nearest_cumulative" in first
    assert "diff_rs" in first

    # Worse days list
    assert "worse_days" in data
    assert isinstance(data["worse_days"], list)
    for wd in data["worse_days"]:
        assert "date" in wd
        assert "diff_rs" in wd
        assert wd["diff_rs"] < 0
        assert "reason" in wd

    # Honest assessment
    assert "honest_assessment" in data
    assert len(data["honest_assessment"]) > 10


def test_proof_page_frontend_requirements():
    """Verifies that proof.js contains Chart.js integration, stat cards, worse days, and formula breakdown."""
    proof_path = ROOT_DIR / "frontend" / "js" / "pages" / "proof.js"
    assert proof_path.exists(), "frontend/js/pages/proof.js must exist"

    content = proof_path.read_text(encoding="utf-8")

    # API integration
    assert "api.getBacktest" in content
    assert "backtest-chart" in content
    assert "new window.Chart" in content or "window.Chart" in content

    # Stat cards
    assert "average_extra_rs_per_quintal" in content
    assert "percent_days_better" in content
    assert "days_tested" in content

    # Worse days
    assert "worse_days" in content
    assert "renderWorseDays" in content

    # Plain note on limits
    assert "limitations" in content.lower() or "plain note" in content.lower()

    # Step-by-step formula breakdown for Try demo
    assert "renderDemoFormula" in content or "formula" in content.lower()
    assert "Tomato" in content
    assert "Pune" in content
    assert "20" in content


def test_about_page_frontend_requirements():
    """Verifies that about.js contains problem, 4-step architecture, limitations, and exact Agmarknet credit."""
    about_path = ROOT_DIR / "frontend" / "js" / "pages" / "about.js"
    assert about_path.exists(), "frontend/js/pages/about.js must exist"

    content = about_path.read_text(encoding="utf-8")

    # The Problem
    assert "problem" in content.lower() or "headline price" in content.lower()

    # 4-step how-it-works
    assert "Step 1" in content
    assert "Step 2" in content
    assert "Step 3" in content
    assert "Step 4" in content

    # Limitations
    assert "limitations" in content.lower()

    # Required Exact Data Credit
    assert "Data source: Agmarknet (agmarknet.gov.in)" in content
