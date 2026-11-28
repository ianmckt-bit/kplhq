"""Build data.json for the KPL Thanksgiving promo from the site's /api/fantasy + /api/nfl and ESPN athlete overviews.
usage: python3 -I build_tday.py WORKDIR   (expects fantasy.json, nfl.json, espn/<id>.json; writes show/data.json)"""
import json, os, sys
os.chdir(sys.argv[1])
f=json.load(open('fantasy.json'));n=json.load(open('nfl.json'))
logos={'1':'c','2':'s','3':'k','4':'m','5':'t','6':'h','7':'b','8':'u','9':'e','10':'w','11':'r','12':'v'}
T={t['teamId']:t for t in f['teams']}
nm=lambda s:s.strip().upper()
def stat(pid,pos):
    d=json.load(open(f'espn/{pid}.json'));s=d['statistics'];rs=[x for x in s['splits'] if x['displayName']=='Regular Season'][0]['stats']
    L=list(zip(s['labels'],rs));g=lambda lab:[v for l,v in L if l==lab][0]
    if pos=='QB': return f"{g('YDS')} YDS · {g('TD')} TD · {g('INT')} INT"
    if pos=='RB': return f"{g('YDS')} RUSH YDS · {g('TD')} TD"
    if pos in('WR','TE'): return f"{g('REC')} REC · {g('YDS')} YDS · {g('TD')} TD"
    if pos=='K': return f"{g('FG')} FG · LONG {g('LNG')}"
    return ''
games=[]
for gid in ('401873081','401873080','401873082'):
    e=[e for e in n['events'] if e['id']==gid][0];c=e['competitions'][0]
    tm={x['homeAway']:x['team'] for x in c['competitors']}
    rec={x['homeAway']:(x.get('records') or [{}])[0].get('summary','') for x in c['competitors']}
    games.append(dict(id=gid,away=tm['away']['abbreviation'],home=tm['home']['abbreviation'],awayName=tm['away']['shortDisplayName'].upper(),homeName=tm['home']['shortDisplayName'].upper(),
      awayColor='#'+tm['away']['color'],awayAlt='#'+tm['away']['alternateColor'],homeColor='#'+tm['home']['color'],homeAlt='#'+tm['home']['alternateColor'],
      awayRec=rec['away'],homeRec=rec['home'],kick=c['status']['type']['shortDetail'].split(' - ')[-1].upper(),venue=c['venue']['fullName'].upper(),
      tv=', '.join(b['names'][0] for b in c.get('broadcasts',[])).upper(),players=[]))
gm={}
for g in games: gm[g['away']]=g; gm[g['home']]=g
matchups=[]
for m in f['matchups']:
    row=[]
    for side in ('home','away'):
        s=m[side];tid=s['teamId'];cnt=0
        for p in s['players']:
            if p['started'] and p['proTeam'] in gm:
                cnt+=1;dst=p['playerId'].startswith('-')
                gm[p['proTeam']]['players'].append(dict(id=p['playerId'],name=p['name'].upper(),pos=p['position'],nfl=p['proTeam'],kpl=nm(s['teamName']),logo=logos[tid],proj=round(p['projection'],1),stat='' if dst else stat(p['playerId'],p['position'])))
        row.append(dict(name=nm(s['teamName']),logo=logos[tid],score=s['score'],proj=round(s['totalProjectedPoints'],1),win=round(s['winProbability']*100),rec=f"{T[tid]['record']['wins']}-{T[tid]['record']['losses']}",tday=cnt))
    matchups.append(row)
for g in games: g['players'].sort(key=lambda p:-p['proj'])
allp=[p for g in games for p in g['players'] if not p['id'].startswith('-')]
top=sorted(allp,key=lambda p:-p['proj'])[:5]
for p in top: g=gm[p['nfl']];p['game']=f"{g['away']} @ {g['home']}"
def gl(pid):
    d=json.load(open(f'espn/{pid}.json'))['gameLog']['statistics'][0];ev=[e for e in d['events'] if e['eventId']=='401873079'][0]['stats'];return dict(zip(d['labels'],ev)),d['displayName']
wed=[]
for m in f['matchups']:
    for side in ('home','away'):
        s=m[side]
        for p in s['players']:
            if p['started'] and p['points']>0 and p['proTeam'] in('LAR','GB') and not p['playerId'].startswith('-'):
                L,kind=gl(p['playerId'])
                line=f"{L['CAR']} CAR · {L['YDS']} YDS · {L['TD']} TD" if kind=='Rushing' else (f"{L['REC']} REC · {L['YDS']} YDS · {L['TD']} TD" if kind=='Receiving' else '')
                wed.append(dict(id=p['playerId'],name=p['name'].upper(),pos=p['position'],nfl=p['proTeam'],kpl=nm(s['teamName']),logo=logos[s['teamId']],pts=p['points'],line=line))
wed.sort(key=lambda p:-p['pts'])
stand=[dict(rank=s['standing'],name=nm(s['teamName']),logo=logos[s['teamId']],rec=f"{s['record']['wins']}-{s['record']['losses']}",pf=round(s['record']['pointsFor'],1)) for s in f['standings']]
out=dict(week=f['matchupPeriod'],asof=f['meta']['fetchedAt'],games=games,top=top,wed=wed,matchups=matchups,standings=stand,
  nTday=sum(len(g['players']) for g in games),nTeamsWithTday=len({p['kpl'] for g in games for p in g['players']}))
json.dump(out,open('show/data.json','w'),indent=1)
print('starters',out['nTday'],'teams',out['nTeamsWithTday'])
for g in games: print(g['away'],'@',g['home'],g['kick'],g['tv'],g['awayRec'],g['homeRec'],len(g['players']))
for p in top: print('TOP',p['name'],p['proj'],p['kpl'],p['stat'])
for p in wed: print('WED',p['name'],p['pts'],p['kpl'],p['line'])
for r in matchups: print([(x['name'],x['score'],x['win'],x['tday']) for x in r])
