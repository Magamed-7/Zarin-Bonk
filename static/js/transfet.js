(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Элементы DOM ─────────────────────────────────────────
  const receiverInput  = document.getElementById('id_receiver_number');
  const receiverBox    = document.getElementById('receiverBox');
  const receiverName   = document.getElementById('receiverName');
  const receiverCur    = document.getElementById('receiverCurrency');
  const lookupSpinner  = document.getElementById('lookupSpinner');
  const amountInput    = document.getElementById('id_amount');
  const amountCurrency = document.getElementById('amountCurrency');
  const balanceAvail   = document.getElementById('balanceAvailable');
  const balanceAfter   = document.getElementById('balanceAfter');
  const transferBtn    = document.getElementById('transferBtn');
  const transferForm   = document.getElementById('transferForm');
  const senderCards    = document.querySelectorAll('.account-radio-card');

  // ── Получаем данные выбранного счёта ─────────────────────
  function getSelectedAccount() {
    const checked = document.querySelector('.account-radio-input:checked');
    if (!checked) return null;

    const card = checked.closest('.account-radio-card');
    return {
      balance:  parseFloat(card.dataset.balance) || 0,
      currency: card.dataset.currency || 'TJS',
    };
  }

  // ── Обновляем отображение баланса и остатка ───────────────
  function updateBalanceDisplay() {
    const acc = getSelectedAccount();
    if (!acc) return;

    const amount = parseFloat(amountInput.value) || 0;

    // Обновляем бейдж валюты в поле суммы
    amountCurrency.textContent = acc.currency;

    // Доступный баланс
    balanceAvail.textContent = `Доступно: ${acc.balance.toFixed(2)} ${acc.currency}`;

    // Остаток после перевода
    if (amount <= 0) {
      balanceAfter.textContent = '';
      balanceAfter.className   = 'balance-hint-after';
      return;
    }

    const after = acc.balance - amount;

    if (amount > acc.balance) {
      balanceAfter.textContent = `Недостаточно средств на ${(amount - acc.balance).toFixed(2)} ${acc.currency}`;
      balanceAfter.className   = 'balance-hint-after is-error';
    } else if (after < acc.balance * 0.1) {
      // Остаток меньше 10% — предупреждение
      balanceAfter.textContent = `Останется: ${after.toFixed(2)} ${acc.currency}`;
      balanceAfter.className   = 'balance-hint-after is-warning';
    } else {
      balanceAfter.textContent = `Останется: ${after.toFixed(2)} ${acc.currency}`;
      balanceAfter.className   = 'balance-hint-after is-ok';
    }
  }

  // ── AJAX поиск получателя с debounce ─────────────────────
  let lookupTimer = null;

  function lookupReceiver() {
    const number = receiverInput.value.trim();

    // Меньше 10 символов — не ищем
    if (number.length < 10) {
      receiverBox.dataset.state = 'empty';
      lookupSpinner.classList.remove('visible');
      return;
    }

    // Показываем спиннер
    lookupSpinner.classList.add('visible');
    receiverBox.dataset.state = 'empty';

    clearTimeout(lookupTimer);

    // Ждём 400мс после последнего нажатия — debounce
    lookupTimer = setTimeout(() => {
      fetch(`${window.LOOKUP_URL}?number=${encodeURIComponent(number)}`)
        .then((response) => response.json())
        .then((data) => {
          lookupSpinner.classList.remove('visible');

          if (data.found) {
            receiverName.textContent = data.name;
            receiverCur.textContent  = data.currency ? `Счёт в ${data.currency}` : '';
            receiverBox.dataset.state = 'found';
          } else {
            receiverBox.dataset.state = 'notfound';
          }
        })
        .catch(() => {
          // Сеть недоступна — просто скрываем
          lookupSpinner.classList.remove('visible');
          receiverBox.dataset.state = 'empty';
        });
    }, 400);
  }

  // ── Обработчики событий ───────────────────────────────────

  // Ввод номера получателя
  if (receiverInput) {
    receiverInput.addEventListener('input', lookupReceiver);
  }

  // Смена счёта отправителя
  senderCards.forEach((card) => {
    const radio = card.querySelector('.account-radio-input');
    if (radio) {
      radio.addEventListener('change', updateBalanceDisplay);
    }
  });

  // Ввод суммы
  if (amountInput) {
    amountInput.addEventListener('input', updateBalanceDisplay);
  }

  // Отправка формы — показываем спиннер кнопки
  if (transferForm) {
    transferForm.addEventListener('submit', () => {
      if (transferBtn) {
        transferBtn.classList.add('is-loading');
        transferBtn.disabled = true;
      }
    });
  }

  // ── Инициализация при загрузке ────────────────────────────
  updateBalanceDisplay();

  // Если номер получателя уже заполнен (при ошибке формы) — запускаем поиск
  if (receiverInput && receiverInput.value.trim().length >= 10) {
    lookupReceiver();
  }
})();