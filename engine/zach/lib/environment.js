// ─── Vartaji Engine v2 — Environment Builder ──────────────────
// Ground, forest, kadamba tree, campfire, props, atmosphere.
// Returns handles for the animation system.
import * as THREE from 'three';
import { seededRNG, fbm, noise2D } from './math.js';
import { mat, woodMat, leafMat, metalMat, fireMat, stoneMat, groundMat } from './materials.js';

const rng = seededRNG('vartaji-env-2024');

// ─── Ground with noise displacement + vertex colours ───────────
function buildGround(scene) {
  const geo = new THREE.PlaneGeometry(24, 24, 56, 56);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    const dist = Math.sqrt(x * x + z * z);
    const h = fbm(x * 0.25 + 3, z * 0.25 + 7, 0, 3) * 0.12;
    // Flatten the clearing centre
    const flatten = Math.max(0, 1 - dist / 3);
    pos.setY(i, h * (1 - flatten * 0.9));
    // Vertex colours — earthy tones with moss variation
    const n = fbm(x * 0.4 + 10, z * 0.4 + 10, 0, 2);
    const clearing = dist < 2.5 ? 1 : 0;
    colors[i * 3]     = 0.08 + n * 0.04 + clearing * 0.02;
    colors[i * 3 + 1] = 0.09 + n * 0.05 + clearing * 0.01;
    colors[i * 3 + 2] = 0.05 + n * 0.02;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  const ground = new THREE.Mesh(geo, groundMat());
  ground.receiveShadow = true;
  scene.add(ground);
  return ground;
}

// ─── Forest ring & Background Depth ───────────────────────────
function buildForest(scene) {
  const trunkMats = [mat('#4c3a29', 0.82), mat('#3f3224', 0.82), mat('#55402e', 0.82)];
  const leafMats  = [leafMat('#2a6845', 0.76), leafMat('#367c54', 0.76), leafMat('#438c62', 0.78), leafMat('#235839', 0.76)];

  // 1. Framing trees flanking the Great Kadamba tree directly behind the seat
  const framingCoords = [
    [-1.7, -2.6, 4.4], [ 1.7, -2.6, 4.4],
    [-2.8, -3.2, 4.6], [ 2.8, -3.2, 4.6],
    [-4.2, -4.0, 4.8], [ 4.2, -4.0, 4.8],
    [-1.0, -4.8, 5.2], [ 1.0, -4.8, 5.2],
    [-3.0, -5.6, 5.0], [ 3.0, -5.6, 5.0],
  ];
  for (let k = 0; k < framingCoords.length; k++) {
    const [fx, fz, fh] = framingCoords[k];
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(0.14, 0.22, fh, 9),
      trunkMats[k % 3]
    );
    trunk.position.set(fx, fh / 2, fz); trunk.castShadow = true; scene.add(trunk);
    for (let c = 0; c < 4; c++) {
      const cr = 0.95 + rng() * 0.35;
      const can = new THREE.Mesh(new THREE.IcosahedronGeometry(cr, 1), leafMats[(k + c) % leafMats.length]);
      can.position.set(fx + (c - 1.5) * 0.42, fh * 0.55 + c * 0.45, fz + (rng() - 0.5) * 0.4);
      can.scale.set(1.25, 0.80, 1.20);
      scene.add(can);
    }
  }

  // 2. Surrounding deep forest perimeter ring
  for (let i = 0; i < 34; i++) {
    const a = i * 2.399, r = 5.0 + (i % 7) * 0.85;
    const x = Math.cos(a) * r, z = Math.sin(a) * r - 1.2;
    const h = 3.8 + (i % 5) * 0.65;

    // Trunk with slight bend
    const tGeo = new THREE.CylinderGeometry(0.11 + rng() * 0.05, 0.17 + rng() * 0.06, h, 8);
    const tp = tGeo.attributes.position;
    for (let j = 0; j < tp.count; j++) {
      const ny = (tp.getY(j) + h / 2) / h;
      tp.setX(j, tp.getX(j) + ny * ny * (rng() - 0.5) * 0.18);
    }
    tGeo.computeVertexNormals();
    const trunk = new THREE.Mesh(tGeo, trunkMats[i % 3]);
    trunk.position.set(x, h / 2, z); trunk.castShadow = true;
    scene.add(trunk);

    // Canopy clusters — icosahedrons for stylised faceted look
    const nCan = 3 + (i % 3);
    for (let k = 0; k < nCan; k++) {
      const cr = 0.90 + rng() * 0.45;
      const canopy = new THREE.Mesh(
        new THREE.IcosahedronGeometry(cr, 1), leafMats[(i + k) % leafMats.length]);
      canopy.position.set(
        x + (rng() - 0.5) * cr * 0.7,
        h * 0.65 + k * 0.4 + rng() * 0.3,
        z + (rng() - 0.5) * cr * 0.7);
      canopy.scale.set(1.25, 0.75, 1.20);
      scene.add(canopy);
    }
  }
}

