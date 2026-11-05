# Aurora Archipelago - P1 props (out_props)

Generated 2026-10-12T07:14:10 by headless Blender 5.2 from `_src/` (pipeline adapted from the Lantern Grove library: registry -> build_all -> fitcheck -> docs). **All props are visual only**; collision = holes.json.

## Files

| Path | What |
|---|---|
| `fbx/<prop>.fbx` | One FBX per prop (root empty + one mesh per material, textures embedded). `aa_kit_*` reused kit, `aa_hNN_*` per-hole props, `aa_world_*` world pieces |
| `fbx/aa_hNN_dressing.fbx` | Per-hole static P1 dressing merged per material in the HOLE FRAME (origin = holes.json world_offset, rotated by world_yaw: `PivotTo(holeRoot)`), < 20k tris each |
| `textures/*.png` | 512x512 tiling textures (timber, snow, slate_rock, basalt_hex, ice, felt, coral, moonstone); also embedded |
| `manifest.json` | Per file: holes, bbox, tris, materials/parts, pivot, motion; `holes[]` per-hole instances (hole frame + world pos); `world_instances[]`; `lights[]`; `hole_dressing_files[]` |
| `fitcheck_p1props_validated.txt`, `fitcheck_report.json` | Numeric fitcheck vs holes.json (ALL PASS) = the latest run, `fitcheck_walls_validated.txt` (Round 4 'walls'); `fitcheck_clear_validated.txt` = the Round 3 'clear' run, `fitcheck_railskin_validated.txt` = the rail-skin run |
| `fbx/aa_h12_paddle_wheel_collision.fbx`, `fbx/aa_h14_icicle_bell_collision.fbx` | Round 3: the movers' holes.json blockers as box meshes (one MeshPart per box, CollisionFidelity Box, Transparency 1), origin = pivot (`collision_fbx_files[]`) |
| `previews/walls/` | Round 4 'walls': H11 slot lintel (1.27) with the floe, H12 icebreaker stern (z -18.01) with the paddle wheel; eye, 3/4, side |
| `previews/clear/` | Round 3: H12/H14 eye, 3/4, side view at the lowest point + 1-stud close-ups of the felt gap (visual / collider) |
| `fbx_validation.json` | Re-import check of every FBX |
| `previews/<prop>_eye.png`, `_34.png` | Eye height 5 with a 5-stud reference capsule (blue), and 3/4 view; movers show their axis (red = rotate/swing, cyan = slide) |
| `previews/tee_hNN.png`, `tee_contact_sheet.png` | VR tee view (5 studs) of every hole over the pass-2b world |
| `contact_sheet.png` | All prop previews, labelled |
| `aurora_props_p1.blend`, `aurora_props_p1_in_world.blend` | All props laid out; props placed in the 2b world |
| `props_p1_summary.md` | P1 coverage, tris, per-hole near field, movers, conflicts, caveats |
| `_src/` | Generators: `aalib.py`, `registry.py`, `holesdata.py`, `skins.py`, `props_kit.py`, `props_movers.py`, `props_holes.py`, `textures.py`, `build_all.py`, `fitcheck.py` (+ `fitcheck_decor.py`, pass 2e; `fitcheck_clear.py`, Round 3), `collision_movers.py` (Round 3), `previews_clear.py`, `verify_fbx.py`, `tee_views.py`, `make_docs.py`, `build.ps1` |

Rebuild: `_src/build.ps1` (textures -> build_all -> fitcheck -> verify_fbx -> tee_views -> make_docs).

## Export / axes

1 Blender unit = 1 stud, scene units NONE, modelled Z-up. FBX `axis_forward='-Z'`, `axis_up='Y'`, scale 1.0, `FBX_SCALE_UNITS`, embedded textures, face smoothing. Roblox (x, y, z) = Blender (x, -z, y). Import with the scale unit **Stud**.

## Import (build bot)

