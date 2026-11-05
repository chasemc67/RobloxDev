import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
old=read(S/'rev4_before.json');untouched=read(S/'rev4_unchanged.json');audit={}
for path,digest in untouched.items():assert sha(D/path)==digest,path
ranges={7:('sheet02-batch1-h05-h08.png',1432,1696),8:('sheet02-batch1-h05-h08.png',1696,2268),9:('sheet03-h09-h13.png',62,607),15:('sheet04-h15-h17.png',60,630),17:('sheet04-h15-h17.png',882,1728)}
for b,ns,changedholes in [(1,[1,2,3,5,7,8],[7,8]),(2,[9,10,11,12,13,15,16,17],[9,15,17])]:
 s=M/f'_src/props_batch{b}';pv=M/f'previews/props_batch{b}';ids=set(read(s/'rev4_ids.json'));m=read(M/f'props_batch{b}_manifest.json');fit=read(s/'fitcheck_report.json');ver=read(s/'fbx_validation.json');assert fit['all_pass'] and ver['all_pass']
 before={p['id']:p for p in old[str(b)]['parts']};by={p['id']:p for p in fit['parts']};src={p['id']:p for p in read(s/'parts.json')}
 for p in m['parts']:
  q=before[p['id']]
  if p['id'] not in ids:assert p==q,p['id']
  else:
   assert p['tris']<=3000 and p['max_mesh_tris']<20000
   for k in ['pivot_hole_local','pivot_world','yaw_local','placement_yaw','motion']:assert p[k]==q[k],(p['id'],k)
   assert by[p['id']]['status']=='PASS'
   assert Image.open(pv/(p['id']+'_34.png')).size==(1280,960)
   if b==1 and src[p['id']]['skin_ids']:
    og=read(s/'_backup_pre_rev4/_src/props_batch1/parts.json');op=next(v for v in og if v['id']==p['id']);col=next(iter(op['groups']))
    assert src[p['id']]['groups'][col]['verts'][:8]==op['groups'][col]['verts'][:8],p['id']
    assert src[p['id']]['groups'][col]['faces'][:6]==op['groups'][col]['faces'][:6],p['id']
 cols=3 if b==1 else 4;out=Image.new('RGB',(cols*400,680),'#222233');dr=ImageDraw.Draw(out)
 for i,n in enumerate(ns):
  out.paste(ImageOps.contain(Image.open(pv/f'h{n:02d}_34.png'),(400,300)),(i%cols*400,i//cols*340));dr.text((i%cols*400+12,i//cols*340+308),f'H{n:02d}'+(' / Rev4' if n in changedholes else ''),fill='white')
 out.save(pv/'contact_sheet.jpg',quality=95)
 for n in changedholes:
  name,lo,hi=ranges[n];sheet=Image.open(D/'silhouettes'/name).convert('RGB');parts=[p for p in m['parts'] if p['id'] in ids and p['hole']==n];hh=550+250*math.ceil(len(parts)/4)
  out=Image.new('RGB',(1600,hh),'white');dr=ImageDraw.Draw(out)
  out.paste(ImageOps.contain(sheet.crop((0,lo,sheet.width,min(hi,sheet.height)))),(0,0)) if False else None
  out.paste(ImageOps.contain(sheet.crop((0,lo,sheet.width,min(hi,sheet.height))),(1090,480)),(0,40));out.paste(ImageOps.contain(Image.open(pv/f'h{n:02d}_34.png'),(490,368)),(1100,40))
  dr.text((12,12),f'H{n:02d}: supplied silhouette / Rev4 CPU renders',fill='black');dr.text((1100,430),'Rev4 brief supersedes earlier crown/no-gap notes.',fill='black')
  for i,p in enumerate(parts):
   x=i%4*400;y=550+i//4*250;out.paste(ImageOps.contain(Image.open(pv/(p['id']+'_34.png')),(390,215)),(x,y));dr.text((x+8,y+218),p['id'],fill='black')
  out.save(pv/f'silhouette_compare_h{n:02d}.jpg',quality=95)
 notes=['NOTE H1 collider-to-rail gap 0.0786796564 retained under existing exception.'] if b==1 else ['NOTE H17 crystal_piers and ice_bridge intentionally cover their own railed felt; own rail skins and below-felt decks are exempt only within authorized footprints.','NOTE H15 ice_parapet intentionally crosses the lip; felt/head overlap authorized, rail clearance still checked. IceGuard transparency 0.9 retained.','NOTE H12 paddle_wheel unchanged; authorized 0.06 felt clearance retained.','NOTE Rev4 coral_spit nose flare reduced locally from 0.3 to 0.18; top y=-0.45 below felt slab.']
 ff=M/f'fitcheck_props_batch{b}.txt';tx=ff.read_text();tx=tx.replace('ALL PASS: YES','\n'.join(notes)+'\nALL PASS: YES');ff.write_text(tx)
 tx='\n\n## Rev4\n\n'+('18 corals: 3-5 separate flattened fan lobes with visible crown gaps, rounded neon tips and trunks tapering 0.15H to 0.10H at the 0.3H split. Exact H8 collider bases, anchors, pivots and existing hues preserved. Prior giant/narrow-footprint limits retained.' if b==1 else 'Bridge: bevelled timber rails, posts every 4 studs, connected lumpy ~0.3 white snow caps and frosted deck edges. Parapet: seven chunky ice blocks with tops varying -0.4..+0.4, frosted tops and front icicles. Spit: bumpy pink/purple rock sides with polyp bumps, irregular skirt flaring 0.3; nose flare locally reduced to 0.18. Top lowered below the felt slab to y=-0.45. Purple rock uses the existing AuroraViolet hue without emission.')
 tx+='\n\n| Asset | Tris before | Tris after | Rail minimum |\n|---|---:|---:|---:|\n'
 for p in m['parts']:
  if p['id'] in ids:tx+=f"| {p['id']} | {before[p['id']]['tris']} | {p['tris']} | {by[p['id']]['min_rail_clearance']:.6f} |\n"
 tx+='\n'+ '\n'.join(notes)+'\n\nEvery changed piece <=3000 triangles; every material mesh <20k. Exported triangle/OBB fitcheck ALL PASS: YES; FBX reimport ALL PASS: YES. Unrelated FBX hashes and manifest records unchanged. Backups: `_backup_pre_rev4/`, retaining models-relative paths. Changed hole/asset previews, silhouette comparisons and contact sheet refreshed. holes.json MD5 unchanged: `2f1402fe19fc98a303c4e58dae680be9`.\n\nSource pipeline: rev4.py preparation, amend_rev4.py and amend_spit_rev4.py visual/budget refinements, selective build_rev4.py/build_ice_rev4.py/build_spit_rev4.py, fitcheck_batch*.py and verify_batch*.py. All Blender jobs ran headless, serially through run_blender.ps1 with Cycles CPU. Current parts.json is the final source; historical generators must not be rerun blindly. Evidence logs and rev4_audit.json are in props_batch2.\n'
 with (s/'summary.md').open('a',encoding='utf-8') as f:f.write(tx)
 audit[str(b)]=dict(changed=sorted(ids),all_pass=True,changed_tris={p['id']:p['tris'] for p in m['parts'] if p['id'] in ids})
with (M/'README.md').open('a',encoding='utf-8') as f:f.write('\n\n## Rev4\n\n21 requested assets revised: 18 H7/H8 corals, H17 ice bridge, H15 ice parapet and H9 coral spit. Separate fan lobes and neon tips; bevelled snow-capped bridge rails/posts; uneven frosted ice blocks/icicles; pink/purple bumpy coral skirt. Every changed piece <=3000 tris. Both exported fitchecks and FBX reimport checks ALL PASS. Unrelated exports, anchors/pivots, exact H8 collider bases and existing exceptions preserved. Spit nose flare reduced to 0.18 and skirt top lowered below felt slab. Backups in each batch `_backup_pre_rev4`. See both summaries Rev4 sections for before/after triangles and measured clearances.\n')
(S/'rev4_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
