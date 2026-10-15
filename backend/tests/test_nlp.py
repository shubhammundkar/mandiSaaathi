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


def test_marathi_pune_jilha_query():
    """Verifies that 'Mala 20 quintal tomato vikaycha aahe, Pune jilha'

    returns crop Tomato, quantity 20, district Pune.
    """
    res = client.post("/api/chat", json={
        "message": "Mala 20 quintal tomato vikaycha aahe, Pune jilha"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["entities"]["crop"] == "Tomato"
    assert data["entities"]["quantity"] == 20.0
    assert data["entities"]["location"] == "Pune"
    assert data["intent"] == "best_market"
    assert data["follow_up_needed"] is False


def test_blank_gemini_key_fallback(monkeypatch):
    """Verifies that with GEMINI_API_KEY blank, fallback still works."""
    import backend.services.nlp_service as nlp
    monkeypatch.setattr(nlp, "GEMINI_API_KEY", "")

    res = client.post("/api/chat", json={
        "message": "Nashik me 50 kwintal pyaaz kaha bechu?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["entities"]["crop"] == "Onion"
    assert data["entities"]["quantity"] == 50.0
    assert data["entities"]["location"] == "Nashik"


def test_vague_query_price_follow_up():
    """Verifies that a vague query like 'price?' gets a single follow-up question."""
    res = client.post("/api/chat", json={
        "message": "price?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "price_check"
    assert data["missing_field"] == "crop"
    assert data["follow_up_needed"] is True
    assert ("crop" in data["reply"].lower() or "फसल" in data["reply"] or "पीक" in data["reply"])


def test_chat_trailing_slash_tolerance():
    """Verifies that both /api/chat and /api/chat/ succeed with 200 (no 405 Method Not Allowed)."""
    msg = {"message": "Should I sell or store Onion in Lasalgaon?"}
    res_no_slash = client.post("/api/chat", json=msg)
    assert res_no_slash.status_code == 200
    assert res_no_slash.json()["intent"] == "store_or_sell"

    res_slash = client.post("/api/chat/", json=msg)
    assert res_slash.status_code == 200
    assert res_slash.json()["intent"] == "store_or_sell"


# =============================================================================
# Marathi Complete Voice Conversation Tests
# =============================================================================

def test_marathi_natural_speech_best_market():
    """Verifies natural colloquial Marathi query: 'माझा २० क्विंटल टोमॅटो आहे, कुठे विकू?'."""
    res = client.post("/api/chat", json={
        "message": "पुण्यात माझा २० क्विंटल टोमॅटो आहे, कुठे विकू?",
        "language": "mr"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["language"] == "mr"
    assert data["intent"] == "best_market"
    assert data["entities"]["crop"] == "Tomato"
    assert data["entities"]["quantity"] == 20.0
    assert data["entities"]["location"] == "Pune"
    assert data["follow_up_needed"] is False

    # Response must be in Marathi Devanagari with real economics
    reply = data["reply"]
    assert "टोमॅटो" in reply
    assert "₹" in reply
    assert "निव्वळ नफा" in reply
    assert "वाहतूक खर्च" in reply
    assert "सल्ला:" in reply
    # No English leaks
    assert "Sell locally" not in reply
    assert "Gross Mandi Price" not in reply


def test_marathi_natural_speech_price_check():
    """Verifies natural colloquial Marathi query: 'पुण्यात टोमॅटोचा आजचा भाव काय आहे?'."""
    res = client.post("/api/chat", json={
        "message": "पुण्यात टोमॅटोचा आजचा भाव काय आहे?",
        "language": "mr"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["language"] == "mr"
    assert data["intent"] == "price_check"
    assert data["entities"]["crop"] == "Tomato"
    assert data["entities"]["location"] == "Pune"
    assert data["follow_up_needed"] is False

    reply = data["reply"]
    assert "टोमॅटो" in reply
    assert "₹" in reply
    assert "सरासरी (मॉडेल) भाव" in reply or "किमान भाव" in reply
    assert "Agmarknet" in reply


def test_marathi_natural_speech_store_or_sell():
    """Verifies natural colloquial Marathi query: 'माझ्याकडे कांदा आहे, आता विकू की साठवून ठेवू?'."""
    res = client.post("/api/chat", json={
        "message": "लासलगावमध्ये माझ्याकडे कांदा आहे, आता विकू की साठवून ठेवू?",
        "language": "mr"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["language"] == "mr"
    assert data["intent"] == "store_or_sell"
    assert data["entities"]["crop"] == "Onion"
    assert data["follow_up_needed"] is False

    reply = data["reply"]
    assert "कांदा" in reply
    assert "₹" in reply
    assert "शिफारस:" in reply
    assert "विश्लेषण:" in reply
    # Must not contain English "(Sell now)" or English rationale
    assert "(Sell now)" not in reply
    assert "Holding for" not in reply


def test_marathi_multi_turn_conversation_with_context():
    """Verifies multi-turn contextual conversation where session state is preserved across turns.

    Turn 1: "मला २० क्विंटल माल विकायचा आहे, कुठे नेऊ?" -> AI asks for crop in Marathi.
    Turn 2: "टोमॅटो" -> AI remembers quantity=20 and asks for location in Marathi.
    Turn 3: "पुणे" -> AI has crop=Tomato, quantity=20, location=Pune and gives full best market recommendation.
    Turn 4: "आणि नाशिकचा काय भाव आहे?" -> AI maintains crop=Tomato, updates location=Nashik, intent=price_check.
    Turn 5: "साठवून ठेवू का?" -> AI maintains crop=Tomato and gives storage advice in Marathi.
    Turn 6: "धन्यवाद" -> AI responds warmly in Marathi.
    """
    session_id = "test-session-marathi-101"

    # Turn 1: Missing crop
    res1 = client.post("/api/chat", json={
        "message": "मला २० क्विंटल माल विकायचा आहे, कुठे नेऊ?",
        "session_id": session_id,
        "language": "mr"
    })
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["language"] == "mr"
    assert d1["follow_up_needed"] is True
    assert d1["missing_field"] == "crop"
    assert "कोणत्या पिकासाठी" in d1["reply"]

    # Turn 2: User provides crop
    res2 = client.post("/api/chat", json={
        "message": "टोमॅटो",
        "session_id": session_id,
        "language": "mr"
    })
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["language"] == "mr"
    assert d2["follow_up_needed"] is True
    assert d2["missing_field"] == "location"
    assert d2["entities"]["crop"] == "Tomato"
    assert d2["entities"]["quantity"] == 20.0
    assert "कोणत्या जिल्ह्यातून" in d2["reply"]

    # Turn 3: User provides location
    res3 = client.post("/api/chat", json={
        "message": "पुणे",
        "session_id": session_id,
        "language": "mr"
    })
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["language"] == "mr"
    assert d3["follow_up_needed"] is False
    assert d3["entities"]["crop"] == "Tomato"
    assert d3["entities"]["quantity"] == 20.0
    assert d3["entities"]["location"] == "Pune"
    assert "निव्वळ नफा" in d3["reply"]
    assert "₹" in d3["reply"]

    # Turn 4: Contextual follow-up for different location price
    res4 = client.post("/api/chat", json={
        "message": "आणि नाशिकचा काय भाव आहे?",
        "session_id": session_id,
        "language": "mr"
    })
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["language"] == "mr"
    assert d4["entities"]["crop"] == "Tomato"
    assert d4["entities"]["location"] == "Nashik"
    assert "नाशिक" in d4["reply"] or "Nashik" in str(d4["data"])

    # Turn 5: Contextual follow-up for storage
    res5 = client.post("/api/chat", json={
        "message": "साठवून ठेवू का?",
        "session_id": session_id,
        "language": "mr"
    })
    assert res5.status_code == 200
    d5 = res5.json()
    assert d5["language"] == "mr"
    assert d5["intent"] == "store_or_sell"
    assert d5["entities"]["crop"] == "Tomato"
    assert "नाशवंत" in d5["reply"] or "साठवणूक" in d5["reply"]

    # Turn 6: Gratitude
    res6 = client.post("/api/chat", json={
        "message": "धन्यवाद",
        "session_id": session_id,
        "language": "mr"
    })
    assert res6.status_code == 200
    d6 = res6.json()
    assert d6["language"] == "mr"
    assert "स्वागत" in d6["reply"]


def test_marathi_word_numbers_and_units():
    """Verifies that Marathi number words and agricultural units (पोती, टन, गाडी) are parsed."""
    # 50 poti = 25 quintals
    res1 = client.post("/api/chat", json={
        "message": "पुण्यात पन्नास पोती कांदा कुठे विकू?",
        "language": "mr"
    })
    assert res1.status_code == 200
    assert res1.json()["entities"]["crop"] == "Onion"
    assert res1.json()["entities"]["quantity"] == 25.0
    assert res1.json()["entities"]["location"] == "Pune"

    # 2 ton = 20 quintals
    res2 = client.post("/api/chat", json={
        "message": "लातूरला २ टन सोयाबीन नेऊ का?",
        "language": "mr"
    })
    assert res2.status_code == 200
    assert res2.json()["entities"]["crop"] == "Soybean"
    assert res2.json()["entities"]["quantity"] == 20.0
    assert res2.json()["entities"]["location"] == "Latur"


def test_marathi_greetings_and_identity():
    """Verifies greeting ('नमस्कार') and identity ('तू कोण आहेस')."""
    res_greet = client.post("/api/chat", json={
        "message": "नमस्कार",
        "language": "mr"
    })
    assert res_greet.status_code == 200
    assert "नमस्कार शेतकरी मित्र" in res_greet.json()["reply"]

    res_who = client.post("/api/chat", json={
        "message": "तू कोण आहेस?",
        "language": "mr"
    })
    assert res_who.status_code == 200
    assert "मंडी साथी" in res_who.json()["reply"]



