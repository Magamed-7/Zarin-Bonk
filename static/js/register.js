(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── DOM refs ──────────────────────────────────────────────
  const card    = document.querySelector('.register-card');
  const wrapper = document.querySelector('.register-wrapper');
  const form    = document.querySelector('.register-form');
  const btn     = document.querySelector('.register-btn');

  if (!card || !form) return;

  // ── 3D tilt on mouse move ─────────────────────────────────
  if (!prefersReducedMotion && wrapper) {
    wrapper.addEventListener('mousemove', onMouseMove, { passive: true });
    wrapper.addEventListener('mouseleave', onMouseLeave, { passive: true });
  }

  function onMouseMove(e) {
    const rect   = wrapper.getBoundingClientRect();
    const cx     = rect.left + rect.width  / 2;
    const cy     = rect.top  + rect.height / 2;
    const dx     = (e.clientX - cx) / (rect.width  / 2);
    const dy     = (e.clientY - cy) / (rect.height / 2);
    const rotateX =  dy * -8;   // degrees
    const rotateY =  dx *  8;

    card.style.transform =
      `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    card.style.boxShadow =
      `${-rotateY * 2}px ${rotateX * 2}px 40px rgba(0,0,0,0.5),` +
      `0 0 0 1px rgba(255,215,0,0.08)`;
  }

  function onMouseLeave() {
    card.style.transition = 'transform 0.5s ease, box-shadow 0.5s ease';
    card.style.transform  = '';
    card.style.boxShadow  = '';
    setTimeout(() => { card.style.transition = ''; }, 500);
  }

  // ── Field rules ───────────────────────────────────────────
  const RULES = {
    id_first_name: {
      validate: v => v.trim().length >= 2,
      ok:    'Отлично',
      error: 'Минимум 2 символа',
    },
    id_last_name: {
      validate: v => v.trim().length >= 2,
      ok:    'Отлично',
      error: 'Минимум 2 символа',
    },
    id_email: {
      validate: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()),
      ok:    'Корректный email',
      error: 'Введите корректный email',
    },
    id_phone: {
      validate: v => {
        if (!v.trim()) return true;           // optional
        return /^\+?[\d\s\-()]{7,20}$/.test(v.trim());
      },
      ok:    '',
      error: 'Некорректный номер',
    },
    id_password: {
      validate: v => v.length >= 8,
      ok:    'Надёжный пароль',
      error: 'Минимум 8 символов',
    },
    id_password_confirm: {
      validate: v => {
        const pwd = document.getElementById('id_password');
        return pwd && v === pwd.value;
      },
      ok:    'Пароли совпадают',
      error: 'Пароли не совпадают',
    },
  };

  // ── Attach listeners ──────────────────────────────────────
  Object.keys(RULES).forEach(id => {
    const input = document.getElementById(id);
    if (!input) return;

    input.addEventListener('input', () => validateField(input), { passive: true });
    input.addEventListener('blur',  () => validateField(input, true), { passive: true });
  });

  // Re-validate confirm when password changes
  const pwdInput = document.getElementById('id_password');
  if (pwdInput) {
    pwdInput.addEventListener('input', () => {
      updateStrength(pwdInput.value);
      const confirm = document.getElementById('id_password_confirm');
      if (confirm && confirm.value) validateField(confirm, true);
    }, { passive: true });
  }

  // ── Password toggles ───────────────────────────────────────
  function setupPasswordToggle(inputId) {
    const input = document.getElementById(inputId);
    const fieldWrap = input ? input.closest('.field-input-wrap') : null;
    const toggle = fieldWrap ? fieldWrap.querySelector('.field-toggle') : null;

    if (input && toggle) {
      toggle.addEventListener('click', () => {
        const isText = input.type === 'text';
        input.type = isText ? 'password' : 'text';
        toggle.textContent = isText ? '👁️' : '🙈';
      });
    }
  }

  setupPasswordToggle('id_password');
  setupPasswordToggle('id_password_confirm');

  function validateField(input, strict = false) {
    const rule  = RULES[input.id];
    if (!rule) return true;

    const field = input.closest('.field');
    if (!field) return true;

    const hint  = field.querySelector('.field-hint');
    const value = input.value;

    if (!strict && !value) {
      field.classList.remove('is-valid', 'is-invalid');
      if (hint) hint.textContent = '';
      return true;
    }

    const valid = rule.validate(value);
    field.classList.toggle('is-valid',   valid);
    field.classList.toggle('is-invalid', !valid);

    if (hint) {
      hint.textContent = valid
        ? (rule.ok || '')
        : rule.error;
    }

    return valid;
  }

  // ── Password strength ─────────────────────────────────────
  function updateStrength(pwd) {
    const fill = document.querySelector('.strength-fill');
    if (!fill) return;

    let score = 0;
    if (pwd.length >= 8)              score++;
    if (/[A-Z]/.test(pwd))            score++;
    if (/[0-9]/.test(pwd))            score++;
    if (/[^A-Za-z0-9]/.test(pwd))    score++;

    const pct    = (score / 4) * 100;
    const colors = ['#ff4444', '#ff944d', '#ffd700', '#48c774'];
    fill.style.width      = pct + '%';
    fill.style.background = colors[score - 1] || 'rgba(255,255,255,0.1)';
  }

  // ── Form submit ───────────────────────────────────────────
  form.addEventListener('submit', e => {
    // Run all validations
    let allValid = true;
    Object.keys(RULES).forEach(id => {
      const input = document.getElementById(id);
      if (input && !validateField(input, true)) allValid = false;
    });

    if (!allValid) {
      e.preventDefault();
      shakeCard();
      return;
    }

    // Show loading state
    if (btn) {
      btn.classList.add('loading');
      btn.disabled = true;
    }
    card.classList.add('is-submitting');
  });

  function shakeCard() {
    if (prefersReducedMotion) return;
    card.style.animation = 'none';
    card.offsetHeight;   // reflow
    card.style.animation = 'shake 0.4s ease';
  }

  // Inject shake keyframe once
  if (!document.getElementById('zp-shake-style')) {
    const style = document.createElement('style');
    style.id = 'zp-shake-style';
    style.textContent = `
      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20%       { transform: translateX(-8px) rotateZ(-1deg); }
        40%       { transform: translateX( 8px) rotateZ( 1deg); }
        60%       { transform: translateX(-5px) rotateZ(-0.5deg); }
        80%       { transform: translateX( 5px) rotateZ( 0.5deg); }
      }
    `;
    document.head.appendChild(style);
  }
})();