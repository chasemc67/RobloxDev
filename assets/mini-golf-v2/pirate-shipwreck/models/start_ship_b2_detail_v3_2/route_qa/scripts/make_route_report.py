# Builds out/route_qa.json, route_qa.md, report.txt, route_topdown.png from route_qa_raw.json + route_geom.json + probe_hullext.json.
# Run with system Python 3.12 (numpy + matplotlib), no Blender:  python out/scripts/make_route_report.py out
import json, sys, os, math, hashlib, datetime
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon as MPoly

OUT = sys.argv[1]
R = json.load(open(os.path.join(OUT, 'route_qa_raw.json'))); G = json.load(open(os.path.join(OUT, 'route_geom.json')))
HX = json.load(open(os.path.join(OUT, 'probe_hullext.json')))
SRC = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'source_v3_2.blend')
sha = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()
SHA_EXPECTED = '9d75ae96912ff0ca4b7a97b5b6287e3cc10d55edefa0c2719c6cfec2dd0bf333'
KEY = 'studio_yawed'; RT = R['route'][KEY]; RU = R['route']['as_exported_unyawed']
PROPS = ['Prop_SternWheel', 'Prop_TreasureChest']

def capsule(a, b, r, n=24):
    a, b = np.array(a, float), np.array(b, float); d = b - a; L = np.linalg.norm(d); t = d / L if L else np.array((1.0, 0.0))
    th0 = math.atan2(t[1], t[0]); pts = []
    for k in range(n + 1): th = th0 - math.pi / 2 + math.pi * k / n; pts.append(b + r * np.array((math.cos(th), math.sin(th))))   # cap around b
    for k in range(n + 1): th = th0 + math.pi / 2 + math.pi * k / n; pts.append(a + r * np.array((math.cos(th), math.sin(th))))   # cap around a
    return np.array(pts)

# ------------------------------------------------------------------ verdicts
res = {}
for pn in PROPS:
    m = RT['corridor_main'][pn]; c = RT['corridor_conservative12'][pn]; mu = RU['corridor_main'][pn]
    res[pn] = dict(
        bbox_min=R['props'][pn]['bbox_min'], bbox_max=R['props'][pn]['bbox_max'], tris=R['props'][pn]['tris'], origin=R['props'][pn]['origin'],
        main_full_projection=dict(min_clearance=m['full_projection']['min_clearance'], closest_segment=m['full_projection']['closest_segment'],
                                  centreline_dist=m['full_projection']['centreline_dist'], corridor_half_width=m['full_projection']['half_width'],
                                  closest_prop_xz=m['full_projection']['closest_prop_xz'], closest_centreline_xz=m['full_projection']['closest_route_xz'],
                                  nearest_prop_vertex_roblox=m['full_projection']['nearest_prop_vertex_roblox'], nearest_prop_vertex_blender=m['full_projection']['nearest_prop_vertex_blender']),
        main_clipped_y_23p5_30=dict(min_clearance=m['clip_y_23.5_30']['min_clearance'], tris=m['clip_y_23.5_30']['tris'], closest_segment=m['clip_y_23.5_30']['closest_segment']),
        conservative12_full_projection=dict(min_clearance=c['full_projection']['min_clearance'], closest_segment=c['full_projection']['closest_segment'],
                                            note='12-wide (r6) on cabin/deck too + whole COL_Outrigger platform + COL_Flight1_Surface as areas'),
        as_exported_unyawed_main=mu['full_projection']['min_clearance'],
        bbox_reference_main=m['bbox_reference'],
        per_segment_main=[dict(segment=s['segment'], half_width=s['half_width'], centreline_dist=s['centreline_dist'], clearance=s['clearance'], intersects=s['intersects_corridor'])
                          for s in m['full_projection']['per_segment']],
        pass_=m['full_projection']['min_clearance'] > 0 and c['full_projection']['min_clearance'] > 0 and mu['full_projection']['min_clearance'] > 0)
props_pass = all(res[p]['pass_'] for p in PROPS)
ca = R['collider_audit']['per_prop']
collider_ok = all(not ca[p]['collider_names_matching_prop'] and not ca[p]['prop_in_Collision_collection'] for p in PROPS)

