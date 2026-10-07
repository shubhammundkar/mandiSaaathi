// Mandi Saathi - Advisor Page
// Interactive recommendation engine form with 1-click Demo, live data badge,
// collapsible advanced parameters, 5-day forecast corridor, and voice playback.

import { t, getLanguage } from '../i18n.js';
import { api } from '../api.js';

// Crops list with icons and emojis
const CROPS = [
  { key: 'Tomato', labelKey: 'crop_tomato', emoji: '🍅', defaultDistrict: 'Pune' },
  { key: 'Onion', labelKey: 'crop_onion', emoji: '🧅', defaultDistrict: 'Nashik' },
  { key: 'Soybean', labelKey: 'crop_soybean', emoji: '🌱', defaultDistrict: 'Latur' },
  { key: 'Tur', labelKey: 'crop_tur', emoji: '🥣', defaultDistrict: 'Latur' },
  { key: 'Cotton', labelKey: 'crop_cotton', emoji: '☁️', defaultDistrict: 'Akola' },
  { key: 'Potato', labelKey: 'crop_potato', emoji: '🥔', defaultDistrict: 'Pune' },
  { key: 'Wheat', labelKey: 'crop_wheat', emoji: '🌾', defaultDistrict: 'Pune' }
];

// Supported vehicles
const VEHICLES = [
  { key: 'tempo', labelKey: 'vehicle_tempo', icon: 'truck', rate: '₹18/km' },
  { key: 'truck', labelKey: 'vehicle_truck', icon: 'container', rate: '₹28/km' },
  { key: 'own_vehicle', labelKey: 'vehicle_own', icon: 'bike', rate: '₹6/km' }
];

// Default available Maharashtra APMC districts
const DEFAULT_DISTRICTS = [
  'Pune', 'Nashik', 'Ahilyanagar', 'Solapur', 'Latur',
  'Jalgaon', 'Akola', 'Amravati', 'Kolhapur', 'Nagpur', 'Mumbai'
];

// Persistent state
const state = {
  selectedCrop: 'Tomato',
  selectedDistrict: 'Pune',
  quantity: 20.0,
  vehicle: 'tempo',
  departureHour: 7.0,
  isAdvancedOpen: false,
  overrides: {
    rate_per_km: '',
    market_fee_percent: '',
    spoilage_rate: '',
    loading_per_quintal: ''
  },
  dataStatus: null,
  districts: DEFAULT_DISTRICTS,
  isLoading: false,
  advisoryResult: null,
  forecastResult: null,
  storageResult: null,
  chartInstance: null,
  isSpeaking: false
};

