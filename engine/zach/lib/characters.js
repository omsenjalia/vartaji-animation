// ─── Vartaji Engine v2 — Character Builder (Zach D. Style) ────
// High-fidelity procedural 3D stylized cartoon human figures.
import * as THREE from 'three';
import { seededRNG } from './math.js';
import { skinMat, clothMat, hairMat, mat } from './materials.js';

// ─── Geometry Primitives with Proper Subdivision ───────────────
const sph = (r, m, p=[0,0,0], s=[1,1,1], seg=24) => {
  const o = new THREE.Mesh(new THREE.SphereGeometry(r, seg, Math.round(seg * 0.75)), m);
  o.position.set(...p); o.scale.set(...s); o.castShadow = true; return o;
};

const cap = (r, l, m, p=[0,0,0], rot=[0,0,0], seg=18) => {
  const o = new THREE.Mesh(new THREE.CapsuleGeometry(r, l, 8, seg), m);
  o.position.set(...p); o.rotation.set(...rot); o.castShadow = true; return o;
};

const cyl = (rt, rb, h, m, p=[0,0,0], r=[0,0,0], seg=20) => {
  const o = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), m);
  o.position.set(...p); o.rotation.set(...r); o.castShadow = true; return o;
};

const box = (w, h, d, m, p=[0,0,0], rot=[0,0,0]) => {
  const o = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  o.position.set(...p); o.rotation.set(...rot); o.castShadow = true; return o;
};

// ─── Sculpted Head Geometry ────────────────────────────────────
function makeHeadGeo() {
  const geo = new THREE.SphereGeometry(0.14, 28, 22);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    let x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);

    // Jaw taper & chin definition
    if (y < -0.01) {
      const t = Math.min(1, (-y - 0.01) / 0.13);
      x *= 1 - t * 0.26;
      if (z > 0) z += t * 0.012; // defined chin protrusion
      else z *= 1 - t * 0.22;
    }

    // Forehead curve
    if (y > 0.05 && z > 0.03) {
      z += 0.006;
    }

    // Gentle eye socket depression
    if (y > 0.005 && y < 0.055 && Math.abs(x) > 0.025 && Math.abs(x) < 0.075 && z > 0.08) {
      z -= 0.010;
    }

    pos.setX(i, x); pos.setY(i, y); pos.setZ(i, z);
  }
  geo.computeVertexNormals();
  return geo;
}

// ─── Authentic Vraj Pagdi (Turban) ─────────────────────────────
function makeTurban(a, rng) {
  const g = new THREE.Group();
  const c = clothMat(a.turban.color, 0.9);
  const accent = clothMat(a.turban.color === '#efe2c2' ? '#d8b97b' : '#b8442a', 0.85);

  // 1. Skull cap fitting snugly over the upper head
  const baseDome = new THREE.Mesh(
    new THREE.SphereGeometry(0.148, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.52),
    c
  );
  baseDome.position.set(0, 0.02, -0.01);
  baseDome.castShadow = true;
  g.add(baseDome);

  // 2. Sculpted wrapping rolls around brow and temples (angled, not flat rings)
  const wrapLevels = a.turban.layers || 3;
  for (let lvl = 0; lvl < wrapLevels; lvl++) {
    const yOff = 0.035 + lvl * 0.038;
    const rMajor = 0.146 + lvl * 0.008;
    const rTube = 0.026 + (wrapLevels - lvl) * 0.004;

    // Elliptical wrap with slight diagonal tilt characteristic of Braj headwear
    const pts = [];
    const numPts = 32;
    const tilt = 0.06 * (lvl % 2 === 0 ? 1 : -0.7);
    for (let i = 0; i <= numPts; i++) {
      const ang = (i / numPts) * Math.PI * 2;
      const x = Math.cos(ang) * (rMajor * 1.05);
      const z = Math.sin(ang) * (rMajor * 0.98) - 0.01;
      const y = yOff + Math.sin(ang + Math.PI * 0.25) * tilt;
      pts.push(new THREE.Vector3(x, y, z));
    }
    const curve = new THREE.CatmullRomCurve3(pts, true);
    const wrapGeo = new THREE.TubeGeometry(curve, 32, rTube, 8, true);
    const wrapMesh = new THREE.Mesh(wrapGeo, lvl === 1 ? accent : c);
    wrapMesh.castShadow = true;
    g.add(wrapMesh);
  }

  // 3. Top crown crest (turra / kalgi mount)
  const topCrown = new THREE.Mesh(
    new THREE.SphereGeometry(0.11, 20, 10),
    c
  );
  topCrown.position.set(0, 0.145, -0.02);
  topCrown.scale.set(1.1, 0.5, 0.95);
  topCrown.castShadow = true;
  g.add(topCrown);

  // 4. Vraj style side/back tail fold
  if (a.turban.style === 'vraj') {
    const tailPts = [
      new THREE.Vector3(0.12, 0.09, -0.07),
      new THREE.Vector3(0.15, 0.02, -0.11),
      new THREE.Vector3(0.14, -0.08, -0.13),
    ];
    const tailCurve = new THREE.CatmullRomCurve3(tailPts);
    const tailMesh = new THREE.Mesh(new THREE.TubeGeometry(tailCurve, 12, 0.022, 6, false), c);
    tailMesh.castShadow = true;
    g.add(tailMesh);
  }

  return g;
}

