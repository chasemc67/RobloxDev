# Lantern Grove props: pass 6 summary (2026-10-10): holes.json v2 (playtest Rounds 5/6)

Brief: `_src/brief_pass6.md`. Step log: `_src/pass6_progress.md`. "Before" state: `_src/manifest_before_pass6.json`.
`holes.json`, `props.md`, the world files, `_src/fly*`, `previews/fly_frames` and `previews/flythrough_v1*` were only
read, never edited.

**Result:**
- `fitcheck.py`: **ALL PASS, 168 checks** (29 new pass-6 checks). Saved as `_src/fitcheck.txt` and
  `_src/fitcheck_pass6_validated.txt`.
- Tee and top views re-rendered for **all 9 holes** (32 spp). Flags are new on every hole, and H6's dressing changed.
- `tee_contact_sheet.png`, `contact_sheet.png`, `README.md` and `lantern_grove_props.blend` were rebuilt by a full
  `build.sh` run.

## What changed (v2 vs Round 4, from `tools/out/holes-r5-start.json` -> `holes.json`)

| Hole | holes.json v2 change | Pass-6 response |
|---|---|---|
| all | `cup.flag` (pole 7.5 / H9 8.0, 2.0 x 1.2 #e03c31 banner, `top`, `collision: false`) | `cup_flag_h01..h09` placed at the cup, banner turned to the tee |
| H1, H3, H6 | flag only | flag; dressing unchanged (H6: see Dressing) |
| H2 | chute signs + felt arrow decals | `h2_chute_sign_left/right`, `h2_chute_arrow_decal` x2 |
| H4 | spinner arms 3.8 -> 2.3 (r 0.7..3.0), 36 -> 30 deg/s; side-gap lantern anchor | `h4_carousel_bar` rebuilt (short padded arms); `h4_side_gap_post` x2 on the rail tops |
| H5 | stream `reset: respawn` at (0, 0, -13.5) | `h5_respawn_stone` flush at the respawn point |
| H7 | log travel +-6 -> +-7; gap x 3.5..7 -> 4..6.5; cup moved | log motion updated; gap lantern posts moved to x 3.75 / 6.75; more dressing |
| H8 | ring r 0.35 -> 0.55; c1 removed (everything 9 nearer the tee); `alcove_bank`; door +-2.5 -> +-3.5 into pockets; exit ring -> (9, 1.5, -47); cup -> (4, 1.5, -37) | entry ring rebuilt (1.1 glow disc, wider ring gap); exit ring moved; `h8_alcove_bank_cladding`; `h8_door_pocket` x2; door motion; c2 root arch and glow mushrooms moved; dressing re-placed |
| H9 | lantern bar + post -> `lantern_pendulum` (swing); tunnel dip; gate 0..1.2 @0.6 -> 0..1.8 @0.9; cup -> (26, -0.8, -52) | `h9_lantern_pendulum` + `h9_pendulum_root_beam`; bar + post removed; `h9_tunnel_dip_trim`; gate motion; tunnel arch lowered; heart lantern cluster raised; spot retargeted |

### Moving parts (all keep the MoveRed / MoveCream bands)
- **H9 pendulum** (`fbx/h9_lantern_pendulum.fbx`, 2,604 tris):
  - origin = hinge (22, 8.96, -38.5), axis +Z;
  - angle(t) = 35 deg x sin(360 t / 4 s + 0), peak 55 deg/s;
  - manifest `motion` = {type swing, amplitude_deg 35, period_s 4, phase 0, range [-35, 35], speed 54.98,
    course_local_pivot, axis_roblox};
  - the bob (red body, cream ribs/caps, Neon window band) fills the 1.6 x 1.8 x 1.0 blocker 7 below the hinge, 0.06
    above the felt;
  - 15 alternating red/cream chain links.
- **H4 bar**: arms 2.3 long, cushion pads and rounded tip bumpers; below y 1 everything stays inside the new blockers.
  2,314 -> 2,946 tris.
- **H7 log** +-7, **H8 door** +-3.5, **H9 gate** 0..1.8 @ 0.9: the meshes are unchanged; only the motion metadata
  changed (checked == holes.json).

### Lights
- The H9 lantern-bar spot is gone. The new `H9_lantern_pendulum_moving_part` hangs beside the hinge at local
  (22, 8.96, -36.5), 2 studs off the swing plane, outside the swept envelope.
- The H8 cup spot followed the cup to (3.29, 8.5, -36.29).
- The H8 cup lanterns (`cup_lantern_stake` x2) sit 7.5-9 studs out. The closer spots are in the world tree roots, so
  the accent search ring was widened from 7 to 9.
- The H8/H9 brightness work (bright felt, cream trim, cup/gate lanterns, spots over moving parts) is all kept.

### Other hero fixes found by the new checks
- **`heart_lantern_cluster`**: raised from y 1.0 to y 7.5. It blocked the H9 tee -> flag sightline (the line runs at
  y 6.9-7.2 over the heart).
- **`trunk_tunnel_arch`**: top lowered from about 6.1 to 5.69, so the buttress top is <= y 6 (holes.json LOS note).
- **`firefly_ring_entry`**: ring R 0.85 with a 120-degree bottom gap, and motes lifted >= 1 above the felt, so the
  0.55 trigger column is clear.

## FBX paths

**New (19 props + previews `previews/<name>_{eye,34}.png`):**
- `fbx/cup_flag_h01.fbx` ... `fbx/cup_flag_h09.fbx`
- `fbx/h2_chute_sign_left.fbx`, `fbx/h2_chute_sign_right.fbx`, `fbx/h2_chute_arrow_decal.fbx`
- `fbx/h4_side_gap_post.fbx`
- `fbx/h5_respawn_stone.fbx`
- `fbx/h8_alcove_bank_cladding.fbx`, `fbx/h8_door_pocket.fbx`
- `fbx/h9_lantern_pendulum.fbx` (MOVING), `fbx/h9_pendulum_root_beam.fbx`, `fbx/h9_tunnel_dip_trim.fbx`

**Changed (mesh and/or placement / motion):**
- Mesh: `fbx/h4_carousel_bar.fbx`, `fbx/firefly_ring_entry.fbx`, `fbx/trunk_tunnel_arch.fbx`.
- Motion only: `fbx/h7_floating_log.fbx`, `fbx/h8_root_door.fbx`, `fbx/h9_root_portcullis.fbx`.
- Placement only: `fbx/firefly_ring_exit.fbx`, `fbx/root_arch_large.fbx`, `fbx/heart_lantern_cluster.fbx`,
  `fbx/glowing_mushrooms.fbx`, `fbx/lantern_post.fbx`.
- Dressing groups: `fbx/dressing_h06_a.fbx`, `_h06_cards`, `fbx/dressing_h07_a.fbx`, `fbx/dressing_h08_a.fbx`,
  `fbx/dressing_h09_a.fbx` (content changed). Every `dressing_hNN_*` file was re-exported; H1-H5 content is identical.
- The full `build.sh` re-exported every prop FBX from the same generators (the others are unchanged).

**Removed:** `fbx/h9_lantern_bar.fbx`, `fbx/h9_lantern_post_static.fbx`, plus their 4 previews and manifest entries.

## Dressing per hole (pass 5 -> pass 6, `manifest.dressing.holes.HN.stats.pass6_vs_pass5`)

Unchanged = same prop within 0.05 studs. Moved = same prop within 12 studs. Otherwise removed. Added = new.

| Hole | Instances | 3D + cards (p6) | Unchanged | Moved | Removed | Added | Own tris p5 -> p6 | Near-field tris p5 -> p6 (<= 34,000) |
|---|---|---|---|---|---|---|---|---|
| H1 | 48 -> 48 | 27 + 21 | 48 | 0 | 0 | 0 | 16,860 -> 16,860 | 32,308 -> 32,308 |
| H2 | 42 -> 42 | 22 + 20 | 42 | 0 | 0 | 0 | 18,354 -> 18,354 | 33,998 -> 33,998 |
| H3 | 43 -> 43 | 29 + 14 | 43 | 0 | 0 | 0 | 18,920 -> 18,920 | 32,204 -> 32,204 |
| H4 | 37 -> 37 | 24 + 13 | 37 | 0 | 0 | 0 | 16,862 -> 16,862 | 33,536 -> 33,536 |
| H5 | 34 -> 34 | 27 + 7 | 34 | 0 | 0 | 0 | 19,406 -> 19,406 | 29,958 -> 27,114 |
| H6 | 25 -> 19 | 18 + 1 | 18 | 1 | 6 | 0 | 13,636 -> 10,792 | 31,392 -> 32,348 |
| H7 | 13 -> 25 | 25 + 0 | 6 | 5 | 2 | 14 | 9,002 -> 12,402 | 33,922 -> 33,954 |
| H8 | 15 -> 13 | 13 + 0 | 3 | 8 | 4 | 2 | 14,028 -> 13,504 | 33,862 -> 33,802 |
| H9 | 27 -> 26 | 26 + 0 | 20 | 2 | 5 | 4 | 17,016 -> 16,936 | 27,766 -> 27,162 |
| **Total** | 284 -> 287 | | | | | | **144,084 -> 144,036** | max **33,998** |

Notes on the table:
- **H7** (barest at 13) is now 25 instances, still within budget. H7 goes first in the seed round-robin, and 14 cheap
  low ground-cover + 3 mid props (all < 2 studs high) are placed before the seed pass.
  - H7's near field, and H8's (which covers all of H7), are shared with H6/H8/H9 dressing, so the gain costs
    something elsewhere.
  - H6 gave up 5 small ground-cover props + 1 tree (25 -> 19).
  - Two other approaches were tried and reverted (see the progress log): a 7,000-tri H7 reserve cost H6 12 props for
    +5 in H7; a 10.5k cap per foreign hole gave H7 only +1.
- **H8 / H9** changes come from the v2 geometry: the H8 felt moved under old dressing, H8's cup moved, and H9's tunnel,
  cup and pendulum changed.
- **H5**: the near-field number dropped because H6 and H8 dressing moved away. Its own dressing is unchanged.
- **Tris** of the new hero props (not dressing, not in the near-field budget, as in earlier passes): flags 1,012-1,300
  each, H2 signs 2,616 / 2,848, pendulum 2,604, beam 1,650, the rest 156-672.

## Fitcheck (ALL PASS, 168)
New pass-6 checks (`_src/fitcheck_pass6.py`, exec'd by `fitcheck.py`):
- **Removed parts**: lantern bar/post gone (manifest + FBX), and no spot light tied to them.
- **Motion data**: every holes.json v2 moving part has exactly one prop whose motion matches it (type, pivot, axis,
  speed/range, or amplitude/period/phase for the swing).
- **H7 log**: the mesh end at +-7 is 0.455 short of the rail face.
- **H9 pendulum**:
  - bob inside its blocker, chain slim, 0.06 above the felt at rest;
  - swing envelope (bob + chain, +-35 deg, grown 0.25, 142 boxes) clear of all re-imported dressing FBX and every H9
    hero prop;
  - spot light outside the envelope.
- **H8**:
  - the door never touches its pockets, and both ends slide into a pocket;
  - entry glow disc r = 0.55 and the ring gap clears the trigger;
  - exit ring at the v2 exit with the right yaw;
  - the alcove cladding is <= 0.03 above the bank plane and inside its footprint.
- **Flags**:
  - at the cup, pole top = `cup.flag.top`, pole/banner sizes, facing the tee;
  - `collision false` in the placement, holes.json and the notes;
  - a dressing keep-out exists.
- **Line of sight**: tee -> flag top is not blocked by any static hero prop on H1-H2 and H4-H9 (H3 blocked by design).
- **H9 arch**: top <= y 6.
- **Flush props**: decals <= 0.01 and the respawn stone <= 0.02 above the felt, and on the felt.
- **On / beside rails**:
  - H4 posts stand on the rail tops;
  - H2 signs are >= 0.5 from the felt and outside every wall;
  - the dip trim stays on the rail footprints;
  - the beam legs are off the felt and outside the rails;
  - the H7 gap posts sit at the v2 rail ends.
- **H7 dressing**: richer than pass 5 and within budget.
- **Pass-5 checks updated**: H4 carousel bounds use the new blockers, the H9 lantern-bar bound became a pendulum bound,
  the moving-part colour list includes the pendulum, and the cup-lantern distance limit is 9 (was 7).
- **Shared code**: `dressing_lib.sweep_vols` handles `swing`, so the keep-outs sweep the pendulum through +-35 deg.
  `world_fitcheck.py`'s negative test now uses the pendulum.

## Open issues
- **Rail kit at the H8 pockets**: in Studio, notch the visual rail kit on rail16 / rail14 over x 4.2..5.3, where the
  `h8_door_pocket`s sit. The pocket housing covers the rail section, but a rail-kit block would show inside the slot.
  The collision rails stay unchanged (holes.json).
- **H9 rails in the preview**: the preview places the 1-stud rail kit at the collision wall's top - 1. The tunnel dip
  trim assumes the Studio rail kit sits at the corridor felt height (1.0), per the rail-kit note. If RobloxDevBot
  places the tunnel rails differently, the trim's top (y 1.0) should follow the rail-kit bottom.
- **H6 is thinner** (19 instances, 18 3D) after giving H7 room in the shared near fields. It is still more than H7 had
  in pass 5. If H6 reads bare, the next lever is cheaper H9 interior props (glowing_mushrooms are 2,040 tris each and
  sit in H8's window).
- **The pendulum light moves**: the Neon window band is the light source, so parent its PointLight to the moving bob.
  The static spot beside the hinge stays put.
- **H8 cup lanterns are 7.5-9 studs from the cup** (not <= 7 as in pass 5); the closer ground is world tree roots.
- **Light units**: preview spot watts vs Roblox Brightness are unchanged from pass 5. Tune at night in Studio.
- **Pass-2 overviews**: `assembly_hNN.png` (old pass-2 overviews) are still stale, as before.
