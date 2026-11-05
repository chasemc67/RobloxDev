# python make_reports_v32.py <workdir>   (plain Python 3, no bpy) -> out/fitcheck.md, out/manifest.json, out/report.txt
import json, os, sys, hashlib, platform, datetime
W = sys.argv[1]; O = os.path.join(W, 'out')
def J(p): return json.load(open(os.path.join(O, p)))
def sha(p): h = hashlib.sha256(); h.update(open(p, 'rb').read()); return h.hexdigest()
F = J('fitcheck.json'); RL = J('logs/repair_log.json'); V = J('logs/fbx_verify.json'); OLD = json.load(open(os.path.join(W, 'fitcheck.json')))
PR = json.load(open(os.path.join(O, 'logs/probe.json')))
src = os.path.join(W, 'source_v3_1.blend'); SRC_BEFORE = 'e207cfd07b8f96cdb0f3a0c5992d5dae4ddc7c5c93974a883c839558e5c037d6'   # hashed before any Blender step
SRC_AFTER = sha(src); BLEND = os.path.join(O, 'start_ship_v3_2.blend')
steps = open(os.path.join(O, 'logs/step_exit_codes.txt'), encoding='utf-8-sig', errors='replace').read().replace('\x00', '').strip().splitlines()
d12 = RL['repairs']['D1_D2_Prop_BowRaise_plank_line_trim']; d3 = RL['repairs']['D3_Prop_CapRails_underside_vs_Hull_rail']; d4 = RL['repairs']['D4_Prop_CapRails_start_vs_SternCastle_tier_end']
ms = F['meshes_vs_source']; col = F['collision']; mast = col['COL_Mast_Main']
flag = PR['flag']; flag_fc = ms['Prop_Flag']
REPAIRS = [
 dict(defect='D1 Prop_BowRaise vs Prop_CapRails at Roblox [72.48,55.44,-20.13] (high side)', cause='BowRaise dark plank line (WoodDk tube, 0.64 tall) climbs into the CapRails underside at a shallow angle; its top face crossed the cap bottom between x71-74 (gap -0.04..+0.06)',
      fix='trim endpoint: plank line start moved x56 -> x77 (first ring >=0.10 below the cap underside; measured 0.157); 7 rings / %d verts / %d faces removed, 1 WoodDk end face added (UVs copied from the old end face)' % (d12[0]['verts_removed'], d12[0]['faces_removed']),
      displacement='no vertex moved; 21.0 studs of the line removed (x56-77, where it was already 0.04-0.44 buried in the cap underside)'),
 dict(defect='D2 Prop_BowRaise vs Prop_CapRails at Roblox [72.48,37.95,45.15] (low side)', cause='mirror of D1', fix='same trim on the low-side plank line (x56 -> x77, new start 0.157 below cap); %d verts / %d faces removed, 1 face added' % (d12[1]['verts_removed'], d12[1]['faces_removed']), displacement='none (trim)'),
 dict(defect='D3 Prop_CapRails vs Hull at Roblox [51.54,54.24,-22.28]', cause='high-side cap underside crosses the Hull WoodDk rail top near x51.5 (gap -0.06 at x50, +0.06 at x53); region lies inside the BowRaise panel / under the cap overhang',
      fix='surface displacement on CapRails only: bottom 2 verts of rings x50, x53, x56 set to 0.10 below the Hull rail top (hull-frame vertical, 15 deg tilt); next untouched ring x59 is +0.354 above so the transition face stays >=0.08 clear; Hull untouched',
      displacement='6 verts moved down %s studs (max %.4f); cap locally 0.04-0.30 deeper, no topology change' % ([m['moved_hull_frame_y'] for m in d3['verts_moved']], d3['max_displacement'])),
 dict(defect='D4 Prop_CapRails vs Prop_SternCastle at Roblox [-118.0,66.93,-27.33]', cause='high-side cap start face at x-118 lay exactly on the SternCastle lower-tier end face (x-118); both are inside the SternCastle step-end post box (x-118.6..-117.0)',
      fix='trim endpoint: cap start ring slid 0.5 along the tube toward ring 2 (x-118 -> x-117.5); start face stays hidden inside the post; SternCastle not modified',
      displacement='4 verts moved %s studs' % [m['displacement'] for m in d4['verts_moved']]),
]
OK = F['pass_hard_checks'] and V['all_ok'] and SRC_AFTER == SRC_BEFORE
# ---------------------------------------------------------------- fitcheck.md
md = ['# Fitcheck: start ship v3_2 (out/start_ship_v3_2.blend) vs baseline source_v3_1.blend', '',
      '**Overall hard checks: %s**' % ('PASS' if F['pass_hard_checks'] else 'FAIL'), '', '## FAILS', *(['- ' + x for x in F['fail']] or ['- none']), '', '## Warnings', *['- ' + x for x in F['warn']],
      '- no runtime/Studio validation was run (no Studio in this job)', '',
      '## Coplanarity (checker unchanged: same 14 objects, find_nearest 0.03, |dot|>0.995, plane gap <0.02)',
      '- v3_1: 4 coplanar pairs; v3_2: **%d** (%d faces checked)' % (F['coplanarity']['coplanar_pairs'], F['coplanarity']['faces_checked']),
      '- repair script re-ran the identical test before/after: %d -> %d' % (RL['detections_before']['coplanar_pairs'], RL['detections_after']['coplanar_pairs']), '',
      '## Repairs (geometry-local, Prop_BowRaise + Prop_CapRails only; Prop_SternCastle not modified)', '']
