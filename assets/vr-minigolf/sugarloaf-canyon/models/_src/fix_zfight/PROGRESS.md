# Sugarloaf fix_zfight — PROGRESS (2026-10-14 ~03:50 PT)
List: no saved RobloxDevBot list found on disk; derived from Playtest v21 scan (/tmp/s_sc-v21-studio/zfight.json, meshOwner3D models): 186 models -> 182 FBX + 4 Studio-renamed instances of movers/h07_teleport_pads.fbx and h07_teleport_pad_exit.fbx (added). Placements solved from v21 inventory (MeshPart centres/sizes, yaw in 90° steps; Studio z offset -5000); felt/rails from holes.json world_offset/yaw. H3 holes.json differs from the v21 Studio felt (H3 moved since v21) — clearance for H3 assets is vs current holes.json.
Backup: _backup_20261014_0231 (listed FBX + manifests tar, protected_sha256.txt 303 files) — verified unchanged at end.
True-mesh before: 144 of 184 fail (int 140, coplanar 124, gap 113, thin 110, >=3k tris 40, clearance 39); 38 pass outright (cliff kits, shell parts, card, landing).
Priority: ranger_station (hand fix: sign board+glyphs moved down 0.606 under porch roof and forward of posts, glyphs 0.206 deep with 0.09 spacing; door/windows/sills proud of walls; roof planes -> one slab; gables extruded and trimmed under roof; flag stripes separated) before tris 1090 int 89 gap 17 cop 104 thin 21 -> 1842/0/0/0/0, IoU .99/.96/1.0. h01_dress_plants: 1744/256/44/100/53 -> 2980/0/0/0/0 (gap-safe decimation), felt 2.26 rail 1.75, IoU .89/.93/.94 (flag).
Exported 45 (reimported, import==build, roots same, all hard checks pass): ok 24: h07_bridge_skirts, h07_gap_floor_mist, dam_crest_parapets, stair_flight_5, h06_bell_tower, peppermint_dam_part1, balloon_a, balloon_b, balloon_c, h04_geode_wall, h03_ranger_station, h10_dress_plants, h02_headframe, h11_lock_keeper_hut, scatter_rock_candy_narrows, h09_pump_house, h17_dress_props, ranger_station, scatter_hoodoo_garden, scatter_taffy_mesa, h05_dress_plants, h06_dress_plants, h11_dress_plants, hoodoos_south
Look-change flag (IoU .80-.95) 21: h17_hour_stone_I, h11_quay_lip, h17_hour_stone_IV, h17_hour_stone_VII, walk_boardwalk_6x12, h17_hour_stone_VIII, h18_arch_gate, h01_trailhead_arch, lift_cage, h14_cableway_trestle, h17_shadow_arms, gondola_cabin, h06_sluice_frame, h14_dress_plants, h14_ore_bucket, slot_w24_h24_p4, h10_sluice_flume, h13_maze_rock, intake_tower, h15_dress_props, h01_dress_plants
NOT exported:
- rebuild wrecks the look (IoU<.8) 14: rim_silhouette, h17_hour_stone_X, h17_hour_stone_XI, flag, h11_lock_gate, h17_gnomon, h08_gumdrops, h11_lock_lift, h16_sinkhole_rim, h15_sugar_dune, h07_rope_bridges, h11_lock_chamber, h07_teleport_pads, h07_teleport_pad_exit
- still fails a hard rule after rebuild 72 (mostly >3k tris / over the original count; grounds, dress_props/plants, cacti clusters, hoodoos): railing_12, h06_sluice_gate, cableway_trestle, h05_echo_walls, old_sugarloaf_shell_part5, h14_dress_props, lift_frame_rock_candy, h04_dress_props, h12_intake_tower, water_tower, gondola_station, lift_frame_crown, h17_plinth, scatter_crown, lift_frame_taffy_cliff, lift_frame_gumdrop, peppermint_dam_part2, mine_head, h07_dress_props, slot_w24_h48_p2, h16_dress_props, slotT_w24_h48_p3, h14_loading_dock, h15_dress_plants, h08_dress_props, h01_dress_props, gondola_station_bottom, h09_dress_props, h08_dress_plants, h17_dress_plants, sunset_arch, h10_dress_props, scatter_dam, h07_dress_plants, h18_dress_props, h12_dress_plants, h03_dress_plants, h16_ground, h03_dress_props, h09_windpump_rotor, licorice_rope_bridge, h16_dress_plants, h13_dress_props, h15_ground, scatter_junction, h04_ground, h10_ground, h01_ground, h06_dress_props, h07_ground, h05_ground, h11_dress_props, h11_ground, narrows_crystals, h14_ground, hoodoos_mid, h17_ground, h03_ground, hoodoos_north, h02_dress_props, h13_dress_plants, h05_dress_props, h12_dress_props, h12_ground, h09_dress_plants, h02_dress_plants, h13_ground, h18_dress_plants, cacti_crown, cacti_taffy_north, cacti_floor, cacti_taffy_south
- rebuild crashed (out of memory at 6 GB cap, or every part dropped) 15: h07_island_respawn_stone, h17_hour_stone_III, h17_hour_stone_IX, h17_hour_stone_XII, h07_bridge_parapets, h09_water_tank, ranger_footbridge, gondola_cable, junction_town, trading_post_deck, h06_ground, h09_ground, h08_ground, h18_ground, h02_ground
Out: fbx/fix_zfight/ (45 FBX, fix_zfight_manifest.json, fix_zfight_fitcheck.json, silhouettes_fix_zfight.png). Scripts/metrics: _src/fix_zfight/work/. PC: all 3dmb_* tasks deleted, no Blender running.

