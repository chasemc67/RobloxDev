"""Euclidean triangle/convex-solid distance; signed SAT escape depth on overlap.

Caches must come from freshly imported FBX, never generator triangles.
Negative values are minimum translational penetration depths per triangle;
the mesh result is the minimum over its triangles (no skin exemptions).
"""
import itertools
import json
from pathlib import Path
import numpy as np

S = Path(__file__).resolve().parent
D = S.parents[2]
FACES = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
EDGES = [(i,j) for i in range(8) for j in range(i+1,8) if (i^j) in (1,2,4)]

def solids(h):
    out = []
    for kind, entries in [('rail', h['walls']), ('felt', h['felt'])]:
        for b in entries:
            size = b['size'] if kind == 'rail' else [b['size'][0], b.get('thickness', .4), b['size'][1]]
            v = np.array(list(itertools.product(*[(-x/2,x/2) for x in size])), float)
            if kind == 'felt':
                v[:,1] -= size[1]/2
                sl = b.get('slope')
                if sl:
                    axis = 0 if sl['axis'] == 'x' else 2
                    v[:,1] += v[:,axis]*sl['rise']/size[axis]
            a = np.radians(b.get('yaw',0)); c,s = np.cos(a),np.sin(a)
            v = v @ np.array([[c,0,-s],[0,1,0],[s,0,c]]) + b['center']
            out.append(dict(kind=kind,id=b['id'],vertices=v))
    return out

def point_triangle(p,t):
    a,b,c=t; ab=b-a; ac=c-a
    n=np.cross(ab,ac); nn=n@n
    if nn > 1e-24:
        q=p-n*((p-a)@n/nn)
        if all(np.cross(y-x,q-x)@n >= -1e-10 for x,y in zip(t,np.roll(t,-1,axis=0))):
            return float(np.linalg.norm(p-q)),q
    best=(float('inf'),None)
    for x,y in zip(t,np.roll(t,-1,axis=0)):
        e=y-x; q=x+e*np.clip((p-x)@e/max(e@e,1e-30),0,1)
        if np.linalg.norm(p-q)<best[0]: best=(float(np.linalg.norm(p-q)),q)
    return best

def segment_segment(a,b,c,d):
    u=b-a; v=d-c; w=a-c; A=u@u; B=u@v; C=v@v; E=u@w; F=v@w
    candidates=[]
    det=A*C-B*B
    if det>1e-24:
        s=(B*F-C*E)/det; t=(A*F-B*E)/det
        if 0<=s<=1 and 0<=t<=1: candidates.append((a+s*u,c+t*v))
    for p in [a,b]: candidates.append((p,c+v*np.clip((p-c)@v/max(C,1e-30),0,1)))
    for p in [c,d]: candidates.append((a+u*np.clip((p-a)@u/max(A,1e-30),0,1),p))
    return min(((float(np.linalg.norm(p-q)),p,q) for p,q in candidates), key=lambda z:z[0])

def triangle_solid(t,b):
    v=b['vertices']; te=np.roll(t,-1,axis=0)-t
    be=[v[j]-v[i] for i,j in EDGES]
    axes=[np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]) for f in FACES]
    axes += [np.cross(te[0],te[1])]+[np.cross(e,f) for e in te for f in be]
    penetration=float('inf'); separated=False
    for n in axes:
        length=np.linalg.norm(n)
        if length<1e-12: continue
        n=n/length; x=t@n; y=v@n
        depth=min(y.max()-x.min(),x.max()-y.min())
        if depth < -1e-9: separated=True
        penetration=min(penetration,depth)
    if not separated: return -max(0.,float(penetration)),t.mean(axis=0),v.mean(axis=0)
    best=(float('inf'),None,None)
    for f in FACES:
        for indices in [(f[0],f[1],f[2]),(f[0],f[2],f[3])]:
            bt=v[list(indices)]
            for p in t:
                dist,q=point_triangle(p,bt)
                if dist<best[0]: best=(dist,p,q)
    for p in v:
        dist,q=point_triangle(p,t)
        if dist<best[0]: best=(dist,q,p)
    for i in range(3):
        for j,k in EDGES:
            result=segment_segment(t[i],t[(i+1)%3],v[j],v[k])
            if result[0]<best[0]: best=result
    return best

def measure(triangles, boxes, kinds=('rail','felt')):
    result={}
    for kind in kinds:
        best=None
        for b in boxes:
            if b['kind']!=kind: continue
            for i,t in enumerate(triangles):
                v=b['vertices']
                lower=float(np.linalg.norm(np.maximum(0,np.maximum(v.min(0)-t.max(0),t.min(0)-v.max(0)))))
                if best is not None and lower>max(0,best['clearance'])+1e-10: continue
                value,p,q=triangle_solid(t,b)
                if best is None or value<best['clearance']:
                    best=dict(id=b['id'],clearance=value,triangle=i,mesh_point=p.tolist(),solid_point=q.tolist())
        if best is None: raise ValueError('Missing '+kind+' solids')
        result[kind]=best
    return result

def main(stage):
    from common import records, load_cache, write_json
    holes={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
    rows={p['id']:measure(load_cache(p,stage),solids(holes[p['hole']])) for p in records(stage)}
    write_json(S/f'clearance_{stage}.json',rows)
    lines=['| Asset | Nearest rail | Clearance | Nearest felt | Clearance |','|---|---|---:|---|---:|']
    for id,r in rows.items(): lines.append(f"| {id} | {r['rail']['id']} | {r['rail']['clearance']:.6f} | {r['felt']['id']} | {r['felt']['clearance']:.6f} |")
    (S/f'clearance_{stage}.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    import sys
    main(sys.argv[1])
