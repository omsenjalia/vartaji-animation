// ─── Vartaji Engine v2 — Shared Materials ─────────────────────
import * as THREE from 'three';

// Skin — warm, slightly translucent look via low roughness
export function skinMat(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.65, metalness: 0.02 });
}

// Cloth — fabric roughness, no shine
export function clothMat(color, roughness = 0.88) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 });
}

// Wood
export function woodMat(color = '#4a2f1d') {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.92, metalness: 0 });
}

// Foliage — double-sided for flat quads
export function leafMat(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.95, metalness: 0, side: THREE.DoubleSide });
}

// Brass / metal
export function metalMat(color = '#a8792c') {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.7 });
}

// Fire / emissive glow
export function fireMat(color, opacity = 0.9) {
  return new THREE.MeshBasicMaterial({ color, transparent: true, opacity, depthWrite: false });
}

// Hair / beard — dark matte
export function hairMat(color = '#20160e') {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.95, metalness: 0 });
}

// Ground with vertex colours
export function groundMat() {
  return new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0 });
}

// Generic shorthand
export function mat(color, roughness = 0.85, metalness = 0) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
}

// Stone
export function stoneMat(color = '#3a3530') {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.95, metalness: 0 });
}
