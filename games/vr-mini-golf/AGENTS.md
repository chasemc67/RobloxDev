# VR Mini Golf — build runbook (AGENTS.md)

Every coding-agent build run (Codex, Claude Code) in `games/vr-mini-golf/` reads this first.
Owner: RobloxDevBot. Source: the Notion pages "Course Design" and "Course Design Retrospective"
(Roblox Games / VR Mini Golf, Oct 12 2026). Chase agreed to every retrospective suggestion.

## Places (source of truth: `places.json`, `ReplicatedStorage.Golf.Places`)
| Place | Place ID | Role (`PlaceRole` workspace attribute) |
|---|---|---|
| VR Mini Golf (lobby, start place) | 87725688219952 | `lobby` |
| Lantern Grove | 91438142503824 | `lantern_grove` |
| Sugarloaf Canyon | 124440050576723 | `sugarloaf_canyon` |
| Aurora Archipelago | 79649062523043 | `aurora_archipelago` |

- Universe 10769274294, owner MetavrseBuilder (user 1818120139). Builds on the Mini sign in as MetavrseBuilder.
- Playtesting on the PC uses MetavrsePlumber. Never edit the same place on both machines.
- Plumber's original place 135374506016678 is private and must not be touched.
- Aurora Archipelago is a course place in this experience (stage pub-au1); its lobby card and arch use LoadingAurora.

## Machine rules on the Mini
- **One Studio job and one open place at a time.** Before you start, check that no other stage job is running (`pgrep -fl "codex|claude"`, plus the stage logs). Never kill or edit a stage job you didn't start.
- Close Studio when the stage ends.
- The scripts are the same in all places, and `src/` is the source of truth. For each place in turn: open the one place, then
  `python3 tools/run_playtests.py push $(find src -name '*.luau')`, then `python3 tools/run_playtests.py smoke`, then Save and Publish, then close it. Then do the next place.
- Stages live in `logs/stages/` (gitignored). Each stage has `<x>-prompt.md`, a `run-<x>.sh` runner and a `<x>.log`, and the log ends in a `RESULT` line.

## Coding agent
- Use Codex for now, because Claude Code is nearly out for the week. Models: `gpt-6-astra` (default) or `gpt-6.1-sol`.
- Over SSH, always pipe in empty input: `codex exec -m gpt-6-astra "$(cat logs/stages/<x>-prompt.md)" </dev/null >> logs/stages/<x>.log 2>&1`.
- A run is one-shot and has no memory of earlier stages, so put everything it needs in the prompt file and this file.
- Batch notes until a pass finishes. Sending a new note mid-run drops earlier instructions.

## Assets
- Bots make assets on the Linux box in `/workspace/RobloxDev/assets/vr-minigolf/`. RobloxDevBot copies them **by hand** to the Mini's `~/src/RobloxDev/assets/vr-mini-golf/` before an import. Note that the folder names differ: `vr-minigolf` on the box, `vr-mini-golf` on the Mini.
- An automatic one-way sync (by MacBot) is proposed but not approved yet. Until Chase approves it, keep copying by hand.
- Every 3D handoff comes with FBX + `manifest.json` (CFrame, pivot, collision, triangle counts, materials) + `README.md`, plus a silhouette sheet (front, side and top views). Import from the manifest, and don't guess.
- Limits: under 20k triangles per mesh (backdrop zones about 15k). Glowing parts become Neon. Far backdrops use Persistent streaming and no collision.

## Physics values (from `src/ReplicatedStorage/Golf/Config.luau`; change them there, never copy them into other files)
- Scale: 1 stud = 0.3 m. `workspace.Gravity` = 32.7 (9.81 m/s²). The ball's radius is 0.08 and the cup depth is 0.35.
- Roll: RollDecel 0.5 studs/s², RollDrag 0.25/s, EngineRollLoss 0.2. StopSpeed 0.2 and RestTime 0.5 s. MaxBallSpeed 42, MaxRollTime 25 s, StrokeTimeout 20 s.
- Cup capture under 5.33 studs/s (1.6 m/s).
- WallElasticity 0.63, WallFriction 0.05, BumperElasticity 0.65. Skid after a hit: SpinKeep 0.5, SlideFriction 0.3.
- Safety: PinNudgeTime 1.5 s. AutoResetStill 3 s on holes with movers or teleports.
- Touch: TouchMaxSpeed 19.8 (a 60-stud putt), TouchPowerCurve 1.3. VR: VRHitMultiplier 1.7, VRTangentialTransfer 0.1.
- Exploring uses local gravity of 196.2 and JumpPower 38.
- Game Art Bot's simulator (`tools/sim.py`) must use these same values. Tell Game Art Bot when any of them changes.

## Order for a new course (blockout first)
1. **`holes.json`.** Game Art Bot's top-down layouts in studs, already stress-tested in the simulator (par spread, block rates within the target bands, no stuck spots).
2. **Blender blockout.** 3D Model Bot builds a rough model of the course from `holes.json`.
3. **Test place.** RobloxDevBot imports the blockout into a test place, with exact colliders generated from `holes.json` (`tools/holes_to_lua.py`). The felt and walls come from the data, not the meshes. Post one screenshot after the first import so 3D Model Bot can check the scale and lighting.
4. **Playtest Bot sweeps** on the test place: cup drops, stuck-ball sweeps and block rates against the simulator's bands. Fix the problems, then sweep again.
5. **Paintover.** Game Art Bot paints over the eye-height renders. Paint only gimmick holes and hero vistas.
6. **Full build.** Final meshes, props and far scenery (one pass with a quick approval, no repeated polishing).

