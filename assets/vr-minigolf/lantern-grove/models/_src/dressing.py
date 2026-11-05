"""Per-hole set-dressing layouts (pass 2).

  blender -b --factory-startup -P models/_src/dressing.py [-- --holes 1,3]

For every hole: places autumn trees, bushes, toadstools, ferns, leaf piles and lanterns around (never on) the
course, using the keep-out volumes in dressing_lib.py (felt, rails, hazards, moving-part sweeps, teleports, hero
props, walking paths, all from holes.json + manifest placements). Deterministic (seeded per hole).
Writes:
  manifest.json > dressing.holes.HN.instances  [{prop, pos (hole-local, origin), yaw, scale, role}]
  manifest.json > dressing.holes.HN.lights     glow-core centres (hole-local) for PointLights
  fbx/dressing_hNN_<a,b,..>.fbx                the same instances merged per material (<20k tris per file)
"""
import bpy, bmesh, sys, os, json, math, random, importlib
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import lglib, registry, dressing_lib as DL
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6", "props_pass7", "props_pass8"):
    importlib.import_module(m)
REG = {p["name"]: p for p in registry.PROPS}

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY_HOLES = [int(x) for x in argv[argv.index("--holes") + 1].split(",")] if "--holes" in argv else None
TRI_BUDGET = 19000
DEBUG = set(argv[argv.index("--debug") + 1].split(",")) if "--debug" in argv else set()

# ----------------------------------------------------------------------------- pools (prop: weight)
TREES = {
    "forest": {"maple_tree_round": 3, "red_maple_tree": 2, "maple_tree_tall": 2, "golden_birch_tree": 2,
               "oak_tree_orange": 1, "maple_tree_lanterns": 2},
    "village": {"maple_tree_round": 3, "red_maple_tree": 2, "maple_tree_tall": 2, "oak_tree_orange": 1,
                "maple_tree_lanterns": 2, "golden_birch_tree": 1},
    "stream": {"oak_tree_orange": 3, "maple_tree_round": 2, "golden_birch_tree": 2, "maple_tree_tall": 2,
               "maple_tree_lanterns": 1, "red_maple_tree": 1},
    "hollow": {"oak_tree_orange": 3, "maple_tree_lanterns": 2, "maple_tree_round": 2, "maple_tree_tall": 1,
               "golden_birch_tree": 1},
}
NEAR = {"leaf_pile": 2, "leaf_pile_wide": 1, "leaf_scatter": 1, "toadstool_trio_small": 2, "grass_tuft": 3,
        "fern_clump": 2, "red_leaf_bush": 4, "gold_leaf_bush": 3, "orange_leaf_bush": 3, "toadstool_cluster": 1}
MID = {"orange_leaf_bush": 3, "red_bush_tall": 2, "toadstool_tall": 1, "toadstool_orange_cluster": 1,
       "fern_clump_large": 2, "mossy_boulder": 1, "maple_sapling": 2, "red_leaf_bush": 1, "toadstool_cluster": 1}
THEME_EXTRA = {
    "forest": dict(near={}, mid={"golden_birch_tree": 0}, far=[]),
    "village": dict(near={"toadstool_cluster": 2, "toadstool_trio_small": 2},
                    mid={"toadstool_tall": 3, "toadstool_orange_cluster": 2}, far=[("mushroom_house_medium", 2)]),
    "stream": dict(near={"fern_clump": 2, "grass_tuft": 2}, mid={"mossy_boulder": 3, "fern_clump_large": 2},
                   far=[("rock_outcrop", 4)]),
    "hollow": dict(near={"glowing_mushrooms": 3, "fern_clump": 2}, mid={"glowing_mushrooms": 2, "toadstool_tall": 1},
                   far=[("rock_outcrop", 1)]),
}
THEME = {1: "forest", 2: "forest", 3: "village", 4: "village", 5: "stream", 6: "stream", 7: "stream", 8: "hollow",
         9: "hollow"}
CAPS = dict(tree=34, mid=80, near=100, span=3, string=2, hook=6, far=4, backdrop=34)
ROLE_ORDER = ["tree", "backdrop", "far", "span", "string", "hook", "mid", "near"]


