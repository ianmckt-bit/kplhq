"""Data-driven sound effects (no music) for rivalry.html. usage: python3 -I sfx_rivalry.py data.json out.wav
Timings mirror rivalry.html: intro 6.0 s, 8.4 s per match, 4.0 s outro."""
import array, json, math, random, sys, wave

D = json.load(open(sys.argv[1])); MS = D['matches']
SR = 44100; MD = 8.4; DUR = 6.0 + MD * len(MS) + 4.0
N = int(SR * DUR); buf = [0.0] * N; rnd = random.Random(12)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def tone(t0, dur, f0, vol, kind='sq', duty=.5, f1=None, decay=6.0):
    s0, n = int(t0 * SR), int(dur * SR); ph = 0.0; f1 = f0 if f1 is None else f1
    for k in range(n):
        i = s0 + k
        if not 0 <= i < N: continue
        x = k / n; f = f0 * (f1 / f0) ** x
        ph = (ph + f / SR) % 1
        v = (1 if ph < duty else -1) if kind == 'sq' else (4 * abs(ph - .5) - 1) if kind == 'tri' else rnd.uniform(-1, 1)
        buf[i] += v * vol * math.exp(-decay * k / SR) * min(1, (n - k) / 150)

blip = lambda t, n, d=.06, v=.1: tone(t, d, hz(n), v, 'sq', .25, decay=12)
def kick(t, v=.55): tone(t, .18, 160, v, 'tri', f1=38, decay=12)
def crash(t, v=.2, d=.7): tone(t, d, 1, v, 'noise', decay=5)
def whoosh(t, v=.08, up=True): tone(t, .3, 220 if up else 1200, v, 'tri', f1=1200 if up else 220, decay=3); tone(t, .3, 1, v * .6, 'noise', decay=9)
def chime(t, n, v=.07): tone(t, .6, hz(n), v, 'tri', decay=4); tone(t, .4, hz(n + 12), v * .45, 'sq', .125, decay=8)

# intro
tone(0, 1.2, 70, .12, 'tri', f1=140, decay=1)                   # sun rises
kick(.1); crash(.1, .12); kick(.3); chime(.35, 79)
for i in range(len(MS)): whoosh(1.2 + i * .14, .05)
for i, m in enumerate(MS):
    lead = m['wins'][0] - m['wins'][1]; blip(3.4 + i * .12, 76 if lead > 0 else 69 if lead < 0 else 72, .08, .08)
# matches
for i, m in enumerate(MS):
    s = 6.0 + i * MD; n = len(m['games'])
    whoosh(s - .2, .09)                                         # sunset wipe
    whoosh(s + .25, .07); whoosh(s + .35, .07); kick(s + .9, .45)
    bt = [1.3 + k * min(.24, 2.5 / n) for k in range(n)]
    for k, g in enumerate(m['games']):
        blip(s + bt[k], 79 if g['w'] == 'A' else 67, .07, .1); tone(s + bt[k], .05, 1, .05, 'noise', decay=40)
    end = s + bt[-1] + .45
    kick(end, .5); crash(end, .14, .5); blip(end + .02, 84, .1, .1)
    if m['streak']['n'] >= 3:                                   # embers crackle on long streaks
        for k in range(40): tone(end + .4 + k * .05 + rnd.random() * .03, .03, 1, .05 * (1 - k / 40), 'noise', decay=60)
    if m['wins'][0] == m['wins'][1]:                            # all square shimmer
        for k, nn in enumerate((72, 76, 79, 84)): chime(end + .3 + k * .08, nn, .05)
    whoosh(s + 3.9, .06); whoosh(s + 4.05, .06)
    for k in range(4):
        for q in range(8): blip(s + 4.3 + k * .12 + q * .11, 76 + q, .025, .025)
    mx = max(g['m'] for g in m['games'])
    big = max(range(n), key=lambda k: m['games'][k]['m']) if mx >= 60 else -1
    for k, g in enumerate(m['games']):
        t = s + 4.6 + k * .16 + .25; r = g['m'] / mx
        tone(t, .14, 60 + 60 * r, .12 + .25 * r, 'tri', f1=40, decay=14)
        if k == big: kick(t, .8); crash(t, .3, 1.0); tone(t, .5, 300, .1, 'sq', .5, f1=60, decay=4)
    cl = [k for k, g in enumerate(m['games']) if g['m'] < 3]
    if cl:                                                      # photo finish heartbeat
        k = min(cl, key=lambda k: m['games'][k]['m']); t = s + 4.6 + k * .16 + .5
        for b in range(3): kick(t + b * .55, .35); kick(t + b * .55 + .16, .25)
# outro
o = 6.0 + MD * len(MS)
whoosh(o - .2, .09); tone(o, 1.2, 70, .1, 'tri', f1=140, decay=1)
for k, nn in enumerate((72, 76, 79, 84, 88)): chime(o + .3 + k * .12, nn, .07)
kick(o + .3, .5)
for i in range(int((DUR - .5) * SR), N): buf[i] *= 1 - (i - (DUR - .5) * SR) / (.5 * SR)
peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[2], round(DUR, 1), 's')
