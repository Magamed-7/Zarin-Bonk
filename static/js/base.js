(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const state = {
    tiltEnabled: !prefersReducedMotion,
  };

  // Flash message close
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

  // 3D tilt cards
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

  const bindTilt = () => {
    cards.forEach((el) => {
      el.addEventListener("mousemove", (ev) => {
        if (!state.tiltEnabled) return;
        applyTilt(el, ev);
      });
      el.addEventListener("mouseleave", () => resetTilt(el));
    });
  };

  bindTilt();

  const tiltToggle = document.getElementById("ui-tilt-toggle");
  if (tiltToggle) {
    tiltToggle.addEventListener("click", () => {
      state.tiltEnabled = !state.tiltEnabled;
      tiltToggle.classList.toggle("is-on", state.tiltEnabled);
      cards.forEach((c) => resetTilt(c));
    });
  }

  // Chart.js mini chart
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

  // Three.js particle background
  const mount = document.getElementById("bg3d");
  if (!mount || !window.THREE || prefersReducedMotion) return;

  const THREE = window.THREE;
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  mount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    55,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.z = 68;

  const particleCount = 900;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount; i += 1) {
    const i3 = i * 3;
    positions[i3 + 0] = (Math.random() - 0.5) * 170;
    positions[i3 + 1] = (Math.random() - 0.5) * 110;
    positions[i3 + 2] = (Math.random() - 0.5) * 140;

    const gold = Math.random() < 0.38;
    if (gold) {
      colors[i3 + 0] = 1.0;
      colors[i3 + 1] = 0.86;
      colors[i3 + 2] = 0.25;
    } else {
      colors[i3 + 0] = 0.42;
      colors[i3 + 1] = 0.60;
      colors[i3 + 2] = 1.0;
    }
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: 0.85,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, material);
  scene.add(points);

  let mouseX = 0;
  let mouseY = 0;
  window.addEventListener(
    "mousemove",
    (e) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    },
    { passive: true }
  );

  const onResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  };
  window.addEventListener("resize", onResize, { passive: true });

  const animate = () => {
    points.rotation.y += 0.0009;
    points.rotation.x += 0.0003;
    points.position.x = mouseX * 1.8;
    points.position.y = -mouseY * 1.2;
    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
  };

  animate();
})();
