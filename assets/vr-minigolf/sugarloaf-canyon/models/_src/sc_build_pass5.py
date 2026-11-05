"""Pass 5 Blender build: gondola_cable + gondola_cabin -> fbx/, tri cache, eye/3-4 previews, FBX re-import check.
Reuses sc_build.py helpers (reset/export/cache_tris/mesh_info/ground/capsule/render/previews) by exec'ing it without
its main(), so sc_build.py itself and its manifest writing are untouched. Writes _src/_cache/pass5_build.json (piece
records for finalize_pass5.py) and _src/reimport_pass5.txt.

  & _src/run_blender.ps1 -Script _src/sc_build_pass5.py -Log build_pass5.log
"""
import bpy, sys, os, json, math, time
from pathlib import Path
from mathutils import Vector

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
code = (SRC / "sc_build.py").read_text(encoding="utf-8")
code = code[:code.rindex("\nmain()")]
NS = {"__file__": str(SRC / "sc_build.py"), "__name__": "sc_build_lib"}
exec(compile(code, str(SRC / "sc_build.py"), "exec"), NS)
L, FBX, PREV, MODELS = NS["L"], NS["FBX"], NS["PREV"], NS["MODELS"]
import gondola_geom as G
import sc_gondola as SG


def log(s):
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + s
    print(line, flush=True)
    with open(SRC / "PROGRESS.md", "a", encoding="utf-8") as f:
        f.write(line + "\n")


PIECES = [
    dict(id="gondola_cable", group="lift", build=SG.gondola_cable, cast_shadow_off={"Licorice"},
         notes="Sunset Gondola haul ropes: up + down line 7.6 apart (bull-wheel groove radius 3.8), 6-sided Licorice "
               "tubes r0.18, parabolic catenary spans (sag 10 bottom->tower, 2.5 tower->top) and one candy-striped "
               "portal support tower on the Crown lip (plan distance 524 from the bottom wheel). World-placed.",
         origin="bottom bull-wheel centre = line start, world (130.392, 25.6, 542.811), yaw 0; geometry baked at world offsets"),
    dict(id="gondola_cabin", group="lift", build=SG.gondola_cabin, cast_shadow_off=set(),
         notes="Seated enclosed candy-striped cabin 5.2 x 6.0 body (local X across the line x local Z along it), "
               "6.4 grip-to-floor (fits the station's 6.8 rope-to-platform opening), Window glazing band, sliding doors "
               "both sides, hanger + grip meshes suffixed _hanger. Moving part.",
         origin="cable grip point (haul-rope centreline); front local -Z = travel direction; hanger arm steps to local +X"),
]


def build_piece(p):
    sc, cam = NS["reset"]()
    col = bpy.data.collections.new(p["id"])
    sc.collection.children.link(col)
    pb = p["build"]()[0]
    root, objs = L.finalize(pb, col, pb.y0)
    path = os.path.join(FBX, p["id"] + ".fbx")
    NS["export"](root, objs, path)
    NS["cache_tris"](objs, p["id"])
    meshes = [NS["mesh_info"](o) for o in objs]
    for m in meshes:
        if m["material"] in p["cast_shadow_off"]:
            m["cast_shadow"] = False
        if m["mesh"].endswith("_hanger"):
            m["role"] = "hanger + grip"
        elif p["id"] == "gondola_cabin":
            m["role"] = "cabin body"
    mn, mx = L.bbox_blender(objs)
    size, center = L.to_roblox_bbox(mn, mx)
    rec = dict(id=p["id"], group=p["group"], notes=p["notes"], pivot=p["origin"], files=[f"fbx/{p['id']}.fbx"],
               tris=L.tri_count(objs), max_mesh_tris=max(m["tris"] for m in meshes), meshparts=len(objs),
               materials=sorted({m["material"] for m in meshes}), bbox_size=[round(v, 2) for v in size],
               bbox_center_from_origin=[round(v, 2) for v in center],
               parts=[dict(file=f"fbx/{p['id']}.fbx", role=pb.role, strata_y0=pb.y0, tris=L.tri_count(objs),
                           meshparts=len(objs), bbox_size=[round(v, 2) for v in size],
                           bbox_center_from_origin=[round(v, 2) for v in center], meshes=meshes)])
    log(f"[pass5 build] {p['id']}: tris {rec['tris']} max mesh {rec['max_mesh_tris']} meshparts {rec['meshparts']} "
        f"bbox {rec['bbox_size']} centre {rec['bbox_center_from_origin']} -> {path}")
    return sc, cam, root, objs, rec