## Batch 2 (04:30–05:20 PT) — the 101 not exported (99 + 2 teleport pads)
Ladder per asset (box, ulimit 5 GB, timeout 500 s, 3 at a time): chunked rebuild (overlap groups rebuilt separately), "big" vs "small-first" pocket order, pre-decimation to 1600/900 for >2.4k originals, then gap-safe decimation to <=3k. Hour stones III/IX/XII are skins of code walls H17:hour_stone_* (same 1.2x0.8x1.2 box) -> those walls exempted from their own clearance (only these 3). PC: 4 sequential detached build+reimport jobs (12 assets each), tasks deleted, no Blender left.
Exported 46 more to fbx/fix_zfight/ (manifest/fitcheck merged, batch=2; sheet silhouettes_fix_zfight_batch2.png). h16_dress_plants failed the reimport check, not exported. Protected files verified unchanged.

## fix_zfight2 (05:10 PT) — h11_lock_gate braces restored
Hand build: Timber top/bottom rails 0.206, 6 alternating PepRed/MintWhite bars + 2 Iron bars (0.206), all 0.086 apart; ends x±1.79, back face z−0.178 (rail5/rail7 0.15). 120 tris, all checks pass, IoU .88/.83/.86. Batch-2 file untouched (sha same). Out: fbx/fix_zfight2/.

