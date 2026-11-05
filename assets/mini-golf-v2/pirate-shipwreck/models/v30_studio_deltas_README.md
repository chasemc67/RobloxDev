# Pirate Shipwreck v30 Studio deltas

Manifest for Studio-side fixes applied on top of ship asset **start_ship_b2_detail_v3_2** (handoff commit `c9dd207`) in place **131316561222931** (VR Mini Golf V2), published as place version **30**.

**File:** `v30_studio_deltas.json`

These deltas are **not** in Rojo/`chasemc67/vr-mini-golf-v2` source. Per RobloxDev `AGENTS.md`, Studio is the source of truth for instances. Numbers were captured with a read-only Studio MCP `execute_luau` dump of the open Edit place on 2026-11-05 (America/Los_Angeles), cross-checked against `games/vr-mini-golf-v2/playtests/v30-ship-v4/v30_report.md`.

## What to preserve on the next ship import (v5)

1. **Landing exit widen** — `COL_Landing_RailW` Size.Z = **3.5** (was 12.9), north endpoint kept; footprint gap vs `COL_Landing_RailS` ≈ **12.54** studs. `RampLanding` visual unchanged.
2. **HullExt notch** — `COL_HullExt_0_07` and `COL_HullExt_1_07` stay non-colliding / non-querying / non-touching (`V28Disabled`).
3. **Hull side/underside refit** — 930 `COL_HullSide*` + 80 `COL_HullUnder*` band Parts (4-stud stations). Full CFrame/size/flags are in the JSON. If the v5 hull silhouette changes a lot, regenerate bands from the new Hull mesh instead of pasting these transforms blindly.
4. **Stern palette** — `Hull`, `Prop_SternCurl`, `Prop_SternCastle` use texture `rbxassetid://123993872360188` (HullWood RGB 130,90,55 / WoodDk RGB 80,50,30). Other meshes keep `127118214115521`.
5. **Placement** — `CFrame(-690, 0.6, 160) * yaw 102° * bbox centre * flip 180°`. Keep Hole1, gangplank, anchors, deck route.

CFrame values are Roblox `GetComponents()` 12-tuples: `x,y,z, R00,R01,R02, R10,R11,R12, R20,R21,R22`.

On reimport, RobloxDevBot should reapply colliders/landing from this manifest independently until Blender/source sync is verified.
