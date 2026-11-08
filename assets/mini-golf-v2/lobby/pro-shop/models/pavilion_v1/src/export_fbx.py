"""Derived FBX export (gitignored; regenerate from the .blend, never hand-edit).

Usage:
  blender -b <pro_shop_pavilion_v1.blend> --python export_fbx.py -- --output <pro_shop_pavilion_v1.fbx>
          [--with-collision <collision.fbx>]
Exports every mesh in collections flagged ps_export (no UI placeholder, anchors, proxies, env).
Roblox: scale 1.0, forward -Z, up Y, textures embedded.
"""
import argparse
import os
import sys

import bpy


def select(pred):
    bpy.ops.object.select_all(action="DESELECT")
    n = 0
    for o in bpy.context.scene.objects:
        if pred(o):
            o.hide_set(False)
            o.select_set(True)
            n += 1
    return n


def export(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=os.path.abspath(path), use_selection=True, object_types={"MESH"},
                             global_scale=1.0, apply_unit_scale=True, axis_forward="-Z", axis_up="Y",
                             path_mode="COPY", embed_textures=True, mesh_smooth_type="FACE",
                             use_mesh_modifiers=True, add_leaf_bones=False)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--with-collision", default=None)
    a = ap.parse_args(argv)

    def is_exp(o):
        c = o.users_collection[0] if o.users_collection else None
        return o.type == "MESH" and c is not None and c.get("ps_export", False)
    n = select(is_exp)
    export(a.output)
    print(f"EXPORTED {n} meshes -> {a.output}", flush=True)
    if a.with_collision:
        n = select(lambda o: o.name.startswith("COL_"))
        export(a.with_collision)
        print(f"EXPORTED {n} collision proxies -> {a.with_collision}", flush=True)


if __name__ == "__main__":
    main()