## Batch 3 (05:00–06:30 PT) — 40 of the 55 exported (manifest batch=3, sheets silhouettes_fix_zfight_batch3.png + _batch3b.png)
- Over 3k (8): hand cleanup per part (decimate → simplified hull → shrunk hull, each re-verified): junction_town 2950, gondola_station_bottom 2948, h12_dress_props 2934, h13_dress_plants 2944, h02_dress_plants 2950, h18_dress_plants 2948, slotT_w24_h48_p3 2932; narrows_crystals fixed limit 4000 (approved original is 3876) -> 3988.
- Hand builds: h07_island_respawn_stone (raised 0.156), h07_bridge_parapets (rail skins: moved 0.656 outboard of rope rails, shortened to clear end rails, posts/panels/rope/beam 0.086 apart).
- Grounds: 16 tile sets (6–12 tiles each, max 2922 tris/tile, tiles 0.086 apart, same pivot; manifest tile_of/tile_set + top-level tile_sets). h04_ground and h17_ground failed reimport/set check — not exported.
- Hard failures fixed: h06_sluice_gate, mine_head, h12_intake_tower (pair pocketing + rail pad), h17_plinth (skin of code wall H17:gnomon_plinth_* -> exempt), hour stones III/IX/XII (stones straddle edge rails: trimmed 0.3 off the rail side; numerals inlaid in pockets).
- Shape loss fixed: hour stones X/XI (inlaid numerals), h08_gumdrops (skin of H8:gumdrop1/2 -> exempt, IoU .94), flag, rim_silhouette, h17_gnomon, h11_lock_chamber (face-on IoU ≥.89; loss is the mandated 0.206 thickness of thin sheets).
Left (15): h04_ground, h17_ground, h16_dress_plants (1 thin part after reimport), trading_post_deck (placement fit error 9.17, rail −0.48), licorice_rope_bridge (6016 tris, 13 stacked), cacti_crown/floor/taffy_north/taffy_south (15–21k tris, scatter sets), h11_lock_lift, h16_sinkhole_rim, h15_sugar_dune, h07_rope_bridges, h07_teleport_pads, h07_teleport_pad_exit.
PC: all 3dmb_* tasks deleted, no Blender running. Protected files verified unchanged.

## Batch 4 (06:07–07:00 PT) — in progress
- Grounds: NEW heightfield-slab method (box: /workspace/sc/hf4.py): grid-resampled original top (1.0 grid, bilinear), bottom = original bottom or top-0.206, clearance holes only where the slab band meets felt/rail (+0.16), pinch/sliver cleanup, tiles cut on grid lines with identical seam verts and no seam walls. All 18 sets pass per tile; merged reimported set watertight (0 open edges); top-view holes 0–0.21 sq studs per set (batch 3 had 52–652). Exported 188 tiles -> fbx/fix_zfight3/ (manifest/fitcheck/silhouettes_fix_zfight3_grounds.png). Batch 3 grounds untouched.
- rim_silhouette -> fbx/fix_zfight4/ (full wavy top outline, 33 pts, extruded 0.206; batch-3 file untouched).
- Exported to fbx/fix_zfight/ (batch=4): cacti_crown(7 tiles), cacti_floor(8), cacti_taffy_north(9), licorice_rope_bridge(1880 tris, single file), h07_rope_bridges, h07_teleport_pads, h07_teleport_pad_exit (lifted 0.156 off felt; placements from v21), h11_lock_lift (hand rebuild 20 lip segs+deck), h15_sugar_dune, h16_sinkhole_rim (cup pieces offset inward, no cut).
- Also exported (07:00): cacti_taffy_south (12 tiles), h16_dress_plants (2882), trading_post_deck (1878, layout.json placement, 0 rail1 tall-part violations) after thin-safety fix + PC rebuild; sheet silhouettes_fix_zfight_batch4b.png.
- DONE: batch 4 complete. fix_zfight 275 FBX total, fix_zfight3 188, fix_zfight4 1. Protected hashes OK.
- PC: 3dmb tasks deleted, no Blender.

## fix_zfight5 (07:10 PT) — h16_sinkhole_rim round lip — EXPORTED (fbx/fix_zfight5: fbx, manifest, fitcheck, sheet); reimport == build, all checks pass, felt 0.167, 1236 tris; PC clean; protected hashes OK
- geom b3/geom5_h16_sinkhole_rim.json (sink5.py 1.06 1.3 64): 64-seg GeodeRim annulus, bottom y 0.167 over felt edge; whole-asset top IoU 0.596 (target .85 unreachable: thickened ropes cap posts/ropes region at ~0.70; sinkhole is square x/z ±1.2 per holes.json).

