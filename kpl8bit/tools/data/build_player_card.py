"""Build data.json for templates/player-card from ESPN weekly league files (tools/data/fetch_weeks.sh).
usage: python3 -I build_player_card.py RAWDIR PLAYER_ID WEEK OUT.json [--theme feast] [--sprite assets/players/<id>_hero.png] [--copy copy.json]
Every number on screen comes from here; nothing is typed in by hand. Re-run after games finish to refresh."""
import argparse, datetime, json
ap = argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('pid', type=int); ap.add_argument('week', type=int); ap.add_argument('out')
ap.add_argument('--theme', default='feast'); ap.add_argument('--copy', default=None, help='JSON of wording overrides, deep-merged last (numbers stay from ESPN)'); ap.add_argument('--sprite', default=None); ap.add_argument('--season', default=2026, type=int)
a = ap.parse_args()
LOGO = {1: 'c', 2: 's', 3: 'k', 4: 'm', 5: 't', 6: 'h', 7: 'b', 8: 'u', 9: 'e', 10: 'w', 11: 'r', 12: 'v'}
POS = {1: 'QB', 2: 'RB', 3: 'WR', 4: 'TE', 5: 'K', 16: 'D/ST'}
NFL = {1:'ATL',2:'BUF',3:'CHI',4:'CIN',5:'CLE',6:'DAL',7:'DEN',8:'DET',9:'GB',10:'TEN',11:'IND',12:'KC',13:'LV',14:'LAR',15:'MIA',16:'MIN',17:'NE',18:'NO',19:'NYG',20:'NYJ',21:'PHI',22:'ARI',23:'PIT',24:'LAC',25:'SF',26:'SEA',27:'TB',28:'WSH',29:'CAR',30:'JAX',33:'BAL',34:'HOU'}
BENCH = (20, 21)
weeks, started, info, teamNames, teamRec, mu = [], {}, {}, {}, {}, None
for w in range(1, a.week + 1):
    d = json.load(open(f'{a.raw}/wk{w}.json'))
    for t in d.get('teams', []):
        teamNames[t['id']] = t['name'].strip()
        r = t.get('record', {}).get('overall'); teamRec[t['id']] = f"{r['wins']}-{r['losses']}" if r else ''
    for m in d['schedule']:
        if m['matchupPeriodId'] != w or 'away' not in m: continue
        sides = {}
        for s in ('home', 'away'):
            side = m[s]; tot = 0; roster = []
            for e in (side.get('rosterForCurrentScoringPeriod') or {}).get('entries', []):
                pe = e['playerPoolEntry']; p = pe['player']; pts = round(pe.get('appliedStatTotal', 0), 2)
                info[e['playerId']] = (p['fullName'], POS.get(p.get('defaultPositionId'), '?'), NFL.get(p.get('proTeamId'), ''))
                if e['lineupSlotId'] not in BENCH: tot += pts; started[e['playerId']] = started.get(e['playerId'], 0) + pts; roster.append((pts, e['playerId']))
                if e['playerId'] == a.pid:
                    st = {x.get('statSourceId'): x for x in p['stats'] if x.get('scoringPeriodId') == w and x.get('statSplitTypeId') == 1}
                    act = st.get(0, {}).get('stats', {}); proj = st.get(1, {}).get('appliedTotal')
                    weeks.append(dict(wk=w, team=side['teamId'], pts=pts, proj=proj, played=bool(act), car=act.get('23', 0), ryd=act.get('24', 0), rtd=act.get('25', 0),
                                      rec=act.get('53', 0), cyd=act.get('42', 0), ctd=act.get('43', 0), pyd=act.get('3', 0), ptd=act.get('4', 0), pint=act.get('20', 0)))
            sides[side['teamId']] = (round(tot, 2), sorted(roster, reverse=True))
        if w == a.week and any(e['playerId'] == a.pid for s in ('home', 'away') for e in (m[s].get('rosterForCurrentScoringPeriod') or {}).get('entries', [])):
            mu = sides
