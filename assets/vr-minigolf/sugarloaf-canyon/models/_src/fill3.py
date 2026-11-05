import json,sys,numpy as np,collections
src=open('edgefix.py').read().split("E=[n for n")[0].replace("D=json.load(open('layout_look7_dressing.json'))","D=json.load(open('layout_look7_dressing_edgefix2.json'))")
exec(src)
A=json.load(open('layout_look7_dressing_edgefix.json'))['instances']
key=lambda i:(i['piece'],tuple(i['pos']),i['yaw'])
K=set(key(i) for i in I);drop=[i for i in A if key(i) not in K]
print('dropped',len(drop))
Ms=[mesh(i) for i in I];C=np.array([i['pos'] for i in I])
R=lambda m:np.linalg.norm(m.extents[[0,2]])/2;Rr=np.array([R(m) for m in Ms])
# gap test: does the dropped footprint stay covered by kept neighbours of same kind? (fraction of its top-down sample points covered)
import shapely.geometry as sg, shapely.ops as so
def fp(m): 
    t=m.triangles[:,:,[0,2]];return so.unary_union([sg.Polygon(x).buffer(0) for x in t if sg.Polygon(x).area>1e-6])
fills=[];res=[]
for d in drop:
    md=mesh(d);near=np.nonzero(np.hypot(*(C-d['pos'])[:,[0,2]].T)<R(md)+Rr+0.5)[0]
    cov=so.unary_union([fp(Ms[q]) for q in near if I[q]['piece'].startswith('cliff')]) if len(near) else sg.Polygon()
    f=fp(md);unc=f.difference(cov).area/f.area
    rec=dict(piece=d['piece'],pos=d['pos'],uncovered=round(unc,3),fill=None)
    if unc>0.15:
        a=np.radians(d['yaw']);u=np.array([np.sin(a),0,np.cos(a)]);v=np.array([np.cos(a),0,-np.sin(a)])
        for s in (0.9,0.8,0.7,0.6,0.5,0.4):
            for sh in (0,0.5,-0.5,1.0,-1.0):
              for sv in (0,0.5,-0.5):
                j=dict(d,pos=[round(x,3) for x in np.array(d['pos'])+u*sh+v*sv],scale=[s,1.0,s],src='edgefix3 fill (scaled)')
                m=mesh(j)
                if any(bad(m,Ms[q]) for q in near) or any(bad(m,mm) for mm,_ in fills): continue
                c=M.measure(np.array(m.triangles),M.WORLD)
                if c['felt']['clearance']<0.167 or c['rail']['clearance']<0.317: continue
                fills.append((m,j));rec['fill']=dict(scale=s,shift=[sh,sv],felt=round(c['felt']['clearance'],3),rail=round(c['rail']['clearance'],3),uncovered_after=round(f.difference(cov.union(fp(m))).area/f.area,3));break
              if rec['fill']: break
            if rec['fill']: break
    res.append(rec);print(rec,flush=True)
out=I+[j for _,j in fills]
# full verify
Ms2=Ms+[m for m,_ in fills];C2=np.array([i['pos'] for i in out]);R2=np.array([R(m) for m in Ms2])
pairs=sum(bad(Ms2[a],Ms2[b]) for a in range(len(Ms2)) for b in (np.nonzero(np.hypot(*(C2[a+1:]-C2[a])[:,[0,2]].T)<R2[a]+R2[a+1:]+0.3)[0]+a+1))
cl=[M.measure(np.array(m.triangles),M.WORLD) for m,_ in fills];
D3=dict(D,generated='2026-10-14 look7 edgefix3',instances=out,edgefix3=dict(input='layout_look7_dressing_edgefix2.json',dropped_steps=len(drop),gaps=sum(r['uncovered']>0.15 for r in res),filled=len(fills),fills=res,verify_overlap_coplanar_pairs=int(pairs),fill_min_felt=min([c['felt']['clearance'] for c in cl],default=None),fill_min_rail=min([c['rail']['clearance'] for c in cl],default=None),rule='fills: same piece scaled in x/z (y=1) + small shift, gap>=0.086 to all neighbours, 0 coplanar, felt>=0.15 rail>=0.30'))
json.dump(D3,open('layout_look7_dressing_edgefix3.json','w'),indent=0)
json.dump(dict(drop=drop,fills=[j for _,j in fills]),open('fill3_marks.json','w'))
print('SUMMARY',{k:v for k,v in D3['edgefix3'].items() if k!='fills'})