## fix_zfight6 (07:15 PT) — h16_sinkhole_rim SQUARE frame — EXPORTED fbx/fix_zfight6 (manifest, fitcheck, sheet); 756 tris, felt 0.167, all checks pass, reimport == build

## Placeholders ph1 (07:30 PT) — in progress
- /workspace/sc/ph/gen.py builds 13 new meshes in anchor-local coords (holes.json decoration_anchors, world via world_offset/world_yaw); all pass checks on box. Next: Blender build (build_new.py creates materials), reimport, export fbx/placeholders_ph1/.
- DONE: fbx/placeholders_ph1/ — 13 FBX (60–584 tris each), all pass gaps/thickness/felt≥0.167/no coplanar; PC build+reimport tri counts match all 13; manifest (anchors, instance paths, neon_parts, collision/query/touch off), fitcheck.json, silhouette_sheet.png. PC cleaned (no 3dmb_ tasks, no Blender).
- Flags: plank_respawn_stone likely better as flat Studio decal; tunnel_lanterns is one lantern at anchor (notes say every 6 studs — duplicate in Studio).
- DONE: fbx/placeholders_ph1/ — 13 FBX (60–584 tris each), all pass gaps/thickness/felt≥0.167/no coplanar; PC build+reimport tri counts match all 13; manifest (anchors, instance paths, neon_parts, collision/query/touch off), fitcheck.json, silhouette_sheet.png. PC cleaned (no 3dmb_ tasks, no Blender).
- Flags: plank_respawn_stone likely better as flat Studio decal; tunnel_lanterns is one lantern at anchor (notes say every 6 studs — duplicate in Studio).

## LOOK7 / kit fitcheck 0.15 felt, 0.30 rail (2026-10-14 ~12:05 PT) — in progress
- Kit = layout.json (144 pieces, 874 instances) resolved to latest approved FBX (fix_zfight3 tiles, fix_zfight, top-level). First pass: 22 fails (18 grounds rail 0.16-0.20, h02/h09/h11/h13 dress_props rail 0.27-0.30).
- Fixes: hf5.py (rail-footprint dip to 0.33 below rail bottom, PAD 0.33) -> 191 ground tiles; dress_props rebuilt with CLR 0.317. Built on PC (l7g/l7p/l7d), reimport tris 208/208 match. Exported to fbx/fit030/ (195 FBX).
- Dressing: 11 rule-fixed kit props (_v2) + 2 thick dirt patches -> fbx/look7_dressing/. Layout additions generated by /workspace/sc/look7/gen_dress.py (edging, dirt, props, cliff steps).
- Box rebooted ~11:35 (lost files after 11:40 snapshot; ssh/tailscale restarted); recovered build inputs from PC.
- 12:06 PT DONE. Final kit fitcheck (layout 874 instances/144 pieces, latest FBX incl. fit030): 0 fails, min felt 0.335, min rail 0.323. 208 new FBX all pass anti-flash checks (<3k tris, no intersect/stack/coplanar/thin).
- fbx/fit030/ (191 ground tiles h01-h18 + 4 dress_props) + manifest, kit_fitcheck_030.json, silhouettes. fbx/look7_dressing/ (13 FBX + layout_look7_dressing.json: 439 edging, 34 dirt, 886 props, 101 cliff steps).
- Render: _src/render_hero_look7.py -> previews/hero/V1-hub-tee1_look7.png (+_draft, _vs_concept, look7_render_report.json). Sun 277/25 #FFC890 key 8, exposure 0.65, orange->turquoise sky, fill 400k/amb 0.5.
- Gondola cable/cabin: existing fix_zfight versions pass (cable 2850 tris, cabin 1624); no new meshes built. PC clean.
- 12:21 PT Game Art Bot priorities:
  - fbx/placeholders_ph2/tunnel_lanterns.fbx: lantern + iron hanger rod + crossbar arm + wall plate (east tunnel side), 132 tris, all checks pass, reimport 132=132. manifest/fitcheck/silhouette.
  - render_hero_look8.py -> previews/hero/V1-hub-tee1_look8.png (+_draft, _vs_concept, look8_render_report.json). Render-only: far cliffs hidden -> sparse separate hoodoo spires (varied scale), far terrain x0.2 beyond 70 studs, upper tiers hidden, sun 18/6 in frame, orange->pink->violet sky, trading-post foreground props + rope posts. Fixed bug: shot loop reset hide_render on instances.
