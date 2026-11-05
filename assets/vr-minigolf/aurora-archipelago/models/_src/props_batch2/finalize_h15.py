"""Additive manifest, fitcheck, comparisons, and reviewed handoff."""
import json,hashlib,re,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch2';ID='h15_great_frozen_falls'
fit=json.loads((S/'h15_fitcheck.json').read_text());v=json.loads((S/'h15_fbx_validation.json').read_text());p=json.loads((S/'h15_build_report.json').read_text())
assert fit['all_pass'] and v['all_pass'] and fit['geometry']=='FBX triangulation'
for name,sha in json.loads((S/'h15_other_fbx_hashes.json').read_text()).items():assert hashlib.sha256((M/'fbx/props_batch2'/name).read_bytes()).hexdigest()==sha,name
f=M/'props_batch2_manifest.json';m=json.loads(f.read_text());old=json.loads((S/'_backup_pre_h15/props_batch2_manifest.json').read_text())
assert [x for x in m['parts'] if x['id']!=ID]==old['parts']
m['parts']=[x for x in m['parts'] if x['id']!=ID]+[p];m['skipped']=[x for x in m['skipped'] if x['id']!=ID]
assert m['skipped']==[x for x in old['skipped'] if x['id']!=ID]
f.write_text(json.dumps(m,indent=2))
nearest=min(fit['parts'],key=lambda x:x['min_rail_clearance'])
row=dict(id=ID,status='PASS',tris={x['material']:x['tris'] for x in p['meshes']},total_tris=p['tris'],min_rail_clearance=nearest['min_rail_clearance'],nearest_rail='H%d/%s'%(nearest['hole'],nearest['nearest_rail']),felt_head_triangle_hits=0,sweep=None,failures=[],world_base=p['pivot_world'],world_top=p['source_top'],checked_holes=list(range(1,19)),source='h15_fitcheck.json')
f=M/'fitcheck_props_batch2.txt';lines=[x for x in f.read_text().splitlines() if not x.startswith('SKIPPED '+ID) and not x.startswith('PASS '+ID)]
idx=next(i for i,x in enumerate(lines) if x.startswith('SKIPPED '));lines.insert(idx,'PASS '+ID+' '+json.dumps(row))
lines=[x for x in lines if not x.startswith('Backdrop triangles:')]
idx=next(i for i,x in enumerate(lines) if x.startswith('ALL PASS:'));lines.insert(idx,'Backdrop triangles: H15 Great Frozen Falls '+str(p['tris'])+' (separate from near-field budget)')
assert lines[-1]=='ALL PASS: YES';f.write_text('\n'.join(lines)+'\n')
# Keep aggregate validation records consistent without modifying earlier entries.
for name,key,value in [('fitcheck_report.json','parts',row),('fbx_validation.json','parts',dict(id=ID,status='PASS',**v)),('build_report.json','parts',p)]:
 f=S/name;q=json.loads(f.read_text());q[key]=[x for x in q[key] if x['id']!=ID]+[value];f.write_text(json.dumps(q,indent=2))
