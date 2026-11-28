"""8-bit sound effects (no music) for showcase8.html. usage: python3 sfx8.py out.wav"""
import array, math, random, sys, wave

SR, DUR = 44100, 31.6
N = int(SR * DUR); buf = [0.0] * N; rnd = random.Random(8)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def tone(t0, dur, f0, vol, kind='sq', duty=.5, f1=None, decay=6.0, vib=0.0):
    s0, n = int(t0 * SR), int(dur * SR); ph = 0.0; f1 = f0 if f1 is None else f1
    for k in range(n):
        i = s0 + k
        if not 0 <= i < N: continue
        x = k / n; f = f0 * (f1 / f0) ** x if f0 > 0 and f1 > 0 else f0
        if vib: f *= 1 + vib * math.sin(2 * math.pi * 9 * k / SR)
        ph = (ph + f / SR) % 1
        v = (1 if ph < duty else -1) if kind == 'sq' else (4 * abs(ph - .5) - 1) if kind == 'tri' else rnd.uniform(-1, 1)
        buf[i] += v * vol * math.exp(-decay * k / SR) * min(1, (n - k) / 150)

blip = lambda t, n, d=.06, v=.13: tone(t, d, hz(n), v, 'sq', .25, decay=12)
def crash(t, v=.25, d=.7): tone(t, d, 1, v, 'noise', decay=5)
def kick(t, v=.5): tone(t, .16, 160, v, 'tri', f1=40, decay=14)
def swoosh(t, up=True, v=.1): tone(t, .22, 300 if up else 1400, v, 'sq', .5, f1=1400 if up else 300, decay=4)
def ticks(t0, t1, n, base=72, rise=12, v=.06):
    for i in range(n):
        u = i / n; x = 1 - (1 - u) ** (1 / 3)
        blip(t0 + (t1 - t0) * x, base + int(rise * u), .03, v)
def arp(t, notes, step=.07, v=.13, d=.09):
    for i, n in enumerate(notes): blip(t + i * step, n, d, v)

# 1 intro
swoosh(0.0); arp(.3, [60, 67, 72], .06); kick(.6); tone(.6, .7, 200, .08, 'sq', .5, f1=900, decay=2)
blip(1.2, 76, .1, .14); blip(1.35, 79, .1, .14); crash(1.5, .18, .5); kick(1.5)
blip(1.8, 84, .05, .1); blip(2.05, 88, .05, .1)
# transitions
for t in (3.6, 9.0, 14.2, 20.6, 24.0, 28.6): swoosh(t - .04, True, .09)
# 2 game stats
ticks(3.9, 5.6, 26); kick(5.6); crash(5.6, .1, .3)
for i, t in enumerate((5.6, 5.8, 6.0)): blip(t, 72 + 4 * i, .08, .13)
arp(7.0, [72, 76, 79, 84, 88], .05, .12)                         # power-up on the badge
# 3 fantasy: one rising blip per ring block, coin on landing
for i in range(36): blip(9.3 + 2.0 * (i / 36), 60 + i // 2, .035, .06)
blip(11.3, 83, .07, .15); blip(11.37, 88, .3, .15); kick(11.3)
blip(11.2, 76, .06, .1); blip(11.3, 79, .06, .1); ticks(12.2, 13.1, 14, 79, 10, .05)
# 4 highlights
for i in range(7): blip(14.6 + i * .32, 67 + i * 2, .07, .11)
td = 14.2 + .4 + 6 * .32 + .35
tone(td - .7, .7, 150, .12, 'sq', .5, f1=1200, decay=0)          # riser into the TD
kick(td, .6); crash(td, .3, 1.0); arp(td + .05, [72, 76, 79, 84, 79, 84, 88], .08, .14, .12)
swoosh(td + 2.0, False, .1)
for i in (1, 2): blip(td - .35 + 2.6 + i * .35, 84 + 2 * i, .07, .11)
# 5 matchup
swoosh(20.7, True, .08); swoosh(20.85, True, .08); kick(21.2, .4); crash(21.2, .12, .4)
ticks(21.2, 22.1, 14, 70, 10, .05); ticks(22.0, 22.8, 12, 76, 8, .05)
# 6 postgame sip
tone(24.05, .45, 220, .08, 'sq', .5, f1=660, decay=2)               # frame rises
tone(24.5, .6, 180, .09, 'sq', .25, f1=520, decay=2)                # cup comes up
for i in range(8): blip(25.3 + i * .12, 64 + (i % 3) * 3, .05, .07)  # SLURRRRP typing
for k in range(14):                                                 # gurgling straw
    t = 25.35 + k * .145; tone(t, .12, rnd.choice((90, 110, 130)), .16, 'noise', decay=18)
    tone(t, .1, hz(48 + rnd.randrange(6)), .07, 'sq', .5, f1=hz(55), decay=10)
tone(27.5, .7, hz(76), .13, 'sq', .5, f1=hz(64), decay=1.5, vib=.03)  # AHHH
for i, t in enumerate((27.6, 27.8, 28.0, 28.2)): blip(t, 91 + (i % 2) * 5, .05, .06)
# 7 outro
blip(28.65, 83, .07, .15); blip(28.72, 88, .35, .15); kick(28.65)
for i, t in enumerate((28.8, 29.05, 29.3, 29.5)): blip(t, 72 + 3 * i, .05, .09)
arp(30.0, [79, 76, 72, 67, 60], .12, .12, .14); tone(30.6, .8, hz(48), .18, 'tri', decay=2)

for i in range(int(31.1 * SR), N): buf[i] *= 1 - (i - 31.1 * SR) / (.5 * SR)
peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1])
