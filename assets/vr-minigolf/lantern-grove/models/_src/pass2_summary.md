# Lantern Grove props: pass 2 summary (2026-10-09): dressing + textures

Art-director note: the tee views looked much barer than the concepts. This pass adds per-hole set dressing,
textured warm materials, variety props and golden-hour previews. holes.json stays the source of truth.

## What changed

1. **Per-hole set dressing** (`_src/dressing.py`, `_src/dressing_lib.py`)
   - Deterministic layouts for all 9 holes: **1,502 instances** in total (119 to 220 per hole).
   - Passes, in order:
     - tee-framing trees, including a new leaning maple that overhangs the lane with lanterns;
     - lantern spans across lanes, lantern hooks and lantern strings along the rails;
     - rail-side ground cover: bushes, toadstools, grass, ferns, leaf piles;
     - mid-ground bushes and toadstools;
     - near-ring trees plus theme extras (background mushroom houses on H3/H4, rock outcrops on the stream holes);
     - after all holes are laid out, a far ring of cheap tree clumps so no view ends in bare ground.
   - Themes per zone: forest (H1-2), village (H3-4), stream (H5-7), hollow (H8-9, with glowing mushrooms).
   - **Keep-outs** are built from holes.json plus the hero placements, in world space, against every hole:
     - felt, plus 1.25 (rails and a walk-by gap);
     - collision walls;
     - water/pit hazards;
     - every moving part's blockers and visual bbox, swept through the full motion (36 angle steps or 9 slide steps);
     - teleport entries and exits;
     - hero bboxes, and the hollow-tree trunk wall annulus (only props up to 4.5 tall inside the cavity);
     - tee pad and run-up;
     - straight walking corridors from each cup to the next tee.
   - Anything may overhang felt or paths only when it is at least **6.5 studs** above them (lantern spans, maple canopies).
   - Exported as:
     - `manifest.json > dressing.holes.HN.instances[]` (`prop`, hole-local `pos`, `yaw`, `scale`, `role`);
     - `lights[]`: 286 glow-core centres for PointLights;
     - `fbx/dressing_hNN_<a..k>.fbx`: 73 files, each under 20k tris (max 18,988). They are the same instances
       merged per material, with origin at the hole origin.
2. **Preview-only ground**: `dressing_lib.Ground` is a stepped, blurred heightfield (nearest felt - 0.6, water - 0.5) with
   the leaf-litter texture, plus a far apron. It is only used by `assembly.py` and is **never exported**. Dressing
   `pos.y` is sampled from it; in Studio, raycast onto Terrain instead.
