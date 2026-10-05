// Mandi Saathi - Advisor Page (Stub for Phase 1)
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="badge badge-green" style="margin-bottom: 8px;">🌱 Phase 1 Setup Ready</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);" data-i18n="advisor_heading">${t('advisor_heading')}</h1>
        <p style="color: var(--muted); font-size: 0.95rem; max-width: 600px; margin: 0 auto;" data-i18n="advisor_subheading">
          ${t('advisor_subheading')}
        </p>
      </div>

      <div class="card" style="text-align: center; padding: 40px 20px;">
        <div style="width: 64px; height: 64px; background: var(--primary-light); color: var(--primary-dark); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
          <i data-lucide="compass" style="width: 32px; height: 32px;"></i>
        </div>
        <h2 style="font-size: 1.3rem; margin-bottom: 8px;">Advisor Engine Ready for Phase 2</h2>
        <p style="color: var(--muted); max-width: 500px; margin: 0 auto 20px;">
          Input crop, harvest size, pickup location and vehicle to calculate net returns after transport, loading, and spoilage.
        </p>
        <div style="display: flex; gap: 12px; justify-content: center;">
          <a href="#/design" class="btn btn-primary">
            <i data-lucide="palette"></i> Preview Design System (#/design)
          </a>
        </div>
      </div>
    </div>
  `;
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
