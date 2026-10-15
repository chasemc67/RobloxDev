# Stage au8 (Claude Code): Aurora Archipelago h18 ramp lantern cage, h07 mogul trim, separation

Status: **NOCHANGE.** Live Aurora v13 already contains both approved props, the exact au7 imports of these FBX files, at the right frames and with the right look and flags. VisualSeparation made 0 new fixes. Per the Step 0 gate I made no edits and no publish, and quit Studio without saving. Aurora published-only is still **v13** (`au8-au-published-v13.png`). Evidence: `playtests/stage-au8/gate.json`.

## Preflight
- One Studio (MCP `Aurora Archipelago (placeId: 79649062523043)`), signed in as MetavrseBuilder (StudioService 1818120139). PlaceVersion 13 (checkPlaceVersionRequest returned 13). PlaceRole `aurora_archipelago`. `Workspace.CourseAurora` has Hole1-Hole18. Workspace children: CourseAurora, Terrain, SpawnLocation, Camera. 1851 BaseParts.
- No other stage job. The only one is this run (screen `au8` -> `run-au8.sh`).
- **Open place = v13:** I fingerprinted every Workspace BasePart (path, class, CFrame, size, collide/query/touch, anchored, group, material, transparency, physics, custom physics, tags; `tools/au8_fingerprint.py` has the same line format in Python) and compared it with au7's `inventory-final.json`.
  - The 615 gameplay parts match (digest `aa4ce434` on both sides), so the colliders equal the au7 final collider verification.
  - Every hole digest matches except Hole12 and Hole14. There, 4 non-gameplay mover helpers (MoverRoot/MoverBase of `Mover_paddle_wheel` and `Mover_icicle_bell`) differ only in the sign of one zero rotation component (`0.0000` vs `-0.0000`), which is float noise.
  - Hole7 and Hole18 match exactly.

## Step 0 gate
- **SHA256** matches the manifests: h18_ramp_lanterns `1c7b27ca...b5e8` (props_fix_overlap4), h07_mogul_trim `74a70da8...00e` (props_fix_overlap3).
- **h18_ramp_lanterns** (`Workspace.CourseAurora.Hole18.Decor`):
  - Pivot (-243.9, 224.9, -265), yaw 0. This is the approved batch-3 pivot record au7 asserted.
  - Parts (size, offset from pivot, EditableMesh tris):
    - Brass: 1.898 x 6.512 x 7.95 @ (0.5, 3.413, 0), 492 tris
    - Glow: 0.206 x 0.206 x 7.206 @ (0, 6.185, 0), 36 tris, **Neon**, no shadow
    - Snow: 0.51 x 0.206 x 7.51 @ (0, 6.858, 0), 228 tris
    - Timber: 0.6 x 5.168 x 7.6 @ (0, 3.03, 0), 36 tris
  - Total 792 tris, as in the overlap4 manifest. The Glow cube is 0.206 inside the new corner-bar cage.
  - The kit copy `ServerStorage.AuroraBatch3Kit.h18_ramp_lanterns` is identical (same mesh IDs, sizes, appearance, flags).
- **h07_mogul_trim** (`Workspace.CourseAurora.Hole7.Decor`):
  - Pivot (365, 112, 308), yaw 0.
  - Snow 7.4 x 0.206 x 27.8 @ (0, 1.497, 0), 2240 tris. Timber 7.4 x 1.158 x 27.8 @ (0, 0.729, 0), 304 tris.
  - This matches overlap3: 2544 tris, the 7.4 width pulled in from 9.0.
  - There is no kit copy, and none existed before au7.
- **Mesh IDs** are the au7 uploads (`playtests/stage-au7/imported.json`). EditableMesh bounds are a uniform x73.67 of part Size on all axes (the importer auto-scale), so the mesh proportions equal the FBX true bounds.
- **Flags** on all 6 Workspace parts and all 4 kit parts: CanCollide, CanQuery and CanTouch off, Anchored, `VisualQueryDisabled`=true.
- **Copies:** exactly 3 (the 2 Workspace models and the 1 kit model). There are no duplicates, no leftover older cage or trim, and no AU8Backup was needed.
- **VisualSeparation probe:** `CourseBuilder.ApplyVisualSeparation(CourseAurora)` (gap 0.08, min 0.2) ran in Edit:
  - 544 operations, the same idempotent reapplications as au7.
  - 0 unresolved, 0 thin, 0 invariant failures, 99 joints reconnected.
  - **0 Workspace parts changed** (CFrame, size, flags, material, colour, transparency compared before and after) and 0 removed. So there were 0 new fixes.
  - The place was not saved afterward.

## Not run (gate stopped the stage)
Smoke, the 18-hole sweep, the z-scans, the screenshots, the publish and the rbxl download were skipped by design: the place is unchanged from v13. au7 already recorded these for v13: sweep 54/54, 36/0/0/0; z-scan 1087 -> 1017, 0 exposed; smoke 0 errors.

## Close-out
- Quit Studio (application quit, no save prompt). The Studio log shows no save or publish (only layout save and DataModel shutdown). **No RobloxStudio process remains.**
- Creator Hub Aurora "Show published only": 13, 8, 6, 4, 3, 2 (`au8-au-published-v13.png`, an already-open Chrome tab captured read-only).
- Lobby, Lantern Grove, Sugarloaf, 135374506016678 and the Windows PC were never opened. No assets were created, deleted or archived. The sshd-session prompt was not on screen, and no keystrokes were sent.

No build or publish was needed.

RESULT=NOCHANGE AU_NEW=13 H18=already H07=already SEP=0/0 COLLIDERS=same STUDIO_CLOSED=yes

BUILD DONE, STUDIO CLOSED
