"""Rev2 artifact validation, reference comparisons and handoff documentation."""
import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch1'
manifest=json.loads((M/'props_batch1_manifest.json').read_text());fit=json.loads((S/'fitcheck_report.json').read_text());verify=json.loads((S/'fbx_validation.json').read_text())
assert fit['all_pass'] and verify['all_pass']
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='4ee4f942c3b0c12627d7ce81a3831d4c'
assert len(manifest['parts'])==36
ids={p['id'] for p in manifest['parts']}
for p in manifest['parts']:
 assert (M/p['fbx']).stat().st_size>1000
 assert p['tris']<20000 and p['max_mesh_tris']<20000
 assert Image.open(PV/(p['id']+'_34.png')).size==(1280,960)
 a=p['pivot_hole_local'];r=math.radians(p['world_yaw']);o=p['world_offset'];want=[a[0]*math.cos(r)+a[2]*math.sin(r)+o[0],a[1]+o[1],-a[0]*math.sin(r)+a[2]*math.cos(r)+o[2]]
 assert max(abs(x-y) for x,y in zip(want,p['pivot_world']))<1e-7
 assert not any(m['material'] in ['MoveRed','MoveCream'] for m in p['meshes']) or p['motion']
# All removed exports/previews are preserved in the immutable existing backup or supplemental snapshot.
for p in (M/'fbx/props_batch1').glob('*.fbx'):
 if p.stem not in ids:
  assert (S/'_backup_before_rev2'/p.relative_to(M)).exists() or (S/'_backup_rev1'/p.name).exists()
  p.unlink()
for p in PV.glob('*_34.png'):
 if p.stem.startswith('h') and len(p.stem)>6 and p.stem[:-3] not in ids:
  assert (S/'_backup_before_rev2'/p.relative_to(M)).exists();p.unlink()
