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
