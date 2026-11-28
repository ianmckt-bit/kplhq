"""Rivalry Week head-to-head stats by ESPN team slot. usage: python3 -I rivalry_stats.py RIVALRY_DIR"""
import json, os, sys
D = sys.argv[1]
PAIRS = [(8, 1), (10, 9), (12, 7), (5, 4), (11, 2), (6, 3)]
games = [tuple(g) for g in json.load(open(f'{D}/flaim_2018_2021.json'))['games']]
for y in range(2022, 2027):
    s = json.load(open(f'{D}/raw/s{y}.json'))
    for m in s['schedule']:
        wk = m['matchupPeriodId']
        if wk > 12 or m.get('winner') in (None, 'UNDECIDED') or 'away' not in m: continue
        a, h = m['away'], m['home']; w = a['teamId'] if m['winner'] == 'AWAY' else h['teamId']
        if frozenset((a['teamId'], h['teamId'])) in [frozenset(p) for p in PAIRS]:
            games.append((y, wk, a['teamId'], round(a['totalPoints'], 2), h['teamId'], round(h['totalPoints'], 2), w))
cur = json.load(open(f'{D}/raw/s2026.json'))
name = {t['id']: t['name'].strip() for t in cur['teams']}
rec = {t['id']: f"{t['record']['overall']['wins']}-{t['record']['overall']['losses']}" for t in cur['teams']}
proj = {}
for m in cur['schedule']:
    if m['matchupPeriodId'] == 12:
        for s in ('home', 'away'): proj[m[s]['teamId']] = None
f = json.load(open(f'{D}/../tday/fantasy.json')) if os.path.exists(f'{D}/../tday/fantasy.json') else None
if f:
    for m in f['matchups']:
        for s in ('home', 'away'): proj[int(m[s]['teamId'])] = round(m[s]['totalProjectedPoints'], 1)
out = []
for A, Bt in PAIRS:
    g = sorted([x for x in games if {x[2], x[4]} == {A, Bt}], key=lambda x: (x[0], x[1]))
    rows = []
    for (y, wk, t1, p1, t2, p2, w) in g:
        pa, pb = (p1, p2) if t1 == A else (p2, p1)
        rows.append(dict(y=y, wk=wk, a=pa, b=pb, w='A' if w == A else 'B', m=round(abs(pa - pb), 2)))
    wa = sum(r['w'] == 'A' for r in rows); wb = len(rows) - wa
    st, k = rows[-1]['w'], 0
    for r in reversed(rows):
        if r['w'] == st: k += 1
        else: break
    best = lambda s: max([r['m'] for r in rows if r['w'] == s], default=0)
    out.append(dict(A=A, B=Bt, nameA=name[A], nameB=name[Bt], recA=rec[A], recB=rec[Bt], wins=[wa, wb], streak=dict(team=st, n=k),
        avgA=round(sum(r['a'] for r in rows) / len(rows), 1), avgB=round(sum(r['b'] for r in rows) / len(rows), 1),
        bestA=round(best('A'), 1), bestB=round(best('B'), 1), last=rows[-1], projA=proj.get(A), projB=proj.get(Bt), games=rows))
json.dump(out, open(f'{D}/rivalry.json', 'w'), indent=1)
for r in out:
    s = r['streak']; who = r['nameA'] if s['team'] == 'A' else r['nameB']
    print(f"{r['nameA']} vs {r['nameB']}: {r['wins'][0]}-{r['wins'][1]} | {who} x{s['n']} | avg {r['avgA']}/{r['avgB']} | best +{r['bestA']}/+{r['bestB']} | last {r['last']['y']} W{r['last']['wk']} {r['last']['a']}-{r['last']['b']} | proj {r['projA']}/{r['projB']} | rec {r['recA']}/{r['recB']}")
    print('   ', ' '.join(f"'{x['y']%100:02d}{x['w']}({x['m']:.0f})" for x in r['games']))
