# Lantern Grove props: pass 3 summary (2026-10-10): world-scale background pieces

This pass builds the meshes for the continuous world (`../world/world.json`, README "Hollow tree", "Background
pieces" and "Rings"). Everything is in `models/world/` and is decoration only. `holes.json` and `world.json` were
only read, never changed.

## What was built

39 pieces in 50 FBX files, 290k tris in total. The biggest single file is 19.2k tris (`sister_tree_nw`), so every
FBX is under 20k (checked again after re-import).

1. **hollow_tree_world_shell** (top priority). Origin = trunk base centre **[-74, 39.6, 6]**, yaw 0.
   - **Trunk**: one closed surface of revolution, 320 segments. Outer r 45.84 with a base flare and buttress ridges,
     tapering to about 41 at the top. Inner r 38.84 up to y+50, then a dome to the **oculus (r 14) at y+78**, and a
     shaft open through the top cap at y+100. The skirt goes to -4.6 to meet the terrain.
   - **Bark**: lumps plus spiral furrows. The inside uses the new warm `Heartwood` texture.
   - **Heartwood Door**: EXACT boolean through the wall. 14 wide x 20 high at map angle 53.1 deg, splaying to
     17.5 wide inside. Oak arch frame, keystone and two bracket lanterns.
   - **Split into 7 parts**:
     - parts 1-4: wall sectors, with the door sector first;
     - part 5: buttress roots to r 65.8;
     - part 6: outer details (door, 8 glowing windows, bracket fungi, moss, hook lanterns);
     - part 7: interior (5 lantern strings across the hollow, wall lanterns, glowing mushrooms, gold fungi).
   - **Roots grow against the fit rules**: each root is grown, checked against the keep-outs, and shortened until it
     is clear. On the H8 / Heartwood-walkway side (map angles about 0-45 deg) the roots are short, and the base flare
     is pulled in (to r 44.6) where p_h8_h9 hugs the trunk.
2. **hollow_tree_crown**. Origin = crown base centre **[-74, 139.6, 6]**.
   - 9 lumpy gold/orange leaf masses: a drooping lower ring of 6 plus an upper tier of 3 (the brief asked for 5-7;
     the extra upper tier was added in iteration 2, see below). They leave a small light gap over the oculus.
   - 9 limbs rise from the trunk-top rim, and 12 big hanging lanterns sit under the outer crown.
   - Fitted to exactly 176 x 78 x 176. The limbs dip 3 below the crown base into the trunk top.
   - 6 parts, each under 16.7k tris.
3. **Sister trees** (`sister_tree_nw` / `_sw` / `_ne`): background variants in the hollow_tree look: furrowed lathe
   trunk, buttress roots, limbs, lumpy masses and hanging lanterns. NW has a glowing arched door and windows (the
   hero's cousin). Recoloured: golden, red maple, golden oak. Fitted to 60x90x60, 55x80x55 and 50x75x50.
4. **Everything else**:
   - **Waterfalls**:
     - `grand_falls_curtain`, `twin_falls_curtain` (two strands) and `lantern_falls_curtain` (lantern posts at the
       lip, floating lanterns at the base);
     - each is built from the exact world.json top/bottom points, with yaw = flow direction;
     - each has a translucent sheet, foam ribbons, splash, Mist puffs and a backing slab.
   - **Rock kits**:
     - `highland_cliff_kit_a..d` (strata / columns / overhang / convex corner): 12 placements along the scarp,
       computed from the terrain, base at the foot, sy = drop / 30;
     - `terrace_rock_faces_a..c`: 20 placements on steep Rock cells, at most 4 on the tree mound.
   - **Landmarks**: `old_lantern_tower` (ruined with an amber lantern loft), `hill_mushroom_houses` (4 scaled
     mushroom_house_medium in red / orange / gold), `mere_dock` (yaw from the mere's normal), `mere_lantern_boat`
     (x8), `sky_lantern` (x24 around the crown, y 150-280).
   - **Sky**: `cloud_card_a/b` (x7, r 1800-2400).
   - **Tree line**: `treeline_clump_{a,b,c}_{gold_orange,red_orange,red_gold,gold_green}` (3 meshes x 4 colour
     mixes, mapped onto the 56 world.json treeline instances with per-instance scale).
   - **Distant scenery**: `far_hill_a/b` (x18) and `mountain_a/b/c` (x12, violet low-poly).

Every instance (world pos, yaw, scale, source world.json id) is in `models/world/manifest.json`, in
`models/world/layout.json`, and in the new `world` section of `models/manifest.json`. `build_all.py` now keeps that
section when it rewrites the manifest.

## H9 fit (world_fitcheck.py → models/world/fitcheck_world.txt): ALL PASS

The check re-imports the exported FBX files and places them in the world. It then runs an **exact triangle-vs-box
(SAT) test on every triangle** against:
- H9 and H8 elements transformed with the world.json placements (origin [-57.6, 40, 30.7], yaw 62.3 for H9):
  - felt +1.25 up to felt top + 6.5;
  - walls;
  - moving-part sweeps (root gate, lantern bar) + 0.5;
  - teleports;
  - tee pad + run-up;
  - hero props;
- walkways p_h7_h8 and p_h8_h9: width/2 + 0.75, 6.5 high, and 12 high near the door;
- the walkways' lantern posts.

Results:
- No shell or crown triangle hits anything.
- Inner wall r ≥ 39.15 vs H9's footprint r 33.84, which leaves **5.3 studs of walking room**.
- **Door**: 30 rays along p_h8_h9 through the arch (±3.5 sideways, up to 11 high) are all unobstructed. The measured
  opening is **14.0 wide x 20.0 high**.
- Negative tests (a triangle on the felt, in the lantern-bar sweep, and in the door corridor) are all flagged.
- The waterfalls, rock kits, dock, tower, village and sister trees were checked against **every** hole, walkway and
  lantern post.

**Bugs the check caught and that are now fixed**:
- the base flare and door-threshold moss were in the walkway;
- the door lanterns hung into the 12-high door corridor;
- the twin-falls lip rocks sat on H5's felt and stream;
- one terrace face was on the Lookout Descent.

## Vista iterations (models/world/previews/vista_*.png)

The vistas render over a preview-only terrain mesh built from terrain-4stud.json, with material colours from the
legend and water cells. It also has holes.json felt and walls, path ribbons, the hole hero props, the 54 lantern
posts and all 179 world instances. The cameras are the world README vista points: H1 tee, Lookout Rock, foot of the
Root Stair, and aerial.

**Iteration 1 problems**:
- the crown read as a flat cushion on a stump;
- the far hills looked like patchwork quilts (per-face colours);
- the highland/terrace kits looked like dry-stone walls (small pillowy blocks, limestone brick texture);
- the preview water was too dark.

**Fixes**:
- a second, upper tier of crown masses, plus taller drooping lower masses;
- trunk buttress ridges;
- far hills now use one low-frequency base colour plus 150 canopy bumps;
- strata are now long tilted slate slabs;
- lighter preview water;
- H1 camera pitched up so the tree and crown fit.

**Iteration 2 problems**:
- the corner cliff style was still bricky;
- the mountains washed out to white;
- rock faces were crowding the tree mound.

**Fixes**:
- bigger corner blocks;
- the haze material only on the top faces;
- at most 4 faces on the mound;
- stronger buttresses.

**Iteration 3 (final)**:
- From the H1 tee the giant tree dominates with a golden domed crown, sky lanterns and hanging lanterns. The lit door
  faces the course, with the mere, Lantern Falls and the village cliffs on the right.
- Lookout Rock shows H5-H7, Twin Falls, the Grand Falls scarp kit and the tower on the highlands.

## Known issues / notes for Studio

- **Preview-only parts**: the terrain mesh, felt boxes and path ribbons in the vistas are not exported. The
  stepped dark zigzags along the stream in the vistas are 4-stud water cells in that preview.
- **Root Stair vista**: it mostly shows the stair ribbon and the root-terrace rock slope. From that exact camera the
  terrain hides the tree, as in the real world.
- **Tree mound**: the rocky ring around the mound is the world terrain's own Rock cliff, not these meshes.
- **Sister trees**: their trunks read a bit slim against the canopies. That is fine at 100+ studs.
- **Non-uniform scales**: rock kits, tree line, hills and mountains use them. Scale each MeshPart per axis, or
  accept a uniform `ScaleTo(sy)` for distant pieces.
- **Light shaft**: the oculus light shaft is not a mesh. Add a SurfaceLight/Beam in Studio. The crown leaves only a
  small gap over the oculus.
- **Atmosphere**: the clouds and mountains are beyond the 800-stud terrain. They rely on Roblox Atmosphere and
  render distance, so check them in VR.

## Files

- **New code** (`_src/`):
  - `world_fit.py`: world transforms, terrain sampler, keep-out boxes, triangle SAT;
  - `world_pieces.py`: geometry;
  - `world_layout.py`: placements;
  - `world_build.py`: FBX, previews, manifests;
  - `world_fitcheck.py`;
  - `world_vista.py`;
  - `world_docs.py`: contact sheet and the README section;
  - `build_world.sh`: runs everything.
- **Changed**:
  - `textures.py`: new `heartwood.png`;
  - `make_docs.py`: appends `world_readme.md`;
  - `build_all.py`: keeps `manifest.world`.
- **Output**:
  - `models/world/{fbx,previews,manifest.json,layout.json,fitcheck_world.txt,contact_sheet_world.png}`;
  - the README "World pieces" section.

Rebuild: `models/_src/build_world.sh` (about 4 minutes).
