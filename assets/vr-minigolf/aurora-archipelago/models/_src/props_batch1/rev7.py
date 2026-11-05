"""Giant coral rev7: shorter bare trunk + 3 stacked, offset, lumpy dome clusters inside the 4x4 cap. Only h08_giant_coral changes."""
import json,math,shutil,hashlib,sys,subprocess
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import numpy as np
from collections import deque
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch1'
ID='h08_giant_coral';BK=S/'_backup_rev6_giant_coral'
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (S/log).open('w') as f:subprocess.run(args,cwd=D,stdout=f,stderr=subprocess.STDOUT,check=True)
def blender(script,log):run(['powershell','-NoProfile','-File',str(M/'_src/run_blender.ps1'),'-Script',str(S/script),'-Log','props_batch1/'+log],log+'.launcher')
def main():
 assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
 paths=[M/'fbx/props_batch1/h08_giant_coral.fbx']+[PV/n for n in ['h08_giant_coral_34.png','h08_giant_coral_front.png','h08_34.png','silhouette_compare_h08.jpg','contact_sheet.jpg']]+[M/'props_batch1_manifest.json',M/'fitcheck_props_batch1.txt',S/'summary.md',S/'parts.json',S/'triangles.json',S/'build_report.json',S/'fitcheck_report.json',S/'fbx_validation.json']
 for p in paths:
  assert p.exists(),p
  q=BK/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():shutil.copy2(p,q)
 old=read(BK/'models/props_batch1_manifest.json');ps=read(BK/'models/_src/props_batch1/parts.json')
 untouched={str(p.relative_to(D)):sha(p) for p in (M/'fbx').rglob('*.fbx') if p.stem!=ID}
 write(S/'rev7_unchanged.json',untouched);write(S/'rev7_ids.json',[ID])
 sys.path.insert(0,str(M/'_src/props_batch2'));import geometry as g
 p=next(p for p in ps if p['id']==ID);col='CoralPink';q=g.Part(ID,8,[0,0,0])
 def blob(mat,c,size,n=8,steps=5):
  rings=[]
  for j in range(steps+1):
   ang=-math.pi/2+math.pi*j/steps;rr=max(.001,math.cos(ang))
   rings.append([[c[0]+size[0]/2*rr*math.cos(math.tau*i/n),c[1]+size[1]/2*math.sin(ang),c[2]+size[2]/2*rr*math.sin(math.tau*i/n)] for i in range(n)])
  q.loft(mat,rings)
 # Short bare trunk (0..3.5), flared root, same base radius as rev6 (1.05).
 g.tube(q,col,[0,0,0],[0,.5,0],1.05,.75,n=10)
 g.tube(q,col,[0,.5,0],[0,3.3,0],.75,.5,n=10)
 start=len(q.g[col][0])
 # Three domes: (centre xz, bottom y, width, height, depth) big low-left, medium mid-right, small top-left.
 domes=[([-.55,.3],3.0,3.0,3.2,2.9),([.85,-.35],4.9,2.5,2.9,2.4),([-.15,.15],6.8,2.1,2.5,1.9)]
 cores=[]
 for k,((cx,cz),y0,w,h,d) in enumerate(domes):
  cy=y0+h*.5
  g.tube(q,col,[0,3.1,0],[cx*.8,y0+h*.45,cz*.8],.4,.28,n=6)
  blob(col,[cx,cy,cz],[w*.86,h*.82,d*.86],n=10,steps=6)
  for i in range(5):
   t=math.tau*(i/5+.13*k);r=.3
   lc=[cx+w*r*math.cos(t),cy+h*(.08+.06*(i%2)),cz+d*r*math.sin(t)]
   blob(col,lc,[w*.48,h*.46,d*.48])
   if i%3==0:cores.append([lc[0],lc[1]+h*.19,lc[2]])
  blob(col,[cx,cy+h*.27,cz],[w*.5,h*.46,d*.5]);cores.append([cx,cy+h*.45,cz])
 for c in cores:blob('CoralMint',c,[.34,.22,.34],n=4,steps=2)
 crown=[v for mat,(verts,_) in q.g.items() for v in verts[(start if mat==col else 0):]]
 lo=[min(v[i] for v in crown) for i in range(3)];hi=[max(v[i] for v in crown) for i in range(3)]
 for v in crown:
  v[0]=(v[0]-(hi[0]+lo[0])/2)*4/(hi[0]-lo[0]);v[2]=(v[2]-(hi[2]+lo[2])/2)*4/(hi[2]-lo[2])
 allv=[v for _,(verts,_) in q.g.items() for v in verts]
 W=max(v[0] for v in allv)-min(v[0] for v in allv);Dp=max(v[2] for v in allv)-min(v[2] for v in allv);Ht=max(v[1] for v in allv)
 note=f'Giant coral rev7: short bare trunk to ~3.2 studs, three offset stacked lumpy domes (big low-left, medium mid-right, small top-left), each a core dome + 5 shoulder lumps + top lump, {len(cores)} neon cores. Overall {W:.3f} W x {Ht:.3f} H x {Dp:.3f} D; exact 4-stud occluder cap retained.'
 p['groups']={m:dict(verts=v,faces=f) for m,(v,f) in q.g.items()};p['notes'].append(note)
 tris=sum(len(f)-2 for gg in p['groups'].values() for f in gg['faces']);assert tris<3000,tris
 shape=dict(id=ID,width=W,height=Ht,depth=Dp,trunk_top=3.2,domes=len(domes),neon_cores=len(cores),tris=tris,notes=note)
 write(S/'parts.json',ps);write(S/'rev7_shapes.json',[shape]);cache=read(S/'triangles.json');write(S/'triangles.json',{k:v for k,v in cache.items() if k!=ID})
 run([sys.executable,str(S/'fitcheck_batch1.py')],'rev7_preflight.log')
 src=(S/'build_rev6.py').read_text().replace('rev6','rev7').replace("7 if 'giant' in id","5 if 'giant' in id").replace("for n in [7,8]:\n    visible","for n in [8]:\n    visible").replace("for id in ['h07_coral_w2','h08_coral_1','h08_giant_coral']:","for id in ['h08_giant_coral']:")
 assert "for n in [8]:" in src and "for id in ['h08_giant_coral']:" in src
 (S/'build_rev7.py').write_text(src)
 blender('build_rev7.py','rev7_build.log');run([sys.executable,str(S/'fitcheck_batch1.py')],'rev7_fit.log');blender('verify_batch1.py','rev7_verify.log')
 finalize(old,untouched,shape)