1. Import each FBX as a Model; every child `<prop>__<Material>` becomes a MeshPart. Set Color / Material / Transparency from `manifest.json > props[].parts[]` (table below). Neon parts are glow cores; add PointLights from `lights[]` (position world + hole-local, range, brightness, colour).
2. Every MeshPart: `Anchored=true, CanCollide=false, CanQuery=false, CanTouch=false, CollisionFidelity=Box`; CastShadow off on Neon/Steam/Lagoon/IceSheen.
3. Per-hole dressing: `Model:PivotTo(CFrame.new(world_offset) * CFrame.Angles(0, math.rad(world_yaw), 0))`. Loose instances (flag, movers, puffs): `holeCF * CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0)` with `pos/yaw/scale` from `holes[].instances[]`. World pieces: `world_instances[]` (world coordinates; non-uniform `scale` = set each MeshPart.Size).
4. Movers: origin = holes.json pivot. Drive with the blocker formula every Heartbeat: rotate `pivotCF * CFrame.fromAxisAngle(axis, rad(speed*t + phase))`; slide `pivotCF + axis*offset(t)` (ping-pong with dwell); swing `hingeCF * CFrame.fromAxisAngle(axis, rad(amp*sin(2*pi*t/period + phase)))`; H17 span = Transparency toggle. Red/cream bands appear only on moving parts.
5. Flag: rotate the `__FlagRed` banner (or the whole model) about the pole axis (origin Y) to face the tee.

## Material table (flat-colour fallback)

