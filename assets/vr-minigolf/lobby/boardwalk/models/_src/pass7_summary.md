# Pass7 completed

Placed lobby: **110,321 triangles**, 271 instances, 56 FBX files. Every file <20k; placed lobby <120k.

Fitcheck and independent FBX reimport: ALL PASS. Fixed arches, portal surfaces, apron, nameplate/sign, arch collision and triggers remain unchanged; SHA256 checked against _backup_pass6. No Roblox, Studio or Player was opened or touched. Own Blender invocations were sequential and exited.

## Changes and review

Grove trunks have a lobed cross-section with150-degree rotation, three helical strands and root flares. Layered rounded autumn leaf blobs descend to aboutY6 on the outside of each arch side and join the upper crown. The canopy lateral extent is about2 studs outside the chunky trunk outline. Six branch anchors remain unchanged and all lanterns were re-exported.

Sugarloaf has17 smooth rounded band segments per side with3-segment bevels, not blocky slabs. Imported geometry measures approx27.7 studs high and9.780 degrees inward lean. Crystals are3.0-5.7 studs (2x pass6) with doubled radii;12 per side at tower/arch joints plus6 at bases. Cactus assembly is exactly1.5x pass5 height, about0.754x pass6, with a red/cream geometric spiral disc on a stick. Preview iteration removed coplanar disc faces.

Aurora uses the supplied script byte-for-byte, directly calling build_crown and splitting only by material for export. No count, size, radius, position, splay, colour or tip-fraction changes. All exported vertex coordinates independently match the supplied build_crown geometry within0.002stud FBX tolerance. No nudges needed. The old crown geometry is removed entirely, including old shelves/footing. No optional snow mesh added. Crown pivot stays at arch-base origin as explicitly specified; pure crystal crown has no collision boxes. Existing shoulder rocks remain unchanged.

## Crown as built

| Crystal | Length | Radius | Base X | Base Y(up) | Blender depth Y | Splay | Twist | Apex Y(up) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|1|27.0|2.3|3.0|14.5|0.4|10.0|0.0|41.0898|
|2|18.0|1.7|-3.6|14.5|0.3|-15.0|15.0|31.8867|
|3|18.0|1.6|7.0|14.0|0.2|20.0|30.0|30.9145|
|4|10.0|1.1|-7.2|13.8|0.0|-25.0|8.0|22.8631|
|5|10.0|1.0|-0.6|15.0|-0.5|-12.0|22.0|24.7815|
|6|10.0|1.1|5.6|15.2|0.9|25.0|40.0|24.2631|

Exactly276 triangles:240 shaft/base triangles,36 Neon tip triangles. Col is imported and explicitly connected to the preview shader. Glow_Tips separate MeshPart/material: Material=Neon, Color=#9FE6F2, preview emission4. Closeup camera(0,-25,22) in Blender, aimed at(1,0,27),78degree field of view frames crown+lintel.

## Triangles per file

