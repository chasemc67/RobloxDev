"""Round 4 'walls' props stage (adapted from railskin_props.py): H11 / H12 rail skins vs the Round 4 holes.json
(H11 slot lintel 1.17 -> 1.27 + __cut2/3 side pieces; H12 stern wall line z -18 -> -18.01). Run after
  blender -b --factory-startup -P out_props/_src/build_all.py -- --only aa_h11_rails,aa_h12_rails      (FBX + previews)
then
  blender -b --factory-startup -P walls_props.py -- --no-render
1. exec the unchanged build_all.py (no previews) writing ONLY aa_h11_dressing.fbx / aa_h12_dressing.fbx (they embed the rail skins);
   manifest/.blend writes redirected; diff the regenerated manifest vs the current one, refresh the 4 entries, add pass_walls (+ the aa_h11_ice_floe notes text)
2. reimport-check the 4 FBXs: tris/bbox = manifest, < 20k, one material/mesh; rails == generator; dressing minus its rail skin
   == the pre-rebuild dressing minus the pre-rebuild rail skin (every other merged prop byte-for-byte in geometry)
3. swap the rail-skin (and dressing, if present) meshes in aurora_props_p1.blend / aurora_props_p1_in_world.blend"""
import bpy, os, sys, json, datetime
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent
P = R / 'out_props'
BK = R / 'out_props_bak_walls'
RAILS = ['aa_h11_rails', 'aa_h12_rails']
DRESS = ['aa_h11_dressing', 'aa_h12_dressing']
TARGET = set(RAILS + DRESS)


def log(s):
    print('[walls] ' + s, flush=True)
    with open(R / 'PROGRESS.md', 'a', encoding='utf8') as f:
        f.write(datetime.datetime.now().isoformat() + ' - WALLS PROPS ' + s + '\n')


assert '--no-render' in sys.argv
src = open(P / '_src/build_all.py', encoding='utf8').read()


def rep(a, b):
    global src
    assert src.count(a) == 1, a
    src = src.replace(a, b)


rep('def export_fbx(root, objs, path):\n',
    'def export_fbx(root, objs, path):\n    if os.path.splitext(os.path.basename(path))[0] not in RS_DRESS:\n        return\n    RS_WRITTEN.append(path)\n')
rep('json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)', 'json.dump(manifest, open(RS_REGEN, "w"), indent=1)')
rep('bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "aurora_props_p1.blend"), compress=True)', 'pass')
(R / 'props_work').mkdir(exist_ok=True)
written = []
g = {'__file__': str(P / '_src/build_all.py'), '__name__': '__main__', 'RS_WRITTEN': written, 'RS_DRESS': set(DRESS),
     'RS_REGEN': str(R / 'props_work/manifest_regen_walls.json')}
exec(compile(src, str(P / '_src/build_all.py'), 'exec'), g)
import aalib, registry, holesdata as D
rel = sorted('fbx/' + os.path.basename(p) for p in written)
assert rel == sorted(f'fbx/{d}.fbx' for d in DRESS), rel
log('re-exported dressing FBXs: ' + ', '.join(rel))

# ---------------------------------------------------------------- 1. manifest
old = json.load(open(P / 'manifest.json'))
regen = json.load(open(R / 'props_work/manifest_regen_walls.json'))


def diffs(a, b, path=''):
    out = []
    if type(a) != type(b):
        return [f'{path}: {str(a)[:80]} -> {str(b)[:80]}']
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f'{path}/{k}: {"added" if k not in a else "removed"}')
            else:
                out += diffs(a[k], b[k], f'{path}/{k}')
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f'{path}: len {len(a)} -> {len(b)}')
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += diffs(x, y, f'{path}[{x.get("name", x.get("file", i)) if isinstance(x, dict) else i}]')
    elif a != b:
        out.append(f'{path}: {str(a)[:80]} -> {str(b)[:80]}')
    return out


