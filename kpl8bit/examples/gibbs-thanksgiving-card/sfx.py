"""Sound effects (no music) synced to gibbs12.html. usage: python3 -I sfx_gibbs12.py data.json out.wav"""
import array, json, math, random, sys, wave
D = json.load(open(sys.argv[1])); SR, DUR = 44100, 24.6; N = int(SR * DUR); buf = [0.0] * N; rnd = random.Random(12)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
def tone(t0, dur, f0, vol, kind='sq', duty=.5, f1=None, decay=6.0, att=0.0, vib=0.0, vibf=9):
    s0, n = int(t0 * SR), int(dur * SR); ph = 0.0; f1 = f0 if f1 is None else f1
    for k in range(n):
        i = s0 + k
        if not 0 <= i < N: continue
        x = k / n; f = f0 * (f1 / f0) ** x
        if vib: f *= 1 + vib * math.sin(2 * math.pi * vibf * k / SR)
        ph = (ph + f / SR) % 1
        v = (1 if ph < duty else -1) if kind == 'sq' else (4 * abs(ph - .5) - 1) if kind == 'tri' else rnd.uniform(-1, 1)
        a = min(1, k / (att * SR)) if att else 1
        buf[i] += v * vol * a * math.exp(-decay * k / SR) * min(1, (n - k) / 300)
blip = lambda t, n, d=.05, v=.1: tone(t, d, hz(n), v, 'sq', .25, decay=14)
def kick(t, v=.6): tone(t, .18, 160, v, 'tri', f1=38, decay=12)
def crash(t, v=.2, d=.7): tone(t, d, 1, v, 'noise', decay=5)
def whoosh(t, v=.08, up=True): tone(t, .3, 220 if up else 1300, v, 'tri', f1=1300 if up else 220, decay=3); tone(t, .28, 1, v * .6, 'noise', decay=9)
def coin(t, v=.12): blip(t, 83, .06, v); blip(t + .06, 88, .3, v)
def gobble(t):
    for i, f in enumerate((520, 470, 420)): tone(t + i * .13, .12, f, .14, 'sq', .5, f1=f * .8, decay=4, vib=.25, vibf=34)
def ticks(t0, t1, n, base=72, rise=12, v=.04):
    for i in range(n):
        u = i / n; x = 1 - (1 - u) ** (1 / 3); blip(t0 + (t1 - t0) * x, base + int(rise * u), .03, v)
# A: badge slam, leaf burst, title slams, turkey
tone(0, .4, 900, .1, 'sq', .5, f1=140, decay=1); kick(.4, .7); crash(.42, .22, .6)
for i in range(22): blip(.3 + i * .022, 84 + (i % 5) * 3, .03, .045)
for t, n in ((.7, 72), (.95, 79)): kick(t); crash(t, .15, .4); blip(t, n, .08, .12)
blip(1.2, 84, .05, .08); gobble(1.4); whoosh(1.9, .1); whoosh(2.6, .08, False)
# B: holo card
T = 2.8; ticks(T + .6, T + 2.3, 28, 64, 22, .045); coin(T + 2.3, .14)
for i in range(3): kick(T + 1.5 + i * .15, .3); blip(T + 1.5 + i * .15, 76 + 3 * i, .06, .08)
for k in range(2):
    for q in range(7): blip(T + .55 + k * 3.1 + q * .07, 91 + (q % 3) * 4, .03, .03)
# C: box score + breakdown
T = 9.0; whoosh(T - .15, .09)
for i in range(6): a = T + .3 + i * .14; whoosh(a, .04); ticks(a + .1, a + 1.0, 8, 70 + i, 8, .025)
for i, p in enumerate(D['parts']): a = T + 2.0 + i * .35; tone(a, .45, 200 + 60 * i, .05, 'tri', f1=500 + 80 * i, decay=3); blip(a + .45, 76 + i * 3, .06, .08)
coin(T + 4.0)
# D: duel
T = 15.0; whoosh(T - .15, .09); whoosh(T + .1, .07); whoosh(T + .25, .07); kick(T + .6, .5)
ticks(T + .7, T + 1.8, 18, 64, 18, .035); coin(T + 1.9, .1)
for i in range(3): tone(T + 1.8 + i * .25, .9, 180, .05, 'tri', f1=420, decay=2)
# E: outro
T = 20.6; whoosh(T - .15, .1); tone(T + .5, .4, 900, .1, 'sq', .5, f1=160, decay=1); kick(T + .9, .6); crash(T + .9, .2); gobble(T + 1.0)
for i, n in enumerate((72, 76, 79, 84, 88)): blip(T + 1.4 + i * .1, n, .1, .11)
for i in range(int((DUR - .5) * SR), N): buf[i] *= 1 - (i - (DUR - .5) * SR) / (.5 * SR)
peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[2], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[2])
