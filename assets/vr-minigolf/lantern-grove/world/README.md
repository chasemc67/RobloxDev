# Lantern Grove: continuous world

One Walkabout-style world for the 9 Lantern Grove holes, at different heights and joined by walkways, stairs, cliffs and water, with scenery out to the horizon. Everything is generated from `world.json` by the scripts in `tools/`, and `../holes.json` is only read, never changed. Units: **studs, +Y up, +X east, -Z north (map up)**. **1 stud = 0.3 m**.

**World:** terrain 800 x 800 studs (240 x 240 m), x -360..440, z -400..400, heights 4..146. Backdrop meshes go out to r 2400. **Walk H1 cup to H9 tee: 641 studs (192 m).** Validation: **CLEAN** (log in `validation.md`).

Story arc as you walk: spawn on the **sunny forest-edge meadow** (SE, H1-H2). Climb the Toadstool Stair to the **Mushroom Village** terraces (E, H3 at y44, H4 at y48, the highest hole). Go past Lookout Rock and down to the **upper valley**, where Lantern Brook leaves the Grand Falls plunge pool (H5). Follow the brook down its **west bank** past Twin Falls, the mill (H6) and the three-step cascade (H7). Then climb the **Root Stair** to the giant hollow tree's roots (H8) and walk through the Heartwood Door to play **H9 inside the trunk**. The tree stands west of the valley, so from the first holes it is backlit by the golden-hour sun.

## Files

| File | What it is | How to use it |
|---|---|---|
| `world.json` | Source of truth: bounds, hole placements, terrain recipe, stream, mere, waterfalls, mill flume, walkways and stairs, tree, POIs, lanterns, backdrop pieces, spawn | Read with code. Every other file is generated from it |
| `heightmap.png` | 16-bit grayscale, 800x800 px, **1 px = 1 stud** | Pixel (col i, row j) centre maps to x = -360 + i + 0.5, z = -400 + j + 0.5 (row 0 = north edge, col 0 = west edge). y = gray/65535 x 140 (black = y 0, white = y 140) |
| `heightmap-8bit.png` | Same, 8-bit preview (y = gray/255 x 140, about 0.55 stud per level) | Preview only, or for importers that need 8-bit |
| `materials-map.png` | Same pixel grid. Colours are Roblox default terrain material colours | Colormap for the Terrain importer, or classify pixels by the legend below |
| `materials-legend.png` | Legend image for the material map | - |
| `terrain-4stud.json` | 200x200 cells of 4 studs (Roblox voxel size): `height`, `water` surface (or null), `mat` index | Easiest input for a Luau terrain-building script (see job list) |
| `world-map.png` | Annotated plan: holes with par, 4-stud contours (labels every 20), stream, waterfalls, walkways with stair ticks, tree, POIs, lanterns, scale bar, north arrow | For humans and bots |
| `world-map-base.png` | Same plan with shapes only and no text | Reference image for an image generator |
| `validation.md` | Log of every validator run (iterations) | - |
| `tools/worldlib.py` | Transforms + the deterministic heightfield `height_at()` | Shared by all scripts |
| `tools/build_world.py` | Authoring script that writes world.json | Edit placements, paths and regions here, then re-run everything |
| `tools/validate.py` | Checks overlap, felt vs terrain, walkways, tree line of sight and walk length | `python3 tools/validate.py "note"` appends to validation.md |
| `tools/make_maps.py` | Writes the PNGs and terrain-4stud.json | - |
| `tools/write_readme.py` | Writes this README | - |

Regenerate: `cd world && python3 tools/build_world.py && python3 tools/validate.py "what changed" && python3 tools/make_maps.py && python3 tools/write_readme.py`.

## Placing the holes (exact)

For every holes.json element of hole N (felt, walls, hazards, cup, tee, moving-part pivots, teleports, decoration anchors), apply this to its **local** coordinates:

```
x' =  lx*cos(yaw) + lz*sin(yaw) + origin.x
z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z
y' =  ly + origin.y
piece_yaw_world = piece.yaw + yaw
```
This is a rotation about +Y (right-handed, positive = counter-clockwise in the map view) followed by a translation. In Roblox:

