# Pass 1 summary: Golden Hour Boardwalk lobby props (SRV-137)

2026-10-11 21:27, Windows PC, Blender 5.2.2 LTS (Cycles OptiX for previews).

* **Exported:** 29 FBX matching the builder `assetName`s exactly (no `bw_course_card_plane`), shared atlas
  `textures/bw_atlas_1024.png`, `manifest.json` (props, 242 instances, totals).
* **Fit check:** RESULT: ALL PASS. Bbox within 10% of spec for all 29, every mesh < 20k, card faces at X -8/0/+8, Y 5.5,
  inset 0.15, normal +Z; arch openings >= 10 x 12 (Lantern Grove 10.18 x
  12.42, Sugarloaf 10.08 x
  12.20, Aurora 10.12 x
  12.44); pivots at base centre (blades at hub); spawn
  10-stud radius free of props; nothing above the bumper on the practice tee->cup lines except the windmill.
* **Tris:** lobby 48,656 (limit 120k, target ~115k). Deck 1,520 (10 per tile), railing 9,324
  (222 per section), arches 12,490, shack 3,754,
  canopy 5,600.
* **Art notes applied (OVERRIDE 3):** deck strip has seeded per-plank value/hue jitter around #B5835A with a few
  #7A4E2D-leaning boards, and tiles A/B sample different U halves; `bw_rock_arch` is the backdrop hero (one clean
  swept arch with a clear opening, smooth chunky section, warm vertex-colour bands), sea stacks kept simpler.
* **Review fixes during the pass:** Sugarloaf rebuilt after comparing with concept_arches.png (chunky tapered
  faceted towers, ~4 wide bands, crenellated block lintel instead of thin striped tubes); portrait card/panel faces
  use plain parchment (the bordered cell stretched); the builder's 8-stud pier row and pier rail ends are scaled
  per instance.
* **Open questions:** 10 in README "Spec questions for Game Art Bot". The ones that need action:
  leaderboard yaw (-90 faces west with a +Z front), blade hub Y 7.4, canopy Y 10 floats, string-light span vs
  posts.
* **Renders:** previews/props/*.png, previews/contact_sheet.png, previews/spawn_view.png, previews/topdown.png,
  previews/overview.png.
