"""Pass 6 Blender build: gondola recolour/raise, new prop + ground-dressing kit, per-hole merged dressing, reworked cliff
kit. Reuses sc_build.py helpers (reset/export/cache_tris/mesh_info/ground/capsule/render/previews) by exec'ing it
without its main(), so sc_build.py and its manifest writing are untouched. Build records are merged into
_src/_cache/pass6_build.json (keyed by piece id) for finalize_pass6.py; re-import results go to
_src/_cache/reimport_pass6_<tag>.json and are collated into _src/reimport_pass6.txt by finalize_pass6.py.

  & _src/run_blender.ps1 -Script _src/sc_build_pass6.py -ScriptArgs @('--step1') -Log build_pass6_step1.log
  & _src/run_blender.ps1 -Script _src/sc_build_pass6.py -ScriptArgs @('--only','gondola_cable,gondola_station_bottom')
  & _src/run_blender.ps1 -Script _src/sc_build_pass6.py -ScriptArgs @('--group','props') [--no-render]
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
import sc_pieces as P
import sc_pieces_pass6 as P6

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
# run_blender.ps1 may hand the args over as one joined string; split it back
argv = [a for x in argv for a in x.split()]
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
GROUPS = set(argv[argv.index("--group") + 1].split(",")) if "--group" in argv else None
RENDER = "--no-render" not in argv
STEP1 = "--step1" in argv
TAG = argv[argv.index("--tag") + 1] if "--tag" in argv else time.strftime("%H%M%S")
RECS = SRC / "_cache" / "pass6_build.json"


def log(s):
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + s
    print(line, flush=True)
    with open(SRC / "PROGRESS.md", "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ----------------------------------------------------------------------------- registry
def E(id_, group, build, notes, origin="base centre", cast_shadow_off=(), views=("eye", "34"), az=35.0, preview="std",
      fbx_name=None, world_ids=()):
    return dict(id=id_, group=group, build=build, notes=notes, origin=origin, cast_shadow_off=set(cast_shadow_off),
                views=views, az=az, preview=preview, world_ids=list(world_ids))


GONDOLA = [
    E("gondola_cable", "lift", SG.gondola_cable,
      "Sunset Gondola haul ropes: up + down line 7.6 apart (bull-wheel groove radius 3.8), 6-sided Licorice tubes r0.18, "
      "parabolic spans (sag 10 bottom->tower, 2.5 tower->top) and one portal support tower on the Crown lip (plan "
      "distance 524 from the bottom wheel). Pass 6: tower in sun-weathered timber (TimberWeathered) with dark iron "
      "fittings and brass bolt plates; only the turning sheaves keep red/cream. Bottom attach raised 7.2 (raised "
      "bottom station). World-placed.",
      origin="bottom bull-wheel centre = line start (world, see layout); yaw 0; geometry baked at world offsets",
      cast_shadow_off={"Licorice"}, preview="cable", world_ids=["lifts:Sunset Gondola"]),
    E("gondola_station_bottom", "structure", lambda: P.gondola_station(G.BOTTOM_RAISE, "gondola_station_bottom"),
      "Sunset Gondola BOTTOM station (pass 6): the gondola_station model lifted 7.2 studs onto an open timber/sandstone "
      "undercroft (deck top 8.0 above the ground, bull wheel 14.8), brass-bolted iron post caps, and a 10-riser "
      "sandstone side stair (0.8 x 1.5, 5.8 wide) on local +X from the ground at the open end up to the back of the "
      "deck. The ground boarding point (world 130, 18, 540 = station-local (2, 0, -4)) stays clear underneath.",
      origin="base centre of the station footprint (ground level), same as gondola_station",
      world_ids=["gondola_bottom_station"]),
]


def registry():
    reg = sorted(GONDOLA, key=lambda r: r["id"] != "gondola_station_bottom") + [E(**r) for r in P6.registry()]
    return {r["id"]: r for r in reg}


# ----------------------------------------------------------------------------- build
def build_piece(p):
    sc, cam = NS["reset"]()
    col = bpy.data.collections.new(p["id"])
    sc.collection.children.link(col)
    pbs = p["build"]()
    parts, all_objs, roots = [], [], []
    for pb in pbs:
        if len(pbs) == 1:
            pb.name = p["id"]
        root, objs = L.finalize(pb, col, pb.y0)
        path = os.path.join(FBX, pb.name + ".fbx")
        NS["export"](root, objs, path)
        NS["cache_tris"](objs, pb.name)
        meshes = [NS["mesh_info"](o) for o in objs]
        for m in meshes:
            if m["material"] in p["cast_shadow_off"] or p["group"] in ("far_card", "sky"):
                m["cast_shadow"] = False
            if m["mesh"].endswith("_hanger"):
                m["role"] = "hanger + grip"
        mn, mx = L.bbox_blender(objs)
        size, center = L.to_roblox_bbox(mn, mx)
        parts.append(dict(file=f"fbx/{pb.name}.fbx", role=pb.role, strata_y0=pb.y0, tris=L.tri_count(objs),
                          meshparts=len(objs), bbox_size=[round(v, 2) for v in size],
                          bbox_center_from_origin=[round(v, 2) for v in center], meshes=meshes))
        all_objs += objs
        roots.append(root)
    mn, mx = L.bbox_blender(all_objs)
    size, center = L.to_roblox_bbox(mn, mx)
    meshes = [m for pt in parts for m in pt["meshes"]]
    rec = dict(id=p["id"], group=p["group"], notes=p["notes"], pivot=p["origin"], files=[pt["file"] for pt in parts],
               tris=sum(pt["tris"] for pt in parts), max_mesh_tris=max(m["tris"] for m in meshes),
               meshparts=sum(pt["meshparts"] for pt in parts), materials=sorted({m["material"] for m in meshes}),
               bbox_size=[round(v, 2) for v in size], bbox_center_from_origin=[round(v, 2) for v in center],
               world_json_ids=p["world_ids"], parts=parts, built=time.strftime("%Y-%m-%d %H:%M"),
               blender=bpy.app.version_string)
    extra = getattr(pbs[0], "meta", None)
    if extra:
        rec["meta"] = extra
    log(f"[pass6 build] {p['id']}: tris {rec['tris']} max mesh {rec['max_mesh_tris']} meshparts {rec['meshparts']} "
        f"bbox {rec['bbox_size']} -> {rec['files']}")
    if rec["max_mesh_tris"] >= 20000:
        log(f"[pass6 build] WARNING {p['id']} has a mesh >= 20k tris")
    return sc, cam, roots, all_objs, rec


def import_fbx(fname, pos, yaw, origin):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(FBX, fname + ".fbx"), use_anim=False)
    new = [o for o in set(bpy.data.objects) - before]
    for r in [o for o in new if o.parent is None]:
        r.location = Vector((pos[0] - origin[0], -(pos[2] - origin[2]), pos[1] - origin[1]))
        r.rotation_euler = (r.rotation_euler.x, r.rotation_euler.y, math.radians(yaw))
    for o in new:
        if o.type == "MESH":
            for s in o.material_slots:
                nm = o.name.split("__")[-1].split(".")[0].split("_")[0]
                if nm in L.MATS:
                    s.material = L.lglib.get_mat(nm)
    return new


def cable_previews(sc, cam):
    o = G.ORIGIN
    out = []
    import_fbx("gondola_station_bottom", G.STATIONS["bottom"][0], G.STATIONS["bottom"][1], o)
    import_fbx("gondola_station", G.STATIONS["top"][0], G.STATIONS["top"][1], o)
    W = lambda p: Vector((p[0] - o[0], -(p[2] - o[2]), p[1] - o[1]))
    gb = NS["ground"](sc, 18.0 - o[1] - 0.02, 1600, "FloorSand")
    A = G.ropes()["up_line"][0]
    import_fbx("gondola_cabin", A, G.CABIN_YAW_UP, o)
    eye = W(G.to_world(*G.STATIONS["bottom"], (-26.0, 5.0, 22.0)))
    tgt = W(G.to_world(*G.STATIONS["bottom"], (0.0, 14.0, -30.0)))
    cap = NS["capsule"](sc, W(G.to_world(*G.STATIONS["bottom"], (2.0, 0.0, -4.0))))     # capsule ON the boarding point
    fp = os.path.join(PREV, "gondola_cable_eye.png")
    NS["render"](sc, cam, fp, eye, tgt, 70)
    out.append(os.path.relpath(fp, MODELS))
    bpy.data.objects.remove(cap)
    bpy.data.objects.remove(gb)
    tc = G.tower_centre()
    gt = NS["ground"](sc, 190.0 - o[1] - 0.02, 400, "MesaTop")
    xdir = Vector((-G.UDIR[1], G.UDIR[0]))
    cap = NS["capsule"](sc, W((tc[0] + xdir[0] * 13.5, 190.0, tc[2] + xdir[1] * 13.5)))
    c = W((tc[0], 205.0, tc[2]))
    dB = Vector((G.UDIR[0], -G.UDIR[1], 0.0))
    pB = Vector((dB.y, -dB.x, 0.0))
    view = (pB * 0.75 - dB * 0.65).normalized()
    d = 62.0
    fp = os.path.join(PREV, "gondola_cable_34.png")
    NS["render"](sc, cam, fp, c + view * d * 0.9 + Vector((0, 0, d * 0.42)), c, 50)
    out.append(os.path.relpath(fp, MODELS))
    bpy.data.objects.remove(cap)
    bpy.data.objects.remove(gt)
    return out


def previews(p, sc, cam, roots, objs):
    if not RENDER or p["preview"] == "none":
        return []
    if p["preview"] == "cable":
        return cable_previews(sc, cam)
    if p["preview"] == "world":                    # world-placed merged piece: bbox-framed overview from above
        mn, mx = L.bbox_blender(objs)
        c = (mn + mx) / 2
        ext = mx - mn
        rad = max(ext.length / 2, 4.0)
        NS["ground"](sc, mn.z - 0.3, max(800, rad * 8), "FloorSand")
        out = []
        for v, (az, el, fov) in (("eye", (200.0, 14.0, 60)), ("34", (35.0, 48.0, 45))):
            fp = os.path.join(PREV, f"{p['id']}_{v}.png")
            d = rad / math.sin(math.radians(fov) / 2) * (0.85 if v == "eye" else 1.0)
            a, e = math.radians(az), math.radians(el)
            loc = c + Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))) * d
            NS["render"](sc, cam, fp, loc, c, fov)
            out.append(os.path.relpath(fp, MODELS))
        return out
    entry = dict(id=p["id"], group=p["group"], views=p["views"], az=p["az"])
    return NS["previews"](sc, cam, entry, objs)


def reimport(recs, tag):
    res = []
    for rec in recs:
        for part in rec["parts"]:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            path = os.path.join(MODELS, part["file"])
            bpy.ops.import_scene.fbx(filepath=path, use_anim=False)
            meshes = [o for o in bpy.data.objects if o.type == "MESH"]
            roots = [o for o in bpy.data.objects if o.parent is None]
            tris = 0
            for o in meshes:
                o.data.calc_loop_triangles()
                tris += len(o.data.loop_triangles)
            mn, mx = L.bbox_blender(meshes)
            size, center = L.to_roblox_bbox(mn, mx)
            exp = {m["mesh"]: m for m in part["meshes"]}
            got = {o.name.split(".")[0]: o for o in meshes}
            names_ok = set(exp) == set(got)
            mat_ok = all(o.material_slots and o.material_slots[0].material and
                         o.material_slots[0].material.name.split(".")[0] == exp[n]["material"]
                         for n, o in got.items() if n in exp)
            sc_ok = all(all(abs(s - 1) < 1e-4 for s in o.matrix_world.to_scale()) for o in meshes)
            tri_ok = tris == part["tris"]
            bb_ok = all(abs(a - b) < 0.02 for a, b in zip(size, part["bbox_size"])) and \
                all(abs(a - b) < 0.02 for a, b in zip(center, part["bbox_center_from_origin"]))
            stem = Path(part["file"]).stem
            root_ok = len(roots) == 1 and roots[0].name.split(".")[0] == stem and roots[0].type == "EMPTY"
            imgs = sorted({f"{i.name}{' (packed)' if i.packed_file else ' (external ' + i.filepath + ')'}"
                           for i in bpy.data.images if i.type == "IMAGE"})
            mx_mesh = max(len(o.data.loop_triangles) for o in meshes)
            ok = names_ok and mat_ok and sc_ok and tri_ok and bb_ok and root_ok and mx_mesh < 20000
            res.append(dict(file=part["file"], ok=ok, root=[r.name for r in roots], root_ok=root_ok,
                            meshes=sorted(got), names_ok=names_ok, mat_ok=mat_ok, tris=tris, built_tris=part["tris"],
                            tri_ok=tri_ok, scale_ok=sc_ok, max_mesh_tris=mx_mesh, bbox=[round(v, 3) for v in size],
                            built_bbox=part["bbox_size"], centre=[round(v, 3) for v in center],
                            built_centre=part["bbox_center_from_origin"], bbox_ok=bb_ok, images=imgs))
            log(f"[pass6 reimport] {part['file']}: {'PASS' if ok else 'FAIL'} tris {tris} bbox {[round(v, 2) for v in size]}")
    (SRC / "_cache" / f"reimport_pass6_{tag}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return all(r["ok"] for r in res)


def save_recs(recs):
    old = json.loads(RECS.read_text()) if RECS.exists() else {}
    for r in recs:
        old[r["id"]] = r
    RECS.write_text(json.dumps(old, indent=1), encoding="utf-8")


def step1():
    """Gondola tower recolour on the UNCHANGED pass-5 line (bottom raise 0): export, re-import and compare tris/bbox with
    the pass-5 manifest record. Writes _cache/pass6_step1.json; the FBX is overwritten again by the step-1b build."""
    G.set_bottom_raise(0.0)
    p = registry()["gondola_cable"]
    sc, cam, roots, objs, rec = build_piece(p)
    ref = json.loads((SRC / "backup_pass6" / "manifest.json").read_text())
    ref = next(x for x in ref["pieces"] if x["id"] == "gondola_cable")
    reimport([rec], "step1")
    rr = json.loads((SRC / "_cache" / "reimport_pass6_step1.json").read_text())[0]
    same = (rec["tris"] == ref["tris"] and rec["bbox_size"] == ref["bbox_size"]
            and rec["bbox_center_from_origin"] == ref["bbox_center_from_origin"] and rr["ok"])
    out = dict(pass5=dict(tris=ref["tris"], bbox=ref["bbox_size"], centre=ref["bbox_center_from_origin"],
                          meshes={m["mesh"]: m["tris"] for m in ref["parts"][0]["meshes"]}),
               pass6_recolour=dict(tris=rec["tris"], bbox=rec["bbox_size"], centre=rec["bbox_center_from_origin"],
                                   meshes={m["mesh"]: m["tris"] for m in rec["parts"][0]["meshes"]},
                                   reimport_tris=rr["tris"], reimport_bbox=rr["bbox"], reimport_ok=rr["ok"]),
               identical_geometry=same)
    (SRC / "_cache" / "pass6_step1.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    log(f"[pass6 step1] gondola_cable recolour at the pass-5 line: tris {rec['tris']} vs {ref['tris']}, bbox "
        f"{rec['bbox_size']} vs {ref['bbox_size']}, centre {rec['bbox_center_from_origin']} vs "
        f"{ref['bbox_center_from_origin']} -> {'IDENTICAL' if same else 'DIFFERENT'}")


def main():
    t0 = time.time()
    if STEP1:
        step1()
        return
    reg = registry()
    sel = [r for r in reg.values() if (not ONLY or r["id"] in ONLY) and (not GROUPS or r["group"] in GROUPS)]
    log(f"[pass6 build] {len(sel)} pieces: {[r['id'] for r in sel][:40]}{' ...' if len(sel) > 40 else ''}")
    recs = []
    for p in sel:
        sc, cam, roots, objs, rec = build_piece(p)
        rec["previews"] = previews(p, sc, cam, roots, objs)
        recs.append(rec)
        save_recs([rec])
    ok = reimport(recs, TAG)
    log(f"[pass6 build] done {len(recs)} pieces in {time.time() - t0:.0f}s; reimport {'ALL PASS' if ok else 'FAIL'} "
        f"(_cache/reimport_pass6_{TAG}.json)")


main()
