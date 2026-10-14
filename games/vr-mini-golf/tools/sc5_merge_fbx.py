"""Stage sc5: merge many Sugarloaf FBX files into ONE FBX for a single Studio 3D Importer pass.
Variant of merge_fbx_for_import.py for sources whose mesh objects share names (ground tiles, cacti groups):
every mesh is renamed <stem>__<suffix> (suffix = original name after '__'), and with --split-materials a
multi-material mesh is separated into one mesh per material (<stem>__<Material>), because a Roblox MeshPart
renders a single material. Geometry is not changed. Each source sits under one top-level Empty named its stem.

  Blender -b --factory-startup --python sc5_merge_fbx.py -- <out.fbx> <list.json> [--split-materials]

list.json: [{"stem":..., "fbx": absolute path}, ...]. Writes <out>_report.json with per-mesh Roblox-axis bounds
(center/size relative to the source pivot; Roblox = (bx, bz, -by)) and a re-import check (tris + bbox per mesh).
"""
import bpy, bmesh, json, re, sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT = Path(args[0]).resolve()
SOURCES = json.loads(Path(args[1]).read_text())
SPLIT = '--split-materials' in args
IMPORT_KW = dict(axis_forward='-Z', axis_up='Y', global_scale=1.0)
EXPORT_KW = dict(axis_forward='-Z', axis_up='Y', global_scale=1, path_mode='COPY', embed_textures=True,
                 add_leaf_bones=False, bake_anim=False)
SUFFIX = re.compile(r'\.\d{3}$')
TOL = 1e-3


def strip(n):
    return SUFFIX.sub('', n)


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def rbx_bounds(o):
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    lo = [min(v.x for v in ws), min(v.z for v in ws), -max(v.y for v in ws)]
    hi = [max(v.x for v in ws), max(v.z for v in ws), -min(v.y for v in ws)]
    return dict(center=[round((a + b) / 2, 4) for a, b in zip(lo, hi)], size=[round(b - a, 4) for a, b in zip(lo, hi)])


def import_fbx(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path), **IMPORT_KW)
    return [o for o in bpy.data.objects if o not in before]


bpy.ops.wm.read_factory_settings(use_empty=True)
meshes = {}   # final name -> info
problems = []
for s in SOURCES:
    stem = s['stem']
    new = import_fbx(s['fbx'])
    tops = [o for o in new if o.parent is None]
    root = bpy.data.objects.new('__tmp_root', None)
    bpy.context.scene.collection.objects.link(root)
    for o in tops:
        mw = o.matrix_world.copy()
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
        o.matrix_world = mw
    src_meshes = [o for o in new if o.type == 'MESH']
    # rename non-mesh descendants out of the way
    for o in new:
        if o.type != 'MESH':
            o.name = '__x_%s_%s' % (stem, strip(o.name))
    for o in src_meshes:
        orig = strip(o.name)
        suffix = orig.split('__', 1)[1] if '__' in orig else orig
        pieces = [o]
        if SPLIT and len([m for m in o.data.materials if m]) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='MATERIAL')
            bpy.ops.object.mode_set(mode='OBJECT')
            pieces = [x for x in bpy.context.selected_objects if x.type == 'MESH']
        for p in pieces:
            mats = [m for m in p.data.materials if m]
            if len(pieces) > 1:
                # keep only used material slot
                used = {poly.material_index for poly in p.data.polygons}
                mname = strip(p.data.materials[min(used)].name) if used else 'Empty'
                name = '%s__%s' % (stem, mname)
            else:
                name = '%s__%s' % (stem, suffix)
            if name in meshes:
                problems.append('duplicate final name ' + name)
            p.name = name
            p.data.name = name
            used = sorted({poly.material_index for poly in p.data.polygons})
            meshes[name] = dict(stem=stem, source_object=orig, materials=[strip(p.data.materials[i].name) for i in used if p.data.materials[i]],
                                tris=tris(p), **rbx_bounds(p))
    # pin the per-source empty
    root.name = stem
    if root.name != stem:
        problems.append('empty name clash ' + stem)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(OUT), use_selection=True, **EXPORT_KW)

# re-import check
bpy.ops.wm.read_factory_settings(use_empty=True)
new = import_fbx(OUT)
got = {strip(o.name): o for o in new if o.type == 'MESH'}
fails = []
for name, info in meshes.items():
    o = got.get(name)
    if o is None:
        fails.append(name + ' missing'); continue
    b = rbx_bounds(o)
    err = max(abs(a - c) for a, c in zip(b['center'] + b['size'], info['center'] + info['size']))
    if tris(o) != info['tris'] or err > TOL:
        fails.append('%s tris %d/%d err %.4f' % (name, tris(o), info['tris'], err))
suffixed = [o.name for o in new if SUFFIX.search(o.name)]
tops = [o for o in new if o.parent is None]
report = dict(result='PASS' if not fails and not problems and not suffixed else 'FAIL', output=str(OUT),
              size_mb=round(OUT.stat().st_size / 1048576, 2), sources=len(SOURCES), top_level=len(tops),
              meshes=len(meshes), total_tris=sum(m['tris'] for m in meshes.values()),
              max_mesh_tris=max(m['tris'] for m in meshes.values()), split_materials=SPLIT,
              fails=fails, problems=problems, suffixed=suffixed, mesh_info=meshes)
Path(str(OUT)[:-4] + '_report.json').write_text(json.dumps(report, indent=1))
print('SC5_MERGE', report['result'], report['size_mb'], 'MB sources', len(SOURCES), 'meshes', len(meshes),
      'tris', report['total_tris'], 'max', report['max_mesh_tris'], 'fails', fails[:5], 'problems', problems[:5])
