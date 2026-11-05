# SRV-131 pass 1 summary: Sugarloaf Canyon world pieces
Built on the box (headless Blender 4.x, Workbench previews). Claude Code opus-5.5 did steps 0-4 and then hit its session limit at about 17:55 PT. Codex auth had expired (401), so steps 5-6 (holes.json clearance, contact sheet, docs) were finished by hand.
99 pieces / 104 FBX / 738 placed instances / about 308k placed tris in the world. Max single mesh is 4,324 tris (<20k). Far cards and sky total 1,638 tris, with CastShadow off.
Fitcheck: ALL PASS (footprints min 2.10, walkway overhead min 9.25). Also checked against the final holes.json, see fitcheck_pass1_validated.txt.
No per-hole props or moving parts.

## Assumptions
See layout.json "assumptions" (dam dims, arch orientation, building yaws, mine-head, lift frames, cliff auto-placement, invented scatter, clusters baked at world pos).

## Questions for Game Art Bot
1. Sun vs far arch: from the Crown (eye -370,196,165) the far arch opening sits at bearing 276.8 +-8.4, elev -12.5..0.9; sun is bearing 262 elev 6, so the sun is NOT inside the arch. Move the far_arch card south and up in world.json, or retune sun? (I can move the card.)
2. Strata: 6 bands every 6 studs by world y via a 36-stud tiling strip texture on one StrataRock material per kit piece. OK, or do you want a separate MeshPart per band colour (6x MeshParts)?
3. Mine-head is not in world.json backdrop.pieces; placed at (134, ground, 392) east of H2. Confirm.
4. Cliff kit auto-placed (309 stacks) along heightfield drops >=10; outer rim left to terrain. Want rim coverage too (more tris)?
5. Scrub/rocks/gumdrop boulders scatter is invented (not in world.json). Density OK?
6. H3: ranger_footbridge deck end sits 2.9 studs (lower bound) from an H3 rail. Fine as a walkway, or pull it back?
7. Gondola cable/cabin and lift cage motion are not modelled (moving/out of scope).

## Needs PC (Cycles OptiX) renders
- Hero stills: Old Sugarloaf skyline, Sunset Arch at sunset from the Crown, Peppermint Dam and crest walk, Narrows crystal walls, Junction town.
- World vista/flythrough with terrain heightmap and sunset lighting.
- Only Workbench previews were made on the box.

