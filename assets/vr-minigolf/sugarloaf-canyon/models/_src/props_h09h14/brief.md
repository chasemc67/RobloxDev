# Task: write gen_tankdock.py (pure Python 3 + numpy, no Blender) in this directory.
Model it on ../props_batch4/gen_batch4.py: copy its Part class and helpers (box, bar, prism_*, cyl, loft, hexa, octa, mk/anchor) and its output format.
Output parts.json next to the script (same schema as gen_batch4.py writes: id, hole, anchor, notes, envelope, env_boxes, sweep_boxes, groups...). Coords are Roblox hole-local (x, y up, z), geometry relative to the anchor position (base-centre pivot = anchor). Read holes.json from /workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/holes.json.
Allowed material keys ONLY: Timber, TimberWeathered, Iron, Brass, Rope, Water, plus new ore key 'RockCandyLilac' (lilac rock candy). NO red, pink-red, cream, MintWhite, PepRed, Canvas, CreamTaffy, Cherry (reserved for moving parts).
Budget: each part < 3000 triangles total (count quads as 2). Cylinders n=12..16.

## Part 1: h09_water_tank. anchor = holes.json h09 decoration_anchors 'water_tank' (position [-11.65,0,-40], approx_size [4,8,4]).
All geometry inside x -13.6..-9.7, y 0..8, z -41.95..-38.05 (hole-local). rail7 outer face is at x -9.5, so keep >= 0.15 off it (x <= -9.65).
- 4 square TimberWeathered legs (0.35) from ground y 0 to y 3.2, slightly splayed (feet at +-1.75 from anchor, tops +-1.45), cross braces (X on each side) Timber 0.18, Iron foot plates 0.06 tall.
- Platform: Timber plank deck y 3.2..3.45, 3.6x3.6 square, made of 5 planks with small gaps.
- Barrel tank: Timber vertical body, slightly bulged (loft of 16-sided rings: r 1.55 at y3.45, 1.7 at mid y5.6, 1.55 at y7.6), 3 Iron hoops (thin rings r+0.04, 0.18 tall) at y 3.9, 5.6, 7.2. Conical TimberWeathered roof y 7.6..8.0 (r 1.75 -> small cap), Iron knob top <= 8.0.
- Short Iron spout: pipe from tank side at y 4.0 pointing -x? NO: point it toward +z or -z (not toward rail7 at +x); a 0.6 long pipe r 0.12 plus a down-turned 0.4 nozzle and a Brass valve wheel. Keep all inside the box above.
- Rope coil hanging from one leg optional (Rope), Water: a thin disc at tank top inside r 1.45 at y 7.55 is NOT needed (roof covers); skip.
## Part 2: h14_loading_dock. anchor = holes.json h14 'loading_dock' (position [0,0,-33]). The holes.json anchor box sits on the ramp felt (x -4..4, z -36..-30), which must stay clear, so build the dock WEST of the ramp, outside rail2 (x -4.25 thick 0.5 -> outer face -4.5) and north of nothing; rail3 runs at z -35.75 (z -36..-35.5) for x -8.5..-4.0; trestle leg/foot of cableway_trestle near x -5.0..-4.6, z -24.6..-23.4 (stay z <= -24.9).
Footprint: x -9.6..-4.65, z -35.35..-25.2, y 0..2.6. Set env_boxes = [[[-9.6,0,-35.35],[-4.65,2.6,-25.2]]].
- Low deck: Timber planks running along x (each 0.9 wide in z, small 0.05 gaps), top y 0.95, 0.15 thick, on a TimberWeathered frame; 6 square posts 0.35 down to y 0 with Iron post caps/feet; Iron band strap along the deck edge facing the ramp (x ~ -4.75, top face).
- Two short steps on the -x side (outer) down to ground (Timber).
- 2..3 ore crates: Timber boxes ~1.2 cube with TimberWeathered edge slats and Iron corner bands, one heaped with RockCandyLilac octahedra crystals (top <= 2.6). Keep crates at x <= -5.6 (away from the rail).
- One small Iron mine-cart wheel-stop or a coil of Rope on a post is fine.
Notes: put a short honest note string in p.notes for each part describing placement and clearances.
At the end print tris per part. Also write a quick self-check: assert all verts inside env boxes, min x of h09 >= -13.65 and max x <= -9.65; h14 all x <= -4.65 and z <= -25.2, z >= -35.35.