- Edging overlap fix (parked): layout_look7_dressing_edgefix.json written (7 edging pair + 50 edging-vs-prop issues found; 81 shifted, 37 dropped, 402 kept, 0 remaining edging-edging). Full felt/rail re-fitcheck of that file not yet run.
- 2026-10-14 12:40 PT: placeholders_ph2/tunnel_lanterns_post.fbx (132 tris) built on PC; wall plate -> 0.206x0.3 iron post to tunnel ground (gap 0.086), felt 0.94 rail 0.32, 0 intersect/coplanar/thin. manifest+fitcheck updated, silhouette_sheet_post.png. Next: look9.
- 12:26 PT edgefix fitcheck: layout_look7_dressing_edgefix.json 1423 inst, min felt 0.218, rail 0.333, 0 clear fails; 64 cliffT self-overlap pairs -> dropped 40 cliffT steps -> layout_look7_dressing_edgefix2.json (1383 kept, verify 0 pairs).
- 12:30 PT placeholders_ph2/tunnel_lanterns_post2.fbx: post bottom world y 18.27 (pierces ground 0.1), 132 tris, checks in fitcheck.json.
- 12:39 PT look9: _src/render_hero_look9.py -> previews/hero/V1-hub-tee1_look9.png (+look8_vs_look9, look9_render_report.json). 6 wide layered mesas (5 banded tiers each) replace hoodoo spires; removed peppermint_dam (striped building), mine_head, gondola cable/cabin/station + lift_frame tower, far cards, floating creeks/falls, pass4 cloud streaks; right red terrain wall clamped (render-only); sky #FF8A2A>#FFAA55>#FFC283>#FFB894>#FFA7A4>#F49FB2, exposure 0.85. No 3dmb_ tasks left.
- 12:50 PT edgefix3: 40 dropped cliffT steps all left gaps (top-down) -> 40 scaled fills (xz 0.4-0.9) -> fbx/look7_dressing/layout_look7_dressing_edgefix3.json (1423 inst), 0 overlap/coplanar pairs, fills felt/rail far (>99). Top-downs previews/look7_dressing/cliff_steps_topdown_{before,after}.png. Layout copies in fbx/look7_dressing/.
- 12:50 PT look10: _src/render_hero_look10.py -> previews/hero/V1-hub-tee1_look10.png; station+cabin restored (out of frame from this eye), cable hidden (streaks), lift tower moved 88 studs into gap between mesas, sun halo. Alt with tower hidden: _look10_alt_tower_hidden.png. PC clean.
- 13:00 PT final hero = previews/hero/V1-hub-tee1_final.png (copy of look10_alt_tower_hidden). edgefix4: fbx/cliff_fillers/cliff_filler_rock_{a,b}.fbx (32 tris each, Strata, manifest) x409 placements -> fbx/look7_dressing/layout_look7_dressing_edgefix4.json (1832 inst), 0 overlap/coplanar, min felt 0.218 rail 0.333, min filler dim 0.49. Top-down previews/look7_dressing/cliff_steps_topdown_edgefix4.png. PC clean.
- 13:15 PT h16_rim_2slot: fbx/h16_rim_2slot/h16_sinkhole_rim.fbx (852 tris) = zfight6 frame/rope/posts + batch4 12 crystals split CrystalPink (6 large) / CrystalAmber (6 small), Neon; manifest + preview_close/wide.png. Crystals as-is fail thickness (0.12) and felt (0.06).
- 13:25 PT h16_rim_2slot_b: rule-compliant crystals (thickened, moved inward), 2 slots, checks pass; manifest + previews.
- 13:50 PT v42 item5: ranger_station (fix_zfight) clean on triangles (Lic/Mint gap 0.086, 0 coplanar; OBB proxy false positive) - no revision. h03_dress_props: boulder bases intentionally sunk 0.55-0.69 (0 coplanar); 3 Strata slabs with tops 0.02-0.06 under ground lifted -> fbx/fix_v42_item5/h03_dress_props.fbx (1966 tris, all checks pass) + manifest.
- 14:00 PT fix_v42_item5b/h03_dress_props.fbx: 3 Strata slabs planted (bottom 0.10 below ground, top 0.20-0.42 above), original materials kept, all checks pass, preview_slabs.png.
- 14:15 PT fix_v42_item5c/h03_dress_props.fbx: 7 off-tile H3 prop clusters moved onto fit030 tiles (0.5-13.5 studs), none deleted; checks pass; closeup_before_after.png.

