"""Alerts, Farmer Reports, and Data Quality Service for Mandi Saathi.

Handles:
1. Alert Subscriptions & WhatsApp-style morning market message previews built from real data.
2. "I sold today" Farmer Reports saved to farmer_reports with strict sanity checks and distinct badges.
3. Mandi data quality metrics (last reported date, 30-day coverage, confidence badge).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.database import execute_query, fetch_all, fetch_one
from backend.services.advisory_engine import calculate_advisory
from backend.services.agmarknet_fetcher import get_canonical_commodity_name
from backend.services.data_service import load_mandi_matrix
from backend.services.forecast_engine import get_storage_advice

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 1. Alert Subscriptions & WhatsApp Morning Preview
# -----------------------------------------------------------------------------

def subscribe_alert(
    crop: str,
    district: str,
    language: str = "mr",
    nickname: Optional[str] = None
) -> Dict[str, Any]:
    """Subscribes a farmer to daily mandi price alerts."""
    if not crop or not crop.strip():
        raise ValueError("Crop name is required.")
    if not district or not district.strip():
        raise ValueError("District is required.")

    canonical_crop = get_canonical_commodity_name(crop.strip())
    clean_district = district.strip().title()
    clean_lang = language.strip().lower() if language else "mr"
    if clean_lang not in ("en", "hi", "mr"):
        clean_lang = "mr"
    clean_nick = nickname.strip() if nickname and nickname.strip() else "शेतकरी मित्र"

    # Check if subscription already exists
    existing = fetch_one("""
        SELECT id, crop, district, language, nickname, is_active, created_at
        FROM alert_subscriptions
        WHERE crop = ? AND district = ? AND is_active = 1
    """, (canonical_crop, clean_district))

    if existing:
        execute_query("""
            UPDATE alert_subscriptions
            SET language = ?, nickname = ?, is_active = 1
            WHERE id = ?
        """, (clean_lang, clean_nick, existing["id"]))
        return {
            "id": existing["id"],
            "crop": canonical_crop,
            "district": clean_district,
            "language": clean_lang,
            "nickname": clean_nick,
            "is_active": 1,
            "message": "Subscription updated successfully."
        }

    execute_query("""
        INSERT INTO alert_subscriptions (crop, district, language, nickname, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (canonical_crop, clean_district, clean_lang, clean_nick))

    created = fetch_one("""
        SELECT id, crop, district, language, nickname, is_active, created_at
        FROM alert_subscriptions
        WHERE crop = ? AND district = ? AND is_active = 1
        ORDER BY id DESC LIMIT 1
    """, (canonical_crop, clean_district))

    return {
        "id": created["id"] if created else None,
        "crop": canonical_crop,
        "district": clean_district,
        "language": clean_lang,
        "nickname": clean_nick,
        "is_active": 1,
        "message": "Subscribed successfully."
    }


def get_active_alerts() -> List[Dict[str, Any]]:
    """Returns all active alert subscriptions."""
    rows = fetch_all("""
        SELECT id, crop, district, language, nickname, is_active, created_at
        FROM alert_subscriptions
        WHERE is_active = 1
        ORDER BY created_at DESC
    """)
    return rows


def delete_alert(subscription_id: int) -> bool:
    """Deactivates an alert subscription."""
    count = execute_query("""
        UPDATE alert_subscriptions
        SET is_active = 0
        WHERE id = ?
    """, (subscription_id,))
    return count > 0