// ─── Great kadamba tree ────────────────────────────────────────
function buildKadamba(scene) {
  const tree = new THREE.Group(); tree.position.set(0, 0, -2.5);
  const trunkH = 4.4;

  // Trunk with root flares
  const tGeo = new THREE.CylinderGeometry(0.28, 0.50, trunkH, 14);
  const tp = tGeo.attributes.position;
  for (let i = 0; i < tp.count; i++) {
    const y = tp.getY(i) + trunkH / 2;
    if (y < 0.9) {
      const rt = 1 - y / 0.9;
      const ang = Math.atan2(tp.getZ(i), tp.getX(i));
      const bulge = 1 + rt * 0.4 * (0.5 + 0.5 * Math.sin(ang * 4.5 + 2));
      tp.setX(i, tp.getX(i) * bulge);
      tp.setZ(i, tp.getZ(i) * bulge);
    }
  }
  tGeo.computeVertexNormals();
  const trunk = new THREE.Mesh(tGeo, mat('#523926', 0.82));
  trunk.position.y = trunkH / 2; trunk.castShadow = true;
  tree.add(trunk);

  // Major branches spreading gracefully behind and above the seat
  for (let i = 0; i < 6; i++) {
    const ang = (i / 6) * Math.PI * 2 + 0.2;
    const pts = [
      new THREE.Vector3(0, trunkH * 0.52, 0),
      new THREE.Vector3(Math.cos(ang) * 0.9, trunkH * 0.64 + (i % 2) * 0.25, Math.sin(ang) * 0.8),
      new THREE.Vector3(Math.cos(ang) * 1.8, trunkH * 0.62 + (i % 3) * 0.30, Math.sin(ang) * 1.6),
    ];
    const curve = new THREE.CatmullRomCurve3(pts);
    const branch = new THREE.TubeGeometry(curve, 10, 0.07 + (i % 2) * 0.02, 8, false);
    const m = new THREE.Mesh(branch, mat('#442e1d', 0.85));
    m.castShadow = true; tree.add(m);
  }

  // Canopy mass — rich moonlit Kadamba foliage filling the upper background
  const lMats = [leafMat('#2b6845', 0.76), leafMat('#387e56', 0.76), leafMat('#489467', 0.78)];
  for (let i = 0; i < 16; i++) {
    const ang = (i / 16) * Math.PI * 2;
    const cr = 1.10 + (i % 3) * 0.25;
    const canopy = new THREE.Mesh(new THREE.IcosahedronGeometry(cr, 1), lMats[i % lMats.length]);
    canopy.position.set(
      Math.cos(ang) * (1.3 + (i % 2) * 0.4),
      trunkH * 0.65 + Math.sin(i * 0.9) * 0.5 + 0.5,
      Math.sin(ang) * 1.1);
    canopy.scale.set(1.3, 0.75, 1.25);
    tree.add(canopy);
  }
  scene.add(tree);
}