## 2026-10-14 — Playtest v49 items 5 and 3
- **Item 5:** `fbx/look7_dressing/layout_look7_dressing_v49fix.json`, made from edgefix4. It has 1,393 instances; 439 were deleted.
  - 409 cliff fillers were deleted because they were buried 2–96 studs under the terrain.
  - 30 pieces were deleted by Game Art Bot's rule: no footprint on the felt, and at least 1 stud in plan view from any rail.
  - 162 floaters were lowered by the Studio gap + 0.12. All 162 passed re-verification: felt ≥0.15, rail ≥0.30, 0 bad pairs.
  - All 23 flush records checked on real triangles: false positives. The 17 ground records already overlap their tile with 0 coplanar faces and needed no lowering. 3 records were on pieces deleted by the rule. The 3 cliff pairs have real gaps of 0.35, 0.86 and 1.00.
- **Item 3:** `fbx/look7_dressing_lod/` has 9 LOD FBXs, `manifest.json` and `silhouettes_src_vs_lod.png`. Ratios run from 0.31 to 0.82; cactus and barrels are limited by the 0.2 thickness rule.
  - H1 tee estimate: 1.35M → 1.11M with LOD → 1.077M with `layout_look7_dressing_v49fix_thin60.json` (112 dressing pieces >60 studs from every hole deleted).
  - The 0.9M target is NOT met. Reaching it needs about 572 near-hole cuts; that needs a Game Art Bot decision.

## 2026-10-14 — H16 rim 2slot_c
- `fbx/h16_rim_2slot_c/`: made from 2slot_b, which is untouched. The 12 crystals were pushed outward so the minimum plan radius is 1.110 from the hole centre.
- Because they now sit under the felt deck, they were lowered to top y -0.556.
- Frame, rope and posts are unchanged; rim height 0.167. GeodeRim frame is #C8463F, Studio material Rock.
- Reimport checks: thickness 0.206, gap 0.086, 0 coplanar, 0 intersecting, felt 0.156, crystal-to-frame 0.723, crystal-to-post 5.97.
- Includes previews, a silhouette sheet and a manifest.

## 2026-10-14 — H16 rim 2slot_d (2slot_c rejected: crystals hidden)
- `fbx/h16_rim_2slot_d/`: made from 2slot_b; b and c untouched. Crystals keep their 2slot_b positions.
- Crystal tops were scaled vertically to -0.086, i.e. 0.086 below the ball plane. Amber bases are 0.068 lower to keep 0.2 thickness. Four pinks were also scaled in plan to 0.91–0.94.
- Checks: thickness 0.203, gap 0.086, 0 coplanar, 0 intersecting, felt 0.167, rail 0.16, crystal-to-frame 0.294.
- GeodeRim frame is #C8463F, Studio material Rock.