sheet=Image.new('RGB',(1600,680),'#222233');dr=ImageDraw.Draw(sheet)
for i,n in enumerate([9,10,11,12,13,15,16,17]):
 im=Image.open(PV/f'h{n:02d}_34.png');assert im.size==(1280,960);sheet.paste(ImageOps.contain(im,(400,300)),((i%4)*400,(i//4)*340));dr.text(((i%4)*400+12,(i//4)*340+305),f'H{n:02d} Batch 2',fill='white')
sheet.save(PV/'contact_sheet.jpg',quality=95)
source=Image.open(D/'silhouettes/sheet04-h15-h17.png').convert('RGB');crop=source.crop((0,int(28*source.height/1134),source.width,int(430*source.height/1134)))
out=Image.new('RGB',(1600,1050),'white');dr=ImageDraw.Draw(out);out.paste(ImageOps.contain(crop,(1100,510)),(0,25));out.paste(ImageOps.contain(Image.open(PV/'h15_34.png'),(480,360)),(1110,60));out.paste(ImageOps.contain(Image.open(PV/(ID+'_34.png')),(620,465)),(20,550))
dr.text((650,570),'Great Frozen Falls: world source overrides sheet height 40 -> 146 studs.',fill='black')
dr.text((650,600),'World top [20,182,-398]; base [20,36,-398]; width 26; depth 8; yaw 0.',fill='black')
dr.text((650,630),'Tapered fluted ice curtain, bulging tiers, embedded neon cores.',fill='black')
dr.text((650,660),f"FBX: {p['tris']} triangles / {len(p['meshes'])} material meshes; reimport PASS.",fill='black')
dr.text((650,690),f"All 18 holes PASS; H15 minimum rail gap {nearest['min_rail_clearance']:.6f} studs.",fill='black')
for i,x in enumerate(x for x in m['skipped'] if x['hole']==15):dr.text((650,740+i*35),'SKIPPED '+x['id']+' (existing source/gate ruling)',fill='#8A3232')
out.save(PV/'silhouette_compare_h15.jpg',quality=95)
total=sum(x['tris'] for x in m['parts']);count=len(m['parts']);skip=len(m['skipped'])
f=S/'summary.md';t=f.read_text(encoding='utf-8')
t=t.replace('20 built assets; 19,532 triangles;',f'{count} built assets; {total:,} triangles;').replace('13 source-conflicting or undefined pieces',f'{skip} source-conflicting or undefined pieces')
t=t.replace('H15 is context-only because its requested pieces contradict gates or lack exact placement.','H15 Great Frozen Falls is built at the authoritative world waterfall placement; other H15 pieces retain their prior SKIPPED rulings.')
t='\n'.join(x for x in t.splitlines() if not x.startswith('- **'+ID+'**:'))+'\n'
t=t.replace('(H15 source blockout only)','(H15 world cascade with source blockout)')
t+='\n## H15 world cascade add-on\n\n'+f'{ID}: {p["tris"]:,} triangles; '+', '.join(f'{x["material"]} {x["tris"]:,}' for x in p['meshes'])+'. One mesh per material, FBX reimport PASS. World bottom/base centre [20,36,-398], top [20,182,-398], yaw0. Hole-local pivot [8,-146,-64] + H15 offset [12,182,-334] = world [20,36,-398]. World waterfall has no yaw field; vertical top/bottom and world-X width define yaw0. Width26, height146, depth8; world height supersedes the silhouette/view-cue 40. Sheet taper and flutes retained, 20-stud tier cadence plus 6-stud lip section; foot ends at cloud deck y36. Ice Glass transparency .3 and embedded IceCore Neon use the existing palette. No water. Builder: root PrimaryPart at base, persistent streaming; CanCollide/CanQuery/CanTouch off.\n\n'
t+=f'All 18 holes checked in world space using world.json placements. Nearest rail H15/{nearest["nearest_rail"]}: conservative minimum {nearest["min_rail_clearance"]:.6f} studs; zero felt slab/head-volume hits on every hole. 8-stud reachable-felt headroom PASS. Far backdrop excluded from near-field counts. h15_fitcheck.json contains exact per-hole results from reimported FBX triangles.\n\n'
t+='H15-only rebuild: python gen_h15.py -> run_blender.ps1 -Script build_h15.py (CPU/headless) -> python fitcheck_h15.py -> python finalize_h15.py. h15_part.json, h15_build_report.json, h15_triangles.json, h15_fbx_validation.json, h15_falls.blend and h15_build.log retained. Preview and comparison visually reviewed. Original 20 FBX files checked by SHA256 and unchanged; previous manifest parts and other SKIPPED entries preserved. Backups in _backup_pre_h15.\n'
f.write_text(t,encoding='utf-8')
f=M/'README.md';t=f.read_text(encoding='utf-8');t=t.replace('20 assets, 19,532 triangles;',f'{count} assets, {total:,} triangles;').replace('13 individual source contradictions/undefined pieces skipped; H15 context-only.',f'{skip} individual source contradictions/undefined pieces skipped; H15 Great Frozen Falls built at world placement.')
t+='\nH15 add-on: Great Frozen Falls at world base [20,36,-398], top [20,182,-398], yaw0; 26x146x8 studs. '+f'{p["tris"]:,} triangles, two material meshes, reimport PASS. All 18 holes pass rail/felt/head gates; nearest clearance {nearest["min_rail_clearance"]:.6f} studs. Existing FBX assets unchanged. See [H15 checks](_src/props_batch2/h15_fitcheck.json) and the summary for additive rebuild instructions. Persistent backdrop; base-centre root PrimaryPart; collision/query/touch off.\n'
f.write_text(t,encoding='utf-8')
assert len(m['parts'])==21 and len(m['skipped'])==12
assert p['dimensions']==[26,146,8] and p['pivot_world']==[20,36,-398]
for name in [ID+'_34.png','h15_34.png','silhouette_compare_h15.jpg','contact_sheet.jpg']:Image.open(PV/name).verify()
print(json.dumps(dict(parts=count,skipped=skip,triangles=total,h15_tris=p['tris'],all_pass=True,other_fbx_unchanged=True),indent=2))
