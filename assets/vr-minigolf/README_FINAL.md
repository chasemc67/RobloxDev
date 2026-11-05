# VR Mini Golf: final 3D assets guide (written 2026-10-14, before Chase's review pause)

One combined guide for all four areas. Paths are relative to each course's `models/` folder unless stated otherwise. Nothing was moved or deleted to write this guide. "Approved" means approved in the review threads, PROGRESS.md or manifests. Anything not confirmed there is marked **unconfirmed**.

## Anti-flashing (z-fight) rules, which apply to every FBX here
- Separate parts must be at least **0.08** apart (built at 0.086). Pieces must not intersect, touch or stack.
- Every part must be at least **0.2** thick (built at 0.206), measured as the smallest extent of its oriented box.
- **No coplanar faces** between parts, or against ground tiles. Pieces resting on the ground are sunk at least 0.1 below it instead of sitting flush.
- **Felt clearance at least 0.15** (sometimes built at 0.156–0.167) and **rail clearance at least 0.30**, measured against the holes.json solids. Dressing must never sit on the felt and must stay at least 1 stud from rails in plan view (Game Art Bot rule, v49).
- At most 3k triangles per mesh (fixed exceptions are noted in the manifests). Decoration has CanCollide, CanQuery and CanTouch off.
- A revision always goes into a **new folder** with its own manifest, fitcheck and preview or silhouette sheet. Approved files are never overwritten.
- Checks are run on the re-imported FBX: Blender 5.2 on the PC, with the triangle counts compared against the build.

## `_polish` folders (Aurora only)
`aurora-archipelago/models/fbx/props_batch1_polish/` and `props_batch3_polish/` hold the polish variants. Their manifests are `props_batch1_polish_manifest.json` and `props_batch3_polish_manifest.json`, with fitchecks in `fitcheck_*_polish.txt`. They use the same anchors, pivots and clearances as the approved originals in `props_batch1/` and `props_batch3/`, which are kept byte for byte.
- The whole polish set was approved by Game Art Bot on 2026-10-13 at 5:08 PM: corals, lanterns, buoys, palms, snowpuffs and the H4 ice bank (ice channel edge).
- Aurora's live build is still v13. The `props_fix_overlap*` fixes, including `props_fix_overlap4/` h18_ramp_lanterns, go into the next Aurora pass.

No other course has `_polish` folders.

---
## Sugarloaf Canyon (`sugarloaf-canyon/models/`)
Builds are named by the Studio attributes SC6/SC7/SC8/SC9. The current build is **sc9**: Playtest v63 shows `SC9Layout = look7_dressing/layout_look7_dressing_v49fix_thin60.json` and an `SC9LODKit` of `*_lod` meshes.

### Final and approved
| Folder or file | What it is | Used by |
|---|---|---|
| `fbx/*.fbx` (top level) | Pass-1 to pass-3 world kit: cliff, cliffT, slot and slotT kit; hero pieces; buildings; cards; sky. Used wherever no fix folder replaces a piece | all builds |
| `fbx/fix_zfight/` (275 FBX), `fix_zfight2/` (h11_lock_gate) | Anti-flash rebuilds of the v21 scan assets | SC6 and later |
| `fbx/fix_zfight3/` (188 tiles) | Heightfield ground tiles; replaced by fit030 for grounds | superseded (see below) |
| `fbx/fix_zfight4/` | rim_silhouette, with the full wavy top | SC6 and later |
| `fbx/fit030/` (191 ground tiles and 4 dress_props) | Ground tiles and dress_props refit to 0.30 rail clearance | SC7 and later |
| `fbx/look7_dressing/` | 13 rule-fixed `_v2` dressing props, plus the layouts | SC7 and later |
| `fbx/look7_dressing/layout_look7_dressing_v49fix_thin60.json` | **Final layout** (1,281 instances): the v49 fixes plus 112 far pieces thinned out | **sc9** |
| `fbx/look7_dressing/layout_look7_dressing_v49fix.json` | v49 fixes before thinning (1,393 instances) | input to thin60 |
| `fbx/look7_dressing_lod/` | 9 low-detail `*_v2_lod` meshes, with manifest and silhouettes | **sc9** (SC9LODKit). sc10 switches pieces within 15 studs of the felt back to full detail |
| `fbx/placeholders_ph1/` (13 FBX) | Real meshes for decoration-anchor placeholders | SC6 and later |
| `fbx/placeholders_ph2/tunnel_lanterns_post2.fbx` | Tunnel lantern on a post, 0.1 into the ground (approved) | latest |
| `fbx/fix_v42_item5b/`, `fix_v42_item5c/` (`h03_dress_props.fbx`) | 5b: H3 slabs planted (approved). 5c: off-tile props moved onto tiles (5c builds on 5b) | latest |
| `fbx/h16_rim_2slot_d/` | **H16 sinkhole rim, final**: 12 crystals (CrystalPink and CrystalAmber Neon), frame GeodeRim Rock #C8463F | **sc10** (approved 3:05 PM 2026-10-14). sc9/v63 still has the old Neon pink frame |
| `fbx/movers/`, `gondola/`, `lift_cage/`, `mine_head/`, `props_batch1-4/`, `props_h09h14/`, `scatter/` | Movers and per-hole props from the earlier passes (see `_src/movers/PROGRESS.md` and the batch manifests). The fix_zfight versions win wherever the same name exists | all builds |
| `fbx/cliff_fillers/` | Filler rocks used only by edgefix4. Not used in v49fix (they were buried under the terrain) | none now |
| `previews/hero/V1-hub-tee1_final.png` | Final hero render (look10 with the lift tower hidden) | marketing |

