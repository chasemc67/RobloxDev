# Pass 9 completed

Placed lobby: **104,452 triangles**; all files <20k. Fitcheck and FBX reimport: ALL PASS.

Supplied pass9_geo.py is byte-identical; no geometry/API edits. Seven replacements: four cluster groups per Sugarloaf side, six-crystal12-sided beveled crown with flat normals, three twisted strands/root flares per Grove side plus retained pass8 leaf masses, eight snowy rocks per Aurora side. Glow_Crystal uses Neon from Col; Glow_Tips Neon #9FE6F2. Preview Glow emission1.5, Standard transform, ambient0.9, large soft key; permitted Eevee fallback after GPU slowdown.

Two collision boxes per trunk follow lower centreline x=Â±8.4 Y0..13 and upper inward curl; two per rock pile. All boxes clear A/B and snowpuff footprint. Pure crystals/crown collision off. Snowpuff spot[-6.5,0,1.25] unchanged.

Six lantern exports and anchors unchanged: cords still contact retained canopy (measured below). Towers, cactus, planters, snowpuff, arches, surfaces, apron, signs, triggers and all remaining FBXs byte-identical to pass8 backup.

## Triangles

| Mesh | Tris | Instances | Placed tris |
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
|bw_scn_aurora_crown|1532|1|1532|
|bw_scn_aurora_rocks_e|640|1|640|
|bw_scn_aurora_rocks_w|640|1|640|
|bw_scn_lantern_grove_planter_e|2244|1|2244|
|bw_scn_lantern_grove_planter_w|2244|1|2244|
|bw_scn_lantern_grove_trunk_e|2246|1|2246|
|bw_scn_lantern_grove_trunk_w|2246|1|2246|
|bw_scn_sugarloaf_crystals_e|506|1|506|
|bw_scn_sugarloaf_crystals_w|506|1|506|
|bw_scn_sugarloaf_lollipop_cactus|5156|1|5156|
|bw_scn_sugarloaf_tower_e|9832|1|9832|
|bw_scn_sugarloaf_tower_w|9832|1|9832|
|bw_sea_stacks|1088|1|1088|
|bw_signpost|390|1|390|
|bw_string_lights|384|1|384|
|bw_tee_mat|12|2|24|
|bw_windmill|622|1|622|
|bw_windmill_blades|404|1|404|

## Portal group totals

| Course | Tris |
|---|---:|
|lantern_grove|23310|
|sugarloaf_canyon|33578|
|aurora_archipelago|12158|

## Zone minima

Arch-local Roblox A X[-5,5]Y[0,12]Z[-12,4]; B X[-11,11]Y[0,18]Z[4,34]. Triangle-to-volume distance, studs.

| Mesh | A | B | Trigger |
|---|---:|---:|---:|
|bw_arch_aurora_archipelago_lantern_01|1.32447|2.36|1.32447|
|bw_arch_aurora_archipelago_lantern_02|1.32447|2.36|1.32447|
|bw_arch_lantern_grove_lantern_01|7.88774|2.01159|9.79472|
|bw_arch_lantern_grove_lantern_02|7.88774|2.01159|9.79472|
|bw_arch_lantern_grove_lantern_03|8.31459|2.75436|10.33325|
|bw_arch_lantern_grove_lantern_04|8.31459|2.75436|10.33325|
|bw_arch_lantern_grove_lantern_05|9.27|3.62305|11.28931|
|bw_arch_lantern_grove_lantern_06|9.27|3.62305|11.28931|
|bw_arch_sugarloaf_canyon_lantern_01|1.02447|2.01|1.14422|
|bw_arch_sugarloaf_canyon_lantern_02|1.02447|2.01|1.14422|
|bw_scn_aurora_crown|0.55182|2.22426|2.5309|
|bw_scn_aurora_rocks_e|0.51892|0.27173|1.13908|
|bw_scn_aurora_rocks_w|0.58129|0.13876|1.2878|
|bw_scn_lantern_grove_planter_e|1.926|1.575|1.926|
|bw_scn_lantern_grove_planter_w|1.926|1.575|1.926|
|bw_scn_lantern_grove_trunk_e|0.28304|1.15407|0.28304|
|bw_scn_lantern_grove_trunk_w|0.4|1.15407|0.4|
|bw_scn_sugarloaf_crystals_e|2.28306|0.3704|2.31833|
|bw_scn_sugarloaf_crystals_w|2.35651|0.52511|2.41129|
|bw_scn_sugarloaf_lollipop_cactus|5.8402|2.81595|5.8402|
|bw_scn_sugarloaf_tower_e|0.71478|1.90952|1.0187|
|bw_scn_sugarloaf_tower_w|0.71478|1.90952|1.0187|

## Lantern anchors

| Asset | Anchor X,Y,Z | Cord surface distance | Anchor inside canopy |
|---|---|---:|---|
|bw_arch_lantern_grove_lantern_02|[8.2, 21.3, 2.3]|0.01921|True|
|bw_arch_lantern_grove_lantern_04|[6, 22.3, 2.3]|0.02012|True|
|bw_arch_lantern_grove_lantern_06|[3.5, 23.3, 2.3]|0.03844|True|
|bw_arch_lantern_grove_lantern_01|[-8.2, 21.3, 2.3]|0.00094|False|
|bw_arch_lantern_grove_lantern_03|[-6, 22.3, 2.3]|0.08559|True|
|bw_arch_lantern_grove_lantern_05|[-3.5, 23.3, 2.3]|0.00048|False|

## Honest notes

All source geometry is preserved, including the supplied crown face-to-crystal attribution where crystals overlap. Fixed arches retain their embedded historical accents. Canopy replaces no leaf positions/colors/topology; old trunk/bark and its atlas inset are removed. Sugarloaf crystals render very bright/pale with the requested Glow emission1.5; supplied vertex values were preserved rather than darkened. Eevee fallback was used after own GPU render slowdown. Crown pixel samples: {"violet_base": {"xy": [240, 650], "rgb": [123, 94, 208]}, "cyan_tip": {"xy": [600, 300], "rgb": [191, 255, 255]}}. Preview lighting alters displayed swatches; these are toy meshes rather than painted concepts. No Roblox application opened. All Blender calls ran directly and sequentially; only our own instances were used and exited.

## Rebuild

build_pass9.py -> fitcheck_pass9.py -> reimport_pass9.py -> render_pass9.py using Blender5.2. compose_pass3.py -> finalize_pass9.py using Python. Backup: _backup_pass8.