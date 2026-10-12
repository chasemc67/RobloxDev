#!/usr/bin/env python3
"""Read historic H9 timing runs. No Studio access and no shots are fired."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RUNS = {'round4':'round4/blockrate','round5':'round5/blockrate-h9','round6':'round6/blockrate-h9',
        'stage-p':'stage-p/blockrate','stage-q':'stage-q/blockrate'}

def main():
    runs = {}
    for name, folder in RUNS.items():
        path = ROOT/'playtests'/folder/'results.json'
        d = json.loads(path.read_text())['blockrate']['default']['holes']['h9']
        errors = [round((r['seen']-r['phase']+d['period']/2)%d['period']-d['period']/2, 3) for r in d['rows']]
        runs[name] = dict(source=str(path.relative_to(ROOT)), **d,
                          phaseErrorMin=min(errors), phaseErrorMax=max(errors),
                          flags=sum(r['flags'] for r in d['rows']),
                          allRest=all(r['outcome']=='rest' for r in d['rows']))
    changes = []
    for old, new in zip(runs['round5']['rows'],runs['round6']['rows']):
        if old['blocked'] != new['blocked']:
            changes.append({'phase':old['phase'],'round5':old,'round6':new})
    def header(folder):
        return json.loads((ROOT/'playtests'/folder/'blockrate.jsonl').read_text().splitlines()[0])
    a,b=header(RUNS['round5']),header(RUNS['round6'])
    out = {'runs':runs,'round5To6BlockChanges':changes,
           'round5To6ConfigIdentical':a['config']==b['config'],
           'round5To6PhysicsIdentical':a['physics']==b['physics'],
           'newShotsFired':0}
    dest=ROOT/'playtests/stage-s/h9-historical-analysis.json'
    dest.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:{x:v[x] for x in ('shots','blocked','touched','lag','phaseErrorMin','phaseErrorMax','allRest','flags')} for k,v in runs.items()},indent=2))
    print('Changed blocked phases:', [r['phase'] for r in changes])
    print('Configuration identical:',out['round5To6ConfigIdentical'],'Physics identical:',out['round5To6PhysicsIdentical'])

if __name__=='__main__':main()
