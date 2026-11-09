---
name: roblox-minigolf-playtesting
description: QA playtesting procedure for Roblox mini golf courses (VR, desktop and phone). Use when asked to playtest or regression-check a mini golf place from a handed-off local .rbxl copy, to run a blockout gate or full-round check, to compare in-engine results with a course simulator, or to review a hole layout for playability. Covers safe local copies, machine and session ownership, the no-save/no-publish rule, check lists, evidence tiers, bug reports and retests. QA only, not fixes. Not for building, publishing or tuning courses.
---

# Roblox mini golf playtesting (QA)

The job is to **find and report problems with evidence**. Fixes belong to the owner of the layout, build or tool. A playtest never changes the game.

Related:
- [`roblox-studio-mcp`](../roblox-studio-mcp/SKILL.md): how to drive Studio. [`roblox-dev-workflow`](../roblox-dev-workflow/SKILL.md): the overall operating model.
- VR Mini Golf specifics: the [build runbook](../../../games/vr-mini-golf/AGENTS.md) (course order, Testing section) and the [harness guide](../../../games/vr-mini-golf/playtesting.md) (test mode, scenarios, stuck/escape definitions, `compare`).
- [`roblox-publishing`](../roblox-publishing/SKILL.md) is the build owner's job, never part of a playtest.
- A difficulty-simulator skill is being written separately. If `.agents/skills/` has one, use it for simulator runs and follow its limits. This skill doesn't implement or validate a simulator.
- Report layout: [references/report-template.md](references/report-template.md).

## 1. Set the round scope first
Write the scope at the top of the report. It changes per round, so don't copy it forward without checking:
- **Places and versions** under test, from the build handoff.
- **Focus**: for example the newest course in depth with older courses as a quick smoke check, or only the world and scenery, or only flow. A narrow focus like "world only" applies to this round, not to later ones.
- **Devices and modes**: desktop, phone emulator, SimulateVR, live server.
- **Out of scope**, and who said so.

Defaults from the repo (`games/vr-mini-golf/AGENTS.md`): test mostly the newest course. Older courses get a quick regression check unless they changed. Drop a check after it passes twice on an unchanged course. Prefer quick random sweeps to scripted par shots. If the handoff and these defaults disagree, follow the handoff and note it.

## 2. Before touching any machine
1. **Ownership.** Use only a machine and session you've been given for this round. If Studio, the Roblox player or an agent job is already running and you don't know whose it is, **don't take it over, close it or kill it**. Stop and ask. Run one Studio job at a time per machine.
2. **Accounts.** If the test account is already in use elsewhere (for example someone playing in the headset), wait and ask. Don't retry into their session.
3. **Safe copy.** Test a local `.rbxl` copy whose name or note gives the place and its version, as handed off (for example `playtest-<place>-v<N>.rbxl`). Make your own working copy so the handed-off file stays clean. Never open the live place for testing. If there's no copy or no version, ask the build owner for one. Don't make it yourself from the live place.
4. **Record version evidence** (section 6) before running anything.

## 3. Read-only rules (during the whole round)
- **Never** save, publish, Save to Roblox, or accept an agreement pop-up.
- **Never** change source or resync it: no edits to `src/`, no harness `push`/`export`, no builders that write course data into the place (`holes_to_lua`, `world_to_lua`, `props_to_lua`, `WorldBuilder`, `PropsBuilder` and the like). If a check needs one of these, it's out of scope. Report it.
- Temporary test-mode attributes and markers are fine on the local copy. Clear them afterwards and leave Studio in Edit mode.
- If you find a bug, report it. Don't patch it, even if the fix is one line.

## 4. Checks
Pick from these per the scope. The course's harness guide has the exact commands and pass rules.

### Blockout gate (rough geometry, exact colliders)
Cheap checks while layout fixes still only touch `holes.json`:
1. **Cup drop**: a ball dropped into every cup counts.
2. **Stuck / escape sweep**: random shots plus slow rollers per hole, seeded. Flag balls that stop somewhere unplayable, time out, leave the course or need the safety nudge or auto-reset. Count designed hazards separately from escapes.
3. **Clearances and collider gaps** against the values in that course's `holes.json` or notes. They differ per course.
4. **Difficulty vs simulator**, only if the round includes difficulty (see section 5).
5. Console errors and warnings.

