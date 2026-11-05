"""Compose rendered views and deterministic documentation; does not alter exports."""
from pathlib import Path
import json,datetime
from PIL import Image,ImageDraw,ImageOps
SRC=Path(__file__).parent;ROOT=SRC.parent;LOBBY=ROOT.parent.parent;KIT=LOBBY/'kit'
def thumb(path,w,h):
    return ImageOps.pad(Image.open(path).convert('RGB'),(w,h),color='#eee5d6')
def sheet(items,path,cols=3,w=400,h=400):
    canvas=Image.new('RGB',(cols*w,((len(items)+cols-1)//cols)*(h+35)),'#eee5d6');d=ImageDraw.Draw(canvas)
    for i,(label,p) in enumerate(items):
        x=(i%cols)*w;y=(i//cols)*(h+35);canvas.paste(thumb(p,w,h),(x,y));d.text((x+8,y+h+8),label,fill='#30281f')
    canvas.save(path)
courses=('lantern_grove','sugarloaf_canyon','aurora_archipelago');dest=ROOT/'previews/portals'
canvas=Image.new('RGB',(1600,3*485),'#eee5d6');d=ImageDraw.Draw(canvas)
for i,c in enumerate(courses):
    y=i*485
    canvas.paste(thumb(dest/(c+'_eye.png'),480,450),(0,y));canvas.paste(thumb(dest/(c+'_34.png'),480,450),(480,y));canvas.paste(thumb(LOBBY/('portal_'+c+'.png'),640,450),(960,y))
    d.text((12,y+459),c+' | eye at 5 studs + 2x5 capsule | 3/4 | supplied concept',fill='#30281f')
canvas.save(dest/'portals_vs_concepts.png')
kit=json.loads((KIT/'manifest.json').read_text());man=json.loads((ROOT/'manifest.json').read_text())
sheet([(e['name'],KIT/'previews'/(e['name']+'_34.png')) for e in kit['props']],KIT/'previews/kit_contact_sheet.png',cols=4,w=320,h=320)
def table(entries):return '| Asset | Tris | Bbox W/H/D | Pivot |\n|---|---:|---|---|\n'+'\n'.join('| '+e['name']+' | '+str(e['triangles'])+' | '+ '/'.join(str(round(v,3)) for v in e['bbox_size_studs'])+' | '+e['pivot']+' |' for e in entries)
portals=[e for e in man['props'] if e['name'].startswith(('bw_arch_','bw_portal_'))]
text='''# Lobby pass 2

Generated with Blender 5.2.2 LTS. All portal opening/envelope/trigger and aggregate budget checks pass, and portal/kit FBX reimport checks pass. Triangle clipping includes face interiors. See `fitcheck_pass2_validated.txt`, `reimport_check_pass2.txt`, and `../../../kit/_src/reimport_check_pass2.txt`.

Pass1 exports/manifest/previews preserved once in `../_backup_pass1/`. Source-only changes; every FBX was generated through PB/export_fbx. Shared 1024 atlas, no extra portal textures, separate Neon and vertex-colour materials, no real model lights.

## Portal files and tris

'''+table(portals)+'''

Combined static + moving + surface: Lantern Grove 6,858; Sugarloaf Canyon 2,174; Aurora Archipelago 3,394 tris. Apron 12 tris per instance, reused nameplate/sign budgets unchanged. Manifest assembly includes 10 new attached instances; total lobby '''+str(man['totals']['tris_total'])+''' tris, '''+str(len(man['instances']))+''' instances, well below 120k.

## Collision and attachment

Each arch: legs centre (-6.5,9,0)/(6.5,9,0), size 3x18x4; lintel centre (0,14,0), size 10x4x4. All decorative MeshParts CanCollide false; collision is invisible boxes only. No mesh geometry or modelled trigger in the opening.

Trigger metadata: PortalTrigger_<courseId>, centre (0,5,0), size 10x10x3, CanCollide/CanQuery false, Transparency 1. Portal quad is intentionally inside the trigger and excluded from decorative clearance. Quad at Z=1.5, 0.5 behind front envelope, 10x12, 2 tris, UV 0-1. Shared arch base origin preserved for all children.

Nameplate centre (0,14.5,2.25), sign centre (0,12.7,2.25); rope anchors (+/-2,13.5,2.25). Their reused meshes have base pivots: place nameplate base Y=13.5, sign base Y=11.7, plus the listed front Z. Sign is forward of arch/trigger depth. Lantern cord anchors listed per course in manifest. Separate apron origin (0,0,4), top Y=0, bottom -0.1, no step; intentionally outside arch envelope. Snowpuff keeps arch-local origin; optional bob <=0.1. Lantern sets share arch pivot; individually articulated lanterns require splitting at the documented anchors.

## Kit

'''+table(kit['props'])+'''

Kit manifest records hooks, cloth/soil attach origins and panel face rectangles. Leaderboard panels are separate two-triangle FBXs sharing frame origin, W3.4 H5.6 centred at X=-4.3/0/4.3, Y5, Z=-0.65, facing -Z. Span/bunting origins at base centre; use recorded hook heights to hang them. Banner cloth origin top centre for sway. No collision on any kit prop.

## Previews, rebuild and caveats

Portal eye/34 renders and concept comparison sheet: `../previews/portals/`. Kit eye/34 and contact sheet: `../../../kit/previews/`. Cycles OptiX used. Reference capsule is 2x5, in opening, moved forward of opaque portal display so visible. Eye camera Y=5 at ~20 studs in front. Preview nameplates reused; preview portal shader is illustrative noise colour only, runtime swirl/ribbons, particles, state controls and teleport remain RobloxDevBot's. FBX cannot preserve shader emission wiring: set Neon from manifest, preserve vertex colour attribute Col. Imported material count/geometry/pivot/orientation verified. Tiny texture marks are atlas paint, not modelled detail. Flat display planes and prescribed apron are exceptions to minimum solid detail thickness. Model shapes simplify painted concepts for VR/mobile budgets.

Run Blender directly, one instance at a time, never `_src/run_blender.ps1`:

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/build_all.py -- --group arches
python boardwalk/models/_src/metadata_pass2.py
python boardwalk/models/_src/build_all.py --assemble
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/fitcheck.py -- --pass2
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/reimport_check.py
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P kit/_src/build_kit.py
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/reimport_check.py -- C:/Users/chase/bw_lobby2/lobby/kit --kit
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/render_pass2.py
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b --factory-startup -P boardwalk/models/_src/render_pass2.py -- C:/Users/chase/bw_lobby2/lobby/kit --kit
python boardwalk/models/_src/finalize_pass2.py
```
'''
(SRC/'pass2_summary.md').write_text(text)
(KIT/'README.md').write_text('# Modular lobby dressing kit\n\n21 decoration FBXs, shared boardwalk atlas, base-centre pivots except banner cloth top pivots and leaderboard panels sharing frame base origin. Facing -Z. Scale 1 BU = 1 stud, FBX forward -Z up Y, textures embedded. MeshParts Anchored=true, CanCollide/CanQuery/CanTouch=false; no mesh collision. Neon material from manifest; Col vertex colours must be retained.\n\n'+table(kit['props'])+'\n\nHook positions, soil filler swaps and SurfaceGui panel rectangles are in manifest.json. Put swappable plants at planter filler_attach. Put cloth top pivot at banner_pole.cloth_attach. For string spans, align both recorded hooks to poles, rotate/translate whole asset only. No lights or animation baked. Cloth may gently sway +/-4 degrees; avoid flicker near spawn. Neutral wood/brass/stone kit works with treehouse, islands and boardwalk layouts; themed fillers and banners supply the three course palettes.\n\nBuild with `_src/build_kit.py` using own Blender headless instance. Preview/validation commands are in [pass2 summary](../boardwalk/models/_src/pass2_summary.md). 42 per-asset eye/34 previews plus kit_contact_sheet.png; eye camera 5 studs, capsule 2x5. Reimport ALL PASS at `_src/reimport_check_pass2.txt`.\n')
readme=ROOT/'README.md';old=readme.read_text()
if '# Pass 2 update' in old:old=old[old.index('# Golden Hour Boardwalk:'):]
readme.write_text('# Pass 2 update\n\nThree portal arches replaced; moving lantern sets, snowpuff, full-UV portal quads and flush apron exported separately. 37 prop FBXs, 252 manifest instances, '+str(man['totals']['tris_total'])+' lobby tris. Portal fitcheck and FBX reimport ALL PASS. Kit: 21 separate decoration assets, independent manifest.\n\nSee [_src/pass2_summary.md](_src/pass2_summary.md) for current geometry, collision, hooks, pivots, rebuild commands and caveats; [portal concept comparison](previews/portals/portals_vs_concepts.png) and [kit contact sheet](../../kit/previews/kit_contact_sheet.png). Pass1 backup at `_backup_pass1/`. Earlier pass1 tables/previews below are historical; current manifest is authoritative.\n\n'+old)
print('Sheets and documentation complete')
