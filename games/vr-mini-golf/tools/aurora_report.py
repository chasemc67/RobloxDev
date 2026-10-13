#!/usr/bin/env python3
"""Combine saved Aurora engine tests and geometry audits; never infer unrun tests passed."""
import hashlib
import json
import re
from pathlib import Path

OUT=Path('playtests/stage-ac2')

def read(path,default=None):
    return json.loads(path.read_text()) if path.exists() else default


def scenario(folder,n):
    p=OUT/folder/f'h{n}.jsonl'
    if p.exists():
        for line in reversed(p.read_text().splitlines()):
            item=json.loads(line)
            if item.get('type')=='result':return item['result']
    return {}


def main():
    rows=[];mover_holes={5,11,12,13,14,17}
    clearance=read(OUT/'spec-clearance.json',{'holes':[]})
    for n in range(1,19):
        phase='h1-spawn-recheck' if n==1 else 'cupdrop'
        cup=scenario(phase,n).get('cupdrop',{})
        sweep=scenario('h1-spawn-recheck' if n==1 else 'sweep',n);fuzz=sweep.get('fuzz',{});slow=sweep.get('slow',{})
        issues=sweep.get('issues',[])
        expected_slow=6 if n in mover_holes else 0
        complete=fuzz.get('shots')==8 and slow.get('shots')==expected_slow and not sweep.get('error')
        timeout=sum(x.get('timeouts',0) for x in [fuzz,slow])
        stuck=sum(x.get('stuck',0) for x in [fuzz,slow])
        escapes=sum(x.get('escapes',0) for x in [fuzz,slow])
        hazards=sum(x.get('hazards',0) for x in [fuzz,slow])
        rows.append({'hole':n,'name':sweep.get('name'),'cupdrop_sunk':cup.get('sunk'),'cupdrop_total':cup.get('n'),
                     'random_shots':fuzz.get('shots'),'slow_rollers':slow.get('shots'),'expected_slow':expected_slow,
                     'escapes':escapes if complete else None,'hazard_returns':hazards if complete else None,
                     'lost_balls':0 if complete and timeout==0 else None,
                     'timeouts':timeout,'stuck_shots':stuck if complete else None,
                     'stuck_flags':[v for v in issues if v['kind'] not in ['escape','unstuck','autoreset']],
                     'issues':issues,'complete':complete,'error':sweep.get('error'),
                     'cup_wall_clearance':next((h['cup_wall_clearance'] for h in clearance['holes'] if h['hole']==n),None)})
    console={}
    for phase in ['cupdrop','sweep','h1-spawn-recheck']:
        p=OUT/phase/'summary.md'
        txt=p.read_text() if p.exists() else ''
        console[phase]={side.lower():int(count) for side,count in re.findall(r'(Server|Client) warnings/errors: (\d+)',txt)}
    copies=read(OUT/'cloud-copies.json',{})
    local={}
    for name in ['aurora-test.rbxl','playtest-aurora-blockout.rbxl']:
        p=Path(name)
        if p.exists():local[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    result={'stage':'ac2','result':'PARTIAL','console':console,'cloud_copies':copies,'local_files':local,
            'cupdrop_sunk':sum(r['cupdrop_sunk'] or 0 for r in rows),'cupdrop_total':54,
            'sweep_complete':all(r['complete'] for r in rows),'escapes':sum(r['escapes'] or 0 for r in rows),
            'stuck_shots':sum(r['stuck_shots'] or 0 for r in rows),
            'lost_definition':'No unrecovered/missing ball observed when every requested shot completed without harness errors or timeouts. OOB returns are separately escapes/hazard_returns; unknown is null.',
            'static_movers':['H17 aurora_span: toggle unsupported; remains solid'],
            'limitations':['H2 cup-wall clearance 1.0 < 2.2 studs','H4 random shot forcedrest: wedged','H17 toggle remains static; timing not tested','Local mesh portability to another machine unverified'],
            'shutdown':read(OUT/'shutdown.json'),
            'geometry':read(OUT/'geometry-audit.json'),'spec_clearance':clearance,
            'mover_clearance':read(OUT/'mover-clearance.json'),'holes':rows}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['| Hole | Cupdrop | Random / slow | Escapes | Lost | Stuck shots | Reasons |','|---|---|---|---|---|---|---|']
    for r in rows:
        reasons=', '.join(sorted({v.get('reason',v['kind']) for v in r['stuck_flags']})) or '—'
        lines.append(f"| H{r['hole']:02d} | {r['cupdrop_sunk']}/{r['cupdrop_total']} | {r['random_shots']} / {r['slow_rollers']} | {r['escapes']} | {r['lost_balls']} | {r['stuck_shots']} | {reasons} |")
    (OUT/'per-hole.md').write_text('\n'.join(lines)+'\n')
    print('complete',result['sweep_complete'],'cup',result['cupdrop_sunk'],'escapes',result['escapes'],'stuck',result['stuck_shots'])

if __name__=='__main__':main()