for r in REPAIRS: md += ['- **%s**: %s. Fix: %s. Displacement: %s.' % (r['defect'], r['cause'], r['fix'], r['displacement'])]
md += ['', '## Changed meshes vs v3_1: %s (everything else exact)' % F['changed_meshes_vs_v3_1'], '',
       '| object | category | geometry | UV | material assignment | origin matrix | datablock | collections | tris v3_1 -> v3_2 |', '|---|---|---|---|---|---|---|---|---|']
for n in sorted(ms):
    e = ms[n]; md.append('| %s | %s | %s | %s | %s | %s | %s | %s | %d -> %d |' % (n, e['category'], e['geometry_identical'], e['uv_identical'], e['material_assignment_identical'], e['origin_matrix_identical'], e['mesh_datablock_name_identical'], e['collections_identical'], e['tris_v3_1'], e['tris_v3_2']))
md += ['', 'Anchors exact: ' + ', '.join('%s=%s' % (k, v['exact_equal']) for k, v in F['anchors'].items()) + '; all empties identical set %s, matrices identical %s' % (F['empties_all']['identical_set'], F['empties_all']['all_matrix_identical']),
       '', '## Collision', '- %d/%d colliders, names identical %s, **all 190 byte-identical to v3_1: %d**, max world vertex diff %s' % (col['count_v3_2'], col['count_source'], col['names_identical'], col['all_190_byte_identical'], col['max_abs_world_vertex_diff']),
       '- COL_Mast_Main exact v3_1: %s; along-axis height %s (tilt %s deg); history: v3_1 shortened 157.0 -> 98.3 (delta 58.7), bottom fixed, source v3_1 unchanged; untouched here' % (mast['exact_vs_v3_1'], mast['height_along_axis_v3_2'], mast['axis_tilt_from_vertical_deg']),
       '', '## Hull / walk / probes', '- Hull identical %s; bottom/skirt profile identical at all %d stations: %s (same submersion)' % (ms['Hull']['geometry_identical'], len(F['hull_submersion']['stations']), F['hull_submersion']['all_identical']),
       '- walk surfaces identical %s; spawn headroom %s identical %s; door rays identical %s; tee sightlines identical %s' % (F['walk_surfaces']['identical'], F['spawn_headroom']['v3_2'], F['spawn_headroom']['identical'], F['door_clearance']['identical'], F['tee_sightlines']['identical']),
       '- floating-part scan (isolated components, same method as v3_1 dump): identical to v3_1 %s (%d components)' % (F['floaters']['identical_isolated'], F['floaters']['v3_2']['components']),
       '', '## Route corridor (zones/method unchanged from prior script)', '', '| zone | min clearance all props (obj) | repaired meshes only (obj) |', '|---|---|---|']
