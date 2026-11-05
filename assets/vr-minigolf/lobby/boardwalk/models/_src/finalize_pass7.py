from pathlib import Path
import json,datetime,hashlib,math
from PIL import Image
S=Path(__file__).parent;R=S.parent;JOB=R.parent.parent.parent
m=json.loads((R/'manifest.json').read_text());mins=json.loads((S/'clearance_pass7.json').read_text());measures=json.loads((S/'measure_pass7.json').read_text());audit=[]
def check(ok,label):
 audit.append(('PASS ' if ok else 'FAIL ')+label)
 if not ok:raise RuntimeError(label)
for f in ('fitcheck_pass7_validated.txt','reimport_check_pass7.txt'):check('RESULT: ALL PASS' in (S/f).read_text(),f)
for f in ('build_pass7.log','render_pass7.log','fitcheck_pass7.log','reimport_pass7.log'):
 raw=(S/f).read_bytes();t=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
 check('Traceback' not in t and ('Blender quit' in t or 'RESULT: ALL PASS' in t),f+' own invocation completed')
check((S/'props_arches.py').read_bytes()==(R/'_backup_pass6/_src/props_arches.py').read_bytes(),'arch generator unchanged')
check((S/'aurora_crown_explicit.py').read_bytes()==(JOB/'aurora_crown_explicit.py').read_bytes(),'explicit source byte-identical')
for e in m['props']:
 check((R/e['fbx']).is_file() and e['triangles']<20000,e['name']+' exported below20k')
 if not e['name'].startswith(('bw_scn_','bw_arch_lantern_grove_lantern_')):check(hashlib.sha256((R/e['fbx']).read_bytes()).digest()==hashlib.sha256((R/'_backup_pass6'/e['fbx']).read_bytes()).digest(),e['name']+' immutable SHA256')
check(sum(next(e['triangles'] for e in m['props'] if e['name']==i['asset']) for i in m['instances'])==m['totals']['tris_total']<120000,'placed triangle total verified')
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
 for view in ('eye','34'):
  p=R/f'previews/portals/{c}_{view}.png';im=Image.open(p);check(im.size==(960,960),p.name+' rendered960x960')
check(Image.open(R/'previews/portals/aurora_crown_closeup.png').size==(960,960),'crown closeup present')
check((R/'previews/portals/portals_vs_concepts.png').exists(),'concept comparison refreshed')
for e in m['props']:
 n=e['name']
 if n in measures:e['pass7_measurements']=measures[n]
 if 'lantern_grove_trunk_' in n:e['notes']='Pass7: chunky lobed trunk cross-section rotates150 degrees over21.5 studs; three helical bark strands, six root flares; layered rounded orange/red/gold foliage descends to aboutY6 along outer sides. Branch anchors unchanged.'
 if 'sugarloaf_tower_' in n:e['notes']='Pass7:17 smooth rounded sandstone segments with12-sided round section and3-segment soft bevels; approx27.7 tall, measured inward lean9.780degrees; four collision boxes follow centreline.'
 if 'sugarloaf_crystals_' in n:e['notes']='Pass7:18 candy shards per side, lengths3.0/3.9/4.8/5.7 studs, doubled radii vs pass6;12 on arch-leg/lintel joints,6 at bases; separate Neon pink/yellow materials.'
 if 'lollipop_cactus' in n:e['notes']='Pass7:full assembly normalized to exactly1.5x original pass5 bbox height; geometric red #E2574C / cream #F6EBD8 spiral disc on cream stick, green saguaro; disc face offset prevents z-fighting.'
 if n=='bw_scn_aurora_crown':
  e['notes']='Pass7 EXACT supplied six hexagonal crystals; bottom80% shaft, top20% Glow_Tips. Source unmodified, exported vertex positions independently compared against build_crown. Shared arch-base pivot per explicit source. No nudges; no old crown, shelves or footing.'
  e['source_sha256']=hashlib.sha256((S/'aurora_crown_explicit.py').read_bytes()).hexdigest();e['crystal_nudges']=[]
  e['tallest_top_arch_local_y']=14.5+27*math.cos(math.radians(10))
  for p in e['parts']:
   if p['material']=='Glow_Tips':p.update(Material='Neon',Color='#9FE6F2')
  m['materials']['BW_Crown_Crystal']={'vertex_colour_attribute':'Col','source_gradient':['#7A4FD0','#8FE3EE'],'note':'Exact explicit source colours; render shader uses imported Col'}
  m['materials']['Glow_Tips'].update(Material='Neon',Color='#9FE6F2',preview_emission_strength=4)
  (S/'manifest_parts'/f'{n}.json').write_text(json.dumps(e,indent=1))
