# Live place exports

Read-only snapshots of the scripts in the live (published) VR Mini Golf places, made by stages exp1 and exp2 on Oct 15, 2026.

Each folder is `exports/<PlaceRole>-v<published version>/`:
- `src/`: every LuaSourceContainer in the place, in the same layout as `games/vr-mini-golf/src` (`.server.luau` = Script, `.client.luau` = LocalScript, `.luau` = ModuleScript).
- `manifest.json`: placeId, version, role, export time, script count and total bytes, sha256 per script, Workspace top-level children with BasePart counts (Terrain counts as one BasePart), total BaseParts, MeshPart count, whether terrain has cells, and the sha256/size of the matching downloaded copy `playtest/playtest-<role>-v<N>.rbxl` (gitignored, on the Mini only).

## How they were made
1. Open the place in Studio in Edit mode: `open "roblox-studio:1+launchmode:edit+task:EditPlace+placeId:<id>+universeId:10769274294"`.
2. Check that exactly one Studio is open, that it's on that place, and that `game.PlaceVersion` equals the published version. If the version differs (Studio opens the latest *saved* version, which can be newer than the published one), the place is skipped, so no export ever comes from the wrong version.
3. `GOLF_EXPORT_DIR=exports/<role>-v<N>/src python3 tools/run_playtests.py export`. The `GOLF_EXPORT_DIR` override makes export write there (and only remove stale files there) instead of the shared `src/`.
4. Write the manifest from Edit-mode reads, then quit Studio without saving.

exp2 (lobby, LG, AU): the cloud places open at newer saved-unpublished versions, so these three were exported from the File-downloaded copies of the published versions instead (`playtest/playtest-<role>-v<N>.rbxl`):
1. Copy the file to `/tmp/exp2/<role>.rbxl` and open the copy: `open -a /Applications/RobloxStudio.app /tmp/exp2/<role>.rbxl`. (On a cold start Studio can come up on the start page without loading the file. Running the same `open` again loads it.) The MCP lists the studio by file name, e.g. `lobby.rbxl`.
2. Check `workspace:GetAttribute("PlaceRole")`. A local file reads `game.PlaceId` = 0 and `game.PlaceVersion` = 0, so the version comes from the downloaded file's name, and the repo file's sha256 is recorded in the manifest.
3. `GOLF_STUDIO=<role>.rbxl GOLF_EXPORT_DIR=exports/<role>-v<N>/src python3 tools/run_playtests.py export`, then the manifest.
4. Quit. Studio shows a "Save changes to <role>.rbxl?" prompt (export's Edit-mode Luau marks the file dirty). It's never answered: the AppleScript quit is cancelled and the process is killed, which discards. The `/tmp` copies and the repo files hash the same as before.

These manifests also have `"source": "local downloaded copy"`, `studioPlaceId`, and `rbxlCopy.openedCopy`/`note`.

Nothing was saved or published.

## Contents
| Place | Published | Source | Folder | Scripts | BaseParts / MeshParts / terrain |
|---|---|---|---|---|---|
| lobby 87725688219952 | v251 | exp2: downloaded copy `playtest-lobby-v251.rbxl` (sha256 `a0ebd043…a241`) | `lobby-v251/` | 58 (1,750,959 B) | 376 / 320 / no |
| lantern_grove 91438142503824 | v25 | exp2: downloaded copy `playtest-lantern_grove-v25.rbxl` (`5f6abe22…4ab0`) | `lantern_grove-v25/` | 59 (1,759,148 B) | 3,785 / 2,525 / yes |
| sugarloaf_canyon 124440050576723 | v103 | exp1: live cloud place, Studio `PlaceVersion` 103 | `sugarloaf_canyon-v103/` | 59 (1,775,428 B) | 7,501 / 5,138 / yes |
| aurora_archipelago 79649062523043 | v13 | exp2: downloaded copy `playtest-aurora_archipelago-v13.rbxl` (`c662d267…1352`) | `aurora_archipelago-v13/` | 59 (1,760,039 B) | 1,851 / 406 / no |

In exp1, the lobby, LG and AU cloud places opened at v252, v26 and v14 (saved but unpublished), so exp1 skipped them.

`script-diff.md` compares the exports with `src/`.
