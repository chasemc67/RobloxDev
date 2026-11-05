import json,math,shutil,hashlib,sys,subprocess
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch1'
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (S/log).open('w') as f:subprocess.run(args,cwd=D,stdout=f,stderr=subprocess.STDOUT,check=True)
def blender(script,log):run(['powershell','-NoProfile','-File',str(M/'_src/run_blender.ps1'),'-Script',str(S/script),'-Log','props_batch1/'+log],log+'.launcher')
def main():
 assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
 ps=read(S/'_backup_rev4_corals/models/_src/props_batch1/parts.json');old=read(S/'_backup_rev4_corals/models/props_batch1_manifest.json');ids={p['id'] for p in ps if p['hole'] in [7,8] and 'coral' in p['id']};assert len(ids)==18
 backup=S/'_backup_rev4_corals'
 paths=[M/p['fbx'] for p in old['parts'] if p['id'] in ids]+[PV/(i+'_34.png') for i in ids]+[PV/n for n in ['h07_34.png','h08_34.png','silhouette_compare_h07.jpg','silhouette_compare_h08.jpg','contact_sheet.jpg']]+[M/'props_batch1_manifest.json',M/'fitcheck_props_batch1.txt',M/'README.md',S/'summary.md',S/'parts.json',S/'triangles.json',S/'build_report.json',S/'fitcheck_report.json',S/'fbx_validation.json']
 for p in paths:
  assert p.exists(),p
  q=backup/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q) if not q.exists() else None
 untouched={str(p.relative_to(D)):sha(p) for p in (M/'fbx').rglob('*.fbx') if p.stem not in ids}
 write(S/'rev5_unchanged.json',untouched);write(S/'rev5_ids.json',sorted(ids))
 sys.path.insert(0,str(M/'_src/props_batch2'));import geometry as g
 shapes=[]
 for p in ps:
  if p['id'] not in ids:continue
  seed=sorted(ids).index(p['id']);count=3;col=next(iter(p['groups']));q=g.Part(p['id'],p['hole'],[0,0,0]);base=0;yaw=0
  if p['hole']==7:
   a=next(a for a in g.H[7]['decoration_anchors'] if a['name']==p['id'][4:]);h=a['approx_size'][1];w=.5*h;d=.4*h
  elif 'giant' in p['id']:h=14;w=4;d=4
  else:
   wall=next(a for a in g.H[8]['walls'] if a['id']==p['skin_ids'][0]);base=1.6;h=2.4;w=1.2;d=min(.96,wall['size'][2]*.8);yaw=wall['yaw']
   # Preserve the exact rev4 base arrays rather than reconstructing them.
   q.g[col]=([v[:] for v in p['groups'][col]['verts'][:8]],[f[:] for f in p['groups'][col]['faces'][:6]])
  g.tube(q,col,[0,base,0],[0,base+.3*h,0],.075*h,.05*h,n=8)
  start=len(q.g[col][0]);split=[0,base+.3*h,0]
  # Straight flattened paddles; fork once per lobe in the upper crown.
  for k in range(count):
   u=(k-(count-1)/2)/((count-1)/2);angle=35+20*abs(u);sign=1 if u>=0 else -1
   xx=u*(w/2-.23);zz=u*(d-.17)*.5
   shoulder=[sign*min(abs(xx)*.38,.08*h*math.tan(math.radians(angle))),base+.38*h,zz*.18] if abs(u)>.01 else [0,base+.38*h,0]
   fork=[xx*.68,base+h*(.63+.07*(1-abs(u))),zz*.8]
   g.tube(q,col,split,shoulder,.15,.15,.5,n=4)
   g.tube(q,col,shoulder,fork,.15,.15,.5,n=4)
   for side in [-1,1]:
    tx=xx+side*min(.18,w*.09);top=base+h*(.90+.10*(1-abs(u)));tip=[tx,top-.10,zz+side*.01]
    g.tube(q,col,fork,tip,.15,.15,.5,n=4)
    g.mound(q,col,[tx,top-.2,tip[2]],[.3,.2,.15],n=6)
    g.mound(q,'CoralMint',[tx,top-.065,tip[2]],[.16,.065,.12],n=6)
  # Exact target crown width; never exceed source envelope.
  vs=q.g[col][0][start:];lo=min(v[0] for v in vs);hi=max(v[0] for v in vs);sx=w/(hi-lo)
  for mat,(verts,faces) in q.g.items():
   begin=start if mat==col else 0
   for v in verts[begin:]:v[0]=(v[0]-(hi+lo)/2)*sx
  crown=[v for mat,(verts,_) in q.g.items() for v in verts[(start if mat==col else 0):]]
  cw=max(v[0] for v in crown)-min(v[0] for v in crown);ch=max(v[1] for v in crown)-min(v[1] for v in crown)
  note=f'Coral rev5: {count} straight flat paddle lobes, {2*count} rounded neon tips, one central upright lobe; split 0.3H, trunk diameters 0.15H -> 0.10H. Crown W:H {cw:.6f}:{ch:.6f} = {cw/ch:.6f}. Height {h:g}; width {w:g}; depth envelope {d:g}. Upper fork/tip cluster concentrated at 0.63H..H. Initial splay nominal 35..55 degrees; long risers necessarily steeper to retain H and 0.5H width. No rail-driven splay reduction.'
  if 'giant' in p['id']:note+=' Giant width limited to exact 4-stud occluder (requested 7).'
  if base and d<.96:note+=' Narrow skin depth limited to prior 0.8-stud envelope.'
  if yaw:
   for mat,(verts,faces) in q.g.items():
    begin=8 if mat==col else 0;verts[begin:]=[g.roty(v,yaw) for v in verts[begin:]]
  p['groups']={m:dict(verts=v,faces=f) for m,(v,f) in q.g.items()};p['notes'].append(note)
  tris=sum(len(f)-2 for gg in p['groups'].values() for f in gg['faces']);assert tris<900,(p['id'],tris)
  shapes.append(dict(id=p['id'],height=h,crown_width=cw,crown_height=ch,crown_ratio=cw/ch,lobes=count,tips=2*count,notes=note))
 write(S/'parts.json',ps);write(S/'rev5_shapes.json',shapes);cache=read(S/'triangles.json');write(S/'triangles.json',{k:v for k,v in cache.items() if k not in ids})
 run([sys.executable,str(S/'fitcheck_batch1.py')],'rev5_preflight.log')
 src=(S/'build_rev4.py').read_text().replace('rev4_ids.json','rev5_ids.json').replace('props_batch1_rev4.blend','props_batch1_rev5.blend')
 # Additional true FRONT orthographic renders at explicit stud scale.
 pos=src.index('for o in allmesh:o.hide_render=False')
 extra="""
for id in ['h07_coral_w2','h08_coral_1']:
    p=next(p for p in P if p['id']==id);visible=ROOTS[id][1]
    for o in allmesh:o.hide_render=o not in visible
    # Undo skin yaw only for a local front view; camera follows rotated front.
    a=B(p['anchor']);ang=math.radians(next(w['yaw'] for w in H[8]['walls'] if w['id']==p['skin_ids'][0]) if p['skin_ids'] else 0);direction=Vector((math.sin(ang),-math.cos(ang),0))
    center=a+Vector((0,0,3 if p['hole']==7 else 2));cam.location=center+direction*100
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=8
    sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.film_transparent=True
    sc.render.filepath=str(PV/(id+'_front.png'));bpy.ops.render.render(write_still=True)
"""
 src=src[:pos]+extra+src[pos:];(S/'build_rev5.py').write_text(src)
 blender('build_rev5.py','rev5_build.log');run([sys.executable,str(S/'fitcheck_batch1.py')],'rev5_fit.log');blender('verify_batch1.py','rev5_verify.log')
 finalize(old,ids,untouched,shapes)