W = RT['walk_and_width']; OP = R['landing_exit_opening'][KEY]; occ = HX['occupancy']
widths = {s: dict(section=w['section'], min_clear_width_colliders=w['min_clear_width_colliders']['width'], at_xz=w['min_clear_width_colliders']['at_xz'],
                  by=[w['min_clear_width_colliders']['left'][1], w['min_clear_width_colliders']['right'][1]],
                  min_clear_width_visual=w['min_clear_width_visual']['width'], vis_at_xz=w['min_clear_width_visual']['at_xz'],
                  walk_samples=w['samples'], samples_without_walk_collider=w['samples_without_walk_collider'], walk_y_range=w['walk_y_range'],
                  max_step_0p5=w['max_step_between_0p5_samples'], walk_objects=w['walk_objects']) for s, w in W.items()}
hull_block = {k: v for k, v in occ.items() if k.startswith('COL_HullExt')}

Q = dict(
    task='LAST TARGETED ROUTE QA: Prop_SternWheel + Prop_TreasureChest vs continuous cabin->door->deck->gangplank route',
    date=str(datetime.date.today()), model='claude-opus-5-5', blender=R['blender'], source=SRC, source_sha256_before=SHA_EXPECTED, source_sha256_after=sha,
    source_unchanged=sha == SHA_EXPECTED, model_modified=False, new_blend_written=False,
    verdict='PASS' if props_pass and collider_ok else 'FAIL',
    verdict_scope='both props are outside the full continuous swept route corridor (main 8/12 and conservative 12) with exact triangle-edge distances; no model change made',
    player_capsule_radius=R['player_capsule_radius'],
    route_definition=dict(frame='Roblox model-local x,y(up),z; XZ projection; Flight2 yawed -30 deg about its origin (Studio assembly) = primary, as-exported unyawed also evaluated',
                          centreline=RT['centreline'], segments=RT['segments'], area_elements_main=['COL_Landing_FloorA', 'COL_Landing_FloorB', 'COL_Flight2_Surface', 'COL_Flight2_Apron'],
                          joints=RT['joints'], landing_points=RT['landing_points']),
    props=res, collider_audit=R['collider_audit'],
    walk_and_clear_width=widths, door_opening_min_width=R['door_opening_min_width'], landing_exit_opening=R['landing_exit_opening'],
    walk_collider_joints=R['walk_collider_joints'],
    hullext_walk_band_occupancy=dict(occupancy=hull_block, verts_roblox={k: HX['verts'][k] for k in ('COL_HullExt_0_07', 'COL_HullExt_1_07')}),
    width_established=dict(
        cabin_to_door_to_tee='8 established (door jambs 8.0 collider & visual = bottleneck; cabin interior wider)',
        tee_to_rampstart='NOT established by colliders: COL_HullExt_0_07/1_07 occupy y24.1-30 across the notch x-128..-112 at z47-55.5 (only a 0.2 sliver x-120.5..-120.3); visual notch is 18.8 wide',
        flight1='12 established (rails 12.0 collider; visual 11.2 at top posts)', landing_entry='12.1 (Landing_RailN_W..N_E)',
        landing_exit_to_flight2='NOT 8/12: collider opening 5.42 (Landing_RailW end -> Landing_RailS start), > capsule dia 4.0', flight2_and_apron='12 established (rails 12.0 collider)'),
    files=['route_qa.json', 'route_qa.md', 'route_topdown.png', 'report.txt', 'route_qa_raw.json', 'route_geom.json', 'route_samples.json', 'probe_hullext.json',
           'scripts/route_qa.py', 'scripts/probe_hullext.py', 'scripts/probe_names.py', 'scripts/make_route_report.py', 'logs/route_qa.log'])
json.dump(Q, open(os.path.join(OUT, 'route_qa.json'), 'w'), indent=1)