// ─── Expressive Stylized Face ──────────────────────────────────
function makeFace(a, skin, rng) {
  const face = new THREE.Group();
  const isGrey = a.face.beard && a.face.beard.includes('grey');
  const hairColor = isGrey ? '#aba396' : '#1e140d';
  const browM = hairMat(hairColor);
  const beardM = hairMat(isGrey ? '#b4aca0' : '#22160d');
  const darkPupil = mat('#080503', 0.2);
  const eyeHighlight = mat('#ffffff', 0.05);
  const eyes = [];

  // Stylized expressive cartoon eyes with radiant catchlight
  const eyeR = 0.020;
  for (const side of [-1, 1]) {
    const x = side * 0.048;
    const eyeGrp = new THREE.Group();
    eyeGrp.position.set(x, 0.028, 0.126);

    // Sclera (bright, clean warm ivory)
    const sclera = sph(eyeR, mat('#fffcf5', 0.3), [0, 0, 0], [1.12, 0.90, 0.45], 16);
    eyeGrp.add(sclera);

    // Iris (warm deep amber / hazel / brown)
    const iris = sph(eyeR * 0.65, mat(a.face.eyeColor || '#2c1b10', 0.25), [0, 0, eyeR * 0.28], [1, 1, 0.4], 14);
    eyeGrp.add(iris);

    // Pupil (crisp dark)
    const pupil = sph(eyeR * 0.36, darkPupil, [0, 0, eyeR * 0.37], [1, 1, 0.3], 12);
    eyeGrp.add(pupil);

    // Catchlight highlight (gleam of intelligence & devotion)
    const glint = sph(eyeR * 0.18, eyeHighlight, [side * 0.003 + 0.003, 0.004, eyeR * 0.40], [1, 1, 0.3], 8);
    eyeGrp.add(glint);

    // Subtle upper eyelid fold (dignified calm curve)
    const lid = box(eyeR * 2.2, eyeR * 0.45, eyeR * 1.2, skin, [0, eyeR * 0.72, eyeR * 0.25]);
    eyeGrp.add(lid);

    face.add(eyeGrp);
    eyes.push(eyeGrp);

    // Eyebrow — expressive arched curve
    const brow = box(0.040, 0.007, 0.006, browM, [x, 0.056, 0.130]);
    brow.rotation.z = side < 0 ? 0.09 : -0.09;
    face.add(brow);
  }

  // Sculpted Nose
  const noseBase = new THREE.Mesh(
    new THREE.ConeGeometry(0.016, 0.048, 12),
    skin
  );
  noseBase.position.set(0, 0.006, 0.140);
  noseBase.rotation.x = Math.PI * 0.45;
  face.add(noseBase);
  // Nose tip ball
  const noseTip = sph(a.face.nose === 'broad' ? 0.015 : 0.012, skin, [0, -0.012, 0.146], [1.1, 0.85, 0.85]);
  face.add(noseTip);

  // Beard (sculpted jawline wrap)
  if (a.face.beard && a.face.beard !== 'none') {
    const isFull = a.face.beard.includes('full');
    const beardLength = a.face.beard === 'short-full' ? 0.09 : 0.13;

    // Jaw hugging beard volume
    const bGeo = new THREE.SphereGeometry(0.12, 20, 14);
    const bp = bGeo.attributes.position;
    for (let i = 0; i < bp.count; i++) {
      let x = bp.getX(i), y = bp.getY(i), z = bp.getZ(i);
      if (y < 0) {
        x *= 1 - Math.abs(y) * 0.35;
        z = z > 0 ? z * 1.05 : z * 0.4;
      }
      bp.setX(i, x); bp.setY(i, y); bp.setZ(i, z);
    }
    bGeo.computeVertexNormals();

    const beardMesh = new THREE.Mesh(bGeo, beardM);
    beardMesh.position.set(0, -0.068, 0.036);
    beardMesh.scale.set(0.92, isFull ? beardLength / 0.11 : 0.6, 0.65);
    beardMesh.castShadow = true;
    face.add(beardMesh);
  }

  // Mustache & Serene Warm Smile
  if (a.face.mustache) {
    for (const side of [-1, 1]) {
      // Horizontal swept mustache with outer tips curved gracefully upward
      const mst = new THREE.Mesh(
        new THREE.CylinderGeometry(0.004, 0.006, 0.034, 10),
        browM
      );
      mst.position.set(side * 0.021, -0.022, 0.142);
      mst.rotation.set(0, 0, Math.PI * 0.5 + side * 0.14);
      mst.castShadow = true;
      face.add(mst);
    }
    // Gentle serene warm mouth line
    const mouth = box(0.026, 0.004, 0.006, mat('#6e2a1e'), [0, -0.032, 0.140]);
    face.add(mouth);
  }

  // Sacred Tilak (Pushtimarg Urdhva Pundra — positioned clearly on brow between eyes)
  const tilakMat = mat(a.tilak.color || '#d43820', 0.35);
  const tilakGrp = new THREE.Group();
  tilakGrp.position.set(0, 0.042, 0.140);

  // Left prong, right prong, and base connection
  const prongL = box(0.0036, 0.034, 0.004, tilakMat, [-0.008, 0.004, 0]);
  const prongR = box(0.0036, 0.034, 0.004, tilakMat, [ 0.008, 0.004, 0]);
  const prongB = box(0.018, 0.0040, 0.004, tilakMat, [0, -0.012, 0]);
  // Golden Chandan inner line & sacred red kumkum bindu
  const chandanCenter = box(0.0024, 0.026, 0.004, mat('#f4dfa4', 0.4), [0, 0.002, 0.001]);
  const tilakDot = sph(0.0036, mat('#e02814', 0.3), [0, -0.003, 0.003]);
  tilakGrp.add(prongL, prongR, prongB, chandanCenter, tilakDot);
  face.add(tilakGrp);

  return { face, eyes };
}

