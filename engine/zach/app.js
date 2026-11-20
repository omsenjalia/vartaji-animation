// ─── Vartaji Engine v2 — Orchestrator ─────────────────────────
// Imports all subsystems, loads data, wires the render loop.
import * as THREE from 'three';
import { makeCharacter } from './lib/characters.js';
import { buildEnvironment } from './lib/environment.js';
import { buildLighting } from './lib/lighting.js';
import { createCameraSystem } from './lib/camera.js';
import { createAnimationSystem } from './lib/animation.js';
import { createCaptionSystem } from './lib/captions.js';

// ─── Renderer ─────────────────────────────────────────────────
const FORMAT = new URLSearchParams(location.search).get('format') || 'reel';
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.4;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('stage').appendChild(renderer.domElement);

// ─── Scene ────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color('#0c182b');
scene.fog = new THREE.FogExp2('#12243d', 0.016);
const camera = new THREE.PerspectiveCamera(36, innerWidth / innerHeight, 0.02, 90);

// ─── Load data ────────────────────────────────────────────────
const specs = await Promise.all(
  ['gokulnathji', 'kalyanbhatt', 'young-vaishnav', 'damodardas']
    .map(id => fetch(`/bible/characters/${id}.json`).then(r => r.json())));

let script = null, capsData = [];
try { script = await (await fetch('/reels/intro-gokulnath/script.json')).json(); } catch (e) { console.error('script', e); }
try { capsData = await (await fetch('/reels/intro-gokulnath/captions.json')).json(); } catch (e) { console.error('caps', e); }

// ─── Build characters ─────────────────────────────────────────
const chars = {};
for (const s of specs) chars[s.id] = makeCharacter(s);

const gokul = chars.gokulnathji;
gokul.position.set(0, 0.52, -1.55);
scene.add(gokul);

const kalyan = chars.kalyanbhatt;
kalyan.position.set(0.78, 0.02, -1.35);
kalyan.rotation.y = -0.45;
scene.add(kalyan);

// Assembly — 13 figures in semicircle, with authentic period colors & varied scale
const ASSEMBLY_PALETTES = [
  { upper: '#efe8d8', turban: '#d9d3c4' }, // natural unbleached cotton
  { upper: '#d89e42', turban: '#efe2c2' }, // ochre / pitambari
  { upper: '#8f432e', turban: '#c8552f' }, // terracotta bhagwa
  { upper: '#425844', turban: '#efe8d8' }, // deep forest sage
  { upper: '#dfd2b5', turban: '#e5d9bf' }, // light khadi
  { upper: '#c76e32', turban: '#e8ddc4' }, // questioner (young-vaishnav)
  { upper: '#634b3c', turban: '#dfd2b5' }, // earthy walnut
  { upper: '#ede5d4', turban: '#d8ceb8' }, // ivory
  { upper: '#c8552f', turban: '#c8552f' }, // damodardas (saffron)
  { upper: '#a38153', turban: '#efe8d8' }, // sandalwood
  { upper: '#3a4e40', turban: '#dcd2bd' }, // cypress
  { upper: '#cc7f3b', turban: '#f0e6d2' }, // warm amber
  { upper: '#e8e0ce', turban: '#dcd2bd' }, // milk white
];

const assembly = [];
for (let i = 0; i < 13; i++) {
  const baseSpec = specs.find(s => s.id === (i === 8 ? 'damodardas' : 'young-vaishnav'));
  const col = ASSEMBLY_PALETTES[i % ASSEMBLY_PALETTES.length];
  const spec = {
    ...baseSpec,
    seed: (baseSpec.seed || baseSpec.id) + '-row-' + i,
    appearance: {
      ...baseSpec.appearance,
      upper: { ...baseSpec.appearance.upper, color: col.upper },
      turban: { ...baseSpec.appearance.turban, color: col.turban },
    },
  };
  const a = makeCharacter(spec);
  const ang = -1.15 + i * (2.3 / 12);
  const R = 1.55 + (i % 3) * 0.18;
  a.position.set(Math.sin(ang) * R, 0, Math.cos(ang) * R + 0.35);
  a.rotation.y = Math.PI + ang * 0.5;
  // Varied scale for organic row — not identical clones
  a.scale.multiplyScalar(0.84 + (i * 7 % 11) * 0.016);
  scene.add(a);
  assembly.push(a);
}
const questioner = assembly[5];
const damodarRow = assembly[8];

// ─── Build environment ────────────────────────────────────────
const env = buildEnvironment(scene);

// ─── Build lighting + post-processing ─────────────────────────
const { composer, updateLighting } = buildLighting(scene, renderer, camera);

// ─── Create subsystems ────────────────────────────────────────
const cam = createCameraSystem(camera, { gokul, kalyan, assembly, questioner, damodarRow, env });
const anim = createAnimationSystem(gokul, kalyan, assembly, questioner, damodarRow, env);
const captions = createCaptionSystem(document.getElementById('caption'), capsData);

// ─── Render at time t ─────────────────────────────────────────
function renderAt(t) {
  const shot = script.shots.find(s => t >= s.start && t < s.end) || script.shots.at(-1);

  cam.update(t, shot);
  anim.update(t, shot);
  updateLighting(t, shot);
  captions.update(t, shot);

  // Use composer for post-processed output (bloom + grade + vignette)
  composer.render();
}

window.renderAt = renderAt;
window.DURATION = script ? script.duration : 88;
window.ready = true;
renderAt(0);
