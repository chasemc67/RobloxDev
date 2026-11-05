"""Write README.md and _src/pass1_summary.md from manifest.json + fitcheck results.  python -I make_docs.py"""
import os, json, time

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
man = json.load(open(os.path.join(OUT, "manifest.json")))
fit = open(os.path.join(SRC, "fitcheck_pass1_validated.txt"), encoding="utf-8").read()
result = fit.strip().splitlines()[-1].split('  (')[0]
P = {p["name"]: p for p in man["props"]}
tot = man["totals"]


def fmt(v):
    return " x ".join(f"{x:g}" for x in v)


rows = []
for p in man["props"]:
    rows.append(f"| `{p['name']}.fbx` | {p['group']} | {fmt([round(x, 2) for x in p['bbox_size_studs']])} | "
                f"{fmt(p['target_size_studs'])} | {p['triangles']} | {p['tris_max']} | {p['builder_count']} | "
                f"{p['tris_x_count']} | {', '.join(p['materials'])} | {p['front'].split(' (')[0].split(' =')[0]} |")
named = []
for p in man["props"]:
    for part in p["parts"]:
        if "__" not in part["mesh"]:
            named.append(f"`{p['name']}` -> `{part['mesh']}`")
cf = P["bw_course_board"]["cardFaces"]
inst_counts = {}
for i in man["instances"]:
    inst_counts[i["asset"]] = inst_counts.get(i["asset"], 0) + 1
deck = sum(P[n]["tris_x_count"] for n in ("bw_deck_plank_a", "bw_deck_plank_b"))
rail = P["bw_railing"]["tris_x_count"]
arches = sum(P[n]["triangles"] for n in ("bw_arch_lantern_grove", "bw_arch_sugarloaf_canyon", "bw_arch_aurora_archipelago"))

QUESTIONS = [
    ("Leaderboard facing", "The brief puts `panel_1..3` on the local +Z (south) face, \"before its -90 yaw\". With "
     "`CFrame.Angles(0, rad(-90), 0)` local +Z turns to world **west** (toward the west rail at X 10), but lobby.json "
     "says the wall faces **east**. I modelled decorative twin parchment panels on the back so both sides read. "
     "Fix options: builder uses yaw **+90** (panels face east), or keep -90 and I move `panel_1..3` to the -Z face "
     "in pass 2. Which one?"),
    ("Windmill blade pivot", "`bw_windmill_blades` pivots at the hub (brief). The builder entry (150, 3.4, 67.3) "
     "looks like a base-centre placement of an 8x8 box; with a hub pivot it must be **(150, 7.4, 67.3)** "
     "(windmill pivot + `blade_hub.local` (0, 7.0, 3.3) in the manifest). Please confirm RobloxDevBot will use the "
     "hub position (the spawn render does)."),
    ("Lantern-tree canopy height", "The builder places `bw_lantern_tree_canopy` with its base at **Y 10**, which "
     "floats it: the mesh includes its trunks (base at local Y 0). Suggest Y -0.1 (on the sand strip). The spawn/top "
     "renders use -0.1."),
    ("Spawn clear radius vs south rail", "lobby.json puts the south deck edge (rail centre line Z 110) exactly 10 "
     "studs from spawn (Z 100), so the railing's inner face sits at **9.7** studs. No placed prop is inside 10. "
     "OK to treat the mandatory edge railing as an exception, or should the spawn move to Z 99.5?"),
    ("Practice green size", "Builder size is 34 x 0.4 x 20 (slab only). The mesh is 34 x **1.2** x 20 because the "
     "bumper rail rises 0.8 above the turf (inside the footprint). The builder must **not** scale it to 0.4 tall."),
    ("String lights span", "`bw_string_lights` is 20 long at Y 7 between X 155..175, but the pier lantern posts are "
     "at X 153 and 177 (24 apart, 7.05 tall). Scale X 1.2 (supported: `scalable: x`) or move the posts to 155/175?"),
    ("Backdrop placement", "`bw_sea_stacks` (Z 210) and `bw_rock_arch` (Z 230) are south of the pier, i.e. behind "
     "the spawn view (which looks north); they frame the sunset view from the pier. Intended? If they should also "
     "read from spawn, a copy north of the sand strip would be needed."),
    ("Budget headroom", f"The lobby lands at **{tot['tris_total']:,}** tris with the builder counts (target ~115k), "
     f"because the deck tile is 10 tris and every hero prop is under its target (arches {arches:,} of 33k). Spend "
     "the ~65k headroom on hero detail in pass 2 (e.g. Sugarloaf / Aurora / shack), or keep the Quest headroom?"),
    ("Neon colours", "`BW_Neon` is #FFC867 everywhere except `bw_arch_aurora_archipelago`, whose `BW_Neon` mesh is "
     "#9FE6F2 (crystal tips). The manifest `parts[].color` carries the colour per file; OK to keep one material name?"),
    ("Board lantern height", "The two Neon lanterns on the course board's side posts put its top at Y 10.75 (spec 10, "
     "within 10%). OK, or lower them into the 10-stud envelope?"),
]