export async function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 900px;">
      
      <!-- Page Header & Data Source Status -->
      <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 24px;">
        <div id="data-status-badge" style="margin-bottom: 10px;">
          <span class="badge badge-sky">
            <i data-lucide="database" style="width: 14px; height: 14px;"></i>
            <span data-i18n="data_source_snapshot">${t('data_source_snapshot')}</span>
          </span>
        </div>
        <h1 style="font-size: 1.85rem; font-weight: 700; color: var(--text); line-height: 1.25; margin-bottom: 8px;" data-i18n="advisor_heading">
          ${t('advisor_heading')}
        </h1>
        <p style="color: var(--muted); font-size: 0.95rem; max-width: 640px; margin: 0 auto;" data-i18n="advisor_subheading">
          ${t('advisor_subheading')}
        </p>
      </div>

      <!-- Main Input Form Card -->
      <div class="card" style="margin-bottom: 24px; padding: 24px;">
        <form id="advisor-form" onsubmit="return false;">
          
          <!-- 1. Crop Selection Chips -->
          <div style="margin-bottom: 20px;">
            <label class="input-label" style="display: flex; justify-content: space-between; align-items: center;">
              <span data-i18n="select_crop">${t('select_crop')}</span>
              <span style="font-size: 0.8rem; color: var(--muted);">7 APMC Crops Monitored</span>
            </label>
            <div class="chip-group" id="crop-chips">
              ${CROPS.map(c => `
                <button type="button" class="chip ${c.key === state.selectedCrop ? 'active' : ''}" data-crop="${c.key}">
                  <span>${c.emoji}</span>
                  <span data-i18n="${c.labelKey}">${t(c.labelKey)}</span>
                </button>
              `).join('')}
            </div>
          </div>

          <!-- 2. District & Quantity (Grid on Desktop) -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 20px;">
            
            <!-- District Dropdown -->
            <div class="input-group" style="margin-bottom: 0;">
              <label class="input-label" for="district-select" data-i18n="select_district">
                ${t('select_district')}
              </label>
              <select id="district-select" class="select">
                ${state.districts.map(d => `
                  <option value="${d}" ${d.toLowerCase() === state.selectedDistrict.toLowerCase() ? 'selected' : ''}>${d} District</option>
                `).join('')}
              </select>
            </div>

            <!-- Quantity Stepper -->
            <div class="input-group" style="margin-bottom: 0;">
              <label class="input-label" for="quantity-input" data-i18n="input_quantity">
                ${t('input_quantity')}
              </label>
              <div style="display: flex; align-items: center; gap: 8px;">
                <button type="button" class="btn btn-ghost" id="qty-minus" style="width: 48px; min-width: 48px; height: 48px; padding: 0;">
                  <i data-lucide="minus"></i>
                </button>
                <input type="number" id="quantity-input" class="input" min="1" max="500" step="1" value="${state.quantity}" style="text-align: center; font-weight: 600; font-size: 1.1rem;">
                <button type="button" class="btn btn-ghost" id="qty-plus" style="width: 48px; min-width: 48px; height: 48px; padding: 0;">
                  <i data-lucide="plus"></i>
                </button>
              </div>
            </div>

          </div>

          <!-- 3. Vehicle Selection Buttons -->
          <div style="margin-bottom: 20px;">
            <label class="input-label" data-i18n="select_vehicle">
              ${t('select_vehicle')}
            </label>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 6px;">
              ${VEHICLES.map(v => `
                <button type="button" class="btn ${v.key === state.vehicle ? 'btn-primary' : 'btn-ghost'} vehicle-btn" data-vehicle="${v.key}" style="flex-direction: column; height: 64px; border-radius: var(--radius-md); padding: 8px 12px;">
                  <span style="font-weight: 600; font-size: 0.9rem;" data-i18n="${v.labelKey}">${t(v.labelKey)}</span>
                  <span style="font-size: 0.75rem; opacity: 0.85;">${v.rate}</span>
                </button>
              `).join('')}
            </div>
          </div>

          <!-- 4. Collapsible Advanced Settings -->
          <div style="border-top: 1px dashed var(--border); padding-top: 14px; margin-bottom: 24px;">
            <button type="button" id="toggle-advanced" class="btn btn-ghost" style="width: 100%; justify-content: space-between; min-height: 40px; padding: 6px 12px; font-size: 0.85rem; color: var(--muted);">
              <span style="display: flex; align-items: center; gap: 8px;">
                <i data-lucide="sliders" style="width: 16px; height: 16px;"></i>
                <span data-i18n="advanced_title">${t('advanced_title')}</span>
              </span>
              <i data-lucide="${state.isAdvancedOpen ? 'chevron-up' : 'chevron-down'}" id="advanced-chevron" style="width: 16px; height: 16px;"></i>
            </button>

            <div id="advanced-panel" style="display: ${state.isAdvancedOpen ? 'grid' : 'none'}; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 14px;">
              <div class="input-group" style="margin-bottom: 0;">
                <label class="input-label" style="font-size: 0.8rem;" data-i18n="label_rate_km">${t('label_rate_km')}</label>
                <input type="number" id="override-rate-km" class="input" placeholder="Default (e.g. 18)" value="${state.overrides.rate_per_km}" style="min-height: 40px;">
              </div>
              <div class="input-group" style="margin-bottom: 0;">
                <label class="input-label" style="font-size: 0.8rem;" data-i18n="label_fee_pct">${t('label_fee_pct')}</label>
                <input type="number" id="override-fee-pct" class="input" placeholder="Default (1.5%)" step="0.1" value="${state.overrides.market_fee_percent}" style="min-height: 40px;">
              </div>
              <div class="input-group" style="margin-bottom: 0;">
                <label class="input-label" style="font-size: 0.8rem;" data-i18n="label_spoil_rate">${t('label_spoil_rate')}</label>
                <input type="number" id="override-spoil-rate" class="input" placeholder="Default (e.g. 2.5%)" step="0.001" value="${state.overrides.spoilage_rate}" style="min-height: 40px;">
              </div>
              <div class="input-group" style="margin-bottom: 0;">
                <label class="input-label" style="font-size: 0.8rem;" data-i18n="label_loading_rate">${t('label_loading_rate')}</label>
                <input type="number" id="override-loading-rate" class="input" placeholder="Default (15)" value="${state.overrides.loading_per_quintal}" style="min-height: 40px;">
              </div>
            </div>
          </div>

          <!-- 5. Action Buttons -->
          <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center;">
            <button type="button" class="btn btn-primary" id="btn-submit" style="flex: 2; min-width: 200px; height: 52px; font-size: 1.05rem;">
              <i data-lucide="compass"></i>
              <span data-i18n="btn_calculate">${t('btn_calculate')}</span>
            </button>
            <button type="button" class="btn btn-ghost" id="btn-demo" style="flex: 1; min-width: 180px; height: 52px; border: 1.5px solid var(--primary); background: var(--primary-light); color: var(--primary-dark); font-weight: 600;">
              <span data-i18n="btn_try_demo">${t('btn_try_demo')}</span>
            </button>
          </div>

        </form>
      </div>

      <!-- Results Display Container -->
      <div id="results-container">
        <!-- Injected dynamically on calculation -->
      </div>

    </div>
  `;

  // Attach event handlers
  bindEvents(container);

  // Refresh icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Load live data status & mandis list
  fetchDataStatus(container);
  fetchMandis(container);

  // If there's already an active advisory result in memory, render it
  if (state.advisoryResult) {
    renderResults(container);
  }
}

// Bind all interactive controls
function bindEvents(container) {
  // Crop chips
  container.querySelectorAll('#crop-chips .chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const crop = btn.getAttribute('data-crop');
      if (crop) {
        state.selectedCrop = crop;
        container.querySelectorAll('#crop-chips .chip').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');

        // Auto-select common default district for crop if available
        const cropMeta = CROPS.find(c => c.key === crop);
        if (cropMeta && cropMeta.defaultDistrict) {
          const select = container.querySelector('#district-select');
          if (select) {
            select.value = cropMeta.defaultDistrict;
            state.selectedDistrict = cropMeta.defaultDistrict;
          }
        }
      }
    });
  });

  // District select
  const districtSelect = container.querySelector('#district-select');
  if (districtSelect) {
    districtSelect.addEventListener('change', (e) => {
      state.selectedDistrict = e.target.value;
    });
  }

  // Quantity Stepper
  const qtyInput = container.querySelector('#quantity-input');
  const qtyPlus = container.querySelector('#qty-plus');
  const qtyMinus = container.querySelector('#qty-minus');

  if (qtyPlus && qtyInput) {
    qtyPlus.addEventListener('click', () => {
      let val = Math.max(1, (parseFloat(qtyInput.value) || 20) + 5);
      qtyInput.value = val;
      state.quantity = val;
    });
  }

  if (qtyMinus && qtyInput) {
    qtyMinus.addEventListener('click', () => {
      let val = Math.max(1, (parseFloat(qtyInput.value) || 20) - 5);
      qtyInput.value = val;
      state.quantity = val;
    });
  }

  if (qtyInput) {
    qtyInput.addEventListener('input', (e) => {
      state.quantity = Math.max(1, parseFloat(e.target.value) || 1);
    });
  }

  // Vehicle selector
  container.querySelectorAll('.vehicle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const v = btn.getAttribute('data-vehicle');
      if (v) {
        state.vehicle = v;
        container.querySelectorAll('.vehicle-btn').forEach(b => {
          b.classList.remove('btn-primary');
          b.classList.add('btn-ghost');
        });
        btn.classList.remove('btn-ghost');
        btn.classList.add('btn-primary');
      }
    });
  });

  // Collapsible Advanced Settings
  const toggleAdv = container.querySelector('#toggle-advanced');
  const advPanel = container.querySelector('#advanced-panel');
  if (toggleAdv && advPanel) {
    toggleAdv.addEventListener('click', () => {
      state.isAdvancedOpen = !state.isAdvancedOpen;
      advPanel.style.display = state.isAdvancedOpen ? 'grid' : 'none';
      const chevron = toggleAdv.querySelector('#advanced-chevron');
      if (chevron) {
        chevron.setAttribute('data-lucide', state.isAdvancedOpen ? 'chevron-up' : 'chevron-down');
        if (window.lucide) window.lucide.createIcons();
      }
    });
  }

  // Read overrides inputs
  ['rate-km', 'fee-pct', 'spoil-rate', 'loading-rate'].forEach(key => {
    const el = container.querySelector(`#override-${key}`);
    if (el) {
      el.addEventListener('input', (e) => {
        const field = key.replace('-', '_');
        state.overrides[field] = e.target.value;
      });
    }
  });

  // Submit Advice Button
  const btnSubmit = container.querySelector('#btn-submit');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', () => executeAdvisory(container));
  }

  // Try Demo Button (1-Click Tomato + Pune + 20q)
  const btnDemo = container.querySelector('#btn-demo');
  if (btnDemo) {
    btnDemo.addEventListener('click', () => {
      // 1. Set pre-fill values
      state.selectedCrop = 'Tomato';
      state.selectedDistrict = 'Pune';
      state.quantity = 20.0;
      state.vehicle = 'tempo';

      // 2. Update form DOM
      container.querySelectorAll('#crop-chips .chip').forEach(c => {
        if (c.getAttribute('data-crop') === 'Tomato') c.classList.add('active');
        else c.classList.remove('active');
      });

      if (districtSelect) districtSelect.value = 'Pune';
      if (qtyInput) qtyInput.value = 20;

      container.querySelectorAll('.vehicle-btn').forEach(b => {
        if (b.getAttribute('data-vehicle') === 'tempo') {
          b.classList.remove('btn-ghost');
          b.classList.add('btn-primary');
        } else {
          b.classList.remove('btn-primary');
          b.classList.add('btn-ghost');
        }
      });

      if (window.showToast) {
        window.showToast('Pre-filled Demo: Tomato • Pune • 20 Quintals • Tempo', 'info');
      }

      // 3. Immediately execute calculation
      executeAdvisory(container);
    });
  }
}

