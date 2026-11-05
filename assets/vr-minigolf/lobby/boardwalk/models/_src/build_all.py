"""Build Golden Hour Boardwalk props: FBX export + per-prop manifest fragments; assemble manifest.json.

Blender (via run_blender.ps1):
  -P build_all.py -- --group structure        # one group (structure|board|arches|green|social|backdrop)
  -P build_all.py -- --only bw_bench,bw_crate
Plain python (no Blender needed):
  python -I build_all.py --assemble           # manifest.json from _src/manifest_parts/*.json + builder_Lobby.luau
"""
import sys, os, json, math, time

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
PARTS_DIR = os.path.join(SRC, "manifest_parts")
FBX_DIR = os.path.join(OUT, "fbx")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
argv = [a for x in argv for a in x.replace("=", " ").split(" ") if a]   # accepts --group=x or "--group x"


def r3(v):
    return [round(x, 3) for x in v]


# ----------------------------------------------------------------------------- Blender build
def build(names):
    import bpy
    import bwlib as L
    import registry
    registry.load_all()
    os.makedirs(PARTS_DIR, exist_ok=True)
    os.makedirs(FBX_DIR, exist_ok=True)
    results = []
    for p in registry.PROPS:
        if p["name"] not in names:
            continue
        t0 = time.time()
        name = p["name"]
        sc = L.reset_scene()
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
        pb = L.PB(name)
        post = p["fn"](pb)
        objs = pb.finalize(col)
        recenter = [0, 0, 0]
        if p["pivot"] == "base":
            off = L.recenter_base(objs)
            recenter = r3(off)
            if off.length > 1e-3:
                print(f"[note] {name}: geometry recentered by {recenter} to put the pivot at the base centre")
        extras = {}
        if callable(post):
            extras = post(objs) or {}
        mn, mx = L.bbox_blender(objs)
        size, center = L.to_roblox_bbox(mn, mx)
        tris = L.tri_count(objs)
        path = os.path.join(FBX_DIR, name + ".fbx")
        L.export_fbx(objs, path)
        parts = []
        for o in objs:
            m = o.data.materials[0]
            pmn, pmx = L.bbox_blender([o])
            psz, pc = L.to_roblox_bbox(pmn, pmx)
            parts.append(dict(mesh=o.name, material=m.name, tris=L.tri_count([o]),
                              color=m.get("bw_hex") if m.name.startswith("BW_Neon") else None,
                              roblox_material="Neon" if m.name.startswith("BW_Neon") else "SmoothPlastic",
                              size=r3(psz), center_from_pivot=r3(pc)))
        if p["collision"] is None:
            coll = [dict(center=r3(center), size=r3(size))]
        elif callable(p["collision"]):
            coll = p["collision"](size, center)
        else:
            coll = p["collision"]
        tgt = p["target"]
        e = dict(name=name, group=p["group"], fbx=f"fbx/{name}.fbx", front=p["front"], notes=p["notes"],
                 pivot=("hub axle centre (rotation axis through local origin)" if p["pivot"] == "hub"
                        else "local origin (0,0,0), shared arch base centre" if p["pivot"] == "local" else "base centre: bbox centre X/Z, min Y = 0"),
                 pivot_recenter_applied=recenter,
                 bbox_size_studs=r3(size), bbox_center_from_pivot=r3(center),
                 bbox_min_roblox=r3([mn.x, mn.z, -mx.y]), bbox_max_roblox=r3([mx.x, mx.z, -mn.y]),
                 target_size_studs=tgt,
                 size_ratio_vs_target=[round(s / t, 3) if t else None for s, t in zip(size, tgt)],
                 triangles=tris, tris_max=p["tris_max"],
                 materials=sorted({pp["material"] for pp in parts}), parts=parts,
                 collision=coll, motion=p["motion"], scalable=p["scalable"],
                 can_collide=False)
        e.update(extras)
        json.dump(e, open(os.path.join(PARTS_DIR, name + ".json"), "w"), indent=1)
        results.append((name, tris, r3(size), tgt))
        print(f"[built] {name:30s} tris={tris:6d} size={r3(size)} target={tgt} ({time.time() - t0:.1f}s)")
    return results


