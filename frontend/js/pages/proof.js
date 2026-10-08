// Mandi Saathi - Proof & Calculation Logic Page
import { api } from '../api.js';
import { t, getCurrentLanguage } from '../i18n.js';

let currentChart = null;

const CROPS = [
  { id: 'Tomato', name: 'Tomato (टोमॅटो)' },
  { id: 'Onion', name: 'Onion (कांदा)' },
  { id: 'Soyabean', name: 'Soybean (सोयाबीन)' },
  { id: 'Red gram/Arhar/Tur(whole)', name: 'Tur / Arhar (तूर)' },
  { id: 'Cotton', name: 'Cotton (कापूस)' },
  { id: 'Potato', name: 'Potato (बटाटा)' },
  { id: 'Wheat', name: 'Wheat (गहू)' }
];

const DISTRICTS = [
  'Pune', 'Nashik', 'Latur', 'Ahilyanagar', 'Solapur',
  'Jalgaon', 'Akola', 'Amravati', 'Kolhapur', 'Nagpur',
  'Satara', 'Sangli', 'Chhatrapati Sambhajinagar'
];

export async function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 960px; padding-bottom: 60px;">
      <!-- Page Header -->
      <div style="margin-bottom: 28px; text-align: center;">
        <span class="badge badge-green" style="margin-bottom: 8px;">
          <i data-lucide="scale" style="width: 14px; height: 14px;"></i> Empirical Proof & Mathematical Transparency
        </span>
        <h1 style="font-size: 1.85rem; font-weight: 700; color: var(--text); margin-bottom: 8px;">
          Backtest Proof & Calculation Logic
        </h1>
        <p style="color: var(--muted); font-size: 0.95rem; max-width: 700px; margin: 0 auto;">
          Strictly leak-free simulation over the historical record across 23 Maharashtra APMC markets.
          See real empirical alpha, cumulative returns, worse days, and step-by-step mathematical formulas.
        </p>
      </div>

      <!-- Controls Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-title" style="font-size: 1.05rem;">
          <i data-lucide="sliders" style="width: 18px; height: 18px; color: var(--primary);"></i>
          Simulate Historical Backtest
        </div>
        <div class="card-subtitle">
          Test how Mandi Saathi would have performed on every trading day versus always selling at the nearest local APMC.
        </div>

        <form id="backtest-form" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; align-items: end; margin-top: 14px;">
          <div class="input-group">
            <label for="bt-crop" class="input-label">Crop</label>
            <select id="bt-crop" class="input-control">
              ${CROPS.map((c) => `<option value="${c.id}">${c.name}</option>`).join('')}
            </select>
          </div>

          <div class="input-group">
            <label for="bt-district" class="input-label">Origin District</label>
            <select id="bt-district" class="input-control">
              ${DISTRICTS.map((d) => `<option value="${d}">${d}</option>`).join('')}
            </select>
          </div>

          <div class="input-group">
            <label for="bt-vehicle" class="input-label">Vehicle</label>
            <select id="bt-vehicle" class="input-control">
              <option value="tempo">Tempo (Pickup - ₹14/km)</option>
              <option value="truck">Mini Truck (₹22/km)</option>
              <option value="own_vehicle">Own Vehicle (Fuel only - ₹9/km)</option>
            </select>
          </div>

          <div class="input-group">
            <label for="bt-qty" class="input-label">Quantity (Quintals)</label>
            <input type="number" id="bt-qty" class="input-control" value="20" min="1" max="500" step="1">
          </div>

          <div>
            <button type="submit" class="btn btn-primary" id="btn-run-backtest" style="width: 100%; min-height: 42px;">
              <i data-lucide="play" style="width: 16px; height: 16px;"></i> Run Backtest
            </button>
          </div>
        </form>
      </div>

      <!-- Backtest Results Container -->
      <div id="backtest-results-container">
        <div class="card" style="text-align: center; padding: 40px;">
          <div class="spinner" style="margin: 0 auto 16px;"></div>
          <p style="color: var(--muted);">Calculating leak-free backtest simulation...</p>
        </div>
      </div>

      <!-- Section: Step-by-Step Formula Breakdown for Demo Result -->
      <div class="card" style="margin-top: 32px;" id="formula-section">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 8px;">
          <div class="card-title" style="font-size: 1.15rem; margin-bottom: 0;">
            <i data-lucide="calculator" style="width: 20px; height: 20px; color: var(--primary);"></i>
            Step-by-Step Formula Breakdown (Try Demo Trip)
          </div>
          <button class="btn btn-ghost" id="btn-recalc-demo" style="font-size: 0.85rem; padding: 6px 14px;">
            <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i> Refresh with Live Engine
          </button>
        </div>
        <div class="card-subtitle">
          Representative Scenario: <strong>Tomato • 20 Quintals • Origin: Pune District (Tempo)</strong>.
          Demonstrating why a higher headline price at a distant mandi can be an illusion once transit deductions are applied.
        </div>

        <div id="demo-formula-container" style="margin-top: 16px;">
          <!-- Content dynamically rendered by renderDemoFormula() -->
        </div>
      </div>

      <!-- Section: Plain Note on Limits -->
      <div class="card" style="margin-top: 24px; background: #FFFDF9; border: 1px solid #FFE0B2;">
        <div class="card-title" style="color: #E65100; font-size: 1.05rem;">
          <i data-lucide="alert-triangle" style="width: 18px; height: 18px; color: #F57C00;"></i>
          Plain Note on Real-World Limitations & Constraints
        </div>
        <div style="font-size: 0.9rem; color: #4E342E; line-height: 1.6; display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
          <div>
            <strong>1. Intra-Day Auction Floor Volatility:</strong>
            Agmarknet records the daily modal (most common) clearing price. However, physical APMC auctions clear between 6:00 AM and 12:00 PM, where prices fluctuate based on instantaneous morning lorry arrivals, buyer cartels, and individual crate moisture/size sorting.
          </div>
          <div>
            <strong>2. Freight Rate & Negotiation Variations:</strong>
            Mandi Saathi uses standardized rural road rates (Tempo ₹14/km, Mini-Truck ₹22/km) with a 1.25 road winding factor. Actual negotiated charges with local transporters or unionized drivers may vary based on return-load availability, fuel price spikes, and toll charges.
          </div>
          <div>
            <strong>3. Auction Cutoff Friction:</strong>
            Departing late or encountering highway traffic can cause arrival after the 12:00 PM auction close. When cutoffs are missed, stock must be held overnight, incurring additional storage or overnight perishability loss.
          </div>
          <div>
            <strong>4. Leak-Free Simulation Requirement:</strong>
            The backtest simulates trading strictly on dates where paired settlements exist. Days where one market failed to report arrival figures to Agmarknet are omitted to avoid lookahead bias or fabricated estimates.
          </div>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();

  // Attach backtest form submission
  const btForm = container.querySelector('#backtest-form');
  btForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await loadBacktest(container);
  });

  // Attach live demo formula reload
  const btnRecalc = container.querySelector('#btn-recalc-demo');
  if (btnRecalc) {
    btnRecalc.addEventListener('click', async () => {
      await renderDemoFormula(container);
    });
  }

  // Initial load
  await loadBacktest(container);
  await renderDemoFormula(container);
}

