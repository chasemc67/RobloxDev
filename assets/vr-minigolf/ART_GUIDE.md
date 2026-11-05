# VR Mini Golf — Final 2D Art Guide

Rule of thumb: fixes landed in **new folders**; originals were never overwritten. Prefer the newest **approved** folder. Paths are under `/workspace/RobloxDev/assets/vr-minigolf/` unless noted. 3D meshes are out of scope except one note.

---

## Lobby

**Final**
- `lobby/concept_C_boardwalk.png` (+ `layout_C_boardwalk.png`) — approved lobby: Golden Hour Boardwalk (option C).
- `lobby/vignettes/LG2.png`, `SL1.png`, `AU2.png` — approved backdrop concepts (root = post-pass2 views).
- `lobby/backdrops/fbx/bd_lg2_lantern_grove.fbx` — LG2 build (see `backdrops/README.md`).
- `lobby/backdrops/fbx/bd_sl1_sugarloaf_canyon.fbx` — **SL1 pass 3** (approved import).
- `lobby/backdrops/fbx/bd_au2_aurora_archipelago.fbx` — AU2 build.
- `lobby/backdrops/previews/{LG2,SL1,AU2}_boardwalk_eye.png` — eye-height previews for those builds.
- `lobby/portal_textures/portal_{lantern_grove,sugarloaf,aurora}.png` + `portal_rim_glow.png` — scroll/swirl portal panels.
- `lobby/portal_surfaces/portal_surface_*.png` — solid portal face fills.
- `lobby/portal_*.png` — course portal hero art (lantern / sugarloaf / aurora).
- `store/ui/card_lanterngrove_v2.png`, `card_sugarloafcanyon_v2.png`, `card_auroraarchipelago_v2.png` — live course board cards.
- `store/ui/title_bg_v2.png` — title background.

**Superseded / ignore**
- `lobby/concept_A_*`, `concept_B_*`, `options/A_*`, `options/B_*` — unused lobby pitches.
- `lobby/vignettes/pass1/`, `pass2/` — early vignette framing.
- `lobby/backdrops/_backup_pass*`, `fbx_pass4/`, `fbx_pass5/`, `previews_pass4/`, `previews_pass5/` — SL1 pass 4/5 were review-only; pass 3 stays final.
- `store/ui/card_soon_*`, `card_lanterngrove_A/B.png` — coming-soon / older card art.
- `store/ui/title_bg.png` (non-v2), `store/ui/wrist/wrist_card_bg.png` — older than `ui/wrist/`.

---

## UI (shared)

**Final**
- `ui/wrist/wrist_card_bg_nobuttons.png` — wrist HUD card (text drawn live). Mock: `wrist_card_mock_nobuttons.png`.
- `store/ui/wrist/icon_hole.png, icon_par.png, icon_total.png, icon_best.png`, `pointer_dot.png`, `menu_hover_glow.png` — wrist icons.
- `ui/scorecard/settings_button.png` (+ `_pressed`) — scorecard gear.
- `ui/menu/menu_frame.png`, `menu_button.png`, `close_x.png` — and root `menu_frame_9slice.png`.
- `ui/loading/loading_{lantern_grove,sugarloaf,aurora}.png` — course loading screens (+ `loading_contact_sheet.png`).

**Superseded / ignore**
- `/workspace/gameart/vr-minigolf/loading/` — early LG/SC/AU loading gens.
- `/workspace/gameart/vr-minigolf/round1/` — round-1 concepts, holes, video; historical only.

---

## Lantern Grove

**Final**
- `lantern-grove/h01-concept.png` … `h09-concept.png` (+ `holes_concepts_sheet.jpg`, `course-map.png`) — hole concepts.
- `lantern-grove/h0N-layout.png` — top-down layouts.
- `lantern-grove/textures/slope_felt_{A,B,C}.png` (+ `_tile2x2`) — felt options; **C** is newest candidate (`slope_sheet.jpg`).
- `lantern-grove/textures/h05_disc/h05_disc_color.png` + `h05_disc_glow_mask.png` — disc textures (see Gaps).
- `lantern-grove/store/{T1–T4,I1–I4}.png` — store thumbs/icons (+ sheets).
- `lantern-grove/_ref/C08-lantern-grove.png`, `C08n-*-night.png`, `L05-overview-*.png` — style refs.

**Superseded / ignore**
- `lantern-grove/_work/` — older concept passes (v1/v2/r4/r5).
- `lantern-grove/store/_raw/` — raw gens before cleanup.

---

## Sugarloaf Canyon

**Final**
- `sugarloaf-canyon/h01-concept.png` … `h18-concept.png` (+ `holes_concepts_sheet.jpg`, `course-map.png`) — hole concepts.
- `sugarloaf-canyon/h0N-layout.png` — layouts.
- `sugarloaf-canyon/decals/` — **all live course decals** (signs, felt/route arrows, teleport pads). Preview: `decals/decals_preview.png` (+ `decal-sheet.png`, `manifest.json`).
- `sugarloaf-canyon/silhouettes/sheet01–05-*.png` (+ `contact.jpg`) — prop silhouette sheets (not the bak- backup).
- 3D only: hole 16 rim final is `models/fbx/h16_rim_2slot_d/` (not 2D).

**Superseded / ignore**
- `sugarloaf-canyon/_work/superseded/`, `_work/redesign-superseded/`, `_work/p7*`, `p8/`, `p9/` work dumps — older concepts.
- `silhouettes/bak-20261012-1925/` — old silhouette sheets.
- `/workspace/gameart/sc-decals/` — generator scratch; use `sugarloaf-canyon/decals/` instead.
- Older rim folders `h16_rim_2slot`, `_b`, `_c` — superseded by `_d`.

---

## Aurora Archipelago

**Final**
- `aurora-archipelago/h01-concept.png` … `h18-concept.png` (+ `holes_concepts_sheet.jpg`, `course-map.png`, `contact-sheet.jpg`) — hole concepts.
- `aurora-archipelago/h0N-layout.png` — layouts.
- `ui/loading-cards/aurora_loading_card.png` — extra Aurora loading card variant.

**Superseded / ignore**
- `aurora-archipelago/_work/` — work dumps.
- `holes_layouts_sheet.jpg.bak-*` — layout-sheet backup.

---

## Gaps (art side)

1. **No `decals/` for Lantern Grove or Aurora** — only Sugarloaf has a finished in-course decal pack.
2. **`ui/loading-cards/`** only has Aurora; LG/SC live under `ui/loading/` instead (folder incomplete).
3. **LG hole 5 disc** — `textures/h05_disc/` exists but is flagged wrong in-game; needs a replacement pass.
4. **TRADING POST board** — no dedicated 2D board texture here; board raise is a 3D/place fix (`trading_post_deck` mesh). Confirm look in sc10 once live.
5. **Slope felt A/B/C** — which variant is live in Lantern Grove is unclear from folders alone; confirm in Studio.
6. **SL1 pass 4/5** — left on disk as candidates; do not import over pass 3 unless Chase re-approves.
