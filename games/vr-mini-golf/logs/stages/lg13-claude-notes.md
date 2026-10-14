# Stage lg13 (Claude Code): Lantern Grove fix_zfight models + separation fixes

Status: **PASS. Lantern Grove published v19** (Creator Hub Version History, "Show published only": 19, 12, 9, ...; v19 = Oct 14 2026 9:37 AM). Evidence: `lg13-v19.png`, `lg13-history-all.png`.

## Preflight
- One Studio, already open on Lantern Grove from the cloud (EditPlace 91438142503824), signed in as MetavrseBuilder (StudioService user 1818120139). MCP: PlaceRole `lantern_grove`, `Workspace.Course` Hole1-Hole9, local PlaceVersion 13.
- No other stage job was running (only the ChatGPT/Codex desktop app). Accessibility and Screen Recording now work for this runner (`screencapture`, CGPreflight checks True), which unblocked the earlier lg13 attempts.
- The open place matched the published v12 file exactly: the full Workspace inventory (3822 parts) was identical to attempt 1's v12 inventory, and the scan total was the same (3208).
- macOS showed a "com.apple.sshd-session ... bypass the system private window picker" prompt the whole time. I left it alone (did not Allow). I clicked "Don't Allow" on an automation prompt ("sshd-keygen-wrapper wants to control Google Chrome") that my own osascript triggered.

## Import (3D Importer, one pass)
- Blender-merged `/tmp/lg13/lg13_props.fbx` (merge PASS: 6 files, 22 meshes, 4982 tris, max 834). SHA256 of every source FBX matches its manifest.
- Sources: `fix_zfight4/h5_respawn_stone.fbx` (flat 0.206 disc), plus from `fix_zfight/`: `gold_leaf_bush`, `grass_tuft`, `lantern_span_20`, `h9_lantern_pendulum`, `h9_lantern_pendulum_h9dim`.
- Importer settings (same as au6): Import Only as a Model off, Upload on, Add to Workspace, Insert Using Scene Position, Set Pivot to Scene Origin, Anchored, cages and zero-influence bones off, Stud, scale 1.
- The importer auto-scaled the scene x99.4 and baked a Y half-turn. Each mesh was normalized from the true FBX bounds (`tools/fbx_bounds.py`) with the half-turn undone (`tools/lg13_props.py`).
- Replaced the kit (`ServerStorage.LanternGroveProps`, 6 models; `LG13Source`/`LG13Sha256` attributes) and all 43 placed copies once each: 30 grass_tuft, 10 gold_leaf_bush, H8 lantern_span_20, the H5 h5_respawn_stone, and the H9 pendulum PropVisual (h9dim variant). Each copy keeps its pivot, ScaleTo factor, colours/materials (H9 dim), lights (2 moved), SurfaceAppearances and mover welds. The staging model was deleted, leaving no duplicates. Details: `playtests/stage-lg13-claude/props-imported.json`.
- H5: the stand-ins `Hazards.RespawnStone` (hidden) and `Decor.bridge_respawn_stone` (invisible ForceField anchor) were left in place as placeholders. The new stone is 0.206 thick; its bottom is 0.156 above the felt and it clears everything by 0.156.