def generate_morning_alert_preview(
    crop: str,
    district: str,
    language: str = "mr",
    nickname: Optional[str] = None
) -> Dict[str, Any]:
    """Generates a WhatsApp-style morning message preview using real advisory and forecast figures."""
    canonical_crop = get_canonical_commodity_name(crop.strip() if crop else "Tomato")
    clean_district = district.strip().title() if district else "Pune"
    clean_lang = language.strip().lower() if language else "mr"
    if clean_lang not in ("en", "hi", "mr"):
        clean_lang = "mr"
    clean_nick = nickname.strip() if nickname and nickname.strip() else ("शेतकरी मित्र" if clean_lang == "mr" else "Kisan Mitra")

    # Fetch real advisory data
    advisory = calculate_advisory(
        crop=canonical_crop,
        district=clean_district,
        quantity_quintals=20.0
    )

    best = advisory.get("best_recommendation")
    comparisons = advisory.get("comparisons", [])

    today_str = datetime.now().strftime("%d %b %Y")
    
    # Translations for crops
    crop_trans = {
        "Tomato": {"en": "Tomato", "hi": "टमाटर", "mr": "टोमॅटो"},
        "Onion": {"en": "Onion", "hi": "प्याज", "mr": "कांदा"},
        "Soyabean": {"en": "Soybean", "hi": "सोयाबीन", "mr": "सोयाबीन"},
        "Wheat": {"en": "Wheat", "hi": "गेहूं", "mr": "गहू"},
        "Cotton": {"en": "Cotton", "hi": "कपास", "mr": "कापूस"},
        "Potato": {"en": "Potato", "hi": "आलू", "mr": "बटाटा"},
        "Red gram/Arhar/Tur(whole)": {"en": "Tur / Arhar", "hi": "तूर (अरहर)", "mr": "तूर"}
    }
    crop_display = crop_trans.get(canonical_crop, {}).get(clean_lang, canonical_crop)

    # Storage advice
    best_market_name = best["market"] if best else "Pune"
    storage_info = get_storage_advice(crop=canonical_crop, market=best_market_name)
    verdict = storage_info.get("verdict", "Sell now")

    if not best:
        if clean_lang == "mr":
            msg = f"🌅 *मंडी साथी प्रभात अलर्ट* 🌾\n📅 *दिनांक:* {today_str}\n\nनमस्कार {clean_nick}!\n\n{clean_district} परिसरात {crop_display} पिकासाठी सध्या सक्रिय व्यवहार आढळले नाहीत. कृपया दुपारनंतर पुन्हा तपासा."
        elif clean_lang == "hi":
            msg = f"🌅 *मंडी साथी सुबह का अलर्ट* 🌾\n📅 *दिनांक:* {today_str}\n\nनमस्ते {clean_nick}!\n\n{clean_district} क्षेत्र में {crop_display} के लिए सक्रिय मंडी भाव अभी उपलब्ध नहीं हैं। कृपया दोपहर बाद पुनः देखें।"
        else:
            msg = f"🌅 *Mandi Saathi Morning Alert* 🌾\n📅 *Date:* {today_str}\n\nHello {clean_nick}!\n\nNo recent trading records found for {crop_display} around {clean_district}. Please check back later today."

        return {
            "preview_text": msg,
            "crop": canonical_crop,
            "district": clean_district,
            "language": clean_lang,
            "nickname": clean_nick,
            "best_recommendation": None
        }

    # Format numbers
    modal_price = int(round(best["gross_modal_price"]))
    net_return = int(round(best["net_return_per_quintal"]))
    distance_km = best["distance_km"]
    cutoff = best.get("auction_cutoff", "12:00")
    mkt = best["market"]

    # Comparisons snippet (up to 2)
    alt_lines = []
    for comp in comparisons[:2]:
        c_mkt = comp["market"]
        c_price = int(round(comp["gross_modal_price"]))
        c_dist = comp["distance_km"]
        if clean_lang == "mr":
            alt_lines.append(f"• *{c_mkt}:* ₹{c_price}/क्विंटल ({c_dist} किमी)")
        elif clean_lang == "hi":
            alt_lines.append(f"• *{c_mkt}:* ₹{c_price}/क्विंटल ({c_dist} किमी)")
        else:
            alt_lines.append(f"• *{c_mkt}:* ₹{c_price}/q ({c_dist} km)")
    alt_text = "\n".join(alt_lines) if alt_lines else "• इतर पर्याय: उपलब्ध नाहीत"

    # Verdict translation
    if clean_lang == "mr":
        verdict_map = {
            "Sell now": "आजच विक्री करा (किंमत अनुकूल आहे)",
            "Wait": "काही दिवस साठवून ठेवा (पुढील ५ दिवसांत तेजी अपेक्षित)",
            "Sell-or-store": "विक्री किंवा साठवणूक (भाव स्थिर राहण्याची शक्यता)"
        }
        verdict_text = verdict_map.get(verdict, verdict)

        msg = (
            f"🌅 *मंडी साथी दैनिक सकाळचा बाजारभाव अलर्ट* 🌾\n"
            f"📅 *दिनांक:* {today_str}\n"
            f"👋 *नमस्कार {clean_nick}!* आजचे बाजारभाव खालीलप्रमाणे आहेत:\n\n"
            f"📍 *क्षेत्र:* {clean_district} | *पीक:* {crop_display}\n\n"
            f"🏆 *आजची सर्वोत्तम कृषी उत्पन्न बाजार समिती:*\n"
            f"👉 *{mkt}*\n"
            f"💰 *बाजारभाव:* ₹{modal_price}/क्विंटल\n"
            f"🚚 *अंदाजे निव्वळ नफा:* *₹{net_return}/क्विंटल* (वाहतूक व खर्च वजा जाता)\n"
            f"⏱️ *अंतर:* {distance_km} किमी | *नीलामी वेळ:* सकाळी {cutoff} पूर्वी\n\n"
            f"📊 *इतर जवळचे बाजार:*\n{alt_text}\n\n"
            f"🔮 *विक्री की साठवणूक सल्ला:* *{verdict_text}*\n\n"
            f"💡 *सल्ला:* {best.get('verdict_reason', 'स्थानिक बाजारात थेट विक्री फायदेशीर ठरते.')}\n\n"
            f"_टीप: हे अंदाज आहेत, हमी नाही. अधिक माहितीसाठी Mandi Saathi ॲप उघडा._"
        )
    elif clean_lang == "hi":
        verdict_map = {
            "Sell now": "आज ही बेचें (भाव अनुकूल हैं)",
            "Wait": "भंडारण करें (अगले 5 दिनों में तेजी संभव)",
            "Sell-or-store": "बेचें या रखें (बाजार भाव स्थिर)"
        }
        verdict_text = verdict_map.get(verdict, verdict)

        msg = (
            f"🌅 *मंडी साथी दैनिक सुबह का मंडी भाव अलर्ट* 🌾\n"
            f"📅 *दिनांक:* {today_str}\n"
            f"👋 *नमस्ते {clean_nick}!* आज की ताज़ा मंडी रिपोर्ट:\n\n"
            f"📍 *जिला:* {clean_district} | *फसल:* {crop_display}\n\n"
            f"🏆 *आज की सर्वश्रेष्ठ मंडी:*\n"
            f"👉 *{mkt}*\n"
            f"💰 *मॉडल भाव:* ₹{modal_price}/क्विंटल\n"
            f"🚚 *अनुमानित शुद्ध लाभ:* *₹{net_return}/क्विंटल* (परिवहन खर्च के बाद)\n"
            f"⏱️ *दूरी:* {distance_km} किमी | *नीलामी समय:* सुबह {cutoff} तक\n\n"
            f"📊 *अन्य नजदीकी मंडियां:*\n{alt_text}\n\n"
            f"🔮 *बेचें या रखें निर्णय:* *{verdict_text}*\n\n"
            f"💡 *सलाह:* {best.get('verdict_reason', 'स्थानीय मंडी में बेचना सर्वोत्तम है।')}\n\n"
            f"_नोट: यह अनुमान है, गारंटी नहीं। Mandi Saathi AI._"
        )
    else:
        msg = (
            f"🌅 *Mandi Saathi Daily Morning Market Alert* 🌾\n"
            f"📅 *Date:* {today_str}\n"
            f"👋 *Hello {clean_nick}!* Here is your market intelligence:\n\n"
            f"📍 *District:* {clean_district} | *Crop:* {crop_display}\n\n"
            f"🏆 *Best APMC Option Today:*\n"
            f"👉 *{mkt}*\n"
            f"💰 *Modal Price:* ₹{modal_price}/quintal\n"
            f"🚚 *Est. Net Return:* *₹{net_return}/quintal* (after transport & fees)\n"
            f"⏱️ *Distance:* {distance_km} km | *Auction Cutoff:* {cutoff}\n\n"
            f"📊 *Nearby Alternatives:*\n{alt_text}\n\n"
            f"🔮 *Sell vs Store Verdict:* *{verdict}*\n\n"
            f"💡 *Rationale:* {best.get('verdict_reason', 'Low transport distance maximizes net profit.')}\n\n"
            f"_Estimates, not guarantees. Powered by Mandi Saathi AI._"
        )

    return {
        "preview_text": msg,
        "crop": canonical_crop,
        "district": clean_district,
        "language": clean_lang,
        "nickname": clean_nick,
        "best_recommendation": best,
        "verdict": verdict,
        "comparisons": comparisons[:3]
    }


