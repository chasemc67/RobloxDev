# Modular lobby dressing kit

21 decoration FBXs, shared boardwalk atlas, base-centre pivots except banner cloth top pivots and leaderboard panels sharing frame base origin. Facing -Z. Scale 1 BU = 1 stud, FBX forward -Z up Y, textures embedded. MeshParts Anchored=true, CanCollide/CanQuery/CanTouch=false; no mesh collision. Neon material from manifest; Col vertex colours must be retained.

| Asset | Tris | Bbox W/H/D | Pivot |
|---|---:|---|---|
| kit_stringlight_pole | 236 | 1.76/9.73/1.5 | base centre |
| kit_string_lights_span_10 | 584 | 10.447/2.447/0.425 | base centre |
| kit_string_lights_span_20 | 864 | 20.447/2.524/0.425 | base centre |
| kit_banner_pole | 288 | 4.0/10.0/1.5 | base centre |
| kit_banner_lantern_grove | 208 | 3.0/4.5/0.56 | top centre |
| kit_banner_sugarloaf_canyon | 452 | 3.0/4.5/0.5 | top centre |
| kit_banner_aurora_archipelago | 130 | 3.0/4.5/0.5 | top centre |
| kit_flag_pennant_string | 137 | 10.047/1.728/0.3 | base centre |
| kit_bench_a | 1188 | 6.0/3.3/2.25 | base centre |
| kit_bench_b | 304 | 6.0/3.2/2.0 | base centre |
| kit_planter_square | 648 | 3.0/2.1/3.0 | base centre |
| kit_planter_round | 224 | 3.0/2.1/3.0 | base centre |
| kit_plant_autumn | 348 | 2.673/3.305/2.693 | base centre |
| kit_plant_cactus_candy | 396 | 2.551/3.85/0.8 | base centre |
| kit_plant_crystal | 88 | 2.374/3.245/1.937 | base centre |
| kit_lamp_post | 288 | 1.5/8.8/1.5 | base centre |
| kit_lamp_post_double | 504 | 3.646/8.0/1.5 | base centre |
| kit_leaderboard_frame | 1728 | 14.0/9.85/1.75 | base centre |
| kit_leaderboard_panel_1 | 2 | 3.4/5.6/0.0 | shared local origin |
| kit_leaderboard_panel_2 | 2 | 3.4/5.6/0.0 | shared local origin |
| kit_leaderboard_panel_3 | 2 | 3.4/5.6/0.0 | shared local origin |

Hook positions, soil filler swaps and SurfaceGui panel rectangles are in manifest.json. Put swappable plants at planter filler_attach. Put cloth top pivot at banner_pole.cloth_attach. For string spans, align both recorded hooks to poles, rotate/translate whole asset only. No lights or animation baked. Cloth may gently sway +/-4 degrees; avoid flicker near spawn. Neutral wood/brass/stone kit works with treehouse, islands and boardwalk layouts; themed fillers and banners supply the three course palettes.

Build with `_src/build_kit.py` using own Blender headless instance. Preview/validation commands are in [pass2 summary](../boardwalk/models/_src/pass2_summary.md). 42 per-asset eye/34 previews plus kit_contact_sheet.png; eye camera 5 studs, capsule 2x5. Reimport ALL PASS at `_src/reimport_check_pass2.txt`.
