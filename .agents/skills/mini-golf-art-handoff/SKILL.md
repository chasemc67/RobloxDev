---
name: mini-golf-art-handoff
description: Art direction for a mini-golf course (VR or desktop), the 2D-to-3D handoff to the modeling bot, and visual acceptance of the built meshes. Covers style options, the style sheet, when to paint over, what every 3D handoff sheet must contain, approval states, mesh review notes and where chosen art goes in the repo. Use when choosing or changing a course's look, writing or reviewing a handoff for 3D Model Bot, or reviewing imported art in Studio. Not for gameplay simulation, playtesting, Blender modeling technique (see blender-asset-pipeline) or publishing.
---

# Mini-golf art direction, 3D handoff and visual acceptance

## Roles
| Who | Owns |
|---|---|
| Game Art Bot | style options, the chosen 2D assets, handoff sheets, art review |
| 3D Model Bot | editable Blender sources (`.blend`) and exports |
| RobloxDevBot | import, implementation in Studio, publishing |
| Playtest Bot | gameplay validation |

**Art approval is not playtest acceptance and not a publish.** Never report a course as "done" from an art review alone.

## 1. Pick a look (once per course)
- Make **three distinct style options**, never more. Chase picks one (or asks for a mix).
- For the chosen look, make **one style sheet** and **at most one hero vista**. No painting per hole.
- The style sheet fixes: palette (swatches with RGB/hex), materials, lighting mood, shape language, prop scale next to a 5-stud player, and VR comfort notes (no flicker, no DepthOfField, nothing bright filling the view).
- Treat lighting values on the sheet as starting points to tune in Studio and a headset, not as fixed numbers.
- Original, Roblox-friendly art only. No copies of trademarked ships, characters, logos or other games' assets.

## 2. Art follows the layout, not the other way round
- Start from the dimensioned layout (holes in studs) and a blockout that has already been accepted for play. For VR Mini Golf, that order is in `games/vr-mini-golf/AGENTS.md` ("Order for a new course").
- After blockout acceptance, **paint over eye-height renders** only for hero vistas and gimmick holes.
- Felt, rails, cups and other collision geometry are gameplay. Art never provides a playing surface and never changes authored gameplay values (sizes, heights, clearances, physics). Decorative polish that conflicts with them loses.
- Don't make fly-through videos or a concept painting per hole unless Chase asks.

## 3. The 3D handoff sheet
One sheet (or one section of `handoff.md`) per mesh or prop group. Use this template:

```markdown
## <asset name>  (status: draft | ready for 3D | approved | revise)
Owner now: <bot>   Next step: <what, by whom>
Sheet: assets/<game>/concepts/<round>/<file>.png
Style: <look name>, style sheet assets/<game>/concepts/<round>/<file>.png

Views: front / side / top silhouettes on the sheet
Shape notes: <3-6 short lines: key forms, what must read from the tee>
Dimensions (studs): W x L x H = ...   [authored | inferred | proposed] for each number
Triangle budget: <n> per mesh (hard cap 20k; split into parts as listed)
Parts / materials: <part> = <material>, RGB (...)  (one mesh per recolourable colour)
Glow: <which parts are emissive/Neon, colour, any light to add>
Placement: <where it sits, facing, clearance from pads/felt in studs>
Collision: none (decor) | <what collides, owned by layout data>
Open questions: <numbered>
```

- **Mark every dimension's source.** *Authored* = from the layout data or a number Chase approved. *Inferred* = measured off the concept. *Proposed* = your guess. The concept image shows the look; it is not proof of hidden or off-screen geometry, and it may draw things at the wrong scale. When the sheet and the layout disagree, the layout wins and the conflict goes in Open questions.
- Keep VR scale practical: check props against a 5-stud player and the tee eye height, not against how big they look in the painting.

## 4. Visual acceptance (after import)
- Review in Studio at the **actual tee eye height**, for every hole the asset is visible from: does it read, does it block the sightline to the flag/cup, does the felt stay clearly the brightest, highest-contrast surface?
- Send mesh review notes **once per pass, batched and numbered** (`1. hull: stern rail 2 studs too tall, blocks pad 1 sightline`). No drip-fed notes mid-pass.
- Far scenery gets **one restrained pass**: atmosphere/haze hides fine detail, so don't polish it.
- Record the result explicitly in the handoff: `approved`, or `revise` with the numbered notes and the owner of each fix.

## 5. Where art lives (check `.gitignore` and AGENTS.md "What to commit" before adding)
- Chosen art goes in the repo under `assets/<game>/`, in art folders: `concepts/`, `textures/`, `ui/`, `icons/`, `marketing/`, `thumbnails/`, plus chosen final renders in `final/`. A handoff that only points at a temporary workspace path is not finished; copy the chosen files in and cite repo paths.
- `.blend` is the 3D source (Git LFS). `.fbx` is derived build output and gitignored; re-export it from the `.blend`.
- Never commit preview/iteration screenshots (`previews/`, `screens/`, `shots*/`), logs or videos.

## Handoff checklist
- [ ] Look chosen by Chase (or status says "options, not final").
- [ ] Layout/blockout accepted before any paintover or final-mesh sheet.
- [ ] Each sheet: front/side/top silhouettes, shape notes, dimensions in studs with source tags, triangle budget, parts/colours, glow, placement, collision.
- [ ] No art provides a playing surface; gameplay values untouched.
- [ ] Paths are repo paths; status (draft / ready / approved / revise), current owner and next step stated.
- [ ] Review notes batched and numbered; far scenery reviewed once.
- [ ] Nothing reported as playtested or published from art review alone.
