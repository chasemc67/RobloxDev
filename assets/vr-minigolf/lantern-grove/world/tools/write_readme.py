"""Write world/README.md from world.json (tables) + hand-written guidance and vista prompts."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

w = W.load_world()
val = json.load(open(os.path.join(W.WORLD_DIR, "validation_latest.json")))
b = w["bounds"]
t = w["hollow_tree"]
hm = w["heightmap"]
H = {h["number"]: h for h in w["holes"]}


def bearing(a, c):
    dx, dz = c[0] - a[0], c[2] - a[2]
    return round(math.degrees(math.atan2(dx, -dz)) % 360), round(math.hypot(dx, dz))


L = []
A = L.append
A("# Lantern Grove: continuous world\n")
A("One Walkabout-style world for the 9 Lantern Grove holes, at different heights and joined by walkways, stairs, cliffs and water, "
  "with scenery out to the horizon. Everything is generated from `world.json` by the scripts in `tools/`, and `../holes.json` is only read, never changed. "
  "Units: **studs, +Y up, +X east, -Z north (map up)**. **1 stud = 0.3 m**.\n")
A(f"**World:** terrain {b['size'][0]:.0f} x {b['size'][1]:.0f} studs ({b['size'][0]*0.3:.0f} x {b['size'][1]*0.3:.0f} m), x {b['x'][0]:.0f}..{b['x'][1]:.0f}, z {b['z'][0]:.0f}..{b['z'][1]:.0f}, "
  f"heights 4..146. Backdrop meshes go out to r 2400. **Walk H1 cup to H9 tee: {val['total_walk']:.0f} studs ({val['total_walk']*0.3:.0f} m).** "
  f"Validation: **{'CLEAN' if val['clean'] else 'FAILING'}** (log in `validation.md`).\n")
A("Story arc as you walk: spawn on the **sunny forest-edge meadow** (SE, H1-H2). Climb the Toadstool Stair to the **Mushroom Village** terraces "
  "(E, H3 at y44, H4 at y48, the highest hole). Go past Lookout Rock and down to the **upper valley**, where Lantern Brook leaves the Grand Falls plunge pool (H5). "
  "Follow the brook down its **west bank** past Twin Falls, the mill (H6) and the three-step cascade (H7). Then climb the **Root Stair** to the giant hollow tree's roots (H8) "
  "and walk through the Heartwood Door to play **H9 inside the trunk**. The tree stands west of the valley, so from the first holes it is backlit by the golden-hour sun.\n")

A("## Files\n")
A("| File | What it is | How to use it |\n|---|---|---|")
A("| `world.json` | Source of truth: bounds, hole placements, terrain recipe, stream, mere, waterfalls, mill flume, walkways and stairs, tree, POIs, lanterns, backdrop pieces, spawn | Read with code. Every other file is generated from it |")
A(f"| `heightmap.png` | 16-bit grayscale, {int(b['size'][0]/hm['stud_per_px'])}x{int(b['size'][1]/hm['stud_per_px'])} px, **1 px = {hm['stud_per_px']:.0f} stud** | Pixel (col i, row j) centre maps to x = {b['x'][0]:.0f} + i + 0.5, z = {b['z'][0]:.0f} + j + 0.5 (row 0 = north edge, col 0 = west edge). y = gray/65535 x {hm['y_max']:.0f} (black = y 0, white = y {hm['y_max']:.0f}) |")
A("| `heightmap-8bit.png` | Same, 8-bit preview (y = gray/255 x 140, about 0.55 stud per level) | Preview only, or for importers that need 8-bit |")
A("| `materials-map.png` | Same pixel grid. Colours are Roblox default terrain material colours | Colormap for the Terrain importer, or classify pixels by the legend below |")
A("| `materials-legend.png` | Legend image for the material map | - |")
A("| `terrain-4stud.json` | 200x200 cells of 4 studs (Roblox voxel size): `height`, `water` surface (or null), `mat` index | Easiest input for a Luau terrain-building script (see job list) |")
A("| `world-map.png` | Annotated plan: holes with par, 4-stud contours (labels every 20), stream, waterfalls, walkways with stair ticks, tree, POIs, lanterns, scale bar, north arrow | For humans and bots |")
A("| `world-map-base.png` | Same plan with shapes only and no text | Reference image for an image generator |")
A("| `validation.md` | Log of every validator run (iterations) | - |")
A("| `tools/worldlib.py` | Transforms + the deterministic heightfield `height_at()` | Shared by all scripts |")
A("| `tools/build_world.py` | Authoring script that writes world.json | Edit placements, paths and regions here, then re-run everything |")
A("| `tools/validate.py` | Checks overlap, felt vs terrain, walkways, tree line of sight and walk length | `python3 tools/validate.py \"note\"` appends to validation.md |")
A("| `tools/make_maps.py` | Writes the PNGs and terrain-4stud.json | - |")
A("| `tools/write_readme.py` | Writes this README | - |")
A("\nRegenerate: `cd world && python3 tools/build_world.py && python3 tools/validate.py \"what changed\" && python3 tools/make_maps.py && python3 tools/write_readme.py`.\n")

A("## Placing the holes (exact)\n")
A("For every holes.json element of hole N (felt, walls, hazards, cup, tee, moving-part pivots, teleports, decoration anchors), apply this to its **local** coordinates:\n")
A("```\nx' =  lx*cos(yaw) + lz*sin(yaw) + origin.x\nz' = -lx*sin(yaw) + lz*cos(yaw) + origin.z\ny' =  ly + origin.y\npiece_yaw_world = piece.yaw + yaw\n```")
A("This is a rotation about +Y (right-handed, positive = counter-clockwise in the map view) followed by a translation. In Roblox:\n")
A("```lua\nlocal holeRoot = CFrame.new(origin[1], origin[2], origin[3]) * CFrame.Angles(0, math.rad(yaw_deg), 0)\n"
  "part.CFrame = holeRoot * localCFrame   -- localCFrame built from holes.json exactly as before\n"
  "-- axes (moving parts, teleport exit dir) rotate only: holeRoot:VectorToWorldSpace(axis)\n```")
A("Check: yaw 90 turns local -Z (the play direction) to world -X (west), and yaw 180 turns it to world +Z (south). **Ignore `world_offset`/`world_yaw` in holes.json**, because they belong to the old flat layout.\n")
A("| Hole | Par | origin [x, y, z] | yaw | felt y | footprint x / z | Surroundings |\n|---|---|---|---|---|---|---|")
hj = W.load_holes()
for h in w["holes"]:
    pl = h["placement"]
    bb = h["footprint_bbox"]
    A(f"| H{h['number']} {h['name']} | {h['par']} | {pl['origin']} | {pl['yaw_deg']} | {h['felt_y_range'][0]}..{h['felt_y_range'][1]} | "
      f"{bb['x'][0]:.0f}..{bb['x'][1]:.0f} / {bb['z'][0]:.0f}..{bb['z'][1]:.0f} | {h['surroundings']} |")
A(f"\nSpawn: `{w['spawn']['pos']}` in Welcome Plaza, facing H1's tee `{H[1]['tee_world']}`.\n")

A("## Hollow tree (H9 is inside it)\n")
A(f"- Trunk centre `[{t['center'][0]}, {t['base_y']}, {t['center'][2]}]`, the centre of the minimal enclosing circle of H9's transformed felt+walls (radius {t['h9_footprint_circle']['radius']}).")
A(f"- **Interior radius {t['trunk_inner_radius']}** (5 studs of walking room around H9), wall {t['wall_thickness']}, **outer radius {t['trunk_outer_radius']}** (trunk {2*t['trunk_outer_radius']:.0f} studs = {2*t['trunk_outer_radius']*0.3:.0f} m across). Roots flare to r {t['root_flare_radius']}.")
A(f"- Trunk is {t['trunk_height']:.0f} tall. The hollow is open up to y {t['oculus']['y']}, with an oculus (r {t['oculus']['radius']:.0f}) that throws a light shaft onto the heart. "
  f"The crown centre is at y {t['crown']['center_y']}, r {t['crown']['radius_xz']:.0f}, {t['crown']['height']:.0f} tall, so the top is about y {t['crown']['center_y'] + t['crown']['height']/2:.0f} ({(t['crown']['center_y'] + t['crown']['height']/2 - t['base_y'])*0.3:.0f} m above its base).")
A(f"- **Heartwood Door**: an arch {t['doorway']['width']:.0f} wide x {t['doorway']['height']:.0f} high at angle {t['doorway']['angle_deg']} deg (atan2(dz,dx), south-east side), outer point `{t['doorway']['outer_point']}`. Walkway p_h8_h9 passes through it to H9's tee.")
A("- The existing `models/fbx/hollow_tree.fbx` (about 49x57x59) is **too small** to contain H9. Use it as a sister tree in the background. A new world-scale shell is listed below.\n")

A("## Water\n")
A(f"- **{w['stream']['name']}** (stream polyline in world.json, north to south): highland spring y81, then Grand Falls to the plunge pool (39), H5's water hazard (37.0, the same as the stream), Twin Falls (to 29.8), the mill take-off, the 3-step cascade into H7's pool (23.0, the same as the stream), Lantern Falls (to 9.2), and Lantern Mere (8). "
  "Width 6-16 and bed depth 3. Fill Water from the bed up to `level`, which interpolates linearly between vertices.")
A("- **Lantern Mere**: ellipse centre (14, 146), radii 82 x 52, water at y 8, with a 10-stud sandy beach.")
A("- **Mill flume**: a timber trough at ground level from the Twin pool to the mill house and H6's mill-race hazard (29.2). A plank step crosses it where the Twin Falls Steps walkway passes.")
A("| Waterfall | top [x,y,z] | bottom | drop | width |\n|---|---|---|---|---|")
for wf in w["waterfalls"]:
    A(f"| {wf['name']} | {wf['top']} | {wf['bottom']} | {wf['drop']} | {wf['width']} |")
A("")

A("## Walkways\n")
A("Every walkway runs from cup to next tee. It leaves the green over the rail (segment `on_hole`) and reaches the tee from behind. Segments: `walk`/`ramp` (max grade 10%), "
  "`stairs` (one flight: steps x rise, tread 1.5, rise 0.8 or less, at most 10 steps per flight), and `landing` (flat, 4 studs between flights). Width 6 (7 at the Heartwood Door, 8 for the Welcome Walk). "
  "The terrain under each walkway is graded to its profile, and under stairs it is graded to the nosing line minus 0.6 so step parts sit on it.\n")
A("| Walkway | Name | Length | Climb | Steps | Note |\n|---|---|---|---|---|---|")
for p in w["paths"]:
    steps = sum(s.get("steps", 0) for s in p["segments"])
    climb = p["segments"][-1]["end"][1] - p["segments"][0]["start"][1]
    A(f"| {p['id']} | {p['name']} | {p['length']:.0f} | {climb:+.1f} | {steps} | {p['note']} |")
A(f"\nLantern posts: {w['lanterns']['count']} points (`world.json lanterns.points`), every 10 studs alternating sides, 1 stud outside the walkway edge. Use lantern_post.fbx with lantern_medium plus a PointLight (range 8). Stair runs use newel posts.\n")

A("## Materials map legend\n")
A("| Key | Roblox material | RGB | Rule |\n|---|---|---|---|")
for m in w["materials"]["legend"]:
    A(f"| {m['key']} | {m['roblox']} | {tuple(m['rgb'])} | {m['rule']} |")
A("")

A("## Terrain job list (RobloxDevBot)\n")
A(f"""1. **Clear** the region x {b['x'][0]:.0f}..{b['x'][1]:.0f}, z {b['z'][0]:.0f}..{b['z'][1]:.0f}, y -10..160.
2. **Heightfield.** Choose one of:
   - *Import (Terrain Editor > Import)*: Heightmap = `heightmap.png` (use `heightmap-8bit.png` if the importer rejects 16-bit), Colormap = `materials-map.png`. Region **size (800, 140, 800)**, region **centre (40, 70, 0)**, so the min corner is (-360, 0, -400). Black = y 0, white = y 140. Afterwards spot-check H1's tee pad at (190, 23.6, 170) and the H9 floor at (-57.6, 39.6, 30.7).
   - *Script (recommended, exact)*: read `terrain-4stud.json`. For each cell, `Terrain:FillBlock(CFrame.new(x, (height-12)/2 ... ), Vector3.new(4, height+12, 4), material)` from y -12 up to `height`, or use WriteVoxels with occupancy taken from the fractional height in the top voxel. Mud goes under water cells.
