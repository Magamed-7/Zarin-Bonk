(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const revealItems = document.querySelectorAll(".reveal");

  if (revealItems.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.16 }
    );

    revealItems.forEach((el) => io.observe(el));
  }

  if (prefersReducedMotion) return;

  const layers = Array.from(document.querySelectorAll(".parallax-layer"));
  if (!layers.length) return;

  let ticking = false;

  const onScroll = () => {
    if (ticking) return;
    ticking = true;

    window.requestAnimationFrame(() => {
      const scrollY = window.scrollY || window.pageYOffset;
      layers.forEach((layer) => {
        const speed = Number(layer.dataset.speed || 0.1);
        const offset = Math.round(scrollY * speed);
        layer.style.transform = `translate3d(0, ${offset}px, 0)`;
      });
      ticking = false;
    });
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
