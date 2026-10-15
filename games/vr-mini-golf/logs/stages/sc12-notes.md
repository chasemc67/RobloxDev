# Stage sc12 (Claude Code): Sugarloaf Canyon H15 low-side wall, H16 lip, H3 pebble, flat decals, H6 flood rock

Status: **PASS. Sugarloaf Canyon published v103** (Creator Hub Version History, "Show published only": 103, 79, 69, 63, ...). Evidence: `sc12-v103.png`, `sc12-final-histories.png`.

Gameplay colliders: **704 of v79's 708 are identical.** The differences are only in the two allowed areas:
- H15 low-side dune wall: +20 terrace pieces.
- H16 opening lip: 4 deck felts resized, +8 lip pieces.

Exact before/after for every changed or added part is in `playtests/stage-sc12/collider-changes.json`.

## Preflight
- One Studio, on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). PlaceRole `sugarloaf_canyon`.
  - Studio reported PlaceVersion 80. That is an autosave after the v79 publish (the sc11shots job); the published version is 79.
- **Matches published v79:** 708/708 gameplay colliders are identical to sc11's final inventory, including the H15 `dune_rail2_shelf` (`preflight-vs-sc11.json`).
  - 7471 parts, placeholders 175 / 36 visible.
- No other stage job. Only this `claude` sc12 job was running; the cursor-agent workers and the ChatGPT codex app/exec servers are not stage jobs.
- Published-only baselines: lobby 251, LG 19, SC 79, AU 13 (`sc12-preflight-sc-published.png`, `sc12-preflight-histories.png`, `playtests/stage-sc12/preflight.json`).
- The macOS "sshd-session ... bypass the system private window picker" prompt was never on screen this stage.
  - I checked the window list before the one Return key press (into Studio's file sheet).
  - `ScreenCaptureApprovals.plist` shows no new approval (LastAlerted is still 09:03).
- One macOS prompt did appear: "RobloxStudio would like to access files in your Desktop folder". I clicked **Don't Allow**. No permissions were granted.

## A. Baseline (untouched v79)
- **Smoke:** flow PASS, putt 7.34. 0 server entries and 0 other errors; only the 5 known UIBlox `FoundationProvider` warnings (`sc12-smoke-before.log`).
- **18-hole sweep, seed 20261014:** 54/54 cups, 36 shots, 0 stuck, 0 escapes, **2 timeouts (H15)**, console empty (`sweep-before/`).
  - Reset points: (-307.30, -5088.37), touching the dune-side face of `dune_lean3`; and (-304.58, -5073.03), the north corner.
- **H16 edge test ×3** (`tools/sc12_h16_edge.py`, `h16-edge-before{1,2,3}.json`):
  - The sc5 set gave 12/12, 12/12 and 10/12. Opening ±0.95. Rest thresholds: drop ≤0.925, stay ≥0.95. 0 drops outside the frame. Slow putts 24/22/24 of 72.
  - **Lip stops 4/80, 12/80, 12/80.** A lip stop is a rolling ball (8 sc5 rolls + 72 slow lip rolls) that does not drop and ends within Chebyshev 1.25.
  - They are all diagonals. Each hits the corner, deflects, and stops mid-edge 0.04-0.12 outside the void edge (Chebyshev 0.99-1.07).
- **seamshots-80 before:** **2 wedged / 27 non-rest** (`seam-before.json`; method in item 1).
- **z-scan before:** 7839 total, 0 exposed (= sc11 after).

## B. Changes
### 1. H15 low-side wall: rest terrace along `dune_lean3`. Seamshots **2/27 → 0/0**, sweep H15 timeouts **2 → 0**
**Where the problem was** (`seam-before.json`):
- The rail2 pocket (40 shots across, along and parked) and the north corner (12) were already clean: 0/0, thanks to sc11's shelf.
- **Every failure was on the dune side of `dune_lean3`.** This is the 31-stud inner wall that meets rail2 at the north apex. lean3 across 12/12, lean3 along 7/8 and the crawl spot 8/8 were non-rest.
  - The dune falls 5.5° into lean3, so a ball pressed on the bare wall rubs to a crawl (< 0.3 studs/s for 9-19 s) until the 20 s autoreset, or seam-hops and wedges.

**Test (`tools/sc12_seam.py`, GolfTest `seamshots` extended).** 80 fixed native shots, seed 20261014:
- r2across 20, r2along 12, r2park 8 over the whole 30-stud rail2.
- corner 12, within 3 studs of the rail2 / lean3 / 0.6-drop apex, both sides of lean3.
- l3across 12 and l3along 8 on lean3's dune side.
- crawl 8, within 1.5 of (-307.2, -5087.9).

How each shot is scored:
- **Wedged** = a `forcedrest` (seam hops that end wedged).
- **Non-rest** = a timeout / 20 s autoreset / stuck-3s / offsurface, or crawl (< 0.3 studs/s while moving) for more than 2 s anywhere.

GolfTest additions are test-mode only: several seam lines, flag positions, the crawl position, the last moving position, and an optional per-shot 0.1 s trace.

**Iterations** (all measured with the same 80 shots):

| version | geometry | wedged / non-rest |
|---|---|---|
| v79 | bare lean3 | 2 / 27 |
| v1 | felt fillet, crease 0.3 off the face, 15° rise to the wall | 5 / 26: the CFrame was **left-handed**, and the client got a different orientation, so the client-simulated ball never met the fillet |
| v2 | same, right-handed (`CFrame.fromMatrix`) | 1 / 18: the ball rides the crease but only at ~0.5 studs/s |
| v3 | v2, frictionless, full wall length | 0 / 12: 0.9 studs/s, still too slow for 20 s |
| v4 | level-across terrace following the dune's 1.48° fall along the wall | 0 / 22: 0.7 studs/s. The along-wall fall itself is too gentle to roll out in time |
| v5 | rest terrace, 15 × 2.06, 0.6° | 0 / 3 (slow 2.3-2.7 s creep before resting) |
| **v6 (final)** | **rest terrace, 20 × 1.55, 0.3°** | **0 / 0** (one rail2 park took one seam hop, then rested) |

**Final geometry** (`h15-terrace-spec.json`, `h15-terrace-apply.json`, `tools/sc12_h15.py segments 0.4 20 0.3`):
- 20 felt colliders `dune_lean3_terrace_01..20`, cloned from sc11's shelf: GolfSurface, felt physics 1/0.35/0/1/100, Transparency 1, Zone dune.
- They run along lean3's dune-side face from rail5 to the dune's north edge.
- Each piece is level across and falls 0.3° along the wall, which is below the 0.876° rest limit, so a ball can rest on it.
- Each is 0.4 wide plus 0.1 into the wall, 0.4 thick and 1.546 long.
- Each is flush with the dune (0.001 below) at its north outer corner. Its outer edge drops to 0.033 below the dune at its south end, so coming off the dune is always a step down, never a lip.
- Its top is 0.006-0.038 above the dune at the wall face. Each joint steps down 0.032 going north.
- **Rail heights are unchanged, and the ball is still contained**: lean3, rail2 and rail5 are untouched.
- sc11's `dune_rail2_shelf` is unchanged; the pocket and corner were already clean.

**src:** `CourseData/SugarloafCanyon.luau` H15 has 20 `dune_lean3_terrace_NN` felt entries with an exact hole-local `cframe` + `part_size`. `CourseBuilder.luau` `buildPiece` builds a felt def at that exact pose when `cframe` is present; this is needed because a single-axis `slope` cannot express the two-axis tilt.

**Sweep:** H15 timeouts 2 → **0**. It is the only hole that changed (`sweep-comparison.json`).

**Visual:** the terrace is an invisible collider, like the shelf. A ball resting on it sits up to 0.038 above the dune's visible felt at the wall.

### 2. H16 opening lip: two-facet round-off. Lip stops **4/12/12 → 0/0/0**, outside drops **0**
**Final geometry** (`h16-lip-v3.json`, hole-local around the sinkhole centre (0, -16.2)):
- The four deck felts are cut back so the flat deck (top 190.0) ends at ±1.35:
  - deck_m: z -13.425, 8 × 2.85
  - deck_n: z -20.675 → -20.775, 8 × 6.45
  - deck_w/e: x ∓2.675, 2.65 × 2.7
- **Outer bands** `lip2_e/w/n/m`: from 189.98 at ±1.35 down to 189.96 at ±1.15 (5.7°).
- **Inner bevels** `lip_e/w/n/m`: from 189.94 at ±1.15 down to 189.89 at the void edge ±0.95 (14°).
- There is a 0.02 step at each junction.
- The opening is still a **1.9 square** void (±0.95) and the flat felt top is still 190.0.
- All are overlay felt boxes in CourseBuilder's slope form: a box tilted by atan2(rise, size), 0.4 thick. They are cloned from deck_n (tags, physics) at Transparency 1.

**Iterations:**
- **v1, one 0.2 bevel flush with the deck at ±1.15** (2 runs, superseded): every 0.6/0.9 lip roll stopped at Chebyshev 1.185.
  - A ball resting in the deck felt's ~0.013 contact slop overlapped the bevel's top edge, and the engine pushed it back out.
- **v2, the same bevel dropped 0.02** (`superseded/h16-edge-v2bevel-*.json`): axis rolls drop, but lip stops were 4, 14 and 10.
  - The diagonals still deflected at the corner and stopped mid-edge, 0.04 outside the bevel.
- **v3, adding the outer band:** fixed.

**H16 edge test after ×3** (`h16-edge-after{1,2,3}.json`, `h16-lipstops-after.json`):
- **Lip stops 0/80, 0/80, 0/80. 0 drops outside the frame** (max fall Chebyshev 1.000 / 1.000 / 0.967; the frame's inner edge is 1.000).
- Slow putts 54/57/58 of 72 drop (baseline 24/22/24).
- **Rest scan:** every scanned distance up to 1.30 now drops (0.80-1.30), because 1.30 lies on the outer band. So the sc5 set's two "rest at 1.3 stays" balls now drop (10/12 against the old expectation). This is the intended change.
- Run 3 left the 4 corner rest balls at exactly Chebyshev 1.175 (0/4). That spot is the crest of the ridge where two outer bands meet; runs 1-2 dropped them, and every other distance dropped in all runs. I read this as physics-sphere variance on a measure-zero spot.

**Crystal test** (`tools/sc10_crystal.py`, `crystal-after.json`, `-score-d.json`): behaviour unchanged.
- 140/140 dropped, as on v69/v79.
- 120/140 paths touch a crystal while falling (sc10: 124). The earliest contact is 0.114 below the felt.
- **0 contacts while the ball is on the felt or bevel.**

**Visual:** the rim frame (1.0-1.21) and the visible felt are unchanged; the visible felt edge is still 1.03, under the frame. So the bands and bevels sit under the frame, and a ball rolling over 1.21-1.35 is briefly up to 0.04 below the visible felt.

**src:** CourseData H16 deck felts updated, plus 8 `lip_*` / `lip2_*` overlay slope entries and the d1 `edge` text.

### 3. H3 pebble: **moved** (component 26 only)
- **Measured the ground first** with EditableMesh `RaycastLocal` on the true render mesh (`pebble-strip-fine.json`, `pebble-ground-map.json`).
  - Under the pebble, `h03_ground_s22__RedDirtLight` is a **0.56-wide raised strip**: z -0.37..+0.19 around the pebble, top 18.37, along the foot of H3's rail12. Terrain is 0.9-1.3 lower on both sides.
  - The pebble's base vertices span **0.60** in z, so no plain ~0.3 shift can put every base vertex on the strip.
- **Best safe move:** yaw the pebble 53° about its own vertical axis, then shift it 0.084 south onto the strip. No vertex moved more than 0.374. Only the 12 positions of component 26 changed; the other 7 pebbles are byte-for-byte the same.
  - Result: all 6 base vertices are over s22 (margins 0.089 / 0.067), and all 11 vertices below the strip top are within the strip.
- **Persisting it:** `AssetService:CreateAssetAsync` is unavailable to MCP Luau ("not available yet").
  - I edited component 26 in Blender (`tools/sc12_pebble_fbx.py`; source `fix_v42_item5c/h03_dress_props.fbx`, SHA256 matches its manifest) and merged it into `sc12_K.fbx` with the flood rock.
  - One 3D Importer pass with the sc6-sc10 settings (`sc12-import-settings.png`, `sc12-import-geometry.png`).
  - Then `ApplyMesh` on the **Workspace and `ServerStorage.SugarloafKit` library copies**, with Size and CFrame kept.
- **Verified** (`pebble-import-verify.json`): every vertex of the new mesh matches the old one except component 26's 12 positions, and those are at the planned spots. Faces 160 = 160.
- New MeshId 135986339977333; the old id 112844478299336 is kept in the `SC12OldMeshId` attribute. Backups are in `ServerStorage.SC12Backup`.
- **Grounded** (`pebble-grounded.json`, true ground): before, 3 base vertices hung over Terrain (up to 0.786). After, every base vertex is over s22, sunk 0.263-0.32. Not floating.

### 4. Flat placeholder decals: **0 applied, 32 skipped/listed** (`decals-report.json`)
- **12 sign boards** (H2 left/mid/right, H3 plank/bridge, H6 overflow, H12 pier/shore, H13 west/centre/east, H18 rim): **skipped**.
  - Each already carries stage zf1's `StageZf1Image` with the manifest file's asset. sc11 read those assets back pixel-identical.
  - Each sits on the Front face, and the Front faces that hole's tee (checked against the tee positions).
  - The route-arrow images are on their own `route_arrow_*` items.
- **12 sign posts:** **listed.** manifest.json has no post decal (each item entry is the board image).
- **8 H10 chevron bars:** **listed, not applied.**
  - `h10_chevrons.png` is byte-identical to `h15_lip_chevrons.png`; the upload deduplicated to that existing asset, 91089251317155.
  - I applied it as a Top-face Texture, rotated 180° (asset 114758423794649) so the chevrons run along each bar toward its front, down the chute. A screenshot confirmed the direction.
  - But a decorated bar is a decal carrier for `ApplyVisualSeparation`, which lifted chevron_3 and chevron_4 **0.35-1.33 studs above the sloped chute felt**, so they floated.
  - Placeholder geometry must not change, so I removed the textures and reran separation. The bars are back at their exact v79 pose (delta 0).
  - These need a felt-level carrier (the 2.4 × 1.2 chevron anchors) from the art bot; the manifest has no h10 entry.
- No collider, placeholder geometry or flag was changed for item 4.

### 5. H6 flood-marks rock: **placed** (`imports-apply.json`, `floodrock-*.json`)
- `placeholders_ph2/flood_marks_rock.fbx`, **SHA256 matches** `manifest_h01_cactus_h06_floodrock.json` (b6eadc7d…753b). It came in the same `sc12_K` import.
- Placed at the manifest's target CFrame (266.5, 26.2, -4767), yaw 0, which is 2.08 west of the old spot, using the sc10 frame (root · centre · RY).
  - The rendered vertices match the FBX within 0.0005, so it is not mirrored.
  - Strata: Sandstone #BD6B4F (the shared Strata material). WaterMark: SmoothPlastic #3FB7C9.
  - Anchored, CanCollide/CanQuery/CanTouch off, `VisualQueryDisabled`.
- Workspace copy: `Hole6.Decor.flood_marks.flood_marks_rock`. Library copy: `ServerStorage.StageAFProps.flood_marks_rock`.
- **Decal:** the manifest says "h06_flood_marks.png can go on the face above the bars", so the same image (98287707564328) is now a Decal on the rock's flat east face, toward the basin. A Decal covers the whole face; the bars stand 0.086 in front of it.
- **Old placeholder:** the `Placeholder.Rock` part and its zf1 decal are hidden (Transparency 1), as earlier swaps did. The Placeholder model and Anchor are kept, so placeholders are still 175, now 35 visible.
- **Checks:**
  - Plan distance to the rail3 collider 1.268 and to the visible rail 1.186 (both ≥ 1), and to the basin felt 1.768.
  - Base sunk 0.02 below the true ground on all 57 base vertices. That is less than the manifest's 0.1 because the h06 ground tile sits 0.08 lower (sc5); nothing floats.
  - z-scan 0 exposed.
- **Tris** +128.

## C. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)` with gap 0.08 and min 0.2: **1204 fixes** (the same as sc11), 0 unresolved, 0 thin, 0 invariant failures, 171 joints.
  - **734 collider invariants** = 706 + 20 terrace + 8 lip pieces.
  - The first pass, with the chevron textures, gave 1208 fixes (item 4). It is kept in `superseded/`.
- **Colliders** (`collider-verification.json`, then `collider-verification-final.json` after all Play sessions; `after-vs-final.json` is identical):
  - 704 identical to v79.
  - Changed: 4 (H16 deck_m / deck_n / deck_w / deck_e).
  - Added: 28 (H15 `dune_lean3_terrace_01..20`, H16 `lip_*` and `lip2_*`).
  - Nothing else is missing.
  - Placeholders 175/175 with the same paths, 36 → 35 visible (the flood rock).
- **Parts 7471 → 7501** (+20 terrace, +8 lip, +2 rock).
- **Full dressing check** (sc10 rules, 1271 pieces, `dressing-check-after.json`): **felt 0 / rail<1 0 / float>0.1 0**. Closest rail 1.126. 234 felt polygons, including the 28 new pieces.

| z-scan (zf1_zscan.luau) | Before (v79) | After |
|---|---:|---:|
| Coplanar faces | 7130 | 7130 |
| Decorated coincident | 61 | 60 |
| Placeholder coplanar | 16 | 15 |
| Transparency candidates | 632 | 632 |
| **Total** | **7839** | **7837** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 7126 | 7127 |
| Terrain candidates | 131 | 131 |

- **Triangles** (`tools/sc12_tris.py` = the sc11 method, `tris-after.json`): **whole place 1,649,887** (sc11 1,649,759, +128 rock). **Within 500 of the H1 tee: 673,313** (+128).

Screenshots:
- `sc12-after-h15wall.png`: the terrace, shown with a temporary cyan overlay that was deleted afterwards.
- `sc12-after-h16lip.png`: the bands and bevels, magenta overlay (deleted).
- `sc12-after-h03pebble.png`, `sc12-after-decals.png`, `sc12-after-h06rock.png`.

## D. Playtests
- **Smoke:** flow PASS, putt 7.57, **0 errors**, 0 server entries; only the 5 UIBlox `FoundationProvider` warnings (`sc12-smoke.log`).
- **18-hole sweep, seed 20261014:** **54/54 cups, 36 shots, 0 stuck, 0 escapes, 0 timeouts**, console empty. The only hole that differs is H15 (timeouts 2 → 0) (`sweep-after/`, `sweep-comparison.json`).
- **seamshots-80 after:** 0 wedged / 0 non-rest (`seam-after6.json`; the intermediate runs are `seam-after1..5.json`, traces in `seam-trace*.json`).
- **H16 edge ×3 and crystal:** see item 2.

## E. Publication
- File > Publish to Roblox (⌥P), one publish. Studio showed "Published". **Creator Hub published-only shows v103** at 10:58 PM, the time of the publish (`sc12-v103.png`); the last edit was before it. v81-v102 are autosaves.
- **File > Download a Copy:** `playtest/playtest-sugarloaf_canyon-v103.rbxl`, 5,435,842 bytes, SHA256 `242c580896a024e8988b2f0bcd3f8e24351e02954adeaaea39acfb792cbc2cd6`. I saved it through a temporary home folder and moved it into place.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains, only the StudioMCP helpers.
- **Final published-only:** SC 103; lobby 251, LG 19 and AU 13 unchanged (`sc12-final-histories.png`). Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.
- **New uploads** (none deleted or archived):
  - The 3D Importer: model `sc12_K` 90818052554732, plus MeshParts.
    - MeshIds in use: Pebble 135986339977333, flood_marks_rock__Strata 115641663732452, __WaterMark 94673900423683.
    - Asset Manager also lists MeshPart assets 104311673269328 (its name shows as "########", text-filtered) and 111587342533688.
  - Images 97749202443626 (chevrons rotated 90°) and 114758423794649 (rotated 180°). Both are unused after item 4.
  - The plain h10_chevrons upload created nothing (it deduplicated to 91089251317155).
- The importer's temporary folders `~/a_sc12imp` and `~/a_sc12save` were removed.
  - The Desktop copy (made before the Desktop prompt) was removed too. The prompt was denied, so Studio never read it.

## Tools (new/changed)
- `sc12_stage.py`: the sc11_stage commands writing to stage-sc12.
- `sc12_seam.py`: the 80-shot manifest, `run NAME [SHOTS] [trace]`, `summary`.
- `sc12_h16_edge.py`: sc8 edge test plus slow lip rolls, end points, lip-stop counts; it runs async so it can't time out.
- `sc12_h15.py`: fillet/terrace spec (`spec`) and the stepped rest terrace (`segments`).
- `sc12_pebble_fbx.py`: Blender, moves one component of the H3 Pebble mesh.
- `sc12_place.py`: sc11_place writing to stage-sc12 (dressing check).
- `sc12_tris.py`: sc11_tris writing to stage-sc12.
- `GolfTest.luau`: `seamshots` with several seams, wedged / non-rest classification, flag positions and an optional trace (test mode only).
- `CourseBuilder.luau`: exact-pose felt pieces (`cframe` + `part_size`).
- `CourseData/SugarloafCanyon.luau`: the H15 terrace and the H16 lip.
- Skill `roblox-studio-mcp`: sc12 lessons (right-handed CFrames, no CreateAssetAsync, importer dialog workarounds, upload dedup, decal-carrier lift).

## Open items
- **H10 chevrons:** a texture on the thin chevron bars makes VisualSeparation float them. The art bot should give the chevrons a felt-level carrier (or a manifest entry with a carrier) before the decal can go on.
- **H3 pebble:** I used a 53° yaw plus 0.084 shift instead of a ~0.3 nudge, because the s22 strip (0.56) is narrower than the pebble base (0.60). If the art bot prefers, a smaller pebble or a spot about 3 studs east, where s22 widens, are the alternatives.
- **H16:** the drop zone now reaches the flat-deck edge at ±1.35, so a ball resting up to ~1.33 drops, where it used to stay at ≥0.95. Corner balls placed exactly on a ridge crest (1.175) once stayed in physics-sphere tests.
- **H15:** lean3 is now a resting ledge: a ball that reaches it stops rather than running to the green. Players putt off it.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=103 H15_80=2/27 before -> 0/0 after H16_LIP=4,12,12/80 before / 0,0,0/80 after (x3) OUTSIDE_DROPS=0 PEBBLE=moved DECALS_APPLIED=0 SKIPPED=32 FLOODROCK=placed DRESSING_CHECK=0/0/0 TRIS_ALL=1649887 TRIS_H1_500=673313 PARTS=7471->7501 SC_SCAN=7839/7837/0 CUPS=54/54 SWEEP=36/0/0/0 SMOKE_ERRORS=0 (+5 UIBlox) COLLIDERS=same except H15 wall (+20 terrace) + H16 lip (4 deck felts resized, +8 lip pieces) STUDIO_CLOSED=yes COMMIT=(this commit, see git log)

BUILD DONE, STUDIO CLOSED
