# Lantern Grove props: pass 7 summary (2026-10-10): legible flags, H8 Firefly Hollow, darker felt with a stronger nap

Brief: `_src/brief_pass7.md`. Step log: `_src/pass7_progress.md`. "Before" state: `_src/manifest_before_pass7.json`.
`../holes.json`, `props.md`, the world files, `_src/fly*`, `previews/fly_frames` and `/workspace/fly/` were only read,
never edited.

**Result:**
- `fitcheck.py`: **ALL PASS, 175 checks** (168 in pass 6 + 7 new). Saved as `_src/fitcheck.txt` and
  `_src/fitcheck_pass7_validated.txt`.
- A full `build.sh` ran: 118 props, previews, `manifest.json`, `lantern_grove_props.blend`, dressing, fitcheck,
  README and contact sheets.
- Tee and top views were re-rendered for all 9 holes at 32 spp; H8 and H9 were rendered again after the cup-spot fix.
- `tee_contact_sheet.png` was rebuilt with a pass-7 title.

## 1. Cup flags (`cup_flag_h01..h09`, generator `_src/props_pass6.py`)

| | Pass 6 | Pass 7 |
|---|---|---|
| Pole | 0.15 dia, cream, 3 red bands | **0.30** dia, cream with red bands every 0.84 (up to 0.48 under the pennant) |
| Banner | 2.0 x 1.2 rectangle | **3.2 x 2.0 tapered pennant** (tip 1.1 tall), slight wave |
| Markings | small cream number, lantern emblem, gold bars | **cream hoist band + cream top/bottom borders + 1.45-stud cream hole number** on both faces |
| Extras | lantern finial at the free corner | gold tie rings at the pole; no finial or emblem (they were clutter at distance) |
| Pole top | gold knob at `cup.flag.top` | unchanged: knob centre = holes.json `cup.flag.top` (checked <= 0.06) |
| Collision | none | none (CanCollide / CanTouch / CanQuery = false, notes say NO COLLISION) |
| Tris | 1,012-1,300 | 940-1,228 |

- The sizes are constants in `props_pass6.py`: `FLAG_POLE_D`, `FLAG_BANNER`, `FLAG_TIP_H`, `FLAG_TOP_GAP`.
- holes.json still lists 0.15 / 2.0 x 1.2. The flag check now treats those as minimums.

**Fitcheck flag checks** (`fitcheck_pass6.py`), updated for the new sizes:
- The pole radius must equal `FLAG_POLE_D`/2.
- The pennant must be 3.2 x 2.0 (measured on the FlagRed geometry above the pole bands), and both sizes must be >= the
  holes.json minimums.
- The pennant must sit under the pole top.
- The knob is found as the highest CapGold cluster (the tie rings are excluded).

**Line-of-sight checks:**
- Kept: tee eye (+5.5) -> flag top, not blocked by any hero prop on H1-H2 and H4-H9 (H3 is blocked by design).
- New: tee eye -> **pennant centre** on the same holes. PASS; H3 is blocked by `mushroom_house_large_tunnel`, by design.
- New: the H8/H9 cup-pool spot lights are >= 1.5 from the pennant (H8 2.10, H9 2.22). See the render note below.

**Legibility in the tee renders:**
- The pennant and number read clearly on H1 ("1"), H2, H4, H5, H7, H8 ("8") and H9 (red/cream pennant at the heart;
  its lower edge is partly behind the tunnel arch rib).
- H3 is hidden by design (stem house).
- H6: in this tee framing the flag is behind the millwheel. Its sightline is clear of static props (holes.json: the
  wheel crosses it 44% of the cycle).

**Render iteration (spot light):** in iteration 1 the H9 pennant was blown out by the H9 cup-pool PointLight, which
hung about 1 stud from it.
- `dressing_world.py` now hangs each cup spot 2 studs from the pole on the side away from the pennant, 7 above the cup.
- New positions: H8 (2.01, 8.5, -37.21), H9 (24.21, 6.2, -52.89).

## 2. H8 Firefly Hollow

**New props** (`_src/props_pass7.py`; dressing only, no collision, role `hollow`):

| Prop | Tris | Height | What |
|---|---|---|---|
| `firefly_cluster_low` | 128 | 1.7 | 16 `Firefly` Neon specks (r 0.1-0.22) hovering 0.3..1.8 above the ground |
| `firefly_swarm` | 208 | 4.1 | 26 specks (r 0.1-0.24) rising in a loose spiral. Tall, so it stays 3 studs back from rails |
| `glow_shroom_patch` | 214 | 1.2 | 3 low-poly glow mushrooms (`ShroomGlow` caps, `Firefly` spots) on a moss pad |
| `glow_root_arch` | 250 | 1.75 | `RootBark` surface root arching out of the leaf floor, side root, moss, 2 glow shrooms |

