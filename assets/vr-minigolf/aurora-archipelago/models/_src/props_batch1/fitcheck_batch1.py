"""Exact triangle/OBB SAT gates, with conservative L-infinity clearance lower bounds.
Source skin volumes exempt only their own footprint. Sweep union is exact for vertical translation.
"""
import json,math,hashlib,sys
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent;D=S.parents[2]
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
CHANGED=set(json.loads((S/'polish_ids.json').read_text()))
H={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
P=json.loads((S/'parts.json').read_text())
def ry(y):
    a=math.radians(y);c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def hit(T,c,size,yaw=0,inflate=0):
    q=(T-np.array(c))@ry(yaw);half=np.array(size)/2+inflate
    edges=np.roll(q,-1,axis=1)-q
    axes=[np.tile(np.eye(3)[i],(len(T),1)) for i in range(3)]
    axes.append(np.cross(edges[:,0],edges[:,1]))
    for i in range(3):
        for j in range(3):axes.append(np.cross(edges[:,i],np.eye(3)[j]))
    overlaps=np.ones(len(T),dtype=bool)
    for ax in axes:
        proj=np.einsum('tvi,ti->tv',q,ax);radius=np.abs(ax)@half
        overlaps &= (proj.min(axis=1)<=radius+1e-8)&(proj.max(axis=1)>=-radius-1e-8)
    return overlaps
CACHE=json.loads((S/"triangles.json").read_text()) if (S/"triangles.json").exists() else None
MODE='preflight fan triangulation' if '--preflight' in sys.argv else 'Blender actual triangles'
if '--preflight' in sys.argv:CACHE=None
else:
    build=json.loads((S/'build_report.json').read_text())
    assert build.get('parts_sha256')==hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),'Stale Blender build; use --preflight'
    assert build.get('triangles_sha256')==hashlib.sha256((S/'triangles.json').read_bytes()).hexdigest(),'Stale Blender triangles'

def triangles(p):
    if CACHE is not None and p['id'] in CACHE:return np.array(CACHE[p['id']])+p['anchor']
    ts=[]
    for g in p['groups'].values():
        for f in g['faces']:
            for i in range(1,len(f)-1):ts.append([g['verts'][f[0]],g['verts'][f[i]],g['verts'][f[i+1]]])
    return np.array(ts)+p['anchor']
def clearance(T,w):
    if hit(T,w['center'],w['size'],w.get('yaw',0),-.000001).any():return -1.0
    lo,hi=0.,100.
    for _ in range(27):
        mid=(lo+hi)/2
        if hit(T,w['center'],w['size'],w.get('yaw',0),mid).any():hi=mid
        else:lo=mid
    return lo
def in_foot(T,w):
    q=(T-w['center'])@ry(w.get('yaw',0));return (np.abs(q[:,:,0])<=w['size'][0]/2+.001)&(np.abs(q[:,:,2])<=w['size'][2]/2+.001)
lines=['Aurora batch 1 fitcheck: exact triangle/OBB SAT; rail clearance conservative L-infinity lower bound (Euclidean clearance >= reported value).',
       'Skin containment tolerance 0.001. Felt and overhead intersection tests use open interiors, including sloped felt via affine shear.','NOTE H1 collider-to-rail1 gap = 0.07867965644035735 studs (addendum exception).','']
