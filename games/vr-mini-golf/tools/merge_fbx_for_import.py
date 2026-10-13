"""Merge many FBX files into ONE FBX for a single Studio 3D Importer pass (generalized from
assets/vr-mini-golf/sugarloaf-canyon/models/_src/movers/merge_for_import.py, stage w).

Run headless:
  Blender -b --factory-startup --python merge_fbx_for_import.py -- <out.fbx> <in1.fbx> <in2.fbx> ...

Each source file goes under one top-level Empty named exactly its file stem at the world origin.
Materials are renamed <stem>__<Material>; images are de-duplicated by content. Export settings match the kits
(forward -Z, up Y, scale 1, textures embedded). The merged file is re-imported and every mesh's world bbox,
triangle count, material and texture are compared with the source file imported alone; the report is written
next to the output as <out>_merge_report.json.
"""
import bpy, json, hashlib, os, re, shutil, tempfile
from pathlib import Path
from mathutils import Vector

import sys
_args = sys.argv[sys.argv.index('--') + 1:]
OUT_FBX = Path(_args[0]).resolve()
OUT_DIR = OUT_FBX.parent
REPORT = OUT_DIR / (OUT_FBX.stem + '_merge_report.json')
_INPUTS = [Path(a).resolve() for a in _args[1:]]
TOL = 1e-4
TRI_LIMIT = 20000

IMPORT_KW = dict(axis_forward='-Z', axis_up='Y', global_scale=1.0)
EXPORT_KW = dict(axis_forward='-Z', axis_up='Y', global_scale=1, path_mode='COPY',
                 embed_textures=True, add_leaf_bones=False, bake_anim=False)

SUFFIX = re.compile(r'\.\d{3}$')


def strip_suffix(name):
    return SUFFIX.sub('', name)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_fbx(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path), **IMPORT_KW)
    return [o for o in bpy.data.objects if o not in before]


def image_of(mat):
    if not mat or not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            return n.image
    return None


def image_hash(img):
    if img is None:
        return None
    if img.packed_file:
        return hashlib.sha1(bytes(img.packed_file.data)).hexdigest()
    p = bpy.path.abspath(img.filepath)
    if os.path.isfile(p):
        return hashlib.sha1(Path(p).read_bytes()).hexdigest()
    return 'pixels:' + hashlib.sha1(bytes(str(list(img.pixels[:64])), 'utf8')).hexdigest()


def mat_base(name, stem=None):
    n = strip_suffix(name)
    if stem and n.startswith(stem + '__'):
        n = n[len(stem) + 2:]
    return n


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def wbbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return ([min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)])


def mesh_info(o, stem=None):
    mats = [m for m in o.data.materials if m]
    img = image_of(mats[0]) if mats else None
    lo, hi = wbbox(o)
    return dict(name=o.name, tris=tris(o), bbox_min=lo, bbox_max=hi,
                materials=[mat_base(m.name, stem) for m in mats],
                image=strip_suffix(Path(img.filepath).name or img.name) if img else None,
                image_hash=image_hash(img))


def descendants(o):
    out = []
    for c in o.children:
        out.append(c)
        out.extend(descendants(c))
    return out


files = sorted(_INPUTS, key=lambda p: p.name)
assert files, 'no input FBX'
assert len({f.stem for f in files}) == len(files), 'duplicate file stems'

# ---------------------------------------------------------------- 1. reference data
reference = {}
for f in files:
    reset()
    new = import_fbx(f)
    reference[f.stem] = {o.name: mesh_info(o) for o in new if o.type == 'MESH'}

# ---------------------------------------------------------------- 2. merge
reset()
problems = []
tex_dir = Path(tempfile.mkdtemp(prefix='sugarloaf_merge_tex_'))
img_by_key = {}      # (basename, hash) -> image
used_names = {}      # basename -> set(hash)
empties = []

for f in files:
    stem = f.stem
    new = import_fbx(f)
    tops = [o for o in new if o.parent is None]
    root = None
    for o in tops:
        if o.type == 'EMPTY' and strip_suffix(o.name) == stem and o.matrix_world.to_translation().length < 1e-6:
            root = o
            break
    if root is None:
        root = bpy.data.objects.new(stem, None)
        bpy.context.scene.collection.objects.link(root)
    for o in tops:
        if o is root:
            continue
        mw = o.matrix_world.copy()
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
        o.matrix_world = mw
    if root.name != stem:
        clash = bpy.data.objects.get(stem)
        if clash:
            clash.name = stem + '__clash'
            problems.append(f'object name clash on empty {stem}')
        root.name = stem
    empties.append(root)

    for o in descendants(root):
        src_name = strip_suffix(o.name)
        if o.name != src_name:
            if bpy.data.objects.get(src_name) is None:
                o.name = src_name
            else:
                problems.append(f'{stem}: object {o.name} clashes with {src_name}')
        if o.type != 'MESH':
            continue
        for slot in o.material_slots:
            m = slot.material
            if not m:
                continue
            base = mat_base(m.name)
            m.name = f'{stem}__{base}'
            img = image_of(m)
            if img is None:
                continue
            fname = strip_suffix(Path(img.filepath).name or img.name)
            h = image_hash(img)
            key = (fname, h)
            if key not in img_by_key:
                hashes = used_names.setdefault(fname, [])
                hashes.append(h)
                disk_name = fname if len(hashes) == 1 else f'{Path(fname).stem}_{len(hashes)}{Path(fname).suffix}'
                if len(hashes) > 1:
                    problems.append(f'info: different image content shares name {fname}; saved as {disk_name}')
                dst = tex_dir / disk_name
                if img.packed_file:
                    dst.write_bytes(bytes(img.packed_file.data))
                elif Path(bpy.path.abspath(img.filepath)).resolve() != dst.resolve():
                    shutil.copyfile(bpy.path.abspath(img.filepath), dst)
                ni = bpy.data.images.load(str(dst))
                ni.name = disk_name
                img_by_key[key] = ni
            ni = img_by_key[key]
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image is img:
                    n.image = ni

