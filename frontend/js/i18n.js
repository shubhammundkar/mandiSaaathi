// Mandi Saathi - Internationalization System (Marathi, Hindi, English)
// Strict requirement: Default language for new users is Marathi ('mr')

const STORAGE_KEY = 'mandisaathi_lang';

export const translations = {
  // =========================================================================
  // ENGLISH (en)
  // =========================================================================
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
    nav_design: "UI System",

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
    data_source_manual_csv: "Manual Agmarknet CSV",
    data_source_snapshot: "90-Day Verified Snapshot",
    data_source_sample: "Sample data",

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
    results_transport_deduction: "Transport / q",
    results_fees_labor: "Fees & Labor",
    results_batch_qty: "For your batch of quintals",
    results_confidence_high: "High Confidence",
    results_confidence_medium: "Medium Confidence",
    results_confidence_low: "Low Confidence",
    results_auction_today: "Today's Auction",
    results_auction_next: "Auction Day+1",
    results_local_nearest: "Local Nearest Market",
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

    // Chat & Voice
    chat_welcome: "Hello farmer friends! I am **Mandi Saathi**. Ask me about the best mandi to sell your harvest, today's prices, or storage timing. Speak or type below!",
    chat_title: "AI Voice & Text Mandi Advisor",
    chat_subtitle: "Ask in English, Hindi, or Marathi to get instant net return prices and storage advice.",
    chat_input_placeholder: "Type or tap the mic to speak (e.g. 20q tomato Pune)...",
    chat_quick_1: "Where to sell 20q Tomato in Pune?",
    chat_quick_2: "Should I sell or store Onion in Lasalgaon?",
    chat_quick_3: "What is today's tomato price in Pune?",
    chat_quick_4: "Where should I sell 30q Tur in Latur?",
    chat_voice_unsupported: "Voice input is not supported in this browser. You can type your question directly below.",
    chat_listening: "Listening... speak now",
    chat_mute_voice: "Mute voice",
    chat_unmute_voice: "Unmute voice",
    chat_view_in_advisor: "View in Advisor",
    chat_sending: "Analyzing...",
    chat_mic_title: "Voice Search (Marathi / Hindi / English)",
    chat_card_top_choice: "Top Choice",
    chat_card_gross: "Gross",
    chat_card_freight: "Freight",
    chat_card_total_profit: "Total Profit",
    chat_card_distance: "Distance",
    chat_card_current: "Current",
    chat_card_min: "Min",
    chat_card_max: "Max",
    chat_card_date: "Date",
    chat_card_today: "Today",
    chat_error_network: "⚠️ Unable to connect to advisory engine. Please verify the server is running.",
    chat_mic_perm_error: "Please check microphone permissions or type your question below",
    chat_voice_muted_toast: "Voice speech muted",
    chat_voice_unmuted_toast: "Voice speech unmuted",

    // Alerts & Community
    alerts_heading: "Mandi Alerts, Farmer Reports & Data Quality",
    alerts_subheading: "Get daily morning WhatsApp market alerts, log actual crop sales, and inspect real-time reporting coverage across 23 Maharashtra APMC markets.",
    alerts_hero_badge: "Alerts & Community Intelligence",
    alerts_tab_daily: "Daily Alerts & WhatsApp Preview",
    alerts_tab_sold: '"I Sold Today" (Farmer Reports)',
    alerts_tab_quality: "Mandi Data Quality",
    alerts_subscribe_title: "Daily WhatsApp Mandi Alert",
    alerts_subscribe_subtitle: "Receive morning prices, price changes, and best market recommendations directly on your phone every morning at 7:00 AM.",
    alerts_phone_label: "WhatsApp Number (10 digits)",
    alerts_btn_subscribe: "Subscribe to Free Alerts",
    alerts_live_preview_title: "WhatsApp Message Live Preview",
    alerts_sold_title: 'Log Your Sale ("I Sold Today")',
    alerts_sold_subtitle: "Help fellow farmers verify actual ground prices and beat trader misinformation.",
    alerts_sold_price_label: "Actual Price Received (₹/quintal)",
    alerts_sold_btn_submit: "Submit Ground Report",
    alerts_quality_title: "Maharashtra Mandi Data Health & Freshness",

    // Proof & Math
    proof_heading: "Backtest Proof & Calculation Logic",
    proof_subheading: "Strictly leak-free simulation over the historical record across 23 Maharashtra APMC markets.",
    proof_hero_badge: "Empirical Proof & Mathematical Transparency",
    proof_controls_title: "Simulate Historical Backtest",
    proof_controls_subtitle: "Test how Mandi Saathi would have performed on every trading day versus always selling at the nearest local APMC.",
    proof_btn_run_backtest: "Run Historical Simulation",
    proof_stat_avg_extra: "Average Extra / Quintal",
    proof_stat_pct_better: "% Days Better",
    proof_stat_days_tested: "Days Tested",
    proof_math_heading: "Step-by-Step Mathematical Formula",
    proof_worse_days_title: "Transparency: Days When Distant Market Underperformed",

    // About
    about_heading: "About Mandi Saathi",
    about_subheading: "An AI-powered market co-pilot protecting Indian farmers from the headline price trap through transparent net-in-pocket math and sell-timing intelligence.",
    about_hero_badge: "VORTEX 2K26 • Climate, Agriculture & Rural Innovation",
    about_problem_title: "The Problem: The \"Headline Price Trap\"",
    about_how_it_works_title: "How It Works: 4-Step Decision Architecture",

    // Footer
    footer_credit: "Data source: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • Climate, Agriculture & Rural Innovation"
  },

  // =========================================================================
  // HINDI (hi)
  // =========================================================================
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
    data_source_manual_csv: "मैनुअल अगमार्कनेट CSV",
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
    results_transport_deduction: "परिवहन / क्विंटल",
    results_fees_labor: "शुल्क व हमाली",
    results_batch_qty: "आपके माल के लिए",
    results_confidence_high: "उच्च विश्वसनीयता",
    results_confidence_medium: "मध्यम विश्वसनीयता",
    results_confidence_low: "कम विश्वसनीयता",
    results_auction_today: "आज का लिलाव",
    results_auction_next: "कल का लिलाव (Day+1)",
    results_local_nearest: "नजदीकी स्थानीय मंडी",
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

    // Chat & Voice
    chat_welcome: "नमस्ते किसान भाइयो! मैं **मंडी साथी** हूँ। आपको किस फसल का मंडी भाव, सबसे अच्छी बिक्री मंडी या भंडारण सलाह चाहिए? बोलकर या लिखकर पूछें।",
    chat_title: "AI आवाज़ एवं चैट मंडी सलाहकार",
    chat_subtitle: "मराठी, हिंदी या अंग्रेजी में बोलें या लिखें और तुरंत मंडी भाव व बिक्री समय सलाह पाएं।",
    chat_input_placeholder: "लिखें या माइक दबाकर बोलें (उदा: 20q टमाटर पुणे)...",
    chat_quick_1: "पुणे में 20 क्विंटल टमाटर कहाँ बेचूं?",
    chat_quick_2: "लासलगांव में प्याज रखें या बेचें?",
    chat_quick_3: "पुणे में टमाटर का आज का भाव क्या है?",
    chat_quick_4: "लातूर में 30 क्विंटल तूर कहाँ बेचूं?",
    chat_voice_unsupported: "इस ब्राउज़र में आवाज़ पहचान उपलब्ध नहीं है। आप नीचे लिखकर पूछ सकते हैं।",
    chat_listening: "सुन रहे हैं... बोलिए",
    chat_mute_voice: "आवाज़ म्यूट करें",
    chat_unmute_voice: "आवाज़ चालू करें",
    chat_view_in_advisor: "सलाहकार में देखें",
    chat_sending: "जांच रहे हैं...",
    chat_mic_title: "आवाज़ द्वारा पूछें (मराठी / हिंदी / अंग्रेजी)",
    chat_card_top_choice: "सर्वोत्तम विकल्प",
    chat_card_gross: "थोक भाव",
    chat_card_freight: "भाड़ा",
    chat_card_total_profit: "कुल शुद्ध लाभ",
    chat_card_distance: "दूरी",
    chat_card_current: "मौजूदा",
    chat_card_min: "न्यूनतम",
    chat_card_max: "अधिकतम",
    chat_card_date: "दिनांक",
    chat_card_today: "आज",
    chat_error_network: "⚠️ सलाहकार सर्वर से संपर्क नहीं हो सका: कृपया जांचें कि सर्वर चालू है।",
    chat_mic_perm_error: "कृपया माइक्रोफ़ोन अनुमति जांचें या लिखकर पूछें",
    chat_voice_muted_toast: "आवाज़ म्यूट की गई",
    chat_voice_unmuted_toast: "आवाज़ चालू की गई",

    // Alerts & Community
    alerts_heading: "मंडी अलर्ट, किसान रिपोर्ट एवं डेटा गुणवत्ता",
    alerts_subheading: "दैनिक सुबह व्हाट्सएप बाजार भाव अलर्ट प्राप्त करें, अपनी बिक्री दर्ज करें, और 23 एपीएमसी मंडियों की रिपोर्टिंग देखें।",
    alerts_hero_badge: "अलर्ट एवं सामुदायिक सूचना",
    alerts_tab_daily: "दैनिक अलर्ट एवं व्हाट्सएप पूर्वावलोकन",
    alerts_tab_sold: '"मैंने आज बेचा" (किसान रिपोर्ट)',
    alerts_tab_quality: "मंडी डेटा गुणवत्ता",
    alerts_subscribe_title: "दैनिक व्हाट्सएप मंडी भाव अलर्ट",
    alerts_subscribe_subtitle: "प्रतिदिन सुबह 7:00 बजे अपने फोन पर ताज़ा भाव, भाव बदलाव और सर्वोत्तम मंडी सिफारिश प्राप्त करें।",
    alerts_phone_label: "व्हाट्सएप नंबर (10 अंक)",
    alerts_btn_subscribe: "निःशुल्क अलर्ट शुरू करें",
    alerts_live_preview_title: "व्हाट्सएप संदेश पूर्वावलोकन",
    alerts_sold_title: 'अपनी बिक्री दर्ज करें ("मैंने आज बेचा")',
    alerts_sold_subtitle: "अन्य किसान भाइयों को वास्तविक ज़मीनी भाव जानने में मदद करें।",
    alerts_sold_price_label: "वास्तविक प्राप्त भाव (₹/क्विंटल)",
    alerts_sold_btn_submit: "बिक्री रिपोर्ट जमा करें",
    alerts_quality_title: "महाराष्ट्र मंडी डेटा गुणवत्ता एवं ताज़गी",

    // Proof & Math
    proof_heading: "बैकटेस्ट परिणाम एवं गणितीय प्रमाण",
    proof_subheading: "महाराष्ट्र की 23 मंडियों के ऐतिहासिक आंकड़ों पर पूरी तरह पारदर्शी एवं लीक-मुक्त सिमुलेशन।",
    proof_hero_badge: "वास्तविक प्रमाण एवं गणितीय पारदर्शिता",
    proof_controls_title: "ऐतिहासिक बैकटेस्ट सिमुलेशन",
    proof_controls_subtitle: "जांचें कि हमेशा नजदीकी मंडी में बेचने की तुलना में मंडी साथी ने हर कारोबारी दिन कैसा प्रदर्शन किया।",
    proof_btn_run_backtest: "सिमुलेशन चलाएं",
    proof_stat_avg_extra: "औसत अतिरिक्त लाभ / क्विंटल",
    proof_stat_pct_better: "% दिन बेहतर परिणाम",
    proof_stat_days_tested: "परीक्षण किए गए दिन",
    proof_math_heading: "चरणबद्ध गणितीय सूत्र",
    proof_worse_days_title: "पारदर्शिता: वे दिन जब दूर की मंडी में लाभ कम रहा",

    // About
    about_heading: "मंडी साथी के बारे में",
    about_subheading: "किसानों को उच्च थोक भाव के धोखे से बचाने और सही शुद्ध मुनाफे तक पहुंचाने वाला एआई-संचालित कृषि सलाहकार।",
    about_hero_badge: "VORTEX 2K26 • जलवायु, कृषि एवं ग्रामीण नवाचार",
    about_problem_title: "समस्या: \"उच्च थोक भाव का धोखा\" (Headline Price Trap)",
    about_how_it_works_title: "कार्यप्रणाली: 4-चरणीय निर्णय प्रणाली",

    // Footer
    footer_credit: "डेटा स्रोत: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • जलवायु, कृषि एवं ग्रामीण नवाचार"
  },

  // =========================================================================
  // MARATHI (mr) - DEFAULT FOR ALL NEW USERS
  // =========================================================================
  mr: {
    // Brand
    brand_name: "मंडी साथी",
    brand_tagline: "शेतकऱ्यांसाठी AI बाजारभाव आणि विक्री सल्लागार",

    // Nav
    nav_advisor: "सल्लागार",
    nav_chat: "व्हॉइस चॅट",
    nav_alerts: "अलर्ट्स",
    nav_proof: "हिशोब / पुरावा",
    nav_about: "माहिती",
    nav_design: "डिझाइन",

    // Common Buttons
    btn_calculate: "विक्रीसाठी सर्वोत्तम बाजार शोधा",
    btn_try_demo: "⚡ डेमो बघा (टोमॅटो • पुणे • २० क्विंटल)",
    btn_listen: "सल्ला ऐका",
    btn_speaking: "बोलत आहे...",
    btn_speak: "बोलून विचारा",
    btn_stop_speaking: "ऐकत आहे...",
    btn_sell_now: "आजच विका",
    btn_wait_store: "साठवून ठेवा",
    btn_retry: "पुन्हा प्रयत्न करा",
    btn_save: "अलर्ट सेव्ह करा",
    btn_view_details: "तपशील बघा",

    // Common Badges & Statuses
    badge_best_net: "सर्वाधिक निव्वळ नफा",
    badge_fresh: "ताजे भाव",
    badge_unreliable: "जुना / संशयास्पद",
    badge_high_conf: "उच्च विश्वासार्हता",
    badge_med_conf: "मध्यम विश्वासार्हता",
    badge_low_conf: "कमी विश्वासार्हता",
    data_source_live: "थेट ॲगमार्कनेट (Live)",
    data_source_manual_csv: "मॅन्युअल ॲगमार्कनेट CSV",
    data_source_snapshot: "९० दिवसांचा पडताळलेला डेटा",
    data_source_sample: "नमुना डेटा",

    // Advisor placeholders & form
    advisor_heading: "स्मार्ट कृषी विक्री सल्लागार",
    advisor_subheading: "वाहतूक खर्च, बाजार समिती फी आणि नासाडी वजा जाता प्रत्यक्ष खिशात सर्वाधिक निव्वळ नफा राहणारा बाजार शोधा.",
    select_crop: "पीक निवडा",
    select_district: "तुमचा जिल्हा",
    input_quantity: "मालाचे प्रमाण (क्विंटल)",
    select_vehicle: "वाहतूक वाहन",
    advanced_title: "इतर खर्च पर्याय (वैकल्पिक)",
    label_rate_km: "वाहतूक भाडे (₹/किमी)",
    label_fee_pct: "बाजार समिती उपकर / फी (%)",
    label_spoil_rate: "वाटेतील नासाडी (%/दिवस)",
    label_loading_rate: "हमाली व तोलाई (₹/क्विंटल)",
    loading_calculating: "बाजारभाव व वाहतूक खर्चाचे विश्लेषण सुरू आहे...",

    // Vehicles
    vehicle_tempo: "टेम्पो (पिकअप)",
    vehicle_truck: "छोटा ट्रक",
    vehicle_own: "स्वतःचे वाहन",

    // Crops
    crop_tomato: "टोमॅटो",
    crop_onion: "कांदा",
    crop_soybean: "सोयाबीन",
    crop_tur: "तूर (अरहर)",
    crop_cotton: "कापूस",
    crop_potato: "बटाटा",
    crop_wheat: "गहू",

    // Results screen
    results_hero_title: "सर्वात जास्त नफा देणारा बाजार",
    results_net_return: "खिशात पडणारा निव्वळ नफा",
    results_total_earnings: "एकूण निव्वळ उत्पन्न",
    results_gross_price: "मंडीचा सरासरी भाव",
    results_total_deductions: "एकूण खर्च (कपात)",
    results_gain_vs_nearest: "जवळच्या बाजारापेक्षा जास्तीचा नफा",
    results_distance: "अंतर",
    results_travel_time: "प्रवासाची वेळ",
    results_arrival: "लिलाव वेळ",
    results_breakeven_title: "किमान फायदेशीर भाव (Break-Even)",
    results_forecast_title: "पुढील ५ दिवसांचा भाव अंदाज",
    results_storage_title: "साठवणूक की त्वरित विक्री निर्णय",
    results_comparisons_title: "इतर बाजार समित्यांशी तुलना",
    results_transport_deduction: "वाहतूक / क्विंटल",
    results_fees_labor: "शुल्क व हमाली",
    results_batch_qty: "तुमच्या मालासाठी",
    results_confidence_high: "उच्च विश्वासार्हता",
    results_confidence_medium: "मध्यम विश्वासार्हता",
    results_confidence_low: "कमी विश्वासार्हता",
    results_auction_today: "आजचा लिलाव",
    results_auction_next: "उद्याचा लिलाव (Day+1)",
    results_local_nearest: "स्थानिक जवळची बाजार समिती",
    table_mandi: "बाजार समिती",
    table_modal: "सरासरी भाव",
    table_deductions: "वाहतूक व फी",
    table_net: "निव्वळ नफा",
    table_verdict: "शिफारस",

    // Disclaimer & States
    disclaimer_title: "अंदाज आहेत, हमी नाही",
    disclaimer_text: "बाजार समितीमधील भाव सकाळची आवक, मालाचा दर्जा आणि प्रतवारीनुसार बदलतात. वाहतूक आणि बाजार खर्च हे सर्वसामान्य दरांवर आधारित गणितीय अंदाज आहेत.",
    freshness_fresh: "ताजे (०-१ दिवस)",
    freshness_moderate: "मध्यम (२-३ दिवस)",
    freshness_stale: "जुने (>३ दिवस)",
    chart_low: "किमान अंदाज",
    chart_likely: "संभाव्य भाव",
    chart_high: "कमाल अंदाज",
    empty_title: "कोणतीही नोंद आढळली नाही",
    empty_text: "निवडलेल्या जिल्ह्यामध्ये या पिकासाठी आज कोणतीही अधिकृत लिलाव नोंद आढळली नाही. कृपया दुसरे पीक किंवा जवळचा जिल्हा निवडा.",
    error_title: "सल्लागार इंजिनशी संपर्क होऊ शकला नाही",
    error_server_down: "मंडी साथी सर्व्हरशी संपर्क होत नाहीये. कृपया इंटरनेट किंवा बॅकएंड सर्व्हर चालू असल्याचे तपासा.",

    // Chat & Voice
    chat_welcome: "नमस्कार शेतकरी मित्रांनो! मी **मंडी साथी** आहे. तुम्हाला कोणत्या पिकाचे बाजारभाव, विक्रीसाठी सर्वोत्तम मंडी किंवा साठवणुकीचा सल्ला हवा आहे? खालील बटण दाबून बोला किंवा लिहा.",
    chat_title: "AI बोलून विचारा - मंडी सल्लागार",
    chat_subtitle: "मराठी, हिंदी किंवा इंग्रजीत बोला किंवा लिहा आणि अचूक बाजारभाव व विक्री सल्ला मिळवा.",
    chat_input_placeholder: "लिहा किंवा माइक दाबून बोला (उदा: २० क्विंटल टोमॅटो पुणे)...",
    chat_quick_1: "पुण्यात २० क्विंटल टोमॅटो कुठे विकू?",
    chat_quick_2: "लासलगावमध्ये कांदा विकू की ठेवू?",
    chat_quick_3: "पुण्यात टोमॅटोचा आजचा भाव काय आहे?",
    chat_quick_4: "लातूरमध्ये ३० क्विंटल तूर कुठे विकू?",
    chat_voice_unsupported: "या ब्राउझरमध्ये व्हॉइस इनपुट समर्थित नाही. तुम्ही खाली थेट टाइप करू शकता.",
    chat_listening: "ऐकत आहे... बोला",
    chat_mute_voice: "आवाज बंद करा",
    chat_unmute_voice: "आवाज सुरू करा",
    chat_view_in_advisor: "सल्लागारामध्ये बघा",
    chat_sending: "विश्लेषण सुरू आहे...",
    chat_mic_title: "बोलून विचारा (मराठी / हिंदी / इंग्रजी)",
    chat_card_top_choice: "सर्वोत्कृष्ट पर्याय",
    chat_card_gross: "सरासरी भाव",
    chat_card_freight: "वाहतूक खर्च",
    chat_card_total_profit: "एकूण निव्वळ नफा",
    chat_card_distance: "अंतर",
    chat_card_current: "चालू भाव",
    chat_card_min: "किमान",
    chat_card_max: "कमाल",
    chat_card_date: "दिनांक",
    chat_card_today: "आज",
    chat_error_network: "⚠️ सल्लागार सर्व्हरशी संपर्क होऊ शकला नाही: कृपया सर्व्हर सुरू असल्याचे तपासा.",
    chat_mic_perm_error: "कृपया मायक्रोफोन परवानगी तपासा किंवा टाईप करा",
    chat_voice_muted_toast: "आवाज बंद केला",
    chat_voice_unmuted_toast: "आवाज सुरू केला",

    // Alerts & Community
    alerts_heading: "बाजारभाव अलर्ट, शेतकरी नोंदी व डेटा गुणवत्ता",
    alerts_subheading: "दररोज सकाळी व्हॉट्सॲपवर बाजारभाव मिळवा, स्वतःचे विक्री भाव नोंदवा आणि २३ बाजार समित्यांची अचूक आकडेवारी तपासा.",
    alerts_hero_badge: "बाजारभाव अलर्ट व शेतकरी समूह माहिती",
    alerts_tab_daily: "दैनिक अलर्ट व व्हॉट्सॲप मेसेज",
    alerts_tab_sold: '"मी आज विकले" (शेतकरी नोंदी)',
    alerts_tab_quality: "बाजार डेटा गुणवत्ता",
    alerts_subscribe_title: "दररोज सकाळी व्हॉट्सॲपवर बाजारभाव अलर्ट",
    alerts_subscribe_subtitle: "दररोज सकाळी ७:०० वाजता ताज्या लिलावाचे भाव आणि सर्वोत्तम बाजाराची शिफारस थेट तुमच्या व्हॉट्सॲपवर मिळवा.",
    alerts_phone_label: "व्हॉट्सॲप नंबर (१० अंक)",
    alerts_btn_subscribe: "मोफत अलर्ट सुरू करा",
    alerts_live_preview_title: "व्हॉट्सॲप मेसेज प्रत्यक्ष पूर्वावलोकन",
    alerts_sold_title: 'स्वतःची विक्री नोंदवा ("मी आज विकले")',
    alerts_sold_subtitle: "इतर शेतकरी बांधवांना प्रत्यक्ष मिळालेला खरा भाव कळावा यासाठी नोंद करा.",
    alerts_sold_price_label: "प्रत्यक्ष मिळालेला भाव (₹/क्विंटल)",
    alerts_sold_btn_submit: "विक्रीची नोंद सबमिट करा",
    alerts_quality_title: "महाराष्ट्रातील २३ बाजार समित्यांची डेटा अचूकता व ताजेपणा",

    // Proof & Math
    proof_heading: "बॅकटेस्ट पडताळणी व हिशोबाचा पुरावा",
    proof_subheading: "महाराष्ट्रातील २३ बाजार समित्यांच्या ९० दिवसांच्या प्रत्यक्ष व्यवहारांवर आधारित पारदर्शक व वस्तुनिष्ठ पडताळणी.",
    proof_hero_badge: "वस्तुनिष्ठ पडताळणी व हिशोबाचा पुरावा",
    proof_controls_title: "ऐतिहासिक आकडेवारीवर आधारित पडताळणी",
    proof_controls_subtitle: "नेहमी जवळच्या बाजारात विक्री करण्याऐवजी मंडी साथीच्या सल्ल्यानुसार विक्री केली असती तर किती नफा झाला असता ते तपासा.",
    proof_btn_run_backtest: "पडताळणी सिमुलेशन चालवा",
    proof_stat_avg_extra: "सरासरी अतिरिक्त नफा / क्विंटल",
    proof_stat_pct_better: "% दिवस अधिक फायदेशीर",
    proof_stat_days_tested: "तपासलेले दिवस",
    proof_math_heading: "टप्प्याटप्प्याने हिशोबाचे गणितीय सूत्र",
    proof_worse_days_title: "पारदर्शकता: ज्या दिवशी लांबच्या बाजारात जाणे तोट्याचे ठरले",

    // About
    about_heading: "मंडी साथी बद्दल",
    about_subheading: "शेतकऱ्यांना लांबच्या बाजारातील खोट्या दरांच्या फसवणुकीपासून वाचवून खऱ्या निव्वळ नफ्याची हमी देणारा एआय तंत्रज्ञान सल्लागार.",
    about_hero_badge: "VORTEX 2K26 • हवामान, कृषी आणि ग्रामीण नवकल्पना",
    about_problem_title: "समस्या: लांबच्या बाजारातील \"खोट्या जास्त भावाचा सापळा\"",
    about_how_it_works_title: "कार्यप्रणाली: ४-टप्प्यांची एआय निर्णय प्रणाली",

    // Footer
    footer_credit: "माहिती स्त्रोत: Agmarknet (agmarknet.gov.in) via data.gov.in",
    footer_hackathon: "VORTEX 2K26 • हवामान, कृषी आणि ग्रामीण नवकल्पना"
  }
};

