"""v210b FBX re-import check (from reimport_v210.py): every FBX in models/fbx re-imported (Roblox frame), tris / bbox /
materials / per-part tris vs manifest (props and the per-hole dressing fbx[] entries), emission, embedded textures.
Run: LG_HOLES_JSON=<holes.json> blender -b --factory-startup -P models/_src/reimport_v210b.py
Writes _src/reimport_v210b.json."""
import bpy, os, sys, json
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import dressing_lib as DL

CHANGED = ("bank_backing_stone", "h8_alcove_bank_cladding", "dressing_h03_a", "dressing_h08_a")
NEW = ("rail_straight_4_h9", "rail_straight_2_h9", "rail_end_post_h9", "h9_bank_lip")
man = json.load(open(os.path.join(OUTD, "manifest.json")))
MP = {p["name"]: p for p in man["props"]}
DF = {f["fbx"]: f for h in man["dressing"]["holes"].values() for f in h.get("fbx", [])}


def lin2hex(c):
    s = [(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in c[:3]]
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02X}" for v in s)


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    bpy.context.view_layer.update()
    parts, allV = {}, []
    roots = [o.name for o in bpy.data.objects if o.parent is None]
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        V = np.stack([V[:, 0], V[:, 2], -V[:, 1]], -1)
        allV.append(V)
        mats = []
        for m in me.materials:
            bs = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m and m.node_tree else None
            mats.append(dict(name=m.name if m else None,
                             base_color=lin2hex(bs.inputs["Base Color"].default_value) if bs else None,
                             emission=round(float(bs.inputs["Emission Strength"].default_value), 3) if bs else None,
                             textures=sorted(n.image.name for n in m.node_tree.nodes
                                             if n.type == "TEX_IMAGE" and n.image) if m and m.node_tree else []))
        mn, mx = V.min(0), V.max(0)
        parts[o.name] = dict(tris=len(me.loop_triangles), materials=mats,
                             origin=[round(v, 4) for v in (mw[0, 3], mw[2, 3], -mw[1, 3])],
                             bbox_size=[round(v, 3) for v in mx - mn], bbox_center=[round(v, 3) for v in (mn + mx) / 2])
    V = np.concatenate(allV)
    mn, mx = V.min(0), V.max(0)
    return dict(roots=roots, tris=sum(p["tris"] for p in parts.values()), images=len(bpy.data.images),
                bbox_size=[round(v, 3) for v in mx - mn],
                bbox_center=[round(v, 3) for v in (mn + mx) / 2], parts=parts), V


rep = dict(note="v210b re-import of every FBX in fbx/ (Blender " + bpy.app.version_string + ", forward -Z up Y, scale 1; "
                "coordinates converted to Roblox x, y, z = Blender x, z, -y)", files={})
ok_all = True
for f in sorted(os.listdir(os.path.join(OUTD, "fbx"))):
    if not f.endswith(".fbx"):
        continue
    d, V = load(os.path.join(OUTD, "fbx", f))
    name = f[:-4]
    e = MP.get(name)
    if e:
        mparts = {q["mesh"]: q for q in e["parts"]}
        checks = dict(
            tris_lt_20k=d["tris"] < 20000,
            tris_eq_manifest=d["tris"] == e["triangles"],
            bbox_eq_manifest=bool(np.allclose(d["bbox_size"], e["bbox_size_studs"], atol=0.002) and
                                  np.allclose(d["bbox_center"], e["bbox_center_from_origin"], atol=0.002)),
            parts_eq_manifest=set(d["parts"]) == set(mparts),
            one_material_per_part=all(len(p["materials"]) == 1 for p in d["parts"].values()),
            material_colour_eq_manifest=all(p["materials"][0]["base_color"] == mparts[k]["color"]
                                            for k, p in d["parts"].items() if k in mparts),
            part_tris_eq_manifest=all(p["tris"] == mparts[k]["tris"] for k, p in d["parts"].items() if k in mparts),
            origins_at_prop_origin=all(max(abs(v) for v in p["origin"]) < 1e-4 for p in d["parts"].values()),
            single_root_named_prop=d["roots"] == [name],
        )
        d["manifest_parts"] = {k: dict(color=q["color"], roblox_material=q["roblox_material"],
                                       reflectance=q.get("reflectance")) for k, q in mparts.items()}
    else:
        m = DF.get(f"fbx/{f}")
        checks = dict(tris_lt_20k=d["tris"] < 20000,
                      tris_eq_manifest=(m is not None and d["tris"] == m["triangles"]) if m else None,
                      part_tris_eq_manifest=({k: p["tris"] for k, p in d["parts"].items()} ==
                                             {q["mesh"]: q["tris"] for q in m["parts"]}) if m else None)
    d["checks"] = checks
    d["changed_in_v210b"] = name in CHANGED
    d["new_in_v210b"] = name in NEW
    d["pass"] = all(v for v in checks.values() if v is not None)
    ok_all &= d["pass"]
    rep["files"][f] = d
    if name == "h8_door_pocket":
        # rail17 (H8 lane east rail) overlap of the placed pocket (decoration vs collision box; info only)
        h8 = [h for h in DL.load_holes() if h["number"] == 8][0]
        r17 = [w for w in h8["walls"] if w["id"] == "rail17"][0]
        r16 = [w for w in h8["walls"] if w["id"] == "rail16"][0]
        pl = e["placements"][0]
        W = V * [-1, 1, -1] + pl["pos"]                       # yaw 180
        x0 = r17["center"][0] + r17["size"][0] / 2
        zr = (r17["center"][2] - r17["size"][2] / 2, r17["center"][2] + r17["size"][2] / 2)
        inside = W[(W[:, 0] < x0) & (W[:, 2] > zr[0]) & (W[:, 2] < zr[1])]
        rep["h8_door_pocket_placed"] = dict(
            world_bbox_hole_local=[[round(v, 3) for v in W.min(0)], [round(v, 3) for v in W.max(0)]],
            rail17_inner_face_x=x0 - r17["size"][0], rail17_outer_face_x=x0,
            verts_west_of_rail17_outer_face=int(len(inside)),
            max_overlap_into_rail17=round(float(x0 - inside[:, 0].min()), 3) if len(inside) else 0.0,
            reaches_lane_felt=bool(len(inside) and inside[:, 0].min() < x0 - r17["size"][0]),
            z_range_of_overlap=[round(float(inside[:, 2].min()), 3), round(float(inside[:, 2].max()), 3)] if len(inside) else None,
            rail16=r16)
rep["all_pass"] = bool(ok_all)
rep["lip_no_glow"] = all(p["materials"][0]["emission"] == 0 for p in rep["files"]["h9_bank_lip.fbx"]["parts"].values())
rep["all_pass"] = bool(ok_all and rep["lip_no_glow"])
json.dump(rep, open(os.path.join(SRC, "reimport_v210b.json"), "w"), indent=1, default=float)
print("[reimport]", json.dumps({k: (v["tris"], v["pass"]) for k, v in rep["files"].items()}), "all_pass", ok_all,
      json.dumps(rep.get("h8_door_pocket_placed")))
