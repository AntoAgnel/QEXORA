// QEXORA – main.js

// ── Apply saved theme immediately on every page ──────────────────────────────
(function() {
  const saved = localStorage.getItem('qexora_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {

  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity    = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Animate bar charts on load
  document.querySelectorAll('.bar-inner').forEach(bar => {
    const w = bar.style.width;
    bar.style.width = '0';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = w; }, 100);
    });
  });

});