def import_station(sc, pos, yaw, origin, fname="gondola_station"):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(FBX, fname + ".fbx"), use_anim=False)
    new = [o for o in set(bpy.data.objects) - before]
    roots = [o for o in new if o.parent is None]
    for r in roots:
        r.location = Vector((pos[0] - origin[0], -(pos[2] - origin[2]), pos[1] - origin[1]))
        r.rotation_euler = (r.rotation_euler.x, r.rotation_euler.y, math.radians(yaw))
    for o in new:
        if o.type == "MESH":
            for s in o.material_slots:
                nm = o.name.split("__")[-1].split(".")[0]
                if nm in L.MATS:
                    s.material = L.lglib.get_mat(nm)
    return new


def cable_previews(sc, cam):
    o = G.ORIGIN
    out = []
    for which in ("bottom", "top"):
        pos, yaw = G.STATIONS[which]
        import_station(sc, pos, yaw, o)
    W = lambda p: Vector((p[0] - o[0], -(p[2] - o[2]), p[1] - o[1]))
    gb = NS["ground"](sc, 18.0 - o[1] - 0.02, 1600, "FloorSand")
    # eye: canyon floor beside/behind the bottom station, 5 studs up, looking at the open end and the rising ropes;
    # the cabin FBX is shown at its boarding point (up line, grip on the rope)
    A, Tw, B = G.ropes()["up_line"]
    import_station(sc, A, G.CABIN_YAW_UP, o, "gondola_cabin")
    eye = W(G.to_world(*G.STATIONS["bottom"], (-24.0, 5.0, 16.0)))
    tgt = W(G.to_world(*G.STATIONS["bottom"], (0.0, 12.0, -30.0)))
    cap = NS["capsule"](sc, W(G.to_world(*G.STATIONS["bottom"], (-16.5, 0.0, 9.0))))
    fp = os.path.join(PREV, "gondola_cable_eye.png")
    NS["render"](sc, cam, fp, eye, tgt, 70)
    out.append(os.path.relpath(fp, MODELS))
    bpy.data.objects.remove(cap)
    bpy.data.objects.remove(gb)
    # 3/4: support tower on the Crown lip (ground at 190), capsule at the leg footing
    tc = G.tower_centre()
    gt = NS["ground"](sc, 190.0 - o[1] - 0.02, 400, "MesaTop")
    xdir = Vector((-G.UDIR[1], G.UDIR[0]))           # Roblox plan "right" of travel
    cpos = (tc[0] + xdir[0] * 13.5, 190.0, tc[2] + xdir[1] * 13.5)
    cap = NS["capsule"](sc, W(cpos))
    c = W((tc[0], 205.0, tc[2]))
    dB = Vector((G.UDIR[0], -G.UDIR[1], 0.0))       # Blender plan direction bottom -> top
    pB = Vector((dB.y, -dB.x, 0.0))
    view = (pB * 0.75 - dB * 0.65).normalized()     # quarter view from the downhill side
    d = 62.0
    loc = c + view * d * 0.9 + Vector((0, 0, d * 0.42))
    fp = os.path.join(PREV, "gondola_cable_34.png")
    NS["render"](sc, cam, fp, loc, c, 50)
    out.append(os.path.relpath(fp, MODELS))
    bpy.data.objects.remove(cap)
    bpy.data.objects.remove(gt)
    return out


def cabin_previews(sc, cam, root, objs):
    root.location.z = G.HANG                        # floor on the preview ground; FBX already exported at the grip pivot
    bpy.context.view_layer.update()
    entry = dict(id="gondola_cabin", group="lift", views=("eye", "34"), az=35.0)
    out = NS["previews"](sc, cam, entry, objs)
    root.location.z = 0.0
    return out


