# start_ship_b2_detail_v3 - mast collider fix

Original v3 release ship (`start_ship_b2_detail_v3/out/start_ship_v3.blend`, sha256 `87b319a5b6308c1d7d3deaac91b4b4e16b651572ac569a14606a8446442cc92f`) with ONE change: collider `COL_Mast_Main` shortened from 157.0 to 98.3 studs along its 18 deg axis (bottom fixed). All visuals, ramps, props, materials, textures, anchors and the other 189 colliders are byte-identical to v3, so the existing v3 previews still apply.

## Files
- `start_ship_v3_mastfix.blend`: full scene (Visual / Ramps / Props / Collision collections, palette packed).
- `fbx/start_ship_b2_visual.fbx` (28 meshes + 4 anchor empties, 49405 tris), `fbx/start_ship_b2_col.fbx` (190 COL boxes), `fbx/RampFlight1_own_origin.fbx`, `fbx/RampLanding_own_origin.fbx`, `fbx/RampFlight2_own_origin.fbx`. Same names as v3.
- `manifest.json`, `fitcheck.json`, `fitcheck.md`, `report.txt`; `src/` holds the release scripts (mastfix.py, export.py, verify.py). `logs/` is scratch (ignored).

## Axes, pivots, placement (unchanged from v3)
- 1 Blender unit = 1 stud. Blender Z-up; Roblox local (x, y, z) = (bx, bz, -by). FBX: axis_forward -Z, axis_up Y, scale 1, FBX_SCALE_UNITS, embedded textures, face smoothing.
- Pivots/origins unchanged; the ramp own-origin FBXs have origin 0. Placement unchanged: **Roblox worldY = localY + 0.6** (water at world Y 0).

## Collision delta
- COL_Mast_Main top centre Roblox local (10.000, 156.924, 50.988) -> (10.000, 101.097, 32.849); world (10.000, 157.524, 50.988) -> (10.000, 101.697, 32.849). Highest collider point world Y 158.297 -> 102.470.
- Bottom centre (10.000, 7.608, 2.472) (unchanged), cross-section 5.00 x 5.00 (unchanged), origin matrix unchanged. Full per-vertex table in fitcheck.md.

## Rebuild (from the workdir; one Blender process at a time)
```
B="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
"$B" -b --factory-startup original_v3.blend --python-exit-code 1 --python out/src/mastfix.py -- out/start_ship_v3_mastfix.blend
"$B" -b --factory-startup out/start_ship_v3_mastfix.blend --python-exit-code 1 --python out/src/export.py -- out/fbx
"$B" -b --factory-startup <blend> --python-exit-code 1 --python out/src/verify.py -- dump out/logs/<src|donor|fix>.json
"$B" -b --factory-startup --python-exit-code 1 --python out/src/verify.py -- fbx out/fbx out/logs/fbx.json
"$B" -b --factory-startup --python-exit-code 1 --python out/src/verify.py -- check out/logs/src.json out/logs/donor.json out/logs/fix.json out/logs/fbx.json out out/logs/steps.txt
```
mastfix.py embeds the measured donor coordinates (no donor file needed) and refuses to run on anything but the v3 source sha256. The donor dump is only used by verify.py as evidence.