readme = f"""# Golden Hour Boardwalk: lobby props, pass 1 (SRV-137)

Generated {time.strftime('%Y-%m-%d')} on the Windows PC with Blender 5.2.2 LTS. Everything is procedural; rebuild
with the scripts in `_src/` (see Rebuild below). Fit check: **{result.replace('RESULT: ', '')}**
(`_src/fitcheck_pass1_validated.txt`).

* **29 FBX files** in `fbx/`, named exactly like the `assetName`s in RobloxDevBot's `_src/builder_Lobby.luau`.
  `bw_course_card_plane` is **not** exported (OVERRIDE 2: the cards are RobloxDevBot's, the board has 3 recessed
  card faces instead).
* **Lobby total: {tot['tris_total']:,} tris** for {tot['instances']} builder instances (limit 120,000, target ~115k).
  Deck tiles {deck:,} (152 x 10), railings {rail:,} (42 x {P['bw_railing']['triangles']}).
* One shared atlas `textures/bw_atlas_1024.png` (1024x1024, 8-bit RGB, no metadata) and `manifest.json` with
  per-file bbox, tris, materials, pivot, front, motion, collision boxes, the instance list and totals.

## Files

| file | what |
|---|---|
| `fbx/bw_*.fbx` | 29 props (table below) |
| `textures/bw_atlas_1024.png` | shared atlas, layout `_src/atlas_layout.md` / `_src/atlas_def.py` (embedded in every atlas FBX too) |
| `manifest.json` | per-prop data + `instances[]` (from the builder) + `totals` |
| `previews/props/<name>.png` | 3/4 view + eye-height (5 studs) view with a 2x5 reference capsule |
| `previews/contact_sheet.png` | all props, labelled |
| `previews/spawn_view.png` | whole lobby from the spawn: Roblox (100, 5, 100) looking north, 90 deg hfov, golden hour |
| `previews/topdown.png` | orthographic plan of the assembled lobby |
| `previews/overview.png` | extra: elevated view from behind the spawn |
| `_src/` | generators, fit check, renders, logs, `PROGRESS.md`, `pass1_summary.md` |

## Axes, units, pivots

* 1 Blender unit = 1 stud. Import at **scale 1.0**. FBX exported with forward -Z, up Y, transforms applied (every
  object sits at the prop origin with an identity transform), textures embedded.
* Built in Blender Z-up: Blender +Y = Roblox -Z = north, Blender -Y = Roblox +Z = south.
* Every prop is built at **yaw 0 in the lobby.json frame**; the builder's yaw (`CFrame.Angles(0, rad(yaw), 0)`)
  is applied on top. `front` in the manifest says which local side is the viewer side:
  board, leaderboard panels, signpost, arches, nameplates, coming-soon signs, windmill = **+Z (south, toward
  spawn)**; bench and shack = **-Z (north)** so the builder's yaw 180 (benches face south) and yaw 90 (shack
  counter faces west) come out right.
* **Pivot = base centre** (bbox centre X/Z, min Y = 0) for every prop except `bw_windmill_blades`, whose pivot is the
  **hub** (rotation axis = local Z, 6 rpm; hub sits at windmill local (0, 7.0, +3.3)).
* `bw_cup_flag`: the pole is on the pivot axis (place the pivot on the cup centre at turf height Y 0.4).

## Materials and import notes

* `BW_Atlas`: all opaque parts, one MeshPart per FBX (UVs into the shared atlas). `BW_Neon`: emissive parts as their
  own MeshPart: set **Material = Neon** and Color from `parts[].color` (#FFC867; #9FE6F2 on the Aurora arch).
  `BW_Backdrop`: `bw_sea_stacks` / `bw_rock_arch`, vertex colour only, no texture.
* Decoration only: **Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false** on every MeshPart;
  gameplay collision = the manifest `collision[]` boxes (1 box per prop, arches 3: two legs + lintel) or the
  lobby.json colliders. No mesh collision.
* No alpha anywhere. No real lights baked in: the Neon parts are good PointLight hosts (lantern posts, board
  lanterns, shack lanterns, arch lanterns); keep to ~8 PointLights in the lobby.
* Scalable instances (`scalable` in the manifest; builder sizes are honoured as `instances[].scale`): deck tiles in
  X/Z (the 8-stud last pier row), `bw_railing` in X (8-stud pier ends), `bw_string_lights` in X.
* Named faces for SurfaceGui / art: {', '.join(named)}.

### Course board card faces (OVERRIDE 2)
3 flat recessed faces on the south face, each 6 x 8 studs, inset 0.15 behind the brass frame surface (local Z +1.0),
2 tris each, normal +Z. Centres in local Roblox studs from the pivot:

| face | centre [x, y, z] | size | insetDepth | normal |
|---|---|---|---|---|
""" + "\n".join(f"| `{c['name']}` | {c['center']} | {c['size']} | {c['insetDepth']} | {c['normal']} |" for c in cf) + f"""

## Per-file table (bbox in Roblox X x Y x Z studs)

| file | group | bbox | spec | tris | budget | builder count | tris x count | materials | front |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""
| **total** | | | | | | **{tot['instances']}** | **{tot['tris_total']:,}** | | |

## Instance plan

`manifest.instances[]` is RobloxDevBot's `builder_Lobby.luau` placement list verbatim (id, asset, position = base
centre, yaw, size, solid), plus `scale` where the builder size differs on a scalable axis. Counts:
{', '.join(f'{k} x{v}' for k, v in sorted(inst_counts.items(), key=lambda kv: -kv[1]))}.

Budget decision (OVERRIDE): deck tiles are top + 4 sides only (**10 tris**, plank gaps and per-plank tint
jitter live in the atlas deck strip; A and B use different U halves so they don't read as a repeat), railing
sections are {P['bw_railing']['triangles']} tris (<= 350). All other props sit at or under their props.md targets.

## Notes / deviations

* `bw_practice_green`: bbox Y is 1.2 (0.4 slab + bumper 0.8 above the turf); the builder lists the slab only (0.4).
  Don't scale it.
* `bw_lantern_tree_canopy` includes its trunks (base at Y 0). The builder's Y 10 floats it (spawn/top renders use
  Y -0.1).
* `bw_windmill_blades`: place at the hub (150, 7.4, 67.3), not the builder's (150, 3.4, 67.3) (see questions).
* `bw_leaderboard_wall`: decorative twin panels on the back because of the yaw question below.
* Railings: the 10-stud section has its post at the centre and the rope swag dips at the section ends, so
  consecutive sections read as one continuous railing.

## Spec questions for Game Art Bot

""" + "\n".join(f"{k + 1}. **{t}**: {q}" for k, (t, q) in enumerate(QUESTIONS)) + """

## Rebuild

```
python -I _src/make_atlas.py                                        # atlas (Pillow)
_src/run_blender.ps1 -Script _src/build_all.py -ScriptArgs "--group=structure,board,arches,green,social,backdrop"
python -I _src/build_all.py --assemble                              # manifest.json
_src/run_blender.ps1 -Script _src/fitcheck.py                       # -> _src/fitcheck_pass1_validated.txt
_src/run_blender.ps1 -Script _src/render_props.py ; python -I _src/post_previews.py
_src/run_blender.ps1 -Script _src/render_lobby.py                   # spawn_view / overview / topdown
python -I _src/make_docs.py                                         # README.md + _src/pass1_summary.md
```
Library: `_src/bwlib.py` (adapted from the Lantern Grove `lglib.py`, self-contained), `_src/registry.py`,
generators `_src/props_{structure,board,arches,green,social,backdrop}.py`.
"""
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(readme)

