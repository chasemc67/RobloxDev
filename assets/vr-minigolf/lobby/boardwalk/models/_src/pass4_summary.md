# Pass 4 standalone portal scenery

Twelve standalone scenery FBXs plus six canopy-anchored Lantern Grove lanterns. All arch geometry, other moving assets, portal quads, apron, nameplate and sign FBXs remain byte-identical to pass 3. Three collision boxes and trigger/surface metadata per arch are preserved. No Roblox application was opened.

## Validation

`fitcheck_pass4_validated.txt`: ALL PASS. Includes pass 3 envelope, face/opening/trigger, UV, material, hinge and original aggregate budget checks; per-scenery strict <20,000 triangle cap, measured base-centre pivots, collision metadata, full triangle/exclusion-volume clearance, exact Euclidean triangle-to-corridor minima, all lantern extended-opening tests, and preserved FBX SHA256 comparisons.
`reimport_check_pass4.txt`: ALL PASS over all portal/scenery exports, including all 18 new or changed files. Imported bbox, orientation, triangle counts, material counts, identity origin and scale match manifest.
Walk-in corridor: X [-5,5], Y [0,12], Z [-2,24]. Forbidden scenery box: X [-11,11], Y [0,18], Z [-8,30]. No intersecting triangle faces. Above Y18 is permitted. Minimum distances use triangle/box vertex-face and edge-edge features, not vertex-only sampling.

## Per-file triangles and clearance

| File | Triangles | Minimum distance to walk-in corridor (studs) | Pivot in arch-local X,Y,Z | Collision boxes |
|---|---:|---:|---|---:|
| bw_arch_lantern_grove_lantern_01.fbx | 148 | accessory: extended opening clear | [-12.8, 21.3, 1.3] | 0 |
| bw_arch_lantern_grove_lantern_02.fbx | 148 | accessory: extended opening clear | [12.8, 21.3, 1.3] | 0 |
| bw_arch_lantern_grove_lantern_03.fbx | 148 | accessory: extended opening clear | [-7, 22.3, 1.3] | 0 |
| bw_arch_lantern_grove_lantern_04.fbx | 148 | accessory: extended opening clear | [7, 22.3, 1.3] | 0 |
| bw_arch_lantern_grove_lantern_05.fbx | 148 | accessory: extended opening clear | [-3.5, 23.3, 1.3] | 0 |
| bw_arch_lantern_grove_lantern_06.fbx | 148 | accessory: extended opening clear | [3.5, 23.3, 1.3] | 0 |
| bw_scn_aurora_crown.fbx | 780 | 8.56522 | [0.7309, 0.0, -14.5286] | 2 |
| bw_scn_aurora_rocks_e.fbx | 1,868 | 7.18465 | [15.5983, 0.0, -0.6576] | 2 |
| bw_scn_aurora_rocks_w.fbx | 1,868 | 7.17388 | [-15.4721, 0.0, -0.6576] | 2 |
| bw_scn_lantern_grove_planter_e.fbx | 2,244 | 7.30000 | [15.0, 0.0, 3.0] | 2 |
| bw_scn_lantern_grove_planter_w.fbx | 2,244 | 7.30000 | [-15.0, 0.0, 3.0] | 2 |
| bw_scn_lantern_grove_trunk_e.fbx | 8,016 | 7.16838 | [8.9139, 0.0237, -0.3258] | 2 |
| bw_scn_lantern_grove_trunk_w.fbx | 8,016 | 7.16831 | [-9.059, 0.0229, -0.2462] | 2 |
| bw_scn_sugarloaf_crystals_e.fbx | 532 | 8.07003 | [15.3185, 0.0, 3.5474] | 2 |
| bw_scn_sugarloaf_crystals_w.fbx | 532 | 8.07003 | [-15.3185, 0.0, 3.5474] | 2 |
| bw_scn_sugarloaf_lollipop_cactus.fbx | 504 | 12.55607 | [-21.0, 0.0, 1.7] | 2 |
| bw_scn_sugarloaf_tower_e.fbx | 3,372 | 7.73868 | [15.5666, 0.0, 0.1333] | 2 |
| bw_scn_sugarloaf_tower_w.fbx | 3,372 | 7.66895 | [-15.5381, 0.0, 0.1571] | 2 |

Retained portal-component files:

| File | Triangles |
|---|---:|
| bw_arch_aurora_archipelago.fbx | 8,170 |
| bw_arch_aurora_archipelago_lantern_01.fbx | 144 |
| bw_arch_aurora_archipelago_lantern_02.fbx | 144 |
| bw_arch_aurora_archipelago_snowpuff.fbx | 514 |
| bw_arch_lantern_grove.fbx | 13,252 |
| bw_arch_nameplate.fbx | 176 |
| bw_arch_sugarloaf_canyon.fbx | 7,084 |
| bw_arch_sugarloaf_canyon_lantern_01.fbx | 144 |
| bw_arch_sugarloaf_canyon_lantern_02.fbx | 144 |
| bw_coming_soon_sign.fbx | 184 |
| bw_portal_apron.fbx | 12 |
| bw_portal_surface_aurora_archipelago.fbx | 2 |
| bw_portal_surface_lantern_grove.fbx | 2 |
| bw_portal_surface_sugarloaf_canyon.fbx | 2 |

## Per-portal group totals

Includes original arch, portal quad, lanterns, snowpuff where applicable; full display total also includes one apron and one reused nameplate, plus coming-soon sign for Sugarloaf/Aurora. Shared components are counted separately in the manifest placed-scene total.

| Portal | Original constrained group | New scenery | Complete display group |
|---|---:|---:|---:|
| lantern_grove | 14,142 | 20,520 | 34,850 |
| sugarloaf_canyon | 7,374 | 8,312 | 16,058 |
| aurora_archipelago | 8,974 | 4,516 | 13,862 |

Placed-scene manifest total: **100,176** triangles; original limit 120,000. Unique props: 56; instances: 271.

## Lantern anchors and snowpuff

Six Grove cord-anchor pivots, in arch-local Roblox axes:
- `bw_arch_lantern_grove_lantern_01`: [-12.8, 21.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.
- `bw_arch_lantern_grove_lantern_02`: [12.8, 21.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.
- `bw_arch_lantern_grove_lantern_03`: [-7, 22.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.
- `bw_arch_lantern_grove_lantern_04`: [7, 22.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.
- `bw_arch_lantern_grove_lantern_05`: [-3.5, 23.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.
- `bw_arch_lantern_grove_lantern_06`: [3.5, 23.3, 1.3]; swing axis [0, 0, 1]; Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.

Snowpuff geometry and arch-base FBX origin are unchanged. Figure footprint remains by the west leg around X=-6.5, Z=1.25; asset origin [0,0,0]. New west snow-rocks begin outside X=-11, leaving its original spot clear. Exact snowpuff bbox is in manifest.

## Placement, materials and collision

Each scenery FBX is base-centred. Use `pivot_position_arch_local` for its origin; all `collision[].center` values are relative to that origin in Roblox axes. Manifest instances already include parent-relative scenery placement in lobby world coordinates. MeshParts are decoration only: CanCollide/CanQuery/CanTouch false. Only invisible simple rock, trunk, tower, cactus-stem or stone-planter collision boxes may collide; foliage and crystals remain noncolliding.
Opaque `BW_Backdrop` uses exported Col vertex colours. `BW_Atlas` uses embedded shared `textures/bw_atlas_1024.png`; no extra textures. `BW_Neon` and `BW_Neon_Yellow` are separate material meshes; use each parts[].color and Material=Neon. Grove lanterns #FFC867, candy tips #F6A6C8 and #FFE08A, Aurora tips #9FE6F2. No asset contains a real light.

## Render review and caveats

Six 960x960 Cycles GPU previews show arch, all scenery, separate lanterns, portal/apron/signs and 2x5 capsule in both views. Eye camera is Y=5, pulled back to fit the whole group. Comparison sheet: `previews/portals/portals_vs_concepts.png`.
Reviewed against all three supplied portal concepts. Iterated sparse lower Grove foliage, uniform Aurora crown and low snow-rock silhouettes; added layered leaf skirts, varied tilted crown shards, substantial snow boulders and two Neon candy colours. Grove has two connected overhead autumn canopies and gnarled side trunks; Canyon has tall chipped sandstone bands, candy clusters and a lollipop cactus; Aurora has a large faceted crown behind the arch and dark snow-capped rocks.
The mandatory six-stud offset and unchanged 16x18x4 arch create wider, clearly separate scenery than the tightly packed concepts. This is deliberate to retain the specified walk-in corridor. Concept photographic leaf/stone detail is translated into toy low-poly masses. Portal preview shader is display-only; production portal export remains unchanged for runtime animation. No real in-engine import/playtest was attempted under the Roblox prohibition.

## Rebuild

Run from lobby root, one own Blender process at a time; never use run_blender.ps1 (it waits on the unrelated job):

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\build_pass4.py
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\fitcheck.py -- --pass4
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\reimport_pass4.py
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P boardwalk\models\_src\render_pass4.py
python boardwalk\models\_src\compose_pass3.py
python boardwalk\models\_src\finalize_pass4.py
```

`build_pass4.py` imports props_scenery, reuses build_all export/manifest assembly, updates Grove lantern generator closure anchors, and adds scenery instances. Do not rebuild the full arches group to preserve pass3 exports. Backup `_backup_pass3` contains original FBX, manifest, previews and all Python generators existing before this pass.
