from pathlib import Path
import json,datetime,hashlib,colorsys
from PIL import Image
S=Path(__file__).parent;R=S.parent;JOB=R.parent.parent.parent
m=json.loads((R/'manifest.json').read_text());old=json.loads((R/'_backup_pass5/manifest.json').read_text());mins=json.loads((S/'clearance_pass6.json').read_text());measures=json.loads((S/'measure_pass6.json').read_text())
audit=[]
def check(ok,label):
 audit.append(('PASS ' if ok else 'FAIL ')+label)
 if not ok:raise RuntimeError(label)
for f in ('fitcheck_pass6_validated.txt','reimport_check_pass6.txt'):check('RESULT: ALL PASS' in (S/f).read_text(),f)
for f in ('build_pass6.log','render_pass6.log'):
 raw=(S/f).read_bytes();t=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
 check('Blender quit' in t and 'Traceback' not in t,f+' own Blender exited cleanly')
for f in ('fitcheck_pass6.log','reimport_pass6.log'):
 raw=(S/f).read_bytes();t=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
 check('RESULT: ALL PASS' in t and 'Traceback' not in t,f+' own Blender completed')
check((S/'props_arches.py').read_bytes()==(R/'_backup_pass5/_src/props_arches.py').read_bytes(),'unchanged arch generator')
for e in m['props']:
 check((R/e['fbx']).is_file() and e['triangles']<20000,e['name']+' exported and <20k')
 if not e['name'].startswith(('bw_scn_','bw_arch_lantern_grove_lantern_')):
  check(hashlib.sha256((R/e['fbx']).read_bytes()).digest()==hashlib.sha256((R/'_backup_pass5'/e['fbx']).read_bytes()).digest(),e['name']+' immutable SHA256')
check(sum(next(e['triangles'] for e in m['props'] if e['name']==i['asset']) for i in m['instances'])==m['totals']['tris_total']<120000,'placed total under 120k')
# Actual preview pixels, excluding the lower original arch and portal surface.
pixels=[]
for view in ('eye','34'):
 im=Image.open(R/f'previews/portals/aurora_archipelago_{view}.png').convert('RGB');w,h=im.size
 selected=[]
 for y in range(int(h*.18),int(h*.52)):
  for x in range(int(w*.25),int(w*.75)):
   rgb=im.getpixel((x,y));hv,sv,vv=colorsys.rgb_to_hsv(*(v/255 for v in rgb))
   if .66<=hv<=.81 and sv>=.45 and vv>=.2:selected.append(sv)
 check(len(selected)>400,view+' crown violet high-saturation preview pixels '+str(len(selected)))
 pixels.append({'view':view,'violet_pixels':len(selected),'mean_saturation':sum(selected)/len(selected),'hue_range':[.66,.81],'minimum_saturation':.45,'crop_fraction':[.25,.18,.75,.52]})
(S/'preview_colour_pass6.json').write_text(json.dumps(pixels,indent=2))
check('va.layer_name = "Col"' in (S/'render_lib.py').read_text() and "assert 'Col' in o.data.color_attributes" in (S/'render_pass6.py').read_text(),'preview explicitly uses and asserts imported Col vertex-colour wiring')
for e in m['props']:
 if e['name'] in measures:e['pass6_measurements']=measures[e['name']]
 if e['name']=='bw_scn_aurora_crown':
  e.update(main_crystal_count=7,main_crystal_lengths_studs=[5,7,5,8.8,7,5,5],tallest_top_arch_local_y=27,vertex_colour_attribute='Col',gradient_hex=['#6A3FD6','#7FE3E8'],preview_glow_strength=4)
  e['notes']='Pass6: seven crystals in three sizes, tallest off-centre X0.8 at Y27; saturated violet to icy teal Col gradient; broad overlapping crown footing hides the lintel join; Glow_Tips Material=Neon Color=#9FE6F2.'
 if 'sugarloaf_crystals_' in e['name']:e['notes']='Pass6: 18 full Neon candy crystals, 1.5-2.85 studs, 12 on front tower/arch leg and lintel joints plus 6 at bases. Pink #F6A6C8 and yellow #FFE08A.'
 if 'sugarloaf_tower_' in e['name']:e['notes']='Pass6 rebuilt 17 stepped chipped sandstone bands, approximately 27 studs; measured inward lean recorded in pass6_measurements; 4 centreline-following collision boxes.'
 if 'lantern_grove_trunk_' in e['name']:e['notes']='Pass6 rounded overlapping leaf blobs in orange/red/gold form a domed crown above Y18; unchanged six branch/cord anchors; no flat canopy cap.'
