# Pass8 completed

Placed lobby: **107,904 triangles**. All meshes <20,000; fitcheck and independent FBX reimport ALL PASS.

Supplied crown v2 and rock_candy copied byte-identically. Crown12-side initial build1284tris; permitted runtime SIDES16 produces1716tris. Six crystals unchanged, no nudges; tallest tip BlenderZ / RobloxY=27.0. Glow_Tips retains the supplied top20% assignment, Neon #9FE6F2, preview emission1.5. Col byte colours preserved and preview shaders explicitly read Col.

Sugarloaf: per side one eight-crystal size2.0 cluster at joint(+-9.5,15,.8), plus six/five-crystal size1.0 base clusters. Three clusters merged into one base-centred FBX per side and mirrored. Prior slab-crystal scenery deleted/replaced. Pure crystals have no collision boxes. Existing tower/cactus exports retained.

Grove: three tapering strands visibly spiral240degrees, root flares, width about4.5 before root flare. Varied radius1.2-4.5 blobs in layered top/core and smaller staggered outer cascades. Lower trunks exposed; six lantern anchors unchanged, lanterns re-exported.

Aurora: standalone shoulder debris removed, snow/rocks gathered into tight grounded clusters at each leg. Snowpuff spot[-6.5,0,1.25] remains clear.

Previews use Standard, neutral world0.9 and large soft key. Pixel samples: {"violet_base": {"xy": [240, 650], "rgb": [108, 79, 175]}, "teal_tip": {"xy": [600, 320], "rgb": [191, 255, 255]}}. Base is violet, caps cyan; lighting and gradient mean pixels differ from exact material swatches.

## Honest notes

Fixed arches were required to remain byte-identical. Their original embedded rock/snow and tiny candy accents therefore remain, including the small Aurora lintel accents visible in closeup; all standalone shoulder pieces were removed. Supplied crown face-to-crystal attribution is preserved exactly; overlapping crystals can inherit the source attribution. The toy geometry remains simpler than painted concepts. Eye-height trunks show spiral strands, although existing arch legs obscure their inner portions. No Roblox/Studio/Player opened; all own Blender processes exited.

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
|bw_scn_aurora_crown|1716|1|1716|
|bw_scn_aurora_rocks_e|1228|1|1228|
|bw_scn_aurora_rocks_w|1228|1|1228|
|bw_scn_lantern_grove_planter_e|2244|1|2244|
|bw_scn_lantern_grove_planter_w|2244|1|2244|
|bw_scn_lantern_grove_trunk_e|3380|1|3380|
|bw_scn_lantern_grove_trunk_w|3380|1|3380|
|bw_scn_sugarloaf_crystals_e|418|1|418|
|bw_scn_sugarloaf_crystals_w|418|1|418|
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
|lantern_grove|25578|
|sugarloaf_canyon|33402|
|aurora_archipelago|13518|

## Zone minimum distances

A=X[-5,5]Y[0,12]Z[-12,4]; B=X[-11,11]Y[0,18]Z[4,34]. Distances measured from imported triangles; collision boxes separately checked.

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
|bw_scn_aurora_crown|0.55182|2.25619|2.52203|
|bw_scn_aurora_rocks_e|2.86637|2.50711|2.86637|
|bw_scn_aurora_rocks_w|2.86085|2.50711|2.86085|
|bw_scn_lantern_grove_planter_e|1.926|1.575|1.926|
|bw_scn_lantern_grove_planter_w|1.926|1.575|1.926|
|bw_scn_lantern_grove_trunk_e|0.33741|0.91594|0.33741|
|bw_scn_lantern_grove_trunk_w|0.33739|0.91603|0.33739|
|bw_scn_sugarloaf_crystals_e|2.54303|0.11882|2.56976|
|bw_scn_sugarloaf_crystals_w|2.54303|0.11882|2.56976|
|bw_scn_sugarloaf_lollipop_cactus|5.8402|2.81595|5.8402|
|bw_scn_sugarloaf_tower_e|0.71478|1.90952|1.0187|
|bw_scn_sugarloaf_tower_w|0.71478|1.90952|1.0187|

## Anchors

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

## Rebuild

Sequential direct Blender invocations: build_pass8.py, fitcheck_pass8.py, reimport_pass8.py, render_pass8.py. Python compose_pass3.py then finalize_pass8.py. Backup in _backup_pass7.

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
  },
  "crown": {
    "tallest_tip_Z": 27.0,
    "triangles": 1716,
    "nudges": []
  }
}