## Fixes
1. **Duplicate H7 stakes:** deleted `Hole7.Decor.Props.Dressing.rail_lantern_stake` (3 instances under one path, at (34.25,-15.64), (49.64,1.25), (45.75,-15.64)). Each was an exact copy of the `Light_H7_rail_right_01/left_02/left_01` stake, 0.05 lower. They were not colliding and nothing referenced them.
2. **H8 Base:** `Hole8.Geometry.Base` (6.5,35.8,12) went 0.1229 into the ramp felt. Its collider is unchanged and hidden; a new noncolliding `ZF1VisualLayers.Visual_Base` is trimmed 0.204 at its -Z face, leaving a gap of **0.0811**.
3. **EntryRing (source):** `src/ServerStorage/CourseBuilder.luau` `Hole:buildTeleport` (now around lines 1500-1509). The ring and glow disc are 0.2 thick, lifted 0.18 (a 0.08 gap above the felt), side by side, with the disc radius = ring radius - 0.18 (0.08 radial gap). Applied in place to the H8 and H9 EntryRings with ZF1 base poses rebased. (The OBB scan still flags ring segments against the disc's square box; the true circular gap is 0.08.)
4. **H7 gold_leaf_bush** (47.83,-24.21): it overlapped `leaf_pile` by 0.331. Moved 0.75 to (48.02,-24.94); it now clears every visual part by 0.125 and colliders by 2.28 (was 2.09).
5. **Rail pulls (OBB, conservative; parallel rails):**
   - H5 drop_face_stone at x72.2: +X 0.59, ends trimmed 0.08/0.24. Clearance 0.090.
   - H5 drop_face_stone at x84.8: +X 0.68, ends trimmed 0.26/0.16. Clearance 0.088.
   - H2 drop_face_stone: +Z 0.75, ends trimmed 0.12/0.08. Clearance 0.086.
   - H6 drop_face_stone: +Z 0.275. Clearance 0.083.
   - H2 lantern_post (rail1): +X 0.24, foot clears rail1 by 0.090.
   - ZF1 base poses were rebased for all of these. The strips still stay embedded in their bases. The perpendicular T-crossings with rails 7/8 remain as intersections, not coplanar faces.
6. **VisualSeparation** reran through `CourseBuilder.ApplyVisualSeparation` (after a full `src` push): gap 0.08, min 0.2, unresolved 0, thinAfter 0, invariantFailures 0, 1148 operations (idempotent reapplications included), 93 joints reconnected.

## Verification
| Category | Before (v12) | After |
|---|---:|---:|
| Coplanar faces | 2857 | 2719 |
| Decorated coincident | 0 | 0 |
| Placeholder coplanar | 0 | 0 |
| Transparency candidates | 351 | 378 |
| Total | 3208 | 3097 |
| Exposed planar candidates | 0 | 0 |
| Imported mesh hits | 2803 | 2683 |
| Terrain candidates | 117 | 117 |

- After classes: 2477 non-planar or mesh-bbox and 242 opposing-interface reviews. The transparency count rose by 27, mostly from the thicker translucent EntryRing glows.
- Colliders: all **396 gameplay parts (270 colliders)** are identical to v12 for path, CFrame, size, collide/query/touch, physics, group, anchored and custom physics. This was rechecked after Play. No collider was deleted.
- Placeholders 0/0. Workspace BaseParts went 3822 -> 3805 (-15 from the 3 stake models, -2 from the h5 stone and lantern_span meshes).
- Smoke PASS (real putt, 0 server/client errors or warnings).
- 9-hole sweep: **27 cups / 18 shots / 0 stuck / 0 escapes / 0 timeouts**, console empty. That matches the v12 baseline exactly on every hole (`playtests/stage-lg13-claude/sweep/summary.json`).
- H9 pendulum in Play: swings ±11° (samples 0.7, 8.5, 11.0, 7.0, -1.3, -8.8 deg), rigid to its Blocker, PointLight present.

## Publication
- File > Publish to Roblox, a single publish to the open cloud place (the first menu click did not register; the ⌥P publish did).
- Creator Hub shows **v19 published, Oct 14 2026 9:37 AM**. Versions 13-18 are unpublished saves (13 = Oct 13 11:00 PM; 14-18 are Studio cloud saves at 9:10-9:30 AM during this stage), which explains the skip from 12.
- Local copy via File > Download a Copy: `playtest/playtest-lantern_grove-v19.rbxl`, 3,472,650 bytes, SHA256 `19f50f07c7efdeb1326896a08035f79d70eafd1b2685f3aeb6333a762b921f7e`.
- Studio quit normally.

## Open items
- **H5 stone colour zones:** the fix_zfight4 stone is a single mesh with 3 material slots, so Roblox renders it as one Slate MeshPart. The ShroomGlow centre and Moss sector don't show without a texture or SurfaceAppearance.
- **H7 crooks:** the four Dressing `rail_lantern_crook` models also duplicate `Light_H7_rail_*` crooks (0.05 offset). They were not in scope, so they are left in place. The source data (dressing + pointLights) would recreate both duplicates on a fresh `PropsBuilder.Place()`.
- **Persistence:** the in-place fixes (bush move, rail pulls, stake deletion, Visual_Base) live in the place only, not in PropPlacements or holes data. Only the EntryRing change is in `src`. The EntryRing source change also affects any other course that has teleports on its next push.
- Not done: the `.rbxl` copy to the Linux box, a lobby/SC/AU published-version recheck (Creator Hub), and a headset check.
