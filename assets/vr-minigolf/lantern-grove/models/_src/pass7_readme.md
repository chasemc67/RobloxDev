## Pass 7: legible cup flags, H8 Firefly Hollow, darker felt with a stronger nap

This section supersedes the pass-6 flag description below. Full log: `_src/pass7_summary.md`.

**Cup flags** (`cup_flag_h01` .. `cup_flag_h09`, rebuilt so they read from the tee):
- Thicker pole: 0.30 diameter (holes.json minimum 0.15), cream with red bands.
- Bigger pennant: 3.2 long, 2.0 tall at the hoist, tapering to 1.1 at the tip (holes.json minimum 2.0 x 1.2). It is
  bright `FlagRed` `#E03C31` with a cream hoist band, cream top/bottom borders and a big cream hole number on both faces.
- Unchanged: the gold knob at the pole top is still exactly at holes.json `cup.flag.top`; the pole foot sits at the cup
  centre; the banner turns to the tee; **no collision** (CanCollide / CanTouch / CanQuery = false).
- The lantern emblem and the lantern finial are gone, for legibility.
- holes.json still says 0.15 / 2.0 x 1.2. Those are the minimums; use these FBX as they are.

**H8 Firefly Hollow** (new dressing props, `_src/props_pass7.py`, role `hollow`, `marks = firefly_hollow:<area>`):

| Prop | Tris | What |
|---|---|---|
| `firefly_cluster_low` | 128 | 16 Neon firefly specks (`Firefly` `#D8FF6A`) hovering 0.3..1.8 above the ground, no ground contact |
| `firefly_swarm` | 208 | 26 specks rising in a loose spiral up to ~4.1 (tall: kept >= 3 studs back from rails) |
| `glow_shroom_patch` | 214 | 3 small bioluminescent mushrooms (`ShroomGlow` Neon caps, Firefly spots) on a moss pad |
| `glow_root_arch` | 250 | Gnarled `RootBark` surface root arching out of the leaf floor, side root, moss, 2 glow shrooms |

- **Placement:** placed around the alcove (east of rail15, north of rail16), past the junction's back rail (the open
  ground straight down the tee view), beside the lane and in the middle ground towards the green.
- **Lights:** H8 `spot_lights` gained `kind: firefly_glow` PointLights (#D8FF6A, range 12, Brightness 2.0) about 2.4
  above the firefly swarms (`over: firefly_swarm:<k>`, `target_pos` = the swarm's pos).
- **Budget cost:** the H6/H7/H8 near fields are shared and were full, so the new props had to be paid for. What was
  trimmed:
  - H8's own maple behind its tee (never in the tee view);
  - the heavy 984-tri `toadstool_trio_small` seed ground cover of H8/H9;
  - one H9 interior `glowing_mushrooms` (the H9 interior refill now also uses `glow_shroom_patch`);
  - 3 small ground-cover pieces each on H6 and H9 (H9 still ends up +1 instance);
  - 2 H3 far cards (24 tris).

  See the table below.

**Felt** (`textures/felt.png`, `felt_bright.png`, `felt_normal.png`):
- `felt.png` is about 10% darker and has about 2x the nap: stronger colour streaks along V, and normal ridges at x4.0
  (was x2.2).
- `felt_bright.png` (H8/H9) is only about 5% darker, so it stays relatively brighter (1.43x the base felt, was 1.35x).
- Flat colours: `Felt` `#478C35` (was `#4F9A3A`), `FeltBright` `#66B547` (was `#6CBF4C`).
- In Studio, use felt_normal.png as the SurfaceAppearance NormalMap at full strength; it is what makes slopes and the H9
  dip read. The preview material uses normal strength 1.0 (was 0.6) and sheen 0.45 (was 0.3).