// ─── Bench under the kadamba ───────────────────────────────────
function buildBench(scene) {
  const wd = woodMat();
  scene.add(new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.16, 0.85), wd).translateY(0.42).translateZ(-1.55));
  for (const x of [-0.5, 0.5])
    for (const z of [-1.85, -1.25])
      scene.add(new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.42, 0.09), wd).translateY(0.21).translateX(x).translateZ(z));
}

// ─── Campfire ──────────────────────────────────────────────────
function buildFire(scene) {
  const fire = new THREE.Group(); fire.position.set(0, 0, 0.2);

  // Stone ring
  for (let i = 0; i < 10; i++) {
    const ang = (i / 10) * Math.PI * 2;
    const stone = new THREE.Mesh(
      new THREE.DodecahedronGeometry(0.065 + rng() * 0.025, 0), stoneMat());
    stone.position.set(Math.cos(ang) * 0.32, 0.025, Math.sin(ang) * 0.32);
    stone.rotation.set(rng(), rng(), rng());
    stone.scale.set(1, 0.55, 1.15);
    fire.add(stone);
  }

  // Log pile
  const logM = mat('#2a1508', 0.92);
  for (let i = 0; i < 5; i++) {
    const ang = (i / 5) * Math.PI;
    fire.add(new THREE.Mesh(
      new THREE.CylinderGeometry(0.035 + rng() * 0.015, 0.045 + rng() * 0.015, 0.55 + rng() * 0.2, 6),
      logM
    ).translateY(0.055).rotateX(Math.PI / 2).rotateZ(ang + rng() * 0.3).translateX(rng() * 0.06));
  }

  // Embers bed
  const embers = new THREE.Mesh(
    new THREE.SphereGeometry(0.18, 16, 8),
    fireMat('#a03008', 0.65));
  embers.position.y = 0.035; embers.scale.set(1, 0.2, 1);
  fire.add(embers);

  // Flame — layered organic fire tongues
  const flame1 = new THREE.Mesh(
    new THREE.ConeGeometry(0.12, 0.44, 18, 1, true), fireMat('#ff8524', 0.88));
  flame1.position.y = 0.26; fire.add(flame1);

  const flame2 = new THREE.Mesh(
    new THREE.ConeGeometry(0.065, 0.34, 16, 1, true), fireMat('#ffbe44', 0.92));
  flame2.position.y = 0.22; fire.add(flame2);

  const flame3 = new THREE.Mesh(
    new THREE.ConeGeometry(0.035, 0.22, 14, 1, true), fireMat('#fff5ba', 0.96));
  flame3.position.y = 0.18; fire.add(flame3);

  // Fire light
  const fireLight = new THREE.PointLight('#ff8a3c', 2.8, 12, 1.4);
  fireLight.position.set(0, 0.55, 0.2);
  fireLight.castShadow = true; fireLight.shadow.mapSize.set(1024, 1024);
  scene.add(fireLight);

  scene.add(fire);

  // Floor glow + moving shadow for the quiet midnight beat (s04)
  const floorGlow = new THREE.PointLight('#ffb163', 0, 5, 1.3);
  floorGlow.position.set(0, 0.35, 0.1); scene.add(floorGlow);
  const floorShadow = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({ color: '#000', transparent: true, opacity: 0, depthWrite: false }));
  floorShadow.rotation.x = -Math.PI / 2; floorShadow.position.set(0, 0.012, 0.6);
  scene.add(floorShadow);

  // Sparks
  const sparks = [];
  for (let i = 0; i < 30; i++) {
    const s = new THREE.Mesh(
      new THREE.SphereGeometry(0.009, 3, 3),
      new THREE.MeshBasicMaterial({ color: '#ffb45a', transparent: true }));
    s.userData = { a: i * 2.399, r: 0.08 + (i % 6) * 0.06, base: i * 0.37, speed: 0.25 + rng() * 0.3 };
    scene.add(s); sparks.push(s);
  }

  return { fire, flame1, flame2, flame3, embers, fireLight, floorGlow, floorShadow, sparks };
}

