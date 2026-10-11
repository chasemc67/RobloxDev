# Lantern Grove v1: build report (stages a-d)

Place 87725688219952 (universe 10769274294, owner MetavrseBuilder). Audience: Friends and Playtesters (unchanged
throughout). All times Pacific, 2026-10-10.

## Versions

| Version | Published | What |
|---|---|---|
| v23 | 00:02 | Round 1, flat greybox: 9 holes from holes.json on a flat plane |
| v43 | 13:52 | Round 1 for Playtest Bot: world terrain/water/paths/hollow tree, team fixes (stage b) |
| (stage c) | saved 16:50, not published | Spec v2 re-import, props pass 6, world pieces |
| **v79** | **17:11** | **Final (stage d): movement, Explore mode, round-1 UI fixes, everything from stage c** |

## Per-hole status (final build)

Random-shot sweep, stage d: 20 random shots per hole (any direction, 20-100% power, 1 in 3 from the tee), 180 shots.
Stuck = no movement for over 3 s away from the cup. On holes with moving parts or teleports, a ball stuck 3 s
auto-resets to the stroke start; those resets are counted separately. Timeouts = stroke still moving after 20 s.

| Hole | Built | Shots | Escapes | Stuck | Auto-resets | Timeouts | Nudges | Hazards (designed) | Holed | Console |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 Acorn Ledge | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 Toadstool Row | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 4 Spore Spinner | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 Rootbridge Crossing | yes | 20 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 |
| 6 Mill Wheel Run | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 Cascade Steps | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 Firefly Hollow | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 Heart of the Grove | yes | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Totals: 180 shots, 0 escapes, 0 stuck, 0 auto-resets, 0 stroke timeouts, 0 nudges, 0 console errors/warnings. All 9 holes built; all movers running. Hazards are the designed H5 stream misses (the ball returns to the bridge entry).

Movers (all server physics, phase-locked to server time; `movers` scenario, stage c): H4 padded spinner, H6 mill
wheel, H7 sliding log (stops 0.5 short of the rails), H8 root door (slides into its pockets), H9 root gate and
lantern pendulum (max error 1.1 deg). Teleports: H8 firefly ring, H9 Lantern Knot (exit FX).

Console: 0 errors / 0 warnings in the sweep, `progress` (all 9 holes in a row, simulated VR) and the normal-play
smoke tests (desktop and iPhone emulation).

## Stage d (this stage)

- **Movement**
  - Holing out shows the score, then fades to black (camera ColorCorrection, so it also covers a headset) and puts
    you on the next tee. Measured on desktop: black at ~3.4 s after the hole-out, hole switches while black, back in
    ~0.6 s later.
  - VR: trigger warps you to your ball (Walkabout style); the `progress` run checks the rig lands 1.5 studs from the
    ball on every tee.
  - Desktop/phone: the camera always follows your ball and your avatar stands beside it, so there's nothing to
    walk to.
- **Explore mode** (Chase, 13:37): an orange **Explore** button on the HUD.
  - No ball, no score: the server parks your ball where it was, or at the stroke start if it was rolling.
  - Walk/run/jump with the normal controls (touch thumbstick + jump button), with normal-feeling gravity for the
    character only. **Sprint** toggle (Shift), **Fly** toggle (F, Up/Down buttons).
  - **Teleport** menu: H1-H9 tee views plus Welcome Plaza, Grand Falls, Hollow Tree, Lantern Mere and Lookout Rock.
  - Falling under the world respawns you on the nearest walkway. Invisible walls (players only) sit 12 studs inside
    the terrain edge.
  - **Back to golf** puts the ball back unchanged.
  - Per player (other rounds untouched; players never collide with balls). Tested on the iPhone 17 Pro emulator.
- **Playtest Bot round 1 (v43) fixes**
  1. The Roblox player list is hidden during play, so it no longer covers Reset Ball. The scorecard lists every
     player.
  2. Your own avatar is fully hidden in the putting camera (re-applied every frame).
  3. The hole/par/strokes panel moves below the Roblox chat area:
     - desktop: always, because message notices pop up there;
     - phone: while chat is open.
  4. Explore button (above).
  5. Narrow screens:
     - the help line wraps onto two lines;
     - the scorecard fits the screen, with shorter rows and a scrolling player list.
  6. Plants out of a 1-stud strip along the rails: Terrain Grass grows tall blades that poked through the rails
     and felt (H1). `WorldBuilder.ClearGrassNearRails` turns Grass into LeafyGrass (no blades) within 1 stud
     (+ half a voxel) of every rail, on all 9 holes. It's part of the carve step, so a re-import keeps it. No
     decor props were within 1 stud of a rail.
- **Self-review**: top-down, tee view and two follow-cam frames per hole. Nothing broken. The follow cam
  sometimes looks through a lantern prop (cosmetic).