rc = F['route_corridor']
for z, v in rc['per_zone_all_props'].items(): q = rc['per_zone_repaired_only'][z]; md.append('| %s | %s (%s) | %s (%s) |' % (z, v['min_dist'], v['closest'], q['min_dist'], q['closest']))
md += ['', 'Any vertex/centre inside: %s. Any triangle intersection: %s' % (rc['any_vertex_or_centre_inside'], rc['any_triangle_intersection']), '', '## Triangles', '', '| mesh | status | tris |', '|---|---|---|']
ml = J('logs/mesh_stats.json')['allm']
for n in sorted(ml): md.append('| %s | %s | %d |' % (n, ml[n]['status'], ml[n]['tris']))
t = F['tris']; md += ['', 'Total visual: **%d** (v3_1: %d). All meshes <20k: %s (largest %s). Collision tris: %d.' % (t['total_visual'], t['total_v3_1_visual'], t['all_under_20k'], t['max_mesh'], t['collision_tris']),
                      'Caveat: ~51k total is above the ~40k near-field target (counts pier, rocks, rigging; not all near-field). Not reduced in this repair-only pass.',
                      '', '## Textures', *['- %s packed=%s' % (k, v['packed']) for k, v in F['images'].items()], '', '## Not checked / limits', *['- ' + x for x in F['not_checked']]]