// ─── Authentic Continuous Seated Body & Robe (Padmasana) ───────
function makeBody(a, clothM, dhotiM) {
  const g = new THREE.Group();

  // 1. Asana Gaddi (Round sacred meditation cushion resting on the platform)
  const gaddiColor = '#efe6d6';
  const gaddiM = clothMat(gaddiColor, 0.9);
  const gaddiBorder = clothMat(a.shawl ? a.shawl.color : '#a83c26', 0.85);
  const gaddi = cyl(0.42, 0.44, 0.08, gaddiM, [0, 0.04, 0.05], [0, 0, 0], 28);
  const border = cyl(0.435, 0.445, 0.025, gaddiBorder, [0, 0.025, 0.05], [0, 0, 0], 28);
  g.add(gaddi, border);

  // 2. Core Upper Torso (Chest & Waist — erect meditative posture)
  const chest = cap(0.145, 0.28, clothM, [0, 0.62, 0], [0, 0, 0], 20);
  g.add(chest);

  // 3. Collar & Neckline
  const collar = cyl(0.085, 0.11, 0.045, clothM, [0, 0.77, 0], [0, 0, 0], 20);
  g.add(collar);

  // 4. Waist Sash (Kamarbandh)
  const sashColor = a.shawl ? a.shawl.color : '#b8442a';
  const sash = cyl(0.195, 0.20, 0.055, clothMat(sashColor, 0.85), [0, 0.47, 0], [0, 0, 0], 22);
  g.add(sash);
  const sashDrape = box(0.042, 0.20, 0.02, clothMat(sashColor, 0.85), [0.13, 0.36, 0.16], [0, 0, -0.12]);
  g.add(sashDrape);

  // 5. Flowing Jama Robe Skirt (Drapes smoothly over hips and down to lap)
  const skirt = cyl(0.18, 0.32, 0.32, clothM, [0, 0.36, 0.04], [0.10, 0, 0], 24);
  g.add(skirt);

  // 6. Authentic Sadhu Cross-legged Posture (Padmasana / Sukhasana)
  // Wide thighs extending outward horizontally onto the cushion
  const thighL = cap(0.085, 0.28, dhotiM, [-0.20, 0.12, 0.12], [0.10, 0.55, -Math.PI * 0.45], 16);
  const thighR = cap(0.085, 0.28, dhotiM, [ 0.20, 0.12, 0.12], [0.10, -0.55, Math.PI * 0.45], 16);
  g.add(thighL, thighR);

  // Rounded knees resting solidly on the cushion
  const kneeL = sph(0.088, dhotiM, [-0.28, 0.12, 0.22], [1.1, 0.85, 1.2], 16);
  const kneeR = sph(0.088, dhotiM, [ 0.28, 0.12, 0.22], [1.1, 0.85, 1.2], 16);
  g.add(kneeL, kneeR);

  // Shins folded horizontally across the front (forming the classic crossed base)
  const shinCross = cap(0.078, 0.38, dhotiM, [0, 0.10, 0.24], [0, 0, Math.PI * 0.5], 18);
  g.add(shinCross);

  // Draped lap cloth connecting thighs, knees, and pelvis into an elegant unified seat
  const lapCloth = sph(0.18, dhotiM, [0, 0.16, 0.14], [1.4, 0.55, 1.1], 20);
  g.add(lapCloth);

  // Cascading front dhoti pleats (patli)
  for (let i = 0; i < 4; i++) {
    const x = -0.045 + i * 0.03;
    g.add(cap(0.012, 0.16, dhotiM, [x, 0.12, 0.28], [Math.PI * 0.12, 0, 0], 10));
  }

  // Tucked bare feet (Padmasana: right foot resting on left calf/crease, left foot tucked)
  const footSkin = skinMat(a.skin);
  const footR = sph(0.032, footSkin, [-0.14, 0.13, 0.25], [1.1, 0.55, 0.8], 12);
  const footL = sph(0.032, footSkin, [ 0.14, 0.09, 0.23], [1.1, 0.55, 0.8], 12);
  g.add(footR, footL);

  // 7. Placket button line down the front
  g.add(box(0.016, 0.30, 0.01, mat('#ede2cc'), [0, 0.60, 0.150]));
  for (let b = 0; b < 4; b++) {
    g.add(sph(0.007, mat('#d4af37', 0.4, 0.6), [0.014, 0.50 + b * 0.07, 0.152], [1, 1, 1], 10));
  }

  return { group: g, torso: chest };
}

