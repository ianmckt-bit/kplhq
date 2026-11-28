"""Recompute KPL season graphics data (weeks 1..N) from ESPN league JSON. usage: python3 -I season_stats.py league.json out.json"""
import json, sys
d = json.load(open(sys.argv[1]))
name = {t['id']: t['name'].strip() for t in d['teams']}
games = [m for m in d['schedule'] if m.get('winner') not in (None, 'UNDECIDED') and m['matchupPeriodId'] <= 11]
W = max(m['matchupPeriodId'] for m in games)
rows = []
for m in games:
    a, h = m['away'], m['home']; wk = m['matchupPeriodId']
    rows.append(dict(wk=wk, a=a['teamId'], ap=round(a['totalPoints'], 2), h=h['teamId'], hp=round(h['totalPoints'], 2), winner=m['winner']))
scores = [(r['wk'], r['a'], r['ap']) for r in rows] + [(r['wk'], r['h'], r['hp']) for r in rows]
hi = max(scores, key=lambda x: x[2]); lo = sorted(scores, key=lambda x: x[2])
top4 = sorted(scores, key=lambda x: -x[2])[:4]
def res(r):
    win, los = (('a', 'h') if r['winner'] == 'AWAY' else ('h', 'a'))
    return dict(wk=r['wk'], w=r[win], wp=r[win + 'p'], l=r[los], lp=r[los + 'p'], margin=round(r[win + 'p'] - r[los + 'p'], 2))
R = [res(r) for r in rows]
close = min(R, key=lambda x: x['margin']); blow = max(R, key=lambda x: x['margin'])
tough = max(R, key=lambda x: x['lp']); lucky = min(R, key=lambda x: x['wp'])
# cumulative wins per team per week
cum = {t: [0] for t in name}
for wk in range(1, W + 1):
    for t in name: cum[t].append(cum[t][-1])
    for x in R:
        if x['wk'] == wk: cum[x['w']][-1] += 1
# all-play expected wins
exp = {t: 0.0 for t in name}
for wk in range(1, W + 1):
    wsc = [(t, p) for (w, t, p) in scores if w == wk]
    for t, p in wsc:
        others = [q for u, q in wsc if u != t]
        exp[t] += (sum(1 for q in others if p > q) + .5 * sum(1 for q in others if p == q)) / len(others)
wins = {t: cum[t][-1] for t in name}
luck = sorted([dict(team=name[t], w=wins[t], exp=round(exp[t], 1), luck=round(wins[t] - exp[t], 1)) for t in name], key=lambda x: -x['luck'])
draft = sorted([dict(team=name[t['id']], draft=t['draftDayProjectedRank'], now=t['currentProjectedRank']) for t in d['teams']], key=lambda x: x['draft'])
out = dict(throughWeek=W, highest=dict(team=name[hi[1]], pts=hi[2], wk=hi[0], top4=[(name[t], p, w) for w, t, p in top4]),
    lowest=[dict(team=name[t], pts=p, wk=w) for w, t, p in lo[:3]],
    closest=dict(w=name[close['w']], wp=close['wp'], l=name[close['l']], lp=close['lp'], margin=close['margin'], wk=close['wk']),
    blowout=dict(w=name[blow['w']], wp=blow['wp'], l=name[blow['l']], lp=blow['lp'], margin=blow['margin'], wk=blow['wk']),
    tough=dict(team=name[tough['l']], pts=tough['lp'], w=name[tough['w']], wp=tough['wp'], wk=tough['wk']),
    lucky=dict(team=name[lucky['w']], pts=lucky['wp'], l=name[lucky['l']], lp=lucky['lp'], wk=lucky['wk']),
    race={name[t]: cum[t] for t in name}, luck=luck, draft=draft)
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('race', 'luck', 'draft')}, indent=0))
for k, v in out['race'].items(): print('RACE', k, v)
for x in luck: print('LUCK', x)
for x in draft: print('DRAFT', x)