def label(mask):
 labs=np.zeros(mask.shape,dtype=np.int32);n=0
 for y,x in zip(*np.where(mask)):
  if labs[y,x]:continue
  n+=1;labs[y,x]=n;todo=deque([(y,x)])
  while todo:
   a,b=todo.popleft()
   for c,e in [(a-1,b),(a+1,b),(a,b-1),(a,b+1)]:
    if 0<=c<mask.shape[0] and 0<=e<mask.shape[1] and mask[c,e] and not labs[c,e]:labs[c,e]=n;todo.append((c,e))
 return labs,n
def finalize(old,untouched,shape):
 fr=read(S/'fitcheck_report.json');assert fr['all_pass'] and read(S/'fbx_validation.json')['all_pass']
 for path,digest in untouched.items():assert sha(D/path)==digest,path
 new=read(M/'props_batch1_manifest.json');prev={p['id']:p for p in old['parts']}
 for p in new['parts']:
  if p['id']!=ID:assert p==prev[p['id']],p['id']
  else:
   assert p['tris']<3000 and p['can_collide']==prev[ID]['can_collide']
   for k in ['pivot_hole_local','pivot_world','yaw_local','placement_yaw','motion']:assert p[k]==prev[ID][k]
   p['coral_rev6']=prev[ID].get('coral_rev6');p['giant_coral_rev7']=shape
 write(M/'props_batch1_manifest.json',new)
 mask=np.asarray(Image.open(PV/(ID+'_front.png')).convert('RGBA'))[:,:,3]>127;labs,n=label(mask);sizes=np.bincount(labs.ravel())[1:];assert (sizes>5).sum()==1,sizes.tolist()
 out=Image.new('RGB',(1200,680),'#222233');dr=ImageDraw.Draw(out)
 for i,n in enumerate([1,2,3,5,7,8]):
  out.paste(ImageOps.contain(Image.open(PV/f'h{n:02d}_34.png'),(400,300)),(i%3*400,i//3*340));dr.text((i%3*400+10,i//3*340+310),f'H{n:02d}'+(' / Coral rev6' if n==7 else (' / Coral rev6, giant rev7' if n==8 else '')),fill='white')
 out.save(PV/'contact_sheet.jpg',quality=95)
 sheet=Image.open(D/'silhouettes/sheet02-batch1-h05-h08.png').convert('RGB');box,unit=(440,2000,643,2265),39.75
 out=Image.new('RGB',(1600,1100),'white');dr=ImageDraw.Draw(out);dr.text((15,12),'H08 Coral rev6 (small) + giant rev7 / FRONT orthographic, common 50 px per stud',fill='black')
 crop=sheet.crop(box);crop=crop.resize((round(crop.width*50/unit),round(crop.height*50/unit)));out.paste(crop,(20,round(470-(2201-box[1])*50/unit)))
 im=Image.open(PV/'h08_coral_1_front.png').convert('RGBA').resize((400,400));out.paste(im,(450,170),im)
 gi=Image.open(PV/(ID+'_front.png')).convert('RGBA');out.paste(gi,(780,470-650),gi)
 dr.line((15,470,1590,470),fill='#80b0a0');dr.text((450,480),'h08_coral_1 (8-stud span)',fill='black');dr.text((1000,480),'h08_giant_coral rev7 (16-stud span, same 50 px/stud)',fill='black')
 ps=[p for p in new['parts'] if p['hole']==8 and 'coral' in p['id']]
 for i,p in enumerate(ps):
  x=i%5*320;y=540+i//5*270;out.paste(ImageOps.contain(Image.open(PV/(p['id']+'_34.png')),(310,230)),(x,y));dr.text((x+5,y+235),p['id']+(' (rev7)' if p['id']==ID else ''),fill='black')
 out.save(PV/'silhouette_compare_h08.jpg',quality=95)
 shutil.copy2(BK/'models/_src/props_batch1/summary.md',S/'summary.md')
 fp=next(r for r in fr['parts'] if r['id']==ID)
 with (S/'summary.md').open('a',encoding='utf-8') as f:f.write(f"\n\n## Giant coral rev7\n\nOnly `h08_giant_coral` changed (per Game Art Bot): bare trunk shortened to ~3.2 studs (rev6 split was 6.65), topped by three stacked, offset, overlapping lumpy domes of different sizes (big low-left, medium mid-right, small top-left), each built from a core dome + 5 shoulder lumps + a top lump, with {shape['neon_cores']} mint neon cores. Exact 4-stud occluder cap kept in X and Z.\n\n| Coral | Tris | W | H | D | Nearest rail | Clearance | Fitcheck |\n|---|---:|---:|---:|---:|---|---:|---|\n| {ID} | {shape['tris']} | {shape['width']:.3f} | {shape['height']:.3f} | {shape['depth']:.3f} | {fp['nearest_rail']} | {fp['min_rail_clearance']:.3f} | {fp['status']} |\n\nPivot, anchor, yaw, colours/materials and can_collide=false unchanged. All other FBX SHA256 hashes and manifest records unchanged. holes.json MD5 2f1402fe19fc98a303c4e58dae680be9. FBX reimport PASS. Backup: `_backup_rev6_giant_coral/`.\n")
 fit=M/'fitcheck_props_batch1.txt';tx=fit.read_text().replace('ALL PASS: YES','NOTE H1 existing authorized collider-to-rail gap 0.0786796564 retained.\nNOTE Coral rev6 dimensions and per-coral crown W:H are in manifest/summary; source occluder limits retained.\nNOTE Giant coral rev7: shorter trunk + 3 stacked domes, 4x4 cap retained.\nALL PASS: YES');fit.write_text(tx)
 write(S/'rev7_audit.json',dict(all_pass=True,changed=[ID],shape=shape,fitcheck=fp,unchanged_fbx_count=len(untouched)))
 (S/'done_rev7.flag').write_text('Giant coral rev7 COMPLETE\n');print('DONE_REV7',json.dumps(fp),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  (S/'failed_rev7.flag').write_text(repr(e)+'\n');raise
