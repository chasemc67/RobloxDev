"""Triangle/OBB SAT with slope shear and .15 plan buffer; analytic continuous bell sweep."""
import sys as _guard_sys
from pathlib import Path as _GuardPath
_guard_sys.path.insert(0, str(_GuardPath(__file__).resolve().parent.parent))
from polish_guard import start_guard
_PROTECTED_VERIFY = start_guard()

import sys,hashlib
from checks import *
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
P4='--polish2' in sys.argv
if P4:
 import checks
 CACHE=json.loads((S/'polish2_triangles.json').read_text());checks.CACHE=CACHE
 report_build=json.loads((S/'polish2_build_report.json').read_text())
 if report_build['parts_sha256']!=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest():raise SystemExit('Stale P4 geometry')
 if report_build['triangles_sha256']!=hashlib.sha256((S/'polish2_triangles.json').read_bytes()).hexdigest():raise SystemExit('Stale P4 triangle evidence')
 validation=json.loads((S/'polish2_fbx_validation.json').read_text())
 polish_ids=set(json.loads((S/'polish_ids.json').read_text()))
 if not validation['all_pass'] or set(validation['exported_ids'])!=polish_ids:raise SystemExit('All ten polish FBX validations required')
 expected=report_build['fbx_sha256']
 if validation.get('fbx_sha256')!=expected or validation['parts_sha256']!=report_build['parts_sha256']:raise SystemExit('Polish reimport provenance mismatch')
 for asset in polish_ids:
  path=D/'models/fbx/props_batch3_polish'/(asset+'.fbx')
  if hashlib.sha256(path.read_bytes()).hexdigest()!=expected[asset]:raise SystemExit('Polish FBX differs from validated evidence: '+asset)
 if set(CACHE)!=polish_ids:raise SystemExit('Missing polish triangle evidence')
 # Every other asset uses approved originals and their original triangle cache.
 approved=json.loads((S/'triangles_prepolish.json').read_text())
 originals={p['id']:p for p in json.loads((S/'parts_prepolish.json').read_text())}
 P=[p if p['id'] in polish_ids else originals[p['id']] for p in P]
 CACHE={**{k:v for k,v in approved.items() if k not in polish_ids},**CACHE};checks.CACHE=CACHE
elif '--preflight' in sys.argv:
 import checks
 checks.CACHE=None
 CACHE=None
elif CACHE is None:raise SystemExit('No triangles.json: use --preflight until Blender build exists')
else:
 report_build=json.loads((S/'build_report.json').read_text())
 if report_build.get('parts_sha256')!=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest():raise SystemExit('Blender triangles are stale for current parts.json; run user Blender build or --preflight')
 if report_build.get('triangles_sha256')!=hashlib.sha256((S/'triangles.json').read_bytes()).hexdigest():raise SystemExit('Blender triangle provenance mismatch')
 if set(CACHE)!={p['id'] for p in P}:raise SystemExit('Missing/extra Blender triangle assets')

def bounds_box(v):
 lo=v.min(axis=0);hi=v.max(axis=0);return dict(center=(lo+hi)/2,size=hi-lo)
def contains(v,b):
 q=(v-np.array(b['center']))@ry(b.get('yaw',0));return (np.abs(q)<=np.array(b['size'])/2+1e-5).all(axis=-1)
def continuous_bounds(v,pivot,lo=-9,hi=9):
 q=v-pivot;mins=q.copy();maxs=q.copy();miny=(100,None)
 for axis in [0,1]:
  A=q[:,0] if axis==0 else q[:,1];B=-q[:,1] if axis==0 else q[:,0]
  phase=np.arctan2(B,A)
  angles=[np.full(len(q),math.radians(lo)),np.full(len(q),math.radians(hi))]
  for k in range(-2,3):angles.append(np.clip(phase+k*math.pi,math.radians(lo),math.radians(hi)))
  vals=np.array([A*np.cos(t)+B*np.sin(t) for t in angles]);mins[:,axis]=vals.min(axis=0);maxs[:,axis]=vals.max(axis=0)
  if axis==1:
   i,j=np.unravel_index(vals.argmin(),vals.shape);miny=(float(vals[i,j]+pivot[1]),float(math.degrees(angles[i][j])))
 return dict(center=(mins.min(axis=0)+maxs.max(axis=0))/2+pivot,size=maxs.max(axis=0)-mins.min(axis=0)),miny
def clip_polygon(poly,axis,bound,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[axis]-bound);db=sign*(b[axis]-bound)
  if da>=-1e-10:out.append(a)
  if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
 return out

