2026-10-11 19:29:41 Prep on box: brief_pass1.md, atlas_layout.md, _lg_ref copied. Waiting for PC queue (movers, H9 dim, Sugarloaf look) to finish.
2026-10-11 19:44:43 Builder name map added to brief (29 builder names). PC still busy (codex movers job); Blender not started.
2026-10-11 20:42:54 pass1 launch (Claude Code claude-opus-5-5 on PC)
2026-10-11 20:46:35 Launch Blender 5.2: C:/Users/chase/bw/tmp_probe/probe.py 
2026-10-11 20:46:36 Blender exited: C:/Users/chase/bw/tmp_probe/probe.py (exit 0)
 NOTICE: Sugarloaf movers pass 4 has priority. Do NOT start Blender except via _src\run_blender.ps1 (it now blocks until movers pass 4 is done). Continue writing scripts/atlas (Pillow) meanwhile; if a Blender wait times out your shell, just retry later.
2026-10-11 20:48 NOTICE: Sugarloaf movers pass 4 has priority. Do NOT start Blender except via _src\run_blender.ps1 (it now blocks until movers pass 4 is done). Keep doing non-Blender work (scripts, Pillow atlas) meanwhile; if a wait times out your shell, retry later.
2026-10-11 20:50:22 STEP 1: bwlib.py (adapted from _lg_ref/lglib.py), atlas_def.py, make_atlas.py -> textures/bw_atlas_1024.png (1024x1024 RGB 8-bit, no metadata; deck rows jittered per plank, a/b at U 0/0.5). parse_builder.py reads builder_Lobby.luau (242 instances, 29 assets).
2026-10-11 20:50:22 STEP 1 DONE
2026-10-11 20:56:30 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 20:58:30 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 21:00:30 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 21:02:30 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 21:04:30 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 21:06:31 PAUSED: waiting for Sugarloaf movers pass 4 (DONE4 / movers_pass4_summary.md); next check in 120 s. Keep doing non-Blender work.
2026-10-11 21:06:49 pass1: Blender gated (movers pass 4); writing props_*.py / fitcheck / render scripts meanwhile.
2026-10-11 21:18:27 pass1: movers pass 4 done (sc_movers4/out/DONE4.txt); starting Blender builds.
2026-10-11 21:18:28 Launch Blender 5.2: build_all.py --group,structure
2026-10-11 21:18:28 build_all ['--group,structure']: built 0 props: 
2026-10-11 21:18:29 Blender exited: build_all.py (exit 0)
2026-10-11 21:18:39 Launch Blender 5.2: build_all.py --group=structure
2026-10-11 21:18:39 build_all ['--group', 'structure']: built 4 props: bw_deck_plank_a=10, bw_deck_plank_b=10, bw_railing=222, bw_pier_piling=232
2026-10-11 21:18:40 Blender exited: build_all.py (exit 0)
2026-10-11 21:18:46 STEP 2a DONE (structure: deck_plank_a/b 10 tris, railing 222, pier_piling 232)
2026-10-11 21:18:46 Launch Blender 5.2: build_all.py --group=board
2026-10-11 21:18:47 build_all ['--group', 'board']: built 5 props: bw_course_board=1606, bw_leaderboard_wall=1736, bw_signpost=390, bw_arch_nameplate=176, bw_coming_soon_sign=184
2026-10-11 21:18:47 Blender exited: build_all.py (exit 0)
2026-10-11 21:19:01 Launch Blender 5.2: build_all.py --group=board,arches
2026-10-11 21:19:02 build_all ['--group', 'board,arches']: built 8 props: bw_course_board=1606, bw_leaderboard_wall=1736, bw_signpost=390, bw_arch_nameplate=176, bw_coming_soon_sign=184, bw_arch_lantern_grove=9456, bw_arch_sugarloaf_canyon=2630, bw_arch_aurora_archipelago=1678
2026-10-11 21:19:03 Blender exited: build_all.py (exit 0)
2026-10-11 21:19:10 STEP 2b DONE (board/UI: course_board 1606, leaderboard 1736, signpost 390, nameplate 176, coming_soon 184)
2026-10-11 21:19:10 STEP 2c DONE (arches: lantern_grove 9456, sugarloaf 2630, aurora 1678; openings >= 10.08 x 12.25)
2026-10-11 21:19:10 Launch Blender 5.2: build_all.py --group=green,social,backdrop
2026-10-11 21:19:12 Blender exited: build_all.py (exit 1)
2026-10-11 21:19:49 Launch Blender 5.2: build_all.py --group=green,social,backdrop
2026-10-11 21:19:51 build_all ['--group', 'green,social,backdrop']: built 17 props: bw_practice_green=576, bw_windmill=622, bw_windmill_blades=404, bw_cup_flag=140, bw_tee_mat=12, bw_birdie_bites_shack=3754, bw_bench=300, bw_picnic_table=588, bw_barrel=212, bw_crate=44, bw_flower_planter=756, bw_beach_umbrella=334, bw_lantern_post=224, bw_string_lights=368, bw_rock_arch=1228, bw_sea_stacks=1088, bw_lantern_tree_canopy=5600
2026-10-11 21:19:52 Blender exited: build_all.py (exit 0)
2026-10-11 21:20:02 Launch Blender 5.2: build_all.py --only=bw_string_lights
2026-10-11 21:20:03 build_all ['--only', 'bw_string_lights']: built 1 props: bw_string_lights=248
2026-10-11 21:20:03 Blender exited: build_all.py (exit 0)
2026-10-11 21:20:03 STEP 2d DONE (green: practice_green 576 w/ 2 boolean cups, windmill 622, blades 404 pivot=hub, cup_flag 140, tee_mat 12)
2026-10-11 21:20:03 STEP 2e DONE (social: shack 3754, bench 300, picnic 588, barrel 212, crate 44, planter 756, umbrella 334, lantern_post 224, string_lights)
2026-10-11 21:20:03 STEP 2f DONE (backdrop: rock_arch 1228, sea_stacks 1088, lantern_tree_canopy 5600)
2026-10-11 21:20:14 Launch Blender 5.2: build_all.py --only=bw_string_lights
2026-10-11 21:20:15 build_all ['--only', 'bw_string_lights']: built 1 props: bw_string_lights=248
2026-10-11 21:20:15 Blender exited: build_all.py (exit 0)
2026-10-11 21:20:16 Launch Blender 5.2: render_props.py 
2026-10-11 21:20:39 render_props: 29 props rendered to previews/props/_views
2026-10-11 21:20:40 Blender exited: render_props.py (exit 0)
2026-10-11 21:22:08 Launch Blender 5.2: build_all.py --only=bw_arch_sugarloaf_canyon,bw_rock_arch
2026-10-11 21:22:09 build_all ['--only', 'bw_arch_sugarloaf_canyon,bw_rock_arch']: built 2 props: bw_arch_sugarloaf_canyon=1356, bw_rock_arch=1228
2026-10-11 21:22:09 Blender exited: build_all.py (exit 0)
2026-10-11 21:22:09 Launch Blender 5.2: render_props.py --only=bw_arch_sugarloaf_canyon,bw_rock_arch
2026-10-11 21:22:12 render_props: 2 props rendered to previews/props/_views
2026-10-11 21:22:12 Blender exited: render_props.py (exit 0)
2026-10-11 21:22:39 Launch Blender 5.2: build_all.py --only=bw_arch_sugarloaf_canyon,bw_rock_arch
2026-10-11 21:22:40 build_all ['--only', 'bw_arch_sugarloaf_canyon,bw_rock_arch']: built 2 props: bw_arch_sugarloaf_canyon=1356, bw_rock_arch=1164
2026-10-11 21:22:40 Blender exited: build_all.py (exit 0)
2026-10-11 21:22:41 Launch Blender 5.2: render_props.py --only=bw_arch_sugarloaf_canyon
2026-10-11 21:22:42 render_props: 1 props rendered to previews/props/_views
2026-10-11 21:22:43 Blender exited: render_props.py (exit 0)
2026-10-11 21:22:56 STEP 2 review: sugarloaf rebuilt to concept (tapered faceted towers, wide bands, crenellated lintel; 1356 tris); rock_arch bands + flared feet (1164). manifest.json assembled: 29 props, 242 instances, 48656 tris.
2026-10-11 21:22:56 Launch Blender 5.2: fitcheck.py 
2026-10-11 21:22:58 fitcheck: ALL PASS; total tris 48656
2026-10-11 21:22:58 Blender exited: fitcheck.py (exit 0)
2026-10-11 21:23:26 STEP 3 DONE fitcheck ALL PASS (fitcheck_pass1_validated.txt): total 48656 tris; card faces, openings, pivots, spawn radius, green lines OK
2026-10-11 21:23:26 Launch Blender 5.2: render_lobby.py 
2026-10-11 21:23:31 render_lobby: previews/spawn_view.png
2026-10-11 21:23:32 render_lobby: previews/topdown.png
2026-10-11 21:23:33 Blender exited: render_lobby.py (exit 0)
2026-10-11 21:24:08 Launch Blender 5.2: render_lobby.py --only=spawn
2026-10-11 21:24:12 render_lobby: previews/spawn_view.png (fog composited from depth, lobby.json start 180 end 420)
2026-10-11 21:24:13 Blender exited: render_lobby.py (exit 0)
2026-10-11 21:24:34 Launch Blender 5.2: build_all.py --only=bw_course_board,bw_leaderboard_wall,bw_birdie_bites_shack
2026-10-11 21:24:34 build_all ['--only', 'bw_course_board,bw_leaderboard_wall,bw_birdie_bites_shack']: built 3 props: bw_course_board=1606, bw_leaderboard_wall=1736, bw_birdie_bites_shack=3754
2026-10-11 21:24:35 Blender exited: build_all.py (exit 0)
2026-10-11 21:24:35 Launch Blender 5.2: render_lobby.py 
2026-10-11 21:24:39 render_lobby: previews/spawn_view.png (fog composited from depth, lobby.json start 180 end 420)
2026-10-11 21:24:41 render_lobby: previews/overview.png (extra: elevated view from behind spawn)
2026-10-11 21:24:42 render_lobby: previews/topdown.png
2026-10-11 21:24:42 Blender exited: render_lobby.py (exit 0)
2026-10-11 21:25:37 Launch Blender 5.2: build_all.py --group=structure
2026-10-11 21:25:38 build_all ['--group', 'structure']: built 4 props: bw_deck_plank_a=10, bw_deck_plank_b=10, bw_railing=222, bw_pier_piling=232
2026-10-11 21:25:38 Blender exited: build_all.py (exit 0)
2026-10-11 21:25:45 Launch Blender 5.2: render_lobby.py 
2026-10-11 21:25:49 render_lobby: previews/spawn_view.png (fog composited from depth, lobby.json start 180 end 420)
2026-10-11 21:25:50 render_lobby: previews/overview.png (extra: elevated view from behind spawn)
2026-10-11 21:25:52 render_lobby: previews/topdown.png
2026-10-11 21:25:52 Blender exited: render_lobby.py (exit 0)
2026-10-11 21:25:52 Launch Blender 5.2: fitcheck.py 
2026-10-11 21:25:54 fitcheck: ALL PASS; total tris 48656
2026-10-11 21:25:54 Blender exited: fitcheck.py (exit 0)
2026-10-11 21:25:55 Launch Blender 5.2: render_props.py 
2026-10-11 21:26:18 render_props: 29 props rendered to previews/props/_views
2026-10-11 21:26:19 Blender exited: render_props.py (exit 0)
2026-10-11 21:26:42 STEP 4 DONE renders (Cycles OptiX): previews/props/<name>.png x29 (3/4 + eye-5 with 2x5 capsule), previews/contact_sheet.png, previews/spawn_view.png (fog from depth pass, lobby.json 180-420), previews/topdown.png, extra previews/overview.png. Deck/rail instance scale per builder size (8-stud pier row/ends) applied.
2026-10-11 21:27:57 STEP 5: README.md (files, axes, pivots, tris table, instance plan, import notes, 10 spec questions), _src/pass1_summary.md written. Atlas embedded in atlas FBXs (verified PNG bytes); backdrop FBXs vertex colour only.
2026-10-11 21:27:57 STEP 5 DONE
2026-10-11 21:30:31 pass1 copied back from PC
