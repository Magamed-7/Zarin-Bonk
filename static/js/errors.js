(() => {
  document.querySelectorAll(".reveal").forEach((el) => {
    el.classList.add("in-view");
  });

  const mount = document.getElementById("error3d");
  if (!mount || !window.THREE) return;

  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion) return;

  const THREE = window.THREE;
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  mount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.z = 6;

  const gold = new THREE.Color(0xffd700);
  const blue = new THREE.Color(0x5a8cff);

  const torus = new THREE.Mesh(
    new THREE.TorusGeometry(1.4, 0.22, 16, 64),
    new THREE.MeshStandardMaterial({
      color: gold,
      emissive: gold,
      emissiveIntensity: 0.25,
      metalness: 0.7,
      roughness: 0.25,
      transparent: true,
      opacity: 0.9,
    })
  );
  scene.add(torus);

  const inner = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.75, 0),
    new THREE.MeshStandardMaterial({
      color: blue,
      emissive: blue,
      emissiveIntensity: 0.15,
      metalness: 0.5,
      roughness: 0.35,
      wireframe: true,
    })
  );
  scene.add(inner);

  const light1 = new THREE.PointLight(0xffd700, 2.2, 20);
  light1.position.set(3, 2, 4);
  scene.add(light1);

  const light2 = new THREE.PointLight(0x5a8cff, 1.4, 20);
  light2.position.set(-3, -2, 3);
  scene.add(light2);

  scene.add(new THREE.AmbientLight(0xffffff, 0.35));

  const resize = () => {
    const w = mount.clientWidth;
    const h = mount.clientHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };

  resize();
  window.addEventListener("resize", resize, { passive: true });

  const animate = () => {
    torus.rotation.x += 0.008;
    torus.rotation.y += 0.012;
    inner.rotation.x -= 0.01;
    inner.rotation.z += 0.014;
    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
  };

  animate();
})();
