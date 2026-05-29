(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const card    = document.querySelector('.login-card');
  const wrapper = document.querySelector('.login-wrapper');
  const form    = document.querySelector('.login-form');
  const btn     = document.querySelector('.login-btn');
  const errorBanner = document.querySelector('.login-error');

  if (!card || !form) return;

  // ── 3D tilt ───────────────────────────────────────────────
  if (!prefersReducedMotion && wrapper) {
    wrapper.addEventListener('mousemove', onMouseMove, { passive: true });
    wrapper.addEventListener('mouseleave', onMouseLeave, { passive: true });
  }

  function onMouseMove(e) {
    const rect  = wrapper.getBoundingClientRect();
    const dx    = (e.clientX - rect.left - rect.width  / 2) / (rect.width  / 2);
    const dy    = (e.clientY - rect.top  - rect.height / 2) / (rect.height / 2);
    card.style.transform =
      `rotateX(${dy * -7}deg) rotateY(${dx * 7}deg)`;
  }

  function onMouseLeave() {
    card.style.transition = 'transform 0.5s ease';
    card.style.transform  = '';
    setTimeout(() => { card.style.transition = ''; }, 500);
  }

  // ── Password toggle ───────────────────────────────────────
  const pwdInput  = document.getElementById('id_password');
  const pwdToggle = document.querySelector('.field-toggle');

  if (pwdInput && pwdToggle) {
    pwdToggle.addEventListener('click', () => {
      const isText = pwdInput.type === 'text';
      pwdInput.type        = isText ? 'password' : 'text';
      pwdToggle.textContent = isText ? '👁️' : '🙈';
    });
  }

  // ── Real-time validation ──────────────────────────────────
  const emailInput = document.getElementById('id_email');

  if (emailInput) {
    emailInput.addEventListener('blur', () => validateEmail(), { passive: true });
    emailInput.addEventListener('input', () => {
      if (emailInput.closest('.field').classList.contains('is-invalid')) {
        validateEmail();
      }
    }, { passive: true });
  }

  if (pwdInput) {
    pwdInput.addEventListener('blur', () => validatePassword(), { passive: true });
  }

  function validateEmail() {
    const field = emailInput.closest('.field');
    const hint  = field.querySelector('.field-hint');
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(emailInput.value.trim());
    field.classList.toggle('is-invalid', !valid && emailInput.value.length > 0);
    if (hint) hint.textContent = valid ? '' : 'Введите корректный email';
    return valid;
  }

  function validatePassword() {
    const field = pwdInput.closest('.field');
    const hint  = field.querySelector('.field-hint');
    const valid = pwdInput.value.length >= 1;
    field.classList.toggle('is-invalid', !valid);
    if (hint) hint.textContent = valid ? '' : 'Введите пароль';
    return valid;
  }

  // ── Error banner (server-side errors) ────────────────────
  if (errorBanner && errorBanner.dataset.hasErrors === 'true') {
    errorBanner.classList.add('visible');
    shakeCard();
  }

  // ── Submit ────────────────────────────────────────────────
  form.addEventListener('submit', e => {
    const emailOk = validateEmail();
    const pwdOk   = validatePassword();

    if (!emailOk || !pwdOk) {
      e.preventDefault();
      shakeCard();
      return;
    }

    if (btn) {
      btn.classList.add('loading');
      btn.disabled = true;
    }
  });

  function shakeCard() {
    if (prefersReducedMotion) return;
    card.style.animation = 'none';
    card.offsetHeight;
    card.style.animation = 'shake 0.4s ease';
  }

  if (!document.getElementById('zp-shake-style')) {
    const style = document.createElement('style');
    style.id = 'zp-shake-style';
    style.textContent = `
      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20%       { transform: translateX(-8px) rotateZ(-1deg); }
        40%       { transform: translateX( 8px) rotateZ( 1deg); }
        60%       { transform: translateX(-5px); }
        80%       { transform: translateX( 5px); }
      }
    `;
    document.head.appendChild(style);
  }
})();