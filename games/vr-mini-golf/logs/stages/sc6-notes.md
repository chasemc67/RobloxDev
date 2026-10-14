# Stage sc6 (Claude Code): Sugarloaf Canyon TRADING POST board, H16 neon crystals, fit030 grounds

Status: **PASS. Sugarloaf Canyon published v42** (Creator Hub Version History, "Show published only": 42, 34, 23, 21, ...; v42 = Oct 14 2026 12:59 PM). Evidence: `sc6-v42.png`, `sc6-history-all.png`, `sc6-final-histories.png`.

## Preflight
- One Studio, opened from the cloud on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 34 at open. `Workspace.CourseSugarloaf` has Hole1-Hole18.
- **Matches published v34:** all 707 gameplay parts are identical to sc5's final inventory (= v34), 4454/4454 parts. Placeholders are 175 parts / 36 visible, same paths. The z-scan total is 6368, every category equal to sc5's after scan.
- No other stage job (`pgrep -fl "claude -p"` empty).
- Creator Hub published-only baselines: lobby 251, LG 19, SC 34, AU 13 (`sc6-preflight-sc-published.png`, `sc6-preflight-others.png`, `playtests/stage-sc6/preflight.json`).
- The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt was up the whole stage. I never answered it and sent no Return key. File dialogs were confirmed by double-clicking the Go-to suggestion and clicking Open/Save.

## 1. Baseline (untouched v34)
- Smoke PASS: real putt 7.08 studs, 0 server/client errors or warnings (`sc6-smoke-before.log`).
- 18-hole sweep, seed 20261014 (the same as sc5): **54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15)**, console empty (`sweep-before/`).
- z-scan before: `zscan-before.json` (6368, 0 exposed planar). Screenshot: `sc6-before.png`.

