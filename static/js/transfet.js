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
  const conversionHint = document.getElementById('conversionHint');
  const conversionText = document.getElementById('conversionText');

  // ── Курсы валют (те же что в views.py) ───────────────────
  const EXCHANGE_RATES = { TJS: 1.0, USD: 10.92, EUR: 11.80 };

  function convertCurrency(amount, from, to) {
    if (from === to) return amount;
    const inTjs = amount * EXCHANGE_RATES[from];
    return inTjs / EXCHANGE_RATES[to];
  }

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

  // ── Обновляем отображение баланса, остатка и конвертации ─
  function updateBalanceDisplay() {
    const acc = getSelectedAccount();
    if (!acc) return;

    const amount = parseFloat(amountInput.value) || 0;

    // Обновляем бейдж валюты в поле суммы
    amountCurrency.textContent = acc.currency;

    // Доступный баланс
    balanceAvail.textContent = `Доступно: ${acc.balance.toFixed(2)} ${acc.currency}`;

    // Валюта получателя
    const receiverCurrencyRaw  = receiverCur ? receiverCur.textContent.replace('Счёт в ', '').trim() : '';
    const receiverCurrencyCode = receiverCurrencyRaw || acc.currency;

    // Показываем конвертацию если валюты разные и получатель найден
    if (
      amount > 0 &&
      receiverBox &&
      receiverBox.dataset.state === 'found' &&
      receiverCurrencyCode !== acc.currency &&
      EXCHANGE_RATES[receiverCurrencyCode]
    ) {
      const converted = convertCurrency(amount, acc.currency, receiverCurrencyCode);
      if (conversionText) {
        conversionText.textContent =
          `${amount.toFixed(2)} ${acc.currency} → ${converted.toFixed(2)} ${receiverCurrencyCode}`;
      }
      if (conversionHint) conversionHint.style.display = 'flex';
    } else {
      if (conversionHint) conversionHint.style.display = 'none';
    }

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

    if (number.length < 10) {
      receiverBox.dataset.state = 'empty';
      lookupSpinner.classList.remove('visible');
      if (conversionHint) conversionHint.style.display = 'none';
      return;
    }

    lookupSpinner.classList.add('visible');
    receiverBox.dataset.state = 'empty';

    clearTimeout(lookupTimer);

    lookupTimer = setTimeout(() => {
      fetch(`${window.LOOKUP_URL}?number=${encodeURIComponent(number)}`)
        .then((response) => response.json())
        .then((data) => {
          lookupSpinner.classList.remove('visible');

          if (data.found) {
            receiverName.textContent  = data.name;
            receiverCur.textContent   = data.currency ? `Счёт в ${data.currency}` : '';
            receiverBox.dataset.state = 'found';
          } else {
            receiverBox.dataset.state = 'notfound';
          }

          // Пересчитываем конвертацию после получения данных о получателе
          updateBalanceDisplay();
        })
        .catch(() => {
          lookupSpinner.classList.remove('visible');
          receiverBox.dataset.state = 'empty';
        });
    }, 400);
  }

  // ── Обработчики событий ───────────────────────────────────

  if (receiverInput) {
    receiverInput.addEventListener('input', lookupReceiver);
  }

  senderCards.forEach((card) => {
    const radio = card.querySelector('.account-radio-input');
    if (radio) {
      radio.addEventListener('change', updateBalanceDisplay);
    }
  });

  if (amountInput) {
    amountInput.addEventListener('input', updateBalanceDisplay);
  }

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

  if (receiverInput && receiverInput.value.trim().length >= 10) {
    lookupReceiver();
  }
})();