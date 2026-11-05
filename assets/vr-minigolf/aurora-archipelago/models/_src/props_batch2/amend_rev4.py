import json,sys,math
from pathlib import Path
S=Path('models/_src/props_batch2').resolve();sys.path.insert(0,str(S));import geometry as g
ps=json.loads((S/'parts.json').read_text())
def bevel(q,m,c,size):
 x,y,z=c;w,h,d=size;b=min(w,d,h)*.12
 poly=[[-w/2+b,-d/2],[w/2-b,-d/2],[w/2,-d/2+b],[w/2,d/2-b],[w/2-b,d/2],[-w/2+b,d/2],[-w/2,d/2-b],[-w/2,-d/2+b]]
 q.loft(m,[[[x+xx*sc,yy,z+zz*sc] for xx,zz in poly] for sc,yy in [(.92,y),(1,y+b),(1,y+h-b),(.92,y+h)]])
for p in ps:
 if p['id'] not in ['h15_ice_parapet','h17_ice_bridge']:continue
 q=g.Part(p['id'],p['hole'],[0,0,0])
 if p['hole']==15:
  for k in range(7):
   x=-3.35+(k+.5)*6.7/7;hh=3.5+[-.35,.2,-.1,.4,-.25,.1,-.4][k]
   bevel(q,'IceGuard',[x,0,0],[6.7/7-.018,hh,.3]);bevel(q,'Snow',[x,hh-.08,0],[6.7/7-.04,.08,.28])
  for k in [0,2,4,6]:
   x=-3.35+(k+.5)*6.7/7;hh=3.5+[-.35,.2,-.1,.4,-.25,.1,-.4][k];g.tube(q,'IceGuard',[x,hh-.07,.12],[x+.025,hh-.65-(k%3)*.12,.15],.06,.006,n=6)
 else:
  q.box('Ice',[0,-.3,0],[4,.6,24.7]);q.box('IceCore',[0,-.04,0],[3.6,.05,24.5])
  for x in [-2.25,2.25]:
   bevel(q,'Timber',[x,-.5,0],[.42,1.5,24.7])
   for z in [-12,-8,-4,0,4,8,12]:bevel(q,'Timber',[x,-.5,z],[.5,1.65,.45])
   for k in range(13):g.mound(q,'Snow',[x,1,-11.4+k*1.9],[.48,.3+.025*(k%3),2.15],n=6)
  for x in [-1.88,1.88]:bevel(q,'Snow',[x,-.14,0],[.22,.12,24.5])
 p['groups']={m:dict(verts=v,faces=f) for m,(v,f) in q.g.items()}
 print(p['id'],sum(len(f)-2 for gg in p['groups'].values() for f in gg['faces']))
(S/'parts.json').write_text(json.dumps(ps,indent=2))
cache=json.loads((S/'triangles.json').read_text())
for id in ['h15_ice_parapet','h17_ice_bridge']:cache.pop(id,None)
(S/'triangles.json').write_text(json.dumps(cache))
src=(S/'build_rev4.py').read_text().replace("CHANGED=set(json.loads((S/'rev4_ids.json').read_text()))","CHANGED={'h15_ice_parapet','h17_ice_bridge'}").replace('for n in [9,15,17]:','for n in [15,17]:');(S/'build_ice_rev4.py').write_text(src)
