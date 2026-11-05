# Aurora Archipelago: gimmick-hole paint-overs (Oct 12 2026)

Base: 3D Model Bot's blockout tee renders (`../previews/blockout/hNN_tee.png`), same camera. Style refs: `../hNN-concept.png`, course.md, AU2 backdrop.
Tool: `/workspace/gameart/tools/gen-image.mjs`, model openai/gpt-image-2.5-sunburst, image-to-image (`run.sh hNN [suffix] [extra]`).
Side-by-side check: `contact.jpg` (blockout left, paint right). Mood and material direction only. **Geometry and colliders come from holes.json and the blockout, not from these images.**

| Hole | Mechanism | File | Takes | Notes |
|---|---|---|---|---|
| H05 Geyser Hop | slide (geyser lift) | h05_paint.png | 1 | Lift shown as an ice/steam column with a basalt cap |
| H09 Conch Shortcut | teleport | h09_paint.png | 1 | No moving part. Conch shells not painted in, because the blockout has none yet |
| H11 Floe Drift | slide (ice floe) | h11_paint.png | 3 | v1 and v2 turned the floe into water. v3 keeps it as a raised ice slab |
| H12 Icebreaker Wheel | rotate (paddle wheel) | h12_paint.png | 2 | v1 put an ice disc where the sweep volume was. v2 is clean |
| H13 Snowpuff Carousel | rotate (sweeper) | h13_paint.png | 2 | v1 lost the arms. v2 has sleds on the hub, but the arms read low and small |
| H14 Bell Buoy | swing (pendulum) | h14_paint.png | 2 | v1 painted a lantern-drum. v2 has a brass bell under a timber gantry |
| H17 Aurora Bridge | toggle (light bridge) | h17_paint.png | 2 | v1 lost the bridge. v2 shows a faint aurora ribbon in the middle channel |

Rejected takes are in `_rejected/`. Cost is in `cost.json`.
Remaining drift (paint only, does not affect the build): background islands and lanterns are invented; rails are drawn as thicker snowy timber than the blockout; the sweep volumes are removed by design.