// ─── Smooth Continuous Arms (Natural Resting on Knees in Mudra) ──
function makeArms(a, clothM, skinM) {
  const arms = [];
  for (const side of [-1, 1]) {
    const armGrp = new THREE.Group();
    // Shoulder anchor at side of upper chest
    armGrp.position.set(side * 0.18, 0.68, 0.01);

    // Continuous smooth cloth sleeve from shoulder to knee
    // Control points: shoulder -> upper arm -> elbow -> forearm -> wrist
    const pts = [
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(side * 0.01, -0.13, 0.01),
      new THREE.Vector3(side * 0.02, -0.26, 0.04),
      new THREE.Vector3(side * 0.05, -0.40, 0.14),
      new THREE.Vector3(side * 0.08, -0.51, 0.23),
    ];
    const curve = new THREE.CatmullRomCurve3(pts);
    const sleeveGeo = new THREE.TubeGeometry(curve, 18, 0.040, 10, false);
    const sleeve = new THREE.Mesh(sleeveGeo, clothM);
    sleeve.castShadow = true;
    armGrp.add(sleeve);

    // Shoulder cap for smooth blending into collar
    const shoulder = sph(0.048, clothM, [0, 0, 0], [1, 1, 1], 14);
    armGrp.add(shoulder);

    // Clean fitted cuff at wrist
    const cuff = cyl(0.038, 0.038, 0.018, mat('#ede2cc'), [side * 0.08, -0.51, 0.23], [0.65, 0, -side * 0.22], 12);
    armGrp.add(cuff);

    // Hand & Fingers resting solidly on top of the knee
    const handGrp = new THREE.Group();
    handGrp.position.set(side * 0.09, -0.52, 0.26);

    if (side === 1) {
      // Right hand: Sacred Gyan / Upadesha Mudra (teaching & wisdom)
      handGrp.rotation.set(0.40, 0.15, 0.12);
      const palm = sph(0.026, skinM, [0, 0, 0.016], [1.1, 0.50, 1.0], 12);
      handGrp.add(palm);

      // Thumb & Index finger meet in sacred circle of knowledge
      const thumb = cap(0.0055, 0.022, skinM, [ 0.009, 0.004, 0.024], [Math.PI * 0.32, 0,  0.42], 8);
      const indexF = cap(0.0052, 0.024, skinM, [ 0.002, 0.006, 0.028], [Math.PI * 0.42, 0,  0.18], 8);
      // Other 3 fingers (middle, ring, pinky) extended gracefully forward over knee curve
      const midF = cap(0.0055, 0.028, skinM, [-0.006, -0.003, 0.036], [Math.PI * 0.46, 0, -0.02], 8);
      const ringF = cap(0.0052, 0.026, skinM, [-0.014, -0.003, 0.034], [Math.PI * 0.46, 0, -0.06], 8);
      const pinky = cap(0.0048, 0.022, skinM, [-0.021, -0.003, 0.030], [Math.PI * 0.46, 0, -0.10], 8);
      handGrp.add(thumb, indexF, midF, ringF, pinky);
    } else {
      // Left hand: Dhyana / Peacefully resting open palm on left knee
      handGrp.rotation.set(0.40, -0.15, -0.12);
      const palm = sph(0.026, skinM, [0, 0, 0.016], [1.1, 0.50, 1.0], 12);
      handGrp.add(palm);

      for (let f = 0; f < 4; f++) {
        const finger = cap(0.0052, 0.026, skinM,
          [(f - 1.5) * 0.008, -0.003, 0.032],
          [Math.PI * 0.45, 0, (f - 1.5) * 0.05], 8);
        handGrp.add(finger);
      }
      const thumb = cap(0.0060, 0.020, skinM, [-0.013, 0.002, 0.020], [Math.PI * 0.32, 0, -0.42], 8);
      handGrp.add(thumb);
    }

    armGrp.add(handGrp);
    arms.push(armGrp);
  }
  return arms;
}