summary = f"""# Pass 1 summary: Golden Hour Boardwalk lobby props (SRV-137)

{time.strftime('%Y-%m-%d %H:%M')}, Windows PC, Blender 5.2.2 LTS (Cycles OptiX for previews).

* **Exported:** 29 FBX matching the builder `assetName`s exactly (no `bw_course_card_plane`), shared atlas
  `textures/bw_atlas_1024.png`, `manifest.json` (props, 242 instances, totals).
* **Fit check:** {result}. Bbox within 10% of spec for all 29, every mesh < 20k, card faces at X -8/0/+8, Y 5.5,
  inset 0.15, normal +Z; arch openings >= 10 x 12 (Lantern Grove {P['bw_arch_lantern_grove']['opening_clear']['width']:.2f} x
  {P['bw_arch_lantern_grove']['opening_clear']['height']:.2f}, Sugarloaf {P['bw_arch_sugarloaf_canyon']['opening_clear']['width']:.2f} x
  {P['bw_arch_sugarloaf_canyon']['opening_clear']['height']:.2f}, Aurora {P['bw_arch_aurora_archipelago']['opening_clear']['width']:.2f} x
  {P['bw_arch_aurora_archipelago']['opening_clear']['height']:.2f}); pivots at base centre (blades at hub); spawn
  10-stud radius free of props; nothing above the bumper on the practice tee->cup lines except the windmill.
* **Tris:** lobby {tot['tris_total']:,} (limit 120k, target ~115k). Deck {deck:,} (10 per tile), railing {rail:,}
  ({P['bw_railing']['triangles']} per section), arches {arches:,}, shack {P['bw_birdie_bites_shack']['triangles']:,},
  canopy {P['bw_lantern_tree_canopy']['triangles']:,}.
* **Art notes applied (OVERRIDE 3):** deck strip has seeded per-plank value/hue jitter around #B5835A with a few
  #7A4E2D-leaning boards, and tiles A/B sample different U halves; `bw_rock_arch` is the backdrop hero (one clean
  swept arch with a clear opening, smooth chunky section, warm vertex-colour bands), sea stacks kept simpler.
* **Review fixes during the pass:** Sugarloaf rebuilt after comparing with concept_arches.png (chunky tapered
  faceted towers, ~4 wide bands, crenellated block lintel instead of thin striped tubes); portrait card/panel faces
  use plain parchment (the bordered cell stretched); the builder's 8-stud pier row and pier rail ends are scaled
  per instance.
* **Open questions:** {len(QUESTIONS)} in README "Spec questions for Game Art Bot". The ones that need action:
  leaderboard yaw (-90 faces west with a +Z front), blade hub Y 7.4, canopy Y 10 floats, string-light span vs
  posts.
* **Renders:** previews/props/*.png, previews/contact_sheet.png, previews/spawn_view.png, previews/topdown.png,
  previews/overview.png.
"""
open(os.path.join(SRC, "pass1_summary.md"), "w", encoding="utf-8").write(summary)
print("README.md + pass1_summary.md written;", result)
