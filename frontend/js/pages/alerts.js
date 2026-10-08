// Mandi Saathi - Alerts, Farmer Reports, and Data Quality Page
import { api } from '../api.js';
import { t, getCurrentLanguage } from '../i18n.js';

let activeTab = 'alerts'; // 'alerts' | 'sold' | 'quality'
let previewData = null;
let subscriptionsList = [];
let farmerReportsList = [];
let qualityData = null;

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
  'Pune', 'Nashik', 'Ahilyanagar', 'Solapur', 'Kolhapur',
  'Jalgaon', 'Akola', 'Amravati', 'Latur', 'Nagpur', 'Mumbai',
  'Satara', 'Sangli', 'Chhatrapati Sambhajinagar', 'Jalna'
];

export async function render(container) {
  if (window.location.hash === '#/data-quality') {
    activeTab = 'quality';
  } else if (window.location.hash === '#/farmer-reports') {
    activeTab = 'sold';
  } else if (window.location.hash === '#/alerts') {
    activeTab = 'alerts';
  }

  const currentLang = getCurrentLanguage();

  container.innerHTML = `
    <div class="container" style="max-width: 960px; padding-bottom: 60px;">
      <!-- Page Header -->
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="badge badge-green" style="margin-bottom: 8px;">
          <i data-lucide="bell" style="width: 14px; height: 14px;"></i> Alerts & Community Intelligence
        </span>
        <h1 style="font-size: 1.85rem; font-weight: 700; color: var(--text); margin-bottom: 8px;">
          Mandi Alerts, Farmer Reports & Data Quality
        </h1>
        <p style="color: var(--muted); font-size: 0.95rem; max-width: 650px; margin: 0 auto;">
          Get daily morning WhatsApp market alerts, log actual crop sales, and inspect real-time reporting coverage across 23 Maharashtra APMC markets.
        </p>
      </div>

      <!-- Segmented Tab Navigation -->
      <div class="alerts-tab-bar" role="tablist">
        <button class="alerts-tab-btn ${activeTab === 'alerts' ? 'active' : ''}" data-tab="alerts">
          <i data-lucide="bell" style="width: 16px; height: 16px;"></i> Daily Alerts & WhatsApp Preview
        </button>
        <button class="alerts-tab-btn ${activeTab === 'sold' ? 'active' : ''}" data-tab="sold">
          <i data-lucide="badge-percent" style="width: 16px; height: 16px;"></i> "I Sold Today" (Farmer Reports)
        </button>
        <button class="alerts-tab-btn ${activeTab === 'quality' ? 'active' : ''}" data-tab="quality">
          <i data-lucide="activity" style="width: 16px; height: 16px;"></i> Mandi Data Quality
        </button>
      </div>

      <!-- Tab Content Placeholder -->
      <div id="alerts-tab-content">
        <div class="card" style="text-align: center; padding: 40px;">
          <div class="spinner" style="margin: 0 auto 16px;"></div>
          <p style="color: var(--muted);">Loading data...</p>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();

  // Attach tab switcher
  container.querySelectorAll('.alerts-tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      activeTab = btn.getAttribute('data-tab');
      container.querySelectorAll('.alerts-tab-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      renderActiveTab(container);
    });
  });

  // Load initial tab
  await renderActiveTab(container);
}

async function renderActiveTab(container) {
  const contentArea = container.querySelector('#alerts-tab-content');
  if (!contentArea) return;

  if (activeTab === 'alerts') {
    await renderAlertsTab(contentArea);
  } else if (activeTab === 'sold') {
    await renderSoldTab(contentArea);
  } else if (activeTab === 'quality') {
    await renderQualityTab(contentArea);
  }

  if (window.lucide) window.lucide.createIcons();
}

// =============================================================================
// TAB 1: Daily Alerts & WhatsApp Preview
// =============================================================================

async function renderAlertsTab(target) {
  target.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; align-items: start;">
      <!-- Left Column: Subscription Form & Active Subscriptions -->
      <div style="display: flex; flex-direction: column; gap: 24px;">
        <!-- Subscription Form Card -->
        <div class="card">
          <div class="card-title">
            <i data-lucide="send" style="width: 20px; height: 20px; color: var(--primary);"></i>
            Subscribe for Daily Mandi Alerts
          </div>
          <div class="card-subtitle">
            Receive morning price intelligence on your phone before the 12:00 PM APMC auction cutoff.
          </div>

          <form id="subscribe-form" style="display: flex; flex-direction: column; gap: 16px;">
            <div class="input-group">
              <label for="sub-crop" class="input-label">Select Crop</label>
              <select id="sub-crop" class="input-control" required>
                ${CROPS.map((c) => `<option value="${c.id}">${c.name}</option>`).join('')}
              </select>
            </div>

            <div class="input-group">
              <label for="sub-district" class="input-label">Your District</label>
              <select id="sub-district" class="input-control" required>
                ${DISTRICTS.map((d) => `<option value="${d}">${d}</option>`).join('')}
              </select>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="input-group">
                <label for="sub-lang" class="input-label">Alert Language</label>
                <select id="sub-lang" class="input-control">
                  <option value="mr" selected>मराठी (Marathi)</option>
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="en">English</option>
                </select>
              </div>

              <div class="input-group">
                <label for="sub-nick" class="input-label">Your Nickname</label>
                <input type="text" id="sub-nick" class="input-control" placeholder="उदा. रामभाऊ" value="शेतकरी मित्र">
              </div>
            </div>

            <div id="sub-msg" style="display: none; font-size: 0.88rem; padding: 10px; border-radius: var(--radius-md);"></div>

            <div style="display: flex; gap: 10px; margin-top: 6px;">
              <button type="submit" class="btn btn-primary" style="flex: 1;" id="btn-sub-submit">
                <i data-lucide="bell-plus" style="width: 18px; height: 18px;"></i> Subscribe
              </button>
              <button type="button" class="btn btn-ghost" id="btn-sub-preview">
                <i data-lucide="eye" style="width: 18px; height: 18px;"></i> Preview
              </button>
            </div>
          </form>
        </div>

        <!-- Active Subscriptions List -->
        <div class="card">
          <div class="card-title" style="justify-content: space-between;">
            <span style="display: flex; align-items: center; gap: 8px;">
              <i data-lucide="bookmark" style="width: 18px; height: 18px; color: var(--primary);"></i>
              Active Subscriptions
            </span>
            <span class="badge badge-sky" id="subs-count-badge">0 Active</span>
          </div>
          <div id="subs-list-container" style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;">
            <p style="color: var(--muted); font-size: 0.9rem; text-align: center; padding: 16px;">
              Loading subscriptions...
            </p>
          </div>
        </div>
      </div>

      <!-- Right Column: WhatsApp Morning Message Preview -->
      <div style="position: sticky; top: 80px;">
        <div class="whatsapp-window">
          <!-- WhatsApp Header Bar -->
          <div class="whatsapp-header">
            <div class="whatsapp-avatar">🌱</div>
            <div style="flex: 1;">
              <div style="font-weight: 700; font-size: 0.95rem; line-height: 1.2;">Mandi Saathi Daily Alert</div>
              <div style="font-size: 0.75rem; opacity: 0.85;">online • APMC Intelligence</div>
            </div>
            <div style="font-size: 0.8rem; background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: var(--radius-pill);">
              WhatsApp Preview
            </div>
          </div>

          <!-- Chat Body Wallpaper -->
          <div style="padding: 12px; min-height: 380px; display: flex; flex-direction: column; justify-content: flex-start;">
            <div class="whatsapp-bubble" id="whatsapp-bubble-content">
              <div class="spinner" style="margin: 20px auto;"></div>
              <p style="text-align: center; color: #667781; font-size: 0.85rem;">Generating morning intelligence from real mandi prices...</p>
            </div>
          </div>

          <!-- Bottom Action Controls -->
          <div style="background: #F0F2F5; padding: 12px 16px; border-top: 1px solid #D1D7DB; display: flex; gap: 10px;">
            <button class="btn btn-primary" id="btn-copy-preview" style="flex: 1; min-height: 40px; font-size: 0.85rem;">
              <i data-lucide="copy" style="width: 16px; height: 16px;"></i> Copy Message
            </button>
            <a id="btn-share-preview" href="#" target="_blank" rel="noopener noreferrer" class="btn btn-ghost" style="flex: 1; min-height: 40px; font-size: 0.85rem; background: #25D366; color: #FFF; border-color: #25D366; text-decoration: none;">
              <i data-lucide="share-2" style="width: 16px; height: 16px;"></i> WhatsApp
            </a>
          </div>
        </div>
      </div>
    </div>
  `;

  // Fetch subscriptions
  await loadSubscriptions(target);

  // Generate initial preview with default values
  await updateWhatsAppPreview(target, 'Tomato', 'Pune', 'mr', 'शेतकरी मित्र');

  // Event listener: Subscribe form submit
  const subForm = target.querySelector('#subscribe-form');
  subForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const crop = target.querySelector('#sub-crop').value;
    const district = target.querySelector('#sub-district').value;
    const language = target.querySelector('#sub-lang').value;
    const nickname = target.querySelector('#sub-nick').value;
    const msgBox = target.querySelector('#sub-msg');

    try {
      const res = await api.subscribeAlert({ crop, district, language, nickname });
      msgBox.style.display = 'block';
      msgBox.style.background = '#E8F5E9';
      msgBox.style.color = '#2E7D32';
      msgBox.textContent = `✓ ${res.message || 'Subscribed successfully!'}`;
      await loadSubscriptions(target);
      await updateWhatsAppPreview(target, crop, district, language, nickname);
    } catch (err) {
      msgBox.style.display = 'block';
      msgBox.style.background = '#FFEBEE';
      msgBox.style.color = '#C62828';
      msgBox.textContent = `✕ ${err.message}`;
    }
  });

  // Event listener: Preview button click
  const btnPreview = target.querySelector('#btn-sub-preview');
  btnPreview.addEventListener('click', async () => {
    const crop = target.querySelector('#sub-crop').value;
    const district = target.querySelector('#sub-district').value;
    const language = target.querySelector('#sub-lang').value;
    const nickname = target.querySelector('#sub-nick').value;
    await updateWhatsAppPreview(target, crop, district, language, nickname);
  });

  // Event listener: Copy button click
  const btnCopy = target.querySelector('#btn-copy-preview');
  btnCopy.addEventListener('click', () => {
    if (previewData && previewData.preview_text) {
      navigator.clipboard.writeText(previewData.preview_text).then(() => {
        btnCopy.innerHTML = `<i data-lucide="check" style="width:16px;height:16px;"></i> Copied!`;
        if (window.lucide) window.lucide.createIcons();
        setTimeout(() => {
          btnCopy.innerHTML = `<i data-lucide="copy" style="width:16px;height:16px;"></i> Copy Message`;
          if (window.lucide) window.lucide.createIcons();
        }, 2000);
      });
    }
  });
}

