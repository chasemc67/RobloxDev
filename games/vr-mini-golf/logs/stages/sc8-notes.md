# Stage sc8 (Claude Code): Sugarloaf Canyon H16 2-slot rim + sinkhole opening, ground seams, TRADING POST board, H3 props, filler removal

Status: **PASS. Sugarloaf Canyon published v57** (Creator Hub Version History, "Show published only": 57, 49, 42, 34, ...; v57 = Oct 14 2026 2:50 PM). Evidence: `sc8-v57.png`, `sc8-history-all.png`, `sc8-final-histories.png`.

## Preflight
- One Studio, on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 49 at open. `Workspace.CourseSugarloaf` has Hole1-Hole18.
- **Matches published v49:** all 707 gameplay parts identical to sc7's final inventory (= `collider-verification-final.json`, v49), 8387/8387 parts, placeholders 175 / 36 visible, same paths (`preflight-vs-sc7.json`).
- No other stage job (only this `claude -p` sc8 job; the ChatGPT desktop codex app-server/exec-server and the cursor-agent workers are not stage jobs).
- Creator Hub published-only baselines: lobby 251, LG 19, SC 49, AU 13 (`sc8-preflight-sc-published.png`, `sc8-preflight-others.png`, `playtests/stage-sc8/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage. I never answered it and sent no Return key while it was up. No permissions were granted.

## A. Baseline (untouched v49)
- Smoke PASS: real putt 7.42 studs, 0 server/client errors or warnings (`sc8-smoke-before.log`).
- 18-hole sweep, seed 20261014: **54/54 cups, 36 shots, 0 escapes, 2 timeouts (H15)**, console empty (`sweep-before/`). My summary counts **1 "stuck" on H11**: it is the mover-sweep `offsurface` flag on `h11-sweep-lock_lift_deck-1` (the hole's top-level `stuck` field). The fuzz shots had 0 stuck. Untouched v49, so this is run-to-run variance; the after sweep has 0.
- **H16 edge test** (`h16-edge-before.json`, new `tools/sc8_h16_edge.py`): opening measured **±1.2** on all 8 directions. The sc5 set (4 axis rolls, 4 diagonals, rest 0.9 drop / 1.3 stay) all 12 as before. Rest scan: drop at ≤1.175, stay at ≥1.2 (axis and corners). **Slow putts along the frame edge: 48/72 drop with the ball centre outside the frame's inner edge** (falls at up to 1.12 from centre).
  - Note: my first run of the extended test left the sc5 rest balls on the deck and they nudged later balls, which gave a fake asymmetry. Every phase now clears its balls; the rerun above is the recorded baseline.
- z-scan before: `zscan-before.json` (8242, 0 exposed planar). Screenshot: `sc8-before.png` (H16 rim wide and close, board, H3).

## B. Changes (`playtests/stage-sc8/changes.json`, `tools/sc8_place.py`)
**Import:** one 3D Importer pass. `h16_rim_2slot_b/h16_sinkhole_rim.fbx` and `fix_v42_item5c/h03_dress_props.fbx` were merged with `sc5_merge_fbx.py --split-materials` into `sc8_K.fbx`: 12 meshes, 2,818 tris, round-trip PASS. Both SHA256 match their manifests. Settings as sc6/sc7: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages off, No Rig, Stud, scale 1 (`sc8-import-settings.png`, `sc8-import-geometry.png`). The importer scaled by x22.59. Each part was rebuilt from the merge bounds with the Y half-turn undone, and the `sc8_K` bundle was removed.

1. **H16 rim** (Workspace `Hole16.StageAFVisuals.h16_sinkhole_rim` + `ServerStorage.StageAFProps.h16_sinkhole_rim`): 4 parts → 6 (GeodeRim, PepRed, Rope, Timber + **CrystalPink** + **CrystalAmber**).
   - Same frame: the 4 kept slots land with **0 position/size delta** on both copies. GeodeRim bottom is at felt + 0.167 (190.167), as before.
   - CrystalPink is Neon (1, 0.4, 0.75) and CrystalAmber is Neon (1, 0.7, 0.25), CastShadow off. The other slots copy the old part's material, colour and CastShadow.
   - CanCollide/CanQuery/CanTouch are off on every rim part (asserted), and `VisualQueryDisabled` is on the Workspace copy. The old rims are in `ServerStorage.SC8Backup` (`h16_sinkhole_rim__Workspace`, `__ServerStorage`).
   - Flag: following "other slots keep the old rim's look", the GeodeRim frame stays sc6's Neon pink. The art manifest lists it as Rock #C8463F; switch it if the art bot wants the frame as rock now that the crystals carry the glow.
2. **H16 sinkhole opening 2.4 → 1.9 square (half-width 1.2 → 0.95)**, centred where it was (-300, -4871.8). The GeodeRim inner opening is ±1.0 (FBX vertices x/z ∈ {-1.21, -1.0, 1.0, 1.21}), so the new edge is 0.05 inside it.
   - The opening is only the gap between four deck felt colliders. No script constant or attribute defines it; the CourseData `drops` entry is descriptive.
   - Changed colliders (`Hole16.Geometry.Felt`, world coordinates, before → after):

     | id | position | size (x, y, z) |
     |---|---|---|
     | deck_w | (-302.6, 189.8, -4871.8) → (-302.475, 189.8, -4871.8) | (2.8, 0.4, 2.4) → (3.05, 0.4, 1.9) |
     | deck_e | (-297.4, 189.8, -4871.8) → (-297.525, 189.8, -4871.8) | (2.8, 0.4, 2.4) → (3.05, 0.4, 1.9) |
     | deck_n | (-300, 189.8, -4867.3) → (-300, 189.8, -4867.425) | (8, 0.4, 6.6) → (8, 0.4, 6.85) |
     | deck_m | (-300, 189.8, -4874.5) → (-300, 189.8, -4874.375) | (8, 0.4, 3) → (8, 0.4, 3.25) |

   - Rotation, felt top (190.0 = roll height), thickness, flags, tags, physics and collision group are unchanged.
   - Their `ZF1VisualLayers.Visual_Felt` clones were re-based (`ZF1BaseCF`/`ZF1BaseSize` = the new collider), so VisualSeparation keeps the 0.08 inset. The visible felt edge is 1.03, under the frame.
   - **src/CourseData:** `SugarloafCanyon.luau` h16 felt deck_m (centre z -13.625, size 8 x 3.25), deck_w/deck_e (x ∓2.475, 3.05 x 1.9), deck_n (z -20.575, 8 x 6.85), plus the d1 `edge` text. Pushed to the place.
3. **Seams** (visual tiles only; I moved the lower tile, all its material parts):
   - h16_ground_s03 −0.03, h14_ground_s00 −0.04, h09_ground_s00 −0.03 (`seams.json`).
   - The quoted gaps are the tiles' bounding-box top faces. Before → after:
     - h16_s03__RedDirt / h17_s20__RedDirtLight: 0.0008 → 0.029
     - h16_s03__RedDirtLight / h17_s20 and h17_s10: 0.0076 → 0.038
     - h13_s04__RedDirt / h14_s00__RedDirt: 0.0089 → 0.031 (h13 RedDirtLight 0.014 → 0.054)
     - h09_s00 / h09_s01 (both slots): 0.002 → 0.032
     - The minimum over all 14 overlapping neighbour pairs is **0.0008 → 0.029**.
   - True geometry (fit030 triangles at the Studio frames, `seams-geometry.json`): h09's top faces really were coplanar (0.0000 over a ~0.65 sq-stud strip) and are now 0.030 apart. The h16/h17 top surfaces go 0.060 → 0.090 and h13/h14 go 0.071 → 0.111.
   - h16/h17 (0.0019) and h13/h14 (0.014) also meet at vertical side faces with **opposing** normals, which is a buried interface. A vertical move cannot change those distances.
   - **Float check** (`float-check.json`): 7 dressing parts sit over the dropped tiles; every unit's base is still 0.25-0.5 below the ground. Nothing floats.
4. **TRADING POST board:** both sc6 board parts were raised **+0.5** (PepRed 24.811 → 25.311, MintWhite 24.911 → 25.411). Bunting, awnings and lanterns are untouched. The `ServerStorage.SugarloafKit.trading_post_deck` library copies were raised too, to stay in sync. **H1 rail1 clearance ≥ 14.08** (was 13.87) (`board.json`).
5. **H3 dress props from fix_v42_item5c** (item5 / item5b not used). Workspace `Kit.hole_dressing.h03_dress_props.h03_dress_props` and `ServerStorage.SugarloafKit.h03_dress_props`, 6 → 6 parts each.
   - Frame: Workspace root (-95, 18, -4670) (= manifest pivot + layout offset), library root identity. The unmoved GumLime slot lands with 0 delta.
   - Appearance was copied from the old same-named slots (material, colour, variant, transparency, CastShadow). Each mesh keeps the importer's own texture. Old copies are in `SC8Backup`.
   - **Rock check** (`h03-ground.json`): no rock (Strata/Pebble component, from the FBX vertices) overlaps hole-local x 51-54, z 12-14, and ground is under all 117 samples there. One nearby Pebble at local (53.66, 9.21) is sunk 0.32 on h03_ground_s22, but one of its base points overhangs the tile edge onto Terrain 0.79 lower. Reported only; nothing was deleted.
6. **Cliff fillers:** deleted all **409** (205 cliff_filler_rock_a + 204 cliff_filler_rock_b, 1 part each) from `Look7Dressing`. The 2 `SC7Kit` templates were deleted too, because no other part or script used them (`fillers.json`). The rest of the dressing was kept.

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)`: gap 0.08, min 0.2, **1204 fixes, the same set as sc7**, 0 unresolved, 0 thin, 705 collider invariants, 0 failures, 171 joints.
- **Colliders: same except the H16 opening** (`collider-verification.json`, and `collider-verification-final.json` after all Play sessions; `tools/sc8_verify.py`). 703 of the 707 gameplay parts are identical to v49, rails included. The 4 opening felts differ only in CFrame position and size; rotation and every other key are equal. Placeholders 175/175, 36 visible, same paths.
- **Parts: 8387 → 7980** (+2 rim crystal parts, −409 fillers).

| z-scan (zf1_zscan.luau) | Before (v49) | After |
|---|---:|---:|
| Coplanar faces | 7467 | 7293 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 15 | 16 |
| Transparency candidates | 699 | 698 |
| **Total** | **8242** | **8068** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 7529 | 7355 |
| Terrain candidates | 131 | 131 |

The drop comes from the deleted fillers. The +1 placeholder hit is a mesh-bbox candidate (the new H3 Pebble bbox), not planar. Screenshots: `sc8-after-h16.png` (pink and amber crystals in the shaft), `sc8-after-board.png`, `sc8-after-h03.png`, `sc8-after.png` (grid).

## D. Playtests
- Smoke PASS: real putt 7.35 studs, **0 server/client errors or warnings** (`sc8-smoke.log`).
- 18-hole sweep, same seed. **After: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15)**, console empty. **H16 cup drop 3/3.** The only difference from the baseline is the baseline's H11 mover-sweep flag (`sweep-comparison.json`). The H15 slope timeouts predate this stage.
- **H16 edge test after** (`h16-edge.json`):
  - The opening measures **±0.95** in all 8 directions (0.955 on one diagonal: ray step).
  - The sc5 set is unchanged: 4 axis rolls and 4 diagonals drop, rest 0.9 drops, rest 1.3 stays.
  - **Re-derived rest thresholds: drop at ≤0.925, stay at ≥0.95, on the axes and at the corners**, i.e. the ball centre must be over the void.
  - **Slow putts along the frame edge (72: offsets 0.97-1.2, angles 0/15/30°, speeds 0.6/1.2): 0 drop outside the frame** (was 48). The 24 that still drop are the 30° putts that run into the opening; they fall at ≤0.87 from centre, inside the frame.

