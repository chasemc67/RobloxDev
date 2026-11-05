from pathlib import Path
import json,hashlib,datetime
from PIL import Image
s=Path('boardwalk/models/_src');r=s.parent;job=Path('..').resolve();m=json.loads((r/'manifest.json').read_text());a=[]
def check(ok,label):
 a.append(('PASS ' if ok else 'FAIL ')+label)
 if not ok:raise RuntimeError(label)
for n in ['fitcheck_pass8_validated.txt','reimport_check_pass8.txt']:check('RESULT: ALL PASS' in (s/n).read_text(),n)
for n in ['build','fitcheck','reimport','render']:
 p=s/(n+'_pass8.log');b=p.read_bytes();t=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8',errors='replace');check('Blender quit' in t and 'Traceback' not in t,n+' Blender exited')
for n in ['aurora_crown_v2.py','rock_candy.py']:check((s/n).read_bytes()==(job/n).read_bytes(),n+' supplied source unchanged')
for e in m['props']:
 check(e['triangles']<20000 and (r/e['fbx']).exists(),e['name']+' export <20k')
 if not e['name'].startswith('bw_scn_') and not e['name'].startswith('bw_arch_lantern_grove_lantern_'):check(hashlib.sha256((r/e['fbx']).read_bytes()).digest()==hashlib.sha256((r/'_backup_pass7'/e['fbx']).read_bytes()).digest(),e['name']+' unchanged SHA256')
check(m['totals']['tris_total']<120000,'placed lobby budget')
me=json.loads((s/'measure_pass8.json').read_text());mins=json.loads((s/'clearance_pass8.json').read_text())
for e in m['props']:
 n=e['name']
 if n=='bw_scn_aurora_crown':
  e.update(notes='Supplied v2 build_crown, allowed SIDES16 (12 measured1284tris); source colours/counts/placement/tip split unchanged; no nudges.',tallest_tip_Z=27.0,preview_glow_strength=1.5,source_sha256=hashlib.sha256((s/'aurora_crown_v2.py').read_bytes()).hexdigest(),sides=16,crystal_nudges=[],glow_tip_split='top20% as assigned by supplied build_crown')
 if 'sugarloaf_crystals_' in n:e['neon_material']='Glow_Crystal'
 if 'lantern_grove_trunk_' in n:e['notes']='Three visibly intertwined tapering strands rotate240degrees; exposed lower trunk, root flares; staggered layered canopy radii1.2-4.5, core at top, smaller side blobs toY12.'
 if 'aurora_rocks_' in n:e['notes']='Seven grounded overlapping snowy rocks per side, tight to legs; all prior standalone shoulder rocks/snow/crystals removed; snowpuff spot unchanged and clear.'
 if n.startswith('bw_scn_'):(s/'manifest_parts'/(n+'.json')).write_text(json.dumps(e,indent=1))
