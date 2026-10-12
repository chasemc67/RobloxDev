# Wrist card (no buttons) + scorecard settings button
Preview: `wrist_scorecard_preview.jpg`. All of these are procedural PIL (`wrist/_build.py`, `scorecard/_build.py`), cost $0.

## wrist/
- `wrist_card_bg_nobuttons.png`: 1024×784 RGBA, the brass + parchment card with no MENU/SCORES buttons. Its size matches the bracer Top canvas (1024×784, status.md). The layout is left-right symmetric, so **one file works on both wrists**. There's no mirrored copy, because mirroring would only flip the art and the text is drawn on top live.
- `wrist_card_mock_nobuttons.png`: the same card with sample text, for reference only.
- Text zones in px (SurfaceGui on a 1024×784 canvas): header 80,72–944,212; PAR 80,236–498,459; STROKE 526,236–944,459; TOTAL 80,481–498,704; BEST 526,481–944,704. Icon circle at zone x+22..134, y+55..167.
- Text sizes are unchanged from v1 (Fredoka Bold): hole title 76 px, course name 40, labels 38, values 78. Colors: values #4A240E, labels #9C5218. Icons: reuse `store/ui/wrist/icon_*.png` at 96 px (hole flag at 100).

## scorecard/
- `settings_button.png` / `settings_button_pressed.png`: 256×256 RGBA, a cream gear on the same round wood + brass badge as `ui/menu/menu_button.png` and `close_x.png`. In the pressed state the badge drops 10 px with a smaller shadow and is about 18% darker. Readable down to 64 px.
- Use an ImageButton with Image = normal and PressedImage = pressed (HoverImage can stay normal, or add `store/ui/wrist/menu_hover_glow.png` behind it for VR laser hover). Put it in the scorecard header's top-right corner at 64–96 px on phones, or ~0.12 studs on the world panel. Clicking it opens the settings menu (`ui/menu/menu_frame.png`).
