# start_ship_whimsy_v5 — status (2026-11-05 PT)

## Status
VISUAL MODELING COMPLETE (PC Opus job `ship_v5_n5`). Previews + fitcheck ready for art review.
Collision / Studio v30 sync **not** claimed — see `docs/V30_SYNC.md`.

## Deliverables
- `start_ship_whimsy_v5.blend` (textures packed; sha256 8e88f0e97323ffdb0f00f0e55dd14d2afe527e2df3e465c6e71e6dd40d9d2abe)
- `src/` rebuild scripts (`build_v5.py`, `export_v5.py`, `fitcheck_v5*.py`, `render_v5.py`, …)
- `fitcheck.md` / `fitcheck.json` / `manifest.json` / `report.txt`
- `textures/start_ship_palette.png`
- `docs/V30_SYNC.md` — exact sync vs Studio-only override metadata
- `docs/UNSYNCED_keep_studio_v30_colliders.txt`
- Local (gitignored): `fbx/`, `previews/`, `logs/`

## Base
- Refined source: `../start_ship_b2_detail_v3_2/start_ship_v3_2.blend` (commit c9dd207)
- Local read-only copy kept as `start_ship_v3_2_base.blend` (not re-committed; identical to v3_2)

## Hard checks
PASS: DeckCabin + ramps locked; anchors exact; 190 colliders byte-identical to source (untouched); 0 coplanar; route clear; hammock outside walkway.
FLAG: hull belly ×1.15 widen → regenerate Studio hull-side/under bands (do not paste v30 transforms).
WARN: total visual tris 60343 (>~40k near-field).

## Studio v30 (authoritative colliders)
Manifest: `../v30_studio_deltas.json` @ `a47b903` (historical RobloxDev path; now in chasemc67/vr-mini-golf-v2 at `assets/pirate-shipwreck/models/v30_studio_deltas.json`, same data with V2 paths in its `sources` block). Dev reapplies independently on import until source sync verified.