```lua
local holeRoot = CFrame.new(origin[1], origin[2], origin[3]) * CFrame.Angles(0, math.rad(yaw_deg), 0)
part.CFrame = holeRoot * localCFrame   -- localCFrame built from holes.json exactly as before
-- axes (moving parts, teleport exit dir) rotate only: holeRoot:VectorToWorldSpace(axis)
```
Check: yaw 90 turns local -Z (the play direction) to world -X (west), and yaw 180 turns it to world +Z (south). **Ignore `world_offset`/`world_yaw` in holes.json**, because they belong to the old flat layout.

| Hole | Par | origin [x, y, z] | yaw | felt y | footprint x / z | Surroundings |
|---|---|---|---|---|---|---|
| H1 Lantern Gate | 2 | [190.0, 24.0, 170.0] | 0.0 | 24.0..24.5 | 178..194 / 133..172 | Sunny forest-edge meadow (y~24) south-east; red maples, lantern torii; Lantern Mere glitters to the west, the giant tree on the far side |
| H2 Acorn Ledge | 2 | [215.0, 26.0, 128.0] | 0.0 | 24.5..26.0 | 206..224 / 90..130 | Acorn Knoll, a low grassy rise (y~26) beside the meadow; village cliffs rise to the north |
| H3 Toadstool Row | 3 | [150.0, 44.0, 40.0] | 0.0 | 44.0..45.2 | 144..174 / 6..42 | Mushroom Village lower tier (y~44) on a rock-faced terrace above the meadow; mushroom houses around the S-bend |
| H4 Spore Spinner | 3 | [185.0, 48.0, -12.0] | 0.0 | 48.0..48.6 | 178..192 / -58..-10 | Mushroom Village upper tier (y~48), highest hole; looks west over the valley to Grand Falls and the tree |
| H5 Rootbridge Crossing | 3 | [100.0, 38.0, -110.0] | 90.0 | 38.0..38.4 | 58..102 / -116..-94 | Upper valley (y~38) where Lantern Brook leaves the Grand Falls plunge pool; Grand Falls 90 studs north |
| H6 Mill Wheel Run | 3 | [45.0, 30.0, -70.0] | 180.0 | 30.0..30.25 | 24..50 / -72..-42 | Mill terrace (y~30) on the west bank below Twin Falls; mill flume from the Twin pool |
| H7 Cascade Steps | 3 | [40.0, 26.0, -28.0] | 180.0 | 23.6..26.0 | 30..50 / -30..12 | Cascade terraces (y~26->23.6) on the west bank beside the 3-step cascade and its pool |
| H8 Firefly Hollow | 4 | [-10.0, 36.0, -24.0] | 180.0 | 36.0..38.7 | -20..12 / -26..24 | Root terrace (y~36) among giant surface roots right at the trunk of the hollow tree |
| H9 Heart of the Grove | 4 | [-57.6, 40.0, 30.7] | 62.3 | 39.2..42.2 | -100..-54 / -23..35 | INSIDE the hollow tree trunk (floor y~39.6), lantern-lit hollow opening to the crown |

Spawn: `[206.0, 23.6, 214.0]` in Welcome Plaza, facing H1's tee `[190.0, 24.0, 170.0]`.

## Hollow tree (H9 is inside it)

- Trunk centre `[-74.0, 39.6, 6.0]`, the centre of the minimal enclosing circle of H9's transformed felt+walls (radius 33.84).
- **Interior radius 38.84** (5 studs of walking room around H9), wall 7.0, **outer radius 45.84** (trunk 92 studs = 28 m across). Roots flare to r 65.8.
- Trunk is 100 tall. The hollow is open up to y 117.6, with an oculus (r 14) that throws a light shaft onto the heart. The crown centre is at y 173.6, r 88, 78 tall, so the top is about y 213 (52 m above its base).
- **Heartwood Door**: an arch 14 wide x 20 high at angle 53.1 deg (atan2(dz,dx), south-east side), outer point `[-44.68, 39.6, 45.06]`. Walkway p_h8_h9 passes through it to H9's tee.
- The existing `models/fbx/hollow_tree.fbx` (about 49x57x59) is **too small** to contain H9. Use it as a sister tree in the background. A new world-scale shell is listed below.

