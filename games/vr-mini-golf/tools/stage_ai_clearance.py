"""Compare Studio-captured per-mesh bounds against built geometry and authored anchor audit.
Conservative bounds test: joined/disconnected meshes can include empty space. No mesh triangles or physics changed.
"""
import json,sys,collections
from pathlib import Path
GAME=Path(__file__).resolve().parents[1]
ASSET=GAME.parents[1]/'assets/vr-mini-golf/aurora-archipelago'
sys.path.insert(0,str(ASSET/'tools'))
import deco_clearance as dc
# Studio float32 coordinates round 0.15 to 0.14999; retain a 0.0001-stud comparison tolerance.
BOUNDS_EPS=0.0001
OUT=GAME/'playtests/stage-ai'
def hull(points):
 pts=sorted(set((round(p[0],5),round(p[2],5)) for p in points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pts:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=1e-9:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=1e-9:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def box(p):
 pts=p['corners'];return hull(pts),min(v[1] for v in pts),max(v[1] for v in pts)
spec=json.loads((ASSET/'holes.json').read_text()); built=json.loads((OUT/'built-bounds.json').read_text())
rows=[];anchor_rows=[]
for h,b in zip(spec['holes'],built['holes']):
 anchors={a['name']:a for a in h['decoration_anchors']}
 wall=[(p['wall'],*box(p)) for p in b['geometry'] if p.get('wall')]
 felt=[(p.get('piece',p['name']),box(p)[0],box(p)[2]) for p in b['geometry'] if p['surface']]
 allprops=[]
 for p in b['props']:
  nm=p['id'][4:];a=anchors.get(nm)
  cl=dc.classify(h['number'],a) if a else 'dressing'
  allprops.append((p['id'],cl,[box(m) for m in p['parts'] if m['transparency']<1]))
 for p in b['anchors']:
  if p['parts']:
   a=anchors.get(p['id']);cl=dc.classify(h['number'],a) if a else 'dressing'
   allprops.append((p['id'],cl,[box(m) for m in p['parts']]))
 def hits_for(p,id,nm,imported):
  a=anchors.get(nm);cl=dc.classify(h['number'],a) if a else 'dressing';hits={}
  for m in p['parts']:
   if m['transparency']>=1:continue
   for kind,other,sep in dc.box_hits(box(m),wall,felt,[(k,c,bs) for k,c,bs in allprops if k!=id],a.get('mounted_on') if a else None):
    if kind in ('wall','prop') and sep >= dc.G-BOUNDS_EPS: continue
    ocl=next((c for k,c,bs in allprops if k==other),None)
    k=(kind,other)
    r=hits.setdefault(k,dict(kind=kind,other=other,other_cls=ocl,sep=round(sep,5),meshes=[]))
    r['sep']=min(r['sep'],round(sep,5));r['meshes'].append(m['name'])
  actual=list(hits.values())
  for x in actual:
   x['real']=dc.is_real(dict(x,cls=cl))
   if x['kind']=='coplanar':
    visible=[v['path'] for v in b.get('rails',[]) if v.get('wall')==x['other'] and v['transparency']<1]
    x['visible_generated_rail_skins']=visible
    x['visible_zfight_candidate']=bool(visible)
  return dict(hole=h['number'],id=id,anchor=nm,cls=cl,imported=imported,mesh_count=len(p['parts']),hits=actual,real_count=sum(x['real'] for x in actual))
 for p in b['props']:rows.append(hits_for(p,p['id'],p['id'][4:],True))
 for p in b['anchors']:anchor_rows.append(hits_for(p,p['id'],p['id'],False))
source=dc.audit(spec)
coverage=[]
for h in spec['holes']:
 for a in h['decoration_anchors']:
  matches=[r['id'] for r in rows if r['hole']==h['number'] and r['anchor']==a['name']]
  coverage.append({'hole':h['number'],'anchor':a['name'],'cls':dc.classify(h['number'],a),'built_props':matches,'measurement':'per-mesh native bounds' if matches else 'No dedicated built prop/anchor in blockout-mode course; source anchor audit only'})
(OUT/'anchor-coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
allrows=rows+anchor_rows
summary={'gap':dc.G,'felt_headroom':8,'method':'Actual Studio per-MeshPart oriented bounds projected to hole XZ plus Y intervals; built wall and supporting-piece bounds. Conservative for meshes with holes/disconnected pieces. Coplanar bounds are z-fight candidates, not triangle-confirmed z-fighting.','source':{'raw':len(source),'by_class':dict(collections.Counter(x['cls'] for x in source)),'real':sum(dc.is_real(x) for x in source),'coplanar':sum(x['kind']=='coplanar' for x in source)},'built':{'imported_props':len(rows),'anchors':len(anchor_rows),'raw':sum(len(r['hits']) for r in allrows),'by_class':dict(collections.Counter(r['cls'] for r in allrows for _ in r['hits'])),'real':sum(r['real_count'] for r in allrows),'imported_real':sum(r['real_count'] for r in rows),'coplanar_candidates':sum(x['kind']=='coplanar' for r in allrows for x in r['hits']),'visible_coplanar_candidates':sum(x.get('visible_zfight_candidate',False) for r in allrows for x in r['hits']),'imported_props_with_real_bounds_violations':[r['id'] for r in rows if r['real_count']],'visual_collision_errors':built['visualFlags'],'mover_weld_errors':built['weldErrors']}}
(OUT/'built-clearance.json').write_text(json.dumps({'summary':summary,'props':rows,'anchors':anchor_rows},indent=2)+'\n')
(OUT/'clearance-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# Stage ai built bounds clearance','',summary['method'],'','| Hole | Item | Class | Raw overlaps | Real bounds flags | Coplanar candidates |','|---|---|---|---:|---:|---:|']
for r in allrows:
 lines.append(f"| {r['hole']} | {r['id']} | {r['cls']} | {len(r['hits'])} | {r['real_count']} | {sum(x['kind']=='coplanar' for x in r['hits'])} |")
(OUT/'built-clearance.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