// ─── Props — brass vessel, diya, manuscript ────────────────────
function buildProps(scene) {
  // Brass vessel
  const vessel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.17, 0.12, 0.20, 12), metalMat());
  vessel.position.set(1.30, 0.11, 1.10); vessel.castShadow = true;
  scene.add(vessel);

  // Diya floating in the vessel
  const diya = new THREE.Mesh(
    new THREE.SphereGeometry(0.09, 8, 5),
    fireMat('#ffb347', 0.9));
  diya.position.set(1.30, 0.24, 1.10); diya.scale.set(1.1, 0.3, 1.1);
  scene.add(diya);
  const diyaFlame = new THREE.Mesh(
    new THREE.ConeGeometry(0.02, 0.08, 5, 1, true),
    fireMat('#fff0b0'));
  diyaFlame.position.set(1.30, 0.32, 1.10);
  scene.add(diyaFlame);

  // Manuscript
  const book = new THREE.Group(); book.position.set(-0.60, 0.32, 0.50);
  book.add(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.04, 0.24), mat('#e2d3ac')));
  book.add(new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.028, 0.26), mat('#5a2e1c')).translateY(-0.035));
  // Resting hand
  const hand = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 8), mat('#a9774f'));
  hand.position.set(-0.04, 0.055, 0);
  hand.scale.set(1.15, 0.45, 0.9);
  book.add(hand);
  for (let i = 0; i < 4; i++)
    book.add(new THREE.Mesh(
      new THREE.CylinderGeometry(0.009, 0.009, 0.08, 4), mat('#a9774f'))
      .translateY(0.045).translateX(0.02 + i * 0.03).rotateX(Math.PI / 2));
  scene.add(book);

  return { vessel, diya, diyaFlame, book };
}

// ─── Grass (instanced) ────────────────────────────────────────
function buildGrass(scene) {
  const bladeGeo = new THREE.PlaneGeometry(0.012, 0.09, 1, 3);
  // Bend the blade
  const bp = bladeGeo.attributes.position;
  for (let i = 0; i < bp.count; i++) {
    const y = bp.getY(i);
    if (y > 0) bp.setZ(i, y * y * 0.5);
  }
  bladeGeo.computeVertexNormals();
  const grassMat = new THREE.MeshStandardMaterial({
    color: '#2a4019', roughness: 0.92, side: THREE.DoubleSide });
  const grass = new THREE.InstancedMesh(bladeGeo, grassMat, 450);
  const dummy = new THREE.Object3D();

  for (let i = 0; i < 450; i++) {
    const ang = rng() * Math.PI * 2;
    const r = 1.8 + rng() * 5.0;
    dummy.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
    dummy.rotation.set(0, rng() * Math.PI, 0);
    dummy.scale.set(0.8 + rng() * 0.5, 0.5 + rng() * 1.0, 1);
    dummy.updateMatrix();
    grass.setMatrixAt(i, dummy.matrix);
  }
  grass.instanceMatrix.needsUpdate = true;
  scene.add(grass);
}

