# Lantern Grove v210b (2026-10-12): bank backings as stone, duplicate oak faces removed, H9 oak rails, H9 bank lip

Two requests are combined here: Playtest Bot round 8 (H3/H8/H9 bank backings) and the H9 review from Game Art Bot,
which takes precedence for the H9 rails.

The starting point is the Job 1 (v210) state, restored fresh from `lg_v210.tgz`, plus the 3 FBX from `lgfbx2.tgz`.

Backups:
- `_src/manifest_before_v210b.json`;
- `_src/fbx_before_v210b/`: `bank_backing_stone`, `h8_alcove_bank_cladding`, `dressing_h03_a` and `dressing_h08_a`, i.e. every FBX that changed;
- `_src/lantern_grove_props_before_v210b.blend`.

Everything was built in headless Blender 5.2.2 LTS, one instance at a time, with the same FBX settings as before
(forward -Z, up Y, scale 1).

`holes.json` was read only (sha256 `6005ba1b4d1dd02f`, the same as for v210). rail16, the banks and mover speeds were not touched.

## Results

- **Fitcheck: ALL PASS, 59 checks.** Saved as `_src/fitcheck_v210b_validated.txt` (script `_src/fitcheck_v210b.py`).
  - It re-runs the latest suite unchanged: v210 sections A and B, plus C1-C2 (H8 door pocket, still 0.210 clearance).
  - Section D adds the v210b rules. There are 5 negative tests in total: 3 new ones in D, 2 from v210 C2.
  - v210 C3/C4 are replaced by D, because the backing cap is no longer OakDeep.
  - The same input limits as v210 apply: no `world/`, and about 100 FBX are not in this job.
- **Re-import:** 14/14 FBX in `fbx/` pass (`_src/reimport_v210b.json`). Tris, bbox, parts, one material per part, colour and per-part tris all equal the manifest (props and dressing `fbx[]`). Every file is under 20k tris. The lip has emission 0.
- **Coplanar-overlap (z-fight) check:** `_src/coplanar_v210b.py`, full results in `_src/coplanar_v210b.json`.
  - A z-fight here means two triangles that overlap with area > 1e-5, are coplanar within 0.006, face the same way, and belong to different pieces.

| file | before | after | |
|---|---|---|---|
| bank_backing_stone.fbx | 0 | 0 | changed |
| h8_alcove_bank_cladding.fbx | 6 | 0 | changed |
| dressing_h03_a.fbx | 8 | 0 | changed |
| dressing_h08_a.fbx | 8 | 0 | changed |
| rail_straight_4_h9 / rail_straight_2_h9 / rail_end_post_h9 / h9_bank_lip | – | 0 | new |
| dressing_h09_a, dressing_h09_a_h9dim, h8_root_door, stream_bank_rocks | 0 | 0 | unchanged (byte-identical) |
| h8_door_pocket.fbx | 12 | 12 | unchanged: RootBark/RootBark only, not oak/stone (Job 1 pocket) |
| timber_deflector_board.fbx | 32 | 32 | unchanged: RootBark/RootBark only (Job 1 result kept as asked) |

- **Assembled hole-local check (D7)** for all 5 backings, against the rail kit modelled from holes.json with both documented height rules:
  - **0** coplanar faces between a backing or the lip and any rail piece.
  - Backing stone lying under its own oak cap (within 0.01): **35.63 → 0 stud²**.
  - If a rail kit is laid on a `*_backing` wall line, its cap no longer z-fights with the backing cap: **12 → 0** pairs per backing.

## Changes, exactly

### fbx/bank_backing_stone.fbx
Shared by H3 bank1/bank2, H8 bank1/bank2 and H9 bank1. Source: `_src/props_dressing.py`, `bank_backing()`.