def vertical_over_felt(T,f):
 q=(T-np.array(f['center']))@ry(f.get('yaw',0))
 if f.get('slope'):
  sl=f['slope'];axis=0 if sl['axis']=='x' else 2
  q[:,:,1]-=q[:,:,axis]*sl['rise']/f['size'][0 if axis==0 else 1]
 values=[]
 for tri in q:
  if abs(np.cross(tri[1]-tri[0],tri[2]-tri[0])[1])<1e-10:continue
  poly=list(tri)
  for axis,half in [(0,f['size'][0]/2),(2,f['size'][1]/2)]:
   for bound,sign in [(-half,1),(half,-1)]:
    if poly:poly=clip_polygon(poly,axis,bound,sign)
  if poly:values.append(min(float(v[1]) for v in poly))
 return min(values) if values else None

def ball_path_clearance(T,h):
 way=h.get('ai_waypoints',[])
 if isinstance(way,dict):way=way.get('all',[])
 pts=[h['tee']['position']]+[w['pos'] if isinstance(w,dict) else w for w in way]+[h['cup']['position']]
 minima=[]
 for aa,bb in zip(pts,pts[1:]):
  aa=np.array(aa,float);bb=np.array(bb,float)
  for tri in T:
   matrix=np.column_stack((tri[1,[0,2]]-tri[0,[0,2]],tri[2,[0,2]]-tri[0,[0,2]]))
   if abs(np.linalg.det(matrix))<1e-10:continue
   uv0=np.linalg.solve(matrix,aa[[0,2]]-tri[0,[0,2]])
   uv1=np.linalg.solve(matrix,bb[[0,2]]-tri[0,[0,2]])
   weights0=np.array([1-uv0.sum(),*uv0]);weights1=np.array([1-uv1.sum(),*uv1])
   lo,hi=0.,1.
   for a,b in zip(weights0,weights1):
    delta=b-a
    if abs(delta)<1e-12:
     if a<0:hi=-1
    elif delta>0:lo=max(lo,-a/delta)
    else:hi=min(hi,-a/delta)
   if lo<=hi:
    for t in [lo,hi]:
     weights=weights0+t*(weights1-weights0)
     minima.append(float(weights@tri[:,1]-(aa[1]+t*(bb[1]-aa[1]))))
 return dict(minimum=min(minima) if minima else 'none over ball path',path=pts,method='Exact projected triangle/segment clipping; underside minus interpolated waypoint path elevation')

