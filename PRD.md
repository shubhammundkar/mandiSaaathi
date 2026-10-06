# Mandi Saathi — Product Requirements Document (PRD)

**Project Name:** Mandi Saathi (मंडी साथी)  
**Subtitle:** AI Mandi Price & Sell-Timing Advisor with Regional Voice Assistant  
**Event:** VORTEX 2K26 – Global AI Innovation Hackathon  
**Organizer:** Innovation Hacks (`innovationhacks.in`)  
**Track / Theme:** Climate, Agriculture & Rural Innovation (AI for Bharat)  
**Target Submission Window:** 11 October 2026, 9:17 AM IST – 15 October 2026, 11:17 PM IST  
**Document Status:** Complete & Approved (Version 1.0)  

---

## 1. Executive Summary & Vision

### 1.1 The Core Problem
In India, small and marginal farmers typically sell their harvested produce at the nearest Agricultural Produce Market Committee (APMC) mandi out of habit, convenience, or sheer lack of market visibility. However:
- **Price Disparities:** Mandi prices across neighboring districts often differ by ₹200 to ₹800+ per quintal on the exact same day.
- **Hidden Cost Traps:** A distant mandi boasting a higher gross price often yields a *lower net profit* once round-trip diesel, tempo hire, loading/unloading levies, market commission, and transit spoilage are subtracted.
- **Arrival Cutoff & Timing Blindness:** Most mandis conduct auctions early in the morning (typically concluding by 11:00 AM – 12:00 PM). A farmer departing late afternoon often arrives after auction closure, facing distress sales or unplanned overnight holding costs.
- **Information Accessibility Barrier:** Existing portals (such as eNAM and Agmarknet) present dense, tabular reports primarily in English with no actionable decision advisory and zero regional voice capability.

### 1.2 The Solution: Mandi Saathi
**Mandi Saathi** is an intelligent decision engine built specifically for Bharat's farmers. Rather than presenting raw, uncontextualized price tables, Mandi Saathi answers two vital economic questions:
1. **WHERE should I sell?** — Evaluates all mandis within a practical radius and ranks them by **True Net Return** (Gross Price minus Transit, Labor, Commission, and Transit Spoilage).
2. **WHEN should I sell?** — Delivers a 1 to 5-day low/likely/high price outlook with honest confidence bands, advising whether to sell immediately or store (for storage-viable commodities).

All recommendations are accessible via an intuitive pastel mobile-first UI and a **multilingual voice assistant** supporting **Marathi (मराठी)**, **Hindi (हिन्दी)**, and **English**.

---

## 2. Target Audience & User Personas

| Persona | Profile & Behavior | Core Pain Point | How Mandi Saathi Solves It |
| :--- | :--- | :--- | :--- |
| **Babanrao (Smallholder Farmer)** | 2.5 acres in Shirur, Pune. Grows Tomatoes and Onions. Relies on local tempo transport. Prefers spoken Marathi. | Loses up to 25% of profit due to tomato spoilage and selling at Pune mandi when Narayangaon or Khed had higher net margins. | One-tap voice query in Marathi (`"माझा २० क्विंटल टोमॅटो कुठे विकू?"`) returns top net-return mandi, considering tomato perishability and tempo travel time. |
| **Sunita Tai (Soybean / Tur Cultivator)** | 4 acres in Latur. Harvests 35 quintals of Soybean. Has access to local dry storage / warehouse. | Undecided whether to sell today during peak harvest glut or hold stock for 10–14 days. | Accesses the "Sell or Store" forecast badge and historical backtest proof to verify if expected price recovery exceeds storage decay cost. |
| **Hackathon Evaluator / Judge** | Evaluates innovative AI impact, technical execution, and user experience within a 2-minute review window. | Needs instant proof without configuring API keys, entering phone numbers, or signing up. | Dedicated **"Try Demo"** button pre-fills sample scenario (Tomato + Pune + 20 quintals) with 1-click end-to-end visualization, data freshness score, and backtest metrics. |

---

## 3. Product Goals & Success Metrics

### 3.1 Business & Impact Goals
- **Empower Marginal Farmers:** Increase average net realization by **₹150 to ₹350 per quintal** through optimized market selection.
- **Data Honesty & Transparency:** Eliminate "hallucinated AI advice" by computing mathematically grounded net returns backed by real Agmarknet records, displaying explicit confidence ratings and freshness timestamps.
- **Zero-Barrier Accessibility:** Ensure 100% functionality without mandatory user registration, complex passwords, or high-bandwidth app store downloads.

