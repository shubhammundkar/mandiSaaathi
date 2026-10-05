// Mandi Saathi - Hash Router
import { translatePage } from './i18n.js';

const routes = {
  '#/advisor': () => import('./pages/advisor.js'),
  '#/chat': () => import('./pages/chat.js'),
  '#/alerts': () => import('./pages/alerts.js'),
  '#/proof': () => import('./pages/proof.js'),
  '#/about': () => import('./pages/about.js'),
  '#/design': () => import('./pages/design.js')
};

export async function navigate() {
  const hash = window.location.hash || '#/advisor';
  const container = document.getElementById('app-root');
  if (!container) return;

  // Find matching route or fallback to advisor
  const loader = routes[hash] || routes['#/advisor'];

  try {
    const pageModule = await loader();
    if (pageModule && typeof pageModule.render === 'function') {
      pageModule.render(container);
    }
  } catch (err) {
    console.error('Route load error:', err);
    container.innerHTML = `
      <div class="container" style="text-align: center; padding: 40px 20px;">
        <div class="badge badge-red" style="margin-bottom: 12px;">Error</div>
        <h2>Failed to load view</h2>
        <p style="color: var(--muted); margin: 8px 0 16px;">${err.message}</p>
        <a href="#/advisor" class="btn btn-primary">Return to Advisor</a>
      </div>
    `;
  }

  // Update navigation link active states
  document.querySelectorAll('[data-route]').forEach((el) => {
    const target = el.getAttribute('href');
    if (target === hash || (hash === '' && target === '#/advisor')) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });

  // Re-apply translations & icons
  translatePage();
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Scroll to top on navigation
  window.scrollTo(0, 0);
}

export function initRouter() {
  window.addEventListener('hashchange', navigate);
  window.addEventListener('DOMContentLoaded', navigate);
}