R=[]
POLISH_IDS=set(json.loads((S/'polish_ids.json').read_text()))
PREPOLISH={p['id']:p for p in json.loads((S/'parts_prepolish.json').read_text())}
for p in P:
 if P4 and p['id'] not in POLISH_IDS:continue
 h=H[p['hole']];T=triangles(p);v=T.reshape(-1,3);fail=[];exempt=np.zeros(len(T),bool)
 src=next(a for a in h['decoration_anchors'] if a['name']==p['source_anchor']);pos=np.array(src['position']);size=src['approx_size']
 env=dict(center=pos+[0,size[1]/2,0],size=size);boxes=p['override_boxes'] or [env]
 if not np.logical_or.reduce([contains(v,b) for b in boxes]).all():fail.append('envelope containment')
 if src.get('occluders'):
  occ=src['occluders']+p['override_boxes']
  if not np.logical_or.reduce([contains(v,b) for b in occ]).all():fail.append('occluder containment')
 if p['motion']:
  if p['anchor']!=p['motion']['pivot']:fail.append('mover pivot')
 else:
  expected_pivot={'h04_crystal_spire':[-12,0,-18],'h14_rail_bollards':[0,0,0],'h06_tee_lantern':[8.2,0,-4]}.get(p['id'],src['position'])
  if p['anchor']!=expected_pivot:fail.append('static pivot')
 if p.get('can_collide') is not False:fail.append('visual collision must be off')
 for wid in p['skin_ids']:
  w=next(w for w in h['walls'] if w['id']==wid);exempt|=contains(T,w).all(axis=1)
 if p['skin_ids'] and not exempt.all():fail.append('skin volume containment')
 # Exact source skin triangles retain structural end joints with adjacent source rails.
 railT=T[~exempt]
 # Own exact source volumes exempt only their explicitly listed colliders.
 vals=sorted((clearance(T,w),w['id']) for w in h['walls'] if w['id'] not in p['skin_ids']) if len(p['skin_ids']) else sorted((clearance(T,w),w['id']) for w in h['walls'])
 if not vals:vals=[(0,'all source rails explicitly skinned')]
 rail=vals[0]
 if vals[0][1]!='all source rails explicitly skinned' and rail[0]<.15-1e-5:fail.append('rail < .15')
 hits=0;feltvals=[]
 if not p['motion']:
  for f in h['felt']:
   q=(T-np.array(f['center']))@ry(f.get('yaw',0))
   if f.get('slope'):
    s=f['slope'];idx=0 if s['axis']=='x' else 2;q[:,:,1]-=q[:,:,idx]*s['rise']/f['size'][0 if idx==0 else 1]
   flush=np.zeros(len(T),bool)
   if f['id'] in p['felt_skins']:flush=q[:,:,1].max(axis=1)<=.001
   live=q[~(exempt|flush)]
   if len(live):
    slab=dict(center=[0,4,0],size=[f['size'][0]+.3,8-.00002,f['size'][1]+.3]);hits+=int(hit(live,slab['center'],slab['size']).sum())
    feltvals.append((clearance(live,dict(center=[0,4,0],size=[f['size'][0],8,f['size'][1]])),f['id']))
  if hits:fail.append('felt/headroom .15 plan buffer')
 sweep=None
 if p['motion']:
  b,miny=continuous_bounds(v,np.array(p['anchor']));sw=[]
  for w in h['walls']:
   # Triangulate conservative analytic swept AABB and use the same SAT gate.
   from geometry import Part
   temp=Part('sweep',14,[0,0,0]);temp.box('Brass',b['center'],b['size']);gg=temp.g['Brass'];fake=dict(anchor=[0,0,0],groups={'Brass':dict(verts=gg[0],faces=gg[1])},id='sweep')
   sw.append((clearance(triangles(fake),w),w['id']))
  sr=min(sw);dressing=sorted((clearance(triangles(o),b),o['id']) for o in P if o['hole']==14 and not o['motion'])
  nearestwall=next(w for w in h['walls'] if w['id']==sr[1]);anglevals=[]
  for deg in [-9,0,9]:
   t=math.radians(deg);rot=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
   rotated=(T-np.array(p['anchor']))@rot.T+p['anchor'];anglevals.append((clearance(rotated,nearestwall),deg))
  attained,railangle=min(anglevals)
  sweep=dict(method='Analytic vertex extrema over full [-9,+9] degrees; conservative continuous swept AABB for rail/static SAT',range=[-9,9],min_felt_clearance=miny[0],felt_angle_degrees=miny[1],min_rail_clearance=sr[0],rail=sr[1],rail_angle_degrees=None,rail_angle_note='continuous conservative lower bound applies at every angle',min_static_clearance=dressing[0][0],nearest_static=dressing[0][1],contact_shape_exception='Exact holes.json nine-strip skid permits source minimum >=.060; general .15 rule applies to rails and static dressing')
  sweep['rail_angle_degrees']=railangle;sweep['rail_at_angle_clearance']=attained
  sweep['rail_angle_note']='Endpoint/rest triangle SAT attains continuous analytic swept-box lower bound within tolerance' if abs(attained-sr[0])<1e-4 else 'Endpoint/rest measured minimum; certified continuous bound reported separately'
  if miny[0]<.060-1e-5:fail.append('source skid felt minimum')
  if sr[0]<.15-1e-5:fail.append('full sweep rail .15')
  if dressing[0][0]<.15-1e-5:fail.append('full sweep static .15')
  # Exact skid strips retained, while bell body is contained by the yaw30 contact envelope.
  from geometry import Part
  expected=Part('contact',14,[0,0,0])
  for bb in p['motion']['blockers'][1:]:expected.box('Brass',bb['center'],bb['size'],bb.get('yaw',0))
  actual=np.array(p['groups']['Brass']['verts'][:72]);want=np.array(expected.g['Brass'][0])
  if actual.shape!=want.shape or not np.allclose(actual,want,atol=1e-8):fail.append('exact skid collider match')
  body=v[v[:,1]<2.35-1e-7]
  cube=p['motion']['blockers'][0].copy();cube['center']=(np.array(cube['center'])+p['anchor']).tolist()
  # Skid is the sole below-cube exception.
  if not (contains(body,cube)|np.logical_or.reduce([contains(body,dict(center=(np.array(bb['center'])+p['anchor']).tolist(),size=bb['size'],yaw=bb.get('yaw',0))) for bb in p['motion']['blockers'][1:]])).all():fail.append('bell cube envelope')
 counts={m:sum(len(f)-2 for f in g['faces']) for m,g in p['groups'].items()}
 if len(T)>=3000:fail.append('tri budget >=3000')
 if p['id'] in POLISH_IDS:
  old=PREPOLISH[p['id']]
  if any(p.get(k) is not False for k in ['can_collide','can_query','can_touch']):fail.append('interaction flags')
  if any(p[k]!=old[k] for k in ['anchor','yaw_local','skin_ids','felt_skins','motion','override_boxes']):fail.append('polish placement/envelope changed')
  old_tris=sum(len(f)-2 for g in old['groups'].values() for f in g['faces'])
  if 'snowpuffs' in p['id'] and len(T)>(900 if p['hole']==14 else 1600):fail.append('P5 snowpuff triangle cap')
  if 'snowpuffs' in p['id'] and len(T)>=old_tris*1.2:fail.append('snowpuff growth >=20%')
  if 'snowpuffs' not in p['id'] and p['id']!='h06_frosted_palms' and len(T)>900:fail.append('polish light asset >900')
 elif p!=PREPOLISH[p['id']]:fail.append('unlisted asset changed')
 if not p['motion'] and any(m in ['MoveCream','MoveRed','PepRed','Cherry','CreamTaffy','FlagRed','Cream'] for m in counts):fail.append('reserved static material')
 # Exact line/triangle intersection for tee-eye to flag-top, using a thin segment prism SAT.
 eye=np.array(h['tee']['position'])+[0,5.5,0];flag=np.array(h['cup']['flag']['top']);direction=flag-eye
 e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];cross=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.einsum('ij,ij->i',e1,cross);valid=np.abs(det)>1e-10;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);s=eye-T[:,0];u=inv*np.einsum('ij,ij->i',s,cross);qq=np.cross(s,e1);vv=inv*(qq@direction);tt=inv*np.einsum('ij,ij->i',e2,qq);linehits=int((valid&(u>=0)&(vv>=0)&(u+vv<=1)&(tt>=0)&(tt<=1)).sum())
 if linehits:fail.append('tee flag sightline')
 felt=min(feltvals) if feltvals else (miny[0] if sweep else 0,'contact/flush/source skin')
 head_by_felt={f['id']:vertical_over_felt(T,f) for f in h['felt']}
 head_by_felt={k:v for k,v in head_by_felt.items() if v is not None}
 head_min=min(head_by_felt.values()) if head_by_felt else 'none over felt'
 R.append(dict(head_room_min_over_felt=head_min,head_room_over_felt=head_by_felt,ball_path_vertical_clearance=ball_path_clearance(T,h) if p['id']=='h18_halo_arch' else None,id=p['id'],hole=p['hole'],status='FAIL' if fail else 'PASS',total_tris=len(T),material_tris=counts,min_rail_clearance=rail[0],nearest_rail=rail[1],min_felt_clearance=felt[0],nearest_felt=felt[1],head_room_hits=hits,sightline_hits=linehits,sweep=sweep,failures=fail))
