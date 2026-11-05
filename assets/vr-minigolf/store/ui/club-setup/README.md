# VR Club Setup UI

Parchment + brass how-to card and amber/gold/cream icons for the VR club-angle setup mode. Style matches `../wrist/`.

## Files

| File | Size | Notes |
|------|------|-------|
| `howto_card_bg.png` | 1024×784 | Empty card: brass frame, parchment, 3 stacked panels with left icon circles. **No baked text.** |
| `howto_mock.png` | 1024×784 | Layout reference with example SurfaceGui text + icons. Not for in-game. |
| `step1_stance.png` | 256×256 | Transparent. Golfer putting stance, club head on ground. |
| `step2_stick.png` | 256×256 | Transparent. Thumbstick with 4-way arrows. |
| `step3_trigger.png` | 256×256 | Transparent. Trigger pull + check. |
| `icon_reset.png` | 256×256 | Transparent. Circular arrow (reset to default). |
| `ground_marker.png` | 256×256 | Transparent. Glowing amber ring + crosshair for under the club head. |
| `club_setup_sheet.jpg` | 1400×1100 | QA contact sheet. |
| `_build.py` | — | Regenerates all of the above (PIL only). |

## 9-slice / slice margins

**`howto_card_bg.png`**

- Suggested 9-slice margins: **64 px** on all sides (clears corner radius ~56 and rivets at ~25).
- Do **not** 9-slice vertically through the three panels if you need the icon circles to stay round — prefer fixed size, or stretch only the outer brass with a ScreenGui/SurfaceGui ImageLabel and keep panels as separate overlays.
- Brass outer starts ~8 px in; parchment inner starts ~42 px in.

**Icons / marker** — no 9-slice; use as ImageLabels at fixed aspect 1:1.

**`ground_marker.png`** — place as a Decal/Texture or BillboardGui on the ground under the club head; keep world size roughly 0.4–0.6 studs so the ring reads in VR.

## Panel layout (pixel coords on 1024×784)

| Panel | Bounds (x0,y0,x1,y1) | Icon circle center |
|-------|----------------------|--------------------|
| step1 | 72, 68 → 952, 272 | (182, 170), r≈78 |
| step2 | 72, 290 → 952, 494 | (182, 392), r≈78 |
| step3 | 72, 512 → 952, 716 | (182, 614), r≈78 |

Place each step icon (~140×140) centered in the circle. Put SurfaceGui text to the right of the circle (x ≈ 284).

## Suggested SurfaceGui text sizes

Card is designed for a SurfaceGui of about **1024×784** studs-mapped pixels (or scaled equivalently). At that resolution:

| Role | Size | Color | Notes |
|------|------|-------|-------|
| Step labels | **56–64 px** Bold | `#3B2412` | Uppercase. Wrap to 2–3 lines if needed. |
| Reset hint (`B: reset`) | **40–48 px** Bold | `#9C5218` | Bottom-right of step3 panel; pair with `icon_reset` at ~44 px. |
| Optional title | **72–80 px** Bold | `#3B2412` | Only if you add a header strip later. |

Font used in the mock: Fredoka Bold (same as wrist mock). Any bold rounded sans is fine in-game.

## Colors (match wrist)

- Outline / body text: `#3B2412` / `(74,40,18)` halo on icons  
- Amber: `(232,140,40)` · Gold: `(250,196,70)` · Cream: `(255,240,210)`  
- Parchment: `(250,232,198)` · Brass dark/light: `(122,78,30)` / `(246,206,120)`

## In-mode copy (example)

1. STAND LIKE YOU'RE PUTTING  
2. NUDGE THE CLUB HEAD WITH THE STICK  
3. PULL TRIGGER TO SAVE  
- B: reset  

Rebuild: `python3 _build.py` from this folder.
