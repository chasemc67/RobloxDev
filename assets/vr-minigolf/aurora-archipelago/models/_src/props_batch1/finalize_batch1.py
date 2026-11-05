"""Verify artifact inventory, make contact sheet, document the batch, and write completion marker."""
import json,hashlib,datetime,shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;D=S.parents[2];M=D/'models';PV=M/'previews/props_batch1'
def backup(p):
    if p.exists():
        dest=S/'_backup'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')/p.relative_to(M);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
manifest=json.loads((M/'props_batch1_manifest.json').read_text());fit=json.loads((S/'fitcheck_report.json').read_text());verify=json.loads((S/'fbx_validation.json').read_text())
assert fit['all_pass'] and verify['all_pass']
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='20c4e3f92f8100bfb9da07732e622199'
assert len(manifest['parts'])==21
for p in manifest['parts']:
    assert (M/p['fbx']).stat().st_size>1000
    assert p['tris']<20000 and p['max_mesh_tris']<20000
    assert Image.open(PV/(p['id']+'_34.png')).size==(1280,960)
for n in [1,2,3,5,7,8]:assert Image.open(PV/f'h{n:02d}_34.png').size==(1280,960)
for name in ['gen_batch1.py','parts.json','build_batch1.py','fitcheck_batch1.py','build_report.json','triangles.json','props_batch1.blend']:assert (S/name).exists()
sheet=Image.new('RGB',(1200,640),'#222233');draw=ImageDraw.Draw(sheet)
for i,n in enumerate([1,2,3,5,7,8]):
    sheet.paste(ImageOps.contain(Image.open(PV/f'h{n:02d}_34.png'),(400,300)),((i%3)*400,(i//3)*320));draw.text(((i%3)*400+10,(i//3)*320+301),f'H{n:02d} - batch 1',fill='white')
backup(PV/'contact_sheet.jpg');sheet.save(PV/'contact_sheet.jpg',quality=92)
total=sum(p['tris'] for p in manifest['parts']);maxmesh=max(p['max_mesh_tris'] for p in manifest['parts'])
text=f'''# Aurora Archipelago — final props batch 1

Completed with Blender 5.2.2 LTS headless, Cycles CPU, 16 samples, 1280x960. **21 built parts, {total:,} triangles total, maximum material mesh {maxmesh:,} triangles. ALL PASS: YES.** Four H5 pieces are separately SKIPPED/UNRESOLVED under the addendum; completion does not resolve their design contradictions.

Source holes.json MD5: `20c4e3f92f8100bfb9da07732e622199` (unchanged). The previous failure summary and overwritten artifacts are preserved in `_backup/`. The cone ruling and collider-skin ruling supersede the earlier source preflight; that preflight was not rerun. No Roblox Studio or GUI Blender was used.

## Built parts

| Part | Tris | Largest material mesh | Pivot (hole local) |
|---|---:|---:|---|
'''
for p in manifest['parts']:text+=f"| {p['id']} | {p['tris']} | {p['max_mesh_tris']} | {p['pivot_hole_local']} |\n"
text+='\n## Fitcheck and budgets\n\n'
text+='Exact triangle/OBB separating-axis tests validate the exported Blender triangles against every relevant source wall and open felt/head-clearance volume. Rail distances are conservative L-infinity lower bounds: Euclidean clearance is at least the reported distance. Felt slopes are flattened by an affine shear before testing. Skin footprints use tolerance 0.001; only source collider dressing and below-top felt skins receive the stated exceptions. Every material mesh and every prop is below 20,000 tris. All H8 small coral skins are below 900 tris, satisfying the two-heavy-small-props rule.\n\n'
text+='Near-field totals for this batch: '+', '.join('H'+n+' = '+str(v) for n,v in fit['hole_tris'].items())+' tris, each below 34,000. These counts exclude pre-existing blockout/context and other batches; the build bot must include those in the complete-course budget.\n\n'
text+='Geyser full translation sweep 0..4: minimum clearance 0.1499996 studs to upper_rail12 (equivalent source gap 0.15); exact sweep includes endpoints and connecting side prisms. Contact faces remain square 3x3, y -4..0 at rest, and all trim is inset. Motion is copied verbatim from holes.json. H1 boulder source gap to rail1 = 0.0786796564 studs, NOTE under the addendum. Its low geometry remains within the rotated collider footprint; its cap does not widen toward the rail.\n\n'
text+='H2 lintel undersides: left/right local y8; middle local y8..8.03, with >=8 clearance above the sloping middle burrow. The north edge felt is .03 higher than the plaza; faceting the underside avoids the contradiction of a flat y8 beam while keeping minimum underside y8. The three lintels omit lower support legs, which would require additional rail-skin exceptions.\n\n'
text+='## Skipped source contradictions\n\n'
for p in manifest['skipped']:text+='- **'+p['id']+' — SKIPPED**: '+p['reason']+'\n'
text+='''
## Placement self-check: three hand calculations

World placement: x = lx cos(yaw) + lz sin(yaw) + ox; y = ly + oy; z = -lx sin(yaw) + lz cos(yaw) + oz. Placement yaw = world_yaw + local yaw. Every local yaw is 0 because any collider yaw is baked into hole-frame geometry.

1. H2 lantern cue [-9.75,9,-46], yaw -90, offset [-115,60,480]: cos=0, sin=-1; x=46-115=-69; y=9+60=69; z=-9.75+480=470.25. World **[-69,69,470.25]**. holes.json cup [-9.75,0,-46] overrides props.md [-11,0,-46].
2. H3 glimmer islet [24,-20,-36], yaw -45, offset [-40,60,470]: x=(24+36)/sqrt(2)-40=2.4264068712; y=40; z=(24-36)/sqrt(2)+470=461.5147186258. World **[2.4264068712,40,461.5147186258]**.
3. H5 geyser column [0,0,-26.5], yaw -90, offset [215,84,420]: x=26.5+215=241.5; y=84; z=420. World **[241.5,84,420]**.

## Visual decisions and deviations

Chunky faceted slate/snow, brass/ember lanterns, cyan ice with neon cores, and candy coral use the exact Aurora P1 palette and material names. Materials use the flat-colour fallback; there are no image textures to embed, and FBX export has COPY/embed_textures enabled. Static meshes have no red/cream bands; only the geyser has MoveRed/MoveCream. All decoration must be imported noncollidable.

- H1 snow cap and boulder stay inside the footprint rather than using the full possible 4.4-wide visual envelope. The SE mint marker is inset, avoiding a low protruding lip.
- H2 drift masses stay in the occluder interiors with 0.1 separation from burrow walls. Open-top numerical layouts override the closed tunnel mouths painted in the concept. Lintel signs use violet Canvas rather than cream. The hanging cup lantern is a separate head; its rope/pine supports belong to later dressing.
- H3 islet is a single low-poly view cue within the 20x30x20 anchor envelope. The plank lower skirt is 2.4 wide; above y-.6 its visual body is inset .1 on each side of the 2-wide felt to clear shore/green rails. Source felt provides the complete playing surface. The bridge includes exact bridge-rail skins, with shared source corner-junction footprints exempt; its lower skirt clears other rails. Thin bridge deck surfaces skin their matching felt instead of protruding into head space.
- H7 fans occupy the numeric west-side occluder only; the prose requests both sides but supplies no east anchor. Mogul rail trim follows exact source heights, with ends inset .1 from adjacent unskinned rail segments. The standard rail kit fills those seams.
- H8 lower coral bases match all seven source boxes and yaws exactly. Branches remain in the footprints even above top y1.6, reducing visual overhang risk. Giant coral stays inside its 4x14x4 occluder.
- CPU previews show exact holes.json blockout felt/rails in the hole-local frame, together with all built props for that hole. They reconstruct the numerical context instead of importing the course-wide FBX, avoiding other-hole clutter. Preview context is not exported as prop geometry. H5 overview shows the mover at rest; its standalone preview exposes the full below-pivot box.

## Artifacts and validation

FBX: `models/fbx/props_batch1/<id>.fbx`. Manifest: `models/props_batch1_manifest.json`. Fitcheck: `models/fitcheck_props_batch1.txt` plus `_src/props_batch1/fitcheck_report.json`. All 21 FBX files were reimported in a second headless job: one root Empty at zero asset pivot, one Mesh per material, exact triangle totals, and coordinate-bound error below 0.0001. Evidence: `fbx_validation.json`, `verify.log`.

Previews: `models/previews/props_batch1/hNN_34.png` (six), `<id>_34.png` (21), and `contact_sheet.jpg`. Sources: gen_batch1.py -> parts.json -> build_batch1.py -> triangles.json -> fitcheck_batch1.py. Scene: props_batch1.blend. Logs: build.log, build.log.stderr, fitcheck_exported.log, verify.log. Rebuild only via `powershell -File models/_src/run_blender.ps1 -Script models/_src/props_batch1/build_batch1.py -Log props_batch1/build.log` after backing up existing outputs. No external handoff messages were sent.
'''
backup(S/'summary.md');(S/'summary.md').write_text(text,encoding='utf-8')
readme=M/'README.md';backup(readme)
section=f'''\n\n## Final props batch 1 (H1, H2, H3, H5, H7, H8)

21 final prop FBX files, {total:,} triangles total; exported-triangle fitcheck **ALL PASS: YES**, all FBX reimport checks PASS. Largest material mesh: {maxmesh:,} triangles. Four H5 pieces are SKIPPED under the addendum: cone anchor on felt, cliff envelope/rail conflict, signal lamp head-clearance/rail conflict, and steps without exact placement geometry. These require design correction.

See [_src/props_batch1/summary.md](_src/props_batch1/summary.md) for parts, pivots, deviations, skipped reasons and three hand-computed world placements; [props_batch1_manifest.json](props_batch1_manifest.json) for import placement/material/motion; [fitcheck_props_batch1.txt](fitcheck_props_batch1.txt) for numeric gates; [contact sheet](previews/props_batch1/contact_sheet.jpg) for all six holes. FBX in `fbx/props_batch1/`, source/scene/logs in `_src/props_batch1/`. Palette matches Aurora P1, scale1, forward-Z/upY, root at base or exact mover pivot. Decoration is noncollidable.\n'''
readme.write_text(readme.read_text(encoding='utf-8')+section,encoding='utf-8')
print('Final documentation ready; write done.flag after confirming no job remains.')