async function loadSubscriptions(target) {
  const container = target.querySelector('#subs-list-container');
  const countBadge = target.querySelector('#subs-count-badge');
  if (!container) return;

  try {
    const data = await api.getAlerts();
    subscriptionsList = data.subscriptions || [];

    if (countBadge) countBadge.textContent = `${subscriptionsList.length} Active`;

    if (subscriptionsList.length === 0) {
      container.innerHTML = `
        <p style="color: var(--muted); font-size: 0.9rem; text-align: center; padding: 16px;">
          No active subscriptions yet. Subscribe to your favorite crop above!
        </p>
      `;
      return;
    }

    container.innerHTML = subscriptionsList.map((sub) => `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #F8FAF9; border: 1px solid var(--border); border-radius: var(--radius-md);">
        <div>
          <div style="font-weight: 600; font-size: 0.95rem; color: var(--text);">
            ${sub.crop} • ${sub.district}
          </div>
          <div style="font-size: 0.8rem; color: var(--muted);">
            ${sub.nickname || 'Kisan'} • Lang: ${sub.language.toUpperCase()}
          </div>
        </div>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-ghost btn-sub-view" data-id="${sub.id}" data-crop="${sub.crop}" data-dist="${sub.district}" data-lang="${sub.language}" data-nick="${sub.nickname}" style="min-height: 32px; padding: 4px 10px; font-size: 0.8rem;" title="Preview Message">
            <i data-lucide="eye" style="width: 14px; height: 14px;"></i> View
          </button>
          <button class="btn btn-ghost btn-sub-del" data-id="${sub.id}" style="min-height: 32px; padding: 4px 10px; font-size: 0.8rem; color: #C62828;" title="Unsubscribe">
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
          </button>
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();

    // Attach view listeners
    container.querySelectorAll('.btn-sub-view').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const crop = btn.getAttribute('data-crop');
        const dist = btn.getAttribute('data-dist');
        const lang = btn.getAttribute('data-lang');
        const nick = btn.getAttribute('data-nick');
        await updateWhatsAppPreview(target, crop, dist, lang, nick);
      });
    });

    // Attach delete listeners
    container.querySelectorAll('.btn-sub-del').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        if (confirm('Cancel this alert subscription?')) {
          await api.deleteAlert(id);
          await loadSubscriptions(target);
        }
      });
    });
  } catch (err) {
    container.innerHTML = `<p style="color: #C62828; font-size: 0.85rem;">Error loading subscriptions: ${err.message}</p>`;
  }
}

async function updateWhatsAppPreview(target, crop, district, language, nickname) {
  const bubble = target.querySelector('#whatsapp-bubble-content');
  const shareBtn = target.querySelector('#btn-share-preview');
  if (!bubble) return;

  bubble.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 20px 0; color: #667781;">
      <div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div>
      <span>Querying real APMC prices...</span>
    </div>
  `;

  try {
    previewData = await api.getAlertPreview({ crop, district, language, nickname });
    const text = previewData.preview_text || '';

    // Convert WhatsApp markdown (*bold*, _italic_) to HTML for rendering
    let htmlText = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
      .replace(/_(.*?)_/g, '<em>$1</em>');

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    bubble.innerHTML = `
      <div>${htmlText}</div>
      <div class="whatsapp-bubble-time">
        <span>${currentTime}</span>
        <span style="color: #53BDEB; font-weight: bold;">✓✓</span>
      </div>
    `;

    if (shareBtn) {
      shareBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
    }
  } catch (err) {
    bubble.innerHTML = `<p style="color: #C62828;">Error generating alert preview: ${err.message}</p>`;
  }
}

// =============================================================================
// TAB 2: "I Sold Today" (Farmer Reports - Distinct from Agmarknet)
// =============================================================================

async function renderSoldTab(target) {
  const todayDate = new Date().toISOString().split('T')[0];

  target.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Explanatory Notice Banner -->
      <div style="background: #FFF8E1; border: 1px solid #FFE082; border-radius: var(--radius-lg); padding: 16px; display: flex; gap: 12px; align-items: flex-start;">
        <i data-lucide="info" style="width: 22px; height: 22px; color: #F57F17; flex-shrink: 0; margin-top: 2px;"></i>
        <div>
          <strong style="color: #E65100; font-size: 0.95rem;">Farmer Reported Community Data</strong>
          <p style="color: #5D4037; font-size: 0.88rem; margin: 4px 0 0;">
            Log your actual transactions below. Every entry is displayed separately with a visible
            <span class="badge badge-farmer">🧑‍🌾 Farmer reported</span> badge and is <strong>never mixed into official Agmarknet arrivals</strong>.
          </p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; align-items: start;">
        <!-- Submission Form Card -->
        <div class="card">
          <div class="card-title">
            <i data-lucide="receipt" style="width: 20px; height: 20px; color: #E65100;"></i>
            "I Sold Today" Transaction Log
          </div>
          <div class="card-subtitle">
            Help fellow farmers verify realistic street prices with sanity-checked sale data.
          </div>

          <form id="farmer-report-form" style="display: flex; flex-direction: column; gap: 14px;">
            <div class="input-group">
              <label for="fr-crop" class="input-label">Crop Sold</label>
              <select id="fr-crop" class="input-control" required>
                ${CROPS.map((c) => `<option value="${c.id}">${c.name}</option>`).join('')}
              </select>
            </div>

            <div class="input-group">
              <label for="fr-market" class="input-label">APMC Mandi / Market</label>
              <input type="text" id="fr-market" class="input-control" placeholder="उदा. Pune, Pimpalgaon, Lasalgaon" value="Pune" required>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="input-group">
                <label for="fr-price" class="input-label">Price Sold (₹/quintal)</label>
                <input type="number" id="fr-price" class="input-control" min="1" max="50000" step="1" placeholder="₹ 2200" required>
              </div>

              <div class="input-group">
                <label for="fr-quantity" class="input-label">Quantity (Quintals)</label>
                <input type="number" id="fr-quantity" class="input-control" min="0.1" max="10000" step="0.1" placeholder="20.0" value="20.0" required>
              </div>
            </div>

            <div class="input-group">
              <label for="fr-date" class="input-label">Date of Sale</label>
              <input type="date" id="fr-date" class="input-control" value="${todayDate}" max="${todayDate}" required>
            </div>

            <div id="fr-feedback" style="display: none; font-size: 0.88rem; padding: 10px; border-radius: var(--radius-md);"></div>

            <button type="submit" class="btn btn-primary" style="margin-top: 4px; background: linear-gradient(135deg, #F57C00 0%, #E65100 100%);">
              <i data-lucide="check-circle" style="width: 18px; height: 18px;"></i> Submit My Transaction
            </button>
          </form>
        </div>

        <!-- Recent Community Reports Feed -->
        <div class="card">
          <div class="card-title" style="justify-content: space-between;">
            <span style="display: flex; align-items: center; gap: 8px;">
              <i data-lucide="users" style="width: 18px; height: 18px; color: #E65100;"></i>
              Recent Farmer Reports
            </span>
            <span class="badge badge-farmer" id="fr-count-badge">0 Submissions</span>
          </div>
          <div class="card-subtitle">
            Verified local transactions submitted by registered farmers.
          </div>

          <div id="fr-feed-container" style="display: flex; flex-direction: column; gap: 12px; margin-top: 8px;">
            <p style="color: var(--muted); font-size: 0.9rem; text-align: center; padding: 20px;">
              Loading farmer reports...
            </p>
          </div>
        </div>
      </div>
    </div>
  `;

  await loadFarmerReports(target);

  // Form submit handler
  const form = target.querySelector('#farmer-report-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const crop = target.querySelector('#fr-crop').value;
    const market = target.querySelector('#fr-market').value;
    const price = parseFloat(target.querySelector('#fr-price').value);
    const quantity = parseFloat(target.querySelector('#fr-quantity').value);
    const report_date = target.querySelector('#fr-date').value;
    const feedback = target.querySelector('#fr-feedback');

    // Client sanity checks
    if (isNaN(price) || price <= 0 || price > 50000) {
      feedback.style.display = 'block';
      feedback.style.background = '#FFEBEE';
      feedback.style.color = '#C62828';
      feedback.textContent = '✕ Price must be a realistic value between ₹1 and ₹50,000 / quintal.';
      return;
    }

    if (isNaN(quantity) || quantity <= 0 || quantity > 10000) {
      feedback.style.display = 'block';
      feedback.style.background = '#FFEBEE';
      feedback.style.color = '#C62828';
      feedback.textContent = '✕ Quantity must be between 0.1 and 10,000 quintals.';
      return;
    }

    try {
      const res = await api.submitFarmerReport({ crop, market, price, quantity, report_date });
      feedback.style.display = 'block';
      feedback.style.background = '#E8F5E9';
      feedback.style.color = '#2E7D32';
      feedback.textContent = `✓ ${res.message || 'Report logged successfully with Farmer reported badge!'}`;
      target.querySelector('#fr-price').value = '';
      await loadFarmerReports(target);
    } catch (err) {
      feedback.style.display = 'block';
      feedback.style.background = '#FFEBEE';
      feedback.style.color = '#C62828';
      feedback.textContent = `✕ ${err.message}`;
    }
  });
}

async function loadFarmerReports(target) {
  const container = target.querySelector('#fr-feed-container');
  const countBadge = target.querySelector('#fr-count-badge');
  if (!container) return;

  try {
    const res = await api.getFarmerReports();
    farmerReportsList = res.reports || [];

    if (countBadge) countBadge.textContent = `${farmerReportsList.length} Reports`;

    if (farmerReportsList.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 24px; color: var(--muted);">
          <i data-lucide="inbox" style="width: 32px; height: 32px; margin: 0 auto 8px; opacity: 0.5;"></i>
          <p>No transactions logged yet. Be the first farmer to share your sale price!</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    container.innerHTML = farmerReportsList.slice(0, 15).map((r) => `
      <div style="padding: 12px 14px; background: #FFFDF9; border: 1px solid #FFE0B2; border-radius: var(--radius-md); display: flex; flex-direction: column; gap: 6px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="font-weight: 700; color: var(--text); font-size: 0.95rem;">
            ${r.crop} @ ${r.market}
          </span>
          <span class="badge badge-farmer">🧑‍🌾 ${r.badge || 'Farmer reported'}</span>
        </div>
        <div style="display: flex; align-items: baseline; justify-content: space-between;">
          <span style="font-size: 1.15rem; font-weight: 700; color: #E65100;">
            ₹ ${Math.round(r.price)} / q
          </span>
          <span style="font-size: 0.85rem; color: var(--muted);">
            Qty: ${r.quantity} q • Date: ${r.report_date}
          </span>
        </div>
      </div>
    `).join('');

    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    container.innerHTML = `<p style="color: #C62828;">Error loading reports: ${err.message}</p>`;
  }
}

// =============================================================================
// TAB 3: Mandi Data Quality & Coverage Metrics
// =============================================================================

async function renderQualityTab(target) {
  target.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Overview Header -->
      <div class="card" style="padding: 24px;">
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
          <div>
            <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); margin-bottom: 4px;">
              Mandi Data Quality & 30-Day Coverage Monitor
            </h2>
            <p style="color: var(--muted); font-size: 0.88rem; margin: 0;">
              Real-time reporting frequency, data staleness, and confidence grades across monitored APMC markets.
            </p>
          </div>
          <button class="btn btn-ghost" id="btn-refresh-quality" style="min-height: 38px; padding: 6px 14px; font-size: 0.85rem;">
            <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i> Refresh
          </button>
        </div>

        <!-- Summary KPI Cards -->
        <div id="quality-kpi-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 20px;">
          <div style="background: var(--background); padding: 14px; border-radius: var(--radius-md); border: 1px solid var(--border); text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);" id="kpi-total-mandis">--</div>
            <div style="font-size: 0.8rem; color: var(--muted);">Monitored Mandis</div>
          </div>
          <div style="background: #E8F5E9; padding: 14px; border-radius: var(--radius-md); border: 1px solid #C8E6C9; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #2E7D32;" id="kpi-high-conf">--</div>
            <div style="font-size: 0.8rem; color: #2E7D32;">High Confidence (Green)</div>
          </div>
          <div style="background: #FFF9C4; padding: 14px; border-radius: var(--radius-md); border: 1px solid #FFF59D; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #F57F17;" id="kpi-med-conf">--</div>
            <div style="font-size: 0.8rem; color: #F57F17;">Medium Confidence (Yellow)</div>
          </div>
          <div style="background: #FFEBEE; padding: 14px; border-radius: var(--radius-md); border: 1px solid #FFCDD2; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #C62828;" id="kpi-low-conf">--</div>
            <div style="font-size: 0.8rem; color: #C62828;">Low / Stale (Red)</div>
          </div>
        </div>
      </div>

      <!-- Mandis Table & Breakdown -->
      <div class="card" style="padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div style="font-weight: 700; font-size: 1.05rem; color: var(--text);">
            Per-Mandi Coverage Breakdown
          </div>
          <input type="text" id="mandi-filter-input" class="input-control" placeholder="Search market or district..." style="max-width: 250px; min-height: 38px; font-size: 0.85rem;">
        </div>

        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); color: var(--muted); font-size: 0.8rem; text-transform: uppercase;">
                <th style="padding: 10px;">Mandi & District</th>
                <th style="padding: 10px;">Last Reported</th>
                <th style="padding: 10px;">30-Day Coverage</th>
                <th style="padding: 10px;">Confidence Badge</th>
                <th style="padding: 10px;">Coordinates</th>
              </tr>
            </thead>
            <tbody id="quality-table-body">
              <tr>
                <td colspan="5" style="text-align: center; padding: 30px; color: var(--muted);">
                  Calculating data quality metrics across APMC markets...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  await loadDataQuality(target);

  // Filter input listener
  const filterInput = target.querySelector('#mandi-filter-input');
  if (filterInput) {
    filterInput.addEventListener('input', () => {
      renderQualityTable(target, filterInput.value);
    });
  }

  // Refresh button listener
  const btnRefresh = target.querySelector('#btn-refresh-quality');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', async () => {
      await loadDataQuality(target);
    });
  }
}

async function loadDataQuality(target) {
  try {
    qualityData = await api.getDataQuality();

    const totalEl = target.querySelector('#kpi-total-mandis');
    const highEl = target.querySelector('#kpi-high-conf');
    const medEl = target.querySelector('#kpi-med-conf');
    const lowEl = target.querySelector('#kpi-low-conf');

    if (totalEl) totalEl.textContent = qualityData.total_monitored_mandis || 0;
    if (highEl) highEl.textContent = qualityData.high_confidence_mandis || 0;
    if (medEl) medEl.textContent = qualityData.medium_confidence_mandis || 0;
    if (lowEl) lowEl.textContent = qualityData.low_confidence_mandis || 0;

    renderQualityTable(target);
  } catch (err) {
    const tbody = target.querySelector('#quality-table-body');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="5" style="color: #C62828; padding: 20px; text-align: center;">Error loading data quality: ${err.message}</td></tr>`;
    }
  }
}

