(() => {
  'use strict';

  const oldInput     = document.getElementById('id_old_password');
  const newInput     = document.getElementById('id_new_password');
  const confirmInput = document.getElementById('id_password_confirm');
  const submitBtn    = document.querySelector('.cp-btn');

  // ── Показать/скрыть пароль ────────────────────────────────
  document.querySelectorAll('.field-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.field-input-wrap').querySelector('.field-input');
      if (!input) return;
      const isText    = input.type === 'text';
      input.type      = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁️' : '🙈';
    });
  });

  // ── Сила пароля ───────────────────────────────────────────
  const strengthFill = document.querySelector('.strength-fill');

  function updateStrength(value) {
    if (!strengthFill) return;
    let score = 0;
    if (value.length >= 8)           score++;
    if (/[A-Z]/.test(value))         score++;
    if (/[0-9]/.test(value))         score++;
    if (/[^A-Za-z0-9]/.test(value))  score++;

    const colors = ['#ff4444', '#ff944d', '#ffd700', '#48c774'];
    strengthFill.style.width      = (score / 4 * 100) + '%';
    strengthFill.style.background = colors[score - 1] || 'rgba(255,255,255,0.1)';
  }

  if (newInput) {
    newInput.addEventListener('input', () => {
      updateStrength(newInput.value);
      validateNew();
      if (confirmInput && confirmInput.value) validateConfirm();
    }, { passive: true });
  }

  // ── Валидация полей ───────────────────────────────────────
  function setField(input, valid, okText, errorText) {
    if (!input) return;
    const field = input.closest('.field');
    const hint  = field.querySelector('.field-hint');
    if (!field) return;

    field.classList.toggle('is-valid',   valid);
    field.classList.toggle('is-invalid', !valid);
    if (hint) hint.textContent = valid ? okText : errorText;
  }

  function validateOld() {
    if (!oldInput) return true;
    const ok = oldInput.value.length >= 1;
    if (oldInput.value.length > 0) {
      setField(oldInput, ok, '', 'Введите старый пароль');
    }
    return ok;
  }

  function validateNew() {
    if (!newInput) return true;
    const ok = newInput.value.length >= 8;
    if (newInput.value.length > 0) {
      setField(newInput, ok, 'Минимум 8 символов', 'Минимум 8 символов');
    }
    return ok;
  }

  function validateConfirm() {
    if (!confirmInput || !newInput) return true;
    const ok = confirmInput.value === newInput.value && confirmInput.value.length > 0;
    if (confirmInput.value.length > 0) {
      setField(confirmInput, ok, 'Пароли совпадают', 'Пароли не совпадают');
    }
    return ok;
  }

  if (oldInput)     oldInput.addEventListener('blur',  validateOld,     { passive: true });
  if (confirmInput) confirmInput.addEventListener('input', validateConfirm, { passive: true });

  // ── Submit ────────────────────────────────────────────────
  const form = document.querySelector('.cp-form');
  if (form) {
    form.addEventListener('submit', e => {
      const ok = validateOld() && validateNew() && validateConfirm();
      if (!ok) {
        e.preventDefault();
        // Тряска карточки
        const card = document.querySelector('.change-password-card');
        if (card) {
          card.style.animation = 'none';
          card.offsetHeight;
          card.style.animation = 'shake 0.4s ease';
        }
      }
    });
  }

  // Keyframe для тряски
  if (!document.getElementById('zp-shake-style')) {
    const style = document.createElement('style');
    style.id = 'zp-shake-style';
    style.textContent = `
      @keyframes shake {
        0%,100% { transform: translateX(0); }
        25%      { transform: translateX(-8px); }
        75%      { transform: translateX( 8px); }
      }
    `;
    document.head.appendChild(style);
  }
})();