# Mandi Saathi (मंडी साथी) 🌾

> **AI Price & Sell-Timing Advisor for Indian Smallholder Farmers**  
> Built for **VORTEX 2K26 Hackathon** • *Theme: Climate, Agriculture & Rural Innovation*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 50 Passed](https://img.shields.io/badge/tests-50%20passed-brightgreen.svg)](#testing)
[![Data: Agmarknet](https://img.shields.io/badge/data-agmarknet.gov.in-orange.svg)](#data-source--attribution)

---

## 🌐 Live Application & Demo

- **Live URL**: [https://mandisaathi.onrender.com](https://mandisaathi.onrender.com) *(Deployment Placeholder)*
- **GitHub Repository**: [https://github.com/shubhammundkar/mandiSaaathi](https://github.com/shubhammundkar/mandiSaaathi)

---

## 📸 Screenshots & UI Previews

*(Screenshots Placeholder)*

| 1. Smart Crop Sell Advisor | 2. AI Voice & Multilingual Chat |
| :---: | :---: |
| ![Smart Advisor Preview](https://via.placeholder.com/600x380/E8F5E9/2E7D32?text=Smart+Advisor+Net+Return+Ranking) | ![Voice Chat Preview](https://via.placeholder.com/600x380/E8F5E9/2E7D32?text=Multilingual+Voice+Chat+in+MR/HI/EN) |
| *Calculates true net returns after freight, fees & spoilage* | *Voice recognition and speech synthesis in Marathi, Hindi & English* |

| 3. WhatsApp Morning Alerts & Farmer Feed | 4. 90-Day Empirical Proof & Alpha Chart |
| :---: | :---: |
| ![Alerts & Reports Preview](https://via.placeholder.com/600x380/FFF8E1/E65100?text=WhatsApp+Morning+Alert+Preview) | ![Backtest Proof Preview](https://via.placeholder.com/600x380/E3F1FB/0277BD?text=90-Day+Cumulative+Returns+Chart) |
| *Authentic WhatsApp alerts & crowd-sourced transaction logs* | *Chart.js cumulative alpha curve with transparent worse-days disclosure* |

---

## 🚨 The Problem: The "Headline Price Trap"

Smallholder farmers across rural India typically check wholesale mandi prices through basic apps or word-of-mouth. When a distant APMC 120 km away advertises a gross price of **₹2,200/quintal** while their local market offers **₹1,800/quintal**, farmers see a tempting **₹400/quintal windfall**.

### The Hidden Financial Reality:
For a standard 20-quintal pickup load:
- **Roundtrip Freight**: 240 km × ₹14/km = ₹3,360 (**₹168/q**)
- **Loading & Hamali Labor**: ₹30/q (**₹30/q**)
- **APMC Market Cess & Tax**: 1.5% of gross trade value (**₹33/q**)
- **Transit Spoilage**: Heat and vibration decay over a 3.5-hour journey (**₹50/q**)
- **Total Deductions**: **₹281/quintal**

If highway congestion delays arrival past the **12:00 PM APMC auction cutoff**, the farmer faces distressed secondary sales or overnight holding expenses. The apparent ₹400 windfall evaporates into a **crushing net loss**.

**Mandi Saathi eliminates this trap** by calculating the true **Net-in-Pocket Return** before the farmer starts their engine.

---

## ✨ Key Features

1. **True Net-in-Pocket Optimization Engine**:
   - Incorporates realistic road distances using Haversine formulas with a 1.25 rural winding factor.
   - Deducts vehicle-specific roundtrip freight (Tempo ₹14/km, Mini-Truck ₹22/km, Own Vehicle ₹9/km), handling fees, statutory APMC market cess (1.05%), and hourly perishable decay.
   - Computes the exact **break-even price threshold** required before traveling to a distant market.

2. **Auction Cutoff Feasibility**:
   - Tracks morning auction cutoffs (typically 12:00 PM) across all 23 monitored Maharashtra mandis.
   - Warns when travel duration exceeds departure hours and automatically applies conservative next-day holding haircuts.

3. **5-Day Price Corridor & Sell/Store Decision**:
   - Forecasts Low, Likely, and High price corridors using time-series modeling (Holt-Winters / ARIMA).
   - Delivers clear economic verdicts: *"Sell now"* vs. *"Wait & Store"* based on whether projected price appreciation exceeds monthly warehouse storage costs.

4. **Multilingual Voice & NLP Chat Advisor**:
   - Web Speech API voice input (`SpeechRecognition`) and audio playback (`speechSynthesis`) supporting Marathi (`mr-IN`), Hindi (`hi-IN`), and English (`en-IN`).
   - Uses Google Gemini REST API when `GEMINI_API_KEY` is configured; automatically falls back to an offline rule-based parser with dialect synonyms (*kanda/pyaaz = onion, tamatar = tomato, quintal/kwintal*).
   - Inline WhatsApp-styled message bubbles and mini advisory cards.

5. **Morning WhatsApp Alert Previews**:
   - Generates authentic morning market updates formatted with WhatsApp markdown (`*bold*`, emojis).
   - One-click copy to clipboard and direct WhatsApp Web sharing (`https://api.whatsapp.com/send?text=...`).

6. **"I Sold Today" Farmer Community Reports (Isolated Feed)**:
   - Allows farmers to log actual transaction prices with sanity checks ($0 < \text{price} \le ₹50,000/\text{q}$, $0 < \text{quantity} \le 10,000\text{q}$).
   - Displayed with an amber **`🧑‍🌾 Farmer reported`** badge.
   - **Strict Data Isolation Guarantee**: Farmer reports are persisted exclusively in `farmer_reports` and **never mixed into official Agmarknet arrivals**.

7. **Mandi Data Quality & 30-Day Coverage Monitor**:
   - Evaluates all 23 monitored APMC markets for last reported arrival dates, 30-day coverage percentages, and confidence badges (`HIGH`/Green, `MEDIUM`/Yellow, `LOW`/Red).
   - Verifies verified latitude/longitude coordinates (excluding unlocated mandis from recommendations).

8. **Empirical 90-Day Backtest Proof**:
   - Strictly leak-free simulation: trading decisions on Day $T$ use only data reported prior to Day $T$.
   - Renders interactive Chart.js cumulative net return curves comparing Mandi Saathi against the nearest local APMC.
   - Transparently discloses **worse days** where market clearing prices inverted intra-day.
   - Interactive 6-step formula walkthrough for representative demo trips.

---

## 🏗️ System Architecture

```
                               ┌───────────────────────────────────────────────┐
                               │           Farmer Client (Browser / PWA)       │
                               │  - Vanilla ES6 Modules (Zero Build Tools)     │
                               │  - Hash Router (#/advisor, #/chat, #/alerts)  │
                               │  - Web Speech API (Voice in mr-IN/hi-IN/en-IN)│
                               │  - Chart.js 4.4 + Lucide Icons 0.344          │
                               └──────────────────────┬────────────────────────┘
                                                      │ HTTP / JSON
                                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FastAPI Backend (Python 3.11+)                            │
├─────────────────────────┬───────────────────────────┬────────────────────────────────────────┤
│     Advisory Engine     │      Forecast Engine      │            NLP / Chat Engine           │
│  - Haversine + 1.25 W   │  - Holt-Winters / ARIMA   │  - Gemini REST API (when key present)  │
│  - Roundtrip Freight    │  - 5-Day Price Corridors  │  - Deterministic Fallback Parser       │
│  - APMC Cess + Spoilage │  - Sell vs Store Verdict  │  - Vernacular Dialects & Synonyms      │
├─────────────────────────┴───────────────────────────┴────────────────────────────────────────┤
│                                  Alerts & Quality Service                                    │
│  - WhatsApp Message Generator   - Sanity-Checked Community Reports   - 30-Day Coverage Audit │
└──────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                               │
                                               ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SQLite Database (WAL Mode)                                 │
│  - mandi_prices (Agmarknet official wholesale records; is_sample=0 or is_sample=1)           │
│  - farmer_reports (Crowd-sourced transactions; strictly segregated)                          │
│  - alert_subscriptions (Notification preferences per crop and district)                      │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Local Setup & Installation

### Prerequisites
- Python 3.10+ (Python 3.11+ recommended)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/shubhammundkar/mandiSaaathi.git
cd mandiSaaathi
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Available environment variables:
| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Web server listening port |
| `HOST` | `127.0.0.1` | Web server listening host (`0.0.0.0` for containers) |
| `DATABASE_PATH` | `data/mandisaathi.db` | SQLite database file location |
| `GEMINI_API_KEY` | `""` *(empty)* | Optional Google Gemini API key for conversational NLP |

*(Note: Mandi Saathi works out-of-the-box with zero configuration using its deterministic parser!)*

### 5. Launch the Server
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at **`http://localhost:8000`**. On startup, the application automatically builds the SQLite database schema and ingests verified snapshot data if empty.

---

## 🧪 Automated Testing

Run the full pytest test suite:
```bash
python -m pytest -v
```

The test suite covers:
- Advisory calculation engine & cutoff logic (`test_advisory.py`)
- WhatsApp morning previews, farmer report isolation & data quality (`test_alerts_and_community.py`)
- Strictly leak-free 90-day simulation engine (`test_backtest.py`)
- Holt-Winters price forecasting corridors (`test_forecast.py`)
- Multilingual NLP parsing in English, Hindi, and Marathi (`test_nlp.py`)
- Startup database hydration & price queries (`test_prices_and_startup.py`)
- Proof and About page mathematical compliance (`test_proof_and_about.py`)
- Polish, accessibility & mobile responsiveness (`test_polish_and_mobile.py`)

---

## 🚀 Deployment (Render / Railway)

Mandi Saathi includes pre-configured deployment manifests for **Render** (`render.yaml`) and **Railway** (`railway.json`, `Procfile`).

### Render Deployment
1. Connect your repository to [Render](https://render.com).
2. Create a new **Web Service**:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/health`
3. Optional Environment Variables:
   - `GEMINI_API_KEY`: *(Your optional Gemini API key)*
4. Click **Deploy**. On initial startup, the container automatically initializes `mandisaathi.db` from `data/sample_history.csv` or `agmarknet_maharashtra_snapshot.csv`.

### Railway Deployment
1. Deploy directly via Railway dashboard or CLI:
   ```bash
   railway up
   ```
2. The provided `Procfile` and `railway.json` will configure the `0.0.0.0:$PORT` binding and `/api/health` check automatically.

---

## 📊 Data Source & Attribution

- **Mandatory Attribution**:
  > **Data source: Agmarknet (agmarknet.gov.in)**  
  > Ingested via the Open Government Data (OGD) Platform India ([data.gov.in](https://data.gov.in)).
- **Resource ID**: `9ef84268-d588-465a-a308-a864a43d0070`
- **Coverage**: 23 Agricultural Produce Market Committees (APMCs) across Maharashtra (*Pune, Nashik, Pimpalgaon, Lasalgaon, Baramati, Sangamner, Latur, Solapur, Akola, Kolhapur, etc.*).
- **Manual CSV Ingestion**:
  ```bash
  python scripts/load_manual_csv.py path/to/agmarknet_download.csv
  ```
  Appends real government rows with `source='manual_csv'` and `is_sample=0`.

---

## ⚠️ Real-World Limitations

1. **Intra-Day Auction Spread**: Physical APMC bidding takes place between 6:00 AM and 12:00 PM. Clearing prices fluctuate with morning lot arrivals, crate sorting, and moisture content.
2. **Transport Rate Negotiations**: Freight is modeled on benchmark rural hiring rates (Tempo ₹14/km). Actual rates with local driver unions may vary based on fuel prices, return-cargo availability, and tolls.
3. **Mandi Reporting Latency**: Some rural sub-yards report arrivals with a 24–48 hour delay. Mandi Saathi flags any record older than 2 days as "Stale".
4. **Macro Shocks**: Statistical time-series corridors cannot anticipate unseasonal hailstorms, highway strikes, or abrupt governmental export/import policy bans.

---

## 🔒 Security & Privacy Notice

- **No Secrets Committed**: Mandi Saathi enforces strict exclusion of `.env`, API credentials, and local database files via `.gitignore`.
- **Zero Lookahead Leakage**: Backtest simulations are verified against artificial future price corruptions to prevent lookahead bias.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
