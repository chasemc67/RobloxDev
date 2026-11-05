import json,sys,numpy as np,collections,trimesh,shapely.geometry as sg,shapely.ops as so
exec(open('edgefix.py').read().split("E=[n for n")[0].replace("D=json.load(open('layout_look7_dressing.json'))","D=json.load(open('layout_look7_dressing_edgefix3.json'))"))
# filler rock: low faceted lump, unit footprint radius 1, height 1, base at y=0
rng=np.random.default_rng(4);ROCK={}
for v,seed in (('a',4),('b',9)):
    r=np.random.default_rng(seed);a=np.linspace(0,2*np.pi,10)[:-1]+r.uniform(-.2,.2,9);rr=r.uniform(.8,1,9)
    P=np.r_[np.c_[rr*np.cos(a),np.zeros(9),rr*np.sin(a)],np.c_[.6*rr*np.cos(a+.3),r.uniform(.75,1,9),.6*rr*np.sin(a+.3)]]
    m=trimesh.convex.convex_hull(P);m.merge_vertices();ROCK['cliff_filler_rock_'+v]=m;B['cliff_filler_rock_'+v]=m
mk=json.load(open('fill3_marks.json'))
Ms=[mesh(i) for i in I];C=np.array([i['pos'] for i in I]);Rr=np.array([np.linalg.norm(m.extents[[0,2]])/2 for m in Ms])
def fp(m): return so.unary_union([sg.Polygon(x).buffer(0) for x in m.triangles[:,:,[0,2]] if sg.Polygon(x).area>1e-6])
add=[];addm=[];rep=[]
for k,d in enumerate(mk['drop']):
    md=mesh(d);near=np.nonzero(np.hypot(*(C-d['pos'])[:,[0,2]].T)<np.linalg.norm(md.extents[[0,2]])/2+Rr+1)[0]
    occ=so.unary_union([fp(Ms[q]) for q in near]);hole=fp(md).difference(occ.buffer(0.1))
    a0=hole.area;placed=0
    for _ in range(60):
        hole=hole.buffer(0)
        if hole.is_empty or hole.area<0.3: break
        # best interior point = max distance to boundary
        xs=np.array(hole.bounds);gx,gz=np.meshgrid(np.arange(xs[0],xs[2],0.25),np.arange(xs[1],xs[3],0.25))
        pts=[sg.Point(x,z) for x,z in zip(gx.ravel(),gz.ravel())];pts=[p for p in pts if hole.contains(p)]
        if not pts: break
        dist=np.array([hole.boundary.distance(p) for p in pts]);b=int(dist.argmax());rad=dist[b]-0.02
        if rad<0.42: break
        rad=min(rad,2.2);p=pts[b];ok=False
        for s in (1.0,0.85,0.7,0.55):
            rs=rad*s
            if rs<0.42: break
            h=float(np.clip(rs*0.8,0.5,1.6))
            j=dict(piece='cliff_filler_rock_'+'ab'[len(add)%2],pos=[round(p.x,3),round(d['pos'][1]-0.12,3),round(p.y,3)],yaw=float(rng.uniform(0,360)),scale=[round(rs,3),round(h,3),round(rs,3)],src=f'edgefix4 filler site{k:02d}')
            m=mesh(j)
            if any(bad(m,Ms[q]) for q in near) or any(bad(m,mm) for mm in addm[-40:]): continue
            c=M.measure(np.array(m.triangles),M.WORLD)
            if c['felt']['clearance']<0.167 or c['rail']['clearance']<0.317: continue
            add.append(j);addm.append(m);hole=hole.difference(fp(m).buffer(0.1));ok=True;placed+=1;break
        if not ok: hole=hole.difference(p.buffer(max(rad,0.3)))
    rep.append(dict(site=k,opening_area=round(a0,2),fillers=placed,open_after=round(fp(md).difference(so.unary_union([occ]+[fp(m) for m in addm[-placed:]] if placed else [occ])).area/fp(md).area,3)))
    print(rep[-1],flush=True)
out=I+add;Ms2=Ms+addm;C2=np.array([i['pos'] for i in out]);R2=np.r_[Rr,[np.linalg.norm(m.extents[[0,2]])/2 for m in addm]]
pairs=int(sum(bad(Ms2[a],Ms2[b]) for a in range(len(Ms2)) for b in (np.nonzero(np.hypot(*(C2[a+1:]-C2[a])[:,[0,2]].T)<R2[a]+R2[a+1:]+0.3)[0]+a+1)))
cl=[M.measure(np.array(m.triangles),M.WORLD) for m in Ms2]
th=min(min(j['scale'][1],2*j['scale'][0]*0.8) for j in add) if add else None
D4=dict(D,generated='2026-10-14 look7 edgefix4',instances=out,edgefix4=dict(input='layout_look7_dressing_edgefix3.json',fillers=len(add),sites=rep,verify_overlap_coplanar_pairs=pairs,min_felt_all=round(min(c['felt']['clearance'] for c in cl),3),min_rail_all=round(min(c['rail']['clearance'] for c in cl),3),min_filler_dim=th,mean_open_before=round(np.mean([1.0]*0),3) if False else None,rule='filler rocks (Strata) in openings, gap>=0.086 to all, 0 coplanar, felt>=0.15, rail>=0.30'))
json.dump(D4,open('layout_look7_dressing_edgefix4.json','w'),indent=0)
json.dump(dict(fillers=add),open('fill4_marks.json','w'))
for k,m in ROCK.items(): json.dump({k:dict(objects=[dict(name=k+'__Strata',mats=['Strata'],verts=m.vertices.round(4).tolist(),tris=m.faces.tolist(),mat_index=[0]*len(m.faces))])},open(f'filler/build_{k}.json','w'))
print('SUMMARY',{k:v for k,v in D4['edgefix4'].items() if k!='sites'},'tris',{k:len(m.faces) for k,m in ROCK.items()})