# ----------------------------------------------------------------------------- templates
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
TCOL = bpy.data.collections.new("_dress_templates")
sc.collection.children.link(TCOL)
TPL = {}


def template(name):
    if name in TPL:
        return TPL[name]
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(TCOL, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
        lglib.box_uv_objects(objs)
    vb = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in objs])
    v = np.stack([vb[:, 0], vb[:, 2], -vb[:, 1]], 1)  # Blender -> Roblox
    rad = np.hypot(v[:, 0], v[:, 2])
    low = v[:, 1] < 1.0
    base_r = float(rad[low].max()) if low.any() else 0.5
    hi = v[:, 1] > 5.0
    crown_r = float(rad[hi].max()) if ("tree" in name or "sapling" in name) and hi.any() else 0.0
    bases = [(0.0, 0.0, min(base_r, 2.2 if crown_r else base_r))]
    if name.startswith("lantern_span_") or name == "lantern_string_poles":
        hx = float(np.abs(v[:, 0]).max()) - 0.3
        bases = [(-hx, 0.0, 0.5), (hx, 0.0, 0.5)]
    if name == "lantern_hook_pair":
        bases = [(0.0, 0.0, 0.5)]
    # glow cores -> light positions
    lights = []
    for o in objs:
        if lglib.mat_of(o.name) not in ("Glow",):
            continue
        b = bmesh.new()
        b.from_mesh(o.data)
        seen = set()
        for vert in b.verts:
            if vert.index in seen:
                continue
            stack, isl = [vert], []
            seen.add(vert.index)
            while stack:
                q = stack.pop()
                isl.append(q.co.copy())
                for e in q.link_edges:
                    w = e.other_vert(q)
                    if w.index not in seen:
                        seen.add(w.index)
                        stack.append(w)
            c = sum(isl, Vector()) / len(isl)
            lights.append((c.x, c.z, -c.y))
        b.free()
    TPL[name] = dict(name=name, objs=objs, v=v, height=float(v[:, 1].max()), base_r=base_r, crown_r=crown_r,
                     bases=bases, tris=lglib.tri_count(objs), lights=lights)
    return TPL[name]


# ----------------------------------------------------------------------------- layout
holes = DL.load_holes()
man_path = os.path.join(OUT, "manifest.json")
manifest = json.load(open(man_path))
VOLS, TREE_VOLS = DL.build_keepouts(holes, manifest["props"])
PLACED = []   # world: dict(bases=[(x,z,r)], crown=(x,z,r) or None)


def wchoice(rnd, pool):
    items = [(k, w) for k, w in pool.items() if w > 0]
    t = rnd.uniform(0, sum(w for _, w in items))
    for k, w in items:
        t -= w
        if t <= 0:
            return k
    return items[-1][0]


