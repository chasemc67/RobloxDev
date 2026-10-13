# Stage ai — local Aurora v4 props and per-piece ice drag

Status: **PARTIAL — saved locally and Studio closed.** Gameplay checks pass; conservative built-prop clearance findings and visible coplanar candidates remain unresolved.

## Scope and local preflight

Read the game AGENTS.md and ag/ah/af notes plus af-portability first. No competing stage job matched the requested process check. Studio's welcome screenshot showed MetavrseBuilder. Opened only `playtest/playtest-aurora-v3.rbxl` using File > Open from File and immediately used Save to File As for `playtest/playtest-aurora-v4.rbxl`. Native UI confirmed that exact local path. MCP retains the original v3 display name, as in previous stages. Preflight verified PlaceId=0, GameId=0, no NetworkClient, role aurora_archipelago, one open place.

No cloud place was opened/saved, no experience created/published, no git push, and protected place 135374506016678 was not touched. The importer was visibly set to Upload to Roblox unchecked, scene position/origin enabled, anchored enabled, cages disabled. Its automatic child mesh asset creation is within the explicit exception for this stage. No other upload was performed.

## Data and ice

Pushed all 50 shared sources. Regenerated AuroraArchipelago with `tools/aurora_to_lua.py` from the Oct 13 09:08 holes.json (SHA256 c8bb4f4c73bcdd33b5520cf678c695a422d69864c29e016f4775930de5a89501), then rebuilt CourseAurora using the existing shared builder, preserving the previous imported blockout. Latest decoration moves and H4 ice data are included. AuroraLayout was unchanged.

Full recursive inspection finds **only `H4.felt.ice.decel_scale = 0.7`** as an explicit per-piece rolling field. No independent `drag_scale`, `roll_drag_scale`, or other drag scale exists in this JSON. The global metadata still lists ice default 0.35; it does not override the explicit piece value. Stage ag already propagates decel_scale through static felt, cup surfaces and mover felt, and BallController reads the supporting raycast part every frame. That existing path scales both Config.RollDecel and Config.RollDrag, plus the static/slope rest threshold. No speculative fields or duplicated physics constants were added. The source comment now documents the actual authored-field contract.

Config unchanged: RollDecel=0.5, RollDrag=0.25, EngineRollLoss=0.2. H4 effective nominal constant=0.35, drag coefficient=0.175/s, and script-applied constant after engine-loss compensation=0.15. Other pieces default to scale 1. Native Edit attributes confirm ice=0.7. `ice-fields.json` records every recursive decel/drag field and static propagation checks.

All **312 wall boxes** match holes.json within 0.000026 studs; all **103 felt pieces** match top planes and outer extents within 0.001 studs. No felt/wall geometry was moved to accommodate props. No new mesh collision or unauthorized primitive collision was added.

## Approved prop import

Merged only the FBXs listed by props_batch1_manifest.json and props_batch2_manifest.json, with one source empty per prop. Blender merge round-trip PASS: **74 props, 188 meshes, 65,088 triangles**, largest mesh **4,416 triangles** (`h13_hub_base__Snow`), no source/merged mesh/material/bounds discrepancies and no missing manifest items. Source FBX hashes are recorded. Reapplied source-FBX mesh dimensions/centers, importer 180-degree Y correction, manifest pivot/yaw, material/color/transparency and lights. Every render mesh has CanCollide/CanQuery/CanTouch=false, including H17 piers/bridge/span, H15 parapet and all corals. Moving models weld to the existing exact MoverRoot, preserving manifest pivots. Audit found zero missing/wrong welds or physical visual meshes.

Manifest revision evidence: **rev4** h17_ice_bridge, h15_ice_parapet, h09_coral_spit; **rev6** ten H7 corals and seven H8 small corals; **rev7** h08_giant_coral. Other 53 props have no revision number stated. Revisions come from structured coral revision fields and manifest notes, not filenames or assumptions. `import-specs.json` and `prop-placeholder-mapping.json` retain the evidence.

Two manifest pivots lag the latest holes.json decoration anchors: H10 bobsled hut [-7.5,0,-6] versus [-7.65,0,-6], and H11 fishing hut [-9,0,-30] versus [-9.127,0,-30.638]. Placement follows the explicitly requested manifests; neither was silently relocated. H15 waterfall world placement difference is intentional and explained in the manifest. These do not change felt or walls.

H17's imported span is a visual-only child of the existing toggle model, registered with ToggleVisual. Shared Movers uses the same server-time solid window to show it during solid and hide it otherwise; collision remains solely on the authored felt. It uses a hard visual on/off transition rather than adding an unrequested timing/fade profile. The schedule check includes mesh visibility and all three physical flags.

## Clearance method and limits

