"""Assembled-world sanity renders (Blender Workbench): heightmap terrain + every placed instance from the triangle cache.

  blender -b --factory-startup -P models/_src/sc_overview.py   -> models/previews/world_*.png
Instances are coloured by group (not by material); this is a placement check, not a beauty render.
"""
import bpy, os, sys, json, math
import numpy as np
from mathutils import Vector

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
WORLD_DIR = os.path.join(os.path.dirname(MODELS), "world")
sys.path.insert(0, SRC)
LAY = json.load(open(os.path.join(MODELS, "layout.json")))
MAN = json.load(open(os.path.join(MODELS, "manifest.json")))
W = json.load(open(os.path.join(WORLD_DIR, "world.json")))
FILES = {p["id"]: [f.split("/")[-1][:-4] for f in p["files"]] for p in MAN["pieces"]}
GROUP = {p["id"]: p["group"] for p in MAN["pieces"]}
COL = {"cliff_kit": (0.86, 0.42, 0.40), "hero": (0.85, 0.20, 0.24), "building": (0.95, 0.85, 0.30),
       "structure": (0.95, 0.85, 0.30), "lift": (0.15, 0.15, 0.2), "bridge": (0.35, 0.22, 0.12),
       "walkway": (0.35, 0.22, 0.12), "scenery": (0.2, 0.6, 0.25), "cluster": (0.2, 0.62, 0.25),
       "far_card": (0.7, 0.6, 0.8), "sky": (1.0, 0.8, 0.4)}


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    return m


def mesh_from_tris(name, T, m):
    n = len(T)
    me = bpy.data.meshes.new(name)
    v = T.reshape(-1, 3)
    vb = np.stack([v[:, 0], -v[:, 2], v[:, 1]], 1)        # Roblox -> Blender
    me.vertices.add(n * 3)
    me.vertices.foreach_set("co", vb.ravel().astype(np.float32))
    me.loops.add(n * 3)
    me.loops.foreach_set("vertex_index", np.arange(n * 3, dtype=np.int32))
    me.polygons.add(n)
    me.polygons.foreach_set("loop_start", np.arange(0, n * 3, 3, dtype=np.int32))
    me.update()
    me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def place(inst, T):
    T = T.copy()
    if "scale" in inst:
        T *= np.array(inst["scale"])[None, None, :]
    a = math.radians(inst["yaw"])
    c, s = math.cos(a), math.sin(a)
    x, z = T[..., 0].copy(), T[..., 2].copy()
    T[..., 0] = x * c + z * s + inst["pos"][0]
    T[..., 2] = -x * s + z * c + inst["pos"][2]
    T[..., 1] += inst["pos"][1]
    return T


def terrain(step=4):
    img = bpy.data.images.load(os.path.join(WORLD_DIR, "heightmap.png"))
    img.colorspace_settings.name = "Non-Color"
    wpx, hpx = img.size
    px = np.empty(wpx * hpx * 4, np.float32)
    img.pixels.foreach_get(px)
    im = px.reshape(hpx, wpx, 4)[::-1, :, 0].astype(np.float64)      # row 0 = north edge
    h = im[::step, ::step] * 260.0
    n = h.shape[0]
    xs = -640 + (np.arange(n) * step + 0.5)
    X, Z = np.meshgrid(xs, xs)
    V = np.stack([X, h, Z], -1)
    a, b, c, d = V[:-1, :-1], V[:-1, 1:], V[1:, 1:], V[1:, :-1]
    T = np.concatenate([np.stack([a, c, b], 2).reshape(-1, 3, 3), np.stack([a, d, c], 2).reshape(-1, 3, 3)])
    mesh_from_tris("terrain", T, mat("terrain", (0.78, 0.58, 0.45)))
    wl = 108.0
    wt = np.array([[[-200, wl, -540], [200, wl, -320], [200, wl, -540]], [[-200, wl, -540], [-200, wl, -320], [200, wl, -320]]])
    mesh_from_tris("reservoir", wt, mat("water", (0.25, 0.72, 0.79)))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_shadows = True
    sh.show_cavity = True
    sc.display.light_direction = (-0.6, -0.2, 0.75)
    sc.render.resolution_x, sc.render.resolution_y = 1280, 800
    w = bpy.data.worlds.new("w")
    w.color = (0.97, 0.66, 0.6)
    sc.world = w
    terrain()
    groups = {}
    for inst in LAY["instances"]:
        g = GROUP.get(inst["piece"], "scenery")
        if g in ("sky",) or inst["piece"].endswith("_card"):
            continue
        T = np.concatenate([np.load(os.path.join(SRC, "_cache", "tris", f + ".npy")) for f in FILES[inst["piece"]]])
        groups.setdefault(g, []).append(place(inst, T.astype(np.float64)))
    for g, L in groups.items():
        mesh_from_tris(g, np.concatenate(L), mat(g, COL.get(g, (0.5, 0.5, 0.5))))
    # walkway centrelines as thin ribbons
    rib = []
    for p in W["paths"]:
        for s in p["segments"]:
            if s["type"] in ("lift", "gondola"):
                continue
            A, B = np.array(s["start"]), np.array(s["end"])
            d = B - A
            L = np.hypot(d[0], d[2])
            if L < 0.1:
                continue
            nx, nz = -d[2] / L * p["width"] / 2, d[0] / L * p["width"] / 2
            o = np.array([nx, 0.15, nz])
            a1, a2, b1, b2 = A + o, A - o * [1, -1, 1], B + o, B - o * [1, -1, 1]
            rib += [[a1, b1, b2], [a1, b2, a2]]
    mesh_from_tris("walkways", np.array(rib), mat("walk", (0.98, 0.98, 0.9)))
    for h in W["holes"]:
        b = h["footprint_bbox"]
        y = h["placement"]["origin"][1] + 0.3
        x0, x1, z0, z1 = b["x"][0], b["x"][1], b["z"][0], b["z"][1]
        T = np.array([[[x0, y, z0], [x1, y, z1], [x1, y, z0]], [[x0, y, z0], [x0, y, z1], [x1, y, z1]]])
        mesh_from_tris(f"fp{h['number']}", T, mat(f"fp{h['number']}", (0.3, 0.66, 0.24)))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.clip_end = 20000
    sc.collection.objects.link(cam)
    sc.camera = cam
    views = {
        "world_overview": ((900, 1150, 900), (0, 0, 60), 50),
        "world_narrows": ((330, 120, 330 + 160), (250, 30, 260), 55),     # Roblox (x, y, z) eye, target
        "world_dam": ((60, 170, -160), (0, 80, -305), 55),
        "world_crown": ((-200, 260, 320), (-380, 190, 170), 55),
        "world_junction": ((180, 70, 600), (60, 18, 420), 55),
        "world_hoodoo": ((-200, 220, -60), (-380, 150, -200), 55),
        "world_taffy": ((470, 150, 260), (360, 70, 60), 55),
    }
    for name, (eye, tgt, fov) in views.items():
        cam.data.angle = math.radians(fov)
        cam.location = Vector((eye[0], -eye[2], eye[1]))
        t = Vector((tgt[0], -tgt[2], tgt[1]))
        cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(MODELS, "previews", name + ".png")
        bpy.ops.render.render(write_still=True)
        print("[overview]", name)


main()
