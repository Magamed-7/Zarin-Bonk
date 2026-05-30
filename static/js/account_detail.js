(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── 3D tilt на карточках ──────────────────────────────────
  if (!prefersReducedMotion) {
    document.querySelectorAll('.detail-card').forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width  - 0.5;
        const y = (e.clientY - rect.top)  / rect.height - 0.5;
        card.style.transform = `perspective(900px) rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg)';
      });
    });
  }

  // ── График баланса за 30 дней ─────────────────────────────
  const canvas = document.getElementById('balanceChart');
  if (!canvas || !window.Chart) return;

  const labels = window.BALANCE_LABELS || [];
  const data   = window.BALANCE_DATA   || [];

  const ctx  = canvas.getContext('2d');

  // Градиент под линией
  const gradient = ctx.createLinearGradient(0, 0, 0, 200);
  gradient.addColorStop(0, 'rgba(255, 215, 0, 0.30)');
  gradient.addColorStop(1, 'rgba(255, 215, 0, 0.01)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Баланс',
        data: data,
        borderColor: 'rgba(255, 215, 0, 0.9)',
        backgroundColor: gradient,
        borderWidth: 2,
        tension: 0.4,        // плавная кривая
        pointRadius: 0,      // без точек на линии
        pointHitRadius: 12,  // но hover работает
        fill: true,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: prefersReducedMotion ? 0 : 800,
      },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(10, 14, 28, 0.92)',
          borderColor: 'rgba(255, 215, 0, 0.25)',
          borderWidth: 1,
          titleColor: 'rgba(255, 255, 255, 0.9)',
          bodyColor: 'rgba(255, 255, 255, 0.75)',
          padding: 10,
          callbacks: {
            // Форматируем сумму в тултипе
            label(ctx) {
              return ` ${ctx.parsed.y.toFixed(2)}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.04)',
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.4)',
            font: { size: 11 },
            // Показываем только каждый 5-й лейбл чтобы не было каши
            maxTicksLimit: 6,
          },
        },
        y: {
          grid: {
            color: 'rgba(255, 255, 255, 0.04)',
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.4)',
            font: { size: 11 },
            callback(value) {
              // Сокращаем большие числа: 12000 → 12K
              if (Math.abs(value) >= 1000) {
                return (value / 1000).toFixed(1) + 'K';
              }
              return value;
            },
          },
        },
      },
    },
  });
})();