"""8-bit sound effects (no music) synced to tday.html. usage: python3 sfx_tday.py data.json out.wav"""
import array, json, math, random, sys, wave

D = json.load(open(sys.argv[1]))
SR, DUR = 44100, 68.4
N = int(SR * DUR); buf = [0.0] * N; rnd = random.Random(26)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def tone(t0, dur, f0, vol, kind='sq', duty=.5, f1=None, decay=6.0, vib=0.0, vibf=9):
    s0, n = int(t0 * SR), int(dur * SR); ph = 0.0; f1 = f0 if f1 is None else f1
    for k in range(n):
        i = s0 + k
        if not 0 <= i < N: continue
        x = k / n; f = f0 * (f1 / f0) ** x
        if vib: f *= 1 + vib * math.sin(2 * math.pi * vibf * k / SR)
        ph = (ph + f / SR) % 1
        v = (1 if ph < duty else -1) if kind == 'sq' else (4 * abs(ph - .5) - 1) if kind == 'tri' else rnd.uniform(-1, 1)
        buf[i] += v * vol * math.exp(-decay * k / SR) * min(1, (n - k) / 150)

blip = lambda t, n, d=.05, v=.12: tone(t, d, hz(n), v, 'sq', .25, decay=14)
def kick(t, v=.6): tone(t, .16, 170, v, 'tri', f1=40, decay=14)
def crash(t, v=.22, d=.6): tone(t, d, 1, v, 'noise', decay=6)
def slam(t, n=72): kick(t); crash(t); blip(t, n, .08, .14); blip(t + .05, n + 12, .1, .12)
def whoosh(t, v=.1): tone(t, .18, 260, v, 'sq', .5, f1=1800, decay=3); tone(t, .2, 1, v * .8, 'noise', decay=10)
def coin(t, v=.13): blip(t, 83, .06, v); blip(t + .06, 88, .25, v)
def gobble(t):
    for i, f in enumerate((520, 470, 420)):
        tone(t + i * .13, .12, f, .14, 'sq', .5, f1=f * .8, decay=4, vib=.25, vibf=34)
def ticks(t0, t1, n, base=72, rise=12, v=.05):
    for i in range(n):
        u = i / n; x = 1 - (1 - u) ** (1 / 3)
        blip(t0 + (t1 - t0) * x, base + int(rise * u), .03, v)

cuts = [2.6, 4.6, 9.0, 13.4, 17.4, 18.4, 25.4, 30.0, 36.6, 40.6, 19.8, 21.2, 22.6, 24.0, 41.5, 47.5, 53.0, 58.5, 64.0]
for c in cuts: whoosh(c - .14)
# A: cold open
tone(0, .4, 900, .1, 'sq', .5, f1=140, decay=1)            # badge slams in
kick(.4, .7); crash(.42, .22, .6)
for i in range(22): blip(.38 + i * .022, 84 + (i % 5) * 3, .03, .05)    # leaves burst into the wreath
slam(1.15, 72); slam(1.4, 79); blip(1.8, 84, .05, .1); gobble(2.0)
# B: number slams
for i, t in enumerate((2.6, 3.25, 3.9)): slam(t, 72 + 5 * i)
# C: three game blocks
for gi, t0 in enumerate((4.6, 9.0, 13.4)):
    kick(t0 + .3, .6); crash(t0 + .3, .15, .4); blip(t0 + .34, 79, .08, .12)      # VS slam
    for k in range(10): blip(t0 + .4 + k * .045, 88, .02, .04)                       # record pips
    tone(t0 + .55, .2, hz(84), .06, 'sq', .5, decay=8, vib=.02, vibf=30)            # scoreboard clock flickers on
    for k in range(len(D['games'][gi]['players'])):
        blip(t0 + .8 + k * .1, 67 + k * 2, .05, .09); ticks(t0 + .98 + k * .1, t0 + 1.3 + k * .1, 5, 79, 6, .03)
    coin(t0 + 1.9, .1)                                                               # TOP PROJ tag
# D: top-5 countdown
slam(17.4, 67)
for k in range(5):
    t = 18.4 + k * 1.4; slam(t, 64 + 3 * k)
    tone(t + .02, .28, 200, .07, 'sq', .5, f1=800, decay=3)
    ticks(t + .35, t + .8, 10, 72, 10, .05); coin(t + .8)
    for q in range(6): blip(t + .45 + q * .06, 91 + (q % 3) * 4, .04, .045)       # holo shine
# E: Wednesday scorers
for j in range(len(D['wed'])):
    t = 25.4 + .4 + j * .22; blip(t, 72 + 3 * j, .06, .1); ticks(t + .1, t + .8, 8, 76, 8, .04); coin(t + .8, .1)
# F: matchups
for j, m in enumerate(D['matchups']):
    t = 30.0 + .3 + j * .16; blip(t, 70 + 2 * j, .06, .1)
    if abs(m[0]['win'] - m[1]['win']) <= 2:                 # coin-flip matchup gets a flip
        for k in range(6): blip(t + .3 + k * .07, 84 if k % 2 else 91, .04, .08)
# G: standings cascade
for j in range(len(D['standings'])): blip(36.6 + .2 + j * .07, 60 + j * 2, .04, .08)
# K0 + mid-season report: softer, floatier sounds (triangle swells, chimes)
def swell(t, d, f0, f1, v=.07): tone(t, d, f0, v, 'tri', f1=f1, decay=1.2)
def chime(t, n, v=.07): tone(t, .5, hz(n), v, 'tri', decay=5); tone(t, .35, hz(n + 12), v * .5, 'sq', .125, decay=8)
slam(40.6, 67); slam(40.85, 74)
for i in range(6): a = 41.5 + .45 + i * .2; swell(a, .5, 180, 420, .05); chime(a + .4, 72 + (i % 3) * 4, .06)
for i in range(6): ticks(41.5 + .6 + i * .2, 41.5 + 1.75 + i * .2, 6, 76, 8, .025)
swell(47.5 + .5, 1.4, 110, 220, .05)
for k, n in enumerate((60, 64, 67, 72, 76, 79, 84)): chime(47.5 + 1.3 + k * .34, n, .05)
chime(47.5 + 2.6, 79, .07); chime(47.5 + 3.1, 76, .07); chime(47.5 + 3.9, 84, .08)
swell(53.0 + .7, .9, 140, 300, .05)
for k in range(4): swell(53.0 + 1.5 + k * .28, .9, 200, 700, .05); chime(53.0 + 2.5 + k * .28, 79 + k * 2, .07)
swell(58.5 + .3, .6, 120, 260, .05)
for i in range(12): a = 58.5 + .6 + i * .13; swell(a, .45, 160 + i * 12, 420 + i * 20, .035); chime(a + .35, 70 + (i % 4) * 3, .035)
chime(58.5 + 3.7, 84, .07); chime(58.5 + 3.8, 72, .07)
# H: outro (shifted to 64.0)
tone(64.0, .5, 900, .1, 'sq', .5, f1=160, decay=1); kick(64.4, .7); crash(64.4, .25, .8)
gobble(64.5); coin(65.1)
for i, n in enumerate((72, 76, 79, 84, 79, 84, 88)): blip(65.5 + i * .1, n, .1, .12)
tone(66.2, 1.2, hz(48), .2, 'tri', decay=1.5)

for i in range(int(67.9 * SR), N): buf[i] *= 1 - (i - 67.9 * SR) / (.5 * SR)
peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[2])