m['pass7_art_review']={'reviewed':'all six views, supplied concept sheet and crown closeup','notes':'Exact explicit crown overrides earlier height and triangle richness targets. No Roblox opened.','source':'_src/pass7_summary.md'}
(R/'manifest.json').write_text(json.dumps(m,indent=1))
lines=['# Pass7 completed','',f"Placed lobby: **{m['totals']['tris_total']:,} triangles**, {len(m['instances'])} instances, {len(m['props'])} FBX files. Every file <20k; placed lobby <120k.",'','Fitcheck and independent FBX reimport: ALL PASS. Fixed arches, portal surfaces, apron, nameplate/sign, arch collision and triggers remain unchanged; SHA256 checked against _backup_pass6. No Roblox, Studio or Player was opened or touched. Own Blender invocations were sequential and exited.','','## Changes and review','','Grove trunks have a lobed cross-section with150-degree rotation, three helical strands and root flares. Layered rounded autumn leaf blobs descend to aboutY6 on the outside of each arch side and join the upper crown. The canopy lateral extent is about2 studs outside the chunky trunk outline. Six branch anchors remain unchanged and all lanterns were re-exported.','','Sugarloaf has17 smooth rounded band segments per side with3-segment bevels, not blocky slabs. Imported geometry measures approx27.7 studs high and9.780 degrees inward lean. Crystals are3.0-5.7 studs (2x pass6) with doubled radii;12 per side at tower/arch joints plus6 at bases. Cactus assembly is exactly1.5x pass5 height, about0.754x pass6, with a red/cream geometric spiral disc on a stick. Preview iteration removed coplanar disc faces.','','Aurora uses the supplied script byte-for-byte, directly calling build_crown and splitting only by material for export. No count, size, radius, position, splay, colour or tip-fraction changes. All exported vertex coordinates independently match the supplied build_crown geometry within0.002stud FBX tolerance. No nudges needed. The old crown geometry is removed entirely, including old shelves/footing. No optional snow mesh added. Crown pivot stays at arch-base origin as explicitly specified; pure crystal crown has no collision boxes. Existing shoulder rocks remain unchanged.','','## Crown as built','','| Crystal | Length | Radius | Base X | Base Y(up) | Blender depth Y | Splay | Twist | Apex Y(up) |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
crown=next(e for e in m['props'] if e['name']=='bw_scn_aurora_crown')
for i,(length,radius,x,y,depth,splay,twist) in enumerate(crown['crystal_table'],1):lines.append(f'|{i}|{length}|{radius}|{x}|{y}|{depth}|{splay}|{twist}|{y+length*math.cos(math.radians(splay)):.4f}|')
lines+=['','Exactly276 triangles:240 shaft/base triangles,36 Neon tip triangles. Col is imported and explicitly connected to the preview shader. Glow_Tips separate MeshPart/material: Material=Neon, Color=#9FE6F2, preview emission4. Closeup camera(0,-25,22) in Blender, aimed at(1,0,27),78degree field of view frames crown+lintel.','','## Triangles per file','','| File | Tris | Instances | Placed tris |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"|{e['name']}|{e['triangles']}|{e['builder_count']}|{e['tris_x_count']}|")
lines+=['','## Complete portal group totals','','Includes arch, moving parts, scenery, portal quad, apron, nameplate and applicable coming-soon sign.','','| Course | Display tris |','|---|---:|']
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
 total=sum(e['triangles'] for e in m['props'] if e.get('course')==c or e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c or e['name'] in ('bw_portal_apron','bw_arch_nameplate') or c!='lantern_grove' and e['name']=='bw_coming_soon_sign');lines.append(f'|{c}|{total}|')
lines+=['','## Clearance minima','','Arch-local+Z front. A=X[-5,5]Y[0,12]Z[-12,4]; B=X[-11,11]Y[0,18]Z[4,34]; trigger=X[-5,5]Y[0,10]Z[-1.5,1.5]. Independent triangle-volume tests and Euclidean vertex/face, edge/edge distances from imported FBXs; collision boxes also checked.','','| Mesh | A | B | Trigger |','|---|---:|---:|---:|']
for n,d in mins.items():lines.append(f"|{n}|{d['A']:.5f}|{d['B']:.5f}|{d['trigger']:.5f}|")
lines+=['','## Anchors and measurements','','| Asset | Arch-local anchor |','|---|---|']
for e in m['props']:
 if e.get('anchor_position_arch_local'):lines.append(f"|{e['name']}|{e['anchor_position_arch_local']}|")
lines+=['','Snowpuff position[-6.5,0,1.25], unchanged export origin[0,0,0]. Scenery placement uses pivot_position_arch_local; collision centres are pivot-local. Mesh collision off.','',json.dumps(measures,indent=2),'','## Honest notes','','The exact supplied crown is far taller than the earlier27-stud total-height target: its27-stud longest crystal starts at14.5 and reaches41.0898. It is intentionally six simple faceted shafts,276triangles, superseding historical5-8k richness targets. Its source contains colour assignment across existing BMesh faces; preserved exactly as requested. The closeup and full previews restore imported Col and cyan emission. Bright Neon tips can appear nearly white under exposure.','','The rounded foliage reads as a tree frame with side cascades; toy blobs remain much simpler than the painted concept. Trunk twists show best from3/4 and are partly hidden by canopy/unchanged arches. Sandstone bands are rounded but regular; large required candy shards are prominent. Portal shaders in previews are display-only. No particles or runtime lights were exported. In-engine validation was prohibited; only Blender export/reimport and geometric checks were performed.','','## Rebuild','','Run Blender directly one own instance at a time: build_pass7.py; fitcheck.py -- --pass7; reimport_pass7.py; render_pass7.py. Then Python compose_pass3.py; finalize_pass7.py. Never use run_blender.ps1; never open Roblox/Studio/Player. Backup _backup_pass6 holds pre-pass7 exports, manifest, README, previews and Python sources.','']
(S/'pass7_summary.md').write_text('\n'.join(lines),encoding='utf-8')
p=R/'README.md';t=p.read_text(encoding='utf-8');t=t.split('\n## Pass 7')[0]
t+='\n## Pass 7 current authoritative assets\n\nPass7 supersedes earlier geometry descriptions. Fitcheck and FBX reimport ALL PASS. Placed lobby **'+str(m['totals']['tris_total'])+'** triangles; each file<20k. Fixed arches/surfaces/apron/signs/triggers are unchanged. Clearance zones A=X[-5,5]Y[0,12]Z[-12,4] and B=X[-11,11]Y[0,18]Z[4,34], arch-local+Z front, remain enforced.\n\nGrove: chunkier150degree twisting trunks with three strands, root flares, billowy canopy cascading down outside sides toY6. Canyon: round bevelled sandstone bands,~27.7high/~9.78degree inward lean, doubled joint crystals3-5.7studs, cactus exactly1.5x original height with red/cream spiral disc. Aurora: exact supplied six-crystal source,276triangles,27stud longest crystal startsY14.5 and topsY41.09. Shared arch-base crown pivot; no collision boxes on pure crystals. Glow_Tips separate material: Material=Neon Color=#9FE6F2. Previews use imported Col and emission4.\n\nSee [_src/pass7_summary.md](_src/pass7_summary.md) for triangle/group totals, crystal table, zone minima, anchors, measurements and honest notes; [concept comparison](previews/portals/portals_vs_concepts.png) and [crown closeup](previews/portals/aurora_crown_closeup.png). Earlier summaries are historical. No Roblox applications were opened.\n'
p.write_text(t,encoding='utf-8');audit.append('RESULT: ALL PASS');(S/'artifact_audit_pass7.txt').write_text('\n'.join(audit)+'\n')
with (S/'PROGRESS_pass7.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Final visual review, fitcheck/reimport/artifact audit ALL PASS; manifest and README updated; complete pass7_summary written. All own Blender runs exited.\n')
print(m['totals'])
