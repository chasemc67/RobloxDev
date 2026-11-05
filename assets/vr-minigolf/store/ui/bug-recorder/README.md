# VR Bug Recorder UI

Parchment + brass cards and amber/gold/cream icons for the in-game bug recorder (trigger, tags, toast, My Reports list, replay controls). Style matches `../club-setup/` and `../wrist/`.

Drawn crisp with PIL (`_build.py`). Rebuild: `python3 _build.py` from this folder.

## Files

| File | Size | Notes |
|------|------|-------|
| `icon_bug_button.png` | 512×512 | Transparent. Phone bug button + VR hint. Bug on amber badge with red ! |
| `rec_dot.png` | 256×256 | Transparent. Pulsing red live-record dot (glow rings). |
| `rec_badge.png` | 512×160 | Dark red pill with live dot + **REC 5s** cream text. |
| `rec_indicator.png` | 640×180 | Convenience strip: `rec_dot` + `rec_badge` side by side. |
| `tag_physics.png` | 256×256 | Transparent. Golf ball + motion arcs. |
| `tag_club.png` | 256×256 | Transparent. Putter shaft + head. |
| `tag_camera.png` | 256×256 | Transparent. Camera / viewfinder. |
| `tag_ui.png` | 256×256 | Transparent. Window panel with title bar. |
| `tag_other.png` | 256×256 | Transparent. Ellipsis in circle. |
| `toast_report_saved.png` | 720×160 | Brass + parchment toast with green check + **REPORT SAVED**. |
| `reports_list_bg.png` | 1024×784 | Empty My Reports card: header band + 4 row slots (icon circle + time chip). **No baked text.** |
| `reports_list_mock.png` | 1024×784 | Layout reference with sample rows. Not for in-game. |
| `ctrl_play.png` | 256×256 | Transparent. Play triangle in amber circle. |
| `ctrl_pause.png` | 256×256 | Transparent. Pause bars. |
| `ctrl_slowmo.png` | 256×256 | Transparent. Clock + ½ badge. |
| `ctrl_scrub.png` | 768×96 | Scrub track with thumb (~40% filled). |
| `ctrl_freecam.png` | 256×256 | Transparent. Camera + N/S/E/W free-move arrows. |
| `replay_bar_mock.png` | 1600×200 | Composite replay bar reference. Not for in-game. |
| `bug_recorder_sheet.jpg` | 1800×2200 | QA contact sheet. |
| `mock_composite.jpg` | 1800×2200 | Same as sheet (alias for deliverable name). |
| `_build.py` | — | Regenerates all of the above (PIL only). |

## 9-slice / layout

**`reports_list_bg.png` (1024×784)**

- Suggested 9-slice margins: **64 px** all sides (clears corner radius ~56 and rivets ~25).
- Brass outer ~8 px in; parchment inner ~42 px in.
- Prefer fixed size for the list card; don't 9-slice through row slots if icon circles must stay round.

| Zone | Bounds (x0,y0,x1,y1) | Notes |
|------|----------------------|-------|
| header | 72, 80 → 952, 152 | Title SurfaceGui text |
| row0 | 72, 168 → 952, ~291 | Icon circle left, time chip right |
| row1–row3 | stacked below with 16 px gap | Same structure |

Icon circle radius ≈42, center x ≈142. Place tag icons ~72×72 centered in the circle. Row title text to the right (~x 200), `#3B2412`, **56 px** Bold uppercase. Time chip on the right.

**Icons / controls** — no 9-slice; ImageLabels at fixed 1:1 (or scrub at 8:1).

**`toast_report_saved.png`** — BillboardGui / ScreenGui overlay; keep aspect 720:160.

**`rec_badge` / `rec_indicator`** — HUD overlay while recording (post-trigger countdown).

## Suggested SurfaceGui / ScreenGui text

| Role | Size | Color | Notes |
|------|------|-------|-------|
| List / toast labels | **56–64 px** Bold | `#3B2412` | Uppercase. Cream `#FFF4DC` 2 px stroke if drawn in code. |
| Row meta / tags | **32–40 px** Bold | `#9C5218` | `#tag` + relative time |
| REC badge text | baked in asset | cream on dark red | Or override countdown in code |

Font used in mocks: Fredoka Bold (same as club-setup / wrist).

## Colors (match club-setup / wrist)

- Outline / body text: `#3B2412` · cream stroke: `#FFF4DC`
- Amber `(232,140,40)` · Gold `(250,196,70)` · Cream `(255,240,210)`
- Parchment `(250,232,198)` · Brass dark/light `(122,78,30)` / `(246,206,120)`
- Record red `(220,48,48)`

## Intended wiring (for RobloxDevBot)

1. **Trigger:** phone ImageButton ← `icon_bug_button`; VR hold-X/Y hint can reuse it small.
2. **While capturing post-trigger:** show `rec_indicator` (or `rec_dot` + `rec_badge` with live seconds).
3. **Tag picker:** five ImageButtons ← `tag_*`.
4. **On save:** flash `toast_report_saved`.
5. **Settings → My reports:** SurfaceGui on `reports_list_bg`; rows filled at runtime.
6. **Replay viewer:** `ctrl_play` / `ctrl_pause` / `ctrl_slowmo` / `ctrl_scrub` / `ctrl_freecam`.

Hand-off path: `/workspace/RobloxDev/assets/vr-minigolf/store/ui/bug-recorder/`
