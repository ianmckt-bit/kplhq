/* KPL 8-bit video kit: shared runtime.
   Every video page is a pure function of time: window.render(t) draws frame t, window.setData(d) loads data.
   tools/render.js steps t frame by frame and screenshots, so nothing here may depend on wall-clock time
   or randomness that is not seeded. Everything is exposed on window.K8. See STYLE.md for the rules. */
(function () {
  const K8 = {};
  // ---------- math + easing ----------
  const cl = x => Math.max(0, Math.min(1, x)), P = (t, a, b) => cl((t - a) / (b - a));
  Object.assign(K8, {
    cl, P,
    oc: x => 1 - Math.pow(1 - x, 3),                                   // ease-out cubic
    oq: x => 1 - Math.pow(1 - x, 5),                                   // ease-out quint (drops, rises)
    io: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2, // ease-in-out cubic (wipes, exits)
    sine: x => -(Math.cos(Math.PI * x) - 1) / 2,                       // count-ups
    spr: x => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.exp(-6.5 * x) * Math.cos(8.5 * x), // soft spring (floaty)
    snap: (v, g = 6) => Math.round(v / g) * g,                          // pixel grid snap
    blink: (t, p = .5) => Math.floor(t / p) % 2 === 0,
    fmt: v => Math.round(v).toLocaleString('en-US'),
    rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647 }
  });
  // ---------- DOM helpers ----------
  K8.$ = s => document.getElementById(s);
  K8.el = x => typeof x === 'string' ? K8.$(x) : x;
  K8.set = (x, css) => Object.assign(K8.el(x).style, css);
  /** spring in: opacity + translate from (dx,dy) to rest between u=a and a+d, then gentle float */
  K8.fin = (x, u, a, d = .7, dy = 60, dx = 0) => { const p = P(u, a, a + d), e = K8.spr(p), E = K8.el(x); E.style.opacity = Math.min(1, p * 2.4); E.style.transform = `translate(${(1 - e) * dx}px,${(1 - e) * dy}px)` };
  /** NFL-style slam: scale 2.4 -> 1 */
  K8.slam = (x, u, a, d = .22) => { const p = P(u, a, a + d); K8.set(x, { transform: `scale(${p < 1 ? 2.4 - 1.4 * K8.oq(p) : 1})`, opacity: p > 0 ? 1 : 0 }) };
  /** count a number up between a and b (sine eased); decimals as given */
  K8.count = (x, u, a, b, value, dec = 1, prefix = '') => { K8.el(x).textContent = prefix + (value * K8.sine(P(u, a, b))).toFixed(dec) };
  // ---------- timeline ----------
  /** scenes: [[id,start,end],...]; returns {scene(t)->[id,u], end, starts} */
  K8.timeline = scenes => ({ scenes, end: scenes[scenes.length - 1][2], starts: scenes.slice(1).map(s => s[1]),
    scene(t) { const s = scenes.find(s => t >= s[1] && t < s[2]) || scenes[scenes.length - 1]; return [s[0], t - s[1]] },
    show(t) { const [id] = this.scene(t); document.querySelectorAll('.scene').forEach(e => e.style.display = e.id === id ? 'block' : 'none'); return this.scene(t) } });

  // ---------- pixel art ----------
  const LEAF = ['....X....', '.X..X..X.', '.XX.X.XX.', '..XXXXX..', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..', '....S....', '....S....'];
  K8.LEAF_COLS = ['#ff8a1f', '#b8481a', '#ffe32b', '#c4002b'];
  K8.leaf = (c, cx, cy, S, col, flip) => { const at = (x, y) => LEAF[y] && LEAF[y][x] && LEAF[y][x] !== '.';
    for (let y = -1; y <= 9; y++) for (let x = -1; x <= 9; x++) { const X = flip ? 8 - x : x; let f = null;
      if (at(X, y)) f = LEAF[y][X] === 'S' ? '#6b3612' : col; else if (at(X + 1, y) || at(X - 1, y) || at(X, y + 1) || at(X, y - 1)) f = '#0c0a14';
      if (f) { c.fillStyle = f; c.fillRect(cx + (x - 4) * S, cy + (y - 4) * S, S, S) } } };
  const BAT = [['..x.....x..', '..xx...xx..', '.xxxxxxxxx.', 'xxx.xxx.xxx', 'x....x....x'], ['...........', '..x.....x..', '.xxxxxxxxx.', 'xxxxxxxxxxx', '.x.......x.']];
  K8.bat = (c, x, y, S, frame) => { c.fillStyle = '#000'; BAT[frame % 2].forEach((r, yy) => [...r].forEach((ch, xx) => { if (ch === 'x') c.fillRect(Math.round(x) + xx * S, Math.round(y) + yy * S, S, S) })) };
  /** pixel blood-moon / harvest sun */
  K8.moon = (c, cx, cy, R, t, pal = ['#7a1410', '#a8261c', '#d0402e', '#ff6a3d']) => { const S = 10;
    for (let y = -R; y <= R; y += S) for (let x = -R; x <= R; x += S) { const d = Math.hypot(x, y); if (d > R) continue; const k = d / R;
      c.fillStyle = k > .9 ? pal[0] : k > .7 ? pal[1] : ((x * 7 + y * 3) % 9 === 0 ? pal[1] : pal[2]); c.fillRect(cx + x, cy + y, S, S) }
    c.globalAlpha = .18 + .06 * Math.sin(t * 2); c.fillStyle = pal[3]; c.beginPath(); c.arc(cx, cy, R + 30, 0, 7); c.fill(); c.globalAlpha = 1 };
  /** original pixel turkey on a 32x32 grid; flaps its tail on t */
  K8.turkey = (cv, t) => { const c = cv.getContext('2d'), S = cv.width / 32; c.clearRect(0, 0, cv.width, cv.height); const G = []; const flap = Math.floor(t / .18) % 2;
    for (let y = 0; y < 32; y++) { G[y] = []; for (let x = 0; x < 32; x++) { let col = null; const dx = x - 15.5, dy = y - 19.5, r = Math.hypot(dx, dy), a = Math.atan2(dy, dx);
      if (y <= 20 && r >= 7 && r < 15.5 - (flap && (Math.floor((a + Math.PI) / (Math.PI / 7)) % 2) ? 1 : 0)) { const band = Math.floor((a + Math.PI) / (Math.PI / 7)); col = ['#c4002b', '#ff8a1f', '#ffe32b', '#b8481a', '#ff8a1f', '#c4002b', '#ffe32b', '#b8481a'][band % 8]; if (r > 14) col = '#6b3612' }
      if (((dx / 7) ** 2 + ((y - 21) / 8) ** 2) <= 1) col = (x > 13 && x < 18 && y > 20) ? '#b8724a' : '#7a4016'; if (Math.hypot(x - 15.5, y - 11.5) <= 3.4) col = '#9c5a2e';
      if ((x === 14 || x === 15) && y === 10) col = '#f8fbff'; if (x === 15 && y === 11) col = '#000000'; if ((x >= 16 && x <= 18) && y === 12) col = '#ffe32b'; if (x === 16 && (y >= 13 && y <= 15)) col = '#ff1644'; if (x === 15 && y === 14) col = '#ff1644';
      if ((x === 13 || x === 18) && y >= 28 && y <= 30) col = '#ff8a1f'; if (y === 30 && (x === 12 || x === 14 || x === 17 || x === 19)) col = '#ff8a1f'; G[y][x] = col } }
    for (let y = 0; y < 32; y++) for (let x = 0; x < 32; x++) { let col = G[y][x]; if (!col && [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([a, b]) => G[y + b] && G[y + b][x + a])) col = '#0c0a14'; if (col) { c.fillStyle = col; c.fillRect(x * S, y * S, S, S) } } };
  /** ring of leaves bursting out around (cx,cy); burst starts at u=a */
  K8.wreath = (c, u, cx, cy, a = .3, n = 22, r1 = 300, r2 = 250) => { for (let i = 0; i < n; i++) { const ang = -Math.PI / 2 + i / n * 2 * Math.PI, p = K8.oq(P(u, a + i * .012, a + .5 + i * .012)); if (p <= 0) continue;
    const r = (i % 2 ? r2 : r1) * p; K8.leaf(c, K8.snap(cx + Math.cos(ang) * r + Math.sin(u * 3 + i) * 6 * p, 6), K8.snap(cy + Math.sin(ang) * r, 6), i % 2 ? 8 : 9, K8.LEAF_COLS[i % 4], i % 2) } };
  /** feast table (1080x440 canvas): cloth, roast turkey + steam, candles, pumpkins, pie. rise = px offset from below */
  K8.feast = (cv, t, rise = 0) => { const c = cv.getContext('2d'); c.clearRect(0, 0, cv.width, cv.height); const S = 8, px = (x, y, col) => { c.fillStyle = col; c.fillRect(x * S, y * S, S, S) }; c.save(); c.translate(0, rise);
    for (let x = 4; x < 131; x++) for (let y = 36; y < 44; y++) px(x, y, y === 36 ? '#000' : (y === 43 ? '#efe2d0' : ((x + y) % 7 === 0 ? '#8c1a20' : '#a8212a'))); for (let x = 4; x < 131; x++) px(x, 44, '#000');
    for (const lx of [12, 13, 121, 122]) for (let y = 45; y < 54; y++) px(lx, y, '#2a0a08');
    for (let x = 46; x < 89; x++) for (let y = 33; y < 36; y++) px(x, y, y === 33 ? '#c6b0a3' : '#efe2d0');
    for (let y = 18; y < 33; y++) for (let x = 50; x < 85; x++) { const d = ((x - 67.5) / 17) ** 2 + ((y - 27) / 9) ** 2; if (d <= 1) px(x, y, d > .8 ? '#4a1e0c' : (y < 22 && x > 58 && x < 72) ? '#e09a4a' : (d < .4 ? '#b8641e' : '#8a4414')) }
    for (const [dx, dir] of [[50, -1], [84, 1]]) { for (let k = 0; k < 6; k++) { px(dx + dir * k, 26 - k, '#8a4414'); px(dx + dir * k, 27 - k, '#b8641e') } px(dx + dir * 6, 19, '#efe2d0'); px(dx + dir * 7, 18, '#efe2d0'); px(dx + dir * 7, 19, '#efe2d0') }
    for (let k = 0; k < 3; k++) { const sx = 60 + k * 8, sy = 17 - Math.floor(((t * 6 + k * 3) % 12) / 2); px(sx, sy, 'rgba(239,226,208,.5)'); px(sx + 1, sy - 2, 'rgba(239,226,208,.35)') }
    for (const cxp of [26, 108]) { for (let y = 22; y < 36; y++) { px(cxp, y, '#efe2d0'); px(cxp + 1, y, '#c6b0a3') } const fl = Math.floor(t * 10) % 2; px(cxp, 21, '#f2a52b'); px(cxp + 1 - fl, 20, '#ffd27a'); px(cxp, 19, fl ? '#ff6a3d' : '#f2a52b');
      c.globalAlpha = .18 + .06 * Math.sin(t * 9 + cxp); c.fillStyle = '#f2a52b'; c.beginPath(); c.arc(cxp * S + 8, 20 * S, 70, 0, 7); c.fill(); c.globalAlpha = 1; for (let x = cxp - 2; x < cxp + 4; x++) px(x, 35, '#6b161b') }
    for (const [p0, r] of [[34, 5], [98, 4], [115, 5]]) { for (let y = -r; y <= r; y++) for (let x = -r - 2; x <= r + 2; x++) if ((x / (r + 2)) ** 2 + (y / r) ** 2 <= 1) px(p0 + x, 35 - r + y, (x % 3 === 0) ? '#c4600e' : '#ff8a1f'); px(p0, 35 - 2 * r - 1, '#2f5a1a'); px(p0, 35 - 2 * r, '#2f5a1a') }
    for (let y = 0; y < 4; y++) for (let x = -6 + y; x <= 6 - y; x++) px(14 + x, 35 - y, y === 3 ? '#e8b46a' : (y === 0 ? '#8a4414' : '#c4600e')); c.restore() };
  /** 8-bit player sprite (from tools/pixelate.py), bottom-centred in the canvas */
  K8.sprite = (cv, img, scale) => { const c = cv.getContext('2d'); c.imageSmoothingEnabled = false; c.clearRect(0, 0, cv.width, cv.height); if (!img) return; const w = img.width * scale, h = img.height * scale; c.drawImage(img, Math.round((cv.width - w) / 2), cv.height - h, w, h) };
  K8.loadImg = src => new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = src });

  // ---------- backgrounds (canvas 1080x1920 or 1920x1080) ----------
  const R = K8.rng(1137);
  const STARS = [...Array(150)].map(() => ({ x: R(), y: R(), z: 1 + Math.floor(R() * 3), c: R() }));
  const LEAVES = [...Array(26)].map(() => ({ x: R(), y: R(), s: .5 + R(), c: Math.floor(R() * 3), w: R() * 6 }));
  const EMBERS = [...Array(60)].map(() => ({ x: R(), y: R(), s: .4 + R(), c: R() }));
  const BATS = [...Array(5)].map(() => ({ y: .14 + R() * .36, sp: 60 + R() * 70, ph: R() * 1000, sc: R() < .5 ? 4 : 6 }));
  function leaves(c, t, W, H, speed = 100) { for (const l of LEAVES) { const y = (l.y * H + t * speed * l.s) % H, x = l.x * W + Math.sin(t * 1.5 + l.w) * 40; K8.leaf(c, K8.snap(x, 4), K8.snap(y, 4), l.s > 1 ? 4 : 3, ['#ff8a1f', '#b8481a', '#ffe32b'][l.c], l.c % 2) } }
  /** KPL HQ look: navy grid, scrolling starfield, optional falling leaves, turf strip */
  K8.bgKPL = (c, t, o = {}) => { const W = c.canvas.width, H = c.canvas.height; c.fillStyle = '#020f3d'; c.fillRect(0, 0, W, H);
    c.fillStyle = 'rgba(91,145,255,.07)'; for (let x = 0; x < W; x += 48) c.fillRect(x, 0, 2, H); for (let y = (t * 60) % 48; y < H; y += 48) c.fillRect(0, y, W, 2);
    for (const s of STARS) { const y = (s.y * H + t * s.z * 60) % H; c.fillStyle = s.c < .12 ? '#ffe32b' : s.c < .22 ? '#ff8a1f' : 'rgba(207,224,255,' + (.25 + s.z * .2) + ')'; c.fillRect(K8.snap(s.x * W, 4), K8.snap(y, 4), s.z * 4, s.z * 4) }
    if (o.leaves) leaves(c, t, W, H);
    if (o.turf !== false) { const y0 = H - 160; c.fillStyle = '#0b3e28'; c.fillRect(0, y0, W, 160); c.fillStyle = '#35f377'; for (let x = -(t * 120 % 96); x < W; x += 96) c.fillRect(x, y0, 48, 8); c.fillStyle = 'rgba(248,251,255,.5)'; for (let x = -(t * 120 % 120); x < W; x += 120) c.fillRect(x, y0 + 60, 8, 100) } };
  // castle skyline for the haunted look (House of Heck)
  const CASTLE = (W, H) => { const h = []; const k = W / 1080; for (let x = 0; x < W; x += 12) { const xx = x / k; let y = H - 140 - ((Math.sin(xx * .011) + 1) * 30); if ((xx > 120 && xx < 240) || (xx > 780 && xx < 900)) y = H - 320; if (xx > 420 && xx < 660) y = H - 380; if ((xx > 140 && xx < 170) || (xx > 800 && xx < 830)) y = H - 420; if (xx > 520 && xx < 560) y = H - 480; h.push([x, Math.round(y / 12) * 12]) } return h };
  /** haunted night: crimson gradient, grid, red moon, embers, bats, leaves, castle with flickering windows.
      o.moon = {x,y,r} or null; o.leaves (bool); o.bats (bool) */
  K8.bgHaunted = (c, t, o = {}) => { const W = c.canvas.width, H = c.canvas.height; const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0b0306'); g.addColorStop(.6, '#1a0508'); g.addColorStop(1, '#2a070b'); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.fillStyle = 'rgba(191,54,43,.06)'; for (let x = 0; x < W; x += 48) c.fillRect(x, 0, 2, H); for (let y = (t * 30) % 48; y < H; y += 48) c.fillRect(0, y, W, 2);
    if (o.moon) K8.moon(c, o.moon.x, o.moon.y, o.moon.r, t);
    for (const e of EMBERS) { const y = H - ((H - e.y * H + t * 90 * e.s) % H), x = e.x * W + Math.sin(t * 1.3 + e.y * 99) * 20; c.fillStyle = e.c < .4 ? '#f2a52b' : e.c < .75 ? '#bf362b' : '#efe2d0'; c.globalAlpha = .25 + .5 * e.s * (y / H); c.fillRect(K8.snap(x, 4), K8.snap(y, 4), e.s > 1 ? 8 : 4, e.s > 1 ? 8 : 4) } c.globalAlpha = 1;
    if (o.leaves) leaves(c, t, W, H, 90);
    if (o.bats !== false) for (const b of BATS) K8.bat(c, ((t * b.sp + b.ph) % (W + 220)) - 110, b.y * H + Math.sin(t * 2 + b.ph) * 30, b.sc, Math.floor(t * 8 + b.ph));
    const cs = CASTLE(W, H); c.fillStyle = '#050103'; cs.forEach(([x, y]) => c.fillRect(x, y, 12, H - y));
    for (let i = 0; i < 26; i++) { const x = 60 + ((i * 173) % (W - 120)), y = H - 300 + ((i * 97) % 220); if (Math.sin(t * (1.3 + i % 3) + i * 7) <= -.6) continue; const col = cs.find(p => p[0] <= x && x < p[0] + 12); if (!col || y < col[1] + 24) continue; c.fillStyle = i % 4 ? '#f2a52b' : '#bf362b'; c.fillRect(K8.snap(x), K8.snap(y), 12, 18) } };

  // ---------- holo card ----------
  /** sweeping foil band (element with class .holo) cycling every `period` seconds */
  K8.holo = (x, u, period = 3.1) => K8.set(x, { transform: `translateX(${-200 + 1900 * K8.io(P(u % period, .3, 1.6))}px) rotate(20deg)` });
  K8.sparkles = (c, u, cols = ['#efe2d0', '#f2a52b']) => { const W = c.canvas.width, H = c.canvas.height; c.clearRect(0, 0, W, H); for (let i = 0; i < 26; i++) { const x = (i * 233) % (W - 20) + 10, y = (i * 419) % (H - 30) + 10, a = Math.max(0, Math.sin(u * 3 + i * 1.7)); if (a < .6) continue; c.globalAlpha = (a - .6) * 2.5; c.fillStyle = cols[i % 3 ? 0 : 1]; c.fillRect(x, y - 8, 4, 20); c.fillRect(x - 8, y, 20, 4) } c.globalAlpha = 1 };
  /** card choreography: flip in from the back, hold, slide out left, return small for the outro.
      k = {flipIn:[a,b], show:b, exit:[a,b], outro:a, outroPose:{s,y}} ; t is global time */
  K8.cardPose = (wrap, card, t, k) => { let s = 1, x = 0, y = 0, op = 1, ry = 0;
    if (t < k.flipIn[0]) op = 0;
    else if (t < k.show) { const p = K8.oq(P(t, k.flipIn[0], k.flipIn[1])); s = .3 + .7 * p; y = (1 - p) * 500; ry = 180 - 180 * K8.sine(P(t, k.flipIn[1], k.show + .1)) }
    else if (t < k.exit[0]) { } else if (t < k.exit[1]) { const p = K8.io(P(t, k.exit[0], k.exit[1])); x = -1300 * p; ry = -25 * p }
    else if (t < k.outro) op = 0; else { const p = K8.spr(P(t, k.outro, k.outro + .9)); s = k.outroPose.s; y = k.outroPose.y; x = (1 - p) * 1300; ry = (1 - p) * 30 }
    ry += Math.sin(t * 1.2) * 5; K8.el(wrap).style.opacity = op; K8.el(wrap).style.transform = `translate(${x}px,${y + Math.sin(t * 1.5) * 8}px) scale(${s})`; K8.el(card).style.transform = `rotateY(${ry}deg) rotateX(${Math.cos(t * .9) * 3}deg)` };

  // ---------- charts ----------
  /** weekly fantasy bars. o={x0,x1,y,h,max,weeks:[{wk,pts,played}],best:wk,avg,hot:40,cols:{bar,hot,best,grid,text},u,start,step,labels:{week:id-prefix,value:id-prefix}} */
  K8.weekBars = (c, o) => { const W = o.weeks, n = W.length, bw = (o.x1 - o.x0) / n, sc = o.h / o.max, u = o.u, C = o.cols;
    c.globalAlpha = P(u, .3, .7); c.fillStyle = C.grid; for (let v = 0; v <= o.max; v += 10) c.fillRect(o.x0, o.y - v * sc, o.x1 - o.x0, 2); c.fillStyle = C.text; c.font = '14px PS2P'; c.textAlign = 'right'; for (let v = 0; v <= o.max; v += 20) c.fillText(v, o.x0 - 14, o.y - v * sc + 6); c.fillRect(o.x0, o.y, o.x1 - o.x0, 4); c.globalAlpha = 1;
    W.forEach((w, i) => { const a = o.start + i * o.step, p = K8.spr(P(u, a, a + .8)), x = o.x0 + i * bw + 10, bwid = bw - 20, lab = K8.$(o.labels.value + i); K8.$(o.labels.week + i).style.opacity = P(u, .3, .6);
      if (!w.played) { c.globalAlpha = P(u, a, a + .3); c.strokeStyle = C.bye; c.lineWidth = 4; c.strokeRect(x, o.y - 60, bwid, 60); for (let k = 0; k < 60; k += 12) { c.fillStyle = C.bye; c.fillRect(x, o.y - 60 + k, bwid, 4) } c.globalAlpha = 1; lab.style.top = (o.y - 96) + 'px'; lab.style.opacity = P(u, a + .2, a + .5); return }
      const h = w.pts * sc * p, best = w.wk === o.best, hot = w.pts >= o.hot, col = best ? C.best : hot ? C.hot : C.bar; c.shadowColor = col; c.shadowBlur = hot ? 26 + 10 * Math.sin(u * 5 + i) : 12; c.fillStyle = col; c.fillRect(x, o.y - h, bwid, h); c.shadowBlur = 0;
      c.fillStyle = 'rgba(255,255,255,.3)'; c.fillRect(x, o.y - h, bwid, 8); c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(x + bwid - 10, o.y - h, 10, h);
      if (hot && p > .95) for (let k = 0; k < 6; k++) { const life = ((u * 1.4 + k * .17 + i * .31) % 1); c.globalAlpha = 1 - life; c.fillStyle = k % 2 ? C.hot : '#ff6a3d'; c.fillRect(x + ((k * 29 + i * 13) % bwid), o.y - h - life * 70, 8, 8) } c.globalAlpha = 1;
      lab.style.top = (o.y - w.pts * sc - 40) + 'px'; lab.style.opacity = P(u, a + .5, a + .8) });
    const end = o.start + n * o.step; const ap = K8.sine(P(u, end + .4, end + 1.1)), ay = o.y - o.avg * sc; if (ap > 0) { c.fillStyle = C.text; for (let x = o.x0; x < o.x0 + (o.x1 - o.x0) * ap; x += 28) c.fillRect(x, ay, 16, 4); c.font = '16px PS2P'; c.textAlign = 'left'; c.globalAlpha = P(u, end + .9, end + 1.2); c.fillText('AVG ' + o.avg.toFixed(1), o.x0 + 6, ay - 14); c.globalAlpha = 1 }
    const bi = W.findIndex(w => w.wk === o.best), bx = o.x0 + bi * bw + bw / 2, cp = K8.spr(P(u, end + 1.4, end + 2.1)); if (bi >= 0 && cp > 0) { const by = o.y - W[bi].pts * sc - 80; c.save(); c.translate(bx, by); c.scale(cp, cp); c.fillStyle = C.best; c.fillRect(-24, 0, 48, 14); c.fillRect(-24, -14, 8, 14); c.fillRect(-4, -20, 8, 20); c.fillRect(16, -14, 8, 14); c.restore();
      if (o.crownLabel) { c.globalAlpha = P(u, end + 1.7, end + 2.0); c.fillStyle = C.best; c.font = '16px PS2P'; c.textAlign = 'right'; c.fillText(o.crownLabel, bx + 20, by - 34); c.globalAlpha = 1 } } };
  /** stacked breakdown bar (e.g. how fantasy points were scored). parts=[[label,value],...] */
  K8.stackBar = (c, o) => { let acc = 0; const tot = o.parts.reduce((s, p) => s + p[1], 0);
    o.parts.forEach((p, i) => { const a = o.start + i * o.step, f = K8.sine(P(o.u, a, a + .5)), w = o.w * p[1] / tot; if (f > 0) { c.shadowColor = o.cols[i]; c.shadowBlur = 14; c.fillStyle = o.cols[i]; c.fillRect(o.x + o.w * acc / tot, o.y, w * f, o.h); c.shadowBlur = 0; c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(o.x + o.w * acc / tot + w * f - 6, o.y, 6, o.h) } acc += p[1] });
    c.strokeStyle = '#000'; c.lineWidth = 6; c.strokeRect(o.x, o.y, o.w, o.h) };
  /** segmented power bar markup: n blocks, `on` lit with class */
  K8.pbar = (n, on, cls = 'on') => '<span class="pbar">' + [...Array(n)].map((_, i) => `<b data-on="${i < on ? cls : ''}"></b>`).join('') + '</span>';

  // ---------- transitions ----------
  /** diagonal slash wipe across each cut time (fx canvas above the stage) */
  K8.slashWipe = (c, t, cuts, cols = ['#ff8a1f', '#bf362b', '#6b161b', '#000'], half = .25) => { const W = c.canvas.width, H = c.canvas.height; c.clearRect(0, 0, W, H);
    for (const T of cuts) { const d = t - T; if (d > -half && d < half) { const p = (d + half) / (2 * half); cols.forEach((col, i) => { c.fillStyle = col; c.save(); c.translate(W / 2, H / 2); c.rotate(-.5); c.fillRect(-2400 + 4800 * K8.io(cl(p * 1.15 - i * .06)) - 200, -1600, 170 + i * 40, 3200); c.restore() }) } } };
  /** fade the whole page to black over the last `d` seconds */
  K8.fadeOut = (t, end, d = .5) => { document.body.style.filter = t > end - d ? `brightness(${1 - P(t, end - d, end)})` : 'none' };
  window.K8 = K8;
})();