open(os.path.join(O, 'fitcheck.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
# ---------------------------------------------------------------- manifest.json
fbx = {}
for fn, v in V['files'].items():
    p = os.path.join(O, 'fbx', fn); fbx[fn] = dict(path='out/fbx/' + fn, bytes=v['bytes'], objects=v['objects_exported'], tris=v['tris_exported'], reimport_ok=v['ok'], sha256=sha(p),
                                                     **({'collision_vs_v3_1': v['collision_vs_v3_1']} if v.get('collision_vs_v3_1') else {}))
man = dict(asset='start_ship', version='start_ship_b2_detail_v3_2', date=str(datetime.date.today()), blend='out/start_ship_v3_2.blend', blend_sha256=sha(BLEND),
           source='source_v3_1.blend', source_sha256_before=SRC_BEFORE, source_sha256_after=SRC_AFTER, source_unchanged=SRC_AFTER == SRC_BEFORE,
           axes='FBX axis_forward -Z, axis_up Y, scale 1 (1 unit = 1 stud), FBX_SCALE_UNITS, embedded textures; Blender +Y = Roblox -Z',
           placement_note='water world Y0 = model local -0.6; RampFlight2 is yawed -30 deg in Studio (exported unyawed, as v3/v3_1)',
           changed_meshes_vs_v3_1=F['changed_meshes_vs_v3_1'], repairs=REPAIRS, coplanar_detections=dict(v3_1=4, v3_2=F['coplanarity']['coplanar_pairs']),
           mast_collider_history=dict(object='COL_Mast_Main', v3_to_v3_1='height along 18-deg axis 157.0 -> 98.3 (delta 58.7), bottom fixed', v3_2='unchanged, exact v3_1 (%s along axis)' % mast['height_along_axis_v3_2']),
           fbx=fbx, meshes=ml, tris=dict(total_visual=t['total_visual'], total_v3_1=t['total_v3_1_visual'], collision=t['collision_tris'], all_under_20k=t['all_under_20k'], caveat='above ~40k near-field target; not runtime-validated'),
           anchors={k: dict(roblox=v['roblox'], exact=v['exact_equal']) for k, v in F['anchors'].items()},
           previews=['out/previews/ship_3q.png', 'out/previews/ship_tee.png'], fitcheck_pass=F['pass_hard_checks'], fbx_reimport_all_ok=V['all_ok'])
json.dump(man, open(os.path.join(O, 'manifest.json'), 'w'), indent=1)
# ---------------------------------------------------------------- report.txt
fl_canvas = [c for c in flag['components'] if c['mats'] == ['Canvas']]
rep = ['START SHIP v3_2 - coplanar repair report', '=' * 60, 'Result: %s' % ('PASS - fitcheck hard checks pass, FBX reimport verified, previews rendered' if OK else 'FAIL - see below'), '',
       'Environment: Windows PC %s (%s), Claude Code model claude-opus-5-5, Blender %s headless (--factory-startup, one process at a time), Cycles CPU for previews' % (platform.node(), platform.platform(), F['blender']),
       'Workdir: %s' % W, '', 'SOURCE', '  source_v3_1.blend sha256 before: %s' % SRC_BEFORE, '  source_v3_1.blend sha256 after : %s  (unchanged: %s; opened read-only, saved AS out/start_ship_v3_2.blend)' % (SRC_AFTER, SRC_AFTER == SRC_BEFORE),
       '  out/start_ship_v3_2.blend sha256: %s (images packed)' % man['blend_sha256'], '', 'REPAIRS (only the 4 reported coplanar defects)']
for r in REPAIRS: rep += ['  * ' + r['defect'], '      cause: ' + r['cause'], '      fix: ' + r['fix'], '      displacement: ' + r['displacement']]
rep += ['  Mesh stats before -> after: ' + '; '.join('%s verts %d->%d faces %d->%d tris %d->%d components %d->%d' % (n, s['before']['verts'], s['after']['verts'], s['before']['faces'], s['after']['faces'], s['before']['tris'], s['after']['tris'], s['before']['components'], s['after']['components']) for n, s in RL['mesh_stats'].items()),
        '  Changed meshes vs v3_1: %s. Prop_SternCastle NOT modified (D4 fixed on the CapRails side). No origins/transforms/names/material slots changed.' % F['changed_meshes_vs_v3_1'],
        '  Coplanar detections (identical checker & tolerances): before %d -> after %d (repair script) ; fitcheck on saved blend: %d' % (RL['detections_before']['coplanar_pairs'], RL['detections_after']['coplanar_pairs'], F['coplanarity']['coplanar_pairs']),
        '  Gaps: plank line new start 0.157 below cap (>=0.08); cap underside embedded 0.10 into hull rail at x50-56, transition to x59 face mean >=0.08; cap start face 0.5 off the tier end face, 0.5 inside post end; all pieces unchanged in thickness (cap 1.3+, plank 0.64) -> >=0.2.',
        '', 'FITCHECK (out/fitcheck.json/.md): %s' % ('PASS' if F['pass_hard_checks'] else 'FAIL ' + str(F['fail'])),
        '  all source mesh names/origins/datablocks exact: %s' % all(e['origin_matrix_identical'] and e['mesh_datablock_name_identical'] for e in ms.values()),
        '  all non-permitted meshes (incl. Hull, DeckCabin, ramps) geometry/UV/materials exact v3_1: %s' % all(e['geometry_identical'] and e['uv_identical'] and e['material_assignment_identical'] for n, e in ms.items() if n not in ('Prop_BowRaise', 'Prop_CapRails', 'Prop_SternCastle')),
        '  colliders: %d/190 byte-identical to v3_1, max world diff %s; COL_Mast_Main exact, %s along axis (history 157 -> 98.3 in v3_1, untouched)' % (col['all_190_byte_identical'], col['max_abs_world_vertex_diff'], mast['height_along_axis_v3_2']),
        '  anchors exact: %s' % {k: v['exact_equal'] for k, v in F['anchors'].items()},
        '  route corridor clear: inside=%s tri-intersections=%s min clearance %s' % (rc['any_vertex_or_centre_inside'], rc['any_triangle_intersection'], rc['min_clearance']),
        '  hull submersion identical: %s; walk/door/spawn/tee probes identical: %s/%s/%s/%s; floaters identical: %s' % (F['hull_submersion']['all_identical'], F['walk_surfaces']['identical'], F['door_clearance']['identical'], F['spawn_headroom']['identical'], F['tee_sightlines']['identical'], F['floaters']['identical_isolated']),
        '  tris: total visual %d (v3_1 %d), all meshes <20k %s. CAVEAT: ~51k total vs approximate ~40k near-field target; not reduced here; no runtime/Studio/Quest validation.' % (t['total_visual'], t['total_v3_1_visual'], t['all_under_20k']),
        '  warnings: %s' % F['warn'], '',
        'FBX (out/fbx, exported from the saved v3_2 blend; -Z forward, Y up, scale 1, embedded textures; same names as v3_1):']
for fn, v in fbx.items(): rep.append('  %s  %d objects, %d tris, reimport ok %s%s, sha256 %s' % (fn, v['objects'], v['tris'], v['reimport_ok'], (', colliders vs v3_1 max world diff %.2e' % v['collision_vs_v3_1']['max_abs_world_vertex_diff_vs_v3_1']) if 'collision_vs_v3_1' in v else '', v['sha256']))
rep += ['  (reimported collider diff is FBX float round-trip only; the blend colliders are byte-identical)', '',
        'PROP_FLAG CHECK (not modified: geometry/UV/materials identical to v3_1 = %s)' % (flag_fc['geometry_identical'] and flag_fc['uv_identical'] and flag_fc['material_assignment_identical']),
        '  provenance: Prop_Flag is unchanged since source v3 (v3_1 fitcheck status "unchanged"); it is not generated by build_v31.py (no flag code in prior_scripts) - its generator predates this script set; object note: "%s"' % flag['props'].get('note'),
        '  mesh: %d verts, %d tris, materials %s; 1 Red cloth component (226 faces) + %d Canvas emblem pieces (%d per side, mirrored on both faces of the cloth)' % (flag['verts'], flag['tris'], flag['mats'], len(fl_canvas), len(fl_canvas) // 2),
        '  emblem pieces per side: two long crossing diagonal bars (club shafts), small end blocks (club heads/grips), one 14-face round disc (golf ball) and a small block under it (tee); no skull/face/eye-socket shapes, no text, no logo',
        '  verdict: original generic golf-club/ball emblem in crossed-bones style; no skull, no copied franchise art or logo detected. Visual check: 3q preview shows small light crossed shapes on the red flag.', '',
        'PREVIEWS: out/previews/ship_3q.png, ship_tee.png (1600x1000, prior_scripts/render_v31.py unchanged: same cameras, lighting, CPU Cycles 64 spp). Inspected once: no z-fight artefacts or missing parts seen; plank line now starts at x77 (small visual change at the bow, hard to see at this distance). Preview-ready: %s (fitcheck passed).' % F['pass_hard_checks'], '',
        'OBSERVATIONS (reported, not changed):',
        '  - The low-side cap rail probably crosses the Hull rail top at the same x (~51) as D3, but the identical checker does not flag it (its stations are offset 1 stud), it is inside the BowRaise panel, it was not measured, and it is out of scope, so it was left alone.',
        '  - The first render wrote to C:\\out\\previews (Blender resolved the relative path from C:\\); re-rendered with an absolute path. The tool sandbox blocked deleting the stray C:\\out folder (2 PNGs); please remove it manually.',
        '  - export_v32.py first run failed (Python kwarg typo, exit 1); fixed and rerun (exit 0). Blender returns 0 on script errors unless --python-exit-code is used; all steps used --python-exit-code 1.', '',
        'STEP EXIT CODES:', *['  ' + s for s in steps], '',
        'SCRIPTS (out/src): repair_v32.py, fitcheck_v32.py + fitcheck_v32_check.py (v3_1 checker adapted: baseline v3_1, only 3 permitted meshes may change), export_v32.py, render_v31.py (unchanged), probe_v32.py, make_reports_v32.py, plus shiplib.py and the prior scripts for reference.',
        'Reproduce: blender -b --factory-startup --python-exit-code 1 source_v3_1.blend --python out/src/repair_v32.py -- out/start_ship_v3_2.blend out/logs/repair_log.json ; fitcheck_v32.py dump (source_v3_1) then check (v3_2) ; export_v32.py ; render_v31.py ship_3q ship_tee ; python make_reports_v32.py <workdir>']
open(os.path.join(O, 'report.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
print('REPORTS_OK overall', OK)
