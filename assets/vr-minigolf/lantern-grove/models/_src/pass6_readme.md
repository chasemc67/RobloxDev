## Pass 6: holes.json v2 (playtest Rounds 5/6)

Everything below was rebuilt against `../holes.json` v2 (source of truth), `../world/world.json` and
`../world/terrain-4stud.json`. Only H3 and H6 kept their geometry (they gained flags). Full log: `_src/pass6_summary.md`.

**New props** (decoration only, no collision, stud scale; generators in `_src/props_pass6.py` and `_src/props_moving.py`):

| Prop | Hole | What / where (hole-local) |
|---|---|---|
| `cup_flag_h01` .. `cup_flag_h09` | all | Lantern-themed flag per hole: cream pole with red bands, `FlagRed` `#E03C31` banner 2.0 x 1.2 with the hole number + lantern emblem on both faces, gold knob at `cup.flag.top`, small glowing paper lantern at the banner's free corner. Pole foot at the cup centre, banner turned to the tee. **No collision** |
| `h2_chute_sign_left` / `_right` | H2 | Fingerposts at (-5.2 / 5.2, 0, -16.5) outside the lane rails; 1.8-long arrow boards along holes.json `facing`, carved 'Bold Line' + rabbit / 'Safe Line' on both faces, mini lantern under the tip |
| `h2_chute_arrow_decal` (x2) | H2 | Glowing leaf arrows, 0.01 thick, flush on the lane felt at (+-2.75, 0, -17), pointing -Z into each chute |
| `h4_side_gap_post` (x2) | H4 | Small lantern posts standing on the plaza rail tops at x = +-7.25, z -17 (y = rail top 1.0) |
| `h5_respawn_stone` | H5 | Glowing mossy marker disc, 0.02 tall, flush in the felt at the stream `respawn` point (0, 0, -13.5) |
| `h8_alcove_bank_cladding` | H8 | Root-bark skin ON the new `alcove_bank` felt plane (x 7.7..9, z -15..-8, rising 0.5 east), <= 0.03 above it |
| `h8_door_pocket` (x2) | H8 | Root-knot pockets on rail16 (north, yaw 180) and rail14 (south, yaw 0) at x 4.75: the root door's ends slide into them at +-3.5. **Notch the visual rail kit over x 4.2..5.3** where a pocket sits (collision rail unchanged) |
| `h9_lantern_pendulum` (MOVING) | H9 | Great lantern (red body, cream bands/caps, Neon window band) on a 7-stud red/cream chain. Origin = hinge (22, 8.96, -38.5); swing about +Z, angle(t) = 35 x sin(360 t / 4 s). Bob fills the 1.6 x 1.8 x 1.0 blocker, 0.06 above the felt at rest |
| `h9_pendulum_root_beam` | H9 | Root beam x 14..30 at y 9.2..10.4 with the hinge bracket; two root legs to the floor outside the chamber rails (feet x 12.4 / 31.6), 2 small lanterns |
| `h9_tunnel_dip_trim` | H9 | Root-and-moss wedges under the straight tunnel rail kit (rail8 / rail4 footprints) following the 0.4 rolling dip, x 8..14 |

**Changed**: `h4_carousel_bar` (arms 2.3 long, r 0.7..3.0, padded cream cushions + tip bumpers, 30 deg/s), `h7_floating_log`
(travel +-7), `h8_root_door` (+-3.5, into the pockets), `h9_root_portcullis` (0..1.8 at 0.9 studs/s), `firefly_ring_entry`
(trigger r 0.55: glow disc 1.1 across, ring R 0.85 with a 120-degree bottom gap), `firefly_ring_exit` (moved to
(9, 1.5, -47), yaw -26.57 along the exit dir), `root_arch_large` (c2 arch to z -22), `glowing_mushrooms` (H8 copy off the
moved c2 felt), `lantern_post` (H7 gap posts at x 3.75 / 6.75), `trunk_tunnel_arch` (top <= y 6 for the flag sightline),
`heart_lantern_cluster` (raised to y 7.5: at y 1.0 it blocked the H9 tee -> flag sightline). All moving parts keep the
MoveRed / MoveCream bands.

**Removed**: `h9_lantern_bar` and `h9_lantern_post_static` (FBX, previews, manifest entries). The H9 spot light over the bar
is replaced by `H9_lantern_pendulum_moving_part`, hung beside the hinge at (22, 8.96, -36.5), off the swing plane.

**Dressing**: re-placed against v2 (`dressing_world.py`). H7 (the barest hole at 13 props) goes first in the seed
pass and gets 17 cheap low ground-cover / mid props before it; it now has 25 (12,402 tris). H7's and H8's near fields
are shared with H6/H8/H9, so H6 gave up 5 small ground-cover props and 1 tree (25 -> 19 instances). Every hole stays
<= 34,000 near-field tris. The moved H8 cup's two lanterns sit 7.5-9 studs out (the closer spots are in the tree roots).
