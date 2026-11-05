# v25save report: local .rbxl copy of the published Pirate Shipwreck v25

2026-11-01, ~22:16–22:22Z (14:16–14:22 PST). No publish, no Save to Roblox, no Ctrl+S, no edits to the world.

## 1. Closed the Lobby (pid 52091)
- File > Close Place → Qt dialog "Save changes to VR Mini Golf V2?" (Save / Don't Save / Cancel). Frontmost check (`/tmp/p4/act.sh 52091` → 52091), then `cliclick c:1005,518` = **Don't Save**. Window went back to "Roblox Studio" (start page).
- App menu > Quit Roblox Studio → **pid 52091 gone**.

## 2. Opened Pirate Shipwreck 131316561222931
- `open "roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371"` → new **pid 65468** (no Low System Resources dialog).
- Log `~/Library/Logs/Roblox/0.745.0.7451137_20261101T221849Z_Studio_1e60c_last.log`: **`id=131316561222931&version=25`**.
  - Note: the first log match my wait loop hit was the old `…20261101T132308Z_Studio_c0bae_last.log` (`version=19`), which old pid 93578 keeps touching. That was not my instance; the new log is the 22:18:49Z one above.
- MCP studio id `bfd88f06-8056-4740-9976-1175fde3c259` (the only instance reporting a place name). I confirmed it was the fresh pid and not 18508: `os.clock()` = 52 s / `elapsedTime()` = 53 s at check time.

## 3. Read-only MCP checks (Edit DataModel, before saving)
| Check | Result |
|---|---|
| game.PlaceId | 131316561222931 |
| Workspace.World.Dressing | **exists** |
| TrunkColliders (Workspace descendants named TrunkCollider) | **706** |
| World.Meshes.WreckV2 | **present** |
| Workspace attributes | HutTextureId, PlaceRole only; **no Gravity attribute** (Workspace.Gravity 196.2) |
| HttpService.HttpEnabled | **false** |
| game descendants | 8030 |

**Rojo synced on open:** `ReplicatedStorage.Shared.BuildInfo` = **sha 0bedef445e3d60d20cd0e58e1041d1ecf0ea3717**, dirty false, stampedAt 2026-11-01T22:11:25Z, builderHash 0716f229a84e…. The published v25 has stamp 98cb502; 0bedef4 is the docs-only deploys-rows commit on top of it, so only the stamp differs. `game.Name` reads "vr-mini-golf-v2" (Rojo project name). The saved file contains this 0bedef4 stamp. I made no other changes.

## 4. Save to File As
- File > Save to File As → native macOS "Save As" panel (default folder `playtest`, name "Pirate Shipwreck"). Cmd+Shift+G → `/Users/chase-mini/stage/` → Return. Cmd+A in the name field → `pirate_shipwreck_v25.rbxl`. Screenshot confirmed folder `stage` and the name, then Return (Save). No overwrite prompt; the file did not exist before.
- Studio log: `[FLog::CreatorOutput] Saved to '/Users/chase-mini/stage/pirate_shipwreck_v25.rbxl'` at 22:20:23Z. There is no "Saved new changes … to Roblox" or "Published" line in this session's log.

## 5. File verification
- Path: **/Users/chase-mini/stage/pirate_shipwreck_v25.rbxl**
- Size: **1,302,526 bytes** (> 1 MB)
- mtime: **2026-11-01 14:20:23 -0800** (22:20:23Z)
- md5: **77277d82dc07e92477aba99d097607a5**
- `file`: `data`. Header `<roblox!89ff0d0a1a0a`, so this is a Roblox **binary** place.
- Chunks are compressed, so a plain `strings`/grep finds nothing. I decompressed them with a small parser (`/tmp/p4/v25chk/rbxl.py`: pure-Python LZ4 plus the `zstd` CLI):
  - format 0, 93 classes, 4679 instances; chunks SSTR 1 / INST 93 / PROP 1710 / PRNT 1 / END 1 (parsed cleanly to END)
  - MeshPart 2962, Part 1367, **PointLight 74** (matches the chk20 count of 74), ModuleScript 59, Model 52, Folder 34, ParticleEmitter 15
  - String hits in the decompressed data: **TrunkCollider 706**, **WreckV2 1**, **Dressing 1**, Meshes 1, PlaceRole 21, HutTextureId 1, `0bedef445e3d` 1 (BuildInfo stamp), `98cb502` 0
- After closing and quitting, the size and md5 were unchanged.

## 6. Cleanup
- File > Close Place: **no prompt** (the local file was saved), and the start page showed. App menu > Quit → **pid 65468 gone**.
- No Studio instance of mine is left open. The remaining RobloxStudio pids are exactly 5180, 18508, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578. I touched none of them.

## Dialogs
1. pid 52091 "Save changes to VR Mini Golf V2?" → Don't Save (cliclick 1005,518 after the frontmost check).
2. pid 65468 macOS "Save As" panel → saved to ~/stage/pirate_shipwreck_v25.rbxl.
No Screen Recording prompt appeared. Screenshots are `/tmp/p4/v25_*.png`; `screencapture` was already permitted.

## Rules kept
No publish, no Save to Roblox, no Ctrl+S on the cloud place, no world edits (only the Rojo BuildInfo sync). One place open at a time. No access, collaborator or Robux changes. Nothing pushed or posted.

DONE_V25SAVE