### Superseded or rejected (kept, do not import)
- **H16 rim:**
  - `fbx/h16_rim_2slot/`: crystals too thin and touching the felt.
  - `fbx/h16_rim_2slot_b/`: replaced by 2slot_d. The crystals poked above the ball plane.
  - `fbx/h16_rim_2slot_c/`: rejected because the crystals were hidden under the deck.
  - The rim versions in `fix_zfight5/` (round lip) and `fix_zfight6/` (square frame) are earlier frame-only versions; 2slot_d keeps the zfight6 frame.
- **Look7 layouts:** `layout_look7_dressing.json` and `_edgefix.json` through `_edgefix4.json`. edgefix4 was the SC7 layout and is replaced by v49fix_thin60.
- **Other files:**
  - `fbx/fix_v42_item5/` was replaced by 5b.
  - `placeholders_ph1/tunnel_lanterns.fbx`, `placeholders_ph2/tunnel_lanterns.fbx` and `tunnel_lanterns_post.fbx` were replaced by `tunnel_lanterns_post2.fbx`.
  - The `fix_zfight3` ground tiles were replaced by `fit030`.
- **Hero renders:** the look7 to look10 renders in `previews/hero/` are drafts.

### Open items at pause
- Triangle target (Game Art Bot, 3:56 PM 2026-10-14): 0.9M or less within 500 studs of the H1 tee. sc9 **passes**: 0.66M by RobloxDevBot's mesh-data sum, 470k by Playtest Bot's render stats.
- v63 P3 (LOD pieces next to the felt): **handled in sc10**.
- H16 rim 2slot_d, with the frame as Rock #C8463F: **brought in by sc10**.

---
## Aurora Archipelago (`aurora-archipelago/models/`)
| Folder | Status |
|---|---|
| `fbx/props_batch1/`, `props_batch2/`, `props_batch3/` | Approved base sets (pre-polish, kept byte for byte) |
| `fbx/props_batch1_polish/`, `props_batch3_polish/` | See the `_polish` section above |
| `fbx/props_fix_overlap/` (12 FBX) | Overlap and flashing fixes. They replace the same-named batch files (lintels, rookery, respawn stone, bobsled hut, snow walls, falls, lip ice, crystal chute) |
| `fbx/props_fix_overlap2/` | h18_crystal_bank_ne/sw_deco. Replace the batch3 versions |
| `fbx/props_fix_overlap3/` | h07_mogul_trim. Replaces the batch1 version |
| `fbx/props_fix_overlap4/` | h18_ramp_lanterns, with the cage as bars. Replaces batch3, polish and fix_overlap |
| `models/props/` (P1 placeholders), `_props_pre*` | Superseded backups. Do not import |

Rule of thumb: the newest fix folder that contains a name wins, then the polish version (if approved), then the batch version. Aurora is at v13. The polish and overlap fixes go into the next Aurora pass.

---
## Lantern Grove (`lantern-grove/models/`)
| Folder | Status |
|---|---|
| `fbx/*.fbx` (top level, passes 1–10b) | Approved props. H9 uses the `*_h9dim` variants |
| `fbx/fix_zfight/` | gold_leaf_bush, grass_tuft, the h9 pendulum and its h9dim variant, and lantern_span_20 (anti-flash rebuilds). Its h5_respawn_stone is superseded |
| `fbx/fix_zfight2/`, `fix_zfight3/` | h5_respawn_stone attempts. fix_zfight (0.64 tall) was rejected. fix_zfight2 and fix_zfight3 were superseded by fix_zfight4 |
| `fbx/fix_zfight4/h5_respawn_stone.fbx` | Latest H5 respawn stone: one flat disc mesh with 3 slots, 384 tris. Approval is **unconfirmed** in the notes |

---
## Lobby (`lobby/`, there is no `models/` folder)
- `backdrops/fbx/`: LG2, SL1 and AU2 far backdrops.
  - SL1 pass 3 is the approved import.
  - Pass 4 (`fbx_pass4/`, spires) was a review candidate.
  - Pass 5 (`fbx_pass5/`, spires removed) is **approved** (Game Art Bot, 2026-10-13 8:01 PM).
- `boardwalk/models/`: portal arches, lantern sets and the apron (pass 2 and later; the latest pass is in its README). `kit/`: 21 decoration assets. Backups are in `_backup_pass*/` (do not import).

---
## Findings checked for this guide
- **H15 seam wedge mesh:** never made or approved. "H15 wedge" in the playtests (sc-fix2, v21) is a **ball-physics wedge**: the ball got stuck 1 time in 40 at the dune rail seam (`h15-fuzz-18`, around -313.7, 146.7). No FBX named seam or wedge exists anywhere under assets. The offline tile seam check (`playtest-bot/sugarloaf-grounds-seams/`) shows the h15_ground tiles PASS with 0 gaps and 0 coplanar faces. H15 dune or rail work went into fix_zfight (h15_sugar_dune) and ground tiles, not a wedge mesh.
- **97 Sugarloaf placeholders:** **not confirmed as all replaced.**
  - v21 and sc-fix2 counted 97 visible Placeholder parts. sc-v23 counted 65 (32 replaced), with per-hole counts by hole 5,9,6,0,1,3,13,1,0,8,3,7,7,0,0,0,0,2.
  - Later, 13 placeholder meshes were built (`placeholders_ph1`), and the tunnel lanterns were moved into `placeholders_ph2`. A decal was only *suggested* for plank_respawn_stone.
  - The playtests after v23 (v42, v49, v57, v63) did not re-count visible placeholders; they only note the old Placeholder parts on rebuilt items are Transparency 1.
  - So the zero-placeholder gate has not been re-verified. A Studio re-count is needed.
