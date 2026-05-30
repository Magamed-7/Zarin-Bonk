(() => {
  'use strict';

  // ── Код (страница ввода кода) ─────────────────────────────
  const boxes       = document.querySelectorAll('.code-input');
  const hiddenInput = document.getElementById('id_code');
  const form        = document.querySelector('.reset-form');

  if (boxes.length && hiddenInput) {
    boxes.forEach((box, index) => {
      box.addEventListener('keydown', e => {
        if (e.key === 'Backspace') {
          box.value = '';
          syncHidden();
          if (index > 0) boxes[index - 1].focus();
          e.preventDefault();
          return;
        }
        if (!/^\d$/.test(e.key) && !e.metaKey && !e.ctrlKey) {
          e.preventDefault();
        }
      });

      box.addEventListener('input', () => {
        box.value = box.value.slice(-1).replace(/\D/, '');
        box.classList.toggle('filled', box.value !== '');
        syncHidden();
        if (box.value && index < boxes.length - 1) {
          boxes[index + 1].focus();
        }
        if (getCode().length === 6) {
          setTimeout(() => form && form.submit(), 200);
        }
      });

      box.addEventListener('paste', e => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData)
          .getData('text').replace(/\D/g, '').slice(0, 6);
        pasted.split('').forEach((char, i) => {
          if (boxes[i]) { boxes[i].value = char; boxes[i].classList.add('filled'); }
        });
        syncHidden();
        if (pasted.length === 6) setTimeout(() => form && form.submit(), 200);
      });
    });

    function getCode() {
      return Array.from(boxes).map(b => b.value).join('');
    }

    function syncHidden() {
      hiddenInput.value = getCode();
    }

    // Фокус на первый пустой
    const firstEmpty = Array.from(boxes).find(b => !b.value);
    if (firstEmpty) firstEmpty.focus();
  }

  // ── Password toggle (страница нового пароля) ──────────────
  document.querySelectorAll('.field-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.field-input-wrap').querySelector('.field-input');
      if (!input) return;
      const isText = input.type === 'text';
      input.type    = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁️' : '🙈';
    });
  });
})();