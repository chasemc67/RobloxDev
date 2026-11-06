# start_ship_whimsy_v5_1 — art corrections from v5

## Status
COMPLETE pending Game Art review (2026-11-05 ~5:07 PM PT). Not approved for handoff.

## Base
- Preserved first pass: `../start_ship_whimsy_v5/start_ship_whimsy_v5.blend` (commit `2e4023b`, sha256 `8e88f0e973…`) — UNTOUCHED
- Deliverable: `start_ship_whimsy_v5_1.blend` (sha256 `fd7798af4c…`)

## Fitcheck
Hard PASS. Collision 190/190 byte-identical, untouched, UNSYNCED vs Studio v30. DeckCabin/ramps/anchors exact. Tris 63635 (warn). Hull-side FLAG: up to 3.21 studs outside stale COL — regenerate bands.

## Caveats for art/builder
- High-side bow eye centre 1.2 lower than v5 (cap-rail fit); low-side higher; lids/pupils readable.
- Preview coral fixed via Standard view transform (AgX washed it); asset palette RGB unchanged.
- Tee coil still peeking bottom-right of ship_tee; wheel/chest off sightline (0 visible verts).
- Aft patches lower (Y19–21) than bow pair due to wale/portholes.
