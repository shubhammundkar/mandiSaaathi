// Mandi Saathi - Internationalization (EN / HI / MR)

const STORAGE_KEY = 'mandisaathi_lang';

export const translations = {
  en: {
    // Brand
    brand_name: "Mandi Saathi",
    brand_tagline: "AI Price & Sell-Timing Advisor for Farmers",
    
    // Nav
    nav_advisor: "Advisor",
    nav_chat: "Voice Chat",
    nav_alerts: "Alerts",
    nav_proof: "Proof / Math",
    nav_about: "About",
    nav_design: "Design System",

    // Common Buttons
    btn_calculate: "Find Best Place to Sell",
    btn_try_demo: "⚡ Try Demo (Tomato • Pune • 20q)",
    btn_listen: "Listen to Advice",
    btn_speaking: "Speaking...",
    btn_speak: "Tap & Speak",
    btn_stop_speaking: "Listening...",
    btn_sell_now: "Sell Now",
    btn_wait_store: "Store & Wait",
    btn_retry: "Try Again",
    btn_save: "Save Alert",
    btn_view_details: "View Breakdown",

    // Common Badges & Statuses
    badge_best_net: "Highest Net Return",
    badge_fresh: "Fresh Data",
    badge_unreliable: "Stale / Unreliable",
    badge_high_conf: "High Confidence",
    badge_med_conf: "Medium Confidence",
    badge_low_conf: "Low Confidence",
    data_source_live: "Live Agmarknet",
    data_source_snapshot: "90-Day Verified Snapshot",
    data_source_sample: "Sample Fallback",

    // Advisor placeholders & form
    advisor_heading: "Smart Crop Sell Advisor",
    advisor_subheading: "Find out where and when to sell for the maximum net profit in your pocket after transport, market fee, and spoilage.",
    select_crop: "Select Crop",
    select_district: "Your Location (District)",
    input_quantity: "Harvest Quantity (Quintals)",
    select_vehicle: "Transport Vehicle",
    advanced_title: "Advanced Cost Settings (Optional)",
    label_rate_km: "Transport Rate (₹/km)",
    label_fee_pct: "APMC Market Fee (%)",
    label_spoil_rate: "Transit Spoilage (%/day)",
    label_loading_rate: "Loading Labor (₹/q)",
    loading_calculating: "Analyzing APMC prices & freight costs...",

    // Vehicles
    vehicle_tempo: "Tempo (Pickup)",
    vehicle_truck: "Mini Truck",
    vehicle_own: "Own Vehicle",

    // Crops
    crop_tomato: "Tomato",
    crop_onion: "Onion",
    crop_soybean: "Soybean",
    crop_tur: "Tur (Arhar)",
    crop_cotton: "Cotton",
    crop_potato: "Potato",
    crop_wheat: "Wheat",

    // Results screen
    results_hero_title: "Top Recommended Mandi",
    results_net_return: "Net Return",
    results_total_earnings: "Total Net Earnings",
    results_gross_price: "Gross Modal Price",
    results_total_deductions: "Total Deductions",
    results_gain_vs_nearest: "Extra Net vs Nearest",
    results_distance: "Distance",
    results_travel_time: "Travel Time",
    results_arrival: "Auction Arrival",
    results_breakeven_title: "Break-Even Price Threshold",
    results_forecast_title: "5-Day Price Outlook Corridor",
    results_storage_title: "Sell or Store Decision",
    results_comparisons_title: "Ranked Mandi Comparison",
    table_mandi: "Mandi / Market",
    table_modal: "Gross Price",
    table_deductions: "Freight & Fees",
    table_net: "Net In Pocket",
    table_verdict: "Verdict",

    // Disclaimer & States
    disclaimer_title: "Estimates, not guarantees",
    disclaimer_text: "APMC auction prices fluctuate daily based on morning arrivals, lot quality, and local moisture grade. Freight and APMC deductions are mathematical model estimates based on standard vehicle and market rates.",
    freshness_fresh: "Fresh (0–1d)",
    freshness_moderate: "Moderate (2–3d)",
    freshness_stale: "Stale (>3d)",
    chart_low: "Low Bound",
    chart_likely: "Likely Price",
    chart_high: "High Bound",
    empty_title: "No Trading Records Found",
    empty_text: "No APMC markets reported transactions for this crop in the selected district recently. Please try another crop or nearby district.",
    error_title: "Unable to Connect to Mandi Engine",
    error_server_down: "The Mandi Saathi backend service is offline or unreachable. Please verify your connection or ensure the backend service is running.",

    // Footer
    footer_credit: "Data source: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • Climate, Agriculture & Rural Innovation"
  },
  hi: {
    // Brand
    brand_name: "मंडी साथी",
    brand_tagline: "किसानों के लिए AI मंडी भाव और सही समय सलाहकार",
    
    // Nav
    nav_advisor: "सलाहकार",
    nav_chat: "आवाज़ बातचीत",
    nav_alerts: "अलर्ट",
    nav_proof: "हिसाब-किताब",
    nav_about: "परिचय",
    nav_design: "डिज़ाइन सिस्टम",

    // Common Buttons
    btn_calculate: "सर्वोत्तम बिक्री मंडी खोजें",
    btn_try_demo: "⚡ डेमो आज़माएं (टमाटर • पुणे • 20 क्विंटल)",
    btn_listen: "सलाह सुनें",
    btn_speaking: "बोल रहे हैं...",
    btn_speak: "बोलकर पूछें",
    btn_stop_speaking: "सुन रहे हैं...",
    btn_sell_now: "अभी बेचें",
    btn_wait_store: "रोकें व भंडार करें",
    btn_retry: "पुनः प्रयास करें",
    btn_save: "अलर्ट सेट करें",
    btn_view_details: "विस्तार से देखें",

    // Common Badges & Statuses
    badge_best_net: "अधिकतम शुद्ध लाभ",
    badge_fresh: "ताज़ा भाव",
    badge_unreliable: "पुराना / संदेहास्पद",
    badge_high_conf: "उच्च विश्वसनीयता",
    badge_med_conf: "मध्यम विश्वसनीयता",
    badge_low_conf: "कम विश्वसनीयता",
    data_source_live: "लाइव अगमार्कनेट",
    data_source_snapshot: "90-दिन सत्यापित स्नैपशॉट",
    data_source_sample: "नमूना डेटा",

    // Advisor placeholders & form
    advisor_heading: "स्मार्ट फसल बिक्री सलाहकार",
    advisor_subheading: "परिवहन, मंडी शुल्क और खराबी खर्च घटाने के बाद अपनी जेब में अधिकतम शुद्ध मुनाफा पाने के लिए सही मंडी चुनें।",
    select_crop: "फसल चुनें",
    select_district: "आपका ज़िला",
    input_quantity: "फसल की मात्रा (क्विंटल)",
    select_vehicle: "परिवहन वाहन",
    advanced_title: "उन्नत लागत सेटिंग्स (वैकल्पिक)",
    label_rate_km: "परिवहन दर (₹/किमी)",
    label_fee_pct: "मंडी शुल्क (%)",
    label_spoil_rate: "खराबी नुकसान (%/दिन)",
    label_loading_rate: "हमाली व भराई (₹/क्विंटल)",
    loading_calculating: "मंडी भाव एवं परिवहन खर्च का विश्लेषण जारी है...",

    // Vehicles
    vehicle_tempo: "टेंपो (पिकअप)",
    vehicle_truck: "छोटा ट्रक",
    vehicle_own: "स्वयं का वाहन",

    // Crops
    crop_tomato: "टमाटर",
    crop_onion: "प्याज",
    crop_soybean: "सोयाबीन",
    crop_tur: "तुअर (अरहर)",
    crop_cotton: "कपास",
    crop_potato: "आलू",
    crop_wheat: "गेहूं",

    // Results screen
    results_hero_title: "सर्वश्रेष्ठ अनुशंसित मंडी",
    results_net_return: "जेब में शुद्ध मुनाफा",
    results_total_earnings: "कुल शुद्ध कमाई",
    results_gross_price: "मंडी का थोक भाव",
    results_total_deductions: "कुल खर्च (कटौती)",
    results_gain_vs_nearest: "निकटतम मंडी से अतिरिक्त लाभ",
    results_distance: "दूरी",
    results_travel_time: "यात्रा का समय",
    results_arrival: "मंडी आगमन",
    results_breakeven_title: "समान लाभ सीमा (ब्रेक-इवन भाव)",
    results_forecast_title: "अगले 5 दिनों का भाव गलियारा",
    results_storage_title: "रोकें या अभी बेचें",
    results_comparisons_title: "अन्य मंडियों की तुलना",
    table_mandi: "मंडी / बाज़ार",
    table_modal: "थोक भाव",
    table_deductions: "किराया व खर्च",
    table_net: "शुद्ध मुनाफा",
    table_verdict: "फैसला",

    // Disclaimer & States
    disclaimer_title: "अनुमान, गारंटी नहीं",
    disclaimer_text: "मंडी में भाव दैनिक आवक, माल की गुणवत्ता और नमी के अनुसार बदलते हैं। परिवहन और मंडी शुल्क मानक दरों पर आधारित गणितीय अनुमान हैं।",
    freshness_fresh: "ताज़ा भाव (0-1 दिन)",
    freshness_moderate: "मध्यम (2-3 दिन)",
    freshness_stale: "पुराना (>3 दिन)",
    chart_low: "न्यूनतम सीमा",
    chart_likely: "संभाव्य भाव",
    chart_high: "अधिकतम सीमा",
    empty_title: "कोई व्यापार रिकॉर्ड नहीं मिला",
    empty_text: "चयनित ज़िले में इस फसल के लिए हाल ही में कोई मंडी भाव दर्ज नहीं हुआ है। कृपया अन्य फसल या नजदीकी ज़िला चुनें।",
    error_title: "मंडी सेवा से संपर्क नहीं हो पाया",
    error_server_down: "मंडी साथी बैकएंड सेवा अभी बंद है या संपर्क नहीं हो पा रहा है। कृपया अपना इंटरनेट कनेक्शन जांचें या सर्वर शुरू करें।",

    // Footer
    footer_credit: "डेटा स्रोत: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • जलवायु, कृषि एवं ग्रामीण नवाचार"
  },
  mr: {
    // Brand
    brand_name: "मंडी साथी",
    brand_tagline: "शेतकऱ्यांसाठी AI बाजारभाव आणि विक्री सल्लागार",
    
    // Nav
    nav_advisor: "सल्लागार",
    nav_chat: "बोलून विचारा",
    nav_alerts: "अलर्ट",
    nav_proof: "हिशोब / पुरावा",
    nav_about: "माहिती",
    nav_design: "डिझाइन सिस्टीम",

    // Common Buttons
    btn_calculate: "विक्रीसाठी उत्तम बाजार शोधा",
    btn_try_demo: "⚡ डेमो बघा (टोमॅटो • पुणे • 20 क्विंटल)",
    btn_listen: "सल्ला ऐका",
    btn_speaking: "बोलत आहे...",
    btn_speak: "बोलून सांगा",
    btn_stop_speaking: "ऐकत आहे...",
    btn_sell_now: "आता विका",
    btn_wait_store: "साठवणूक करा",
    btn_retry: "पुन्हा प्रयत्न करा",
    btn_save: "अलर्ट सेव्ह करा",
    btn_view_details: "तपशील बघा",

    // Common Badges & Statuses
    badge_best_net: "सर्वाधिक निव्वळ नफा",
    badge_fresh: "ताजे भाव",
    badge_unreliable: "जुने / संशयास्पद",
    badge_high_conf: "उच्च विश्वासार्हता",
    badge_med_conf: "मध्यम विश्वासार्हता",
    badge_low_conf: "कमी विश्वासार्हता",
    data_source_live: "थेट ॲगमार्कनेट",
    data_source_snapshot: "90-दिवसीय पडताळलेला डेटा",
    data_source_sample: "नमुना डेटा",

    // Advisor placeholders & form
    advisor_heading: "स्मार्ट पीक विक्री सल्लागार",
    advisor_subheading: "वाहतूक खर्च, बाजार समिती फी आणि नासाडी वजा जाता तुमच्या खिशात सर्वाधिक निव्वळ नफा राहण्यासाठी योग्य बाजार निवडा.",
    select_crop: "पीक निवडा",
    select_district: "तुमचा जिल्हा",
    input_quantity: "मालाचे वजन (क्विंटल)",
    select_vehicle: "वाहतूक साधन",
    advanced_title: "प्रगत खर्च सेटिंग्ज (ऐच्छिक)",
    label_rate_km: "वाहतूक दर (₹/किमी)",
    label_fee_pct: "बाजार समिती फी (%)",
    label_spoil_rate: "नासाडी प्रमाण (%/दिवस)",
    label_loading_rate: "हमाली व तोलाई (₹/क्विंटल)",
    loading_calculating: "बाजारभाव आणि वाहतूक खर्चाचे विश्लेषण करत आहे...",

    // Vehicles
    vehicle_tempo: "टॅम्पो (पिकअप)",
    vehicle_truck: "छोटा ट्रक",
    vehicle_own: "स्वतःचे वाहन",

    // Crops
    crop_tomato: "टोमॅटो",
    crop_onion: "कांदा",
    crop_soybean: "सोयाबीन",
    crop_tur: "तूर",
    crop_cotton: "कापूस",
    crop_potato: "बटाटा",
    crop_wheat: "गहू",

    // Results screen
    results_hero_title: "सर्वात फायदेशीर बाजार",
    results_net_return: "खिशात पडणारा निव्वळ नफा",
    results_total_earnings: "एकूण निव्वळ कमाई",
    results_gross_price: "बाजारातील मूळ भाव",
    results_total_deductions: "एकूण खर्च (वजावट)",
    results_gain_vs_nearest: "जवळच्या बाजारापेक्षा जास्तीचा नफा",
    results_distance: "अंतर",
    results_travel_time: "प्रवासाची वेळ",
    results_arrival: "बाजारात पोहोचण्याची वेळ",
    results_breakeven_title: "तोटा-नफा समतोल किंमत (ब्रेक-इव्हन)",
    results_forecast_title: "पुढील 5 दिवसांचा संभाव्य भाव",
    results_storage_title: "साठवणूक करावी का?",
    results_comparisons_title: "इतर बाजारांची तुलना",
    table_mandi: "बाजार समिती",
    table_modal: "मूळ भाव",
    table_deductions: "वाहतूक व फी",
    table_net: "निव्वळ नफा",
    table_verdict: "निर्णय",

    // Disclaimer & States
    disclaimer_title: "अंदाज, हमी नाही",
    disclaimer_text: "बाजार समितीमधील भाव दररोज मालाची आवक, प्रत आणि ओलावा यावर बदलतात. वाहतूक व बाजार फी ही प्रमाणित दरांवर आधारित गणितीय अंदाज आहेत.",
    freshness_fresh: "ताजे भाव (0-1 दिवस)",
    freshness_moderate: "मध्यम (2-3 दिवस)",
    freshness_stale: "जुने (>3 दिवस)",
    chart_low: "किमान मर्यादा",
    chart_likely: "संभाव्य भाव",
    chart_high: "कमाल मर्यादा",
    empty_title: "कोणतेही व्यवहार उपलब्ध नाहीत",
    empty_text: "निवडलेल्या जिल्ह्यात या पिकासाठी अलीकडे कोणतेही बाजारभाव नोंदवले गेले नाहीत. कृपया दुसरे पीक किंवा जवळचा जिल्हा निवडा.",
    error_title: "मंडी सर्व्हरशी संपर्क होऊ शकला नाही",
    error_server_down: "मंडी साथी बॅकएंड सर्व्हिस सध्या बंद आहे किंवा संपर्क होत नाही आहे. कृपया आपले इंटरनेट कनेक्शन तपासा किंवा सर्व्हर सुरू करा.",

    // Footer
    footer_credit: "माहिती स्त्रोत: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • हवामान, कृषी आणि ग्रामीण नवकल्पना"
  }
};

export function getLanguage() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && ['en', 'hi', 'mr'].includes(saved)) {
    return saved;
  }
  return 'en';
}

export function setLanguage(lang) {
  if (['en', 'hi', 'mr'].includes(lang)) {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    window.dispatchEvent(new CustomEvent('languagechange', { detail: { lang } }));
  }
}

export function t(key) {
  const lang = getLanguage();
  return translations[lang]?.[key] || translations['en']?.[key] || key;
}

export function translatePage() {
  const lang = getLanguage();
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (key && translations[lang]?.[key]) {
      el.textContent = translations[lang][key];
    }
  });

  document.querySelectorAll('.lang-btn').forEach((btn) => {
    if (btn.getAttribute('data-lang') === lang) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}