### 3.2 Hackathon Evaluation Criteria Alignment
- **Innovation & Originality:** Net-return equation, arrival-day cutoff logic, break-even price thresholding, and voice-driven regional interface.
- **Technical Rigor:** Automated resilient data ingestion with offline CSV snapshots, SQLite indexing, leak-free historical backtesting, and fallback NLP.
- **Real-World Usability:** Lightweight HTML5/CSS3/Vanilla JS PWA-ready architecture optimized for sub-₹10,000 Android phones on 3G/4G rural networks (tested at 360px viewport).
- **Presentation & Demo Readiness:** Single-URL deployment (Render/Railway), one-click demo auto-fill, and pre-recorded offline video backup.

---

## 4. Comprehensive Feature Specifications

### Feature 1: Multi-Mandi Market Comparison
- **Description:** Real-time query across all functional mandis in the state/district for the selected commodity.
- **Data Displayed:** Mandi Name, District, Min Price, Modal Price, Max Price (₹/quintal), Distance (km), Estimated Travel Time (hrs), and Days Since Last Reported.
- **Rule:** Never display a single deterministic price as absolute truth; always provide the (Min – Modal – Max) trading range.

### Feature 2: Net-Return Ranking Engine
- **Description:** Ranks candidate mandis strictly by calculated **Net Return per Quintal**, not gross modal price.
- **Formula:**
  $$\text{Net Return} = P_{\text{expected}} - (\text{Transport} + \text{Handling} + \text{Commission} + \text{Transit Spoilage})$$
- **Breakdown Cards:** Highlights the top-ranked mandi with explicit earnings uplift compared to the nearest geographical mandi.

### Feature 3: Arrival-Day & Auction Cutoff Logic
- **Description:** Adjusts the evaluated selling price based on the farmer's estimated arrival time.
- **Mechanism:**
  - Standard APMC morning auction cutoff is configured at 12:00 PM (configurable in `config.yaml`).
  - If `Departure Time + Transit Duration > 12:00 PM`, the system flags Day+1 arrival.
  - Automatically factors in Day+1 forecasted price and applies overnight holding/vehicle waiting charges.

### Feature 4: Break-Even Price Thresholding
- **Description:** For every distant mandi evaluated, calculates the exact minimum price required to justify travelling past the nearest mandi.
- **User Facing Message:** *"Worth the trip to Nashik only if the market price exceeds ₹2,420/quintal (covers extra ₹180 transport and ₹40 handling)."*

### Feature 5: Short-Term Price Outlook (1–5 Days)
- **Description:** Time-series projection generating Low, Likely, and High price corridors over a 5-day horizon using moving averages, momentum trends, and weekly day-of-week seasonality.
- **Visual Presentation:** Interactive Chart.js range corridor highlighting optimistic, pessimistic, and expected trajectories with an explicit confidence badge.

### Feature 6: Sell-or-Store Decision Advisory
- **Description:** Specialized recommendation engine for storage-resilient crops (Onion, Soybean, Tur/Pigeon Pea, Potato, Wheat).
- **Decision Engine Output:**
  - `SELL NOW`: If 5-day forecast trend is negative or expected price gain is lower than daily storage cost + weight loss.
  - `STORE (Wait 3–7 Days)`: If projected upward swing significantly exceeds cumulative holding costs.
  - `INSUFFICIENT DATA`: Triggered when mandi reporting frequency fails reliability thresholds.

### Feature 7: Data Freshness & Confidence Scoring
- **Scoring Rubric:**
  - **High Confidence (Green):** Updated today or yesterday (0–1 day lag) with $\ge 20$ trading records in the past 30 days.
  - **Medium Confidence (Yellow):** Updated 2–3 days ago; cautionary badge shown.
  - **Low Confidence / Stale (Red):** $> 3$ days without report. Excluded from top ranking or highlighted with explicit warning.
- **Data Integrity:** Strict rule against fabricating or imputing missing prices.

### Feature 8: Trilingual Regional Voice Assistant
- **Input:** Web Speech API `SpeechRecognition` supporting Marathi (`mr-IN`), Hindi (`hi-IN`), and Indian English (`en-IN`).
- **Processing:** Natural speech transcription parsed for crop entities, quantity in quintals, and location.
- **Output:** Native `speechSynthesis` playback summarizing the best mandi and net earnings, accompanied by a mute/unmute control.