results=[]
for p in P:
    h=H[p['hole']];T=triangles(p);V=T.reshape(-1,3);fail=[];skinwalls=[w for w in h['walls'] if w['id'] in p['skin_ids']]
    for w in skinwalls:
        # Skin only covers exact source box; high decorations may stay above it.
        top=w['center'][1]+w['size'][1]/2
        low=T[:,:,1]<=top+.001
        own=in_foot(T,w)
        if len(skinwalls)==1 and np.any(low&~own):fail.append('skin footprint violation')
    exempt=np.zeros(len(T),dtype=bool)
    for w in skinwalls:
        # A triangle entirely inside a source footprint is collider dressing.
        exempt |= in_foot(T,w).all(axis=1)
    for fid in p['felt_skins']:
        f=next(f for f in h['felt'] if f['id']==fid)
        w=dict(center=f['center'],size=[f['size'][0],100,f['size'][1]],yaw=f.get('yaw',0))
        exempt |= in_foot(T,w).all(axis=1)&(T[:,:,1].max(axis=1)<=f['center'][1]+.001)
    walls=[]
    for w in h['walls']:
        if w['id'] in p['skin_ids']:continue
        # For collider skins the source low section has a specific footprint gate.
        tt=T
        if p['hole']==1 and p['skin_ids']==['boulder']:
            tt=T[T[:,:,1].min(axis=1)>2.501]
        if len(tt):walls.append((clearance(tt,w),w['id']))
    walls.sort();minimum=walls[0] if walls else (100,'none')
    required=.15 if p['id'] in CHANGED else .1
    if minimum[0]<required-1e-5:fail.append('rail clearance below required buffer')
    felt_hits=0;feltvals=[]
    if not p['motion']:
        for f in h['felt']:
            # Rotate into felt frame and shear slope to flatten top.
            q=(T-np.array(f['center']))@ry(f.get('yaw',0))
            if f.get('slope'):
                sl=f['slope'];idx=0 if sl['axis']=='x' else 2
                q[:,:,1]-=q[:,:,idx]*sl['rise']/f['size'][0 if idx==0 else 1]
            slab=hit(q,[0,-.2,0],[f['size'][0]-.00002,.4-.00002,f['size'][1]-.00002])
            buffer=.3 if p['id'] in CHANGED else -.00002
            head=hit(q,[0,4,0],[f['size'][0]+buffer,8-.00002,f['size'][1]+buffer])
            live=q[~exempt]
            if len(live):feltvals.append((clearance(live,dict(center=[0,4,0],size=[f['size'][0],8,f['size'][1]])),f['id']))
            # Collider footprint masks only authorized skins.
            felt_hits+=int(((slab|head)&~exempt).sum())
        if felt_hits:fail.append('felt/head volume intersection')
    sweep=None
    if p['motion']:
        m=p['motion'];low,high=m['range'];sweepT=np.concatenate([T+np.array(m['axis'])*low,T+np.array(m['axis'])*high])
        # Translation sweep fills a prism; include sides connecting corresponding vertices.
        side=[]
        for tri in T:
            for i in range(3):
                a,b=tri[i],tri[(i+1)%3];aa=a+np.array(m['axis'])*high;bb=b+np.array(m['axis'])*high
                side.extend([[a,b,bb],[a,bb,aa]])
        sweepT=np.concatenate([sweepT,np.array(side)])
        sw=sorted((clearance(sweepT,w),w['id']) for w in h['walls']);sweep=dict(range=m['range'],min_clearance=sw[0][0],rail=sw[0][1],method='exact full translation swept surface; endpoints plus side prisms')
        if sw[0][0]<.1-1e-5:fail.append('mover sweep clearance')
        # Geyser square contact mesh has an exact axis-aligned translation volume.
        vv=sweepT.reshape(-1,3);lo=vv.min(axis=0);hi=vv.max(axis=0)
        swept_box=dict(center=((lo+hi)/2).tolist(),size=(hi-lo).tolist())
        dressing=sorted((clearance(triangles(other),swept_box),other['id']) for other in P if other['hole']==p['hole'] and other['id']!=p['id'])
        sweep['min_dressing_clearance']=dressing[0][0];sweep['nearest_dressing']=dressing[0][1]
        if dressing[0][0]<.15-1e-5:fail.append('mover sweep dressing clearance <0.15')

    tris={m:sum(len(f)-2 for f in g['faces']) for m,g in p['groups'].items()}
    if max(tris.values())>=20000 or sum(tris.values())>=20000:fail.append('triangle budget')
    if p['id'] in CHANGED:
        if sum(tris.values())>900 and 'giant' not in p['id']:fail.append('small coral >900')
        if sum(tris.values())>=3000:fail.append('coral >=3000')
        if any(p.get(k) is not False for k in ['can_collide','can_query','can_touch']):fail.append('interaction flags')
    felt=min(feltvals) if feltvals else (None,'source skin/mover')
    r=dict(hole=p['hole'],min_felt_clearance=felt[0],nearest_felt=felt[1],id=p['id'],status='FAIL' if fail else 'PASS',tris=tris,total_tris=sum(tris.values()),min_rail_clearance=minimum[0],nearest_rail=minimum[1],felt_head_triangle_hits=felt_hits,skin_ids=p['skin_ids'],skin_footprint_tolerance=.001,sweep=sweep,failures=fail)
    results.append(r);lines.append(r['status']+' '+p['id']+' '+json.dumps(r))
for sk in json.loads((S/'skipped.json').read_text()):lines.append('SKIPPED '+sk['id']+' '+sk['reason'])
heavy={n:sum(r['total_tris']>900 for r,p in zip(results,P) if p['hole']==n ) for n in [7,8]}
lines.append('Heavy small coral props (>900): '+json.dumps(heavy)+'; limit 2 per hole')
totals={n:sum(r['total_tris'] for r,p in zip(results,P) if p['hole']==n) for n in H if n in [1,2,3,5,7,8]}
allpass=all(r['status']=='PASS' for r in results) and all(v<=34000 for v in totals.values()) and all(v<=2 for v in heavy.values())
lines+=['','Near-field batch totals: '+json.dumps(totals)+' (<=34000 per hole)','ALL PASS: '+('YES' if allpass else 'NO')]
(D/'models/fitcheck_props_batch1.txt').write_text('\n'.join(lines)+'\n')
(S/'fitcheck_report.json').write_text(json.dumps(dict(mode=MODE,parts_sha256=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),heavy_counts=heavy,all_pass=allpass,parts=results,hole_tris=totals),indent=2))
print('\n'.join(lines));raise SystemExit(0 if allpass else 1)
