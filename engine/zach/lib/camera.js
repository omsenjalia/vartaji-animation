// ─── Vartaji Engine v2 — Camera System ────────────────────────
import * as THREE from 'three';
import { smooth, range, easeInOut, cameraShake, lerp } from './math.js';

// Shot configs for intro-gokulnath scene layout.
// p = position, l = lookAt, f = FOV, plus per-shot modifiers.
const SHOTS = {
  s01: { p: [0, 8.0, 6.5],    l: [0, 0.3, 0],       f: 50, descend: 6.6 },
  s02: { p: [0, 2.0, 5.4],    l: [0, 0.85, -0.4],    f: 50, tilt: 0.5 },
  s03: { p: [-1.10, 1.48, 0.45], l: [0, 1.52, -1.55], f: 38, push: 0.005 },
  s04: { p: [0.7, 0.62, 1.55], l: [0, 0.27, 0.3],    f: 40, push: 0.004 },
  s05: { p: [0.2, 1.25, 1.4],  l: [-1.05, 0.95, 1.25],f: 46, push: 0.006 },
  s06: { p: [0, 1.25, 2.4],    l: [0, 0.62, -1.4],   f: 38, push: 0.006 },
  s07: { p: [0.25, 1.5, 1.2],  l: [0, 1.55, -1.5],   f: 38, push: 0.014 },
  s08: { p: [-2.2, 2.3, 2.9],  l: [0, 0.8, 0.2],     f: 46, drift: 2.0 },
  s09: { p: [2.4, 1.0, 2.4],   l: [1.30, 0.12, 1.10],f: 38, push: 0.004 },
  s10: { p: [-2.1, 1.45, 3.0], l: [-0.55, 0.55, 0.35],f: 44, push: 0.004 },
  s11: { p: [0, 2.3, 5.2],     l: [0, 1.15, -0.6],    f: 48, push: 0.003 },
};

// Smooth camera position blending between shots
let prevShot = null, blendStart = 0;
const BLEND_DUR = 0.5;
let prevPos = null, prevLook = null, prevFov = 36;

export function createCameraSystem(camera, refs) {
  const { assembly, damodarRow } = refs;
  const tmpVec = new THREE.Vector3();

  return {
    update(t, shot) {
      const cfg = SHOTS[shot.id] || SHOTS.s02;
      const lt = t - shot.start;
      const dur = shot.end - shot.start;
      const k = smooth(range(t, shot.start, shot.end));

      // ─── Base camera position ──────────────────────
      let px = cfg.p[0], py = cfg.p[1], pz = cfg.p[2];
      let lx = cfg.l[0], ly = cfg.l[1], lz = cfg.l[2];

      // Shot-specific modifiers with eased interpolation
      if (cfg.descend) {
        const d = easeInOut(range(lt, 0, cfg.descend));
        py = cfg.p[1] - 5.4 * d;
        pz = cfg.p[2] - 3.0 * d;
        ly = 0.3 + 0.5 * d;
      }
      if (cfg.tilt) ly += cfg.tilt * smooth(k - 0.5);
      if (cfg.push) {
        const pushT = easeInOut(range(lt, 0, dur));
        px += cfg.push * pushT * dur;
        pz -= cfg.push * pushT * dur * 2;
      }
      if (cfg.drift) px += cfg.drift * smooth(k - 0.5);

      // ─── Shot-specific overrides ───────────────────
      if (shot.id === 's08') {
        // Face-by-face drift — smooth blend between assembly members
        const faceIdx = lt < 4 ? 2 : lt < 8 ? 5 : 8;
        const nextIdx = lt < 4 ? 2 : lt < 8 ? 5 : 8;
        const faceT = lt < 4 ? lt / 4 : lt < 8 ? (lt - 4) / 4 : (lt - 8) / 4;
        if (assembly[faceIdx]) {
          assembly[faceIdx].getWorldPosition(tmpVec); tmpVec.y += 1.0;
          px = lerp(tmpVec.x * 0.35, tmpVec.x * 0.35, smooth(faceT));
          py = tmpVec.y + 0.25;
          pz = -1.05;
          lx = tmpVec.x; ly = tmpVec.y; lz = tmpVec.z;
          camera.fov = 42;
        }
      }

      if (shot.id === 's09' && t >= 72) {
        if (damodarRow) {
          damodarRow.getWorldPosition(tmpVec); tmpVec.y += 1.0;
          px = tmpVec.x + 1.2; py = tmpVec.y + 0.3; pz = tmpVec.z + 1.7;
          lx = tmpVec.x; ly = tmpVec.y; lz = tmpVec.z;
          camera.fov = 42;
        }
      }

      // ─── Handheld micro-motion (Perlin noise) ──────
      const shake = cameraShake(t);
      px += shake.x; py += shake.y; pz += shake.z;

      // ─── Apply ─────────────────────────────────────
      camera.position.set(px, py, pz);
      camera.lookAt(lx, ly, lz);
      if (!['s08', 's09'].includes(shot.id) || (shot.id === 's09' && t < 72)) {
        camera.fov = cfg.f;
      }
      camera.updateProjectionMatrix();
    },
  };
}
