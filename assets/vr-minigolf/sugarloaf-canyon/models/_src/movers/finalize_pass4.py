"""P4 step 6 contact sheet (--sheet) and step 7 manifest / README / summary / DONE4."""
import json,datetime,hashlib,sys,math
from pathlib import Path
from PIL import Image,ImageDraw
from registry_movers import REG,HOLES,HOLES_PATH,H11_CYCLE
S=Path(__file__).resolve().parent;O=S.parent;B=S.parents[1]
R=O/'previews/cycles/pass4'
# Pass 4b H17 arm/head split radius, as measured by fitcheck_pass4 coverage (gen_pass4.ARM_SPLIT).
ARM_SPLIT=json.loads((S/'fitcheck_results_pass4.json').read_text())['coverage']['h17_shadow_arms']['split_radius']
P4=[e for e in REG if e['id'].startswith(('h07_','h09_','h14_','h17_','dam_'))]
STATES={'h09_windpump_vanes':['rest','rot45'],'h14_ore_bucket':['minus9','rest','plus9'],'h17_shadow_arms':['rest','rot45'],**{f'h17_shadow_arm_head_{y}':['rest','rot45'] for y in (0,90,180,270)}}
def renders():
    out=[]
    for e in P4:
        for st in STATES.get(e['id'],['rest']):
            for v in ('eye','34'):out.append((f"{e['id']} {st} {v}",R/f"{e['id']}_{st}_{v}.png"))
        if e['id']=='h17_shadow_arms':
            for st in STATES[e['id']]:
                for v in ('eye','34'):out.append((f"h17 arms+heads assembly {st} {v}",R/f"h17_shadow_arms_assembly_{st}_{v}.png"))
    for h in ('h07','h09','h14','h17'):out.append((f'{h.upper()} tee view, eye 5 studs',R/f'{h}_tee_eye.png'))
    return out
