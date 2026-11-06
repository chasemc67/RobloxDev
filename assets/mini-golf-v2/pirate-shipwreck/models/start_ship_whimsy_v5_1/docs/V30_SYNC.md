# v5_1 ↔ Studio v30 synchronization status

Source of truth for Studio deltas: `../v30_studio_deltas.json` (+ `../v30_studio_deltas_README.md`), commit `a47b903` (schema `pirate-shipwreck-v30-studio-deltas/v1`, place 131316561222931 / publishedVersion 30, ship asset base `start_ship_b2_detail_v3_2` @ `c9dd207`). Reference only; nothing in this pass reads or writes Studio.

Coordinates: Roblox +Y up, studs. Ship placement `CFrame(-690, 0.6, 160) * Angles(0, rad(102), 0) * CFrame(bboxCentre) * Angles(0, pi, 0)` (unchanged). Water world Y=0 ⇒ model local Y=−0.6. CFrame values in the JSON are `GetComponents()` 12-tuples (world). Blender local uses B(x,y,z)=(x,−z,y); do **not** paste world CFrames into Blender without the placement inverse.

This whimsy **v5_1** art-correction pass (`start_ship_whimsy_v5_1.blend`, built from `source_v5.blend` sha `8e88f0e9…`, commit `2e4023b`) is **visual-only**. The Collision collection is still the 190 v3_2 Blender boxes, byte-identical to source_v5 (fitcheck 190/190). **No collision FBX is handed off.** Studio v30 colliders stay authoritative until RobloxDevBot reapplies or regenerates them against the new Hull.

## Per-delta status (v5_1)

| Delta | Manifest key | In v5_1 .blend? | Action on next Studio import |
|---|---|---|---|
| Landing RailW widen (Z 12.9→**3.5**, footprint gap ≈**12.54**) | `landing_exit_widen` | **Not in Blender.** COL_Landing_* untouched (stale). RampLanding visual locked exact. | **Studio reapply** from JSON (size/CFrame of `COL_Landing_RailW`, keep RailS/RailE). |
| HullExt notch disabled (`COL_HullExt_0_07`, `COL_HullExt_1_07` CanCollide/Query/Touch=false) | `hullExt_notch_disabled` | **Not in Blender.** Still colliding in the blend Collision collection. | **Studio reapply** flags from JSON. |
| Hull side / under-band refit (930 `COL_HullSide*` + 80 `COL_HullUnder*`, 4-stud stations) | `hull_side_underside_refit` | **Not in Blender.** | **REGENERATE from the new Hull. Do not paste v30 transforms.** v5_1 belly is rounder than v5 (extra ×(1+0.16·sin²) hump peaking at world Y3, zero at ≥Y14, deck footprint fixed). Widths at x-100: Y-0.6 19.98→22.44, Y3 37.51→43.26, Y6 46.73→52.54. Vs stale v3_2 COL_HullExt: up to **3.21** studs outside (p95 2.43, 419/1766 samples >1 stud; increase vs v5 up to 2.57). |
| Stern palette by mesh name (`Hull`, `Prop_SternCurl`, `Prop_SternCastle` → `rbxassetid://123993872360188`) | `stern_palette` | Studio-side. Palette PNG keeps the same cell colours (+1 new cell: CoralDk 180,80,70 at cell 26). | **Studio reapply** texture IDs by mesh name after import. Note: ShipV5_SternCurl (now 1.8×) uses the shared palette; leave as is unless art asks for the stern texture on it. |
| Ship pivot / placement | `placement` | **Preserved.** Anchors Spawn/Tee1/RampStart/CupRef exact; DeckCabin + 3 ramps byte-identical; every object origin unchanged. | Keep formula, Hole1, gangplank, anchors. |
| Mast COL (`COL_Mast_Main`) | `mast` | Unchanged (part of the 190). | Keep. |

## What changed visually in v5_1 (all names + origins preserved)

- Hull / Prop_Barnacles / Prop_PatchPlanks / Prop_Seaweed / Rigging (low anchor lines only): rounder waterline belly (vertex positions only).
- ShipV5_SheerRise rebuilt: bow rise +7 at the stem (v5 +4), transom crest +4.6 corners / +7 centre (v5 +1.6 / +4), new stern-castle side rise boards.
- ShipV5_SternCurl: vertices scaled 1.8× about its crest base, lifted +3 with the crest (top Y 88.3 → 109.2).
- ShipV5_BowEyes rebuilt ~2× (rim r 5.1), high on the bow flanks, dark pupils + thick lid plank.
- Prop_Figurehead rebuilt 1.6×: Coral (230,120,100) + CoralDk (180,80,70) underside.
- ShipV5_Patches rebuilt: 4 large 20×14 blue/teal patches on the visible low (+Z) side, chunky brass nails.
- Tee read: Prop_SternWheel, Prop_TreasureChest, the tee rope coil in Prop_RopeCoils, and the 3 barrels in Prop_CargoCluster moved (mesh vertices only, origins fixed) out of the tee sightline. The crab's crate stack and Prop_Crab did not move.

## Visual FBX handoff

- `fbx/start_ship_b2_visual.fbx`: visual meshes + ramps + props + anchor empties (49 objects, re-import verified).
- `fbx/RampFlight1_own_origin.fbx`, `fbx/RampLanding_own_origin.fbx`, `fbx/RampFlight2_own_origin.fbx`: ramp own-origin, unchanged locks.
- `fbx/UNSYNCED_keep_studio_v30_colliders.txt` (also in `docs/`): do not replace Studio v30 colliders from this blend.

## Reimport checklist (for RobloxDevBot)

1. Import `start_ship_b2_visual.fbx`; keep v3_2 mesh names for walking-route colliders.
2. **Reapply** landing RailW (Z 3.5 / 12.54 gap) and the HullExt 0_07/1_07 notch flags from the JSON.
3. **Regenerate** hullSide/hullUnder bands from the new Hull (silhouette changed in v5 and again in v5_1), then re-run hull ball tests.
4. Reapply stern texture `123993872360188` by mesh name for Hull / Prop_SternCurl / Prop_SternCastle.
5. Preserve the placement formula. Apply in Studio (no Rojo).

Collision sync is **not** claimed complete until the reapply/regenerate step is verified against this visual hull.
