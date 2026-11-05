"""Contact sheets + README.md + props_p1_summary.md from manifest.json / fitcheck_report.json (system python + Pillow).
  python out_props/_src/make_docs.py"""
import json, os, re, glob, datetime
from PIL import Image, ImageDraw, ImageFont
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
ROOT = os.path.dirname(OUT)
man = json.load(open(os.path.join(OUT, "manifest.json")))
fit = json.load(open(os.path.join(OUT, "fitcheck_report.json")))
fv = json.load(open(os.path.join(OUT, "fbx_validation.json"))) if os.path.exists(os.path.join(OUT, "fbx_validation.json")) else None
rows = json.load(open(os.path.join(SRC, "p1_rows.json")))
try:
    FONT = ImageFont.truetype("arial.ttf", 15)
    FONTB = ImageFont.truetype("arialbd.ttf", 22)
except Exception:
    FONT = FONTB = ImageFont.load_default()

# ------------------------------------------------------------------ contact sheet (eye + 3/4 per prop)
props = man["props"]
S, L = 256, 22
cols = 6
cells = [(p["name"], v) for p in props for v in ("eye", "34")]
rws = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * S, rws * (S + L) + 40), (20, 22, 40))
d = ImageDraw.Draw(sheet)
d.text((10, 8), f"Aurora Archipelago - P1 props ({len(props)} props, eye height 5 + 5-stud capsule | 3/4 view)", fill=(235, 240, 255), font=FONTB)
for k, (n, v) in enumerate(cells):
    x, y = (k % cols) * S, 40 + (k // cols) * (S + L)
    p = os.path.join(OUT, "previews", f"{n}_{v}.png")
    if os.path.exists(p):
        sheet.paste(Image.open(p).convert("RGB").resize((S, S), Image.LANCZOS), (x, y))
    d.text((x + 4, y + S + 3), f"{n} [{v}]"[:36], fill=(220, 228, 255), font=FONT)
sheet.save(os.path.join(OUT, "contact_sheet.png"), optimize=True)
sheet.save(os.path.join(OUT, "previews", "contact_sheet.png"), optimize=True)

# ------------------------------------------------------------------ tee sheet
tees = sorted(glob.glob(os.path.join(OUT, "previews", "tee_h*.png")))
if tees:
    W, H = 640, 360
    ts = Image.new("RGB", (3 * W, ((len(tees) + 2) // 3) * (H + 26) + 40), (20, 22, 40))
    d = ImageDraw.Draw(ts)
    d.text((10, 8), "P1 props over the pass-2b world: VR tee views (eye 5 studs above each tee, looking at the cup)", fill=(235, 240, 255), font=FONTB)
    holes = {h["hole"]: h for h in json.load(open(os.path.join(ROOT, "props_in", "aurora-archipelago", "holes.json")))["holes"] for h in [dict(hole=h["number"], name=h["name"])]}
    for k, p in enumerate(tees):
        n = int(re.findall(r"tee_h(\d+)", p)[0])
        x, y = (k % 3) * W, 40 + (k // 3) * (H + 26)
        ts.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y))
        b = fit["budgets"].get(str(n), {})
        d.text((x + 6, y + H + 4), f"H{n} {holes[n]['name']}  |  near-field {b.get('near_field_total', '?'):,} tris", fill=(220, 228, 255), font=FONT)
    ts.save(os.path.join(OUT, "tee_contact_sheet.png"), optimize=True)
    ts.save(os.path.join(OUT, "previews", "tee_contact_sheet.png"), optimize=True)

# ------------------------------------------------------------------ P1 coverage
by_anchor = {}
for p in props:
    for pl in p["placements"]:
        if pl.get("anchor"):
            by_anchor.setdefault((pl["hole"], pl["anchor"]), []).append(p["name"])
    for a in p.get("anchors", []) or []:
        for h in p["holes"]:
            by_anchor.setdefault((h, a), []).append(p["name"])
SPECIAL = {"geyser_platform": ["aa_h05_geyser_column", "aa_h05_geyser_steam"], "mogul_trim": ["aa_h07_rails"], "run_lip": ["aa_h10_rails"],
           "ice_floe": ["aa_h11_ice_floe"], "paddle_wheel": ["aa_h12_paddle_wheel"], "carousel_arms": ["aa_h13_carousel_arms"],
           "icicle_bell": ["aa_h14_icicle_bell"], "great_frozen_falls": ["aa_world_great_frozen_falls"], "steamwhistle_geyser": ["aa_kit_geyser_cone", "aa_kit_geyser_puff_small"],
           "cup_flag": ["aa_kit_flag"]}
cov = []
for r in rows:
    nm = r["name"].replace(" (LANDMARK)", "")
    got = SPECIAL.get(nm) or by_anchor.get((r["hole"], nm)) or []
    cov.append((r["hole"], nm, sorted(set(got))))
missing = [c for c in cov if not c[2]]

PT = {p["name"]: p for p in props}
tot_unique = sum(p["triangles"] for p in props)
dress = man["hole_dressing_files"]
date = datetime.datetime.now().isoformat(timespec="seconds")

CONFLICTS = [
    "**Halo Arch position** - holes.json H18 anchor [0,0.8,-52] -> world [-235,222.8,-284], depth 4; world.json backdrop `halo_arch` [-235,222,-292], depth 8. **Used holes.json** (one arch, `aa_h18_halo_arch`, legs x +-23, opening >= 18 over the felt). world.json record treated as a stale locator.",
    "**Steamwhistle Geyser** - ONE cone mesh (`aa_kit_geyser_cone`, 6 x 7 x 6) used twice: the H5 instance with the small puff (`aa_kit_geyser_puff_small`) and the world.json cone [262,84,380] at scale [2.333,1.429,2.333] (= 14 x 10 x 14) with the 60-stud steam column (`aa_world_geyser_puff60`). Puffs are separate meshes so their scale differs.",
    "**H5 geyser anchor lies on the felt** - holes.json anchor [-10.5,4,-33] (6 wide) sits inside the upper green felt (x -12.5..12.5) although its own note says 'outside the upper green's west rail'. A collider-less 7-stud cone on the green would fail the felt-clash rule, so the H5 instance is placed at **[-19,4,-33]** (outside upper_rail9, >= 3 studs clear). Designer to confirm.",
    "**Mover specs** - course.md 'starting spec' table superseded by holes.json (H5 dwell 8 s / 1.5 s, H11 3 studs/s, H12 30 deg/s, H13 15 deg/s, H14 9 deg / 4 s, H17 solid 6 s of 9 s). All movers use holes.json pivots/axes exactly (fitcheck verifies).",
    "**H5 hexagonal platform vs square collider** - square 3 x 3 contact faces; hex look in the top texture + brass hex vent ring (props-full section 4).",
    "**H11 floe** - thickness 0.636 (blocker) not 0.6 (anchor); props.md allows snow/snowpuff to 1.2 but the rail5/berg18 slot lintel (collision_cuts) was at y 1.17, so floe decoration stops at **1.12**; Round 4 'walls' raised the lintel to **1.27**, so the unchanged floe now clears it by 0.15.",
    "**H12 paddle tips** - modelled as an arc (props-full: 'model the arc'). Pass 2d pulled it in to r 4.0575 (visual gap 0.0625, colliders 0.020); Round 3 'clear' raised the hub to y 4.16, so the arc is back at the strip-corner radius **r 4.1** and visual and collider both clear the felt by **0.060**. Between strip centres the arc exceeds the stepped strip blockers by up to 0.10 studs (it never falls inside them).",
    "**H13 hub** - 48-sided cylinder r 7.5 as specified; the 48 circumscribed box strips step outward by up to ~0.3 at the chord ends, so a ball can touch an invisible corner just outside the visual base.",
    "**Great Frozen Falls** - geometry from world.json waterfalls (top [20,182,-398] -> bottom y 36, width 26); the H15 anchor [13.5,-4,-30] is a view cue (props-full section 13).",
    "**Red/cream reserved for movers** - the brief allows red/cream bands only on moving parts, but props-full describes a 'striped red-and-cream' bobsled hut, a red-hull/cream-deckhouse icebreaker and a striped fishing hut. Static props were recoloured: violet (`Canvas` #7A5CC8) & snow stripes, deep-teal hull (`HullTeal` #2F5D7A), brass funnel.",
    "**Palette vs pass 2b** - course.md timber #8A5A33 / felt #4FA83D; the terrain pass 2b changed timber to #8A5A3C and felt to #4FC29E; pass 2c retuned felt to #45B892 and pass 2d to #3EA886. Props use **#8A5A3C** timber and **#3EA886** felt strips (aa_h03_ice_plank, aa_h03_dressing; textures/felt.png) so they match the terrain FBXs.",
    "**Priority of walkway pieces** - props.md lists lifts, bridges and teleport pads under P2, props-full section 11 marks them P1. Built as P1 kits with world instances (lift cage, gondola cabin + stations, ice/aurora bridge modules, stair flights, teleport + tee-arrival pads).",
    "**Sign anchors hug the rails** - several sign anchors sit 0.1 stud outside a rail (e.g. H2 sign_left x -12.6 vs rail3 face -12.5). Posts slimmed to 0.18 and the board swung to the side away from rails/felt (`aa_kit_sign_*_L/_R` variants, chosen per anchor by the generator).",
    "**H2 lantern cue** - the 'rope between two frosted pines' needs the P2 pines; P1 uses a timber crane post 3.5 studs outside the west green rail with the arm at y 10.6 and the lantern at y 9.",
    "**Small fit adjustments** - H11 fishing hut 0.25 south (still inside its occluder) to clear pocket_w21; H1 ship's lantern hangs west of its post (>= 3 studs from rail1); H5 shaft lining 3.7 wide (spec 3.2) and cliff face 0.2 behind the step so the rising platform + gauge keep >= 0.15 clearance; H15 parapet split into its own prop (PlayerGuard envelope).",
    "**H3 plank top = felt top (y 0)** - the plank mesh carries the felt look (2-wide Felt strip); the builder should make the 2 x 0.4 felt slab collider invisible there to avoid z-fighting.",
]
FLAGS = fit["summary"]["flags"]

# ------------------------------------------------------------------ summary
s = [f"# Aurora Archipelago - P1 props summary\n", f"Generated {date}. Fitcheck: **{'ALL PASS' if not fit['summary']['fails'] else 'FAILURES'}** ({fit['summary']['passed']} PASS, {len(fit['summary']['fails'])} FAIL, {len(FLAGS)} FLAG) - `fitcheck_p1props_validated.txt`." +
     (f" FBX re-import: **{sum(f['passed'] for f in fv['files'])}/{len(fv['files'])} passed** (`fbx_validation.json`)." if fv else ""), "",
     "**Pass 2d:** Felt #45B892 -> **#3EA886** (terrain pass 2d) in `aa_h03_ice_plank.fbx`, `aa_h03_dressing.fbx` and `textures/felt.png`, the only Felt users. The blocking movers `aa_h12_paddle_wheel` and `aa_h14_icicle_bell` had their visual meshes rebuilt (`build_all.py --only`) for a **0.0625** visual felt gap over the full motion range (was 0.020 / 0.0215). Their holes.json colliders are unchanged and still sit at 0.020 / 0.0215 (see *Pass 2d: blocking movers' felt gap* below). No other geometry or clearance changed.", "",
     "**Pass 2e:** no prop FBX changed (129/129 byte-identical to `out_props_bak_2e`, re-imported again). The fitcheck now also covers the blockout's new decoration - `felt_banks.fbx` (FeltBank #308369 = Felt x 0.78, visual 0.3-stud bank along exposed felt edges) and `course_apron_00..02.fbx` (SnowCourse #C9D6E0 surround, 5-7 studs outside every felt+rail footprint), both CanCollide false - against holes.json felt, rails, cups, tee lanes, movers and gap volumes (`_src/fitcheck_decor.py`, exec()'d by `fitcheck.py`; see *Pass 2e: blockout decoration fitcheck* below). The earlier prop checks are unchanged line for line.", "",
     "**Round 3 'clear' (holes.json clearance fix, playtest-log.md):** H12 paddle-wheel hub y 4.12 -> **4.16** (blockers unchanged relative to the hub); H14 icicle-bell foot = **9 strip colliders** whose outer bottom corners sit on an arc r 10.289 about the hinge. Rebuilt `aa_h12_paddle_wheel.fbx` (tip arc r 4.0575 -> 4.1, follows the strip colliders) and `aa_h14_icicle_bell.fbx` (skid plate = envelope of the 9 strips, curved underside on r 10.289: 0.061 over the felt at the centre, 0.115 at the ends, top 0.461); visual and collider felt gaps are now equal: **0.060 / 0.061** (were visual 0.0625 / collider 0.020-0.0215). **New collision FBX** `aa_h12_paddle_wheel_collision.fbx` (24 boxes) and `aa_h14_icicle_bell_collision.fbx` (10 boxes) = the holes.json blockers exactly, FBX origin = pivot (`manifest.json collision_fbx_files`). The per-hole dressing FBX are unaffected (manifest regen identical outside the two movers; every other FBX byte-identical to `out_props_bak_clear`). holes.json also trimmed H5 upper_rail8/12 and the H17 pier rails by 0.15: every fitcheck rule still passes (the H5 column / H17 span wall flags are gone), so per the brief `aa_h05_rails.fbx` / `aa_h17_rails.fbx` were **not** rebuilt; the fitcheck FLAGs that their on-disk meshes still run 0.15 past the new rail ends (visual only). Previews: `previews/clear/`. Inputs: `_src/inputs_clear/` (Round 3 holes.json, pre-clear holes.json, playtest log, clearance table).", "",
     "**Pass 2g (blockout felt):** Felt #3EA886 -> **#36997A** (blockout pass 2g: the hero_05 felt-snow gap was still < 20 after the rail caps / H3 apron went #EEF3F7) in `aa_h03_ice_plank.fbx`, `aa_h03_dressing.fbx` and `textures/felt.png` (same seeds, ramp -8,-15,-12), the only Felt users; geometry identical (re-import checked), props .blends recoloured. Backup `out_props_bak_p2g`.", "",
     "**Rail skins (Round 3 trims):** `aa_h05_rails.fbx` / `aa_h17_rails.fbx` and the dressing that embeds them, `aa_h05_dressing.fbx` / `aa_h17_dressing.fbx`, **rebuilt** from the Round 3 holes.json: H5 upper_rail8/12 skins now end at x +-1.65, H17 pier_s/pier_n rail skins are 8.85 long (skin reaches 0.00 past every trimmed wall end, was 0.15). Tris and bboxes unchanged (2808 / 3104 / 3528 / 4462); only the rail-skin vertices moved; every other prop merged into the two dressing files is geometrically identical; rails == generator; mesh data swapped in both props .blends. This supersedes the 'not rebuilt' note above and clears the two stale rail-skin FLAGs. Fitcheck `fitcheck_railskin_validated.txt` (= `fitcheck_p1props_validated.txt`); remaining FLAGs are the H11/H12 holes.json-geometry wall clearances. Previews: `previews/railskin/`. Backup `out_props_bak_railskin`.", "",
     "**Round 4 'walls' (playtest-log.md 'Round 4: wall clearance (fitcheck)'):** holes.json moved only walls, not movers. **H11:** rail5/berg18 floe-slot lintel underside **1.17 -> 1.27** (`__cut1` centre y 1.835, height 1.13; side pieces `__cut2`/`__cut3` centre y 0.56, height 1.42). **H12:** icebreaker stern wall line **z -18 -> -18.01** (rail2/hull13 centre z -18.26; rail3/hull18 centre z -21.005, length 5.99; mitred rail1 centre -8.005, length 21.01; hull14 centre -26.005, length 15.99), 0.06 behind the paddles. **Rebuilt:** `aa_h11_rails.fbx`, `aa_h12_rails.fbx` and the dressing that embeds them, `aa_h11_dressing.fbx` / `aa_h12_dressing.fbx` (a full regeneration against the old and new holes.json showed these 4 are the only FBXs that change). Tris and overall bboxes are unchanged (1592 / 3264 / 2139 / 3995). Only rail-skin vertices moved (H11 <= 0.10, H12 <= 0.01). Every other prop merged into the two dressing files is identical, the rails equal the generator, and the meshes were swapped in both .blends. `skins.py` bolt plates use `int(L/2 + 0.01)`, so the 5.99 / 15.99 walls keep 3 / 8 plates (no other wall affected). Unchanged: `aa_h11_ice_floe` (top 1.12, now **0.15** under the lintel), `aa_h12_paddle_wheel`, the `aa_h12_icebreaker` body (its hull boxes end at z -18.2 inside the wall skins, which are the stern faces), the mover collision FBX (= holes.json blockers) and the felt. The fitcheck H11 lintel expectation is now **1.27** (read from holes.json collision_cuts and checked against the `__cut1` bottoms). Fitcheck `fitcheck_walls_validated.txt` (= `fitcheck_p1props_validated.txt`): **361 PASS, 0 FAIL, 0 FLAG**. Both 0.050 flags are gone: H11 ice_floe vs rail5__cut1 **0.150**, H12 paddle_wheel vs rail3/rail2 **0.060**. Decoration was checked against the pass 2g-walls blockout. Previews: `previews/walls/` (H11 slot lintel with the floe at -5.10, H12 stern with the wheel at 0 deg; eye, 3/4, side). Backup `out_props_bak_walls`; pre-walls holes.json `props_in/aurora-archipelago/holes_pre_walls.json`.", "",
     f"{len(props)} prop FBX files ({tot_unique:,} tris, single copies) + {len(dress)} per-hole merged dressing FBX files; {len(man['lights'])} lights in `manifest.json lights[]`. Every mesh and every FBX < 20,000 tris.", "",
     "## P1 coverage (props-full section 8 P1 rows -> files)", "", "| Hole | P1 item | Built as |", "|---|---|---|"]
for h, nm, got in cov:
    s.append(f"| H{h} | {nm} | {', '.join('`' + g + '`' for g in got) if got else '**MISSING**'} |")
s += ["", "Also P1 from props.md / props-full sections 4-7, 9, 11: rail kit (`aa_kit_rail_*`) + every holes.json wall box skinned per hole (`aa_hNN_rails`, tall-wall variants: snow drift H2/H10, snowbank/berg H11, coral H9, hull H12, moonstone H16, frosted ice H17 piers, crystal H18), bumper plinths (H1 boulder, H8 corals 1-7, H13 hub), floating-deck skirts (H3/H17 decks + piers, H9 spit), brass lantern posts (89 world instances + 9-stud hole post), 12 signs, respawn stones (H3/H6/H17), teleport visuals (H5 platform, H9 conch ring + conch x2), Starfrost Spire + orbiting shards, lift cage, gondola cabin/stations, bridge/stair modules, teleport and tee-arrival pads.", ""]
if missing:
    s += ["**Missing:** " + ", ".join(f"H{h} {nm}" for h, nm, _ in missing), ""]
s += ["## Prop list (triangles)", "", "| Prop | Class | Holes | Tris | Mesh parts | Size [x,y,z] | Motion |", "|---|---|---|---:|---:|---|---|"]
for p in props:
    mo = p.get("motion")
    s.append(f"| `{p['name']}` | {p.get('class')} | {','.join(str(h) for h in p['holes']) or 'world/kit'} | {p['triangles']:,} | {p['mesh_parts']} | {p['bbox_size_studs']} | {mo['type'] + ' ' + str(mo.get('speed')) + ' ' + str(mo.get('units')) if mo else ''} |")
s += ["", "## Per-hole near field (Quest; <= 60 studs of the hole's felt)", "", "Own dressing = merged `aa_hNN_dressing.fbx`; loose = flag, movers, puffs; neighbours = other holes' P1 instances within 60 studs; world = lantern posts, pads, bridges, stairs, lifts, gondola, world geyser within 60 (spire / shards / Great Frozen Falls are streamed landmarks, exempt).", "",
      "| Hole | Own dressing | Own loose | Neighbours | World pieces | **Near-field total** | Budget |", "|---|---:|---:|---:|---:|---:|---|"]
for n in range(1, 19):
    b = fit["budgets"][str(n)]
    s.append(f"| H{n} | {b['own_dressing']:,} | {b['own_loose_instances']:,} | {b['neighbour_holes_le60']:,} | {b['world_pieces_le60']:,} | **{b['near_field_total']:,}** | {'lean (H5-8 target)' if 5 <= n <= 8 else ''} <= 40k |")
s += ["", "## Movers (fitcheck sweep)", "", "| Mover | Steps | Min felt clearance | Min wall clearance | Min static-prop clearance |", "|---|---:|---|---|---|"]
for k, v in fit["movers"].items():
    s.append(f"| `{k}` | {v['steps']} | {v['min_felt_clearance'] if v['min_felt_clearance'] is not None else 'n/a'} {('at ' + str(v['at']) + ' ' + v['unit']) if v['at'] is not None else ''} | {v['min_wall_clearance']} ({v['wall']} at {v['wall_at']} {v['unit']}) | {v['min_static_prop_clearance'] if v['min_static_prop_clearance'] is not None else '-'} |")
s += ["", "Flags for the build bot (holes.json geometry, not mesh errors):", ""] + [f"- {f}" for f in FLAGS]
s += ["", "### Blocking movers' felt gap (Round 3 'clear': visual mesh == holes.json collider)", "",
      "The H12 paddle wheel and H14 icicle bell are blocking movers: they must stay under a 0.16 ball but off the felt. Pass 2d moved only the VISUAL meshes "
      "to a 0.0625 gap while the holes.json colliders stayed at 0.020 / 0.0215. Round 3 'clear' moved the COLLIDERS to >= 0.06 (H12 hub +0.04, H14 9-strip foot), "
      "so the visual meshes follow the colliders again. Fine-step sweeps over the full motion range test the exact mesh vertices and the blocker box corners "
      "(and the collision FBX corners) against the holes.json felt tops.", "",
      "| Mover | Visual mesh (Round 3) | Sweep | Visual min felt gap (2d -> clear) | Collider min felt gap (2d -> clear) | Collision FBX |", "|---|---|---|---|---|---|"]
_chg = {"aa_h12_paddle_wheel": "red paddle-tip arc r 4.0575 -> 4.1 = the strip-corner radius (rim, spokes, boards unchanged); pivot hub y 4.16",
        "aa_h14_icicle_bell": "skid plate = envelope of the 9 strip colliders: flat top 0.461 at rest, underside on r 10.289 about the hinge (0.061 centre, 0.115 ends; vertices at every strip edge, never above a strip bottom); body/hanger/icicles unchanged"}
_pre = {"aa_h12_paddle_wheel": ("0.0625", "0.020"), "aa_h14_icicle_bell": ("0.0625", "0.0215")}
_col = {c["prop"]: c for c in man.get("collision_fbx_files", [])}
for k, v in fit["movers"].items():
    f2 = v.get("pass2d_fine_sweep")
    if f2:
        cf = _col.get(k)
        cs = fit.get("clear", {}).get(f"{k}_collision_felt_sweep", {})
        s.append(f"| `{k}` | {_chg.get(k, '')} | {f2['steps']} steps of {f2['step']} {f2['unit']} | {_pre.get(k, ('?', '?'))[0]} -> **{f2['visual']['min_gap']}** at {f2['visual']['at']:+} {f2['unit']} (within 0.0005 at {f2['visual']['range_at_min']}) | "
                 f"{_pre.get(k, ('?', '?'))[1]} -> **{f2['collider']['min_gap']}** at {f2['collider']['at']:+} {f2['unit']} | "
                 + (f"`{cf['file']}`: {cf['meshes']} boxes, {cf['triangles']} tris, swept min {cs.get('min_gap')}" if cf else "-") + " |")
dec = fit.get("decoration")
if dec:
    s += ["", "### Pass 2e: blockout decoration fitcheck (felt banks + SnowCourse apron vs holes.json)", "",
          f"Blockout `{os.path.relpath(dec['blockout'], os.path.dirname(OUT))}` (manifest pass {dec['pass']}); points tested: banks {dec['points']['bank']:,}, apron {dec['points']['apron']:,} "
          "(triangle samples at 0.1 / 0.5 studs + every vertex). Banks: never inside a felt rectangle, never above the felt top they border, under a rail only inside the rail box, "
          ">= r+0.5 from cups, none in the tee-lane felt, clear of every mover's swept blocker volume. Apron: over felt only hidden inside the slab (<= top - 0.1), within 8.5 studs of the footprint, "
          "hugs the terrain (+0.05), clear of cups/tee lanes/movers.", "",
          "| Hole | Bank pts (under rails / outside) | Max over bordered felt top | Min cup dist | Apron pts (over felt, hidden) | Apron band max dist |", "|---|---|---:|---:|---|---:|"]
    for n in range(1, 19):
        h = dec["holes"].get(str(n), {}); b = h.get("bank", {}); a = h.get("apron", {})
        s.append(f"| H{n} | {b.get('points', 0):,} ({b.get('in_wall_footprint', 0):,} / {b.get('outside_walls', 0):,}) | {b.get('max_above_bordered_felt_top', '-')} | {b.get('min_cup_dist', '-')} | "
                 f"{a.get('points', 0):,} ({a.get('inside_felt_rect', 0):,}) | {a.get('band_max_dist', '-')} |")
s += ["", "## Conflicts resolved", ""] + [f"{i + 1}. {c}" for i, c in enumerate(CONFLICTS)]
s += ["", "## Caveats", "",
      "- Decoration only: CanCollide/CanQuery/CanTouch false on every MeshPart; gameplay collision stays the invisible holes.json parts (Round 3: the two blocking movers also ship their colliders as `*_collision.fbx`, identical to holes.json).",
      "- Designer-anchored props (signs, lamps, huts, gantry, conch, lip ice ...) keep their exact holes.json anchor positions; where their envelope already overlaps the rail strip or felt the fitcheck reports it as an envelope note instead of a failure (see `fitcheck_report.json > anchored_envelope_overhang`). Geometry outside an anchor envelope obeys all clash/strip/lane rules.",
      "- Decals are thin meshes (0.01) conformed to the felt; they could equally be SurfaceGui/Decal textures. Sign wording goes on SurfaceGuis on the cream boards (front = +Z).",
      "- Glow (Neon) parts carry Blender emission for previews; in Roblox use Material Neon + PointLights from `lights[]`. Glass ice: Transparency 0.3, Reflectance 0.1 (`IceSheen` 0.15/0.15).",
      "- Animated/scripted parts are separate meshes: flag banner (child `aa_kit_flag__FlagRed`, turns about the pole axis), geyser steam column (Size.Y = offset), puffs, signal-lamp lens (`SignalGreen`), span lamp lens (`AuroraMint`), spire shards.",
      "- World instances of walkway kits use world.json positions (lift cages at the bottom stop; bridges in 4-stud modules with the last one scaled). Teleport kiosk signs and P2/P3 dressing (snowpuffs, pines, palms, coral fans, music lanterns) are not part of this pass.",
      "- `aa_world_starfrost_spire` replaces the terrain blockout spire (hide `spire__*` from the blockout FBX set when both are imported).",
      "- Preview renders are Cycles 16 spp (props) / 32 spp (tee views); tee views use the pass-2b scene with the blockout's placeholder rails/flags hidden."]
open(os.path.join(OUT, "props_p1_summary.md"), "w", encoding="utf8", newline="\n").write("\n".join(s) + "\n")

# ------------------------------------------------------------------ README
mats = man["materials"]
r = [f"# Aurora Archipelago - P1 props (out_props)", "",
     f"Generated {date} by headless Blender 5.2 from `_src/` (pipeline adapted from the Lantern Grove library: registry -> build_all -> fitcheck -> docs). **All props are visual only**; collision = holes.json.", "",
     "## Files", "", "| Path | What |", "|---|---|",
     "| `fbx/<prop>.fbx` | One FBX per prop (root empty + one mesh per material, textures embedded). `aa_kit_*` reused kit, `aa_hNN_*` per-hole props, `aa_world_*` world pieces |",
     "| `fbx/aa_hNN_dressing.fbx` | Per-hole static P1 dressing merged per material in the HOLE FRAME (origin = holes.json world_offset, rotated by world_yaw: `PivotTo(holeRoot)`), < 20k tris each |",
     "| `textures/*.png` | 512x512 tiling textures (timber, snow, slate_rock, basalt_hex, ice, felt, coral, moonstone); also embedded |",
     "| `manifest.json` | Per file: holes, bbox, tris, materials/parts, pivot, motion; `holes[]` per-hole instances (hole frame + world pos); `world_instances[]`; `lights[]`; `hole_dressing_files[]` |",
     "| `fitcheck_p1props_validated.txt`, `fitcheck_report.json` | Numeric fitcheck vs holes.json (ALL PASS) = the latest run, `fitcheck_walls_validated.txt` (Round 4 'walls'); `fitcheck_clear_validated.txt` = the Round 3 'clear' run, `fitcheck_railskin_validated.txt` = the rail-skin run |",
     "| `fbx/aa_h12_paddle_wheel_collision.fbx`, `fbx/aa_h14_icicle_bell_collision.fbx` | Round 3: the movers' holes.json blockers as box meshes (one MeshPart per box, CollisionFidelity Box, Transparency 1), origin = pivot (`collision_fbx_files[]`) |",
     "| `previews/walls/` | Round 4 'walls': H11 slot lintel (1.27) with the floe, H12 icebreaker stern (z -18.01) with the paddle wheel; eye, 3/4, side |",
     "| `previews/clear/` | Round 3: H12/H14 eye, 3/4, side view at the lowest point + 1-stud close-ups of the felt gap (visual / collider) |",
     "| `fbx_validation.json` | Re-import check of every FBX |",
     "| `previews/<prop>_eye.png`, `_34.png` | Eye height 5 with a 5-stud reference capsule (blue), and 3/4 view; movers show their axis (red = rotate/swing, cyan = slide) |",
     "| `previews/tee_hNN.png`, `tee_contact_sheet.png` | VR tee view (5 studs) of every hole over the pass-2b world |",
     "| `contact_sheet.png` | All prop previews, labelled |",
     "| `aurora_props_p1.blend`, `aurora_props_p1_in_world.blend` | All props laid out; props placed in the 2b world |",
     "| `props_p1_summary.md` | P1 coverage, tris, per-hole near field, movers, conflicts, caveats |",
     "| `_src/` | Generators: `aalib.py`, `registry.py`, `holesdata.py`, `skins.py`, `props_kit.py`, `props_movers.py`, `props_holes.py`, `textures.py`, `build_all.py`, `fitcheck.py` (+ `fitcheck_decor.py`, pass 2e; `fitcheck_clear.py`, Round 3), `collision_movers.py` (Round 3), `previews_clear.py`, `verify_fbx.py`, `tee_views.py`, `make_docs.py`, `build.ps1` |", "",
     "Rebuild: `_src/build.ps1` (textures -> build_all -> fitcheck -> verify_fbx -> tee_views -> make_docs).", "",
     "## Export / axes", "",
     "1 Blender unit = 1 stud, scene units NONE, modelled Z-up. FBX `axis_forward='-Z'`, `axis_up='Y'`, scale 1.0, `FBX_SCALE_UNITS`, embedded textures, face smoothing. Roblox (x, y, z) = Blender (x, -z, y). Import with the scale unit **Stud**.", "",
     "## Import (build bot)", "",
     "1. Import each FBX as a Model; every child `<prop>__<Material>` becomes a MeshPart. Set Color / Material / Transparency from `manifest.json > props[].parts[]` (table below). Neon parts are glow cores; add PointLights from `lights[]` (position world + hole-local, range, brightness, colour).",
     "2. Every MeshPart: `Anchored=true, CanCollide=false, CanQuery=false, CanTouch=false, CollisionFidelity=Box`; CastShadow off on Neon/Steam/Lagoon/IceSheen.",
     "3. Per-hole dressing: `Model:PivotTo(CFrame.new(world_offset) * CFrame.Angles(0, math.rad(world_yaw), 0))`. Loose instances (flag, movers, puffs): `holeCF * CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0)` with `pos/yaw/scale` from `holes[].instances[]`. World pieces: `world_instances[]` (world coordinates; non-uniform `scale` = set each MeshPart.Size).",
     "4. Movers: origin = holes.json pivot. Drive with the blocker formula every Heartbeat: rotate `pivotCF * CFrame.fromAxisAngle(axis, rad(speed*t + phase))`; slide `pivotCF + axis*offset(t)` (ping-pong with dwell); swing `hingeCF * CFrame.fromAxisAngle(axis, rad(amp*sin(2*pi*t/period + phase)))`; H17 span = Transparency toggle. Red/cream bands appear only on moving parts.",
     "5. Flag: rotate the `__FlagRed` banner (or the whole model) about the pole axis (origin Y) to face the tee.", "",
     "## Material table (flat-colour fallback)", "", "| Material | Colour | Roblox Material | Emission | Transparency | Use |", "|---|---|---|---:|---:|---|"]
for k, v in mats.items():
    r.append(f"| `{k}` | `{v['color']}` | {v['roblox_material']} | {v['emission']} | {v['transparency']} | {v['note']} |")
r += ["", "## Hole dressing files", "", "| File | Hole | Tris | Mesh parts | Instances merged |", "|---|---|---:|---:|---|"]
for h in dress:
    c = h["contents"] if isinstance(h["contents"], list) else []
    r.append(f"| `{h['file']}` | H{h['hole']} | {h['triangles']:,} | {h['mesh_parts']} | {', '.join(sorted(set(x['prop'] for x in c)))} |")
open(os.path.join(OUT, "README.md"), "w", encoding="utf8", newline="\n").write("\n".join(r) + "\n")
print("docs written; missing:", missing)