// ─── Draped Shawl (Uttariya / Chadar) ──────────────────────────
function makeShawl(a) {
  if (!a.shawl) return null;
  const c = clothMat(a.shawl.color, 0.92);
  const shawlGrp = new THREE.Group();

  // Draped band across left shoulder to right waist (flattened like real cloth)
  const pts = [
    new THREE.Vector3(-0.21, 0.72, 0.02),
    new THREE.Vector3(-0.16, 0.75, 0.06),
    new THREE.Vector3( 0.00, 0.68, 0.14),
    new THREE.Vector3( 0.16, 0.52, 0.13),
    new THREE.Vector3( 0.22, 0.38, 0.05),
    new THREE.Vector3( 0.18, 0.28, -0.08),
    new THREE.Vector3( 0.00, 0.36, -0.15),
    new THREE.Vector3(-0.18, 0.52, -0.09),
    new THREE.Vector3(-0.21, 0.72, 0.02),
  ];
  const curve = new THREE.CatmullRomCurve3(pts, true);
  // Slim tube radius, then scale flat against body
  const shawlGeo = new THREE.TubeGeometry(curve, 36, 0.018, 10, true);
  const shawlMesh = new THREE.Mesh(shawlGeo, c);
  shawlMesh.scale.set(1.0, 1.0, 0.55); // Flattens into a ribbon / shawl drape
  shawlMesh.castShadow = true;
  shawlGrp.add(shawlMesh);

  return shawlGrp;
}

