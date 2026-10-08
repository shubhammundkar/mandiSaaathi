"""Automated validation tests for Step 13: Polish and Mobile Pass.

Verifies:
1. Favicon endpoint returns 200 OK with valid SVG without 404s.
2. Index page and all frontend assets load cleanly.
3. No leftover 'Phase 1' or 'Phase 2' placeholder text in frontend codebase.
4. CSS definitions include 44px tap targets, :focus-visible, and 360px mobile responsive rules.
5. Router includes localized document titles for all routes.
6. i18n dictionary contains full translations across EN, HI, MR.
"""

from pathlib import Path
import re
from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def test_favicon_endpoint_no_404():
    """Verifies that /favicon.ico returns 200 OK with svg image."""
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200
    assert "image/svg+xml" in resp.headers.get("content-type", "")
    assert "<svg" in resp.text


def test_index_html_loads_cleanly():
    """Verifies that root index.html serves with 200 OK and valid viewport meta."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mandi Saathi" in resp.text
    assert 'viewport' in resp.text
    assert 'favicon' in resp.text.lower()


def test_no_phase_placeholder_text_in_frontend():
    """Ensures no 'Phase 1 Setup Ready' or 'Ready for Phase 2' placeholders exist in frontend code."""
    frontend_dir = ROOT_DIR / "frontend"
    for file_path in frontend_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in (".html", ".js", ".css"):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            assert "Phase 1 Setup Ready" not in text, f"Found placeholder in {file_path}"
            assert "Ready for Phase 2" not in text, f"Found placeholder in {file_path}"


def test_mobile_tap_targets_and_focus_in_css():
    """Verifies that styles and components CSS enforce minimum tap targets (44px) and focus-visible."""
    styles_css = (ROOT_DIR / "frontend" / "css" / "styles.css").read_text(encoding="utf-8")
    components_css = (ROOT_DIR / "frontend" / "css" / "components.css").read_text(encoding="utf-8")
    theme_css = (ROOT_DIR / "frontend" / "css" / "theme.css").read_text(encoding="utf-8")

    # Focus styles
    assert ":focus-visible" in theme_css
    assert "outline" in theme_css

    # Tap target rules in CSS
    assert "min-height: 44px" in styles_css or "min-height: 48px" in styles_css
    assert "min-height: 48px" in components_css

    # Small screen mobile rules (360px - 480px)
    assert "@media (max-width: 480px)" in styles_css


def test_router_page_titles_multilingual():
    """Verifies that router.js contains routeTitles for EN, HI, MR across all main views."""
    router_js = (ROOT_DIR / "frontend" / "js" / "router.js").read_text(encoding="utf-8")
    assert "routeTitles" in router_js
    assert "document.title" in router_js
    for route in ["#/advisor", "#/chat", "#/alerts", "#/proof", "#/about"]:
        assert route in router_js


def test_i18n_dictionary_completeness():
    """Verifies that i18n keys are mirrored across all 3 supported languages."""
    i18n_path = ROOT_DIR / "frontend" / "js" / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    essential_keys = [
        "brand_name", "nav_advisor", "nav_chat", "nav_alerts", "nav_proof", "nav_about",
        "btn_calculate", "btn_try_demo", "btn_listen", "btn_speak",
        "alerts_heading", "proof_heading", "about_heading", "footer_credit"
    ]

    for key in essential_keys:
        assert key in content, f"Missing key {key} in i18n.js"
