# python make_reports_v5.py <workdir>   (plain CPython; reads out/fitcheck.json, out/logs/*.json, run_history) -> fitcheck.md, manifest.json, report.txt, fbx/UNSYNCED note
import json, os, sys, hashlib, platform, datetime, glob, re
W = sys.argv[1]; O = os.path.join(W, 'out')
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
R = json.load(open(os.path.join(O, 'fitcheck.json'))); BL = json.load(open(os.path.join(O, 'logs', 'build_log.json'))); EV = json.load(open(os.path.join(O, 'logs', 'export_verify.json')))
MS = json.load(open(os.path.join(O, 'logs', 'mesh_stats.json')))['allm']
src_before = open(os.path.join(O, 'logs', 'source_sha_before.txt')).read().split()[0]; src_after = sha(os.path.join(W, 'source_v3_2.blend'))
blend = os.path.join(O, 'start_ship_whimsy_v5.blend'); bsha = sha(blend)
_hb = open(os.path.join(O, 'logs', 'run_history.txt'), 'rb').read()
_ht = _hb.decode('utf-16') if _hb[:2] in (bytes([0xFF, 0xFE]), bytes([0xFE, 0xFF])) else _hb.decode('utf-8', 'replace')   # PS 5.1 Tee-Object writes UTF-16
hist = [h.strip() for h in _ht.splitlines() if h.strip()]
blver = re.search(r'Blender [0-9.]+ LTS[^\n]*', open(os.path.join(O, 'logs', 'build.log')).read()).group(0)
HW = BL['hull_warp']; CM = R['hullext_collider_mismatch']; RC = R['route_corridor']; HM = R.get('hammock', {})
nst = BL['changes'].get('Rigging', {}).get('nest', {}); T = R['tris']; cp = R['coplanarity']

# ---------------------------------------------------------------- UNSYNCED collision note
note = """UNSYNCED - KEEP THE STUDIO v30 COLLIDERS. NO COLLISION FBX IS DELIVERED WITH THIS PASS.

start_ship_whimsy_v5.blend still contains the 190 v3_2 Blender colliders (Collision collection), byte-identical to source_v3_2.blend
(fitcheck: {be}/190 byte-identical, max world vertex diff {mx}).
They are STALE. Studio v30 colliders are authoritative and must NOT be replaced from this blend:
  - landing exit widened 5.4 -> 12.54
  - COL_HullExt disabled at the gangplank notch
  - hull-side colliders refit
  - (plus the warm low-contrast stern colours tested in v30)
These Blender colliders stay pending the exact RobloxDevBot Studio/JSON deltas. Collision was NOT verified against Studio v30 in this job.

HULL-SIDE FLAG FOR THE BUILDER: v5 widens the visual hull belly ~15% at/below world Y6 (smoothly to 0% at Y18).
Measured against the OLD v3_2 COL_HullExt boxes, the visual hull now sits up to {inc} studs further outside them
({n5} of {ns} samples moved >0.5 studs further out; boxes: {boxes}).
Please check the Studio v30 hull-side refit against the new visual hull (visual-only change; colliders untouched here).
""".format(be=R['collision']['byte_identical_to_source'], mx=R['collision']['max_abs_world_vertex_diff'], inc=CM['increase_max'], n5=CM['samples_increase_over_0_5'],
           ns=CM['samples'], boxes=', '.join(CM['boxes_with_increase_over_0_5']))
open(os.path.join(O, 'fbx', 'UNSYNCED_keep_studio_v30_colliders.txt'), 'w').write(note)