## Water

- **Lantern Brook** (stream polyline in world.json, north to south): highland spring y81, then Grand Falls to the plunge pool (39), H5's water hazard (37.0, the same as the stream), Twin Falls (to 29.8), the mill take-off, the 3-step cascade into H7's pool (23.0, the same as the stream), Lantern Falls (to 9.2), and Lantern Mere (8). Width 6-16 and bed depth 3. Fill Water from the bed up to `level`, which interpolates linearly between vertices.
- **Lantern Mere**: ellipse centre (14, 146), radii 82 x 52, water at y 8, with a 10-stud sandy beach.
- **Mill flume**: a timber trough at ground level from the Twin pool to the mill house and H6's mill-race hazard (29.2). A plank step crosses it where the Twin Falls Steps walkway passes.
| Waterfall | top [x,y,z] | bottom | drop | width |
|---|---|---|---|---|
| Grand Falls | [114, 77.8, -205] | [112, 39.0, -199] | 38.8 | 9.0 |
| Twin Falls | [77.5, 37.0, -90] | [76, 29.8, -86] | 7.2 | 9.0 |
| Cascade Step 1 | [62, 29.4, -36] | [60, 27.3, -32] | 2.1 | 7.0 |
| Cascade Step 2 | [58, 27.2, -26] | [57, 25.1, -22] | 2.1 | 7.0 |
| Cascade Step 3 (into H7 pool) | [56, 25.0, -17] | [54.5, 23.0, -14] | 2.0 | 6.0 |
| Lantern Falls | [38, 22.2, 57] | [36, 9.2, 62] | 13.0 | 8.0 |
| Mill Spring (H6 decor) | [14.999999999999996, 41.25, -46.0] | [20.999999999999996, 30.25, -46.0] | 11.0 | 4.0 |

## Walkways

Every walkway runs from cup to next tee. It leaves the green over the rail (segment `on_hole`) and reaches the tee from behind. Segments: `walk`/`ramp` (max grade 10%), `stairs` (one flight: steps x rise, tread 1.5, rise 0.8 or less, at most 10 steps per flight), and `landing` (flat, 4 studs between flights). Width 6 (7 at the Heartwood Door, 8 for the Welcome Walk). The terrain under each walkway is graded to its profile, and under stairs it is graded to the nosing line minus 0.6 so step parts sit on it.

| Walkway | Name | Length | Climb | Steps | Note |
|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0 | Spawn plaza -> under the lantern torii view to H1 tee |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 0 |  |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 25 | Two stair runs with a mid terrace up the village cliff (+20) |
| p_h3_h4 | Village Steps | 34 | +4.0 | 5 |  |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 13 | Passes Lookout Rock (village terrace NW corner) then 14 steps down |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 10 | Stairs down the Twin Falls cliff; plank step over the mill flume at z~-80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 6 |  |
| p_h7_h8 | Root Stair | 85 | +12.4 | 16 | Climbs between giant surface roots to the root terrace |
| p_h8_h9 | Heartwood Door | 82 | +2.5 | 4 | Root steps up to the arched doorway in the trunk; H9 is played inside |

Lantern posts: 55 points (`world.json lanterns.points`), every 10 studs alternating sides, 1 stud outside the walkway edge. Use lantern_post.fbx with lantern_medium plus a PointLight (range 8). Stair runs use newel posts.

## Materials map legend

| Key | Roblox material | RGB | Rule |
|---|---|---|---|
| grass | Grass | (106, 127, 63) | default ground |
| leafy | LeafyGrass | (115, 132, 74) | inside material_zones (forest floor, village, roots) |
| rock | Rock | (102, 108, 111) | slope > 40 deg (cliffs, falls, terrace walls) |
| path | Ground | (102, 92, 59) | walkway corridors (width/2) and plazas |
| water | Water | (12, 84, 92) | terrain below a water surface (stream, mere, hazards): paint bed Mud, fill Water to level |
| sand | Sand | (143, 126, 95) | dry ground within 3 studs of the stream / 10 of the mere and < 1.5 above water |

## Terrain job list (RobloxDevBot)

