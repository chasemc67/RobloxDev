"""v210b: put the rebuilt / new props into lantern_grove_props.blend and patch metadata-only manifest entries.
blender -b <lantern_grove_props.blend> -P update_blend_v210b.py -- <report.json>
  * replaced in place (same collection + grid location): bank_backing_stone, h8_alcove_bank_cladding
  * added (own collection, new row after the existing grid): rail_straight_4_h9, rail_straight_2_h9, rail_end_post_h9,
    h9_bank_lip
  * manifest: rail_straight_4_trim / rail_straight_2_trim / rail_end_post_trim get holes + notes from the registry
    (H9 moved to the _h9 kit); their geometry / FBX are unchanged so they are not rebuilt.
"""
import bpy, sys, os, json, importlib

REP = sys.argv[sys.argv.index("--") + 1:][0]
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import lglib, registry
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6",
          "props_pass7", "props_pass8", "props_pass10", "props_v210b"):
    importlib.import_module(m)
REG = {p["name"]: p for p in registry.PROPS}
REPLACE = ("bank_backing_stone", "h8_alcove_bank_cladding")
ADD = ("rail_straight_4_h9", "rail_straight_2_h9", "rail_end_post_h9", "h9_bank_lip")
META = ("rail_straight_4_trim", "rail_straight_2_trim", "rail_end_post_trim")


def build(name, col):
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(col, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
        lglib.box_uv_objects(objs)
    return root, objs


rep = {}
for name in REPLACE:
    old = bpy.data.objects[name]
    loc = tuple(old.location)
    col = list(old.users_collection)[0]
    kids = list(old.children)
    old_parts = sorted(o.name for o in kids)
    for o in kids + [old]:
        me = o.data if o.type == "MESH" else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    root, objs = build(name, col)
    root.location = loc
    rep[name] = dict(collection=col.name, location=[round(v, 4) for v in loc], old_parts=old_parts,
                     new_parts=sorted(o.name for o in objs), tris=lglib.tri_count(objs))
# new props: one row below the current grid (grid grows along +Y in build_all)
bpy.context.view_layer.update()
from mathutils import Vector
ymax = max((o.matrix_world @ Vector(c)).y for o in bpy.data.objects if o.type == "MESH" for c in o.bound_box)
x = 0.0
for name in ADD:
    assert name not in bpy.data.objects, name
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    root, objs = build(name, col)
    mn, mx = lglib.bbox_blender(objs)
    root.location = (x - mn.x, ymax + 4 - mn.y, 0)
    x += (mx.x - mn.x) + 4
    rep[name] = dict(collection=col.name, location=[round(v, 4) for v in root.location], old_parts=None,
                     new_parts=sorted(o.name for o in objs), tris=lglib.tri_count(objs))
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
bpy.ops.wm.save_mainfile(compress=True)
rep["materials"] = {k: bool(bpy.data.materials.get(k)) for k in ("BankLip", "OakDeep", "Limestone")}

# manifest: metadata-only refresh of the trim kit (holes / notes)
mp = os.path.join(OUT, "manifest.json")
man = json.load(open(mp))
for e in man["props"]:
    if e["name"] in META:
        fresh = registry.manifest_entry(REG[e["name"]])
        rep.setdefault("manifest_meta", {})[e["name"]] = dict(holes=[e["holes"], fresh["holes"]],
                                                              notes_changed=e["notes"] != fresh["notes"])
        e["holes"], e["notes"] = fresh["holes"], fresh["notes"]
json.dump(man, open(mp, "w"), indent=1)
json.dump(rep, open(REP, "w"), indent=1)
print("[blend]", json.dumps(rep))