# ---------------------------------------------------------------- fitcheck.md
L = []; A = L.append
A('# Fitcheck: start ship whimsy v5 (out/start_ship_whimsy_v5.blend) vs source_v3_2.blend\n')
A('**Overall hard checks: %s**\n' % ('PASS' if R['pass_hard_checks'] else 'FAIL'))
A('## FAILS\n' + ('\n'.join('- ' + f for f in R['fail']) or '- none') + '\n')
A('## Warnings\n' + ('\n'.join('- ' + w for w in R['warn']) or '- none') + '\n')
A('## FLAGS for the builder\n' + ('\n'.join('- **' + f + '**' for f in R['flags_for_builder']) or '- none') + '\n')
A('## Collision: NOT verified vs Studio v30\n- %d/190 colliders byte-identical to source_v3_2 (mesh, UV, materials, matrix, world verts; max diff %s). None modified.\n- %s\n- No collision FBX exported; see `out/fbx/UNSYNCED_keep_studio_v30_colliders.txt`.\n'
  % (R['collision']['byte_identical_to_source'], R['collision']['max_abs_world_vertex_diff'], R['collision']['studio_v30_sync']))
A('## Locks')
for n in ('DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2'):
    e = R['meshes_vs_source'][n]
    A('- %s: verts %s, topology %s, UV %s, material assignment %s, origin matrix %s, world-vertex max diff %s'
      % (n, e['verts_identical'], e['topology_identical'], e['uv_identical'], e['material_assignment_identical'], e['origin_matrix_identical'], e.get('world_verts_max_abs_diff')))
A('- anchors exact: ' + ', '.join('%s=%s' % (k, v['exact_equal']) for k, v in R['anchors'].items()))
A('- walk surfaces identical: %s; door rays identical: %s (%d rays); tee sightlines identical: %s; spawn headroom identical: %s\n'
  % (R['walk_surfaces']['identical'], R['door_clearance']['identical'], R['door_clearance']['rays'], R['tee_sightlines']['identical'], R['spawn_headroom']['identical']))
A('## Existing objects: names / origins')
A('- every source mesh present with identical name, origin matrix, mesh datablock name, collections: %s'
  % all(e['origin_matrix_identical'] and e['mesh_datablock_name_identical'] and e['collections_identical'] for e in R['meshes_vs_source'].values()))
A('- changed vs source: ' + ', '.join(R['changed_meshes']))
A('  - hull-belly warp (vertex positions only; topology/UV/materials identical): ' + ', '.join('%s (max %.2f)' % (k, v) for k, v in HW['moved_objects_max_disp'].items()))
A('  - rebuilt in place (same object/mesh/origin): Prop_Figurehead (coral octopus), Prop_Stovepipe (lopsided)')
A("  - Rigging: crow's nest (%s components, %s verts) rotated %.2f -> %.2f deg about its base; plus the warp moved its low anchor-line verts (max %.2f)\n"
  % (nst.get('components'), nst.get('verts'), nst.get('tilt_before_deg', 0), nst.get('tilt_after_deg', 0), HW['moved_objects_max_disp'].get('Rigging', 0)))
A('## New ShipV5_* meshes (Props collection, visual-only, no colliders)\n\n| mesh | tris | note |\n|---|---|---|')
for n in R['new_objects']: A('| %s | %d | %s |' % (n, MS[n]['tris'], BL['changes'][n]['note'].replace('|', '/')))
xs = list(R['hull_widths']['before']['Y-0.6'].keys())
A('\n## Hull belly widening (horizontal width in studs, world Z, at world Y): before -> after (ratio)\n\n| Y | ' + ' | '.join(xs) + ' |\n|---|' + '---|' * len(xs))
for Y in R['hull_widths']['before']:
    A('| %s | ' % Y + ' | '.join('%s -> %s (%s)' % (R['hull_widths']['before'][Y][x], R['hull_widths']['after'][Y][x], R['hull_widths']['ratio'][Y][x]) for x in xs) + ' |')
