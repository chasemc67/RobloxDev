# Lobby far-backdrop zones: LG2 / SL1 / AU2 (pass 2)

Built 2026-10-12 in Blender 5.2 on the Windows PC with explicit headless bpy (`_src/build_backdrops.py`, run by `_src/run.ps1` from a one-off schtasks task). No Claude Code was used. Pass 1 is backed up in `_backup_pass1/`.

Pass 2 applies Game Art Bot's five fixes:
1. The zones sit on the horizon, directly behind their own portals and scaled up.
2. Only a light tint is baked in.
3. LG2 has an umbrella canopy and 10 lanterns.
4. SL1 has flat-topped mesas, a thick cable and a big car.
5. AU2 is bright, with frozen falls and a hero ice spire.

## SL1 pass 3
SL1 was rebuilt with true mesas: flared talus bases, tapered uneven sides and flat green tops. The strata stripes are uneven and tilt with the slope. The tall hero mesa sits off-centre on the right. The pale cascade falls down the hero mesa's west-front flank, clear of the portal pillar from the boardwalk. The gondola, cable, pylons, placement and root are unchanged. The `SL1_mesa_tops` mesh is gone; the tops are now part of `SL1_mesas`. Comparison image: `previews/SL1_concept_vs_build.jpg`.

## Files
- `fbx/bd_lg2_lantern_grove.fbx`: 8,072 tris, 7 meshes, about 256×234×213 studs
- `fbx/bd_sl1_sugarloaf_canyon.fbx`: 11,042 tris, 7 meshes, about 647×282×395 studs (pass 3, includes the shore ring). Pass 2 SL1 is in `_backup_pass2/`.
- `fbx/bd_au2_aurora_archipelago.fbx`: 4,040 tris, 9 meshes, about 397×282×150 studs
- `manifest.json`: per-mesh tris and bboxes, placement CFrames with yaw, offsets from the arches, Neon parts, motion data
- Previews:
  - `previews/{LG2,SL1,AU2}_boardwalk_eye.png`: from spawn eye height (100,5,100), looking through each portal, with 36-40° lenses
  - `previews/all_zones_from_spawn.png`: 100° wide shot from spawn
  - `previews/concept_vs_build.jpg`: concept on the left, build on the right

## Placement
Each zone sits on the sightline from spawn through its arch centre, 820-860 studs from spawn. That's about 750-800 studs past the portal row, with about 260-500 studs of open sea between neighbouring zones. Local +Z faces spawn after the yaw.

| zone | CFrame |
|---|---|
| LG2 | `CFrame.new(-415.7, -4, -537.6) * CFrame.Angles(0, math.rad(38.97), 0)` |
| SL1 | `CFrame.new(225.1, -4, -750.8) * CFrame.Angles(0, math.rad(-8.36), 0)` |
| AU2 | `CFrame.new(707.5, -4, -450.8) * CFrame.Angles(0, math.rad(-47.8), 0)` |

Scale is baked into the meshes (×3.2 / ×3.0 / ×3.2), so import at scale 1.0. Axes are -Z forward and Y up, with transforms baked; this matches boardwalk/models. The sea plane and Atmosphere need to reach about 1000 studs.

## Import (RobloxDevBot)
- **One Model per zone.** The PrimaryPart is `<zone>_root` (`LG2_root`/`SL1_root`/`AU2_root`), a 1×1×1 cube centred on the base-centre pivot. Set its Transparency to 1. ModelStreamingMode is Persistent, which RobloxDevBot sets.
- Every MeshPart is Anchored, with CanCollide, CanQuery and CanTouch all false. There are no collision meshes. Nothing is near the portal clearance zones.
- **Haze:** only a light sky tint is baked in, up to 10% toward #F2A57E above world Y 30. The lobby Atmosphere provides the real haze, so don't stack more.
- `BD_VC` meshes use vertex colour only: SmoothPlastic, Color white.
- Neon meshes:
  - `LG2_lanterns_neon` #FFC867, 10 lanterns. Good PointLight hosts.
  - `SL1_crystals_neon` #F59AC8
  - `AU2_crystals_{main,left,right}_neon` #9FE6F2. These include the hero spire and the frozen falls, which are tinted pale blue #BFEFFF in the preview.
  - `AU2_crystals_amethyst_neon` #B07CF0
  - If the frozen falls glow too hard in Neon, switch them to Glass or SmoothPlastic #BFEFFF.
- Motion:
  - SL1: tween `SL1_gondola_cabin` (8×6×6 before scaling, so about 24×18×18 studs) along the cable. The endpoints are in the manifest, before scaling.
  - AU2: bob each `AU2_island_<n>` together with its `AU2_crystals_<n>_neon`.

## SL1 pass 4: backdrop spires pass (2026-10-13, review candidate)
Pass 3 is unchanged and still the approved import (`fbx/bd_sl1_sugarloaf_canyon.fbx`, `manifest.json`, `previews/`). Pass 4 is separate:
- `fbx_pass4/bd_sl1_sugarloaf_canyon_pass4.fbx`: 14,126 tris (pass 3 had 11,042; budget 15k). Meshes: SL1_mesas 10,208, new SL1_spires 3,160, shore 284, pylons 76, cascade 98, cabin 48, crystals_neon 240, root 12.
- `manifest_sl1_pass4.json`: same schema; placement CFrame, scale, motion endpoints, neon and pylon tops are identical to pass 3. Far scenery: CanCollide/CanQuery/CanTouch off, Persistent.
- Changes: gentle vertex wobble on the mesa tops and rim outline (zeroed around the two gondola pylons); thin darker rims along the strata band edges and under the top lip; 5 slender striped spires among and behind the mesas, all over 110 studs from the cable corridor.
- `fitcheck_sl1_pass4.txt` (all_pass), `_src/reimport_sl1_pass4.json` (all_pass), previews and silhouettes in `previews_pass4/`, sheet `previews_pass4/sheet_sl1_pass4_before_after.png`.
- Source: `_src/build_sl1_pass4.py`, `_src/run_sl1p4.ps1`, `_src/sl1_pass4_summary.md`. The pre-pass-4 backup is in `_backup_pass4_pre_20261013_1718/`.

## SL1 pass 5 (2026-10-13, Game Art Bot decision: lobby backdrop only)
Built from pass 4 with the 5 spires removed. It keeps the mesa-top wobble, the darker stripe rims and the red/cream strata; SL1_mesas is the same 10,208 tris as pass 4. The course far spires are untouched. Pass 3 (approved) and pass 4 are unchanged.
- `fbx_pass5/bd_sl1_sugarloaf_canyon_pass5.fbx`: 10,966 tris (mesas 10,208, shore 284, crystals_neon 240, cascade 98, pylons 76, cabin 48, root 12)
- `manifest_sl1_pass5.json`: placement, scale, motion, neon and pylon tops identical to pass 3. Collision, query and touch off.
- `fitcheck_sl1_pass5.txt` all_pass, `_src/reimport_sl1_pass5.json` all_pass
- Preview `previews_pass5/sl1_pass5_boardwalk_eye.png` (eye (100,5,100) through the SL1 portal)
- Source `_src/build_sl1_pass5.py`, `_src/run_sl1p5.ps1`
