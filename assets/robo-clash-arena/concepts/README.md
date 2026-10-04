# Robo Clash Arena — modeling references

Clean references for Blender (low-to-mid poly, chunky, Roblox-friendly). Every sheet was generated with `google/gemini-3-pro-image` (Nano Banana Pro) using the round-1 concept as the reference image, then checked against that concept. Palettes were sampled from the concept pixels with k-means / hue medians, not picked by eye.

Source concepts:

- C01 Scout: `/workspace/gameart/round1/characters/C01-robot-scout.png`
- C05 Aerial: `/workspace/gameart/round1/characters/C05-robot-aerial.png`
- R05 Yokai spirit: `/workspace/gameart/round1/characters/R05-yokai-spirit.png`
- S04 Homework Desk: `/workspace/gameart/round1/stages/S04-homework-desk.png`

`.json` files next to the images are generation metadata (model, cost, prompt). Ignore them for modeling.

## Characters

### c01 — Scout robot

- `c01-turnaround.png` — front, right side, back. Orthographic, same scale, feet on one line, plain grey. This is the cleanest of the three turnarounds: the side view is a real profile and the colors match the concept.
- `c01-parts.png` — twin-barrel blaster, sticky-mine launcher (plus one loose mine), one drone pod, the helmet, and one roller foot. Each from two angles.
- `c01-palette.png`, `c01-palette.md` — six swatches.

Modeler notes: about 3 heads tall; the head with its ear fins is roughly a third of the height. Reverse-joint legs end in two-wheel roller skates. Right arm is the twin blaster, left forearm is the mine launcher, two eyed drone pods sit on short arms off the back. Black is only the joints, the faceplate and the muzzles. Keep the visor as one horizontal slit, not two eyes.

### c05 — Aerial hover robot

- `c05-turnaround.png` — front, side, back, same scale, hovering.
- `c05-parts.png` — forearm cannon, one ducted fan, the six-bomb clamshell, one eye drone, one hover foot. Each from two angles.
- `c05-palette.png`, `c05-palette.md` — seven swatches.

Modeler notes: about 3 heads tall and nearly as wide as it is tall once the fans are included. No knees bent into a run; both feet hang level with a thruster ring under each. Right arm is the straight forearm cannon (no pistol grip), left arm is the open clamshell of six yellow spheres. Two big fans on the shoulders, three small eye drones behind them, one short antenna. Compromise: the middle view is still a three-quarter, not a true profile, after three attempts, and the back view invents a vent panel the concept never showed. Trust the front view plus `c05-parts.png` where they disagree.

### r05 — Yokai fox-mask spirit

- `r05-turnaround.png` — front, right profile, back. Floating, no legs.
- `r05-parts.png` — kitsune mask, paper-lantern cannon, paper-talisman box launcher, one flame lantern pod, the spirit-flame tail. Each from two angles.
- `r05-palette.png`, `r05-palette.md` — eight swatches.

Modeler notes: the mask plus ears is about a third of the height. There are no legs; the lower body is one pale-blue flame tail. Right hand holds the large lantern cannon (longer than the torso), left hand holds the smaller talisman launcher. Three black-and-gold flame pods ride the shoulders and back. Compromise: the turnaround draws the left-hand launcher too small. Use `r05-parts.png` for its real size and shape. The red markings are paint, not separate geometry.

## Stage S04 — Homework Desk

- `s04-hero.png` — the round-1 concept itself, copied unchanged, so it matches exactly. 3/4 gameplay view of the playset on a desk. The lamp, pencil cup, books and the two fighters are scene dressing, not part of the blockout.
- `s04-topdown.png` — near-overhead plan of the playset with a floor grid. Use this for the blockout.
- `s04-palette.png`, `s04-palette.md` — seven swatches, brighter-half medians of the lit faces so shadow doesn't darken them.

Layout, inner mat first: a rounded green grid mat with a yellow circle and star in the middle, ringed by a low fence of red, blue, yellow and green blocks with round corner posts. Cover, roughly where the plan puts them: pink eraser lower-left; blue tunnel building upper-left with a small tree on its roof; a plain yellow ruler used as a bridge from that building toward center; a yellow sticky-note cube just above the star; one grey crate below the star; one blue block right of the star; a red fort on the right with crayons on the roof and one red ramp; a small tree and an orange flag inside the fence at the lower-right.

Modeler notes: the inner mat is about 10 to 12 robot-widths across, so fights stay close. The fence is about knee height. The eraser, the note cube and the crates are about one robot tall; the two buildings are about two robots tall. Compromise: the plan is not perfectly orthographic (a little of each side face still shows), and it keeps one extra grey crate up against the top fence and an extra blue vertical piece on the left that are not distinct in the hero shot. Drop those two if you want the strict hero layout. The ruler is a blank yellow bar on purpose; the generated version had printed numerals and they were removed.

## Textures (`textures/`, 1024x1024, tileable)

Checked as a 2x2 repeat.

- `desk-wood.png` — light oak for the desk. The generated photo had a visible seam, so this one was rebuilt as periodic grain in the same oak. No seam in the 2x2.
- `paper-grid-mat.png` — mint grid for the play mat. The generated image already tiled; left/right edge difference is about 1 level.
- `plastic.png` — glossy red toy plastic for the blocks. The first version was a beveled tile with grout lines, so it was cropped to the flat face and edge-blended. Tint it for the blue, yellow, green and pink blocks rather than making more textures.

## Spend

About **$2.37** for this set (gateway balance $71.69 to $69.32), including the regenerations. Well under the $8 budget.
