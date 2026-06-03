// Resend Verification Email
window.resendVerification = async () => {
  const bannerBtn = document.getElementById('resendBannerBtn');
  const profileBtn = document.getElementById('resendProfileBtn');
  const banner = document.getElementById('unverifiedBanner');

  const disableButtons = (text) => {
    if (bannerBtn) {
      bannerBtn.disabled = true;
      bannerBtn.textContent = text;
    }
    if (profileBtn) {
      profileBtn.disabled = true;
      profileBtn.textContent = text;
    }
  };

  const enableButtons = () => {
    if (bannerBtn) {
      bannerBtn.disabled = false;
      bannerBtn.textContent = 'Отправить письмо';
    }
    if (profileBtn) {
      profileBtn.disabled = false;
      profileBtn.textContent = '📧 Отправить письмо повторно';
    }
  };

  const showFlash = (message, type = 'success') => {
    const container = document.querySelector('.page');
    if (!container) return;

    const flash = document.createElement('div');
    flash.className = `flash flash-${type}`;
    flash.style.marginTop = '1rem';
    flash.innerHTML = `
      <div class="flash-dot" aria-hidden="true"></div>
      <div class="flash-text">${message}</div>
      <button class="flash-close" type="button" aria-label="Закрыть">✕</button>
    `;

    container.insertBefore(flash, container.firstChild);

    // Auto-remove flash after 5 seconds
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-6px)';
      flash.style.transition = 'opacity .18s ease, transform .18s ease';
      setTimeout(() => flash.remove(), 190);
    }, 5000);

    // Close button
    const closeBtn = flash.querySelector('.flash-close');
    closeBtn.addEventListener('click', () => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-6px)';
      flash.style.transition = 'opacity .18s ease, transform .18s ease';
      setTimeout(() => flash.remove(), 190);
    });
  };

  try {
    disableButtons('Отправка...');

    const response = await fetch('/accounts/resend-verification/', {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    });

    const data = await response.json();

    if (response.ok) {
      showFlash(data.message, 'success');

      // Start cooldown timer
      const cooldownSeconds = data.cooldown || 60;
      let remaining = cooldownSeconds;

      const countdown = setInterval(() => {
        remaining--;
        const text = `Подождите ${remaining}с`;
        if (bannerBtn) bannerBtn.textContent = text;
        if (profileBtn) profileBtn.textContent = `⌛ Подождите ${remaining}с`;

        if (remaining <= 0) {
          clearInterval(countdown);
          enableButtons();
        }
      }, 1000);

    } else {
      showFlash(data.message || 'Ошибка отправки письма', 'warning');
      enableButtons();
    }

  } catch (error) {
    console.error('Error resending verification:', error);
    showFlash('Произошла ошибка при отправке', 'error');
    enableButtons();
  }
};

(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!prefersReducedMotion) {
    document.documentElement.style.scrollBehavior = "smooth";
  }

  // Loading Overlay Functions
  const loadingOverlay = document.getElementById("loadingOverlay");
  window.showLoading = () => {
    if (loadingOverlay) {
      loadingOverlay.style.display = "flex";
    }
  };
  window.hideLoading = () => {
    if (loadingOverlay) {
      loadingOverlay.style.display = "none";
    }
  };

  // Page Transition on click
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a[href]");
    if (link && link.href && !link.href.startsWith("javascript:") && !link.target) {
      const url = new URL(link.href, window.location.origin);
      if (url.origin === window.location.origin && !link.href.includes("#")) {
        e.preventDefault();
        const page = document.querySelector(".page");
        if (page) {
          page.classList.add("fade-out");
          setTimeout(() => {
            window.location.href = link.href;
          }, 300);
        } else {
          window.location.href = link.href;
        }
      }
    }
  });

  // Close flash messages
  document.querySelectorAll(".flash-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      const el = btn.closest(".flash");
      if (!el) return;
      el.style.opacity = "0";
      el.style.transform = "translateY(-6px)";
      el.style.transition = "opacity .18s ease, transform .18s ease";
      window.setTimeout(() => el.remove(), 190);
    });
  });

  // Card 3D tilt effect
  const state = {
    tiltEnabled: !prefersReducedMotion,
  };

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const cards = Array.from(document.querySelectorAll(".card-3d"));

  const applyTilt = (el, ev) => {
    const r = el.getBoundingClientRect();
    const px = (ev.clientX - r.left) / r.width;
    const py = (ev.clientY - r.top) / r.height;
    const rx = clamp((0.5 - py) * 10, -10, 10);
    const ry = clamp((px - 0.5) * 14, -14, 14);
    el.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-1px)`;
  };

  const resetTilt = (el) => {
    el.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg)";
  };

  cards.forEach((el) => {
    el.addEventListener("mousemove", (ev) => {
      if (!state.tiltEnabled) return;
      applyTilt(el, ev);
    });
    el.addEventListener("mouseleave", () => resetTilt(el));
  });

  const tiltToggle = document.getElementById("ui-tilt-toggle");
  if (tiltToggle) {
    tiltToggle.addEventListener("click", () => {
      state.tiltEnabled = !state.tiltEnabled;
      tiltToggle.classList.toggle("is-on", state.tiltEnabled);
      cards.forEach((c) => resetTilt(c));
    });
  }

  // Optional mini chart (if Chart.js is available)
  const canvas = document.getElementById("miniChart");
  if (canvas && window.Chart) {
    const ctx = canvas.getContext("2d");
    const grad = ctx.createLinearGradient(0, 0, 0, 180);
    grad.addColorStop(0, "rgba(255, 215, 0, 0.40)");
    grad.addColorStop(1, "rgba(255, 215, 0, 0.02)");

    // eslint-disable-next-line no-new
    new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [
          {
            label: "Balance",
            data: [11200, 11420, 11610, 11540, 11820, 12150, 12480],
            borderColor: "rgba(255, 215, 0, 0.95)",
            backgroundColor: grad,
            tension: 0.35,
            pointRadius: 0,
            fill: true,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: "rgba(10, 14, 28, 0.92)",
            borderColor: "rgba(255, 215, 0, 0.25)",
            borderWidth: 1,
            titleColor: "rgba(255,255,255,0.95)",
            bodyColor: "rgba(255,255,255,0.85)",
          },
        },
        scales: {
          x: { display: false },
          y: { display: false },
        },
      },
    });
  }
})();