MOVERS = ('aa_h12_paddle_wheel', 'aa_h14_icicle_bell')
D_ = [d for k in regen for d in diffs(old.get(k), regen[k], k)]
known = [d for d in D_ if any(m in d for m in MOVERS) and ('/collision' in d)]          # Round-3 collider notes added after build_all
floe_note = [d for d in D_ if 'aa_h11_ice_floe' in d and d.split(':')[0].endswith('/notes')]   # Round 4: lintel 1.17 -> 1.27 in the note text
known += floe_note
other = [d for d in D_ if d not in known]
rail_d = [d for d in other if any(t in d for t in TARGET)]
outside = [d for d in other if d not in rail_d]
log(f'manifest regen vs current: {len(D_)} differences ({len(known) - len(floe_note)} = the known mover collider notes, {len(floe_note)} = aa_h11_ice_floe notes text); rail-skin/dressing entries: {rail_d}; outside: {outside}')
assert not outside, outside
new = json.loads(json.dumps(old))
for i, p in enumerate(new['props']):
    if p['name'] in RAILS:
        rp = next(q for q in regen['props'] if q['name'] == p['name'])
        new['props'][i] = rp
    if p['name'] == 'aa_h11_ice_floe':
        new['props'][i]['notes'] = next(q for q in regen['props'] if q['name'] == p['name'])['notes']
for i, h in enumerate(new['hole_dressing_files']):
    if os.path.splitext(os.path.basename(h['file']))[0] in DRESS:
        new['hole_dressing_files'][i] = next(q for q in regen['hole_dressing_files'] if q['file'] == h['file'])
assert json.dumps({k: v for k, v in new.items()}, sort_keys=True) != '' and [d for k in regen for d in diffs(new.get(k), regen[k], k) if d not in known] == []

# ---------------------------------------------------------------- 2. reimport checks
from mathutils import Vector


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def snap(path):
    obs = load(path)
    tris, verts = {}, {}
    for o in obs:
        o.data.calc_loop_triangles()
        tris[o.name] = len(o.data.loop_triangles)
        key = o.material_slots[0].material.name.split('.')[0]
        verts.setdefault(key, []).extend(tuple(round(c, 4) for c in (o.matrix_world @ x.co)) for x in o.data.vertices)
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    size = [max(p.x for p in pts) - min(p.x for p in pts), max(p.z for p in pts) - min(p.z for p in pts), max(p.y for p in pts) - min(p.y for p in pts)]
    return dict(n=len(obs), tris=tris, verts=verts, one=all(len(o.material_slots) == 1 for o in obs),
                imgs=len([i for i in bpy.data.images if i.source == 'FILE']), size=size)


want = {p['fbx']: p for p in new['props']}
want.update({h['file']: h for h in new['hole_dressing_files']})
val = json.load(open(P / 'fbx_validation.json'))
idx = {r['file']: i for i, r in enumerate(val['files'])}
checks = {}
S = {}
for nm in RAILS + DRESS:
    f = f'fbx/{nm}.fbx'
    S[nm] = (snap(P / f), snap(BK / f))
    s, s0 = S[nm]
    m = want[f]
    berr = max(abs(a - b) for a, b in zip(s['size'], m['bbox_size_studs']))
    ok = sum(s['tris'].values()) == m['triangles'] and max(s['tris'].values()) < 20000 and sum(s['tris'].values()) < 20000 and s['one'] and berr < .05
    r = dict(file=f, passed=ok, meshes=s['n'], tris=sum(s['tris'].values()), manifest_tris=m['triangles'], max_mesh_tris=max(s['tris'].values()),
             one_material_per_mesh=s['one'], embedded_textures=s['imgs'], bbox_size=[round(v, 3) for v in s['size']], bbox_err=round(berr, 4))
    val['files'][idx[f]] = r
    changed = sorted(k for k in set(s['verts']) | set(s0['verts']) if sorted(s['verts'].get(k, [])) != sorted(s0['verts'].get(k, [])))
    checks[f] = dict(tris_before=sum(s0['tris'].values()), tris_after=r['tris'], materials_with_changed_vertices=changed)
    assert ok, (f, r)