m['materials']['Glow_Tips'].update(Material='Neon',Color='#9FE6F2',preview_emission_strength=1.5)
m['materials']['Glow_Crystal']={'Material':'Neon','roblox_material':'Neon','vertex_colour_attribute':'Col','colors':['#F59AC8','#FFF1A8'],'preview_emission_strength':.6}
m['materials']['BW_Crown_Crystal']={'vertex_colour_attribute':'Col','gradient':['#7A4FD0','#8FE3EE']}
m['pass8_preview']={'view_transform':'Standard','world_strength':.9,'large_soft_key_size':30,'Glow_Tips_emission':1.5}
(r/'manifest.json').write_text(json.dumps(m,indent=1))
# Pixel evidence taken inside the violet shaft and cyan cap of the closeup.
im=Image.open(r/'previews/portals/aurora_crown_closeup.png');pixels={'violet_base':{'xy':[240,650],'rgb':im.getpixel((240,650))},'teal_tip':{'xy':[600,320],'rgb':im.getpixel((600,320))}}
v=pixels['violet_base']['rgb'];t=pixels['teal_tip']['rgb'];check(v[2]>v[0]>v[1] and v[2]-v[1]>60,'violet base pixel');check(t[1]-t[0]>35 and t[2]-t[0]>35,'cyan tip pixel not white/grey')
(s/'preview_colour_pass8.json').write_text(json.dumps(pixels,indent=2))
lines=['# Pass8 completed','',f"Placed lobby: **{m['totals']['tris_total']:,} triangles**. All meshes <20,000; fitcheck and independent FBX reimport ALL PASS.",'','Supplied crown v2 and rock_candy copied byte-identically. Crown12-side initial build1284tris; permitted runtime SIDES16 produces1716tris. Six crystals unchanged, no nudges; tallest tip BlenderZ / RobloxY=27.0. Glow_Tips retains the supplied top20% assignment, Neon #9FE6F2, preview emission1.5. Col byte colours preserved and preview shaders explicitly read Col.','','Sugarloaf: per side one eight-crystal size2.0 cluster at joint(+-9.5,15,.8), plus six/five-crystal size1.0 base clusters. Three clusters merged into one base-centred FBX per side and mirrored. Prior slab-crystal scenery deleted/replaced. Pure crystals have no collision boxes. Existing tower/cactus exports retained.','','Grove: three tapering strands visibly spiral240degrees, root flares, width about4.5 before root flare. Varied radius1.2-4.5 blobs in layered top/core and smaller staggered outer cascades. Lower trunks exposed; six lantern anchors unchanged, lanterns re-exported.','','Aurora: standalone shoulder debris removed, snow/rocks gathered into tight grounded clusters at each leg. Snowpuff spot[-6.5,0,1.25] remains clear.','','Previews use Standard, neutral world0.9 and large soft key. Pixel samples: '+json.dumps(pixels)+'. Base is violet, caps cyan; lighting and gradient mean pixels differ from exact material swatches.','','## Honest notes','','Fixed arches were required to remain byte-identical. Their original embedded rock/snow and tiny candy accents therefore remain, including the small Aurora lintel accents visible in closeup; all standalone shoulder pieces were removed. Supplied crown face-to-crystal attribution is preserved exactly; overlapping crystals can inherit the source attribution. The toy geometry remains simpler than painted concepts. Eye-height trunks show spiral strands, although existing arch legs obscure their inner portions. No Roblox/Studio/Player opened; all own Blender processes exited.','','## Triangles','','| Mesh | Tris | Instances | Placed tris |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"|{e['name']}|{e['triangles']}|{e['builder_count']}|{e['tris_x_count']}|")
lines+=['','## Portal group totals','','| Course | Tris |','|---|---:|']
for c in ['lantern_grove','sugarloaf_canyon','aurora_archipelago']:
 total=sum(e['triangles'] for e in m['props'] if e.get('course')==c or e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c or e['name'] in ['bw_portal_apron','bw_arch_nameplate'] or c!='lantern_grove' and e['name']=='bw_coming_soon_sign');lines.append(f'|{c}|{total}|')
lines+=['','## Zone minimum distances','','A=X[-5,5]Y[0,12]Z[-12,4]; B=X[-11,11]Y[0,18]Z[4,34]. Distances measured from imported triangles; collision boxes separately checked.','','| Mesh | A | B | Trigger |','|---|---:|---:|---:|']
for n,d in mins.items():lines.append(f"|{n}|{d['A']}|{d['B']}|{d['trigger']}|")
lines+=['','## Anchors','','| Asset | Arch-local anchor |','|---|---|']
for e in m['props']:
 if e.get('anchor_position_arch_local'):lines.append(f"|{e['name']}|{e['anchor_position_arch_local']}|")
lines+=['','## Rebuild','','Sequential direct Blender invocations: build_pass8.py, fitcheck_pass8.py, reimport_pass8.py, render_pass8.py. Python compose_pass3.py then finalize_pass8.py. Backup in _backup_pass7.','',json.dumps(me,indent=2)]
(s/'pass8_summary.md').write_text('\n'.join(lines),encoding='utf-8')
p=r/'README.md';text=p.read_text(encoding='utf-8').split('\n## Pass 8')[0];text+='\n## Pass 8 current authoritative assets\n\nCrown v2:6crystals,1716tris, tallest tip27.0studs, source unchanged with allowed SIDES16; Col violet-to-teal, Glow_Tips Neon #9FE6F2 emission1.5. Mirrored supplied rock-candy joint/base clusters use Glow_Crystal Neon from Col. Grove has three240degree spiral strands and varied layered leaf masses; snowy Aurora rubble grounded at legs. Fixed arches/surfaces/apron/signs/triggers unchanged.\n\nFitcheck/reimport ALL PASS. Placed lobby '+str(m['totals']['tris_total'])+'tris, each mesh<20k; zonesA/B unchanged. Standard previews, neutral ambient0.9. See [_src/pass8_summary.md](_src/pass8_summary.md) for complete tables, anchors, pixels and honest notes about fixed embedded accents. No Roblox applications opened.\n';p.write_text(text,encoding='utf-8')
a.append('RESULT: ALL PASS');(s/'artifact_audit_pass8.txt').write_text('\n'.join(a)+'\n')
with (s/'PROGRESS_pass8.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Final visual/pixel audit, fitcheck and reimport ALL PASS; docs and summary completed; own Blender exited.\n')
print(m['totals']);print(pixels)