class HoleLayout:
    def __init__(self, h):
        self.h = h
        self.n = h["number"]
        self.rnd = random.Random(1000 + self.n)
        self.G = DL.Ground(h, margin=84.0)
        self.inst = []
        self.count = {k: 0 for k in CAPS}
        self.reject = {}
        tee = np.array(h["tee"]["position"], float)
        self.tee = tee
        self.aim = np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
        self.right = np.array([-self.aim[2], 0, self.aim[0]])
        th = THEME[self.n]
        self.trees = TREES[th]
        self.near = dict(NEAR, **THEME_EXTRA[th]["near"])
        self.mid = dict(MID, **THEME_EXTRA[th]["mid"])
        self.far = THEME_EXTRA[th]["far"]

    def dist(self, x, z):
        return float(DL.felt_distance(self.h, np.array([x]), np.array([z]))[0])

    def in_view(self, x, z):
        d = np.array([x, 0, z]) - (self.tee - self.aim * 1.0)
        L = np.linalg.norm(d)
        return L > 1 and (d @ self.aim) / L > math.cos(math.radians(42))

    def try_place(self, name, x, z, yaw, s, role):
        if self.count[role] >= CAPS[role]:
            return False
        T = template(name)
        y = self.G.y(x, z) - (0.1 if T["crown_r"] else 0.04)
        Rm = DL.yaw_mat(yaw)
        bases_w = []
        for (bx, bz, br) in T["bases"]:
            pw = DL.to_world(self.h, np.array([x, 0, z]) + Rm @ np.array([bx * s, 0, bz * s]))
            bases_w.append((pw[0], pw[2], br * s))
        cw = DL.to_world(self.h, [x, 0, z])
        crown = (cw[0], cw[2], T["crown_r"] * s) if T["crown_r"] else None
        small = T["height"] * s < 3.6
        for q in PLACED:
            k = 0.55 if (small and q.get("small")) else 0.62 if (small or q.get("small")) else 1.0
            for (ax, az, ar) in bases_w:
                for (bx, bz, br) in q["bases"]:
                    if math.hypot(ax - bx, az - bz) < (ar + br) * k + 0.2:
                        self.reject["_overlap_" + role] = self.reject.get("_overlap_" + role, 0) + 1
                        return False
            if crown and q["crown"]:
                if math.hypot(crown[0] - q["crown"][0], crown[1] - q["crown"][1]) < 0.62 * (crown[2] + q["crown"][2]):
                    return False
        P = DL.transform_verts(T["v"], (x, y, z), yaw, s, self.h)
        bad = DL.violations(P, VOLS, TREE_VOLS, prop_height=T["height"] * s, first_only=not DEBUG)
        if DEBUG and role in DEBUG:
            print("[dbg]", self.n, name, round(x, 1), round(z, 1), bad)
        if bad:
            k = next(iter(bad)).split(":")[1] if ":" in next(iter(bad)) else next(iter(bad))
            self.reject[k] = self.reject.get(k, 0) + 1
            return False
        PLACED.append(dict(bases=bases_w, crown=crown, small=small))
        self.inst.append(dict(prop=name, pos=[round(x, 3), round(y, 3), round(z, 3)], yaw=round(yaw, 1),
                              scale=round(s, 3), role=role))
        self.count[role] += 1
        return True

    # --- passes
    def frame_trees(self):
        names = list(self.trees)
        k = 0
        for t in (1.5, 7.0, 13.5, 20.0, 27.0, 35.0, 44.0):
            for side in (-1, 1):
                ok = False
                for u in np.arange(4.0, 30.0, 1.25):
                    p = self.tee + self.aim * t + self.right * side * u
                    if self.dist(p[0], p[2]) < 2.0:
                        continue
                    for attempt in range(3):
                        if attempt == 0 and t < 30:
                            # leaning maple, local +X pointing back toward the lane centre line
                            dvec = -self.right * side
                            nm, yaw = "maple_tree_overhang", math.degrees(math.atan2(-dvec[2], dvec[0])) + self.rnd.uniform(-15, 15)
                        else:
                            nm = wchoice(self.rnd, self.trees) if k % 3 else names[(k // 3) % len(names)]
                            yaw = self.rnd.uniform(0, 360)
                        if self.try_place(nm, p[0], p[2], yaw, self.rnd.uniform(0.95, 1.15), "tree"):
                            ok = True
                            k += 1
                            break
                    if ok:
                        break

    def spans(self):
        felt = sorted(self.h["felt"], key=lambda f: -max(f["size"]))
        done = []
        for f in felt:
            if f.get("overlay") or f.get("kind") in ("bank",):
                continue
            sx, sz = f["size"]
            across, along = (sx, sz) if sz >= sx else (sz, sx)
            yaw = f.get("yaw", 0.0) + (0 if sz >= sx else 90)
            if along < 6:
                continue
            Rf = DL.yaw_mat(f.get("yaw", 0.0))
            axis = Rf @ (np.array([0, 0, 1.0]) if sz >= sx else np.array([1.0, 0, 0]))
            c = np.array(f["center"], float)
            for off in np.arange(-along / 2 + 3, along / 2 - 2, 4.0):
                p = c + axis * off
                if any(np.linalg.norm(p - q) < 10 for q in done):
                    continue
                for w in (12, 16, 20):
                    if w / 2 < across / 2 + DL.FELT_MARGIN + 0.4:
                        continue
                    if self.try_place(f"lantern_span_{w}", p[0], p[2], yaw, 1.0, "span"):
                        done.append(p)
                        break

    def edge_points(self, step, off_lo, off_hi, normals=False):
        pts = []
        for f in self.h["felt"]:
            if f.get("overlay"):
                continue
            Rf = DL.yaw_mat(f.get("yaw", 0.0))
            c = np.array(f["center"], float)
            hx, hz = f["size"][0] / 2, f["size"][1] / 2
            for (n, t, L, e) in (((1, 0), (0, 1), hz, hx), ((-1, 0), (0, 1), hz, hx), ((0, 1), (1, 0), hx, hz),
                                 ((0, -1), (1, 0), hx, hz)):
                nv = Rf @ np.array([n[0], 0, n[1]], float)
                tv = Rf @ np.array([t[0], 0, t[1]], float)
                for a in np.arange(-L + step / 2, L, step):
                    o = self.rnd.uniform(off_lo, off_hi)
                    p = c + nv * (e + o) + tv * (a + self.rnd.uniform(-0.6, 0.6))
                    if self.dist(p[0], p[2]) >= o - 0.3:
                        yaw_edge = math.degrees(math.atan2(tv[0], tv[2])) - 90  # local +X along the edge
                        pts.append((p, nv if normals else yaw_edge))
        self.rnd.shuffle(pts)
        return pts

    def hooks_and_strings(self):
        for p, ye in self.edge_points(10.0, 2.0, 2.6):
            if self.count["hook"] >= CAPS["hook"]:
                break
            if self.in_view(p[0], p[2]) or self.rnd.random() < 0.4:
                self.try_place("lantern_hook_pair", p[0], p[2], ye, 1.0, "hook")
        for p, ye in self.edge_points(12.0, 2.6, 3.2):
            if self.count["string"] >= CAPS["string"]:
                break
            self.try_place("lantern_string_poles", p[0], p[2], ye, 1.0, "string")

    def near_pass(self):
        """Rail-side ground cover: each prop sits just outside the felt margin, by its own footprint radius."""
        pts = self.edge_points(1.8, 0.0, 0.0, normals=True) + self.edge_points(2.6, 0.0, 0.0, normals=True)
        if DEBUG:
            print("[dbg] near edge points", len(pts))
        for p, nv in pts:
            if self.rnd.random() < 0.12:
                continue
            for _ in range(3):
                nm = wchoice(self.rnd, self.near)
                s = self.rnd.uniform(0.85, 1.15)
                o = DL.FELT_MARGIN + template(nm)["base_r"] * s + self.rnd.uniform(0.05, 1.6)
                q = p + nv * o
                if self.dist(q[0], q[2]) < o - 0.3:
                    continue
                if self.try_place(nm, q[0], q[2], self.rnd.uniform(0, 360), s, "near"):
                    break

    def ring_points(self, dlo, dhi, n):
        G = self.G
        xs = G.X[0]
        zs = G.Z[:, 0]
        out = []
        tries = 0
        while len(out) < n and tries < n * 40:
            tries += 1
            x = self.rnd.uniform(xs[0] + 4, xs[-1] - 4)
            z = self.rnd.uniform(zs[0] + 4, zs[-1] - 4)
            d = self.dist(x, z)
            if dlo <= d <= dhi:
                out.append((x, z, self.in_view(x, z), d))
        # favour what the tee camera sees, and nearer rings
        out.sort(key=lambda q: -self.rnd.random() * (4.0 if q[2] else 1.0) / (1.0 + (q[3] - dlo) / 12.0))
        return [q[:3] for q in out]

    def mid_pass(self):
        for x, z, _ in self.ring_points(2.6, 12.0, 600):
            if self.count["mid"] >= CAPS["mid"]:
                break
            self.try_place(wchoice(self.rnd, self.mid), x, z, self.rnd.uniform(0, 360), self.rnd.uniform(0.85, 1.25), "mid")

    def far_pass(self):
        total = 0
        for nm, cap in self.far:
            k = 0
            self.count["far"] = 0   # CAPS["far"] is a per-prop cap here
            for x, z, _ in self.ring_points(9.0, 30.0, 120):
                if k >= cap:
                    break
                if self.try_place(nm, x, z, self.rnd.uniform(0, 360), self.rnd.uniform(0.8, 1.3), "far"):
                    k += 1
            total += k
        self.count["far"] = total
        for x, z, _ in self.ring_points(4.5, 24.0, 900):
            if self.count["tree"] >= CAPS["tree"]:
                break
            self.try_place(wchoice(self.rnd, self.trees), x, z, self.rnd.uniform(0, 360), self.rnd.uniform(0.85, 1.25), "tree")

    def dist_all(self, x, z):
        """Distance to the nearest felt of ANY hole (world space)."""
        pw = DL.to_world(self.h, [x, 0, z])
        best = 1e9
        for h2 in holes:
            Rw, off = DL.hole_xf(h2)
            pl = (pw - off) @ Rw
            best = min(best, float(DL.felt_distance(h2, np.array([pl[0]]), np.array([pl[2]]))[0]))
        return best

    def backdrop_pass(self):
        """Far forest wall: cheap tree clumps 20..75 studs out (from every hole) so no tee view ends in bare ground."""
        for x, z, _ in self.ring_points(20.0, 75.0, 1200):
            if self.count["backdrop"] >= CAPS["backdrop"]:
                break
            if self.dist_all(x, z) < 18.0:
                continue
            self.try_place("tree_backdrop_cluster", x, z, self.rnd.uniform(0, 360), self.rnd.uniform(1.0, 1.5), "backdrop")

    def run(self):
        """Phase A (course-side dressing). The backdrop ring runs later, for all holes, in main()."""
        self.frame_trees()
        self.spans()
        self.hooks_and_strings()
        self.near_pass()
        self.far_pass()
        self.mid_pass()
        return self


# ----------------------------------------------------------------------------- FBX groups
def inst_matrix_bl(it):
    x, y, z = it["pos"]
    s = it["scale"]
    return Matrix.Translation(lglib.R(x, y, z)) @ Matrix.Rotation(math.radians(it["yaw"]), 4, "Z") @ Matrix.Diagonal((s, s, s, 1))


def export_group(name, insts):
    col = bpy.data.collections.new(name)
    sc.collection.children.link(col)
    acc = {}
    scratch = bpy.data.meshes.new("_scr")
    for it in insts:
        T = template(it["prop"])
        Mx = inst_matrix_bl(it)
        for o in T["objs"]:
            m = lglib.mat_of(o.name)
            tb = bmesh.new()
            tb.from_mesh(o.data)
            bmesh.ops.transform(tb, matrix=Mx, verts=tb.verts)
            tb.to_mesh(scratch)
            tb.free()
            acc.setdefault(m, bmesh.new()).from_mesh(scratch)
    root = bpy.data.objects.new(name, None)
    col.objects.link(root)
    objs = []
    for m, b in sorted(acc.items()):
        me = bpy.data.meshes.new(f"{name}__{m}")
        b.to_mesh(me)
        b.free()
        me.materials.append(lglib.get_mat(m))
        ob = bpy.data.objects.new(f"{name}__{m}", me)
        col.objects.link(ob)
        ob.parent = root
        objs.append(ob)
    for c in sc.collection.children:
        sc.view_layers[0].layer_collection.children[c.name].exclude = (c.name != name)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [root] + objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, "fbx", f"{name}.fbx"), use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
        global_scale=1.0, axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"EMPTY", "MESH"},
        use_custom_props=False)
    tris = lglib.tri_count(objs)
    parts = [dict(mesh=o.name, material=lglib.mat_of(o.name), tris=lglib.tri_count([o])) for o in objs]
    for o in objs:
        bpy.data.meshes.remove(o.data)
    bpy.data.objects.remove(root)
    bpy.data.collections.remove(col)
    return tris, parts


