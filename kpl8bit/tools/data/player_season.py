"""KPL season card data for one player from ESPN weekly league files. usage: python3 -I player_season.py RAWDIR PLAYER_ID OUT.json"""
import json, sys
R, PID, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
POS = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'D/ST'}
started, weeks, teamPts, info = {}, [], {}, {}
for w in range(1, 13):
    d = json.load(open(f'{R}/wk{w}.json'))
    for m in d['schedule']:
        if m['matchupPeriodId'] != w: continue
        for s in ('home', 'away'):
            side = m.get(s, {}); tid = side.get('teamId')
            for e in (side.get('rosterForCurrentScoringPeriod') or {}).get('entries', []):
                pe = e['playerPoolEntry']; p = pe['player']; pts = round(pe.get('appliedStatTotal', 0), 2)
                info[e['playerId']] = (p['fullName'], POS.get(p.get('defaultPositionId'), '?'))
                if e['lineupSlotId'] not in (20, 21):
                    started[e['playerId']] = started.get(e['playerId'], 0) + pts; teamPts[(tid, w)] = teamPts.get((tid, w), 0) + pts
                if e['playerId'] == PID:
                    stats = {}
                    for st in p['stats']:
                        if st.get('scoringPeriodId') == w and st.get('statSourceId') == 0 and st.get('statSplitTypeId') == 1: stats = st['stats']
                    weeks.append(dict(wk=w, team=tid, slot=e['lineupSlotId'], pts=pts, car=stats.get('23', 0), ryd=stats.get('24', 0), rtd=stats.get('25', 0),
                                      rec=stats.get('53', 0), tgt=stats.get('58', 0), cyd=stats.get('42', 0), ctd=stats.get('43', 0), played=bool(stats)))
rank = sorted(started.items(), key=lambda x: -x[1])
pos = info[PID][1]; posRank = [x for x in rank if info[x[0]][1] == pos]
hoh = weeks[0]['team']; teamTot = sum(v for (t, w), v in teamPts.items() if t == hoh)
mine = sum(x['pts'] for x in weeks if x['slot'] not in (20, 21))
g = [x for x in weeks if x['played']]
tot = lambda k: sum(x[k] for x in g)
out = dict(player=info[PID][0], pos=pos, weeks=weeks, games=len(g), fpts=round(sum(x['pts'] for x in g), 1), startedPts=round(mine, 1),
    avg=round(sum(x['pts'] for x in g) / len(g), 1), best=max(g, key=lambda x: x['pts']), over20=sum(x['pts'] >= 20 for x in g), over40=sum(x['pts'] >= 40 for x in g),
    car=tot('car'), ryd=tot('ryd'), rtd=tot('rtd'), rec=tot('rec'), tgt=tot('tgt'), cyd=tot('cyd'), ctd=tot('ctd'),
    leagueRank=[i for i, x in enumerate(rank) if x[0] == PID][0] + 1, posRank=[i for i, x in enumerate(posRank) if x[0] == PID][0] + 1,
    teamShare=round(100 * mine / teamTot, 1), teamTotal=round(teamTot, 1), next=[(info[x[0]][0], round(x[1], 1)) for x in rank[:5]])
json.dump(out, open(OUT, 'w'), indent=1)
print({k: v for k, v in out.items() if k != 'weeks'})
for x in weeks: print(x)