### Full round (final build) adds
6. **VR view (SimulateVR)**: ball and club head visible, wrist card readable on both hands, menus and pointer work, props don't block the view.
7. Club orientation and thumbstick controls in both hands.
8. Camera wall and occlusion probes from the desktop camera and the VR head, from a saved spot list so retests reuse the same spots.
9. Readability: slopes look downhill, props are lit, decorations are to scale and off the line.
10. **Flow**: menu, scorecard, settings, portals, Back to Lobby, scores carrying over. Teleports, portals and saved bests need a live server, so they're the only live checks.
11. **Health**: 0 script errors, frame rate on the heaviest holes, desktop and phone emulator.

### Layout review (no Studio)
Fair par and a clear path, room for the camera, expected mover blocking, readable slopes, decorations off the line. Numbered list with owners.

## 5. Evidence tiers: say which one every number comes from
| Tier | What it is | It shows |
|---|---|---|
| **Engine** | Real Roblox physics in a Studio play session (scripted shots through the game's own hit code) | How the build behaves in Studio |
| **Probe** | Raycasts, clearance scans, camera probes, single-shot debug probes, static audits | Geometry facts, not play |
| **Manual** | A person or input automation actually playing | Feel, controls and flow, in that mode only |
| **Simulator** | An offline model of the course | What a model predicts |

When you compare engine results with a simulator, label all three:
- **Model**: which simulator and its version, and whether its physics values match the game's `Config`.
- **Policy**: aimed intended line, random sweep, or AI golfer at a skill level. A random-sweep contact rate isn't the same measure as an aimed block rate (see `games/vr-mini-golf/playtests/stage-s/h9-variance.md`).
- **Sampling**: number of shots, seeds, mover phases. Small samples swing a lot (20 shots can move a rate by about 20 points), so give `n/N`, not just a percentage.

Use the target band and its definition from that course's simulator output or notes. There's no universal band or clearance. A miss is a finding for the layout owner, not proof the engine is wrong.

**Par:** authored par (from `holes.json` / the design) and measured results (for example strokes for a given policy) are separate. Report a measured recommendation next to the authored par with its policy and `n`. Never present it as the new par.

## 6. Version evidence
Each report states: place and role, the version from the handoff (and whether it was seen in Version History), the local copy's file name, the machine and mode, the harness or tool revision if known, and seeds and options. A finding without a version can't be retested.

## 7. Honest coverage
Always list what wasn't tested and why. Common gaps:
- **SimulateVR is not a headset**: grip axis, swing feel, haptics, tracking noise, floor calibration and comfort still need a real headset check.
- **Phone emulator is not a phone**: touch feel, performance and screen safe areas on real devices are untested.
- **Studio is not the live game**: teleports, DataStore and saved bests, multiple players, network lag.
- Anything skipped because of access, time or scope.

## 8. Findings and severity
One numbered finding per problem:
- **P1**: blocks play or progress, loses score, ball stuck with no reset, escape, crash, script error in normal play.
- **P2**: clearly wrong but playable (bad camera spot, unreadable UI, off-target difficulty).
- **P3**: polish.

Each finding has: exact repro (place and version, hole, spot in hole-local coordinates, aim and speed or seed, mover phase, device and mode, steps), expected vs actual, how often (`k/n`), evidence tier, a screenshot path or numbers, and an **owner** (build owner for gameplay and Studio, model owner for geometry, layout owner for layouts and visuals, machine owner for broken tools). List passes briefly.

Keep raw logs, screenshots and recordings out of git (see the repo `AGENTS.md`, "What to commit"). Link to where they're stored. Give Chase only a short summary of what needs him. Details go to the team.

## 9. Retest and regression
- Rerun the **same** checks with the same seeds, options, sample sizes and spot lists, so the numbers can be compared. Use the harness's `compare` if there is one.
- Report before and after side by side with both versions. Mark each finding fixed, still there, or new.
- If the method changed between runs (harness, sampling, policy), say so. Don't call it a regression or a fix on that alone.

## Source and status
Adapted from the Playtest Bot's current `roblox-minigolf-playtesting` skill (attached to the request for this PR). **That copy stays the source of truth until Chase accepts this one and the merge is verified.** Moving over is a separate step. Left out on purpose: machine access commands, accounts and IDs, harness flags, transient versions and paths, and course-specific thresholds. Those belong to the handoff, the per-game runbook or the course notes.