// Fetch live backend data source status
async function fetchDataStatus(container) {
  try {
    const status = await api.getDataStatus();
    state.dataStatus = status;

    const badgeContainer = container.querySelector('#data-status-badge');
    if (badgeContainer && status) {
      const source = status.source || 'snapshot';
      let badgeClass = 'badge-sky';
      let iconName = 'database';
      let labelText = t('data_source_snapshot');

      if (source === 'live') {
        badgeClass = 'badge-green';
        iconName = 'radio';
        labelText = t('data_source_live');
      } else if (source === 'sample') {
        badgeClass = 'badge-yellow';
        iconName = 'alert-triangle';
        labelText = t('data_source_sample');
      }

      badgeContainer.innerHTML = `
        <span class="badge ${badgeClass}" title="Total Records: ${status.total_records || 5514} • Mandis: ${status.monitored_mandis || 20}">
          <i data-lucide="${iconName}" style="width: 14px; height: 14px;"></i>
          <span>${labelText}</span>
          <span style="font-weight: 400; opacity: 0.85;">(${status.total_records} rows • ${status.latest_date})</span>
        </span>
      `;
      if (window.lucide) window.lucide.createIcons();
    }
  } catch (err) {
    console.warn('Data status fetch error:', err);
  }
}

// Fetch mandis metadata for district list
async function fetchMandis(container) {
  try {
    const res = await api.getMandis();
    if (res && res.mandis && res.mandis.length > 0) {
      const uniqueDistricts = [...new Set(res.mandis.map(m => m.district).filter(Boolean))].sort();
      if (uniqueDistricts.length > 0) {
        state.districts = uniqueDistricts;
        const select = container.querySelector('#district-select');
        if (select) {
          const currentVal = select.value || state.selectedDistrict;
          select.innerHTML = state.districts.map(d => `
            <option value="${d}" ${d.toLowerCase() === currentVal.toLowerCase() ? 'selected' : ''}>${d} District</option>
          `).join('');
        }
      }
    }
  } catch (err) {
    console.warn('Mandis fetch error:', err);
  }
}

