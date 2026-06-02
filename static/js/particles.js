(() => {
  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const mount = document.getElementById("bg3d");
  if (!mount || typeof window.THREE === "undefined" || prefersReducedMotion) return;

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
      colors[i3 + 1] = 0.6;
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