# drop now-unused imported images
for img in list(bpy.data.images):
    if img.users == 0:
        bpy.data.images.remove(img)

# ---------------------------------------------------------------- 3. export
OUT_DIR.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT_FBX), use_selection=True, **EXPORT_KW)

# ---------------------------------------------------------------- 4. verify
reset()
new = import_fbx(OUT_FBX)
merged_tops = [o for o in new if o.parent is None]
top_empties = [o for o in merged_tops if o.type == 'EMPTY']
all_meshes = [o for o in new if o.type == 'MESH']

per_file = {}
overall = True
for f in files:
    stem = f.stem
    root = bpy.data.objects.get(stem)
    entry = dict(empty_found=bool(root and root.type == 'EMPTY' and root.parent is None))
    if root and entry['empty_found']:
        entry['empty_at_origin'] = root.matrix_world.to_translation().length < TOL
    got = {o.name: mesh_info(o, stem) for o in descendants(root) if o.type == 'MESH'} if root else {}
    objs = []
    ok = entry['empty_found'] and entry.get('empty_at_origin', False) and set(got) == set(reference[stem])
    if set(got) != set(reference[stem]):
        entry['missing'] = sorted(set(reference[stem]) - set(got))
        entry['extra'] = sorted(set(got) - set(reference[stem]))
    for name, ref in sorted(reference[stem].items()):
        g = got.get(name)
        r = dict(name=name, tris=ref['tris'], bbox_min=[round(v, 6) for v in ref['bbox_min']],
                 bbox_max=[round(v, 6) for v in ref['bbox_max']], material=ref['materials'],
                 image=ref['image'])
        if g is None:
            r['pass'] = False
        else:
            d = max(abs(a - b) for a, b in zip(g['bbox_min'] + g['bbox_max'], ref['bbox_min'] + ref['bbox_max']))
            r['bbox_max_err'] = d
            r['merged_material'] = g['materials']
            r['pass_tris'] = g['tris'] == ref['tris']
            r['pass_bbox'] = d <= TOL
            r['pass_material'] = g['materials'] == ref['materials']
            r['pass_texture'] = g['image_hash'] == ref['image_hash']
            r['pass'] = r['pass_tris'] and r['pass_bbox'] and r['pass_material'] and r['pass_texture']
        ok = ok and r['pass']
        objs.append(r)
    entry['objects'] = objs
    entry['tris'] = sum(o['tris'] for o in objs)
    entry['pass'] = ok
    overall = overall and ok
    per_file[stem] = entry

total_tris = sum(tris(o) for o in all_meshes)
max_mesh = max(all_meshes, key=tris)
names = [o.name for o in new]
suffixed = [n for n in names if SUFFIX.search(n)]
mat_names = sorted(m.name for m in bpy.data.materials)
report = dict(
    result='PASS' if overall and len(top_empties) == len(files) and not suffixed else 'FAIL',
    output=str(OUT_FBX),
    size_bytes=OUT_FBX.stat().st_size,
    size_mb=round(OUT_FBX.stat().st_size / 1048576, 3),
    source_files=len(files),
    top_level_empties=len(top_empties),
    top_level_non_empty=[o.name for o in merged_tops if o.type != 'EMPTY'],
    mesh_objects=len(all_meshes),
    total_tris=total_tris,
    max_mesh=dict(name=max_mesh.name, tris=tris(max_mesh)),
    any_mesh_over_20000_tris=tris(max_mesh) > TRI_LIMIT,
    object_names_with_numeric_suffix=suffixed,
    materials=len(mat_names),
    images=sorted(i.name for i in bpy.data.images if i.size[0]),
    problems=problems,
    export_settings=EXPORT_KW,
    files=per_file,
)
REPORT.write_text(json.dumps(report, indent=1))
shutil.rmtree(tex_dir, ignore_errors=True)
print('MERGE_RESULT', report['result'], report['size_mb'], 'MB empties', len(top_empties),
      'meshes', len(all_meshes), 'tris', total_tris, 'max', report['max_mesh'], 'problems', problems)