1. **Clear** the region x -360..440, z -400..400, y -10..160.
2. **Heightfield.** Choose one of:
   - *Import (Terrain Editor > Import)*: Heightmap = `heightmap.png` (use `heightmap-8bit.png` if the importer rejects 16-bit), Colormap = `materials-map.png`. Region **size (800, 140, 800)**, region **centre (40, 70, 0)**, so the min corner is (-360, 0, -400). Black = y 0, white = y 140. Afterwards spot-check H1's tee pad at (190, 23.6, 170) and the H9 floor at (-57.6, 39.6, 30.7).
   - *Script (recommended, exact)*: read `terrain-4stud.json`. For each cell, `Terrain:FillBlock(CFrame.new(x, (height-12)/2 ... ), Vector3.new(4, height+12, 4), material)` from y -12 up to `height`, or use WriteVoxels with occupancy taken from the fractional height in the top voxel. Mud goes under water cells.
3. **Water**: for every cell with `water` not null, fill Water from the terrain surface up to the water y (the stream, Lantern Mere, the H5 and H7 hazard pools). Then fill H6's mill-race hazard (29.2) and add the timber flume.
4. **Hole pads**: place each hole with the transform above. Then, for every felt piece, `FillBlock` **Air** over the felt rectangle plus 0.5 from felt bottom to 6 above, so smoothed voxels never poke through the felt. Rails can go down into the terrain.
5. **Cliffs**: rock faces are the slopes over 40 deg on the material map (highland scarp, village terrace walls, Twin and Lantern Falls lips, the tree mound). Dress them with the rock kit pieces.
6. **Walkways**: paint `Ground` (already in the colormap) and add plank edging. Build each `stairs` segment as `steps` blocks (tread 1.5, rise as given, width = path width), with a 4-stud landing between flights. Add handrails on the Toadstool Stair and the Root Stair, which have the biggest drops. A plank step goes over the mill flume.
7. **Tree**: place the world-scale trunk shell at the trunk centre with the doorway at 53.1 deg. Floor = terrain (y 39.6). Add the crown, roots over H8, and a SurfaceLight shaft from the oculus.
8. **Waterfalls**: Beams plus mist ParticleEmitters at each waterfall top/bottom (table above). Add a Sound per falls with a 60-stud rolloff.
9. **Lanterns**: place posts at `lanterns.points` (54). Also put lantern strings at Toadstool Square, Lookout Rock and the Heartwood Door.
10. **Lighting**: as in ../course.md. Sun from the WSW so the tree is backlit from H1-H4. At night the moon rises behind the tree. Atmosphere density 0.32 hides the terrain edge behind the backdrop.
11. **Edges**: put invisible walls at the walkway edges where the drop is more than 4 studs (stairs and the cliff paths), plus a soft boundary at the rim hills (r about 0.8 of the rim).

## Background pieces (3D Model Bot)

All pieces are low-detail and non-colliding. Positions are world studs: base centre, with y = terrain height where it matters. Each piece is listed in `world.json backdrop.pieces` with id, pos, size and yaw.

