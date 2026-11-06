# v5 ↔ Studio v30 synchronization status

Source of truth for Studio deltas: `../v30_studio_deltas.json` (+ `../v30_studio_deltas_README.md`), commit `a47b903` (schema `pirate-shipwreck-v30-studio-deltas/v1`, place 131316561222931 / publishedVersion 30, ship asset base `start_ship_b2_detail_v3_2` @ `c9dd207`).

Coordinates: Roblox +Y up, studs. Ship placement `CFrame(-690, 0.6, 160) * Angles(0, rad(102), 0) * CFrame(bboxCentre) * Angles(0, pi, 0)`. Water world Y=0 ⇒ model local Y=−0.6. CFrame values in the JSON are `GetComponents()` 12-tuples (world). Blender local uses B(x,y,z)=(x,−z,y); do **not** paste world CFrames into Blender without the placement inverse.

This whimsy v5 pass (`start_ship_whimsy_v5.blend`) is **visual-only**. Collision collection is still the 190 v3_2 Blender boxes (byte-identical to source; fitcheck 190/190). **No collision FBX is handed off.** Studio v30 colliders remain authoritative until RobloxDevBot re-applies / regenerates from the manifest against the new Hull.

## Per-delta status

| Delta | Manifest key | In v5 .blend / source? | Action on next Studio import |
|---|---|---|---|
| Landing RailW widen (Z 12.9→**3.5**, footprint gap ≈**12.54**) | `landing_exit_widen` | **Not in Blender.** COL_Landing_* untouched (stale). RampLanding visual locked exact. | **Reapply from JSON** (size/CFrame of `COL_Landing_RailW` + keep RailS/RailE). Studio-only override until Blender COL regenerated. |
| HullExt notch disabled (`COL_HullExt_0_07`, `COL_HullExt_1_07` CanCollide/Query/Touch=false, `V28Disabled`) | `hullExt_notch_disabled` | **Not in Blender.** Those Parts still collide in the blend Collision collection. | **Reapply flags from JSON.** Studio-only override. |
| Hull side / under-band refit (930 `COL_HullSide*` + 80 `COL_HullUnder*` @ 4-stud stations) | `hull_side_underside_refit` | **Not in Blender.** Blend still has old COL_HullExt boxes. | **Do NOT paste v30 transforms blindly.** v5 Hull belly is widened ×1.15 at/below world Y6 → ×1.0 by Y18 (deck footprint fixed). Fitcheck vs stale v3_2 HullExt: up to **0.83 studs** further out (106/1766 samples >0.5). **Regenerate** bands from the new Hull mesh (`generate_hull_bands.luau` or equivalent). |
| Stern palette by mesh name (`Hull`, `Prop_SternCurl`, `Prop_SternCastle` → texture `rbxassetid://123993872360188` HullWood/WoodDk; others `127118214115521`) | `stern_palette` | **Partial / Studio-side.** Packed palette PNG in blend keeps same cell colours; MeshPart.Color alone does not tint opaque legacy textures. UV-only Studio correction was applied on v3_2 import without changing source FBX. | **Reapply texture IDs by mesh name** after visual FBX import. Studio-only override metadata until a dedicated UV/texture sync pass. |
| Ship pivot / placement | `placement` | **Preserved.** Anchors Spawn/Tee1/RampStart/CupRef exact; DeckCabin + 3 ramps world matrices exact. | Keep formula and Hole1 / gangplank / anchors. |
| Mast COL (`COL_Mast_Main` 5×5×98.3 tilted) | `mast` | Unchanged in blend (part of the 190). | Keep; already includes mastfix. |

## Visual FBX handoff (this folder)

- `fbx/start_ship_b2_visual.fbx` — visual meshes only (gitignored; local/PC artifact).
- `fbx/RampFlight{1,2}_own_origin.fbx`, `fbx/RampLanding_own_origin.fbx` — ramp own-origin (unchanged locks).
- `fbx/UNSYNCED_keep_studio_v30_colliders.txt` (also copied under `docs/`) — explicit: do not replace Studio v30 colliders from this blend.

## Fitcheck summary (hard PASS)

- Locks: DeckCabin + 3 ramps exact; 4 anchors exact; walk surfaces / door rays / tee sightlines / spawn headroom identical; 0 coplanar.
- Collision: 190/190 byte-identical to v3_2 source; **not** verified against Studio v30.
- Route: no new/changed mesh enters continuous walkway corridor; hammock ≥123 studs from prior zones / ≥147 from corridor.
- Tris: visual total **60343** (source 51307, +9036); each mesh <20k (largest Rigging 8154). Warning: above ~40k near-field target.
- FLAG: hull-side mismatch vs stale Blender COL (see above) — regenerate against new Hull after import.

## Reimport checklist (for RobloxDevBot)

Follow `reimport_instructions_for_v5` in the JSON:

1. Keep v3_2 mesh names for walking-route colliders.
2. After importing new visual FBX, **independently reapply** landing RailW, HullExt notch flags, and **regenerate** hullSide/hullUnder from the new Hull (silhouette changed).
3. Reapply stern texture `123993872360188` by mesh name for Hull / Prop_SternCurl / Prop_SternCastle.
4. Preserve placement formula.
5. Do not rely on Rojo — apply in Studio.

Collision sync is **not** claimed complete until that reapply/regenerate is verified against this visual hull.
