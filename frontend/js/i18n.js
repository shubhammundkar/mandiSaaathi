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
    btn_calculate: "Find Best Mandi",
    btn_listen: "Listen (Voice)",
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

    // Advisor placeholders
    advisor_heading: "Smart Crop Sell Advisor",
    advisor_subheading: "Find out where and when to sell for the maximum net profit in your pocket.",
    select_crop: "Select Crop",
    select_district: "Your Location (District)",
    input_quantity: "Harvest Quantity (Quintals)",
    select_vehicle: "Transport Vehicle",

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
    btn_calculate: "सर्वोत्तम मंडी खोजें",
    btn_listen: "सुनें (आवाज़)",
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

    // Advisor placeholders
    advisor_heading: "स्मार्ट फसल बिक्री सलाहकार",
    advisor_subheading: "जानिए कहाँ और कब बेचने पर आपकी जेब में सबसे ज्यादा शुद्ध मुनाफा बचेगा।",
    select_crop: "फसल चुनें",
    select_district: "आपका ज़िला",
    input_quantity: "फसल की मात्रा (क्विंटल)",
    select_vehicle: "परिवहन वाहन",

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
    btn_calculate: "उत्तम बाजार शोधा",
    btn_listen: "ऐका (आवाज)",
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

    // Advisor placeholders
    advisor_heading: "स्मार्ट पीक विक्री सल्लागार",
    advisor_subheading: "तुमच्या खिशात सर्वाधिक निव्वळ नफा राहण्यासाठी कुठे आणि कधी विकायचे ते जाणून घ्या.",
    select_crop: "पीक निवडा",
    select_district: "तुमचा जिल्हा",
    input_quantity: "मालाचे वजन (क्विंटल)",
    select_vehicle: "वाहतूक साधन",

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
  // Update all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (key && translations[lang]?.[key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Update active state of language switcher buttons
  document.querySelectorAll('.lang-btn').forEach((btn) => {
    if (btn.getAttribute('data-lang') === lang) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}
