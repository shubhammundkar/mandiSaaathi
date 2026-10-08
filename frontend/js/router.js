import { translatePage, getLanguage } from './i18n.js';

const routes = {
  '#/advisor': () => import('./pages/advisor.js'),
  '#/chat': () => import('./pages/chat.js'),
  '#/alerts': () => import('./pages/alerts.js'),
  '#/data-quality': () => import('./pages/alerts.js'),
  '#/farmer-reports': () => import('./pages/alerts.js'),
  '#/proof': () => import('./pages/proof.js'),
  '#/about': () => import('./pages/about.js'),
  '#/design': () => import('./pages/design.js')
};

const routeTitles = {
  '#/advisor': { en: 'Advisor | Mandi Saathi', hi: 'सलाहकार | मंडी साथी', mr: 'सल्लागार | मंडी साथी' },
  '#/chat': { en: 'Voice Chat | Mandi Saathi', hi: 'आवाज़ बातचीत | मंडी साथी', mr: 'बोलून विचारा | मंडी साथी' },
  '#/alerts': { en: 'Daily Alerts | Mandi Saathi', hi: 'मंडी भाव अलर्ट | मंडी साथी', mr: 'बाजारभाव अलर्ट | मंडी साथी' },
  '#/data-quality': { en: 'Data Quality | Mandi Saathi', hi: 'डेटा गुणवत्ता | मंडी साथी', mr: 'डेटा गुणवत्ता | मंडी साथी' },
  '#/farmer-reports': { en: 'Farmer Reports | Mandi Saathi', hi: 'किसान रिपोर्ट | मंडी साथी', mr: 'शेतकरी नोंदी | मंडी साथी' },
  '#/proof': { en: 'Proof & Calculation Logic | Mandi Saathi', hi: 'हिसाब-किताब व पुरावा | मंडी साथी', mr: 'हिशोब व पुरावा | मंडी साथी' },
  '#/about': { en: 'About | Mandi Saathi', hi: 'परिचय | मंडी साथी', mr: 'माहिती | मंडी साथी' },
  '#/design': { en: 'Design System | Mandi Saathi', hi: 'डिज़ाइन सिस्टम | मंडी साथी', mr: 'डिझाइन सिस्टीम | मंडी साथी' }
};

export async function navigate() {
  const hash = window.location.hash || '#/advisor';
  const container = document.getElementById('app-root');
  if (!container) return;

  // Set localized document title
  const currentLang = getLanguage() || 'en';
  const titleObj = routeTitles[hash] || routeTitles['#/advisor'];
  document.title = titleObj[currentLang] || titleObj['en'] || 'Mandi Saathi';

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
