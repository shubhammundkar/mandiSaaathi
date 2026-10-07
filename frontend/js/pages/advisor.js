// Mandi Saathi - Advisor Page
// Full recommendation interface with:
// - Top Recommendation Hero Card (Net Return, total profit, confidence & freshness badges)
// - Ranked Mandi Cards with visual Min/Modal/Max bar, distance, travel time, and freight
// - Break-Even threshold note
// - Chart.js 5-Day Low/Likely/High Price Outlook with Sell-or-Store Verdict Chip
// - Trilingual Web Speech API Listen button (MR/HI/EN)
// - "Estimates, not guarantees" Disclaimer
// - Shimmer skeleton loading, empty, and error states

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

// Persistent UI state
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
  chartInstance: null
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

  // Load live data status, crops, & mandis list
  fetchDataStatus(container);
  fetchCrops(container);
  fetchMandis(container, state.selectedCrop);

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
          state.selectedDistrict = cropMeta.defaultDistrict;
        }
        // Dynamically reload districts for this crop from API
        fetchMandis(container, crop);
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

// Fetch mandis metadata for district list from /api/mandis?crop=...
async function fetchMandis(container, crop = '') {
  try {
    const res = await api.getMandis(crop);
    if (res && res.mandis && res.mandis.length > 0) {
      const uniqueDistricts = [...new Set(res.mandis.map(m => m.district).filter(Boolean))].sort();
      if (uniqueDistricts.length > 0) {
        state.districts = uniqueDistricts;
        const select = container.querySelector('#district-select');
        if (select) {
          const currentVal = select.value || state.selectedDistrict;
          const matchVal = state.districts.find(d => d.toLowerCase() === currentVal.toLowerCase()) || state.districts[0];
          state.selectedDistrict = matchVal;
          select.innerHTML = state.districts.map(d => `
            <option value="${d}" ${d.toLowerCase() === matchVal.toLowerCase() ? 'selected' : ''}>${d} District</option>
          `).join('');
        }
      }
    }
  } catch (err) {
    console.warn('Mandis fetch error:', err);
  }
}

// Fetch monitored crops metadata from /api/crops
async function fetchCrops(container) {
  try {
    const res = await api.getCrops();
    if (res && res.crops && res.crops.length > 0) {
      console.log('Real crops loaded from /api/crops:', res.crops.length, 'commodities');
    }
  } catch (err) {
    console.warn('Crops fetch error:', err);
  }
}

// Shimmer Skeleton Loading State
function renderLoadingSkeleton(resultsDiv) {
  resultsDiv.innerHTML = `
    <div class="card" style="padding: 32px; margin-bottom: 24px;">
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
        <div class="skeleton skeleton-circle" style="width: 56px; height: 56px;"></div>
        <div style="flex: 1;">
          <div class="skeleton skeleton-text" style="width: 45%; height: 22px;"></div>
          <div class="skeleton skeleton-text" style="width: 65%; height: 16px;"></div>
        </div>
      </div>
      <div class="skeleton skeleton-card" style="height: 90px; margin-bottom: 16px;"></div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 20px;">
        <div class="skeleton" style="height: 60px;"></div>
        <div class="skeleton" style="height: 60px;"></div>
        <div class="skeleton" style="height: 60px;"></div>
        <div class="skeleton" style="height: 60px;"></div>
      </div>
      <div style="text-align: center; color: var(--muted); font-size: 0.95rem;">
        <span data-i18n="loading_calculating">${t('loading_calculating')}</span>
      </div>
    </div>
  `;
}

// Clean Empty State
function renderEmptyState(resultsDiv, crop, district) {
  resultsDiv.innerHTML = `
    <div class="card" style="text-align: center; padding: 48px 24px; margin-bottom: 24px;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--yellow); color: #8D6E12; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
        <i data-lucide="package-search" style="width: 32px; height: 32px;"></i>
      </div>
      <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 8px;" data-i18n="empty_title">
        ${t('empty_title')}
      </h3>
      <p style="color: var(--muted); max-width: 520px; margin: 0 auto 20px; font-size: 0.95rem;" data-i18n="empty_text">
        ${t('empty_text')}
      </p>
      <div style="display: inline-flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
        <span class="badge badge-sky">${crop}</span>
        <span class="badge badge-sky">${district} District</span>
      </div>
    </div>
  `;
  if (window.lucide) window.lucide.createIcons();
}

