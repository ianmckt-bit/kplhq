// Frame renderer: loads a video page, calls setData(data) once, then render(t) + screenshot per frame.
// usage: node tools/render.js PAGE_DIR OUT_DIR FPS DURATION [t1,t2,... preview times]
//   env: PAGE (default index.html)  DATA (default data.json)  W/H (default 1080x1920)
//        FROM/TO (frame range, for re-rendering just part of a video)
// Uses the Playwright + Chromium preinstalled in the session (no install step).
const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), require('child_process').execSync('npm root -g').toString().trim()] }));
const fs = require('fs'), path = require('path');
(async () => {
  const [dir, out, fps, dur, list] = process.argv.slice(2);
  if (!dir || !out || !fps || !dur) { console.error('usage: node tools/render.js PAGE_DIR OUT_DIR FPS DURATION [t1,t2,...]'); process.exit(2) }
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +(process.env.W || 1080), height: +(process.env.H || 1920) }, deviceScaleFactor: 1 });
  p.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1 });
  await p.goto('file://' + path.resolve(dir, process.env.PAGE || 'index.html'));
  await p.evaluate(d => window.setData(d), JSON.parse(fs.readFileSync(path.join(dir, process.env.DATA || (fs.existsSync(path.join(dir, 'data.json')) ? 'data.json' : 'data.example.json')))));
  await p.evaluate(() => document.fonts.ready);
  const F0 = +(process.env.FROM || 0), F1 = +(process.env.TO || Math.round(fps * dur));
  const idx = [...Array(F1 - F0).keys()].map(i => i + F0);
  const times = list ? list.split(',').map(Number) : idx.map(i => i / fps);
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => window.render(t), times[i]);
    await p.screenshot({ path: path.join(out, (list ? 'preview_' + times[i] : 'frame_' + String(idx[i]).padStart(4, '0')) + '.png') });
  }
  await b.close();
})();
