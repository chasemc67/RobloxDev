# Stage am — Aurora v5 (local)

Result: **PASS — requested local build and verification completed.** Clearance findings remain explicitly reported below; PASS does not mean zero decoration bounds findings.

## Local scope and preflight

Read game AGENTS.md and ag/ah/af notes plus af-portability before work; also read ai notes for the import/audit workflow. No competing stage job matched the requested process check. Studio welcome screenshot confirmed MetavrseBuilder. Opened only local `playtest/playtest-aurora-v4.rbxl` through File > Open from File, immediately Save to File As `playtest/playtest-aurora-v5.rbxl`; native UI confirmed the exact path. One MCP Studio, Edit PlaceId=0, GameId=0, no NetworkClient, role aurora_archipelago. MCP retains the original v4 display name after Save As.

No cloud place opened/saved, no place created/published, no git push, no asset fetch/sync. Protected place 135374506016678 was not touched. Import used Upload to Roblox unchecked, scene position/origin enabled, anchored enabled, cages disabled, matching ai. As documented in af, this does not prevent Studio's child mesh asset creation; no inventory-model upload or separate upload action was performed.

## Data, meshes and source

Regenerated AuroraArchipelago/AuroraLayout with `tools/aurora_to_lua.py` from local holes.json, modified **Oct 13 12:24:41**. Input snapshot and preflight hash are retained. Pushed source and rebuilt CourseAurora, preserving all 74 approved earlier props and reconnecting their mover welds.

Imported only the 23 FBXs named in props_batch3_manifest.json from the supplied Mini assets. `import-hashes.json` records every SHA1; `batch3-manifest.json` and `import-specs.json` preserve revisions, motion, pivots, colors/materials and source mesh bounds. **h18_halo_arch rev2; h06_kettle_pool rev2, no Steam mesh.** Other revision labels are reported only where stated in the manifest.

Merged source round-trip PASS: **23 props, 83 meshes, 20,268 triangles**, maximum mesh **1,004 triangles** (`h14_icicle_bell__Brass`), no mesh/material/bounds discrepancies. New AuroraPropsBuilder.PrepareKit follows ai's source-FBX bounds normalization, 180-degree importer correction and exact manifest world placement; retains normalized kit copies in ServerStorage.AuroraBatch3Kit. Visual meshes have all collision/query/touch flags false and VisualQueryDisabled. H14 bell is massless and welded to the existing exact MoverRoot. No collider geometry was tuned for decoration.

Superseded H6 pool, H14 moving-bell and H18 complete rail-network blockout render skins are hidden; H18 generated rail presentation is hidden under its approved exact skin. Existing ai replacement rules are reapplied. Obsolete H6 blockout cup/flag presentation is also hidden to remove the duplicate cup marker visible from the tee. Physics remains generated from holes.json.

## Effects

AuroraEffects.Apply runs after manifest placement. H6 steam is a white ParticleEmitter with rate 5, speed 0.22–0.4, lifetime 1.2–1.8, opacity at most 0.14 and small particle size, positioned just above the authored water center. No replacement Steam mesh. The final tee-eye screenshot and raycast-free projection check confirm cup visibility (details below).

H17 fade values are derived from holes.json profile: fade-in 0.6, solid 6, fade-out 0.6, gone 1.8, period 9. Collider flags switch together only within `[0.6,6.6)`. Span and ribbon fade with the shared schedule; lamp is mint during solid, violet during fades and dark during gone; three elevated emitters fray into sparkles during fade-out. Native exact-boundary check passed, including repeated-cycle boundaries 9.6 and 15.6. Authored aurora_gap retains +1 penalty and light-entry respawn `[0,0,-14.5]`.

## Clearance

Exact source checker `--all`: **296 raw findings, 12 real findings across 3 props**. Native built audit: **429 raw findings, 56 prop-class findings across 15 props**. Combined union: **16 unique flagged props**. `flagged-props.md` lists EVERY source real finding and built prop-class finding, signed gap and target. Negative signed gaps indicate bounds overlap; felt values use the checker's vertical headroom convention.

