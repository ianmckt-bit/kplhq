"""Sound effects (no music) synced to gibbs.html. usage: python3 -I sfx_gibbs.py data.json out.wav"""
import array, json, math, random, sys, wave

D = json.load(open(sys.argv[1]))
SR, DUR = 44100, 31.6
N = int(SR * DUR); buf = [0.0] * N; rnd = random.Random(6)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def tone(t0, dur, f0, vol, kind='sq', duty=.5, f1=None, decay=6.0, att=0.0):
    s0, n = int(t0 * SR), int(dur * SR); ph = 0.0; f1 = f0 if f1 is None else f1
    for k in range(n):
        i = s0 + k
        if not 0 <= i < N: continue
        x = k / n; f = f0 * (f1 / f0) ** x
        ph = (ph + f / SR) % 1
        v = (1 if ph < duty else -1) if kind == 'sq' else (4 * abs(ph - .5) - 1) if kind == 'tri' else rnd.uniform(-1, 1)
        a = min(1, k / (att * SR)) if att else 1
        buf[i] += v * vol * a * math.exp(-decay * k / SR) * min(1, (n - k) / 300)

blip = lambda t, n, d=.05, v=.1: tone(t, d, hz(n), v, 'sq', .25, decay=14)
def kick(t, v=.6): tone(t, .18, 160, v, 'tri', f1=38, decay=12)
def crash(t, v=.2, d=.7): tone(t, d, 1, v, 'noise', decay=5)
def whoosh(t, v=.08, up=True): tone(t, .3, 220 if up else 1300, v, 'tri', f1=1300 if up else 220, decay=3); tone(t, .28, 1, v * .6, 'noise', decay=9)
def chime(t, n, v=.07): tone(t, .6, hz(n), v, 'tri', decay=4); tone(t, .4, hz(n + 12), v * .45, 'sq', .125, decay=8)
def ticks(t0, t1, n, base=72, rise=12, v=.04):
    for i in range(n):
        u = i / n; x = 1 - (1 - u) ** (1 / 3); blip(t0 + (t1 - t0) * x, base + int(rise * u), .03, v)

# A: haunted open
for n_ in (38, 45, 50, 53): tone(0, 2.8, hz(n_), .07, 'tri', decay=.6, att=.5)          # D minor organ swell
tone(.15, .4, 1200, .1, 'sq', .5, f1=150, decay=2); kick(.55, .8); crash(.55, .25, 1.0)
for i in range(22): blip(.6 + i * (.8 / 22), 70 + (i % 5) * 2, .03, .05)
chime(1.4, 74); whoosh(2.1, .1); whoosh(2.9, .08, False)
# B: holo card
T = 3.2
ticks(T + .6, T + 2.4, 30, 64, 20, .045); blip(T + 2.4, 83, .07, .14); blip(T + 2.47, 88, .3, .14)
for i in range(3): kick(T + 1.6 + i * .15, .3); blip(T + 1.6 + i * .15, 76 + 3 * i, .06, .08)
for k in range(2):
    for q in range(7): blip(T + .3 + k * 3.1 + .25 + q * .07, 91 + (q % 3) * 4, .03, .03)   # holo shine
# C: stats grid
T = 9.4; whoosh(T - .15, .09)
for i in range(8):
    a = T + .35 + i * .17 + (.5 if i >= 4 else 0); whoosh(a, .04); ticks(a + .1, a + 1.1, 8, 70 + i, 8, .025)
chime(T + 3.3, 79); chime(T + 3.4, 84)
# D: weekly chart
T = 15.4; whoosh(T - .15, .09)
for i, w in enumerate(D['weeks']):
    a = T + .6 + i * .17 + .25
    if not w['played']: blip(a, 55, .12, .06); continue
    r = w['pts'] / 60; tone(a, .16, 60 + 90 * r, .14 + .2 * r, 'tri', f1=40, decay=12)
    if w['pts'] >= 40:
        for q in range(10): tone(a + .1 + q * .05 + rnd.random() * .02, .03, 1, .04, 'noise', decay=60)
tone(T + 2.9, .7, 300, .05, 'tri', f1=600, decay=2)                                         # average line
for q, n_ in enumerate((72, 76, 79, 84)): blip(T + 3.9 + q * .09, n_, .1, .1)               # season-high crown
# E: Thanksgiving spotlight
T = 21.8; whoosh(T - .15, .09); kick(T + .1, .7); crash(T + .1, .2)
tone(T + .4, 4.2, 1, .07, 'noise', decay=.4, att=.4)                                         # fire roar
ticks(T + .9, T + 2.2, 24, 62, 24, .045); kick(T + 2.2, .5); blip(T + 2.2, 88, .3, .12)
for q in range(5): blip(T + 2.6 + q * .05, 72 + q * 4, .05, .09)
# F: outro
T = 27.2; whoosh(T - .15, .1); whoosh(T + .1, .07); kick(T + .5, .6); crash(T + .5, .15)
for q, n_ in enumerate((62, 65, 69, 74)): chime(T + .8 + q * .12, n_, .06)
tone(T + 1.4, 2.4, hz(38), .1, 'tri', decay=1)
for i in range(int((DUR - .5) * SR), N): buf[i] *= 1 - (i - (DUR - .5) * SR) / (.5 * SR)
peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[2])
