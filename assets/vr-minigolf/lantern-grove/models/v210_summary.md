# Lantern Grove props v210 (2026-10-12): H8 door pocket clearance + H9 timber colour

Before: `_src/manifest_before_v210.json`, `_src/fbx_before_v210/` (the 3 original FBX),
`_src/lantern_grove_props_before_v210.blend`. holes.json was only read (sha256 `6005ba1b4d1dd02f…`).
Built with Blender 5.2.2 LTS (the earlier passes used 4.5.9), with the same FBX settings: forward -Z, up Y, scale 1.0,
1 unit = 1 stud.

## Result

- **Fitcheck: ALL PASS, 42 checks.** Saved as `_src/fitcheck_v210_validated.txt`; the script is `_src/fitcheck_v210.py`.
  - The newest suite is `fitcheck.py` + `fitcheck_pass6..10.py`, not pass 9. Most of it needs `world/` and about 100
    FBX that are not in this job, so the full 235-check chain **cannot run here**. The v210 script runs the parts that
    can:
    - `fitcheck.py` sections 1-6 (18 checks);
    - pass-6 section 3 (H8 door + pockets, rings, cladding) and the tee-to-flag sightline (5 checks), unchanged code,
      in the hole-local frame;
    - 19 new v210 checks, including 3 negative tests.
  - The world keep-out checks that include the pocket were **not** re-run.
- **FBX re-import:** 7/7 FBX pass (`_src/reimport_v210.json`). Tris, bbox, part names, one material per part,
  material colour and part origins all equal the manifest. Every file is under 20k tris.

## H8 door pocket (`fbx/h8_door_pocket.fbx`, 416 tris)

- **Change:** the generator (`props_pass6.py`, `POCKET_SX/RAISE/DEEPER`) puts the whole mesh through one frame:
  - X scaled ×1.4 about the origin, which is the door centre line;
  - raised +0.17;
  - moved 0.05 deeper along local -Z, which is world +Z, the door's opening direction, so away from the door.
- **Origin and placement are unchanged** (H8 `[4.75, 0, -7.75]`, yaw 180), so only the FBX needs re-importing.
- **Verified** on the re-imported FBX: every vertex equals the old FBX under exactly this transform (max deviation
  3e-7).
  - bbox 1.45 × 2.135 × 2.663 → **2.03 × 2.135 × 2.663**;
  - centre shift (+0.002, **+0.17**, **-0.05**);
  - the walls still reach y -0.18, below the felt.
- **Door sweep:** the door is a slider (holes.json `slide`, range 0..4, axis +Z), so the "angle" is the slide offset.
  - **Min door ↔ pocket mesh clearance = 0.210 at offset 4.000** (fully open: the door end at z -5.70 against the
    back plate at z -5.49). Required: ≥ 0.187.
  - It was 0.064 before, at offset 2.546, where the side lip passed the door's root tubes.
  - Sampling: 401 offsets at 0.01, then 41 at 0.0005 around the minimum. Exact triangles with 0.005 edge sampling,
    both ways. Profile: `_src/door_pocket_sweep_v210.json`.
  - Pocket against the door's collider box: also 0.21.
  - Negative tests are flagged: the old pocket (0.064), and the pocket moved 0.05 toward the door instead of away
    (0.110).

## H9 timber (`fbx/timber_deflector_board.fbx` 400 tris, `fbx/bank_backing_stone.fbx` 940 tris)

- **New material `OakDeep`:** `#7A4E32`, Roblox WoodPlanks, **Reflectance 0**. It is in manifest `parts[].reflectance`
  and in `manifest.v210.roblox`.
  - It is untextured, so `MeshPart.Color` is exactly #7A4E32 and no SurfaceAppearance overrides it.
  - The preview material has specular 0.
- **Parts renamed:** `timber_deflector_board__Oak` → `__OakDeep` (the 3 planks), and `bank_backing_stone__Oak` →
  `__OakDeep` (the cap timber).
- **Unchanged:** the stone faces stay `bank_backing_stone__Limestone` `#B8AFA0` as their own part. The moss, root-bark
  posts/cap (#5B3A22) and iron bands are also unchanged. All geometry is identical to the old FBX (deviation 0).
- **Note: both props are shared.** The new colour applies to every placement: the timber board at H1/H6/H9 and the
  backing stone at H3/H8/H9. If only H9 should change, these would need `_h9` variants, as `h9dim` did.

## Not touched

- holes.json, rail16 and the banks.
- `h8_root_door.fbx` and the H8/H9 dressing FBX (byte-identical to the shipped files).
- The other 119 manifest prop entries (identical), and every top-level manifest block. `build_all.py` now keeps
  unknown top-level keys such as `h9_emissive_dim`, which an `--only` build used to drop.
- Sugarloaf: no changes.

## Open issue

- **rail17 overlap:** the wider pocket's west wall now reaches **0.272 studs into the rail17 collision box** (the H8
  lane east rail, x 3.5..4.0) over z -7.93..-5.27. This is a consequence of the requested ×1.4 scale.
  - It is visual only: the pocket has no collision, and it does not reach the lane felt (x < 3.5).
  - The rail-kit visual on rail17 may clip into the bark wall there. Before v210 the gap was 0.03.
  - rail16 and rail17 were left alone as instructed. If that clipping shows in Studio, either notch the rail17 visual
    as well or scale the pocket asymmetrically (+X side only).

## Changed files (in `lg_v210.tgz`)

- `fbx/h8_door_pocket.fbx`, `fbx/timber_deflector_board.fbx`, `fbx/bank_backing_stone.fbx`.
- `manifest.json`: the 3 entries rebuilt, plus a new top-level `v210` block.
- `lantern_grove_props.blend`: the 3 props replaced in place, plus the `OakDeep` material.
- `_src/props_pass6.py`, `_src/props_dressing.py`, `_src/lglib.py`, `_src/build_all.py` (generator changes).
- New in `_src/`:
  - `fitcheck_v210.py`, `fitcheck_v210.txt`, `fitcheck_v210_validated.txt`;
  - `reimport_v210.py`, `reimport_v210.json`;
  - `door_pocket_sweep_v210.json`, `previews_v210.py`;
  - backups: `manifest_before_v210.json`, `fbx_before_v210/`, `lantern_grove_props_before_v210.blend`.
- `previews/v210/`:
  - `h8_door_pocket_v210_eye.png` and `_34.png`: the pocket with the door fully open;
  - `h8_door_pocket_v210_plan.png`: a plan section clipped at y 1.12 at the minimum-clearance position;
  - `h9_timber_v210_eye.png` and `_34.png`: the deflector board and the backing stone.
- `v210_summary.md`.

**What RobloxDevBot pulls in:** re-import the 3 FBX. Keep the pocket's CFrame. Set both `__OakDeep` MeshParts to
Color `#7A4E32`, Material WoodPlanks, Reflectance 0, with no SurfaceAppearance.
