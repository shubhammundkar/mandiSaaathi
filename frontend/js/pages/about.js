// Mandi Saathi - About Page
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="hackathon-badge" style="margin-bottom: 8px;">VORTEX 2K26 Hackathon</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);">About Mandi Saathi</h1>
        <p style="color: var(--muted); font-size: 0.95rem;">
          Theme: Climate, Agriculture & Rural Innovation
        </p>
      </div>

      <div class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="sprout"></i> The Problem We Solve
        </h2>
        <p style="color: var(--text); margin-bottom: 12px;">
          Smallholder farmers frequently travel to far-off mandis based on headline prices, only to find that diesel, loading, transit spoilage, and missed auction timings erase their entire profit.
        </p>
        <p style="color: var(--muted);">
          <strong>Mandi Saathi</strong> acts as a pragmatic, conservative co-pilot: comparing true net returns in your pocket, accounting for travel decay, and giving an honest range forecast instead of false certainty.
        </p>
      </div>

      <div class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="database"></i> Transparent Open Data
        </h2>
        <p style="color: var(--muted); margin-bottom: 8px;">
          All wholesale market arrival and price statistics are ingested from Agmarknet via data.gov.in.
        </p>
        <div class="badge badge-sky">Agmarknet Resource ID: 9ef84268-d588-465a-a308-a864a43d0070</div>
      </div>
    </div>
  `;
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