// ─── Atmospheric — sky dome, moon, stars, mist, fireflies ────
function buildAtmosphere(scene) {
  // 1. Luminous Night Sky Dome (Inverted hemisphere with vertical twilight gradient)
  const skyRadius = 48;
  const skyGeo = new THREE.SphereGeometry(skyRadius, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.5);
  const skyColors = new Float32Array(skyGeo.attributes.position.count * 3);
  const skyPos = skyGeo.attributes.position;
  // Deep midnight navy at zenith (#0c182b: 0.047, 0.094, 0.168) to moonlit cobalt horizon (#1e3e64: 0.117, 0.243, 0.392)
  for (let i = 0; i < skyPos.count; i++) {
    const yNorm = Math.max(0, Math.min(1, skyPos.getY(i) / skyRadius));
    const t = 1 - yNorm; // 1 at horizon, 0 at zenith
    skyColors[i * 3 + 0] = 0.047 + t * 0.095;
    skyColors[i * 3 + 1] = 0.094 + t * 0.180;
    skyColors[i * 3 + 2] = 0.168 + t * 0.260;
  }
  skyGeo.setAttribute('color', new THREE.BufferAttribute(skyColors, 3));
  const skyMat = new THREE.MeshBasicMaterial({
    vertexColors: true,
    side: THREE.BackSide,
    depthWrite: false,
  });
  const skyDome = new THREE.Mesh(skyGeo, skyMat);
  scene.add(skyDome);

  // 2. Radiant Luminous Moon
  const moonGrp = new THREE.Group();
  moonGrp.position.set(-8, 15, -22);
  moonGrp.lookAt(0, 0, 0);

  // Moon inner disc
  const moonDisc = new THREE.Mesh(
    new THREE.CircleGeometry(1.65, 32),
    new THREE.MeshBasicMaterial({ color: '#f2f7ff', depthWrite: false })
  );
  moonGrp.add(moonDisc);

  // Moon soft glowing halos
  const halo1 = new THREE.Mesh(
    new THREE.CircleGeometry(3.2, 24),
    new THREE.MeshBasicMaterial({ color: '#a6c8f5', transparent: true, opacity: 0.32, depthWrite: false })
  );
  const halo2 = new THREE.Mesh(
    new THREE.CircleGeometry(6.5, 24),
    new THREE.MeshBasicMaterial({ color: '#5684be', transparent: true, opacity: 0.14, depthWrite: false })
  );
  moonGrp.add(halo1, halo2);
  scene.add(moonGrp);

  // 3. Sparkling Stars (110 varied points of celestial light)
  for (let i = 0; i < 110; i++) {
    const a1 = rng() * Math.PI * 2;
    const a2 = 0.12 + rng() * Math.PI * 0.38;
    const r = 42 + rng() * 4;
    const starR = 0.06 + rng() * 0.08;
    const starCol = i % 4 === 0 ? '#ffe6b8' : '#eaf2ff';
    const star = new THREE.Mesh(
      new THREE.SphereGeometry(starR, 4, 4),
      new THREE.MeshBasicMaterial({ color: starCol, transparent: true, opacity: 0.45 + rng() * 0.50, depthWrite: false })
    );
    star.position.set(
      Math.cos(a1) * Math.cos(a2) * r,
      Math.sin(a2) * r + 2,
      Math.sin(a1) * Math.cos(a2) * r
    );
    scene.add(star);
  }

  // 4. Soft Moonlit Ground Mist (Translucent layers along forest floor)
  const mistMat = new THREE.MeshBasicMaterial({
    color: '#6e98c6',
    transparent: true,
    opacity: 0.08,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  for (let m = 0; m < 8; m++) {
    const mist = new THREE.Mesh(new THREE.CircleGeometry(4.2 + (m % 3) * 1.5, 16), mistMat);
    mist.rotation.x = -Math.PI * 0.5;
    const ang = m * (Math.PI * 2 / 8);
    mist.position.set(Math.cos(ang) * 4.5, 0.12 + (m % 3) * 0.05, Math.sin(ang) * 4.5 - 1.5);
    scene.add(mist);
  }

  // 5. Fireflies
  const fireflies = [];
  for (let i = 0; i < 22; i++) {
    const fly = new THREE.Mesh(
      new THREE.SphereGeometry(0.010, 4, 4),
      new THREE.MeshBasicMaterial({ color: '#caff78', transparent: true, opacity: 0 }));
    fly.userData = {
      base: [rng() * 10 - 5, 0.4 + rng() * 2.8, rng() * 8 - 4],
      phase: rng() * Math.PI * 2,
      speed: 0.25 + rng() * 0.45,
      brightness: 0.4 + rng() * 0.6,
    };
    scene.add(fly); fireflies.push(fly);
  }

  return { fireflies };
}

// ─── Main builder ──────────────────────────────────────────────
export function buildEnvironment(scene) {
  const ground = buildGround(scene);
  buildForest(scene);
  buildKadamba(scene);
  buildBench(scene);
  const fireData = buildFire(scene);
  const props = buildProps(scene);
  buildGrass(scene);
  const atmo = buildAtmosphere(scene);

  return { ground, ...fireData, ...props, ...atmo };
}
