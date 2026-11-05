"""Pass-1 fit check. Runs in Blender (via run_blender.ps1): re-imports every exported FBX and validates it
independently of the build step, then checks the lobby-level rules against builder_Lobby.luau instances.
Writes _src/fitcheck_pass1_validated.txt and _src/fitcheck_measure.json (used by the renders / README)."""
import bpy, os, sys, json, math, struct, time
from mathutils import Vector

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import parse_builder  # noqa: E402

if "--pass7" in sys.argv:
    from pass7_checks import run
    run(os.path.dirname(SRC),fit=True)
    sys.exit(0)

if "--pass6" in sys.argv:
    from pass6_checks import run
    run(OUT, fit=True)
    sys.exit(0)

if "--pass5" in sys.argv:
    from pass5_checks import run
    run(OUT, fit=True)
    sys.exit(0)

if "--pass4" in sys.argv:
    from pass4_checks import run
    run(OUT, fit=True)
    sys.exit(0)

if "--pass3" in sys.argv:
    from pass3_checks import run
    run(OUT, fit=True)
    sys.exit(0)

if "--pass2" in sys.argv:
    from pass2_checks import run
    run(OUT, fit=True)
    sys.exit(0)

EXPECTED = ["bw_deck_plank_a", "bw_deck_plank_b", "bw_railing", "bw_pier_piling", "bw_course_board",
            "bw_leaderboard_wall", "bw_signpost", "bw_arch_lantern_grove", "bw_arch_sugarloaf_canyon",
            "bw_arch_aurora_archipelago", "bw_arch_nameplate", "bw_coming_soon_sign", "bw_practice_green",
            "bw_windmill", "bw_windmill_blades", "bw_cup_flag", "bw_tee_mat", "bw_birdie_bites_shack", "bw_bench",
            "bw_picnic_table", "bw_barrel", "bw_crate", "bw_flower_planter", "bw_beach_umbrella", "bw_lantern_post",
            "bw_string_lights", "bw_lantern_tree_canopy", "bw_sea_stacks", "bw_rock_arch"]
STRICT_TRIS = {"bw_deck_plank_a": 100, "bw_deck_plank_b": 100, "bw_railing": 350}
FLOOR = {"bw_deck_plank_a", "bw_deck_plank_b"}
ARCHES = ["bw_arch_lantern_grove", "bw_arch_sugarloaf_canyon", "bw_arch_aurora_archipelago"]
SPAWN = (100.0, 100.0)
lines = []
fails = []


def rec(ok, label, detail=""):
    s = f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else "")
    lines.append(s)
    if not ok:
        fails.append(s)
    print(s)


def info(s):
    lines.append("       " + s)
    print("       " + s)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_fbx(path):
    clear()
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y", global_scale=1.0)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def bbox(objs):
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    for o in objs:
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
    return mn, mx


def rb_box(mn, mx):
    """Blender bbox -> Roblox min/max (x, y, z)."""
    return [mn.x, mn.z, -mx.y], [mx.x, mx.z, -mn.y]


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def png_chunks(path):
    out = []
    with open(path, "rb") as f:
        sig = f.read(8)
        while True:
            h = f.read(8)
            if len(h) < 8:
                break
            n, t = struct.unpack(">I4s", h)
            data = f.read(n)
            f.read(4)
            out.append((t.decode("latin1"), data))
            if t == b"IEND":
                break
    return sig, out


