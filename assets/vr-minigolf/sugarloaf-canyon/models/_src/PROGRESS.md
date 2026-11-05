2026-10-11 17:23:31 pass1 brief written, launching claude
2026-10-11 17:27:27 step0 read brief/skills/course.md/world README+json; moved unused Lantern Grove generators to _src/_lg_ref/ (kept lglib.py + textures.py helpers)
2026-10-11 17:28:54 step1 sc_textures.py: 12 tiling 512 PNGs (strata strip = 6 bands/36 studs, sandstone, timber, rope, peppermint concrete red/white, cactus, sands, crystals) + 6 RGBA alpha-cut cards
2026-10-11 17:35:50 step2 sc_specs.py + sc_layout.py -> layout.json (world.json pieces, auto cliff/slot kit along heightfield, clusters, scatter, dunes, cards, sky)
2026-10-11 17:43:47 step3 sc_pieces.py + sc_build.py: first full build, 98 pieces, FBX + tri cache + Workbench previews + manifest.json
2026-10-11 17:49:02 step4 sc_fitcheck.py written; fixes (lift shaft yaw/open faces, bridge ends, kit widths, mine-head x 134, boardwalk trimmed) -> fitcheck ALL PASS (footprints >= 2.1, overhead >= 9.25)
2026-10-11 17:51:12 addendum: holes.json available; pass2 will fit to it + PC renders
2026-10-11 18:01:25 claude hit session limit after step4; continuing with codex
2026-10-11 18:01:41 codex auth expired (401); finishing remaining steps by hand
2026-10-11 18:02:43 step5 holes.json rail/felt clearance check -> _src/fitcheck_pass1_validated.txt (PASS, H3 footbridge 2.9 flagged); contact_sheet.png
2026-10-11 18:03:08 step6 README.md + _src/pass1_summary.md written. Pass 1 done on box; PC Cycles hero renders pending
2026-10-11 18:06:11 pass2 brief (rim silhouettes + scatter sightlines); launching codex
2026-10-11 18:08:17 pass2 starting on PC via codex
2026-10-11 18:10:34 Pass2 visibility: 80/80 rim stretches visible from 363 tee/walkway samples; scatter screen all 18 holes, 0 removals (existing footprint exclusions already clear both corridors). Added reproducible rules and stable seeds; Blender 5.2 material API fix.
2026-10-11 18:10:34 Launch Blender 5.2: _src/sc_build.py --only rim_silhouette
2026-10-11 18:10:36 Blender exited: _src/sc_build.py (exit 0)
2026-10-11 18:12:46 Launch Blender 5.2: _src/render_hero.py --preview
2026-10-11 18:12:47 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:12:57 Launch Blender 5.2: _src/render_hero.py --preview
2026-10-11 18:12:58 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:13:01 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:13:01 Render start old_sugarloaf_skyline
2026-10-11 18:13:03 Render complete old_sugarloaf_skyline: 1.5s
2026-10-11 18:13:03 Render start dam_crest_walk
2026-10-11 18:13:04 Render complete dam_crest_walk: 1.1s
2026-10-11 18:13:04 Render start narrows_crystal_walls
2026-10-11 18:13:05 Render complete narrows_crystal_walls: 1.1s
2026-10-11 18:13:05 Render start junction_town
2026-10-11 18:13:06 Render complete junction_town: 1.1s
2026-10-11 18:13:06 Render start world_vista
2026-10-11 18:13:07 Render complete world_vista: 1.2s
2026-10-11 18:13:07 Render start sunset_arch_from_crown
2026-10-11 18:13:08 Render complete sunset_arch_from_crown: 1.0s
2026-10-11 18:13:08 Hero run finished in 10.6s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:13:09 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:13:58 Launch Blender 5.2: _src/render_hero.py --preview
2026-10-11 18:14:00 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:14:03 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:14:03 Render start old_sugarloaf_skyline
2026-10-11 18:14:05 Render complete old_sugarloaf_skyline: 1.5s
2026-10-11 18:14:05 Render start dam_crest_walk
2026-10-11 18:14:06 Render complete dam_crest_walk: 1.2s
2026-10-11 18:14:06 Render start narrows_crystal_walls
2026-10-11 18:14:07 Render complete narrows_crystal_walls: 1.2s
2026-10-11 18:14:07 Render start junction_town
2026-10-11 18:14:08 Render complete junction_town: 1.1s
2026-10-11 18:14:08 Render start world_vista
2026-10-11 18:14:09 Render complete world_vista: 1.2s
2026-10-11 18:14:09 Render start sunset_arch_from_crown
2026-10-11 18:14:11 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:14:11 Hero run finished in 11.0s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:14:12 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:14:53 Launch Blender 5.2: _src/render_hero.py --preview
2026-10-11 18:14:54 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:14:57 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:14:57 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:14:57 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:14:57 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:14:57 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:14:57 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:14:57 Render start old_sugarloaf_skyline
2026-10-11 18:14:59 Render complete old_sugarloaf_skyline: 1.4s
2026-10-11 18:14:59 Render start dam_crest_walk
2026-10-11 18:15:00 Render complete dam_crest_walk: 1.1s
2026-10-11 18:15:00 Render start narrows_crystal_walls
2026-10-11 18:15:01 Render complete narrows_crystal_walls: 1.2s
2026-10-11 18:15:01 Render start junction_town
2026-10-11 18:15:02 Render complete junction_town: 1.1s
2026-10-11 18:15:02 Render start world_vista
2026-10-11 18:15:03 Render complete world_vista: 1.1s
2026-10-11 18:15:03 Render start sunset_arch_from_crown
2026-10-11 18:15:04 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:15:04 Hero run finished in 10.4s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:15:05 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:15:27 Launch Blender 5.2: _src/render_hero.py --preview --shots world_vista,sunset_arch_from_crown
2026-10-11 18:15:28 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:15:31 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:15:31 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:31 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:31 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:31 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:31 Alpha restored CardTwins: STRAIGHT
2026-10-11 18:15:31 Alpha restored CardMesa: STRAIGHT
2026-10-11 18:15:31 Alpha restored CardArch: STRAIGHT
2026-10-11 18:15:31 Alpha restored SunGold: STRAIGHT
2026-10-11 18:15:31 Alpha restored CardButte: STRAIGHT
2026-10-11 18:15:31 Alpha restored CardCloud: STRAIGHT
2026-10-11 18:15:31 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:15:31 Render start world_vista
2026-10-11 18:15:33 Render complete world_vista: 1.4s
2026-10-11 18:15:33 Render start sunset_arch_from_crown
2026-10-11 18:15:34 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:15:34 Hero run finished in 5.7s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:15:34 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:15:48 Launch Blender 5.2: _src/render_hero.py --preview --shots sunset_arch_from_crown
2026-10-11 18:15:49 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:15:52 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:15:52 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:52 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:52 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:52 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:15:52 Alpha restored CardButte: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_butte.png
2026-10-11 18:15:52 Alpha restored SunGold: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha'), ('Color', 'Emission Color')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\sun_disc.png
2026-10-11 18:15:52 Alpha restored CardArch: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_far_arch.png
2026-10-11 18:15:52 Alpha restored CardCloud: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_cloud.png
2026-10-11 18:15:52 Alpha restored CardMesa: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_mesa.png
2026-10-11 18:15:52 Alpha restored CardTwins: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_twins.png
2026-10-11 18:15:52 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:15:52 Render start sunset_arch_from_crown
2026-10-11 18:15:54 Render complete sunset_arch_from_crown: 1.4s
2026-10-11 18:15:54 Hero run finished in 4.6s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:15:54 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:16:03 Launch Blender 5.2: _src/render_hero.py --preview --shots world_vista,sunset_arch_from_crown
2026-10-11 18:16:04 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:16:07 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:16:07 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:07 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:07 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:07 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:07 Alpha restored SunGold: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha'), ('Color', 'Emission Color')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\sun_disc.png
2026-10-11 18:16:07 Alpha restored CardTwins: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_twins.png
2026-10-11 18:16:07 Alpha restored CardMesa: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_mesa.png
2026-10-11 18:16:07 Alpha restored CardButte: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_butte.png
2026-10-11 18:16:07 Alpha restored CardCloud: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_cloud.png
2026-10-11 18:16:07 Alpha restored CardArch: STRAIGHT; links [('BSDF', 'Surface'), ('Color', 'Base Color'), ('Alpha', 'Alpha')]; image C:\Users\chase\sc\sugarloaf-canyon\models\textures\card_far_arch.png
2026-10-11 18:16:07 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:16:07 Render start world_vista
2026-10-11 18:16:09 Render complete world_vista: 1.4s
2026-10-11 18:16:09 Render start sunset_arch_from_crown
2026-10-11 18:16:10 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:16:10 Hero run finished in 6.0s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:16:11 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:16:43 Launch Blender 5.2: _src/render_hero.py --preview --shots world_vista,sunset_arch_from_crown
2026-10-11 18:16:44 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:16:47 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:16:47 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:47 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:48 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:48 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:16:48 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:16:48 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:16:48 Render start world_vista
2026-10-11 18:16:49 Render complete world_vista: 1.5s
2026-10-11 18:16:49 Render start sunset_arch_from_crown
2026-10-11 18:16:50 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:16:50 Hero run finished in 6.5s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:16:51 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:17:07 Launch Blender 5.2: _src/render_hero.py --preview --shots sunset_arch_from_crown
2026-10-11 18:17:08 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:17:11 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:17:11 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:17:11 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:17:11 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:17:11 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.0, 1.0, 0.0, 1.0)]
2026-10-11 18:17:11 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:11 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:17:11 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:17:13 Render complete sunset_arch_from_crown: 1.3s
2026-10-11 18:17:13 Hero run finished in 4.7s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:17:13 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:17:43 Launch Blender 5.2: _src/render_hero.py --preview --shots world_vista,sunset_arch_from_crown
2026-10-11 18:17:45 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:17:47 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:17:48 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:17:48 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:17:48 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:17:48 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:17:48 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:17:48 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:17:48 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:17:48 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:17:48 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:17:48 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:48 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:48 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:48 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:48 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:48 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:17:49 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:17:49 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:17:50 Render complete world_vista: 1.4s
2026-10-11 18:17:50 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:17:51 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 18:17:51 Hero run finished in 6.6s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:17:52 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:18:33 Launch Blender 5.2: _src/render_hero.py --preview --shots world_vista,sunset_arch_from_crown
2026-10-11 18:18:34 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:18:37 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:18:37 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:18:37 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:18:37 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:18:37 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:18:38 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:18:38 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:18:38 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:18:38 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:18:38 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:18:38 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:18:38 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:18:38 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:18:40 Render complete world_vista: 1.4s
2026-10-11 18:18:40 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:18:41 Render complete sunset_arch_from_crown: 1.0s
2026-10-11 18:18:41 Hero run finished in 6.6s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:18:41 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:19:16 Launch Blender 5.2: _src/render_hero.py --preview
2026-10-11 18:19:17 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:19:20 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:19:20 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:19:20 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:19:20 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:19:20 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:19:20 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:19:21 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:19:21 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:19:21 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:19:21 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:19:21 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:19:21 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:19:21 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 18:19:23 Render complete old_sugarloaf_skyline: 1.6s
2026-10-11 18:19:23 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 18:19:24 Render complete dam_crest_walk: 1.3s
2026-10-11 18:19:24 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 18:19:26 Render complete narrows_crystal_walls: 1.4s
2026-10-11 18:19:26 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 18:19:27 Render complete junction_town: 1.3s
2026-10-11 18:19:27 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:19:28 Render complete world_vista: 1.3s
2026-10-11 18:19:28 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:19:30 Render complete sunset_arch_from_crown: 1.4s
2026-10-11 18:19:30 Hero run finished in 12.8s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:19:30 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:20:33 Waiting for existing Blender process; next check in 60 seconds.
2026-10-11 18:21:33 Launch Blender 5.2: _src/render_hero.py 
2026-10-11 18:21:34 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:21:37 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:21:37 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:21:37 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:21:38 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:21:38 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:21:38 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:21:38 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:21:38 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:21:38 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:21:38 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:21:38 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:21:38 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:21:39 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 18:21:43 Render complete old_sugarloaf_skyline: 4.8s
2026-10-11 18:21:43 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 18:21:48 Render complete dam_crest_walk: 5.1s
2026-10-11 18:21:49 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 18:21:54 Render complete narrows_crystal_walls: 5.7s
2026-10-11 18:21:54 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 18:21:59 Render complete junction_town: 4.7s
2026-10-11 18:21:59 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:22:04 Render complete world_vista: 4.6s
2026-10-11 18:22:04 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:22:08 Render complete sunset_arch_from_crown: 4.5s
2026-10-11 18:22:08 Hero run finished in 34.2s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:22:09 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:23:44 Final QA: six 1920x1080 Cycles images inspected; added exact -640..640 terrain edge vertices. Refresh final stills and saved scene to match current render script; Crown shot remains last.
2026-10-11 18:23:44 Launch Blender 5.2: _src/render_hero.py 
2026-10-11 18:23:45 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:23:48 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:23:48 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:23:48 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:23:48 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:23:48 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:23:48 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:23:48 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:23:49 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:23:49 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:23:49 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:23:49 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:23:49 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:23:49 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 18:23:54 Render complete old_sugarloaf_skyline: 4.9s
2026-10-11 18:23:54 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 18:23:59 Render complete dam_crest_walk: 5.0s
2026-10-11 18:23:59 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 18:24:05 Render complete narrows_crystal_walls: 5.7s
2026-10-11 18:24:05 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 18:24:10 Render complete junction_town: 4.7s
2026-10-11 18:24:10 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:24:14 Render complete world_vista: 4.4s
2026-10-11 18:24:14 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:24:18 Render complete sunset_arch_from_crown: 4.2s
2026-10-11 18:24:18 Hero run finished in 33.7s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:24:19 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:24:32 Pass2 complete: ALL PASS, six final Cycles/OptiX PNG metadata checks (1920x1080, 128 samples), packed scene saved; manifest/layout/README/contact sheets/summary updated.
2026-10-11 18:35:40 pass3 starting on PC via codex
2026-10-11 18:50:03 pass3 relaunch (codex ended early after analysis)
2026-10-11 18:50:55 Pass3 steps 0-2: vistas reviewed; snapshots saved; cream/ochre/rose/terracotta maps and radius72 height110 rounded dome implemented.
2026-10-11 18:51:36 Launch Blender 5.2: _src/sc_build.py --only old_sugarloaf_shell,sunset_arch,mine_head,cliff_w24_h6_p0,cliff_w24_h6_p1,cliff_w24_h6_p2,cliff_w24_h6_p3,cliff_w24_h6_p4,cliff_w24_h6_p5,cliff_w24_h12_p0,cliff_w24_h12_p1,cliff_w24_h12_p2,cliff_w24_h12_p3,cliff_w24_h12_p4,cliff_w24_h12_p5,cliff_w24_h24_p0,cliff_w24_h24_p1,cliff_w24_h24_p2,cliff_w24_h24_p3,cliff_w24_h24_p4,cliff_w24_h24_p5,cliff_w24_h48_p0,cliff_w24_h48_p1,cliff_w24_h48_p2,cliff_w24_h48_p3,cliff_w24_h48_p4,cliff_w24_h48_p5,slot_w24_h24_p0,slot_w24_h24_p1,slot_w24_h24_p2,slot_w24_h24_p3,slot_w24_h24_p4,slot_w24_h24_p5,slot_w24_h48_p0,slot_w24_h48_p1,slot_w24_h48_p2,slot_w24_h48_p3,slot_w24_h48_p4,slot_w24_h48_p5,hoodoo_spire_a,hoodoo_spire_b,hoodoo_spire_c,hoodoo_spire_d,crystal_cluster_a,crystal_cluster_b,crystal_cluster_c,rock_a,rock_b,hoodoos_north,hoodoos_mid,hoodoos_south,narrows_crystals,scatter_junction,scatter_rock_candy_narrows,scatter_taffy_mesa,scatter_dam,scatter_hoodoo_garden,scatter_crown,rim_silhouette,distant_mesa_card,butte_spire_card,far_arch_card,far_butte_card
2026-10-11 18:51:45 Blender exited: _src/sc_build.py (exit 0)
2026-10-11 18:51:57 Launch Blender 5.2: _src/render_hero.py 
2026-10-11 18:51:57 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:52:00 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:52:00 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:52:00 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:52:00 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:52:00 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:52:00 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:52:00 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:52:00 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:52:00 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:52:00 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:52:00 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:00 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:00 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:00 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:00 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:00 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:52:01 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:52:01 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 18:52:05 Render complete old_sugarloaf_skyline: 4.6s
2026-10-11 18:52:05 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 18:52:10 Render complete dam_crest_walk: 4.7s
2026-10-11 18:52:10 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 18:52:15 Render complete narrows_crystal_walls: 5.1s
2026-10-11 18:52:15 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 18:52:20 Render complete junction_town: 4.6s
2026-10-11 18:52:20 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:52:24 Render complete world_vista: 4.1s
2026-10-11 18:52:24 Crown render-only exclusions: heightmap terrain, rim silhouettes, near sunset_arch; reveal far arch without moving world pieces
2026-10-11 18:52:24 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:52:28 Render complete sunset_arch_from_crown: 4.2s
2026-10-11 18:52:28 Hero run finished in 30.7s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:52:29 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:52:59 Launch Blender 5.2: _src/render_hero.py 
2026-10-11 18:53:00 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 18:53:02 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 18:53:02 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 18:53:02 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 18:53:02 Cutout CardButte: alpha 0.0..1.0
2026-10-11 18:53:02 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 18:53:02 Cutout CardArch: alpha 0.0..1.0
2026-10-11 18:53:02 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 18:53:03 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 18:53:03 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 18:53:03 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 18:53:03 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 18:53:03 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 18:53:03 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 18:53:07 Render complete old_sugarloaf_skyline: 4.4s
2026-10-11 18:53:07 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 18:53:12 Render complete dam_crest_walk: 4.6s
2026-10-11 18:53:12 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 18:53:17 Render complete narrows_crystal_walls: 5.0s
2026-10-11 18:53:17 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 18:53:21 Render complete junction_town: 4.5s
2026-10-11 18:53:21 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 18:53:26 Render complete world_vista: 4.0s
2026-10-11 18:53:26 Crown render-only exclusions: heightmap terrain, rim silhouettes, near sunset_arch; reveal far arch without moving world pieces
2026-10-11 18:53:26 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 18:53:29 Render complete sunset_arch_from_crown: 3.4s
2026-10-11 18:53:29 Hero run finished in 29.1s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
2026-10-11 18:53:30 Blender exited: _src/render_hero.py (exit 0)
2026-10-11 18:54:24 Pass3 steps3-7 complete: one review iteration, all six final metadata verified, ALL PASS, manifest/layout/README/counts/contact/compare/summary updated.
2026-10-11 18:54:42 Final self-review: six renders inspected; arch sun partially touches lintel, visible beneath it; dam plain spillway sheet visible. Remaining sparse layout/kit seams and illustration gap recorded.
2026-10-11 18:54:46 Pass3 steps3-7 complete: one review iteration, all six final metadata verified, ALL PASS, manifest/layout/README/counts/contact/compare/summary updated.

