// Mandi Saathi - Design System Preview Page
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px;">
        <span class="badge badge-sky" style="margin-bottom: 8px;">🎨 Design System</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);">Mandi Saathi UI Components</h1>
        <p style="color: var(--muted); font-size: 0.95rem;">
          Clean, accessible, mobile-first design tokens and reusable widgets tailored for farmers.
        </p>
      </div>

      <!-- Colors & Palette -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="palette"></i> Color Tokens
        </h2>
        <p class="card-subtitle">Pastel, high-contrast, nature-inspired palette</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; margin-top: 12px;">
          <div style="background: var(--bg); border: 1px solid var(--border); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--bg</div>
            <div style="color: var(--muted); font-size: 0.75rem;">#F4FAF5</div>
          </div>
          <div style="background: var(--card); border: 1px solid var(--border); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--card</div>
            <div style="color: var(--muted); font-size: 0.75rem;">#FFFFFF</div>
          </div>
          <div style="background: var(--primary); color: white; padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--primary</div>
            <div style="font-size: 0.75rem;">#81C784</div>
          </div>
          <div style="background: var(--primary-dark); color: white; padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--primary-dark</div>
            <div style="font-size: 0.75rem;">#4CAF50</div>
          </div>
          <div style="background: var(--peach); color: var(--text); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--peach</div>
            <div style="font-size: 0.75rem;">#FFE9D2</div>
          </div>
          <div style="background: var(--sky); color: var(--text); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--sky</div>
            <div style="font-size: 0.75rem;">#E3F1FB</div>
          </div>
          <div style="background: var(--yellow); color: var(--text); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--yellow</div>
            <div style="font-size: 0.75rem;">#FFF6D6</div>
          </div>
          <div style="background: var(--red-soft); color: var(--text); padding: 12px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-weight: 600; font-size: 0.85rem;">--red-soft</div>
            <div style="font-size: 0.75rem;">#F9D3CF</div>
          </div>
        </div>
      </section>

      <!-- Buttons -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="mouse-pointer-click"></i> Buttons (.btn, .btn-primary, .btn-ghost)
        </h2>
        <p class="card-subtitle">Min 48px height, rounded corners, soft shadows</p>
        <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center;">
          <button class="btn btn-primary">
            <i data-lucide="check-circle-2"></i> ${t('btn_calculate')}
          </button>
          <button class="btn btn-ghost">
            <i data-lucide="volume-2"></i> ${t('btn_listen')}
          </button>
          <button class="btn btn-ghost" style="border-color: var(--primary); color: var(--primary-dark);">
            <i data-lucide="mic"></i> ${t('btn_speak')}
          </button>
          <button class="btn btn-primary btn-icon" title="Action Icon">
            <i data-lucide="arrow-right"></i>
          </button>
        </div>
      </section>

      <!-- Badges -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="tag"></i> Badges (.badge)
        </h2>
        <p class="card-subtitle">Freshness indicators, confidence ratings, and sell actions</p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          <span class="badge badge-green">
            <i data-lucide="sparkles"></i> ${t('badge_best_net')}
          </span>
          <span class="badge badge-green">
            <i data-lucide="clock"></i> ${t('badge_fresh')}
          </span>
          <span class="badge badge-sky">
            <i data-lucide="shield-check"></i> ${t('badge_high_conf')}
          </span>
          <span class="badge badge-yellow">
            <i data-lucide="alert-triangle"></i> ${t('badge_med_conf')}
          </span>
          <span class="badge badge-red">
            <i data-lucide="alert-octagon"></i> ${t('badge_unreliable')}
          </span>
          <span class="badge badge-peach">
            <i data-lucide="truck"></i> Far Mandi (-15%)
          </span>
        </div>
      </section>

      <!-- Form Inputs & Selects -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="form-input"></i> Form Elements (.input, .select, .chip)
        </h2>
        <p class="card-subtitle">Touch-friendly inputs with large tap targets</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;">
          <div class="input-group">
            <label class="input-label">${t('select_crop')}</label>
            <select class="select">
              <option value="onion">🧅 Onion (कांदा)</option>
              <option value="tomato">🍅 Tomato (टोमॅटो)</option>
              <option value="soybean">🌱 Soybean (सोयाबीन)</option>
              <option value="cotton">🌾 Cotton (कापूस)</option>
            </select>
          </div>

          <div class="input-group">
            <label class="input-label">${t('input_quantity')}</label>
            <input type="number" class="input" placeholder="e.g. 50" value="40" />
          </div>
        </div>

        <div style="margin-top: 12px;">
          <label class="input-label">Quick Select Crop (Chips)</label>
          <div class="chip-group">
            <div class="chip active">🧅 Onion</div>
            <div class="chip">🍅 Tomato</div>
            <div class="chip">🌱 Soybean</div>
            <div class="chip">🌾 Cotton</div>
            <div class="chip">🥔 Potato</div>
          </div>
        </div>
      </section>

      <!-- Tabs & Skeletons -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="layers"></i> Tabs & Loading Skeletons (.tabs, .skeleton)
        </h2>
        <div class="tabs" style="margin-bottom: 20px;">
          <button class="tab-btn active">Overview</button>
          <button class="tab-btn">Price Trend</button>
          <button class="tab-btn">Route Math</button>
        </div>

        <div style="display: flex; gap: 16px; align-items: center;">
          <div class="skeleton skeleton-circle"></div>
          <div style="flex: 1;">
            <div class="skeleton skeleton-text" style="width: 70%;"></div>
            <div class="skeleton skeleton-text" style="width: 45%;"></div>
          </div>
        </div>
        <div class="skeleton skeleton-card" style="margin-top: 16px;"></div>
      </section>

      <!-- Interactive Toasts -->
      <section class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="bell"></i> Interactive Toasts (.toast)
        </h2>
        <p class="card-subtitle">Click to trigger feedback messages</p>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button id="demo-toast-success" class="btn btn-ghost" style="border-color: #81C784; color: #2E7D32;">
            <i data-lucide="check"></i> Trigger Success Toast
          </button>
          <button id="demo-toast-error" class="btn btn-ghost" style="border-color: #F9D3CF; color: #C62828;">
            <i data-lucide="alert-circle"></i> Trigger Error Toast
          </button>
        </div>
      </section>
    </div>
  `;

  // Bind toast actions
  document.getElementById('demo-toast-success')?.addEventListener('click', () => {
    window.showToast('✅ Calculation completed successfully with 5 APMC mandis!', 'success');
  });

  document.getElementById('demo-toast-error')?.addEventListener('click', () => {
    window.showToast('⚠️ Data for this mandi is older than 3 days (unreliable).', 'error');
  });

  // Re-run Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
