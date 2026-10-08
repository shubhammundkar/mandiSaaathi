// Mandi Saathi - About Page
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 920px; padding-bottom: 60px;">
      <!-- Hero Header -->
      <div style="margin-bottom: 32px; text-align: center;">
        <span class="badge badge-green" style="margin-bottom: 10px;">
          <i data-lucide="sprout" style="width: 14px; height: 14px;"></i> VORTEX 2K26 • Climate, Agriculture & Rural Innovation
        </span>
        <h1 style="font-size: 2rem; font-weight: 700; color: var(--text); margin-bottom: 8px;">
          About Mandi Saathi (मंडी साथी)
        </h1>
        <p style="color: var(--muted); font-size: 1rem; max-width: 680px; margin: 0 auto; line-height: 1.5;">
          An AI-powered market co-pilot protecting Indian farmers from the headline price trap through transparent net-in-pocket math and sell-timing intelligence.
        </p>
      </div>

      <!-- 1. The Problem We Solve -->
      <div class="card" style="margin-bottom: 24px; padding: 24px;">
        <div class="card-title" style="font-size: 1.2rem; color: #C62828;">
          <i data-lucide="alert-octagon" style="width: 22px; height: 22px; color: #D32F2F;"></i>
          The Problem: The "Headline Price Trap"
        </div>
        <div style="color: var(--text); font-size: 0.95rem; line-height: 1.6; display: flex; flex-direction: column; gap: 12px; margin-top: 12px;">
          <p>
            Across rural India, smallholder farmers check wholesale mandi prices on generic apps or WhatsApp groups. When an APMC market 120 km away advertises a gross price of ₹2,200/quintal versus their local market at ₹1,800/quintal, the farmer sees an apparent <strong>₹400/quintal windfall</strong>.
          </p>
          <div style="background: #FFF8E1; border-left: 4px solid #FFA000; padding: 14px 18px; border-radius: 0 var(--radius-md) var(--radius-md) 0; font-size: 0.9rem; color: #5D4037;">
            <strong>The Harsh Reality:</strong>
            For a typical 20-quintal tempo load, roundtrip diesel and vehicle hire cost ₹3,360 (₹168/q), loading/unloading labor costs ₹600 (₹30/q), statutory APMC market cess costs ₹660 (₹33/q), and transit heat vibration spoils another ₹50/q.
            <br/><br/>
            Total deductions reach <strong>₹281/quintal</strong>. If the farmer hits highway traffic and arrives after the 12:00 PM auction close, prices crash or the crop must be sold in distress to middlemen. The apparent ₹400 windfall evaporates into a net loss.
          </div>
          <p>
            Existing agricultural software provides retrospective lists or simple price averages. <strong>None calculate whether the farmer will actually pocket more money after the truck stops rolling.</strong> Mandi Saathi was built to fix this fundamental economic friction.
          </p>
        </div>
      </div>

      <!-- 2. 4-Step How It Works -->
      <div class="card" style="margin-bottom: 24px; padding: 24px;">
        <div class="card-title" style="font-size: 1.2rem;">
          <i data-lucide="layers" style="width: 22px; height: 22px; color: var(--primary);"></i>
          How It Works: 4-Step Decision Architecture
        </div>
        <div class="card-subtitle">
          From open government data ingestion to real-time net return ranking and time-series sell-timing advisory.
        </div>

        <div class="about-step-grid">
          <!-- Step 1 -->
          <div class="about-step-card">
            <div class="about-step-icon">
              <i data-lucide="database" style="width: 22px; height: 22px;"></i>
            </div>
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase;">Step 1</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--text);">Live Agmarknet Data Ingestion</div>
            <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.5; margin: 0;">
              Ingests daily wholesale arrivals, modal prices, and minimum/maximum clearing spreads across 23 Maharashtra APMC markets. Automatically sanitizes commodities, flags stale markets (>3 days), and verifies geographic coordinates.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="about-step-card">
            <div class="about-step-icon">
              <i data-lucide="truck" style="width: 22px; height: 22px;"></i>
            </div>
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase;">Step 2</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--text);">Road-Aware Logistics & Deductions</div>
            <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.5; margin: 0;">
              Computes actual road distances using Haversine with a 1.25 winding factor. Deducts vehicle-specific roundtrip freight (Tempo ₹14/km, Mini-Truck ₹22/km), loading labor (₹30/q), statutory APMC cess (1.05%), and perishable decay per transit hour.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="about-step-card">
            <div class="about-step-icon">
              <i data-lucide="bar-chart-2" style="width: 22px; height: 22px;"></i>
            </div>
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase;">Step 3</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--text);">Honest Net-in-Pocket Ranking</div>
            <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.5; margin: 0;">
              Ranks reachable APMCs strictly by true net return per quintal. Evaluates travel duration against each market's 12:00 PM auction cutoff, applies conservative lower-bound haircuts for distant markets, and calculates the break-even threshold.
            </p>
          </div>

          <!-- Step 4 -->
          <div class="about-step-card">
            <div class="about-step-icon">
              <i data-lucide="trending-up" style="width: 22px; height: 22px;"></i>
            </div>
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase;">Step 4</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--text);">5-Day Corridor & Sell/Store Verdict</div>
            <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.5; margin: 0;">
              Projects a 5-day Low, Likely, and High price outlook corridor using time-series modeling. Generates a clear verdict: "Sell now" vs. "Wait & Store" based on whether expected price rise outweighs monthly storage holding cost.
            </p>
          </div>
        </div>
      </div>

      <!-- 3. Real-World Limitations -->
      <div class="card" style="margin-bottom: 24px; padding: 24px;">
        <div class="card-title" style="font-size: 1.2rem; color: #E65100;">
          <i data-lucide="alert-triangle" style="width: 22px; height: 22px; color: #F57C00;"></i>
          System Limitations & Honest Assumptions
        </div>
        <div class="card-subtitle">
          We believe in complete scientific and operational transparency with farmers.
        </div>

        <ul style="margin: 12px 0 0 18px; font-size: 0.9rem; color: var(--text); line-height: 1.6; display: flex; flex-direction: column; gap: 8px;">
          <li>
            <strong>Intra-Day Auction Spread:</strong> APMC transactions take place between commission agents (Adatyas) and buyers in morning open auctions. Individual lot price depends on crate blemish sort, moisture percentage, and arrival volume surges.
          </li>
          <li>
            <strong>Variable Transporter Charges:</strong> Freight rates are modeled on standard rural hiring benchmarks (Tempo ₹14/km). Actual driver negotiations may fluctuate based on return-cargo availability, diesel cost changes, and toll roads.
          </li>
          <li>
            <strong>Data Latency:</strong> APMC market secretaries upload arrival records via Agmarknet. While most major markets update daily by 6:00 PM, smaller rural sub-yards may occasionally have a 1–2 day reporting lag. Mandi Saathi flags any records older than 2 days as "Stale".
          </li>
          <li>
            <strong>Black Swan Climatic & Policy Events:</strong> Time-series price corridors model statistical seasonal trends; they cannot predict unseasonal hailstorms, transport strikes, or abrupt governmental export/import policy interventions.
          </li>
        </ul>
      </div>

      <!-- 4. Data Credit & Open Data Attribution -->
      <div class="card" style="padding: 24px; background: #F1F8E9; border: 1px solid #C5E1A5;">
        <div class="card-title" style="font-size: 1.15rem; color: #2E7D32;">
          <i data-lucide="award" style="width: 22px; height: 22px; color: #2E7D32;"></i>
          Open Data Credit & Governance
        </div>
        <div style="font-size: 0.92rem; color: #1B5E20; line-height: 1.6; margin-top: 10px;">
          <p style="margin-bottom: 10px;">
            All wholesale market arrival statistics, minimum, maximum, and modal clearing prices used by Mandi Saathi are ingested from:
          </p>
          <div style="background: #FFFFFF; border: 1px solid #A5D6A7; border-radius: var(--radius-md); padding: 14px 18px; margin: 12px 0; font-weight: 600; font-size: 1rem; color: #1B5E20; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <span>Data source: Agmarknet (agmarknet.gov.in)</span>
            <a href="https://agmarknet.gov.in" target="_blank" rel="noopener noreferrer" class="btn btn-ghost" style="font-size: 0.82rem; min-height: 32px; padding: 4px 12px; background: #E8F5E9; color: #2E7D32; border-color: #A5D6A7; text-decoration: none;">
              Visit Agmarknet Portal <i data-lucide="external-link" style="width: 14px; height: 14px; margin-left: 4px;"></i>
            </a>
          </div>
          <p style="font-size: 0.85rem; color: #33691E; margin-bottom: 0;">
            Provided through the Open Government Data (OGD) Platform India (<a href="https://data.gov.in" target="_blank" rel="noopener noreferrer" style="color: #2E7D32; font-weight: 600;">data.gov.in</a>). Verified 90-day Maharashtra APMC historical dataset maintained in SQLite with strict leak-free temporal separation.
          </p>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}
