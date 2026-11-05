"""Full-cycle <=.015-stud sweep. Triangle/OBB SAT; distances are conservative
separating-axis lower bounds, not exact Euclidean distances. No hidden exemptions.
Static-base comparisons use component AABBs conservatively; failures need review.
"""
import json,math,datetime
from pathlib import Path
import numpy as np
from registry_movers import REG,HOLES,motion
SRC=Path(__file__).resolve().parent
def sat(tri,c,s,yaw):
    a=math.radians(yaw);r=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    t=(tri-np.array(c))@r;half=np.array(s)/2
    edges=np.roll(t,-1,axis=1)-t
    axes=[np.broadcast_to(v,(len(t),3)) for v in np.eye(3)]
    axes.append(np.cross(edges[:,0],edges[:,1]))
    for j in range(3):
        for v in np.eye(3):axes.append(np.cross(edges[:,j],v))
    gap=np.full(len(t),-np.inf)
    for ax in axes:
        norm=np.linalg.norm(ax,axis=1);valid=norm>1e-9
        ax=ax/np.maximum(norm[:,None],1e-9)
        proj=np.einsum('nvi,ni->nv',t,ax);rad=np.abs(ax)@half
        g=np.maximum(proj.min(axis=1)-rad,-rad-proj.max(axis=1));g[~valid]=-np.inf
        gap=np.maximum(gap,g)
    idx=int(gap.argmin());return float(gap[idx]),tri[idx].mean(axis=0).tolist()
def transformed(e,t,tri,angle_override=None):
    d,tilt=motion(e['id'],t);v=tri.copy()
    if angle_override is not None:tilt=angle_override
    if 'lift' in e['id']:
        # North-edge hinge: Roblox -X rotation raises south edge.
        a=math.radians(tilt);z=v[:,:,2];y=v[:,:,1].copy()
        v[:,:,1]=y*math.cos(a)+z*math.sin(a)+d
        v[:,:,2]=-y*math.sin(a)+z*math.cos(a)
    elif e['moving']:v[:,:,0 if e['hole']==5 else 1]+=d
    return v+np.array(e['pivot']),d,tilt
def main():
    lines=['SRV-132 partial fitcheck: STRICT (no pocket/felt/rail exemptions)',
    'Triangle/OBB SAT signed separation lower bounds; negative = intersection, zero = contact.',
    'Full cycle dt<=0.005 s: translations <=0.015 stud; return tilt steps <=0.134 degree; top tilt separately swept <=0.25 degree.',
    'Felt represented as a 0.001-thick top surface. Bank slopes conservatively enclosed.',
    'Static bases use individual primitive AABBs (conservative for rounded/cylindrical details).']
    results={};cache={e['id']:np.array(json.loads((SRC/(e['id']+'_triangles.json')).read_text())) for e in REG}
    for e in REG:
        h=HOLES[e['hole']];obstacles=[]
        for w in h.get('walls',[])+h.get('rails',[]):obstacles.append((w['id'],w['center'],w['size'],w.get('yaw',0),'rail/wall'))
        for f in h['felt']:
            rise=(f.get('slope') or {}).get('rise',0)
            obstacles.append(('felt_'+f['id'],f['center'],[f['size'][0],max(.001,rise),f['size'][1]],f.get('yaw',0),'felt'))
        cup=h['cup'];obstacles.append(('cup',cup['position'],[cup['radius']*2,.001,cup['radius']*2],0,'cup'))
        obstacles.append(('tee',h['tee']['position'],[2,.001,2],0,'tee'))
        if e['moving']:
            for base in REG:
                if base['hole']==e['hole'] and not base['moving']:
                    comps=json.loads((SRC/(base['id']+'_components.json')).read_text())
                    for j,comp in enumerate(comps):
                        obstacles.append((base['id']+'_'+str(j),np.array(comp['center'])+base['pivot'],comp['size'],0,'base_primitive_AABB_conservative'))
        best={};period=7.866666666666667 if e['hole']==5 else 9.6
        times=np.linspace(0,period,math.ceil(period/.005)+1) if e['moving'] else [0]
        states=[(t,None) for t in times]
        if 'lift' in e['id']:states.extend((7.45,float(a)) for a in np.linspace(0,4,17))
        seen=set()
        for t,angle_override in states:
            tri,d,ang=transformed(e,t,cache[e['id']],angle_override);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1))
            key=(round(d,10),round(ang,10))
            if key in seen:continue
            seen.add(key)
            for name,c,s,yaw,kind in obstacles:
                # Cull obstacles too remote to improve the existing minimum.
                radius=np.linalg.norm(s)/2
                if np.linalg.norm(np.maximum(np.maximum(lo-np.array(c),np.array(c)-hi),0))-radius>best.get(kind,{}).get('clearance',float('inf')):continue
                g,loc=sat(tri,c,s,yaw)
                if g<best.get(kind,{}).get('clearance',float('inf')):
                    best[kind]=dict(clearance=g,obstacle=name,time=float(t),offset=d,tilt=ang,location=loc)
        results[e['id']]=best;lines.append('\n'+e['id'])
        for kind,b in best.items():lines.append(('FLAG' if b['clearance']<.05 else 'PASS')+' '+kind+' '+json.dumps(b))
        lines.append('Mesh budget PASS' if all(m['tris']<20000 for m in next(x for x in json.loads((SRC/'movers_manifest.json').read_text())['movers'] if x['id']==e['id'])['meshes']) else 'Mesh budget FAIL')
    lines.extend(['\nBlocker coverage: H6 exact source blocker union, length 7.000051 (rounding +0.000051 stud); face bands project 0.018 stud beyond source.',
    'H11 gate exact 3.6 x 1.2 x 0.5 source blocker covered; bands project 0.018 stud beyond source.',
    'Lift covers lock felt footprint except 0.005-stud plank seams. Lift is 0.15 thick below top, so flush rest intersects unchanged lock felt.',
    'TIMING FAIL: 2.0 s rise +1.5 s return >2.8 s fully closed gate dwell. No schedule satisfies all fixed constraints.',
    'ALL PASS: NO. Passing validation file intentionally not created. Final Cycles conditional step not authorized until ALL PASS.'])
    (SRC/'fitcheck_movers_pass1_failed.txt').write_text('\n'.join(lines));(SRC/'fitcheck_results.json').write_text(json.dumps(results,indent=2))
    with (SRC/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Full sweep complete: unresolved source geometry/timing conflicts; no passing certificate.\n')
    print('\n'.join(lines))
if __name__=='__main__':
    from fitcheck_pass2 import main as pass2_main
    pass2_main()
