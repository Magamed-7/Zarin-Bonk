document.addEventListener('DOMContentLoaded', function() {
  // Анимация прогресс-баров при загрузке
  const progressFills = document.querySelectorAll('.goal-progress-fill');
  progressFills.forEach(fill => {
    const width = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => {
      fill.style.width = width;
    }, 100);
  });

  // Конфетти при достижении цели
  function createConfetti(x, y) {
    const colors = ['#ffd700', '#ff6b6b', '#48c774', '#3298dc', '#ffb347'];
    for (let i = 0; i < 30; i++) {
      const confetti = document.createElement('div');
      confetti.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        left: ${x}px;
        top: ${y}px;
        pointer-events: none;
        z-index: 9999;
        border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
      `;
      document.body.appendChild(confetti);

      const angle = Math.random() * Math.PI * 2;
      const velocity = 5 + Math.random() * 10;
      const vx = Math.cos(angle) * velocity;
      const vy = Math.sin(angle) * velocity - 5;
      let posX = x;
      let posY = y;
      let opacity = 1;
      let rotation = 0;

      function animate() {
        posX += vx;
        posY += vy;
        vy += 0.5;
        opacity -= 0.02;
        rotation += 10;

        confetti.style.left = posX + 'px';
        confetti.style.top = posY + 'px';
        confetti.style.opacity = opacity;
        confetti.style.transform = `rotate(${rotation}deg)`;

        if (opacity > 0) {
          requestAnimationFrame(animate);
        } else {
          confetti.remove();
        }
      }
      animate();
    }
  }

  // Проверка на достигнутые цели и запуск конфетти
  const completedCards = document.querySelectorAll('.goal-card--completed');
  completedCards.forEach(card => {
    const rect = card.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    setTimeout(() => {
      createConfetti(centerX, centerY);
    }, 500);
  });

  // Анимация карточек при наведении
  const goalCards = document.querySelectorAll('.goal-card:not(.goal-card--completed)');
  goalCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-8px) scale(1.02)';
    });
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });

  // Плавное появление карточек при прокрутке
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '0';
        entry.target.style.transform = 'translateY(20px)';
        entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, 100);
        
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  goalCards.forEach(card => {
    observer.observe(card);
  });
});
