// Mandi Saathi - Alerts Page Stub
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="badge badge-yellow" style="margin-bottom: 8px;">🔔 Price Alerts</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);">Crop Price Alerts</h1>
        <p style="color: var(--muted); font-size: 0.95rem;">
          Get notified when prices at your preferred APMC cross your target threshold.
        </p>
      </div>

      <div class="card" style="text-align: center; padding: 40px 20px;">
        <div style="width: 64px; height: 64px; background: var(--yellow); color: #8D6E12; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
          <i data-lucide="bell" style="width: 32px; height: 32px;"></i>
        </div>
        <h2 style="font-size: 1.3rem; margin-bottom: 8px;">Alert Watchlist Configured</h2>
        <p style="color: var(--muted); max-width: 500px; margin: 0 auto 20px;">
          Saved to local SQLite database with phone and notification thresholds.
        </p>
      </div>
    </div>
  `;
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
