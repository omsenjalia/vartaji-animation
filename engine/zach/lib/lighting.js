// ─── Vartaji Engine v2 — Lighting + Post-Processing ───────────
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// Cinematic night film grade: preserves deep night mood while keeping background forest and faces rich & clear
const CinematicGradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    contrast: { value: 1.04 },
    saturation: { value: 1.10 },
    vignetteStrength: { value: 0.28 },
  },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */`
    uniform sampler2D tDiffuse;
    uniform float contrast;
    uniform float saturation;
    uniform float vignetteStrength;
    varying vec2 vUv;

    void main() {
      vec4 tex = texture2D(tDiffuse, vUv);
      vec3 color = tex.rgb;

      // Gentle filmic tone curve lifting shadows for forest visibility
      color = pow(max(vec3(0.001), color), vec3(0.88));
      color = mix(color, color * color * (3.0 - 2.0 * color), 0.18);

      // Saturation
      float lum = dot(color, vec3(0.299, 0.587, 0.114));
      color = mix(vec3(lum), color, saturation);

      // Atmospheric night palette: rich moonlight cool blues in shadows, warm golden fire in mid-highlights
      color.b += 0.022 * smoothstep(0.45, 0.0, lum);
      color.r += 0.016 * smoothstep(0.18, 0.75, lum);

      // Soft vignette focusing attention to the central gathering
      vec2 coord = (vUv - 0.5) * vec2(1.0, 1.45);
      float dist = dot(coord, coord);
      float vig = smoothstep(0.75, 0.20, dist);
      color *= mix(1.0 - vignetteStrength, 1.0, vig);

      gl_FragColor = vec4(clamp(color, 0.0, 1.0), tex.a);
    }
  `,
};

export function buildLighting(scene, renderer, camera) {
  // ─── Hemisphere Light (Sky cool twilight blue + ground dark forest moss) ─
  const hemi = new THREE.HemisphereLight('#4e729f', '#1c281a', 0.95);
  scene.add(hemi);

  // ─── Ambient Light (Gentle base visibility) ─────────────────
  const ambient = new THREE.AmbientLight('#263a50', 0.70);
  scene.add(ambient);

  // ─── Main Moonlight (Direct cool blue key from upper-left) ────
  const moon = new THREE.DirectionalLight('#92b7e8', 0.90);
  moon.position.set(-6, 11, 4);
  moon.castShadow = true;
  moon.shadow.mapSize.set(1024, 1024);
  moon.shadow.bias = -0.0008;
  scene.add(moon);

  // ─── Forest Frontal Moon Light (Illuminates tree trunks and canopy facing camera) ─
  const forestTarget = new THREE.Object3D();
  forestTarget.position.set(0, 2.5, -3.5);
  scene.add(forestTarget);

  const forestFront = new THREE.DirectionalLight('#78a4d8', 1.45);
  forestFront.position.set(-2, 7.5, 4);
  forestFront.target = forestTarget;
  scene.add(forestFront);

  // ─── Back Rim Light (Luminous silver edge on characters & Kadamba) ───
  const rim = new THREE.DirectionalLight('#86b0e6', 1.15);
  rim.position.set(1, 6, -5.5);
  scene.add(rim);

  // ─── Dedicated Portrait Key Light (Illuminates Guru's face & eyes in s03 & close-ups) ──
  const portraitKey = new THREE.PointLight('#ffb366', 2.2, 5.0, 1.1);
  portraitKey.position.set(-0.9, 1.62, -0.6);
  scene.add(portraitKey);

  // ─── Portrait Rim Light (Crisp pagdi & jawline separation) ────
  const portraitRim = new THREE.PointLight('#9ec2f2', 1.4, 4.0, 1.2);
  portraitRim.position.set(0.9, 1.85, -1.9);
  scene.add(portraitRim);

  // ─── Post-Processing Pipeline ───────────────────────────────
  const size = new THREE.Vector2(renderer.domElement.width, renderer.domElement.height);
  const composer = new EffectComposer(renderer);
  composer.setSize(size.x, size.y);

  // 1. Scene render
  composer.addPass(new RenderPass(scene, camera));

  // 2. Bloom — glows only fire, sparks, and bright moonlit rim
  const bloom = new UnrealBloomPass(size, 0.42, 0.35, 0.82);
  composer.addPass(bloom);

  // 3. Cinematic Color Grade
  const grade = new ShaderPass(CinematicGradeShader);
  composer.addPass(grade);

  // 4. Output color management
  composer.addPass(new OutputPass());

  function updateLighting(t, shot) {
    const isPortrait = shot && (shot.id === 's03' || shot.id === 's07');
    portraitKey.intensity = isPortrait ? 2.6 : 1.4;
    portraitRim.intensity = isPortrait ? 1.6 : 0.9;
    bloom.strength = isPortrait ? 0.38 : 0.45;
  }

  return { composer, updateLighting };
}
