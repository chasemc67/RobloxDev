"""Create pass4 documentation and audit required deliverables; no export edits."""
from pathlib import Path
import json,hashlib,datetime
SRC=Path(__file__).parent;ROOT=SRC.parent;LOBBY=ROOT.parent.parent
man=json.loads((ROOT/'manifest.json').read_text());mins=json.loads((SRC/'clearance_pass4.json').read_text())
courses=('lantern_grove','sugarloaf_canyon','aurora_archipelago')
changed=[e for e in man['props'] if e['name'].startswith('bw_scn_') or e['name'].startswith('bw_arch_lantern_grove_lantern_')]
lines=['# Pass 4 standalone portal scenery','',
'Twelve standalone scenery FBXs plus six canopy-anchored Lantern Grove lanterns. All arch geometry, other moving assets, portal quads, apron, nameplate and sign FBXs remain byte-identical to pass 3. Three collision boxes and trigger/surface metadata per arch are preserved. No Roblox application was opened.','',
'## Validation','',
'`fitcheck_pass4_validated.txt`: ALL PASS. Includes pass 3 envelope, face/opening/trigger, UV, material, hinge and original aggregate budget checks; per-scenery strict <20,000 triangle cap, measured base-centre pivots, collision metadata, full triangle/exclusion-volume clearance, exact Euclidean triangle-to-corridor minima, all lantern extended-opening tests, and preserved FBX SHA256 comparisons.',
'`reimport_check_pass4.txt`: ALL PASS over all portal/scenery exports, including all 18 new or changed files. Imported bbox, orientation, triangle counts, material counts, identity origin and scale match manifest.',
'Walk-in corridor: X [-5,5], Y [0,12], Z [-2,24]. Forbidden scenery box: X [-11,11], Y [0,18], Z [-8,30]. No intersecting triangle faces. Above Y18 is permitted. Minimum distances use triangle/box vertex-face and edge-edge features, not vertex-only sampling.','',
'## Per-file triangles and clearance','',
'| File | Triangles | Minimum distance to walk-in corridor (studs) | Pivot in arch-local X,Y,Z | Collision boxes |',
'|---|---:|---:|---|---:|']
for e in changed:
    a=e.get('pivot_position_arch_local',e.get('anchor_position_arch_local'))
    d=f"{mins[e['name']]:.5f}" if e['name'] in mins else 'accessory: extended opening clear'
    lines.append(f"| {e['name']}.fbx | {e['triangles']:,} | {d} | {a} | {len(e['collision'])} |")
lines+=['','Retained portal-component files:','','| File | Triangles |','|---|---:|']
for e in man['props']:
    if e not in changed and e['name'].startswith(('bw_arch_','bw_portal_','bw_coming_soon_sign')):lines.append(f"| {e['name']}.fbx | {e['triangles']:,} |")
lines+=['','## Per-portal group totals','','Includes original arch, portal quad, lanterns, snowpuff where applicable; full display total also includes one apron and one reused nameplate, plus coming-soon sign for Sugarloaf/Aurora. Shared components are counted separately in the manifest placed-scene total.','','| Portal | Original constrained group | New scenery | Complete display group |','|---|---:|---:|---:|']
totals={}
for c in courses:
    original=sum(e['triangles'] for e in man['props'] if e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c)
    scenery=sum(e['triangles'] for e in man['props'] if e.get('course')==c)
    shared=sum(e['triangles'] for e in man['props'] if e['name'] in ('bw_portal_apron','bw_arch_nameplate') or (c!='lantern_grove' and e['name']=='bw_coming_soon_sign'))
    totals[c]={'original':original,'scenery':scenery,'display':original+scenery+shared}
    lines.append(f'| {c} | {original:,} | {scenery:,} | {original+scenery+shared:,} |')
lines+=['',f"Placed-scene manifest total: **{man['totals']['tris_total']:,}** triangles; original limit 120,000. Unique props: {len(man['props'])}; instances: {len(man['instances'])}.",'','## Lantern anchors and snowpuff','','Six Grove cord-anchor pivots, in arch-local Roblox axes:']
for e in changed:
    if e.get('anchor_position_arch_local'):lines.append(f"- `{e['name']}`: {e['anchor_position_arch_local']}; swing axis {e['swing_axis']}; {e['suggested_motion']}")