## 2. TRADING POST board (`tools/sc6_place.py board`, `board.json`)
- The board is two v23 parts: `trading_post_deck__MintWhite` (the 10 x 1.3 board, texture rbxassetid://103236692622281) and `trading_post_deck__PepRed` (the 6.68 x 0.67 lettering plate, texture rbxassetid://93459777512926). sc5's fix_zfight mesh has neither.
- `game:GetObjects` on assetdelivery `?id=124440050576723&version=23` returns no Workspace, so the template (mesh, texture, colour) came from v23 `ServerStorage.SugarloafKit.trading_post_deck`. The Workspace pose and size came from the v23 Workspace inventory (`stage-sc5/inventory-before.json`). Check: live deck pivot × v23 library CFrame = that pose, **delta 0**, rotation equal.
- Placed in `Kit.hole_dressing.trading_post_deck.trading_post_deck`. CanCollide/CanQuery/CanTouch are off and it is anchored. The v23 library parts were also added to `ServerStorage.SugarloafKit.trading_post_deck`. Awnings and lanterns are untouched.
- **H1 rail1 clearance:** both board parts are at least **13.87** studs from `Hole1.Rails.Rail_rail1` / `RailCap_rail1` (75-point box sample per part).

## 3. H16 sinkhole rim crystals (`h16-rim.json`)
- fix_zfight6 dropped the batch-4 `CrystalGlow` part, which was Neon pink in v23. Its README says the crystals were carried over into the rim. The only crystal/rim part is now `h16_sinkhole_rim__GeodeRim`, a single square ring with one material slot.
- Set Material=Neon, Color = placeholders_ph1 crystal_cue `NeonPink` (1, 0.4, 0.75), CastShadow off, in `Workspace...Hole16.StageAFVisuals.h16_sinkhole_rim` and `ServerStorage.StageAFProps.h16_sinkhole_rim`. All rim parts keep CanCollide/CanQuery/CanTouch off, and `VisualQueryDisabled` stays (asserted).
- **Amber was not applied.** crystal_cue has only one Neon slot (NeonPink). The only amber Neon slot in placeholders_ph1 is tunnel_lanterns `NeonAmber` (1, 0.7, 0.25). A MeshPart shows one colour, so pink plus amber needs the art bot to split the rim mesh into two material slots (open item).

## 4. fit030 swap (`tools/sc6_import.py`, `imported.json`)
- Sources: all 195 fit030 FBX files, SHA256 matching `fit030_manifest.json`: 191 ground tiles (fix_zfight3 had 188; H2 adds s04/s14/s24) plus h02/h09/h11/h13_dress_props. No look7, placeholders_ph2 or other kit props were imported.
- Blender merge (`sc5_merge_fbx.py --split-materials`), both PASS on round-trip. **B1** = h01-h09 tiles, 83 sources, 194 meshes, 155,384 tris (max 2,356). **B2** = h10-h18 tiles + the 4 dress props, 112 sources, 278 meshes, 207,336 tris (max 2,194). Reports are in `merge/`.
- 3D Importer, 2 passes, settings as in sc5: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages off, No Rig, Stud, scale 1 (`sc6-import-settings.png`, `sc6-import-geometry.png`). The importer scaled uniformly (x53.71, x30.06). Every mesh was rebuilt from the true merge bounds with the Y half-turn undone.
- **Frame from `kit_fitcheck_030.json`**, not guessed: Workspace copy = fitcheck pos + SugarloafLayout offset (0,0,-5000), identity rotation, **-0.08 on even holes**. Library copies sit at the origin. A dry run checked every frame against the old parts' FBX bounds: all 46 copies fit within a median of **0.005** (even holes included, so the sc5 drop is carried over exactly).
- Replaced **whole sets, once each**: 18 Workspace grounds (H8 in `Hole8.StageAJVisuals`) + 20 library grounds (SugarloafKit ×18, StageAEProps/StageAJProps h08) + 4 Workspace and 4 SugarloafKit dress props = **46 copies, 994 old parts → 1006 new parts**.
- After the swap: **0 fix_zfight3 tiles left anywhere**, no copy mixes old and new tiles, no duplicate names, no appearance fallbacks, all new parts have collide/query/touch off. Appearance came from the old part with the same name.
- The 0.08 drop sits in the frame on even Workspace holes (`SC6GroundDrop` attribute on 9 grounds + h02 dress props).
- **Float check** (`float-check.json`, `float-gaps*.json`): the sc5 drop planner gives the same drop set as sc5. Its one "float risk", h02_dress_props, was already dropped with the ground and sits flush (25/33 contacts within 0.15). It is only flagged because new parts lack sc5's fitcheck attribute. Signed gaps under all 145 visual units: the units with a bbox gap over 0.05 are the merged dress_plants sets. They show the same gaps on the old tiles (6 before, 5 after, differences under 0.005), so **the fit030 grounds make nothing float**.
- Old parts went to `ServerStorage.SC6Backup` and were deleted (994) only after the final collider check. The staging bundles `sc6_B1`/`sc6_B2` were removed from Workspace. No recovery was needed.

## 5. VisualSeparation and verification
- `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)`: gap 0.08, min 0.2, **1204 fixes, 0 unresolved, 0 thin, 705 collider invariants, 0 failures**, 171 joints reconnected. The fix set is identical to sc5's (idempotent). No fix touched the new grounds, the board or the rim. The fit030 `h02_dress_props__Bubblegum` box (0.136 high) was raised to 0.2, as sc5 did with the old one.
- ZF1 rebase: no existing part moved (sets were replaced, not moved; the board is new; the rim changed colour only). New parts carry no copied ZF1 attributes, so there was nothing to rebase.
- **Colliders: same.** All 707 gameplay parts are identical to untouched v34 (path, CFrame, size, collide/query/touch, physics, group, anchored, custom physics), after separation and again after all Play sessions (`collider-verification.json`, `collider-verification-final.json`). Rails are unchanged. Placeholders 175/175, 36 visible, same paths. Parts went 4454 → 4462 (+6 H2 tiles, +2 board).

| z-scan (zf1_zscan.luau) | Before (v34) | After |
|---|---:|---:|
| Coplanar faces | 5985 | 5918 |
| Decorated coincident | 61 | 61 |
| Placeholder coplanar | 16 | 15 |
| Transparency candidates | 306 | 304 |
| **Total** | **6368** | **6298** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 5655 | 5585 |
| Terrain candidates | 131 | 131 |

Screenshot: `sc6-after.png` (TRADING POST board on the deck, pink Neon H16 rim, H2 and H13 grounds and dress props).

## 6. Playtests
- Smoke PASS: real putt 7.26 studs, **0 server/client errors or warnings** (`sc6-smoke.log`).
- 18-hole sweep, same seed. **Before: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15). After: 54/54, 36, 0, 0, 2 (H15)**, console empty both times. Every hole is identical (`sweep-comparison.json`). The H15 slope timeouts predate this stage (sc5 and zf1).
- **H16 sinkhole edge** (`h16-edge.json`): the 4 axis rolls and 4 diagonal rolls drop, balls at rest 0.9 from centre drop, and balls at rest 1.3 stay. All 12 outcomes are the same as sc5. The rim keeps all flags off.

## 7. Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v42** at 12:59 PM. v35-v41 are Studio autosaves from this session.
- File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v42.rbxl`, 5,026,631 bytes, SHA256 `b0f183f80704f366233a7e7011ab5f8cab257116da0546ae1ddc679208a8f09c`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains.
- Final Creator Hub published-only: **lobby 251, LG 19, AU 13 unchanged**; SC 42. Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.

## Open items
- **H16 amber:** the rim is one MeshPart, so it got crystal_cue pink only. Pink plus amber needs an art-bot rim with two crystal material slots (or a separate crystal mesh).
- **Persistence:** the fit030 swap, board and rim colour live in the place and the ServerStorage library copies, not in `src`/CourseData.
- The importer uploaded `sc6_B1`/`sc6_B2` model assets. They are unused (the parts live in the place).
- The trading post board parts overlap each other by design, as in v23 (lettering plate behind the board). The z-scan shows no exposed planar hits.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=42 SC_SCAN=6368/6298/0 CUPS=54/54 SWEEP=36/0/0/2 H16=same SMOKE_ERRORS=0 COLLIDERS=same
