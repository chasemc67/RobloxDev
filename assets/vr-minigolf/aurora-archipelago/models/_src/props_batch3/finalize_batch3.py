"""Plain Python manifest/report writer; preflight never claims FBX or Blender validation."""
import sys as _guard_sys
from pathlib import Path as _GuardPath
_guard_sys.path.insert(0, str(_GuardPath(__file__).resolve().parent.parent))
from polish_guard import start_guard
_PROTECTED_VERIFY = start_guard()

import json,math,hashlib
from datetime import datetime, timezone
from pathlib import Path
S=Path(__file__).resolve().parent;D=S.parents[2]
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='fb913741b5dd4812b6d2318e258bcc46'
P=json.loads((S/'parts.json').read_text());F=json.loads((S/'fitcheck_report.json').read_text());assert F['all_pass']
H={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']};PAL=json.loads((S/'palette.json').read_text());by={r['id']:r for r in F['parts']}
actual=F['mode']=='Blender actual triangles'
B=json.loads((S/'build_report.json').read_text()) if (S/'build_report.json').exists() else None
current_hash=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest()
assert F.get('parts_sha256')==current_hash, 'Fitcheck stale for current geometry'
current_build=bool(B and B.get('generated_by')=='Blender bpy' and B.get('parts_sha256')==current_hash)
V=json.loads((S/'fbx_validation.json').read_text()) if (S/'fbx_validation.json').exists() else None
validated=bool(V and V.get('parts_sha256')==current_hash and V.get('all_pass') and {r['id'] for r in V.get('parts',[])}==set(V.get('exported_ids',[p['id'] for p in P])))
if actual:assert current_build and validated, 'Current Blender build and successful FBX validation required'

if actual:
 report=json.loads((S/'build_report.json').read_text());parts=report['parts']
 assert {p['id'] for p in parts}=={p['id'] for p in P}
 for p in parts:assert (D/'models'/p['fbx']).is_file()
else:
 parts=[]
 for p in P:
  h=H[p['hole']];a=p['anchor'];ang=math.radians(h['world_yaw']);off=h['world_offset'];world=[a[0]*math.cos(ang)+a[2]*math.sin(ang)+off[0],a[1]+off[1],-a[0]*math.sin(ang)+a[2]*math.cos(ang)+off[2]]
  verts=[v for g in p['groups'].values() for v in g['verts']];lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
  meshes=[dict(mesh=p['id']+'__'+m,material=m,colour=PAL[m][0],color=PAL[m][0],roblox_material=PAL[m][1],transparency=PAL[m][3],tris=by[p['id']]['material_tris'][m]) for m in p['groups']]
  r=dict(id=p['id'],hole=p['hole'],fbx='fbx/props_batch3_polish/'+p['id']+'.fbx',export_status='pending user Blender run',tris=by[p['id']]['total_tris'],max_mesh_tris=max(m['tris'] for m in meshes),meshes=meshes,pivot_hole_local=a,anchor_local=a,pivot_world=world,yaw_local=0,world_offset=off,world_yaw=h['world_yaw'],placement_yaw=h['world_yaw'],motion=p['motion'],notes=p['notes'],override_boxes=p['override_boxes'],bbox_asset_local=[lo,hi],bbox=[lo,hi],bbox_hole_local=[[lo[i]+a[i] for i in range(3)],[hi[i]+a[i] for i in range(3)]],dimensions=[hi[i]-lo[i] for i in range(3)],lights=[],can_collide=False,can_query=False,can_touch=False)
  if p['motion']:
   ax=p['motion']['axis'];r['motion_axis_world']=[ax[0]*math.cos(ang)+ax[2]*math.sin(ang),ax[1],-ax[0]*math.sin(ang)+ax[2]*math.cos(ang)]
  parts.append(r)
polish_ids=set(json.loads((S/'polish_ids.json').read_text()))
if actual:assert set(V['exported_ids'])==polish_ids,'Polish requires precisely the ten requested exports'
polish_shapes={p['id']:p for p in json.loads((S/'polish_shapes.json').read_text())}
original_manifest=json.loads((D/'models/props_batch3_manifest.json').read_text())
original_records={p['id']:p for p in original_manifest['parts']}
from polish_manifest import read_parts
retained_records=read_parts(D/'models',S.name)
for i,p in enumerate(parts):
 if p['id'] not in polish_ids:
  parts[i]=retained_records[p['id']]
 else:
  for k in ['pivot_hole_local','pivot_world','yaw_local','placement_yaw','motion']:assert p[k]==original_records[p['id']][k],(p['id'],k)
  p['fitcheck']=by[p['id']]
  p['polish']=polish_shapes[p['id']]
  p.update(can_collide=False,can_query=False,can_touch=False,export_status='validated Blender export' if actual else 'pending user Blender run')
manifest=dict(course='aurora-archipelago',batch=3,validation_stage=F['mode'],all_pass=True,source_md5='fb913741b5dd4812b6d2318e258bcc46',parts=[p for p in parts if p['id'] in polish_ids],skipped=[],axes=dict(forward='-Z',up='Y',scale=1))
(D/'models/props_batch3_polish_manifest.json').write_text(json.dumps(manifest,indent=2))
(D/'models/fitcheck_props_batch3_polish.txt').write_text((S/'fitcheck_report.txt').read_text())
rows=['| Hole | Assets | Triangles | Result |','|---|---:|---:|---|']
for n in [4,6,14,18]:rows.append(f'| H{n:02} | {sum(p["hole"]==n for p in P)} | {F["hole_tris"][str(n)]} | PASS |')
notes='# Batch 3 revision 2 handoff\n\n'+str(len(P))+' assets; none skipped. ALL PASS: YES ('+F['mode']+').\n\n'
if B:
 notes+='Existing build_report.json records Blender '+B.get('blender_version','unknown')+' and '+str(len(B.get('parts',[])))+' asset records. '
 notes+='It matches the current parts source.\n\n' if current_build else 'It belongs to an earlier revision and does not validate rev2 geometry.\n\n'
 notes+='Build report mtime: '+str((S/'build_report.json').stat().st_mtime)+'; triangles mtime: '+str((S/'triangles.json').stat().st_mtime)+'. Source hashes are checked for new builds.\n\n'
notes+='Current revision FBX re-import validation: '+('PASS' if validated else 'pending user Blender run')+'. Current fitcheck uses '+F['mode']+'.\n\n'
notes+='Historical revision notes are preserved in summary_prepolish.md. Current Blender facts above derive from build_report.json and fbx_validation.json and require matching source hashes.\n\n'+'\n'.join(rows)+'\n\n## Source conflicts and shape overrides\n\n'
for p in P:
 for note in p['notes']:notes+='- '+p['id']+': '+note+'\n'
notes+='\nChute skin extends to the connected H18 rail network; every exempt collider is explicitly listed and filled exactly. No exemption for unowned adjacent rails. Rail zero for skins is reported as exempt. Snow replaces cream bellies; buoy stripes use mint/violet/snow/brass. Every static pivot remains the source anchor.\n\n## Run sequence\n\n`python gen_batch3.py`, `python fitcheck_batch3.py --preflight`, `python finalize_batch3.py`, `python make_sheet05.py`. User then runs Blender 5.2 headless with `--background --python build_batch3.py`; CPU Cycles12 at1024x768. Afterwards run `python fitcheck_batch3.py`, `python finalize_batch3.py`, `python make_sheet05.py`. No script starts Blender.\n\nSheet fourth column labels current Blender context, current per-asset previews, earlier build context, or PIL geometry according to preview freshness. The build script re-imports every FBX in a fresh scene and compares meshes, materials, triangle counts and bounds; fbx_validation.json is required for exported handoff.\n'
(S/'summary.md').write_text(notes,encoding='utf-8')
print('\n'.join(rows));print('ALL PASS: YES; '+F['mode'])

lines=['| ID | Tris | Heavy (>900) | Nearest rail (studs) | Nearest felt (studs) |','|---|---:|:---:|---|---|']
for r in sorted(F['parts'],key=lambda r:(r['hole'],r['id'])):
 rail='exempt exact skin' if r['nearest_rail']=='all source rails explicitly skinned' else f"{r['nearest_rail']} {r['min_rail_clearance']:.4f}"
 felt='exempt exact skin' if r['id']=='h18_crystal_chute' else ('flush cue' if r['id']=='h06_respawn_stone' else f"{r['nearest_felt']} {r['min_felt_clearance']:.4f}")
 lines.append(f"| {r['id']} | {r['total_tris']} | {'yes' if r['heavy'] else 'no'} | {rail} | {felt} |")
lines+=['','| Hole | Total tris | Heavy count |','|---|---:|---:|']
for n in [4,6,14,18]:lines.append(f"| H{n:02} | {F['hole_tris'][str(n)]} | {F['heavy_counts'][str(n)]} |")
(S/'summary_table.md').write_text('\n'.join(lines)+'\n')
with (S/'summary.md').open('a',encoding='utf-8') as out:out.write('\n## Triangle and clearance table\n\n'+'\n'.join(lines)+'\n')
print('\n'.join(lines))

arch=by['h18_halo_arch'];pool=by['h06_kettle_pool']
revision='\n## Revision 2 baseline (before Polish)\n\nRevision 2 changed h18_halo_arch and h06_kettle_pool; the Polish pass preserves both assets exactly. Rev1 scripts backed up as gen_batch3_rev1.py and build_batch3_rev1.py. Foot centres/base heights and complete inward half preserved exactly; added foot width extends outside only. Every leg/crown segment is doubled outward/upward, with twelve-sided chamfers and light IceCore inner facets. All kettle Steam mesh removed. All 23 current preflight asset checks pass.\n\n'
metrics=F['arch_rev2_measurements']
revision+=f"Measured tube thickness (rev1 -> rev2): crown {metrics['crown_thickness_rev1_rev2']}; legs {metrics['legs_thickness_rev1_rev2']} studs. Inner-edge maximum deviation: {metrics['inner_edge_max_deviation']:.12f} studs; {metrics['fixed_inner_facets']} complete inward facets unchanged. All segment thickness ratios pass 2x. Foot centres: {metrics['foot_centres']}.\n\n"
revision+=f"Arch: {arch['total_tris']} triangles; headroom over each crossed felt: {arch['head_room_over_felt']} studs; minimum {arch['head_room_min_over_felt']:.6f} studs. Ball-path clearance: {arch['ball_path_vertical_clearance']['minimum']}; the waypoint tee-to-cup path ends before the arch footprint. Sightline hits: {arch['sightline_hits']}.\n\n"
revision+=f"Kettle pool: {pool['total_tris']} triangles; headroom: {pool['head_room_min_over_felt']}.\n\n"
if current_build and validated:
 exported_ids=V.get('exported_ids',[r['id'] for r in V['parts']])
 def report_time(value):
  return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
 revision+=f"Current-source Blender {B['blender_version']} build confirmed by {B['generated_by']} and matching parts_sha256. Started {report_time(B['started_utc'])}; exported {report_time(B['exported_utc'])}; fresh-scene FBX re-import validation PASS at {report_time(V['validated_utc'])}.\n\n"
 selective=set(exported_ids)!={p['id'] for p in P}
 revision+=('Selective' if selective else 'Full')+' build exported/reimported '+str(len(exported_ids))+' assets: '+', '.join(exported_ids)+'. Build report covers '+str(len(B['parts']))+' assets.\n'
 if selective:revision+='Selective build arguments: `-- --only '+','.join(exported_ids)+'`. Other FBXs stay unchanged.\n'
 revision+='Sheet05 selects previews by timestamp and labels per-asset previews separately from hole context.\n'
else:
 revision+='No current-source validated Blender build is recorded; exports and CPU previews await the user build. Sheet05 labels available previews by provenance.\n'
with (S/'summary.md').open('a',encoding='utf-8') as out:out.write(revision)
print(revision)

shapes=json.loads((S/'polish_shapes.json').read_text())
polish='\n## Polish\n\nOnly the ten requested assets changed. Original anchors, pivots, yaw, foot caps and authorized clearance envelopes retained; all other source assets and manifest records remain identical to prepolish backups. Rounded snowpuff bodies and heads have at least twelve segments, Snow bellies, Beak and scarves. Eleven broad, arched drooping palm fronds have thin Snow top strips. Twelve-sided mint/violet/Snow bulged harbour barrels have brass lamp cages and a frosted rope coil. Ramp lantern heads and posts are about 1.5x wider, with Glow #FFB861 Neon panes and Brass caps/finials.\n\nIce banks: chunky faceted volumes 0.82-1.09 studs tall with IceCore strips along the upper inner edge. Width is 0.40 studs: the original outer envelope x=+/-5.05 and the required 0.15 rail gap leave only 0.40, so the requested 0.6-1.0 width cannot fit without extending the envelope. Existing envelope retained.\n\nCurrent-source '+F['mode']+': ALL PASS. Current-source Blender/FBX validation: '+('PASS' if current_build and validated else 'pending user Blender run')+'.\n\n'
polish+='| ID | Old tris | New tris | Nearest rail | Nearest felt | Heavy count per hole |\n|---|---:|---:|---|---|---:|\n'
for shape in shapes:
 r=by[shape['id']]
 polish+=f"| {r['id']} | {shape['old_tris']} | {r['total_tris']} | {r['nearest_rail']} {r['min_rail_clearance']:.4f} | {r['nearest_felt']} {r['min_felt_clearance']:.4f} | {F['heavy_counts'][str(r['hole'])]} |\n"
polish+='\nSelective user build arguments: `-- --only '+','.join(sorted(polish_ids))+'`. After build: `python fitcheck_batch3.py`, `python finalize_batch3.py`; after both batches: `python ../make_polish_sheet.py`. No Python script launches Blender.\n'
with (S/'summary.md').open('a',encoding='utf-8') as out:out.write(polish)
print(polish)
