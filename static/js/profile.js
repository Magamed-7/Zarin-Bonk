(() => {
  'use strict';

  // ── Клик на аватар открывает file input ───────────────────
  const avatarWrap  = document.querySelector('.avatar-wrap');
  const avatarInput = document.querySelector('.avatar-input');
  const avatarImg   = document.querySelector('.avatar-img');
  const avatarPlaceholder = document.querySelector('.avatar-placeholder');
  const avatarForm  = document.querySelector('#avatar-form');

  if (avatarWrap && avatarInput) {
    avatarWrap.addEventListener('click', () => {
      avatarInput.click();
    });

    // Предпросмотр выбранного аватара и отправка формы
    avatarInput.addEventListener('change', () => {
      const file = avatarInput.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        if (avatarImg) {
          avatarImg.src = e.target.result;
        } else if (avatarPlaceholder) {
          // Заменяем placeholder на img
          const img = document.createElement('img');
          img.src       = e.target.result;
          img.className = 'avatar-img';
          avatarPlaceholder.replaceWith(img);
        }
        // Отправляем форму с аватаром
        if (avatarForm) {
          avatarForm.submit();
        }
      };
      reader.readAsDataURL(file);
    });
  }

  // ── Предупреждение если уходят с несохранёнными изменениями
  const form   = document.querySelector('.profile-form');
  let changed  = false;

  if (form) {
    form.querySelectorAll('input, textarea').forEach(el => {
      el.addEventListener('input', () => { changed = true; }, { passive: true });
    });

    form.addEventListener('submit', () => { changed = false; });

    window.addEventListener('beforeunload', e => {
      if (changed) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
  }
})();