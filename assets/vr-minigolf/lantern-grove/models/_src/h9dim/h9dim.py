# Blender 5.2 headless: make *_h9dim FBX variants with Neon glow materials dimmed 30%, + before/after preview.
import bpy, sys, os, json, math
from mathutils import Vector
ROOT = sys.argv[sys.argv.index("--")+1]          # models dir (has fbx/)
F = 0.7
PROPS = ["tee_sign_h09","cup_lantern_stake","h9_lantern_pendulum","hollow_tree","heart_lantern_cluster",
         "trunk_tunnel_arch","lantern_knot","heart_well_rim","lantern_string","glowing_mushrooms",
         "h9_pendulum_root_beam","h9_tunnel_dip_trim","lantern_large_hanging","dressing_h09_a"]
GLOW = {"Glow":("#FFB347",4.0),"Firefly":("#D8FF6A",8.0),"ShroomGlow":("#7FE3D0",6.0)}
SELF = {"Paper":("#F7C873",0.6),"PaperOrange":("#F08A3C",0.6)}
def s2l(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def hexrgb(h,k=1.0): return [s2l(int(h[i:i+2],16)/255*k) for i in (1,3,5)]
def hexdim(h): return "#%02X%02X%02X"%tuple(round(int(h[i:i+2],16)*F) for i in (1,3,5))
EXP = dict(axis_forward='-Z', axis_up='Y', apply_scale_options='FBX_SCALE_UNITS', global_scale=1.0,
           mesh_smooth_type='FACE', add_leaf_bones=False, bake_anim=False, path_mode='COPY', embed_textures=True)
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def basemat(m): return m.name.split(".")[0]
def setmat(m, dim, preview):
    b = basemat(m)
    if not m.use_nodes: m.use_nodes = True
    p = next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'), None)
    if p is None: return
    if b in GLOW:
        h,e = GLOW[b]; k = F if dim else 1.0
        p.inputs["Base Color"].default_value = (*hexrgb(h,k),1)
        if preview:
            p.inputs["Emission Color"].default_value = (*hexrgb(h,k),1)
            p.inputs["Emission Strength"].default_value = e*k
        else:
            p.inputs["Emission Color"].default_value = (*hexrgb(h,k),1)
            p.inputs["Emission Strength"].default_value = e*k
    elif b in SELF and preview:
        h,e = SELF[b]
        p.inputs["Emission Color"].default_value = (*hexrgb(h),1); p.inputs["Emission Strength"].default_value = e
report = {}
os.makedirs(os.path.join(ROOT,"fbx"),exist_ok=True)
for name in PROPS:
    src = os.path.join(ROOT,"fbx",name+".fbx"); dst = os.path.join(ROOT,"fbx",name+"_h9dim.fbx")
    clear(); bpy.ops.import_scene.fbx(filepath=src, axis_forward='-Z', axis_up='Y', global_scale=1.0)
    bb0 = [tuple(round(v,4) for v in o.dimensions) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=='MESH']
    hit=[]
    for m in bpy.data.materials:
        if basemat(m) in GLOW: setmat(m,True,False); hit.append(basemat(m))
    for o in list(bpy.data.objects):  # snapshot: renaming re-sorts bpy.data in 5.x
        if o.name.startswith(name) and not o.name.startswith(name+"_h9dim"): o.name = name+"_h9dim"+o.name[len(name):]
        if o.data and hasattr(o.data,"name") and o.data.name.startswith(name) and not o.data.name.startswith(name+"_h9dim"): o.data.name = name+"_h9dim"+o.data.name[len(name):]
    bpy.ops.export_scene.fbx(filepath=dst, **EXP)
    # verify
    clear(); bpy.ops.import_scene.fbx(filepath=dst, axis_forward='-Z', axis_up='Y', global_scale=1.0)
    bb1 = [tuple(round(v,4) for v in o.dimensions) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=='MESH']
    tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.data.objects if o.type=='MESH')
    report[name] = dict(out=os.path.basename(dst), dimmed=sorted(set(hit)), dims_match=bb0==bb1, tris=tris,
                        objects=sorted(o.name for o in bpy.data.objects))
    print("DONE", name, report[name]["dims_match"], hit)
json.dump(report, open(os.path.join(ROOT,"_src","h9dim","h9dim_report.json"),"w"), indent=1)

# ---- preview: before (top row) vs after (bottom row), dark night scene ----
clear(); sc = bpy.context.scene
PV = ["lantern_large_hanging","heart_lantern_cluster","h9_lantern_pendulum","cup_lantern_stake","glowing_mushrooms","tee_sign_h09"]
x = 0.0; xs = {}
for name in PV:
    for row,suf in ((0,""),(1,"_h9dim")):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT,"fbx",name+suf+".fbx"), axis_forward='-Z', axis_up='Y')
        new = [o for o in bpy.data.objects if o not in before]
        for o in new: o["_row"]=row; o["_prop"]=name
        for o in new:
            for s in o.material_slots:
                if s.material and not s.material.get("_done"):
                    s.material = s.material.copy(); setmat(s.material, row==1, True); s.material["_done"]=1
# layout by bbox
def bbox(objs):
    pts=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])
bpy.context.view_layer.update()
groups = {}
for o in bpy.data.objects:
    if o.parent is None: groups.setdefault((o["_prop"],o["_row"]),[]).append(o)
H = 0
for name in PV:
    allobjs=[c for k in ((name,0),(name,1)) for r in groups[k] for c in [r]+list(r.children_recursive)]
    lo,hi=bbox(allobjs); h=hi.z-lo.z; w=hi.x-lo.x; s=2.0/max(h,w,1e-3)
    for row in (0,1):
        for r in groups[(name,row)]:
            r.scale=(s,s,s); r.location=(0,0,0)
    bpy.context.view_layer.update()
    for row in (0,1):
        objs=[c for r in groups[(name,row)] for c in [r]+list(r.children_recursive)]
        lo,hi=bbox(objs)
        for r in groups[(name,row)]:
            r.location += Vector((x-(lo.x+hi.x)/2, -(lo.y+hi.y)/2, (0 if row==1 else 2.6)-lo.z))
    x += 2.6
bpy.ops.mesh.primitive_plane_add(size=60, location=(x/2-1.3,0,-0.01))
gm=bpy.data.materials.new("ground"); gm.use_nodes=True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.02,0.03,0.02,1)
bpy.context.object.data.materials.append(gm)
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.004,0.006,0.012,1)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50),0,math.radians(30))); bpy.context.object.data.energy=0.15
cx=x/2-1.3
bpy.ops.object.camera_add(location=(cx,-14,2.4), rotation=(math.radians(90),0,0)); sc.camera=bpy.context.object
bpy.context.object.data.type='ORTHO'; bpy.context.object.data.ortho_scale=x+0.6
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1600; sc.render.resolution_y=int(1600*5.4/(x+0.6))
sc.view_settings.view_transform='AgX'
try:
    sc.use_nodes=True
except Exception: pass
sc.render.filepath=os.path.join(ROOT,"_src","h9dim","preview_raw.png")
bpy.ops.render.render(write_still=True)
print("PREVIEW OK", PV)