def main():
    old = manifest.get("dressing", {}).get("holes", {})
    out = {}
    for h in holes:
        H = f"H{h['number']}"
        if ONLY_HOLES and h["number"] not in ONLY_HOLES:
            if H in old:
                out[H] = old[H]
                # keep their footprints so the rerun holes respect them
                for it in old[H]["instances"]:
                    T = template(it["prop"])
                    cw = DL.to_world(h, [it["pos"][0], 0, it["pos"][2]])
                    PLACED.append(dict(bases=[(cw[0], cw[2], T["bases"][0][2] * it["scale"])],
                                       crown=(cw[0], cw[2], T["crown_r"] * it["scale"]) if T["crown_r"] else None,
                                       small=T["height"] * it["scale"] < 3.6))
            continue
    layouts = [HoleLayout(h).run() for h in holes if not (ONLY_HOLES and h["number"] not in ONLY_HOLES)]
    for L in layouts:
        L.backdrop_pass()
    for L in layouts:
        h = L.h
        H = f"H{h['number']}"
        insts = sorted(L.inst, key=lambda it: (ROLE_ORDER.index(it["role"]), it["prop"]))
        # remove stale group files for this hole
        for fn in os.listdir(os.path.join(OUT, "fbx")):
            if fn.startswith(f"dressing_h{h['number']:02d}"):
                os.remove(os.path.join(OUT, "fbx", fn))
        groups, cur, ct = [], [], 0
        for it in insts:
            t = template(it["prop"])["tris"]
            if cur and ct + t > TRI_BUDGET:
                groups.append(cur)
                cur, ct = [], 0
            cur.append(it)
            ct += t
        if cur:
            groups.append(cur)
        files = []
        for gi, g in enumerate(groups):
            nm = f"dressing_h{h['number']:02d}_{'abcdefghijklmnop'[gi]}"
            tris, parts = export_group(nm, g)
            files.append(dict(fbx=f"fbx/{nm}.fbx", triangles=tris, instances=len(g), parts=parts))
            print(f"[dressing] {nm}: {len(g)} instances, {tris} tris")
        lights = []
        for it in insts:
            T = template(it["prop"])
            for c in T["lights"]:
                p = DL.transform_verts(np.array([c]), it["pos"], it["yaw"], it["scale"])[0]
                lights.append([round(float(v), 2) for v in p])
        out[H] = dict(theme=THEME[h["number"]], counts={k: v for k, v in L.count.items() if v},
                      triangles=sum(f["triangles"] for f in files), instances=insts, fbx=files, lights=lights,
                      rejected_by=L.reject)
        print(f"[dressing] {H}: {len(insts)} instances {L.count} rejects {L.reject}")
    manifest["dressing"] = dict(
        note=("Hole-local set dressing. Preferred import: one Model per instance from fbx/<prop>.fbx, "
              "Model:PivotTo(holeCF * CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0)) then Model:ScaleTo(scale). "
              "pos.y was sampled from a preview ground (nearest felt top - 0.6, water - 0.5); in Studio raycast down "
              "onto your Terrain from pos + (0, 20, 0) and use hit.Y instead. Alternative: fbx[] files are the same "
              "instances pre-merged per material (origin = hole origin, place at holeCF). lights[] = glow-core centres "
              "(hole-local) for PointLights (Range 8, Brightness 0.6 day / 1.6 night, #FFB347)."),
        rules=dict(clear_above_felt=DL.CLEAR, felt_margin=DL.FELT_MARGIN, wall_margin=DL.WALL_MARGIN,
                   checked_by="_src/fitcheck.py (dressing section)", keepouts=DL.__doc__.split("A dressing vertex")[1].strip()),
        holes={k: out[k] for k in sorted(out, key=lambda s: int(s[1:]))},
    )
    uses = {}
    for d in out.values():
        for it in d["instances"]:
            uses[it["prop"]] = uses.get(it["prop"], 0) + 1
    manifest["dressing"]["prop_use_counts"] = dict(sorted(uses.items(), key=lambda kv: -kv[1]))
    for p in manifest["props"]:
        p["dressing_uses"] = uses.get(p["name"], 0)
    json.dump(manifest, open(man_path, "w"), indent=1)


main()