m['pass6_art_review']={'reviewed':'six Cycles GPU renders and concept sheet; iterated three times','preview_colour_audit':'_src/preview_colour_pass6.json','geometry_measurements':'_src/measure_pass6.json'}
(R/'manifest.json').write_text(json.dumps(m,indent=1))
lines=['# Pass 6 targeted portal fixes','',f"Placed lobby: **{m['totals']['tris_total']:,} triangles**, {len(m['instances'])} instances, {len(m['props'])} files. Every file <20,000; placed total <120,000.",'','Fitcheck and independent FBX reimport: ALL PASS. Immutable arch/portal/apron/nameplate/sign exports SHA256 match _backup_pass5; exact arch collision boxes and trigger metadata remain unchanged. No Roblox application was opened. Each own Blender invocation ran sequentially and completed.','','## Geometry and measured lean','','Tower centres are independently measured from imported FBX vertices in lower Y0.2-1.4 and upper Y25.8-27.7 slices (bounding-section centres, ignoring surface facet noise); angle = atan(abs(delta X)/delta Y).']
for n,v in measures.items():lines.append(f'- {n}: '+(f"base {v['base_centre']}, top {v['top_centre']}, inward lean {v['lean_degrees']:.3f} degrees." if 'lean_degrees' in v else f"height/pass5 = {v['height_ratio_pass5']:.4f}."))
lines+=['','Four tower collision boxes track the inward centreline. Canyon joints carry 18 crystals per side: 12 at leg/lintel joints and 6 at bases, each 1.5-2.85 studs. Cactus is rebuilt at scale5.4 with five substantial stem rings and a larger proportional base.','','## Triangles per file','','| File | Pass6 tris | Instances | Placed tris |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"| {e['name']} | {e['triangles']} | {e['builder_count']} | {e['tris_x_count']} |")
lines+=['','## Geometry change hashes','','| Rebuilt Sugarloaf file | Pass5 tris | Pass6 tris | Pass6 SHA256 |','|---|---:|---:|---|']
for e in m['props']:
 if e['name'] in measures or 'sugarloaf_crystals_' in e['name']:
  prev=next(q for q in old['props'] if q['name']==e['name']);lines.append(f"| {e['name']} | {prev['triangles']} | {e['triangles']} | {hashlib.sha256((R/e['fbx']).read_bytes()).hexdigest()} |")
lines+=['','## Portal group totals','','Includes unchanged arch, moving parts, portal quad, scenery, apron and nameplate; Canyon/Aurora also include coming-soon sign.','','| Course | Complete display tris |','|---|---:|']
for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago'):
 total=sum(e['triangles'] for e in m['props'] if e.get('course')==c or e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c or e['name'] in ('bw_portal_apron','bw_arch_nameplate') or c!='lantern_grove' and e['name']=='bw_coming_soon_sign');lines.append(f'| {c} | {total} |')
lines+=['','## Clearance minima','','Arch-local +Z front. A: X[-5,5] Y[0,12] Z[-12,4]. B: X[-11,11] Y[0,18] Z[4,34]. Trigger X[-5,5] Y[0,10] Z[-1.5,1.5]. Full triangle-volume clipping and Euclidean vertex/face and edge/edge distances; collision boxes also checked. Only geometry above Y18 overhangs the approach.','','| Mesh | Zone A | Zone B | Trigger |','|---|---:|---:|---:|']
for n,d in mins.items():lines.append(f"| {n} | {d['A']:.5f} | {d['B']:.5f} | {d['trigger']:.5f} |")
lines+=['','## Anchors and materials','','Grove canopy branches retain the pass5 hinge anchors, and lanterns were re-exported.','','| Lantern | Arch-local anchor |','|---|---|']
for e in m['props']:
 if e['name'].startswith('bw_arch_lantern_grove_lantern_'):lines.append(f"| {e['name']} | {e['anchor_position_arch_local']} |")
lines+=['','Snowpuff: [-6.5,0,1.25], original export origin [0,0,0], unchanged clear footprint. All scenery uses manifest pivot_position_arch_local; collision centres are pivot-local. Mesh collision off; use only the recorded simple collision boxes.','', 'Aurora: seven main crystals, sizes 5/7/8.8 studs, off-centre tallest X0.8, top Y27. Saturated #6A3FD6 base holds through the lower body then fades toward #7FE3E8. Col vertex colours are exported, explicitly wired in previews, and asserted after FBX import. Glow_Tips is a separate part/material: **Material=Neon, Color=#9FE6F2**, preview emission strength4. Shared BW_Atlas texture, opaque BW_Backdrop, no extra textures or exported lights.','']
for v in pixels:lines.append(f"{v['view']} preview upper-crown crop contains {v['violet_pixels']} violet pixels with saturation >=0.45; mean saturation {v['mean_saturation']:.3f}. See preview_colour_pass6.json for actual pixel test bounds.")
lines+=['','## Honest concept review','','Reviewed the complete side-by-side sheet and all six views; iterated canopy depth, crown position/footing, violet gradient and Neon preview exposure. Grove has a rounded billowy silhouette with overlapping large orange/red/gold blobs above Y18, hiding the overhead join and retaining hanging lanterns. Canyon reads as an inward leaning striped sandstone gateway; pink/yellow crystals are visible on the front joints and bases, and the cactus is doubled. Aurora has a violet crown joined into its shoulder rocks with icy tips and snow shelves; the crown covers the upper beam from the eye-height view.','', 'The concept paintings have finer chipped surfaces, rich foliage, dramatic sunset lights and portal particles. These remain stylized toy meshes with preserved original arch silhouettes, no alpha foliage, no real asset lights. The doubled cactus is deliberately more dominant than the reference. The Aurora snow ledges and broad crown footing are chunky; the cyan emission tips can approach white at their brightest pixels. Original arch crystals/leaves remain visible below the new crowns. In-engine validation was prohibited; no Roblox or Studio launch/import/playtest was attempted.','', '## Rebuild','','Run Blender directly, one own instance at a time: build_pass6.py, fitcheck.py -- --pass6, reimport_pass6.py, render_pass6.py. Then Python compose_pass3.py and finalize_pass6.py. Do not use run_blender.ps1. Backup _backup_pass5 contains pre-pass6 FBX, manifest, README, previews and all Python sources.','']
(S/'pass6_summary.md').write_text('\n'.join(lines),encoding='utf-8')
p=R/'README.md';t=p.read_text(encoding='utf-8');t=t.split('\n## Pass 6 targeted portal fixes\n')[0];t+='\n## Pass 6 targeted portal fixes\n\nCurrent authoritative pass: pass6. Clearance remains zones A/B from pass5: X[-5,5] Y[0,12] Z[-12,4] and X[-11,11] Y[0,18] Z[4,34], with +Z front. All scenery/lantern triangles and collision boxes pass clearance. Original arch, surfaces, apron, signs and triggers are preserved.\n\nRebuilt leaning sandstone towers (9.907 and 9.669 degrees), front joint Neon candy clusters, cactus at 1.9905x prior height, domed autumn canopy, and seven-crystal saturated violet/teal crown. Glow_Tips: Material=Neon, Color=#9FE6F2. Preview Col wiring and actual violet pixels verified.\n\nFitcheck and FBX reimport: ALL PASS. Placed lobby total '+f"**{m['totals']['tris_total']:,}** triangles (<120,000). All files <20k. See [_src/pass6_summary.md](_src/pass6_summary.md) for measurements, hashes, triangles, zone minima, anchors, honest concept review and rebuild instructions; [comparison](previews/portals/portals_vs_concepts.png). Earlier pass summaries are historical.\n";p.write_text(t,encoding='utf-8')
audit.append('RESULT: ALL PASS');(S/'artifact_audit_pass6.txt').write_text('\n'.join(audit)+'\n')
(S/'PROGRESS_pass6.md').open('a').write(datetime.datetime.now().isoformat()+' Final six-view concept review and violet pixel audit complete; fitcheck/reimport/artifact ALL PASS; docs updated; all own Blender invocations exited.\n')
print(m['totals']);print(pixels)
