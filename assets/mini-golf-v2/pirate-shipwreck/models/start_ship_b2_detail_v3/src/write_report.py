# plain python3: python write_report.py <out_dir>  -> report.txt (+ ../DONE)
import json, os, sys
O = sys.argv[1]; os.chdir(O)
F = json.load(open('fitcheck.json')); M = json.load(open('manifest.json'))
steps = open('logs/steps.txt', encoding='utf-8-sig').read()
tri = '\n'.join('  %-24s %-9s %6d  %s' % (k, v['collection'], v['tris'], v['status']) for k, v in sorted(M['meshes'].items(), key=lambda kv: (kv[1]['collection'], kv[0])))
rc = F['route_corridor']; S = M['source']
txt = f"""START SHIP v3 DETAIL PASS (start_ship_b2_detail_v3) - report
Date: 2026-11-05 (12:01-12:40 PST)
Agent/model: Claude Code, model claude-opus-5-5 (Opus 5.5). No model fallback was needed; no usage/model errors.
Machine: this Windows PC (Windows 11 Pro 10.0.26300, 32 threads, RTX 4090 in use by Roblox Studio -> renders on Cycles CPU).
Blender: 5.2.2 LTS (hash d13f752e3b9c, built 2026-09-15), run headless:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup <blend> --python <script> -- <args>
  One Blender process at a time, all launched from PowerShell. Studio/node/roblox processes, credentials and git were not touched. No video, no publish.
  No blender.exe was left running at the end.

SOURCE: C:\\Users\\chase\\sc_fix\\ship_upgrade_n5\\source.blend (approved v2_3), opened read-only. Saved with save_as(copy) to out/ only.
  sha256 before {S['sha256_before']}
  sha256 after  {S['sha256_after']}  -> source UNCHANGED: {S['sha256_before'] == S['sha256_after']}

STEPS (exit codes / seconds, from out/logs/steps.txt; every Blender run exited 0):
{steps}
  (draft renders went to out/logs/prev_draft*, source comparison renders to out/logs/prev_source; final evidence renders are in out/previews)

WHAT CHANGED (art)
- Hull (same name/origin): the straight bowsprit beam (12 tris) is replaced by an upcurled tapered bowsprit with rope lashings and a brass knob. Outer planking
  is recoloured Wood -> new HullWood (130,90,55); dark wales/stern plank lines stay WoodDk (80,50,30). All 4207 other source tris are retained at identical positions.
- Rigging (same name/origin, rebuilt in the 18 deg roll frame): main mast snapped at ~2/3 (stump top Y~106 in the rig frame) with a pale splinter crown,
  iron bands and a crow's nest tilted 11 deg on the stump; sagging upper yard; torn, billowed cream sails with 2-3 large scalloped rips each on the main,
  plus CanvasDk patches. Intact fore mast (original 126 height, matching COL_Mast_Fore) with nest, furled top sail and brass cap; ropes re-run.
- New Props collection (18 separate named meshes): Prop_SternCurl (tall curled stern scroll + corner volutes + stern deck-line trim),
  Prop_Figurehead (original grinning teal fish), Prop_Portholes (brass rims), Prop_Cannons (3 cannons in decorative proud ports with open lids,
  NO hull cut), Prop_PatchPlanks (+ oversized nails), Prop_CapRails, Prop_BulwarkFrames (inner ribs + stringers), Prop_CabinWindows,
  Prop_CargoCluster (barrels/crates by the cabin), Prop_Crab (waving crab gag), Prop_DoorLantern + Prop_DoorLantern_Glow (kit lantern),
  Prop_SternWheel, Prop_TreasureChest (lid ajar, gold peeking), Prop_RopeCoils, Prop_Flag (faded red, ORIGINAL emblem: crossed golf clubs
  over a golf ball on a tee, no skull), Prop_Barnacles + Prop_Seaweed (waterline).
- Palette: the packed start_ship_palette.png is updated in place. 9 new cells/materials: HullWood, RopeLt 190/160/110, Brass 200/160/70, Barnacle 115/100/92,
  Seaweed, Gold, Crab, FishTeal, Shadow. Canvas is recoloured 225/205/165 -> 225/210/175 and Red 200/50/40 -> 170/60/50 (used only by sails/flag).
  All 15 source material names are kept (Wood/WoodDk unchanged); the per-colour materials use exact sRGB->linear base colours.

TRI TABLE (triangulated)
{tri}
  TOTAL all meshes {M['tris']['total_all_meshes']}; largest single mesh {M['tris']['max_single_mesh']} {M['tris']['max_single_mesh_tris']} (<20k: {M['tris']['all_under_20k']}).
  Near-field from the tee/deck (everything except Pier, RockBumper, Ramps, and the low hull-side cannons/patches/barnacles/seaweed/portholes) is about 40k tris.

VERIFICATION (measured; details in fitcheck.md / fitcheck.json). Hard checks: {'PASS' if F['pass_hard_checks'] else 'FAIL'}
- Anchors Spawn/Tee1/RampStart/CupRef: exact float equality with the source (max diff 0).
- Collision: {F['collision']['byte_identical']}/190 byte-identical (vertex data, loops, polys, matrix_world); max transformed-vertex diff {F['collision']['max_abs_world_vertex_diff']}; names and collection identical.
- Ramps (3): geometry/material/UV/origin identical, world-vertex diff 0. DeckCabin, Pier, RockBumper, Dressing and Dressing_Glow are byte-identical.
- Walking surfaces: Y24 deck tops 382 faces / 16654.784 sq studs, identical; Y30 forecastle tops identical.
- Spawn headroom ray identical (DeckCabin roof at 29.195). Door: 80/80 rays clear in both. Tee sightlines identical to source.
- MIN ROUTE CLEARANCE of new/rebuilt geometry: {rc['min_clearance']['studs']} studs ({rc['min_clearance']['zone']}, {rc['min_clearance']['object']}). These are windows on the outside
  of the 2-stud cabin wall. Door approach 5.2 (door lantern), tee stance 3.67 (door lantern), outrigger 10.0, flight1 29.1, landing 61.6,
  flight2/apron 67.3, cup 12-stud zone 134.7. Nothing is inside any corridor zone.
- Hull submersion: the lowest hull point is identical to the source at all 32 stations. It sits 1.42-1.49 studs under the water (local -0.6) from the stern to x 72,
  1.39 at x 82 and 0.35 at x 92, then the bow rises onto the beach as before. No hull hole; the cannons are proud relief only.
- Coplanarity: {F['coplanarity']['coplanar_pairs']} coplanar pairs over {F['coplanarity']['faces_checked']} new/rebuilt faces. Three found during the pass were fixed (seaweed seating, crate brace chamfer, bow stringer end).
- FBX re-import: visual {M['fbx_reimport']['start_ship_b2_visual.fbx']['objects']} objects (28 meshes + 4 empties, {M['fbx_reimport']['start_ship_b2_visual.fbx']['tris_total']} tris, palette embedded), col 190 boxes, 3 ramp FBXs at origin 0.

DEVIATIONS / CAVEATS (honest)
1. Source artifact found and covered, not edited: the DeckCabin deck slab's stern end face (x=-160, Y22..24) is coplanar with the Hull stern cap and
   faces inward, so it renders as a black band on the transom (visible in the source too: logs/prev_source/ship_stern.png). DeckCabin is a walking-surface
   mesh, so I left it byte-identical and covered the band with a proud WoodDk deck-line trim plank (part of Prop_SternCurl). No floaters found (0 isolated components).
2. COL_Mast_Main is unchanged and still spans the original 8..165 mast. The visual main mast is now snapped at ~106 (splinters to ~113), so this optional
   mast collider sticks ~50 studs above the visible stump. Suggest disabling or shortening it in Studio.
3. The deck props (cargo, crab, chest, wheel, rope coils) are visual only on the walkable deck, with no collider. They are outside the route corridor;
   the build bot may add simple CanCollide boxes if walk-through matters.
4. Visual beyond the source envelopes (scenery, no collider): Prop_SternCurl overhangs aft by 14 studs and is 2-3.5 studs wider (volutes) than the source
   ship visual envelope. Prop_Figurehead, Hull (its bowsprit, as in the source) and Rigging go beyond the collider union in X+.
5. Rigging was rebuilt, not edited in place (same object name, origin and mesh datablock name). The old flags moved into Prop_Flag. The Canvas/Red palette
   cells were recoloured to the brief values (names kept).
6. The flight2 30 deg yaw and the water/sand/cup marker are render-only (render_v3.py); none of it is saved into the blend.
7. Extra evidence renders were added: ship_beach.png (cannons, patches, portholes, barnacles from beach eye level), ship_bow.png (figurehead + bowsprit),
   ship_stern.png (stern curl + trim).

PATHS (all under C:\\Users\\chase\\sc_fix\\ship_upgrade_n5\\out)
  start_ship_v3.blend   (collections Visual 11 / Ramps 3 / Collision 190 / Props 18; palette packed)
  fbx\\start_ship_b2_visual.fbx, fbx\\start_ship_b2_col.fbx, fbx\\RampFlight1_own_origin.fbx, fbx\\RampLanding_own_origin.fbx, fbx\\RampFlight2_own_origin.fbx
  previews\\ship_3q.png, ship_tee.png, ship_route.png (+ ship_beach.png, ship_bow.png, ship_stern.png), 1600x1000 Cycles CPU
  manifest.json, fitcheck.json, fitcheck.md, report.txt, textures\\start_ship_palette.png
  src\\ (shiplib.py, build_v3.py, render_v3.py, export_v3.py, fitcheck_v3.py, verify_fbx.py, make_reports.py, write_report.py, inspect_source.py,
        probe_stern.py, scan_hull_faces.py, pick_pixels.py, art_brief.md)
  logs\\ (build/fitcheck/render/export logs, source dump, draft renders)
REPRODUCE: build_v3.py on source.blend -> fitcheck_v3.py dump (source) + check (v3) -> export_v3.py -> render_v3.py -> verify_fbx.py -> make_reports.py -> write_report.py
"""
open('report.txt', 'w', encoding='utf-8').write(txt)
open(os.path.join('..', 'DONE'), 'w').write('DONE 2026-11-05 - start_ship_b2_detail_v3 complete; hard checks %s; see out/report.txt\n' % ('PASS' if F['pass_hard_checks'] else 'FAIL'))
print('REPORT_OK')
