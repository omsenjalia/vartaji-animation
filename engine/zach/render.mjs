// Vartaji 3D renderer.
//   node engine/zach/render.mjs stills 0.5,10,46 reels/intro-gokulnath/stills
//   node engine/zach/render.mjs video reels/intro-gokulnath/out.mp4
//   node engine/zach/render.mjs mux reels/intro-gokulnath/out.mp4 reels/intro-gokulnath/audio/vo.mp4
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.mp3': 'audio/mpeg', '.mp4': 'video/mp4', '.png': 'image/png',
};
const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]);
  const p = path.join(ROOT, rel === '/' ? '/engine/zach/index.html' : rel);
  if (!p.startsWith(ROOT)) { res.writeHead(403); res.end(); return; }
  fs.readFile(p, (e, d) => {
    if (e) { res.writeHead(404); res.end('not found: ' + rel); return; }
    res.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' });
    res.end(d);
  });
}).listen(0);
const port = server.address().port;

// One renderer, two formats. See production/formats.md.
const FORMAT = process.env.FORMAT === 'long' ? 'long' : 'reel';
const W = Number(process.env.W || (FORMAT === 'long' ? 1280 : 720));
const H = Number(process.env.H || (FORMAT === 'long' ? 720 : 1280));
const GL = process.env.GL === 'swiftshader'
  ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
  : ['--enable-gpu'];
const browser = await chromium.launch({ args: [...GL, '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
page.on('pageerror', e => console.log('[pageerror]', e.message));
page.on('response', r => { if (r.status() >= 400) console.log('[http]', r.status(), r.url()); });
await page.goto(`http://localhost:${port}/engine/zach/index.html?render=1`);
await page.waitForFunction(() => window.renderAt && window.ready, null, { timeout: 90000 });
await page.evaluate(() => document.fonts.ready);

const shot = () => page.screenshot({ clip: { x: 0, y: 0, width: W, height: H }, type: 'png' });
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const [mode, a, b, c, d] = process.argv.slice(2);

if (mode === 'stills') {
  fs.mkdirSync(b, { recursive: true });
  for (const t of a.split(',').map(Number)) {
    const t0 = Date.now();
    await page.evaluate(t => window.renderAt(t), t);
    fs.writeFileSync(path.join(b, `t_${t.toFixed(2).padStart(6, '0')}.png`), await shot());
    console.log('still', t, Date.now() - t0, 'ms');
  }
} else if (mode === 'video') {
  const fps = Number(process.env.FPS || 30);
  const dur = await page.evaluate(() => window.DURATION);
  const from = Number(b || 0), to = Math.min(Number(c || dur), dur);
  const n0 = Math.round(from * fps), n1 = Math.floor(to * fps);
  fs.mkdirSync(path.dirname(a), { recursive: true });
  const ff = spawn(FFMPEG, [
    '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps),
    '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-preset', 'fast',
    '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), a,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const T0 = Date.now();
  for (let n = n0; n < n1; n++) {
    await page.evaluate(t => window.renderAt(t), n / fps);
    const buf = await shot();
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (n % 60 === 0) console.log(`frame ${n}/${n1} ${((Date.now() - T0) / (n - n0 + 1)).toFixed(0)} ms/frame`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log('video', a, ((Date.now() - T0) / 1000).toFixed(1), 's');
} else if (mode === 'mux') {
  const vo = b;
  if (!fs.existsSync(vo)) { console.error('VO not found:', vo); process.exitCode = 1; }
  else {
    const out = a.replace(/\.mp4$/, '_vo.mp4');
    await new Promise((res, rej) => {
      const ff = spawn(FFMPEG, [
        '-y', '-v', 'error', '-i', a, '-i', vo, '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', out,
      ], { stdio: 'inherit' });
      ff.on('close', code => code === 0 ? res() : rej(new Error('ffmpeg ' + code)));
    });
    console.log('muxed', out);
  }
} else {
  console.error('modes: stills | video | mux');
}

await browser.close();
server.close();