# ----------------------------------------------------------------------------- assemble (plain python)
def assemble():
    import parse_builder
    inst = parse_builder.parse()
    # Pass2 children use the fixed parent frame; keep builder source untouched.
    for parent in list(inst):
        a=parent['asset']
        if a in ('bw_arch_lantern_grove','bw_arch_sugarloaf_canyon','bw_arch_aurora_archipelago'):
            course=a.removeprefix('bw_arch_')
            children=[('bw_portal_surface_'+course,[0,0,0]),('bw_portal_apron',[0,0,4])]
            for fragment in sorted(os.listdir(PARTS_DIR)):
                if fragment.startswith(a+'_lantern_') and fragment.endswith('.json'):
                    moving=json.load(open(os.path.join(PARTS_DIR,fragment)))
                    children.append((moving['name'],moving['anchor_position_arch_local']))
            if course=='aurora_archipelago':children.append((a+'_snowpuff',[0,0,0]))
            for asset,offset in children:
                inst.append(dict(id=parent['id']+'__'+asset,asset=asset,position=[parent['position'][k]+offset[k] for k in range(3)],yaw=parent.get('yaw',0),parent_id=parent['id'],solid=False))
    parts = {}
    for f in sorted(os.listdir(PARTS_DIR)):
        if f.endswith(".json"):
            e = json.load(open(os.path.join(PARTS_DIR, f)))
            parts[e["name"]] = e
    counts = {}
    for i in inst:
        counts[i["asset"]] = counts.get(i["asset"], 0) + 1
    props = []
    total = 0
    missing = []
    for name, e in parts.items():
        e["builder_count"] = counts.get(name, 0)
        e["tris_x_count"] = e["triangles"] * e["builder_count"]
        total += e["tris_x_count"]
        props.append(e)
    for a in counts:
        if a not in parts:
            missing.append(a)
    instances = []
    for i in inst:
        d = dict(id=i["id"], asset=i["asset"], position=i["position"], yaw=i.get("yaw", 0.0),
                 size=i.get("size"), solid=i.get("solid"))
        if i.get('parent_id'):d['parent_id']=i['parent_id']
        e = parts.get(i["asset"])
        if e and e.get("scalable") and i.get("size") and e.get("target_size_studs"):
            sc = [round(i["size"][k] / e["target_size_studs"][k], 4) if "xyz"[k] in e["scalable"] else 1
                  for k in range(3)]
            if any(abs(v - 1) > 1e-3 for v in sc):
                d["scale"] = sc
        instances.append(d)
    order = {n: k for k, n in enumerate(json.load(open(os.path.join(SRC, "asset_order.json"))))} \
        if os.path.exists(os.path.join(SRC, "asset_order.json")) else {}
    props.sort(key=lambda e: order.get(e["name"], 999))
    man = dict(
        lobby="Golden Hour Boardwalk (SRV-137) - pass 3 richer portals and original props",
        units="studs; 1 Blender unit = 1 stud; all sizes/positions in Roblox axes (X east, Y up, Z south)",
        axes=dict(blender="Z-up; Blender +Y = Roblox -Z (north); Blender -Y = Roblox +Z (south)",
                  fbx="axis_forward -Z, axis_up Y, scale 1.0, transforms applied (identity objects)",
                  yaw="deg about +Y (CFrame.Angles(0, rad(yaw), 0)); props are built at yaw 0 in the lobby.json frame"),
        fbx_export=dict(blender="5.2.2 LTS", axis_forward="-Z", axis_up="Y", global_scale=1.0,
                        apply_scale_options="FBX_SCALE_UNITS", bake_space_transform=True, embed_textures=True,
                        path_mode="COPY", mesh_smooth_type="FACE", object_types=["MESH"]),
        materials=dict(
            BW_Atlas=dict(texture="textures/bw_atlas_1024.png", note="shared 1024x1024 atlas, all opaque parts"),
            BW_Neon=dict(color="#FFC867 (bw_arch_aurora_archipelago: #9FE6F2 crystal tips)",
                         roblox_material="Neon", note="emissive parts, own MeshPart, flat colour, no texture"),
            BW_Backdrop=dict(note="vertex colour only (bw_sea_stacks, bw_rock_arch); no texture")),
        import_notes=["Import each FBX at scale 1.0 (1 unit = 1 stud).",
                      "Anchored=true, CanCollide=false, CanQuery=false, CanTouch=false on every MeshPart; "
                      "gameplay collision = the collision[] boxes (invisible Parts) or lobby.json colliders.",
                      "BW_Neon MeshParts: Material=Neon, Color from parts[].color.",
                      "Each FBX = one mesh per material (+ named faces: card_face_1..3, panel_1..3, plate_face) "
                      "sharing the prop pivot."],
        builder_source="_src/builder_Lobby.luau (generated from lobby.json sha1 2c8ac9133299)",
        props=props,
        instances=instances,
        totals=dict(unique_meshes=len(parts), instances=len(instances), tris_total=total, tris_limit=120000,
                    tris_target=115000, missing_assets=missing),
    )
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"manifest.json: {len(parts)} props, {len(instances)} instances, total tris {total}, missing {missing}")
    return man


if __name__ == "__main__":
    if "--assemble" in argv:
        assemble()
    else:
        sys.path.insert(0, SRC)
        import registry
        names = set()
        if "--only" in argv:
            names = set(argv[argv.index("--only") + 1].split(","))
        if "--group" in argv:
            import importlib
            registry.load_all()
            gs = set(argv[argv.index("--group") + 1].split(","))
            names |= {p["name"] for p in registry.PROPS if p["group"] in gs}
        try:
            res = build(names)
            import bwlib
            bwlib.log(f"build_all {argv}: built {len(res)} props: " +
                      ", ".join(f"{n}={t}" for n, t, _, _ in res))
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