# rails == generator (hole frame, Roblox axes, 4 dp)
for nm in RAILS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('g')
    bpy.context.scene.collection.children.link(col)
    pr = next(p for p in registry.PROPS if p['name'] == nm)
    aalib._scratch = None
    pb = aalib.PB(nm)
    pr['fn'](pb)
    _, objs = pb.finalize(col, pr.get('smooth_angle', 40))
    G = {}
    for o in objs:
        G.setdefault(aalib.mat_of(o.name), []).extend(tuple(round(c, 4) for c in (o.matrix_world @ v.co)) for v in o.data.vertices)
    F = S[nm][0]['verts']
    eq = set(G) == set(F) and all(np.allclose(np.unique(np.array(G[k]), axis=0), np.unique(np.array(F[k]), axis=0), atol=2e-4) for k in G)
    checks[f'fbx/{nm}.fbx']['equals_generator'] = bool(eq)
    assert eq, nm

# dressing: everything except the rail skin is unchanged (rails are placed at the hole origin, yaw 0, scale 1)
for nm, rn in zip(DRESS, RAILS):
    pl = next(p for p in registry.PROPS if p['name'] == rn)['placements']
    assert len(pl) == 1 and pl[0]['pos'] == [0, 0, 0] and pl[0].get('yaw', 0.0) == 0.0 and pl[0].get('scale', 1.0) == 1.0, pl
    res = {}
    for k in set(S[nm][0]['verts']) | set(S[nm][1]['verts']):
        def minus(a, b):
            from collections import Counter
            c = Counter(a)
            c.subtract(Counter(b))
            assert all(v >= 0 for v in c.values()), 'rail verts not found in dressing'
            return sorted(c.elements())
        new_rest = minus(S[nm][0]['verts'].get(k, []), S[rn][0]['verts'].get(k, []))
        old_rest = minus(S[nm][1]['verts'].get(k, []), S[rn][1]['verts'].get(k, []))
        res[k] = new_rest == old_rest
    checks[f'fbx/{nm}.fbx']['non_rail_geometry_identical_per_material'] = res
    assert all(res.values()), (nm, res)
val['all_passed'] = all(r['passed'] for r in val['files'])
val['pass_walls'] = dict(re_exported=sorted(f'fbx/{n}.fbx' for n in RAILS + DRESS), checks=checks,
                         note='rail skins of H11/H12 rebuilt from the Round 4 walls holes.json; every other FBX untouched')
json.dump(val, open(P / 'fbx_validation.json', 'w'), indent=1)
log('reimport checks: ' + json.dumps(checks))
assert val['all_passed']

# ---------------------------------------------------------------- manifest write
new['pass_walls'] = (
    "Round 4 'walls' (playtest-log.md 'Round 4: wall clearance (fitcheck)'): rail skins rebuilt against the Round 4 holes.json. "
    "H11: rail5/berg18 floe-slot lintel underside 1.17 -> 1.27 (__cut1 centre y 1.835, height 1.13; __cut2/__cut3 side pieces centre y 0.56, height 1.42); "
    "the floe mesh aa_h11_ice_floe is unchanged (top 1.12, now 0.15 under the lintel). H12: icebreaker stern wall line z -18 -> -18.01 "
    "(rail2/hull13 centre z -18.26; rail3/hull18 centre z -21.005, length 5.99; mitred rail1 centre -8.005 length 21.01, hull14 centre -26.005 length 15.99), "
    "0.06 behind the paddles; paddle wheel, felt and aa_h12_icebreaker body unchanged (its hull boxes end at z -18.2, inside the wall skins; the skins are the stern faces). "
    "Re-exported: fbx/aa_h11_rails.fbx, fbx/aa_h12_rails.fbx and the per-hole dressing that embeds them, fbx/aa_h11_dressing.fbx, fbx/aa_h12_dressing.fbx "
    "(+ rail previews, previews/walls/). Tris: " + ', '.join(f"{n} {checks['fbx/' + n + '.fbx']['tris_after']}" for n in RAILS + DRESS) +
    " (tris and overall bboxes unchanged; skins.py bolt-plate count uses int(L/2 + 0.01) so the 5.99/15.99 walls keep 3/8 plates). Only rail-skin vertices moved (H11 <= 0.10, H12 <= 0.01); "
    "all other merged props identical. Mover collision FBX (aa_h12_paddle_wheel_collision, aa_h14_icicle_bell_collision) are holes.json blockers - unchanged. "
    "Fitcheck: fitcheck_walls_validated.txt (H11 lintel expectation 1.27).")