hole_totals={n:sum(r['total_tris'] for r in R if r['hole']==n) for n in [4,6,14,18]}
heavy_counts={n:sum(r['total_tris']>900 for r in R if r['hole']==n) for n in [4,6,14,18]}
if P4:
 from polish_manifest import read_parts
 totals={asset:p['tris'] for asset,p in read_parts(D/'models',S.name).items()}
 totals.update({r['id']:r['total_tris'] for r in R})
 if set(totals)!={p['id'] for p in P}:raise SystemExit('Incomplete approved/polish per-hole totals')
 hole_totals={n:sum(totals[p['id']] for p in P if p['hole']==n) for n in [4,6,14,18]}
 heavy_counts={n:sum(totals[p['id']]>900 for p in P if p['hole']==n) for n in [4,6,14,18]}
for r in R:
 r['heavy']=r['total_tris']>900
 if hole_totals[r['hole']]>=20000:r['failures'].append('hole merged >=20000')
 if heavy_counts[r['hole']]>2:r['failures'].append('hole heavy count >2')
 allowed={4:['h04_snowpuffs','h04_steam_vents'],6:['h06_frosted_palms','h06_snowpuffs'],14:['h14_icicle_bell','h14_snowpuffs'],18:['h18_halo_arch','h18_snowpuffs']}
 if r['heavy'] and r['id'] not in allowed[r['hole']]:r['failures'].append('unplanned heavy asset')
 r['status']='FAIL' if r['failures'] else 'PASS'
ok=all(r['status']=='PASS' for r in R)
from measure_arch_rev2 import measure
arch_measurements=None if P4 else measure()
report=dict(arch_rev2_measurements=arch_measurements,parts_sha256=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),all_pass=ok,mode='preflight fan triangulation' if CACHE is None else 'Blender actual triangles',parts=R,heavy_counts=heavy_counts,hole_tris=hole_totals)
(S/('polish2_fitcheck_report.json' if P4 else 'fitcheck_report.json')).write_text(json.dumps(report,indent=2))
lines=['Batch3 '+report['mode'],'Exact source skins exempt only explicitly owned collider boxes. Source bell contact skid exempt generic .15 felt clearance.']+[r['status']+' '+r['id']+' '+json.dumps(r) for r in R]+['ALL PASS: '+('YES' if ok else 'NO')]
(S/('polish2_fitcheck_report.txt' if P4 else 'fitcheck_report.txt')).write_text('\n'.join(lines));print('\n'.join(r['status']+' '+r['id']+' '+str(r['failures']) for r in R));print(lines[-1]);sys.exit(0 if ok else 1)