| Material | Colour | Roblox Material | Emission | Transparency | Use |
|---|---|---|---:|---:|---|
| `Timber` | `#8A5A3C` | WoodPlanks | 0 | 0 | snow-capped timber rails/posts (pass 2b warm timber) |
| `Snow` | `#F4F6FF` | Snow | 0 | 0 | thick rounded snow caps, drifts |
| `SnowShadow` | `#C9C3EC` | Snow | 0 | 0 | shaded snow / packed snow walls |
| `Rock` | `#5E6177` | Slate | 0 | 0 | slate-violet rock |
| `Basalt` | `#3A3550` | Basalt | 0 | 0 | dark basalt (geyser, cliff, rims) |
| `Brass` | `#C9A04A` | Metal | 0 | 0 | brass fittings, bolts, lanterns, gauge |
| `Glow` | `#FFB861` | Neon | 4.0 | 0 | ember lantern core (PointLight #FFB861) |
| `Ice` | `#8FE3FF` | Glass | 0.3 | 0.3 | glass-look glacier ice (Transparency 0.3, Reflectance 0.1) |
| `IceCore` | `#BFF6FF` | Neon | 3.0 | 0 | crystal-core neon inside glass ice |
| `IceSheen` | `#9FE3F2` | Glass | 0 | 0.15 | H4 glassy ice felt (Transparency 0.15, Reflectance 0.15) |
| `AuroraMint` | `#5CFFB0` | Neon | 3.0 | 0 | aurora mint: decals, cues, ribbons |
| `AuroraViolet` | `#B07CFF` | Neon | 3.0 | 0 | aurora violet: ribbon gradient end |
| `AuroraTeal` | `#3DE2C8` | Neon | 2.0 | 0 | aurora teal accents |
| `Lime` | `#D8FF6A` | Neon | 4.0 | 0 | teleport / respawn aurora-lime glow |
| `Lagoon` | `#2FD6C8` | Glass | 0.4 | 0.3 | lagoon / hot-spring water |
| `Steam` | `#E9FBFF` | SmoothPlastic | 0.3 | 0.5 | steam puffs (Transparency 0.5; particles in game) |
| `CoralPink` | `#FF6FB5` | SmoothPlastic | 0 | 0 | bubblegum coral-ice |
| `CoralOrange` | `#FFA552` | SmoothPlastic | 0 | 0 | tangerine coral-ice |
| `CoralMint` | `#6FFFD2` | Neon | 2.5 | 0 | coral neon core / glowing tips |
| `Pine` | `#2F6B4F` | Grass | 0 | 0 | frosted pine boughs |
| `Ink` | `#222233` | SmoothPlastic | 0 | 0 | snowpuff body / sign lettering / gauge face |
| `Cream` | `#FFF4E2` | SmoothPlastic | 0 | 0 | snowpuff belly, sign boards |
| `Beak` | `#FF9A3C` | SmoothPlastic | 0 | 0 | snowpuff beak |
| `FlagRed` | `#E03C31` | Fabric | 0 | 0 | cup-flag banner (holes.json cup.flag.banner_color) |
| `MoveRed` | `#D3362A` | SmoothPlastic | 0 | 0 | moving-part signal red (bands ONLY on moving parts) |
| `MoveCream` | `#FFF2D8` | SmoothPlastic | 0 | 0 | moving-part signal cream (bands ONLY on moving parts) |
| `Moonstone` | `#E6E2F0` | Marble | 0 | 0 | H16 pearl moonstone coping / flags |
| `Silver` | `#C8CDD8` | Metal | 0 | 0 | silver inlay, crescent spout trim |
| `Canvas` | `#7A5CC8` | Fabric | 0 | 0 | static hut canvas/paint violet (static props avoid red/cream) |
| `HullTeal` | `#2F5D7A` | WoodPlanks | 0 | 0 | H12 static icebreaker hull (not red: red/cream reserved for movers) |
| `Felt` | `#36997A` | Fabric | 0 | 0 | felt top strips on meshes that carry felt (H3 plank); matches pass 2g felt |
| `SignalGreen` | `#5CFF7A` | Neon | 3.0 | 0 | H5 signal lamp lens (script tints green/amber) |

## Hole dressing files

| File | Hole | Tris | Mesh parts | Instances merged |
|---|---|---:|---:|---|
| `fbx/aa_h01_dressing.fbx` | H1 | 2,178 | 6 | aa_h01_decals, aa_h01_harbour_lantern, aa_h01_rails, aa_h01_snow_boulder |
| `fbx/aa_h02_dressing.fbx` | H2 | 3,410 | 11 | aa_h02_decals, aa_h02_lantern_cue, aa_h02_lintel_left, aa_h02_lintel_mid, aa_h02_lintel_right, aa_h02_rails, aa_h02_rookery_drift, aa_kit_sign_lantern_L, aa_kit_sign_lantern_R |
| `fbx/aa_h03_dressing.fbx` | H3 | 3,824 | 11 | aa_h03_decals, aa_h03_ice_plank, aa_h03_rails, aa_kit_ice_bridge_deck, aa_kit_sign_lantern_R, aa_kit_sign_plank |
| `fbx/aa_h04_dressing.fbx` | H4 | 2,662 | 5 | aa_h04_decals, aa_h04_ice_sheen, aa_h04_rails |
| `fbx/aa_h05_dressing.fbx` | H5 | 3,528 | 8 | aa_h05_cliff_face, aa_h05_decals, aa_h05_rails, aa_h05_signal_lamp, aa_kit_geyser_cone |
| `fbx/aa_h06_dressing.fbx` | H6 | 2,996 | 7 | aa_h06_decals, aa_h06_kettle_pool, aa_h06_rails |
| `fbx/aa_h07_dressing.fbx` | H7 | 3,744 | 3 | aa_h07_rails |
| `fbx/aa_h08_dressing.fbx` | H8 | 5,156 | 7 | aa_h08_coral_1, aa_h08_coral_2, aa_h08_coral_3, aa_h08_coral_4, aa_h08_coral_5, aa_h08_coral_6, aa_h08_coral_7, aa_h08_giant_coral, aa_h08_rails |
| `fbx/aa_h09_dressing.fbx` | H9 | 4,224 | 12 | aa_h09_conch, aa_h09_decals, aa_h09_rails, aa_h09_reef_lagoon, aa_kit_sign_lantern_L, aa_kit_sign_plank |
| `fbx/aa_h10_dressing.fbx` | H10 | 1,700 | 7 | aa_h10_bobsled_hut, aa_h10_rails, aa_h10_snow_walls |
| `fbx/aa_h11_dressing.fbx` | H11 | 2,139 | 10 | aa_h11_decals, aa_h11_fishing_hut, aa_h11_rails, aa_kit_sign_lantern_R |
| `fbx/aa_h12_dressing.fbx` | H12 | 3,995 | 8 | aa_h12_decals, aa_h12_icebreaker, aa_h12_rails, aa_kit_sign_lantern_R |
| `fbx/aa_h13_dressing.fbx` | H13 | 3,646 | 11 | aa_h13_carousel_canopy, aa_h13_decals, aa_h13_hub_base, aa_h13_rails |
| `fbx/aa_h14_dressing.fbx` | H14 | 2,875 | 8 | aa_h14_bell_gantry, aa_h14_decals, aa_h14_rails, aa_kit_sign_lantern |
| `fbx/aa_h15_dressing.fbx` | H15 | 2,188 | 6 | aa_h15_decals, aa_h15_lip_ice, aa_h15_lip_parapet, aa_h15_rails |
| `fbx/aa_h16_dressing.fbx` | H16 | 1,344 | 4 | aa_h16_moonwell, aa_h16_rails |
| `fbx/aa_h17_dressing.fbx` | H17 | 4,462 | 11 | aa_h17_aurora_ribbon, aa_h17_crystal_piers, aa_h17_decals, aa_h17_rails, aa_h17_span_lamp, aa_kit_ice_bridge_deck, aa_kit_sign_lantern_R, aa_kit_sign_plank |
| `fbx/aa_h18_dressing.fbx` | H18 | 1,754 | 4 | aa_h18_crystal_bank_ne_deco, aa_h18_crystal_bank_sw_deco, aa_h18_crystal_chute, aa_h18_decals, aa_h18_halo_arch, aa_h18_rails |
