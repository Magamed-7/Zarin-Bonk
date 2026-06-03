(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Fetch and update rates widget
  async function updateRatesWidget() {
    try {
      const response = await fetch('/banking/api/rates/');
      if (!response.ok) return;
      const rates = await response.json();

      const usdEl = document.getElementById('rate-usd');
      const eurEl = document.getElementById('rate-eur');
      const rubEl = document.getElementById('rate-rub');
      const tjsEl = document.getElementById('rate-tjs');
      const gbpEl = document.getElementById('rate-gbp');

      if (usdEl) usdEl.textContent = rates.USD ? rates.USD.toFixed(2) : '-';
      if (eurEl) eurEl.textContent = rates.EUR ? rates.EUR.toFixed(4) : '-';
      if (rubEl) rubEl.textContent = rates.RUB ? rates.RUB.toFixed(4) : '-';
      if (tjsEl) tjsEl.textContent = rates.TJS ? rates.TJS.toFixed(4) : '-';
      if (gbpEl) gbpEl.textContent = rates.GBP ? rates.GBP.toFixed(4) : '-';
    } catch (err) {
      console.warn('Failed to fetch rates:', err);
    }
  }

  // Initial load and refresh every 60s
  updateRatesWidget();
  setInterval(updateRatesWidget, 60000);

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

// ── Card Carousel ───────────────────────────────────────────
const cards = document.querySelectorAll('.carousel-card');
const dots = document.querySelectorAll('.carousel-dot');
const prevBtn = document.getElementById('prevCard');
const nextBtn = document.getElementById('nextCard');
let currentIndex = 0;

if (cards.length > 0 && dots.length > 0) {
  function updateCarousel() {
    cards.forEach((card, index) => {
      card.classList.remove('active');
      
      // Calculate the offset from the current index
      const offset = index - currentIndex;
      
      if (offset === 0) {
        // Active card
        card.classList.add('active');
        card.style.transform = 'scale(1) translateX(0) rotateY(0)';
        card.style.zIndex = 10;
        card.style.opacity = 1;
        card.style.filter = 'blur(0)';
      } else if (offset > 0) {
        // Cards after active
        const scale = Math.max(0.85 - (offset - 1) * 0.1, 0.75);
        const translateX = 120 + (offset - 1) * 40;
        const rotateY = 8 + (offset - 1) * 4;
        card.style.transform = `scale(${scale}) translateX(${translateX}px) rotateY(${rotateY}deg)`;
        card.style.zIndex = 10 - offset;
        card.style.opacity = 1 - offset * 0.2;
        card.style.filter = `blur(${offset * 2}px)`;
      } else {
        // Cards before active
        const positiveOffset = -offset;
        const scale = Math.max(0.85 - (positiveOffset - 1) * 0.1, 0.75);
        const translateX = -120 - (positiveOffset - 1) * 40;
        const rotateY = -8 - (positiveOffset - 1) * 4;
        card.style.transform = `scale(${scale}) translateX(${translateX}px) rotateY(${rotateY}deg)`;
        card.style.zIndex = 10 - positiveOffset;
        card.style.opacity = 1 - positiveOffset * 0.2;
        card.style.filter = `blur(${positiveOffset * 2}px)`;
      }
    });

    dots.forEach((dot, index) => {
      dot.classList.remove('active');
      if (index === currentIndex) {
        dot.classList.add('active');
      }
    });
  }

  // Initial render
  updateCarousel();

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      currentIndex = (currentIndex - 1 + cards.length) % cards.length;
      updateCarousel();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      currentIndex = (currentIndex + 1) % cards.length;
      updateCarousel();
    });
  }

  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      currentIndex = index;
      updateCarousel();
    });
  });

  // Touch/Swipe support
  const carousel = document.getElementById('cardCarousel');
  let startX = 0;
  let endX = 0;

  if (carousel) {
    carousel.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      handleSwipe();
    });

    carousel.addEventListener('mousedown', (e) => {
      startX = e.clientX;
    });

    carousel.addEventListener('mouseup', (e) => {
      endX = e.clientX;
      handleSwipe();
    });

    function handleSwipe() {
      const diff = startX - endX;
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          currentIndex = (currentIndex + 1) % cards.length;
        } else {
          currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        }
        updateCarousel();
      }
    }
  }
}