def reimport(recs):
    lines = [f"Pass 5 FBX re-import check ({time.strftime('%Y-%m-%d %H:%M')}, Blender {bpy.app.version_string}); "
             "clean factory scene per file, default FBX importer (forward -Z, up Y), Roblox bbox = Blender (x, z, -y)."]
    ok_all = True
    for rec in recs:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = os.path.join(MODELS, rec["files"][0])
        bpy.ops.import_scene.fbx(filepath=path, use_anim=False)
        meshes = [o for o in bpy.data.objects if o.type == "MESH"]
        roots = [o for o in bpy.data.objects if o.parent is None]
        tris = 0
        for o in meshes:
            o.data.calc_loop_triangles()
            tris += len(o.data.loop_triangles)
        mn, mx = L.bbox_blender(meshes)
        size, center = L.to_roblox_bbox(mn, mx)
        exp = {m["mesh"]: m for m in rec["parts"][0]["meshes"]}
        got = {o.name.split(".")[0]: o for o in meshes}
        names_ok = set(exp) == set(got)
        mat_ok = all(o.material_slots and o.material_slots[0].material and
                     o.material_slots[0].material.name.split(".")[0] == exp[n]["material"] for n, o in got.items() if n in exp)
        sc_ok = all(all(abs(s - 1) < 1e-4 for s in o.matrix_world.to_scale()) for o in meshes)
        tri_ok = tris == rec["tris"]
        bb_ok = all(abs(a - b) < 0.02 for a, b in zip(size, rec["bbox_size"])) and \
            all(abs(a - b) < 0.02 for a, b in zip(center, rec["bbox_center_from_origin"]))
        root_ok = len(roots) == 1 and roots[0].name.split(".")[0] == rec["id"] and roots[0].type == "EMPTY"
        packed = sorted(i.name for i in bpy.data.images if i.packed_file)
        emb = [f"{i.name}{' (packed from FBX)' if i.packed_file else ' (external path ' + i.filepath + ')'}"
               for i in bpy.data.images if i.type == "IMAGE"]
        ok = names_ok and mat_ok and sc_ok and tri_ok and bb_ok and root_ok
        ok_all &= ok
        lines += ["", f"{'PASS' if ok else 'FAIL'} {rec['files'][0]}",
                  f"  root empty: {[r.name for r in roots]} (ok {root_ok})",
                  f"  meshes: {sorted(got)} (names match manifest {names_ok})",
                  f"  materials: {[got[n].material_slots[0].material.name for n in sorted(got)]} (ok {mat_ok})",
                  f"  tris: {tris} vs built {rec['tris']} (ok {tri_ok}); per mesh "
                  + ", ".join(f"{n}={len(got[n].data.loop_triangles)}" for n in sorted(got)),
                  f"  world scale of every mesh = 1 (ok {sc_ok}); max mesh tris {max(len(o.data.loop_triangles) for o in meshes)} < 20000",
                  f"  Roblox bbox size {[round(v, 3) for v in size]} vs built {rec['bbox_size']}; centre from pivot "
                  f"{[round(v, 3) for v in center]} vs built {rec['bbox_center_from_origin']} (axes/scale ok {bb_ok})",
                  f"  images referenced/embedded: {sorted(set(emb)) or 'none (untextured palette materials only)'}"]
        log(f"[pass5 reimport] {rec['id']}: {'PASS' if ok else 'FAIL'} tris {tris} bbox {[round(v, 2) for v in size]}")
    lines += ["", f"RESULT: {'ALL PASS' if ok_all else 'FAIL'}"]
    (SRC / "reimport_pass5.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ok_all


def main():
    t0 = time.time()
    recs = []
    for p in PIECES:
        sc, cam, root, objs, rec = build_piece(p)
        if p["id"] == "gondola_cable":
            rec["previews"] = cable_previews(sc, cam)
        else:
            rec["previews"] = cabin_previews(sc, cam, root, objs)
        log(f"[pass5 build] previews {rec['previews']}")
        recs.append(rec)
    os.makedirs(SRC / "_cache", exist_ok=True)
    (SRC / "_cache" / "pass5_build.json").write_text(json.dumps(recs, indent=1), encoding="utf-8")
    ok = reimport(recs)
    log(f"[pass5 build] done in {time.time() - t0:.0f}s; reimport {'ALL PASS' if ok else 'FAIL'}")


main()