function renderQualityTable(target, filterText = '') {
  const tbody = target.querySelector('#quality-table-body');
  if (!tbody || !qualityData || !qualityData.mandis) return;

  const cleanFilter = filterText.toLowerCase().trim();
  const mandis = qualityData.mandis.filter((m) => {
    if (!cleanFilter) return true;
    return m.market.toLowerCase().includes(cleanFilter) || m.district.toLowerCase().includes(cleanFilter);
  });

  if (mandis.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 24px; color: var(--muted);">No mandis match "${filterText}"</td></tr>`;
    return;
  }

  tbody.innerHTML = mandis.map((m) => {
    // Confidence badge styling
    let badgeHtml = '';
    if (m.confidence === 'HIGH') {
      badgeHtml = `<span class="badge badge-green">✓ HIGH (${m.confidence_badge})</span>`;
    } else if (m.confidence === 'MEDIUM') {
      badgeHtml = `<span class="badge badge-yellow">⚠ MEDIUM</span>`;
    } else {
      badgeHtml = `<span class="badge badge-red">✕ LOW</span>`;
    }

    // Staleness format
    const daysAgo = m.days_since_report;
    let daysAgoText = 'Unknown';
    if (daysAgo !== null && daysAgo !== undefined) {
      if (daysAgo === 0) daysAgoText = '<span style="color: #2E7D32; font-weight: 600;">Today</span>';
      else if (daysAgo === 1) daysAgoText = 'Yesterday';
      else daysAgoText = `${daysAgo} days ago`;
    }

    // Coordinates indicator
    const coordsHtml = m.coordinates_present
      ? `<span class="badge badge-sky" title="lat: ${m.lat}, lng: ${m.lng}">📍 Known Coords</span>`
      : `<span class="badge badge-red">⚠️ Location Unknown</span>`;

    // Coverage bar color
    const barColor = m.coverage_pct_30d >= 70 ? '#4CAF50' : (m.coverage_pct_30d >= 40 ? '#FBC02D' : '#E53935');

    return `
      <tr style="border-bottom: 1px solid var(--border);">
        <td style="padding: 12px 10px;">
          <div style="font-weight: 600; color: var(--text);">${m.market}</div>
          <div style="color: var(--muted); font-size: 0.8rem;">${m.district}</div>
        </td>
        <td style="padding: 12px 10px;">
          <div style="font-weight: 500;">${m.latest_reported_date || 'No reports'}</div>
          <div style="font-size: 0.78rem; color: var(--muted);">${daysAgoText}</div>
        </td>
        <td style="padding: 12px 10px; min-width: 140px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span style="font-weight: 600;">${m.coverage_pct_30d}%</span>
            <span style="color: var(--muted);">${m.active_trading_days_30d}/25 days</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${m.coverage_pct_30d}%; background: ${barColor};"></div>
          </div>
        </td>
        <td style="padding: 12px 10px;">
          ${badgeHtml}
        </td>
        <td style="padding: 12px 10px;">
          ${coordsHtml}
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) window.lucide.createIcons();
}