| File | Tris | Instances | Placed tris |
|---|---:|---:|---:|
|bw_arch_aurora_archipelago|8170|1|8170|
|bw_arch_aurora_archipelago_lantern_01|144|1|144|
|bw_arch_aurora_archipelago_lantern_02|144|1|144|
|bw_arch_aurora_archipelago_snowpuff|514|1|514|
|bw_arch_lantern_grove|13252|1|13252|
|bw_arch_lantern_grove_lantern_01|148|1|148|
|bw_arch_lantern_grove_lantern_02|148|1|148|
|bw_arch_lantern_grove_lantern_03|148|1|148|
|bw_arch_lantern_grove_lantern_04|148|1|148|
|bw_arch_lantern_grove_lantern_05|148|1|148|
|bw_arch_lantern_grove_lantern_06|148|1|148|
|bw_arch_nameplate|176|3|528|
|bw_arch_sugarloaf_canyon|7084|1|7084|
|bw_arch_sugarloaf_canyon_lantern_01|144|1|144|
|bw_arch_sugarloaf_canyon_lantern_02|144|1|144|
|bw_barrel|212|1|212|
|bw_beach_umbrella|334|1|334|
|bw_bench|300|6|1800|
|bw_birdie_bites_shack|3754|1|3754|
|bw_coming_soon_sign|184|2|368|
|bw_course_board|1606|1|1606|
|bw_crate|44|1|44|
|bw_cup_flag|140|2|280|
|bw_deck_plank_a|10|76|760|
|bw_deck_plank_b|10|76|760|
|bw_flower_planter|756|1|756|
|bw_lantern_post|224|6|1344|
|bw_lantern_tree_canopy|5600|1|5600|
|bw_leaderboard_wall|1736|1|1736|
|bw_picnic_table|588|1|588|
|bw_pier_piling|232|8|1856|
|bw_portal_apron|12|3|36|
|bw_portal_surface_aurora_archipelago|2|1|2|
|bw_portal_surface_lantern_grove|2|1|2|
|bw_portal_surface_sugarloaf_canyon|2|1|2|
|bw_practice_green|576|1|576|
|bw_railing|222|42|9324|
|bw_rock_arch|1164|1|1164|
|bw_scn_aurora_crown|276|1|276|
|bw_scn_aurora_rocks_e|2872|1|2872|
|bw_scn_aurora_rocks_w|2877|1|2877|
|bw_scn_lantern_grove_planter_e|2244|1|2244|
|bw_scn_lantern_grove_planter_w|2244|1|2244|
|bw_scn_lantern_grove_trunk_e|3516|1|3516|
|bw_scn_lantern_grove_trunk_w|3516|1|3516|
|bw_scn_sugarloaf_crystals_e|564|1|564|
|bw_scn_sugarloaf_crystals_w|564|1|564|
|bw_scn_sugarloaf_lollipop_cactus|5156|1|5156|
|bw_scn_sugarloaf_tower_e|9832|1|9832|
|bw_scn_sugarloaf_tower_w|9832|1|9832|
|bw_sea_stacks|1088|1|1088|
|bw_signpost|390|1|390|
|bw_string_lights|384|1|384|
|bw_tee_mat|12|2|24|
|bw_windmill|622|1|622|
|bw_windmill_blades|404|1|404|

## Complete portal group totals

Includes arch, moving parts, scenery, portal quad, apron, nameplate and applicable coming-soon sign.

| Course | Display tris |
|---|---:|
|lantern_grove|25850|
|sugarloaf_canyon|33694|
|aurora_archipelago|15371|

## Clearance minima

Arch-local+Z front. A=X[-5,5]Y[0,12]Z[-12,4]; B=X[-11,11]Y[0,18]Z[4,34]; trigger=X[-5,5]Y[0,10]Z[-1.5,1.5]. Independent triangle-volume tests and Euclidean vertex/face, edge/edge distances from imported FBXs; collision boxes also checked.

| Mesh | A | B | Trigger |
|---|---:|---:|---:|
|bw_arch_aurora_archipelago_lantern_01|1.32447|2.36000|1.32447|
|bw_arch_aurora_archipelago_lantern_02|1.32447|2.36000|1.32447|
|bw_arch_lantern_grove_lantern_01|7.88774|2.01159|9.79472|
|bw_arch_lantern_grove_lantern_02|7.88774|2.01159|9.79472|
|bw_arch_lantern_grove_lantern_03|8.31459|2.75436|10.33325|
|bw_arch_lantern_grove_lantern_04|8.31459|2.75436|10.33325|
|bw_arch_lantern_grove_lantern_05|9.27000|3.62305|11.28931|
|bw_arch_lantern_grove_lantern_06|9.27000|3.62305|11.28931|
|bw_arch_sugarloaf_canyon_lantern_01|1.02447|2.01000|1.14422|
|bw_arch_sugarloaf_canyon_lantern_02|1.02447|2.01000|1.14422|
|bw_scn_aurora_crown|2.08333|2.40814|4.07925|
|bw_scn_aurora_rocks_e|0.49986|1.40725|1.34911|
|bw_scn_aurora_rocks_w|0.64471|1.40725|1.40857|
|bw_scn_lantern_grove_planter_e|1.92600|1.57500|1.92600|
|bw_scn_lantern_grove_planter_w|1.92600|1.57500|1.92600|
|bw_scn_lantern_grove_trunk_e|0.14995|1.13374|0.14995|
|bw_scn_lantern_grove_trunk_w|0.15003|1.13379|0.15003|
|bw_scn_sugarloaf_crystals_e|1.22066|0.58399|3.03726|
|bw_scn_sugarloaf_crystals_w|1.22066|0.58399|3.02796|
|bw_scn_sugarloaf_lollipop_cactus|5.84020|2.81595|5.84020|
|bw_scn_sugarloaf_tower_e|0.71478|1.90952|1.01870|
|bw_scn_sugarloaf_tower_w|0.71478|1.90952|1.01870|

