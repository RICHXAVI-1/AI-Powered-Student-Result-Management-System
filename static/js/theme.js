/**
 * Theme Manager — Light / Dark mode toggle
 * Persists preference to localStorage.
 * Applies theme BEFORE first paint to prevent flash.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'ars-theme';
  const DARK        = 'dark';
  const LIGHT       = 'light';

  /** Return the resolved theme: stored pref → OS pref → light */
  function getInitialTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === DARK || stored === LIGHT) return stored;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return DARK;
    return LIGHT;
  }

  /** Apply theme to <html> element (fast, no transition) */
  function applyTheme(theme, animate) {
    const html = document.documentElement;
    if (animate) {
      html.classList.add('theme-transitioning');
      setTimeout(() => html.classList.remove('theme-transitioning'), 400);
    }
    html.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateToggleUI(theme);
  }

  /** Sync the toggle button appearance to the current theme */
  function updateToggleUI(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    const isDark = theme === DARK;
    btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    btn.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
    const label = btn.querySelector('.toggle-label');
    if (label) label.textContent = isDark ? 'Light' : 'Dark';
  }

  /** Public toggle — called by the button onclick */
  window.toggleTheme = function () {
    const current = document.documentElement.getAttribute('data-theme') || LIGHT;
    applyTheme(current === DARK ? LIGHT : DARK, true);
  };

  /* ── Apply immediately (before DOM ready) to kill FOUC ── */
  applyTheme(getInitialTheme(), false);

  /* ── After DOM loads, sync button UI ─────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    const theme = document.documentElement.getAttribute('data-theme') || LIGHT;
    updateToggleUI(theme);

    /* Listen for OS-level preference changes */
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        /* Only follow OS if user hasn't manually set a preference */
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? DARK : LIGHT, true);
        }
      });
    }
  });
})();