/**
 * Returns current language code ('mr', 'hi', or 'en').
 * Defaults strictly to 'mr' (Marathi) for new users.
 */
export function getLanguage() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && ['en', 'hi', 'mr'].includes(saved)) {
    return saved;
  }
  return 'mr'; // Marathi default for new users
}

export const getCurrentLanguage = getLanguage;

/**
 * Persists user's language selection and emits languagechange event.
 */
export function setLanguage(lang) {
  if (['en', 'hi', 'mr'].includes(lang)) {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    translatePage();
    window.dispatchEvent(new CustomEvent('languagechange', { detail: { lang } }));
  }
}

/**
 * Retrieves localized string for given key. Falls back to Marathi, then English, then key itself.
 */
export function t(key) {
  const lang = getLanguage();
  return translations[lang]?.[key] || translations['mr']?.[key] || translations['en']?.[key] || key;
}

/**
 * Updates all DOM elements with i18n data attributes across active page:
 * - data-i18n: updates element textContent
 * - data-i18n-placeholder: updates input placeholder
 * - data-i18n-title: updates element title tooltip
 * - data-i18n-aria-label: updates aria-label
 * - .lang-btn: updates active state
 */
export function translatePage() {
  const lang = getLanguage();

  // Text content
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (key && translations[lang]?.[key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Input Placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (key && translations[lang]?.[key]) {
      el.placeholder = translations[lang][key];
    }
  });

  // Tooltips & Titles
  document.querySelectorAll('[data-i18n-title]').forEach((el) => {
    const key = el.getAttribute('data-i18n-title');
    if (key && translations[lang]?.[key]) {
      el.title = translations[lang][key];
    }
  });

  // Accessibility Aria-Labels
  document.querySelectorAll('[data-i18n-aria-label]').forEach((el) => {
    const key = el.getAttribute('data-i18n-aria-label');
    if (key && translations[lang]?.[key]) {
      el.setAttribute('aria-label', translations[lang][key]);
    }
  });

  // Update switcher buttons
  document.querySelectorAll('.lang-btn').forEach((btn) => {
    if (btn.getAttribute('data-lang') === lang) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}
