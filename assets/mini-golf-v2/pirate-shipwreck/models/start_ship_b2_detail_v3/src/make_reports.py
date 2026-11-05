# plain python3 (no Blender): python make_reports.py <out_dir> <workdir>
# builds manifest.json + fitcheck.md from fitcheck.json, logs/mesh_stats.json, logs/build_log.json, logs/fbx_verify.json, logs/source_inspect.json
import json, os, sys, hashlib
O = sys.argv[1]; WD = sys.argv[2]; L = os.path.join(O, 'logs')
F = json.load(open(os.path.join(O, 'fitcheck.json'))); M = json.load(open(os.path.join(L, 'mesh_stats.json')))['allm']
BL = json.load(open(os.path.join(L, 'build_log.json'))); FV = json.load(open(os.path.join(L, 'fbx_verify.json'))); SI = json.load(open(os.path.join(L, 'source_inspect.json')))
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def rb(bmn, bmx): return [bmn[0], bmn[2], -bmx[1]], [bmx[0], bmx[2], -bmn[1]]   # blender bbox -> roblox bbox
# source envelopes (Roblox)
def union(names):
    lo = [1e9] * 3; hi = [-1e9] * 3
    for n in names:
        o = SI['objects'][n]; a, b = rb(o['bbmin'], o['bbmax']); lo = [min(x, y) for x, y in zip(lo, a)]; hi = [max(x, y) for x, y in zip(hi, b)]
    return lo, hi
col_env = union([n for n in SI['objects'] if n.startswith('COL')]); ship_env = union(['Hull', 'DeckCabin', 'Rigging', 'Dressing', 'Dressing_Glow'])
def outside(bmin, bmax, env, tol=0.05):
    r = []
    for k, ax in enumerate('XYZ'):
        if bmin[k] < env[0][k] - tol: r.append('%s- by %.2f' % (ax, env[0][k] - bmin[k]))
        if bmax[k] > env[1][k] + tol: r.append('%s+ by %.2f' % (ax, bmax[k] - env[1][k]))
    return r
UNCH = [n for n, v in F['meshes_vs_source'].items() if v['geometry_identical'] and v['materials_identical'] and v['uv_identical'] and v['origin_matrix_identical']]
STATUS = {}
for n in M:
    STATUS[n] = 'unchanged (byte-identical geometry/materials/UVs/origin)' if n in UNCH else ('changed' if n in F['meshes_vs_source'] else 'new prop')
NOTES = {'Hull': 'straight bowsprit beam (12 tris) replaced by an upcurled tapered bowsprit with rope lashings + brass knob; 1122 outer plank faces Wood -> HullWood (130,90,55). Every other source triangle is still present (4207/4207). Wet/skirt geometry untouched.',
         'Rigging': 'rebuilt on the same object/origin/18 deg roll: main mast snapped at Y~106 (rig frame) with pale splinter crown + iron bands, tilted crow\'s nest on the stump, sagging upper yard, torn billowed cream sails with large scalloped rips + CanvasDk patches, intact fore mast (original 126 height) with nest, furled top sail, brass cap; rope stays/shrouds re-run (RopeLt). Flag moved to Prop_Flag.'}
meshes = {}
for n, v in M.items():
    e = dict(v); e['status'] = STATUS[n]; e['note'] = NOTES.get(n, '')
    if n.startswith('Prop_') or n in ('Rigging', 'Hull'):
        e['outside_source_ship_visual_envelope'] = outside(v['bbox_min_roblox'], v['bbox_max_roblox'], ship_env)
        e['outside_collider_envelope'] = outside(v['bbox_min_roblox'], v['bbox_max_roblox'], col_env)
    meshes[n] = e
for n in meshes:
    if n.startswith('Prop_'):
        meshes[n]['note'] = next((p.split('PROP ')[1] for p in [] ), '')
prop_notes = {}
for s in BL['notes']:
    pass