| id | kind | pos [x,y,z] | size [x,y,z] studs | notes |
|---|---|---|---|---|
| hollow_tree_world_shell | hero_tree | [-74.0, 39.6, 6.0] | [91.7, 100, 91.7] | Trunk shell: outer radius 45.8, inner 38.8, hollow to y+78 with a 14-radius oculus, doorway 14x20 at angle 53 deg; roots flare to r 66 |
| hollow_tree_crown | hero_tree | [-74.0, 139.6, 6.0] | [176, 78, 176] | Golden/orange canopy, base at y+100 above trunk base; lumpy, 5-7 big leaf masses; sky lanterns drift around it |
| grand_falls_curtain | waterfall | [113, 39.0, -202] | [12, 39, 6] | Waterfall mesh/beam curtain 77.8 -> 39, mist particles in the plunge pool |
| twin_falls_curtain | waterfall | [76.8, 29.8, -88] | [10, 7.5, 4] | Two-strand falls 37 -> 29.8 |
| lantern_falls_curtain | waterfall | [37, 9.2, 59.5] | [9, 13, 4] | Falls 22.2 -> 9.2 into the mere inflow pool |
| highland_cliff_kit | rock | [40, 60, -222] | [40, 30, 14] | Modular slate cliff faces (x10-12) dressing the 20-50 stud highland scarp along z ~ -205..-240 |
| terrace_rock_faces | rock | [150, 34, 60] | [24, 12, 6] | Rock facing pieces for the village terrace walls, mill terrace, root terrace and tree mound (x20) |
| old_lantern_tower | background | [60, 84, -262] | [12, 38, 12] | Ruined stone tower with a big amber lantern at top; silhouette on the highlands |
| sister_tree_nw | background | [-190, 32.3, -110] | [60, 90, 60] | Large golden tree (smaller cousin of the hero tree) in the NW forest |
| sister_tree_sw | background | [-150, 15.7, 230] | [55, 80, 55] | Large red maple giant on the SW hills |
| sister_tree_ne | background | [260, 46.7, -150] | [50, 75, 50] | Golden oak giant on the NE shoulder above the village |
| hill_mushroom_houses | background | [290, 44.9, -40] | [30, 25, 30] | Cluster of 3-4 mushroom houses on the east hills (village continues into the distance), lit windows |
| mere_lantern_boats | decor | [14, 8, 146] | [6, 3, 3] | 8 tiny paper-lantern boats drifting on Lantern Mere (slow tween) |
| mere_dock | decor | [80, 8.5, 128] | [14, 3, 5] | Plank dock with lanterns |
| sky_lanterns | sky | [-74.0, 200, 6.0] | [1.5, 2, 1.5] | 24 floating paper lanterns orbiting the crown, y 150-280 |
| cloud_banks | sky | [40.0, 650, 0.0] | [600, 120, 200] | 7 soft golden cumulus cards at r 1800-2400 |

**Rings** (positions for every instance are in world.json):

- **Tree line**: 56 autumn tree clumps of 40 x 35-55 x 40 on the rim hills (superellipse r 0.88, terrain y 30-110). Use 4 colour mixes and 2-3 mesh variants, rotated randomly. Examples: [392.0, 55.8, -1.2], [44.1, 43.5, 352.0], [-312.0, 64.3, -5.5], [45.8, 112.6, -352.0].
- **Far forested hills**: 18 impostor hill shells r 530-640 from (40, 0), 240-320 wide, 70-130 tall, base y 10, outside the terrain. Hazed autumn forest.
- **Distant mountains**: 12 silhouettes r 1150-1550, 420-700 wide, about 220-460 tall (tallest north and west). Atmospheric violet `#7C7FA8` to `#A9A3C7`. Positions: 01 1249,-60 h242, 02 1077,548 h225, 03 752,949 h221, 04 148,1397 h247, 05 -673,926 h341, 06 -989,751 h370, 07 -1258,-50 h387, 08 -1246,-608 h366, 09 -609,-1091 h412, 10 68,-1360 h444, 11 772,-947 h379, 12 1048,-586 h334.
- **Sky**: sun at azimuth 242 and elevation 14 (WSW, golden hour). The night moon rises behind the tree. 7 cloud cards at r 1800-2400 and y 500-850, and 24 sky lanterns around the crown.

## vista_prompts

Four image prompts, each describing what is actually visible from the stated point given the placements in world.json. Common style: cozy autumn fairy-forest mini golf in VR, golden hour, warm hazy atmosphere, chunky hand-made shapes, storybook, high detail, no text.

### 1. H1 tee looking across to the giant tree
Camera: H1 tee [190.0, 24.0, 170.0], eye height 5.5 (y 29.5), looking WNW (bearing 302 deg, slightly down), 70 deg FOV.
> First-person VR view from the first tee of a fairy-forest mini golf course on a sunny meadow at golden hour. In the foreground, a green felt lane with low stone-and-oak rails runs straight ahead. About 20 steps away, a timber torii arch hung with two paper lanterns stands over a gentle ramp. A carved welcome sign is on the left and a big red maple on the right. Past the hole, the grassy meadow falls away to the left to a calm oval lake 30-50 m away and 5 m lower, where tiny paper-lantern boats drift and a sandy beach curves round. Beyond the lake, a white ribbon of waterfall drops off a mossy cliff into the lake's inflow. Across the valley, about 90 m away, rises a colossal hollow golden tree: a 27 m wide gnarled trunk on a root-bound mound with an arched glowing doorway. Its huge orange-and-gold crown towers about 55 m above eye level. A low sun just out of frame to the left gives it glowing rim light, and sky lanterns float around it. On the right edge of the frame, a rocky cliff terrace rises 6 m with red-capped mushroom houses on top. Behind everything, forested autumn hills roll into violet distant mountains. Warm haze, long shadows, magical and inviting.