Ran the exact requested source checker with `--all`. Its summary is **296 raw findings**: dressing 222, flat 40, prop 12, envelope 9, exception 13; **12 real findings**, **20 coplanar findings** across all classes. These include intentionally overlapping skins and the checker-authorized exception class; raw count is not a count of gameplay obstructions.

Separately captured native Studio per-mesh bounds, transformed into hole coordinates, and compared them with actual built wall and felt bounds. Gap=0.15; felt head volume follows the checker (felt minus 0.4 through felt plus 8). A 0.0001-stud comparison tolerance avoids flagging float32 representations of exactly 0.15. The report lists every imported prop, individual meshes, obstacle IDs and signed separations. Bounds of material-joined/disconnected meshes contain empty space, so bounds violations and coplanar candidates do **not** alone prove triangle intersections or visible z-fighting. No zero-clearance claim is made from this conservative audit.

Blockout-mode CourseBuilder does not create dedicated Decor placeholders. Of 153 authored anchors, 67 map directly to the imported manifest props; the other 86 have no dedicated built anchor/prop to measure in this file. This is distinguished from **zero missing approved manifest items**. `anchor-coverage.json` records all 153 rather than pretending absent anchors were measured.

Evidence root: `playtests/stage-ai/`. It includes source-checker JSON, native bounds and audit, full anchor coverage, manifest input hashes/revisions, geometry comparisons, per-shot telemetry, summaries and console/schedule checks. Images and local place binaries remain uncommitted.

## Final built clearance findings

Built summary: **377 raw findings** (dressing 310, prop 46, exception 17, flat 4). **46 prop-class bounds violations** affect 13 props: h02_rookery_drift, h02_lintel_left, h02_lintel_mid, h02_lintel_right, h05_cliff_face_w, h05_cliff_face_e, h09_conch_entry, h10_bobsled_hut, h10_snow_walls_w, h11_fishing_hut, h11_floe_frame_e, h12_icebreaker, h15_lip_ice. Full mesh/obstacle pairs and separations are in built-clearance.json and built-clearance.md. The H10 hut has a measured 0.125-stud gap against the 0.15 requirement; the approved manifest placement is retained.

Four coplanar boundary candidates were detected: two H3 bridge boundaries against shore_rail4/green_rail8 and two H17 bridge boundaries against hidden rail skins. **Two visible candidates remain, both H3.** Screenshots do not establish animated z-fighting, and bounding boxes of disconnected meshes can enclose empty space. These are unresolved bounds/coplanarity findings, not claims of confirmed triangle intersections. The final DECO value is 46 (built prop-class bounds findings); the source checker separately reports 12 real findings.

## Runtime fixes and native verification

Hid 149 superseded render skins, including H17's underlying timed-felt rendering; its collider and all felt/wall geometry remain intact. Runtime inspection found CameraOcclusion was making visible decoration queryable. Added VisualQueryDisabled to all 188 imported meshes and made CameraOcclusion honor it. Final server and client audits both find all 188 visual meshes with CanCollide/CanQuery/CanTouch=false, zero bad meshes. The first diagnostic H17 schedule report is retained as h17-schedule-before-visual-hide.json; its query-flag failures were fixed before the final audit.

- Cupdrop: **54/54**, three on each of all 18 holes.
- Random shots: **144**, eight per hole.
- Slow movers: **36**, six each on H5/H11/H12/H13/H14/H17.
- H4 focused shots: **12**, zero moving after 15 seconds; rest times 3.199–5.716 seconds. These were biased shots on H4, with ten labeled ice and two lane in telemetry. Its eight ordinary random shots also had no issue flags.
- **Stuck 0, escapes 0, timeouts 0.** Two authored hazard returns. One pinned-ball nudge on H11 slow shot 5 successfully reached rest; this recovery is retained in the telemetry.
- Final H17 bridge schedule: **324 samples over 19.983 seconds, zero mismatches** across visibility, collision/query/touch, and hidden underlying felt.
- Server/client console: **zero errors or warnings**, both full sweep and final session.
- Final comparison: **all 50 Studio sources equal repository source**. Ten final hole screenshots and contact sheet were inspected; image evidence remains local and uncommitted.

## Local save and handoff

Saved with File > Save to File to `games/vr-mini-golf/playtest/playtest-aurora-v4.rbxl`, then quit Studio. Both the Studio process check and MCP studio inventory confirm it is closed. Saved-binary inspection finds all **188 expected mesh asset IDs**, none missing. v3 is unchanged.

Final v4: **1,089,884 bytes**, SHA256 `6c9b809b00ac747cb5cbf9a6027b9bbc0fbcea2e94636c057f8e6ffbec4b7a56`. See final-state.json and saved-file-inspection.json. No cloud place was opened/saved or published, and no git push was performed. Commit scope is source, stage-ai tools, text/JSON evidence, these notes and the status entry; no RBXL, FBX or images.
