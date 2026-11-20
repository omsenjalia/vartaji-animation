// ─── Vartaji Engine v2 — Caption System ───────────────────────
// Smooth fade transitions, no overlapping display.

export function createCaptionSystem(el, capsData) {
  let lastText = '';
  let fadeTimer = 0;

  return {
    update(t, shot) {
      const lt = t - shot.start;
      const dur = shot.end - shot.start;
      const inShot = lt > 0.04 && lt < dur - 0.04;

      // Find the active caption (use the latest-starting one to resolve overlaps)
      let cap = null;
      for (const c of capsData) {
        if (t >= c.s && t < c.e) {
          if (!cap || c.s > cap.s) cap = c;
        }
      }

      const text = cap && inShot ? cap.text : '';
      if (text !== lastText) {
        el.textContent = text;
        el.classList.toggle('on', text !== '');
        // Section-style for opening beats
        el.classList.toggle('section', false);
        lastText = text;
      }
    },
  };
}
