"""Multilingual NLP Service for Mandi Saathi.

Extracts crop, quantity, location, and intent (best_market, store_or_sell, price_check, help)
from user messages in English, Hindi, and Marathi.
Uses Gemini REST API when GEMINI_API_KEY is available (requesting JSON schema only);
otherwise falls back to a deterministic, high-accuracy keyword and regex parser with full synonyms.
Formulates actionable replies containing real economic numbers from the advisory,
forecasting, and data engines.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from backend.config import GEMINI_API_KEY
from backend.services.advisory_engine import calculate_advisory
from backend.services.data_service import get_latest_prices_for_crop
from backend.services.forecast_engine import get_storage_advice

logger = logging.getLogger(__name__)

# Supported canonical crops
CANONICAL_CROPS = ["Tomato", "Onion", "Soybean", "Tur", "Cotton", "Potato", "Wheat"]

# Crop names in Hindi and Marathi for natural language replies
CROP_NAMES_TRANSLATION = {
    "Tomato": {"en": "Tomato", "hi": "टमाटर", "mr": "टोमॅटो"},
    "Onion": {"en": "Onion", "hi": "प्याज", "mr": "कांदा"},
    "Soybean": {"en": "Soybean", "hi": "सोयाबीन", "mr": "सोयाबीन"},
    "Tur": {"en": "Tur / Arhar", "hi": "तूर (अरहर)", "mr": "तूर"},
    "Cotton": {"en": "Cotton", "hi": "कपास", "mr": "कापूस"},
    "Potato": {"en": "Potato", "hi": "आलू", "mr": "बटाटा"},
    "Wheat": {"en": "Wheat", "hi": "गेहूं", "mr": "गहू"},
}

# Extensive multilingual crop synonyms
CROP_SYNONYMS: Dict[str, List[str]] = {
    "Tomato": [
        "tomato", "tomatoes", "tamatar", "tamater", "tameta",
        "टोमॅटो", "टोमॅटोचे", "टोमॅटोचा", "टोमॅटोला", "टोमॅटोत", "टमाटर", "टमाटरों"
    ],
    "Onion": [
        "onion", "onions", "kanda", "kande", "kandya", "kandyache", "kandyala", "kandacha",
        "pyaaz", "pyaj", "pyaz", "कांदा", "कांदे", "कांद्याचे", "कांद्याला",
        "कांद्याचा", "कांद्याची", "कांद्यात", "प्याज", "प्याज़"
    ],
    "Soybean": [
        "soybean", "soyabean", "soya", "soyabin",
        "सोयाबीन", "सोयाबीनचे", "सोयाबीनला", "सोया", "सोयाबिन"
    ],
    "Tur": [
        "tur", "toor", "arhar", "tuvar", "red gram", "pigeon pea",
        "तूर", "तुरीचे", "तुरीला", "तुरीचा", "अरहर", "तुवर"
    ],
    "Cotton": [
        "cotton", "kapas", "kapaas", "kappas",
        "कापूस", "कापसाचे", "कापसाला", "कापसाचा", "कपास"
    ],
    "Potato": [
        "potato", "potatoes", "aloo", "alu", "batata", "batate",
        "बटाटा", "बटाटे", "बटाट्याचे", "बटाट्याला", "आलू"
    ],
    "Wheat": [
        "wheat", "gehu", "gehun", "gahu", "gahvache",
        "गहू", "गव्हाचे", "गव्हाला", "गव्हाचा", "गेहूं"
    ]
}

# Maharashtra districts & mandis
LOCATION_SYNONYMS: Dict[str, List[str]] = {
    "Pune": [
        "pune", "poona", "पुणे", "पुण्यात", "पुण्याला", "पुण्याची", "पुण्याचा",
        "narayangaon", "नारायणगाव", "manchar", "मंचर", "khed", "खेड",
        "chakan", "चाकण", "baramati", "बारामती"
    ],
    "Nashik": [
        "nashik", "nasik", "नाशिक", "नाशिकला", "नाशिकमध्ये",
        "pimpalgaon", "पिंपळगाव", "lasalgaon", "लासलगाव"
    ],
    "Ahilyanagar": [
        "ahilyanagar", "ahmednagar", "nagar", "अहिल्यानगर", "अहमदनगर", "नगर",
        "संगमनेर", "sangamner"
    ],
    "Solapur": [
        "solapur", "sholapur", "सोलापूर", "सोलापुरात", "सोलापूरला"
    ],
    "Latur": [
        "latur", "लातूर", "लातुरात", "लातूरला"
    ],
    "Jalgaon": [
        "jalgaon", "जळगाव", "जळगावात"
    ],
    "Akola": [
        "akola", "अकोला", "अकोल्यात"
    ],
    "Amravati": [
        "amravati", "अमरावती", "अमरावतीत"
    ],
    "Kolhapur": [
        "kolhapur", "कोल्हापूर", "कोल्हापुरात"
    ],
    "Nagpur": [
        "nagpur", "नागपूर", "नागपुरात"
    ],
    "Mumbai": [
        "mumbai", "bombay", "vashi", "मुंबई", "मुंबईत", "वाशी"
    ],
    "Satara": [
        "satara", "सातारा", "साताऱ्यात"
    ],
    "Sangli": [
        "sangli", "सांगली", "सांगलीत"
    ]
}

# Word to number mappings for Hindi / Marathi / English
WORD_NUMBERS: Dict[str, float] = {
    "ten": 10.0, "twenty": 20.0, "thirty": 30.0, "forty": 40.0, "fifty": 50.0, "hundred": 100.0,
    "दहा": 10.0, "दस": 10.0, "पंधरा": 15.0, "पंद्रह": 15.0,
    "वीस": 20.0, "बीस": 20.0, "पंचवीस": 25.0, "पच्चीस": 25.0,
    "तीस": 30.0, "चाळीस": 40.0, "चालीस": 40.0,
    "पन्नास": 50.0, "पचास": 50.0, "शंभर": 100.0, "सौ": 100.0
}


def detect_language(text: str) -> str:
    """Detects if text is primarily English, Hindi, or Marathi."""
    text_lower = text.lower()
    
    # Check Devanagari script
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in text)
    if has_devanagari:
        # Distinct Marathi markers
        marathi_markers = [
            "आहे", "का", "कुठे", "विकू", "साठवू", "ठेवू", "पाहिजे", "कधी", "होईल",
            "टोमॅटो", "कांदा", "तूर", "गहू", "बटाटा", "क्विंटल", "मधील", "मध्ये"
        ]
        if any(m in text for m in marathi_markers):
            return "mr"
        
        # Distinct Hindi markers
        hindi_markers = [
            "है", "कहाँ", "कहा", "बेचूं", "बेचें", "रखें", "चाहिए", "क्या", "आज",
            "टमाटर", "प्याज", "आलू", "गेहूं", "फसल"
        ]
        if any(m in text for m in hindi_markers):
            return "hi"
        
        return "mr"

    # Transliterated Marathi markers
    if any(m in text_lower for m in ["kuthe", "viku", "thevu", "kiti", "ahe", "kanda", "saathv"]):
        return "mr"

    # Transliterated Hindi markers
    if any(m in text_lower for m in ["kaha", "bechu", "beche", "pyaaz", "tamatar", "bhav", "hai"]):
        return "hi"

    return "en"


def parse_devanagari_number(num_str: str) -> str:
    """Converts Devanagari numerals (०-९) to standard digits (0-9)."""
    dev_map = str.maketrans("०१२३४५६७८९", "0123456789")
    return num_str.translate(dev_map)


def extract_entities_regex(query: str) -> Dict[str, Any]:
    """Fallback deterministic regex & keyword parser with full synonyms."""
    clean_query = parse_devanagari_number(query)
    clean_lower = clean_query.lower()
    lang = detect_language(query)

    # 1. Crop extraction
    extracted_crop: Optional[str] = None
    for crop_name, synonyms in CROP_SYNONYMS.items():
        for syn in synonyms:
            pattern = rf"\b{re.escape(syn.lower())}\b"
            if re.search(pattern, clean_lower) or syn in clean_query:
                extracted_crop = crop_name
                break
        if extracted_crop:
            break

    # 2. Location extraction
    extracted_location: Optional[str] = None
    for loc_name, synonyms in LOCATION_SYNONYMS.items():
        for syn in synonyms:
            pattern = rf"\b{re.escape(syn.lower())}\b"
            if re.search(pattern, clean_lower) or syn in clean_query:
                extracted_location = loc_name
                break
        if extracted_location:
            break

    # 3. Quantity extraction
    extracted_quantity: Optional[float] = None
    
    # Case A: Pattern like "20 quintal", "50 kwintal", "30 क्विंटल"
    qty_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:quintals?|kwintals?|qtl|qtls|q|क्विंटल|क्विन्टल|क्वि)\b",
        r"(?:quintals?|kwintals?|क्विंटल|क्विन्टल)\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:tons?|tonnes?|टन)\b",
        r"(\d+(?:\.\d+)?)\s*(?:bags?|कट्टे|कट्टा|बोरी|बोरे|पोते|पोती|बॅग)\b"
    ]
    for pat in qty_patterns:
        match = re.search(pat, clean_lower)
        if match:
            val = float(match.group(1))
            if "ton" in pat or "टन" in pat:
                val *= 10.0
            elif "bag" in pat or "कट्ट" in pat or "बोर" in pat or "पोत" in pat:
                val *= 0.5  # Standard APMC 50kg bag
            extracted_quantity = round(val, 2)
            break

    # Case B: Word numbers (e.g. "twenty quintal", "वीस क्विंटल")
    if extracted_quantity is None:
        for word, val in WORD_NUMBERS.items():
            if re.search(rf"\b{re.escape(word)}\b", clean_lower):
                extracted_quantity = val
                break

    # Case C: Standalone number near crop or location
    if extracted_quantity is None:
        num_matches = re.findall(r"\b(\d+(?:\.\d+)?)\b", clean_lower)
        for num_str in num_matches:
            val = float(num_str)
            if 1.0 <= val <= 1000.0 and val not in [2024, 2025, 2026]:
                extracted_quantity = val
                break

    # 4. Intent extraction
    extracted_intent = None

    # Check Help / Greetings
    help_words = [
        "help", "hello", "hi", "hey", "namaste", "madat", "how does this work",
        "मदत", "मदद", "नमस्ते", "सहायता", "नमस्कार", "कसे वापरावे", "काय करू शकता"
    ]
    if any(re.search(rf"\b{re.escape(w)}\b", clean_lower) for w in help_words) and not extracted_crop:
        extracted_intent = "help"

    # Check Store or Sell (Devanagari, Transliterated, and English)
    store_patterns = [
        r"store|storage|sell now or wait|wait or sell|hold|keep|sell or store",
        r"viku ki thevu|thevu ki viku|thambayche|saathv|saathvuk|thevu ka|thambu ka|kadhi viku",
        r"साठव|साठवणूक|ठेवू की विकू|विकू की ठेवू|थांबायचे|थांबू का|कधी विकू|साठवून|साठवावे",
        r"bechu ya rakhu|rakhu ya bechu|roke ya beche|kab bechu|intazar|bechna ya rakhna",
        r"रोकें|रोका जाए|भंडारण|रखें या बेचें|बेचें या रखें|कब बेचें|इंतजार करें|रोकना|रखना"
    ]
    if not extracted_intent and any(re.search(pat, clean_lower) for pat in store_patterns):
        extracted_intent = "store_or_sell"

    # Check Price Check (Devanagari, Transliterated, and English)
    price_patterns = [
        r"today(?:'s)? price|current price|market price|what is the price|modal price",
        r"aaj(?:cha| ka)? bhav|bhav kya|bhav kitna|rate kya|rate kitna|bhav sanga|bhav kay",
        r"आजचा भाव|बाजारभाव|दर काय|भाव काय|दर किती|भाव सांगा|भाव किती",
        r"आज का भाव|रेट क्या|भाव क्या|भाव कितना|दाम क्या|दाम कितना|भाव बताओ"
    ]
    if not extracted_intent and any(re.search(pat, clean_lower) for pat in price_patterns):
        # Only set price_check if not asking for "best market" / "where to sell"
        if not any(w in clean_lower for w in ["best", "where", "kuthe", "kaha", "कुठे", "कहाँ", "सर्वोत्तम"]):
            extracted_intent = "price_check"

    # Check Best Market (Devanagari, Transliterated, and English)
    best_market_patterns = [
        r"best market|where to sell|where should i sell|which market|best place|recommend|suggest|sell",
        r"kaha bechu|kaha beche|kaun si mandi|kaha fayda|sabse achhi mandi|kaha bechna",
        r"कहाँ बेचूं|कहा बेचू|कौन सी मंडी|कहाँ फायदा|सबसे अच्छी मंडी|कहाँ बेचें|कहाँ बेचना",
        r"kuthe viku|koni mandi|konti mandi|konta bajar|kuthe fayda|sarvottam bajar|jast nafa|kuthe vikave|kuthe vikaayche",
        r"कुठे विकू|कोणती मंडी|कोणता बाजार|कुठे फायदा|सर्वोत्तम बाजार|जास्त नफा|कुठे विकावे|कुठे विकायचे"
    ]
    if not extracted_intent and any(re.search(pat, clean_lower) for pat in best_market_patterns):
        extracted_intent = "best_market"

    if not extracted_intent:
        if any(w in clean_lower for w in ["bhav", "rate", "price", "भाव", "दर", "दाम"]):
            extracted_intent = "price_check"
        else:
            extracted_intent = "best_market"

    return {
        "crop": extracted_crop,
        "quantity": extracted_quantity,
        "location": extracted_location,
        "intent": extracted_intent,
        "language": lang
    }


def extract_entities_gemini(query: str) -> Optional[Dict[str, Any]]:
    """Calls Gemini REST API with strict JSON schema instructions when API key is set."""
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
You are an NLP parser for Mandi Saathi, an agricultural price advisor for Maharashtra farmers.
Analyze the user message in English, Hindi, or Marathi:
User message: "{query}"

Extract strictly into JSON:
- "crop": One of ["Tomato", "Onion", "Soybean", "Tur", "Cotton", "Potato", "Wheat"] or null.
- "quantity": Number in quintals (float) or null. (1 ton = 10 quintals, 1 bag = 0.5 quintals).
- "location": District or Mandi name in Maharashtra (e.g. Pune, Nashik, Latur, Solapur, Ahilyanagar, Jalgaon, Akola, Kolhapur, Nagpur, Mumbai, Pimpalgaon, Lasalgaon, etc.) or null.
- "intent": One of ["best_market", "store_or_sell", "price_check", "help"].
- "language": One of ["en", "hi", "mr"].

Return ONLY raw valid JSON without markdown fences.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text_part = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_part)
                # Normalize crop
                crop = parsed.get("crop")
                if crop and crop not in CANONICAL_CROPS:
                    for c in CANONICAL_CROPS:
                        if c.lower() in crop.lower():
                            parsed["crop"] = c
                            break
                return parsed
    except Exception as exc:
        logger.warning(f"Gemini API NLP extraction failed, falling back to regex: {exc}")
        return None

    return None


def extract_entities(query: str) -> Dict[str, Any]:
    """Unified extractor: prefers Gemini when API key is available, falls back to regex."""
    if GEMINI_API_KEY:
        gemini_result = extract_entities_gemini(query)
        if gemini_result and gemini_result.get("intent"):
            return gemini_result

    return extract_entities_regex(query)


def generate_follow_up(missing_field: str, crop: Optional[str], lang: str) -> str:
    """Generates a polite, single targeted follow-up question in the requested language."""
    crop_info = CROP_NAMES_TRANSLATION.get(crop or "", {"en": crop or "crop", "hi": crop or "फसल", "mr": crop or "पीक"})

    if missing_field == "crop":
        if lang == "mr":
            return "तुम्हाला कोणत्या पिकासाठी सल्ला हवा आहे? (उदा. टोमॅटो, कांदा, सोयाबीन, तूर, बटाटा, गहू किंवा कापूस)"
        elif lang == "hi":
            return "आप किस फसल के लिए सलाह चाहते हैं? (जैसे: टमाटर, प्याज, सोयाबीन, तूर, आलू, गेहूं या कपास)"
        else:
            return "Which crop would you like advice for? (e.g. Tomato, Onion, Soybean, Tur, Potato, Wheat, Cotton)"

    elif missing_field == "location":
        if lang == "mr":
            return f"तुम्ही तुमचा {crop_info['mr']} कोणत्या जिल्ह्यातून किंवा भागातून विक्रीसाठी आणणार आहात? (उदा. पुणे, नाशिक, लातूर, सोलापूर)"
        elif lang == "hi":
            return f"आप अपने {crop_info['hi']} किस ज़िले या स्थान से मंडी ले जाना चाहते हैं? (जैसे: पुणे, नाशिक, लातूर, सोलापूर)"
        else:
            return f"Which district or town in Maharashtra are you bringing your {crop_info['en']} from? (e.g. Pune, Nashik, Latur, Solapur)"

    elif missing_field == "quantity":
        if lang == "mr":
            return f"तुमच्याकडे विक्रीसाठी {crop_info['mr']} चे किती क्विंटल प्रमाण आहे?"
        elif lang == "hi":
            return f"आपके पास बिक्री के लिए {crop_info['hi']} की कितनी मात्रा (क्विंटल) है?"
        else:
            return f"What is the quantity of {crop_info['en']} you plan to sell (in quintals)?"

    return "Could you please specify more details about your crop and location?"


def process_chat_message(
    message: str,
    explicit_language: Optional[str] = None
) -> Dict[str, Any]:
    """Processes chat query, verifies completeness, queries backend engines, and returns response."""
    entities = extract_entities(message)
    lang = explicit_language or entities.get("language") or "en"
    crop = entities.get("crop")
    quantity = entities.get("quantity")
    location = entities.get("location")
    intent = entities.get("intent", "best_market")

    # 1. Intent: HELP
    if intent == "help":
        if lang == "mr":
            reply = (
                "नमस्कार! मी **मंडी साथी**, महाराष्ट्रातील शेतकऱ्यांसाठी AI बाजारभाव आणि विक्री सल्लागार आहे.\n\n"
                "तुम्ही मला असे विचारू शकता:\n"
                "• **विक्री सल्ला:** 'पुण्यात २० क्विंटल टोमॅटो कुठे विकू?'\n"
                "• **साठवणूक सल्ला:** 'लासलगावमध्ये कांदा विकू की ठेवू?'\n"
                "• **ताज़ा बाजारभाव:** 'पुण्यात टोमॅटोचा आजचा भाव काय आहे?'"
            )
        elif lang == "hi":
            reply = (
                "नमस्ते! मैं **मंडी साथी** हूँ, महाराष्ट्र के किसानों के लिए AI मंडी भाव और बिक्री सलाहकार।\n\n"
                "आप मुझसे इस प्रकार पूछ सकते हैं:\n"
                "• **सर्वोत्तम मंडी:** 'पुणे में 20 क्विंटल टमाटर कहाँ बेचूं?'\n"
                "• **भंडारण सलाह:** 'लासलगांव में प्याज रखें या बेचें?'\n"
                "• **ताज़ा भाव:** 'पुणे में टमाटर का आज का भाव क्या है?'"
            )
        else:
            reply = (
                "Hello! I am **Mandi Saathi**, your AI crop price and sell-timing advisor for Maharashtra APMC mandis.\n\n"
                "You can ask me questions like:\n"
                "• **Best Market:** 'I have 20 quintals of tomato in Pune, where should I sell?'\n"
                "• **Storage Decision:** 'Should I sell or store onion in Lasalgaon?'\n"
                "• **Price Check:** 'What is the price of tomato in Pune today?'"
            )

        return {
            "reply": reply,
            "intent": intent,
            "entities": entities,
            "missing_field": None,
            "follow_up_needed": False,
            "data": None,
            "language": lang
        }

    # 2. Check for missing essential fields -> Ask ONE follow-up
    if not crop:
        follow_up_msg = generate_follow_up("crop", None, lang)
        return {
            "reply": follow_up_msg,
            "intent": intent,
            "entities": entities,
            "missing_field": "crop",
            "follow_up_needed": True,
            "data": None,
            "language": lang
        }

    # For best_market intent, location is required to calculate haversine distance and transport
    if intent == "best_market" and not location:
        follow_up_msg = generate_follow_up("location", crop, lang)
        return {
            "reply": follow_up_msg,
            "intent": intent,
            "entities": entities,
            "missing_field": "location",
            "follow_up_needed": True,
            "data": None,
            "language": lang
        }

    # Default quantity if omitted in best_market
    effective_qty = quantity if (quantity and quantity > 0) else 20.0
    crop_names = CROP_NAMES_TRANSLATION.get(crop, {"en": crop, "hi": crop, "mr": crop})

    # 3. Handle Intent: BEST_MARKET
    if intent == "best_market":
        adv_res = calculate_advisory(
            crop=crop,
            district=location or "Pune",
            quantity_quintals=effective_qty,
            vehicle_type="tempo"
        )
        best = adv_res.get("best_recommendation")
        if not best:
            reply = f"Sorry, no active trading records were found for {crop} in {location}."
            if lang == "mr":
                reply = f"क्षमस्व, {location} जवळ {crop_names['mr']} पिकासाठी सध्या सक्रिय बाजारभाव उपलब्ध नाहीत."
            elif lang == "hi":
                reply = f"क्षमा करें, {location} के पास {crop_names['hi']} के लिए सक्रिय मंडी भाव उपलब्ध नहीं हैं।"
            return {
                "reply": reply,
                "intent": intent,
                "entities": entities,
                "missing_field": None,
                "follow_up_needed": False,
                "data": adv_res,
                "language": lang
            }

        net_ret = best["net_return_per_quintal"]
        total_earn = best["total_net_earnings"]
        gross = best["gross_modal_price"]
        trans = best["costs"]["transport_per_q"]
        mkt = best["market"]
        dist = best["district"]
        dist_km = best["distance_km"]
        reason = best["verdict_reason"]
        be_price = best.get("break_even_price")

        if lang == "mr":
            be_note = f"\n⚖️ **किमान फायदेशीर भाव:** ₹{be_price}/क्विंटल (यापेक्षा कमी भावात स्थानिक बाजारात विकणे परवडेल)" if be_price and not best["is_nearest"] else ""
            reply = (
                f"**{location}** मधील तुमच्या **{effective_qty:g} क्विंटल {crop_names['mr']}** साठी सर्वात फायदेशीर बाजार **{mkt}** ({dist} जिल्हा) आहे!\n\n"
                f"💰 **खिशात निव्वळ नफा:** **₹{net_ret:,.2f}/क्विंटल** (एकूण निव्वळ कमाई: **₹{total_earn:,.0f}**)\n"
                f"📊 **मंडी भाव:** ₹{gross:,.2f}/क्विंटल\n"
                f"🚚 **वाहतूक खर्च:** -₹{trans:,.2f}/क्विंटल ({dist_km} किमी, पिकअप टेम्पो)\n"
                f"{be_note}\n"
                f"💡 **सल्ला:** {reason}"
            )
        elif lang == "hi":
            be_note = f"\n⚖️ **ब्रेक-ईवन भाव:** ₹{be_price}/क्विंटल (इससे कम भाव मिलने पर नजदीकी मंडी बेहतर रहेगी)" if be_price and not best["is_nearest"] else ""
            reply = (
                f"**{location}** से आपके **{effective_qty:g} क्विंटल {crop_names['hi']}** के लिए सबसे अच्छी मंडी **{mkt}** ({dist} ज़िला) है!\n\n"
                f"💰 **आपकी जेब में शुद्ध लाभ:** **₹{net_ret:,.2f}/क्विंटल** (कुल शुद्ध लाभ: **₹{total_earn:,.0f}**)\n"
                f"📊 **मंडी मॉडल भाव:** ₹{gross:,.2f}/क्विंटल\n"
                f"🚚 **भाड़ा कटौती:** -₹{trans:,.2f}/क्विंटल ({dist_km} किमी, टेम्पो)\n"
                f"{be_note}\n"
                f"💡 **सलाह:** {reason}"
            )
        else:
            be_note = f"\n⚖️ **Break-Even Threshold:** ₹{be_price}/quintal (price required at far mandi to beat local market)" if be_price and not best["is_nearest"] else ""
            reply = (
                f"For your **{effective_qty:g} quintals** of **{crop}** from **{location}**, the most profitable market is **{mkt}** ({dist} district)!\n\n"
                f"💰 **Net in your pocket:** **₹{net_ret:,.2f}/quintal** (Total Net Earnings: **₹{total_earn:,.0f}**)\n"
                f"📊 **Gross Mandi Price:** ₹{gross:,.2f}/quintal\n"
                f"🚚 **Freight Deduction:** -₹{trans:,.2f}/quintal ({dist_km} km via Tempo)\n"
                f"{be_note}\n"
                f"💡 **Verdict:** {reason}"
            )

        return {
            "reply": reply,
            "intent": intent,
            "entities": {**entities, "quantity": effective_qty},
            "missing_field": None,
            "follow_up_needed": False,
            "data": adv_res,
            "language": lang
        }

    # 4. Handle Intent: STORE_OR_SELL
    elif intent == "store_or_sell":
        storage_res = get_storage_advice(crop=crop, market=location)
        rec = storage_res.get("recommendation", "Sell now")
        current_price = storage_res.get("current_price", 0.0)
        net_gain = storage_res.get("net_benefit_per_quintal", 0.0)
        rationale = storage_res.get("rationale", "")
        market_label = location or storage_res.get("market", "Maharashtra")

        if lang == "mr":
            rec_mr = "आता विका (Sell now)" if "sell" in rec.lower() else ("काही दिवस थांबा (Wait)" if "wait" in rec.lower() else "अपुरा डेटा")
            reply = (
                f"**{market_label}** मध्ये **{crop_names['mr']}** साठवणूक आणि विक्री निर्णय:\n\n"
                f"🎯 **शिफारस:** **{rec_mr}**\n"
                f"📈 **चालू भाव:** ₹{current_price:,.2f}/क्विंटल\n"
                f"⚖️ **संभाव्य निव्वळ फायदा:** ₹{net_gain:,.2f}/क्विंटल (साठवणूक खर्च व घट वजा जाता)\n"
                f"💡 **विश्लेषण:** {rationale}"
            )
        elif lang == "hi":
            rec_hi = "अभी बेचें (Sell now)" if "sell" in rec.lower() else ("कुछ दिन रुकें (Wait)" if "wait" in rec.lower() else "अपर्याप्त डेटा")
            reply = (
                f"**{market_label}** में **{crop_names['hi']}** भंडारण और बिक्री सलाह:\n\n"
                f"🎯 **सिफारिश:** **{rec_hi}**\n"
                f"📈 **मौजूदा भाव:** ₹{current_price:,.2f}/क्विंटल\n"
                f"⚖️ **अनुमानित शुद्ध लाभ:** ₹{net_gain:,.2f}/क्विंटल (गोदाम खर्च और वजन घटौती के बाद)\n"
                f"💡 **विश्लेषण:** {rationale}"
            )
        else:
            reply = (
                f"Storage vs Immediate Sale advice for **{crop}** in **{market_label}**:\n\n"
                f"🎯 **Recommendation:** **{rec}**\n"
                f"📈 **Current Modal Price:** ₹{current_price:,.2f}/quintal\n"
                f"⚖️ **Net Storage Benefit:** ₹{net_gain:,.2f}/quintal (after storage charges and moisture shrinkage)\n"
                f"💡 **Rationale:** {rationale}"
            )

        return {
            "reply": reply,
            "intent": intent,
            "entities": entities,
            "missing_field": None,
            "follow_up_needed": False,
            "data": storage_res,
            "language": lang
        }

    # 5. Handle Intent: PRICE_CHECK
    elif intent == "price_check":
        price_rows = get_latest_prices_for_crop(crop)
        if not price_rows:
            reply = f"No recent market price records found for {crop}."
            if lang == "mr":
                reply = f"{crop_names['mr']} पिकासाठी सध्या कोणतीही बाजारभाव नोंद उपलब्ध नाही."
            elif lang == "hi":
                reply = f"{crop_names['hi']} फसल के लिए हाल ही में कोई मंडी भाव उपलब्ध नहीं है।"
            return {
                "reply": reply,
                "intent": intent,
                "entities": entities,
                "missing_field": None,
                "follow_up_needed": False,
                "data": None,
                "language": lang
            }

        # Look for matching location or pick the top reporting market
        target_mandi = None
        if location:
            for row in price_rows:
                if (location.lower() in row["market"].lower() or
                    location.lower() in row["district"].lower()):
                    target_mandi = row
                    break
        if not target_mandi:
            target_mandi = price_rows[0]

        modal = target_mandi["modal_price"]
        min_p = target_mandi["min_price"]
        max_p = target_mandi["max_price"]
        arr_date = target_mandi["arrival_date"]
        mkt = target_mandi["market"]
        dist = target_mandi["district"]

        if lang == "mr":
            reply = (
                f"**{mkt}** ({dist} जिल्हा) APMC मध्ये **{crop_names['mr']}** चा ताज़ा बाजारभाव:\n\n"
                f"📊 **सरासरी (मॉडेल) भाव:** **₹{modal:,.2f}/क्विंटल**\n"
                f"📉 **किमान भाव:** ₹{min_p:,.2f}/क्विंटल\n"
                f"📈 **कमाल भाव:** ₹{max_p:,.2f}/क्विंटल\n"
                f"📅 **नोंदणी दिनांक:** {arr_date}"
            )
        elif lang == "hi":
            reply = (
                f"**{mkt}** ({dist} ज़िला) मंडी में **{crop_names['hi']}** का ताज़ा भाव:\n\n"
                f"📊 **मॉडल भाव:** **₹{modal:,.2f}/क्विंटल**\n"
                f"📉 **न्यूनतम भाव:** ₹{min_p:,.2f}/क्विंटल\n"
                f"📈 **अधिकतम भाव:** ₹{max_p:,.2f}/क्विंटल\n"
                f"📅 **दिनांक:** {arr_date}"
            )
        else:
            reply = (
                f"Latest APMC price for **{crop}** at **{mkt}** ({dist} district):\n\n"
                f"📊 **Modal Price:** **₹{modal:,.2f}/quintal**\n"
                f"📉 **Min Price:** ₹{min_p:,.2f}/quintal\n"
                f"📈 **Max Price:** ₹{max_p:,.2f}/quintal\n"
                f"📅 **Reported Date:** {arr_date}"
            )

        return {
            "reply": reply,
            "intent": intent,
            "entities": entities,
            "missing_field": None,
            "follow_up_needed": False,
            "data": target_mandi,
            "language": lang
        }

    # Fallback response
    return {
        "reply": "How can I help you with Maharashtra APMC mandi prices and sell timing?",
        "intent": intent,
        "entities": entities,
        "missing_field": None,
        "follow_up_needed": False,
        "data": None,
        "language": lang
    }
