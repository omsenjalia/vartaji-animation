// ─── Vartaji Engine v2 — Animation System ─────────────────────
import * as THREE from 'three';
import { smooth, range, noise3D } from './math.js';

export function createAnimationSystem(gokul, kalyan, assembly, questioner, damodarRow, env) {
  const { flame1, flame2, flame3, embers, fireLight, floorGlow, floorShadow, sparks,
          diyaFlame, book, fireflies } = env;

  // Per-character blink timers (staggered)
  const gokulBlink = { next: 3.2, dur: 0.12 };
  const kalyanBlink = { next: 4.5, dur: 0.12 };

  function doBlink(t, blinkState) {
    if (t > blinkState.next) {
      blinkState.next = t + 2.5 + Math.random() * 3;
    }
    return (t > blinkState.next - blinkState.dur && t < blinkState.next) ? 0.12 : 1;
  }

  return {
    update(t, shot) {
      const lt = t - shot.start;
      const dur = shot.end - shot.start;
      const k = smooth(range(t, shot.start, shot.end));

      // ─── Fire animation ────────────────────────────
      const fl = 1 + Math.sin(t * 13) * 0.1 + Math.sin(t * 7.3) * 0.06 + noise3D(t * 2, 0, 0) * 0.08;
      flame1.scale.set(0.9 * fl, 1.0 * fl, 0.9 * fl);
      flame2.scale.set(0.85 * fl, 1.0 * fl, 0.85 * fl);
      if (flame3) flame3.scale.set(0.8 * fl, 1.0 * fl, 0.8 * fl);
      // Flame sway
      flame1.position.x = Math.sin(t * 3.5) * 0.008;
      flame2.position.x = Math.sin(t * 4.1 + 1) * 0.005;
      if (flame3) flame3.position.x = Math.sin(t * 4.8 + 2) * 0.004;
      flame1.rotation.z = Math.sin(t * 2.7) * 0.06;

      fireLight.intensity = 2.8 * fl * (1 + 0.3 * (shot.id === 's07' ? k : 0));
      // Colour temperature shift
      const tempShift = Math.sin(t * 5) * 0.03;
      fireLight.color.setHSL(0.065 + tempShift, 0.95, 0.55);

      embers.material.opacity = 0.45 + 0.15 * fl;
      diyaFlame.scale.set(0.8 * fl, 1.0 * fl, 0.8 * fl);

      // Sparks — varied speeds and heights
      for (const s of sparks) {
        const u = ((t * s.userData.speed * 0.35 + s.userData.base) % 1);
        const rr = s.userData.r + u * 0.3;
        s.position.set(
          Math.cos(s.userData.a) * rr + 0,
          0.2 + u * s.userData.r * 12,
          Math.sin(s.userData.a) * rr + 0.2);
        s.material.opacity = 0.7 * (1 - u);
        s.scale.setScalar(1 - u * 0.6);
      }

      // ─── Shot-specific staging ─────────────────────
      // s04: quiet midnight — floor glow + shadows
      if (shot.id === 's04') {
        floorGlow.intensity = 1.5;
        floorShadow.material.opacity = 0.4;
        floorShadow.scale.set(1.1 + lt * 0.3, 1, 1);
        floorShadow.position.x = -0.3 + lt * 0.08;
        book.rotation.z = Math.sin(t * 3.2) * 0.04;
      } else {
        floorGlow.intensity = 0;
        floorShadow.material.opacity = 0;
        book.rotation.z = 0;
      }

      // s05: questioner leans forward
      if (shot.id === 's05') {
        const lean = smooth(range(lt, 0, 3.5));
        questioner.rotation.z = -0.065 * lean;
        questioner.position.x = questioner.position.x - lean * 0.001;
      } else {
        questioner.rotation.z = 0;
      }

      // Clear assembly for intimate shots
      const clearRow = ['s06', 's09', 's10'].includes(shot.id);
      assembly.forEach(a => { a.visible = !clearRow; });
      if (shot.id === 's09' && t >= 72) damodarRow.visible = true;

      // ─── Character breathing ───────────────────────
      const breathe = 1 + Math.sin(t * 1.9) * 0.01;
      const breathe2 = 1 + Math.sin(t * 1.7 + 0.5) * 0.008;
      for (const [c, br] of [[gokul, breathe], [kalyan, breathe2]]) {
        if (c.userData.torso?.scale) c.userData.torso.scale.set(br, 1, br);
      }

      // ─── Arm sway ──────────────────────────────────
      if (gokul.userData.arms?.[0]) {
        gokul.userData.arms[0].rotation.z = Math.sin(t * 1.1) * 0.015;
        gokul.userData.arms[1].rotation.z = -Math.sin(t * 1.1 + 0.3) * 0.015;
      }
      if (kalyan.userData.arms?.[0]) {
        kalyan.userData.arms[0].rotation.z = Math.sin(t * 0.9) * 0.01;
        kalyan.userData.arms[1].rotation.z = -Math.sin(t * 0.9 + 0.5) * 0.01;
      }

      // ─── Head motion — responsive to narrative ─────
      // In shot 3, head turns slightly toward the camera/campfire profile
      const s03Turn = shot.id === 's03' ? -0.32 : (t > 30 && t < 44 ? 0.05 : 0);
      const gokulHead = gokul.userData.head;
      gokulHead.rotation.y = noise3D(t * 0.3, 0, 10) * 0.04 + s03Turn
        + (shot.id === 's07' ? noise3D(t * 0.5, 0, 20) * 0.02 : 0); // animated during answer
      gokulHead.rotation.x = noise3D(0, t * 0.4, 15) * 0.012;
      gokulHead.rotation.z = noise3D(t * 0.25, 0, 25) * 0.015
        + (shot.id === 's03' ? -0.02 : 0);  // gentle noble tilt

      // Kalyanbhatt: listening, gentle nod
      kalyan.userData.head.rotation.y = noise3D(t * 0.2, 0, 30) * 0.02;
      kalyan.userData.head.rotation.x = noise3D(0, t * 0.3, 35) * 0.01;

      // ─── Assembly — staggered gentle motion ────────
      assembly.forEach((a, i) => {
        if (!a.visible) return;
        const phase = i * 0.7;
        a.position.y = (a.position.y > 0.3 ? a.position.y : 0)
          + Math.sin(t * 1.4 + phase) * 0.004;
        // Subtle head turns toward the teacher
        if (a.userData?.head?.rotation) {
          a.userData.head.rotation.y = noise3D(t * 0.15 + i * 3, 0, 40 + i) * 0.03;
          a.userData.head.rotation.x = Math.sin(t * 0.8 + phase) * 0.008;
        }
      });

      // ─── Face Visibility (Always visible, eyes clear & luminous) ──
      gokul.userData.face.visible = true;

      // Natural, intelligent blinking — no closed or sleepy eyes
      const gokulBlinkScale = doBlink(t, gokulBlink);
      const kalyanBlinkScale = doBlink(t, kalyanBlink);
      for (const e of gokul.userData.eyes) {
        if (e.scale) e.scale.y = e.scale.y > 0 ? gokulBlinkScale : e.scale.y;
      }
      for (const e of (kalyan.userData.eyes || [])) {
        if (e.scale) e.scale.y = e.scale.y > 0 ? kalyanBlinkScale : e.scale.y;
      }

      // ─── Fireflies ─────────────────────────────────
      if (fireflies) {
        for (const fly of fireflies) {
          const { base, phase, speed, brightness } = fly.userData;
          const ft = t * speed + phase;
          fly.position.set(
            base[0] + Math.sin(ft * 0.7) * 0.45,
            base[1] + Math.sin(ft * 0.5 + 1) * 0.25,
            base[2] + Math.cos(ft * 0.3) * 0.35);
          // Pulse — fades in/out gently
          fly.material.opacity = brightness * Math.max(0, Math.sin(ft * 2.5)) * 0.6;
        }
      }
    },
  };
}