# ------------------------------------------------------------------ diagram
pts = {p['name']: np.array(p['xz']) for p in G['route'][KEY]}; segs = G['segs']
fig, axes = plt.subplots(1, 2, figsize=(22, 13), gridspec_kw=dict(width_ratios=[1.0, 1.15]))
for ax, (xl, zl, title) in zip(axes, [((-178, -55), (-25, 200), 'Overview (Studio assembly, Flight2 yawed -30 deg)'),
                                      ((-135, -62), (-6, 70), 'Zoom: cabin / door / deck / outrigger vs Wheel + Chest')]):
    feet = G['col_feet'][KEY]
    for n, f in feet.items():
        f = np.array(f)
        if len(f) < 3: continue
        walk = any(k in n for k in ('Deck_', 'CabinFloor', 'Outrigger', 'Surface', 'Landing_Floor', 'Apron'))
        hullx = n in ('COL_HullExt_0_07', 'COL_HullExt_1_07')
        ax.add_patch(MPoly(f, closed=True, fc=('#efe6cf' if walk else ('#f4c7c3' if hullx else 'none')), ec=('#b9a77a' if walk else ('#c0392b' if hullx else '#9a9a9a')),
                           lw=0.5 if not hullx else 1.0, alpha=0.9 if walk else (0.55 if hullx else 0.8), zorder=1 if walk else 2, hatch='///' if hullx else None))
    for i, (sn, rm, rc, sec) in enumerate(segs):
        a, b = sn.split('->'); ax.add_patch(MPoly(capsule(pts[a], pts[b], rc), closed=True, fc='none', ec='#1f5fbf', ls='--', lw=0.9, zorder=4))
        ax.add_patch(MPoly(capsule(pts[a], pts[b], rm), closed=True, fc='#3d7fe0', ec='#1f5fbf', alpha=0.28, lw=0.6, zorder=3))
    for an, f in G['areas'][KEY].items(): ax.add_patch(MPoly(np.array(f), closed=True, fc='#3d7fe0', ec='#1f5fbf', alpha=0.18, lw=0.6, zorder=3))
    C = np.array([pts[p['name']] for p in G['route'][KEY]]); ax.plot(C[:, 0], C[:, 1], '-', color='#0b2e6b', lw=1.6, zorder=6)
    for p in G['route'][KEY]:
        q = np.array(p['xz']); ax.plot(*q, 'o', color='#0b2e6b', ms=4, zorder=7)
        if xl[0] <= q[0] <= xl[1] and zl[0] <= q[1] <= zl[1]: ax.annotate(f"{p['name']}\n({q[0]:.1f},{q[1]:.1f})", q, xytext=(6, -4), textcoords='offset points', fontsize=7.5, color='#0b2e6b', zorder=8)
    for pn, col in zip(PROPS, ('#d35400', '#8e44ad')):
        T = np.array(G['props'][pn]); ax.add_collection(PolyCollection(T, fc=col, ec=col, lw=0.1, alpha=0.65, zorder=5))
        bmn, bmx = R['props'][pn]['bbox_min'], R['props'][pn]['bbox_max']
        ax.add_patch(MPoly([[bmn[0], bmn[2]], [bmx[0], bmn[2]], [bmx[0], bmx[2]], [bmn[0], bmx[2]]], closed=True, fc='none', ec=col, ls=':', lw=0.8, zorder=5))
        r_ = res[pn]['main_full_projection']; a = np.array(r_['closest_prop_xz']); b = np.array(r_['closest_centreline_xz'])
        ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=1.2, zorder=6)
        lab = f"{pn.replace('Prop_', '')}\ncentreline {r_['centreline_dist']:.2f}\n- half-width {r_['corridor_half_width']:.0f} = clear {r_['min_clearance']:.2f}"
        ax.annotate(lab, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), xytext=(0, 10 if pn.endswith('Wheel') else -30), textcoords='offset points', fontsize=8, color=col, ha='center', zorder=9,
                    bbox=dict(fc='white', ec=col, alpha=0.85, lw=0.6))
    ax.annotate('door 8.0 (jambs)', (-120, 24), xytext=(-60, 8), textcoords='offset points', fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.6), zorder=9)
    if xl[0] < -124 < xl[1] and zl[0] < 128 < zl[1]:
        ax.annotate(f"landing exit {OP['min_gap']:.2f} (collider)", (-124, 127.95), xytext=(40, -10), textcoords='offset points', fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.6), zorder=9)
    ax.annotate('COL_HullExt_0_07/1_07 in walk band\n(z47-55.5, y24.1-30) - see report', (-116, 51), xytext=(25, 25), textcoords='offset points', fontsize=7.5, color='#c0392b',
                arrowprops=dict(arrowstyle='->', lw=0.6, color='#c0392b'), zorder=9)
    ax.set_xlim(*xl); ax.set_ylim(zl[1], zl[0]); ax.set_aspect('equal'); ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_xlabel('Roblox X (stern -X  ->  bow +X)'); ax.set_ylabel('Roblox Z (high side -Z at top, low/sand side +Z down)'); ax.set_title(title, fontsize=11)
