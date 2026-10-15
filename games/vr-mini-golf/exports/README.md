# Live place exports

Read-only snapshots of the scripts in the live (published) VR Mini Golf places, made by stage exp1 on Oct 15, 2026.

Each folder is `exports/<PlaceRole>-v<published version>/`:
- `src/`: every LuaSourceContainer in the place, in the same layout as `games/vr-mini-golf/src` (`.server.luau` = Script, `.client.luau` = LocalScript, `.luau` = ModuleScript).
- `manifest.json`: placeId, version, role, export time, script count and total bytes, sha256 per script, Workspace top-level children with BasePart counts (Terrain counts as one BasePart), total BaseParts, MeshPart count, whether terrain has cells, and the sha256/size of the matching downloaded copy `playtest/playtest-<role>-v<N>.rbxl` (gitignored, on the Mini only).

## How they were made
1. Open the place in Studio in Edit mode: `open "roblox-studio:1+launchmode:edit+task:EditPlace+placeId:<id>+universeId:10769274294"`.
2. Check that exactly one Studio is open, that it's on that place, and that `game.PlaceVersion` equals the published version. If the version differs (Studio opens the latest *saved* version, which can be newer than the published one), the place is skipped, so no export ever comes from the wrong version.
3. `GOLF_EXPORT_DIR=exports/<role>-v<N>/src python3 tools/run_playtests.py export`. The `GOLF_EXPORT_DIR` override makes export write there (and only remove stale files there) instead of the shared `src/`.
4. Write the manifest from Edit-mode reads, then quit Studio without saving.

Nothing was saved or published.

## Contents (exp1)
| Place | Published | Studio opened | Result |
|---|---|---|---|
| lobby 87725688219952 | v251 | v252 (saved, unpublished) | skipped, no folder |
| lantern_grove 91438142503824 | v25 | v26 (saved, unpublished) | skipped, no folder |
| sugarloaf_canyon 124440050576723 | v103 | v103 | `sugarloaf_canyon-v103/` (59 scripts) |
| aurora_archipelago 79649062523043 | v13 | v14 (saved, unpublished) | skipped, no folder |

`script-diff.md` compares the exports with `src/`.