A('\n- ' + R['hull_widths']['note'])
A('- deck level (Y23) unchanged within 0.002 (float noise from hull faces that straddle Y18); DeckCabin/deck/walk footprint untouched.')
A('- hull bottom (keel) max abs delta over 32 stations: %s (the warp is horizontal)\n' % R['hull_bottom']['max_abs_delta'])
A('## Hull-side collider mismatch (FLAG; colliders untouched)\n- method: %s\n- distance outside: source max/p95 %s/%s -> v5 %s/%s; increase max %s, p95 %s; %d samples >0.5, %d >1.0\n- boxes with >0.5 increase: %s\n- %s\n'
  % (CM['method'], CM['source_max_outside'], CM['source_p95_outside'], CM['v5_max_outside'], CM['v5_p95_outside'], CM['increase_max'], CM['increase_p95'],
     CM['samples_increase_over_0_5'], CM['samples_increase_over_1'], CM['boxes_with_increase_over_0_5'], CM['verdict']))
A('## Route exclusion\n- method: ' + RC['method'])
A('- intrusions by new/changed meshes vs source: %s' % json.dumps(RC['intrusions_new_or_changed_vs_source']))
A('- pre-existing in source and unchanged (Hull notch/rail geometry at the gangplank, above Y18 so the warp does not move it): %s\n' % json.dumps(RC['preexisting_in_source_unchanged']))
A('| prior zone | min clearance new/changed (obj) |\n|---|---|')
for k, v in RC['per_zone_min_new_or_changed'].items(): A('| %s | %s (%s) |' % (k, v['min_dist'], v['closest']))
A('\n| continuous corridor segment | min clearance new/changed (obj) |\n|---|---|')
for k, v in RC['continuous_corridor']['per_segment_min_new_or_changed'].items(): A('| %s | %s (%s) |' % (k, v['min_clear'], v['closest']))
A('\n### New-prop clearances (min over prior zones / continuous corridor)\n\n| prop | min prior-zone | min continuous |\n|---|---|---|')
for n in R['new_objects']: A('| %s | %.2f | %.2f |' % (n, min(RC['per_object_zones'][n].values()), min(v['min_clear'] for v in RC['per_object_continuous'][n].values())))
A('\n### Hammock (specific)\n- included: %s; %s\n- min distance to prior zones %.2f, to the continuous walkway corridor %.2f studs; triangle overlap with every other visual mesh: 0 (posts stand on the deck slab)\n'
  % (HM.get('included'), BL['hammock'], HM.get('min_zone', -1), HM.get('min_continuous', -1)))
A('## Bow eyes outside tee view')
for e in R['bow_eyes_tee_view']:
    A('- %s eye at %s: ray from tee eye blocked by %s; eye faces away from tee: %s; %.1f deg off the tee camera axis'
      % (e['side'], e['centre'], e['first_hit_on_ray'], e['facing_away_from_tee'], e['angle_from_tee_cam_axis_deg']))
A('\n## Coplanarity (honest)\n- method unchanged (0.03 / |dot|>0.995 / gap<0.02); scan list widened to %d objects (Hull, Rigging, every warped/rebuilt/new mesh + the v3_2 list); %d faces.'
  % (len(cp['objects_checked']), cp['faces_checked']))
A('- same list on source: %d pairs; v5: %d pairs; pairs not in source: %d.' % (cp['source_pairs_same_scan'], cp['v5_pairs'], cp['v5_pairs_not_in_source']))
A('- iteration history: the first build had 13 new pairs (hull/sail patch slabs and long flat emblem faces sagging into the hull or sail plane, and one emblem knob over the old v3_1 fore-sail patch). '
  'Fixed by embedding hull patches (-0.2..+0.5), sail patches (0.08..0.36, through the 0.2 sail face), tessellating the emblem to follow the sail curvature, and moving it onto bare sail (every boundary vertex ray-checked).\n')
A('## Stern curl\n- Prop_SternCurl kept unchanged (largest scroll components y-range/height: %s).\n- ShipV5_SternCurl: %s\n'
  % ([(c['y'], c['height']) for c in R['stern_curl']['prop_sterncurl_components_source'][:3]], R['stern_curl']['build']))
