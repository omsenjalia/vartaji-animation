// ─── Vartaji Engine v2 — Math Utilities ───────────────────────
// Noise, easing, interpolation. No external deps.

export const clamp = (x, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));
export const lerp  = (a, b, t) => a + (b - a) * t;
export const range = (t, a, b) => clamp((t - a) / (b - a));
export const mix   = (a, b, t) => a * (1 - t) + b * t;

// Easing
export const easeIn    = t => t * t * t;
export const easeOut   = t => { const u = 1 - t; return 1 - u * u * u; };
export const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
export const smooth    = t => t * t * (3 - 2 * t);       // hermite
export const smoother  = t => t * t * t * (t * (6 * t - 15) + 10);

// Exponential damping for smooth follow
export const damp = (a, b, lambda, dt) => lerp(a, b, 1 - Math.exp(-lambda * dt));

// ─── Perlin noise ──────────────────────────────────────────────
const P = new Uint8Array(512);
{
  const p = new Uint8Array(256);
  for (let i = 0; i < 256; i++) p[i] = i;
  for (let i = 255; i > 0; i--) {
    const j = (i * 16807 + 13) % 256;
    [p[i], p[j]] = [p[j], p[i]];
  }
  for (let i = 0; i < 512; i++) P[i] = p[i & 255];
}

const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
const grad3 = (h, x, y, z) => {
  const k = h & 15;
  const u = k < 8 ? x : y;
  const v = k < 4 ? y : (k === 12 || k === 14 ? x : z);
  return ((k & 1) ? -u : u) + ((k & 2) ? -v : v);
};

export function noise3D(x, y, z) {
  const X = Math.floor(x) & 255, Y = Math.floor(y) & 255, Z = Math.floor(z) & 255;
  x -= Math.floor(x); y -= Math.floor(y); z -= Math.floor(z);
  const u = fade(x), v = fade(y), w = fade(z);
  const A = P[X] + Y, AA = P[A] + Z, AB = P[A + 1] + Z;
  const B = P[X + 1] + Y, BA = P[B] + Z, BB = P[B + 1] + Z;
  return lerp(
    lerp(lerp(grad3(P[AA], x, y, z),     grad3(P[BA], x-1, y, z),   u),
         lerp(grad3(P[AB], x, y-1, z),   grad3(P[BB], x-1, y-1, z), u), v),
    lerp(lerp(grad3(P[AA+1], x, y, z-1), grad3(P[BA+1], x-1, y, z-1), u),
         lerp(grad3(P[AB+1], x, y-1, z-1),grad3(P[BB+1], x-1, y-1, z-1), u), v), w);
}

export function noise2D(x, y) { return noise3D(x, y, 0); }

export function fbm(x, y, z = 0, octaves = 4) {
  let v = 0, amp = 0.5, freq = 1;
  for (let i = 0; i < octaves; i++) {
    v += amp * noise3D(x * freq, y * freq, z * freq);
    freq *= 2; amp *= 0.5;
  }
  return v;
}

// ─── Camera shake — multi-frequency Perlin ─────────────────────
export function cameraShake(t, intensity = 1) {
  return {
    x: (noise3D(t * 0.7, 0, 100) * 0.6 + noise3D(t * 1.3, 0, 200) * 0.3) * 0.014 * intensity,
    y: (noise3D(0, t * 0.5, 300) * 0.6 + noise3D(0, t * 1.1, 400) * 0.3) * 0.007 * intensity,
    z: (noise3D(t * 0.6, t * 0.3, 500) * 0.5 + noise3D(t * 0.9, 0, 600) * 0.3) * 0.011 * intensity,
  };
}

// ─── Seeded PRNG ───────────────────────────────────────────────
export function seededRNG(seed) {
  let h = 2166136261;
  for (const c of String(seed)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); }
  return () => {
    h += 0x6D2B79F5; let t = h;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// ─── Vector3 helpers ───────────────────────────────────────────
export const v3lerp = (a, b, t) => [lerp(a[0],b[0],t), lerp(a[1],b[1],t), lerp(a[2],b[2],t)];