The built test uses individual mesh oriented bounds, which can enclose empty space in arches/gantries or disconnected joined meshes. These flags are conservative bounds findings, not proof of triangle intersections. Approved manifest placements were retained. Two visible H3 coplanar bounds candidates from ai remain separately recorded. Initial built audit: 97 props, zero visual-flag errors, zero mover-weld errors.

## Native tests and final file

- Cupdrop **54/54**, three on each of all 18 holes.
- Random **144/144**, eight completed shots per hole.
- Slow rollers **36/36**, six each on H5/H11/H12/H13/H14/H17.
- **Stuck 0, escapes 0, timeouts 0.** Two successful H11 pinned-ball recovery nudges (one random, one slow) and two authored hazard returns (H6 random, H17 slow) are retained in telemetry.
- Focused H17 **6/6 timed shots** crossed while solid; **3/3 mistimed shots** fell, counted the shot plus exactly one penalty stroke, and rested at the authored light-entry respawn. Tests launched real Ball.hit shots at 8 studs/s from the south pier, local `[0,0,-23]`, at phases 1/1.5/2/2.5/3/3.5 and 6.8/7.1/7.4. Final mistimed horizontal respawn error 0; settled vertical difference 0.0307 studs from the lifted spawn point.
- H17 visual/physics schedule: **301 samples over 20.067 seconds, zero mismatches**, including span/ribbon fades, collider flags, mint lamp/brightness and fade-out-only sparkles. Sampling occurs after physics, with 0.04 alpha tolerance and exact collider/phase assertions; exact mathematical boundaries are separately tested.
- Final server/client audits: **97 props each**, zero collision/query/touch or VisualQueryDisabled violations, zero mover-weld errors. All 23 new props pass native transform/material/revision checks and all 23 FBX hashes remain unchanged.
- Full sweep, focused H17 and final visual sessions each had **zero console warnings/errors**.
- H6 tee-eye camera: `[305,89.0110,478]`, exactly 5 studs above Tee.Position. Steam conservative maximum world Y 84.3276, **4.6834 studs below eye level**. Cup projects to `(414.5,249)`; projected conservative steam rectangle is `(578.19,264.84)`–`(612.60,285.48)`, disjoint from the cup. Inspected `screens/am-h06-tee-eye5.jpg`: cup/flag base visible, no steam obstruction. **No raycast used** in this visibility check. H14/H18 prop views also inspected; screenshots stay local/uncommitted.
- Final Edit: PlaceId 0/GameId 0, no NetworkClient, Aurora role; GolfTestMode/SimulateVR false, test attributes cleared. **All 55 Studio sources match repository files**.
- Saved through File > Save to File; native UI confirmed `playtest/playtest-aurora-v5.rbxl`. Studio closed; MCP inventory empty and no RobloxStudio process. v4 byte-identical.

Final v5: **1,346,139 bytes**, SHA256 `8aebf8e65cd48ac0f90a2d64e996d6fb23a6f2e0facc86b40dc417c83bd25951`. Saved binary contains all **83 expected new mesh IDs**, none missing. No RBXL, FBX, PNG or other screenshots are committed.

The initial visual sampler resumed in PreSimulation before Movers' connected update, yielding 42 stale-frame transition comparisons. Repeating after PostSimulation eliminated all 42 without gameplay/source changes; both diagnostic and final telemetry are retained. This is measurement ordering, not a claimed physics fix.

Harness diagnostics: an initial focused H17 probe had a missing loop terminator, then direct MCP require produced a separate uninitialized BallController module state. Both attempts were stopped before a shot. The final harness uses a temporary gameplay LocalScript and returns JSON through a temporary StringValue; no test script persists in the saved place. Diagnostic attempts are excluded from final gameplay totals.