// =============================================================================
// Backtest Execution & Rendering
// =============================================================================

async function loadBacktest(container) {
  const target = container.querySelector('#backtest-results-container');
  if (!target) return;

  const crop = container.querySelector('#bt-crop').value;
  const district = container.querySelector('#bt-district').value;
  const vehicle = container.querySelector('#bt-vehicle').value;
  const qty = parseFloat(container.querySelector('#bt-qty').value) || 20.0;

  target.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner" style="margin: 0 auto 16px;"></div>
      <p style="color: var(--muted);">Simulating ${crop} backtest for ${district} across historical records...</p>
    </div>
  `;

  try {
    const data = await api.getBacktest(crop, district, qty, vehicle);
    renderBacktestResults(container, data);
  } catch (err) {
    target.innerHTML = `
      <div class="card" style="border-color: #FFCDD2; background: #FFEBEE; padding: 24px; text-align: center;">
        <i data-lucide="alert-circle" style="width: 32px; height: 32px; color: #C62828; margin: 0 auto 8px;"></i>
        <h3 style="color: #C62828; font-size: 1.1rem; margin-bottom: 4px;">Backtest Failed</h3>
        <p style="color: #B71C1C; font-size: 0.9rem;">${err.message}</p>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
  }
}

function renderBacktestResults(container, data) {
  const target = container.querySelector('#backtest-results-container');
  if (!target) return;

  if (data.status === 'THIN_DATA' || data.days_tested === 0) {
    target.innerHTML = `
      <div class="card" style="padding: 30px; text-align: center;">
        <i data-lucide="database-zap" style="width: 40px; height: 40px; color: #F57C00; margin: 0 auto 12px;"></i>
        <h3 style="color: var(--text); font-size: 1.15rem; margin-bottom: 6px;">Insufficient Paired Trading Data</h3>
        <p style="color: var(--muted); font-size: 0.9rem; max-width: 600px; margin: 0 auto;">
          ${data.message || `No overlapping historical trading settlements found for ${data.crop} in ${data.district}. Try Tomato or Onion in Pune / Nashik.`}
        </p>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
    return;
  }

  const avgExtra = Number(data.average_extra_rs_per_quintal || 0);
  const pctBetter = Number(data.percent_days_better || 0);
  const daysTested = Number(data.days_tested || 0);
  const totExtra = Number(data.total_extra_rs_per_quintal || 0);
  const nearestMandi = data.nearest_mandi || 'Nearest Mandi';

  const isPositive = avgExtra >= 0;
  const alphaColor = isPositive ? '#2E7D32' : '#C62828';
  const alphaSign = avgExtra > 0 ? '+' : '';

  target.innerHTML = `
    <!-- 1. Stat KPI Cards -->
    <div class="proof-kpi-grid">
      <div class="proof-kpi-card">
        <div class="proof-kpi-label">Average Extra / Quintal</div>
        <div class="proof-kpi-value" style="color: ${alphaColor};">
          ${alphaSign}₹${avgExtra.toFixed(2)}
        </div>
        <div style="font-size: 0.78rem; color: var(--muted);">vs ${nearestMandi} baseline</div>
      </div>

      <div class="proof-kpi-card">
        <div class="proof-kpi-label">% Days Better</div>
        <div class="proof-kpi-value" style="color: #1976D2;">
          ${pctBetter.toFixed(1)}%
        </div>
        <div style="font-size: 0.78rem; color: var(--muted);">${data.days_better} of ${daysTested} trading days</div>
      </div>

      <div class="proof-kpi-card">
        <div class="proof-kpi-label">Days Tested</div>
        <div class="proof-kpi-value" style="color: var(--text);">
          ${daysTested}
        </div>
        <div style="font-size: 0.78rem; color: var(--muted);">Over 90-day snapshot</div>
      </div>

      <div class="proof-kpi-card">
        <div class="proof-kpi-label">Cumulative Extra Gain</div>
        <div class="proof-kpi-value" style="color: ${alphaColor};">
          ${alphaSign}₹${Math.round(totExtra).toLocaleString('en-IN')}
        </div>
        <div style="font-size: 0.78rem; color: var(--muted);">Total ₹/q over all simulated days</div>
      </div>
    </div>

    <!-- 2. Honest Assessment Narrative Banner -->
    <div style="background: ${isPositive ? '#E8F5E9' : '#FFEBEE'}; border: 1px solid ${isPositive ? '#C8E6C9' : '#FFCDD2'}; border-radius: var(--radius-md); padding: 14px 18px; margin-bottom: 24px; font-size: 0.9rem; color: ${isPositive ? '#1B5E20' : '#B71C1C'}; line-height: 1.5;">
      <strong>Honest Empirical Summary:</strong> ${data.honest_assessment || ''}
    </div>

    <!-- 3. Chart.js Cumulative Returns Line Chart -->
    <div class="card" style="margin-bottom: 24px; padding: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
          <div class="card-title" style="margin-bottom: 2px;">
            <i data-lucide="trending-up" style="width: 18px; height: 18px; color: var(--primary);"></i>
            Cumulative Realized Net Returns (₹ / Quintal)
          </div>
          <div class="card-subtitle">
            Tracking simulated total revenue: Mandi Saathi Strategy (Green) vs. Always Selling at ${nearestMandi} (Slate)
          </div>
        </div>
        <span class="badge badge-sky" style="font-size: 0.75rem;">Leak-Free T-1 Prior Data</span>
      </div>

      <div style="position: relative; height: 320px; width: 100%;">
        <canvas id="backtest-chart"></canvas>
      </div>
    </div>

    <!-- 4. Worse Days List (When Strategy Underperformed) -->
    <div class="card" style="padding: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
          <div class="card-title" style="margin-bottom: 2px; color: #B71C1C;">
            <i data-lucide="shield-alert" style="width: 18px; height: 18px; color: #D32F2F;"></i>
            When Did Mandi Saathi Lose? (Worse-Days Analysis)
          </div>
          <div class="card-subtitle">
            Days where traveling or switching mandis underperformed the local nearest baseline due to unexpected price inversions.
          </div>
        </div>
        <span class="badge badge-red" id="worse-days-count-badge">${(data.worse_days || []).length} Days</span>
      </div>

      <div id="worse-days-container" style="overflow-x: auto;">
        <!-- Rendered by renderWorseDays() -->
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();

  // Render Chart.js
  renderBacktestChart(data.cumulative_series || [], nearestMandi);

  // Render Worse Days
  renderWorseDays(target, data.worse_days || [], nearestMandi);
}

function renderBacktestChart(series, nearestMandi) {
  const canvas = document.getElementById('backtest-chart');
  if (!canvas || !window.Chart) return;

  if (currentChart) {
    currentChart.destroy();
    currentChart.current = null;
  }

  const labels = series.map((s) => s.date);
  const saathiCumulative = series.map((s) => s.mandi_saathi_cumulative);
  const nearestCumulative = series.map((s) => s.nearest_cumulative);

  const ctx = canvas.getContext('2d');
  currentChart = new window.Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Mandi Saathi Advisory',
          data: saathiCumulative,
          borderColor: '#2E7D32',
          backgroundColor: 'rgba(46, 125, 50, 0.08)',
          fill: true,
          borderWidth: 2.5,
          pointRadius: 2,
          pointHoverRadius: 6,
          tension: 0.15
        },
        {
          label: `Nearest Mandi (${nearestMandi}) Baseline`,
          data: nearestCumulative,
          borderColor: '#607D8B',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 6,
          tension: 0.15
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 14,
            font: { family: 'Poppins', size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString('en-IN')}/q`;
            },
            footer: function (items) {
              if (items.length >= 2) {
                const diff = items[0].parsed.y - items[1].parsed.y;
                const sign = diff >= 0 ? '+' : '';
                return `Advantage: ${sign}₹${diff.toFixed(2)}/q`;
              }
              return '';
            }
          }
        }
      },
      scales: {
        y: {
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: {
            callback: (val) => `₹${Number(val).toLocaleString('en-IN')}`,
            font: { family: 'Poppins', size: 11 }
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            maxTicksLimit: 10,
            font: { family: 'Poppins', size: 11 }
          }
        }
      }
    }
  });
}

function renderWorseDays(target, worseDays, nearestMandi) {
  const container = target.querySelector('#worse-days-container');
  if (!container) return;

  if (!worseDays || worseDays.length === 0) {
    container.innerHTML = `
      <div style="background: #E8F5E9; border-radius: var(--radius-md); padding: 18px; text-align: center; color: #2E7D32;">
        <i data-lucide="check-circle" style="width: 24px; height: 24px; margin: 0 auto 6px;"></i>
        <div style="font-weight: 600;">Zero Underperformance Days</div>
        <div style="font-size: 0.85rem; opacity: 0.9;">
          Mandi Saathi matched or outperformed ${nearestMandi} on 100% of the simulated trading days!
        </div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
    return;
  }

  container.innerHTML = `
    <table class="worse-days-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Chosen Market</th>
          <th>Baseline Market</th>
          <th>Realized Deficit</th>
          <th>Actual Clearance Prices</th>
          <th>Root Cause Explanation</th>
        </tr>
      </thead>
      <tbody>
        ${worseDays.map((w) => `
          <tr>
            <td style="font-weight: 600; white-space: nowrap; color: var(--text);">${w.date}</td>
            <td style="font-weight: 500;">${w.recommended_mandi}</td>
            <td style="color: var(--muted);">${w.nearest_mandi || nearestMandi}</td>
            <td style="color: #C62828; font-weight: 700; white-space: nowrap;">
              -₹${Math.abs(w.diff_rs).toFixed(2)}/q
            </td>
            <td style="font-size: 0.82rem; white-space: nowrap;">
              Chosen: ₹${w.actual_price_recommended}/q<br/>
              Nearest: ₹${w.actual_price_nearest}/q
            </td>
            <td style="font-size: 0.82rem; color: #5D4037; line-height: 1.4; min-width: 260px;">
              ${w.reason}
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

// =============================================================================
// Step-by-Step Formula Breakdown (Try Demo Trip)
// =============================================================================

async function renderDemoFormula(container) {
  const target = container.querySelector('#demo-formula-container');
  if (!target) return;

  target.innerHTML = `
    <div style="padding: 20px; text-align: center; color: var(--muted);">
      <div class="spinner" style="margin: 0 auto 10px;"></div>
      Calculating live formula breakdown for Demo Trip (Tomato • Pune • 20q)...
    </div>
  `;

  try {
    const adv = await api.calculateAdvise({
      crop: 'Tomato',
      district: 'Pune',
      quantity_quintals: 20.0,
      vehicle_type: 'tempo',
      departure_hour: 7.0
    });

    const best = adv.best_recommendation;
    const comps = adv.comparisons || [];

    // Find a distant comparison market (e.g. Baramati, Sangamner, or any comparison with dist > 20 km)
    const farComp = comps.find((c) => c.distance_km > 20) || comps[0] || best;

    // Numbers for Pune (Local)
    const pGross = Math.round(best.gross_modal_price);
    const pDist = best.distance_km;
    const pTrans = best.costs.transport_per_q;
    const pLoad = best.costs.loading_unloading_per_q;
    const pCess = best.costs.market_fee_per_q;
    const pSpoil = best.costs.spoilage_per_q;
    const pDed = best.costs.total_deductions_per_q;
    const pNet = best.net_return_per_quintal;
    const pTotal = Math.round(best.total_net_earnings);

    // Numbers for Far Market
    const fMarket = farComp.market;
    const fGross = Math.round(farComp.gross_modal_price);
    const fDist = farComp.distance_km;
    const fTrans = farComp.costs.transport_per_q;
    const fLoad = farComp.costs.loading_unloading_per_q;
    const fCess = farComp.costs.market_fee_per_q;
    const fSpoil = farComp.costs.spoilage_per_q;
    const fDed = farComp.costs.total_deductions_per_q;
    const fNet = farComp.net_return_per_quintal;
    const fTotal = Math.round(farComp.total_net_earnings);

    const headlineDiff = fGross - pGross;
    const netDiff = fNet - pNet;

    target.innerHTML = `
      <!-- Comparison KPI Bar -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px;">
        <!-- Local Market Card -->
        <div style="background: #E8F5E9; border: 2px solid #81C784; border-radius: var(--radius-lg); padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; color: #1B5E20; font-size: 1.05rem;">📍 Local APMC: ${best.market}</span>
            <span class="badge badge-green">Recommended</span>
          </div>
          <div style="font-size: 0.85rem; color: #2E7D32;">Distance: ${pDist} km (0.2 hrs)</div>
          <div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: baseline;">
            <div>
              <div style="font-size: 0.8rem; color: var(--muted);">Gross Price</div>
              <div style="font-size: 1.15rem; font-weight: 600; color: var(--text);">₹${pGross} / q</div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 0.8rem; color: #2E7D32; font-weight: 600;">True Net in Pocket</div>
              <div style="font-size: 1.45rem; font-weight: 700; color: #1B5E20;">₹${Math.round(pNet)} / q</div>
            </div>
          </div>
          <div style="font-size: 0.8rem; color: var(--muted); border-top: 1px dashed #A5D6A7; padding-top: 6px;">
            Total deductions: ₹${pDed.toFixed(1)}/q • Total Net: ₹${pTotal.toLocaleString('en-IN')}
          </div>
        </div>

        <!-- Distant Market Card -->
        <div style="background: #FFF8E1; border: 1px solid #FFE082; border-radius: var(--radius-lg); padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; color: #E65100; font-size: 1.05rem;">🚚 Distant APMC: ${fMarket}</span>
            <span class="badge ${netDiff > 0 ? 'badge-green' : 'badge-red'}">
              ${netDiff > 0 ? '+₹' + netDiff.toFixed(1) + '/q Net Gain' : '-₹' + Math.abs(netDiff).toFixed(1) + '/q Deficit'}
            </span>
          </div>
          <div style="font-size: 0.85rem; color: #E65100;">Distance: ${fDist} km (${farComp.travel_hours || 3.0} hrs)</div>
          <div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: baseline;">
            <div>
              <div style="font-size: 0.8rem; color: var(--muted);">Gross Price</div>
              <div style="font-size: 1.15rem; font-weight: 600; color: #E65100;">
                ₹${fGross} / q ${headlineDiff > 0 ? `(+₹${headlineDiff})` : ''}
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 0.8rem; color: #E65100; font-weight: 600;">True Net in Pocket</div>
              <div style="font-size: 1.45rem; font-weight: 700; color: ${netDiff >= 0 ? '#2E7D32' : '#C62828'};">
                ₹${Math.round(fNet)} / q
              </div>
            </div>
          </div>
          <div style="font-size: 0.8rem; color: var(--muted); border-top: 1px dashed #FFE082; padding-top: 6px;">
            Total deductions: ₹${fDed.toFixed(1)}/q • Total Net: ₹${fTotal.toLocaleString('en-IN')}
          </div>
        </div>
      </div>

      <!-- Step-by-Step Mathematical Formula Walkthrough -->
      <div class="formula-card">
        <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text); margin-bottom: 16px;">
          Detailed 6-Step Deduction Breakdown
        </h3>

        <!-- Step 1 -->
        <div class="formula-step">
          <div class="formula-step-num">1</div>
          <div style="flex: 1;">
            <strong>Step 1: Gross Revenue Valuation</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Value before any deductions = Quantity (Q) × Destination Mandi Modal Price (P).
            </p>
            <div class="formula-code">
              Gross Value (Local ${best.market}) = 20q × ₹${pGross}/q = ₹${(20 * pGross).toLocaleString('en-IN')}<br/>
              Gross Value (Distant ${fMarket}) = 20q × ₹${fGross}/q = ₹${(20 * fGross).toLocaleString('en-IN')}
            </div>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="formula-step">
          <div class="formula-step-num">2</div>
          <div style="flex: 1;">
            <strong>Step 2: Road Transport Freight Cost</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Roundtrip Distance × Freight Rate / Quantity. Tempo rate = ₹14/km (with 1.25 rural winding factor).
            </p>
            <div class="formula-code">
              Transport Cost = (Distance_km × 2 × ₹14) / 20 quintals<br/>
              • Local (${best.market}, ${pDist} km) = (${pDist} × 2 × 14) / 20 = <strong>₹${pTrans.toFixed(2)}/q</strong> (₹${Math.round(pTrans * 20)})<br/>
              • Distant (${fMarket}, ${fDist} km) = (${fDist} × 2 × 14) / 20 = <strong>₹${fTrans.toFixed(2)}/q</strong> (₹${Math.round(fTrans * 20)})
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="formula-step">
          <div class="formula-step-num">3</div>
          <div style="flex: 1;">
            <strong>Step 3: Loading, Hamali & Weighment Labor</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Standardized APMC handling charges for farmgate crate loading and truck unstrapping.
            </p>
            <div class="formula-code">
              Labor Fee = ₹30.00 / quintal across both markets = ₹600.00 total for 20 quintals.
            </div>
          </div>
        </div>

        <!-- Step 4 -->
        <div class="formula-step">
          <div class="formula-step-num">4</div>
          <div style="flex: 1;">
            <strong>Step 4: Statutory APMC Market Cess & Fee</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Maharashtra APMC statutory user fee = 1.05% of gross trade value + 0.05% supervision tax (1.50% total cess).
            </p>
            <div class="formula-code">
              APMC Cess = Modal Price × 1.5%<br/>
              • Local (${best.market}) = ₹${pGross} × 0.015 = <strong>₹${pCess.toFixed(2)}/q</strong><br/>
              • Distant (${fMarket}) = ₹${fGross} × 0.015 = <strong>₹${fCess.toFixed(2)}/q</strong>
            </div>
          </div>
        </div>

        <!-- Step 5 -->
        <div class="formula-step">
          <div class="formula-step-num">5</div>
          <div style="flex: 1;">
            <strong>Step 5: Transit Perishability & Spoilage Loss</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Vibration, crushing and heat decay during travel. Tomato base decay rate = 2.5% per 24 hours.
            </p>
            <div class="formula-code">
              Spoilage Loss = Gross Price × (Travel_Hours / 24) × 0.025<br/>
              • Local (${pDist} km, ~0.2 hrs) = <strong>₹${pSpoil.toFixed(2)}/q</strong> (almost zero decay)<br/>
              • Distant (${fDist} km, ~${farComp.travel_hours || 3.0} hrs) = <strong>₹${fSpoil.toFixed(2)}/q</strong>
            </div>
          </div>
        </div>

        <!-- Step 6 -->
        <div class="formula-step">
          <div class="formula-step-num">6</div>
          <div style="flex: 1;">
            <strong>Step 6: True Net-in-Pocket Return Realization</strong>
            <p style="font-size: 0.85rem; color: var(--muted); margin: 2px 0;">
              Net Return per Quintal = Modal Price - (Transport + Labor + APMC Cess + Spoilage).
            </p>
            <div class="formula-code">
              • Local (${best.market}): ₹${pGross} - (₹${pTrans.toFixed(1)} + ₹30 + ₹${pCess.toFixed(1)} + ₹${pSpoil.toFixed(1)}) = <strong>₹${Math.round(pNet)}/q</strong><br/>
              • Distant (${fMarket}): ₹${fGross} - (₹${fTrans.toFixed(1)} + ₹30 + ₹${fCess.toFixed(1)} + ₹${fSpoil.toFixed(1)}) = <strong>₹${Math.round(fNet)}/q</strong><br/>
              --------------------------------------------------------------------------------<br/>
              Verdict: ${netDiff <= 0 
                ? `Despite ${fMarket} offering a headline price ₹${headlineDiff}/q higher, the extra transport (₹${(fTrans - pTrans).toFixed(1)}/q) and cess completely erased the premium. Local sale at ${best.market} puts ₹${Math.abs(netDiff).toFixed(1)}/q MORE into the farmer's pocket!` 
                : `Distant sale at ${fMarket} justifies travel, generating an extra +₹${netDiff.toFixed(1)}/q net profit after all expenses.`}
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    target.innerHTML = `
      <div style="padding: 16px; color: #C62828;">
        Error rendering demo formula breakdown: ${err.message}
      </div>
    `;
  }
}
