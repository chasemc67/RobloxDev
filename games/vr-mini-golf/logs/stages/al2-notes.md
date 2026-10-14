# Stage al2 — Sugarloaf H9/H14 hint decals (local)

Result: **PASS**, using the route-relative direction interpretation documented below. Saved to the same local fix2 path; Studio is closed.

## Local boundary and upload

Read game AGENTS.md, ag/ah/af/af-portability/al notes and al-inputs/placeholders.md. Preflight found no competing stage job. Studio welcome screenshot confirmed MetavrseBuilder. Opened only `playtest/playtest-sc-fix2.rbxl` through File > Open from File. PlaceId/GameId 0, no NetworkClient, role sugarloaf_canyon. Input SHA256 `b136231f22aa80bf80ca0df0eeb4d672155658e7cd44bbeb11a6f6ea1ac1c8c1`.

The initial import queue was too narrow to expose its controls. Studio's Reset Layout restart left a process with no accessible native window; that task-owned process was terminated before relaunching. Reconfirmed MetavrseBuilder and reopened the exact local file. The input hash remained unchanged. No assets were uploaded before this recovery. Panel layout is now Studio's reset layout.

Selected exactly the five supplied PNGs (excluded decal-sheet.png) in Studio's Import dialog. Import Queue Creator was `Me`, and Start Import completed all five with green success indicators. Asset Manager and Studio MCP user-image inventory independently identified owner MetavrseBuilder, user 1818120139. All five final ContentProvider preloads returned Success. No cloud place was opened/saved, no place was created or published, no protected place was touched, and no git push occurred. The five explicitly approved image uploads are the only cloud asset creation in this stage.

| PNG | Image asset ID |
|---|---|
| h09_sign_bypass.png | 107264623944550 |
| h14_safe_bank_sign.png | 131067632603421 |
| h09_felt_arrow_bypass.png | 123495746026639 |
| h14_safe_bank_arrow.png | 82085948994874 |
| h14_timing_arrow.png | 139894260913924 |

`tools/stage_al2_assets.json` includes creator, IDs, PNG dimensions and source hashes.

## Persistent placement

New `ServerStorage.SugarloafHints` is called by `SugarloafOverrides.Apply`. All placements derive from the existing named decoration anchors. Two 1.8 × 3.2 portrait boards carry Front decals at the former board centers; their posts sit behind the printed faces. Neither target contained a real imported sign mesh: both were primitive SignBoard/SignPost placeholders. Replaced those four placeholder parts and the six old arrow strokes: **10 parts removed**. Unrelated placeholders and all imported meshes remain.

The three 1.4 × 2 felt images use 0.01-stud-thick transparent parts, with top surfaces measured 0.029994–0.030009 studs above native felt ray hits. Every new visual has CanCollide/CanQuery/CanTouch false, no shadow, and VisualQueryDisabled=true. All 705 existing physical colliders retain identical poses, sizes and physical properties. Config and H15 friction TEST remain unchanged.

Idempotence and a temporary H9/H14 reference rebuild in the same local DataModel preserve all five images, absent placeholders, carrier directions and lift. The reference folder was destroyed. Only SugarloafHints and SugarloafOverrides were pushed; unrelated newer shared sources were not pushed into fix2.

## Direction interpretation and visual checks

The written headings need a coordinate-frame distinction. H9's authored −Z bypass runs along **world +X** after its −90° course rotation. Using literal world −Z pointed into the pump house. H14's west/left rail is **world +X** after its 180° rotation; literal world southwest pointed to the opposite rail. A clarification was offered; absent a response, placement follows the actual bypass and printed left-bank route cues. The source note's H14 word “southwest” conflicts with its north=−Z map and forward west-bank route; the final safe-bank arrow points forward-left toward that rail, rather than backward or toward the opposite rail.

| Arrow | Hole-local image top | Studio-world image top |
|---|---|---|
| H9 bypass | (0,0,−1) | (+1,0,0) |
| H14 safe bank | (−1,0,−1), normalized | (+0.707,0,+0.707) |
| H14 timing | (0,0,−1) | (0,0,+1), toward ore bucket |

Roblox's Top-face Decal image top maps to local +Z, opposite Part.LookVector; the carrier frames compensate for that. Early visual QA also caught a post protruding through each sign, corrected by moving each post behind its board. The first static audit incorrectly looked for a GolfSurface attribute; corrected to the actual tag before successful native ray verification.

Seven final screenshots in `playtests/stage-al2/screens/`: five individual approach views plus H9/H14 tee views. Inspected all images: printed faces unobscured, arrow labels readable on approach, no visible z-fighting. H9's bypass arrow is around the pump house and intentionally not visible from the tee. This is desktop Studio visual verification, not headset acceptance. Images remain local and uncommitted.

## Tests and handoff

The first sweep passed H9/H14 cupdrop 3/3 and random 8/8 each, no stuck, escapes or timeouts, zero client/server console warnings/errors. Those results are retained separately under `sweep-world-heading/`; they preceded the route-relative orientation correction. Final orientation was rechecked with the same requested test counts and explicit `course=sugarloaf_canyon`, seed 20261014. Completed-shot records, not placement attempts, are counted.

Final sweep: H9 **3/3 cups + 8/8 completed random shots**, H14 **3/3 cups + 8/8 completed random shots**. Total **6/6 cups, 16 random**, stuck 0, escapes 0, native/harness timeouts 0, zero client/server console warnings/errors. All 16 shots rested normally. Final source equality: both changed modules match the repo. TestMode=false and SimulateVR=false. Final physical comparison: all 705 colliders unchanged.

File > Save to File visibly confirmed the exact fix2 path at 17:47 PT; then Studio quit. MCP returned zero open studios and pgrep found no RobloxStudio process. Output size 3501958 bytes; SHA256 `138ae94d5ed7c6dacb8f68f17a41fed1094f3af4fbefb5c5e58f0837b8197977`. Evidence: `verification-summary.json`, `audit.json`, `runtime-flags.json`, `console.json`, `final-file.json`, the final `sweep/` JSON/JSONL, and local-only screenshots.

Source, tools, notes and text/JSON evidence are committed locally with the requested stage-al2 message. No RBXL, FBX, PNG or JPEG is committed. Publication remains gated on Playtest Bot's clean sweep; this stage does not resolve the pre-existing H15 friction-test findings.
