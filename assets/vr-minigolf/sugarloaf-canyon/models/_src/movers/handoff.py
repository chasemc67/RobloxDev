import json,datetime,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
SRC=Path(__file__).resolve().parent;OUT=SRC.parent;BASE=SRC.parents[1]
def main():
    entries=json.loads((SRC/'movers_manifest.json').read_text())['movers'];results=json.loads((SRC/'fitcheck_results.json').read_text())
    sheet=Image.new('RGB',(1600,5*690),(47,38,49));draw=ImageDraw.Draw(sheet)
    for row,e in enumerate(entries):
        for col,view in enumerate(('eye','34')):
            im=Image.open(OUT/'previews'/(e['id']+'_'+view+'.png')).convert('RGB');im.thumbnail((800,650));sheet.paste(im,(col*800,row*690+30));draw.text((col*800+12,row*690+10),e['id']+' '+view,fill='white')
    sheet.save(OUT/'previews/contact_sheet.png')
    lua='''-- elapsed t in seconds, all coordinates hole-local Roblox studs
local function sluice(t)
 local q=t%(3.2+14/3)
 if q<1.2 then return 0 elseif q<1.2+7/3 then return -3*(q-1.2)
 elseif q<3.2+7/3 then return -7 else return -7+3*(q-3.2-7/3) end
end
local function lockGate(t)
 local q=t%9.6
 if q<5.5 then return -1.3 elseif q<6.15 then return -1.3+2*(q-5.5)
 elseif q<8.95 then return 0 else return -2*(q-8.95) end
end
-- DRAFT lift schedule ONLY; cannot meet the full closed-dwell constraint.
local function lockLift(t)
 local q=t%9.6
 if q<5.45 then return 0,0 elseif q<7.45 then return 2*(q-5.45),0
 elseif q<8.95 then return 4*(1-(q-7.45)/1.5),4*math.max(0,1-(q-7.45)/0.15)
 else return 0,0 end
end
-- lift transform: pivot * CFrame.new(0,height,-2)
-- * CFrame.Angles(-math.rad(tilt),0,0) * CFrame.new(0,0,2)
-- pivot remains top center; tilt hinge is north edge z=-25, Roblox -X axis.
'''
    (SRC/'motion.lua').write_text(lua)
    text=['# SRV-132 H6 + H11 movers pass 1 — DRAFT / FITCHECK FAILED',
    'Five props built reproducibly under out. No manifest.json or library file modified. Decoration meshes: CanCollide=false. Import FBX at scale 1, forward -Z / up Y, textures embedded.',
    '| Prop / FBX | Hole-local pivot | World pivot | Tris | MeshParts |', '|---|---|---|---:|---:|']
    for e in entries:
        if e['id']=='h11_lock_lift':e['motion']['tilt_axis']=[-1,0,0]
        text.append(f"| {e['fbx']} | {e['pivot']} | {e['world_pivot']} | {e['tris']} | {e['MeshParts']} |")
        e['validation_status']='FAILED';e['clearances']=results[e['id']]
    text+=['','H6 slide axis +X, range -7..0, speed 3, dwells closed 1.2/open 2.0, phase 0. Exact period 7.8666667 (source rounds to 7.8667).',
    'H11 gate axis +Y, range -1.3..0, speed 2, dwells open 5.5/closed 2.8, phase -1.3, period 9.6.',
    'H11 lift: 3.2 x 4.0 timber deck, 0.15 thick below its top-center pivot, rise 4 at 2 studs/s; tilt 4 degrees toward north around the north edge z=-25 on Roblox -X (raises the south edge). Return 1.5 seconds. Draft schedule begins rise at t=5.45 while gate is still closing and returns by t=8.95. This is explicitly not approved synchronization.',
    'Signal at [0,5,-25.4], world [150,121,-277.4]; separate h11_lock_chamber__SignalRed and __SignalGreen Neon MeshParts. Optional Studio PointLight range 6, brightness 1, appropriate color; green when gate down, red otherwise. Red/green are separate toggle materials; no Blender light is exported.',
    'Workbench eye camera height 5 studs; five-stud capsule; eye and 3/4 views per prop and contact_sheet.png. Blend sources and mesh triangle/component caches included.',
    '', '## Validation',
    'Read fitcheck_movers_pass1_failed.txt for full swept minima, times, offsets and locations. Fine sampling uses dt<=0.005 s, <=0.015 stud translations, <=0.134 degree return tilt, with a separate <=0.25 degree top tilt sweep. Triangles versus oriented source boxes use SAT signed separation lower bounds, not exact Euclidean distances. Base primitives are conservative AABBs. Bank slope checks use conservative enclosing boxes. Threshold 0.05; no contact exemptions.',
    '| Prop | Obstacle class | Minimum signed lower bound | Time / offset | Location |','|---|---|---:|---|---|']
    for e in entries:
        for kind,b in results[e['id']].items():text.append(f"| {e['id']} | {kind}: {b['obstacle']} | {b['clearance']:.6f} | {b['time']:.4f} / {b['offset']:.4f} | {b['location']} |")
    text+=['','## Conflicts requiring source/design decisions',
    '- H6 board at bottom-center felt pivot has zero felt clearance. Its exact 7-stud pointed board crosses unbroken rail5 and the specified west frame post; pocket/track apertures are absent from source boxes.',
    '- H11 gate intentionally sinks through the lock felt and touches/overlaps chamber rails at its edges. Strict clearance cannot pass with an uncut felt and unaltered rails.',
    '- Lift top flush at rest means zero felt clearance and its thin body occupies the felt thickness. Lock felt must be replaced or visually masked by the moving platform; exit rail requires a designed opening.',
    '- A 3.5-second rise+return does not fit a 2.8-second fully closed dwell. Need a timing decision before approved Lua synchronization. North-edge hinge selected so south edge rises toward north downhill release.',
    '- Static foundations contact source felt and specified winches overlap rail geometry. Required 0.05 separation conflicts with mounted bases.',
    '- H6 exact blocker union is 7.000051 long due to rounded source .4243 end boxes. Painted skins project .018 beyond blockers. H11 source blocker fully covered; platform plank gaps .005. Mesh visual versus blocker differences are decorative only.',
    '', '## Render and handoff status',
    'ALL PASS has not been reached. No passing certificate is fabricated. Final Cycles OptiX renders are conditional on ALL PASS and were not run. render_pc.py supports blend/FBX inputs and rest/max states; refuses final rendering without a passing certificate, and refuses CPU fallback if OptiX is unavailable.',
    'Do not import these as validated final movers. Studio calibration still required: H11 ball release clamp(entrySpeed*0.5,1.5,7), exact maximum 7 for the ace. H9/H14/H17 untouched.']
    (SRC/'movers_pass1_summary.md').write_text('\n'.join(text))
    (SRC/'movers_manifest.json').write_text(json.dumps(dict(movers=entries),indent=2))
    hashes={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('in','lib') for p in (BASE/folder).iterdir() if p.is_file()}
    (SRC/'input_hashes.json').write_text(json.dumps(hashes,indent=2))
    with (SRC/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Contact sheet, Lua draft, manifest and failed-validation handoff written.\n')
if __name__=='__main__':main()
