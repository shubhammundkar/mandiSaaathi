"""Tests for Multilingual NLP Service & Chat Route.

Verifies entity extraction, synonym handling (kanda/pyaaz, tamatar, kwintal),
intent routing (best_market, store_or_sell, price_check, help), single follow-up
prompting when an entity is missing, and real economic calculations in replies.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.nlp_service import (
    extract_entities_regex,
    process_chat_message
)

client = TestClient(app)


def test_query_1_english_best_market():
    """Query 1: English Best Market with full crop, quantity, and location.

    "I have 20 quintals of tomato in Pune, where should I sell?"
    """
    res = client.post("/api/chat", json={
        "message": "I have 20 quintals of tomato in Pune, where should I sell?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "best_market"
    assert data["entities"]["crop"] == "Tomato"
    assert data["entities"]["quantity"] == 20.0
    assert data["entities"]["location"] == "Pune"
    assert data["follow_up_needed"] is False
    assert data["missing_field"] is None

    # Reply must contain real numbers from the advisory engine
    reply = data["reply"]
    assert "₹" in reply
    assert "Pimpalgaon" in reply or "Pune" in reply
    assert "per_quintal" in str(data["data"]) or "net_return_per_quintal" in str(data["data"])
    assert data["data"]["best_recommendation"]["net_return_per_quintal"] > 0


def test_query_2_hindi_best_market_synonyms():
    """Query 2: Hindi Best Market with synonyms (pyaaz = onion, kwintal, kaha bechu).

    "Nashik me 50 kwintal pyaaz kaha bechu?"
    """
    res = client.post("/api/chat", json={
        "message": "Nashik me 50 kwintal pyaaz kaha bechu?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "best_market"
    assert data["entities"]["crop"] == "Onion"
    assert data["entities"]["quantity"] == 50.0
    assert data["entities"]["location"] == "Nashik"
    assert data["follow_up_needed"] is False
    assert data["language"] in ["hi", "mr"]

    # Must contain real numbers in Hindi
    reply = data["reply"]
    assert "₹" in reply
    assert "मंडी" in reply
    assert "क्विंटल" in reply


def test_query_3_marathi_store_or_sell_synonyms():
    """Query 3: Marathi Store or Sell with synonyms (kanda = onion, viku ki thevu).

    "Lasalgaon madhe kanda viku ki thevu?"
    """
    res = client.post("/api/chat", json={
        "message": "Lasalgaon madhe kanda viku ki thevu?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "store_or_sell"
    assert data["entities"]["crop"] == "Onion"
    assert data["entities"]["location"] in ["Nashik", "Lasalgaon"]
    assert data["follow_up_needed"] is False
    assert data["language"] == "mr"

    reply = data["reply"]
    assert "कांदा" in reply
    assert "₹" in reply
    assert ("आता विका" in reply) or ("थांबा" in reply) or ("साठवणूक" in reply)
    assert data["data"] is not None
    assert "recommendation" in data["data"]


def test_query_4_hindi_price_check():
    """Query 4: Hindi Price Check with synonyms (tamatar = tomato, aaj ka bhav).

    "Pune me tamatar ka aaj ka bhav kya hai?"
    """
    res = client.post("/api/chat", json={
        "message": "Pune me tamatar ka aaj ka bhav kya hai?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "price_check"
    assert data["entities"]["crop"] == "Tomato"
    assert data["entities"]["location"] == "Pune"
    assert data["follow_up_needed"] is False
    assert data["language"] in ["hi", "mr"]

    reply = data["reply"]
    assert "₹" in reply
    assert "मॉडल भाव" in reply or "सरासरी" in reply or "भाव" in reply
    assert data["data"] is not None
    assert "modal_price" in data["data"]


def test_query_5_missing_crop_follow_up():
    """Query 5: Follow-up required when crop is missing.

    "Mala 30 quintal vikaayche ahe, kuthe viku?" -> Missing crop
    """
    res = client.post("/api/chat", json={
        "message": "Mala 30 quintal vikaayche ahe, kuthe viku?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "best_market"
    assert data["entities"]["crop"] is None
    assert data["entities"]["quantity"] == 30.0
    assert data["follow_up_needed"] is True
    assert data["missing_field"] == "crop"

    # Must ask ONE targeted question about crop
    reply = data["reply"]
    assert ("पिकासाठी" in reply) or ("crop" in reply.lower()) or ("फसल" in reply)


def test_query_6_missing_location_follow_up():
    """Query 6: Follow-up required when location is missing for best_market.

    "Where should I sell my 25 quintals of Soybean?" -> Missing location
    """
    res = client.post("/api/chat", json={
        "message": "Where should I sell my 25 quintals of Soybean?"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "best_market"
    assert data["entities"]["crop"] == "Soybean"
    assert data["entities"]["quantity"] == 25.0
    assert data["entities"]["location"] is None
    assert data["follow_up_needed"] is True
    assert data["missing_field"] == "location"

    # Must ask ONE targeted question about location
    reply = data["reply"]
    assert "district" in reply.lower() or "town" in reply.lower() or "location" in reply.lower()


def test_query_7_help_intent():
    """Bonus Query 7: Help intent.

    "Namaste, help me use Mandi Saathi"
    """
    res = client.post("/api/chat", json={
        "message": "Namaste, help me use Mandi Saathi"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["intent"] == "help"
    assert data["follow_up_needed"] is False
    assert "Mandi Saathi" in data["reply"] or "मंडी साथी" in data["reply"]


def test_empty_message_validation():
    """Verifies that an empty chat message returns 400."""
    res = client.post("/api/chat", json={"message": "   "})
    assert res.status_code == 400


def test_gemini_fallback_and_extraction(monkeypatch):
    """Verifies that when GEMINI_API_KEY is present, Gemini extraction is invoked

    and handled properly.
    """
    import backend.services.nlp_service as nlp

    # Mock extract_entities_gemini returning valid structured JSON
    def mock_gemini(query):
        return {
            "crop": "Tomato",
            "quantity": 40.0,
            "location": "Pune",
            "intent": "best_market",
            "language": "en"
        }

    monkeypatch.setattr(nlp, "GEMINI_API_KEY", "mock-test-key")
    monkeypatch.setattr(nlp, "extract_entities_gemini", mock_gemini)

    result = nlp.extract_entities("mock query")
    assert result["crop"] == "Tomato"
    assert result["quantity"] == 40.0
    assert result["location"] == "Pune"
    assert result["intent"] == "best_market"

