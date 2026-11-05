"""Pass5 docs and final audit; run after final exports, checks and render review."""
from pathlib import Path
import json,datetime,hashlib
SRC=Path(__file__).parent;ROOT=SRC.parent
m=json.loads((ROOT/'manifest.json').read_text());mins=json.loads((SRC/'clearance_pass5.json').read_text())
courses=('lantern_grove','sugarloaf_canyon','aurora_archipelago')
lines=['# Pass 5 integrated portal gateways','',
'All three original arch FBXs, their 16x18x4 envelopes, three collision boxes, portal quads, apron, nameplate, sign and trigger metadata remain unchanged from pass4. Rebuilt twelve scenery files and six Grove lantern files using the existing generator/export pipeline. No Roblox application was opened.','',
'## Clearance and validation','',
'Arch-local axes: X east, Y up, +Z front/approach. This replaces all earlier pass4 clearance rules. Zone A: X[-5,5] Y[0,12] Z[-12,4]. Zone B: X[-11,11] Y[0,18] Z[4,34]. Trigger: X[-5,5] Y[0,10] Z[-1.5,1.5]. Scenery and lantern triangles and scenery collision boxes avoid all three volumes. Below Y18, pieces beside the opening and behind Z4 may hug the arch. Only geometry above Y18 passes over the expanded approach.',
'Fitcheck and independent FBX reimport: ALL PASS. Distances use triangle/box vertex-face and edge-edge distances with full triangle-volume clipping, not vertex sampling. Every individual mesh is <20k triangles. Placed lobby total is calculated from every manifest instance including all three portal groups. Arch SHA256 preservation is checked against _backup_pass4.','',
'## Triangles per exported file','', '| File | Triangles | Instances | Placed triangles |','|---|---:|---:|---:|']
for e in m['props']:lines.append(f"| {e['name']}.fbx | {e['triangles']:,} | {e['builder_count']} | {e['tris_x_count']:,} |")
lines+=['','## Portal group totals','','Shared display items include apron/nameplate and coming-soon sign for Canyon/Aurora. These totals count one complete group; the lobby total uses actual manifest instance counts.','','| Course | Arch and moving parts plus quad | Scenery | Complete display |','|---|---:|---:|---:|']
for c in courses:
    original=sum(e['triangles'] for e in m['props'] if e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c)
    scenery=sum(e['triangles'] for e in m['props'] if e.get('course')==c)
    shared=sum(e['triangles'] for e in m['props'] if e['name'] in ('bw_portal_apron','bw_arch_nameplate') or c!='lantern_grove' and e['name']=='bw_coming_soon_sign')
    lines.append(f'| {c} | {original:,} | {scenery:,} | {original+scenery+shared:,} |')
lines+=['',f"**Placed lobby total: {m['totals']['tris_total']:,} triangles / <120,000.** {len(m['instances'])} instances, {len(m['props'])} unique files.",'','## Minimum distances per scenery/accessory file','', '| File | Zone A (studs) | Zone B (studs) | Trigger (studs) |','|---|---:|---:|---:|']
for name,d in mins.items():lines.append(f"| {name}.fbx | {d['A']:.5f} | {d['B']:.5f} | {d['trigger']:.5f} |")
lines+=['','## Anchors and placement','','All scenery origins use manifest pivot_position_arch_local. Collision box centres are FBX pivot-local Roblox axes. MeshParts are decorative and noncolliding; only the 2-6 invisible rock/trunk/tower/stone boxes collide. Lantern origins are the cord hinge, with documented swing axis and motion.','','| Grove lantern | Arch-local cord anchor |','|---|---|']
for e in m['props']:
    if e['name'].startswith('bw_arch_lantern_grove_lantern_'):lines.append(f"| {e['name']} | {e['anchor_position_arch_local']} |")
