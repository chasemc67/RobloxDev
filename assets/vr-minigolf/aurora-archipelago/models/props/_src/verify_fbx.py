"""Re-import every exported FBX into a clean scene and verify: triangles = manifest, every mesh and file < 20k,
one material per mesh, textures embedded for textured materials, Roblox-axis bbox = manifest (0.05 studs).
  blender -b --factory-startup -P out_props/_src/verify_fbx.py  -> out_props/fbx_validation.json"""
import bpy, os, json, glob, datetime
from mathutils import Vector
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
man = json.load(open(os.path.join(OUT, "manifest.json")))
want = {p["fbx"]: p for p in man["props"]}
want.update({h["file"]: h for h in man["hole_dressing_files"]})
want.update({c["file"]: c for c in man.get("collision_fbx_files", [])})      # Round 3 'clear': mover collider FBX
res = []
for path in sorted(glob.glob(os.path.join(OUT, "fbx", "*.fbx"))):
    rel = "fbx/" + os.path.basename(path)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    tris = {}
    for o in obs:
        o.data.calc_loop_triangles()
        tris[o.name] = len(o.data.loop_triangles)
    one = all(len(o.material_slots) == 1 for o in obs)
    imgs = [i for i in bpy.data.images if i.source == "FILE"]
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    size = [max(p.x for p in pts) - min(p.x for p in pts), max(p.z for p in pts) - min(p.z for p in pts), max(p.y for p in pts) - min(p.y for p in pts)]
    m = want.get(rel)
    exp_t = (m.get("triangles") if m else None)
    exp_s = (m.get("bbox_size_studs") if m else None)
    berr = max(abs(a - b) for a, b in zip(size, exp_s)) if exp_s else None
    ok = bool(m) and sum(tris.values()) == exp_t and max(tris.values()) < 20000 and sum(tris.values()) < 20000 and one and (berr is not None and berr < 0.05)
    res.append(dict(file=rel, passed=ok, meshes=len(obs), tris=sum(tris.values()), manifest_tris=exp_t, max_mesh_tris=max(tris.values()),
                    one_material_per_mesh=one, embedded_textures=len(imgs), bbox_size=[round(v, 3) for v in size], bbox_err=round(berr, 4) if berr is not None else None))
allok = all(r["passed"] for r in res)
json.dump(dict(all_passed=allok, files=res), open(os.path.join(OUT, "fbx_validation.json"), "w"), indent=1)
with open(os.path.join(os.path.dirname(OUT), "PROGRESS.md"), "a", encoding="utf8") as f:
    f.write(datetime.datetime.now().isoformat() + f" - PROPS FBX reimport validation: {sum(r['passed'] for r in res)}/{len(res)} passed (tris = manifest, <20k, one material/mesh, bbox).\n")
print("VERIFY", allok, sum(r["passed"] for r in res), len(res), [r["file"] for r in res if not r["passed"]][:20])
