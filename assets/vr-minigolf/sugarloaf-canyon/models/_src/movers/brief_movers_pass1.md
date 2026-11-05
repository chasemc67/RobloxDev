# SRV-132 (partial) brief: Sugarloaf Canyon movers, H6 + H11 ONLY

Read first: /home/box/agent-data/workflows/roblox-minigolf-3d-modeling-2/SKILL.md (follow it).
Course dir D=/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/. Inputs: D/holes.json (SOURCE OF TRUTH: holes[5] h06 moving_parts sluice_gate; holes[10] h11 moving_parts lock_gate + teleports lock_lift ride), D/course.md, D/h06-notes.md, D/h11-notes.md, D/h06-layout.png, D/h11-layout.png, D/playtest-log.md, /workspace/writerbot/vr-minigolf-post/playtest-bot/sugarloaf-layout-review/review.md.
Reference library: D/models/_src/sclib.py + lglib.py (import them, DO NOT edit them) and lantern-grove/models/_src (movers there).

CONCURRENCY: another job owns D/models/ world pieces. Write ONLY inside D/models/_src/movers/ (generators, registry_movers.py, build script, fitcheck, logs, PROGRESS.md), D/models/fbx/movers/, D/models/previews/movers/. Do not modify any other file. manifest.json: at the very end, re-read it, append/replace only a top-level key "movers" (list of entries), write to a temp file and os.replace atomically; also write the same content to D/models/_src/movers/movers_manifest.json.
Do NOT touch H9, H14, H17 movers.

Build (Blender 4.5 headless on this box: `blender -b -P ...`), 1 unit = 1 stud, Z-up, FBX forward -Z up Y scale 1, embedded textures:
1. h06_sluice_gate (MOVING): timber board 7 long x 1.0 tall x 0.6 thick, pointed 45deg ends (match blockers), peppermint red/cream bands, iron straps. Pivot = gate centre at offset 0 = hole-local [0,0,-28] bottom-centre on felt. Motion: slide along +X, offset in [-7,0], 3 studs/s, ping-pong, dwell 1.2 s at 0 and 2.0 s at -7, phase 0, period 7.8667 s.
2. h06_sluice_frame (STATIC base): posts at x=+-3.6 (0.6x9x0.6), beam 8 above felt, hand-wheel winch on west wall, wall pocket hint west. No red/cream bands (statics must not use bands).
3. h11_lock_gate (MOVING): one leaf 3.6 wide x 1.2 tall x 0.5 thick, red/cream bands. Pivot hole-local [0,0,-21.25] (bottom centre at offset 0). Slide along +Y, range [-1.3,0], 2 studs/s, dwell 5.5 s at -1.3, 2.8 s at 0, phase -1.3, period 9.6.
4. h11_lock_lift (MOVING): timber raft-deck platform 3.2 x 4.0 (felt piece 'lock' centre [0,0,-23]) top flush with felt at rest, red/cream band trim. Pivot at platform top centre [0,0,-23]. Motion: rises 4.0 at 2 studs/s, tilts 4deg north at top (state tilt axis/hinge edge), returns in 1.5 s, cycle 9.6 synced to gate. Keep it thin so it doesn't intersect felt/chamber.
5. h11_lock_chamber (STATIC base): peppermint concrete walls (4 tall) around lock, brass bollards, gate slot, winch posts at x=+-2.6 z=-21.25, signal lamp at [0,5,-25.4] with separate red & green lamp meshes (Neon) so Studio can toggle.
Rules: moving parts separate FBX/meshes from bases; one mesh per material (<piece>__<Material>); < 20k tris per mesh; decoration only (CanCollide off). Coordinates in manifest in hole-local Roblox studs (Roblox x,y,z = Blender x,z,-y), plus world = hole world_offset (yaw 0).

Fitcheck (fitcheck_movers.py): sweep full motion of each mover in fine steps (<=0.02 stud / 0.25deg) against holes.json felt top (y) and walls/rails boxes and the static bases; report min clearance and where (offset/time + location) per mover, and also check the visual mesh covers the gameplay blockers (state any visual-vs-blocker mismatch). Flag clearance < 0.05. Statics also checked vs rails/felt/cup/tee. Save passing output as fitcheck_movers_pass1_validated.txt. Iterate until ALL PASS.
Previews: Workbench eye (5 studs w/ capsule) + 3/4 per prop into D/models/previews/movers/, plus contact_sheet.png. (Final Cycles renders happen later on the PC; just write a render script render_pc.py that renders given blend/fbx with Cycles OptiX.)
Log each step with timestamp to D/models/_src/movers/PROGRESS.md. Finish with movers_pass1_summary.md: FBX paths, pivots (hole-local + world), axes, motion formulas (Lua-ready), tris and MeshPart counts, lights, min clearances, caveats.
