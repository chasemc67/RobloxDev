# Pirate Shipwreck v24 job report (v23 brief: collision, gravity, bridge)

Working log, step by step. The summary is at the end.

## A. Preflight (2026-11-01 ~20:58Z)
- Repo ~/src/vr-mini-golf-v2 main @ **bd45378** ("Explore: Roblox default gravity (Config.ExploreGravity 196.2) …"). `tools/stamp`: sha bd45378 dirty=false builderHash 0716f229a84e. The only untracked files are the pre-existing drafts/*.md.
- Rojo 7.7.1 serves on :34872 (`/api/rojo` → vr-mini-golf-v2).
- Studio pid **10698** (Workshop v3, MCP 64890c20): File > Close Place → "Save changes to Workshop?" → **Don't Save**. The unsaved BuildInfo stamp was discarded.
- Opened the protocol URL → new pid **31357**. Studio showed its "Low System Resources" dialog; I pressed Continue. MCP studio ae0c5179. Marker `V23_MARKER_4417` is in `0.745.0.7451137_20261101T205838Z_Studio_a9239_last.log`, line 726: `DataModel Loading …?id=131316561222931&version=23`.
- Rojo synced into the place: BuildInfo sha bd45378 (stampedAt 20:57:19Z) == HEAD, dirty false. Config.ExploreGravity = 196.2, Config.Gravity = 32.7. Edit Workspace.Gravity reads 196.2. Studio user 1818120139 (MetavrseBuilder). HttpEnabled false. Workspace attributes: HutTextureId, PlaceRole=pirate_shipwreck.
- Pid 18508 was not touched. The other old pids (5180, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578) were not touched either. 10698 is at the Start page; I will quit it, since it is mine and empty.

## B. Audit before (Edit, published v23 world)
### Collision state (BaseParts under Workspace.World, Terrain excluded)
| Folder | BaseParts | CanCollide | CanQuery |
|---|---|---|---|
| Meshes (WreckV2 4, CaveV2 7, Props 5) | 16 | 0 | 0 |
| Blockout (Pads 151, RestStops 3, HeroPropFootprints 5) | 159 | 1 (Pad01Plinth) | 1 |
| Dressing (Front 951, Edge 401, Fill 393, Far 386, Walkways 498, Mid 162, Moss 139, Set 138, Set2 118, BackdropPersistent 84, Skyline 67, Debris 43, Arches 37, Vines 28, Hang 3) | 3448 | 0 | 0 |
| **World total** | **3623** | **1** | **1** |

- World.Meshes, all CollisionFidelity Default, all CanCollide/CanQuery false: wreck_hull (92×85×327), wreck_rig, wreck_glow, wreck_duck, cave_cliff_lower, cave_cliff_upper, cave_stairs, cave_water (T 0.2), cave_glow (T 0.3), cave_foliage, prop_croc, prop_cannon, prop_coconut, prop_flytrap, prop_captain, plus CaveMouthLightAnchor (Part, T 1).
- Pads: 18 × Felt / Base / RimN / RimS / RimE / RimW, all CanCollide and CanQuery **false**. LightAnchor ×36 and SoftLightAnchor ×6 are invisible. Pad01Plinth is the only colliding part in the world. Pad 1: Felt top 27.00, Base top 26.80 (bottom 24.80 = plinth top), Rim tops 27.50.

### The "bridge through a pool"
**No inland water exists.**
- ReadVoxels over the whole map (res 4, y -32..256): every Water column tops out at y 0..1 (494,403 columns).
- A flood fill finds a single water body, the sea. Water enclosed by land on 7 of 8 sides within 160 studs: the wreck cove (-550,200), a small south inlet (-442,478) and two east inlets (1080,-233), (1066,-358). The east lagoon has only the backdrop canopy_wall hedge slabs standing in it (non-colliding backdrop).
- No Boardwalk (32 runs), StepStone, Gangplank, planks, spar_snapped, hull_rib or rowboat lies over water. Only Pad 1 is over water, on the wreck.
- The cave_water mesh (waterfall plus a small pool high in the cave cliff) has nothing crossing it.
- RestStop2 (-148.5,45.1,-472.5) is a dark-blue 40×40 Slate slab that reads as a pool from above, but nothing crosses it.

**What fits:** pads read as rimmed pools (green "water" felt inside a dark-blue rim), and three **vine_arch** meshes (31.8 wide × 11.3 tall × 8.5 deep; with their railing of vines they look like a small arched footbridge) are placed straight through a pad's **RimN and Base** (GetPartsInPart, geometry):

| Arch | Position | Yaw | Crosses |
|---|---|---|---|
| vine_arch@Arches | (357.66,18.18,163.98) | -84.6° (span along z) | Pad10 RimN + Base |
| vine_arch@Arches | (-162.98,25.20,-105.01) | -106.5° | Pad12 RimN + Base |
| vine_arch@Arches | (-594.85,33.18,-407.49) | 179.0° | Pad14 RimN + Base |

The span runs into the pad: one foot lands outside the rim, the other inside on the felt edge, and the arch passes through the rim (shots `pool_bridge_before_v23.jpg` = pad 10, `pool_bridge_before_pad12_v23.jpg`). I treat these three as the bridge Chase saw and fix all three (step D). The pad 16 ruin_arch only touches the pad's padded box, not the rim or felt.

## C. Dressing rebuild (new placer with the collision pass)
- **Baseline before the rebuild** (the reopened v23 place): chk20 ALL EXPECTED GREEN, meshparts 2962 / instances 3816 / pointlights 74; sig16b `rows=3479 desc=3565 hash=26ef2457` ×2; terr16b green. Identical to the p4 numbers.
- **ltdr** (`~/stage/v23s/ltdr23.luau`: dressing_v20.luau from :8765 with cache key `?v=23_<os.clock()>`), 2.9 s. Placer log:
  - `DR templates 34`
  - `DR walkways: 99 boardwalk planks, 297 stepping stones`
  - `DR mouth torch ground 86.7 on Terrain` / `DR torches 15`
  - **`DR palm shadows off: 8`** (the v22 MeshPart bug is fixed in this placer)
  - `DR hut lanterns lowered 7 (brightness 1)`
  - **`DR collision: box=66 hero=15 hull=1051 pad=109 precise=57 trunk=195 walk=364 trunkColliders=706`**
  - `DR kit_v2 point lights 28`
  - `DR placed 2843 (skipped wet/no-ground 0), cave vine strips 6`
  - `DR counts … fernclump=605 leafclump=683 rock_s=759 …` (the other classes are the same as v22)
  - `DR DONE instances 4231`
  - `LT20D run ok=true nil http=false`
- **After the rebuild:**
  - chk20 **ALL EXPECTED GREEN**: meshparts **2922**, instances **4482**, pointlights 74, lantern 1.00/16×7, felts Plastic ×18, Bloom 1.1, lat 75 / clock 12, Haze 0 / Glare 0.3 / Density 0.2.
  - sig16b `rows=4145 desc=4231 hash=3fc288af` ×2.
  - terr16b green (hump Air / LeafyGrass 0.26 / Air; Rock 286 / LeafyGrass 0; cliff (115,100,92)).
- **Delta vs published v23: instances +666 = +706 TrunkCollider Parts − 40 MeshParts.**
  - The new placer **drops** the 40 items v22 had hidden in place: fernclump −13, leafclump −13, rock_s −14 (v22 §7 and §9: 28 hedge items, 10 pad 12 leafclumps, 2 widened-cell ferns). v22 kept them as Transparency 1 parts; the place now has 0 hidden Dressing MeshParts.
  - So **the MeshPart count is 2922, not 2962 (−40)**. That is the generator turning the v22 hides into drops, not lost content.
  - The sig16b descendant count is 3565 + 706 − 40 = 4231. chk20 hard-codes no instance count, so no chk20_v23 copy is needed.
- **Re-checked what the placer can reset:** hut TextureID 4/4 = rbxassetid://118487047899591; SoftPadLights 15/16/17 all 6 lights Enabled=false; felts Plastic ×18; lat 75 / ClockTime 12; Haze / Glare / Density and Bloom 1.1 unchanged; 8 palms with CastShadow off (4 Mid + 4 Skyline). Nothing needed fixing.
- **TrunkColliders:** 195 palms. 158 non-Skyline palms × 4 + **37 Skyline palms × 2** = 706. The placer uses `last = 3` for Skyline, which gives **2 segments, not the 3 the brief says** (point 3 is about 21 of 46 studs up a palm_l). Noted for the generator; not changed.
- **In-place change 1 (hero meshes):** the placer rule makes every visible MeshPart under World.Meshes solid. That includes the water and glow overlays and the cave foliage. I set **cave_water, cave_glow, wreck_glow, cave_foliage → CanCollide / CanQuery / CanTouch false**, because nobody should stand on a waterfall, a glow overlay or a leaf canopy. Still solid (Default fidelity): wreck_hull, wreck_rig, wreck_duck, cave_cliff_lower / upper, cave_stairs, and the 5 props. → Generator: exclude names matching `_water`, `_glow`, `_foliage` from the hero rule.

## D. Bridge fix (the vine_arches through the pad rims)
I moved each arch along the pad's long axis, away from the pad, until its footprint clears the Base end by 2 studs. Rotation and look are unchanged. Y is re-grounded by the terrain difference (≤ 0.07). None of the three now touches any pad part (GetPartsInPart, geometry). Both feet stand on terrain: arch bottom 0.2–0.4 under the foot ground, as the generator places it.

| Arch (Dressing.Arches.vine_arch) | Before (x,y,z) | **After (x,y,z)** | Yaw | Span × height × depth | Pad-local Z (felt end ±34) |
|---|---|---|---|---|---|
| Pad 10 | (357.66,18.18,163.98) | **(354.45,18.11,164.28)** | -84.6° | 31.78 × 11.26 × 8.46 | 37.0 → **40.23** |
| Pad 12 | (-162.98,25.20,-105.01) | **(-166.07,25.16,-105.93)** | -106.5° | same | 37.0 → **40.23** |
| Pad 14 | (-594.85,33.18,-407.49) | **(-594.79,33.15,-410.72)** | 179.0° | same | 37.0 → **40.22** |

- **Generator entry:** these are ITEMS `vine_arch` placements (folder Arches) at a pad end. Rule: an arch standing at a pad end must sit at pad-local |Z| ≥ Base half-length 34 + arch half-depth 4.23 + 2 = **40.23** (it was at 37.0, inside the 4-stud rim). Final xz values are in the table.
- These arches are vine gateways, not decks. You walk *through* them, and there is no water under them, so the brief's "deck above the water surface" does not apply. Following the placer rule, vines stay non-colliding (CanCollide false), so the character passes through the arch onto the pad (E.6).
- Shots: `pool_bridge_after_v23.jpg` (pad 10, same camera as before), `pool_bridge_after_b_v23.jpg` (pad 10 from low beside the arch), `pool_bridge_after_pad12_v23.jpg`.

## E. Play test (Studio Play, 2D client, MetavrseBuilder; the world as after C + D)
### E1. Gravity / jump: PASS
- Workspace.Gravity: **server 196.2, client 196.2** in the explore world (server `ExploreWorld=true`, player `Exploring=true`). Edit-mode Workspace.Gravity also reads 196.2.
- StarterPlayer: CharacterJumpHeight **7.2**, CharacterJumpPower 50, **CharacterUseJumpPower false**, WalkSpeed 16, MaxSlopeAngle 89. Character Humanoid: JumpHeight 7.2, JumpPower 50, UseJumpPower false, WalkSpeed 16, Jumping state enabled. Explore2D.enter copies the StarterPlayer values, so nothing resets them.
- Jump on the flat pad 1 felt, root sampled every frame (60 Hz):

| Gravity | Apex (studs) | Time to apex | Airtime | Theory (h = 7.2) |
|---|---|---|---|---|
| **196.2 (new)** | **7.31** | 0.25 s | **0.533 s** | 0.542 s |
| 32.7 (old, set at runtime for one jump) | 7.24 | 0.66 s | **1.333 s** | 1.327 s |

- **Why it floated:** UseJumpPower is false, so Roblox launches the character at v = √(2·g·7.2). With the golf gravity 32.7 (Boot set it in every place, the free-roam world too), the jump reaches the same 7.2-stud height but takes 6× less acceleration. It hangs 0.66 s to the apex and 1.33 s in the air, 2.5× Roblox's normal 0.53 s. At 196.2 it matches stock Roblox.
- The brief expects about 0.75–0.9 s of airtime. That is not what Roblox gives for JumpHeight 7.2 at 196.2: the physics gives 0.54 s, and that is what I measured.
- A one-frame `Humanoid.Jump = true` sometimes doesn't take (the control module clears it the next frame). Holding it for 0.25 s or `ChangeState(Jumping)` always jumps, with the same numbers. Chart: `shots_v23/gravity_chart_v23.png` + `.txt` (samples).

### E2. Pad 1 felt: PASS
- Spawn at the tee (-537.5, 238.7): root Y 29.998, HipHeight 1.998, root half-height 1 → **feet 27.00 = felt top 27.00** (before this job: 24.8 on the plinth, 2.2 studs deep in the felt). FloorMaterial Plastic (the felt).

### E3. Standing on things (character PivotTo above, falls, rests 2.5 s; feet = root − 1 − HipHeight)
| Target (nearest item to pad 1 of the class) | Top (ray on the item) | Feet at rest | Standing on | Result |
|---|---|---|---|---|
| rock_l@Set (-371.8,189.5) | 17.48 | 17.48 | rock_l | PASS |
| rock_m@Fill (-419.9,337.5), 6.1 tall | 12.58 | 12.53 | rock_m | PASS |
| boulder_pile@Set2 (-510.9,155.6) | 41.28 | 41.28 | boulder_pile | PASS |
| ruin_arch@Set2 top (-383.9,-229.3) | 48.53 | 48.49 | ruin_arch | PASS |
| ruin_wall@Set2 (190.6,-48.1) | 32.18 | 32.18 | ruin_wall | PASS |
| hut_leanto roof (-97.0,350.4) | 30.93 | 30.95 | hut_leanto | PASS |
| crate@Debris (-465.6,318.8) | 8.79 | 8.79 | crate | PASS |
| barrel@Debris (-458.5,245.2) | 9.35 | 9.35 | barrel | PASS |
| crate_stack@Set2 (187.4,389.9) | 21.29 | 21.29 | crate_stack | PASS |
| spar_snapped@Debris (-550.4,388.4) | 9.96 | 9.96 | spar_snapped | PASS |
| cliff_ridge (far, BackdropPersistent) (-751.9,664.3) | 181.57 | 182.52 | cliff_ridge (rough top) | PASS |
| wreck deck (-560,225) | 17.08 | 17.08 | wreck_hull | PASS |
| wreck (-600,205) / (-640,205) | — | 58.97 / 68.40 | wreck_rig (lands on the rigging/yards) | PASS (rig is solid) |
| gangplank top (-474.5,254.3) | — | 35.78 | wreck_hull | PASS |

Movement (Humanoid:MoveTo):
- **Pass under the ruin_arch** (pad 13, along its LookVector through the opening): reached the far side in 1.8 s, Running throughout. PASS.
- **Hut:** walking at the hut centre from front, back, left and right reaches the centre in 1.6–1.8 s every time. The hut_leanto mesh is a roof on posts with **open sides**, so there is no wall to block (Default collision; the roof holds a character, row above). Not a fault of the collider, but "walk into a wall: blocked" can't happen with this mesh.
- **Palm trunk** palm_l@Mid (-422.8,309.5) (4 TrunkColliders 3.05→2.33 wide, y 9.8–49): walking straight at the trunk is deflected around it. Closest approach to the trunk axis is **2.24** (collider half-width 1.5 + body), and the walk takes 2.3 s against 1.2 s. Walking 4.5 studs to the side, under the fronds, is free (1.2 s, straight). PASS.
- **Rocks / jumping:**
  - rock_m (3.4 above the ground): walked up without a jump; with a jump, feet rise to 16.5 and it lands on top.
  - rock_l@Set (12 tall): also **walked up without a jump** (feet 17.5 = top).
  - boulder_pile (44 tall, at the waterline): **blocks** with or without jumps (the character stays at its foot).
  - So the low rocks are climbable, and so are taller Hull rocks whose sides are not steep. Cause: StarterPlayer.CharacterMaxSlopeAngle **89** (the Roblox default) plus the smooth Hull slopes. If Chase wants tall rocks to block, lower CharacterMaxSlopeAngle (e.g. 50–60) or use Default fidelity on rock_l. Not changed (judgment call: climbing rocks is harmless in free roam, and the setting is place-wide).
- **Raycasts** (12 random items per class, straight down from top + 40, server, all CanQuery parts, character excluded):

| Class | Rays | Own collider | Another solid item first | Terrain | Result |
|---|---|---|---|---|---|
| rock_l | 12 | 6 | 6 (rock_l stacked in clusters) | 0 | PASS |
| rock_m | 12 | 8 | 4 (rock_l) | 0 | PASS |
| rock_s (≥ 2.5) | 12 | 11 | 1 (hut) | 0 | PASS |
| boulder_pile | 12 | 12 | 0 | 0 | PASS |
| ruin_arch / ruin_wall / hut_leanto | 3 / 3 / 4 | all | 0 | 0 | PASS |
| crate / crate_stack / barrel | 9 / 2 / 12 | 5 / 2 / 6 | 4 / 0 / 6 (debris piles) | 0 | PASS |
| planks / spar_snapped / hull_rib | 12 / 10 / 12 | 5 / 10 / 6 | 7 / 0 / 6 (wreck debris piles) | 0 | PASS |
| cliff_ridge | 12 | 12 | 0 | 0 | PASS |
| rowboat_broken | 1 | 0 | 0 | 1 | PASS: the centre ray falls into the open, hollow hull onto the ground inside the boat (5×5 grid over it: 7 hit the boat walls, 8 the ground inside, the rest neighbours) |
| palm_l / m / s / lean_a / lean_b (TrunkCollider, ray at the trunk) | 12 each | 12 / 10 / 12 / 12 / 12 | palm_m: 1 rock_m, 1 another palm's collider | 0 | PASS |
| Boardwalk / StepStone / Gangplank | 12 / 12 / 1 | 11 / 12 / 1 | 0 | 1 (terrain 0.08 over the plank there) | PASS |
| fernclump / leafclump | 12 / 12 | **0** / **0** | rocks under them | 8 / 9 | PASS (non-colliding) |
| vine_arch / vine_strip / canopy_wall | 12 / 12 / 12 | **0** | walkway/rocks | 6 / 5 / 12 | PASS (non-colliding) |

- No colliding class falls through to the terrain.

### E4. Ball bounce: PASS (collision); the "min Y ≥ surface − 0.2 over 5 s" bar can't hold on domes
- How the ball collides (Ball.luau / PieceUtil): the ball is a physics Part in collision group **GolfBall**. Its ground / contact rays use `RaycastParams` with `CollisionGroup = GolfBall`, Exclude = the balls, IgnoreWater. Those rays hit every **CanQuery** part whose group collides with GolfBall (Default does), and the physics hits every CanCollide part in the Default group. The new colliders are Default-group CanCollide + CanQuery, so both paths see them. (Explore parks the ball, and this world has none.)
- Ball rays (GolfBall group, from top + 40): rock_l → rock_l 17.48; boulder_pile → 41.28; hut roof → hut_leanto 30.93; ship → wreck_hull 17.08; palm side (horizontal ray) → **TrunkCollider** face x -424.34. Pad 1 felt at (-500,252) → **wreck_hull 28.08**: the hull's collision mesh pokes 1.08 above the felt at the pad's east end (see problems). At (-525,240) the felt itself.
- Real sphere (radius 0.5, Restitution 0.5, group GolfBall, server-owned), dropped from 30 studs. First-impact bottom (where vertical speed flips) / lowest bottom while over the target:

| Target | Surface | First impact | Lowest over the target | After 5 s |
|---|---|---|---|---|
| rock_l top | 17.48 | 18.68 (one frame after contact) | 17.12 | rolled off the dome to the ground (8.55) |
| boulder_pile | 41.28 | 42.08 | 40.92 | rolled off into the sea |
| hut roof | 30.93 | 32.14 | 30.57 | rolled down the roof slope to the ground |
| pad 1 felt | 27.00 | 29.01 | 28.41 (bounces); first drop rested at 26.99 | after a 30-stud drop it hops the 0.5-high rim and rolls off the pad (no golf here) |
| ship hull deck | 17.08 | 18.16 | 16.72 | rolled along the deck |
| palm trunk (shot sideways at 60 studs/s) | face -424.34 | bounced back at x -424.78 (= face − radius) | max x -424.25 | — |

- Every target stops and bounces the sphere at its surface; none lets it through. "Lowest over the target" is ~0.36 under the top because the sphere is still within 1.5 studs of a sloped dome top, not because it went into the surface. The 5-s "stay above" bar fails only because round tops shed the ball.

### E5. Walk test (Humanoid:MoveTo along route_v20 pointsXZ, every 3rd point, 18 legs from the pad 1 exit to pad 18 and on to the route end (705,-52); each leg starts with a teleport to its first point; 40 s timeout; jump after 0.8 s without progress): PASS after one in-place fix
| Leg | Time | Jumps | Result |
|---|---|---|---|
| 1→2 | 3.5 s | 0 | OK |
| 2→3 | 18.7 | 0 | OK |
| 3→4 | 19.8 | 0 | OK |
| 4→5 | 17.7 | 0 | OK |
| 5→6 | 17.8 | 0 | OK |
| 6→7 | 12.3 | 0 | OK |
| 7→8 | 12.5 | 0 | OK |
| 8→9 | 16.9 | 0 | OK |
| 9→10 | 24.4 | 0 | OK |
| 10→11 | 19.1 | 0 | OK (passes through the pad 10 ruin_arch (359.2,127.2), which straddles the trail) |
| 11→12 | 20.1 | 0 | OK |
| 12→13 | 16.6 | 0 | OK |
| **13→14** | 20.2 | **7** | completed only by jumping: **blocked at (-394.4,27.3,-230.2) by ruin_arch@Set2 (-383.9,33.9,-229.3)** (all 4 ray heights) |
| 14→15 | 21.1 | 0 | OK |
| 15→16 | 32.3 | 0 | OK (pad 16 ruin_arch (140,-472) straddles the trail) |
| 16→17 | 20.0 | 0 | OK |
| 17→18 | 26.5 | 0 | OK |
| 18→end | 32.3 | 0 | OK |

- No leg timed out, nobody swam, and no collider walls off the 8-stud trail anywhere else. No rock_s / hedge / palm collider blocked the route.
- **Blocker table (fixed in place):**

| Item | Where | Why it blocks | In-place fix | Generator |
|---|---|---|---|---|
| ruin_arch@Set2 (pad 13) | (-383.9,33.9,-229.3) | v22 moved it onto the trail sand, but its 34-stud span runs **along** the trail (RightVector (0.987,0,0.162) ∥ trail (-0.91,-0.42)), so the 13-deep solid side stands in the path. | Rotated **+90° about its centre**: RightVector → (0.162,0,-0.987), yaw 80.7° (EulerYXZ), position unchanged. Its lantern_hanging rotated with it: (-392.3,44.6,-230.2) → **(-384.8,44.65,-220.9)**, still under the lintel. Leg ground 19.8 / 23.0 (the uphill leg is buried about 3 studs, which reads as a sunken ruin). | ruin_arch at a trail point: yaw so the span is **perpendicular** to the trail tangent (LookVector along the trail). For this one: pos (-383.9,-229.3), RightVector (0.162,0,-0.987); lantern (-384.8,-220.9) |

- After the fix: leg 13→14 in 20.0 s with **0 jumps**, and the walk under the arch along the trail takes 1.7 s (shot `arch_pass_v23.jpg`). Applied in Edit after the test session (persisted).

### E6. Bridge (the pad 10 vine_arch): PASS
- From pad-local Z +52 (342.7,165.4) through the arch at (354.45,164.28) onto the felt at (384.5,161.4): 3.2 s, Running only (**never Swimming**). Feet under the arch 12.86 (ground), max 14.00 (stepping over the rim, top 14.0), **end 13.50 = felt top**. No water anywhere on this path. Shot `bridge_cross_v23.jpg`.

### E7. Frame rate / load: PASS (no collider cost measurable)
- Play start: the client had its character and Exploring at DistributedGameTime **7.99 s** (p4 v23: 6.99 s); 12.1 s on a later Play right after the hull fidelity experiment. No physics-throttle or collision-memory warning in the log.
- Client FPS (Studio in the background, 10 other Studio instances on this Mac, so the absolute numbers are low): pad 1 tee **14.6** avg (worst frame 262 ms); densest jungle cell (x 128..192, z 320..384, 65 Dressing parts) **14.4**.
- Same spot, same session: colliders on 14.7 / Dressing colliders switched off on the client 14.5 / on again 14.8. **The colliders cost nothing measurable**; the limit is Studio running unfocused.
- Counts: 706 TrunkColliders; the client sees 2369 CanCollide BaseParts (whole map, streamed).

### E8. VR (SimulateVR set at runtime, ClientBootGen 1→2): PASS
- Toast "Exploring: off-hand stick walks, stick click flies". **Feet over the pad 1 felt = cam 32.40 − head 5.40 = 27.00** (p4: 24.80 on the plinth).
- Stick walk 3.89 studs on the felt, feet stay 27.00. In VR the origin drives the character (a character PivotTo is overridden), so to reach a rock I flew: L3 → "Flying (stick click: walk)", right stick rose to feet 54.99, left stick flew 82 studs to over the boulder_pile top (-510.9,155.6), L3 → landed **feet 41.33 on the boulder_pile (top 41.28)**, not the seabed. A stick step on the boulder followed its surface (41.33 → 41.77).
- The VR floor ray (Club floorRay, Workspace.World walkable while exploreWorld) sees the new colliders because they are CanQuery. Non-queryable decor (ferns, leaves) is still ignored.

### E9. Console: PASS
- `[Boot/server] PlaceRole=pirate_shipwreck role=explore sha=bd45378…`, `[Boot/client] … role=explore`, the known `rbxassetid://203785492` warning ×3, `[Boot/client] Studio: SimulateVR changed at runtime; restarting`, and the MCP's own camera-type note. No errors.

### Extra findings during E
1. **Wreck hull collision vs the pad 1 felt (soft, documented).**
   - With Default fidelity the hull's collision decomposition rises **up to ~1.7 studs above the felt over the middle of pad 1**: walking the centre line from the far end to the tee, feet read 27.7–28.7 between x -486 and -525. The tee spot and the tee end are clean (27.00).
   - **PreciseConvexDecomposition** fixes the felt: walking lane x-3 is 26.99–27.00 along the whole length. The hull only rises on the +x side (+0.6 / +2.0 / +3.8 at x 0 / +6 / +12), and that matches the visible deck boards beside the felt.
   - **But** Precise makes the bow wall solid where the gangplank passes through the stem. The gangplank walk then stops halfway (feet 25.6). Blockcasts along 24 alternative plank lines (top z 252–253.8, foot z 244–256) all hit the bow wall, so no plank from the deck to the beach clears an accurate hull.
   - **Kept Default** (the brief's rule): the gangplank and deck are walkable, and the felt float in the middle of pad 1 is the cost.
   - Options for the new boat from the 3D Model Bot: a separate low-poly collision mesh, or a real gap in the bulwark at the gangplank. Then PreciseConvexDecomposition gives a clean felt and a walkable gangplank.
2. **Gangplank:** walked deck → beach in 3.2 s (Default hull). The character rises over the bow stem to feet 41.2 on the way (the plank's middle runs inside the stem, as v22 noted), then descends the plank to the beach at (-447.9,4.46,260.5). A broken **hull_rib@Debris (-458.2,3.1,259.8)** straddles the gangplank foot like an arch (shot `gangplank_walk_v23.jpg`). With a "rope bridge through an arch" look, this is the other thing Chase may have meant by the bridge. It is not over water (sand, ground 4.0, sea surface 0 further west), so I left it.
3. The hut_leanto is an open lean-to; see E3.
4. Hull rocks are walkable up to rock_l size (MaxSlopeAngle 89); see E3.

## F. Publish: Pirate Shipwreck (all of E passing; the wreck-hull felt float is documented as soft)
- Pre-publish (Edit, after the E fixes):
  - chk20 ALL EXPECTED GREEN, meshparts 2922 / instances 4482 / pointlights 74.
  - **sig16b `rows=4145 desc=4231 hash=37177214` ×2** (3fc288af right after the placer; the difference is the in-place D/E edits).
  - terr16b green.
  - TrunkColliders 706; felts solid 18/18; wreck_hull Default; hero overlays (wreck_glow, cave_water, cave_glow, cave_foliage) off; hut texture 4/4.
  - Workspace attributes only HutTextureId + PlaceRole; no VRDebug / GolfTestAPI / test balls; HttpEnabled false; Camera Custom FOV 70.
- `tools/stamp`: bd45378 == HEAD, dirty=false (no code change in this job). Place BuildInfo sha bd45378 (stampedAt 21:35:20Z). Studio user 1818120139 (MetavrseBuilder); window "Pirate Shipwreck - Roblox Studio"; placeId 131316561222931.
- File > Save to Roblox (System Events on pid 31357, frontmost verified): `Publish succeeded for placeId 131316561222931`, **`Saved new changes in "Pirate Shipwreck" to Roblox.` 21:35:38.697Z**.
- File > Publish: **`→ Add publish notes to v24`, `Published new changes in "Pirate Shipwreck" to Roblox.` 21:36:55.525Z = 1:36:55 PM PST.** No dialog. The experience and place were not made public.
- File > Close Place (no prompt). Quit my empty pid 31357. Protocol reopen → **pid 94928** (no resources dialog this time), MCP bd27b55b. Log `0.745.0.7451137_20261101T213725Z_Studio_a49f6_last.log`: **`DataModel Loading …?id=131316561222931&version=24`** (21:37:29Z). **Version 23 → 24.**
- Reopened checks, identical to pre-publish: chk20 ALL EXPECTED GREEN (2922 / 4482 / 74), sig16b 37177214 ×2, terr16b green.
  - TrunkColliders 706; felts CanCollide+CanQuery 18/18; pad 13 arch RightVector (0.162,0,-0.987); the 3 vine_arches at their fixed positions.
  - HutTextureId rbxassetid://118487047899591; BuildInfo bd45378 dirty false; Config.ExploreGravity 196.2; Workspace.Gravity 196.2; HttpEnabled false.

PIRATE_PUBLISHED_V24

## G. Test Course and Workshop (the Explore-gravity code)
### Test Course (92186005456885)
- Closed Pirate Shipwreck in pid 94928. "Save changes?" appeared (only my reopen check script's side effects: Http toggle, camera), so **Don't Save**. Quit my empty pid 94928. Protocol open → **pid 98494**; log `…213933Z_Studio_d07f0_last.log` **`version=19`**; MCP caa4fc94.
- Rojo synced at once: BuildInfo bd45378 dirty false (stampedAt 21:35:20Z), Config.ExploreGravity 196.2, Config.Gravity 32.7. PlaceRole test_course.
- **Smoke PASS** in Edit (`require(Shared:Clone().Course).smoke{head=bd45378, since}`): problems [], 3 holes fresh (straight-walls, ramp-ice, spin-teleport-water), 48/48 grounded. builderHash unchanged (0716f229a84e), so no rebuild.
- Play, flags at runtime on the LocalPlayer only (GolfTestMode, then SimulateVR):

| Check | Measured | Last row (v19) | Result |
|---|---|---|---|
| explore 2D | **19/19** (×2) | 19/19 | PASS |
| Gravity while exploring (client, sampled every 30 ms through the explore job) | `0.0s 32.7/Exploring false → 4.3s 196.2/true → 10.7s 32.7/false → 15.0s 196.2/true → 15.4s 32.7/false` (the second phase is the "Ready ends Explore" step). Server Workspace.Gravity stays **32.7** (Explore.apply is client-side; the character is client-simulated) | new | PASS |
| ui2d | **22/22** (11 s) | 22/22 | PASS |
| explore VR (SimulateVR, ClientBootGen 1→2) | first run **12/12**: the 13th step ("Ready while exploring ends Explore") only runs when the "a putt counts again" putt does not hole, and it holed. Second run **13/13**, gravity 196.2 in both Explore phases, 32.7 after | 13/13 | PASS |
| Ball / golf after Back to golf | "a putt counts again" and "ball and turn restored exactly" pass in every run (ball rolls at 32.7) | — | PASS |
| Console | 0 errors; only the known 203785492 warning ×3 | same | PASS |

- After Stop: Workspace only PlaceRole=test_course; no GolfTestAPI / VRDebug; HttpEnabled false; user 1818120139; window "Test Course - Roblox Studio".
- File > Save to Roblox left no log line (nothing new to save). File > Publish: **`Published new changes in "Test Course" to Roblox.` 21:44:28.345Z, `→ Add publish notes to v20`** (`Publish succeeded for placeId 92186005456885`).
- Close Place, quit my empty pid 98494, reopen → **pid 7900**, log `…214458Z_Studio_0e084_last.log` **`version=20`**; sha bd45378 dirty false, ExploreGravity 196.2, **smoke PASS** (48 grounded). **Version 19 → 20.**

### Workshop (85191839793106)
- Closed the Test Course (no prompt), quit my empty pid 7900. Protocol open → **pid 9873**; log `…214608Z_Studio_5bb0d_last.log` **`version=3`**; MCP 14db5563.
- Rojo synced: sha bd45378 dirty false, ExploreGravity 196.2; Edit place Camera / Baseplate / Terrain / SpawnLocation; PlaceRole workshop.
- Smoke doesn't apply to the Workshop (p4 D2), so I ran the direct ground check on the play server: loaded hole **ramp-ice**; GroundHash 9424bad63851… **== Ground.hash(entry.ground, loaded hole)**; **Ground.check pass, 15/15**; CanTestCourses true.
- explore 2D **19/19** ×2. Gravity timeline: `32.7/false → 5.0s 196.2/true → 11.3s 32.7/false → 16.1s 196.2/true → 16.5s 32.7/false`. Server 32.7. Console: 0 errors, the known warning ×3.
- After Stop: Workspace only PlaceRole=workshop, no harness leftovers, HttpEnabled false.
- Publish: **`Published new changes in "Workshop" to Roblox.` 21:49:08.434Z, `→ Add publish notes to v4`**. Close Place, quit my empty pid 9873, reopen → **pid 15860**, log `…214932Z_Studio_f217f_last.log` **`version=4`**; sha bd45378, ExploreGravity 196.2, Client.Explore present. **Version 3 → 4.**

### Lobby (92425959637314): not published
No behaviour change. The lobby has no Explore (Boot sets Config.Gravity 32.7 there, as before), and the gravity change only touches Explore and explore-role places. As the brief says, no publish.

## H. Deploys rows
- `docs/deploys.md`: 3 rows (Pirate Shipwreck v24 13:36, Test Course v20 13:44, Workshop v4 13:49, PST; SHA bd45378144ae8f08842bc29a16a041cf3996beec). **Commit 14f1d09 "docs: add v23 gravity and collision deploys rows"**, local only, not pushed.
- Re-stamped: BuildInfo 14f1d09 (gitignored). Rojo will sync that stamp into the open Workshop session (pid 15860); it stays unsaved and unpublished, as in p4.

# Summary

**Result: DONE.** Pirate Shipwreck published as **v24**; Test Course **v20** and Workshop **v4** published with the Explore-gravity code. All private. Lobby not published (no behaviour change).

| Place | Before → after | Studio log | SHA |
|---|---|---|---|
| Pirate Shipwreck 131316561222931 | 23 → **24** | "Published new changes in "Pirate Shipwreck"" 21:36:55Z, "Add publish notes to v24"; reopen `version=24` | bd45378 |
| Test Course 92186005456885 | 19 → **20** | "Published new changes in "Test Course"" 21:44:28Z, v20; reopen `version=20` | bd45378 |
| Workshop 85191839793106 | 3 → **4** | "Published new changes in "Workshop"" 21:49:08Z, v4; reopen `version=4` | bd45378 |

**Chase's four points**
1. **Falling through scenery:** fixed by the placer collision pass plus in-place fixes. Every colliding class holds a character (E3), a ball (E4) and the VR floor (E8). The route walks 18/18 legs (E5).
2. **Floaty jump:** fixed by bd45378. Gravity 196.2 in the world: apex 7.31, airtime 0.53 s, against 1.33 s at the golf gravity 32.7 (E1, `gravity_chart_v23.png`).
3. **Bridge through a pool:** there is no inland water in this world. The match is three vine_arches (they look like little arched footbridges) standing through the rims of the pool-like pads 10, 12 and 14. All three were moved off the pads (D). If Chase meant something else, the other candidate is the gangplank: it runs through the bow stem and a broken hull_rib arch at its foot, but it is not over water (E extra 2).
4. **Knee deep in the felt:** fixed. Feet 27.00 = felt top on pad 1 (2D and VR). The felt / base / rims of all 18 pads are solid.

## Generator finals (put these into the generator)
1. **Hero meshes rule:** exclude `cave_water`, `cave_glow`, `wreck_glow` and `cave_foliage` (names with `_water` / `_glow` / `_foliage`): CanCollide / CanQuery / CanTouch false. Keep wreck_hull on **Default** (not PreciseConvexDecomposition) while the gangplank runs through the stem.
2. **vine_arch at a pad end:** pad-local |Z| ≥ Base half-length 34 + arch half-depth 4.23 + 2 = **40.23** (was 37.0, through the rim). Finals (x,y,z): pad 10 **(354.45,18.11,164.28)** yaw -84.6°; pad 12 **(-166.07,25.16,-105.93)** yaw -106.5°; pad 14 **(-594.79,33.15,-410.72)** yaw 179.0° (rotation unchanged, Y = terrain-relative as placed). Non-colliding (vine rule).
3. **ruin_arch on the trail:** span perpendicular to the trail tangent. Pad 13 arch at (-383.9,33.9,-229.3): RightVector **(0.162,0,-0.987)** (was (0.987,0,0.162)). Its lantern_hanging **(-384.8,44.65,-220.9)** (was (-392.3,44.6,-230.2)). The pad 10 (359.2,127.2) and pad 16 (140,-472) arches already straddle the trail.
4. **Collision rule changes from the blocker table:** none. No rock_s, hedge or palm collider blocked the 8-stud trail. The only blocker was the pad 13 arch's orientation.
5. **TrunkColliders on Skyline palms:** the placer makes 2 segments (`last = 3`), not 3. Use `last = 4` if 3 are wanted (+37 Parts).
6. **Optional, not applied:** StarterPlayer.CharacterMaxSlopeAngle is 89 (Roblox default), so Hull rocks up to rock_l size can be walked up without a jump. Set about 55 if tall rocks should block.

## What I could not test
- No headset (VR is SimulateVR only), no real phone, no second account.
- Absolute frame rate: Studio was unfocused with 10 other Studio instances running (14–15 fps either way). The with/without-collider comparison is relative.
- Creator Hub Version History not checked in a browser. Versions come from the Studio log and the reopens.

## Problems / notes
1. **Wreck hull vs the pad 1 felt (soft):** with Default fidelity the hull's convex decomposition rises up to ~1.7 above the felt over the middle of pad 1 (a character walking the centre line floats there; the tee spot is clean). PreciseConvexDecomposition fixes the felt but makes the bow wall solid across the gangplank, and none of 24 alternative plank lines clears it. **Kept Default.** The new boat from the 3D Model Bot should have a simple collision mesh, or a real bulwark gap at the gangplank.
2. **MeshPart count 2922, not 2962:** the new placer drops v22's 40 hidden items instead of hiding them. Explained in C.
3. **Brief expectation vs physics:** a 7.2-stud jump at 196.2 lasts 0.54 s, not 0.75–0.9 s. The measured value matches the physics.
4. **Hut "walk into a wall"** can't happen: the hut_leanto is an open roof on posts (E3, shot `hut_block_v23.jpg`).
5. A one-frame `Humanoid.Jump = true` from execute_luau sometimes doesn't take (the control module clears it the next frame). Hold it a few frames.
6. Studio once stopped answering the MCP for about a minute after the wreck_hull fidelity change (collision rebuild). It recovered on its own.

**Rules kept:** no Script / LocalScript / ModuleScript created or edited through the MCP (no code change in this job; the gravity code is Chase's bd45378 through Rojo). One place open at a time. All places private, no Robux. No Screen Recording prompt appeared. Pid 18508 and the other old pids (5180, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578) untouched. Every GUI input went through `/tmp/p4/p.sh` / `act.sh` (activate by pid, frontmost check). Nothing deleted except the placer's sanctioned Dressing rebuild (no assets, no Blockout parts). The boat's look and position unchanged (only CanCollide / CanQuery on the hull, rig and duck, and wreck_glow off). Commits local only; nothing pushed or posted. `tools_v20/chk20.luau` not edited (no copy needed).

**Studio state at the end:** pid **15860** open on the Workshop v4 (MCP 4be43a8a), with the 14f1d09 BuildInfo stamp unsaved. Pids I opened and quit: 10698 (handed over), 31357, 94928, 98494, 7900, 9873. Rojo serve still on :34872; :8765 / :8767 / :8769 / :8770 still up.

**Files:** this report; `~/stage/shots_v23/` (pad1_stand, jump_rock, ship_deck, gangplank_walk, palm_trunk, hut_block, arch_pass, ball_bounce, pool_bridge_before (+ _pad12), pool_bridge_after (+ _b, _pad12), bridge_cross, gravity_chart (.png + .txt), pad_1_front, pad_14_front, all `_v23`); `~/stage/v23s/` (ltdr23.luau, legs.json, walk.luau, walk_full.luau). Repo commit 14f1d09.

DONE_V23