1. **Cap recoloured to stone.** Object `bank_backing_stone__OakDeep` (44 tris, #7A4E32) → stone #B8AFA0 (Limestone), merged into `bank_backing_stone__Limestone`. The `__OakDeep` part no longer exists.
2. **Cap enlarged by +0.02 outward** around the rail-kit cap envelope: 0.58 × 0.27 × 12.19 (y 1.935..2.205) → **0.60 × 0.32 × 12.2324 (y 1.90..2.22)**.
   - Per side, that is x ±0.29 → ±0.30, bottom −0.035, top +0.015, each end +0.021.
   - The cap now encloses, by exactly 0.02 on every side, the cap that a rail kit laid on the same wall line would have (RAIL_NOTE: base = bank top 1.2, 0.56 × 0.28, length 12.1924). Before, that rail cap's top sat 0.005 under the oak cap top: the duplicate oak cap.
3. **Removed `bank_backing_stone__Moss`** (60 tris, 3 moss tufts).
   - All 36 of its vertices were inside the old cap, so the removal changes no visible pixel.
   - It leaves the backing as one stone part.
4. **Stone blocks unchanged.** Every old `__Limestone` vertex is still present (dev 0).
   - The felt-facing faces stay at x ±0.24, 0.01 behind the felt edge.
   - They could not be enlarged: the felt is on −X for H3 bank1/H8/H9 but on +X for H3 bank2, the H9 lip needs that 0.01, and the ball radius is 0.08.
5. Result: **940 → 880 tris**, one part `bank_backing_stone__Limestone` (836 block + 44 cap tris), bbox 0.58 × 2.185 × 12.19 → 0.60 × 2.20 × 12.232.
6. **Placement fix (manifest):** H8 `bank2_backing` pos z **−49.7753 → −40.7753**.
   - The old position was 9 studs off its holes.json wall (−40.7753), so the H8 bank2 backing had no visible stone at all.
   - All 5 placements now sit on their `*_backing` walls (D2, with a negative test).

### fbx/h8_alcove_bank_cladding.fbx (H8)
Source: `_src/props_pass6.py`, `alcove_cladding()`.

1. **Recoloured** `h8_alcove_bank_cladding__RootBark` (296 tris, #5B3A22) → `h8_alcove_bank_cladding__Limestone` (#B8AFA0, Limestone). Geometry is identical, every vertex (dev 0).
2. **Removed `h8_alcove_bank_cladding__Moss`** (60 tris, 5 flush moss-streak boxes).
   - These were not stone.
   - They contained all 6 coplanar overlap pairs: moss streaks overlapping each other.
3. Result: **356 → 296 tris**. The pass-6 rule (lies on the banked plane, ≤ 0.03 above it) still passes, at 0.02.

### fbx/dressing_h03_a.fbx (H3 near-field dressing)
Removed 4 faces (4 quads = **8 tris**) from `dressing_h03_a__Oak` (176 → 168).
- Each is a 0.26 × 0.26 down-facing lantern-pole oak post bottom lying on its slate footing's bottom face: oak/stone coplanar overlap, the duplicate.
- Locations (hole-local):
  - (−10.0, −0.45, −4.5) and (10.0, −0.45, −4.5): lantern_span_20;
  - (7.482, −0.481, −21.712) and (7.482, −0.481, −31.712): lantern_string_poles.
- Every other polygon, UV, loop order, material, embedded image and transform is identical to the shipped file (`_src/dedupe_v210b.py`, `_src/dedupe_v210b.json`).
- There is no bank-backing geometry in `dressing_h03_a`: the H3 backings are `bank_backing_stone` placements.

### fbx/dressing_h08_a.fbx (H8 near-field dressing)
Removed 4 faces (**8 tris**) from `dressing_h08_a__Oak` (864 → 856), the same lantern-pole duplicate.
- Locations (hole-local):
  - (−8.491, 0.435, −54.092) and (11.509, 0.435, −54.092): lantern_span_20;
  - (−5.363, 2.649, −59.863) and (4.637, 2.649, −59.863): lantern_string_poles.
- Everything else is identical.

### New FBX: H9 rails (game-art review)
Source: `_src/props_dressing.py`, `RAIL_VARIANTS["h9"]`.
- `fbx/rail_straight_4_h9.fbx` (132 tris) and `fbx/rail_straight_2_h9.fbx` (88 tris):
  - rail tops and faces form one part `__OakDeep`, **#7A4E32, WoodPlanks, Reflectance 0**, untextured;
  - the geometry is the same as the trim kit's.
- `fbx/rail_end_post_h9.fbx` (116 tris): one part `__Limestone` #B8AFA0 (block, cap, knob). On the H9 rails, limestone is now only on the posts; the other H9 limestone is the bank backing.
- `hole_skins.H9`: `rail_*_trim` → `rail_*_h9`, with `rail_block` and `rail_cap` OakDeep (Reflectance 0) and the new `rail_post` Limestone. The H9 felt (FeltBright) is unchanged.
- `rail_*_trim` holes `["H8","H9"]` → `["H8"]` (manifest holes/notes only; their FBX are unchanged).

### New FBX: fbx/h9_bank_lip.fbx (H9)
Source: `_src/props_v210b.py`.
- One part `h9_bank_lip__BankLip` (12 tris): a new material `BankLip` **#6CC79F, SmoothPlastic**, emission 0 (not Neon), with no light.
- Visual only: CanCollide/CanQuery/CanTouch off.
- Section 0.05 × 0.05 along the top (high) edge of H9 bank1, the only H9 bank.
- Placed at the `bank1_backing` pos/yaw (−1.2753, 1.0, −26.7753), yaw 135.
  - Backing-local x −0.249..−0.199, y 1.20..1.25 (hole-local y 2.20..2.25 = the bank top edge).
  - Length 6.689: it stops where it would enter the rail5 / rail4 wall boxes.
- Fitcheck (D5):
  - every vertex and 0.01 surface sample (6936 points) lies inside the bank1_backing wall footprint, 0.001 behind the felt's high edge;
  - it is on no playable felt (felt rects minus walls minus the area behind backings) and in no rail wall;
  - it stands 0.009 proud of the stone face, so it shows (see `previews/v210b/h9_bank_lip_v210b_closeup.png`);
  - negative test: moved 0.01 toward the felt, it is flagged.

### Other source / data changes
- `_src/lglib.py`: new material `BankLip`; the `OakDeep` note updated.
- `_src/build_all.py`: imports `props_v210b`.
- `_src/hole_skins.py`: H9 skin as above; `rail_post` colour and `*_reflectance` are written to `manifest.hole_skins`; a note added that rail kits go on rail walls only, never on `*_backing` walls.
- `manifest.json`:
  - the 2 entries above rebuilt;
  - 4 new entries;
  - trim holes/notes updated;
  - `hole_skins.H9` updated;
  - `textures.untextured` + BankLip;
  - `dressing.holes.H3/H8.fbx[]` triangle and Oak part counts (18752 → 18744, 14580 → 14572). The hole-level dressing budget `triangles`/`stats` were not re-summed (−8 tris each);
  - `previews` of the 6 props now point to `previews/v210b/`;
  - new top-level `v210b` block with the Studio steps; it supersedes `v210.roblox["bank_backing_stone__OakDeep"]`.
  - The other 117 prop entries and the other top-level blocks are identical.
- `lantern_grove_props.blend`: `bank_backing_stone` and `h8_alcove_bank_cladding` replaced in place; `rail_straight_4_h9`, `rail_straight_2_h9`, `rail_end_post_h9` and `h9_bank_lip` added in a new row.
- New scripts in `_src/`:
  - `fitcheck_v210b.py`, `reimport_v210b.py`;
  - `coplanar_v210b.py`, `bankfit_v210b.py`, `dedupe_v210b.py`;
  - `previews_v210b.py`, `update_blend_v210b.py`, `manifest_v210b.py`.
- Previews in `previews/v210b/` (29 PNG):
  - eye + 3/4 of each changed or new prop;
  - in-hole context, before and after (eye + 3/4): `h9_bank_corner`, `h3_bank1_corner`, `h8_alcove`;
  - the lip close-up;
  - `h3_pole_footing`: eye + 3/4, plus the underside before/after showing the removed oak duplicate.

## What RobloxDevBot does in Studio (also in `manifest.v210b.roblox`)
1. Re-import `bank_backing_stone`, `h8_alcove_bank_cladding`, `dressing_h03_a` and `dressing_h08_a`.
   - Delete the old `bank_backing_stone__OakDeep`, `bank_backing_stone__Moss`, `h8_alcove_bank_cladding__RootBark` and `h8_alcove_bank_cladding__Moss` MeshParts.
   - Set the stone parts to #B8AFA0 Limestone.
2. Move the H8 bank2 backing to hole-local (−17.7753, 1.5, −40.7753).
3. **Delete any rail-kit piece or end post standing on a `*_backing` wall** (H3 bank1/2, H8 bank1/2, H9 bank1).
   - The backing is their visual; a rail kit there is the duplicate cap.
   - Its 0.48 blocks would still coincide with the backing's felt-facing faces: 144 coplanar pairs per backing remain in that misuse case.
   - At H9 that would be 8.8 stud² of stone covered by oak; it cannot be fixed from the prop side without the stone overhanging the felt.
4. On H9, swap every `rail_*_trim` for `rail_*_h9` (OakDeep #7A4E32, WoodPlanks, Reflectance 0, no SurfaceAppearance), and posts for `rail_end_post_h9`. H8 keeps the trim kit.
5. Add `h9_bank_lip`: #6CC79F, SmoothPlastic, CanCollide/CanQuery/CanTouch false, no light. No mover speed changes.

## Notes / not changed
- **Rails crossing the backings.** Where rails cross a backing at 45° (H3 rail3/4/11/12 oak caps, H9 rail4/5 now oak), the rail passes through the stone at a T-junction. That is reported as a NOTE (1.1–2.5 stud² footprint per backing); it is not coplanar and not hidden stone.
- **`drop_face_stone` at H9** (heart-well drop) still has Limestone. It is not a rail or bank piece, so I read "limestone only on H9 posts + backing" as being about the rails. Say if it should change too.
- **The lantern-pole generator** (`props_variants.pole()`) still starts the oak post at the footing bottom. The same hidden duplicate exists in the other `lantern_span_*` / `lantern_string_poles` FBX and in the H1/H2/H4-H7 dressing, none of which are in this job. Only the H3/H8 dressing FBX were edited.
- **Untouched:**
  - holes.json, rail16, the banks and mover speeds;
  - h8_door_pocket and h8_root_door;
  - timber_deflector_board (the v210 OakDeep result is kept; its RootBark posts and cap are unchanged);
  - dressing_h09_a (no rails or backing in it; 0 overlaps), dressing_h09_a_h9dim;
  - stream_bank_rocks (H5-H7 stream bank, not a backing; 0 overlaps, shipped unchanged);
  - Sugarloaf.
- **Job 1 open issue** (the H8 door pocket overlaps the rail17 box by 0.272, visual only) is unchanged.
