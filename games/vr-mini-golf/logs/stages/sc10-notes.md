# Stage sc10 (Claude Code): Sugarloaf Canyon H16 rim 2slot_d, TRADING POST board +0.3, H3 pebbles, H11/H12 trench, rail rule

Status: **PASS. Sugarloaf Canyon published v69** (Creator Hub Version History, "Show published only": 69, 63, 57, 49, ...). Evidence: `sc10-v69.png`, `sc10-history-all.png`, `sc10-final-histories.png`. Every gameplay collider is identical to v63, including the four H16 deck felts and the 1.9 opening.

Items 1 and 2 changed the place. Items 3, 4 and 5 were checked and needed **no change**: the two pebbles are not floating and sit inside one merged MeshPart, no Look7 piece floats over the trench, and no dressing piece is within 1 stud of a rail. Details below.

## Preflight
- One Studio, on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 63.
- **Matches published v63:** all 707 gameplay parts are identical to sc9's final inventory, which is the inventory behind `collider-verification-final.json` (`preflight-vs-sc9.json`). Parts 7476/7476, placeholders 175 / 36 visible, same paths. Look7Dressing 1277 models / 3012 parts.
- No other stage job was running. Only this `claude -p` sc10 job; the cursor-agent workers and the ChatGPT codex exec-server are not stage jobs.
- Creator Hub published-only baselines: lobby 251, LG 19, SC 63, AU 13 (`sc10-preflight-sc-published.png`, `sc10-preflight-histories.png`, `playtests/stage-sc10/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage. I never answered it and sent no Return key. No permissions were granted.

## A. Baseline (untouched v63)
- **Smoke:** flow PASS (putt 7.58). 0 server entries and 0 other errors. Only the 5 known UIBlox `FoundationProvider not found` client warnings from CorePackages appeared (`sc10-smoke-before.log`).
- **18-hole sweep, seed 20261014:** 54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15), console empty (`sweep-before/`).
  - Compared with sc9's after sweep, the only differences are sc9's H11 mover flag and H15 1→2 timeouts (`sweep-before-vs-sc9.json`).
- **H16 edge test** (`tools/sc8_h16_edge.py`, `h16-edge-before.json`, `h16-edge-before2.json`):
  - Opening ±0.95 in all 8 directions (0.955 on one diagonal). Rest thresholds: drop ≤0.925, stay ≥0.95. 0 putts dropped outside the frame (20 and 22 of 72 dropped).
  - **The 4 sc5 diagonal rolls did not drop in either full run.** Each ball stopped at the corner (radial 1.08, y 190.07), unlike sc8 and sc9.
  - I ran the same sequence twice more, once with a passive Heartbeat trace and once with active sampling. All 4 diagonals dropped both times, crossing the corner at Chebyshev 0.92 and landing on the shaft floor at 186.47.
  - Colliders are byte-identical, so this is run-to-run physics variance on untouched v63. The after run dropped all 4 (below).
- **Crystal baseline (rim b), new `tools/sc10_crystal.py`:** 140/140 balls dropped. 128 ball paths passed through a crystal. **12 balls touched a b crystal while still rolling on the felt**, because the b crystals rise to felt + 0.1.
- **Live dressing check** (sc9 rules, live pivots, new `tools/sc10_dress.py`): felt 0, rail <1 = 0 (closest 1.126, `rock_a_390` to the H10 wall), float >0.1 = 0 (`dressing-check-before.json`).
- **z-scan before:** 7847 total, 0 exposed (equals sc9's after scan).

## B. Changes
### 1. H16 rim → `h16_rim_2slot_d` (`tools/sc10_place.py rim`, `rim.json`, `rim-verify.json`)
- **Import:** the FBX SHA256 matches the manifest (`023218…a54`). It was merged alone with `sc5_merge_fbx.py --split-materials` into `sc10_K.fbx`: 6 meshes, 852 tris (= manifest), PASS (`merge/`).
  - One 3D Importer pass with the sc6-sc9 settings: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages off, No Rig, Stud, scale 1, polygon count 852 (`sc10-import-settings.png`, `sc10-import-geometry.png`).
  - The importer scaled by ×100. Parts were rebuilt from the merge bounds with the Y half-turn undone (the sc8 method). The `sc10_K` bundle was removed.
- **Frame:** the same as sc8. Workspace root = rim model pivot (-300, 190, -4871.8, yaw 180); library root = identity.
  - GeodeRim, PepRed, Rope and Timber land with **0 position/size delta** on both copies. Their geometry is unchanged from b.
  - **GeodeRim bottom = 190.167 = felt + 0.167.**
- **Appearance** (manifest `materials`):

  | Slot | Material | Colour | CastShadow |
  |---|---|---|---|
  | GeodeRim | **Rock** (not Neon) | **#C8463F** | as the sc8 rim |
  | CrystalPink | Neon | #FF6FA8 | off |
  | CrystalAmber | Neon | #FFB347 | off |
  | PepRed | SmoothPlastic | #D9343A | as the sc8 rim |
  | Rope | Fabric | #C9A86A | as the sc8 rim |
  | Timber | WoodPlanks | #8A5A33 | as the sc8 rim |

  - There are no importer textures.
- **Flags:** every rim part has CanCollide/CanQuery/CanTouch off (asserted). `VisualQueryDisabled` is set on the Workspace copy.
- **Backups:** the old rims are in `ServerStorage.SC10Backup` (`h16_sinkhole_rim__Workspace`, `__ServerStorage`).
- **Mesh check in Studio:** the EditableMesh vertices of the placed parts, mapped into the rim frame, match the d FBX vertices within 0.0008.
  - All 12 crystals top out at **189.914 = felt − 0.086**, so nothing rises above the ball plane.
  - Pink crystals reach in to Chebyshev 0.335; amber to 0.671.
- **Frame inner edge vs opening:** GeodeRim inner edge is at **±1.000** (Chebyshev, from the mesh). The opening is **±0.95**, so the frame sits **0.05 outside the opening edge**, the same as sc8.
  - A 0.05 felt collider strip lies inside the frame; the visible felt edge (1.03) is under the frame. The opening is unchanged (still 1.9 square, colliders identical).

### 2. TRADING POST board +0.3 (`board.json`)
- **Workspace:** both sc6 parts (`SC6Source`) were raised +0.3: PepRed 25.311 → **25.611**, MintWhite 25.411 → **25.711**.
- **`ServerStorage.SugarloafKit.trading_post_deck` library copies:** these carry only sc8's `SC8Raise` mark. PepRed 7.95 → 8.25, MintWhite 8.05 → 8.35.
  - Library and Workspace offsets agree within 2e-6.
- Bunting, awnings and lanterns were not touched.
- **H1 rail1 clearance ≥ 14.21** (was 14.08 at sc8).
- Note: my first call raised the Workspace pair and then stopped at the library copy (no `SC6Source` there). I checked the state before the second call (`SC10Raise` attribute), so nothing was raised twice.

### 3. H3 pebbles: **0 deleted (flagged)** (`pebbles.json`, `pebbles-truemesh.json`, `tools/sc10_pebbles.py`)
- **Which pebbles:** the targets are components of the merged MeshPart **`h03_dress_props__Pebble`**, one MeshPart (80 × 21 studs) that holds all **8** pebbles.
  - World (-37.9, -4658.7) = component 24.
  - World (-41.4, -4660.8) = **hole-local (53.66, 9.21)** = component 26. The H3 frame is unrotated at (-95, 18, -4670), so these two prompt points are the same pebble.
  - So the prompt names **2 distinct pebbles**, and neither is a part on its own. The rule says to flag that case, not delete. Deleting either pebble would mean re-exporting the mesh.
- **Raycast, run before any deletion:** ground = Terrain + visible non-dressing parts, excluding h03_dress_props. I checked both collision geometry and the **true render mesh** (EditableMesh `RaycastLocal`). They agree:
  - **Pebble 24:** every base vertex is **0.30-0.37 below** the `h03_ground_s22__RedDirtLight` surface. It is not floating.
  - **Pebble 26:** sunk 0.32 into the s22 tile at its lowest point. Its other base vertices overhang the tile edge, up to 0.79 above Terrain (sc8's flag). It is not floating > 0.3.
- Screenshot `sc10-after-h03.png`: both pebbles sit on the tile beside the timber.
- **For Game Art Bot / 3D Model Bot:** if these should go, re-export `h03_dress_props` with components 24/26 removed from the Pebble slot (or split pebbles into their own objects). Also check whether the reported gap was measured against Terrain only, ignoring the h03 ground tiles.

### 4. H11/H12 trench: **0 grounded / 0 deleted** (`trench-scan.json`, `trench-scan-true.json`, `trench-plan.json`)
- No "trench" is defined in the docs. My reading: the **canyon around the H10-H12 plateau**.
  - The rim is at y about 114-116 and the floor at y 15-18, about 100 studs deep.
  - It includes the gorge north of the peppermint dam (x -32..32, z -5300..-5210) (`sc10-after-trench.png`).
- **Candidates:** every Look7Dressing piece with any point at y 110-122: **347** (H10 105, H11 72, H12 170). For each one I rayed the ground under **every hull vertex and contact-ring point**, using both collision and true render-mesh ground.
- **Results:**
  - **No candidate floats.** The max contact-ring gap is 0.068.
  - **No candidate is over the gorge.** The only Look7 pieces in the gorge are 6 `cliffT_w24_h6` on its floor at y 15-20.
  - A few pieces partly overhang a lower edge with their contact ring still grounded: 425 (up to 4.97), 426 (2.67), 1057 (1.92), and 11 more by 1-1.8. Rule 4 grounds floating pieces; these are not floating, so I didn't move them.
- The loose-looking chips on the gorge walls beside the dam are **not Look7Dressing**: `Kit.cliff_kit.cliffT_w24_h48_p4_1/_2`, `Kit.hero.peppermint_dam` and `WorldMeshes.dam_crest_parapets`. They are outside rule 4 and were left alone.

### 5. Rail rule: **0 moved / 0 deleted** (`rail-plan.json`)
- **Check:** true XZ footprints (sc9_mesh_geom slot hulls at live pivots) against all 322 `Geometry.Wall` plan polygons. **0 pieces are within 1.0**; the closest is 1.126.
  - Against the 577 visible `HoleN.Rails` parts it is also 0; the closest is 1.044 (`rock_a_390` to `Hole10.Rails.Rail_rail8`).
- **Scope:** "dressing" here means the 1277 Look7Dressing pieces, the set with sc9 hulls. The `Kit.hole_dressing.hNN_dress_props/plants` meshes are merged multi-object meshes without sc9 hulls and were not part of this rule.
- **Full dressing check after:** **felt 0, rail <1 = 0, float >0.1 = 0** (1277 pieces, `dressing-check-after.json`).

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)` with gap 0.08 and min 0.2. **1204 fixes**, the same 882-target set as sc9. 0 unresolved, 0 thin, 705 collider invariants, 0 failures, 171 joints.
- **Colliders: same.** All 707 gameplay parts are identical to v63 after separation (`collider-verification.json`) and again after all Play sessions (`collider-verification-final.json`, against sc9's final inventory).
  - The four H16 deck felts (deck_m, deck_w, deck_e, deck_n; 1.9 opening) are identical.
  - Placeholders 175/175, 36 visible, same paths.
- **Parts: 7476 → 7476** (6 rim parts replaced by 6 on each copy).

| z-scan (zf1_zscan.luau) | Before (v63) | After |
|---|---:|---:|
| Coplanar faces | 7138 | 7136 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 16 | 16 |
| Transparency candidates | 632 | 632 |
| **Total** | **7847** | **7845** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 7134 | 7132 |
| Terrain candidates | 131 | 131 |

Screenshots: `sc10-after-h16.png` (rock frame, crystals below the felt), `sc10-after-board.png`, `sc10-after-h03.png`, `sc10-after-trench.png` (H11/H12 gorge and dam).

## D. Playtests
- **Smoke:** flow PASS (putt 7.28). **0 errors** and 0 server entries. The client showed the 5 UIBlox `FoundationProvider` CorePackages warnings, which are known engine noise and identical to the baseline (`sc10-smoke.log`).
- **18-hole sweep, same seed:** **54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15)**, console empty. **No hole differs from the baseline** (`sweep-after/`, `sweep-comparison.json`).
- **H16 edge test after** (`h16-edge.json`):
  - Opening ±0.95 in all 8 directions (0.955 on one diagonal).
  - **sc5 set 12/12 as in sc8/sc9**, all 4 diagonals included.
  - Rest thresholds drop ≤0.925 / stay ≥0.95 on the axes and corners.
  - 72 slow putts: 22 drop (v63 baseline 20 and 22; sc9 24), **0 outside the frame**, max fall 0.866 from centre.
  - Rim flags all off.
- **Slow-drop crystal test** (`crystal-after.json`, `crystal-after-score-d.json`):
  - 80 rest drops at Chebyshev 0.80-0.925 (16 spots and 4 corners each) and 60 slow putts (speed 0.4/0.7/1.0, 4 directions, lateral 0/±0.4/±0.75).
  - Ball centres were sampled each frame in the rim frame and measured against each crystal's convex mesh. A hit means a centre within 0.08 (ball radius) of a crystal.
  - **Drops behave as before:** 140/140 dropped, the same outcome for every ball as on untouched v63.
  - **CRYSTAL_HITS = 124/140:** the ball visually passes through a crystal while it **falls through the shaft**. First contact is 0.012-0.307 below the felt.
  - **0 hits while the ball is still on the felt**; rim b had 12.
  - This is by design of d. The crystals stand inside the 0.95 opening (Chebyshev 0.335-0.676), from 0.086 to 0.5 below the felt, and are non-colliding. Removing the drop-through overlap would mean moving the crystals outside the shaft (Chebyshev > 0.95 + 0.08) or below about felt − 0.5.

## E. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place.
- **Creator Hub published-only shows v69** (`sc10-v69.png`). Its "Last Updated" is 4:56 PM, the time of the last autosave; I pressed ⌥P at about 5:08 PM.
  - From 4:52 on I only ran Play sessions and read-only checks, so the place was unchanged since that autosave. Publishing marked v69 as published and created no newer version.
  - v64-v68 are autosaves from this session (`sc10-history-all.png`). No other job was running.
- **File > Download a Copy:** `playtest/playtest-sugarloaf_canyon-v69.rbxl`, 5,424,556 bytes, SHA256 `c95a0b1217edf874e645d0e129a993622be746dd59e484bb5d7ddbf272499552`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains, only the StudioMCP helpers.
- **Final Creator Hub published-only: lobby 251, LG 19, AU 13 unchanged; SC 69** (`sc10-final-histories.png`). Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.
- **Uploads, listed and not deleted:**
  - New this stage: model `sc10_K` 77716749177127, plus 6 MeshParts.
    - CrystalAmber 82628986603352
    - CrystalPink 129141792512096
    - GeodeRim 128768055276006
    - PepRed 81244010093456
    - Rope 85290265146329
    - Timber 107956133196672
  - Only the 6 MeshParts are used, by the rim parts. The `sc10_K` model asset is unused.
  - Older unused uploads were left as they are: `sc9_LOD` 106220102339860 and the sc8_K/sc7_K models.

## Tools (new)
- `sc10_stage.py`: the sc9_stage commands writing to stage-sc10.
- `sc10_place.py`: probe, rim swap, board, live Look7 pivots, move/delete plans, and `trueground`, a render-mesh ground probe using EditableMesh `RaycastLocal`.
- `sc10_dress.py`: the sc9 felt/rail/float rules on the live place, plus the trench scan.
- `sc10_crystal.py`: the crystal drop test and its scoring.
- `sc10_pebbles.py`: the item 3 raycast.
- `sc10_rimverts.py`: FBX vertices, components and triangles via Blender.

## Open items
- **H3 pebbles (flag):** components 24 and 26 of the merged `h03_dress_props__Pebble` mesh are not floating by raycast (sunk 0.30-0.37; 26 overhangs the tile edge). Deleting them needs a mesh re-export by the art bot.
- **Crystals vs falling ball:** 124/140 drop paths visually pass through a crystal inside the shaft, never on the felt. They are non-colliding, and drops are unchanged.
- **Trench:** no Look7 piece floats in the y 110-122 band. If the reviewer meant the gorge-wall chips, those are Kit cliff_kit / peppermint_dam meshes and need a separate prompt.
- **Rail rule:** nothing within 1 stud on the current place. If the art bot's check finds pieces, compare footprints; sc10 uses true mesh hulls at live pivots.
- **Engine noise:** 5 UIBlox `FoundationProvider not found` warnings in every Play session, also on untouched v63.
- **Baseline H16 diagonal variance:** on untouched v63 the full edge test twice left the 4 diagonals at the corner; traced reruns and the after run dropped all 4.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=69 RIM=d GEODERIM=Rock/#C8463F PEBBLES_DELETED=0 TRENCH=0/0 RAIL_MOVED=0 RAIL_DELETED=0 DRESSING_CHECK=0/0/0 CRYSTAL_HITS=124 H16_EDGE=opening ±0.95, sc5 12/12, rest drop<=0.925 stay>=0.95, putts 22/72 outside 0 PARTS=7476->7476 SC_SCAN=7847/7845/0 CUPS=54/54 SWEEP=36/0/0/2 SMOKE_ERRORS=0 (+5 UIBlox) COLLIDERS=same
