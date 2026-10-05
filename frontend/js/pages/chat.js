// Mandi Saathi - Chat Page (Voice & NLP Stub)
import { t } from '../i18n.js';

export function render(container) {
  container.innerHTML = `
    <div class="container" style="max-width: 860px;">
      <div style="margin-bottom: 24px; text-align: center;">
        <span class="badge badge-sky" style="margin-bottom: 8px;">🎙️ Web Speech & LLM</span>
        <h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text);">Voice & AI Chat Advisor</h1>
        <p style="color: var(--muted); font-size: 0.95rem;">
          Speak or type in Marathi, Hindi, or English to receive instant mandi sell recommendations.
        </p>
      </div>

      <div class="card" style="text-align: center; padding: 40px 20px;">
        <div style="width: 64px; height: 64px; background: var(--sky); color: #0277BD; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
          <i data-lucide="mic" style="width: 32px; height: 32px;"></i>
        </div>
        <h2 style="font-size: 1.3rem; margin-bottom: 8px;">Voice Interface Architecture Ready</h2>
        <p style="color: var(--muted); max-width: 500px; margin: 0 auto 20px;">
          Connects Web Speech API SpeechRecognition & speechSynthesis with rule-based fallback and optional Gemini NLP.
        </p>
      </div>
    </div>
  `;
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
