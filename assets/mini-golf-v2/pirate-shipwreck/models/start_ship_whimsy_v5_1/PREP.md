# start_ship_whimsy_v5_1 — art corrections from v5

## Status
SOURCE COMPLETE. Game Art passed 2026-11-05 5:08 PM PT; builder and Art subsequently reported v31 live/art-pass in the group (parent relayed 2026-11-07). This source has not been verified identical to current live Studio. Collision UNSYNCED caveat below still applies.

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
