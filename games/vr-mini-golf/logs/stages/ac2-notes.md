# Stage ac2 — Aurora blockout, local only

## Scope and preflight

- Read `AGENTS.md` and `logs/stages/ac-notes.md` in the game directory before Studio work. No competing stage job matched the requested process check.
- Launched Studio from closed state. Screenshot showed `Welcome, MetavrseBuilder`.
- Opened Lantern Grove through its Creator Hub page. Closed the separate empty Studio start-page process once the cloud place loaded; only one place was open. MCP verified place 91438142503824, role `lantern_grove`, Edit mode.
- Nothing was published. No cloud place scripts/instances were edited. No new Roblox place was created. Place 135374506016678 was not opened or touched. Download a Copy was the only authorized cloud-save action. No git push.

## Cloud copies

- Lantern Grove had existing unpublished v10 (7:52 PM) before this run. Studio Version History showed v9 Published. Download a Copy at 8:32 PM created unpublished v11; re-read Version History and confirmed v9 remained Published. Saved `playtest-lg-v11.rbxl` (3,391,455 bytes).
- Closed Lantern Grove before opening Sugarloaf Canyon. MCP verified place 124440050576723, role `sugarloaf_canyon`, v19. Version History showed v19 Published. Download a Copy at 8:34 PM created unpublished v20; v19 retained its Published badge. Saved `playtest-sc-v20.rbxl`.
- Closed Sugarloaf and verified MCP had no open studios before local work. Checksums and sizes are in `playtests/stage-ac2/cloud-copies.json`.

## Local Aurora implementation

- Opened the specified `playtest-sc-v4.rbxl` via File > Open from File. Immediately used File > Save to File As to create `aurora-test.rbxl`. Verified PlaceId 0 and no NetworkClient before changes. MCP kept the stale display name `playtest-sc-v4.rbxl` after Save As; the UI showed the actual `aurora-test.rbxl` path. Used the sole open Studio instead of the stale name filter.
- Pushed all current `src/**/*.luau`. Added Aurora mapping as `aurora_archipelago` -> `CourseAurora`, with place ID 0 (no teleport destination or cloud place). Added Aurora spec and test-lane support to GolfTestServer.
- `tools/aurora_to_lua.py` reuses `holes_to_lua.convert/to_lua` and generates `AuroraArchipelago.luau` and `AuroraLayout.luau`. The source JSON world placements are retained with zero added offset.
- Removed CourseSugarloaf with its active Kit/Decor and cleared Terrain. Built all 18 Aurora holes through CourseBuilder, with generated felt/walls, cups using Config.CupDepth, tees, and 42 exact mover blocker boxes. The blockout option uses exact-box rail visuals and bypasses Lantern Grove's slide-range clamp; the ice floe retains the spec range [-7, 0].
- Movers on H5, H11, H12, H13, H14 use the existing constraint driver. **H17 aurora_span remains static/solid** because the existing driver does not support the collision-toggle profile. Its model records `StaticReason`; its six slow rollers test the static fallback only.
- CourseBuilder assigns AutoResetStill from Config on mover/teleport holes. Local rebuild and read-only geometry audit tools are included.
- Imported `blockout_aurora.fbx` with **Upload to Roblox unchecked**, scene position enabled and anchored. No cloud upload was requested. Manifest normalization sets each mesh to its world bounding box and corrects the importer's baked 180-degree Y rotation. Root is `CourseAurora.Blockout` at the origin.
- All 135 imported parts have CanCollide/CanQuery/CanTouch false. Hidden: sweep volumes, clearance rings, player guards, plus duplicate felt and mover skins so the cut cups and animated data visuals remain visible. No manifest mesh names were missing. Local mesh portability to another machine is unverified.

## Tests and limits

- Cupdrop: **54/54** (three gentle putts from 1.4 studs on each of 18 holes). Final cupdrop Play had zero server/client warnings or errors. Initial harness startup failed because its test lane only recognized the previous course folders; fixed before the completed run.
- Sweep uses seed 20261012, eight random shots per hole and six slow rollers on each of H5/H11/H12/H13/H14/H17. Ordinary resting putts are not classified as stuck. Forced-rest/off-surface/timeout flags are retained with reasons and coordinates.
- `lost_balls` means an unrecovered/missing ball; intended hazard returns and out-of-bounds escapes are separately recorded. Unknown/incomplete checks use null, never zero.
- Spec cup-wall check: H2 cup centre is only **1.0 stud** from rail7, below the requested 2.2. Other 17 holes pass that wall-clearance check. Geometry was not redesigned to hide this source-spec issue.
- Exact-box mover checks sample 3,601 poses against all walls, then subtract a between-sample movement bound (and use invariant axle separation where available). Minimum wall margins: H5 0.15, H11 0.15, H12 0.06, H13 ~0.40, H14 ~1.09 studs. H12 wheel and H14 pendulum floor gaps are 0.060 and ~0.061 studs. These are geometric checks, not a guarantee against dynamic ball pinning. H17 toggle timing is not tested.
- Data and telemetry are under `playtests/stage-ac2/`; per-hole results and final geometry audit are recorded there. No FBX, RBXL, or screenshot binaries are committed.

## Final results and handoff

- Full sweep completed: 144 random shots plus 36 slow rollers. Zero escapes, zero unrecovered balls, one stuck shot: H4 `h4-fuzz-4`, forcedrest/wedged at [182.914, 84.0989, 460.9039]. H5 had one successful pinned-ball recovery nudge; H6 had one intended hazard return.
- Final audit matched all 18 holes to their source dimensions/transforms, including 42 mover blocker boxes and configured cup depth; all 135 visual parts are nonphysical.
- Final audit also found the inherited H1 SpawnLocation colliding with the tee. Disabled CanCollide/CanQuery/CanTouch and hid it; repeated H1's three cupdrops and eight random shots successfully. Final per-hole H1 results use `h1-spawn-recheck/`; baseline telemetry is retained. Extra recheck shots are not double-counted in the 54/54 and 144/36 totals.
- All three completed Play runs reported zero server/client warnings or errors. The summary utility now includes all returned hole numbers instead of truncating at nine.
- Captured and visually inspected `h1-tee.png` and `h1-topdown.png` in `playtests/stage-ac2/` (local only, not committed).
- File > Save to File saved `aurora-test.rbxl`; File > Save to File As saved `playtest-aurora-blockout.rbxl`. UI confirmed both local paths. Checksums/sizes are in result.json.
- Quit Studio. MCP returned `{"studios":[]}` and the Studio application process was absent; recorded in shutdown.json.
- Final result: **PARTIAL**, due to H2 cup clearance, H4 wedged-ball flag, and the H17 static toggle fallback. LG remains Published v9 and SC remains Published v19. No publishing or git push.

| Hole | Cupdrop | Random / slow | Escapes | Lost | Stuck shots | Reasons |
|---|---|---|---|---|---|---|
| H01 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H02 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H03 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H04 | 3/3 | 8 / 0 | 0 | 0 | 1 | wedged |
| H05 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H06 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H07 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H08 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H09 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H10 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H11 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H12 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H13 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H14 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H15 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H16 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| H17 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| H18 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