# -----------------------------------------------------------------------------
# 2. "I sold today" Farmer Reports (Separated from Agmarknet)
# -----------------------------------------------------------------------------

def save_farmer_report(
    crop: str,
    market: str,
    price: float,
    quantity: float,
    report_date: Optional[str] = None
) -> Dict[str, Any]:
    """Saves a crowd-sourced transaction to farmer_reports with strict sanity checks.
    
    Never mixed into Agmarknet tables. Labeled with 'Farmer reported' badge.
    """
    # 1. Crop check
    if not crop or not crop.strip():
        raise ValueError("Crop name is required.")
    canonical_crop = get_canonical_commodity_name(crop.strip())

    # 2. Market check
    if not market or not market.strip():
        raise ValueError("Market name is required.")
    clean_market = market.strip()

    # 3. Price sanity checks
    try:
        price_val = float(price)
    except (TypeError, ValueError):
        raise ValueError("Price must be a valid number.")

    if price_val <= 0:
        raise ValueError("Price must be greater than zero.")
    if price_val > 50000.0:
        raise ValueError(f"Price ₹{price_val} is unrealistically high (must be <= ₹50,000/quintal).")

    # 4. Quantity sanity checks
    try:
        qty_val = float(quantity)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a valid number.")

    if qty_val <= 0:
        raise ValueError("Quantity must be greater than zero.")
    if qty_val > 10000.0:
        raise ValueError(f"Quantity {qty_val} quintals exceeds reasonable single-farmer batch limit (max 10,000 q).")

    # 5. Date sanity checks
    today = datetime.now().date()
    if report_date and str(report_date).strip():
        try:
            parsed_date = datetime.strptime(str(report_date).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
    else:
        parsed_date = today

    # Reject future dates (allow up to +1 day for timezones)
    if parsed_date > today + timedelta(days=1):
        raise ValueError("Transaction date cannot be in the future.")
    # Reject dates older than 1 year
    if parsed_date < today - timedelta(days=365):
        raise ValueError("Transaction date cannot be older than 1 year.")

    date_str = parsed_date.strftime("%Y-%m-%d")

    # Insert into farmer_reports (NEVER mandi_prices!)
    execute_query("""
        INSERT INTO farmer_reports (crop, market, price, quantity, report_date)
        VALUES (?, ?, ?, ?, ?)
    """, (canonical_crop, clean_market, round(price_val, 2), round(qty_val, 2), date_str))

    created = fetch_one("""
        SELECT id, crop, market, price, quantity, report_date, created_at
        FROM farmer_reports
        WHERE crop = ? AND market = ? AND price = ? AND quantity = ? AND report_date = ?
        ORDER BY id DESC LIMIT 1
    """, (canonical_crop, clean_market, round(price_val, 2), round(qty_val, 2), date_str))

    return {
        "id": created["id"] if created else None,
        "crop": canonical_crop,
        "market": clean_market,
        "price": round(price_val, 2),
        "quantity": round(qty_val, 2),
        "report_date": date_str,
        "created_at": created["created_at"] if created else datetime.now().isoformat(),
        "source": "farmer_reported",
        "badge": "Farmer reported",
        "is_farmer_reported": True,
        "message": "Report saved successfully with Farmer reported badge."
    }


def get_farmer_reports(
    crop: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieves farmer-submitted price reports, strictly kept separate from Agmarknet."""
    where_parts = []
    params: List[Any] = []

    if crop and crop.strip():
        canonical = get_canonical_commodity_name(crop.strip())
        where_parts.append("(crop = ? OR crop = ?)")
        params.extend([crop.strip(), canonical])

    if market and market.strip():
        where_parts.append("market = ?")
        params.append(market.strip())

    where_sql = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    params.append(int(limit))

    rows = fetch_all(f"""
        SELECT id, crop, market, price, quantity, report_date, created_at
        FROM farmer_reports
        {where_sql}
        ORDER BY report_date DESC, created_at DESC
        LIMIT ?
    """, tuple(params))

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "crop": r["crop"],
            "market": r["market"],
            "price": float(r["price"]),
            "quantity": float(r["quantity"]),
            "report_date": r["report_date"],
            "created_at": r["created_at"],
            "source": "farmer_reported",
            "badge": "Farmer reported",
            "is_farmer_reported": True
        })
    return results


# -----------------------------------------------------------------------------
# 3. Mandi Data Quality & Coverage Metrics
# -----------------------------------------------------------------------------

def get_data_quality() -> Dict[str, Any]:
    """Calculates data quality per mandi: last reported date, 30-day coverage, and confidence badge."""
    today = datetime.now().date()
    cutoff_30d = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    matrix = load_mandi_matrix()
    matrix_map = {m["market"]: m for m in matrix.get("mandis", [])}

    # Query latest date and distinct 30-day counts per mandi
    stats_rows = fetch_all("""
        SELECT 
            market,
            district,
            MAX(arrival_date) as latest_date,
            COUNT(*) as total_records,
            SUM(CASE WHEN arrival_date >= ? THEN 1 ELSE 0 END) as records_30d,
            COUNT(DISTINCT CASE WHEN arrival_date >= ? THEN arrival_date ELSE NULL END) as distinct_dates_30d,
            COUNT(DISTINCT commodity) as total_crops,
            MAX(is_sample) as has_sample,
            MAX(source) as sample_source
        FROM mandi_prices
        GROUP BY market, district
        ORDER BY market
    """, (cutoff_30d, cutoff_30d))

    stats_map = {r["market"]: r for r in stats_rows}
    all_markets = sorted(set(list(matrix_map.keys()) + list(stats_map.keys())))

    mandi_reports = []
    high_count = 0
    medium_count = 0
    low_count = 0

    for mkt in all_markets:
        info = matrix_map.get(mkt, {})
        stat = stats_map.get(mkt, {})

        district = stat.get("district") or info.get("district", "Unknown")
        latest_date_str = stat.get("latest_date")
        
        if latest_date_str:
            try:
                latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d").date()
                days_ago = max(0, (today - latest_date).days)
            except Exception:
                days_ago = 999
        else:
            latest_date_str = None
            days_ago = 999

        distinct_dates_30d = int(stat.get("distinct_dates_30d") or 0)
        records_30d = int(stat.get("records_30d") or 0)
        total_records = int(stat.get("total_records") or 0)

        # Expected trading days in 30 days is ~25 (excluding Sundays)
        coverage_pct = round(min(100.0, (distinct_dates_30d / 25.0) * 100.0), 1)

        # Confidence Badge Determination
        if days_ago <= 2 and distinct_dates_30d >= 15:
            confidence = "HIGH"
            badge_color = "green"
            high_count += 1
        elif days_ago <= 5 and distinct_dates_30d >= 5:
            confidence = "MEDIUM"
            badge_color = "yellow"
            medium_count += 1
        else:
            confidence = "LOW"
            badge_color = "red"
            low_count += 1

        has_coords = info.get("lat") is not None and info.get("lng") is not None

        mandi_reports.append({
            "market": mkt,
            "district": district,
            "lat": float(info["lat"]) if has_coords else None,
            "lng": float(info["lng"]) if has_coords else None,
            "coordinates_present": has_coords,
            "location_flag": "known" if has_coords else "location unknown",
            "latest_reported_date": latest_date_str,
            "days_since_report": days_ago if latest_date_str else None,
            "records_last_30d": records_30d,
            "active_trading_days_30d": distinct_dates_30d,
            "coverage_pct_30d": coverage_pct,
            "total_records": total_records,
            "confidence": confidence,
            "confidence_badge": badge_color,
            "is_sample": bool(stat.get("has_sample", 0)),
            "source": stat.get("sample_source", "none")
        })

    # Sort: HIGH confidence first, then by coverage descending
    conf_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    mandi_reports.sort(key=lambda x: (conf_order.get(x["confidence"], 3), -x["coverage_pct_30d"]))

    return {
        "status": "ready",
        "generated_at": datetime.now().isoformat(),
        "total_monitored_mandis": len(mandi_reports),
        "high_confidence_mandis": high_count,
        "medium_confidence_mandis": medium_count,
        "low_confidence_mandis": low_count,
        "mandis": mandi_reports
    }