### 2. High overlook: several holes and Grand Falls (Lookout Rock)
Camera: Lookout Rock [166.0, 47.6, -80.0], eye y 53, looking bearing 293 deg (WNW) over the upper valley, wide 100 deg FOV.
> Elevated view from a wooden lookout deck on a rocky knoll at the corner of a mushroom village, looking down over a lush valley at golden hour. Straight ahead, 22 m away and 3 m lower, a mini golf hole crosses a clear babbling stream on two bridges: a narrow arched root bridge and a covered plank bridge with a shingle roof. Just left of it the stream tumbles down a 2 m rock ledge as twin waterfalls. Further down the stream's left bank, about 36 m away, an old timber water mill turns its paddle wheel beside a mini golf hole on a grassy terrace. Beyond that, the stream drops down three stepped rock terraces into a pool beside another stepped mini golf hole. On the far right, about 40 m away, a tall 12 m waterfall pours off a long cliff of grey rock and autumn forest into a misty plunge pool. On the horizon to the left stands the colossal hollow golden tree, 75 m away, with its glowing canopy filling the sky. Lantern-lit wooden stairs zig-zag from the deck down to the valley. Autumn trees in red, orange and gold, warm atmospheric haze, storybook detail.

### 3. Mid-course walkway between holes (Root Stair, H7 to H8)
Camera: foot of the Root Stair (22, 23.2, -10), eye y 28.7, looking up the stairs to the NNW (bearing 326 deg), 75 deg FOV.
> First-person VR view on a cozy forest walkway between mini golf holes. A 2 m wide wooden staircase climbs ahead: 10 chunky steps up to a small landing, then 6 more steps onto a raised terrace of mossy roots about 4 m higher. Two enormous gnarled tree roots arch over the landing like a gateway. Paper lantern posts glow amber every 3 m, alternating left and right. At the top, the next mini golf tee sits among giant surface roots. On the left, about 30 m away, the base of the colossal hollow golden tree fills that half of the view: a wall of furrowed bark 27 m wide on a root-bound mound, with huge roots spilling toward the stairs and its golden canopy overhead. On the right, through the trees, a stream cascades down three rock steps into a pool. Fallen orange maple leaves on the steps, ferns and glowing mushrooms along the edges, dappled golden late-afternoon light.

### 4. Aerial overview
Camera: high above the south-east meadow at (200, 320, 330), looking north-west and down about 40 deg, 60 deg FOV.
> Aerial overview of a magical autumn mini golf world at golden hour, like a cozy VR game map. In the foreground, a sunny meadow with a spawn plaza and two holes beside red maples. Right of centre, lantern-lined paths climb a switchback stair onto rocky terraces with a mushroom village of red-capped houses and two more holes. In the middle distance lies a large calm oval lake with a sandy beach and tiny lantern boats. A sparkling stream enters it from the north over a waterfall, then winds up the valley past a three-step cascade hole, a water-mill hole and a stream-crossing hole with two bridges, up to a tall waterfall spilling off a long cliff of grey rock and forest that walls in the north. Left of centre, beyond the lake, rises the colossal hollow golden tree on a root-bound mound, with a glowing doorway and a mini golf hole winding among its roots. Its vast orange-gold canopy is the tallest thing in the scene. Walkways with lantern posts link every hole. Forested hills in red, orange and gold ring the whole world, with hazy violet mountains and soft golden clouds on the horizon. Tilt-shift miniature feel, warm light, high detail.

## Validation summary

Latest run: iteration 8, CLEAN. Walk 641 studs.

- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 7.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)
