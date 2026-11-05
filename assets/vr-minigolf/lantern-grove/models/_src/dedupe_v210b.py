"""v210b: delete duplicate oak faces (oak face coplanar + overlapping + same-facing with a stone / oak face) from the
H3 / H8 near-field dressing FBX, in place. Round trip like h9dim/h9dim.py (import -> edit -> export, same settings).
blender -b --factory-startup -P dedupe_v210b.py -- <models dir> <name,name,...>
Writes _src/dedupe_v210b.json.

Found by coplanar_v210b: the lantern-pole oak posts (props_variants.pole(): lantern_span_* / lantern_string_poles)
start at z 0 like their slate footing, so the post's bottom cap lies on the footing's bottom face. The oak cap is the
duplicate: it is deleted; the slate footing keeps its face. The generator is left as is (its other FBX - every
lantern_span / string-pole prop and the H1/H2/H4-H7 dressing - are not in this job).
"""
import bpy, bmesh, sys, os, json
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, NAMES = a[0], a[1].split(",")
SRC = os.path.join(ROOT, "_src")
sys.path.insert(0, SRC)
import coplanar_v210b as CP

OAK = ("Oak", "OakDeep")
STONE = ("Limestone", "Slate", "TrimStone", "MillSlate")
EXP = dict(axis_forward="-Z", axis_up="Y", apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
           mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False, path_mode="COPY", embed_textures=True,
           use_mesh_modifiers=True, object_types={"EMPTY", "MESH"}, use_custom_props=False)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def load(path):
    clear()
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y", global_scale=1.0)
    bpy.context.view_layer.update()
    out = {}
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        V = np.stack([V[:, 0], V[:, 2], -V[:, 1]], -1)
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int).reshape(-1, 3)
        uvl = me.uv_layers.active
        # polygon keys: corner positions + UVs in loop order (raw) and rotated to a canonical start (cyclic);
        # triangles are NOT compared (Blender's import triangulation of rectangles flips on float ties)
        raw = []
        for p in me.polygons:
            c = [tuple(np.round(me.vertices[me.loops[l].vertex_index].co[:], 4)) +      # local coords (exact)
                 (tuple(np.round(uvl.data[l].uv[:], 4)) if uvl else ())
                 for l in p.loop_indices]
            raw.append(tuple(c))
        cyc = [r[r.index(min(r)):] + r[:r.index(min(r))] for r in raw]
        col = None
        if me.materials and me.materials[0] and me.materials[0].node_tree:
            bs = next((n for n in me.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            col = tuple(round(c, 5) for c in bs.inputs["Base Color"].default_value) if bs else None
        out[o.name.split(".")[0]] = dict(obj=o, T=V[idx], mw=np.round(mw, 6).tolist(), poly=[t.polygon_index for t in me.loop_triangles], key=cyc, raw=raw,
                                         col=col, mat=me.materials[0].name.split(".")[0] if me.materials else None)
    imgs = sorted(i.name for i in bpy.data.images)
    return out, imgs


rep = {}
for name in NAMES:
    path = os.path.join(ROOT, "fbx", f"{name}.fbx")
    P, imgs0 = load(path)
    mat = lambda part: part.split("__", 1)[1]
    cp = CP.count_overlaps({k: v["T"] for k, v in P.items()}, return_pairs=True)
    kill = {}                                   # part -> set of triangle indices (the oak duplicate of each pair)
    for (pa, ia), (pb, ib), _ar in cp["pair_list"]:
        ma, mb = mat(pa), mat(pb)
        if ma in OAK and (mb in STONE or mb in OAK):
            kill.setdefault(pa, set()).add(ia if not (mb in OAK and pa == pb) else max(ia, ib))
        elif mb in OAK and ma in STONE:
            kill.setdefault(pb, set()).add(ib)
    removed = {}
    for part, tris in kill.items():
        d = P[part]
        polys = sorted({d["poly"][t] for t in tris})
        # delete a polygon only if every triangle of it is a duplicate
        for pi in polys:
            assert all(t in tris for t, p in enumerate(d["poly"]) if p == pi), (part, pi)
        bm = bmesh.new()
        bm.from_mesh(d["obj"].data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in polys], context="FACES")
        bm.to_mesh(d["obj"].data)
        bm.free()
        removed[part] = dict(triangles=len(tris), polygons=len(polys))
    old = {k: dict(key=v["key"], raw=v["raw"], col=v["col"], mat=v["mat"], n=len(v["T"]), mw=v["mw"]) for k, v in P.items()}
    killed_polys = {k: sorted({P[k]["poly"][t] for t in kill.get(k, ())}) for k in P}
    if removed:
        bpy.ops.export_scene.fbx(filepath=path, **EXP)
    # verify the written file
    Q, imgs1 = load(path)
    cp2 = CP.count_overlaps({k: v["T"] for k, v in Q.items()})
    ok_parts = set(Q) == set(old)
    from collections import Counter
    same, diffs, start_kept = True, [], 0
    for k in old:
        keep = [i for i in range(len(old[k]["key"])) if i not in killed_polys[k]]
        exp = Counter(old[k]["key"][i] for i in keep)
        got = Counter(Q[k]["key"]) if k in Q else Counter()
        if got != exp or Q[k]["col"] != old[k]["col"] or Q[k]["mat"] != old[k]["mat"] or Q[k]["mw"] != old[k]["mw"]:
            same = False
            diffs.append(k)
        start_kept += sum((Counter(old[k]["raw"][i] for i in keep) & Counter(Q[k]["raw"])).values()) if k in Q else 0
    oak_after = sum(v for kk, v in cp2["by_parts"].items() if any(f"__{m}" in kk for m in OAK))
    rep[name] = dict(removed=removed, coplanar_before=cp["pairs"], coplanar_after=cp2["pairs"],
                     by_parts_before=cp["by_parts"], by_parts_after=cp2["by_parts"], oak_pairs_after=oak_after,
                     parts_same=ok_parts, every_other_polygon_position_uv_material_transform_identical=same, diffs=diffs,
                     polygons_with_same_loop_start=start_kept,
                     polygons_after=sum(len(v["key"]) for v in Q.values()),
                     removed_polygons_corners=[[list(map(list, old[k]["key"][i])) for i in killed_polys[k]]
                                               for k in killed_polys if killed_polys[k]],
                     images_before=len(imgs0), images_after=len(imgs1), images_same=imgs0 == imgs1,
                     tris_before={k: v["n"] for k, v in old.items()}, tris_after={k: len(v["T"]) for k, v in Q.items()},
                     examples=cp["examples"])
    print("[dedupe]", name, json.dumps({k: v for k, v in rep[name].items() if k not in ("examples",)}))
json.dump(rep, open(os.path.join(SRC, "dedupe_v210b.json"), "w"), indent=1)