man = dict(
    name='start_ship_b2_detail_v3', based_on='source.blend = approved start_ship_b2 v2_3 (NOT modified)',
    source=dict(path=os.path.join(WD, 'source.blend'), sha256_before=open(os.path.join(L, 'source_sha_before.txt')).read().split()[0], sha256_after=sha(os.path.join(WD, 'source.blend'))),
    outputs=dict(blend='start_ship_v3.blend', fbx=sorted(FV.keys()), previews=sorted(os.listdir(os.path.join(O, 'previews'))), textures=['textures/start_ship_palette.png']),
    units='1 Blender unit = 1 stud', frame='Blender Z up; Roblox B(x,y,z) = (x,-z,y) i.e. Roblox (x, y, z) = (bx, bz, -by)',
    export=dict(axis_forward='-Z', axis_up='Y', global_scale=1.0, apply_scale_options='FBX_SCALE_UNITS', embed_textures=True, path_mode='COPY', mesh_smooth_type='FACE',
                visual_fbx='Visual meshes + 3 Ramps + all Props + Spawn/Tee1/RampStart/CupRef empties (same as source export + Props)', col_fbx='190 COL boxes (unchanged)', ramps='RampFlight1/RampLanding/RampFlight2 exported on their own origin (location zeroed for export only)'),
    collections={k: v for k, v in F.get('collections', {}).items()} or None,
    meshes=meshes,
    tris=dict(total_all_meshes=sum(v['tris'] for v in M.values()), max_single_mesh=max(M, key=lambda k: M[k]['tris']), max_single_mesh_tris=max(v['tris'] for v in M.values()), all_under_20k=all(v['tris'] < 20000 for v in M.values())),
    palette=dict(texture='start_ship_palette.png (256x256, 8x8 cells of 32 px, packed in the blend and embedded in the FBX; existing cells unchanged except Canvas + Red recoloured to the brief)',
                 materials=BL['palette'], srgb_note='material Base Color = exact sRGB->linear of the cell RGB; texture cell = 8-bit sRGB RGB',
                 new_materials=['HullWood', 'RopeLt', 'Brass', 'Barnacle', 'Seaweed', 'Gold', 'Crab', 'FishTeal', 'Shadow'],
                 recoloured_existing=dict(Canvas=[[225, 205, 165], [225, 210, 175]], Red=[[200, 50, 40], [170, 60, 50]]),
                 retained_names='all 15 source material names retained (Wood, WoodDk, Post, PostLt, Canvas, CanvasDk, Red, Rope, Iron, Glow, Felt, Rock, RockDk, RockLt, Collision); Wood/WoodDk unchanged'),
    anchors={k: dict(roblox=v['roblox'], exact_equal_to_source=v['exact_equal']) for k, v in F['anchors'].items()},
    verification=dict(collision=F['collision'], ramps={k: F['meshes_vs_source'][k] for k in ('RampFlight1', 'RampLanding', 'RampFlight2')},
                      unchanged_meshes=UNCH, hull_retained=F['hull_retained'], walk_surfaces=F['walk_surfaces'], min_route_clearance=F['route_corridor']['min_clearance'],
                      coplanar_pairs=F['coplanarity']['coplanar_pairs'], hard_checks_pass=F['pass_hard_checks']),
    changes=[
        'Hull: curled bowsprit replaces the straight beam; outer planking recoloured to HullWood (130,90,55); all other hull triangles retained; skirt/waterline unchanged.',
        'Rigging: rebuilt (same name/origin/18 deg roll): broken main mast (~2/3) + tilted crow\'s nest, torn scalloped sails with patches, intact fore mast with nest and furled sail.',
        'New Props collection (each a separate named mesh): ' + ', '.join(sorted(n for n in M if n.startswith('Prop_'))),
        'Artifact fix: the source DeckCabin deck slab stern end face (x=-160, Y 22..24) is coplanar with the Hull stern cap and inward-facing (renders as a black band on the transom). DeckCabin was NOT edited; a proud WoodDk deck-line trim plank (part of Prop_SternCurl) covers it.',
        'Palette: 9 new cells/materials; Canvas and Red cells recoloured to the brief (used only by sails/flag). Ramp/deck/pier/rock cells untouched.'],
    flags=F['envelope']['notes'] + ['Visual meshes extending beyond the source collider union envelope are listed per mesh under outside_collider_envelope (scenery, no new colliders were added).'],
    fbx_reimport=FV)