3. **Water**: for every cell with `water` not null, fill Water from the terrain surface up to the water y (the stream, Lantern Mere, the H5 and H7 hazard pools). Then fill H6's mill-race hazard (29.2) and add the timber flume.
4. **Hole pads**: place each hole with the transform above. Then, for every felt piece, `FillBlock` **Air** over the felt rectangle plus 0.5 from felt bottom to 6 above, so smoothed voxels never poke through the felt. Rails can go down into the terrain.
5. **Cliffs**: rock faces are the slopes over 40 deg on the material map (highland scarp, village terrace walls, Twin and Lantern Falls lips, the tree mound). Dress them with the rock kit pieces.
6. **Walkways**: paint `Ground` (already in the colormap) and add plank edging. Build each `stairs` segment as `steps` blocks (tread 1.5, rise as given, width = path width), with a 4-stud landing between flights. Add handrails on the Toadstool Stair and the Root Stair, which have the biggest drops. A plank step goes over the mill flume.
7. **Tree**: place the world-scale trunk shell at the trunk centre with the doorway at {t['doorway']['angle_deg']} deg. Floor = terrain (y {t['base_y']}). Add the crown, roots over H8, and a SurfaceLight shaft from the oculus.
8. **Waterfalls**: Beams plus mist ParticleEmitters at each waterfall top/bottom (table above). Add a Sound per falls with a 60-stud rolloff.
9. **Lanterns**: place posts at `lanterns.points` (54). Also put lantern strings at Toadstool Square, Lookout Rock and the Heartwood Door.
10. **Lighting**: as in ../course.md. Sun from the WSW so the tree is backlit from H1-H4. At night the moon rises behind the tree. Atmosphere density 0.32 hides the terrain edge behind the backdrop.
11. **Edges**: put invisible walls at the walkway edges where the drop is more than 4 studs (stairs and the cliff paths), plus a soft boundary at the rim hills (r about 0.8 of the rim).
""")

A("## Background pieces (3D Model Bot)\n")
A("All pieces are low-detail and non-colliding. Positions are world studs: base centre, with y = terrain height where it matters. Each piece is listed in `world.json backdrop.pieces` with id, pos, size and yaw.\n")
A("| id | kind | pos [x,y,z] | size [x,y,z] studs | notes |\n|---|---|---|---|---|")
for pc in w["backdrop"]["pieces"]:
    if pc["kind"] in ("tree_line_cluster", "distant_mountain", "far_forest_hill"):
        continue
    A(f"| {pc['id']} | {pc['kind']} | {pc['pos']} | {pc['size']} | {pc.get('note','')} |")
tl = [p for p in w["backdrop"]["pieces"] if p["kind"] == "tree_line_cluster"]
mt = [p for p in w["backdrop"]["pieces"] if p["kind"] == "distant_mountain"]
fh = [p for p in w["backdrop"]["pieces"] if p["kind"] == "far_forest_hill"]
A(f"\n**Rings** (positions for every instance are in world.json):\n")
A(f"- **Tree line**: {len(tl)} autumn tree clumps of 40 x 35-55 x 40 on the rim hills (superellipse r 0.88, terrain y 30-110). Use 4 colour mixes and 2-3 mesh variants, rotated randomly. Examples: {tl[0]['pos']}, {tl[14]['pos']}, {tl[28]['pos']}, {tl[42]['pos']}.")
A(f"- **Far forested hills**: {len(fh)} impostor hill shells r 530-640 from (40, 0), 240-320 wide, 70-130 tall, base y 10, outside the terrain. Hazed autumn forest.")
A(f"- **Distant mountains**: {len(mt)} silhouettes r 1150-1550, 420-700 wide, about 220-460 tall (tallest north and west). Atmospheric violet `#7C7FA8` to `#A9A3C7`. Positions: " +
  ", ".join(f"{m['id'][-2:]} {m['pos'][0]},{m['pos'][2]} h{m['size'][1]}" for m in mt) + ".")
A("- **Sky**: sun at azimuth 242 and elevation 14 (WSW, golden hour). The night moon rises behind the tree. 7 cloud cards at r 1800-2400 and y 500-850, and 24 sky lanterns around the crown.\n")

# ---------------------------------------------------------------- vista prompts
h1 = H[1]["tee_world"]
bt1 = bearing(h1, t["center"])
lr = [p for p in w["pois"] if p["id"] == "lookout_rock"][0]["pos"]
A("## vista_prompts\n")
A("Four image prompts, each describing what is actually visible from the stated point given the placements in world.json. "
  "Common style: cozy autumn fairy-forest mini golf in VR, golden hour, warm hazy atmosphere, chunky hand-made shapes, storybook, high detail, no text.\n")
A(f"""### 1. H1 tee looking across to the giant tree
Camera: H1 tee {h1}, eye height 5.5 (y 29.5), looking WNW (bearing {bt1[0]} deg, slightly down), 70 deg FOV.
> First-person VR view from the first tee of a fairy-forest mini golf course on a sunny meadow at golden hour. In the foreground, a green felt lane with low stone-and-oak rails runs straight ahead. About 20 steps away, a timber torii arch hung with two paper lanterns stands over a gentle ramp. A carved welcome sign is on the left and a big red maple on the right. Past the hole, the grassy meadow falls away to the left to a calm oval lake 30-50 m away and 5 m lower, where tiny paper-lantern boats drift and a sandy beach curves round. Beyond the lake, a white ribbon of waterfall drops off a mossy cliff into the lake's inflow. Across the valley, about 90 m away, rises a colossal hollow golden tree: a 27 m wide gnarled trunk on a root-bound mound with an arched glowing doorway. Its huge orange-and-gold crown towers about 55 m above eye level. A low sun just out of frame to the left gives it glowing rim light, and sky lanterns float around it. On the right edge of the frame, a rocky cliff terrace rises 6 m with red-capped mushroom houses on top. Behind everything, forested autumn hills roll into violet distant mountains. Warm haze, long shadows, magical and inviting.

