"""Multilingual NLP Service for Mandi Saathi.

Provides comprehensive support for everyday spoken Marathi, Hindi, and English.
Extracts crop, quantity, location, and intent (best_market, store_or_sell, price_check, help, greeting, thanks, identity)
using Gemini REST API (when GEMINI_API_KEY is available) or a deterministic, high-accuracy Marathi/Hindi/English
regex & synonym parser. Maintains contextual session memory for natural multi-turn conversations and follow-up questions.
Guarantees 100% pure Marathi responses in Devanagari script for Marathi voice and text interactions.
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

# Crop names in English, Hindi, and Marathi for natural language replies
CROP_NAMES_TRANSLATION = {
    "Tomato": {"en": "Tomato", "hi": "टमाटर", "mr": "टोमॅटो"},
    "Onion": {"en": "Onion", "hi": "प्याज", "mr": "कांदा"},
    "Soybean": {"en": "Soybean", "hi": "सोयाबीन", "mr": "सोयाबीन"},
    "Tur": {"en": "Tur / Arhar", "hi": "तूर (अरहर)", "mr": "तूर"},
    "Cotton": {"en": "Cotton", "hi": "कपास", "mr": "कापूस"},
    "Potato": {"en": "Potato", "hi": "आलू", "mr": "बटाटा"},
    "Wheat": {"en": "Wheat", "hi": "गेहूं", "mr": "गहू"},
}

# Extensive multilingual crop synonyms (including spoken/colloquial Marathi forms)
CROP_SYNONYMS: Dict[str, List[str]] = {
    "Tomato": [
        "tomato", "tomatoes", "tamatar", "tamater", "tameta", "tamate",
        "टोमॅटो", "टोमॅटोचे", "टोमॅटोचा", "टोमॅटोची", "टोमॅटोला", "टोमॅटोत", "टोमॅटोसाठी", "टोमॅटोस",
        "टमाटे", "टमाट्याचे", "टमाट्याला", "टमाट्याचं", "टमाटर", "टमाटा", "टमाट्या", "टमाटरों"
    ],
    "Onion": [
        "onion", "onions", "kanda", "kande", "kandya", "kandyache", "kandyala", "kandacha", "kandyach",
        "pyaaz", "pyaj", "pyaz", "कांदा", "कांदे", "कांद्याचे", "कांद्याचं", "कांद्याची", "कांद्याला",
        "कांद्याचा", "कांद्यात", "कांद्यासाठी", "कांद्यास", "कांद्या", "प्याज", "प्याज़"
    ],
    "Soybean": [
        "soybean", "soyabean", "soya", "soyabin", "soyebean",
        "सोयाबीन", "सोयाबीनचे", "सोयाबीनचं", "सोयाबीनला", "सोयाबीनचा", "सोयाबीनची", "सोया", "सोयाबिन", "सोयबीन",
        "सोयाबीनसाठी", "सोयाबीनमध्ये", "सोयाबीनचे भाव"
    ],
    "Tur": [
        "tur", "toor", "arhar", "tuvar", "red gram", "pigeon pea",
        "तूर", "तुरीचे", "तुरीचं", "तुरीला", "तुरीचा", "तुरीची", "तुरीस", "तुरीसाठी", "तुरीमध्ये", "तूरडाळ",
        "अरहर", "तुवर"
    ],
    "Cotton": [
        "cotton", "kapas", "kapaas", "kappas",
        "कापूस", "कापसाचे", "कापसाचं", "कापसाला", "कापसाचा", "कापसाची", "कापसास", "कापसासाठी",
        "कपाशी", "कपाशीचे", "कपाशीला", "कपास", "रुई"
    ],
    "Potato": [
        "potato", "potatoes", "aloo", "alu", "batata", "batate",
        "बटाटा", "बटाटे", "बटाट्याचे", "बटाट्याचं", "बटाट्याला", "बटाट्याचा", "बटाट्याची", "बटाट्यात", "बटाट्यासाठी", "आलू"
    ],
    "Wheat": [
        "wheat", "gehu", "gehun", "gahu", "gahvache", "gahva",
        "गहू", "गव्हाचे", "गव्हाचं", "गव्हाला", "गव्हाचा", "गव्हाची", "गव्हात", "गव्हासाठी", "गेहूं"
    ]
}

# Maharashtra districts & mandis synonyms (English, Hindi, Marathi colloquial)
LOCATION_SYNONYMS: Dict[str, List[str]] = {
    "Pune": [
        "pune", "poona", "पुणे", "पुण्यात", "पुण्याला", "पुण्याची", "पुण्याचा", "पुण्यासाठी", "पुण्याच्या", "पुण्यामध्ये", "पुणेमध्ये",
        "narayangaon", "नारायणगाव", "नारायणगावात", "manchar", "मंचर", "मंचरला", "khed", "खेड", "खेडला",
        "chakan", "चाकण", "चाकणला", "baramati", "बारामती", "बारामतीला", "shirur", "शिरूर", "शिरूरला", "shirurhun",
        "junnar", "जुन्नर", "जुन्नरला", "indapur", "इंदापूर"
    ],
    "Nashik": [
        "nashik", "nasik", "नाशिक", "नाशिकला", "नाशिकमध्ये", "नाशिकचा", "नाशिकात", "नाशिकच्या", "नासिक", "नासिक में", "नासिक से", "नासिक का",
        "pimpalgaon", "पिंपळगाव", "पिंपळगावला", "पिंपळगाव बसवंत", "lasalgaon", "लासलगाव", "लासलगावला", "लासलगावात",
        "yeola", "येवला", "sinnar", "सिन्नर", "malegaon", "मालेगाव", "satana", "सटाणा", "chandwad", "चांदवड", "dindori", "दिंडोरी"
    ],
    "Ahilyanagar": [
        "ahilyanagar", "ahmednagar", "nagar", "अहिल्यानगर", "अहमदनगर", "नगर", "अहिल्यानगरात", "अहमदनगरात",
        "संगमनेर", "संगमनेरला", "sangamner", "kopargaon", "कोपरगाव", "shrirampur", "श्रीरामपूर", "rahuri", "राहुरी", "newasa", "नेवासा"
    ],
    "Solapur": [
        "solapur", "sholapur", "सोलापूर", "सोलापुरात", "सोलापूरला", "सोलापूरमध्ये",
        "barshi", "बार्शी", "pandharpur", "पंढरपूर", "पंढरपुरात", "akluj", "अकलूज", "karmala", "करमाळा", "sangola", "सांगोला"
    ],
    "Latur": [
        "latur", "लातूर", "लातुरात", "लातूरला", "लातूरमध्ये", "udgir", "उदगीर", "उदगीरला", "ausa", "औसा", "nilanga", "निलंगा", "ahmedpur", "अहमदपूर"
    ],
    "Jalgaon": [
        "jalgaon", "जळगाव", "जळगावात", "जळगावला", "जळगावमध्ये", "bhusawal", "भुसावळ", "chalisgaon", "चाळीसगाव", "amalner", "अमळनेर", "chopda", "चोपडा"
    ],
    "Akola": [
        "akola", "अकोला", "अकोल्यात", "अकोल्याला", "अकोलामध्ये", "balapur", "बाळापूर", "murtizapur", "मूर्तिजापूर", "akot", "आकोट"
    ],
    "Amravati": [
        "amravati", "अमरावती", "अमरावतीत", "अमरावतीला", "अमरावतीमध्ये", "achlapur", "अचलपूर", "morshi", "मोर्शी", "warud", "वरुड"
    ],
    "Kolhapur": [
        "kolhapur", "कोल्हापूर", "कोल्हापुरात", "कोल्हापूरला", "कोल्हापूरमध्ये", "jaysingpur", "जयसिंगपूर", "gadhinglaj", "गडहिंग्लज", "shirol", "शिरोळ"
    ],
    "Nagpur": [
        "nagpur", "नागपूर", "नागपुरात", "नागपूरला", "नागपूरमध्ये", "kalmeshwar", "कळमेश्वर", "katol", "काटोल", "umred", "उमरेड", "saoner", "सावनेर"
    ],
    "Mumbai": [
        "mumbai", "bombay", "vashi", "मुंबई", "मुंबईत", "मुंबईला", "वाशी", "वाशीला", "वाशीमध्ये", "नवी मुंबई"
    ],
    "Satara": [
        "satara", "सातारा", "साताऱ्यात", "साताऱ्याला", "सातारामध्ये", "karad", "कराड", "कराडला", "phaltan", "फलटण", "wai", "वाई"
    ],
    "Sangli": [
        "sangli", "सांगली", "सांगलीत", "सांगलीला", "सांगलीमध्ये", "tasgaon", "तासगाव", "miraj", "मिरज", "islampur", "इस्लामपूर", "vita", "विटा"
    ],
    "Chhatrapati Sambhajinagar": [
        "aurangabad", "chhatrapati sambhajinagar", "sambhajinagar", "औरंगाबाद", "छत्रपती संभाजीनगर", "संभाजीनगर",
        "संभाजीनगरला", "संभाजीनगरात", "vaijapur", "वैजापूर", "gangapur", "गंगापूर", "paithan", "पैठण"
    ],
    "Jalna": [
        "jalna", "जालना", "जालन्यात", "जालन्याला", "जालनामध्ये", "partur", "परतूर", "ambad", "अंबड"
    ],
    "Beed": [
        "beed", "बीड", "बीडमध्ये", "बीडला", "बीडात", "georai", "गेवराई", "majalgaon", "माजलगाव", "parli", "परळी", "ambajogai", "अंबाजोगाई"
    ],
    "Dharashiv": [
        "dharashiv", "osmanabad", "धाराशिव", "उस्मानाबाद", "तुळजापूर", "tuljapur", "umarga", "उमरगा"
    ],
    "Nanded": [
        "nanded", "नांदेड", "नांदेडमध्ये", "नांदेडला", "नांदेडात", "loha", "लोहा", "kinwat", "किनवट"
    ],
    "Parbhani": [
        "parbhani", "परभणी", "परभणीत", "परभणीला", "परभणीमध्ये", "gangakhed", "गंगाखेड", "selu", "सेलू"
    ],
    "Hingoli": [
        "hingoli", "हिंगोली", "हिंगोलीत", "हिंगोलीला", "हिंगोलीमध्ये", "basmath", "वसमत"
    ],
    "Buldhana": [
        "buldhana", "बुलढाणा", "बुलढाण्यात", "बुलढाण्याला", "khamgaon", "खामगाव", "shegaon", "शेगाव", "malkapur", "मलकापूर"
    ],
    "Washim": [
        "washim", "वाशिम", "वाशिममध्ये", "वाशिमला", "वाशिमात", "risod", "रिसोड", "karanja", "कारंजा"
    ],
    "Yavatmal": [
        "yavatmal", "यवतमाळ", "यवतमाळात", "यवतमाळला", "यवतमाळमध्ये", "pusad", "पुसद", "wani", "वणी"
    ],
    "Wardha": [
        "wardha", "वर्धा", "वर्ध्यात", "वर्ध्याला", "वर्धामध्ये", "hinganghat", "हिंगणघाट", "arvi", "आर्वी"
    ],
    "Chandrapur": [
        "chandrapur", "चंद्रपूर", "चंद्रपुरात", "चंद्रपूरला", "warora", "वरोरा", "ballarpur", "बल्लारपूर"
    ],
    "Dhule": [
        "dhule", "धुळे", "धुळ्यात", "धुळ्याला", "धुळेमध्ये", "shirpur", "शिरपूर"
    ],
    "Nandurbar": [
        "nandurbar", "नंदुरबार", "नंदुरबारला", "नंदुरबारमध्ये", "shahada", "शहादा"
    ]
}

# Word to number mappings for Marathi, Hindi, and English
WORD_NUMBERS: Dict[str, float] = {
    # Marathi numbers
    "एक": 1.0, "दोन": 2.0, "तीन": 3.0, "चार": 4.0, "पाच": 5.0,
    "सहा": 6.0, "सात": 7.0, "आठ": 8.0, "नऊ": 9.0, "दहा": 10.0,
    "अकरा": 11.0, "बारा": 12.0, "तेरा": 13.0, "चौदा": 14.0, "पंधरा": 15.0,
    "सोळा": 16.0, "सतरा": 17.0, "अठरा": 18.0, "एकोणीस": 19.0, "वीस": 20.0,
    "पंचवीस": 25.0, "तीस": 30.0, "पस्तीस": 35.0, "चाळीस": 40.0, "पंचेचाळीस": 45.0,
    "पन्नास": 50.0, "साठ": 60.0, "सत्तर": 70.0, "ऐंशी": 80.0, "नव्वद": 90.0,
    "शंभर": 100.0, "दीडशे": 150.0, "दोनशे": 200.0, "पाचशे": 500.0, "हजार": 1000.0,
    # Hindi numbers
    "एक": 1.0, "दो": 2.0, "तीन": 3.0, "चार": 4.0, "पाँच": 5.0,
    "छह": 6.0, "सात": 7.0, "आठ": 8.0, "नौ": 9.0, "दस": 10.0,
    "ग्यारह": 11.0, "बारह": 12.0, "तेरह": 13.0, "चौदह": 14.0, "पंद्रह": 15.0,
    "सोलह": 16.0, "सत्रह": 17.0, "अठारह": 18.0, "उन्नीस": 19.0, "बीस": 20.0,
    "पच्चीस": 25.0, "तीस": 30.0, "पैंतीस": 35.0, "चालीस": 40.0, "पैंतालीस": 45.0,
    "पचास": 50.0, "सौ": 100.0, "दो सौ": 200.0, "पाँच सौ": 500.0, "हज़ार": 1000.0,
    # English numbers
    "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
    "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0,
    "fifteen": 15.0, "twenty": 20.0, "twenty five": 25.0, "thirty": 30.0,
    "forty": 40.0, "fifty": 50.0, "hundred": 100.0, "thousand": 1000.0
}

# Contextual conversation memory (session_id -> dict of entities & state)
SESSION_MEMORY: Dict[str, Dict[str, Any]] = {}


def detect_language(text: str) -> str:
    """Detects if text is primarily Marathi, Hindi, or English.
    
    Distinguishes natural spoken and written Devanagari between Marathi and Hindi
    based on distinct vocabulary and verb markers, avoiding false positives on shared words.
    """
    clean_lower = text.lower()

    # Explicit language switch phrases
    if re.search(r"\b(?:speak|talk|tell|switch|reply)\s+(?:in|to)?\s*hindi\b", clean_lower) or any(p in text for p in ["हिंदी में", "हिन्दी में", "हिंदी बताओ"]):
        return "hi"
    if re.search(r"\b(?:speak|talk|tell|switch|reply)\s+(?:in|to)?\s*marathi\b", clean_lower) or any(p in text for p in ["मराठीत", "मराठी मध्ये", "मराठी बोला"]):
        return "mr"
    if re.search(r"\b(?:speak|talk|tell|switch|reply)\s+(?:in|to)?\s*english\b", clean_lower) or any(p in text for p in ["इंग्रजीत", "इंग्लिश मध्ये", "अंग्रेजी में"]):
        return "en"

    # Check Devanagari script presence
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in text)
    if has_devanagari:
        # Distinctively Marathi markers
        marathi_markers = [
            "आहे", "आहेत", "कुठे", "कसं", "कसे", "कधी", "विकू", "विकायचे", "विकायचा",
            "विकायची", "विकायचं", "विकावे", "साठवू", "साठवावे", "साठवणूक", "ठेवू", "थांबू",
            "पाहिजे", "होईल", "किती", "सांगा", "सांग", "मिळेल", "परवडेल", "चाललाय",
            "कांदा", "कांद्याचा", "कांद्याचे", "कांद्याची", "कांद्याला", "कांदे", "कांद्यात",
            "बटाटा", "बटाट्याचे", "गहू", "गव्हाचे", "कापूस", "कापसाचे", "तुरीचे",
            "माझा", "माझी", "माझे", "माझ्याकडे", "आम्हाला", "मला", "तुम्ही", "पोती", "गोणी",
            "मधील", "मध्ये", "कसा"
        ]
        # Distinctively Hindi markers
        hindi_markers = [
            "है", "हैं", "कहाँ", "कहा", "बेचूं", "बेचें", "बेचना", "रखें", "रखूं", "चाहिए", "क्या",
            "प्याज", "प्याज़", "टमाटर", "आलू", "गेहूं", "फसल", "बताओ", "बताइए", "कितना", "कितने", "कितनी",
            "मुझे", "हमे", "हमारा", "मेरा", "मेरी", "मेरे", "दाम", "कीमत", "बोरी", "कट्टे"
        ]

        mr_score = sum(1 for m in marathi_markers if m in text)
        hi_score = sum(1 for h in hindi_markers if h in text)

        if hi_score > mr_score:
            return "hi"
        if mr_score > hi_score:
            return "mr"

        # Break ties on key grammatical verbs
        if any(h in text for h in ["है", "हैं", "प्याज", "कहाँ", "बेचूं", "बताओ", "कितना", "क्या"]):
            return "hi"
        if any(m in text for m in ["आहे", "आहेत", "कांदा", "कुठे", "विकू", "सांगा", "किती", "ठेवू"]):
            return "mr"

        return "mr"  # Default in Maharashtra APMC context

    # Transliterated Hindi markers (SMS / voice typing)
    transliterated_hindi = [
        "kaha", "bechu", "beche", "pyaaz", "tamatar", "hai", "batao", "chahiye", "kitna", "bhav kya hai", "aaj ka bhav"
    ]
    if any(m in clean_lower for m in transliterated_hindi):
        return "hi"

    # Transliterated Marathi markers (SMS / voice typing)
    transliterated_marathi = [
        "kuthe", "viku", "vikaycha", "vikayche", "vikaychi", "vikayca", "thevu", "thambu",
        "kiti", "ahe", "aahe", "kanda", "saathv", "sanga", "parvadel", "chalalay", "neu",
        "mala", "aamhi", "jilha", "madhe", "turi", "gahva", "kapus", "batata", "bajar"
    ]
    if any(m in clean_lower for m in transliterated_marathi):
        return "mr"

    return "en"


def parse_devanagari_number(num_str: str) -> str:
    """Converts Devanagari numerals (०-९) to standard digits (0-9)."""
    dev_map = str.maketrans("०१२३४५६७८९", "0123456789")
    return num_str.translate(dev_map)


def extract_entities_regex(query: str) -> Dict[str, Any]:
    """Fallback deterministic regex & keyword parser supporting natural Marathi, Hindi, and English."""
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

    # Case A: Explicit pattern like "20 quintal", "२० क्विंटल", "२ टन", "५० पोती", "२० क्रेट", "1020 किलो क्विंटल", "500 किलो"
    qty_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:किलो\s*क्विंटल|किलो\s*क्विन्टल|kg\s*quintals?)\b",
        r"(\d+(?:\.\d+)?)\s*(?:quintals?|kwintals?|qtl|qtls|q|क्विंटल|क्विन्टल|क्वि)\b",
        r"(?:quintals?|kwintals?|क्विंटल|क्विन्टल)\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:tons?|tonnes?|टन)\b",
        r"(\d+(?:\.\d+)?)\s*(?:bags?|कट्टे|कट्टा|बोरी|बोरे|पोते|पोती|पोत्या|गोणी|बॅग|बॅगा)\b",
        r"(\d+(?:\.\d+)?)\s*(?:crates?|क्रेट|क्रेट्स)\b",
        r"(\d+(?:\.\d+)?)\s*(?:किलो|kilos?|kgs?)\b",
        r"(\d+(?:\.\d+)?)\s*(?:गाडी|गाड्या|pickup|tempo)\b"
    ]
    for pat in qty_patterns:
        match = re.search(pat, clean_lower)
        if match:
            val = float(match.group(1))
            if "ton" in pat or "टन" in pat:
                val *= 10.0
            elif "किलो\\s*क्विंटल" in pat or "kg\\s*quintal" in pat:
                pass  # Stated as quintals directly
            elif "किलो" in pat or "kilo" in pat or "kg" in pat:
                val /= 100.0  # 100 kg = 1 quintal
            elif any(u in pat for u in ["bag", "कट्ट", "बोर", "पोत", "गोणी", "बॅग"]):
                val *= 0.5  # Standard APMC 50kg bag
            elif "क्रेट" in pat or "crate" in pat:
                val *= 0.25  # Standard 25kg tomato crate
            elif "गाडी" in pat or "pickup" in pat or "tempo" in pat:
                val = 25.0  # Standard tempo load ~25 quintals
            extracted_quantity = round(val, 2)
            break

    # Case B: Marathi and Hindi number words (e.g. "वीस क्विंटल", "दहा टन", "पन्नास पोती")
    if extracted_quantity is None:
        for word, val in WORD_NUMBERS.items():
            if re.search(rf"\b{re.escape(word)}\b", clean_lower):
                # Check if followed by unit
                if any(u in clean_lower for u in ["टन", "ton"]):
                    val *= 10.0
                elif any(u in clean_lower for u in ["पोती", "पोते", "कट्टे", "गोणी", "बॅग", "bag"]):
                    val *= 0.5
                elif any(u in clean_lower for u in ["क्रेट", "crate"]):
                    val *= 0.25
                extracted_quantity = val
                break

    # Case C: Standalone numeral near crop or intent (e.g. "टोमॅटो २०", "कांदा ५०")
    if extracted_quantity is None:
        num_matches = re.findall(r"\b(\d+(?:\.\d+)?)\b", clean_lower)
        for num_str in num_matches:
            val = float(num_str)
            if 1.0 <= val <= 2000.0 and val not in [2024, 2025, 2026, 2027]:
                extracted_quantity = val
                break

    # 4. Intent extraction
    extracted_intent = None

    # Check Greetings
    greetings = [
        "नमस्कार", "राम राम", "नमस्ते", "हॅलो", "हाय", "namaskar", "ram ram", "hello", "hi", "hey"
    ]
    if any(re.search(rf"\b{re.escape(w)}\b", clean_lower) for w in greetings) and not extracted_crop and not extracted_location:
        extracted_intent = "greeting"

    # Check Thanks
    thanks_words = [
        "धन्यवाद", "आभार", "थँक्यू", "थँक्स", "thank you", "thanks", "dhanyavad", "shukriya"
    ]
    if any(re.search(rf"\b{re.escape(w)}\b", clean_lower) for w in thanks_words):
        extracted_intent = "thanks"

    # Check Identity / About
    identity_words = [
        "तू कोण आहेस", "तुझे नाव काय", "काय करू शकतोस", "कशी मदत करू शकतोस", "तू काय आहेस",
        "who are you", "what can you do", "aap kaun ho", "tum kaun ho"
    ]
    if any(w in clean_lower for w in identity_words):
        extracted_intent = "identity"

    # Check Help
    help_words = [
        "help", "madat", "how does this work",
        "मदत", "मदद", "सहायता", "कसे वापरावे", "काय करू शकता", "मदत करा", "कशी मदत"
    ]
    if not extracted_intent and any(re.search(rf"\b{re.escape(w)}\b", clean_lower) for w in help_words) and not extracted_crop:
        extracted_intent = "help"

    # Check Store or Sell (Devanagari Marathi, Transliterated, Hindi, and English)
    store_patterns = [
        r"store|storage|sell now or wait|wait or sell|hold|keep|sell or store",
        r"viku ki thevu|thevu ki viku|thambayche|saathv|saathvuk|thevu ka|thambu ka|kadhi viku",
        r"साठव|साठवणूक|ठेवू की विकू|विकू की ठेवू|थांबायचे|थांबू का|कधी विकू|साठवून|साठवावे|ठेवू का|विकू का|भाव वाढतील का|तेजी येईल का|गोदामात ठेवू",
        r"bechu ya rakhu|rakhu ya bechu|roke ya beche|kab bechu|intazar|bechna ya rakhna",
        r"रोकें|रोका जाए|भंडारण|रखें या बेचें|बेचें या रखें|कब बेचें|इंतजार करें|रोकना|रखना"
    ]
    if not extracted_intent and any(re.search(pat, clean_lower) for pat in store_patterns):
        extracted_intent = "store_or_sell"

    # Check Price Check (Devanagari Marathi, Transliterated, Hindi, and English)
    price_patterns = [
        r"today(?:'s)? price|current price|market price|what is the price|modal price|rate",
        r"aaj(?:cha| ka)? bhav|bhav kya|bhav kitna|rate kya|rate kitna|bhav sanga|bhav kay|dar kay",
        r"आजचा भाव|बाजारभाव|दर काय|भाव काय|दर किती|भाव सांगा|भाव किती|काय भाव चाललाय|काय दर आहे|काय भाव आहे|भाव मिळतोय",
        r"आज का भाव|रेट क्या|भाव क्या|भाव कितना|दाम क्या|दाम कितना|भाव बताओ"
    ]
    if not extracted_intent and any(re.search(pat, clean_lower) for pat in price_patterns):
        # Only set price_check if not asking "where to sell" / "best market"
        if not any(w in clean_lower for w in ["best", "where", "kuthe", "kaha", "कुठे", "कहाँ", "सर्वोत्तम", "नेऊ"]):
            extracted_intent = "price_check"

    # Check Best Market (Devanagari Marathi, Transliterated, Hindi, and English)
    best_market_patterns = [
        r"best market|where to sell|where should i sell|which market|best place|recommend|suggest|sell",
        r"kaha bechu|kaha beche|kaun si mandi|kaha fayda|sabse achhi mandi|kaha bechna",
        r"कहाँ बेचूं|कहा बेचू|कौन सी मंडी|कहाँ फायदा|सबसे अच्छी मंडी|कहाँ बेचें|कहाँ बेचना",
        r"kuthe viku|koni mandi|konti mandi|konta bajar|kuthe fayda|sarvottam bajar|jast nafa|kuthe vikave|kuthe vikaayche|kuthe neu",
        r"कुठे विकू|कोणती मंडी|कोणता बाजार|कुठे फायदा|सर्वोत्तम बाजार|जास्त नफा|कुठे विकावे|कुठे विकायचे|कुठे नेऊ|कुठे परवडेल|कुठे जास्त भाव"
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
You are an NLP parser for Mandi Saathi, an agricultural price & sell advisor for Maharashtra farmers.
Analyze the user message in Marathi, Hindi, or English:
User message: "{query}"

If the message is in Marathi (or Devanagari script used in Maharashtra), ensure "language": "mr".
Extract strictly into JSON:
- "crop": One of ["Tomato", "Onion", "Soybean", "Tur", "Cotton", "Potato", "Wheat"] or null.
- "quantity": Number in quintals (float) or null. (1 ton = 10 quintals, 1 bag/poti = 0.5 quintals, 1 crate = 0.25 quintals).
- "location": District or Mandi name in Maharashtra (e.g. Pune, Nashik, Latur, Solapur, Ahilyanagar, Jalgaon, Akola, Kolhapur, Nagpur, Mumbai, Pimpalgaon, Lasalgaon, Shirur, etc.) or null.
- "intent": One of ["best_market", "store_or_sell", "price_check", "help", "greeting", "thanks", "identity"].
- "language": One of ["mr", "hi", "en"].

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
            return "तुम्हाला कोणत्या पिकासाठी सल्ला हवा आहे? (उदा. टोमॅटो, कांदा, सोयाबीन, तूर, कापूस, बटाटा किंवा गहू)"
        elif lang == "hi":
            return "आप किस फसल के लिए सलाह चाहते हैं? (जैसे: टमाटर, प्याज, सोयाबीन, तूर, आलू, गेहूं या कपास)"
        else:
            return "Which crop would you like advice for? (e.g. Tomato, Onion, Soybean, Tur, Potato, Wheat, Cotton)"

    elif missing_field == "location":
        if lang == "mr":
            return f"तुम्ही तुमचा {crop_info['mr']} कोणत्या जिल्ह्यातून किंवा तालुक्यातून विक्रीसाठी आणणार आहात? (उदा. पुणे, नाशिक, लातूर, सोलापूर, अहिल्यानगर)"
        elif lang == "hi":
            return f"आप अपने {crop_info['hi']} किस ज़िले या स्थान से मंडी ले जाना चाहते हैं? (जैसे: पुणे, नाशिक, लातूर, सोलापूर)"
        else:
            return f"Which district or town in Maharashtra are you bringing your {crop_info['en']} from? (e.g. Pune, Nashik, Latur, Solapur)"

    elif missing_field == "quantity":
        if lang == "mr":
            return f"तुमच्याकडे विक्रीसाठी {crop_info['mr']} चे अंदाजे किती क्विंटल प्रमाण (किंवा किती पोती/गाडी) आहे?"
        elif lang == "hi":
            return f"आपके पास बिक्री के लिए {crop_info['hi']} की कितनी मात्रा (क्विंटल) है?"
        else:
            return f"What is the quantity of {crop_info['en']} you plan to sell (in quintals)?"

    return "Could you please specify more details about your crop and location?"


# -----------------------------------------------------------------------------
# Pure Marathi Devanagari Formatters (Zero English Leaks)
# -----------------------------------------------------------------------------

def format_marathi_best_market_reply(
    location: str,
    crop_name_mr: str,
    effective_qty: float,
    adv_res: Dict[str, Any]
) -> str:
    """Formats best market advice 100% in pure Marathi Devanagari."""
    best = adv_res.get("best_recommendation")
    if not best:
        return f"क्षमस्व, {location} परिसरात {crop_name_mr} पिकासाठी सध्या सक्रिय बाजारभाव उपलब्ध नाहीत. कृपया थोड्या वेळाने पुन्हा तपासा."

    net_ret = best["net_return_per_quintal"]
    total_earn = best["total_net_earnings"]
    gross = best["gross_modal_price"]
    trans = best["costs"]["transport_per_q"]
    mkt = best["market"]
    dist = best["district"]
    dist_km = best["distance_km"]
    cutoff = best.get("auction_cutoff", "12:00")
    be_price = best.get("break_even_price")
    gain = best.get("gain_vs_nearest_per_quintal", 0.0)
    is_nearest = best.get("is_nearest", False)

    # Marathi verdict reason
    if is_nearest:
        verdict = f"स्थानिक {mkt} बाजारात विक्री करा: अंतर केवळ {dist_km} किमी असल्याने कमी वाहतूक खर्च आणि वेळेत लिलाव यामुळे खिशात सर्वाधिक निव्वळ नफा राहील."
    elif gain > 0:
        verdict = f"{mkt} बाजारात जाणे अधिक फायदेशीर: तिथे मिळणारा जास्त भाव वाहतूक व हमाली खर्च भरून काढून प्रति क्विंटल +₹{gain:,.2f} जास्तीचा निव्वळ नफा देतो."
    elif best.get("missed_cutoff"):
        verdict = f"{mkt} बाजारात सकाळी {cutoff} ची लिलाव वेळ हुकण्याचा संभव असल्याने स्थानिक बाजारात विक्री करणे जास्त सुरक्षित आहे."
    else:
        verdict = f"{mkt} बाजार आपल्या {effective_qty:g} क्विंटल मालासाठी सर्वात फायदेशीर ठरतो."

    be_text = ""
    if be_price and not is_nearest:
        be_text = f"\n⚖️ **किमान फायदेशीर भाव (Break-Even):** ₹{be_price:,.2f}/क्विंटल\n*(लांबच्या बाजारात जाण्यासाठी कमीत कमी एवढा भाव मिळणे आवश्यक आहे, अन्यथा स्थानिक बाजारातच विक्री करणे योग्य ठरेल.)*\n"

    # Alternative mandis comparison in Marathi
    comparisons = adv_res.get("comparisons", [])
    comp_lines = []
    for c in comparisons[:2]:
        c_mkt = c["market"]
        c_net = c["net_return_per_quintal"]
        c_dist = c["distance_km"]
        comp_lines.append(f"• **{c_mkt}** ({c_dist} किमी): निव्वळ नफा ₹{c_net:,.2f}/क्विंटल")
    comp_section = "\n📊 **इतर बाजार समित्यांशी तुलना:**\n" + "\n".join(comp_lines) if comp_lines else ""

    return (
        f"**{location}** भागातील तुमच्या **{effective_qty:g} क्विंटल {crop_name_mr}** साठी सर्वात जास्त नफा देणारा बाजार **{mkt}** ({dist} जिल्हा) आहे!\n\n"
        f"💰 **खिशात पडणारा निव्वळ नफा:** **₹{net_ret:,.2f}/क्विंटल**\n"
        f"💵 **एकूण निव्वळ उत्पन्न:** **₹{total_earn:,.0f}** (सर्व खर्च वजा जाता)\n"
        f"📊 **मंडीचा सरासरी भाव:** ₹{gross:,.2f}/क्विंटल\n"
        f"🚚 **वाहतूक खर्च:** -₹{trans:,.2f}/क्विंटल ({dist_km} किमी अंतर, टेम्पो भाडे)\n"
        f"⏱️ **लिलाव वेळ:** सकाळी {cutoff} पूर्वी पोहोचावे\n"
        f"{be_text}"
        f"{comp_section}\n\n"
        f"💡 **सल्ला:** {verdict}"
    )


def format_marathi_store_or_sell_reply(
    crop: str,
    crop_name_mr: str,
    market_label: str,
    storage_res: Dict[str, Any]
) -> str:
    """Formats storage advice 100% in pure Marathi Devanagari."""
    rec = storage_res.get("recommendation", "Sell now")
    current_price = storage_res.get("current_price", 0.0)
    net_gain = storage_res.get("net_benefit_per_quintal", 0.0)
    is_viable = storage_res.get("is_storage_viable", True)

    if not is_viable or crop in ["Tomato"]:
        decision_badge = "आजच तातडीने विक्री करा"
        analysis = f"{crop_name_mr} हे अत्यंत नाशवंत पीक आहे. शेतात किंवा साध्या खोलीत साठवणूक केल्यास मालाची नासाडी व घट वेगाने होते. त्यामुळे आजच्या चालू बाजारात त्वरित विक्री करणे फायदेशीर ठरेल."
    elif "wait" in rec.lower():
        wait_days = storage_res.get("best_wait_days", 3)
        decision_badge = f"{wait_days} दिवस साठवून ठेवा"
        analysis = f"पुढील {wait_days} दिवसांत बाजारभावात तेजीची शक्यता आहे. अपेक्षित भाववाढीमुळे गोदामाचे भाडे आणि वजनातील घट वजा जाता प्रति क्विंटल अंदाजे +₹{net_gain:,.2f} जास्तीचा नफा मिळू शकेल."
    elif "sell" in rec.lower():
        decision_badge = "आजच विक्री करा"
        if net_gain <= 0:
            analysis = "पुढील ५ दिवसांत बाजारभाव स्थिर किंवा घसरण्याची शक्यता असून साठवणुकीचा खर्च आणि वजनातील घट यामुळे तोटा होऊ शकतो. आजच विक्री करणे सर्वात योग्य राहील."
        else:
            analysis = f"साठवणुकीमुळे मिळणारा संभाव्य फायदा (प्रति क्विंटल केवळ +₹{net_gain:,.2f}) खूप कमी असून बाजार चढ-उताराच्या जोखमीसाठी पुरेसा नाही. आजच विक्री करणे सुरक्षित आहे."
    else:
        decision_badge = "अपुरा डेटा"
        analysis = f"{market_label} बाजारात साठवणुकीचा अचूक सल्ला देण्यासाठी पुरेशा ऐतिहासिक नोंदी उपलब्ध नाहीत."

    return (
        f"**{market_label}** मध्ये **{crop_name_mr}** साठवणूक आणि विक्री निर्णय सल्ला:\n\n"
        f"🎯 **शिफारस:** **{decision_badge}**\n"
        f"📈 **आजचा चालू भाव:** ₹{current_price:,.2f}/क्विंटल\n"
        f"⚖️ **साठवणुकीचा निव्वळ फायदा:** ₹{net_gain:,.2f}/क्विंटल (खर्च व घट वजा जाता)\n\n"
        f"💡 **विश्लेषण:** {analysis}"
    )


def format_marathi_price_check_reply(
    crop_name_mr: str,
    target_mandi: Optional[Dict[str, Any]]
) -> str:
    """Formats price check advice 100% in pure Marathi Devanagari."""
    if not target_mandi:
        return f"{crop_name_mr} पिकासाठी सध्या कोणतीही अधिकृत बाजारभाव नोंद उपलब्ध नाही."

    modal = target_mandi["modal_price"]
    min_p = target_mandi["min_price"]
    max_p = target_mandi["max_price"]
    arr_date = target_mandi["arrival_date"]
    mkt = target_mandi["market"]
    dist = target_mandi["district"]

    return (
        f"**{mkt}** ({dist} जिल्हा) कृषी उत्पन्न बाजार समितीमध्ये **{crop_name_mr}** चे ताजे अधिकृत दर:\n\n"
        f"📊 **सरासरी (मॉडेल) भाव:** **₹{modal:,.2f}/क्विंटल**\n"
        f"📉 **किमान भाव:** ₹{min_p:,.2f}/क्विंटल\n"
        f"📈 **कमाल भाव:** ₹{max_p:,.2f}/क्विंटल\n"
        f"📅 **नोंदणी दिनांक:** {arr_date}\n\n"
        f"💡 *टीप: हे दर Agmarknet वरील अधिकृत लिलाव नोंदींनुसार आहेत.*"
    )


def process_chat_message(
    message: str,
    explicit_language: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Processes chat query, maintains multi-turn session context, and returns response."""
    clean_msg = message.strip()
    extracted = extract_entities(clean_msg)

    # Contextual session retrieval & merging
    session: Dict[str, Any] = {}
    if session_id:
        session = SESSION_MEMORY.get(session_id, {})

    # Determine language:
    # 1. Distinct language markers in text override UI preference (e.g. user typed pure Marathi/Hindi/English)
    # 2. Otherwise respect explicit_language (from frontend UI dropdown)
    # 3. Otherwise respect active session language context
    # 4. Default to Marathi (APMC Maharashtra core user base)
    msg_lang = detect_language(clean_msg)
    
    marathi_strong = any(m in clean_msg for m in ["आहे", "आहेत", "कुठे", "कसं", "कसे", "विकू", "विकायचे", "विकायचा", "कांदा", "साठवणूक", "माझ्याकडे", "पोती", "गोणी", "सांगा", "नमस्कार", "धन्यवाद", "होईल"])
    hindi_strong = any(h in clean_msg for h in ["है", "हैं", "कहाँ", "बेचूं", "बेचना", "प्याज", "बताओ", "चाहिए", "मुझे", "नमस्ते", "शुक्रिया"])
    english_strong = bool(re.search(r"\b(where|sell|price|store|should|what|quintals?|hello|thanks)\b", clean_msg, re.IGNORECASE))

    if marathi_strong:
        lang = "mr"
    elif hindi_strong:
        lang = "hi"
    elif english_strong and not any("\u0900" <= ch <= "\u097F" for ch in clean_msg):
        lang = "en"
    elif explicit_language in ["mr", "hi", "en"]:
        lang = explicit_language
    elif session.get("language") in ["mr", "hi", "en"]:
        lang = session["language"]
    else:
        lang = msg_lang if msg_lang in ["mr", "hi", "en"] else "mr"

    intent = extracted.get("intent") or session.get("last_intent") or "best_market"
    crop = extracted.get("crop") or session.get("crop")
    location = extracted.get("location") or session.get("location")
    quantity = extracted.get("quantity") or session.get("quantity")

    # Update session memory
    if session_id:
        SESSION_MEMORY[session_id] = {
            "crop": crop,
            "location": location,
            "quantity": quantity,
            "last_intent": intent,
            "language": lang
        }

    # 1. Handle Conversational Intents: GREETING, THANKS, IDENTITY, HELP
    if intent == "greeting":
        if lang == "mr":
            reply = (
                "नमस्कार शेतकरी मित्र! मी **मंडी साथी** आहे — महाराष्ट्रातील शेतकरी बांधवांसाठी AI कृषी सल्लागार.\n\n"
                "मी तुम्हाला खालील गोष्टींमध्ये मदत करू शकतो:\n"
                "• **विक्रीसाठी सर्वोत्तम बाजार:** उदा. 'पुण्यात २० क्विंटल टोमॅटो कुठे विकू?'\n"
                "• **साठवणूक की विक्री निर्णय:** उदा. 'लासलगावमध्ये कांदा विकू की ठेवू?'\n"
                "• **ताजे बाजारभाव:** उदा. 'लातूरमध्ये सोयाबीनचा आजचा भाव काय आहे?'\n\n"
                "तुम्हाला कोणत्या पिकाबद्दल माहिती हवी आहे? बोला किंवा लिहा! 🌾"
            )
        elif lang == "hi":
            reply = (
                "नमस्ते किसान भाई! मैं **मंडी साथी** हूँ — AI मंडी भाव और सही समय सलाहकार।\n\n"
                "आप मुझसे फसल बिक्री, भंडारण सलाह या ताज़ा मंडी भाव पूछ सकते हैं। बताइए, किस फसल की जानकारी चाहिए?"
            )
        else:
            reply = (
                "Hello farmer friend! I am **Mandi Saathi**, your AI crop price and sell-timing advisor for Maharashtra APMC mandis.\n\n"
                "How can I help you today? You can ask about best markets, price forecasts, or storage decisions."
            )

        return {
            "reply": reply,
            "intent": "help",
            "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": "greeting"},
            "missing_field": None,
            "follow_up_needed": False,
            "data": None,
            "language": lang
        }

    if intent == "thanks":
        if lang == "mr":
            reply = (
                "आपले मनःपूर्वक स्वागत आहे! शेतकरी मित्रांच्या सेवेसाठी आणि योग्य नफा मिळवून देण्यासाठी मंडी साथी सदैव तत्पर आहे.\n\n"
                "इतर कोणत्याही पिकाचा किंवा बाजाराचा भाव जाणून घेण्यासाठी नक्की विचारा! 🌾"
            )
        elif lang == "hi":
            reply = "आपका स्वागत है! किसान भाइयों की सेवा के लिए मंडी साथी सदैव उपलब्ध है। कोई अन्य सवाल हो तो अवश्य पूछें! 🌾"
        else:
            reply = "You are most welcome! Mandi Saathi is always here to help you get the best net returns. Feel free to ask any other questions! 🌾"

        return {
            "reply": reply,
            "intent": "help",
            "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": "thanks"},
            "missing_field": None,
            "follow_up_needed": False,
            "data": None,
            "language": lang
        }

    if intent == "identity":
        if lang == "mr":
            reply = (
                "मी **मंडी साथी (Mandi Saathi)** आहे!\n\n"
                "मी महाराष्ट्रातील शेतकरी बांधवांसाठी विकसित केलेला AI कृषी बाजारभाव आणि विक्री सल्लागार आहे. "
                "मी केवळ बाजारातील भाव न दाखवता, वाहतूक खर्च, हमाली, तोलाई आणि नासाडी वजा करून खिशात राहणारा खरा निव्वळ नफा काढून देतो, जेणेकरून तुमचे कोणतेही नुकसान होणार नाही."
            )
        elif lang == "hi":
            reply = "मैं **मंडी साथी** हूँ — महाराष्ट्र के किसानों के लिए बनाया गया AI कृषि बाज़ार और बिक्री सलाहकार।"
        else:
            reply = "I am **Mandi Saathi**, an AI price and sell-timing advisor built to protect Indian farmers from the headline price trap."

        return {
            "reply": reply,
            "intent": "help",
            "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": "identity"},
            "missing_field": None,
            "follow_up_needed": False,
            "data": None,
            "language": lang
        }

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
            "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": intent},
            "missing_field": None,
            "follow_up_needed": False,
            "data": None,
            "language": lang
        }

    # 2. Check for missing essential fields -> Ask ONE targeted follow-up
    if not crop:
        follow_up_msg = generate_follow_up("crop", None, lang)
        return {
            "reply": follow_up_msg,
            "intent": intent,
            "entities": {"crop": None, "quantity": quantity, "location": location, "intent": intent},
            "missing_field": "crop",
            "follow_up_needed": True,
            "data": None,
            "language": lang
        }

    # For best_market intent, location is required to calculate distance and freight
    if intent == "best_market" and not location:
        follow_up_msg = generate_follow_up("location", crop, lang)
        return {
            "reply": follow_up_msg,
            "intent": intent,
            "entities": {"crop": crop, "quantity": quantity, "location": None, "intent": intent},
            "missing_field": "location",
            "follow_up_needed": True,
            "data": None,
            "language": lang
        }

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
            if lang == "mr":
                reply = f"क्षमस्व, {location} जवळ {crop_names['mr']} पिकासाठी सध्या सक्रिय बाजारभाव उपलब्ध नाहीत."
            elif lang == "hi":
                reply = f"क्षमा करें, {location} के पास {crop_names['hi']} के लिए सक्रिय मंडी भाव उपलब्ध नहीं हैं।"
            else:
                reply = f"Sorry, no active trading records were found for {crop} in {location}."
            return {
                "reply": reply,
                "intent": intent,
                "entities": {"crop": crop, "quantity": effective_qty, "location": location, "intent": intent},
                "missing_field": None,
                "follow_up_needed": False,
                "data": adv_res,
                "language": lang
            }

        if lang == "mr":
            reply = format_marathi_best_market_reply(
                location=location or "पुणे",
                crop_name_mr=crop_names["mr"],
                effective_qty=effective_qty,
                adv_res=adv_res
            )
        elif lang == "hi":
            net_ret = best["net_return_per_quintal"]
            total_earn = best["total_net_earnings"]
            gross = best["gross_modal_price"]
            trans = best["costs"]["transport_per_q"]
            mkt = best["market"]
            dist = best["district"]
            dist_km = best["distance_km"]
            reason = best["verdict_reason"]
            be_price = best.get("break_even_price")
            be_note = f"\n⚖️ **ब्रेक-ईवन भाव:** ₹{be_price:,.2f}/क्विंटल (इससे कम भाव मिलने पर नजदीकी मंडी बेहतर रहेगी)" if be_price and not best["is_nearest"] else ""

            reply = (
                f"**{location}** से आपके **{effective_qty:g} क्विंटल {crop_names['hi']}** के लिए सबसे अच्छी मंडी **{mkt}** ({dist} ज़िला) है!\n\n"
                f"💰 **आपकी जेब में शुद्ध लाभ:** **₹{net_ret:,.2f}/क्विंटल** (कुल शुद्ध लाभ: **₹{total_earn:,.0f}**)\n"
                f"📊 **मंडी मॉडल भाव:** ₹{gross:,.2f}/क्विंटल\n"
                f"🚚 **भाड़ा कटौती:** -₹{trans:,.2f}/क्विंटल ({dist_km} किमी, टेम्पो)\n"
                f"{be_note}\n"
                f"💡 **सलाह:** {reason}"
            )
        else:
            net_ret = best["net_return_per_quintal"]
            total_earn = best["total_net_earnings"]
            gross = best["gross_modal_price"]
            trans = best["costs"]["transport_per_q"]
            mkt = best["market"]
            dist = best["district"]
            dist_km = best["distance_km"]
            reason = best["verdict_reason"]
            be_price = best.get("break_even_price")
            be_note = f"\n⚖️ **Break-Even Threshold:** ₹{be_price:,.2f}/quintal (price required at far mandi to beat local market)" if be_price and not best["is_nearest"] else ""

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
            "entities": {"crop": crop, "quantity": effective_qty, "location": location, "intent": intent},
            "missing_field": None,
            "follow_up_needed": False,
            "data": adv_res,
            "language": lang
        }

    # 4. Handle Intent: STORE_OR_SELL
    elif intent == "store_or_sell":
        storage_res = get_storage_advice(crop=crop, market=location)
        market_label = location or storage_res.get("market", "महाराष्ट्र")

        if lang == "mr":
            reply = format_marathi_store_or_sell_reply(
                crop=crop,
                crop_name_mr=crop_names["mr"],
                market_label=market_label,
                storage_res=storage_res
            )
        elif lang == "hi":
            rec = storage_res.get("recommendation", "Sell now")
            current_price = storage_res.get("current_price", 0.0)
            net_gain = storage_res.get("net_benefit_per_quintal", 0.0)
            rationale = storage_res.get("rationale", "")
            rec_hi = "अभी बेचें (Sell now)" if "sell" in rec.lower() else ("कुछ दिन रुकें (Wait)" if "wait" in rec.lower() else "अपर्याप्त डेटा")
            reply = (
                f"**{market_label}** में **{crop_names['hi']}** भंडारण और बिक्री सलाह:\n\n"
                f"🎯 **सिफारिश:** **{rec_hi}**\n"
                f"📈 **मौजूदा भाव:** ₹{current_price:,.2f}/क्विंटल\n"
                f"⚖️ **अनुमानित शुद्ध लाभ:** ₹{net_gain:,.2f}/क्विंटल (गोदाम खर्च और वजन घटौती के बाद)\n"
                f"💡 **विश्लेषण:** {rationale}"
            )
        else:
            rec = storage_res.get("recommendation", "Sell now")
            current_price = storage_res.get("current_price", 0.0)
            net_gain = storage_res.get("net_benefit_per_quintal", 0.0)
            rationale = storage_res.get("rationale", "")
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
            "entities": {"crop": crop, "quantity": effective_qty, "location": location, "intent": intent},
            "missing_field": None,
            "follow_up_needed": False,
            "data": storage_res,
            "language": lang
        }

    # 5. Handle Intent: PRICE_CHECK
    elif intent == "price_check":
        price_rows = get_latest_prices_for_crop(crop)
        if not price_rows:
            if lang == "mr":
                reply = f"{crop_names['mr']} पिकासाठी सध्या कोणतीही बाजारभाव नोंद उपलब्ध नाही."
            elif lang == "hi":
                reply = f"{crop_names['hi']} फसल के लिए हाल ही में कोई मंडी भाव उपलब्ध नहीं है।"
            else:
                reply = f"No recent market price records found for {crop}."
            return {
                "reply": reply,
                "intent": intent,
                "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": intent},
                "missing_field": None,
                "follow_up_needed": False,
                "data": None,
                "language": lang
            }

        # Match location or pick top reporting mandi
        target_mandi = None
        if location:
            for row in price_rows:
                if (location.lower() in row["market"].lower() or
                    location.lower() in row["district"].lower()):
                    target_mandi = row
                    break
        if not target_mandi:
            target_mandi = price_rows[0]

        if lang == "mr":
            reply = format_marathi_price_check_reply(crop_names["mr"], target_mandi)
        elif lang == "hi":
            modal = target_mandi["modal_price"]
            min_p = target_mandi["min_price"]
            max_p = target_mandi["max_price"]
            arr_date = target_mandi["arrival_date"]
            mkt = target_mandi["market"]
            dist = target_mandi["district"]
            reply = (
                f"**{mkt}** ({dist} ज़िला) मंडी में **{crop_names['hi']}** का ताज़ा भाव:\n\n"
                f"📊 **मॉडल भाव:** **₹{modal:,.2f}/क्विंटल**\n"
                f"📉 **न्यूनतम भाव:** ₹{min_p:,.2f}/क्विंटल\n"
                f"📈 **अधिकतम भाव:** ₹{max_p:,.2f}/क्विंटल\n"
                f"📅 **दिनांक:** {arr_date}"
            )
        else:
            modal = target_mandi["modal_price"]
            min_p = target_mandi["min_price"]
            max_p = target_mandi["max_price"]
            arr_date = target_mandi["arrival_date"]
            mkt = target_mandi["market"]
            dist = target_mandi["district"]
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
            "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": intent},
            "missing_field": None,
            "follow_up_needed": False,
            "data": target_mandi,
            "language": lang
        }

    # Fallback response
    if lang == "mr":
        reply = "मी तुम्हाला महाराष्ट्रातील कृषी उत्पन्न बाजार समित्यांमधील बाजारभाव आणि विक्री सल्ल्यामध्ये कशी मदत करू?"
    elif lang == "hi":
        reply = "मैं महाराष्ट्र की मंडियों में फसल भाव और बिक्री सलाह में आपकी क्या सहायता करूँ?"
    else:
        reply = "How can I help you with Maharashtra APMC mandi prices and sell timing?"

    return {
        "reply": reply,
        "intent": intent,
        "entities": {"crop": crop, "quantity": quantity, "location": location, "intent": intent},
        "missing_field": None,
        "follow_up_needed": False,
        "data": None,
        "language": lang
    }