**Placement** (`dressing_world.py`, `HOLLOW_PLAN`, before the seed pass, right after the H7 extras; tag
`marks = firefly_hollow:<area>`):
- Alcove (east of rail15 / north of rail16 / south of rail14): 1 swarm, 3 roots, 2 patches, 3 clusters.
- `junction_back` (open ground just past the junction's back rail, straight down the tee view): 2 patches.
- `lane_right`: 1 cluster + 1 patch.
- `middle` (towards the green): 1 swarm, 1 root, 1 patch, 1 cluster.
- Total: 17 hollow instances. Every candidate went through the normal keep-out, ground, tall-near-rail and budget tests.

**Lights:** 2 new H8 `spot_lights` of kind `firefly_glow`.
- `#D8FF6A`, range 12, Brightness 2.0, about 2.4 above a swarm's base.
- `over: firefly_swarm:<k>`, with `target_pos` = the swarm's pos; fitcheck checks that target.
- `H8_firefly_swarm_1` sits at the alcove (13.55, 2.32, -17.42); `_2` sits in the middle (-5.24, 2.47, -26.3).

**H8 before / after:**

| | Pass 6 | Pass 7 |
|---|---|---|
| Instances (3D) | **13** | **29** |
| Glowing dressing | 0 | 17 (5 firefly clusters, 2 swarms, 6 glow-shroom patches, 4 glow roots) |
| Own dressing tris | 13,504 | 14,574 |
| Near-field tris | 33,802 | 33,888 (<= 34,000) |
| Spot lights | door + cup | door + cup (moved off the pennant) + 2 firefly glows |

- H8 lost its maple behind the tee (`maple_tree_lanterns`, 2,070 tris) and 1 `toadstool_trio_small` (984).
- It gained the 17 hollow props and one `golden_birch_tree` from the refill.

**Iterations** (detail in `pass7_progress.md`):
1. Pre-seed placement cost H6 5 ground-cover props.
2. Placing after the seed pass fitted only 1 of 24, because the shared H6/H7/H8 near fields are full.
3. Cheaper props plus `hollow_trim()` brought the H6 loss down to 3, then 2.
4. Tee render iteration 1: the alcove group is hidden behind the rails, so H8 still read faint.
5. Iteration 2: bigger specks, a `junction_back` group, brighter firefly spots, cheaper patch/root. Final H6 loss: 3.
6. Moving H6 up the seed order changed nothing, because the binding constraint is H7's near field, which contains all of
   H8. Reverted.

## 3. Felt (`_src/textures.py` felt(), `lglib.py`)

**`felt.png`:**
- Mean about 10% darker (G 135 -> 121 of 255).
- Ramp `#285F25 / #367A2F / #4D923D` (was `#2F6E2C / #3F8836 / #56A044`).
- Nap colour streaks 0.22 -> 0.40, mowing bands 0.08 -> 0.12.

**`felt_bright.png`** (H8/H9): only about 5% darker (G 183 -> 173). It is now 1.43x the base felt (was 1.35x), so
those holes stay relatively brighter.

**`felt_normal.png`:** nap height 0.7 -> 1.0, gradient x2.2 -> x4.0. x/y std went from 37/22 to 67/42, about 2x
stronger.

**Flat colours:** `Felt` `#478C35` (was `#4F9A3A`), `FeltBright` `#66B547` (was `#6CBF4C`), used in
`manifest.hole_skins`.

**Preview material:** normal-map strength 0.6 -> 1.0, sheen 0.3 -> 0.45 (roughness 0.45). The nap now shows on the felt
slopes in the tee renders (e.g. the H9 lane and ramps).

There are no other per-hole felt variants (`hole_skins.py` has only `Felt` / `FeltBright`).

## FBX list

**New:** `fbx/firefly_cluster_low.fbx`, `fbx/firefly_swarm.fbx`, `fbx/glow_shroom_patch.fbx`,
`fbx/glow_root_arch.fbx`, plus previews `previews/<name>_{eye,34}.png`.

**Changed mesh:** `fbx/cup_flag_h01.fbx` ... `fbx/cup_flag_h09.fbx`.

**Changed content (dressing groups):**
- `fbx/dressing_h03_cards.fbx` (-2 cards), `fbx/dressing_h06_a.fbx`, `fbx/dressing_h08_a.fbx`, `fbx/dressing_h09_a.fbx`.
- Every `dressing_hNN_*` file was re-exported; H1, H2, H4, H5 and H7 content is identical.

**Unchanged:** the full `build.sh` re-exported every other prop FBX from the same generators. No prop uses the Felt
material, so the felt change lives in `textures/` and `manifest.hole_skins`.

**Textures:** `textures/felt.png`, `felt_bright.png`, `felt_normal.png`.

## Dressing per hole (pass 6 -> pass 7, `manifest.dressing.holes.HN.stats.pass7_vs_pass6`)

| Hole | Instances | Removed (what was trimmed) | Added | Own tris p6 -> p7 | Near-field tris p6 -> p7 (<= 34,000) |
|---|---|---|---|---|---|
| H1 | 48 -> 48 | - | - | 16,860 -> 16,860 | 32,308 -> 32,308 |
| H2 | 42 -> 42 | - | - | 18,354 -> 18,354 | 33,998 -> 33,998 |
| H3 | 43 -> 41 | 2 far cards (12 tris each; refill knock-on) | - | 18,920 -> 18,896 | 32,204 -> 32,192 |
| H4 | 37 -> 37 | - | - | 16,862 -> 16,862 | 33,536 -> 33,536 |
| H5 | 34 -> 34 | - | - | 19,406 -> 19,406 | 27,114 -> 26,094 |
| H6 | 19 -> 16 | fern_clump_large 384, grass_tuft 224, orange_leaf_bush 400 | - | 10,792 -> 9,784 | 32,348 -> 33,382 |
| H7 | 25 -> 25 | - | - | 12,402 -> 12,402 | 33,954 -> 33,992 |
| H8 | 13 -> 29 | maple_tree_lanterns 2,070 (behind the tee), toadstool_trio_small 984 | 17 hollow + 1 golden birch | 13,504 -> 14,574 | 33,802 -> 33,888 |
| H9 | 26 -> 27 | fern_clump_large 384, orange_leaf_bush 400, red_leaf_bush 320, toadstool_trio_small x3 (2 near, 1 interior; 984 each), glowing_mushrooms 2,040 (interior) | 4 glow_shroom_patch, toadstool_cluster, toadstool_tall, 2 toadstool_trio_small | 16,936 -> 16,684 | 27,162 -> 30,250 |
| **Total** | 287 -> 299 | | | **144,036 -> 143,822** | max **33,998** (H2, unchanged) |

**What paid for the hollow** (`hollow_trim()` in `dressing_world.py`):
- H8's own trees behind its tee (local z > 4);
- the heavy 984-tri `toadstool_trio_small` seed ground cover of H8/H9;
- the cheapest late ground cover in the shared near fields: 3 pieces on H6 and 3 on H9;
- the H9 interior refill, which now also uses the cheap `glow_shroom_patch` (214 vs 2,040 tris) and ends +1 instance.

**Hero-prop tris** (not in the near-field budget, as before): flags 940-1,228 each, 72-28 fewer than in pass 6.

## Fitcheck (ALL PASS, 175)

New pass-7 checks are in `_src/fitcheck_pass7.py`, exec'd by `fitcheck.py` after pass 6:
- H8 has >= 10 hollow props, >= 5 around the alcove, and all 4 kinds (actual: 17 hollow, 10 within 9 studs of the alcove).
- The hollow props glow (Firefly / ShroomGlow Neon) and are each <= 300 tris.
- H8 is richer than in pass 6 (13 -> 29) and its near field is <= 34k (33,888).
- H8 has firefly_glow spot lights (2). They also pass the general spot check: local == world, clear of keep-outs and
  world pieces, within 0.7 x range of the swarm.
- Felt: darker than pass 6 (G 0.475 < 0.5), felt_bright >= 1.3x, nap normal >= 1.5x pass 6 (std 66.9 vs 37).
- The H8/H9 cup spots are >= 1.5 from the pennant (2.10 / 2.22).
- Pass 6 file: flag sizes, plus the new tee -> pennant-centre sightline check.

All generic dressing checks (keep-outs, vertex + triangle tests, tall props >= 3 studs from rails, ground, near field
<= 34k) cover the new instances.

## Open issues
- **holes.json flag sizes:** `cup.flag.pole_diameter` / `banner_size` still say 0.15 / 2.0 x 1.2. The FBX are bigger
  (0.30 / 3.2 x 2.0, pennant), and the pole top is unchanged. If the design agent owns those numbers, it should bump
  them, or treat them as minimums as fitcheck does.
- **H6 is thinner again:** 16 instances (19 in pass 6, 25 in pass 5). The binding constraint is H7's near field, which
  contains all of H8 and most of H6. The next levers:
  - cheaper H7/H8 lanterns (`lantern_hook_pair` 978, `lantern_span_20` 2,016);
  - dropping H8's far trees behind the green (`maple_tree_tall`, `oak_tree_orange`, ~2.8k);
  - a higher budget than 34k if Quest profiling allows.
- **H6 flag** is behind the millwheel in the current tee framing (the static sightline is clear). Check in Studio: a
  slightly different tee camera or VR head position shows it.
- **H9 flag:** the pennant reads red/cream but sits among many lanterns and is partly behind the tunnel arch rib from
  the tee. Raising it is not allowed (pole top = holes.json). If it is still hard to read in VR, the design could raise
  `cup.flag.top`.
- **Firefly specks are static meshes.** In Studio, a gentle bob/flicker script (or a ParticleEmitter at each swarm)
  would sell them more. Add a faint PointLight per swarm/cluster if the 2 firefly_glow spots are not enough at night.
- **Alcove props sit behind rails15/16 from the tee**; they read when walking to the junction. The tee view relies on
  the `junction_back` / `middle` groups.
- **Felt in Studio:** apply felt_normal.png as the SurfaceAppearance NormalMap on every felt part (pass-5 hole_skins
  note); without it the nap and the slopes won't read.
- Pass 6 carry-overs still open:
  - notch the rail kit at the H8 door pockets;
  - the H9 tunnel rail-kit height assumption;
  - the pendulum light should move with the bob;
  - preview light units vs Roblox Brightness.