## 2026-10-14 ~18:30 PT — v69 visible placeholders: H1 lollipop cactus and H6 flood-mark rock (placeholders_ph2)
- **`lollipop_cactus_1.fbx`** (1,860 tris), target CFrame (66, 18.2, -4548).
- **`flood_marks_rock.fbx`** (128 tris), target CFrame (266.5, 26.2, -4767). It was moved 2.08 west, because the placeholder sat on rail3.
- Manifest is `manifest_h01_cactus_h06_floodrock.json`; previews and a silhouette sheet are included. The existing tunnel lantern files and `manifest.json` are untouched.
- Re-imported checks: thickness ≥0.222, gaps ≥0.085, 0 intersecting, 0 coplanar, bases sunk 0.1.
- Clearances: cactus felt 1.88 / rail 1.38; rock felt 2.08 / rail 1.27 (rail distances in plan view).
- Built on the PC by Claude Code (schtask 3dmb_sc_ph3). The task is deleted and no Blender is running.

## 2026-10-15 11:00 PT — PC handed back; 3 jobs (Claude Code, claude-opus-5-5 confirmed available on PC)
- Work dir box /workspace/sc/ph4, PC C:\Users\chase\sc_fix\ph4. One 3dmb_* schtask at a time.
- Job 1 (lollipop_cactus_1 fix): stick now runs y 7.504–8.890, sunk 0.30 into the crown (top 7.804); middle ring (was MintWhite, read gray) -> 6 spiral-cut swirl sectors alternating Bubblegum / Cream #F6E3C8, 0.086 gaps. Box: 2,212 tris, thick .222, gap .086, 0 coplanar. Running 3dmb_sc_j1.
- 11:10 PT Job 1 DONE -> fbx/placeholders_ph3/lollipop_cactus_1.fbx (APPROVED per Chase, no review). Reimport 2,212 tris (Cactus 1276 / Bubblegum 620 / Cream 288 / MintWhite 28), thick .222, gap .086, 0 coplanar, felt 1.88 / rail 1.38, CFrame (66, 18.2, -4548) yaw 0. Manifest manifest_placeholders_ph3.json + 3 previews. ph2 file untouched. 3dmb_sc_j1 deleted, no Blender. (Claude briefly wrote step logs to /tmp on the PC and deleted them.)
- 11:25 PT Job 2 DONE -> fbx/h10_chevrons/h10_chevrons.fbx (NEW, for Game Art Bot review). 160 tris, 1 mesh / 8 chevrons at hole-local z -15..-29 (2.0 apart), 2.36 x 1.2 x 0.206, shaped to the 12.68 deg chute, flat base on the felt plane, apex -Z downhill. UVs: top = chevron cell 1 of h10_chevrons.png (all samples opaque), sides solid amber. Rail 0.32 (rail2/rail3/rail11 inner faces), felt 0.00 by request (base at felt level). CFrame (290, 114.2, -5278) * Angles(0, pi, 0). Previews player/close/top + texture copy + manifest_h10_chevrons.json. First build had sides sampling the strip edge and a mis-framed close-up: refit mesh to the texture outline and re-ran as 3dmb_sc_j2b. Tasks deleted, no Blender.
- 11:40 PT Job 3 (Lantern Grove H5 disc UVs) DONE -> lantern-grove/models/fbx/fix_zfight5_uv/ (logged in lantern-grove PROGRESS.md). All 3 jobs complete; no 3dmb_* tasks left, no Blender running.
- 11:30 PT H10 chevrons rev2 (Game Art Bot rejected v1) -> fbx/h10_chevrons_v2/ (v1 untouched). 160 tris, 8 pieces 0.96 wide, arms 0.22, 0.206 thick sunk so top is 0.080 above the felt (bottom −0.126), tilted 12.68°, 0 faces coplanar with the felt, rail clearance 1.02 (rail2/3/11/12), same pivot/CFrame/spacing. Top textured with h10_chevrons.png. Previews player/close/top. 3dmb_sc_j4 deleted, no Blender.