Pass4: backed up pass3 script; exposure 1.35, lavender ambient .65, stronger west key, peach/turquoise camera sky, lit cumulus; restored real Crown terrain/assets, low downstream dam with streak foam/spray/ring; revised cameras.
2026-10-11 20:28:41 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:28:43 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:28:43 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:28:43 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:28:43 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:28:43 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:28:43 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:28:43 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:28:43 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:28:43 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:28:43 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:28:43 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:43 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:43 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:43 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:43 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:43 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:28:44 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:28:44 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 20:28:44 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:28:45 Render complete old_sugarloaf_skyline: 1.3s
2026-10-11 20:28:45 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:28:47 Render complete dam_crest_walk: 1.4s
2026-10-11 20:28:47 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:28:48 Render complete narrows_crystal_walls: 1.2s
2026-10-11 20:28:48 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:28:49 Render complete junction_town: 1.2s
2026-10-11 20:28:49 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:28:50 Render complete world_vista: 1.1s
2026-10-11 20:28:50 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:28:51 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 20:28:51 Hero run finished in 10.5s; draft composition checks only
2026-10-11 20:29:28 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:29:30 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:29:30 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:29:30 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:29:30 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:29:30 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:29:30 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:29:30 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:29:30 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:29:30 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:29:31 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:29:31 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:29:31 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:29:31 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 20:29:31 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:29:33 Render complete old_sugarloaf_skyline: 1.3s
2026-10-11 20:29:33 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:29:34 Render complete dam_crest_walk: 1.4s
2026-10-11 20:29:34 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:29:35 Render complete narrows_crystal_walls: 1.2s
2026-10-11 20:29:35 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:29:37 Render complete junction_town: 1.2s
2026-10-11 20:29:37 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:29:38 Render complete world_vista: 1.1s
2026-10-11 20:29:38 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:29:39 Render complete sunset_arch_from_crown: 1.0s
2026-10-11 20:29:39 Hero run finished in 10.5s; draft composition checks only
2026-10-11 20:30:12 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:30:14 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:30:14 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:30:14 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:30:14 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:30:14 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:30:14 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:30:14 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:30:14 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:30:14 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:30:14 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:30:14 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:14 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:14 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:14 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:14 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:14 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:15 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:30:15 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; hardcoded sun 277/-3
2026-10-11 20:30:15 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:30:17 Render complete old_sugarloaf_skyline: 1.5s
2026-10-11 20:30:17 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:30:18 Render complete dam_crest_walk: 1.6s
2026-10-11 20:30:18 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:30:20 Render complete narrows_crystal_walls: 1.3s
2026-10-11 20:30:20 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:30:21 Render complete junction_town: 1.3s
2026-10-11 20:30:21 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:30:22 Render complete world_vista: 1.2s
2026-10-11 20:30:22 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:30:23 Render complete sunset_arch_from_crown: 1.2s
2026-10-11 20:30:23 Hero run finished in 11.6s; draft composition checks only
2026-10-11 20:30:50 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:30:52 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:30:52 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:30:52 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:30:52 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:30:52 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:30:52 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:30:52 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:30:52 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:30:52 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:30:52 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:30:53 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:30:53 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:30:53 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; west key 270/25; arch 270/8
2026-10-11 20:30:53 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:30:55 Render complete old_sugarloaf_skyline: 1.5s
2026-10-11 20:30:55 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:30:57 Render complete dam_crest_walk: 1.6s
2026-10-11 20:30:57 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:30:58 Render complete narrows_crystal_walls: 1.3s
2026-10-11 20:30:58 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:30:59 Render complete junction_town: 1.1s
2026-10-11 20:30:59 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:31:00 Render complete world_vista: 1.2s
2026-10-11 20:31:00 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:31:01 Render complete sunset_arch_from_crown: 1.1s
2026-10-11 20:31:01 Hero run finished in 11.6s; draft composition checks only
2026-10-11 20:31:08 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:31:10 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:31:10 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:31:10 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:31:10 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:31:10 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:31:11 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:31:11 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:31:11 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:31:11 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:31:11 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:31:11 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:11 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:11 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:11 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:11 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:11 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:12 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:31:12 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; west key 270/25; arch 270/8
2026-10-11 20:31:12 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:31:17 Render complete old_sugarloaf_skyline: 5.1s
2026-10-11 20:31:17 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:31:24 Render complete dam_crest_walk: 6.7s
2026-10-11 20:31:24 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:31:29 Render complete narrows_crystal_walls: 5.7s
2026-10-11 20:31:29 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:31:34 Render complete junction_town: 4.1s
2026-10-11 20:31:34 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:31:38 Render complete world_vista: 4.4s
2026-10-11 20:31:38 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:31:42 Render complete sunset_arch_from_crown: 4.1s
2026-10-11 20:31:42 Hero run finished in 33.9s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
Pass4 rounds 1-4 inspected: round4 junction camera intersected terrain; reverted to clear round3 camera. Initial full batch interrupted and superseded. Final set uses round3 junction, measured real arch with sun 270/8, full downstream spillway.
2026-10-11 20:31:46 Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls
2026-10-11 20:31:48 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-11 20:31:48 Cutout CardMesa: alpha 0.0..1.0
2026-10-11 20:31:48 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-11 20:31:48 Cutout CardButte: alpha 0.0..1.0
2026-10-11 20:31:48 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-11 20:31:48 Cutout CardArch: alpha 0.0..1.0
2026-10-11 20:31:48 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-11 20:31:48 Cutout CardTwins: alpha 0.0..1.0
2026-10-11 20:31:48 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-11 20:31:48 Cutout CardCloud: alpha 0.0..1.0
2026-10-11 20:31:48 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:48 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:48 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:48 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:48 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:48 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-11 20:31:49 Pass4 imported arch bounds local game: [-8.807289123535156, -2.4000041484832764, -25.719911575317383]..[8.946002960205078, 46.64734649658203, 25.906667709350586]; central inner lintel world y=223.200; opening centre z=205, base y=190.4
2026-10-11 20:31:49 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; west key 270/25; arch 270/8
2026-10-11 20:31:49 Render start old_sugarloaf_skyline engine=CYCLES context=CYCLES
2026-10-11 20:31:54 Render complete old_sugarloaf_skyline: 5.0s
2026-10-11 20:31:54 Render start dam_crest_walk engine=CYCLES context=CYCLES
2026-10-11 20:32:01 Render complete dam_crest_walk: 6.6s
2026-10-11 20:32:01 Render start narrows_crystal_walls engine=CYCLES context=CYCLES
2026-10-11 20:32:07 Render complete narrows_crystal_walls: 5.7s
2026-10-11 20:32:07 Render start junction_town engine=CYCLES context=CYCLES
2026-10-11 20:32:12 Render complete junction_town: 5.6s
2026-10-11 20:32:13 Render start world_vista engine=CYCLES context=CYCLES
2026-10-11 20:32:17 Render complete world_vista: 4.4s
2026-10-11 20:32:17 Render start sunset_arch_from_crown engine=CYCLES context=CYCLES
2026-10-11 20:32:21 Render complete sunset_arch_from_crown: 4.1s
2026-10-11 20:32:21 Hero run finished in 35.4s; scene saved C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\sugarloaf_canyon_hero.blend
Pass4 final completed: six 1920x1080 Cycles OptiX PNGs, packed blend and report; generated labelled contact and vista comparison sheets; summary records camera/sun data and remaining gaps.
2026-10-12 09:42:26 PASS5 start (Claude): read README, pass2/pass4 summaries, sclib, sc_pieces, sc_build, sc_fitcheck, render_hero; tasks gondola cable+cabin, 0.15 holes fitcheck, V1 staged hero
2026-10-12 09:48:55 Task1: gondola_geom.py (attach points from exported station bull wheel; straight chord cuts ~37 studs into the Crown cliff and H17 sits under the line -> one portal support tower at plan d=524 on the Crown lip, rope crest y221, sags 10/2.5), sc_gondola.py builders, sc_build_pass5.py written
2026-10-12 09:48:55 Launch Blender 5.2: sc_build_pass5.py 
2026-10-12 09:48:56 [pass5 build] gondola_cable: tris 2012 max mesh 928 meshparts 5 bbox [553.54, 199.95, 420.0] centre [-274.41, 99.83, -206.8] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cable.fbx
2026-10-12 09:48:57 [pass5 build] previews ['previews\\gondola_cable_eye.png', 'previews\\gondola_cable_34.png']
2026-10-12 09:48:57 [pass5 build] gondola_cabin: tris 512 max mesh 180 meshparts 7 bbox [5.46, 6.95, 6.3] centre [0.0, -2.93, -0.0] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cabin.fbx
2026-10-12 09:48:57 [pass5 build] previews ['previews\\gondola_cabin_eye.png', 'previews\\gondola_cabin_34.png']
2026-10-12 09:48:57 [pass5 reimport] gondola_cable: PASS tris 2012 bbox [553.54, 199.95, 420.0]
2026-10-12 09:48:57 [pass5 reimport] gondola_cabin: PASS tris 512 bbox [5.46, 6.95, 6.3]
2026-10-12 09:48:57 [pass5 build] done in 1s; reimport ALL PASS
2026-10-12 09:48:58 Blender exited: sc_build_pass5.py (exit 0)
2026-10-12 09:49:20 Launch Blender 5.2: sc_build_pass5.py 
2026-10-12 09:49:21 [pass5 build] gondola_cable: tris 2012 max mesh 928 meshparts 5 bbox [553.54, 199.95, 420.0] centre [-274.41, 99.83, -206.8] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cable.fbx
2026-10-12 09:49:21 [pass5 build] previews ['previews\\gondola_cable_eye.png', 'previews\\gondola_cable_34.png']
2026-10-12 09:49:22 [pass5 build] gondola_cabin: tris 512 max mesh 180 meshparts 7 bbox [5.46, 6.95, 6.3] centre [0.0, -2.93, -0.0] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cabin.fbx
2026-10-12 09:49:22 [pass5 build] previews ['previews\\gondola_cabin_eye.png', 'previews\\gondola_cabin_34.png']
2026-10-12 09:49:22 [pass5 reimport] gondola_cable: PASS tris 2012 bbox [553.54, 199.95, 420.0]
2026-10-12 09:49:22 [pass5 reimport] gondola_cabin: PASS tris 512 bbox [5.46, 6.95, 6.3]
2026-10-12 09:49:22 [pass5 build] done in 1s; reimport ALL PASS
2026-10-12 09:49:22 Blender exited: sc_build_pass5.py (exit 0)
2026-10-12 09:50:23 Task1: built gondola_cable (2012 tris, 5 meshparts) + gondola_cabin (512 tris, 7 meshparts) -> fbx/, previews, reimport ALL PASS; finalize_pass5.py merged manifest/layout/pieces_table (backups in backup_pass5)
2026-10-12 09:50:33 Launch Blender 5.2: sc_build_pass5.py 
2026-10-12 09:50:33 [pass5 build] gondola_cable: tris 2012 max mesh 928 meshparts 5 bbox [553.54, 199.95, 420.0] centre [-274.41, 99.83, -206.8] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cable.fbx
2026-10-12 09:50:34 [pass5 build] previews ['previews\\gondola_cable_eye.png', 'previews\\gondola_cable_34.png']
2026-10-12 09:50:34 [pass5 build] gondola_cabin: tris 512 max mesh 180 meshparts 7 bbox [5.46, 6.95, 6.3] centre [0.0, -2.93, -0.0] -> C:\Users\chase\sc\sugarloaf-canyon\models\fbx\gondola_cabin.fbx
2026-10-12 09:50:34 [pass5 build] previews ['previews\\gondola_cabin_eye.png', 'previews\\gondola_cabin_34.png']
2026-10-12 09:50:34 [pass5 reimport] gondola_cable: PASS tris 2012 bbox [553.54, 199.95, 420.0]
2026-10-12 09:50:34 [pass5 reimport] gondola_cabin: PASS tris 512 bbox [5.46, 6.95, 6.3]
2026-10-12 09:50:34 [pass5 build] done in 1s; reimport ALL PASS
2026-10-12 09:50:35 Blender exited: sc_build_pass5.py (exit 0)
2026-10-12 10:21:27 PASS5b start (Claude): render + docs only. Backed up render_hero.py to backup_pass5b (README.md, contact_sheet.png already there); copied to render_hero_pass5.py for staged V1-hub-tee1 + gondola_span
2026-10-12 10:23:12 Launch Blender 5.2: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py --preview
2026-10-12 10:23:12 Pass5b hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls, staged holes
2026-10-12 10:23:15 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-12 10:23:15 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 10:23:15 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 10:23:15 Cutout CardButte: alpha 0.0..1.0
2026-10-12 10:23:15 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 10:23:15 Cutout CardArch: alpha 0.0..1.0
2026-10-12 10:23:15 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 10:23:15 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 10:23:15 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 10:23:15 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 10:23:15 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:15 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:15 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:15 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:15 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:15 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:23:17 Pass5b staging (render-only, holes.json): 126 felt slabs, 308 rails (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 10:23:17 Pass5b relight: key sun 277/7 energy 5.0 (1,.55,.24); orange rim sun energy 2.2 (1,.42,.12); sky #FFB98A>#F48A8C>#B864A0>#6A4FA3
2026-10-12 10:23:17 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass5b key 277/7
2026-10-12 10:23:17 Render start V1-hub-tee1 eye=[60.0, 23.5, 475.0] target=[80.0, -61.5, -130.0] fov=75 key=277/7 rim=330/10
2026-10-12 10:23:20 Render complete V1-hub-tee1: 3.5s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass5b_draft.png
2026-10-12 10:23:20 Render start gondola_span eye=[246.0, 330.0, -184.0] target=[-145.0, 111.0, 335.0] fov=65 key=277/22 rim=300/10
2026-10-12 10:23:23 Render complete gondola_span: 2.7s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\gondola_span_pass5b_draft.png
2026-10-12 10:23:23 Pass5b hero run finished in 10.5s (preview)
2026-10-12 10:23:24 Blender exited: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py (exit 0)
2026-10-12 10:23:59 Pass5b preview1 reviewed: V1 too tight on H1 lane, sky not violet enough, light flat; gondola_span far cards read as slabs. Adjust: V1 eye (60,25.5,482) fov78 pitch -7, key energy 6.5, sky ramp tightened, hide far cards in gondola_span
2026-10-12 10:24:02 Launch Blender 5.2: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py --preview
2026-10-12 10:24:03 Pass5b hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls, staged holes
2026-10-12 10:24:05 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-12 10:24:05 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 10:24:05 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 10:24:05 Cutout CardButte: alpha 0.0..1.0
2026-10-12 10:24:05 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 10:24:05 Cutout CardArch: alpha 0.0..1.0
2026-10-12 10:24:05 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 10:24:05 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 10:24:06 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 10:24:06 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 10:24:06 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:06 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:06 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:06 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:06 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:06 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:07 Pass5b staging (render-only, holes.json): 126 felt slabs, 308 rails (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 10:24:07 Pass5b relight: key sun 277/7 energy 6.5 (1,.55,.24); orange rim sun energy 2.2 (1,.42,.12); sky #FFB98A>#F48A8C>#B864A0>#6A4FA3
2026-10-12 10:24:07 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass5b key 277/7
2026-10-12 10:24:07 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/7 rim=330/10
2026-10-12 10:24:11 Render complete V1-hub-tee1: 4.0s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass5b_draft.png
2026-10-12 10:24:11 Render start gondola_span eye=[246.0, 330.0, -184.0] target=[-145.0, 111.0, 335.0] fov=65 key=277/22 rim=300/10
2026-10-12 10:24:15 Render complete gondola_span: 3.7s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\gondola_span_pass5b_draft.png
2026-10-12 10:24:15 Pass5b hero run finished in 12.1s (preview)
2026-10-12 10:24:15 Blender exited: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py (exit 0)
2026-10-12 10:24:34 Pass5b preview2: V1 framing OK (H1 lane+flag foreground, Old Sugarloaf centred, violet sky top). gondola_span: top 40% empty sky -> eye y400, target (-145,80,335)
2026-10-12 10:24:35 Launch Blender 5.2: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py --preview,--shots,gondola_span
2026-10-12 10:24:35 Pass5b hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls, staged holes
2026-10-12 10:24:37 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-12 10:24:38 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 10:24:38 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 10:24:38 Cutout CardButte: alpha 0.0..1.0
2026-10-12 10:24:38 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 10:24:38 Cutout CardArch: alpha 0.0..1.0
2026-10-12 10:24:38 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 10:24:38 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 10:24:38 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 10:24:38 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 10:24:38 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:38 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:38 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:38 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:38 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:38 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:24:39 Pass5b staging (render-only, holes.json): 126 felt slabs, 308 rails (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 10:24:39 Pass5b relight: key sun 277/7 energy 6.5 (1,.55,.24); orange rim sun energy 2.2 (1,.42,.12); sky #FFB98A>#F48A8C>#B864A0>#6A4FA3
2026-10-12 10:24:39 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; pass5b key 277/7
2026-10-12 10:24:39 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/7 rim=330/10
2026-10-12 10:24:51 Render complete V1-hub-tee1: 11.8s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_staged.png
2026-10-12 10:24:51 Render start gondola_span eye=[246.0, 400.0, -184.0] target=[-145.0, 80.0, 335.0] fov=65 key=277/22 rim=300/10
2026-10-12 10:25:03 Render complete gondola_span: 11.4s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\gondola_span.png
2026-10-12 10:25:03 Pass5b hero run finished in 27.7s
2026-10-12 10:25:04 Blender exited: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py (exit 0)
2026-10-12 10:25:29 Pass5b note: preview3 args were joined by powershell -File, so the run was the full 128-sample 1920x1080 for both shots. gondola_span.png accepted (ropes, tower and both stations readable). V1 felt read teal under the lavender ambient -> felt ramp #23962F..#52C24A; re-render V1 final
2026-10-12 10:25:29 Launch Blender 5.2: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py --shots V1-hub-tee1
2026-10-12 10:25:30 Pass5b hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls, staged holes
2026-10-12 10:25:32 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8888888955116272, 0.8888888955116272, 0.0, 0.7777777910232544)]
2026-10-12 10:25:32 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 10:25:32 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 10:25:32 Cutout CardButte: alpha 0.0..1.0
2026-10-12 10:25:32 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 10:25:32 Cutout CardArch: alpha 0.0..1.0
2026-10-12 10:25:32 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 10:25:33 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 10:25:33 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 10:25:33 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 10:25:33 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:33 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:33 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:33 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:33 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:33 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 10:25:34 Pass5b staging (render-only, holes.json): 126 felt slabs, 308 rails (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 10:25:34 Pass5b relight: key sun 277/7 energy 6.5 (1,.55,.24); orange rim sun energy 2.2 (1,.42,.12); sky #FFB98A>#F48A8C>#B864A0>#6A4FA3
2026-10-12 10:25:34 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; pass5b key 277/7
2026-10-12 10:25:34 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/7 rim=330/10
2026-10-12 10:25:46 Render complete V1-hub-tee1: 11.7s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_staged.png
2026-10-12 10:25:46 Pass5b hero run finished in 16.1s
2026-10-12 10:25:46 Blender exited: C:\Users\chase\sc\sugarloaf-canyon\models\_src\render_hero_pass5.py (exit 0)
2026-10-12 10:26:12 Pass5b finalize: V1-hub-tee1_vs_concept.png written; contact_sheet.png regenerated (1600, 4790) with 72 piece thumbnails incl ['gondola_station', 'gondola_cable', 'gondola_cabin']; pass5b_render_report.json
2026-10-12 10:26:40 Pass5b README.md: appended 'Pass 5 (Sunset Gondola) + 5b' section (backup _src/backup_pass5b/README.md)
2026-10-12 10:27:07 PASS5b complete: pass5b_summary.md written, pass5b_done.flag created
2026-10-12 11:11:28 PASS6 start (Claude): snapshot manifest.json, layout.json, README.md, pieces_table.md -> _src/backup_pass6/
2026-10-12 11:18:59 Launch Blender 5.2: _src/sc_build_pass6.py --step1
2026-10-12 11:19:00 [pass6 build] gondola_cable: tris 2000 max mesh 928 meshparts 7 bbox [553.54, 199.95, 420.0] -> ['fbx/gondola_cable.fbx']
2026-10-12 11:19:00 [pass6 reimport] fbx/gondola_cable.fbx: PASS tris 2000 bbox [553.54, 199.95, 420.0]
2026-10-12 11:19:00 [pass6 step1] gondola_cable recolour at the pass-5 line: tris 2000 vs 2012, bbox [553.54, 199.95, 420.0] vs [553.54, 199.95, 420.0], centre [-274.41, 99.83, -206.8] vs [-274.41, 99.83, -206.8] -> DIFFERENT
2026-10-12 11:19:01 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:19:16 Launch Blender 5.2: _src/sc_build_pass6.py --step1
2026-10-12 11:19:16 [pass6 build] gondola_cable: tris 2012 max mesh 928 meshparts 8 bbox [553.54, 199.95, 420.0] -> ['fbx/gondola_cable.fbx']
2026-10-12 11:19:17 [pass6 reimport] fbx/gondola_cable.fbx: PASS tris 2012 bbox [553.54, 199.95, 420.0]
2026-10-12 11:19:17 [pass6 step1] gondola_cable recolour at the pass-5 line: tris 2012 vs 2012, bbox [553.54, 199.95, 420.0] vs [553.54, 199.95, 420.0], centre [-274.41, 99.83, -206.8] vs [-274.41, 99.83, -206.8] -> IDENTICAL
2026-10-12 11:19:17 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:19:24 PASS6 step 1: gondola tower recolour (TimberWeathered legs/lattice, crossbeam baulks alternating TimberWeathered/Timber, Iron saddles+links+cradles, Brass bolt plates, sheaves PepRed/MintWhite) rebuilt on the pass-5 line: tris 2012 = 2012, bbox [553.54,199.95,420.0] and centre identical, reimport PASS (_cache/pass6_step1.json; FBX kept as _cache/p6/gondola_cable_step1_recolour_pass5line.fbx). First try gave 2000 tris: same-material butted baulks lost 12 coincident end-face tris in remove_doubles -> alternate two timber tones.
2026-10-12 11:19:24 Launch Blender 5.2: _src/sc_build_pass6.py --only gondola_station_bottom,gondola_cable --tag gondola
2026-10-12 11:19:25 [pass6 build] 2 pieces: ['gondola_cable', 'gondola_station_bottom']
2026-10-12 11:19:25 [pass6 build] gondola_cable: tris 2012 max mesh 928 meshparts 8 bbox [553.54, 192.75, 420.0] -> ['fbx/gondola_cable.fbx']
2026-10-12 11:19:25 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:19:30 Launch Blender 5.2: _src/sc_build_pass6.py --only gondola_station_bottom,gondola_cable --tag gondola
2026-10-12 11:19:31 [pass6 build] 2 pieces: ['gondola_station_bottom', 'gondola_cable']
2026-10-12 11:19:31 [pass6 build] gondola_station_bottom: tris 2205 max mesh 744 meshparts 7 bbox [22.0, 21.2, 15.2] -> ['fbx/gondola_station_bottom.fbx']
2026-10-12 11:19:32 [pass6 build] gondola_cable: tris 2012 max mesh 928 meshparts 8 bbox [553.54, 192.75, 420.0] -> ['fbx/gondola_cable.fbx']
2026-10-12 11:19:32 [pass6 reimport] fbx/gondola_station_bottom.fbx: PASS tris 2205 bbox [22.0, 21.2, 15.2]
2026-10-12 11:19:32 [pass6 reimport] fbx/gondola_cable.fbx: PASS tris 2012 bbox [553.54, 192.75, 420.0]
2026-10-12 11:19:32 [pass6 build] done 2 pieces in 1s; reimport ALL PASS (_cache/reimport_pass6_gondola.json)
2026-10-12 11:19:32 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:23:01 PASS6 step 1b: gondola_station_bottom (station +7.2 on timber/sandstone undercroft, 10-riser side stair, 2205 tris) + gondola_cable rebuilt with bottom wheel y 25.6->32.8 (2012 tris, bbox [553.54,192.75,420.0]); layout: bottom instance -> gondola_station_bottom, cable pivot (130.392,32.8,542.811), cabin parked (132.65,32.8,539.755). sc_fitcheck_holes.py pass-6 edition ([B] edge-railing rule for railing_12/peppermint_dam: tris in outer 0.6 of the corridor and <= 4.0 high skipped as INFO; [A] hole_dressing exempt; new [C] lane rules, [D] near-field). Run: p_h18_hub seg 3 PASS, gondola min 10.04 above the walk; ALL PASS before new dressing.
2026-10-12 11:28:12 Launch Blender 5.2: _src/sc_build_pass6.py --group dressing_kit,hole_dressing --tag kit1
2026-10-12 11:28:12 [pass6 build] 16 pieces: ['trading_post_deck', 'barrel_a', 'barrel_b', 'lantern_post', 'lantern_hanging', 'lollipop_cactus_cluster', 'rock_candy_cluster', 'gumdrop_shrub_a', 'gumdrop_shrub_b', 'gumdrop_shrub_c', 'boulder_scatter', 'fallen_rock_scatter', 'red_dirt_patch_a', 'red_dirt_patch_b', 'pebble_scatter', 'clay_brick_edging']
2026-10-12 11:28:13 [pass6 build] trading_post_deck: tris 3504 max mesh 840 meshparts 17 bbox [22.0, 8.55, 11.82] -> ['fbx/trading_post_deck.fbx']
2026-10-12 11:28:13 [pass6 build] barrel_a: tris 252 max mesh 96 meshparts 4 bbox [1.6, 2.02, 1.59] -> ['fbx/barrel_a.fbx']
2026-10-12 11:28:14 [pass6 build] barrel_b: tris 456 max mesh 96 meshparts 8 bbox [1.6, 2.17, 1.59] -> ['fbx/barrel_b.fbx']
2026-10-12 11:28:14 [pass6 build] lantern_post: tris 244 max mesh 108 meshparts 7 bbox [0.9, 5.9, 1.95] -> ['fbx/lantern_post.fbx']
2026-10-12 11:28:14 [pass6 build] lantern_hanging: tris 156 max mesh 108 meshparts 4 bbox [0.62, 1.27, 0.64] -> ['fbx/lantern_hanging.fbx']
2026-10-12 11:28:14 [pass6 build] lollipop_cactus_cluster: tris 696 max mesh 308 meshparts 6 bbox [4.01, 7.02, 3.04] -> ['fbx/lollipop_cactus_cluster.fbx']
2026-10-12 11:28:14 [pass6 build] rock_candy_cluster: tris 204 max mesh 102 meshparts 4 bbox [3.09, 3.9, 2.67] -> ['fbx/rock_candy_cluster.fbx']
2026-10-12 11:28:14 [pass6 build] gumdrop_shrub_a: tris 352 max mesh 102 meshparts 4 bbox [1.97, 1.47, 1.64] -> ['fbx/gumdrop_shrub_a.fbx']
2026-10-12 11:28:14 [pass6 build] gumdrop_shrub_b: tris 236 max mesh 136 meshparts 3 bbox [2.14, 2.08, 1.79] -> ['fbx/gumdrop_shrub_b.fbx']
2026-10-12 11:28:15 [pass6 build] gumdrop_shrub_c: tris 216 max mesh 80 meshparts 4 bbox [2.91, 1.09, 1.94] -> ['fbx/gumdrop_shrub_c.fbx']
2026-10-12 11:28:15 [pass6 build] boulder_scatter: tris 60 max mesh 60 meshparts 1 bbox [4.68, 2.06, 2.79] -> ['fbx/boulder_scatter.fbx']
2026-10-12 11:28:15 [pass6 build] fallen_rock_scatter: tris 100 max mesh 60 meshparts 2 bbox [3.17, 0.85, 2.49] -> ['fbx/fallen_rock_scatter.fbx']
2026-10-12 11:28:15 [pass6 build] red_dirt_patch_a: tris 36 max mesh 24 meshparts 2 bbox [5.84, 0.03, 6.21] -> ['fbx/red_dirt_patch_a.fbx']
2026-10-12 11:28:15 [pass6 build] red_dirt_patch_b: tris 36 max mesh 24 meshparts 2 bbox [8.33, 0.03, 8.39] -> ['fbx/red_dirt_patch_b.fbx']
2026-10-12 11:28:15 [pass6 build] pebble_scatter: tris 80 max mesh 48 meshparts 2 bbox [2.42, 0.3, 2.62] -> ['fbx/pebble_scatter.fbx']
2026-10-12 11:28:15 [pass6 build] clay_brick_edging: tris 120 max mesh 120 meshparts 1 bbox [0.7, 0.45, 8.0] -> ['fbx/clay_brick_edging.fbx']
2026-10-12 11:28:16 [pass6 reimport] fbx/trading_post_deck.fbx: PASS tris 3504 bbox [22.0, 8.55, 11.82]
2026-10-12 11:28:16 [pass6 reimport] fbx/barrel_a.fbx: PASS tris 252 bbox [1.6, 2.02, 1.59]
2026-10-12 11:28:16 [pass6 reimport] fbx/barrel_b.fbx: PASS tris 456 bbox [1.6, 2.17, 1.59]
2026-10-12 11:28:16 [pass6 reimport] fbx/lantern_post.fbx: PASS tris 244 bbox [0.9, 5.9, 1.95]
2026-10-12 11:28:16 [pass6 reimport] fbx/lantern_hanging.fbx: PASS tris 156 bbox [0.62, 1.27, 0.64]
2026-10-12 11:28:16 [pass6 reimport] fbx/lollipop_cactus_cluster.fbx: PASS tris 696 bbox [4.01, 7.02, 3.04]
2026-10-12 11:28:16 [pass6 reimport] fbx/rock_candy_cluster.fbx: PASS tris 204 bbox [3.09, 3.9, 2.67]
2026-10-12 11:28:16 [pass6 reimport] fbx/gumdrop_shrub_a.fbx: PASS tris 352 bbox [1.97, 1.47, 1.64]
2026-10-12 11:28:16 [pass6 reimport] fbx/gumdrop_shrub_b.fbx: PASS tris 236 bbox [2.14, 2.08, 1.79]
2026-10-12 11:28:16 [pass6 reimport] fbx/gumdrop_shrub_c.fbx: PASS tris 216 bbox [2.91, 1.09, 1.94]
2026-10-12 11:28:16 [pass6 reimport] fbx/boulder_scatter.fbx: PASS tris 60 bbox [4.68, 2.06, 2.79]
2026-10-12 11:28:16 [pass6 reimport] fbx/fallen_rock_scatter.fbx: PASS tris 100 bbox [3.17, 0.85, 2.49]
2026-10-12 11:28:16 [pass6 reimport] fbx/red_dirt_patch_a.fbx: PASS tris 36 bbox [5.84, 0.03, 6.21]
2026-10-12 11:28:16 [pass6 reimport] fbx/red_dirt_patch_b.fbx: PASS tris 36 bbox [8.33, 0.03, 8.39]
2026-10-12 11:28:16 [pass6 reimport] fbx/pebble_scatter.fbx: PASS tris 80 bbox [2.42, 0.3, 2.62]
2026-10-12 11:28:16 [pass6 reimport] fbx/clay_brick_edging.fbx: PASS tris 120 bbox [0.7, 0.45, 8.0]
2026-10-12 11:28:16 [pass6 build] done 16 pieces in 4s; reimport ALL PASS (_cache/reimport_pass6_kit1.json)
2026-10-12 11:28:17 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:32:52 Launch Blender 5.2: _src/sc_build_pass6.py --group dressing_kit,hole_dressing --tag kit2
2026-10-12 11:32:52 [pass6 build] 16 pieces: ['trading_post_deck', 'barrel_a', 'barrel_b', 'lantern_post', 'lantern_hanging', 'lollipop_cactus_cluster', 'rock_candy_cluster', 'gumdrop_shrub_a', 'gumdrop_shrub_b', 'gumdrop_shrub_c', 'boulder_scatter', 'fallen_rock_scatter', 'red_dirt_patch_a', 'red_dirt_patch_b', 'pebble_scatter', 'clay_brick_edging']
2026-10-12 11:32:53 [pass6 build] trading_post_deck: tris 3840 max mesh 840 meshparts 17 bbox [22.0, 8.55, 11.82] -> ['fbx/trading_post_deck.fbx']
2026-10-12 11:32:53 [pass6 build] barrel_a: tris 252 max mesh 96 meshparts 4 bbox [1.6, 2.02, 1.59] -> ['fbx/barrel_a.fbx']
2026-10-12 11:32:53 [pass6 build] barrel_b: tris 624 max mesh 128 meshparts 8 bbox [1.6, 2.17, 1.59] -> ['fbx/barrel_b.fbx']
2026-10-12 11:32:54 [pass6 build] lantern_post: tris 244 max mesh 108 meshparts 7 bbox [0.9, 5.9, 1.95] -> ['fbx/lantern_post.fbx']
2026-10-12 11:32:54 [pass6 build] lantern_hanging: tris 156 max mesh 108 meshparts 4 bbox [0.62, 1.27, 0.64] -> ['fbx/lantern_hanging.fbx']
2026-10-12 11:32:54 [pass6 build] lollipop_cactus_cluster: tris 696 max mesh 308 meshparts 6 bbox [4.01, 7.02, 3.04] -> ['fbx/lollipop_cactus_cluster.fbx']
2026-10-12 11:32:54 [pass6 build] rock_candy_cluster: tris 264 max mesh 102 meshparts 4 bbox [3.09, 3.9, 2.81] -> ['fbx/rock_candy_cluster.fbx']
2026-10-12 11:32:54 [pass6 build] gumdrop_shrub_a: tris 592 max mesh 320 meshparts 4 bbox [1.97, 1.47, 1.82] -> ['fbx/gumdrop_shrub_a.fbx']
2026-10-12 11:32:54 [pass6 build] gumdrop_shrub_b: tris 356 max mesh 160 meshparts 3 bbox [2.15, 2.08, 1.9] -> ['fbx/gumdrop_shrub_b.fbx']
2026-10-12 11:32:54 [pass6 build] gumdrop_shrub_c: tris 456 max mesh 320 meshparts 4 bbox [2.91, 1.09, 2.01] -> ['fbx/gumdrop_shrub_c.fbx']
2026-10-12 11:32:54 [pass6 build] boulder_scatter: tris 180 max mesh 180 meshparts 1 bbox [5.06, 2.06, 3.06] -> ['fbx/boulder_scatter.fbx']
2026-10-12 11:32:55 [pass6 build] fallen_rock_scatter: tris 100 max mesh 60 meshparts 2 bbox [3.17, 0.85, 2.49] -> ['fbx/fallen_rock_scatter.fbx']
2026-10-12 11:32:55 [pass6 build] red_dirt_patch_a: tris 36 max mesh 24 meshparts 2 bbox [5.84, 0.03, 6.21] -> ['fbx/red_dirt_patch_a.fbx']
2026-10-12 11:32:55 [pass6 build] red_dirt_patch_b: tris 36 max mesh 24 meshparts 2 bbox [8.33, 0.03, 8.39] -> ['fbx/red_dirt_patch_b.fbx']
2026-10-12 11:32:55 [pass6 build] pebble_scatter: tris 80 max mesh 48 meshparts 2 bbox [2.42, 0.3, 2.62] -> ['fbx/pebble_scatter.fbx']
2026-10-12 11:32:55 [pass6 build] clay_brick_edging: tris 120 max mesh 120 meshparts 1 bbox [0.7, 0.45, 8.0] -> ['fbx/clay_brick_edging.fbx']
2026-10-12 11:32:55 [pass6 reimport] fbx/trading_post_deck.fbx: PASS tris 3840 bbox [22.0, 8.55, 11.82]
2026-10-12 11:32:55 [pass6 reimport] fbx/barrel_a.fbx: PASS tris 252 bbox [1.6, 2.02, 1.59]
2026-10-12 11:32:55 [pass6 reimport] fbx/barrel_b.fbx: PASS tris 624 bbox [1.6, 2.17, 1.59]
2026-10-12 11:32:55 [pass6 reimport] fbx/lantern_post.fbx: PASS tris 244 bbox [0.9, 5.9, 1.95]
2026-10-12 11:32:55 [pass6 reimport] fbx/lantern_hanging.fbx: PASS tris 156 bbox [0.62, 1.27, 0.64]
2026-10-12 11:32:55 [pass6 reimport] fbx/lollipop_cactus_cluster.fbx: PASS tris 696 bbox [4.01, 7.02, 3.04]
2026-10-12 11:32:55 [pass6 reimport] fbx/rock_candy_cluster.fbx: PASS tris 264 bbox [3.09, 3.9, 2.81]
2026-10-12 11:32:55 [pass6 reimport] fbx/gumdrop_shrub_a.fbx: PASS tris 592 bbox [1.97, 1.47, 1.82]
2026-10-12 11:32:56 [pass6 reimport] fbx/gumdrop_shrub_b.fbx: PASS tris 356 bbox [2.15, 2.08, 1.9]
2026-10-12 11:32:56 [pass6 reimport] fbx/gumdrop_shrub_c.fbx: PASS tris 456 bbox [2.91, 1.09, 2.01]
2026-10-12 11:32:56 [pass6 reimport] fbx/boulder_scatter.fbx: PASS tris 180 bbox [5.06, 2.06, 3.06]
2026-10-12 11:32:56 [pass6 reimport] fbx/fallen_rock_scatter.fbx: PASS tris 100 bbox [3.17, 0.85, 2.49]
2026-10-12 11:32:56 [pass6 reimport] fbx/red_dirt_patch_a.fbx: PASS tris 36 bbox [5.84, 0.03, 6.21]
2026-10-12 11:32:56 [pass6 reimport] fbx/red_dirt_patch_b.fbx: PASS tris 36 bbox [8.33, 0.03, 8.39]
2026-10-12 11:32:56 [pass6 reimport] fbx/pebble_scatter.fbx: PASS tris 80 bbox [2.42, 0.3, 2.62]
2026-10-12 11:32:56 [pass6 reimport] fbx/clay_brick_edging.fbx: PASS tris 120 bbox [0.7, 0.45, 8.0]
2026-10-12 11:32:56 [pass6 build] done 16 pieces in 3s; reimport ALL PASS (_cache/reimport_pass6_kit2.json)
2026-10-12 11:32:56 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:33:01 PASS6 step 2/3: new kit built (16 pieces, reimport ALL PASS): trading_post_deck 3840, barrel_a 252, barrel_b 624, lantern_post 244, lantern_hanging 156, lollipop_cactus_cluster 696, rock_candy_cluster 264, gumdrop_shrub_a/b/c 592/356/456, boulder_scatter 180, fallen_rock_scatter 100, red_dirt_patch_a/b 36/36, pebble_scatter 80, clay_brick_edging 120. New materials TimberWeathered/Brass/LanternGlow/Canvas/CanvasRed/ClayBrick/RedDirt/RedDirtLight/Pebble; textures timber_weathered, clay_brick, red_dirt, red_dirt_light (sc_textures_pass6.py). Running sc_dress_pass6.py placement.
2026-10-12 11:37:13 Launch Blender 5.2: _src/sc_build_pass6.py --group hole_dressing --tag dress1
2026-10-12 11:37:13 [pass6 build] 54 pieces: ['trading_post_deck', 'h01_dress_props', 'h01_dress_plants', 'h01_ground', 'h02_dress_props', 'h02_dress_plants', 'h02_ground', 'h03_dress_props', 'h03_dress_plants', 'h03_ground', 'h04_dress_props', 'h04_ground', 'h05_dress_props', 'h05_dress_plants', 'h05_ground', 'h06_dress_props', 'h06_dress_plants', 'h06_ground', 'h07_dress_props', 'h07_dress_plants', 'h07_ground', 'h08_dress_props', 'h08_dress_plants', 'h08_ground', 'h09_dress_props', 'h09_dress_plants', 'h09_ground', 'h10_dress_props', 'h10_dress_plants', 'h10_ground', 'h11_dress_props', 'h11_dress_plants', 'h11_ground', 'h12_dress_props', 'h12_dress_plants', 'h12_ground', 'h13_dress_props', 'h13_dress_plants', 'h13_ground', 'h14_dress_props'] ...
2026-10-12 11:37:13 [pass6 build] trading_post_deck: tris 3840 max mesh 840 meshparts 17 bbox [22.0, 8.55, 11.82] -> ['fbx/trading_post_deck.fbx']
2026-10-12 11:37:14 [pass6 build] h01_dress_props: tris 1928 max mesh 400 meshparts 17 bbox [17.09, 6.38, 50.01] -> ['fbx/h01_dress_props.fbx']
2026-10-12 11:37:14 [pass6 build] h01_dress_plants: tris 1744 max mesh 640 meshparts 7 bbox [11.42, 7.65, 48.52] -> ['fbx/h01_dress_plants.fbx']
2026-10-12 11:37:14 [pass6 build] h01_ground: tris 3458 max mesh 1400 meshparts 5 bbox [69.88, 1.84, 94.15] -> ['fbx/h01_ground.fbx']
2026-10-12 11:37:15 [pass6 build] h02_dress_props: tris 4708 max mesh 1740 meshparts 17 bbox [40.75, 6.12, 68.3] -> ['fbx/h02_dress_props.fbx']
2026-10-12 11:37:15 [pass6 build] h02_dress_plants: tris 5656 max mesh 1920 meshparts 7 bbox [40.41, 7.51, 70.81] -> ['fbx/h02_dress_plants.fbx']
2026-10-12 11:37:15 [pass6 build] h02_ground: tris 5884 max mesh 3520 meshparts 5 bbox [76.16, 1.6, 106.2] -> ['fbx/h02_ground.fbx']
2026-10-12 11:37:15 [pass6 build] h03_dress_props: tris 2944 max mesh 920 meshparts 13 bbox [91.14, 4.61, 44.7] -> ['fbx/h03_dress_props.fbx']
2026-10-12 11:37:15 [pass6 build] h03_dress_plants: tris 2896 max mesh 960 meshparts 7 bbox [83.2, 7.61, 27.45] -> ['fbx/h03_dress_plants.fbx']
2026-10-12 11:37:16 [pass6 build] h03_ground: tris 4048 max mesh 1920 meshparts 5 bbox [126.91, 2.05, 73.07] -> ['fbx/h03_ground.fbx']
2026-10-12 11:37:16 [pass6 build] h04_dress_props: tris 1104 max mesh 300 meshparts 13 bbox [8.21, 5.9, 7.01] -> ['fbx/h04_dress_props.fbx']
2026-10-12 11:37:16 [pass6 build] h04_ground: tris 3294 max mesh 1480 meshparts 5 bbox [88.0, 2.2, 47.52] -> ['fbx/h04_ground.fbx']
2026-10-12 11:37:16 [pass6 build] h05_dress_props: tris 4960 max mesh 1880 meshparts 13 bbox [33.19, 6.91, 69.11] -> ['fbx/h05_dress_props.fbx']
2026-10-12 11:37:16 [pass6 build] h05_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [29.95, 1.16, 45.02] -> ['fbx/h05_dress_plants.fbx']
2026-10-12 11:37:17 [pass6 build] h05_ground: tris 3524 max mesh 1880 meshparts 5 bbox [39.28, 1.79, 76.1] -> ['fbx/h05_ground.fbx']
2026-10-12 11:37:17 [pass6 build] h06_dress_props: tris 3628 max mesh 1100 meshparts 13 bbox [39.26, 6.88, 65.35] -> ['fbx/h06_dress_props.fbx']
2026-10-12 11:37:17 [pass6 build] h06_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [38.38, 1.2, 23.3] -> ['fbx/h06_dress_plants.fbx']
2026-10-12 11:37:17 [pass6 build] h06_ground: tris 4164 max mesh 2480 meshparts 5 bbox [37.26, 0.75, 84.48] -> ['fbx/h06_ground.fbx']
2026-10-12 11:37:17 [pass6 build] h07_dress_props: tris 1400 max mesh 264 meshparts 14 bbox [13.04, 6.39, 86.94] -> ['fbx/h07_dress_props.fbx']
2026-10-12 11:37:18 [pass6 build] h07_dress_plants: tris 2588 max mesh 1440 meshparts 6 bbox [13.02, 2.16, 87.34] -> ['fbx/h07_dress_plants.fbx']
2026-10-12 11:37:18 [pass6 build] h07_ground: tris 3590 max mesh 1680 meshparts 5 bbox [66.85, 1.76, 126.07] -> ['fbx/h07_ground.fbx']
2026-10-12 11:37:18 [pass6 build] h08_dress_props: tris 1772 max mesh 256 meshparts 14 bbox [23.48, 6.78, 44.21] -> ['fbx/h08_dress_props.fbx']
2026-10-12 11:37:18 [pass6 build] h08_dress_plants: tris 2236 max mesh 800 meshparts 7 bbox [27.62, 6.89, 45.55] -> ['fbx/h08_dress_plants.fbx']
2026-10-12 11:37:18 [pass6 build] h08_ground: tris 4446 max mesh 2160 meshparts 5 bbox [75.82, 0.97, 108.59] -> ['fbx/h08_ground.fbx']
2026-10-12 11:37:19 [pass6 build] h09_dress_props: tris 2172 max mesh 780 meshparts 14 bbox [64.6, 6.97, 26.52] -> ['fbx/h09_dress_props.fbx']
2026-10-12 11:37:19 [pass6 build] h09_dress_plants: tris 5620 max mesh 2400 meshparts 7 bbox [58.15, 7.95, 29.28] -> ['fbx/h09_dress_plants.fbx']
2026-10-12 11:37:19 [pass6 build] h09_ground: tris 4826 max mesh 2520 meshparts 5 bbox [102.7, 0.96, 72.79] -> ['fbx/h09_ground.fbx']
2026-10-12 11:37:19 [pass6 build] h10_dress_props: tris 2460 max mesh 420 meshparts 17 bbox [25.94, 9.35, 52.69] -> ['fbx/h10_dress_props.fbx']
2026-10-12 11:37:20 [pass6 build] h10_dress_plants: tris 456 max mesh 320 meshparts 4 bbox [2.89, 1.23, 2.87] -> ['fbx/h10_dress_plants.fbx']
2026-10-12 11:37:20 [pass6 build] h10_ground: tris 3446 max mesh 1520 meshparts 5 bbox [72.22, 4.47, 96.72] -> ['fbx/h10_ground.fbx']
2026-10-12 11:37:20 [pass6 build] h11_dress_props: tris 3780 max mesh 1420 meshparts 17 bbox [35.15, 7.71, 52.51] -> ['fbx/h11_dress_props.fbx']
2026-10-12 11:37:20 [pass6 build] h11_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [33.02, 4.42, 29.39] -> ['fbx/h11_dress_plants.fbx']
2026-10-12 11:37:20 [pass6 build] h11_ground: tris 3824 max mesh 1960 meshparts 5 bbox [79.02, 4.63, 87.08] -> ['fbx/h11_ground.fbx']
2026-10-12 11:37:21 [pass6 build] h12_dress_props: tris 5180 max mesh 2100 meshparts 17 bbox [77.58, 6.34, 39.05] -> ['fbx/h12_dress_props.fbx']
2026-10-12 11:37:21 [pass6 build] h12_dress_plants: tris 2736 max mesh 1920 meshparts 4 bbox [55.8, 1.32, 29.98] -> ['fbx/h12_dress_plants.fbx']
2026-10-12 11:37:21 [pass6 build] h12_ground: tris 5364 max mesh 2940 meshparts 5 bbox [124.2, 0.96, 83.21] -> ['fbx/h12_ground.fbx']
2026-10-12 11:37:21 [pass6 build] h13_dress_props: tris 3276 max mesh 1340 meshparts 13 bbox [50.03, 7.22, 73.86] -> ['fbx/h13_dress_props.fbx']
2026-10-12 11:37:21 [pass6 build] h13_dress_plants: tris 4812 max mesh 1440 meshparts 7 bbox [50.14, 7.76, 68.7] -> ['fbx/h13_dress_plants.fbx']
2026-10-12 11:37:22 [pass6 build] h13_ground: tris 6382 max mesh 3880 meshparts 5 bbox [85.09, 0.78, 105.15] -> ['fbx/h13_ground.fbx']
2026-10-12 11:37:22 [pass6 build] h14_dress_props: tris 596 max mesh 192 meshparts 10 bbox [5.66, 6.61, 7.62] -> ['fbx/h14_dress_props.fbx']
2026-10-12 11:37:22 [pass6 build] h14_dress_plants: tris 712 max mesh 320 meshparts 3 bbox [4.13, 2.02, 5.47] -> ['fbx/h14_dress_plants.fbx']
2026-10-12 11:37:22 [pass6 build] h14_ground: tris 3948 max mesh 1820 meshparts 5 bbox [69.55, 0.68, 88.29] -> ['fbx/h14_ground.fbx']
2026-10-12 11:37:23 [pass6 build] h15_dress_props: tris 1240 max mesh 440 meshparts 13 bbox [28.04, 5.91, 80.56] -> ['fbx/h15_dress_props.fbx']
2026-10-12 11:37:23 [pass6 build] h15_dress_plants: tris 1644 max mesh 480 meshparts 7 bbox [29.88, 6.49, 79.2] -> ['fbx/h15_dress_plants.fbx']
2026-10-12 11:37:23 [pass6 build] h15_ground: tris 3104 max mesh 760 meshparts 5 bbox [90.84, 0.99, 109.19] -> ['fbx/h15_ground.fbx']
2026-10-12 11:37:23 [pass6 build] h16_dress_props: tris 1600 max mesh 360 meshparts 14 bbox [29.08, 9.06, 36.77] -> ['fbx/h16_dress_props.fbx']
2026-10-12 11:37:23 [pass6 build] h16_dress_plants: tris 3052 max mesh 800 meshparts 7 bbox [28.8, 11.0, 38.11] -> ['fbx/h16_dress_plants.fbx']
2026-10-12 11:37:24 [pass6 build] h16_ground: tris 3040 max mesh 1180 meshparts 5 bbox [69.85, 4.26, 90.66] -> ['fbx/h16_ground.fbx']
2026-10-12 11:37:24 [pass6 build] h17_dress_props: tris 1004 max mesh 300 meshparts 10 bbox [15.54, 2.4, 49.97] -> ['fbx/h17_dress_props.fbx']
2026-10-12 11:37:24 [pass6 build] h17_dress_plants: tris 2340 max mesh 676 meshparts 7 bbox [17.09, 7.48, 47.61] -> ['fbx/h17_dress_plants.fbx']
2026-10-12 11:37:24 [pass6 build] h17_ground: tris 4402 max mesh 2160 meshparts 5 bbox [75.84, 1.08, 97.22] -> ['fbx/h17_ground.fbx']
2026-10-12 11:37:24 [pass6 build] h18_dress_props: tris 2540 max mesh 1140 meshparts 14 bbox [39.54, 6.11, 79.58] -> ['fbx/h18_dress_props.fbx']
2026-10-12 11:37:25 [pass6 build] h18_dress_plants: tris 6800 max mesh 1900 meshparts 7 bbox [39.15, 7.86, 83.98] -> ['fbx/h18_dress_plants.fbx']
2026-10-12 11:37:25 [pass6 build] h18_ground: tris 5492 max mesh 2900 meshparts 5 bbox [81.94, 1.12, 123.52] -> ['fbx/h18_ground.fbx']
2026-10-12 11:37:25 [pass6 reimport] fbx/trading_post_deck.fbx: PASS tris 3840 bbox [22.0, 8.55, 11.82]
2026-10-12 11:37:25 [pass6 reimport] fbx/h01_dress_props.fbx: PASS tris 1928 bbox [17.09, 6.38, 50.01]
2026-10-12 11:37:25 [pass6 reimport] fbx/h01_dress_plants.fbx: PASS tris 1744 bbox [11.42, 7.65, 48.52]
2026-10-12 11:37:25 [pass6 reimport] fbx/h01_ground.fbx: PASS tris 3458 bbox [69.88, 1.84, 94.15]
2026-10-12 11:37:25 [pass6 reimport] fbx/h02_dress_props.fbx: PASS tris 4708 bbox [40.75, 6.12, 68.3]
2026-10-12 11:37:26 [pass6 reimport] fbx/h02_dress_plants.fbx: PASS tris 5656 bbox [40.41, 7.51, 70.81]
2026-10-12 11:37:26 [pass6 reimport] fbx/h02_ground.fbx: PASS tris 5884 bbox [76.16, 1.6, 106.2]
2026-10-12 11:37:26 [pass6 reimport] fbx/h03_dress_props.fbx: PASS tris 2944 bbox [91.14, 4.61, 44.7]
2026-10-12 11:37:26 [pass6 reimport] fbx/h03_dress_plants.fbx: PASS tris 2896 bbox [83.2, 7.61, 27.45]
2026-10-12 11:37:26 [pass6 reimport] fbx/h03_ground.fbx: PASS tris 4048 bbox [126.91, 2.05, 73.07]
2026-10-12 11:37:26 [pass6 reimport] fbx/h04_dress_props.fbx: PASS tris 1104 bbox [8.21, 5.9, 7.01]
2026-10-12 11:37:26 [pass6 reimport] fbx/h04_ground.fbx: PASS tris 3294 bbox [88.0, 2.2, 47.52]
2026-10-12 11:37:26 [pass6 reimport] fbx/h05_dress_props.fbx: PASS tris 4960 bbox [33.19, 6.91, 69.11]
2026-10-12 11:37:26 [pass6 reimport] fbx/h05_dress_plants.fbx: PASS tris 1824 bbox [29.95, 1.16, 45.02]
2026-10-12 11:37:26 [pass6 reimport] fbx/h05_ground.fbx: PASS tris 3524 bbox [39.28, 1.79, 76.1]
2026-10-12 11:37:26 [pass6 reimport] fbx/h06_dress_props.fbx: PASS tris 3628 bbox [39.26, 6.88, 65.35]
2026-10-12 11:37:26 [pass6 reimport] fbx/h06_dress_plants.fbx: PASS tris 1824 bbox [38.38, 1.2, 23.3]
2026-10-12 11:37:26 [pass6 reimport] fbx/h06_ground.fbx: PASS tris 4164 bbox [37.26, 0.75, 84.48]
2026-10-12 11:37:26 [pass6 reimport] fbx/h07_dress_props.fbx: PASS tris 1400 bbox [13.04, 6.39, 86.94]
2026-10-12 11:37:26 [pass6 reimport] fbx/h07_dress_plants.fbx: PASS tris 2588 bbox [13.02, 2.16, 87.34]
2026-10-12 11:37:27 [pass6 reimport] fbx/h07_ground.fbx: PASS tris 3590 bbox [66.85, 1.76, 126.07]
2026-10-12 11:37:27 [pass6 reimport] fbx/h08_dress_props.fbx: PASS tris 1772 bbox [23.48, 6.78, 44.21]
2026-10-12 11:37:27 [pass6 reimport] fbx/h08_dress_plants.fbx: PASS tris 2236 bbox [27.62, 6.89, 45.55]
2026-10-12 11:37:27 [pass6 reimport] fbx/h08_ground.fbx: PASS tris 4446 bbox [75.82, 0.97, 108.59]
2026-10-12 11:37:27 [pass6 reimport] fbx/h09_dress_props.fbx: PASS tris 2172 bbox [64.6, 6.97, 26.52]
2026-10-12 11:37:27 [pass6 reimport] fbx/h09_dress_plants.fbx: PASS tris 5620 bbox [58.15, 7.95, 29.28]
2026-10-12 11:37:27 [pass6 reimport] fbx/h09_ground.fbx: PASS tris 4826 bbox [102.7, 0.96, 72.79]
2026-10-12 11:37:27 [pass6 reimport] fbx/h10_dress_props.fbx: PASS tris 2460 bbox [25.94, 9.35, 52.69]
2026-10-12 11:37:27 [pass6 reimport] fbx/h10_dress_plants.fbx: PASS tris 456 bbox [2.89, 1.23, 2.87]
2026-10-12 11:37:27 [pass6 reimport] fbx/h10_ground.fbx: PASS tris 3446 bbox [72.22, 4.47, 96.72]
2026-10-12 11:37:27 [pass6 reimport] fbx/h11_dress_props.fbx: PASS tris 3780 bbox [35.15, 7.71, 52.51]
2026-10-12 11:37:27 [pass6 reimport] fbx/h11_dress_plants.fbx: PASS tris 1824 bbox [33.02, 4.42, 29.39]
2026-10-12 11:37:27 [pass6 reimport] fbx/h11_ground.fbx: PASS tris 3824 bbox [79.02, 4.63, 87.08]
2026-10-12 11:37:27 [pass6 reimport] fbx/h12_dress_props.fbx: PASS tris 5180 bbox [77.58, 6.34, 39.05]
2026-10-12 11:37:27 [pass6 reimport] fbx/h12_dress_plants.fbx: PASS tris 2736 bbox [55.8, 1.32, 29.98]
2026-10-12 11:37:28 [pass6 reimport] fbx/h12_ground.fbx: PASS tris 5364 bbox [124.2, 0.96, 83.21]
2026-10-12 11:37:28 [pass6 reimport] fbx/h13_dress_props.fbx: PASS tris 3276 bbox [50.03, 7.22, 73.86]
2026-10-12 11:37:28 [pass6 reimport] fbx/h13_dress_plants.fbx: PASS tris 4812 bbox [50.14, 7.76, 68.7]
2026-10-12 11:37:28 [pass6 reimport] fbx/h13_ground.fbx: PASS tris 6382 bbox [85.09, 0.78, 105.15]
2026-10-12 11:37:28 [pass6 reimport] fbx/h14_dress_props.fbx: PASS tris 596 bbox [5.66, 6.61, 7.62]
2026-10-12 11:37:28 [pass6 reimport] fbx/h14_dress_plants.fbx: PASS tris 712 bbox [4.13, 2.02, 5.47]
2026-10-12 11:37:28 [pass6 reimport] fbx/h14_ground.fbx: PASS tris 3948 bbox [69.55, 0.68, 88.29]
2026-10-12 11:37:28 [pass6 reimport] fbx/h15_dress_props.fbx: PASS tris 1240 bbox [28.04, 5.91, 80.56]
2026-10-12 11:37:28 [pass6 reimport] fbx/h15_dress_plants.fbx: PASS tris 1644 bbox [29.88, 6.49, 79.2]
2026-10-12 11:37:28 [pass6 reimport] fbx/h15_ground.fbx: PASS tris 3104 bbox [90.84, 0.99, 109.19]
2026-10-12 11:37:28 [pass6 reimport] fbx/h16_dress_props.fbx: PASS tris 1600 bbox [29.08, 9.06, 36.77]
2026-10-12 11:37:28 [pass6 reimport] fbx/h16_dress_plants.fbx: PASS tris 3052 bbox [28.8, 11.0, 38.11]
2026-10-12 11:37:28 [pass6 reimport] fbx/h16_ground.fbx: PASS tris 3040 bbox [69.85, 4.26, 90.66]
2026-10-12 11:37:28 [pass6 reimport] fbx/h17_dress_props.fbx: PASS tris 1004 bbox [15.54, 2.4, 49.97]
2026-10-12 11:37:28 [pass6 reimport] fbx/h17_dress_plants.fbx: PASS tris 2340 bbox [17.09, 7.48, 47.61]
2026-10-12 11:37:28 [pass6 reimport] fbx/h17_ground.fbx: PASS tris 4402 bbox [75.84, 1.08, 97.22]
2026-10-12 11:37:29 [pass6 reimport] fbx/h18_dress_props.fbx: PASS tris 2540 bbox [39.54, 6.11, 79.58]
2026-10-12 11:37:29 [pass6 reimport] fbx/h18_dress_plants.fbx: PASS tris 6800 bbox [39.15, 7.86, 83.98]
2026-10-12 11:37:29 [pass6 reimport] fbx/h18_ground.fbx: PASS tris 5492 bbox [81.94, 1.12, 123.52]
2026-10-12 11:37:29 [pass6 build] done 54 pieces in 16s; reimport ALL PASS (_cache/reimport_pass6_dress1.json)
2026-10-12 11:37:30 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:40:27 Launch Blender 5.2: _src/sc_build_pass6.py --only cliff_w24_h48_p3,cliffT_w24_h48_p3,cliffT_w24_h24_p3,cliff_w24_h12_p3,slot_w24_h48_p4,slotT_w24_h24_p4,rim_silhouette --tag cliftest
2026-10-12 11:40:28 [pass6 build] 7 pieces: ['cliff_w24_h12_p3', 'cliffT_w24_h24_p3', 'cliff_w24_h48_p3', 'cliffT_w24_h48_p3', 'slotT_w24_h24_p4', 'slot_w24_h48_p4', 'rim_silhouette']
2026-10-12 11:40:28 [pass6 build] cliff_w24_h12_p3: tris 232 max mesh 232 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p3.fbx']
2026-10-12 11:40:29 [pass6 build] cliffT_w24_h24_p3: tris 596 max mesh 596 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p3.fbx']
2026-10-12 11:40:29 [pass6 build] cliff_w24_h48_p3: tris 856 max mesh 856 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p3.fbx']
2026-10-12 11:40:29 [pass6 build] cliffT_w24_h48_p3: tris 1012 max mesh 1012 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p3.fbx']
2026-10-12 11:40:29 [pass6 build] slotT_w24_h24_p4: tris 998 max mesh 596 meshparts 4 bbox [24.0, 24.0, 10.89] -> ['fbx/slotT_w24_h24_p4.fbx']
2026-10-12 11:40:29 [pass6 build] slot_w24_h48_p4: tris 1796 max mesh 856 meshparts 4 bbox [24.0, 48.0, 10.74] -> ['fbx/slot_w24_h48_p4.fbx']
2026-10-12 11:40:29 [pass6 build] rim_silhouette: tris 60 max mesh 60 meshparts 1 bbox [64.1, 28.0, 0.0] -> ['fbx/rim_silhouette.fbx']
2026-10-12 11:40:29 [pass6 reimport] fbx/cliff_w24_h12_p3.fbx: PASS tris 232 bbox [24.0, 12.0, 10.5]
2026-10-12 11:40:29 [pass6 reimport] fbx/cliffT_w24_h24_p3.fbx: PASS tris 596 bbox [24.0, 24.0, 10.5]
2026-10-12 11:40:29 [pass6 reimport] fbx/cliff_w24_h48_p3.fbx: PASS tris 856 bbox [24.0, 48.0, 10.5]
2026-10-12 11:40:29 [pass6 reimport] fbx/cliffT_w24_h48_p3.fbx: PASS tris 1012 bbox [24.0, 48.0, 10.5]
2026-10-12 11:40:30 [pass6 reimport] fbx/slotT_w24_h24_p4.fbx: PASS tris 998 bbox [24.0, 24.0, 10.89]
2026-10-12 11:40:30 [pass6 reimport] fbx/slot_w24_h48_p4.fbx: PASS tris 1796 bbox [24.0, 48.0, 10.74]
2026-10-12 11:40:30 [pass6 reimport] fbx/rim_silhouette.fbx: PASS tris 60 bbox [64.1, 28.0, 0.0]
2026-10-12 11:40:30 [pass6 build] done 7 pieces in 2s; reimport ALL PASS (_cache/reimport_pass6_cliftest.json)
2026-10-12 11:40:30 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:41:03 Launch Blender 5.2: _src/sc_build_pass6.py --only cliff_w24_h48_p3,cliffT_w24_h48_p3,cliffT_w24_h24_p3,cliff_w24_h12_p3,slot_w24_h48_p4,slotT_w24_h24_p4,rim_silhouette --tag cliftest
2026-10-12 11:41:04 [pass6 build] 7 pieces: ['cliff_w24_h12_p3', 'cliffT_w24_h24_p3', 'cliff_w24_h48_p3', 'cliffT_w24_h48_p3', 'slotT_w24_h24_p4', 'slot_w24_h48_p4', 'rim_silhouette']
2026-10-12 11:41:04 [pass6 build] cliff_w24_h12_p3: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p3.fbx']
2026-10-12 11:41:05 [pass6 build] cliffT_w24_h24_p3: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p3.fbx']
2026-10-12 11:41:05 [pass6 build] cliff_w24_h48_p3: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p3.fbx']
2026-10-12 11:41:05 [pass6 build] cliffT_w24_h48_p3: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p3.fbx']
2026-10-12 11:41:05 [pass6 build] slotT_w24_h24_p4: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.89] -> ['fbx/slotT_w24_h24_p4.fbx']
2026-10-12 11:41:05 [pass6 build] slot_w24_h48_p4: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.74] -> ['fbx/slot_w24_h48_p4.fbx']
2026-10-12 11:41:05 [pass6 build] rim_silhouette: tris 60 max mesh 60 meshparts 1 bbox [64.1, 28.0, 0.0] -> ['fbx/rim_silhouette.fbx']
2026-10-12 11:41:05 [pass6 reimport] fbx/cliff_w24_h12_p3.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:05 [pass6 reimport] fbx/cliffT_w24_h24_p3.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:05 [pass6 reimport] fbx/cliff_w24_h48_p3.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:05 [pass6 reimport] fbx/cliffT_w24_h48_p3.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:06 [pass6 reimport] fbx/slotT_w24_h24_p4.fbx: PASS tris 894 bbox [24.0, 24.0, 10.89]
2026-10-12 11:41:06 [pass6 reimport] fbx/slot_w24_h48_p4.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.74]
2026-10-12 11:41:06 [pass6 reimport] fbx/rim_silhouette.fbx: PASS tris 60 bbox [64.1, 28.0, 0.0]
2026-10-12 11:41:06 [pass6 build] done 7 pieces in 2s; reimport ALL PASS (_cache/reimport_pass6_cliftest.json)
2026-10-12 11:41:06 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:41:20 Launch Blender 5.2: _src/sc_build_pass6.py --group cliff_kit,far_card --tag cliffs
2026-10-12 11:41:20 [pass6 build] 73 pieces: ['cliff_w24_h6_p0', 'cliffT_w24_h6_p0', 'cliff_w24_h6_p1', 'cliffT_w24_h6_p1', 'cliff_w24_h6_p2', 'cliffT_w24_h6_p2', 'cliff_w24_h6_p3', 'cliffT_w24_h6_p3', 'cliff_w24_h6_p4', 'cliffT_w24_h6_p4', 'cliff_w24_h6_p5', 'cliffT_w24_h6_p5', 'cliff_w24_h12_p0', 'cliffT_w24_h12_p0', 'cliff_w24_h12_p1', 'cliffT_w24_h12_p1', 'cliff_w24_h12_p2', 'cliffT_w24_h12_p2', 'cliff_w24_h12_p3', 'cliffT_w24_h12_p3', 'cliff_w24_h12_p4', 'cliffT_w24_h12_p4', 'cliff_w24_h12_p5', 'cliffT_w24_h12_p5', 'cliff_w24_h24_p0', 'cliffT_w24_h24_p0', 'cliff_w24_h24_p1', 'cliffT_w24_h24_p1', 'cliff_w24_h24_p2', 'cliffT_w24_h24_p2', 'cliff_w24_h24_p3', 'cliffT_w24_h24_p3', 'cliff_w24_h24_p4', 'cliffT_w24_h24_p4', 'cliff_w24_h24_p5', 'cliffT_w24_h24_p5', 'cliff_w24_h48_p0', 'cliffT_w24_h48_p0', 'cliff_w24_h48_p1', 'cliffT_w24_h48_p1'] ...
2026-10-12 11:41:20 [pass6 build] cliff_w24_h6_p0: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliff_w24_h6_p0.fbx']
2026-10-12 11:41:20 [pass6 build] cliffT_w24_h6_p0: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliffT_w24_h6_p0.fbx']
2026-10-12 11:41:20 [pass6 build] cliff_w24_h6_p1: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliff_w24_h6_p1.fbx']
2026-10-12 11:41:20 [pass6 build] cliffT_w24_h6_p1: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 9.66] -> ['fbx/cliffT_w24_h6_p1.fbx']
2026-10-12 11:41:20 [pass6 build] cliff_w24_h6_p2: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliff_w24_h6_p2.fbx']
2026-10-12 11:41:20 [pass6 build] cliffT_w24_h6_p2: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliffT_w24_h6_p2.fbx']
2026-10-12 11:41:20 [pass6 build] cliff_w24_h6_p3: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliff_w24_h6_p3.fbx']
2026-10-12 11:41:21 [pass6 build] cliffT_w24_h6_p3: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 10.01] -> ['fbx/cliffT_w24_h6_p3.fbx']
2026-10-12 11:41:21 [pass6 build] cliff_w24_h6_p4: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.25] -> ['fbx/cliff_w24_h6_p4.fbx']
2026-10-12 11:41:21 [pass6 build] cliffT_w24_h6_p4: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 10.22] -> ['fbx/cliffT_w24_h6_p4.fbx']
2026-10-12 11:41:21 [pass6 build] cliff_w24_h6_p5: tris 104 max mesh 104 meshparts 1 bbox [24.0, 6.0, 10.5] -> ['fbx/cliff_w24_h6_p5.fbx']
2026-10-12 11:41:21 [pass6 build] cliffT_w24_h6_p5: tris 260 max mesh 260 meshparts 1 bbox [24.0, 6.0, 9.87] -> ['fbx/cliffT_w24_h6_p5.fbx']
2026-10-12 11:41:21 [pass6 build] cliff_w24_h12_p0: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p0.fbx']
2026-10-12 11:41:21 [pass6 build] cliffT_w24_h12_p0: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p0.fbx']
2026-10-12 11:41:21 [pass6 build] cliff_w24_h12_p1: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p1.fbx']
2026-10-12 11:41:21 [pass6 build] cliffT_w24_h12_p1: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p1.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h12_p2: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p2.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h12_p2: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p2.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h12_p3: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p3.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h12_p3: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p3.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h12_p4: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p4.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h12_p4: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p4.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h12_p5: tris 180 max mesh 180 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliff_w24_h12_p5.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h12_p5: tris 312 max mesh 312 meshparts 1 bbox [24.0, 12.0, 10.5] -> ['fbx/cliffT_w24_h12_p5.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h24_p0: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p0.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h24_p0: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p0.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h24_p1: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p1.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h24_p1: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p1.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h24_p2: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p2.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h24_p2: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p2.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h24_p3: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p3.fbx']
2026-10-12 11:41:22 [pass6 build] cliffT_w24_h24_p3: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p3.fbx']
2026-10-12 11:41:22 [pass6 build] cliff_w24_h24_p4: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p4.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h24_p4: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p4.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h24_p5: tris 336 max mesh 336 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliff_w24_h24_p5.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h24_p5: tris 492 max mesh 492 meshparts 1 bbox [24.0, 24.0, 10.5] -> ['fbx/cliffT_w24_h24_p5.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p0: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p0.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p0: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p0.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p1: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p1.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p1: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p1.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p2: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p2.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p2: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p2.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p3: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p3.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p3: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p3.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p4: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p4.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p4: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p4.fbx']
2026-10-12 11:41:23 [pass6 build] cliff_w24_h48_p5: tris 648 max mesh 648 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliff_w24_h48_p5.fbx']
2026-10-12 11:41:23 [pass6 build] cliffT_w24_h48_p5: tris 804 max mesh 804 meshparts 1 bbox [24.0, 48.0, 10.5] -> ['fbx/cliffT_w24_h48_p5.fbx']
2026-10-12 11:41:23 [pass6 build] slot_w24_h24_p0: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.76] -> ['fbx/slot_w24_h24_p0.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p0: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.58] -> ['fbx/slotT_w24_h24_p0.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h24_p1: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.97] -> ['fbx/slot_w24_h24_p1.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p1: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.82] -> ['fbx/slotT_w24_h24_p1.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h24_p2: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.96] -> ['fbx/slot_w24_h24_p2.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p2: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.5] -> ['fbx/slotT_w24_h24_p2.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h24_p3: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.53] -> ['fbx/slot_w24_h24_p3.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p3: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.92] -> ['fbx/slotT_w24_h24_p3.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h24_p4: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.95] -> ['fbx/slot_w24_h24_p4.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p4: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.89] -> ['fbx/slotT_w24_h24_p4.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h24_p5: tris 738 max mesh 336 meshparts 4 bbox [24.0, 24.0, 10.87] -> ['fbx/slot_w24_h24_p5.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h24_p5: tris 894 max mesh 492 meshparts 4 bbox [24.0, 24.0, 10.5] -> ['fbx/slotT_w24_h24_p5.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h48_p0: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.97] -> ['fbx/slot_w24_h48_p0.fbx']
2026-10-12 11:41:24 [pass6 build] slotT_w24_h48_p0: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.99] -> ['fbx/slotT_w24_h48_p0.fbx']
2026-10-12 11:41:24 [pass6 build] slot_w24_h48_p1: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.97] -> ['fbx/slot_w24_h48_p1.fbx']
2026-10-12 11:41:25 [pass6 build] slotT_w24_h48_p1: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.65] -> ['fbx/slotT_w24_h48_p1.fbx']
2026-10-12 11:41:25 [pass6 build] slot_w24_h48_p2: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.89] -> ['fbx/slot_w24_h48_p2.fbx']
2026-10-12 11:41:25 [pass6 build] slotT_w24_h48_p2: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.71] -> ['fbx/slotT_w24_h48_p2.fbx']
2026-10-12 11:41:25 [pass6 build] slot_w24_h48_p3: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.82] -> ['fbx/slot_w24_h48_p3.fbx']
2026-10-12 11:41:25 [pass6 build] slotT_w24_h48_p3: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.74] -> ['fbx/slotT_w24_h48_p3.fbx']
2026-10-12 11:41:25 [pass6 build] slot_w24_h48_p4: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 10.74] -> ['fbx/slot_w24_h48_p4.fbx']
2026-10-12 11:41:25 [pass6 build] slotT_w24_h48_p4: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.9] -> ['fbx/slotT_w24_h48_p4.fbx']
2026-10-12 11:41:25 [pass6 build] slot_w24_h48_p5: tris 1588 max mesh 648 meshparts 4 bbox [24.0, 48.0, 11.02] -> ['fbx/slot_w24_h48_p5.fbx']
2026-10-12 11:41:25 [pass6 build] slotT_w24_h48_p5: tris 1744 max mesh 804 meshparts 4 bbox [24.0, 48.0, 10.5] -> ['fbx/slotT_w24_h48_p5.fbx']
2026-10-12 11:41:25 [pass6 build] rim_silhouette: tris 60 max mesh 60 meshparts 1 bbox [64.1, 28.0, 0.0] -> ['fbx/rim_silhouette.fbx']
2026-10-12 11:41:25 [pass6 reimport] fbx/cliff_w24_h6_p0.fbx: PASS tris 104 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:25 [pass6 reimport] fbx/cliffT_w24_h6_p0.fbx: PASS tris 260 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h6_p1.fbx: PASS tris 104 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h6_p1.fbx: PASS tris 260 bbox [24.0, 6.0, 9.66]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h6_p2.fbx: PASS tris 104 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h6_p2.fbx: PASS tris 260 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h6_p3.fbx: PASS tris 104 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h6_p3.fbx: PASS tris 260 bbox [24.0, 6.0, 10.01]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h6_p4.fbx: PASS tris 104 bbox [24.0, 6.0, 10.25]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h6_p4.fbx: PASS tris 260 bbox [24.0, 6.0, 10.22]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h6_p5.fbx: PASS tris 104 bbox [24.0, 6.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h6_p5.fbx: PASS tris 260 bbox [24.0, 6.0, 9.87]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p0.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p0.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p1.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p1.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p2.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p2.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p3.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p3.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p4.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p4.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h12_p5.fbx: PASS tris 180 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h12_p5.fbx: PASS tris 312 bbox [24.0, 12.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h24_p0.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h24_p0.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h24_p1.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliffT_w24_h24_p1.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:26 [pass6 reimport] fbx/cliff_w24_h24_p2.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h24_p2.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h24_p3.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h24_p3.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h24_p4.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h24_p4.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h24_p5.fbx: PASS tris 336 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h24_p5.fbx: PASS tris 492 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p0.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p0.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p1.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p1.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p2.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p2.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p3.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p3.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p4.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p4.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliff_w24_h48_p5.fbx: PASS tris 648 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/cliffT_w24_h48_p5.fbx: PASS tris 804 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:27 [pass6 reimport] fbx/slot_w24_h24_p0.fbx: PASS tris 738 bbox [24.0, 24.0, 10.76]
2026-10-12 11:41:27 [pass6 reimport] fbx/slotT_w24_h24_p0.fbx: PASS tris 894 bbox [24.0, 24.0, 10.58]
2026-10-12 11:41:27 [pass6 reimport] fbx/slot_w24_h24_p1.fbx: PASS tris 738 bbox [24.0, 24.0, 10.97]
2026-10-12 11:41:27 [pass6 reimport] fbx/slotT_w24_h24_p1.fbx: PASS tris 894 bbox [24.0, 24.0, 10.82]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h24_p2.fbx: PASS tris 738 bbox [24.0, 24.0, 10.96]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h24_p2.fbx: PASS tris 894 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h24_p3.fbx: PASS tris 738 bbox [24.0, 24.0, 10.53]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h24_p3.fbx: PASS tris 894 bbox [24.0, 24.0, 10.92]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h24_p4.fbx: PASS tris 738 bbox [24.0, 24.0, 10.95]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h24_p4.fbx: PASS tris 894 bbox [24.0, 24.0, 10.89]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h24_p5.fbx: PASS tris 738 bbox [24.0, 24.0, 10.87]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h24_p5.fbx: PASS tris 894 bbox [24.0, 24.0, 10.5]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h48_p0.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.97]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h48_p0.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.99]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h48_p1.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.97]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h48_p1.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.65]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h48_p2.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.89]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h48_p2.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.71]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h48_p3.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.82]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h48_p3.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.74]
2026-10-12 11:41:28 [pass6 reimport] fbx/slot_w24_h48_p4.fbx: PASS tris 1588 bbox [24.0, 48.0, 10.74]
2026-10-12 11:41:28 [pass6 reimport] fbx/slotT_w24_h48_p4.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.9]
2026-10-12 11:41:29 [pass6 reimport] fbx/slot_w24_h48_p5.fbx: PASS tris 1588 bbox [24.0, 48.0, 11.02]
2026-10-12 11:41:29 [pass6 reimport] fbx/slotT_w24_h48_p5.fbx: PASS tris 1744 bbox [24.0, 48.0, 10.5]
2026-10-12 11:41:29 [pass6 reimport] fbx/rim_silhouette.fbx: PASS tris 60 bbox [64.1, 28.0, 0.0]
2026-10-12 11:41:29 [pass6 build] done 73 pieces in 9s; reimport ALL PASS (_cache/reimport_pass6_cliffs.json)
2026-10-12 11:41:30 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:42:48 Launch Blender 5.2: _src/sc_build_pass6.py --group hole_dressing --tag dress2
2026-10-12 11:42:49 [pass6 build] 54 pieces: ['trading_post_deck', 'h01_dress_props', 'h01_dress_plants', 'h01_ground', 'h02_dress_props', 'h02_dress_plants', 'h02_ground', 'h03_dress_props', 'h03_dress_plants', 'h03_ground', 'h04_dress_props', 'h04_ground', 'h05_dress_props', 'h05_dress_plants', 'h05_ground', 'h06_dress_props', 'h06_dress_plants', 'h06_ground', 'h07_dress_props', 'h07_dress_plants', 'h07_ground', 'h08_dress_props', 'h08_dress_plants', 'h08_ground', 'h09_dress_props', 'h09_dress_plants', 'h09_ground', 'h10_dress_props', 'h10_dress_plants', 'h10_ground', 'h11_dress_props', 'h11_dress_plants', 'h11_ground', 'h12_dress_props', 'h12_dress_plants', 'h12_ground', 'h13_dress_props', 'h13_dress_plants', 'h13_ground', 'h14_dress_props'] ...
2026-10-12 11:42:49 [pass6 build] trading_post_deck: tris 3840 max mesh 840 meshparts 17 bbox [22.0, 8.55, 11.82] -> ['fbx/trading_post_deck.fbx']
2026-10-12 11:42:50 [pass6 build] h01_dress_props: tris 1928 max mesh 400 meshparts 17 bbox [17.09, 6.38, 50.01] -> ['fbx/h01_dress_props.fbx']
2026-10-12 11:42:50 [pass6 build] h01_dress_plants: tris 1744 max mesh 640 meshparts 7 bbox [11.42, 7.65, 48.52] -> ['fbx/h01_dress_plants.fbx']
2026-10-12 11:42:50 [pass6 build] h01_ground: tris 3458 max mesh 1400 meshparts 5 bbox [69.88, 1.84, 94.15] -> ['fbx/h01_ground.fbx']
2026-10-12 11:42:50 [pass6 build] h02_dress_props: tris 4708 max mesh 1740 meshparts 17 bbox [40.75, 6.12, 68.3] -> ['fbx/h02_dress_props.fbx']
2026-10-12 11:42:51 [pass6 build] h02_dress_plants: tris 5656 max mesh 1920 meshparts 7 bbox [40.41, 7.51, 70.81] -> ['fbx/h02_dress_plants.fbx']
2026-10-12 11:42:51 [pass6 build] h02_ground: tris 5884 max mesh 3520 meshparts 5 bbox [76.16, 1.6, 106.2] -> ['fbx/h02_ground.fbx']
2026-10-12 11:42:51 [pass6 build] h03_dress_props: tris 2944 max mesh 920 meshparts 13 bbox [91.14, 4.61, 44.7] -> ['fbx/h03_dress_props.fbx']
2026-10-12 11:42:51 [pass6 build] h03_dress_plants: tris 2896 max mesh 960 meshparts 7 bbox [83.2, 7.61, 27.45] -> ['fbx/h03_dress_plants.fbx']
2026-10-12 11:42:51 [pass6 build] h03_ground: tris 4048 max mesh 1920 meshparts 5 bbox [126.91, 2.05, 73.07] -> ['fbx/h03_ground.fbx']
2026-10-12 11:42:52 [pass6 build] h04_dress_props: tris 1104 max mesh 300 meshparts 13 bbox [8.21, 5.9, 7.01] -> ['fbx/h04_dress_props.fbx']
2026-10-12 11:42:52 [pass6 build] h04_ground: tris 3294 max mesh 1480 meshparts 5 bbox [88.0, 2.2, 47.52] -> ['fbx/h04_ground.fbx']
2026-10-12 11:42:52 [pass6 build] h05_dress_props: tris 4960 max mesh 1880 meshparts 13 bbox [33.19, 6.91, 69.11] -> ['fbx/h05_dress_props.fbx']
2026-10-12 11:42:52 [pass6 build] h05_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [29.95, 1.16, 45.02] -> ['fbx/h05_dress_plants.fbx']
2026-10-12 11:42:52 [pass6 build] h05_ground: tris 3524 max mesh 1880 meshparts 5 bbox [39.28, 1.79, 76.1] -> ['fbx/h05_ground.fbx']
2026-10-12 11:42:53 [pass6 build] h06_dress_props: tris 3628 max mesh 1100 meshparts 13 bbox [39.26, 6.88, 65.35] -> ['fbx/h06_dress_props.fbx']
2026-10-12 11:42:53 [pass6 build] h06_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [38.38, 1.2, 23.3] -> ['fbx/h06_dress_plants.fbx']
2026-10-12 11:42:53 [pass6 build] h06_ground: tris 4164 max mesh 2480 meshparts 5 bbox [37.26, 0.75, 84.48] -> ['fbx/h06_ground.fbx']
2026-10-12 11:42:53 [pass6 build] h07_dress_props: tris 1400 max mesh 264 meshparts 14 bbox [13.04, 6.39, 86.94] -> ['fbx/h07_dress_props.fbx']
2026-10-12 11:42:53 [pass6 build] h07_dress_plants: tris 2588 max mesh 1440 meshparts 6 bbox [13.02, 2.16, 87.34] -> ['fbx/h07_dress_plants.fbx']
2026-10-12 11:42:54 [pass6 build] h07_ground: tris 3590 max mesh 1680 meshparts 5 bbox [66.85, 1.76, 126.07] -> ['fbx/h07_ground.fbx']
2026-10-12 11:42:54 [pass6 build] h08_dress_props: tris 1772 max mesh 256 meshparts 14 bbox [23.48, 6.78, 44.21] -> ['fbx/h08_dress_props.fbx']
2026-10-12 11:42:54 [pass6 build] h08_dress_plants: tris 2236 max mesh 800 meshparts 7 bbox [27.62, 6.89, 45.55] -> ['fbx/h08_dress_plants.fbx']
2026-10-12 11:42:54 [pass6 build] h08_ground: tris 4446 max mesh 2160 meshparts 5 bbox [75.82, 0.97, 108.59] -> ['fbx/h08_ground.fbx']
2026-10-12 11:42:54 [pass6 build] h09_dress_props: tris 2172 max mesh 780 meshparts 14 bbox [64.6, 6.97, 26.52] -> ['fbx/h09_dress_props.fbx']
2026-10-12 11:42:55 [pass6 build] h09_dress_plants: tris 5620 max mesh 2400 meshparts 7 bbox [58.15, 7.95, 29.28] -> ['fbx/h09_dress_plants.fbx']
2026-10-12 11:42:55 [pass6 build] h09_ground: tris 4826 max mesh 2520 meshparts 5 bbox [102.7, 0.96, 72.79] -> ['fbx/h09_ground.fbx']
2026-10-12 11:42:55 [pass6 build] h10_dress_props: tris 2460 max mesh 420 meshparts 17 bbox [25.94, 9.35, 52.69] -> ['fbx/h10_dress_props.fbx']
2026-10-12 11:42:55 [pass6 build] h10_dress_plants: tris 456 max mesh 320 meshparts 4 bbox [2.89, 1.23, 2.87] -> ['fbx/h10_dress_plants.fbx']
2026-10-12 11:42:56 [pass6 build] h10_ground: tris 3446 max mesh 1520 meshparts 5 bbox [72.22, 4.47, 96.72] -> ['fbx/h10_ground.fbx']
2026-10-12 11:42:56 [pass6 build] h11_dress_props: tris 3780 max mesh 1420 meshparts 17 bbox [35.15, 7.71, 52.51] -> ['fbx/h11_dress_props.fbx']
2026-10-12 11:42:56 [pass6 build] h11_dress_plants: tris 1824 max mesh 1280 meshparts 4 bbox [33.02, 4.42, 29.39] -> ['fbx/h11_dress_plants.fbx']
2026-10-12 11:42:56 [pass6 build] h11_ground: tris 3744 max mesh 1880 meshparts 5 bbox [79.02, 4.63, 87.08] -> ['fbx/h11_ground.fbx']
2026-10-12 11:42:57 [pass6 build] h12_dress_props: tris 5180 max mesh 2100 meshparts 17 bbox [77.58, 6.34, 39.05] -> ['fbx/h12_dress_props.fbx']
2026-10-12 11:42:57 [pass6 build] h12_dress_plants: tris 2736 max mesh 1920 meshparts 4 bbox [55.8, 1.32, 29.98] -> ['fbx/h12_dress_plants.fbx']
2026-10-12 11:42:57 [pass6 build] h12_ground: tris 5364 max mesh 2940 meshparts 5 bbox [124.2, 0.96, 83.21] -> ['fbx/h12_ground.fbx']
2026-10-12 11:42:57 [pass6 build] h13_dress_props: tris 3276 max mesh 1340 meshparts 13 bbox [50.03, 7.22, 73.86] -> ['fbx/h13_dress_props.fbx']
2026-10-12 11:42:58 [pass6 build] h13_dress_plants: tris 4812 max mesh 1440 meshparts 7 bbox [50.14, 7.76, 68.7] -> ['fbx/h13_dress_plants.fbx']
2026-10-12 11:42:58 [pass6 build] h13_ground: tris 6382 max mesh 3880 meshparts 5 bbox [85.09, 0.78, 105.15] -> ['fbx/h13_ground.fbx']
2026-10-12 11:42:58 [pass6 build] h14_dress_props: tris 596 max mesh 192 meshparts 10 bbox [5.66, 6.61, 7.62] -> ['fbx/h14_dress_props.fbx']
2026-10-12 11:42:58 [pass6 build] h14_dress_plants: tris 712 max mesh 320 meshparts 3 bbox [4.13, 2.02, 5.47] -> ['fbx/h14_dress_plants.fbx']
2026-10-12 11:42:58 [pass6 build] h14_ground: tris 3948 max mesh 1820 meshparts 5 bbox [69.55, 0.68, 88.29] -> ['fbx/h14_ground.fbx']
2026-10-12 11:42:59 [pass6 build] h15_dress_props: tris 1240 max mesh 440 meshparts 13 bbox [28.04, 5.91, 80.56] -> ['fbx/h15_dress_props.fbx']
2026-10-12 11:42:59 [pass6 build] h15_dress_plants: tris 1644 max mesh 480 meshparts 7 bbox [29.88, 6.49, 79.2] -> ['fbx/h15_dress_plants.fbx']
2026-10-12 11:42:59 [pass6 build] h15_ground: tris 2926 max mesh 736 meshparts 5 bbox [90.84, 0.99, 109.19] -> ['fbx/h15_ground.fbx']
2026-10-12 11:42:59 [pass6 build] h16_dress_props: tris 1600 max mesh 360 meshparts 14 bbox [29.08, 9.06, 36.77] -> ['fbx/h16_dress_props.fbx']
2026-10-12 11:42:59 [pass6 build] h16_dress_plants: tris 3052 max mesh 800 meshparts 7 bbox [28.8, 11.0, 38.11] -> ['fbx/h16_dress_plants.fbx']
2026-10-12 11:43:00 [pass6 build] h16_ground: tris 2912 max mesh 1060 meshparts 5 bbox [69.85, 4.33, 90.66] -> ['fbx/h16_ground.fbx']
2026-10-12 11:43:00 [pass6 build] h17_dress_props: tris 1004 max mesh 300 meshparts 10 bbox [15.54, 2.4, 49.97] -> ['fbx/h17_dress_props.fbx']
2026-10-12 11:43:00 [pass6 build] h17_dress_plants: tris 2340 max mesh 676 meshparts 7 bbox [17.09, 7.48, 47.61] -> ['fbx/h17_dress_plants.fbx']
2026-10-12 11:43:00 [pass6 build] h17_ground: tris 4402 max mesh 2160 meshparts 5 bbox [75.84, 1.08, 97.22] -> ['fbx/h17_ground.fbx']
2026-10-12 11:43:00 [pass6 build] h18_dress_props: tris 2540 max mesh 1140 meshparts 14 bbox [39.54, 6.11, 79.58] -> ['fbx/h18_dress_props.fbx']
2026-10-12 11:43:01 [pass6 build] h18_dress_plants: tris 6800 max mesh 1900 meshparts 7 bbox [39.15, 7.86, 83.98] -> ['fbx/h18_dress_plants.fbx']
2026-10-12 11:43:01 [pass6 build] h18_ground: tris 5492 max mesh 2900 meshparts 5 bbox [81.94, 1.12, 123.52] -> ['fbx/h18_ground.fbx']
2026-10-12 11:43:01 [pass6 reimport] fbx/trading_post_deck.fbx: PASS tris 3840 bbox [22.0, 8.55, 11.82]
2026-10-12 11:43:01 [pass6 reimport] fbx/h01_dress_props.fbx: PASS tris 1928 bbox [17.09, 6.38, 50.01]
2026-10-12 11:43:01 [pass6 reimport] fbx/h01_dress_plants.fbx: PASS tris 1744 bbox [11.42, 7.65, 48.52]
2026-10-12 11:43:01 [pass6 reimport] fbx/h01_ground.fbx: PASS tris 3458 bbox [69.88, 1.84, 94.15]
2026-10-12 11:43:02 [pass6 reimport] fbx/h02_dress_props.fbx: PASS tris 4708 bbox [40.75, 6.12, 68.3]
2026-10-12 11:43:02 [pass6 reimport] fbx/h02_dress_plants.fbx: PASS tris 5656 bbox [40.41, 7.51, 70.81]
2026-10-12 11:43:02 [pass6 reimport] fbx/h02_ground.fbx: PASS tris 5884 bbox [76.16, 1.6, 106.2]
2026-10-12 11:43:02 [pass6 reimport] fbx/h03_dress_props.fbx: PASS tris 2944 bbox [91.14, 4.61, 44.7]
2026-10-12 11:43:02 [pass6 reimport] fbx/h03_dress_plants.fbx: PASS tris 2896 bbox [83.2, 7.61, 27.45]
2026-10-12 11:43:02 [pass6 reimport] fbx/h03_ground.fbx: PASS tris 4048 bbox [126.91, 2.05, 73.07]
2026-10-12 11:43:02 [pass6 reimport] fbx/h04_dress_props.fbx: PASS tris 1104 bbox [8.21, 5.9, 7.01]
2026-10-12 11:43:02 [pass6 reimport] fbx/h04_ground.fbx: PASS tris 3294 bbox [88.0, 2.2, 47.52]
2026-10-12 11:43:02 [pass6 reimport] fbx/h05_dress_props.fbx: PASS tris 4960 bbox [33.19, 6.91, 69.11]
2026-10-12 11:43:02 [pass6 reimport] fbx/h05_dress_plants.fbx: PASS tris 1824 bbox [29.95, 1.16, 45.02]
2026-10-12 11:43:02 [pass6 reimport] fbx/h05_ground.fbx: PASS tris 3524 bbox [39.28, 1.79, 76.1]
2026-10-12 11:43:02 [pass6 reimport] fbx/h06_dress_props.fbx: PASS tris 3628 bbox [39.26, 6.88, 65.35]
2026-10-12 11:43:02 [pass6 reimport] fbx/h06_dress_plants.fbx: PASS tris 1824 bbox [38.38, 1.2, 23.3]
2026-10-12 11:43:02 [pass6 reimport] fbx/h06_ground.fbx: PASS tris 4164 bbox [37.26, 0.75, 84.48]
2026-10-12 11:43:02 [pass6 reimport] fbx/h07_dress_props.fbx: PASS tris 1400 bbox [13.04, 6.39, 86.94]
2026-10-12 11:43:03 [pass6 reimport] fbx/h07_dress_plants.fbx: PASS tris 2588 bbox [13.02, 2.16, 87.34]
2026-10-12 11:43:03 [pass6 reimport] fbx/h07_ground.fbx: PASS tris 3590 bbox [66.85, 1.76, 126.07]
2026-10-12 11:43:03 [pass6 reimport] fbx/h08_dress_props.fbx: PASS tris 1772 bbox [23.48, 6.78, 44.21]
2026-10-12 11:43:03 [pass6 reimport] fbx/h08_dress_plants.fbx: PASS tris 2236 bbox [27.62, 6.89, 45.55]
2026-10-12 11:43:03 [pass6 reimport] fbx/h08_ground.fbx: PASS tris 4446 bbox [75.82, 0.97, 108.59]
2026-10-12 11:43:03 [pass6 reimport] fbx/h09_dress_props.fbx: PASS tris 2172 bbox [64.6, 6.97, 26.52]
2026-10-12 11:43:03 [pass6 reimport] fbx/h09_dress_plants.fbx: PASS tris 5620 bbox [58.15, 7.95, 29.28]
2026-10-12 11:43:03 [pass6 reimport] fbx/h09_ground.fbx: PASS tris 4826 bbox [102.7, 0.96, 72.79]
2026-10-12 11:43:03 [pass6 reimport] fbx/h10_dress_props.fbx: PASS tris 2460 bbox [25.94, 9.35, 52.69]
2026-10-12 11:43:03 [pass6 reimport] fbx/h10_dress_plants.fbx: PASS tris 456 bbox [2.89, 1.23, 2.87]
2026-10-12 11:43:03 [pass6 reimport] fbx/h10_ground.fbx: PASS tris 3446 bbox [72.22, 4.47, 96.72]
2026-10-12 11:43:03 [pass6 reimport] fbx/h11_dress_props.fbx: PASS tris 3780 bbox [35.15, 7.71, 52.51]
2026-10-12 11:43:03 [pass6 reimport] fbx/h11_dress_plants.fbx: PASS tris 1824 bbox [33.02, 4.42, 29.39]
2026-10-12 11:43:03 [pass6 reimport] fbx/h11_ground.fbx: PASS tris 3744 bbox [79.02, 4.63, 87.08]
2026-10-12 11:43:03 [pass6 reimport] fbx/h12_dress_props.fbx: PASS tris 5180 bbox [77.58, 6.34, 39.05]
2026-10-12 11:43:04 [pass6 reimport] fbx/h12_dress_plants.fbx: PASS tris 2736 bbox [55.8, 1.32, 29.98]
2026-10-12 11:43:04 [pass6 reimport] fbx/h12_ground.fbx: PASS tris 5364 bbox [124.2, 0.96, 83.21]
2026-10-12 11:43:04 [pass6 reimport] fbx/h13_dress_props.fbx: PASS tris 3276 bbox [50.03, 7.22, 73.86]
2026-10-12 11:43:04 [pass6 reimport] fbx/h13_dress_plants.fbx: PASS tris 4812 bbox [50.14, 7.76, 68.7]
2026-10-12 11:43:04 [pass6 reimport] fbx/h13_ground.fbx: PASS tris 6382 bbox [85.09, 0.78, 105.15]
2026-10-12 11:43:04 [pass6 reimport] fbx/h14_dress_props.fbx: PASS tris 596 bbox [5.66, 6.61, 7.62]
2026-10-12 11:43:04 [pass6 reimport] fbx/h14_dress_plants.fbx: PASS tris 712 bbox [4.13, 2.02, 5.47]
2026-10-12 11:43:04 [pass6 reimport] fbx/h14_ground.fbx: PASS tris 3948 bbox [69.55, 0.68, 88.29]
2026-10-12 11:43:04 [pass6 reimport] fbx/h15_dress_props.fbx: PASS tris 1240 bbox [28.04, 5.91, 80.56]
2026-10-12 11:43:04 [pass6 reimport] fbx/h15_dress_plants.fbx: PASS tris 1644 bbox [29.88, 6.49, 79.2]
2026-10-12 11:43:04 [pass6 reimport] fbx/h15_ground.fbx: PASS tris 2926 bbox [90.84, 0.99, 109.19]
2026-10-12 11:43:04 [pass6 reimport] fbx/h16_dress_props.fbx: PASS tris 1600 bbox [29.08, 9.06, 36.77]
2026-10-12 11:43:04 [pass6 reimport] fbx/h16_dress_plants.fbx: PASS tris 3052 bbox [28.8, 11.0, 38.11]
2026-10-12 11:43:04 [pass6 reimport] fbx/h16_ground.fbx: PASS tris 2912 bbox [69.85, 4.33, 90.66]
2026-10-12 11:43:04 [pass6 reimport] fbx/h17_dress_props.fbx: PASS tris 1004 bbox [15.54, 2.4, 49.97]
2026-10-12 11:43:04 [pass6 reimport] fbx/h17_dress_plants.fbx: PASS tris 2340 bbox [17.09, 7.48, 47.61]
2026-10-12 11:43:05 [pass6 reimport] fbx/h17_ground.fbx: PASS tris 4402 bbox [75.84, 1.08, 97.22]
2026-10-12 11:43:05 [pass6 reimport] fbx/h18_dress_props.fbx: PASS tris 2540 bbox [39.54, 6.11, 79.58]
2026-10-12 11:43:05 [pass6 reimport] fbx/h18_dress_plants.fbx: PASS tris 6800 bbox [39.15, 7.86, 83.98]
2026-10-12 11:43:05 [pass6 reimport] fbx/h18_ground.fbx: PASS tris 5492 bbox [81.94, 1.12, 123.52]
2026-10-12 11:43:05 [pass6 build] done 54 pieces in 16s; reimport ALL PASS (_cache/reimport_pass6_dress2.json)
2026-10-12 11:43:06 Blender exited: _src/sc_build_pass6.py (exit 0)
2026-10-12 11:43:43 PASS6 steps 2-4 built: 54 per-hole dressing pieces (h01..h18 *_dress_props/_dress_plants/_ground; 68 clusters at all tees + turns; carpet/pebbles/bricks) + trading_post_deck at H1 (47.5,17.36,469) yaw -90; cliff kit reworked into tower panels (72 FBX incl. 36 new cliffT_/slotT_ stack-top variants, 309 stack tops swapped) + rim_silhouette; sc_dress_pass6 lane rule extended to ground triangles. finalize_pass6 + sc_fitcheck_holes: ALL PASS (dressing ZERO intrusions; p_h18_hub seg 3 10.04). Placed tris 305,982 -> 588,476; max near-field (<=60) 29,086 (H5).
2026-10-12 11:44:16 Pass6 art: reimport_pass6.txt ALL PASS (144 FBX); contact_sheet.png (1600, 8060) with 148 thumbnails
2026-10-12 11:46:07 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:46:07 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:46:09 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:46:09 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:46:09 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:46:09 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:46:09 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:46:09 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:46:09 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:46:10 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:46:10 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:46:10 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:46:12 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:12 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:12 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:12 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:12 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:12 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:14 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:46:14 Pass6 relight: key sun 277/4 {'energy': 7.5, 'color': (1, 0.47, 0.14)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 4.0, 'color': (1, 0.36, 0.08)}; sky #FFD27A>#FFC27E>#FFAE88>#F59A8E>#C77BA0
2026-10-12 11:46:14 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4
2026-10-12 11:46:14 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4 rim=300/4
2026-10-12 11:46:15 Render complete V1-hub-tee1: 1.5s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:46:15 Pass6 hero run finished in 8.0s (preview)
2026-10-12 11:46:16 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:46:33 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:46:34 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:46:36 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:46:36 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:46:36 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:46:36 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:46:36 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:46:36 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:46:36 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:46:36 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:46:36 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:46:36 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:46:39 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:39 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:39 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:39 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:39 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:39 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:46:40 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:46:40 Pass6 relight: key sun 277/4 {'energy': 11.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 7.0, 'color': (1, 0.33, 0.06)}; fill {'bounce': 330000, 'ambient': 0.42}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:46:40 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4
2026-10-12 11:46:40 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4 rim=300/4
2026-10-12 11:46:42 Render complete V1-hub-tee1: 1.5s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:46:42 Pass6 hero run finished in 8.0s (preview)
2026-10-12 11:46:42 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:47:04 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:47:04 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:47:06 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:47:06 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:47:06 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:47:06 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:47:07 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:47:07 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:47:07 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:47:07 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:47:07 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:47:07 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:47:09 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:09 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:09 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:09 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:09 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:09 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:11 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:47:11 Pass6 relight: key sun 277/4 {'energy': 11.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 7.0, 'color': (1, 0.33, 0.06)}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.0, 'look': 'AgX - Punchy', 'sky_strength': 0.5}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:47:11 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4
2026-10-12 11:47:11 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4 rim=300/4
2026-10-12 11:47:13 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:47:13 Pass6 hero run finished in 8.2s (preview)
2026-10-12 11:47:13 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:47:21 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:47:22 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:47:24 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:47:24 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:47:24 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:47:24 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:47:24 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:47:24 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:47:24 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:47:24 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:47:24 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:47:24 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:47:27 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:27 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:27 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:27 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:27 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:27 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:28 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:47:28 Pass6 relight: key sun 277/4 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 12.0, 'color': (1, 0.33, 0.06)}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 0.85}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:47:28 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4
2026-10-12 11:47:28 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4 rim=300/4
2026-10-12 11:47:30 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:47:30 Pass6 hero run finished in 7.8s (preview)
2026-10-12 11:47:30 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:47:47 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:47:48 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:47:50 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:47:50 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:47:50 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:47:50 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:47:50 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:47:50 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:47:50 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:47:50 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:47:50 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:47:50 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:47:53 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:53 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:53 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:53 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:53 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:53 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:47:54 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:47:54 Pass6 relight: key sun 277/4 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 12.0, 'color': (1, 0.33, 0.06)}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 0.85}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:47:54 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4
2026-10-12 11:47:54 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4 rim=300/4
2026-10-12 11:47:56 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:47:56 Pass6 hero run finished in 7.9s (preview)
2026-10-12 11:47:56 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:48:07 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:48:08 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:48:10 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:48:10 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:48:10 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:48:10 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:48:10 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:48:10 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:48:10 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:48:10 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:48:10 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:48:10 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:48:13 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:13 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:13 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:13 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:13 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:13 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:14 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:48:14 Pass6 relight: key sun 277/25.0 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 300, 'elev': 4, 'energy': 12.0, 'color': (1, 0.33, 0.06)}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 0.85}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:48:14 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/25.0
2026-10-12 11:48:14 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/25.0 rim=300/4
2026-10-12 11:48:16 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:48:16 Pass6 hero run finished in 7.7s (preview)
2026-10-12 11:48:16 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:48:39 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:48:39 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:48:41 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:48:41 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:48:41 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:48:41 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:48:42 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:48:42 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:48:42 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:48:42 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:48:42 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:48:42 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:48:44 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:44 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:44 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:44 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:44 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:44 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:48:45 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:48:45 Pass6 relight: key sun 277/4.0 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 285, 'elev': 3, 'energy': 4.0, 'color': (1, 0.36, 0.07), 'shadow': False}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 0.85}; sky #FFC23E>#FFB04E>#FF9A66>#F2847E>#B8649A
2026-10-12 11:48:45 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4.0
2026-10-12 11:48:45 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4.0 rim=285/3
2026-10-12 11:48:47 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:48:47 Pass6 hero run finished in 7.7s (preview)
2026-10-12 11:48:48 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:48:57 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:48:57 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:48:59 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:48:59 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:48:59 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:49:00 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:49:00 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:49:00 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:49:00 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:49:00 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:49:00 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:49:00 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:49:02 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:02 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:02 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:02 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:02 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:02 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:03 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:49:03 Pass6 relight: key sun 277/4.0 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 285, 'elev': 3, 'energy': 4.0, 'color': (1, 0.36, 0.07), 'shadow': False}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 1.15}; sky #FFC84A>#FFB25E>#FF9E78>#F48A8E>#A96BA9
2026-10-12 11:49:03 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4.0
2026-10-12 11:49:03 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4.0 rim=285/3
2026-10-12 11:49:05 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:49:05 Pass6 hero run finished in 7.7s (preview)
2026-10-12 11:49:06 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:49:15 Launch Blender 5.2: _src/render_hero_pass6.py --preview
2026-10-12 11:49:16 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:49:18 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:49:18 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:49:18 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:49:18 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:49:18 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:49:18 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:49:18 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:49:18 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:49:18 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:49:18 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:49:21 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:21 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:21 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:21 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:21 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:21 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:22 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:49:22 Pass6 relight: key sun 277/4.0 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 285, 'elev': 3, 'energy': 4.0, 'color': (1, 0.36, 0.07), 'shadow': False}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 1.15}; sky #FFC84A>#FFBC52>#FFA272>#F48A8E>#A96BA9
2026-10-12 11:49:22 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 16 samples; denoise; pass6 key 277/4.0
2026-10-12 11:49:22 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4.0 rim=285/3
2026-10-12 11:49:23 Render complete V1-hub-tee1: 1.6s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6_draft.png
2026-10-12 11:49:23 Pass6 hero run finished in 7.8s (preview)
2026-10-12 11:49:24 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:49:29 Launch Blender 5.2: _src/render_hero_pass6.py 
2026-10-12 11:49:29 Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs
2026-10-12 11:49:31 Card material rim_silhouette__Strata: ['Strata']; UV range [(-0.8916666507720947, 0.8888888955116272, -0.015636568889021873, 0.8010421991348267)]
2026-10-12 11:49:31 Cutout CardMesa: alpha 0.0..1.0
2026-10-12 11:49:31 Card material distant_mesa_card__CardMesa: ['CardMesa']; UV range [(0.0, 1.0, 0.0, 0.9375)]
2026-10-12 11:49:31 Cutout CardButte: alpha 0.0..1.0
2026-10-12 11:49:31 Card material butte_spire_card__CardButte: ['CardButte']; UV range [(0.046875, 0.953125, 0.0, 0.984375)]
2026-10-12 11:49:31 Cutout CardArch: alpha 0.0..1.0
2026-10-12 11:49:31 Card material far_arch_card__CardArch: ['CardArch']; UV range [(0.015625, 0.984375, 0.0, 0.96875)]
2026-10-12 11:49:31 Cutout CardTwins: alpha 0.0..1.0
2026-10-12 11:49:31 Card material far_butte_card__CardTwins: ['CardTwins']; UV range [(0.015625, 0.984375, 0.0, 0.984375)]
2026-10-12 11:49:31 Cutout CardCloud: alpha 0.0..1.0
2026-10-12 11:49:34 Alpha restored CardButte: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:34 Alpha restored CardCloud: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:34 Alpha restored SunGold: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:34 Alpha restored CardTwins: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:34 Alpha restored CardArch: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:34 Alpha restored CardMesa: STRAIGHT; explicit UVMap and transparent mix
2026-10-12 11:49:35 Pass6 staging (render-only, holes.json): 126 felt slabs, 308 rounded clay-brick curbs (bumpers skipped), 18 cups+flags, H1 ball
2026-10-12 11:49:35 Pass6 relight: key sun 277/4.0 {'energy': 24.0, 'color': (1, 0.44, 0.12)}; rim sun {'bearing': 285, 'elev': 3, 'energy': 4.0, 'color': (1, 0.36, 0.07), 'shadow': False}; fill {'bounce': 330000, 'ambient': 0.42}; grade {'exposure': 1.15, 'look': 'AgX - Punchy', 'sky_strength': 1.15}; sky #FFC84A>#FFBC52>#FFA272>#F48A8E>#A96BA9
2026-10-12 11:49:35 Cycles OptiX devices: NVIDIA GeForce RTX 4090; 128 samples; denoise; pass6 key 277/4.0
2026-10-12 11:49:35 Render start V1-hub-tee1 eye=[60.0, 25.5, 482.0] target=[80.0, -49.6, -130.0] fov=78 key=277/4.0 rim=285/3
2026-10-12 11:49:41 Render complete V1-hub-tee1: 5.9s -> C:\Users\chase\sc\sugarloaf-canyon\models\previews\hero\V1-hub-tee1_pass6.png
2026-10-12 11:49:41 Pass6 hero run finished in 12.0s
2026-10-12 11:49:42 Blender exited: _src/render_hero_pass6.py (exit 0)
2026-10-12 11:49:48 Pass6: previews/hero/V1-hub-tee1_pass6_vs_concept.png written
2026-10-12 11:50:35 Pass6 art: reimport_pass6.txt ALL PASS (144 FBX); contact_sheet.png (1600, 8060) with 148 thumbnails
2026-10-12 11:52:17 PASS6 complete: render V1-hub-tee1_pass6.png (+ _vs_concept), README Pass 6 section, pass6_summary.md, manifest/layout/pieces_table final; fitcheck_pass6 ALL PASS (validated copy written); reimport_pass6 ALL PASS (144 FBX). pass6_done.flag created.