def main():
    t0 = time.time()
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    mprops = {p["name"]: p for p in man["props"]}
    inst = parse_builder.parse()
    counts = {}
    for i in inst:
        counts[i["asset"]] = counts.get(i["asset"], 0) + 1
    lines.append(f"Golden Hour Boardwalk pass 1 fitcheck  {time.strftime('%Y-%m-%d %H:%M:%S')}  (Blender {bpy.app.version_string})")
    lines.append("Every FBX re-imported (axis_forward -Z, axis_up Y, scale 1) and measured in Roblox axes.")
    lines.append("")
    # ---------------------------------------------------------------- files
    fbx_dir = os.path.join(OUT, "fbx")
    files = sorted(f[:-4] for f in os.listdir(fbx_dir) if f.endswith(".fbx"))
    rec(sorted(EXPECTED) == files, f"FBX set = the 29 builder names exactly ({len(files)} files)",
        f"missing={sorted(set(EXPECTED) - set(files))} extra={sorted(set(files) - set(EXPECTED))}")
    rec("bw_course_card_plane" not in files, "no bw_course_card_plane exported (OVERRIDE 2)")
    rec(sorted(counts) == sorted(EXPECTED), "builder_Lobby.luau assets == exported set",
        f"builder-only={sorted(set(counts) - set(files))}")
    rec(len(files) <= 40, f"unique meshes <= 40 ({len(files)})")
    # ---------------------------------------------------------------- atlas
    ap = os.path.join(OUT, "textures", "bw_atlas_1024.png")
    sig, ch = png_chunks(ap)
    ihdr = ch[0][1]
    w, h, depth, ctype = struct.unpack(">IIBB", ihdr[:10])
    meta = [t for t, _ in ch if t not in ("IHDR", "IDAT", "IEND")]
    rec(w == 1024 and h == 1024 and depth == 8 and ctype == 2 and not meta,
        "atlas textures/bw_atlas_1024.png is 1024x1024 8-bit RGB with no metadata chunks",
        f"{w}x{h} depth {depth} colortype {ctype} extra chunks {meta}")
    # ---------------------------------------------------------------- per prop
    meas = {}
    total = 0
    lines.append("")
    lines.append(f"{'prop':30s} {'count':>5s} {'tris':>6s} {'max':>6s} {'tris x n':>8s}  size (Roblox X,Y,Z) vs target")
    for name in EXPECTED:
        if name not in files:
            continue
        path = os.path.join(fbx_dir, name + ".fbx")
        objs = import_fbx(path)
        mn, mx = bbox(objs)
        rmn, rmx = rb_box(mn, mx)
        size = [b - a for a, b in zip(rmn, rmx)]
        t = sum(tris(o) for o in objs)
        mp = mprops.get(name, {})
        tgt = mp.get("target_size_studs")
        n = counts.get(name, 0)
        total += t * n
        mats = sorted({s.material.name.split(".")[0] for o in objs for s in o.material_slots if s.material})
        meas[name] = dict(min=rmn, max=rmx, size=size, tris=t, count=n, objects=[o.name for o in objs], mats=mats)
        lines.append(f"{name:30s} {n:5d} {t:6d} {mp.get('tris_max', 0):6d} {t * n:8d}  "
                     f"[{size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}] vs {tgt}")
        # size within 10 %
        if tgt:
            bad = [(ax, round(s, 3), tv) for ax, s, tv in zip("XYZ", size, tgt) if tv and abs(s - tv) > 0.10 * tv + 1e-6]
            rec(not bad, f"{name}: bbox within 10% of spec", f"off: {bad}" if bad else "")
        # tris
        per = [(o.name, tris(o)) for o in objs]
        rec(all(x < 20000 for _, x in per), f"{name}: every mesh < 20k tris", f"max {max(x for _, x in per)}")
        lim = STRICT_TRIS.get(name, mp.get("tris_max"))
        rec(t <= lim, f"{name}: tris {t} <= budget {lim}" + (" (OVERRIDE hard limit)" if name in STRICT_TRIS else ""))
        # materials
        allowed = {"BW_Backdrop"} if name in ("bw_sea_stacks", "bw_rock_arch") else {"BW_Atlas", "BW_Neon"}
        rec(set(mats) <= allowed, f"{name}: materials {mats} within {sorted(allowed)}")
        if name in ("bw_sea_stacks", "bw_rock_arch"):
            vc = all(len(o.data.color_attributes) > 0 for o in objs)
            rec(vc, f"{name}: vertex colours present (vertex colour only, no texture)")
        # pivot
        if mp.get("pivot", "").startswith("hub"):
            c = [(a + b) / 2 for a, b in zip(rmn, rmx)]
            rec(all(abs(v) < 0.05 for v in c), f"{name}: pivot at hub (bbox centred on origin)", f"centre {[round(v, 3) for v in c]}")
        else:
            cx, cz = (rmn[0] + rmx[0]) / 2, (rmn[2] + rmx[2]) / 2
            rec(abs(cx) < 0.02 and abs(cz) < 0.02 and abs(rmn[1]) < 0.02,
                f"{name}: pivot at base centre", f"centre X {cx:.3f} Z {cz:.3f} minY {rmn[1]:.3f}")
        # identity transforms (transforms applied)
        ident = all((o.matrix_world.to_translation().length < 1e-4) for o in objs)
        rec(ident, f"{name}: objects sit at the prop origin (transforms applied)")
        # prop-specific
        if name == "bw_course_board":
            cf = mp.get("cardFaces", [])
            for i, cx in enumerate((-8.0, 0.0, 8.0)):
                o = next((o for o in objs if o.name.startswith(f"card_face_{i + 1}")), None)
                if not o:
                    rec(False, f"card_face_{i + 1} exists")
                    continue
                omn, omx = bbox([o])
                a, b = rb_box(omn, omx)
                c = [(p + q) / 2 for p, q in zip(a, b)]
                sz = [q - p for p, q in zip(a, b)]
                nrm = o.matrix_world.to_3x3() @ o.data.polygons[0].normal
                nrb = (nrm.x, nrm.z, -nrm.y)
                inset = rmx[2] - c[2]
                ok = (abs(c[0] - cx) < 0.02 and abs(c[1] - 5.5) < 0.02 and abs(sz[0] - 6) < 0.02 and abs(sz[1] - 8) < 0.02
                      and nrb[2] > 0.99 and abs(inset - 0.15) < 0.02 and len(o.data.polygons) <= 2)
                mf = cf[i] if i < len(cf) else {}
                ok2 = mf and all(abs(p - q) < 0.02 for p, q in zip(mf.get("center", []), c)) and mf.get("normal") == [0, 0, 1]
                rec(bool(ok and ok2), f"course_board card_face_{i + 1}: 6x8 at X {cx:+.0f}, Y 5.5, +Z normal, inset 0.15, "
                    f"matches manifest cardFaces", f"centre {[round(v, 3) for v in c]} size {[round(v, 3) for v in sz]} "
                    f"inset {inset:.3f} tris {tris(o)}")
        if name == "bw_leaderboard_wall":
            rec(all(any(o.name.startswith(f"panel_{k}") for o in objs) for k in (1, 2, 3)),
                "leaderboard panel_1..3 faces exist")
        if name in ARCHES:
            half, height = 99.0, 99.0
            for o in objs:
                me = o.data
                pts = [o.matrix_world @ v.co for v in me.vertices]
                for e in me.edges:
                    pa, pb = pts[e.vertices[0]], pts[e.vertices[1]]
                    for k in range(1, 8):
                        pts.append(pa.lerp(pb, k / 8))
                for p in pts:
                    if p.z < 12 - 1e-3:
                        half = min(half, abs(p.x))
                    if abs(p.x) < 5 - 1e-3:
                        height = min(height, p.z)
            rec(2 * half >= 10 - 1e-3 and height >= 12 - 1e-3, f"{name}: clear opening >= 10 x 12",
                f"{2 * half:.2f} wide x {height:.2f} tall")
            meas[name]["opening"] = [2 * half, height]
        if name == "bw_windmill_blades":
            rec(bool(mp.get("motion")) and mp["motion"].get("rpm") == 6, "windmill_blades motion recorded (axis, 6 rpm)")
    # ---------------------------------------------------------------- totals
    lines.append("")
    rec(total <= 120000, f"lobby total tris (tris x builder count) {total} <= 120000", f"target ~115k; margin {120000 - total}")
    deck = sum(meas[n]["tris"] * meas[n]["count"] for n in FLOOR)
    rail = meas["bw_railing"]["tris"] * meas["bw_railing"]["count"]
    info(f"deck tiles {deck} tris (<= 15200), railing {rail} tris (<= 14700)")
    rec(deck <= 15200 and rail <= 14700, "deck/rail instance shares within OVERRIDE budget")
    # ---------------------------------------------------------------- footprints
    def corners(i):
        m = meas[i["asset"]]
        sx, _, sz = i.get("_scale", (1.0, 1.0, 1.0))
        x0, x1 = m["min"][0] * sx, m["max"][0] * sx
        z0, z1 = m["min"][2] * sz, m["max"][2] * sz
        return x0, x1, z0, z1

    def to_local(i, x, z):
        yaw = math.radians(i.get("yaw", 0.0))
        dx, dz = x - i["position"][0], z - i["position"][2]
        # inverse of x' = x cos + z sin ; z' = -x sin + z cos
        return dx * math.cos(yaw) - dz * math.sin(yaw), dx * math.sin(yaw) + dz * math.cos(yaw)

    def dist_point(i, x, z):
        lx, lz = to_local(i, x, z)
        x0, x1, z0, z1 = corners(i)
        ddx = max(x0 - lx, 0, lx - x1)
        ddz = max(z0 - lz, 0, lz - z1)
        return math.hypot(ddx, ddz)

    for i in inst:
        mp = mprops.get(i["asset"], {})
        if mp.get("scalable") and i.get("size") and mp.get("target_size_studs"):
            i["_scale"] = tuple(i["size"][k] / mp["target_size_studs"][k] if "xyz"[k] in mp["scalable"] else 1.0
                                for k in range(3))
    # spawn clear radius
    lines.append("")
    near = []
    rail_near = []
    for i in inst:
        if i["asset"] in FLOOR:
            continue
        d = dist_point(i, *SPAWN)
        if d < 10.0:
            (rail_near if i["asset"] == "bw_railing" else near).append((i["id"], round(d, 2)))
    rec(not near, "spawn (100, 0, 100) 10-stud clear radius free of instances (deck floor tiles excluded)",
        f"intruders {near}" if near else "")
    if rail_near:
        info(f"note: lobby.json puts the south deck edge (rail_south_w centre line Z=110) exactly 10 studs from spawn; "
             f"the mandatory edge railing's inner face is at {min(d for _, d in rail_near)} studs: {rail_near}. "
             f"Railings are a lobby.json comfort requirement, not placed props; flagged as a spec question.")
    # practice-green lines
    green_top = 0.4 + 0.8
    holes = [((132.0, 70.0), (158.0, 60.0), "bw_cup_flag_217"), ((140.0, 72.0), (150.0, 58.0), "bw_cup_flag_219")]
    exempt = {"bw_practice_green", "bw_windmill", "bw_windmill_blades", "bw_tee_mat"} | FLOOR
    blockers = []
    for hi, (tee, cup, own_flag) in enumerate(holes):
        for i in inst:
            if i["asset"] in exempt or i["id"] == own_flag:
                continue
            top = i["position"][1] + meas[i["asset"]]["max"][1]
            if top <= green_top:
                continue
            dmin = min(dist_point(i, tee[0] + (cup[0] - tee[0]) * k / 400, tee[1] + (cup[1] - tee[1]) * k / 400)
                       for k in range(401))
            if dmin < 0.5:
                blockers.append((hi + 1, i["id"], round(dmin, 2), round(top, 2)))
    rec(not blockers, "practice-green tee->cup lines: nothing taller than the bumper (Y 1.2) within 0.5 studs "
        "except the windmill (+blades) and each hole's own cup flag", f"{blockers}" if blockers else "")
    # windmill on line 1 (informational)
    wm = next(i for i in inst if i["asset"] == "bw_windmill")
    info(f"windmill footprint distance to hole 1 line: "
         f"{min(dist_point(wm, 132 + 26 * k / 400, 70 - 10 * k / 400) for k in range(401)):.2f} (exempt obstacle)")
    # leaderboard facing (informational)
    lb = next(i for i in inst if i["asset"] == "bw_leaderboard_wall")
    y = math.radians(lb["yaw"])
    fx, fz = math.sin(y), math.cos(y)          # local +Z front after yaw
    dirn = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(round(fx), round(fz))]
    info(f"leaderboard: panel_1..3 on local +Z; builder yaw {lb['yaw']:+.0f} turns them to face {dirn} "
         f"(lobby.json says faces east). Back carries decorative twin panels; see README spec question.")
    # ---------------------------------------------------------------- summary
    lines.append("")
    lines.append(f"RESULT: {'ALL PASS' if not fails else f'{len(fails)} FAIL'}  ({len(lines)} lines, {time.time() - t0:.0f}s)")
    open(os.path.join(SRC, "fitcheck_pass1_validated.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(dict(meas=meas, total=total), open(os.path.join(SRC, "fitcheck_measure.json"), "w"), indent=1)
    import bwlib
    bwlib.log(f"fitcheck: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}; total tris {total}")


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    open(os.path.join(SRC, "fitcheck_pass1_validated.txt"), "w").write("\n".join(lines) + "\nRESULT: CRASHED\n" +
                                                                        traceback.format_exc())