// ─── Draped Tulsi Kanthi Mala ──────────────────────────────────
function makeMala(skinColor) {
  const g = new THREE.Group();
  const pts = [];
  for (let i = 0; i <= 24; i++) {
    const t = i / 24;
    const ang = -Math.PI * 0.45 + t * Math.PI * 0.9;
    pts.push(new THREE.Vector3(
      Math.sin(ang) * 0.16,
      0.62 - Math.cos(ang) * 0.12 - (t > 0.3 && t < 0.7 ? 0.04 : 0),
      0.135 + Math.cos(ang) * 0.06
    ));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const tube = new THREE.TubeGeometry(curve, 28, 0.004, 6, false);
  const mala = new THREE.Mesh(tube, mat('#4a6b2c', 0.8));
  mala.castShadow = true;
  g.add(mala);

  // Individual Tulsi beads
  for (let i = 1; i < 24; i += 2) {
    const p = curve.getPoint(i / 24);
    g.add(sph(0.007, mat('#3b5723', 0.8), [p.x, p.y, p.z], [1, 1, 1], 8));
  }
  return g;
}

// ─── Main Character Factory ────────────────────────────────────
export function makeCharacter(spec) {
  const a = spec.appearance, rng = seededRNG(spec.seed || spec.id);
  const root = new THREE.Group();

  const skin = skinMat(a.skin);
  const cloth = clothMat(a.upper.color);
  const dhoti = clothMat(a.lower.color);

  root.scale.setScalar((a.height || 1.7) / 1.7);

  // 1. Lower & Upper Body
  const { group: bodyGrp, torso } = makeBody(a, cloth, dhoti);
  root.add(bodyGrp);

  // 2. Shawl
  const shawl = makeShawl(a);
  if (shawl) root.add(shawl);

  // 3. Arms
  const arms = makeArms(a, cloth, skin);
  arms.forEach(arm => root.add(arm));

  // 4. Neck (smooth junction between collar and head base)
  const neck = cyl(0.052, 0.062, 0.14, skin, [0, 0.85, 0.01], [0, 0, 0], 20);
  neck.castShadow = true;
  root.add(neck);

  // 5. Head
  const head = new THREE.Group();
  head.position.set(0, 0.98, 0.02);
  root.add(head);

  const headMesh = new THREE.Mesh(makeHeadGeo(), skin);
  headMesh.scale.set(1.0, 1.08, 0.96);
  headMesh.castShadow = true;
  head.add(headMesh);

  // 6. Facial Features
  const { face, eyes } = makeFace(a, skin, rng);
  head.add(face);

  // 7. Pagdi (Turban)
  const turban = makeTurban(a, rng);
  turban.position.set(0, 0.06, -0.01);
  head.add(turban);

  // 8. Tulsi Mala
  if (a.mala === 'tulsi') {
    root.add(makeMala(a.skin));
  }

  root.userData = { head, face, eyes, arms, torso, spec };
  return root;
}
