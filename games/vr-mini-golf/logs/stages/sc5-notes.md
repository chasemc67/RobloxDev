# Stage sc5 (Claude Code): Sugarloaf Canyon fix_zfight imports, ground drop, placeholders, decals

Status: **PASS. Sugarloaf Canyon published v34** (Creator Hub Version History, "Show published only": 34, 23, 21, 19, ...; v34 = Oct 14 2026 10:58 AM). Evidence: `sc5-v34.png`, `sc5-history-all.png`, `sc5-final-histories.png`.

## Preflight
- One Studio, opened from the cloud on Sugarloaf Canyon (EditPlace 124440050576723), signed in as MetavrseBuilder (StudioService 1818120139). MCP: PlaceRole `sugarloaf_canyon`, PlaceVersion 24 at open.
- **Course root:** the place has `Workspace.CourseSugarloaf` (Hole1-Hole18), not `Workspace.Course`. Sugarloaf has always used `CourseSugarloaf` (zf1 tools, the placeholders_ph1 manifest paths), so I treated the gate as an identity check and proved identity directly instead of stopping.
- **Matches published v23:** all 705 colliders identical to `playtests/stage-zf1/colliders-after.json` (zf1 final = v23); placeholders 175 parts / 65 visible (= zf1 final); z-scan total 5617 with every category equal to the zf1 v23 scan.
- No other stage job (only the ChatGPT desktop app's codex exec-server/app-server). The macOS "com.apple.sshd-session ... bypass the system private window picker" prompt stayed on screen the whole stage; I left it alone, and avoided sending Return keys while it was up.
- Creator Hub published-only baselines: lobby 251, LG 19, SC 23, AU 8. Unfiltered latest: lobby 252, LG 19, SC 25, AU 9. Details: `playtests/stage-sc5/preflight.json`.

## Imports (3D Importer, 3 passes)
Settings as lg13: Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages and zero-influence bones off, Stud, scale 1. The importer scaled each scene uniformly (x3.30, x53.7, x62.7) and baked a Y half-turn; every part was rebuilt from the true FBX bounds.
- Merges (`tools/sc5_merge_fbx.py`, Blender 5.2, round-trip PASS for all): **A** = 155 fix_zfight files (119 props + 36 cacti groups) + rim_silhouette (fix_zfight4) + h16_sinkhole_rim (fix_zfight6) + h11_lock_gate (fix_zfight2) + 12 placeholders_ph1 = 170 sources, 768 meshes, 292,819 tris (max 3,916). **B1/B2** = the 188 fix_zfight3 ground tiles, split by material slot (a MeshPart renders one material), 188 + 242 meshes, 351,640 tris (max 2,334). Every source SHA256 matches its manifest.
- Not imported, by design (`imported.json` -> notImported): the 151 old fix_zfight t-tiles (superseded by fix_zfight3), fix_zfight's rim_silhouette / h16_sinkhole_rim / h11_lock_gate (superseded by fix_zfight4/6/2), the two H7 teleport pad meshes (replaced by decals), and plank_respawn_stone (decal, no mesh). The prompt said "184 models" for fix_zfight; the manifest has 275 entries = 124 props + 36 cacti groups + 115 old t-tiles, and 155 of them were imported. I could not reconcile 184.
- Replacement (`tools/sc5_import.py`): every model in CourseSugarloaf and the ServerStorage libraries (SugarloafKit, SugarloafMovers, StageAE/AF/AJProps) whose parts are `<stem>__*` was replaced once: **430 copies (279 Workspace, 151 library), 144 old stems**. Frame per copy = per-axis median scale, the largest part's rotation and the median position, solved against whichever old export of the prop fits (the live StageAE/AF copies are props_batch1/4 exports, not movers/); when zf1 had nudged single parts, the builder-set model pivot was used (22 copies). Appearance comes from the old part with the same material suffix. Mover visuals keep their MoverRoot welds (20), unanchored and massless. The railing_12 copies are stretched x1.127 on Z, and that stretch is kept.
- Ground tiles: all 18 hole grounds (H8's lives in `Hole8.StageAJVisuals`), collision/query/touch off.
- The trading_post_deck was already at layout (47.5, 17.361, 469.0) yaw -90 (Studio z = layout z - 5000). The new mesh bbox is (42.5, 17.21, 458.0)-(54.3, 25.76, 480.0). **Rail1 check (vertex level, 114 pieces):** the 5 pieces taller than 2 studs are at least **3.568** from H1 rail1, so it PASSES (`deck-clearance.json`).
- h16_sinkhole_rim (square frame): CanCollide/CanQuery/CanTouch off, plus `VisualQueryDisabled`. At runtime `CameraOcclusion` was switching CanQuery on for decor without that attribute, and with it the rim stays off in Play.
- placeholders_ph1: 12 meshes at their manifest placements (offset 0,0,-5000), each as `Decor.<name>.SC5Mesh`. crystal_cue, lantern_cue and gate_light Neon slots are Material=Neon. tunnel_lanterns is duplicated every 6 studs along the H2 right tunnel (hole-local z -20/-26/-32/-38, x 9, y 8). The 28 stand-in parts are **hidden, not deleted**.

## Decals (uploaded via Studio MCP)
- `h07_teleport_pad_decal.png` -> rbxassetid://140048238303612 on the 4 entry/island pads; `h07_teleport_pad_exit_decal.png` -> rbxassetid://105141020957957 on the exit pad. Each is 3 x 2 (the pad mesh footprint), on a transparent 0.2 carrier whose top sits 0.08 above `Hole7.Geometry.Felt`. The 4 pad mesh models were removed (visual only, checked to have no gameplay flags or tags); the teleport triggers and colliders are unchanged.
- `plank_respawn_stone_decal.png` -> rbxassetid://135394135115475, 0.8 x 0.5 (the stone footprint at the image's 1.6:1 aspect), flat on H3 felt at the plank respawn stone, 0.08 lift, no mesh. The stand-in is hidden.

## Ground drop (step 4, `tools/sc5_ground.py`, `ground-summary.json`)
- Lowered 0.08: all 9 even-hole grounds, the 17 even-hole dress sets, plus what rests only on even ground (cacti_crown_g02, mine_head, h02_headframe, h04_geode_wall, h06_bell_tower, h12_intake_tower, h14_loading_dock, the ore_carts and big_gumdrop_bg meshes). **35 units, 381 parts.** No colliders moved. Felt/rail contact was taken from the art bot's vertex-level fitcheck (clearance at least 0.156 for all of these), because the merged MeshParts' boxes span whole holes.
- A first pass also moved cacti_taffy_north_g04 and h18_arch_gate. A finer probe showed both rest on Terrain (arch gate bottom = terrain y 190.0), so I moved them back +0.08.
- **The 9 coplanar pairs from results.md**, each checked on a 0.25-stud ray grid with each tile probed on its own: **before**, every pair coplanar (469 samples within 0.02, minimum gap 0.0000); **after**, **0 coplanar samples in all 9 pairs, minimum gap 0.056 (median 0.07-0.09)**, and the same after VisualSeparation (`seams-before.json`, `seams-after.json`).
- **Float check:** every kept unit was sampled. 0 units sit flush (within 0.15) on an even-hole ground, so nothing floats.

## VisualSeparation and verification
- Pushed all of `src` first (Studio was missing CourseBuilder.ApplyVisualSeparation and AuroraVisualCleanup; it now matches src exactly). `CourseBuilder.ApplyVisualSeparation(CourseSugarloaf)`: gap 0.08, min 0.2, **1204 fixes, 0 unresolved, 0 thin, 705 collider invariants, 0 failures**, 171 joints reconnected. VisualSeparation records fresh ZF1 base poses for the new parts; the ground-drop rebase found no old ZF1 poses on the moved parts (all were new meshes).
- **Colliders: same.** All 707 gameplay parts are identical to v23 (path, CFrame, size, collide/query/touch, physics, group, anchored, custom physics). Rechecked after the Play sessions (`collider-verification.json`).
- **Placeholders: 175 / 175 instances** (same paths). Visible went 65 -> 36 (28 ph1 stand-ins plus the plank stand-in are hidden, not deleted).

| z-scan (zf1_zscan.luau) | Before (v23) | After |
|---|---:|---:|
| Coplanar faces | 5073 | 5985 |
| Decorated coincident | 101 | 61 |
| Placeholder coplanar | 41 | 16 |
| Transparency candidates | 402 | 306 |
| **Total** | **5617** | **6368** |
| **Exposed planar candidates** | **0** | **0** |
| Imported mesh hits | 4888 | 5655 |
| Terrain candidates | 119 | 131 |

The raw coplanar count rose with the MeshPart count (tiles split by material, more prop pieces). After classes: 5475 non-planar or mesh-bbox candidates and 510 opposing interfaces, none exposed planar.

## Playtests
- Smoke PASS (real putt 7.57 studs, menu/finish lobby request, 0 server/client errors or warnings): `sc5-smoke.log`.
- 18-hole sweep, same seed as baseline. **Baseline v23: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 2 timeouts (H15). After: 54/54 cups, 36 shots, 0 stuck, 0 escapes, 1 timeout (H15)**, console empty both times. The H15 slope timeouts predate this stage (zf1 saw the same on untouched v21) and the colliders are identical.
- **H16 sinkhole edge** (`h16-edge.json`, Play/Server, r 0.08 spheres): all 4 axis rolls and 4 diagonal rolls (one ball at a time) drop through, balls at rest 0.9 from centre drop, and balls at rest 1.3 (outside the ±1.2 opening, on felt) stay. The collider opening is a ±1.2 square (1.7 at the corners); the rim does not interfere.

## Publication
- File > Publish to Roblox (⌥P), one publish, to the open place. Creator Hub published-only shows **v34** at 10:58 AM. Versions 25-33 are unpublished Studio autosaves from this session (25 = 9:50 AM, before any edit).
- File > Download a Copy: `playtest/playtest-sugarloaf_canyon-v34.rbxl`, 4,991,846 bytes, SHA256 `bcf0f72959ea6d1455d4f6844ae49e4d9b8caf0b29f3d1042cab6fd27dbebcef`.
- Studio quit normally (⌘Q, no prompts). No RobloxStudio process remains.
- Final Creator Hub published-only: **lobby 251, LG 19, AU 8 unchanged**; SC 34. Lobby, LG, AU, 135374506016678 and the Windows PC were never opened or used.

## Incident (recovered before publish)
My first replacement pass solved each copy's frame from its first old part with one uniform scale. That misplaced 69 copies (non-uniform railing stretch, a different FBX export behind the StageAE/AF movers, parts nudged by zf1). ChangeHistory undo only partly reverted it: it removed the new parts and the sc5_A bundle but did not restore the 965 destroyed Workspace parts or the 746 ServerStorage library parts, and Studio autosaved the damaged state (unpublished versions 27-29). Recovery:
1. Re-inserted the uploaded sc5_A model asset 104611014558516.
2. Restored the 5 libraries exactly from place **version 23** (`game:GetObjects` on assetdelivery `?id=124440050576723&version=23`).
3. Rebuilt the 965 Workspace parts from the v23 library templates plus the exact pose, size and flags in `inventory-before.json` (`tools/sc5_restore.py`). The whole Workspace then matched the v23 inventory field for field (4071/4071).
4. Reran the replacement with the robust frame solve; old parts went to a ServerStorage backup, deleted only after verification.
Nothing gameplay was ever touched (all 965 were visual MeshParts). The only loss is the cached ZF1 base attributes on those 965 parts, and those parts were then replaced.

## Open items
- **Persistence:** the replacements, ground drop, placeholder meshes, decals and pad removal live in the place, not in `src`/CourseData. A fresh `SugarloafBuilder.PlaceMeshes` would re-place the H7 pad meshes from SugarloafMovers, and the ServerStorage library copies now hold the new meshes.
- **Look changes flagged by the art bot:** the trading_post_deck lost its "TRADING POST" board, the h16_sinkhole_rim has no CrystalGlow part, and fix_zfight3 tiles are split per material slot.
- **tunnel_lanterns:** the anchor note mentions overhead crossbars every 6 studs; no crossbar exists in the place, so the 4 lanterns hang free at y 26.
- **Fallback appearance:** 14 new suffixes with no old match took a same-suffix part elsewhere (e.g. h14_ore_bucket CandyAmber from the slot kit). Placeholder slots with no match anywhere (NeonPink/Green/Red/Gumdrop/Amber, SandstoneRed, RockCandyPink, RustIron, RivetIron, RiverStone*) use Blender colours.
- Not done: the `.rbxl` copy to the Linux box and a headset check.

RESULT=PASS SC_NEW=34 SC_SCAN=5617/6368/0 PLACEHOLDERS=175/175 CUPS=54/54 SWEEP=36/0/0/1 COLLIDERS=same