// Clean Error State with Retry
function renderErrorState(resultsDiv, errorMessage, container) {
  const isNetworkOrDown = !errorMessage || 
    errorMessage.toLowerCase().includes('failed to fetch') ||
    errorMessage.toLowerCase().includes('network') ||
    errorMessage.toLowerCase().includes('connection') ||
    errorMessage.toLowerCase().includes('timed out');

  const titleText = isNetworkOrDown ? t('error_title') : 'Calculation Error';
  const descText = isNetworkOrDown ? t('error_server_down') : errorMessage;

  resultsDiv.innerHTML = `
    <div class="card" style="padding: 32px 20px; text-align: center; border: 1.5px solid var(--red-soft); margin-bottom: 24px;">
      <div style="width: 56px; height: 56px; border-radius: 50%; background: var(--red-soft); color: #C62828; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
        <i data-lucide="${isNetworkOrDown ? 'wifi-off' : 'alert-octagon'}" style="width: 28px; height: 28px;"></i>
      </div>
      <div class="badge badge-red" style="margin-bottom: 10px;">
        ${isNetworkOrDown ? 'Connection Notice' : 'Advisory Engine Notice'}
      </div>
      <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 8px;">
        ${titleText}
      </h3>
      <p style="color: var(--muted); max-width: 480px; margin: 0 auto 20px; font-size: 0.95rem; line-height: 1.5;">
        ${descText}
      </p>
      <button type="button" class="btn btn-primary" id="btn-retry-advise" style="margin: 0 auto;">
        <i data-lucide="rotate-cw"></i>
        <span data-i18n="btn_retry">${t('btn_retry')}</span>
      </button>
    </div>
  `;
  if (window.lucide) window.lucide.createIcons();
  const btnRetry = resultsDiv.querySelector('#btn-retry-advise');
  if (btnRetry) btnRetry.addEventListener('click', () => executeAdvisory(container));
}

// Helper: Freshness Badge
function getFreshnessBadge(daysAgo, arrivalDate) {
  const days = typeof daysAgo === 'number' ? daysAgo : 0;
  if (days <= 1) {
    return `
      <span class="badge badge-green" title="Reported: ${arrivalDate || 'Today'}">
        <i data-lucide="check-circle" style="width: 12px; height: 12px;"></i>
        <span data-i18n="freshness_fresh">${t('freshness_fresh')}</span>
      </span>
    `;
  } else if (days <= 3) {
    return `
      <span class="badge badge-yellow" title="Reported: ${arrivalDate || `${days}d ago`}">
        <i data-lucide="clock" style="width: 12px; height: 12px;"></i>
        <span data-i18n="freshness_moderate">${t('freshness_moderate')}</span>
      </span>
    `;
  } else {
    return `
      <span class="badge badge-red" title="Reported: ${arrivalDate || `${days}d ago`}">
        <i data-lucide="alert-triangle" style="width: 12px; height: 12px;"></i>
        <span data-i18n="freshness_stale">${t('freshness_stale')}</span>
      </span>
    `;
  }
}

// Helper: Min / Modal / Max graphical price bar
function renderPriceBar(minPrice, modalPrice, maxPrice) {
  const min = typeof minPrice === 'number' && minPrice > 0 ? minPrice : (modalPrice * 0.9);
  const modal = modalPrice;
  const max = typeof maxPrice === 'number' && maxPrice >= modal ? maxPrice : (modalPrice * 1.1);
  const span = Math.max(1, max - min);
  const dotPct = Math.max(4, Math.min(96, ((modal - min) / span) * 100));

  return `
    <div class="price-bar-container">
      <div class="price-bar-labels">
        <span>Min ₹${min.toFixed(0)}</span>
        <span style="font-weight: 600; color: #2E7D32;">Modal ₹${modal.toFixed(0)}</span>
        <span>Max ₹${max.toFixed(0)}</span>
      </div>
      <div class="price-range-track">
        <div class="price-range-span" style="left: 0%; width: 100%;"></div>
        <div class="price-range-dot" style="left: ${dotPct}%;" title="Modal Price: ₹${modal.toFixed(2)}"></div>
      </div>
    </div>
  `;
}

