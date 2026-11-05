# SRV-132 movers pass 4 (p7 movers + p8 H11 retune)

Source of truth: `in/holes.json` (p8, sha256 f13a1ede238ad780...). Inputs unmodified. All 18 exports round-trip verified; fitcheck **ALL PASS** (`src/fitcheck_movers_pass4_validated.txt`).
Conventions: 1 unit = 1 stud, Roblox Y-up; FBX forward -Z, up Y, scale 1, textures embedded; one MeshPart per material; all decoration CanCollide=false (gameplay collision stays the holes.json boxes); red/cream (#B83A35/#FFF0C9, .6) only on moving parts.

## Exports

| Prop | FBX | Hole | Export pivot (hole-local) | World pivot | Tris | MeshParts | Min clearance (obstacle, angle/time) |
|---|---|---|---|---|---:|---:|---|
| h06_sluice_gate | `fbx/h06_sluice_gate.fbx` | h06 | [0, 0, -28] | [280, 26, 227] | 300 | 4 | 0.1500 (rail5__cut3, t 1.33 s) |
| h06_sluice_frame | `fbx/h06_sluice_frame.fbx` | h06 | [0, 0, -28] | [280, 26, 227] | 476 | 3 | 0.0500 (pocket_e23, t 0.0 s) |
| h11_lock_gate | `fbx/h11_lock_gate.fbx` | h11 | [0, 0, -21.25] | [150, 116, -273.25] | 180 | 4 | 0.1500 (rail4__cut1__cut0, t 5.8 s) |
| h11_lock_lift | `fbx/h11_lock_lift.fbx` | h11 | [0, 0, -25] | [150, 116, -277] | 276 | 3 | 0.1500 (rail5__cut1__cut0__cut1, t 6.4025 s) |
| h11_lock_chamber | `fbx/h11_lock_chamber.fbx` | h11 | [0, 0, -23] | [150, 116, -275] | 1684 | 6 | 0.1000 (felt_approach__cut2, t 0.0 s) |
| h11_quay_lip | `fbx/h11_quay_lip.fbx` | h11 | [0, 3.5, -25.45] | [150, 119.5, -277.45] | 72 | 2 | 0.1500 (rail6__cut0__cut2, t 6.9975 s) |
| h09_windpump_vanes | `fbx/h09_windpump_vanes.fbx` | h09 | [0, 4.12, -17.75] | [347.75, 74.12, -110] | 520 | 4 | 0.0200 (felt_approach, angle 17.00 deg) |
| h09_windpump_hub | `fbx/h09_windpump_hub.fbx` | h09 | [0, 4.12, -17.75] | [347.75, 74.12, -110] | 280 | 4 | 0.1750 (anchor_pump_house_1, t 0.0 s) |
| h14_ore_bucket | `fbx/h14_ore_bucket.fbx` | h14 | [0, 10.35, -24] | [-300, 160.35, -176] | 588 | 5 | 0.0750 (felt_lane, angle 2.51 deg) |
| h14_cableway_trestle | `fbx/h14_cableway_trestle.fbx` | h14 | [0, 0, -24] | [-300, 150, -176] | 380 | 4 | 0.1000 (rail1, t 0.0 s) |
| h17_shadow_arms | `fbx/h17_shadow_arms.fbx` | h17 | [0, 0, -36] | [-345, 190, 196] | 624 | 3 | 0.0510 (felt_dial_a, angle 0.00 deg) |
| h17_plinth | `fbx/h17_plinth.fbx` | h17 | [0, 0, -36] | [-345, 190, 196] | 1008 | 5 | 4.1053 (cup, t 0.0 s) |
| h07_bridge_parapets | `fbx/h07_bridge_parapets.fbx` | h07 | [0, 0, -42] | [340, 70, 108] | 912 | 3 | 1.8295 (cup, t 0.0 s) |
| h07_bridge_skirts | `fbx/h07_bridge_skirts.fbx` | h07 | [0, 0, -42] | [340, 70, 108] | 48 | 1 | 0.4990 (felt_lane, t 0.0 s) |
| h07_gap_floor_mist | `fbx/h07_gap_floor_mist.fbx` | h07 | [0, -4.25, -42] | [340, 65.75, 108] | 24 | 2 | 2.5000 (rail1, t 0.0 s) |
| h07_teleport_pads | `fbx/h07_teleport_pads.fbx` | h07 | [0, 0, -25] | [340, 70, 125] | 60 | 2 | 0.5000 (rope_rail12@bridge2_island, t 0.0 s) |
| h07_teleport_pad_exit | `fbx/h07_teleport_pad_exit.fbx` | h07 | [3.8, 0, -59] | [343.8, 70, 91] | 668 | 2 | 0.1470 (cup@bridge2_exit, t 0.0 s) |
| dam_crest_parapets | `fbx/dam_crest_parapets.fbx` | world | [0, 115.7, -305] | [0, 115.7, -305] | 80 | 2 | n/a: world piece, no holes.json collision nearby; exact deck/parapet/skirt boxes covered 100% |

Pad instances: bridge1_entry [0, 0, -25] -> world [340, 70, 125]; bridge1_island [0, 0, -38] -> world [340, 70, 112]; bridge2_island [3.8, 0, -44] -> world [343.8, 70, 106]; bridge2_exit [3.8, 0, -59] -> world [343.8, 70, 91].

## Notes per prop

- **h09_windpump_vanes**: Four lollipop vanes 2.4 wide, radial .6..4.1, depth .4, circular tips r 4.1 (tip arc vertices at every strip corner): covers all 24 holes.json strips. Brass hub square 2.4 x 2.4 (union of the overlapping vane roots) + Iron front boss. Red/cream .6 radial bands from r 1.2. Vane tip passes .02 above felt (holes.json design clearance) and .05 in front of rails rail2/rail3/house13/house18 and the pump-house facade plane z -18.
- **h09_windpump_hub**: Static Iron bearing housing r .45 behind the rotor (front face z -18.12, .17 behind the vane back face), timber mast to the roof line y 8, small timber roof tower with tail vane (y 8..12). Pivot = hub [0,4.12,-17.75]. The pump-house body itself (holes.json anchor envelope) is not part of this pass.
- **h14_ore_bucket**: Riveted bucket 2.1 x 2 x 1.8 exactly on blocker 1 (LipRed/LipCream/LipRed .6 bands + Iron rim), rock-candy heap, hanger rod/spreader/side straps, eye r .28 (|z|<=.045) turning between the trestle twin cap beams. FOOT SHOWN (Game Art Bot): dark Iron skid in the 2.1 x .4 x .15 collider envelope (plate .11 + rivet heads), bottom arc r 10.275 about the hinge: .075 above felt at rest and never lower in the swing (the box collider corner itself dips to .0215 at 5.83 deg).
- **h14_cableway_trestle**: Built (the existing models/cableway_trestle is the separate world backdrop 6x30x6 piece). Legs x +-5 (.8 square, outside rails, .1 gap) on sandstone footings, twin cap beams y 10.35..11.35 with a .4 slot for the hanger eye, top spacer, knee braces, Iron bearing plates. Pivot = anchor base [0,0,-24].
- **h17_shadow_arms**: Four slate arms exactly on the holes.json blockers (r 8.2..11.5, 3.6 wide, top y .9) with red/cream .6 radial bands on both sweep faces; visual underside lifted to y .051 for >=.05 felt clearance (collider still reaches the felt).
- **h17_plinth**: Solid sandstone plinth = convex shell enclosing all 48 gnomon_plinth_* strips (collision not enlarged), top y 1.2 with MintWhite dial face and 12 Licorice hour ticks; Brass base, Bubblegum/MintWhite striped post (covers gnomon occluder 1.2 x 7 x 1.2) and Bubblegum triangular fin to y 9. Pivot [0,0,-36].
- **h07_bridge_parapets**: rope_rail6/7/12/13 exact boxes (top y 3.5): timber posts, sandstone panels, rope course, timber cap; mesh tiles the boxes exactly (no static red/cream). Pivot = rope_bridges anchor [0,0,-42].
- **h07_bridge_skirts**: Four exact skirt boxes, y -4..-.5 (exact boxes overlap the parapets at y -.5..0; parapet mesh covers that band, avoiding coplanar z-fighting). Pivot [0,0,-42].
- **h07_gap_floor_mist**: Opaque comfort floor 30 x .5 x 32 (top y -4) + mist card 30 x 1 x 32 (Mist material: Transparency 0.5, CastShadow off; optional ForceField/Neon at Transparency .85). Ball pit/respawn unchanged. Pivot = gap_view anchor [0,-4.25,-42].
- **h07_teleport_pads**: Flush player-only pads 3 x .02 x 2 (base on felt, top .02): PadLime #D8FF6A Neon frame + PadCore #2F5D3A centre. Not ball teleports. One FBX, 3 instances (bridge1_entry, bridge1_island, bridge2_island); pivot = pad base centre.
- **h07_teleport_pad_exit**: bridge2_exit pad at its exact holes.json box, notched r .65 around the cup (holes.json pad overlaps the H7 cup [3,0,-60] r .5): see Spec questions.
- **dam_crest_parapets**: WORLD coords, pivot = deck centre [0,115.7,-305] (confirmed). Deck 92 x .6 x 8 (top y 116), solid parapets 92 x 3.5 x .6 at z -309.3/-300.7 (MintWhite with PepRed coping), skirts 92 x 8 x .6 at y 112. Matches crest walk path y 116, x -46..46.
- **h11_lock_chamber**: p8 refit: slot cheeks lowered to y -1.5..-.5 to clear the .4-thick approach felt slab; supports/wheels/bollards/signal unchanged (all p8 checks pass: lane 11 wide, approach from z -6, quay 4.4 with .4 pockets). Mover clearances to chamber >= .31.
- **h11_lock_gate**: Unchanged geometry; p8 timing 10.7 s.
- **h11_lock_lift**: Unchanged 3.2 x 3.35 deck; p8 schedule, level (no tilt).
- **h11_quay_lip**: Unchanged 3.6 x 1.5 x .2; p8 flush 7.0-9.2.

## Clearances (fitcheck_pass4.py)

Triangle vs exact convex part SAT lower bounds. Rotors swept 0.5 deg over 360; bucket 0.25 deg over -9..+9 plus dt .01 s period sampling; H6/H11 dt .0025 s plus breakpoints. Thresholds .05 general, .15 mover-to-static-prop and approved cut residuals; H9 vanes-to-felt .02 per holes.json.
- Overall minimum: 0.0200 — felt_approach (felt) at angle 17.0 deg, location [0.137, 0.023, -17.683] (holes.json-specified H9 vane felt clearance).
- Overall minimum excluding that design value: 0.0500 — pocket_e23 (rail/wall), location [3.888, 2.608, -28.283].
- H9 vanes: felt .0200 at 17.0 deg (every 90 deg the tip vertex passes y .02); rails/facade plane .0500 (z gap, all angles); hub 0.170.
- H14 bucket: felt 0.0750 (skid arc); trestle cap beams 0.155 at +-9 deg; rails >= 1.364.
- H17 arms: felt .051 (lifted underside); plinth shell 0.400; plinth hull max radius 7.800 vs arm inner edge 8.2 -> radial gap 0.400.
- H11 (p8): gate 0.150, deck 0.150, lip 0.150 (cut residuals >= .15); chamber static 0.100; moving pairs gate/deck 0.150, lip/deck 0.350.
- H6 (re-run vs p8, unchanged geometry): gate 0.150, frame 0.050; supporting neck-felt contact .02 is the documented exception.

## Motion (src/motion.lua; registry_movers.motion identical)

- `M.windpump(t)` = 20*t deg about hole +Z through [0,4.12,-17.75]; `M.windpumpCFrame(pivot,t)`.
- `M.oreBucket(t)` = 9*sin(2*pi*t/4) deg about hole +Z through hinge [0,10.35,-24]; `M.oreBucketCFrame(pivot,t)`.
- `M.shadowArm(t)` = 12*t deg about hole +Y through [0,0,-36]; `M.shadowArmCFrame(pivot,t)`.
- H11 p8 (10.7 s, overrides pass 3): `lockGate` open -1.3 0-5.5, rise 5.5-5.8, closed 5.8-10.4, lower 10.4-10.7; `lockLift` rise 6.1-7.1, level top 7.1-9.1, down 9.1-10.1, tilt 0; `quayLip` sink 6.9-7.0, flush (top y 4) 7.0-9.2, rise 9.2-9.3, raised top y 5 otherwise; `releaseSpeed` unchanged. `M.sluice` unchanged.
- `pivot` = world CFrame of the export pivot incl. hole world_yaw (H9 yaw -90 -> world axis [-1,0,0]; H14 yaw 180 -> [0,0,-1]; H17 yaw 0).

## Previews

FINAL Cycles OptiX: `out/previews/cycles/pass4/` (36 views + `contact_sheet_pass4.png`): rest + full travel (vanes 0/45, bucket -9/0/+9, arms 0/45) eye (5 studs, reference capsule) and 3/4 for every new prop; H7/H9/H14/H17 tee views at eye 5. Workbench quick looks in `out/previews/`.

## Included / skipped

- Included: h09_windpump_vanes, h09_windpump_hub, h14_ore_bucket (+skid), h14_cableway_trestle, h17_shadow_arms, h17_plinth (+gnomon), h07_bridge_parapets, h07_bridge_skirts, h07_gap_floor_mist, h07_teleport_pads (3) + h07_teleport_pad_exit, dam_crest_parapets; H11 p8 refit (chamber cheeks) + motion retune.
- Skipped (not movers / not these pieces, or unspecified): H7 island_hoodoo, island_respawn_stone, island_edge_lip; H9 pump_house body, water_tank, sign_bypass, felt_arrow_bypass; H14 ore_piles, loading_dock, safe_bank_sign/arrow, timing_arrow, overhead main cableway (world, unspecified); H17 hour_stones (envelope conflicts, see below), safe_east_wait marker; all cup flags (course-wide prop); dam endpoint pads [+-46,116,-305] 4 x .1 x 4 and 8 x .6 x 8 landings (not in this brief); world cableway_trestles (existing models/ piece).

## Spec questions (holes.json wins; logged, not invented)

1. **H7 bridge2_exit player pad overlaps the H7 cup.** Pad [3.8,0,-59] 3 x 2 spans x 2.3..5.3, z -60..-58; cup [3,0,-60] r .5. Visual notched r .65 round the cup (h07_teleport_pad_exit); please move the pad (e.g. east so x >= 4.15 clears cup + .15) or confirm the notch.
2. H7 bridge1_island pad [0,0,-38] (z -39..-37) covers island_respawn_stone anchor [0,0,-38.5] (.8 x .8); respawn stone not built. Confirm which marker wins.
3. H9 vane tip felt clearance is .02 in holes.json ("clearance .02"), below the brief .05 rule: visual kept exactly r 4.1 to cover the 24 strips; fitcheck uses .02 for that pair. Shrink to r 4.07 if .05 is required (strip corners would then poke .03 out of the visual).
4. H9 rotor back face is .05 in front of rails rail2/house13/rail3/house18 and the pump_house envelope face (z -18), below the .15 static-prop rule; set by holes.json pivot/depth. Pump-house builder must keep its facade at z <= -18 (ideally recess behind the rotor).
5. H14 foot collider (2.1 x .4 x .15 box) corner dips to .0215 above felt at 5.83 deg swing (.0373 at 9 deg); the visual skid uses an arc so it never drops below .075. Consider chamfering the collider foot.
6. H14 hinge pivot y 10.35 equals the cableway_trestle beam occluder bottom: the hanger eye turns in a .4 slot between twin cap beams (.155 clearance). Occluder envelope beam [10,1,1] is realised as the twin-beam trestle.
7. H17 arm colliders start at the felt (y 0); visual underside lifted .051. H17 hour_stones envelope [22,1.2,22] at the dial centre reaches r 11 inside the arm sweep (r <= 11.64) and lies on playable felt: not built pending positions/sizes.
8. H17 brief says plinth radius 7.5; the 48 circumscribed strips reach r 7.800 at their corners, so the visual is the convex shell of the strips (min apothem 7.500).
9. H7 exact skirt boxes (y -4..0) overlap the parapet boxes (y -.5..3.5) by .5; skirt mesh stops at y -.5.
10. props.md H11 rows are stale vs p8 (gate speed 2.0, deck 2 studs/s, 2.5 s dwell, lip [5.35,8.05)); holes.json p8 used: gate 4.333 studs/s, deck 4 studs/s, 2 s dwell, lip flush [7.0,9.2] with speed-10 transitions 6.9-7.0 / 9.2-9.3 outside the flush window.
11. Brief cites `_work/p8-report.md`; the copy used is `in/p8-report.md`. holes.json has no world dam record; dam boxes from brief/p7-report/course.md (an older ~/sc world.json shows only the crest path y 116, x -46..46, consistent).
12. H11 gate_light anchor [0,5,-25.4] sits at the raised lip top face (y 5, z -25.55..-25.35); pass-3 signal housing stays at [0,5.9,-26] behind it.

## Files

`src/pass4_specs.json`, `src/registry_movers.py`, `src/gen_pass4.py`, `src/build_movers.py`, `src/fitcheck_pass4.py`, `src/fitcheck_movers_pass4_validated.txt`, `src/fitcheck_results_pass4.json`, `src/verify_exports_pass4.py`, `src/export_verification_pass4.json`, `src/render_pc.py`, `src/render_pass4.ps1`, `src/motion.lua`, `src/movers_manifest.json`, `src/<id>.blend`, `src/<id>_components.json` (convex parts), `src/<id>_triangles.json`. Pass-3 snapshots: `*_pass3.*`.

Handoff: import FBX at scale 1, re-sync all H11 meshes and motion (10.7 s) and the new props; place each export pivot at the listed hole-local pivot transformed by the hole world_offset/world_yaw (dam: world coords).