## Build size
- Small builds: about 3 to 5 items per stage, never 10 or more.
- **Check at the start of every stage, before any work:** Studio is signed in as MetavrseBuilder, the Studio connection works (`tools/studio_mcp.py` / `run_playtests.py smoke` responds), exactly one place is open and it's the right one (check `PlaceRole`), and no other stage is running. If any check fails, stop and report it. Don't push on.
- Save and publish after each place, not only at the end.

## Publish and verify (before telling anyone)
1. Save and publish from Studio.
2. Open Version History for that place and read the **live version number**. A publish only counts once you have that number.
3. Save a local copy `playtest-<place>-v<N>.rbxl`, and copy it to the Linux box (`/workspace/RobloxDev/games/vr-mini-golf/`).
4. Commit `src/`, `tools/` and notes with a message like `vr-mini-golf: stage <x>, <what> (lobby vN, LG vN, SC vN)`, then push.
5. Hand off in one message: the live versions, the paths to the `.rbxl` copies and what to test. Put the paths on the board card too. Report to PM Bot.

## Testing
- **Each round tests mostly the newest course.** Older courses get a quick smoke check. Drop a check once it has passed twice in a row on an unchanged course. The deep pass on every course comes at the end, once all the courses are built.
- **At least 3 Playtest Bot rounds before Chase tests.** After each course milestone, ask Chase for a quick headset check.
- Testing should improve the holes. Use quick random sweeps, not scripted par shots.

### Checklist (RobloxDevBot, every build, before the handoff)
- [ ] Cup drop: a ball dropped into every cup counts (the cup bottom sits below the green).
- [ ] Stuck-ball sweep: random shots plus slow rollers on every hole. No ball stops somewhere unplayable or leaves the course.
- [ ] Collision probes: ray sweeps at obstacle colliders find no gaps.
- [ ] Terrain: no terrain above the felt or inside a cup.
- [ ] Clearances from `holes.json` are met (for example, at least 2.2 studs around each Sugarloaf cup, and 0.06 to 0.15 studs around moving Aurora obstacles).
- [ ] No script errors in Play.
- [ ] Flow: menu, scorecard, leaderboard, portals, Back to Lobby (teleports only work in the live game).
- [ ] Saved and published, live version numbers confirmed in Version History, `.rbxl` copies on the box.

### Playtest Bot's round (for reference)
Sink checks, stuck-ball sweeps, difficulty bands against the simulator, the VR view (ball and club head visible, the wrist card readable, nothing blocking the view), flow, script errors and frame rate. It reports numbered P1 to P3 findings with evidence and an owner.

## Don't
- Make fly-through videos or concept art for every hole unless Chase asks.
- Make more than 3 options for a question.
- Run two Studio jobs, or open a second place.
- Announce a version you haven't seen in Version History.
- Commit `.rbxl` files (they're gitignored), and don't commit large binaries until Git LFS is set up (see below).

## Binaries and git
- `.rbxl`/`.rbxlx`, `logs/`, the reference videos and the concept PNGs are gitignored.
- As of Oct 12 2026, git tracks only 5 FBX files. About 680 FBX, 38 `.blend` and about 1,900 PNG/JPG files under `assets/vr-mini-golf/` are untracked, about 2.1 GB, and they exist only on the Mini and the box.
- Git LFS isn't installed on the Mini. Setting up LFS needs Chase's decision on a GitHub LFS data plan. Until then, don't `git add` asset binaries in bulk.

## Our lobby VR controls (Chase, Oct 12, 2026; stages ad/ae)
- The VR Mini Golf lobby uses OUR VR controls (`VRControls`, wrist card, VR putter, sticks, and B/Y scorecard gear) under both real VR and SimulateVR. Chase decided this on Oct 12, 2026 (stages ad/ae). Desktop keeps LobbyRoam.

## Visual separation (stage zf1, all course builders)
- Apply `VisualSeparation.Apply(course)` after geometry, imported visuals, hints and decals. All visible parts have minimum dimension **0.2 studs**. Stacked/parallel exposed visual layers must have **at least 0.05 studs** normal separation; use **0.08 studs by default** for distance stability.
- Keep gameplay collider CFrames, sizes, collision/query/touch flags and physical properties exactly unchanged. Thicken, inset or offset noncolliding visuals; when a visible collider needs visual changes, preserve the original hidden collider and use an untagged, noncolliding visual copy. Ball roll heights must not change.
- **Felt skins (stage fx1):** a felt visual is inset 0.08 only on its outer edges. Where another visible playing surface (felt, CupPlate) continues at the same height, the edge stays on the collider joint (0.001 setback, so float rounding never makes a coplanar overlap) unless a rail/cap block hides that joint. Overlapping felt is trimmed to meet, not 0.08 apart. CSG felt (cup cut-outs) is never resized. Cup pieces carry the same felt textures as the felt they were cut from (`CourseBuilder.MatchCupFelt`, run by `ApplyVisualSeparation`). Seam audit: `tools/fx1_stage.py seams` (0 interior seams expected).
- Retain every placeholder until explicitly replaced by its owning art bot. Do not delete placeholders to pass a visual audit.
- Audit every hole after the rule runs. Report raw OBB scan counts honestly: imported mesh/CSG/curved bounding boxes are not real polygon faces, and opposing buried block interfaces require separate justification instead of damaging connected geometry to remove conservative hits. Any unresolved **exposed** coplanar face requires a source fix before publishing.