### Feature 9: Conversational WhatsApp-Style Chat UI
- **Design:** Familiar messaging layout with green speech bubbles, quick-reply chips (e.g., *"Today's Tomato Price"*, *"Should I hold Soybean?"*), voice mic button, and rich inline response cards.
- **Offline / Rule Fallback:** Backed by Gemini API with a robust multilingual regex parser fallback ensuring zero downtime even without an active AI key.

### Feature 10: Morning Price Alerts & SMS/WhatsApp Preview
- **Description:** Allows farmers to configure crop and district subscriptions.
- **Functionality:** In-browser notification preview simulating daily morning briefing at 07:00 AM IST summarizing top 3 recommended mandis and day trend.

### Feature 11: Farmer-Reported "Crowd Price" Verification
- **Description:** Crowdsourced modal form (*"I Sold Today"* / *"मी आज विकले"*) allowing farmers to log actual realized mandi rates.
- **Verification Rule:** Crowd submissions are tagged with a distinct `[Farmer Verified]` badge and kept separate from official Agmarknet records to fill reporting blind spots.

### Feature 12: Data Quality & Coverage Health Dashboard
- **Public Audit Screen:** Displays total monitored mandis across Maharashtra, 30-day reporting density, latest sync timestamps, and currently active data source (`Live Agmarknet`, `Offline CSV Snapshot`, or `Sample Simulation`).

### Feature 13: 90-Day Leak-Free Backtest & Proof Dashboard
- **Mathematical Validation:** Runs a simulated 90-day backtest of historical trading days comparing Mandi Saathi's strategy against the baseline "Sell at Nearest Mandi" behavior.
- **Transparent Honesty:** Displays Average Net Profit Gain (₹/quintal), Win Rate percentage, and openly lists the worst-performing days where market volatility caused lower returns.

### Feature 14: Multilingual Internationalization (i18n)
- **Supported Languages:** English, Hindi (हिन्दी), Marathi (मराठी).
- **Architecture:** Zero-dependency static JSON dictionary (`i18n.js`). Active language persisted in browser `localStorage`. Instant UI re-render without page reload.

### Feature 15: One-Click Evaluator "Try Demo"
- **Purpose:** Enables hackathon judges to verify end-to-end execution in under 5 seconds.
- **Behavior:** Auto-fills crop as **Tomato**, location as **Pune**, quantity as **20 quintals**, and vehicle as **Tempo**, immediately rendering the ranked results, map cards, price outlook chart, and speech prompt.

---

## 5. Scope & Crop Coverage (Phase 1–2 Target)

### 5.1 Geographic Scope
- **State:** Maharashtra, India
- **Primary Districts:** Pune, Nashik, Ahmednagar, Solapur, Latur, Jalgaon, Kolhapur, Nagpur, Chhatrapati Sambhajinagar (Aurangabad), Amravati.

### 5.2 Commodity Coverage
1. **Tomato (टोमॅटो)** — High perishability, acute daily volatility.
2. **Onion (कांदा)** — Moderate perishability, strategic seasonal storage.
3. **Soybean (सोयाबीन)** — Non-perishable oilseed, high market volume.
4. **Tur / Arhar (तूर)** — Non-perishable pulse, major MSP and open-market divergence.
5. **Cotton (कापूस)** — High cash crop value, district cluster variation.
6. **Potato (बटाटा)** — Cold-storage sensitive staple.
7. **Wheat (गहू)** — High volume grain staple.

---

## 6. Non-Functional Requirements (NFRs)

| Category | Requirement Specification |
| :--- | :--- |
| **Performance** | API response time $< 300\text{ ms}$ for `/api/advise`. Static frontend load time $< 1.5\text{ s}$ on 3G connections. |
| **Mobile Responsiveness** | Fully fluid layout supporting viewports down to 360px width. Minimum touch-target size of $44\times 44\text{ px}$. |
| **Zero Authentication** | Full public access without login, phone OTP, or account creation for friction-free judge evaluation. |
| **Reliability & Fallbacks** | If live Agmarknet connectivity fails, system seamlessly falls back to local `agmarknet_maharashtra_snapshot.csv`. If Gemini API fails, fallback to regex NLP parser. |
| **Privacy & Security** | No recording of user voice streams on remote servers (Web Speech runs locally in-browser). All backend API keys restricted to `.env`. |
| **Transparency & Attribution** | Agmarknet data attribution clearly displayed across footer and README: *"Data source: Agmarknet (agmarknet.gov.in), Directorate of Marketing & Inspection (DMI)"*. |