fig.suptitle('Top-down (looking down -Y) route corridor QA - source_v3_2.blend, read-only.  Blue fill = main corridor (r4 cabin/deck = 8 wide, r6 flights = 12 wide) + full landing/Flight2/apron walk areas;'
             '\nblue dashed = conservative r6 (12 wide) everywhere; orange = Prop_SternWheel tris, purple = Prop_TreasureChest tris (dotted = bbox); tan = walk colliders; grey = other colliders; '
             f'player capsule r={R["player_capsule_radius"]}', fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(os.path.join(OUT, 'route_topdown.png'), dpi=110); plt.close(fig)

# ------------------------------------------------------------------ markdown + report
def segtable(pn):
    rows = ['| segment / area | half-width | centreline (or area) dist | clearance |', '|---|---|---|---|']
    for s in res[pn]['per_segment_main']: rows.append(f"| {s['segment']} | {s['half_width']} | {s['centreline_dist']:.3f} | {s['clearance']:.3f} |")
    return '\n'.join(rows)
wrows = ['| segment | section | min clear width colliders (by) | at xz | min clear width visual | walk samples / no-walk-hit | walk y | max step/0.5 |', '|---|---|---|---|---|---|---|---|']
for s, w in widths.items():
    wrows.append(f"| {s} | {w['section']} | {w['min_clear_width_colliders']:.2f} ({w['by'][0]} / {w['by'][1]}) | {w['at_xz']} | {w['min_clear_width_visual']:.2f} | {w['walk_samples']} / {w['samples_without_walk_collider']} | {w['walk_y_range']} | {w['max_step_0p5']} |")
jrows = '\n'.join(f"| {j['joint']} | {j['endpoint_gap']} | r{j['disc_r']} disc in prev {j['disc_in_prev']} / next {j['disc_in_next']} | {j['turn_deg']} |" for j in RT['joints'])
wj = '\n'.join(f"| {x['a']} | {x['b']} | {x['footprint_gap']} | {x['top_y']} |" for x in R['walk_collider_joints'][KEY])
cal = []
for pn in PROPS:
    for h in ca[pn]['colliders_overlapping_xz_or_3d']:
        cal.append(f"| {pn} | {h['collider']} | {h['xz_footprint_overlap']} | {h['aabb3d_overlap']} | {h['triangle_overlaps']} | {h['col_y']} | {h['prop_y']} |")
md = f"""# Route QA - Prop_SternWheel / Prop_TreasureChest vs continuous cabin->gangplank route

**Verdict: {Q['verdict']}** - both visual-only props are outside the complete swept route corridor. **No model change** (no v3_3 written; v3_2 previews/exports stay final).
Source `source_v3_2.blend` sha256 before = after = `{sha}` (unchanged: {Q['source_unchanged']}). Blender {R['blender']} headless, read-only (never saved).

![top-down](route_topdown.png)

## Results (main corridor, conservative full XZ projection of every triangle)

| prop | min clearance to corridor | closest segment | centreline dist | half-width | closest prop pt (x,z) | closest centreline pt | clipped y23.5-30 | conservative 12 | unyawed F2 | bbox ref |
|---|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(f"| {pn} | **{r['main_full_projection']['min_clearance']:.3f}** | {r['main_full_projection']['closest_segment']} | {r['main_full_projection']['centreline_dist']:.3f} | {r['main_full_projection']['corridor_half_width']} | {r['main_full_projection']['closest_prop_xz']} | {r['main_full_projection']['closest_centreline_xz']} | {r['main_clipped_y_23p5_30']['min_clearance']:.3f} | {r['conservative12_full_projection']['min_clearance']:.3f} ({r['conservative12_full_projection']['closest_segment']}) | {r['as_exported_unyawed_main']:.3f} | {r['bbox_reference_main']['min_clearance']:.3f} |" for pn, r in res.items()) + f"""

Prop bboxes (Roblox): Wheel {res['Prop_SternWheel']['bbox_min']} .. {res['Prop_SternWheel']['bbox_max']}; Chest {res['Prop_TreasureChest']['bbox_min']} .. {res['Prop_TreasureChest']['bbox_max']}.
Nearest source vertex to the closest point: Wheel Roblox {res['Prop_SternWheel']['main_full_projection']['nearest_prop_vertex_roblox']} (Blender {res['Prop_SternWheel']['main_full_projection']['nearest_prop_vertex_blender']}), Chest Roblox {res['Prop_TreasureChest']['main_full_projection']['nearest_prop_vertex_roblox']} (Blender {res['Prop_TreasureChest']['main_full_projection']['nearest_prop_vertex_blender']}).
The wheel's closest point is its west rim edge x=-71.09 (rim overhang included); the chest's is its west side x=-84.79 at deck level. Both are ~35-49 studs east of the x=-120 route axis: the "centred" look in the tee view is perspective only (see diagram).

### Per-segment distances
**Prop_SternWheel**

{segtable('Prop_SternWheel')}

**Prop_TreasureChest**

{segtable('Prop_TreasureChest')}

## Intended walking route (not the whole deck)
Spawn (-120,24,2.5) inside the cabin -> straight +Z through the 8-stud door (-120,24,24) -> Tee1 (-120,24.4,37) on deck -> through the low-side bulwark notch onto the outrigger -> RampStart (-120,24,62.5) -> Flight1 down its axis x=-120 to its bottom edge z=114.5 (COL_Flight1_Surface) -> landing centre (-120,122.25) -> SW turn to the landing's south exit midpoint (-124,127.95) (between the end of Landing_RailW at (-126.5,126.9) and the start of Landing_RailS at (-121.5,129.0)) -> onto the Flight2 axis 6 studs below its mouth (first station with full 12-stud rail clearance) -> Flight2 (yawed -30 deg about its origin (-126.7,12,127.5), length 52 = COL_Flight2_Surface) -> apron centre (COL_Flight2_Apron, yawed).
Corridor = union of swept capsules over **every** centreline segment (r=4 i.e. 8 wide in cabin/door/deck; r=6 i.e. 12 wide on outrigger-to-Flight1, landing, Flight2, apron) **plus** the full walkable footprints of COL_Landing_FloorA/B, COL_Flight2_Surface and COL_Flight2_Apron. Conservative variant: r=6 (12 wide) on cabin/deck too (ignores the 8-wide door wall) plus the whole COL_Outrigger platform and COL_Flight1_Surface as areas.
Player capsule radius chosen = 2.0 studs: 8-wide route leaves 4.0 centreline margin; door 8.0 leaves 2.0 per side.

### Joints (union continuity)
| joint | endpoint gap | disc test | turn deg |
|---|---|---|---|
{jrows}

Landing points on the landing floor: {RT['landing_points']} (the exit midpoint lies 1.25 past FloorA's edge, on COL_Flight2_Surface / FloorB - walk hit continuous; 3 samples there hit only the Flight2 surface, which overlaps the landing floors: footprint gap 0.0).

### Walk-surface collider joints (footprint gap / top y)
| a | b | gap | top y |
|---|---|---|---|
{wj}

## Actual clear walking width along the route (horizontal rays perpendicular to the centreline at walk+0.5/2.5/4.5, every 0.5 stud)
{chr(10).join(wrows)}

Door opening measured directly (rays +-X, z 22-24, heights 0.5-8.5): colliders {R['door_opening_min_width']['colliders']}, DeckCabin visual {R['door_opening_min_width']['deckcabin_visual']} -> door is 8, not 12 (12 is not demanded through the wall).
Landing exit opening (collider footprint gaps, Studio yawed): {OP['pairs']}; min {OP['min_gap']}. Flight1 rails inner clear {OP['flight1_rail_inner_clear']}, Flight2 rails {OP['flight2_rail_inner_clear']}, landing north entry {OP['landing_north_entry']}.

**Widths established:** cabin->door->tee **8** (door bottleneck); Flight1 **12**; Flight2+apron **12**; landing entry 12.1.
**Not established:** (a) landing exit -> Flight2: collider opening **5.42** (> capsule diameter 4, so passable, but neither 8 nor 12; visual ray chord 3.8-4.7 at RampLanding posts, upper bound); (b) **tee -> RampStart through the bulwark notch: COL_HullExt_0_07 / COL_HullExt_1_07** (tilted 2.5-thick hull-skin slabs, x -160.1..-120.3 and -120.5..-80.7, y 13.6..34.6, z 38.9..57.8) occupy the walk band y 24.1-30 over x -128..-112, z 47-55.5 (inside-volume test, 1-stud grid; only a 0.2-stud sliver at x -120.5..-120.3 is free). Visually the notch is open (18.8 wide between the DeckCabin/hull notch faces). These are locked/byte-identical-to-v3_1 colliders, unrelated to the two props, and were **not** changed here - flag for the parent/collision owner and Studio runtime check.

## Collider audit (props are visual only)
- 190 colliders. Collider names matching the props: Wheel {ca['Prop_SternWheel']['collider_names_matching_prop']}, Chest {ca['Prop_TreasureChest']['collider_names_matching_prop']}. Props in 'Props' collection, not 'Collision'; no parent/children/modifiers.
- Colliders whose footprint or 3D box overlaps the props (actual geometry overlap tested with BVH):

| prop | collider | XZ overlap | 3D AABB overlap | tri overlaps | collider y | prop y |
|---|---|---|---|---|---|---|
{chr(10).join(cal)}

Interpretation: COL_Deck_04/05 are the deck floor slabs (top y 24.0) that the props stand on; the props' bases sink 0.10-0.15 into the deck (prop min y 23.9 / 23.85), which is what the triangle overlaps are. COL_HullExt_1_07/2_07 overlap the chest's 3D box but have 0 triangle overlaps (hull skin outboard/below). No collider exists for, or encloses, either prop; nothing to remove; no collider added.

## Method
1. Opened source_v3_2.blend read-only (`--factory-startup`, never saved; `bpy.data.is_dirty` False at end; sha256 re-verified).
2. Prop geometry: evaluated mesh loop triangles in world space, mapped to Roblox (x, y, z) = (bx, bz, -by); every triangle projected to XZ (wheel 1640 tris incl. rim, chest 980 incl. open lid).
3. Exact 2D distance per triangle to every route segment: segment-vs-triangle-edge distance with proper intersection test (orientation predicates) plus segment-endpoint-in-triangle test; clearance = distance - corridor half-width (capsule). Area elements (landing floors, Flight2 surface, apron, conservative outrigger/Flight1): triangle-vs-convex-polygon distance with edge intersection and two-way containment tests. Min taken over the union of all segments and areas.
4. Route points from source anchors (Spawn/Tee1/RampStart empties), DOORX/cabin front wall, and collider boxes (COL_Flight1_Surface end, landing floors, landing rails, COL_Flight2_Surface length, COL_Flight2_Apron); Flight2 + its colliders yawed -30 deg about RampFlight2's origin (manifest placement_note / prior fitcheck f2_dist); unyawed (as exported) evaluated too.
5. Walk continuity: downward ray every 0.5 stud along the centreline against walk colliders and visual ramps/deck; lateral clear width by horizontal rays (colliders and visual meshes separately) at 3 heights; door opening by direct rays; walk-collider footprint gaps; HullExt walk-band inside-volume probe.
6. Diagram from the same JSON (matplotlib, system Python).

## Limits
- No Studio/runtime validation; Humanoid behaviour on the HullExt slab and through the 5.42 landing exit not tested.
- Height clipping band y23.5-30 is deck-level only (props stand on the deck); full projection is the reported main result (identical minima here).
- Widths are ray chords perpendicular to the centreline (>= true gap at oblique openings); the landing exit gap is taken from collider footprint polygon distances.
- HullExt occupancy probe is a 1-stud x / 0.5-stud z grid at 6 heights.
"""
open(os.path.join(OUT, 'route_qa.md'), 'w', encoding='utf-8').write(md)
rep = f"""REPORT - LAST TARGETED ROUTE QA (start ship v3_2)  {Q['date']}  model claude-opus-5-5  Blender {R['blender']} headless (Windows PC)
VERDICT: {Q['verdict']} - Prop_SternWheel and Prop_TreasureChest are both outside the full continuous swept route corridor. NO model change; no v3_3; v3_2 previews/exports remain final.
SOURCE: {SRC}  sha256 before {SHA_EXPECTED}  after {sha}  unchanged={Q['source_unchanged']}  (opened read-only, never saved)

RESULTS (main corridor: 8 wide cabin/door/deck, 12 wide flights/landing/apron + full landing/Flight2/apron walk areas; exact triangle-edge XZ distance, full projection):
  Prop_SternWheel    min clearance {res['Prop_SternWheel']['main_full_projection']['min_clearance']:.3f} studs  (segment {res['Prop_SternWheel']['main_full_projection']['closest_segment']}, centreline dist {res['Prop_SternWheel']['main_full_projection']['centreline_dist']:.3f} - half-width 4)  prop pt xz {res['Prop_SternWheel']['main_full_projection']['closest_prop_xz']} -> route pt {res['Prop_SternWheel']['main_full_projection']['closest_centreline_xz']}
                     conservative 12-wide {res['Prop_SternWheel']['conservative12_full_projection']['min_clearance']:.3f}; clipped y23.5-30 {res['Prop_SternWheel']['main_clipped_y_23p5_30']['min_clearance']:.3f}; unyawed {res['Prop_SternWheel']['as_exported_unyawed_main']:.3f}; bbox {res['Prop_SternWheel']['bbox_min']}..{res['Prop_SternWheel']['bbox_max']}
  Prop_TreasureChest min clearance {res['Prop_TreasureChest']['main_full_projection']['min_clearance']:.3f} studs  (segment {res['Prop_TreasureChest']['main_full_projection']['closest_segment']}, centreline dist {res['Prop_TreasureChest']['main_full_projection']['centreline_dist']:.3f} - half-width 4)  prop pt xz {res['Prop_TreasureChest']['main_full_projection']['closest_prop_xz']} -> route pt {res['Prop_TreasureChest']['main_full_projection']['closest_centreline_xz']}
                     conservative 12-wide {res['Prop_TreasureChest']['conservative12_full_projection']['min_clearance']:.3f}; clipped {res['Prop_TreasureChest']['main_clipped_y_23p5_30']['min_clearance']:.3f}; unyawed {res['Prop_TreasureChest']['as_exported_unyawed_main']:.3f}; bbox {res['Prop_TreasureChest']['bbox_min']}..{res['Prop_TreasureChest']['bbox_max']}
  Route axis is x=-120 (cabin->notch->Flight1); props sit at x-66.8..-71.1 (wheel) and x-75.2..-84.8 (chest): tee-view "centred" look is perspective.
  Player capsule radius 2.0 (8-wide route -> 4.0 centreline margin; door 8.0 -> 2.0 per side).

ROUTE: Spawn(-120,2.5) -> Door(-120,24) -> Tee1(-120,37) -> RampStart(-120,62.5) -> Flight1_bottom(-120,114.5) -> Landing_centre(-120,122.25) -> Landing_exit(-124,127.95) -> Flight2_axis6(-129.7,132.70) -> Flight2_bottom(-152.7,172.53) -> Apron_centre(-156.58,179.25)  [Roblox x,z; Flight2 yawed -30 deg]
  all 8 joints: endpoint gap 0, min-radius disc inside both adjacent capsules; walk colliders hit at every 0.5-stud sample (max step 0.23 on slopes); walk-collider footprint gaps 0 along the route.

CLEAR WIDTH (actual, colliders): cabin/door {widths['Spawn->Door']['min_clear_width_colliders']:.2f} (door jambs = 8, visual 8.0) | Flight1 {widths['RampStart->Flight1_bottom']['min_clear_width_colliders']:.2f} | Flight2/apron 12.0 | landing entry 12.1 | landing exit -> Flight2 {OP['min_gap']:.2f}
  ESTABLISHED: 8 cabin->door->tee; 12 Flight1, Flight2, apron. NOT established: landing exit 5.42 (passable for r2 capsule, not 8/12);
  tee->RampStart notch: COL_HullExt_0_07/1_07 (locked hull-skin slabs, y13.6-34.6) occupy walk band y24.1-30 at x-128..-112, z47-55.5 (visual notch open 18.8). Not related to the props; NOT changed; flag for collision owner + Studio check.

COLLIDERS: 190 present; none named for / parented to / enclosing either prop; props in 'Props' collection only. Overlaps found = deck floor slabs COL_Deck_04/05 under the props (bases sink 0.10-0.15 into the deck top y24) and HullExt boxes with 0 triangle overlaps. No collider added or removed.

METHOD: see route_qa.md (triangle-edge/segment exact 2D distances with intersection + containment tests over the union of all swept segment capsules and walk areas; ray-cast walk/width; collider footprint polygons; BVH overlap).
LIMITS: no Studio/runtime; landing exit and HullExt behaviour untested in Humanoid; width chords perpendicular to centreline.
FILES: out/route_qa.json, route_qa.md, route_topdown.png, report.txt, route_qa_raw.json, route_geom.json, route_samples.json, probe_hullext.json, scripts/*.py, logs/route_qa.log
"""
open(os.path.join(OUT, 'report.txt'), 'w', encoding='utf-8').write(rep)
print('REPORT_OK', Q['verdict'], sha == SHA_EXPECTED)
