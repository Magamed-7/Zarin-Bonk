(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;

  // ── 3D tilt на карточках счетов ───────────────────────────
  document.querySelectorAll('.account-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const dx   = (e.clientX - rect.left - rect.width  / 2) / (rect.width  / 2);
      const dy   = (e.clientY - rect.top  - rect.height / 2) / (rect.height / 2);

      card.style.transform =
        `translateY(-6px) rotateX(${dy * -5}deg) rotateY(${dx * 5}deg) scale(1.01)`;
    }, { passive: true });

    card.addEventListener('mouseleave', () => {
      card.style.transition = 'transform 0.4s ease, box-shadow 0.4s ease';
      card.style.transform  = '';
      setTimeout(() => { card.style.transition = ''; }, 400);
    }, { passive: true });
  });
})();