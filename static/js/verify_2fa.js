(() => {
  'use strict';

  const boxes      = document.querySelectorAll('.code-input');
  const hiddenInput = document.getElementById('id_code');
  const form       = document.querySelector('.twofa-form');
  const btn        = document.querySelector('.twofa-btn');
  const errorEl    = document.querySelector('.twofa-error');
  const timerEl    = document.querySelector('.timer-value');

  if (!boxes.length || !hiddenInput) return;

  // ── Countdown timer (5 минут) ─────────────────────────────
  let secondsLeft = 5 * 60;

  function updateTimer() {
    const m = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
    const s = String(secondsLeft % 60).padStart(2, '0');
    if (timerEl) {
      timerEl.textContent = `${m}:${s}`;
      timerEl.classList.toggle('expiring', secondsLeft <= 30);
    }

    if (secondsLeft <= 0) {
      if (btn) btn.disabled = true;
      boxes.forEach(b => { b.disabled = true; });
      if (errorEl) {
        errorEl.textContent = 'Код истёк. Вернитесь на страницу входа.';
        errorEl.classList.add('visible');
      }
      return;
    }

    secondsLeft--;
    setTimeout(updateTimer, 1000);
  }

  updateTimer();

  // ── Code input navigation ─────────────────────────────────
  boxes.forEach((box, index) => {
    // Только цифры
    box.addEventListener('keydown', e => {
      if (e.key === 'Backspace') {
        box.value = '';
        syncHidden();
        if (index > 0) boxes[index - 1].focus();
        e.preventDefault();
        return;
      }
      if (e.key === 'ArrowLeft' && index > 0) {
        boxes[index - 1].focus();
        e.preventDefault();
        return;
      }
      if (e.key === 'ArrowRight' && index < boxes.length - 1) {
        boxes[index + 1].focus();
        e.preventDefault();
        return;
      }
      // Разрешаем только цифры
      if (!/^\d$/.test(e.key) && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
      }
    });

    box.addEventListener('input', () => {
      // Оставляем только последний введённый символ
      box.value = box.value.slice(-1).replace(/\D/, '');
      box.classList.toggle('filled', box.value !== '');
      syncHidden();

      if (box.value && index < boxes.length - 1) {
        boxes[index + 1].focus();
      }

      // Автосабмит когда все 6 цифр введены
      if (getCode().length === 6) {
        setTimeout(() => form && form.submit(), 200);
      }
    });

    // Вставка кода из буфера (например из SMS)
    box.addEventListener('paste', e => {
      e.preventDefault();
      const pasted = (e.clipboardData || window.clipboardData)
        .getData('text')
        .replace(/\D/g, '')
        .slice(0, 6);

      pasted.split('').forEach((char, i) => {
        if (boxes[i]) {
          boxes[i].value = char;
          boxes[i].classList.add('filled');
        }
      });

      syncHidden();
      const next = Math.min(pasted.length, boxes.length - 1);
      boxes[next].focus();

      if (pasted.length === 6) {
        setTimeout(() => form && form.submit(), 200);
      }
    });
  });

  function getCode() {
    return Array.from(boxes).map(b => b.value).join('');
  }

  function syncHidden() {
    hiddenInput.value = getCode();
  }

  // ── Shake on server error ─────────────────────────────────
  if (errorEl && errorEl.dataset.hasErrors === 'true') {
    errorEl.classList.add('visible');
    boxes.forEach(b => b.classList.add('is-error'));

    const card = document.querySelector('.twofa-card');
    if (card) {
      card.style.animation = 'shake 0.4s ease';
    }

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
  }

  // Фокус на первый пустой
  const firstEmpty = Array.from(boxes).find(b => !b.value);
  if (firstEmpty) firstEmpty.focus();
})();

// ── Resend countdown timer ────────────────────────────────────
const resendTimerEl = document.querySelector('.resend-timer');
if (resendTimerEl) {
  let seconds = parseInt(resendTimerEl.dataset.seconds, 10) || 0;

  function tickResend() {
    if (seconds <= 0) {
      // Заменяем таймер на ссылку
      const resendWrap = resendTimerEl.closest('.twofa-resend');
      if (resendWrap) {
        resendWrap.innerHTML =
          'Не получили код? <a href="/accounts/resend-2fa/">Отправить снова</a>';
      }
      return;
    }
    resendTimerEl.textContent = seconds;
    seconds--;
    setTimeout(tickResend, 1000);
  }

  tickResend();
}