## Anchors and measurements

| Asset | Arch-local anchor |
|---|---|
|bw_arch_aurora_archipelago_lantern_01|[-6.8, 6.2, 1.25]|
|bw_arch_aurora_archipelago_lantern_02|[6.8, 6.2, 1.25]|
|bw_arch_lantern_grove_lantern_01|[-8.2, 21.3, 2.3]|
|bw_arch_lantern_grove_lantern_02|[8.2, 21.3, 2.3]|
|bw_arch_lantern_grove_lantern_03|[-6, 22.3, 2.3]|
|bw_arch_lantern_grove_lantern_04|[6, 22.3, 2.3]|
|bw_arch_lantern_grove_lantern_05|[-3.5, 23.3, 2.3]|
|bw_arch_lantern_grove_lantern_06|[3.5, 23.3, 2.3]|
|bw_arch_sugarloaf_canyon_lantern_01|[-6.5, 12.6, 1.6]|
|bw_arch_sugarloaf_canyon_lantern_02|[6.5, 12.6, 1.6]|

Snowpuff position[-6.5,0,1.25], unchanged export origin[0,0,0]. Scenery placement uses pivot_position_arch_local; collision centres are pivot-local. Mesh collision off.

{
  "bw_scn_sugarloaf_tower_w": {
    "base_centre": [
      -10.048742294311523,
      0.8030468821525574,
      -0.0
    ],
    "top_centre": [
      -5.582202434539795,
      26.746227264404297,
      -1.9669532775878906e-06
    ],
    "lean_degrees": 9.768632259819864
  },
  "bw_scn_sugarloaf_tower_e": {
    "base_centre": [
      10.048742294311523,
      0.8030468821525574,
      -0.0
    ],
    "top_centre": [
      5.582202434539795,
      26.746227264404297,
      -1.8477439880371094e-06
    ],
    "lean_degrees": 9.768632259819864
  },
  "bw_scn_sugarloaf_lollipop_cactus": {
    "height_ratio_pass5": 1.5000476417341593
  }
}

## Honest notes

The exact supplied crown is far taller than the earlier27-stud total-height target: its27-stud longest crystal starts at14.5 and reaches41.0898. It is intentionally six simple faceted shafts,276triangles, superseding historical5-8k richness targets. Its source contains colour assignment across existing BMesh faces; preserved exactly as requested. The closeup and full previews restore imported Col and cyan emission. Bright Neon tips can appear nearly white under exposure.

The rounded foliage reads as a tree frame with side cascades; toy blobs remain much simpler than the painted concept. Trunk twists show best from3/4 and are partly hidden by canopy/unchanged arches. Sandstone bands are rounded but regular; large required candy shards are prominent. Portal shaders in previews are display-only. No particles or runtime lights were exported. In-engine validation was prohibited; only Blender export/reimport and geometric checks were performed.

## Rebuild

Run Blender directly one own instance at a time: build_pass7.py; fitcheck.py -- --pass7; reimport_pass7.py; render_pass7.py. Then Python compose_pass3.py; finalize_pass7.py. Never use run_blender.ps1; never open Roblox/Studio/Player. Backup _backup_pass6 holds pre-pass7 exports, manifest, README, previews and Python sources.
