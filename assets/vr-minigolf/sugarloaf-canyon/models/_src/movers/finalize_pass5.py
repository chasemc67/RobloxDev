import json,datetime,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;O=S.parent;R=O/'previews/cycles/pass5'
def stamp(msg):
    with (S/'PROGRESS.md').open('a') as f:f.write('\n'+datetime.datetime.now().astimezone().isoformat()+' '+msg+'\n')
def sheet():
    files=sorted(p for p in R.glob('*.png') if not p.name.startswith('contact_sheet'))
    canvas=Image.new('RGB',(1000,((len(files)+3)//4)*220),'#24212a');d=ImageDraw.Draw(canvas)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGB');im.thumbnail((250,195));x=i%4*250;y=i//4*220;canvas.paste(im,(x+(250-im.width)//2,y));d.text((x+4,y+198),p.stem[:38],fill='white')
    canvas.save(R/'contact_sheet_pass5.png')
    return files
if __name__=='__main__':
    files=sheet();print('contact sheet',len(files))
def finish():
    files=sheet();fit=json.loads((S/'fitcheck_results_pass5.json').read_text());ver=json.loads((S/'export_verification_pass5.json').read_text());man=json.loads((S/'movers_manifest.json').read_text())
    assert fit['all_pass'] and len(ver)==len(man['movers'])
    assert all(all(v[k] for k in ('pass_mesh_counts','pass_bbox','pass_origins','pass_material_merge','pass_budget','pass_textures_embedded')) for v in ver)
    spec=fit['pass5_spec'];previews=[str(p.relative_to(O)).replace('\\','/') for p in files]+['previews/cycles/pass5/contact_sheet_pass5.png']
    man.update(pass_number=5,source='in/holes.json',source_sha256=hashlib.sha256((O.parent/'in/holes.json').read_bytes()).hexdigest(),fitcheck_certificate='src/fitcheck_movers_pass5_validated.txt',previews_pass5=previews,preview_engine='Cycles OptiX (RTX 4090)',preview_status='FINAL',tool_used='Steps 1-2 + first fitcheck: Claude Code claude-opus-5-5; remainder: Codex')
    for e in man['movers']:
        if e.get('collision_only'):
            e.update(CanCollide=True,Transparency=1,CastShadow=False,motion_helper='M.windpump / M.windpumpCFrame' if e['id'].startswith('h09') else 'M.oreBucket / M.oreBucketCFrame')
        if e['id']=='h09_windpump_vanes':e['CanCollide']=False
        if e['id'].startswith('h17_hour_stone_'):
            e.update(CanCollide=e['collidable'],pivot_note='base centre',inward_corner_chamfer=0 if e['collidable'] else .48)
    (S/'movers_manifest.json').write_text(json.dumps(man,indent=2))
    lines=['# SRV-132 movers pass 5 (p9b)','',man['tool_used']+'.','',f"Source of truth: in/holes.json; SHA256 {man['source_sha256']}. Inputs unchanged. All {len(ver)} exports round-trip PASS; full fitcheck ALL PASS.",'','## Changes','',
    'H7 pads use the exact p9b positions; exit cup notch removed. Respawn sandstone marker is .8 x .02 x .8, base-centre pivot [0,0,-38.5], static with no red/cream. H17 nine separate numbered stones: XII/I/III/IV/VII/VIII/IX/X/XI; no II/V/VI. XII/III/IX collide and remain unchanged. Six decorative stones have only their inward vertical corner chamfered (.48 along both adjoining edges), inside the exact 1.2 x .8 x 1.2 box.',
    'H9 collision-only mesh contains the exact 48 strips, clipped to r 4.06; visual r .6..4.1 stays collision OFF. H14 collision-only foot contains the exact 14 strips. Skid underside follows the strip bottoms, with raised outer corners; upper skid and rivet vertices may sit above the local strip underside within the bucket footprint as allowed by the addendum. Full sweep confirms the visual never falls below the collider. Unaffected exports preserved.','',
    '## Clearances and angles','',
    'H9 collider minimum 0.05999982 at 171.5 deg (refined 171.502 deg); visual 0.02000009 at 17 deg, art only. H14 centre strips 0.06015487 at +/-2.5 deg, rest 0.06125031; outer corners 0.15021156 at +/-5.9 deg. Approved .06 override applies only to H9/H14 blocking colliders.',
    'Respawn-to-pad gaps: bridge1_entry 12.1, bridge1_island 2.6, bridge2_island 4.1, bridge2_exit 19.1; nearest rail rope_rail6 1.6; no island pad overlap. Exit cup-rim gap .15.',
    f"Hour-stone rail minimum {spec['H17 hour stones vs arm+head sweep']['rail_stone_min']:.8f}; decorative minimum {spec['H17 hour stones vs arm+head sweep']['decorative_min']:.8f} (XI, 310 deg; VIII also 40 deg). Exact per-stone angles and per-prop results are in fitcheck_results_pass5.json.",'',
    'Full checks include unchanged props: rotors .5 deg over 360; bucket .05 deg over +/-9 plus period sampling; H6/H11 timing and approved cuts. Round-trip checks cover mesh counts, triangles, bounding boxes, zero local mesh origins, material merging, embedded textures, and <20k triangles per MeshPart.','',
    '## Motion and import','',
    'motion.lua unchanged. Both H9 meshes reuse M.windpump / M.windpumpCFrame (20 deg/s, 18 s, +Z, pivot [0,4.12,-17.75]). Both H14 meshes reuse M.oreBucket / M.oreBucketCFrame (+/-9 deg, 4 s, +Z, pivot [0,10.35,-24]). H17 arms/heads retain M.shadowArm. Import at scale 1; FBX -Z forward / Y up; Blender +Y = Roblox -Z. One MeshPart per material. Collision-only meshes: Transparency 1, CanCollide ON, CastShadow OFF. Visual vanes OFF; only XII/III/IX hour stones ON.','',
    '## FBX list, triangle totals and pivots','', '| FBX (relative to out) | Tris | MeshParts | Hole-local pivot | Collision |','|---|---:|---:|---|---|']
    for e in man['movers']:lines.append(f"| {e['fbx']} | {e['tris']} | {e['MeshParts']} | {e['pivot']} | {e['CanCollide']} |")
    lines+=['','## Previews','',f'{len(files)} Cycles OptiX views plus contact_sheet_pass5.png, inspected; one framing fix for marker and bucket foot views. Eye height 5 studs; H7 pad assembly and tee, H17 ring eye/top/chamfer and tee, H9 vanes 0/45 with collider overlay and tee, H14 foot/skid -9/0/+9 close-ups and assembly views plus tee. Cyan wire overlay is diagnostic only.']+[f'- {p}' for p in previews]
    lines+=['','## Spec questions','',
    '1. Game Art Bot: exact decorative hour-stone boxes clear the arm blocker sweep by only .04105264, below .15. Per addendum, visual inward-corner chamfers now clear by .26558484; collision remains OFF. Rail stones remain exact and clear by .26000201.',
    '2. Game Art Bot: bridge2_exit exact pad box touches rope_rail13 and rail18 at z=-58 (gap 0). Mesh containment is verified; classified JUNCTION INHERITED per addendum. Flush .02 player pad, no ball collision; position [5.15,0,-59] retained.',
    '3. Source marker thickness is .02 (holes.json), despite the brief describing a low sandstone stone; source dimensions retained.',
    '', '## Files and execution','',
    'Generators: registry_movers.py, gen_pass5.py, gen_p5_profile.py, build_movers.py. Validation: fitcheck_pass5.py, fitcheck_results_pass5.json, fitcheck_movers_pass5_validated.txt, verify_exports_pass5.py, export_verification_pass5.json. Rendering: render_pc_pass5.py, render_batch_pass5.py, render_fix_pass5.py. All Blender invocations used blender_pass4.ps1 sequentially. No Roblox Studio access. No Blender process remains.']
    (S/'movers_pass5_summary.md').write_text('\n'.join(lines),encoding='utf-8')
    (S/'README.md').write_text('SRV-132 pass 5 p9b complete. See movers_pass5_summary.md and movers_manifest.json. Full fitcheck ALL PASS; all FBX exports round-trip verified. motion.lua unchanged; new colliders reuse windpump/oreBucket. Final Cycles OptiX previews: out/previews/cycles/pass5/contact_sheet_pass5.png. Spec questions: decorative source box gap .041 and inherited H7 pad/rail junction.\n')
    (O/'README.md').write_text((S/'README.md').read_text())
    stamp('Manifest, README and summary updated. P5 STEP 7 DONE')