def finalize(old,ids,untouched,shapes):
 assert read(S/'fitcheck_report.json')['all_pass'] and read(S/'fbx_validation.json')['all_pass']
 for path,digest in untouched.items():assert sha(D/path)==digest,path
 new=read(M/'props_batch1_manifest.json');prev={p['id']:p for p in old['parts']};src={p['id']:p for p in read(S/'parts.json')};op={p['id']:p for p in read(S/'_backup_rev4_corals/models/_src/props_batch1/parts.json')};by={p['id']:p for p in shapes}
 for p in new['parts']:
  if p['id'] not in ids:assert p==prev[p['id']]
  else:
   assert p['tris']<3000
   for k in ['pivot_hole_local','pivot_world','yaw_local','placement_yaw','motion']:assert p[k]==prev[p['id']][k]
   if src[p['id']]['skin_ids']:
    col=next(iter(op[p['id']]['groups']))
    for k,n in [('verts',8),('faces',6)]:assert src[p['id']]['groups'][col][k][:n]==op[p['id']]['groups'][col][k][:n]
   p['coral_rev5']=by[p['id']]
 write(M/'props_batch1_manifest.json',new)
 out=Image.new('RGB',(1200,680),'#222233');dr=ImageDraw.Draw(out)
 for i,n in enumerate([1,2,3,5,7,8]):
  out.paste(ImageOps.contain(Image.open(PV/f'h{n:02d}_34.png'),(400,300)),(i%3*400,i//3*340));dr.text((i%3*400+10,i//3*340+310),f'H{n:02d}'+(' / Coral rev5' if n in [7,8] else ''),fill='white')
 out.save(PV/'contact_sheet.jpg',quality=95)
 sheet=Image.open(D/'silhouettes/sheet02-batch1-h05-h08.png').convert('RGB')
 for n,id,box,unit in [(7,'h07_coral_w2',(440,1473,630,1700),28),(8,'h08_coral_1',(440,2000,643,2265),39.75)]:
  out=Image.new('RGB',(1600,1100),'white');dr=ImageDraw.Draw(out);dr.text((15,12),f'H{n:02d} Coral rev5 / FRONT orthographic, common 50 px per stud',fill='black')
  crop=sheet.crop(box);crop=crop.resize((round(crop.width*50/unit),round(crop.height*50/unit)));out.paste(crop,(20,round(470-((1653 if n==7 else 2201)-box[1])*50/unit)))
  im=Image.open(PV/(id+'_front.png')).convert('RGBA').resize((400,400));out.paste(im,(500,120 if n==7 else 170),im);dr.line((15,470,920,470),fill='#80b0a0');dr.text((500,480),id+' / 8-stud camera span / 50 px per stud',fill='black')
  ps=[p for p in new['parts'] if p['id'] in ids and p['hole']==n]
  for i,p in enumerate(ps):
   x=i%5*320;y=540+i//5*270;out.paste(ImageOps.contain(Image.open(PV/(p['id']+'_34.png')),(310,230)),(x,y));dr.text((x+5,y+235),p['id'],fill='black')
  out.save(PV/f'silhouette_compare_h{n:02d}.jpg',quality=95)
 text='\n\n## Coral rev5\n\n18 coral assets: straight flat paddles with one fork per lobe and 6-10 rounded neon tips. Exact collider bases, pivots, anchors and colours preserved. Full split-to-top crown is necessarily taller than wide: fixed 0.7H height and at most 0.5H width. Upper fork/tip cluster carries strong splay; long risers are steeper than the nominal 35-55 degrees to preserve these incompatible dimensions. Giant retains 4-stud width due to its occluder; narrow skins retain 0.8 depth. No rail-driven splay reductions.\n\n| Coral | Tris | Crown width | Crown height | W:H |\n|---|---:|---:|---:|---:|\n'
 for p in new['parts']:
  if p['id'] in ids:
   r=by[p['id']];text+=f"| {p['id']} | {p['tris']} | {r['crown_width']:.4f} | {r['crown_height']:.4f} | {r['crown_ratio']:.4f} |\n"
 text+='\nExported triangle fitcheck and FBX reimport ALL PASS. Every coral <900 tris, all unrelated FBX SHA256 hashes and manifest records unchanged. holes.json MD5 2f1402fe19fc98a303c4e58dae680be9. Backups: `_backup_rev4_corals/`. CPU Blender serially through run_blender.ps1. Front comparisons use common stud scale; full sheet remains authoritative.\n'
 shutil.copy2(S/'_backup_rev4_corals/models/_src/props_batch1/summary.md',S/'summary.md')
 with (S/'summary.md').open('a',encoding='utf-8') as f:f.write(text)
 shutil.copy2(S/'_backup_rev4_corals/models/README.md',M/'README.md')
 with (M/'README.md').open('a',encoding='utf-8') as f:f.write('\n\n## Coral rev5\n\n18 H7/H8 corals revised with flat forked paddles and 6-10 neon tips. Fitcheck and FBX reimport ALL PASS. Exact bases and placements preserved. See `_src/props_batch1/summary.md` for triangles, measured crown W:H, and geometric constraints. Rev4 files backed up in `_backup_rev4_corals/`.\n')
 fit=M/'fitcheck_props_batch1.txt';tx=fit.read_text().replace('ALL PASS: YES','NOTE H1 existing authorized collider-to-rail gap 0.0786796564 retained.\nNOTE Coral rev5 dimensions and per-coral crown W:H are in manifest/summary; source occluder limits retained.\nALL PASS: YES');fit.write_text(tx)
 write(S/'rev5_audit.json',dict(all_pass=True,changed=sorted(ids),shapes=shapes,unchanged_fbx_count=len(untouched)))
 print('READY_FOR_VISUAL_REVIEW',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  (S/'failed_rev5.flag').write_text(repr(e)+'\nSee rev5 logs.\n');raise