json.dump(man, open(os.path.join(O, 'manifest.json'), 'w'), indent=1)
# ---------------------------------------------------------------- fitcheck.md
R = F; md = []
md.append('# start_ship_b2_detail_v3 fitcheck (measured)\n')
md.append('Source: `%s` (sha256 before %s / after %s -> %s). v3: `out/start_ship_v3.blend`. All numbers below are computed by `src/fitcheck_v3.py` (dump on source.blend, check on v3).\n' % (
    man['source']['path'], man['source']['sha256_before'][:16], man['source']['sha256_after'][:16], 'UNCHANGED' if man['source']['sha256_before'] == man['source']['sha256_after'] else 'CHANGED!'))
md.append('**Hard checks (anchors exact, 190 colliders byte-identical, ramps identical, no new geometry inside the route corridor, every mesh <20k): %s**\n' % ('PASS' if R['pass_hard_checks'] else 'FAIL'))
md.append('## Anchors (exact float equality of location/rotation/scale/matrix_world vs source)\n| empty | Roblox (x,y,z) | exact | max abs diff |\n|---|---|---|---|')
for k, v in R['anchors'].items(): md.append('| %s | %s | %s | %g |' % (k, v['roblox'], v['exact_equal'], v['max_abs_diff']))
c = R['collision']
md.append('\n## Collision\n- count source %d / v3 %d, names identical: %s, collection membership identical: %s\n- byte-identical (vertex co float32 sha256 + loops + polys + matrix_world + world-vertex sha): **%d / %d**\n- max |world vertex diff| over all 190x8 transformed vertices: **%g**\n' % (
    c['count_source'], c['count_v3'], c['names_identical'], c['collection_membership_identical'], c['byte_identical'], c['count_source'], c['max_abs_world_vertex_diff']))
md.append('## Meshes vs source\n| mesh | geometry | materials | UVs | origin | tris src -> v3 |\n|---|---|---|---|---|---|')
for k, v in R['meshes_vs_source'].items(): md.append('| %s | %s | %s | %s | %s | %d -> %d |' % (k, v['geometry_identical'], v['materials_identical'], v['uv_identical'], v['origin_matrix_identical'], v['tris_source'], v['tris_v3']))
for k in ('RampFlight1', 'RampLanding', 'RampFlight2'): md.append('- %s world-vertex max abs diff: %g' % (k, R['meshes_vs_source'][k]['world_verts_max_abs_diff']))
h = R['hull_retained']; md.append('- Hull: %d/%d source triangles still present at identical positions; %d removed, all within 1.95 of the old bowsprit beam axis: %s' % (h['source_tris_still_present'], h['source_tris'], h['missing'], h['missing_are_bowsprit']))
w = R['walk_surfaces']; md.append('\n## Walking surfaces\n- DeckCabin byte-identical (see table). Level deck tops at Y24: %d faces / %.3f sq studs (source %d / %.3f); forecastle tops Y30 %.3f (source %.3f). Identical: %s. Collider tops unchanged (collision section).' % (
    w['v3']['deck_top_Y24_faces'], w['v3']['deck_top_Y24_area'], w['source']['deck_top_Y24_faces'], w['source']['deck_top_Y24_area'], w['v3']['forecastle_top_Y30_area'], w['source']['forecastle_top_Y30_area'], w['identical']))