// Helper: Sell-or-Store Verdict Chip
function getStorageVerdictChip(storageResult) {
  if (!storageResult) return '';
  const rec = storageResult.recommendation || 'Sell now';
  let badgeClass = 'badge-yellow';
  if (rec.toLowerCase().includes('wait')) {
    badgeClass = 'badge-green';
  } else if (rec.toLowerCase().includes('not enough')) {
    badgeClass = 'badge-sky';
  }
  return `<span class="badge ${badgeClass}" style="font-size: 0.85rem; padding: 4px 12px;">${rec}</span>`;
}

// Execute advisory calculation & load results
async function executeAdvisory(container) {
  const resultsDiv = container.querySelector('#results-container');
  if (!resultsDiv) return;

  // Show Skeleton Loading State
  renderLoadingSkeleton(resultsDiv);

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
      // Tolerated gracefully
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
    renderErrorState(resultsDiv, err.message, container);
  }
}

// Render Results Presentation Screen
function renderResults(container) {
  const resultsDiv = container.querySelector('#results-container');
  if (!resultsDiv || !state.advisoryResult) return;

  const res = state.advisoryResult;
  const best = res.best_recommendation;

  if (!best) {
    renderEmptyState(resultsDiv, state.selectedCrop, state.selectedDistrict);
    return;
  }

  const isLocal = best.is_nearest || best.gain_vs_nearest_per_quintal <= 0;
  const gainText = best.gain_vs_nearest_per_quintal > 0
    ? `+₹${best.gain_vs_nearest_per_quintal.toFixed(2)}/q extra`
    : `Local Nearest Market`;

  // Combine top recommendation and comparison list for ranked cards
  const allRanked = [best, ...(res.comparisons || [])];

  resultsDiv.innerHTML = `
    <!-- 1. Best Option Hero Card -->
    <div class="card" style="background: linear-gradient(145deg, #FFFFFF 0%, var(--bg) 100%); border: 2.5px solid var(--primary-dark); padding: clamp(16px, 4vw, 28px); margin-bottom: 24px; box-shadow: var(--shadow-md); overflow: hidden; word-break: break-word;">
      
      <!-- Card Header -->
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px;">
        <div style="max-width: 100%;">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px;">
            <span class="badge badge-green" style="font-size: 0.85rem; padding: 4px 14px;">
              <i data-lucide="award" style="width: 14px; height: 14px;"></i>
              <span data-i18n="results_hero_title">${t('results_hero_title')}</span>
            </span>
            <span class="badge ${best.confidence === 'HIGH' ? 'badge-green' : best.confidence === 'MEDIUM' ? 'badge-sky' : 'badge-yellow'}">
              ${best.confidence} Confidence
            </span>
            ${getFreshnessBadge(best.days_ago, best.arrival_date)}
            ${best.missed_cutoff ? `<span class="badge badge-peach">Auction Day+1</span>` : `<span class="badge badge-green">Today's Auction</span>`}
          </div>
          <h2 style="font-size: clamp(1.4rem, 5vw, 2.2rem); font-weight: 700; color: var(--text); margin: 4px 0; word-break: break-word;">
            ${best.market} <span style="font-size: clamp(0.95rem, 3.5vw, 1.15rem); font-weight: 500; color: var(--muted);">(${best.district} District)</span>
          </h2>
        </div>

        <!-- Voice Audio Button -->
        <button type="button" class="btn btn-ghost" id="btn-voice-listen" style="border-radius: var(--radius-pill); border: 1.5px solid var(--primary-dark); color: var(--primary-dark); font-weight: 600; padding: 8px 16px; font-size: 0.9rem;">
          <i data-lucide="volume-2"></i>
          <span id="voice-btn-text" data-i18n="btn_listen">${t('btn_listen')}</span>
        </button>
      </div>

      <!-- Financial Numbers Highlight -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; margin: 18px 0; padding: clamp(14px, 3vw, 20px); background: #FFFFFF; border-radius: var(--radius-md); border: 1px solid var(--border);">
        <div>
          <div style="font-size: 0.85rem; color: var(--muted); margin-bottom: 4px;" data-i18n="results_net_return">${t('results_net_return')}</div>
          <div style="font-size: clamp(1.4rem, 5vw, 2.1rem); font-weight: 700; color: #2E7D32;">
            ₹${best.net_return_per_quintal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span style="font-size: 0.85rem; font-weight: 500; color: var(--muted);">/q</span>
          </div>
          <div style="font-size: 0.8rem; font-weight: 600; color: ${best.gain_vs_nearest_per_quintal > 0 ? '#2E7D32' : 'var(--muted)'}; margin-top: 4px;">
            ${gainText}
          </div>
        </div>

        <div>
          <div style="font-size: 0.85rem; color: var(--muted); margin-bottom: 4px;" data-i18n="results_total_earnings">${t('results_total_earnings')}</div>
          <div style="font-size: clamp(1.4rem, 5vw, 2.1rem); font-weight: 700; color: var(--text);">
            ₹${best.total_net_earnings.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </div>
          <div style="font-size: 0.8rem; color: var(--muted); margin-top: 4px;">
            For your ${state.quantity} quintals batch
          </div>
        </div>
      </div>

      <!-- One-line verdict reasoning -->
      <div style="background: var(--primary-light); border-left: 4px solid var(--primary-dark); padding: 12px 16px; border-radius: 4px; margin-bottom: 18px; word-break: break-word;">
        <p style="font-weight: 500; color: var(--text); font-size: 0.95rem; margin: 0; line-height: 1.45;">
          ${best.verdict_reason}
        </p>
      </div>

      <!-- Cost Breakdown Tags -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(95px, 1fr)); gap: 8px; font-size: 0.85rem;">
        <div style="background: #FFFFFF; padding: 10px 8px; border-radius: var(--radius-sm); border: 1px solid var(--border); text-align: center;">
          <div style="color: var(--muted); font-size: 0.75rem;" data-i18n="results_gross_price">${t('results_gross_price')}</div>
          <div style="font-weight: 600; font-size: 0.95rem;">₹${best.gross_modal_price.toFixed(2)}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px 8px; border-radius: var(--radius-sm); border: 1px solid var(--border); text-align: center;">
          <div style="color: var(--muted); font-size: 0.75rem;">Transport / q</div>
          <div style="font-weight: 600; font-size: 0.95rem; color: #C62828;">-₹${best.costs.transport_per_q.toFixed(2)}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px 8px; border-radius: var(--radius-sm); border: 1px solid var(--border); text-align: center;">
          <div style="color: var(--muted); font-size: 0.75rem;">Fees & Labor</div>
          <div style="font-weight: 600; font-size: 0.95rem; color: #C62828;">-₹${(best.costs.loading_unloading_per_q + best.costs.market_fee_per_q).toFixed(2)}</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px 8px; border-radius: var(--radius-sm); border: 1px solid var(--border); text-align: center;">
          <div style="color: var(--muted); font-size: 0.75rem;">Distance</div>
          <div style="font-weight: 600; font-size: 0.95rem;">${best.distance_km} km</div>
        </div>
        <div style="background: #FFFFFF; padding: 10px 8px; border-radius: var(--radius-sm); border: 1px solid var(--border); text-align: center;">
          <div style="color: var(--muted); font-size: 0.75rem;">Arrival</div>
          <div style="font-weight: 600; font-size: 0.95rem;">${best.arrival_time}</div>
        </div>
      </div>

    </div>

    <!-- 2. Break-Even Price Threshold Note -->
    ${best.break_even_price && !best.is_nearest ? `
      <div class="card" style="border-left: 5px solid #0277BD; background: var(--sky); padding: 18px 24px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <i data-lucide="scale" style="color: #0277BD; width: 20px; height: 20px;"></i>
          <h4 style="font-size: 1rem; font-weight: 600; color: #0277BD; margin: 0;" data-i18n="results_breakeven_title">
            ${t('results_breakeven_title')}
          </h4>
        </div>
        <p style="font-size: 0.95rem; color: var(--text); margin: 0;">
          Traveling to <strong>${best.market}</strong> pays off only if the market price exceeds 
          <strong>₹${best.break_even_price}/q</strong>. Any price below this makes selling at your local 
          <strong>${res.nearest_baseline}</strong> market more profitable after transport costs.
        </p>
      </div>
    ` : `
      <div class="card" style="border-left: 5px solid #2E7D32; background: #E8F5E9; padding: 16px 20px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <i data-lucide="check-circle" style="color: #2E7D32; width: 18px; height: 18px;"></i>
          <h4 style="font-size: 0.95rem; font-weight: 600; color: #2E7D32; margin: 0;">Local Market Optimal</h4>
        </div>
        <p style="font-size: 0.9rem; color: var(--text); margin: 0;">
          Selling at your nearest APMC (<strong>${best.market}</strong>) eliminates distant freight costs. Regional premiums elsewhere do not justify traveling.
        </p>
      </div>
    `}

    <!-- 3. Chart.js 5-Day Low/Likely/High Outlook Chart with Verdict Chip -->
    ${state.forecastResult && state.forecastResult.forecast && state.forecastResult.forecast.length > 0 ? `
      <div class="card" style="padding: 24px; margin-bottom: 24px;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px;">
              <h3 style="font-size: 1.15rem; font-weight: 600; margin: 0;" data-i18n="results_forecast_title">
                ${t('results_forecast_title')}
              </h3>
              ${getStorageVerdictChip(state.storageResult)}
            </div>
            <p style="color: var(--muted); font-size: 0.85rem; margin-top: 2px;">
              5-Day rolling price corridor for ${state.selectedCrop} in ${best.market} (Low ≤ Likely ≤ High)
            </p>
          </div>
          <span class="badge ${state.forecastResult.trend === 'BULLISH' ? 'badge-green' : state.forecastResult.trend === 'BEARISH' ? 'badge-red' : 'badge-sky'}">
            ${state.forecastResult.trend}
          </span>
        </div>

        <!-- Chart.js Canvas -->
        <div style="position: relative; height: 260px; width: 100%; margin-bottom: 14px;">
          <canvas id="forecast-chart"></canvas>
        </div>

        <!-- Sell or Store Decision Note -->
        ${state.storageResult ? `
          <div style="background: #F8FAF8; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px 16px; font-size: 0.9rem;">
            <div style="font-weight: 600; color: var(--text); margin-bottom: 2px;" data-i18n="results_storage_title">${t('results_storage_title')}</div>
            <p style="color: var(--muted); margin: 0;">
              ${state.storageResult.rationale}
            </p>
          </div>
        ` : ''}

      </div>
    ` : ''}

    <!-- 4. Ranked Mandi Cards with Min/Modal/Max Bars -->
    <div style="margin-bottom: 24px;">
      <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 16px;" data-i18n="results_comparisons_title">
        ${t('results_comparisons_title')}
      </h3>

      <div style="display: flex; flex-direction: column; gap: 12px;">
        ${allRanked.slice(0, 8).map((m, idx) => {
          const isTop = idx === 0;
          return `
            <div class="ranked-mandi-card ${isTop ? 'is-best' : ''}">
              
              <!-- Card Top Row: Rank, Market, Distance, Badges -->
              <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span class="badge ${isTop ? 'badge-green' : 'badge-sky'}" style="font-weight: 700;">
                    #${idx + 1} ${isTop ? 'Best Net' : ''}
                  </span>
                  <div>
                    <h4 style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin: 0;">
                      ${m.market}
                      <span style="font-size: 0.85rem; font-weight: 400; color: var(--muted);">(${m.district})</span>
                    </h4>
                  </div>
                </div>

                <div style="display: flex; align-items: center; gap: 8px;">
                  ${getFreshnessBadge(m.days_ago, m.arrival_date)}
                  <span class="badge badge-sky">${m.distance_km} km</span>
                  <span class="badge badge-sky">${m.travel_hours} hrs</span>
                </div>
              </div>

              <!-- Min / Modal / Max Graphical Price Bar -->
              ${renderPriceBar(
                m.price_range ? m.price_range.min : m.gross_modal_price * 0.9,
                m.gross_modal_price,
                m.price_range ? m.price_range.max : m.gross_modal_price * 1.1
              )}

              <!-- Bottom Metrics Grid -->
              <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border);">
                <div style="display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 0.85rem; color: var(--muted);">
                  <span>Freight: <strong style="color: #C62828;">-₹${m.costs.transport_per_q.toFixed(2)}/q</strong></span>
                  <span>Fees & Labor: <strong style="color: #C62828;">-₹${(m.costs.loading_unloading_per_q + m.costs.market_fee_per_q).toFixed(2)}/q</strong></span>
                  <span>Arrival: <strong>${m.arrival_time}</strong></span>
                </div>

                <div style="text-align: right;">
                  <span style="font-size: 0.8rem; color: var(--muted); margin-right: 6px;">Net In Pocket:</span>
                  <span style="font-size: 1.35rem; font-weight: 700; color: #2E7D32;">
                    ₹${m.net_return_per_quintal.toFixed(2)}<span style="font-size: 0.85rem; font-weight: 500; color: var(--muted);">/q</span>
                  </span>
                </div>
              </div>

              <!-- Rationale verdict -->
              <div style="font-size: 0.85rem; color: var(--muted); margin-top: 8px;">
                ${m.verdict_reason}
              </div>

            </div>
          `;
        }).join('')}
      </div>
    </div>

    <!-- 5. Disclaimer Notice Banner -->
    <div class="card" style="background: #FAFAFA; border: 1px solid var(--border); padding: 18px 24px; margin-bottom: 24px; border-radius: var(--radius-md);">
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
        <i data-lucide="info" style="color: #8D6E12; width: 18px; height: 18px;"></i>
        <h4 style="font-size: 0.95rem; font-weight: 600; color: #8D6E12; margin: 0;" data-i18n="disclaimer_title">
          ${t('disclaimer_title')}
        </h4>
      </div>
      <p style="font-size: 0.85rem; color: var(--muted); margin: 0; line-height: 1.5;" data-i18n="disclaimer_text">
        ${t('disclaimer_text')}
      </p>
    </div>

  `;

  // Initialize Chart.js interactive forecast chart
  if (state.forecastResult && state.forecastResult.forecast) {
    renderForecastChart(state.forecastResult.forecast);
  }

  // Bind Listen to Advice Voice Synthesis button
  const btnVoice = resultsDiv.querySelector('#btn-voice-listen');
  if (btnVoice) {
    btnVoice.addEventListener('click', () => speakAdvice(best, res.nearest_baseline));
  }

  // Refresh Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Chart.js 5-day Low / Likely / High Price Outlook Corridor chart
function renderForecastChart(forecastData) {
  const canvas = document.getElementById('forecast-chart');
  if (!canvas || !window.Chart) return;

  if (state.chartInstance) {
    state.chartInstance.destroy();
    state.chartInstance = null;
  }

  const labels = forecastData.map(f => `${f.day} (${f.weekday.slice(0, 3)})`);
  const lows = forecastData.map(f => f.low);
  const likelys = forecastData.map(f => f.likely);
  const highs = forecastData.map(f => f.high);

  const ctx = canvas.getContext('2d');
  state.chartInstance = new window.Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: t('chart_high'),
          data: highs,
          borderColor: 'rgba(2, 119, 189, 0.8)',
          backgroundColor: 'rgba(227, 241, 251, 0.45)',
          fill: '+1',
          borderDash: [5, 5],
          pointRadius: 4,
          tension: 0.25
        },
        {
          label: t('chart_likely'),
          data: likelys,
          borderColor: '#2E7D32',
          backgroundColor: '#2E7D32',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: '#2E7D32',
          tension: 0.25
        },
        {
          label: t('chart_low'),
          data: lows,
          borderColor: 'rgba(198, 40, 40, 0.8)',
          borderDash: [5, 5],
          pointRadius: 4,
          fill: false,
          tension: 0.25
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
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
            label: function(context) {
              return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString('en-IN')}/q`;
            }
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: function(val) {
              return '₹' + val;
            },
            font: { family: 'Poppins', size: 11 }
          },
          grid: {
            color: 'rgba(225, 239, 228, 0.6)'
          }
        },
        x: {
          ticks: {
            font: { family: 'Poppins', size: 11 }
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
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