W = [x for x in weeks if x['wk'] == a.week][0]; mine = W['team']; opp = [k for k in mu if k != mine][0]
name, pos, nfl = info[a.pid]
g = [x for x in weeks if x['played']]; season_pts = round(sum(x['pts'] for x in g), 1); avg = round(season_pts / len(g), 1)
best = max(g, key=lambda x: x['pts']); rank = sorted(started.items(), key=lambda x: -x[1]); lrank = [i for i, x in enumerate(rank) if x[0] == a.pid][0] + 1
# scoring breakdown with KPL rules (from league settings): yardage 0.1, TD 6 (pass 4), rec 1, rush/rec 100/200-yd bonuses
parts = []
if W['ryd']: parts.append(['RUSH YDS', round(W['ryd'] * .1, 1)])
if W['rtd']: parts.append(['RUSH TD', W['rtd'] * 6])
if W['ryd'] >= 200: parts.append(['200-YD RUSH BONUS', 7])
elif W['ryd'] >= 100: parts.append(['100-YD RUSH BONUS', 3])
if W['rec']: parts.append(['RECEPTIONS', W['rec']])
if W['cyd']: parts.append(['REC YDS', round(W['cyd'] * .1, 1)])
if W['ctd']: parts.append(['REC TD', W['ctd'] * 6])
if W['cyd'] >= 200: parts.append(['200-YD REC BONUS', 7])
elif W['cyd'] >= 100: parts.append(['100-YD REC BONUS', 3])
calc = round(sum(p[1] for p in parts), 2)
if abs(calc - W['pts']) > .05: print(f'WARNING breakdown {calc} != ESPN {W["pts"]} (passing/fumbles/2-pt not modelled): check before publishing')
proj = W['proj'] or 0; hi = best['wk'] == a.week
lead = mu[mine][0] - mu[opp][0]; tag = lambda tid: {6: 'HOH', 3: 'DAWGS'}.get(tid, teamNames[tid].split()[-1].upper())
opp_top = [(info[pid][0].upper(), f"{info[pid][2]} · {teamNames[opp].upper()}", p) for p, pid in mu[opp][1][:2]]
asof = datetime.datetime.now(datetime.timezone.utc)
out = dict(theme=a.theme, background='haunted' if a.theme in ('feast', 'hoh') else 'kpl', bug=f'WEEK {a.week}',
  player=dict(name=name.upper(), pos=pos, nfl=nfl, kplLogo=LOGO[mine], sprite=a.sprite or f'assets/players/{a.pid}_hero.png'),
  open=dict(logo=LOGO[mine], lines=[f'WEEK {a.week} STAT CARD', teamNames[mine].upper().rsplit(' ', 1)[0] if len(teamNames[mine]) > 12 else teamNames[mine].upper(), teamNames[mine].upper().rsplit(' ', 1)[1] if len(teamNames[mine]) > 12 else '']),
  card=dict(header=f'KPL · WEEK {a.week}', sub=f'{pos} · {nfl} · {teamNames[mine].upper()}', ghost=f'W{a.week}', total=W['pts'], totalLabel=f'FANTASY PTS · WEEK {a.week}',
    chips=[[f"{'+' if W['pts']>=proj else ''}{W['pts']-proj:.1f}", 'VS HIS<br>PROJECTION'], [f"{W['pts']/proj:.1f}X" if proj else '-', f'PROJECTED<br>{proj:.1f}'], ['HIGH' if hi else f'#{lrank}', 'SEASON-BEST<br>KPL GAME' if hi else 'IN KPL<br>LINEUP PTS']],
    foot=f"{teamNames[mine].upper()} · {teamRec.get(mine,'')}", spriteScale=9),
  box=dict(kicker=f'WEEK {a.week} BOX SCORE', title='ON THE MENU' if a.theme == 'feast' else 'THE BOX SCORE', partsTitle=f"HOW HE SCORED {W['pts']:.1f}",
    stats=[[W['car'], 'CARRIES'], [W['ryd'], 'RUSH YDS'], [W['rtd'], 'RUSH TD'], [round(W['ryd'] / W['car'], 1) if W['car'] else 0, 'YDS/CARRY', 1], [W['rec'], 'CATCHES'], [W['cyd'], 'REC YDS']], parts=parts),
  partCols=['#f2a52b', '#ff8a1f', '#e0202a', '#efe2d0', '#c6b0a3', '#ffd27a', '#bf362b'],
  season=dict(kicker=f'FANTASY POINTS BY WEEK · {a.season}', title='SEASON SO FAR', weeks=[dict(wk=x['wk'], pts=x['pts'], played=x['played']) for x in weeks], best=best['wk'], avg=avg,
    crownLabel='SEASON HIGH', note=f'<span class="t-accent">{season_pts}</span> PTS · <span class="t-accent">#{lrank}</span> IN KPL LINEUP PTS · <span class="t-accent">{len(g)}</span> GAMES'),
  matchup=dict(kicker=f'KPL WEEK {a.week}', title=f"{tag(mine) if lead >= 0 else tag(opp)} {'LEADS' if True else ''} BY {abs(lead):.1f}",
    a=dict(name=teamNames[mine].upper(), logo=LOGO[mine], score=mu[mine][0]), b=dict(name=teamNames[opp].upper(), logo=LOGO[opp], score=mu[opp][0]), rowsTitle='TOP SCORERS',
    rows=[[name.upper(), f'{nfl} · {teamNames[mine].upper()}', W['pts'], '#f2a52b']] + [[n, s, p, '#c6b0a3'] for n, s, p in opp_top],
    foot=f"SCORES AS OF {asof.strftime('%b %d %H:%M UTC').upper()}"),
  outro=dict(title='GOBBLE GOBBLE' if a.theme == 'feast' else 'KPL HQ', line=f"<span class='t-accent'>{W['pts']:.1f}</span> IN WEEK {a.week} · <span class='t-accent'>{season_pts}</span> ON THE SEASON"),
  source=dict(espn_weeks=f'{a.raw}', built=asof.isoformat()))
def merge(d, o):
    for k, v in o.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict): merge(d[k], v)
        else: d[k] = v
if a.copy: merge(out, json.load(open(a.copy)))
json.dump(out, open(a.out, 'w'), indent=1)
print(f"{name}: wk{a.week} {W['pts']} (proj {proj:.1f}) season {season_pts} rank #{lrank} | {teamNames[mine]} {mu[mine][0]} vs {teamNames[opp]} {mu[opp][0]}")
