"""8-bit gameday bed for the KPL promo, synced to its timeline (120 bpm, 1 bar = 2 s = 1 card).
usage: python3 chiptune.py out.wav"""
import array, math, random, sys, wave

SR, DUR = 44100, 20.0
N = int(SR * DUR)
buf = [0.0] * N
random.seed(11)
MUSIC = '--sfx-only' not in sys.argv

def hz(n):  # midi note -> Hz
    return 440 * 2 ** ((n - 69) / 12)

def add(t0, dur, freq, vol, kind='sq', duty=.5, slide=0.0, decay=6.0):
    s0, s1 = int(t0 * SR), min(N, int((t0 + dur) * SR))
    ph = 0.0
    for i in range(s0, s1):
        x = (i - s0) / SR
        f = freq * (1 + slide * x / dur)
        ph = (ph + f / SR) % 1
        if kind == 'sq': v = 1 if ph < duty else -1
        elif kind == 'tri': v = 4 * abs(ph - .5) - 1
        else: v = random.uniform(-1, 1)
        env = math.exp(-decay * x) * min(1, (s1 - i) / 200)
        buf[i] += v * vol * env

def kick(t): add(t, .14, 150, .55, 'tri', slide=-.75, decay=18)
def snare(t): add(t, .12, 0, .22, 'noise', decay=22)
def hat(t, v=.07): add(t, .04, 0, v, 'noise', decay=60)
def blip(t, n, d=.08, v=.16): add(t, d, hz(n), v, 'sq', .25, decay=10)

C, Am, F, G = (48, [60, 64, 67]), (45, [57, 60, 64]), (41, [53, 57, 60]), (43, [55, 59, 62])
prog = [C, Am, F, G, C, G]

# Intro 0-2.5: rising fanfare, crash on the logo landing, hold, pickup
for i, n in enumerate([60, 64, 67, 72, 76, 79]):
    blip(i * .1, n, .1, .14)
add(.6, .9, 0, .25, 'noise', decay=4)
kick(.6)
for i, n in enumerate([72, 76, 79, 84]):
    add(.7 + i * .15, .15, hz(n), .12, 'sq', .5, decay=4)       # GAMEDAY letters
blip(1.35, 79, .12, .14)                                       # WEEK 11 appears
if MUSIC: add(1.35, .9, hz(67), .14, 'sq', .5, decay=2); add(1.35, .9, hz(43), .2, 'tri', decay=1.5)
for i in range(4): blip(1.8 + i * .25, 84, .06, .08)            # PRESS START blink
if MUSIC:
    for i in range(4): snare(2.0 + i * .125)                        # drum fill into the groove

# Cards 2.5-14.5: one bar per matchup
melody = [0, 2, 4, 2, 7, 4, 2, 0]
for b, (root, ch) in enumerate(prog):
    t0 = 2.5 + 2 * b
    add(t0, .18, hz(88), .12, 'sq', .5, slide=.3, decay=8)      # swoosh-in blip
    add(t0 + .5, .25, 0, .18, 'noise', decay=10)                # VS punch
    for beat in range(4 if MUSIC else 0):
        tb = t0 + beat * .5
        (kick if beat % 2 == 0 else snare)(tb)
        hat(tb + .25)
        for e in range(2):
            add(tb + e * .25, .23, hz(root + (12 if e else 0)), .22, 'tri', decay=3)
    for s in range(8 if MUSIC else 0):                          # arpeggio
        add(t0 + s * .25, .2, hz(ch[s % 3] + 12), .07, 'sq', .125, decay=7)
    for s, d in enumerate(melody if MUSIC else []):            # lead
        note = ch[0] + 12 + [0, 2, 4, 5, 7, 9, 11, 12][d % 8] - (ch[0] - root - 12)
        add(t0 + s * .25, .22, hz(ch[0] + 12 + [0, 2, 4, 5, 7, 9, 11, 12][d]), .09, 'sq', .5, decay=4)
    for i in range(12): blip(t0 + .8 + i * .042, 72 + (i * 2) % 12, .03, .05)  # win-bar fill ticks

# Board 14.5-18.5: double-time hats, row whooshes
for b, (root, ch) in enumerate([F, G] if MUSIC else []):
    t0 = 14.5 + 2 * b
    for beat in range(4):
        tb = t0 + beat * .5
        (kick if beat % 2 == 0 else snare)(tb)
        for h in range(4): hat(tb + h * .125, .05)
        add(tb, .45, hz(root), .22, 'tri', decay=2)
    for s in range(16):
        add(t0 + s * .125, .11, hz(ch[s % 3] + 24), .06, 'sq', .25, decay=12)
for i in range(6): blip(14.65 + i * .18, 67 + i * 2, .1, .12)

# Outro 18.5-20: coin, final chord
blip(18.5, 83, .07, .16); blip(18.57, 88, .35, .16)
kick(18.5); add(18.5, .8, 0, .2, 'noise', decay=4)
if MUSIC:
    for n in [60, 64, 67, 72]:
        add(18.6, 1.4, hz(n), .08, 'sq', .5, decay=1.6)
    add(18.6, 1.4, hz(36), .25, 'tri', decay=1.2)

peak = max(abs(v) for v in buf) or 1
pcm = array.array('h', (int(v / peak * .89 * 32767) for v in buf for _ in (0, 1)))
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], 'music' if MUSIC else 'sfx only', DUR, 's')
