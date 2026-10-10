"""Bundle the Lantern Grove prop FBXs into a few 'library' FBXs for one-shot import into Roblox Studio.

  B=/Applications/Blender.app/Contents/MacOS/Blender
  $B -b --factory-startup -P make_library.py -- <models dir> <out dir>

Each prop keeps its own root (named <prop>) with one child mesh per material (<prop>__<Material>), exactly as in
fbx/<prop>.fbx, but the root is moved to a grid cell so the props don't overlap. library.json records every prop's
grid offset in Roblox studs (x, 0, z), so in Studio: model:PivotTo(model:GetPivot() - offset) restores the origin
(or set WorldPivot = CFrame.new(offset) on the imported model). Same export settings as models/_src (studs, -Z fwd, Y up).
"""
import json
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
MODELS, OUT = argv[0], argv[1]
man = json.load(open(os.path.join(MODELS, "manifest.json")))
BUNDLES = {
    "lg_lib_a": ["hero", "moving", "stream", "rail_kit"],
    "lg_lib_b": ["nature", "lanterns", "tee_sign"],
}
GAP = 4.0
ROW_W = 120.0
index = {"note": __doc__, "bundles": {}}

for bundle, groups in BUNDLES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "NONE"
    props = [p for p in man["props"] if p["group"] in groups]
    cx, cz, rowd = 0.0, 0.0, 0.0
    entries = {}
    for p in props:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=os.path.join(MODELS, p["fbx"]), axis_forward="-Z", axis_up="Y", global_scale=1.0)
        new = [o for o in bpy.data.objects if o not in before]
        roots = [o for o in new if o.parent is None]
        sx, sy, sz = p["bbox_size_studs"]
        if cx + sx > ROW_W and cx > 0:
            cx, cz, rowd = 0.0, cz + rowd + GAP, 0.0
        # Roblox offset (x, 0, z); Blender: x = x, y = -z
        ox, oz = cx + sx / 2, cz + sz / 2
        for r in roots:
            r.location.x += ox
            r.location.y += -oz
        # mesh children for the report
        meshes = sorted(o.name for o in new if o.type == "MESH")
        entries[p["name"]] = {"offset": [round(ox, 3), 0, round(oz, 3)], "roots": [r.name for r in roots], "meshes": meshes,
                              "bbox": p["bbox_size_studs"]}
        cx += sx + GAP
        rowd = max(rowd, sz)
    # measure lantern_large height as an import-scale check (should be ~2.12)
    out = os.path.join(OUT, bundle + ".fbx")
    bpy.ops.export_scene.fbx(filepath=out, use_selection=False, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z",
                             axis_up="Y", global_scale=1.0, path_mode="COPY", embed_textures=True, add_leaf_bones=False,
                             bake_anim=False, mesh_smooth_type="FACE")
    tris = sum(len(pl.vertices) - 2 for o in bpy.data.objects if o.type == "MESH" for pl in o.data.polygons)
    index["bundles"][bundle] = {"file": bundle + ".fbx", "props": entries, "triangles": tris,
                                "meshes": sum(len(e["meshes"]) for e in entries.values())}
    print("BUNDLE", bundle, len(entries), "props", tris, "tris", index["bundles"][bundle]["meshes"], "meshes")

json.dump(index, open(os.path.join(OUT, "library.json"), "w"), indent=1)