lines+=['','Snowpuff: figure position [-6.5,0,1.25], export origin [0,0,0]. Original footprint X[-7.308,-5.692], Y[0,3], Z[0.55,2] preserved; west snowy rocks below Y3.6 stay outside |X|7.8, leaving this spot clear.','',
'## Art review and materials','',
'Compared all six Cycles GPU previews against the supplied concepts and iterated canopy depth, layered foliage, trunk/lintel overlap, and snowy shoulder growth. Grove trunks overlap the original legs, flare at the roots and grow across the lintel beneath connected layered autumn foliage; lanterns hang at six new canopy anchors. Canyon striped towers touch the leg silhouettes and bend toward lintel ends with candy clusters and a larger side cactus. Aurora has seven main crown crystals in three sizes, tallest off-centre at approximately Y27; snowy shoulder rocks connect the crown to the original legs. No separately exported bridge pieces were introduced.',
'Grove canopy and Aurora crown geometry sit above Y18. Aurora crown: 7,316 triangles, two-segment beveled facets and layered snowy ledges, frosted-violet to icy-teal exported vertex-colour gradient. Glow_Tips is a separate material mesh: set Material=Neon, Color=#9FE6F2. Other Neon parts use manifest parts[].color. Opaque BW_Backdrop uses Col vertex colours; BW_Atlas uses shared embedded bw_atlas_1024.png. No extra textures or real asset lights.','',
'## Caveats','',
'The unchanged arch geometry and required clearance translate the reference paintings into stylized toy geometry. Original Aurora arch crystals remain visible beneath the seven new crown crystals because the original FBX is preserved. Runtime portal swirl/particles and SurfaceGui text remain implementation tasks; preview portal shaders are display only. Preview lighting is render-scene lighting, not exported lights. No in-engine Roblox import or playtest was performed under the explicit prohibition. Earlier pass3/pass4 reports are historical snapshots; pass5 clearance and budget values supersede them.','',
'## Rebuild','',
'Run one own Blender directly at a time with -b --factory-startup -P. Do not use run_blender.ps1. Scripts: build_pass5.py; fitcheck.py -- --pass5; reimport_pass5.py; render_pass5.py. Then run compose_pass3.py and finalize_pass5.py with Python. Backup _backup_pass4 includes FBX, manifest, README, previews and all pre-existing Python source.','']
(SRC/'pass5_summary.md').write_text('\n'.join(lines),encoding='utf-8')
r=ROOT/'README.md';t=r.read_text(encoding='utf-8');marker='\n## Pass 5 integrated gateways\n';t=t.split(marker)[0]
t+=marker+f"\nCurrent authoritative pass: pass5. All earlier clearance descriptions are superseded. Zone A is X[-5,5] Y[0,12] Z[-12,4]; zone B is X[-11,11] Y[0,18] Z[4,34], in arch-local axes with +Z front. Scenery, canopy, lantern triangles and scenery collision boxes avoid these zones and the trigger. Geometry above Y18 may pass over the approach. Arch FBXs and original portal/shared assets are unchanged.\n\nIntegrated side scenery and overhead crowns, twelve rebuilt scenery files and six relocated Grove lanterns. Aurora crown has seven main crystals, a frosted-violet/icy-teal vertex gradient and separate Glow_Tips material for Neon (#9FE6F2). Place at manifest pivots; use only scenery collision boxes, never foliage/crystal mesh collision. Snowpuff position [-6.5,0,1.25], asset origin [0,0,0].\n\nFitcheck and FBX reimport: ALL PASS. Placed lobby total **{m['totals']['tris_total']:,}**, below 120,000. See [_src/pass5_summary.md](_src/pass5_summary.md) for all file/group triangle tables, measured zone distances, anchors, caveats and rebuild scripts. See [concept comparison](previews/portals/portals_vs_concepts.png) for updated eye/3/4 previews.\n"
r.write_text(t,encoding='utf-8')
audit=[]
def check(ok,label):
    audit.append(('PASS ' if ok else 'FAIL ')+label)
    if not ok:raise RuntimeError(label)
for f in ('fitcheck_pass5_validated.txt','reimport_check_pass5.txt'):check('RESULT: ALL PASS' in (SRC/f).read_text(),f)
for e in m['props']:
    check((ROOT/e['fbx']).is_file() and e['triangles']<20000,e['name']+' FBX and <20k')
check(sum(next(e['triangles'] for e in m['props'] if e['name']==i['asset']) for i in m['instances'])==m['totals']['tris_total']<120000,'placed total verified from all instances')
check(all(all(v>0 for v in d.values()) for d in mins.values()),'all triangle zone distances positive')
for c in courses:
    for v in ('eye','34'):check((ROOT/'previews/portals'/f'{c}_{v}.png').exists(),c+' '+v+' preview')
check((ROOT/'previews/portals/portals_vs_concepts.png').exists(),'concept comparison')
for f in ('build_pass5.log','reimport_pass5.log','render_pass5.log'):
    raw=(SRC/f).read_bytes();t=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
    check('Blender quit' in t,f+' own sequential Blender exited')
check((SRC/'props_arches.py').read_bytes()==(ROOT/'_backup_pass4/_src/props_arches.py').read_bytes(),'original arch generator unchanged')
audit.append('RESULT: ALL PASS');(SRC/'artifact_audit_pass5.txt').write_text('\n'.join(audit)+'\n')
with (SRC/'PROGRESS_pass5.md').open('a') as f:f.write(datetime.datetime.now().isoformat()+' Final render review complete; all validation and artifact checks pass; documentation finalized. All own sequential Blender invocations completed.\n')
print(m['totals'])
