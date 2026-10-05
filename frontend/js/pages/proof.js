// Mandi Saathi - Proof Page (Calculation Breakdown Stub)
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="badge badge-green" style="margin-bottom: 8px;">🧮 Transparent Math</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);">Calculation Proof & Logic</h1>
        <p style="color: var(--muted); font-size: 0.95rem;">
          How Mandi Saathi protects farmers from illusory high prices through true net-return math.
        </p>
      </div>

      <div class="card" style="margin-bottom: 20px;">
        <h2 class="card-title">
          <i data-lucide="scale"></i> Net Return Formula
        </h2>
        <div style="background: var(--bg); border: 1px dashed var(--border); padding: 16px; border-radius: var(--radius-md); font-family: monospace; font-size: 0.95rem; margin: 12px 0;">
          Net Return (₹/Qtl) = Expected Price on Arrival Day<br/>
          &nbsp;&nbsp;- Transport Cost (Distance × Rate / Qtl)<br/>
          &nbsp;&nbsp;- Loading & APMC Mandi Cess<br/>
          &nbsp;&nbsp;- Spoilage Loss (Days in Transit × Daily Decay Rate)
        </div>
        <p style="color: var(--muted); font-size: 0.9rem;">
          If the farmer arrives after the 10:00 AM auction cutoff, the engine automatically projects next day's price range.
        </p>
      </div>
    </div>
  `;
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
