from pathlib import Path
import json,hashlib,datetime
from PIL import Image
s=Path('boardwalk/models/_src');r=s.parent;job=Path('..').resolve();m=json.loads((r/'manifest.json').read_text());audit=[]
def check(ok,label):
 audit.append(('PASS ' if ok else 'FAIL ')+label)
 if not ok:raise RuntimeError(label)
for n in ['fitcheck_pass9_validated.txt','reimport_check_pass9.txt']:check('RESULT: ALL PASS' in (s/n).read_text(),n)
for n in ['build','fitcheck','reimport','render']:
 p=s/(n+'_pass9.log');b=p.read_bytes();t=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8',errors='replace');check('Blender quit' in t and 'Traceback' not in t,n+' Blender exited')
check((s/'pass9_geo.py').read_bytes()==(job/'pass9_geo.py').read_bytes(),'supplied source byte identical')
changed={e['name'] for e in m['props'] if e['name']=='bw_scn_aurora_crown' or any(x in e['name'] for x in ['sugarloaf_crystals_','lantern_grove_trunk_','aurora_rocks_'])}
for e in m['props']:
 check(e['triangles']<20000,e['name']+' <20k')
 if e['name'] not in changed:check((r/e['fbx']).read_bytes()==(r/'_backup_pass8'/e['fbx']).read_bytes(),e['name']+' unchanged')
 if e['name'] in changed:
  e['source_sha256']=hashlib.sha256((s/'pass9_geo.py').read_bytes()).hexdigest()
  if 'trunk_' in e['name']:e['notes']='Exact supplied three-strand 250degree trunk plus byte-equivalent pass8 canopy geometry; old bark and inset removed. Two centreline collision boxes. Lanterns unchanged; all cords contact canopy.'
  elif 'aurora_rocks_' in e['name']:e['notes']='Exact supplied eight-rock snowy pile; two boxes; snowpuff footprint clear.'
  elif 'crystals_' in e['name']:e['notes']='Exact supplied four clusters per side (7/5 joint,6/5 base), builder-selected size2.0; Glow_Crystal Neon from Col.'
  else:e.update(notes='Exact supplied six-crystal 12-sided beveled flat-facet crown; no geometry edits.',tallest_tip_Z=27.0,sides=12,flat_normals=True,glow_tip_split='source face-centre top20% assignment',source='pass9_geo.py')
  (s/'manifest_parts'/(e['name']+'.json')).write_text(json.dumps(e,indent=1))
check(m['totals']['tris_total']<120000,'lobby <120k')
m['materials']['BW_Bark_VC']={'vertex_colour_attribute':'Col','colors':['#6B4429','#4A2F1A']};m['materials']['BW_Rock_VC']={'vertex_colour_attribute':'Col','colors':['#3A3550','#4B4566','#EEF3F7']}
m['materials']['Glow_Crystal'].update(Material='Neon',roblox_material='Neon',preview_emission_strength=1.5)
m['materials']['Glow_Tips'].update(Material='Neon',Color='#9FE6F2',preview_emission_strength=1.5)
m['pass9_preview']=dict(view_transform='Standard',world_strength=.9,Glow_emission=1.5,vertex_colour_attribute='Col')
(r/'manifest.json').write_text(json.dumps(m,indent=1))
for c in ['lantern_grove','sugarloaf_canyon','aurora_archipelago']:
 for view in ['eye','34']:
  p=r/'previews/portals'/(c+'_'+view+'.png');check(Image.open(p).size==(960,960),str(p)+' rendered')