## E. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v57** at 2:50 PM; v50-v56 are Studio autosaves from this session.
- File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v57.rbxl`, 5,288,797 bytes, SHA256 `f10dbb852f909b8f50b771f5225c9233df1f805c3053c8c410415d83ae001f72`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains (only StudioMCP helpers).
- Final Creator Hub: **lobby 251, LG 19, AU 13 unchanged** (latest published); SC 57. Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.

## Open items
- **GeodeRim colour:** the frame is still sc6's Neon pink (per the prompt); the manifest says Rock #C8463F.
- **Crystals vs ball:** the crystals reach 1.02 from centre and up to 0.1 above the felt. A ball rolling along the edge at 0.95-1.0 passes visually over them; they are non-colliding.
- **H3 pebble at local (53.66, 9.21)** partly overhangs the s22 tile edge (one base point 0.79 above Terrain).
- **Persistence:** the rim, H3 swap, board raise, seam drops and filler deletion live in the place (+ ServerStorage library copies). The H16 opening is also in `src` CourseData. `ServerStorage.SC8Backup` holds the old rims and H3 props.
- The importer uploaded the `sc8_K` model asset; it is unused.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=57 H16_OPENING=2.4->1.9 H16_EDGE=sc5 12/12 same; rest drop<=0.925 stay>=0.95 (was 1.175/1.2) OUTSIDE_DROPS=0 SEAMS=0.029/0.031/0.032 H3=item5c FILLERS_DELETED=409 PARTS=8387->7980 SC_SCAN=8242/8068/0 CUPS=54/54 SWEEP=36/0/0/2 SMOKE_ERRORS=0 COLLIDERS=same except H16 opening