### 2. High overlook: several holes and Grand Falls (Lookout Rock)
Camera: Lookout Rock {lr}, eye y 53, looking bearing 293 deg (WNW) over the upper valley, wide 100 deg FOV.
> Elevated view from a wooden lookout deck on a rocky knoll at the corner of a mushroom village, looking down over a lush valley at golden hour. Straight ahead, 22 m away and 3 m lower, a mini golf hole crosses a clear babbling stream on two bridges: a narrow arched root bridge and a covered plank bridge with a shingle roof. Just left of it the stream tumbles down a 2 m rock ledge as twin waterfalls. Further down the stream's left bank, about 36 m away, an old timber water mill turns its paddle wheel beside a mini golf hole on a grassy terrace. Beyond that, the stream drops down three stepped rock terraces into a pool beside another stepped mini golf hole. On the far right, about 40 m away, a tall 12 m waterfall pours off a long cliff of grey rock and autumn forest into a misty plunge pool. On the horizon to the left stands the colossal hollow golden tree, 75 m away, with its glowing canopy filling the sky. Lantern-lit wooden stairs zig-zag from the deck down to the valley. Autumn trees in red, orange and gold, warm atmospheric haze, storybook detail.

### 3. Mid-course walkway between holes (Root Stair, H7 to H8)
Camera: foot of the Root Stair (22, 23.2, -10), eye y 28.7, looking up the stairs to the NNW (bearing 326 deg), 75 deg FOV.
> First-person VR view on a cozy forest walkway between mini golf holes. A 2 m wide wooden staircase climbs ahead: 10 chunky steps up to a small landing, then 6 more steps onto a raised terrace of mossy roots about 4 m higher. Two enormous gnarled tree roots arch over the landing like a gateway. Paper lantern posts glow amber every 3 m, alternating left and right. At the top, the next mini golf tee sits among giant surface roots. On the left, about 30 m away, the base of the colossal hollow golden tree fills that half of the view: a wall of furrowed bark 27 m wide on a root-bound mound, with huge roots spilling toward the stairs and its golden canopy overhead. On the right, through the trees, a stream cascades down three rock steps into a pool. Fallen orange maple leaves on the steps, ferns and glowing mushrooms along the edges, dappled golden late-afternoon light.