## Pieces
| id | group | tris | MeshParts | materials | instances |
|---|---|---|---|---|---|
| old_sugarloaf_shell | hero | 14180 | 10 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite, Strata | 1 |
| sunset_arch | hero | 2528 | 1 | Strata | 1 |
| peppermint_dam | hero | 1652 | 6 | Iron, MintWhite, PepRed, SandBlock | 1 |
| intake_tower | hero | 1040 | 5 | GumCherry, Iron, MintWhite, PepRed, Window | 1 |
| ranger_station | building | 1090 | 6 | Licorice, MintWhite, PepRed, SandBlock, Timber, Window | 1 |
| junction_town | building | 3762 | 8 | Apricot, Bubblegum, GumLemon, Licorice, MintWhite, PepRed, Timber, Window | 1 |
| water_tower | building | 1296 | 5 | GumCherry, Iron, MintWhite, PepRed, Timber | 1 |
| mine_head | building | 1560 | 7 | GumLemon, Iron, Licorice, MintWhite, PepRed, Strata, Timber | 1 |
| gondola_station | structure | 1321 | 5 | Iron, MintWhite, PepRed, SandBlock, Timber | 2 |
| cableway_trestle | structure | 432 | 3 | Iron, PepRed, Timber | 3 |
| lift_frame_rock_candy | lift | 784 | 6 | Iron, MintWhite, PepRed, Rope, SandBlock, Timber | 1 |
| lift_frame_taffy_cliff | lift | 1392 | 6 | Iron, MintWhite, PepRed, Rope, SandBlock, Timber | 1 |
| lift_frame_gumdrop | lift | 1448 | 6 | Iron, MintWhite, PepRed, Rope, SandBlock, Timber | 1 |
| lift_frame_crown | lift | 1344 | 6 | Iron, MintWhite, PepRed, Rope, SandBlock, Timber | 1 |
| lift_cage | lift | 348 | 3 | Iron, PepRed, Timber | 4 |
| ranger_footbridge | bridge | 2284 | 3 | GumCherry, Rope, Timber | 1 |
| licorice_rope_bridge | bridge | 3112 | 4 | Licorice, MintWhite, PepRed, Timber | 1 |
| walk_boardwalk_6x12 | walkway | 168 | 1 | Timber | 3 |
| walk_boardwalk_8x12 | walkway | 168 | 1 | Timber | 0 |
| stair_flight_5 | walkway | 124 | 2 | SandBlock, Timber | 5 |
| landing_6x4 | walkway | 12 | 1 | SandBlock | 10 |
| railing_12 | walkway | 252 | 2 | Rope, Timber | 8 |
| cliff_w24_h6_p0 | cliff_kit | 76 | 1 | Strata | 31 |
| cliff_w24_h6_p1 | cliff_kit | 76 | 1 | Strata | 2 |
| cliff_w24_h6_p2 | cliff_kit | 76 | 1 | Strata | 1 |
| cliff_w24_h6_p3 | cliff_kit | 76 | 1 | Strata | 3 |
| cliff_w24_h6_p4 | cliff_kit | 76 | 1 | Strata | 108 |
| cliff_w24_h6_p5 | cliff_kit | 76 | 1 | Strata | 19 |
| cliff_w24_h12_p0 | cliff_kit | 136 | 1 | Strata | 3 |
| cliff_w24_h12_p1 | cliff_kit | 136 | 1 | Strata | 4 |
| cliff_w24_h12_p2 | cliff_kit | 136 | 1 | Strata | 15 |
| cliff_w24_h12_p3 | cliff_kit | 136 | 1 | Strata | 11 |
| cliff_w24_h12_p4 | cliff_kit | 136 | 1 | Strata | 13 |
| cliff_w24_h12_p5 | cliff_kit | 136 | 1 | Strata | 21 |
| cliff_w24_h24_p0 | cliff_kit | 256 | 1 | Strata | 29 |
| cliff_w24_h24_p1 | cliff_kit | 256 | 1 | Strata | 71 |
| cliff_w24_h24_p2 | cliff_kit | 256 | 1 | Strata | 4 |
| cliff_w24_h24_p3 | cliff_kit | 256 | 1 | Strata | 29 |
| cliff_w24_h24_p4 | cliff_kit | 256 | 1 | Strata | 2 |
| cliff_w24_h24_p5 | cliff_kit | 256 | 1 | Strata | 16 |
| cliff_w24_h48_p0 | cliff_kit | 496 | 1 | Strata | 5 |
| cliff_w24_h48_p1 | cliff_kit | 496 | 1 | Strata | 28 |
| cliff_w24_h48_p2 | cliff_kit | 496 | 1 | Strata | 93 |
| cliff_w24_h48_p3 | cliff_kit | 496 | 1 | Strata | 2 |
| cliff_w24_h48_p4 | cliff_kit | 496 | 1 | Strata | 20 |
| cliff_w24_h48_p5 | cliff_kit | 496 | 1 | Strata | 73 |
| slot_w24_h24_p0 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h24_p1 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h24_p2 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h24_p3 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h24_p4 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 10 |
| slot_w24_h24_p5 | cliff_kit | 658 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h48_p0 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h48_p1 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h48_p2 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 6 |
| slot_w24_h48_p3 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 5 |
| slot_w24_h48_p4 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| slot_w24_h48_p5 | cliff_kit | 1436 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| hoodoo_spire_a | scenery | 426 | 2 | GumCherry, Strata | 0 |
| hoodoo_spire_b | scenery | 486 | 2 | GumLime, Strata | 0 |
| hoodoo_spire_c | scenery | 386 | 2 | GumLemon, Strata | 0 |
| hoodoo_spire_d | scenery | 546 | 2 | Bubblegum, Strata | 0 |
| crystal_cluster_a | scenery | 204 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| crystal_cluster_b | scenery | 238 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| crystal_cluster_c | scenery | 238 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 0 |
| lollipop_cactus_a | scenery | 572 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 0 |
| lollipop_cactus_b | scenery | 572 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 0 |
| lollipop_cactus_c | scenery | 370 | 5 | Bubblegum, Cactus, GumLemon, GumLime, MintWhite | 0 |
| scrub_a | scenery | 100 | 1 | Scrub | 0 |
| scrub_b | scenery | 100 | 1 | Scrub | 0 |
| rock_a | scenery | 80 | 1 | Strata | 0 |
| rock_b | scenery | 160 | 1 | Strata | 0 |
| gumdrop_boulder_a | scenery | 94 | 1 | GumCherry | 0 |
| gumdrop_boulder_b | scenery | 188 | 2 | GumLemon, GumLime | 0 |
| sugar_dune_cap_a | scenery | 344 | 1 | PowderSugar | 5 |
| sugar_dune_cap_b | scenery | 344 | 1 | PowderSugar | 5 |
| hoodoos_north | cluster | 4586 | 5 | Bubblegum, GumCherry, GumLemon, GumLime, Strata | 1 |
| hoodoos_mid | cluster | 4506 | 5 | Bubblegum, GumCherry, GumLemon, GumLime, Strata | 1 |
| hoodoos_south | cluster | 5452 | 5 | Bubblegum, GumCherry, GumLemon, GumLime, Strata | 1 |
| narrows_crystals | cluster | 3876 | 4 | CandyAmber, CandyCore, CandyPink, Strata | 1 |
| cacti_floor | cluster | 9084 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 1 |
| cacti_taffy_north | cluster | 7570 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 1 |
| cacti_taffy_south | cluster | 12482 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 1 |
| cacti_crown | cluster | 6998 | 6 | Bubblegum, Cactus, GumCherry, GumLemon, GumLime, MintWhite | 1 |
| scatter_junction | cluster | 3420 | 2 | Scrub, Strata | 1 |
| scatter_rock_candy_narrows | cluster | 560 | 2 | Scrub, Strata | 1 |
| scatter_taffy_mesa | cluster | 1376 | 4 | GumCherry, GumLime, Scrub, Strata | 1 |
| scatter_dam | cluster | 2480 | 2 | Scrub, Strata | 1 |
| scatter_hoodoo_garden | cluster | 1176 | 5 | Bubblegum, GumCherry, GumLime, Scrub, Strata | 1 |
| scatter_crown | cluster | 1184 | 5 | GumCherry, GumLemon, GumLime, Scrub, Strata | 1 |
| distant_mesa_card | far_card | 10 | 1 | CardMesa | 14 |
| butte_spire_card | far_card | 6 | 1 | CardButte | 10 |
| far_arch_card | far_card | 12 | 1 | CardArch | 1 |
| far_butte_card | far_card | 8 | 1 | CardTwins | 1 |
| sun_disc | sky | 2 | 1 | SunGold | 1 |
| cloud_streak | sky | 6 | 1 | CardCloud | 8 |
| balloon_a | sky | 228 | 5 | Iron, MintWhite, PepRed, Rope, Timber | 2 |
| balloon_b | sky | 228 | 5 | Bubblegum, Iron, MintWhite, Rope, Timber | 2 |
| balloon_c | sky | 228 | 5 | GumLemon, GumLime, Iron, Rope, Timber | 2 |