lines+=['','Snowpuff geometry and arch-base FBX origin are unchanged. Figure footprint remains by the west leg around X=-6.5, Z=1.25; asset origin [0,0,0]. New west snow-rocks begin outside X=-11, leaving its original spot clear. Exact snowpuff bbox is in manifest.','',
'## Placement, materials and collision','',
'Each scenery FBX is base-centred. Use `pivot_position_arch_local` for its origin; all `collision[].center` values are relative to that origin in Roblox axes. Manifest instances already include parent-relative scenery placement in lobby world coordinates. MeshParts are decoration only: CanCollide/CanQuery/CanTouch false. Only invisible simple rock, trunk, tower, cactus-stem or stone-planter collision boxes may collide; foliage and crystals remain noncolliding.',
'Opaque `BW_Backdrop` uses exported Col vertex colours. `BW_Atlas` uses embedded shared `textures/bw_atlas_1024.png`; no extra textures. `BW_Neon` and `BW_Neon_Yellow` are separate material meshes; use each parts[].color and Material=Neon. Grove lanterns #FFC867, candy tips #F6A6C8 and #FFE08A, Aurora tips #9FE6F2. No asset contains a real light.',
'','## Render review and caveats','',
'Six 960x960 Cycles GPU previews show arch, all scenery, separate lanterns, portal/apron/signs and 2x5 capsule in both views. Eye camera is Y=5, pulled back to fit the whole group. Comparison sheet: `previews/portals/portals_vs_concepts.png`.',
'Reviewed against all three supplied portal concepts. Iterated sparse lower Grove foliage, uniform Aurora crown and low snow-rock silhouettes; added layered leaf skirts, varied tilted crown shards, substantial snow boulders and two Neon candy colours. Grove has two connected overhead autumn canopies and gnarled side trunks; Canyon has tall chipped sandstone bands, candy clusters and a lollipop cactus; Aurora has a large faceted crown behind the arch and dark snow-capped rocks.',
'The mandatory six-stud offset and unchanged 16x18x4 arch create wider, clearly separate scenery than the tightly packed concepts. This is deliberate to retain the specified walk-in corridor. Concept photographic leaf/stone detail is translated into toy low-poly masses. Portal preview shader is display-only; production portal export remains unchanged for runtime animation. No real in-engine import/playtest was attempted under the Roblox prohibition.','',
'## Rebuild','',
'Run from lobby root, one own Blender process at a time; never use run_blender.ps1 (it waits on the unrelated job):','',
'```powershell',
r'& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\build_pass4.py',
r'& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\fitcheck.py -- --pass4',
r'& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\reimport_pass4.py',
r'& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\render_pass4.py',
r'python boardwalk\models\_src\compose_pass3.py',
r'python boardwalk\models\_src\finalize_pass4.py',
'```','',
'`build_pass4.py` imports props_scenery, reuses build_all export/manifest assembly, updates Grove lantern generator closure anchors, and adds scenery instances. Do not rebuild the full arches group to preserve pass3 exports. Backup `_backup_pass3` contains original FBX, manifest, previews and all Python generators existing before this pass.']
(SRC/'pass4_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
readme=ROOT/'README.md';text=readme.read_text(encoding='utf-8');marker='\n## Pass 4 standalone portal scenery\n'
if marker in text:text=text.split(marker)[0]
readme.write_text(text+marker+'\nTwelve standalone scenery exports and six canopy-anchored Grove lanterns are complete. See [_src/pass4_summary.md](_src/pass4_summary.md) for triangles, group totals, pivots, collision, clearance minima, anchors and rebuild commands. Both fitcheck and FBX reimport report ALL PASS; preserved exports match the pass3 backup byte-for-byte. Place scenery using manifest `pivot_position_arch_local`, and use only its 2-6 simple collision boxes. Candy tips have separate pink/yellow Neon materials; foliage/crystals never collide. Whole-group previews and concept comparison are in [previews/portals/portals_vs_concepts.png](previews/portals/portals_vs_concepts.png).\n',encoding='utf-8')
audit=[]
def verify(ok,desc):
    audit.append(('PASS ' if ok else 'FAIL ')+desc)
    if not ok:raise RuntimeError(desc)
for f in ('fitcheck_pass4_validated.txt','reimport_check_pass4.txt'):verify('RESULT: ALL PASS' in (SRC/f).read_text(),f)
for e in changed:verify((ROOT/e['fbx']).is_file() and e['triangles']<20000,e['name']+' export and cap')
for c in courses:
    for v in ('eye','34'):verify((ROOT/'previews'/'portals'/(c+'_'+v+'.png')).is_file(),c+' '+v+' preview')
verify((ROOT/'previews'/'portals'/'portals_vs_concepts.png').is_file(),'concept comparison')
verify(min(mins.values())>=6,'all scenery distances >=6')
verify(man['totals']['tris_total']<120000,'placed scene <120k')
verify(len(changed)==18,'exactly 12 scenery + 6 changed lantern files')
verify((SRC/'props_arches.py').read_bytes()==(ROOT/'_backup_pass3'/'_src'/'props_arches.py').read_bytes(),'arch generator unchanged')
for f in ('build_pass4.log','fitcheck_pass4.log','reimport_pass4.log','render_pass4.log'):
    raw=(SRC/f).read_bytes();log=raw.decode('utf-16' if raw.startswith(bytes([255,254])) else 'utf-8',errors='replace')
    verify(('RESULT: ALL PASS' in log if f=='fitcheck_pass4.log' else 'Blender quit' in log),f+' own Blender completed')
audit.append('RESULT: ALL PASS')
(SRC/'artifact_audit_pass4.txt').write_text('\n'.join(audit)+'\n')
with (SRC/'PROGRESS_pass4.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Final review iteration complete: all checks pass, 18 exports, six Cycles previews, comparison sheet, summary and README finalized. All four own sequential Blender jobs exited normally.\n')
print(json.dumps({'triangles':man['totals']['tris_total'],'scenery_triangles':sum(e['triangles'] for e in changed if e['name'] in mins),'minimum_clearance':min(mins.values()),'groups':totals},indent=2))