3. **Textures**: `_src/textures.py` builds 14 seamless 512x512 PNGs into `textures/`:
   - felt (soft #4F9A3A with mowing bands), oak_wood, shingle, root_bark, birch_bark, slate_stone, limestone (rail blocks);
   - moss, plaster, thatch, leaf_litter;
   - foliage_red, foliage_orange, foliage_gold.

   Every mesh gets box-projection UVs (`lglib.box_uv_bmesh`, re-applied after booleans) and Principled BSDF image
   textures. The FBX files embed them (`path_mode='COPY'`, `embed_textures=True`). The README documents the Roblox
   mapping (SurfaceAppearance ColorMap or MeshPart.TextureID, one texture per MeshPart) and keeps the flat-colour
   fallback table.

   New flat accent materials:
   - `Lacquer`: torii red. The torii had been reusing the leaf-textured MapleRed.
   - `CapOrange` / `CapGold`: orange toadstool caps and bracket fungi.
   - `PaperOrange`: orange lanterns.
4. **23 new variety props** (`_src/props_variants.py`):
   - Trees: `maple_tree_round`, `maple_tree_tall`, `oak_tree_orange`, `maple_tree_lanterns`, `maple_tree_overhang`,
     `maple_sapling`, `tree_backdrop_cluster`.
   - Toadstools: `toadstool_tall`, `toadstool_orange_cluster`, `toadstool_trio_small`.
   - Bushes and ground cover: `orange_leaf_bush`, `gold_leaf_bush`, `red_bush_tall`, `grass_tuft`, `fern_clump_large`,
     `leaf_pile_wide`, `leaf_scatter`, `rock_outcrop`.
   - Lanterns: `lantern_span_12/16/20`, `lantern_string_poles`, `lantern_hook_pair`.

   That makes 88 props in total. The heaviest single prop is still `heart_lantern_cluster` (6.5k tris).
5. **Previews**: `assembly.py` was rewritten:
   - textured felt, and rails made of repeated `rail_straight_4` pieces (no stretched textures);
   - collision boxes are hidden in the beauty views and shown in the top view;
   - golden-hour sun (~24°, warm) with a cool fill, and a warm-horizon sky gradient;
   - compositor mist haze plus fog-glow glare on the lanterns;
   - tee view at 1280x720, 72° horizontal FOV, from the VR eye height of 5;
   - neighbouring holes' dressing is drawn too, so each view shows what a player actually sees.

   `tee_sheet.py` writes `tee_contact_sheet.png`, and `--compare` writes concept|render pairs.
6. **fitcheck.py** gained 47 dressing checks, and all **64 checks PASS**. For each hole it checks:
   - no vertex inside any keep-out;
   - minimum gap of low geometry from any felt edge (1.28 to 1.42, needs 1.25 or more);
   - minimum height of anything over felt (6.65 to 8.43, needs 6.5 or more);
   - moving-part sweeps are clear;
   - every dressing FBX re-imported has under 20k tris and matches the manifest count.

   It also checks that every prop FBX is under 20k tris. Negative tests (a box on the felt, in the mill-wheel sweep,
   in the trunk wall, or on a path) are flagged correctly.
7. Docs and pipeline:
   - `build.sh` now runs textures → props → dressing → fitcheck → [assembly] → docs → tee sheet;
   - README regenerated;
   - manifest has a `textures` block, per-part `texture`, per-prop `dressing_uses`, and `dressing.prop_use_counts`;
   - the props.md mill-wheel note is updated (props.md now matches holes.json);
   - the repo skill `blender-asset-pipeline` gained texture and dressing lessons.

## Iterations against the concepts (tee views)

- **It 1**: dressing worked, but the views were bare and foggy. Near trees showed only trunks because the camera was
  pitched too low, the torii picked up the leaf texture, and there were few rail-side props. Fixes:
  - flat `Lacquer` material for the torii;
  - eye pitch about 9° down;
  - Standard view transform with less haze;
  - overhang maple;
  - more bushes in the rail-side pool.
- **It 2**: H1-H4 matched the concepts' framing, but H5-H8 ended in empty beige ground and the rail-side pass was
  starved by its own overlap rule. Fixes:
  - small props may clump (0.55-0.62 base overlap);
  - two edge rows;
  - `tree_backdrop_cluster` far ring;
  - bluer sky and warmer haze;
  - felt mowing bands;
  - cheaper canopies.
- **It 3**: early holes' backdrops stole tree space from later holes (H6 had 4 trees). Fixes:
  - two-phase layout: course-side dressing for all holes first, then the backdrop, measured from every hole's felt;
  - near-tree band 4.5-24 studs, weighted toward the tee view;
  - neighbours' dressing drawn in the previews;
  - slightly brighter exposure.

  Result: every tee view is framed by red/orange canopies with hanging lanterns, has bushes and toadstools along the
  rails, and ends in a forest wall, close to the density and feel of `hNN-concept.png`.

## New files

- `textures/*.png` (14)
- `fbx/dressing_h01_a..h` … `fbx/dressing_h09_a..i` (73)
- `fbx/<23 new props>.fbx`
- `previews/<new props>_{eye,34}.png`
- `tee_contact_sheet.png`
- `_src/textures.py`, `_src/props_variants.py`, `_src/dressing_lib.py`, `_src/dressing.py`, `_src/tee_sheet.py`
- `_src/pass2_summary.md`

## Tee previews

`previews/assembly_h01_tee.png` … `previews/assembly_h09_tee.png`, plus `assembly_hNN_top.png` (cutaway with
collision boxes) and `assembly_hNN.png` (overview). All 9 are on `tee_contact_sheet.png`.

## Known issues

- **Heavy merged groups**: 1.26M dressing tris in total (80k-200k per hole). Imported as **instances** from the
  per-prop FBX (the preferred path) that is a few dozen unique meshes. The merged `dressing_hNN_*` groups don't
  instance or cull well, so use them for quick blockouts.
- **FBX size**: `fbx/` is about 257 MB because every FBX embeds its own copy of the PNGs (about 0.3-0.7 MB each).
  Upload `textures/` once and point SurfaceAppearances at it if import size matters.
- **Preview ground only**: dressing `pos.y` follows a preview ground, not Studio Terrain, so raycast in Studio.
- **Walking paths** are straight corridors; real curved paths may need a re-run with their polylines.
- **Layout shape**: neighbouring holes compete for space (H6 has 12 trees of its own and is framed by H4/H5/H7
  dressing). Spans only fit lanes up to about 17 wide, so the wide H5/H7 greens get hooks and strings, not spans.
- **Not in the concepts' level of detail**: canopies are low-poly blobs with a leaf texture (no leaf cards), there are
  no waterfall particles or rainbow, and there are no cattails or lily pads.
- **Carried over from pass 1**: the H6 visual-rail notch, the Studio import scale check (Stud), and PointLights to add
  at `lights[]` and on the hero Glow parts.