check(Image.open(r/'previews/portals/aurora_crown_closeup.png').size==(960,960),'crown closeup rendered');check((r/'previews/portals/portals_vs_concepts.png').exists(),'comparison sheet')
mins=json.loads((s/'clearance_pass9.json').read_text());anchors=json.loads((s/'anchor_contact_pass9.json').read_text())
lines=['# Pass 9 completed','',f"Placed lobby: **{m['totals']['tris_total']:,} triangles**; all files <20k. Fitcheck and FBX reimport: ALL PASS.",'','Supplied pass9_geo.py is byte-identical; no geometry/API edits. Seven replacements: four cluster groups per Sugarloaf side, six-crystal12-sided beveled crown with flat normals, three twisted strands/root flares per Grove side plus retained pass8 leaf masses, eight snowy rocks per Aurora side. Glow_Crystal uses Neon from Col; Glow_Tips Neon #9FE6F2. Preview Glow emission1.5, Standard transform, ambient0.9, large soft key; permitted Eevee fallback after GPU slowdown.','','Two collision boxes per trunk follow lower centreline x=±8.4 Y0..13 and upper inward curl; two per rock pile. All boxes clear A/B and snowpuff footprint. Pure crystals/crown collision off. Snowpuff spot[-6.5,0,1.25] unchanged.','','Six lantern exports and anchors unchanged: cords still contact retained canopy (measured below). Towers, cactus, planters, snowpuff, arches, surfaces, apron, signs, triggers and all remaining FBXs byte-identical to pass8 backup.','','## Triangles','','| Mesh | Tris | Instances | Placed tris |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"|{e['name']}|{e['triangles']}|{e['builder_count']}|{e['tris_x_count']}|")
lines+=['','## Portal group totals','','| Course | Tris |','|---|---:|']
for c in ['lantern_grove','sugarloaf_canyon','aurora_archipelago']:
 total=sum(e['triangles'] for e in m['props'] if e.get('course')==c or e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c or e['name'] in ['bw_portal_apron','bw_arch_nameplate'] or c!='lantern_grove' and e['name']=='bw_coming_soon_sign');lines.append(f'|{c}|{total}|')
lines+=['','## Zone minima','','Arch-local Roblox A X[-5,5]Y[0,12]Z[-12,4]; B X[-11,11]Y[0,18]Z[4,34]. Triangle-to-volume distance, studs.','','| Mesh | A | B | Trigger |','|---|---:|---:|---:|']
for n,d in mins.items():lines.append(f"|{n}|{d['A']}|{d['B']}|{d['trigger']}|")
lines+=['','## Lantern anchors','','| Asset | Anchor X,Y,Z | Cord surface distance | Anchor inside canopy |','|---|---|---:|---|']
for a in anchors:lines.append(f"|{a['name']}|{a['anchor']}|{a['cord_surface_distance']:.5f}|{a['anchor_inside_canopy']}|")
lines+=['','## Honest notes','','All source geometry is preserved, including the supplied crown face-to-crystal attribution where crystals overlap. Fixed arches retain their embedded historical accents. Canopy replaces no leaf positions/colors/topology; old trunk/bark and its atlas inset are removed. Preview lighting alters displayed swatches; these are toy meshes rather than painted concepts. No Roblox application opened. All Blender calls ran directly and sequentially; only our own instances were used and exited.','','## Rebuild','','build_pass9.py -> fitcheck_pass9.py -> reimport_pass9.py -> render_pass9.py using Blender5.2. compose_pass3.py -> finalize_pass9.py using Python. Backup: _backup_pass8.']
(s/'pass9_summary.md').write_text('\n'.join(lines),encoding='utf-8')
p=r/'README.md';t=p.read_text(encoding='utf-8').split('\n## Pass 9')[0];t+='\n## Pass 9 current authoritative assets\n\nExact pass9_geo.py geometry wired into FBX export, manifest and Standard/Col previews. Flat12-sided beveled crown; explicit Sugarloaf crystals; three-strand twisted trunks with retained pass8 canopy; eight snowy rocks per pile. Glow_Tips Neon #9FE6F2, Glow_Crystal Neon from Col. Lantern anchors unchanged and cords contact canopy. Two collision boxes per trunk/rock pile, clear A/B and snowpuff. Fixed and unrelated exports unchanged.\n\nFitcheck and reimport ALL PASS; placed lobby '+str(m['totals']['tris_total'])+' triangles, every mesh<20k. See [_src/pass9_summary.md](_src/pass9_summary.md) for triangle/group tables, zone distances, anchors and honest notes. Source unchanged; no Roblox applications opened.\n';p.write_text(t,encoding='utf-8')
audit.append('RESULT: ALL PASS');(s/'artifact_audit_pass9.txt').write_text('\n'.join(audit)+'\n')
with (s/'PROGRESS_pass9.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Checks/render/visual audit and documentation complete. Own Blender exited.\n')
print(m['totals'])
