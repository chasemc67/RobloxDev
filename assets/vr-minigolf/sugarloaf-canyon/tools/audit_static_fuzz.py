#!/usr/bin/env python3
"""Audit ALL terminal outcomes of existing valid-felt fuzz sampling, including timeouts.
Unlike fuzz_escapes, retains every failure and reproducible shot input. No physics changes.
"""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import sim as S
import rest_audit


def audit(hole,n,seed):
    captured={}
    original=S.fuzz_batch
    def recording(*args):
        outcomes,ends,pins=rest_audit.audit_batch(*args)
        captured['outcomes']=outcomes
        captured['ends']=ends
        captured['pins']=pins
        captured['inputs']=args[-6:]
        return outcomes,ends
    S.fuzz_batch=recording
    try:
        S.fuzz_escapes(S.HoleArrays(hole),n=n,seed=seed)
    finally:
        S.fuzz_batch=original
    outcomes=captured['outcomes'];ends=captured['ends'];xs,zs,ys,aims,vs,times=captured['inputs']
    pins=captured['pins']
    excluded=np.zeros(n,dtype=bool)
    exclusion=hole.get('rest_exclusion')
    if exclusion:
        cx,_,cz=exclusion['center']
        excluded=(outcomes==0)&(np.hypot(ends[:,0]-cx,ends[:,2]-cz)<exclusion['radius'])
    failures=[]
    for i in np.flatnonzero((outcomes==3)|(outcomes==4)|(pins>0)|excluded):
        failures.append(dict(index=int(i),outcome=int(outcomes[i]),pinned=bool(pins[i]),excluded_rest=bool(excluded[i]),start=[float(xs[i]),float(ys[i]),float(zs[i])],aim_deg=math.degrees(float(aims[i])),speed=float(vs[i]),t0=float(times[i]),end=ends[i].tolist()))
    return dict(hole=hole['number'],n=n,seed=seed,counts={str(k):int(np.sum(outcomes==k)) for k in range(6)},escapes=int(np.sum(outcomes==3)),timeouts=int(np.sum(outcomes==4)),pinned_rests=int(np.sum(pins)),excluded_rests=int(np.sum(excluded)),failures=failures)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--json',default='holes.json');ap.add_argument('--holes',type=int,nargs='*');ap.add_argument('--n',type=int,default=100000);ap.add_argument('--seed',type=int,default=3);ap.add_argument('--out',default='_work/p7-static-fuzz.json');a=ap.parse_args()
    source=Path(a.json);course=json.loads(source.read_text());out=dict(n_per_hole=a.n,seed=a.seed,physics=S.PHYS,geometry_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sim_sha256=hashlib.sha256(Path(S.__file__).read_bytes()).hexdigest(),outcome_codes={'0':'rest','1':'holed','2':'hazard','3':'escape','4':'timeout','5':'respawn'},holes=[])
    for hole in course['holes']:
        if (a.holes is not None and hole['number'] not in a.holes) or (a.holes is None and hole.get('moving_parts')):continue
        row=audit(hole,a.n,a.seed);out['holes'].append(row);Path(a.out).write_text(json.dumps(out,indent=2));print(f"H{hole['number']}: {a.n} shots; escapes={row['escapes']} timeouts={row['timeouts']} pins={row['pinned_rests']} excluded_rests={row['excluded_rests']}",flush=True)
    out['totals']={key:sum(h[key] for h in out['holes']) for key in ('n','escapes','timeouts','pinned_rests','excluded_rests')}
    out['completed_sim_sha256']=hashlib.sha256(Path(S.__file__).read_bytes()).hexdigest()
    out['completed_geometry_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    out['sources_unchanged']=(out['sim_sha256']==out['completed_sim_sha256'] and out['geometry_sha256']==out['completed_geometry_sha256'])
    Path(a.out).write_text(json.dumps(out,indent=2))

if __name__=='__main__':main()
