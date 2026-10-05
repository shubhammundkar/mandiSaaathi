// Mandi Saathi - Main App Entry Point
import { initRouter, navigate } from './router.js';
import { getLanguage, setLanguage, translatePage } from './i18n.js';

// Global Toast System
window.showToast = function (message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'success' ? 'toast-success' : type === 'error' ? 'toast-error' : ''}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  // Set initial language from storage
  const currentLang = getLanguage();
  document.documentElement.lang = currentLang;

  // Bind Language Switcher Buttons
  document.querySelectorAll('.lang-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const selected = btn.getAttribute('data-lang');
      if (selected) {
        setLanguage(selected);
      }
    });
  });

  // Listen for language changes and re-render current route
  window.addEventListener('languagechange', () => {
    translatePage();
    navigate();
  });

  // Start Router
  initRouter();
  navigate();

  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }
});