## Team fixes applied (all stages)
- Playtest Bot pre-round (12:41):
  - H7 log stops 0.5 short of each rail, plus an unstick nudge after 1.5 s of contact.
  - Cup capture 5.33 studs/s (1.6 m/s), verified.
  - H9 Lantern Knot built at (6.5, 1.0, -23.0).
  - Teleport exit FX ~0.3 s; the H8 exit can't overshoot.
  - H8 door and H9 gate push the ball aside.
  - 3 s auto-reset on H4/H6/H7/H8/H9.
- Game Art Bot spec v2 (13:39), re-imported in one regenerate step:
  - H4 skill route + slower padded spinner;
  - H5 wider bridge, and a miss returns to the bridge entry;
  - H8 bigger ring + shorter route + alcove bank;
  - H9 spinner -> lantern pendulum;
  - flags and signs.
- 3D Model Bot pass 6 props + all world pieces (stage c).
- Playtest Bot round 1 (v43) UI items 1-5 and the rail grass strip (stage d, above).

## Known gaps
- **VR**: no headset test of this build. Club grip axis, rig comfort and hit strength still need a Quest. Explore
  is off in VR (the HUD button is desktop/phone only).
- **Terrain grass**: the meadow's Terrain grass blades are very tall next to a life-size ball and character. They
  now stay off the rails and felt, but in Explore they can fill the camera in the meadows. Art call for Game Art
  Bot: shorter grass / LeafyGrass in play areas.
- **Explore**:
  - Fly keeps normal collisions (no noclip). You can climb over anything but not pass through the tree walls;
    the door is open.
  - Golf walls don't block walking characters (by design, so they never shove balls).
- **Lighting.Technology**: not verified. Studio's Properties panel doesn't list it (even when filtered), and MCP
  reads are blocked (RobloxScript capability). `WorldBuilder.ApplyLighting` sets Future in a pcall, which may fail
  silently. Someone with a Studio that shows the property should check it.
- **Chat**: on desktop the info panel always sits below the chat area, even with chat closed. Phones only shift
  it while chat is open.
- **Phone tuning**: `TouchMaxSpeed`/`TouchPowerCurve` haven't been retuned for the faster felt (status.md TODO).
- **Lights**: 157 lights (0 shadows) are the first thing to cut if phones struggle.

## Images
- Per hole, stage d:
  - `stage-d/shots/hole01..09.png` (tee view, HUD on);
  - `topdown_h01..09.png`;
  - `follow_h01..09_a/b.png` (chase cam).
- UI, stage d (`stage-d/ui/`):
  - `desktop_*.png`, `phone_*.png`;
  - golf HUD, scorecard, Explore, teleport menu, fly, Grand Falls view, H5 tee view, back to golf.
- World: `overview.png`, `overview_aerial.png`, `stage-c/shots/` (h9_heart, h9_pendulum, h2_chutes, h8_alcove).
- Earlier rounds: `round1-greybox/`, `iter1-shots/`, `hole01..09.png` (stage b/c).

## Data
- Sweep:
  - `stage-d/sweep-d/` (H1-H5) and `stage-d/sweep-d2/` (H6-H9): summary.md, results.json, jsonl.
- Other runs:
  - progression: `stage-d/progress/`;
  - earlier sweeps: `sweep-b/`, `stage-c/sweep-c-final/`.

## Playtest Bot instructions
Studio must be in Edit mode on place 87725688219952, with the Studio MCP enabled. Then, from
`~/src/RobloxDev/games/vr-mini-golf`:
```bash
# random-shot sweep, 20 per hole, two batches (~10 min each)
python3 tools/run_playtests.py holes 1 2 3 4 5 --opts '{"parts":"fuzz","fuzz":20}' --out playtests/<date>/sweep
python3 tools/run_playtests.py holes 6 7 8 9   --opts '{"parts":"fuzz","fuzz":20}' --out playtests/<date>/sweep-b
# normal play + Explore round trip, desktop and phone emulation (problems must be empty)
python3 tools/run_playtests.py smoke
python3 tools/run_playtests.py smoke --device iphone_17_pro
# HUD/Explore screenshots
python3 tools/ui_shots.py --device iphone_17_pro --out playtests/<date>/ui
```
- What to flag per hole is in `playtesting.md` ("Playtest Bot: random-shot sweep per hole"):
  - stuck (with the auto-reset count);
  - escapes;
  - console errors.
- How to play (desktop, phone, VR, Explore): `playtesting.md`, "How to play".
- In the live game: play hole 1, hole out (watch the fade to the next tee), then press **Explore**:
  1. walk, sprint, fly;
  2. teleport to H5 and Grand Falls;
  3. jump off a cliff edge;
  4. press **Back to golf**.

  Check the ball and stroke count came back unchanged, and that a second player's round wasn't affected.
