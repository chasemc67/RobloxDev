# Stage aj clearance evidence

**Status: unresolved / not clear.** The targeted RailCap repair passes. The broader decoration clearance check does not establish a clean course; authored violations and conservative built envelope candidates remain. No mesh triangles were tested in this audit.

## Counts and meaning

| Evidence | Count | Interpretation |
|---|---:|---|
| Authored `deco_clearance --all` | 492 | Anchor-envelope rows, including dressing, flat and scenery envelopes |
| Authored `is_real` | 88 | Free-standing prop findings under the supplied checker’s classification; unresolved |
| Authored coplanar | 24 | Included in the authored total; generic anchor/wall coplanarity, not the RailCap count |
| Built oriented-bound candidates | 15,652 | Actual visual-part OBB versus physical rail/felt/headroom, gap 0.15; multiple targets/volumes can count the same visual |
| Built name-classified dressing envelopes | 5,198 | Likely skins/decks/plinths; classification is not a waiver or verified clearance |
| Other built candidates | 10,454 | Includes flags, hollow structures and grouped mesh bounds; not that many proven rendered intersections |

The built audit uses 1,830 visible parts and 993 target volumes. It reports 6,247 rail, 2,713 felt, 2,843 ball-headroom and 3,849 player-headroom candidate rows. Player headroom covers felt−0.4 through felt+8 studs; ball headroom is 0.16 studs. OBB overlap can cover empty space inside a hollow or material-grouped mesh. Counts cannot be subtracted from the authored anchor-level counts.

## Exact anchor correspondence

Only exact anchor/model ancestry is mapped. Invisible anchors and hidden placeholders do not establish that a visible imported prop corresponds. Rows for prop-versus-prop and generic coplanar faces lack an equivalent built test. A matching visible model with no matching candidate means that specific envelope finding was not reproduced; it does not clear unmapped geometry.

| Mapping result | Authored rows |
|---|---:|
| built envelope candidate corresponds | 41 |
| unmapped no exact visible model | 43 |
| not comparable prop pair or coplanar | 4 |

| Hole | Anchor | Authored real rows | Exact visible parts | Rows with same-target built candidate |
|---:|---|---:|---:|---:|
| 2 | `headframe` | 1 | 4 | 1 |
| 2 | `left_open_cut` | 13 | 0 | 0 |
| 2 | `rock_face` | 1 | 0 | 0 |
| 2 | `sign_mid` | 1 | 2 | 1 |
| 3 | `ranger_footbridge` | 4 | 0 | 0 |
| 5 | `echo_walls` | 7 | 2 | 6 |
| 7 | `island_edge_lip` | 8 | 0 | 0 |
| 7 | `island_hoodoo` | 1 | 13 | 1 |
| 9 | `pump_house` | 11 | 7 | 10 |
| 10 | `basin_bank` | 3 | 0 | 0 |
| 10 | `sluice_flume` | 5 | 4 | 5 |
| 12 | `pier_posts` | 4 | 1 | 4 |
| 15 | `dune_cliff` | 3 | 0 | 0 |
| 16 | `bowl_rim` | 6 | 0 | 0 |
| 17 | `gnomon` | 9 | 3 | 7 |
| 17 | `hour_stone_I` | 1 | 2 | 1 |
| 17 | `hour_stone_IV` | 1 | 2 | 1 |
| 17 | `hour_stone_VII` | 1 | 2 | 1 |
| 17 | `hour_stone_VIII` | 1 | 2 | 1 |
| 17 | `hour_stone_X` | 1 | 2 | 1 |
| 17 | `hour_stone_XI` | 1 | 2 | 1 |
| 18 | `cliff_edge` | 5 | 0 | 0 |

Full target IDs, separation values and exact model paths: [correspondence JSON](clearance-correspondence.json). Complete conservative built candidates: [built-clearance.json](built-clearance.json). Authored findings: [deco_clearance.json](deco_clearance.json).

## RailCap repair

All 254 current RailCaps are raised and have no remaining overlapping coplanar top face. The supplied baseline identified 253 unique caps; the new H15 build adds one. After measurement uses the rail face normal and overlapping top footprints, with the 0.02-stud world lift projected onto that normal. The additional trim/lip scan found zero remaining visible top-face candidates; baseline non-RailCap lip pairs are physical H11 felt/base geometry, preserved.

| Hole | Baseline coplanar caps | Current caps raised | Coplanar tops after |
|---:|---:|---:|---:|
| 1 | 6 | 6 | 0 |
| 2 | 14 | 14 | 0 |
| 3 | 12 | 12 | 0 |
| 4 | 4 | 4 | 0 |
| 5 | 12 | 12 | 0 |
| 6 | 15 | 15 | 0 |
| 7 | 14 | 14 | 0 |
| 8 | 32 | 32 | 0 |
| 9 | 12 | 12 | 0 |
| 10 | 14 | 14 | 0 |
| 11 | 43 | 43 | 0 |
| 12 | 13 | 13 | 0 |
| 13 | 8 | 8 | 0 |
| 14 | 10 | 10 | 0 |
| 15 | 11 | 12 | 0 |
| 16 | 8 | 8 | 0 |
| 17 | 8 | 8 | 0 |
| 18 | 17 | 17 | 0 |

Full names and measured before/after planes: [railcap-fixed-list.json](railcap-fixed-list.json). Separate lip/trim audit: [trim-lip-audit.json](trim-lip-audit.json).

## Verified targeted checks

H8/H15 generated geometry matches fresh data-built references (132 and 50 parts). All 17 Trading Post parts have collision/query/touch disabled. Seven invisible primitive obstacle proxies pass. H9 water-tank and H14 loading-dock placeholders are absent. Approved H8/H9 import transforms, mesh bounds and visual flags pass. These targeted passes do not resolve the broader decoration findings above. [Built audit summary](built-audit-summary.json).