def sheet():
    items=renders();missing=[str(p) for _,p in items if not p.exists()]
    if missing:raise SystemExit('missing renders: '+', '.join(missing))
    cols=4;w,h=400,320;rows=math.ceil(len(items)/cols)
    im=Image.new('RGB',(cols*w,rows*(h+24)+40),(35,29,37));d=ImageDraw.Draw(im)
    d.text((8,10),'SRV-132 pass 4 FINAL Cycles OptiX previews (holes.json p8). Eye views at 5 studs with 5-stud reference capsule.',fill='white')
    for i,(label,p) in enumerate(items):
        t=Image.open(p).convert('RGB');t.thumbnail((w,h));x=(i%cols)*w;y=40+(i//cols)*(h+24)
        im.paste(t,(x,y+20));d.text((x+5,y+4),label,fill='white')
    im.save(R/'contact_sheet_pass4.png');print('contact sheet',len(items),'views')
def fmt(v,n=3):return '['+', '.join(f'{x:.{n}f}'.rstrip('0').rstrip('.') if isinstance(x,float) else str(x) for x in v)+']'
def main():
    fit=json.loads((S/'fitcheck_results_pass4.json').read_text());assert fit['all_pass'],'fitcheck must pass'
    ver=json.loads((S/'export_verification_pass4.json').read_text())
    assert all(v['pass_mesh_counts'] and v['pass_bbox'] and v['pass_origins'] and v['pass_material_merge'] and v['pass_budget'] and v['pass_textures_embedded'] for v in ver)
    assert (S/'fitcheck_movers_pass4_validated.txt').read_text().strip().endswith('ALL PASS: YES')
    assert (R/'contact_sheet_pass4.png').exists() and all(p.exists() for _,p in renders())
    man=json.loads((S/'movers_manifest.json').read_text());cov=fit['coverage']
    notes={
    'h09_windpump_vanes':'Four lollipop vanes 2.4 wide, radial .6..4.1, depth .4, circular tips r 4.1 (tip arc vertices at every strip corner): covers all 24 holes.json strips. Brass hub square 2.4 x 2.4 (union of the overlapping vane roots) + Iron front boss. Red/cream .6 radial bands from r 1.2. Vane tip passes .02 above felt (holes.json design clearance) and .05 in front of rails rail2/rail3/house13/house18 and the pump-house facade plane z -18.',
    'h09_windpump_hub':'Static Iron bearing housing r .45 behind the rotor (front face z -18.12, .17 behind the vane back face), timber mast to the roof line y 8, small timber roof tower with tail vane (y 8..12). Pivot = hub [0,4.12,-17.75]. The pump-house body itself (holes.json anchor envelope) is not part of this pass.',
    'h14_ore_bucket':'Riveted bucket 2.1 x 2 x 1.8 exactly on blocker 1 (LipRed/LipCream/LipRed .6 bands + Iron rim), rock-candy heap, hanger rod/spreader/side straps, eye r .28 (|z|<=.045) turning between the trestle twin cap beams. FOOT SHOWN (Game Art Bot): dark Iron skid in the 2.1 x .4 x .15 collider envelope (plate .11 + rivet heads), bottom arc r 10.275 about the hinge: .075 above felt at rest and never lower in the swing (the box collider corner itself dips to .0215 at 5.83 deg).',
    'h14_cableway_trestle':'Built (the existing models/cableway_trestle is the separate world backdrop 6x30x6 piece). Legs x +-5 (.8 square, outside rails, .1 gap) on sandstone footings, twin cap beams y 10.35..11.35 with a .4 slot for the hanger eye, top spacer, knee braces, Iron bearing plates. Pivot = anchor base [0,0,-24].',
    'h17_shadow_arms':f'Pass 4b: arm bodies only, r 8.2..{ARM_SPLIT:g} of the four holes.json blockers (3.6 wide, top y .9); the leading ends are the separate h17_shadow_arm_head_* FBXs. Arms + heads together exactly cover the blockers (coverage PASS, seamless at r {ARM_SPLIT:g}). Red/cream .6 radial bands on both sweep faces, sequence continuous into the heads; visual underside lifted to y .051 for >=.05 felt clearance (collider still reaches the felt).',
    **{f'h17_shadow_arm_head_{y}':f"Pass 4b: leading end (head) of the yaw-{y} arm as its own mesh, r {ARM_SPLIT:g}..11.5 x 3.6 wide x y .051..0.9, inside its holes.json blocker; SQUARED-OFF leading faces (plain boxes, no rounding/bevel; pending Game Art Bot's OK). Slate core + red/cream bands (cream/red/cream) continuing the arm sequence. Pivot [0,0,-36], same motion as the arms (M.shadowArm, 12 deg/s about +Y): swap-in without rebuilding arms." for y in (0,90,180,270)},
    'h17_plinth':'Solid sandstone plinth = convex shell enclosing all 48 gnomon_plinth_* strips (collision not enlarged), top y 1.2 with MintWhite dial face and 12 Licorice hour ticks; Brass base, Bubblegum/MintWhite striped post (covers gnomon occluder 1.2 x 7 x 1.2) and Bubblegum triangular fin to y 9. Pivot [0,0,-36].',
    'h07_bridge_parapets':'rope_rail6/7/12/13 exact boxes (top y 3.5): timber posts, sandstone panels, rope course, timber cap; mesh tiles the boxes exactly (no static red/cream). Pivot = rope_bridges anchor [0,0,-42].',
    'h07_bridge_skirts':'Four exact skirt boxes, y -4..-.5 (exact boxes overlap the parapets at y -.5..0; parapet mesh covers that band, avoiding coplanar z-fighting). Pivot [0,0,-42].',
    'h07_gap_floor_mist':'Opaque comfort floor 30 x .5 x 32 (top y -4) + mist card 30 x 1 x 32 (Mist material: Transparency 0.5, CastShadow off; optional ForceField/Neon at Transparency .85). Ball pit/respawn unchanged. Pivot = gap_view anchor [0,-4.25,-42].',
    'h07_teleport_pads':'Flush player-only pads 3 x .02 x 2 (base on felt, top .02): PadLime #D8FF6A Neon frame + PadCore #2F5D3A centre. Not ball teleports. One FBX, 3 instances (bridge1_entry, bridge1_island, bridge2_island); pivot = pad base centre.',
    'h07_teleport_pad_exit':'bridge2_exit pad at its exact holes.json box, notched r .65 around the cup (holes.json pad overlaps the H7 cup [3,0,-60] r .5): see Spec questions.',
    'dam_crest_parapets':'WORLD coords, pivot = deck centre [0,115.7,-305] (confirmed). Deck 92 x .6 x 8 (top y 116), solid parapets 92 x 3.5 x .6 at z -309.3/-300.7 (MintWhite with PepRed coping), skirts 92 x 8 x .6 at y 112. Matches crest walk path y 116, x -46..46.',
    'h11_lock_chamber':'p8 refit: slot cheeks lowered to y -1.5..-.5 to clear the .4-thick approach felt slab; supports/wheels/bollards/signal unchanged (all p8 checks pass: lane 11 wide, approach from z -6, quay 4.4 with .4 pockets). Mover clearances to chamber >= .31.',
    'h11_lock_gate':'Unchanged geometry; p8 timing 10.7 s.','h11_lock_lift':'Unchanged 3.2 x 3.35 deck; p8 schedule, level (no tilt).','h11_quay_lip':'Unchanged 3.6 x 1.5 x .2; p8 flush 7.0-9.2.'}
    previews=[str(p.relative_to(O)).replace(chr(92),'/') for _,p in renders()]+['previews/cycles/pass4/contact_sheet_pass4.png']
    for e in man['movers']:
        pm=fit['per_prop_minima'].get(e['id'])
        if pm:e['minimum_clearance']=dict(value=pm['clearance'],obstacle=pm['obstacle'],kind=pm['kind'],angle_deg=pm.get('angle'),time_s=pm.get('time'),offset=pm.get('offset'),location=pm.get('location'),threshold=pm['threshold'])
        e['clearances']=fit['results'].get(e['id'],{})
        if e['id'] in cov:e['coverage']=cov[e['id']]
        e['roundtrip']=next((v for v in ver if v['id']==e['id']),None)
        if e['id'] in notes:e['notes']=notes[e['id']]
        e['validation_status']='PASS (pass 4, holes.json p8)'
        if e['id'] in {x['id'] for x in P4}:e['previews']=[p for p in previews if Path(p).name.startswith(e['id']+'_')]
        if e['id'].startswith('h11_'):
            e['required_collision_cuts']=[c for c in fit['cuts'] if c['prop']==e['id']]
            e['motion_p8']={'h11_lock_gate':dict(cycle_s=H11_CYCLE,open=[0,5.5],rise=[5.5,5.8],closed=[5.8,10.4],lower=[10.4,10.7],offsets=dict(open=-1.3,closed=0)),
                'h11_lock_lift':dict(cycle_s=H11_CYCLE,rise=[6.1,7.1],top_level=[7.1,9.1],down=[9.1,10.1],height=4,tilt_deg=0,release='clamp(entry*0.5,1.5,7) toward -Z at [0,4,-27] during 7.1-9.1'),
                'h11_quay_lip':dict(cycle_s=H11_CYCLE,sink=[6.9,7.0],flush=[7.0,9.2],rise=[9.2,9.3],raised_top_y=5,flush_top_y=4,offset_flush=-1,export_pivot=e['pivot'],spec_centre_pivot=[0,4.25,-25.45])}.get(e['id'])
            if e['id']=='h11_lock_lift':e['motion'].pop('caveat',None)
    man.update({'pass':4,'source_of_truth':str(HOLES_PATH.relative_to(B)).replace(chr(92),'/'),'source_round':'p8','source_sha256':hashlib.sha256(HOLES_PATH.read_bytes()).hexdigest(),
        'overall_min':fit['overall_min'],'overall_min_strict':fit['overall_min_strict'],'per_prop_minima':fit['per_prop_minima'],'required_studio_cuts':fit['cuts'],
        'preview_engine':'Cycles OptiX (RTX 4090)','preview_status':'FINAL','previews_pass4':previews,'motion_lua':'src/motion.lua','fitcheck_certificate':'src/fitcheck_movers_pass4_validated.txt'})
    man.pop('proposed_additional_cuts_pending_decision',None)
    (S/'movers_manifest.json').write_text(json.dumps(man,indent=2,default=float))
    M={e['id']:e for e in man['movers']}
    L=['# SRV-132 movers pass 4 (p7 movers + p8 H11 retune)','',
    f"Source of truth: `in/holes.json` (p8, sha256 {man['source_sha256'][:16]}...). Inputs unmodified. All {len(man['movers'])} exports round-trip verified; fitcheck **ALL PASS** (`src/fitcheck_movers_pass4_validated.txt`).",
    'Conventions: 1 unit = 1 stud, Roblox Y-up; FBX forward -Z, up Y, scale 1, textures embedded; one MeshPart per material; all decoration CanCollide=false (gameplay collision stays the holes.json boxes); red/cream (#B83A35/#FFF0C9, .6) only on moving parts.','',
    '## Exports','','| Prop | FBX | Hole | Export pivot (hole-local) | World pivot | Tris | MeshParts | Min clearance (obstacle, angle/time) |','|---|---|---|---|---|---:|---:|---|']
    for e in man['movers']:
        mc=e.get('minimum_clearance') or {}
        when=(f"angle {mc.get('angle_deg'):.2f} deg" if e.get('kind') in ('rotate','swing') else f"t {mc.get('time_s')} s") if mc else ''
        L.append(f"| {e['id']} | `{e['fbx']}` | {e['holes'][0]} | {fmt(e['pivot'])} | {fmt(e['world_pivot'])} | {e['tris']} | {e['MeshParts']} | {(f"{mc['value']:.4f} ({mc['obstacle']}, {when})" if mc else 'n/a: world piece, no holes.json collision nearby; exact deck/parapet/skirt boxes covered 100%')} |")
    inst=[f"{i['id']} {fmt(i['pivot'])} -> world {fmt(i['world_pivot'])}" for k in ('h07_teleport_pads','h07_teleport_pad_exit') for i in M[k]['instances']]
    L+=['','Pad instances: '+'; '.join(inst)+'.','','## Notes per prop','']+[f"- **{k}**: {v}" for k,v in notes.items() if k in M]
    ov=fit['overall_min'];os_=fit['overall_min_strict']
    L+=['','## Clearances (fitcheck_pass4.py)','',
    'Triangle vs exact convex part SAT lower bounds. Rotors swept 0.5 deg over 360; bucket 0.25 deg over -9..+9 plus dt .01 s period sampling; H6/H11 dt .0025 s plus breakpoints. Thresholds .05 general, .15 mover-to-static-prop and approved cut residuals; H9 vanes-to-felt .02 per holes.json.',
    f"- Overall minimum: {ov['clearance']:.4f} — {ov['obstacle']} ({ov['kind']}) at angle {ov.get('angle')} deg, location {fmt(ov['location'])} (holes.json-specified H9 vane felt clearance).",
    f"- Overall minimum excluding that design value: {os_['clearance']:.4f} — {os_['obstacle']} ({os_['kind']}), location {fmt(os_['location'])}.",
    f"- H9 vanes: felt .0200 at 17.0 deg (every 90 deg the tip vertex passes y .02); rails/facade plane .0500 (z gap, all angles); hub {fit['results']['h09_windpump_vanes']['h09_windpump_hub_0']['clearance']:.3f}.",
    f"- H14 bucket: felt {fit['results']['h14_ore_bucket']['felt_lane']['clearance']:.4f} (skid arc); trestle cap beams {min(v['clearance'] for k,v in fit['results']['h14_ore_bucket'].items() if k.startswith('h14_cableway_trestle')):.3f} at +-9 deg; rails >= {min(v['clearance'] for k,v in fit['results']['h14_ore_bucket'].items() if k.startswith('rail')):.3f}.",
    f"- H17 arms + heads (split r {ARM_SPLIT:g}): felt .051 (lifted underside, arms and all four heads); heads to plinth shell {min(v['clearance'] for h_ in ('0','90','180','270') for k,v in fit['results']['h17_shadow_arm_head_'+h_].items() if k.startswith('h17_plinth')):.3f}; arms to plinth shell {min(v['clearance'] for k,v in fit['results']['h17_shadow_arms'].items() if k.startswith('h17_plinth')):.3f}; plinth hull max radius {cov['h17_plinth']['hull_max_radius']:.3f} vs arm inner edge 8.2 -> radial gap {cov['h17_plinth']['radial_gap_to_arms']:.3f}.",
    f"- H11 (p8): gate {M['h11_lock_gate']['minimum_clearance']['value']:.3f}, deck {M['h11_lock_lift']['minimum_clearance']['value']:.3f}, lip {M['h11_quay_lip']['minimum_clearance']['value']:.3f} (cut residuals >= .15); chamber static {M['h11_lock_chamber']['minimum_clearance']['value']:.3f}; moving pairs gate/deck {fit['moving_pairs']['h11_lock_gate/h11_lock_lift']['clearance']:.3f}, lip/deck {fit['moving_pairs']['h11_quay_lip/h11_lock_lift']['clearance']:.3f}.",
    f"- H6 (re-run vs p8, unchanged geometry): gate {M['h06_sluice_gate']['minimum_clearance']['value']:.3f}, frame {M['h06_sluice_frame']['minimum_clearance']['value']:.3f}; supporting neck-felt contact .02 is the documented exception.",
    '','## Motion (src/motion.lua; registry_movers.motion identical)','',
    '- `M.windpump(t)` = 20*t deg about hole +Z through [0,4.12,-17.75]; `M.windpumpCFrame(pivot,t)`.',
    '- `M.oreBucket(t)` = 9*sin(2*pi*t/4) deg about hole +Z through hinge [0,10.35,-24]; `M.oreBucketCFrame(pivot,t)`.',
    '- `M.shadowArm(t)` = 12*t deg about hole +Y through [0,0,-36]; `M.shadowArmCFrame(pivot,t)`. Drives h17_shadow_arms AND the four h17_shadow_arm_head_* parts (same pivot, same CFrame each frame).',
    '- H11 p8 (10.7 s, overrides pass 3): `lockGate` open -1.3 0-5.5, rise 5.5-5.8, closed 5.8-10.4, lower 10.4-10.7; `lockLift` rise 6.1-7.1, level top 7.1-9.1, down 9.1-10.1, tilt 0; `quayLip` sink 6.9-7.0, flush (top y 4) 7.0-9.2, rise 9.2-9.3, raised top y 5 otherwise; `releaseSpeed` unchanged. `M.sluice` unchanged.',
    '- `pivot` = world CFrame of the export pivot incl. hole world_yaw (H9 yaw -90 -> world axis [-1,0,0]; H14 yaw 180 -> [0,0,-1]; H17 yaw 0).',
    '','## Previews','',f"FINAL Cycles OptiX: `out/previews/cycles/pass4/` ({len(previews)-1} views + `contact_sheet_pass4.png`): rest + full travel (vanes 0/45, bucket -9/0/+9, arms 0/45, each H17 head 0/45, plus H17 arms+heads assembly 0/45) eye (5 studs, reference capsule) and 3/4 for every new prop; H7/H9/H14/H17 tee views at eye 5. Workbench quick looks in `out/previews/`.",
    '','## Included / skipped','',
    '- Included: h09_windpump_vanes, h09_windpump_hub, h14_ore_bucket (+skid), h14_cableway_trestle, h17_shadow_arms + h17_shadow_arm_head_0/90/180/270 (pass 4b split), h17_plinth (+gnomon), h07_bridge_parapets, h07_bridge_skirts, h07_gap_floor_mist, h07_teleport_pads (3) + h07_teleport_pad_exit, dam_crest_parapets; H11 p8 refit (chamber cheeks) + motion retune.',
    '- Skipped (not movers / not these pieces, or unspecified): H7 island_hoodoo, island_respawn_stone, island_edge_lip; H9 pump_house body, water_tank, sign_bypass, felt_arrow_bypass; H14 ore_piles, loading_dock, safe_bank_sign/arrow, timing_arrow, overhead main cableway (world, unspecified); H17 hour_stones (envelope conflicts, see below), safe_east_wait marker; all cup flags (course-wide prop); dam endpoint pads [+-46,116,-305] 4 x .1 x 4 and 8 x .6 x 8 landings (not in this brief); world cableway_trestles (existing models/ piece).',
    '','## Spec questions (holes.json wins; logged, not invented)','',
    '1. **H7 bridge2_exit player pad overlaps the H7 cup.** Pad [3.8,0,-59] 3 x 2 spans x 2.3..5.3, z -60..-58; cup [3,0,-60] r .5. Visual notched r .65 round the cup (h07_teleport_pad_exit); please move the pad (e.g. east so x >= 4.15 clears cup + .15) or confirm the notch.',
    '2. H7 bridge1_island pad [0,0,-38] (z -39..-37) covers island_respawn_stone anchor [0,0,-38.5] (.8 x .8); respawn stone not built. Confirm which marker wins.',
    '3. H9 vane tip felt clearance is .02 in holes.json ("clearance .02"), below the brief .05 rule: visual kept exactly r 4.1 to cover the 24 strips; fitcheck uses .02 for that pair. Shrink to r 4.07 if .05 is required (strip corners would then poke .03 out of the visual).',
    '4. H9 rotor back face is .05 in front of rails rail2/house13/rail3/house18 and the pump_house envelope face (z -18), below the .15 static-prop rule; set by holes.json pivot/depth. Pump-house builder must keep its facade at z <= -18 (ideally recess behind the rotor).',
    '5. H14 foot collider (2.1 x .4 x .15 box) corner dips to .0215 above felt at 5.83 deg swing (.0373 at 9 deg); the visual skid uses an arc so it never drops below .075. Consider chamfering the collider foot.',
    '6. H14 hinge pivot y 10.35 equals the cableway_trestle beam occluder bottom: the hanger eye turns in a .4 slot between twin cap beams (.155 clearance). Occluder envelope beam [10,1,1] is realised as the twin-beam trestle.',
    '7. H17 arm colliders start at the felt (y 0); visual underside lifted .051. H17 hour_stones envelope [22,1.2,22] at the dial centre reaches r 11 inside the arm sweep (r <= 11.64) and lies on playable felt: not built pending positions/sizes.',
    '8. H17 brief says plinth radius 7.5; the 48 circumscribed strips reach r ' + f"{cov['h17_plinth']['hull_max_radius']:.3f}" + ' at their corners, so the visual is the convex shell of the strips (min apothem ' + f"{cov['h17_plinth']['hull_min_apothem']:.3f}" + ').',
    '9. H7 exact skirt boxes (y -4..0) overlap the parapet boxes (y -.5..3.5) by .5; skirt mesh stops at y -.5.',
    '10. props.md H11 rows are stale vs p8 (gate speed 2.0, deck 2 studs/s, 2.5 s dwell, lip [5.35,8.05)); holes.json p8 used: gate 4.333 studs/s, deck 4 studs/s, 2 s dwell, lip flush [7.0,9.2] with speed-10 transitions 6.9-7.0 / 9.2-9.3 outside the flush window.',
    '11. Brief cites `_work/p8-report.md`; the copy used is `in/p8-report.md`. holes.json has no world dam record; dam boxes from brief/p7-report/course.md (an older ~/sc world.json shows only the crest path y 116, x -46..46, consistent).',
    '12. H11 gate_light anchor [0,5,-25.4] sits at the raised lip top face (y 5, z -25.55..-25.35); pass-3 signal housing stays at [0,5.9,-26] behind it.',
    f"13. **H17 arm heads (pass 4b): squared-off leading faces pending Game Art Bot's OK.** Split radius r {ARM_SPLIT:g} (on a .6 band edge): arms r 8.2..{ARM_SPLIT:g}, heads r {ARM_SPLIT:g}..11.5 (1.5 x 3.6 x .849). If rounded/other heads are wanted later, only the four head FBXs change; the head must stay inside r {ARM_SPLIT:g}..11.5 / its blocker box.",
    '','## Files','','`src/pass4_specs.json`, `src/registry_movers.py`, `src/gen_pass4.py`, `src/build_movers.py`, `src/fitcheck_pass4.py`, `src/fitcheck_movers_pass4_validated.txt`, `src/fitcheck_results_pass4.json`, `src/verify_exports_pass4.py`, `src/export_verification_pass4.json`, `src/render_pc.py`, `src/render_pass4.ps1`, `src/motion.lua`, `src/movers_manifest.json`, `src/<id>.blend`, `src/<id>_components.json` (convex parts), `src/<id>_triangles.json`. Pass-3 snapshots: `*_pass3.*`.',
    '','Handoff: import FBX at scale 1, re-sync all H11 meshes and motion (10.7 s) and the new props; place each export pivot at the listed hole-local pivot transformed by the hole world_offset/world_yaw (dam: world coords).']
    (S/'movers_pass4_summary.md').write_text('\n'.join(L),encoding='utf-8')
    (S/'README.md').write_text('SRV-132 pass 4: see movers_pass4_summary.md. Source of truth in/holes.json (p8). '+str(len(man['movers']))+' exports (H6, H11 p8 retune, H7/H9/H14/H17 movers and comfort pieces, dam crest), validated certificate fitcheck_movers_pass4_validated.txt, 10.7 s H11 motion.lua, FINAL Cycles OptiX previews in previews/cycles/pass4.\n')
    with (S/'PROGRESS.md').open('a') as f:f.write(f"\n- {datetime.datetime.now().astimezone().isoformat()} Step 7: manifest/README/summary updated.\n")
    print('finalized')
if __name__=='__main__':
    sheet() if '--sheet' in sys.argv else main()
