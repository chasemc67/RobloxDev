from pathlib import Path
import shutil,json
S=Path(__file__).resolve().parent;D=S.parents[2];bk=S/'_backup_visual';bk.mkdir(exist_ok=True)
for p in [S/'parts.json',S/'triangles.json',S/'build_report.json',S/'props_batch2.blend',S/'build.log',S/'fitcheck_report.json',D/'models/props_batch2_manifest.json',D/'models/fitcheck_props_batch2.txt']:
 if p.exists():shutil.copy2(p,bk/p.name)
for sub in ['fbx/props_batch2','previews/props_batch2']:
 shutil.copytree(D/'models'/sub,bk/sub,dirs_exist_ok=True)
p=S/'gen_batch2.py';t=p.read_text()
t=t.replace("[[0,1,5,4],[2,3,7,6]]","[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]")
a=t.index(" anc=[0,0,-33] if n==9");b=t.index('\nout=[]',a)
t=t[:a]+''' anc=[0,0,-33] if n==9 else a(n,name)['position'];p=part(n,name,pivot=anc,felt_skins=[f['id'] for f in H[n]['felt']])
 if name=='span_respawn_stone':box(p,mat,[anc[0],anc[1]-sz[1]/2,anc[2]],sz)
 elif name=='conch_ring':
  for j in range(32):
   t=j*math.tau/32;u=(j+1)*math.tau/32
   vs=[[rr*math.cos(tt),yy,rr*math.sin(tt)] for yy in [-.01,0] for rr,tt in [(.22,t),(.3,t),(.3,u),(.22,u)]]
   p.add(mat,vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
 else:
  # A pointed crescent flush below the source trough, not a rectangular decal.
  poly=[]
  for j in range(33):
   tt=math.pi*.5+j*math.pi/32;poly.append([math.cos(tt),math.sin(tt)])
  for j in range(33):
   tt=math.pi*1.5-j*math.pi/32;poly.append([.25+.8*math.cos(tt),math.sin(tt)])
  p.prism_xz(mat,poly,-.01,0)
''' +t[b:]
# visible exterior spiral on side, within source occluder dimensions, evaluated on loft sections
pos=t.index(" p.notes.append('Shell constrained")
t=t[:pos]+''' # Exterior spiral following the side surface of the shell loft.
 profiles=[(-d/2,.15,c[1]),(-d*.3,w*.4,c[1]),(0,w*.5,c[1]),(d*.25,w*.4,c[1]-.4),(d/2-.12,w*.24,c[1]-h*.25)]
 side=[]
 for j in range(49):
  tt=j/48*math.pi*4;sc=1-j/55;zz=-d*.05+d*.27*sc*math.sin(tt);yy=c[1]+h*.27*sc*math.cos(tt)
  aa,bb=next((aa,bb) for aa,bb in zip(profiles,profiles[1:]) if aa[0]<=zz<=bb[0]);f=(zz-aa[0])/(bb[0]-aa[0]);rr=aa[1]+f*(bb[1]-aa[1]);cy=aa[2]+f*(bb[2]-aa[2]);xx=math.sqrt(max(.001,rr*rr-(yy-cy)**2))
  side.append([c[0]+min(w/2-.06,xx),yy,c[2]+zz])
 for aa,bb in zip(side,side[1:]):tube(p,'CoralOrange',aa,bb,.04,n=4)
''' +t[pos:]
p.write_text(t)
# Selection uses the saved complete raw preflight report to keep reproducible source contradictions.
p=S/'select_batch2.py';t=p.read_text().replace("R=json.loads((S/'fitcheck_report.json').read_text())","R=json.loads((S/'preflight_fitcheck_report.json').read_text())");p.write_text(t)