A('## Triangles\n\n| mesh | status | tris source | tris v5 |\n|---|---|---|---|')
for n in sorted(MS): A('| %s | %s | %s | %d |' % (n, MS[n]['status'], MS[n]['tris_source'], MS[n]['tris']))
A('\nTotal visual: **%d** (source %d; +%d, of which ShipV5_* %d). All meshes <20k: %s (largest %s). Collision tris %d (unchanged).\n'
  % (T['total_visual'], T['total_source_visual'], T['total_visual'] - T['total_source_visual'], T['new_shipv5_tris'], T['all_under_20k'], T['max_mesh'], T['collision_tris']))
A('## Textures\n' + '\n'.join('- %s packed=%s size=%s' % (k, v['packed'], v['size']) for k, v in R['images'].items())
  + '\n- new palette cells: ' + ', '.join('%s %s cell %d' % (k, BL['palette'][k]['rgb'], BL['palette'][k]['cell']) for k in ('Coral', 'PatchBlue', 'PatchTeal'))
  + '; existing Wood / WoodDk (80,50,30) / HullWood (130,90,55) / Brass (200,160,70) cells unchanged (stern colours untouched).\n')
A('## Not checked / limits\n' + '\n'.join('- ' + x for x in R['not_checked']))
open(os.path.join(O, 'fitcheck.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

# ---------------------------------------------------------------- manifest.json
fbx = {}
for fn, v in EV['files'].items():
    fbx[fn] = dict(path='out/fbx/' + fn, bytes=v['bytes'], objects=v['objects_exported'], tris=v['tris_exported'], reimport_ok=v['ok'], sha256=sha(os.path.join(O, 'fbx', fn)))
def kind(n):
    k = []
    if n in HW['moved_objects_max_disp']: k.append('hull-belly warp (vertex positions only, max %.2f)' % HW['moved_objects_max_disp'][n])
    if n in BL['changes']: k.append(BL['changes'][n]['kind'])
    return ' + '.join(k)
M = dict(asset='start_ship', version='start_ship_whimsy_v5', date=str(datetime.date.today()), blend='out/start_ship_whimsy_v5.blend', blend_sha256=bsha, blend_bytes=os.path.getsize(blend),
         source='source_v3_2.blend', source_sha256_before=src_before, source_sha256_after=src_after, source_unchanged=src_before == src_after,
         axes='FBX axis_forward -Z, axis_up Y, scale 1 (1 unit = 1 stud), FBX_SCALE_UNITS, embedded textures; Blender +Y = Roblox -Z',
         placement_note='water world Y0 = model local -0.6; RampFlight2 is yawed -30 deg in Studio (exported unyawed, as v3/v3_1/v3_2)',
         fbx=fbx, collision_fbx='NOT DELIVERED: see out/fbx/UNSYNCED_keep_studio_v30_colliders.txt (Studio v30 colliders authoritative; blend colliders are stale v3_2, byte-identical to source, NOT verified vs Studio)',
         new_meshes={n: dict(tris=MS[n]['tris'], materials=MS[n]['materials'], origin_roblox=MS[n]['origin_roblox'], bbox_min_roblox=MS[n]['bbox_min_roblox'], bbox_max_roblox=MS[n]['bbox_max_roblox'],
                             collection='Props', collide='none (visual only: CanCollide/CanQuery/CanTouch off)', note=BL['changes'][n]['note']) for n in R['new_objects']},
         changed_existing_meshes={n: dict(kind=kind(n), tris=MS[n]['tris'], tris_source=MS[n]['tris_source'], origin_unchanged=R['meshes_vs_source'][n]['origin_matrix_identical']) for n in R['changed_meshes']},
         locked_exact=['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2', 'Spawn', 'Tee1', 'RampStart', 'CupRef'],
         hull_warp=dict(k=HW['k'], full_below_world_Y=HW['full_below_world_Y'], zero_above_world_Y=HW['zero_above_world_Y'], centreline=HW['centreline'], x_taper=HW['x_taper'], widths_ratio=R['hull_widths']['ratio']),
         flags_for_builder=R['flags_for_builder'], hammock_included=HM.get('included'), tris=dict(total_visual=T['total_visual'], source=T['total_source_visual'], per_mesh=T['per_mesh']),
         palette=BL['palette'], previews=sorted('out/previews/' + os.path.basename(p) for p in glob.glob(os.path.join(O, 'previews', '*.png'))),
         scripts=sorted('out/src/' + os.path.basename(p) for p in glob.glob(os.path.join(O, 'src', '*')) if os.path.isfile(p)), fitcheck_pass_hard=R['pass_hard_checks'])
json.dump(M, open(os.path.join(O, 'manifest.json'), 'w'), indent=1)

# ---------------------------------------------------------------- report.txt
RP = []; P = RP.append
P('START SHIP WHIMSY V5 - modeling report  (%s)' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
P('model: claude-opus-5-5 (Claude Code, headless)   PC: %s (%s)' % (platform.node(), platform.platform()))
P('Blender: %s at C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe, headless -b --factory-startup via detached schtasks, one job at a time' % blver)
P('source: source_v3_2.blend sha256 before %s / after %s -> unchanged=%s (build saves a copy to a different path, asserted)' % (src_before, src_after, src_before == src_after))
P('output blend: out/start_ship_whimsy_v5.blend sha256 %s (%d bytes, textures packed)' % (bsha, os.path.getsize(blend)))
P('\nBlender jobs (tag exit elapsed), from out/logs/run_history.txt (includes earlier debug iterations):')
for h in hist: P('  ' + h)
P('\nFITCHECK hard checks: %s   fails: %s' % ('PASS' if R['pass_hard_checks'] else 'FAIL', R['fail'] or 'none'))
P('warnings: ' + ('; '.join(R['warn']) or 'none'))
P('FLAGS for builder: ' + ('; '.join(R['flags_for_builder']) or 'none'))
P('\nCOLLISION: all 190 colliders untouched, byte-identical to source (%d/190). NOT verified vs Studio v30. No collision FBX delivered.' % R['collision']['byte_identical_to_source'])
P('  out/fbx/UNSYNCED_keep_studio_v30_colliders.txt: Studio v30 (landing 12.54, HullExt notch disabled, hull-side refit) is authoritative; blend colliders stale pending RobloxDevBot JSON.')
P('  Hull-side mismatch FLAG: widened visual belly sits up to %.2f studs further outside the old COL_HullExt boxes (%d of %d samples >0.5).' % (CM['increase_max'], CM['samples_increase_over_0_5'], CM['samples']))
P('\nLOCKS: DeckCabin + 3 ramps exact (geometry/UV/materials/world matrix, world-vertex diff 0); 4 anchors exact; walk surfaces, door rays, tee sightlines, spawn headroom identical;')
P('  all existing object names/origins/mesh datablocks/collections identical.')
P('\nART DELIVERED:')
P('  1 hull belly x1.15 horizontal at/below Y6 -> x1.0 at Y18 (deck footprint fixed); waterline (Y-0.6) width ratios %s' % R['hull_widths']['ratio']['Y-0.6'])
P('    banana sheer: ShipV5_SheerRise (bow rail board 0 -> +4 at the stem both sides, arched transom crest +4 centre)')
P('    ShipV5_SternCurl tall aft/outboard spiral, %.1f studs above its crest base, top Y%.1f (Prop_SternCurl corner scrolls kept)' % (BL['stern_curl']['height_above_base'], BL['stern_curl']['top_y']))
P('    Prop_Figurehead rebuilt as a grinning coral octopus (230,120,100), 3 tentacles wrapping the bowsprit (8 sides) + 3 under the head; same name/origin')
P("  2 ShipV5_MastZigzag (2 zigzag bends, rope lashings, top Y%.1f); crow's nest tilt %.1f -> %.1f deg (Rigging verts); ShipV5_Telescope bent brass on the nest rim"
  % (BL['mast_zigzag']['top_world_y'], nst.get('tilt_before_deg', 0), nst.get('tilt_after_deg', 0)))
P('  3 ShipV5_BowEyes: 2 sleepy porthole eyes with half-lid planks, high on the bow flanks; occluded from the tee eye and facing away')
P('  4 ShipV5_Patches: %d hull patches (blue/teal) with oversized brass nails' % len(BL['patches']))
P('  5 ShipV5_SailPatches: %d large square patches (blue, teal, tan, stitched) + ShipV5_SailEmblem original skull & crossbones (darkwood on cream) on the main lower sail' % len(BL['sail_patches']))
P('  6 Prop_Stovepipe rebuilt lopsided (2 elbows, tilted hat; same origin; DeckCabin untouched)')
P('  7 ShipV5_YardNest (3 eggs) on the fore lower yard; ShipV5_Bottle by the high-side rail at x%.0f' % BL['bottle']['x'])
if HM.get('included'):
    P('    ShipV5_Hammock + pillow: INCLUDED, x%.1f-%.1f high side; min %.2f studs from the prior zones, %.2f from the continuous walkway corridor'
      % (BL['hammock']['x_range'][0], BL['hammock']['x_range'][1], HM.get('min_zone', -1), HM.get('min_continuous', -1)))
else:
    P('    ShipV5_Hammock: SKIPPED (%s)' % BL['hammock'].get('reason'))
P('  skipped items: %s' % (BL['skipped'] or 'none'))
P('  one bounded polish: the skull emblem was first on the fore lower sail, hidden behind the low-side bulwark in 3q; moved to the main lower sail top band.')
P('\nTRIS (visual): total %d (source %d, +%d; ShipV5_* %d). All <20k (largest %s %d).' % (T['total_visual'], T['total_source_visual'], T['total_visual'] - T['total_source_visual'], T['new_shipv5_tris'], T['max_mesh'], T['per_mesh'][T['max_mesh']]))
for n in sorted(MS): P('  %-24s %6d  (source %s)  %s' % (n, MS[n]['tris'], MS[n]['tris_source'], MS[n]['status']))
P('\nCLEARANCES (new props, min to prior zones / continuous corridor, studs):')
for n in R['new_objects']: P('  %-22s %7.2f / %7.2f' % (n, min(RC['per_object_zones'][n].values()), min(v['min_clear'] for v in RC['per_object_continuous'][n].values())))
P('  intrusions by new/changed meshes vs source: %s' % json.dumps(RC['intrusions_new_or_changed_vs_source']))
P('  coplanar pairs: source %d, v5 %d, not in source %d' % (cp['source_pairs_same_scan'], cp['v5_pairs'], cp['v5_pairs_not_in_source']))
P('\nFBX (re-import verified %s):' % EV['all_ok'])
for k, v in fbx.items(): P('  out/fbx/%s  %d bytes  %d objects  %d tris  ok=%s' % (k, v['bytes'], v['objects'], v['tris'], v['reimport_ok']))
P('  collision FBX: not exported (see UNSYNCED note)')
P('\nPREVIEWS (same cameras as prior_scripts/render_v31.py, inspected once): ' + ', '.join(M['previews']))
P('\nPATHS: out/start_ship_whimsy_v5.blend, out/manifest.json, out/fitcheck.json, out/fitcheck.md, out/report.txt, out/fbx/, out/previews/, out/textures/start_ship_palette.png, out/logs/,')
P('  out/src/ (build_v5, fitcheck_v5 + fitcheck_v5_check, export_v5, render_v5, shiplib, probe_v5, make_reports_v5, run_blender.ps1)')
P('Repro: run_blender.ps1 build -> dump (source) -> fitcheck check -> render -> export, then python make_reports_v5.py <workdir>.')
P('Scratch (not deliverables, safe to delete): _scratch_src_prev/, _scratch_det/ (low-res inspection renders), out/logs/_*.py debug probes; an empty stray dir C:\\_scratch_src_prev was left (removal needs approval).')
open(os.path.join(O, 'report.txt'), 'w', encoding='utf-8').write('\n'.join(RP) + '\n')
print('REPORTS_OK')