// Execute advisory calculation & load results
async function executeAdvisory(container) {
  const resultsDiv = container.querySelector('#results-container');
  if (!resultsDiv) return;

  // Show Loading Skeleton
  resultsDiv.innerHTML = `
    <div class="card" style="padding: 32px; text-align: center; margin-bottom: 24px;">
      <div style="width: 56px; height: 56px; border-radius: 50%; border: 3px solid var(--border); border-top-color: var(--primary-dark); animation: spin 1s linear infinite; margin: 0 auto 16px;"></div>
      <h3 style="font-size: 1.15rem; margin-bottom: 8px;" data-i18n="loading_calculating">
        ${t('loading_calculating')}
      </h3>
      <p style="color: var(--muted); font-size: 0.9rem;">
        Computing Haversine road transit, 12:00 PM cutoff, loading labor, and APMC modal spreads.
      </p>
    </div>
    <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
  `;

  // Build Payload
  const overrides = {};
  if (state.overrides.rate_per_km) overrides.rate_per_km = parseFloat(state.overrides.rate_per_km);
  if (state.overrides.market_fee_percent) overrides.market_fee_percent = parseFloat(state.overrides.market_fee_percent);
  if (state.overrides.spoilage_rate) overrides.spoilage_rate = parseFloat(state.overrides.spoilage_rate);
  if (state.overrides.loading_per_quintal) overrides.loading_per_quintal = parseFloat(state.overrides.loading_per_quintal);

  const payload = {
    crop: state.selectedCrop,
    district: state.selectedDistrict,
    quantity: state.quantity,
    vehicle: state.vehicle,
    departure_hour: state.departureHour,
    overrides: Object.keys(overrides).length > 0 ? overrides : undefined
  };

  try {
    // 1. Primary advisory call
    const advisory = await api.calculateAdvise(payload);
    state.advisoryResult = advisory;

    const topMandi = advisory.best_recommendation ? advisory.best_recommendation.market : 'Pune';

    // 2. Concurrently fetch 5-day forecast & sell-or-store advice
    try {
      const [forecast, storage] = await Promise.all([
        api.getForecast(state.selectedCrop, topMandi).catch(() => null),
        api.getStorageAdvice(state.selectedCrop, topMandi).catch(() => null)
      ]);
      state.forecastResult = forecast;
      state.storageResult = storage;
    } catch (_) {
      // Forecast/storage errors gracefully tolerated
    }

    // Render completed results
    renderResults(container);

    // Scroll smoothly to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    if (window.showToast) {
      window.showToast(`Found best market: ${topMandi}!`, 'success');
    }
  } catch (err) {
    console.error('Advisory execution failed:', err);
    resultsDiv.innerHTML = `
      <div class="card" style="padding: 24px; text-align: center; border: 1.5px solid var(--red-soft);">
        <div class="badge badge-red" style="margin-bottom: 10px;">Calculation Error</div>
        <h3>Unable to calculate advisory</h3>
        <p style="color: var(--muted); margin: 8px 0 16px;">${err.message || 'Please check your connection and parameters.'}</p>
        <button type="button" class="btn btn-primary" id="btn-retry-advise">
          <i data-lucide="rotate-cw"></i> Try Again
        </button>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
    const btnRetry = resultsDiv.querySelector('#btn-retry-advise');
    if (btnRetry) btnRetry.addEventListener('click', () => executeAdvisory(container));
  }
}

// Render Results Presentation Screen
function renderResults(container) {
  const resultsDiv = container.querySelector('#results-container');
  if (!resultsDiv || !state.advisoryResult) return;

  const res = state.advisoryResult;
  const best = res.best_recommendation;

  if (!best) {
    resultsDiv.innerHTML = `
      <div class="card" style="text-align: center; padding: 32px;">
        <h3>No active market trading found for ${state.selectedCrop}</h3>
        <p style="color: var(--muted); margin-top: 8px;">Please select another crop or district.</p>
      </div>
    `;
    return;
  }

  const isLocal = best.is_nearest || best.gain_vs_nearest_per_quintal <= 0;
  const gainText = best.gain_vs_nearest_per_quintal > 0
    ? `+₹${best.gain_vs_nearest_per_quintal.toFixed(2)}/q extra`
    : `Local Nearest Market`;

  resultsDiv.innerHTML = `
    <!-- Top Hero Recommendation Card -->
    <div class="card" style="background: linear-gradient(145deg, #FFFFFF 0%, var(--bg) 100%); border: 2px solid var(--primary); padding: 28px; margin-bottom: 24px; box-shadow: var(--shadow-md);">
      
      <!-- Card Header -->
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge badge-green">
              <i data-lucide="award" style="width: 14px; height: 14px;"></i>
              <span data-i18n="results_hero_title">${t('results_hero_title')}</span>
            </span>
            <span class="badge ${best.confidence === 'HIGH' ? 'badge-green' : best.confidence === 'MEDIUM' ? 'badge-sky' : 'badge-yellow'}">
              ${best.confidence} Confidence
            </span>
            ${best.missed_cutoff ? `<span class="badge badge-peach">Auction Day+1</span>` : `<span class="badge badge-green">Today's Auction</span>`}
          </div>
          <h2 style="font-size: 2rem; font-weight: 700; color: var(--text); margin: 4px 0;">
            ${best.market} <span style="font-size: 1.1rem; font-weight: 500; color: var(--muted);">(${best.district})</span>
          </h2>
        </div>

        <!-- Voice Audio Button -->
        <button type="button" class="btn btn-ghost" id="btn-voice-listen" style="border-radius: var(--radius-pill); border-color: var(--primary); color: var(--primary-dark); font-weight: 600;">
          <i data-lucide="volume-2"></i>
          <span id="voice-btn-text" data-i18n="btn_listen">${t('btn_listen')}</span>
        </button>
      </div>

      <!-- Financial Highlight Numbers -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; padding: 20px; background: #FFFFFF; border-radius: var(--radius-md); border: 1px solid var(--border);">
        <div>
          <div style="font-size: 0.85rem; color: var(--muted); margin-bottom: 4px;" data-i18n="results_net_return">${t('results_net_return')}</div>
          <div style="font-size: 2rem; font-weight: 700; color: #2E7D32;">
            ₹${best.net_return_per_quintal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span style="font-size: 0.9rem; font-weight: 500; color: var(--muted);">/quintal</span>
          </div>
          <div style="font-size: 0.8rem; font-weight: 600; color: ${best.gain_vs_nearest_per_quintal > 0 ? '#2E7D32' : 'var(--muted)'}; margin-top: 4px;">
            ${gainText}
          </div>
        </div>

        <div>
          <div style="font-size: 0.85rem; color: var(--muted); margin-bottom: 4px;" data-i18n="results_total_earnings">${t('results_total_earnings')}</div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--text);">
            ₹${best.total_net_earnings.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </div>
          <div style="font-size: 0.8rem; color: var(--muted); margin-top: 4px;">
            For your ${state.quantity} quintals batch
          </div>
        </div>
      </div>

      <!-- One-line verdict reasoning -->
      <div style="background: var(--primary-light); border-left: 4px solid var(--primary-dark); padding: 12px 16px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: 500; color: var(--text); font-size: 0.95rem; margin: 0;">
          ${best.verdict_reason}
        </p>
      </div>

      <!-- Cost Breakdown Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; font-size: 0.85rem;">
        <div style="background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border);">
          <div style="color: var(--muted);" data-i18n="results_gross_price">${t('results_gross_price')}</div>
          <div style="font-weight: 600; font-size: 1rem;">₹${best.gross_modal_price}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border);">
          <div style="color: var(--muted);">Freight / q</div>
          <div style="font-weight: 600; font-size: 1rem; color: #C62828;">-₹${best.costs.transport_per_q}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border);">
          <div style="color: var(--muted);">Labor & Fee / q</div>
          <div style="font-weight: 600; font-size: 1rem; color: #C62828;">-₹${(best.costs.loading_unloading_per_q + best.costs.market_fee_per_q).toFixed(2)}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border);">
          <div style="color: var(--muted);">Distance</div>
          <div style="font-weight: 600; font-size: 1rem;">${best.distance_km} km</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border);">
          <div style="color: var(--muted);">Arrival Time</div>
          <div style="font-weight: 600; font-size: 1rem;">${best.arrival_time}</div>
        </div>
      </div>

    </div>

    <!-- Break-Even Price Advice Box -->
    ${best.break_even_price && !best.is_nearest ? `
      <div class="card" style="border-left: 5px solid #0277BD; background: var(--sky); padding: 18px 24px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <i data-lucide="scale" style="color: #0277BD; width: 20px; height: 20px;"></i>
          <h4 style="font-size: 1rem; font-weight: 600; color: #0277BD; margin: 0;" data-i18n="results_breakeven_title">
            ${t('results_breakeven_title')}
          </h4>
        </div>
        <p style="font-size: 0.9rem; color: var(--text); margin: 0;">
          Traveling to <strong>${best.market}</strong> pays off only if the market price exceeds 
          <strong>₹${best.break_even_price}/q</strong>. Any price below this makes selling at your local 
          <strong>${res.nearest_baseline}</strong> market more profitable after fuel costs.
        </p>
      </div>
    ` : ''}

    <!-- 5-Day Price Forecast Corridor -->
    ${state.forecastResult && state.forecastResult.forecast && state.forecastResult.forecast.length > 0 ? `
      <div class="card" style="padding: 24px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div>
            <h3 style="font-size: 1.15rem; font-weight: 600; margin: 0;" data-i18n="results_forecast_title">
              ${t('results_forecast_title')}
            </h3>
            <p style="color: var(--muted); font-size: 0.85rem; margin-top: 2px;">
              5-Day low ≤ likely ≤ high corridor for ${state.selectedCrop} in ${best.market}
            </p>
          </div>
          <span class="badge ${state.forecastResult.trend === 'BULLISH' ? 'badge-green' : state.forecastResult.trend === 'BEARISH' ? 'badge-red' : 'badge-sky'}">
            ${state.forecastResult.trend}
          </span>
        </div>

        <!-- Corridor Table -->
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
            <thead>
              <tr style="border-bottom: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;">
                <th style="padding: 8px;">Day</th>
                <th style="padding: 8px;">Date</th>
                <th style="padding: 8px; text-align: right;">Low Bound</th>
                <th style="padding: 8px; text-align: right; color: var(--primary-dark); font-weight: 600;">Likely Price</th>
                <th style="padding: 8px; text-align: right;">High Bound</th>
              </tr>
            </thead>
            <tbody>
              ${state.forecastResult.forecast.map(f => `
                <tr style="border-bottom: 1px solid #F0F6F2;">
                  <td style="padding: 10px 8px; font-weight: 500;">${f.day} (${f.weekday})</td>
                  <td style="padding: 10px 8px; color: var(--muted);">${f.date}</td>
                  <td style="padding: 10px 8px; text-align: right; color: #C62828;">₹${f.low.toFixed(2)}</td>
                  <td style="padding: 10px 8px; text-align: right; font-weight: 700; color: #2E7D32;">₹${f.likely.toFixed(2)}</td>
                  <td style="padding: 10px 8px; text-align: right; color: #0277BD;">₹${f.high.toFixed(2)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    ` : ''}

    <!-- Sell or Store Decision Card -->
    ${state.storageResult ? `
      <div class="card" style="padding: 24px; margin-bottom: 24px; border-left: 5px solid ${state.storageResult.recommendation === 'Sell now' ? '#FFB74D' : '#81C784'};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 1.1rem; font-weight: 600; margin: 0;" data-i18n="results_storage_title">
            ${t('results_storage_title')}
          </h3>
          <span class="badge ${state.storageResult.recommendation === 'Sell now' ? 'badge-yellow' : 'badge-green'}" style="font-size: 0.9rem; padding: 6px 14px;">
            ${state.storageResult.recommendation}
          </span>
        </div>
        <p style="font-size: 0.95rem; color: var(--text); margin: 0;">
          ${state.storageResult.rationale}
        </p>
      </div>
    ` : ''}

    <!-- Ranked Mandi Comparison Table -->
    ${res.comparisons && res.comparisons.length > 0 ? `
      <div class="card" style="padding: 24px; margin-bottom: 24px;">
        <h3 style="font-size: 1.15rem; font-weight: 600; margin-bottom: 16px;" data-i18n="results_comparisons_title">
          ${t('results_comparisons_title')}
        </h3>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); color: var(--muted); font-size: 0.8rem;">
                <th style="padding: 10px 8px;" data-i18n="table_mandi">${t('table_mandi')}</th>
                <th style="padding: 10px 8px;">Distance</th>
                <th style="padding: 10px 8px; text-align: right;" data-i18n="table_modal">${t('table_modal')}</th>
                <th style="padding: 10px 8px; text-align: right;" data-i18n="table_deductions">${t('table_deductions')}</th>
                <th style="padding: 10px 8px; text-align: right; font-weight: 600;" data-i18n="table_net">${t('table_net')}</th>
                <th style="padding: 10px 8px;" data-i18n="table_verdict">${t('table_verdict')}</th>
              </tr>
            </thead>
            <tbody>
              ${res.comparisons.slice(0, 7).map(m => `
                <tr style="border-bottom: 1px solid #F0F6F2;">
                  <td style="padding: 12px 8px;">
                    <div style="font-weight: 600;">${m.market}</div>
                    <div style="font-size: 0.75rem; color: var(--muted);">${m.district}</div>
                  </td>
                  <td style="padding: 12px 8px; color: var(--muted);">${m.distance_km} km</td>
                  <td style="padding: 12px 8px; text-align: right;">₹${m.gross_modal_price}</td>
                  <td style="padding: 12px 8px; text-align: right; color: #C62828;">-₹${m.costs.total_deductions_per_q}</td>
                  <td style="padding: 12px 8px; text-align: right; font-weight: 700; color: #2E7D32;">₹${m.net_return_per_quintal}</td>
                  <td style="padding: 12px 8px; font-size: 0.8rem; color: var(--muted); max-width: 240px;">
                    ${m.verdict_reason}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    ` : ''}
  `;

  // Bind Listen to Advice Voice Synthesis button
  const btnVoice = resultsDiv.querySelector('#btn-voice-listen');
  if (btnVoice) {
    btnVoice.addEventListener('click', () => speakAdvice(best, res.nearest_baseline));
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Spoken voice advice synthesis in Marathi, Hindi, or English
function speakAdvice(best, nearest) {
  if (!window.speechSynthesis) {
    if (window.showToast) window.showToast('Voice synthesis not supported in this browser.', 'error');
    return;
  }

  const lang = getLanguage();
  let speechText = '';

  if (lang === 'mr') {
    speechText = `शेतकरी मित्रांनो, ${state.selectedCrop} पिकासाठी सर्वात फायदेशीर बाजार ${best.market} आहे. ` +
      `येथे वाहतूक खर्च वजा जाता तुमच्या खिशात प्रति क्विंटल निव्वळ ${Math.round(best.net_return_per_quintal)} रुपये नफा राहील. ` +
      `${best.verdict_reason}`;
  } else if (lang === 'hi') {
    speechText = `किसान भाइयो, ${state.selectedCrop} के लिए सबसे अच्छी मंडी ${best.market} है। ` +
      `यहाँ भाड़ा घटाकर आपकी जेब में प्रति क्विंटल शुद्ध ${Math.round(best.net_return_per_quintal)} रुपये बचेंगे। ` +
      `${best.verdict_reason}`;
  } else {
    speechText = `Farmer friends, for ${state.selectedCrop}, the highest net return market is ${best.market}. ` +
      `Your pocket earnings after transport deductions will be Rs ${Math.round(best.net_return_per_quintal)} per quintal. ` +
      `${best.verdict_reason}`;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(speechText);
  utterance.lang = lang === 'mr' ? 'mr-IN' : lang === 'hi' ? 'hi-IN' : 'en-IN';
  utterance.rate = 0.95;

  const btnVoice = document.querySelector('#btn-voice-listen');
  const btnText = document.querySelector('#voice-btn-text');

  utterance.onstart = () => {
    if (btnText) btnText.textContent = t('btn_speaking');
    if (btnVoice) btnVoice.classList.add('active');
  };

  utterance.onend = () => {
    if (btnText) btnText.textContent = t('btn_listen');
    if (btnVoice) btnVoice.classList.remove('active');
  };

  utterance.onerror = () => {
    if (btnText) btnText.textContent = t('btn_listen');
    if (btnVoice) btnVoice.classList.remove('active');
  };

  window.speechSynthesis.speak(utterance);
}