json.dump(new, open(P / 'manifest.json', 'w'), indent=1)
log('manifest.json: refreshed ' + ', '.join(RAILS + DRESS) + ' entries + aa_h11_ice_floe notes, pass_walls added')

# ---------------------------------------------------------------- 3. blends
bpy.context.preferences.filepaths.save_version = 0


def swap_mesh(root, old_obs, new_obs, label):
    """old child mesh <- imported FBX mesh, mapped into the old child's local frame (prop frame = old root frame)"""
    assert set(old_obs) == set(new_obs), (label, sorted(old_obs), sorted(new_obs))
    out = {}
    for k, o in old_obs.items():
        n_ = new_obs[k]
        M = o.matrix_world.inverted() @ root.matrix_world @ n_.matrix_world
        me = n_.data.copy()
        me.transform(M)
        a = np.array([tuple(v.co) for v in o.data.vertices])
        b = np.array([tuple(v.co) for v in me.vertices])
        same = a.shape == b.shape and np.allclose(np.sort(a.round(4), 0), np.sort(b.round(4), 0), atol=2e-4)
        if a.shape == b.shape:          # order-independent: Hausdorff distance between the old and new vertex sets
            dd = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)) if len(a) <= 6000 else None
            disp = float(max(dd.min(0).max(), dd.min(1).max())) if dd is not None else float(np.abs(np.sort(a, 0) - np.sort(b, 0)).max())
        else:
            disp = None
        if same:
            bpy.data.meshes.remove(me)
            out[k] = 'unchanged'
            continue
        assert disp is not None and disp <= 0.2, (label, k, a.shape, b.shape, disp)     # same topology, only the 0.10 / 0.01 wall moves
        mats = list(o.data.materials)
        od = o.data
        o.data = me
        me.materials.clear()
        for mt in mats:
            me.materials.append(mt)
        me.name = od.name
        if od.users == 0:
            bpy.data.meshes.remove(od)
        out[k] = f'replaced (max vertex move {disp:.3f})'
    return out


RAIL_MATS = {}
for bname in ['aurora_props_p1.blend', 'aurora_props_p1_in_world.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(P / bname))
    done = []
    for name in RAILS + DRESS:
        roots = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.split('.')[0] == name]
        if not roots:
            done.append(f'{name}: not in this .blend')
            continue
        for root in roots:
            old_obs = {c.name.split('.')[0].split('__')[1]: c for c in root.children if c.type == 'MESH'}
            before = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=str(P / 'fbx' / f'{name}.fbx'))
            bpy.context.view_layer.update()
            newo = [o for o in bpy.data.objects if o not in before]
            res = swap_mesh(root, old_obs, {o.name.split('.')[0].split('__')[1]: o for o in newo if o.type == 'MESH'}, name)
            for o in newo:
                bpy.data.objects.remove(o, do_unlink=True)
            if name in RAILS:
                RAIL_MATS[name] = {k for k, v in res.items() if v != 'unchanged'}
            else:          # dressing: only materials the rail skin carries may change
                rn = RAILS[DRESS.index(name)]
                bad = {k for k, v in res.items() if v != 'unchanged'} - set(S[rn][0]['verts'])
                assert not bad, (bname, name, bad, res)
            done.append(f'{root.name}: {res}')
    bpy.ops.wm.save_mainfile(compress=True)
    log(f'{bname}: {done}')
log('walls props stage finished')