### 4. Aerial overview
Camera: high above the south-east meadow at (200, 320, 330), looking north-west and down about 40 deg, 60 deg FOV.
> Aerial overview of a magical autumn mini golf world at golden hour, like a cozy VR game map. In the foreground, a sunny meadow with a spawn plaza and two holes beside red maples. Right of centre, lantern-lined paths climb a switchback stair onto rocky terraces with a mushroom village of red-capped houses and two more holes. In the middle distance lies a large calm oval lake with a sandy beach and tiny lantern boats. A sparkling stream enters it from the north over a waterfall, then winds up the valley past a three-step cascade hole, a water-mill hole and a stream-crossing hole with two bridges, up to a tall waterfall spilling off a long cliff of grey rock and forest that walls in the north. Left of centre, beyond the lake, rises the colossal hollow golden tree on a root-bound mound, with a glowing doorway and a mini golf hole winding among its roots. Its vast orange-gold canopy is the tallest thing in the scene. Walkways with lantern posts link every hole. Forested hills in red, orange and gold ring the whole world, with hazy violet mountains and soft golden clouds on the horizon. Tilt-shift miniature feel, warm light, high detail.
""")
A("## Validation summary\n")
A(f"Latest run: iteration {val['iteration']}, {'CLEAN' if val['clean'] else 'FAIL: ' + '; '.join(val['fails'])}. Walk {val['total_walk']:.0f} studs.\n")
for i in val["info"]:
    A(f"- {i}")
open(os.path.join(W.WORLD_DIR, "README.md"), "w").write("\n".join(L) + "\n")
print("README.md written")