sheet=Image.new('RGB',(1200,660),'#222233');draw=ImageDraw.Draw(sheet)
for i,n in enumerate([1,2,3,5,7,8]):
 im=Image.open(PV/f'h{n:02d}_34.png');assert im.size==(1280,960)
 sheet.paste(ImageOps.contain(im,(400,300)),((i%3)*400,(i//3)*330));draw.text(((i%3)*400+12,(i//3)*330+305),f'H{n:02d} REV2',fill='white')
sheet.save(PV/'contact_sheet.jpg',quality=94)
# Each relevant sheet row placed beside its actual prop render; new unsheeted pieces included at bottom.
A=Image.open(D/'silhouettes/sheet01-batch1-h01-h03.png').convert('RGB');B=Image.open(D/'silhouettes/sheet02-batch1-h05-h08.png').convert('RGB')
def row(name,source,lo,hi):return (name,source,(0,lo*2,source.width,hi*2))
rows={1:[row('harbour_lantern',A,30,170),row('snow_boulder',A,170,306)],2:[row('lantern_crook',A,306,444),row('lintel_left',A,444,580),row('rookery_drift',A,580,716)],3:[row('ice_plank',A,716,854),row('ice_bridge',A,854,990),row('glimmer_islet',A,990,1134)],5:[row('steamwhistle_geyser',B,30,164),row('geyser_column',B,164,308),row('cliff_face_w',B,308,446),row('signal_lamp',B,446,584),row('geyser_steps',B,584,716)],7:[row('coral_w2',B,716,848)],8:[row('giant_coral',B,848,986),row('coral_2',B,986,1134)]}

for n,rr in rows.items():
 extras=[p for p in manifest['parts'] if p['hole']==n and p['id'].split('_',1)[1] not in [r[0] for r in rr]]
 height=260*len(rr)+180*((len(extras)+4)//5)+45
 im=Image.new('RGB',(1700,height),'white');dr=ImageDraw.Draw(im);dr.text((20,12),f'H{n:02d} REV2 / supplied silhouette rows and actual CPU renders',fill='black')
 for i,(name,source,box) in enumerate(rr):
  yy=45+i*260;im.paste(ImageOps.contain(source.crop(box),(1280,240)),(0,yy));path=PV/f'h{n:02d}_{name}_34.png'
  if path.exists():im.paste(ImageOps.contain(Image.open(path),(400,230)),(1290,yy))
  else:dr.text((1290,yy+80),'SKIPPED: source rail clearance = 0',fill='red')
  dr.text((1290,yy+235),name,fill='black')
 for i,p in enumerate(extras):
  xx=(i%5)*340;yy=45+len(rr)*260+(i//5)*180;im.paste(ImageOps.contain(Image.open(PV/(p['id']+'_34.png')),(320,155)),(xx,yy));dr.text((xx+8,yy+157),p['id'],fill='black')
 im.save(PV/f'silhouette_compare_h{n:02d}.jpg',quality=94)
# Geometry and bounds facts from final exported triangles.
T=json.loads((S/'triangles.json').read_text());total=sum(p['tris'] for p in manifest['parts']);maxmesh=max(p['max_mesh_tris'] for p in manifest['parts'])
text=f'''# Batch 1 rev2

36 built pieces; {total:,} triangles, largest material mesh {maxmesh:,}. Exported geometry fitcheck ALL PASS: YES; all 36 FBX reimport checks PASS. Two exact-source cliff boxes are SKIPPED. holes.json MD5 4ee4f942c3b0c12627d7ce81a3831d4c.

## Rev1 -> rev2 change list

- H1: tapered faceted harbour post, short bracket, brass/glow lantern and rounded snow. Boulder rebuilt with a SOLID square rotated 3x3 base from felt to y2.5, inset rounded rock/snow crown to y5, and flat SE mint bank line.
- H2: rounded rectangular drift masses around open-top cuts; faceted ice-arch lintels and basalt end pillars included IN EACH LINTEL asset, outside clear burrow widths. New curved shepherd crook with underside >=10.4 and separate lantern cue at exact cup x=-9.75. New left/right 1.8x3.2x.25 signs at x=+-13.9 override the earlier skip ruling.
- H3: inverted floating basalt/slate cone, snow crown, crystalline cluster and side icefall. Plank with two cyan edge cores, thick lower skirt; bridge with rounded snow caps and regularly spaced timber posts.
- H5: cone at revised [-16.75,4,-36], vent crater; exact square 3x3x4 mover with inset hex tiles, vent and flush gauge; green/amber signal housing at [-9.5,2,-27.6]; five 1.5-stud timber treads rising 4 plus 4.5-stud landing and 3.5-high open-side railing. West/east cliff meshes generated against exact source then skipped for zero rail clearance.
- H7: obsolete aggregate coral_fans removed after backup; ten separate coloured branching clumps at all revised positions and heights, 3-5 branches with repeated splits and swollen flattened glowing tips; rounded mogul trim retained.
- H8: branching giant coral and all seven branching bumper skins. Solid bumper bases match exact rotated source footprints felt to y1.6; crowns kept within footprints to satisfy the head-volume gate.

## Fitcheck

Triangle/OBB SAT against all walls and reachable felt (slopes flattened by shear). Rail clearances are conservative L-infinity lower bounds, so Euclidean distances are >= reported numbers. Skin tolerance .001. Exact full vertical translation sweep 0..4 includes endpoints and side prisms. Per-mesh and per-prop <20k, per-hole <34k. Heavy small coral props checked <=2 per hole. Static materials never use MoveRed/MoveCream.

'''
text+='Per-hole triangles: '+', '.join('H'+n+' '+str(v) for n,v in fit['hole_tris'].items())+'.\n\n'
for r in fit['parts']:
 if r['sweep']:text+='Mover sweep: '+json.dumps(r['sweep'])+'\n\n'
text+='## Source contradictions and adaptations\n\n'
for p in manifest['skipped']:text+='- **SKIPPED '+p['id']+'**: '+p['reason']+'\n'
text+='''
- Rookery sheet overall 24x26 rounded rectangle cannot be a solid mass because it crosses reachable burrow/green felt and goes outside source occluders. The built rounded rectangular masses fill only allowed occluder interiors around the open cuts; numerical layout takes priority. Context source walls represent the rest of the overall drift. No closed tunnels.
- Lintel pillar bases start y2.51, leaving .11 above wall tops. Pillars are included in each lintel, never in clear burrow widths. Left outer end flares toward the west support; mid underside y8.04 to accommodate the sloped mouth while preserving eight studs above reachable felt.
- The sheet gives H8 giant envelope 7x14x7 while source occluder is narrower; built crown follows the supplied seven-stud sheet envelope and passes the source rail/felt gates. Coral bumper crowns do not widen over surrounding felt because those triangles would violate the required eight-stud head volume.
- H1 source collider-to-rail1 .0786796564 gap remains an authorized NOTE. Low base is exact collider footprint, upper cap inset and independently rail checked.
- Steps use five 1.5 treads from z-17 to -24.5, followed by a 4.5 landing to z-29, entirely in source x13.5..16.5. Railing occupies the envelope's west edge; rail posts rise 3.5 above treads/landing.
- All silhouettes use faceted low-poly geometry. Flat-colour Aurora P1 material names reused; no image textures needed. FBX embed-texture option enabled.

## World pivot self-checks

R_y(world_yaw) local + offset, yaw baked geometry local0; placement yaw includes hole yaw.
1. H2 lantern cue [-9.75,9,-46], yaw -90, offset [-115,60,480]: x=46-115=-69; y=9+60=69; z=-9.75+480=470.25 => [-69,69,470.25].
2. H3 islet [24,-20,-36], yaw -45, offset [-40,60,470]: x=60/sqrt(2)-40=2.4264068712; y=40; z=-12/sqrt(2)+470=461.5147186258.
3. H5 cone [-16.75,4,-36], yaw -90, offset [215,84,420]: x=36+215=251; y=88; z=-16.75+420=403.25 => [251,88,403.25].

## Built pieces

| ID | Tris | Largest mesh | Local pivot | World pivot | Min rail clearance |
|---|---:|---:|---|---|---:|
'''
by={r['id']:r for r in fit['parts']}
for p in manifest['parts']:text+=f"| {p['id']} | {p['tris']} | {p['max_mesh_tris']} | {p['pivot_hole_local']} | {p['pivot_world']} | {by[p['id']]['min_rail_clearance']:.6f} |\n"
text+='''
## Artifacts and rebuild

FBX: models/fbx/props_batch1/<id>.fbx, one root at zero asset pivot, one mesh per material. Forward -Z, up Y, scale1. Import using manifest pivot_world/placement_yaw and set decoration noncollidable. Geyser motion copied verbatim from holes.json. Signal lamp runtime uses green when flush and amber otherwise; static exported lens is mint.

Previews: six hNN_34.png, 36 per-piece renders, contact_sheet.jpg and six silhouette_compare_hNN.jpg with actual render beside supplied sheet row; skipped cliffs explicitly labelled. Blender scene props_batch1.blend and build/verify logs under _src/props_batch1. CPU Cycles 16 samples, 1280x960. All Blender jobs via models/_src/run_blender.ps1, one at a time; no GUI or Studio.

Existing _backup_rev1 was kept immutable per brief. Supplemental snapshot _backup_before_rev2 preserves every overwritten pre-run artifact, including obsolete aggregate export. Pipeline: gen_batch1.py -> parts.json -> build_batch1.py -> fitcheck_batch1.py -> verify_batch1.py -> finalize_rev2.py. No external messages sent.
'''
(S/'summary.md').write_text(text,encoding='utf-8')
r=M/'README.md';base=r.read_text(encoding='utf-8');heading='\n## Batch 1 rev2\n';base=base.split(heading)[0]
r.write_text(base+heading+f'\n36 revised pieces, {total:,} triangles; **ALL PASS: YES** for built pieces and FBX reimport. Exact H5 cliff_face_w/e SKIPPED for zero source rail clearance. Ten separate H7 branching corals replace coral_fans; H2 crook, pillars and signs, H5 cone/signal/steps, and all H1/H3/H8 meshes rebuilt.\n\n[Summary](_src/props_batch1/summary.md), [manifest](props_batch1_manifest.json), [fitcheck](fitcheck_props_batch1.txt), [contact sheet](previews/props_batch1/contact_sheet.jpg). Six silhouette comparisons in previews/props_batch1. Immutable rev1 backup preserved. Blender headless CPU via run_blender.ps1; decoration noncollidable, forward -Z/up Y, scale1.\n',encoding='utf-8')
print('REV2 artifacts and documentation validated; completion flag must follow visual QA and process exit check.')
