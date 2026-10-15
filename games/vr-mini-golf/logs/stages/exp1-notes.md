# Stage exp1: export the live places into the repo (read-only on Roblox)

Oct 15, 2026, about 00:00 to 00:10 PT, Mac Mini, Claude Code (Opus 5.5). One Studio and one place at a time, Edit-mode reads only. Nothing saved or published, nothing edited, no permissions granted, no Roblox assets touched, PC not used.

## Tool change
`tools/run_playtests.py` `cmd_export`: `GOLF_EXPORT_DIR=<dir>` overrides the output dir (default stays `src/`), and stale-file removal applies only inside that dir. Two added lines and no other changes in the file. Shared `src/` wasn't modified.

## Per place
| Place | Expected (published) | Studio `PlaceVersion` / `PlaceRole` | Result |
|---|---|---|---|
| lobby 87725688219952 | 251 | 252 / lobby | **SKIPPED, version mismatch.** v252 is the known saved-unpublished revision from zf2 (Oct 13, 10:33 PM). |
| lantern_grove 91438142503824 | 25 | 26 / lantern_grove | **SKIPPED, version mismatch.** v26 is a saved, unpublished revision newer than published v25. It's probably a Studio autosave (lg14 notes show autosaves v20-v24 during that stage), but I didn't check its origin in Creator Hub. |
| sugarloaf_canyon 124440050576723 | 103 | 103 / sugarloaf_canyon | **EXPORTED:** 59 scripts, 1,775,428 bytes. 7,501 BaseParts (incl. Terrain), 5,138 MeshParts, terrain present. Matching `playtest/playtest-sugarloaf_canyon-v103.rbxl` sha256 `242c5808…2cc6` (5,435,842 bytes). |
| aurora_archipelago 79649062523043 | 13 | 14 / aurora_archipelago | **SKIPPED, version mismatch.** v14 is a saved, unpublished revision newer than published v13 (origin not checked). |

- Studio's EditPlace launch opens the latest *saved* version, not the latest published one. So any place with a save after its last publish can't be exported live as its published version this way. SC's version stayed 103 across the open, so opening a place doesn't by itself seem to create a new version.
- All four matching `.rbxl` copies already exist (`playtest-lobby-v251`, `playtest-lantern_grove-v25`, `playtest-sugarloaf_canyon-v103`, `playtest-aurora_archipelago-v13`). No new `.rbxl` was created. Exporting from those local copies (opened as local files, never saved) would give the published lobby/LG/AU scripts, but the brief said to record and skip, so I didn't do that.
- Each Studio was quit with an AppleScript quit and closed within 2 to 8 s, with no save prompt (osascript printed a harmless "User canceled (-128)"). `pgrep -x RobloxStudio` was empty before each next open and at the end. Only the StudioMCP bridge processes remain.

## Drift
SC v103 vs `src`: `ServerStorage/CourseData/AuroraBatch3.luau` (src has the au7 h18 lantern cage update) and `ServerStorage/CourseData/PropPlacements.luau` (SC has 8 extra LG rail lantern entries that lg14 removed from src). See `exports/script-diff.md`.

EXPORT DONE, STUDIO CLOSED

## exp2
Oct 15, 2026, about 00:12 to 00:27 PT, Mac Mini, Claude Code (Opus 5.5). This finishes the three places exp1 skipped. Each was exported from the File-downloaded copy of its published version, not the cloud place. One Studio at a time, Edit-mode reads only, no edits to place content. Nothing saved or published, no permissions granted, PC not used. `src/` and `tools/` weren't modified.

Steps for each: copy `playtest/playtest-<role>-v<N>.rbxl` to `/tmp/exp2/<role>.rbxl`, run `open -a /Applications/RobloxStudio.app <copy>`, check that `list_roblox_studios` shows exactly one studio named `<role>.rbxl` and read `PlaceRole`, then `GOLF_STUDIO=<role>.rbxl GOLF_EXPORT_DIR=exports/<role>-v<N>/src python3 tools/run_playtests.py export`, write the manifest (same format as SC v103, plus `source`, `studioPlaceId`, `rbxlCopy.openedCopy`/`note`), and quit.

| Place | Source (repo copy, sha256) | Studio read | Result |
|---|---|---|---|
| lobby v251 | `playtest-lobby-v251.rbxl` `a0ebd0432bbf701d096e0dd4adf93113c2527b7dc559ec71a7973443963ca241` (870,467 B) | PlaceRole lobby, PlaceId 0, PlaceVersion 0 (local file) | **EXPORTED** `exports/lobby-v251/`: 58 scripts, 1,750,959 B. 376 BaseParts, 320 MeshParts, no terrain cells. |
| lantern_grove v25 | `playtest-lantern_grove-v25.rbxl` `5f6abe225eb021a2fbd991e867af40991c2b99574134bde2bdb744ec86374ab0` (3,474,151 B) | PlaceRole lantern_grove, 0 / 0 | **EXPORTED** `exports/lantern_grove-v25/`: 59 scripts, 1,759,148 B. 3,785 BaseParts, 2,525 MeshParts, terrain present. |
| aurora_archipelago v13 | `playtest-aurora_archipelago-v13.rbxl` `c662d2674959315f00c329129e8b33c0b979e0673933424fd1c5cb33a8041352` (1,422,186 B) | PlaceRole aurora_archipelago, 0 / 0 | **EXPORTED** `exports/aurora_archipelago-v13/`: 59 scripts, 1,760,039 B. 1,851 BaseParts, 406 MeshParts, no terrain cells. |

- A local file has no PlaceVersion (it reads 0), so each version comes from the downloaded file's name, backed by the recorded sha256.
- On the first cold `open -a`, Studio came up on the start page without loading the file. A second `open -a` with the same file loaded it. LG and AU loaded on the first try.
- On every quit, Studio showed "Save changes to <role>.rbxl?" (Save / Don't Save / Cancel; export's Edit-mode Luau marks the file dirty). It was never answered: the AppleScript quit got "User canceled (-128)", TERM didn't close it, and `pkill -KILL` did, which discards. `pgrep -x RobloxStudio` was empty before each next open and at the end. The `/tmp/exp2` copies and the three repo `.rbxl` files hash the same as before (`shasum -c` OK).

### Drift (details in `exports/script-diff.md`)
No place matches `src` byte for byte, and no two places match each other. 50 of 59 scripts are identical everywhere. The 9 that drift are `AuroraVisualCleanup` (missing from lobby), `AuroraEffects`, `PropsBuilder`, `VisualSeparation`, `CourseBuilder`, `CourseData/SugarloafCanyon`, `GolfClient/GolfTest`, `CourseData/AuroraBatch3` and `CourseData/PropPlacements`. Each place has its own course's latest data, but older copies of the other courses' data and shared builders. The lobby v251 is oldest (pre-au5/lg13/au6/sc11). Shared client scripts (VRControls, HUD, FrontEnd, BallController…) are identical in all four places.

EXPORT DONE, STUDIO CLOSED
