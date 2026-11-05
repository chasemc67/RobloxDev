# Pass 4 progress (world re-placement of dressing + art-director fixes)

- [x] Step 0 (2026-10-10): read pass2/3 summaries, dressing*, world_fit*, assembly, world README.
  Froze the pass-2 hole-local dressing as `_src/dressing_seed_pass2.json` (1,502 instances, the "before" state)
  and a copy of the manifest as `_src/manifest_before_pass4.json`.
- [x] Step 1: textures.py: felt (softer, darker, faint nap) + new felt_normal.png, paper_glow.png (sky lantern),
  card_red.png / card_gold.png (alpha-cut treeline cards). lglib: CARD_MATS (alpha + per-face card UVs), EMIT_TEX.
- [x] Step 2: props_cards.py: treeline_card_red / treeline_card_gold (3 crossed double-sided quads, 12 tris), FBX built.
- [x] Step 3 (art C/D/E): world_pieces.py: mountains -> MountainFoot/Peach/Mauve/Snow (foot = horizon haze colour);
  sky_lantern 1.1x1.35x1.1 round, SkyPaper (paper_glow.png, self-lit); new hollow_tree_world_shell_part8 (18 low wall
  lantern clusters + 24 glowing mushroom clumps, 30 PointLight spots -> world manifest lights_world and
  manifest.world.h9_interior_lights). world_build --only rebuilt; world_fitcheck ALL PASS (51 FBX).
- [x] Step 4a: world_occ.py (world FBX -> per-part height-interval occupancy, cached) + dressing_world.py (seed ->
  world, clash/ground tests, nudges, near-field budget 34k within 60 studs, backdrop -> cards, refill, FBX groups in
  hole frame + cards file, manifest world/local transforms + stats). Runs in ~20 s.
- [x] Step 5a: world_scene.py (shared world preview scene; world_vista.py now uses it) + assembly_world.py (tee/top
  per hole over the real world). lglib Felt: sheen + felt_normal nap in previews.
- [x] Render iteration 1 (16 spp): clean placement; H1/H2/H5 rail-side cover thin, heavy toadstools eat ground budget.
- [x] Fitcheck rewritten for world dressing (exact SAT on re-imported groups, occupancy, tree rule, grounding, budget, 8 negative tests): ALL PASS.
- [x] Iteration 2 tweaks: heavy small props max 2/hole, cheap ground refill (min 20), hooks min 2, budgets lantern 5.2k / tree 7.4k / ground 6k.
- [x] Render iteration 2 (24 spp): H2-H4/H6 good; H1/H5/H7 rail-side still bare -> ground share 8k, near cap 34, refill 30 aimed at the first 30 studs of the tee view. Fitcheck ALL PASS.
- [x] README/build.sh/tee_sheet/readme_extra updated for pass 4; world_build notes updated (mountains, sky lantern).
- [x] Iteration 3 render (32 spp) + vistas: vista showed a converted card ~15 studs from the H1 tee -> cards must be
  >= 26 from any felt (+ fitcheck). Final stats check showed ground-first starved trees in H6-H8 (0-1 own trees) ->
  `tree1` pass: first 4 trees per hole before ground cover, ground share 6.5k. Fitcheck ALL PASS (118 checks).
- [x] Repo skill blender-asset-pipeline: 2 lessons added. _src/pass4_summary.md drafted.
- [x] Iteration 4: H1 vista blocked by a card wall -> protected vista sightlines (no cards) + card min 32 from any felt;
  fitcheck ALL PASS (120 checks, 9 new negative tests).
- [x] Final re-render (32 spp): previews/assembly_hNN_{tee,top}.png, world vistas, tee_contact_sheet.png,
  world/contact_sheet_world.png, README regenerated. _src/pass4_summary.md final. DONE.
