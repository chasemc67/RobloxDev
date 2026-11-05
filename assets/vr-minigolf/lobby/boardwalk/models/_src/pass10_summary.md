# Pass 10 completed

Placed lobby: **104,772 triangles**. Every mesh <20k; fitcheck and FBX reimport ALL PASS.

Only four FBXs rebuilt from byte-identical pass10_geo.py: Sugarloaf west/east candy (tighter base clusters) and Aurora west/east snowy rocks (taller ten-rock mounds). No supplied shapes, positions or colors changed. All other FBXs verified by SHA256 against _backup_pass9, and their manifest entries remain identical.

Two collision boxes per rock pile follow the new mound bounds: front outer section and rear section. The front inner edge leaves the snowpuff footprint clear; these are simple collision approximations. Zones A/B and trigger clearance independently measured against exported triangles. Snowpuff and six lantern anchors unchanged.

Standard transform, Col vertex colors, bright flat lighting and established cameras retained. Glow_Crystal emission 0.2 from vertex color; source pink #F59AC8 / yellow #FFF1A8. Glow_Tips remains1.5 cyan. All six portal views, crown closeup and comparison sheet re-rendered using the established permitted Eevee fallback. Pixel evidence: preview_colour_pass10.json. Displayed swatches vary with lighting; source colors are independently checked against FBX corners.

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
|bw_scn_aurora_rocks_e|800|1|800|
|bw_scn_aurora_rocks_w|800|1|800|
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

## Portal totals

| Course | Tris |
|---|---:|
|lantern_grove|23310|
|sugarloaf_canyon|33578|
|aurora_archipelago|12478|

## Zone minima

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
|bw_scn_aurora_rocks_e|1.52244|0.27173|1.57259|
|bw_scn_aurora_rocks_w|1.67256|0.13876|1.71915|
|bw_scn_lantern_grove_planter_e|1.926|1.575|1.926|
|bw_scn_lantern_grove_planter_w|1.926|1.575|1.926|
|bw_scn_lantern_grove_trunk_e|0.28304|1.15407|0.28304|
|bw_scn_lantern_grove_trunk_w|0.4|1.15407|0.4|
|bw_scn_sugarloaf_crystals_e|2.28306|0.3704|2.31833|
|bw_scn_sugarloaf_crystals_w|2.35651|0.52511|2.41129|
|bw_scn_sugarloaf_lollipop_cactus|5.8402|2.81595|5.8402|
|bw_scn_sugarloaf_tower_e|0.71478|1.90952|1.0187|
|bw_scn_sugarloaf_tower_w|0.71478|1.90952|1.0187|

No Roblox application opened or touched. Blender ran directly, sequentially; every own instance exited. Backup: _backup_pass9. Rebuild: build_pass10.py, fitcheck_pass10.py, reimport_pass10.py, render_pass10.py (Blender); compose_pass3.py and finalize_pass10.py (Python).
