(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Анимация счётчика баланса ─────────────────────────────
  const balanceEl = document.querySelector('.balance-amount');

  if (balanceEl && !prefersReducedMotion) {
    const target   = parseFloat(balanceEl.dataset.value) || 0;
    const currency = balanceEl.dataset.currency || '';
    const duration = 1400;  // мс
    const start    = performance.now();

    function tick(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);

      // Easing: ease-out
      const eased    = 1 - Math.pow(1 - progress, 3);
      const current  = target * eased;

      balanceEl.textContent =
        current.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
        + ' '
        + currency;

      if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
  }

  // ── Chart.js — расходы за неделю ──────────────────────────
  const chartCanvas = document.getElementById('weeklyChart');

  if (chartCanvas && typeof Chart !== 'undefined') {
    const labels = JSON.parse(chartCanvas.dataset.labels || '[]');
    const data   = JSON.parse(chartCanvas.dataset.values || '[]');

    new Chart(chartCanvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Расходы',
          data,
          backgroundColor: 'rgba(255, 215, 0, 0.25)',
          borderColor:     'rgba(255, 215, 0, 0.8)',
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
        }],
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.raw.toLocaleString('ru-RU')} TJS`,
            },
          },
        },
        scales: {
          x: {
            grid:  { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#8892b0', font: { size: 11 } },
          },
          y: {
            grid:  { color: 'rgba(255,255,255,0.05)' },
            ticks: {
              color: '#8892b0',
              font:  { size: 11 },
              callback: val => val.toLocaleString('ru-RU'),
            },
            beginAtZero: true,
          },
        },
      },
    });
  }
})();


const flipBtn = document.getElementById('flipBtn');
const bankCard = document.getElementById('bankCard');

if (flipBtn && bankCard){

let flipped = false;

let rx = 0;
let ry = 0;

function updateTransform(){

const flipRotation = flipped ? 180 : 0;

bankCard.style.transform =
`rotateX(${rx}deg)
 rotateY(${ry + flipRotation}deg)`;

}

flipBtn.addEventListener('click',()=>{

flipped = !flipped;

updateTransform();

});

bankCard.addEventListener('mousemove',(e)=>{

const rect = bankCard.getBoundingClientRect();

const x = e.clientX - rect.left;
const y = e.clientY - rect.top;

rx = -(y - rect.height/2) / 18;

ry = (x - rect.width/2) / 18;

updateTransform();

});

bankCard.addEventListener('mouseleave',()=>{

rx = 0;
ry = 0;

updateTransform();

});

updateTransform();

}

const amountInput =
document.getElementById(
'amountInput'
);

document
.querySelectorAll(
'.quick-btn'
)
.forEach(btn=>{

btn.addEventListener(
'click',
()=>{

amountInput.value=
btn.dataset.value;

});

});