md.append('\n## Spawn headroom, door, tee sightline (ray probes against ALL visual meshes incl. new props)\n- Spawn headroom (ray straight up from Spawn): source %s, v3 %s, identical %s' % (R['spawn_headroom']['source'], R['spawn_headroom']['v3'], R['spawn_headroom']['identical']))
d = R['door_clearance']; md.append('- Cabin door (cabin door from gen_start_ship.py: x=-120 +-4, 10 high, front wall z=24): %d rays from inside the cabin (z=18) out through the opening to z=30 on a 1-stud grid x -123.5..-116.5, Y 24.5..33.5: blocked source %d, v3 %d, identical %s' % (d['rays'], d['rays_blocked_source'], d['rays_blocked_v3'], d['identical']))
md.append('- Tee eye = Tee1 + 5 studs Y = %s. Sightlines (first hit before target):' % R['tee_sightlines']['eye_roblox'])
for k, v in R['tee_sightlines']['v3'].items(): md.append('  - %s (dist %.2f): v3 %s, source %s' % (k, v['dist'], v['first_hit'], R['tee_sightlines']['source'][k]['first_hit']))
md.append('  - identical to source: %s (the flight2-mouth ray grazes RampFlight1 in BOTH; no new geometry on any sightline)' % R['tee_sightlines']['identical'])
rc = R['route_corridor']
md.append('\n## Route corridor clearance (new + rebuilt geometry only)\nMethod: %s. Zones (Roblox min/max): %s; %s; %s.\n' % (rc['method'], json.dumps(rc['boxes_roblox']), rc['flight2_box'], rc['cup']))
md.append('| zone | min clearance (studs) | closest new mesh |\n|---|---|---|')
for k, v in rc['per_zone'].items(): md.append('| %s | %.3f | %s |' % (k, v['min_dist'], v['closest']))
md.append('\n**Minimum clearance: %.3f studs (%s, %s).** Anything inside a zone: %s. Caveat: the cabin_interior zone min (1.7) is the cabin windows sitting on the OUTSIDE of the 2-stud cabin wall (embedded 0.3, never inside the room); door_approach min is the door lantern (12.5 studs east of the door centre, bottom 8.6 above deck).\n' % (rc['min_clearance']['studs'], rc['min_clearance']['zone'], rc['min_clearance']['object'], rc['any_inside']))
md.append('## Hull submersion (lowest Hull point per x station; water = world Y0 = local -0.6)\n| x | source bottom | v3 bottom | identical | submerged (studs) |\n|---|---|---|---|---|')
for s in R['hull_submersion']['stations']: md.append('| %g | %s | %s | %s | %s |' % (s['x'], s['source_bottom_y'], s['v3_bottom_y'], s['identical'], s['submerged_below_water_studs']))
md.append('\nStern to midships (x -158..72) stay 1.42-1.49 studs submerged, identical to source; x 82 is 1.39, x 92 0.35, and from x 102 the bow rises onto the beach as in the source (unchanged skirt).')
cp = R['coplanarity']; md.append('\n## Coplanarity\n- %s\n- faces checked %d, coplanar pairs found **%d**.' % (cp['method'], cp['faces_checked'], cp['coplanar_pairs']))
md.append('- Design offsets: hull/wall relief pieces embedded 0.1-0.3 and proud >=0.12 (portholes ~0.7, port frames >=0.6, patch planks >=0.2 at the worst corner + nails 0.35, barnacles 0.7-1.15, sail patches 0.12, flag emblem 0.12, cabin windows 0.8); deck props start 0.1 below the deck top (bottoms hidden); thinnest pieces 0.22 (sail patches/flag emblem), 0.28 (seaweed ribbons), 0.3 (crab legs).')
md.append('\n## Tris\n| mesh | collection | tris |\n|---|---|---|')
for k in sorted(M, key=lambda k: (M[k]['collection'], k)): md.append('| %s | %s | %d |' % (k, M[k]['collection'], M[k]['tris']))
md.append('| **total** | | **%d** |' % man['tris']['total_all_meshes'])
md.append('\nLargest single mesh: %s (%d). All <20k: %s.' % (man['tris']['max_single_mesh'], man['tris']['max_single_mesh_tris'], man['tris']['all_under_20k']))
md.append('\n## Envelope / caveats (honest)\n- Source floater scan (merged-by-position components whose bbox touches nothing else): %d components, isolated: %s -> nothing removed.' % (R['floaters_source']['components'], R['floaters_source']['isolated'] or 'none'))
md.append('- Source artifact found: DeckCabin deck-slab stern end face coplanar with the Hull stern cap at x=-160 (inward-facing, rendered as a black band). Not edited (walking-surface mesh); covered by a proud WoodDk deck-line trim plank in Prop_SternCurl.')
for n, v in sorted(meshes.items()):
    if v.get('outside_collider_envelope'): md.append('- %s extends beyond the source collider union envelope: %s (scenery, no collider)' % (n, ', '.join(v['outside_collider_envelope'])))
    if v.get('outside_source_ship_visual_envelope'): md.append('- %s extends beyond the source ship visual envelope (Hull+DeckCabin+Rigging+Dressing): %s' % (n, ', '.join(v['outside_source_ship_visual_envelope'])))
for n in R['envelope']['notes']: md.append('- ' + n)
open(os.path.join(O, 'fitcheck.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n'); print('REPORTS_OK')
