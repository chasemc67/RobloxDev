import bpy,json,sys
from pathlib import Path
SRC=Path(__file__).resolve().parent;OUT=SRC.parent
sys.path.insert(0,str(SRC.parents[1]/'lib'));import sclib as L
report=[]
for e in json.loads((SRC/'movers_manifest.json').read_text())['movers']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(OUT/e['fbx']))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    image_nodes=[n for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    item=dict(id=e['id'],MeshParts=len(meshes),tris=tris,texture_images=sorted({n.image.name for n in image_nodes}),origins=[list(o.location) for o in meshes],pass_mesh_counts=len(meshes)==e['MeshParts'] and tris==e['tris'])
    from mathutils import Vector
    pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
    size=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]];center=[(hi[0]+lo[0])/2,(hi[2]+lo[2])/2,-(hi[1]+lo[1])/2]
    item['bbox_roundtrip']=[size,center]
    item['pass_bbox']=max(abs(a-b) for actual,expected in zip(item['bbox_roundtrip'],e['bbox']) for a,b in zip(actual,expected))<1e-4
    item['pass_origins']=all(max(abs(v) for v in o.location)<1e-5 for o in meshes)
    item['pass_material_merge']=len(set(o.data.materials[0].name for o in meshes))==len(meshes)
    item['pass_budget']=all(sum(len(p.vertices)-2 for p in o.data.polygons)<20000 for o in meshes)
    exp=sorted(L.TEX[m][0] for m in e['materials'] if m in L.TEX);item['textures_expected']=exp
    item['pass_textures_embedded']=all(any(n.startswith(t) for n in item['texture_images']) for t in exp)
    if not all(item[k] for k in ('pass_bbox','pass_origins','pass_material_merge','pass_budget','pass_textures_embedded')):raise RuntimeError('Roundtrip geometry/material/pivot failed '+e['id'])
    report.append(item)
    if not item['pass_mesh_counts']:raise RuntimeError('Export mesh mismatch '+e['id'])
(SRC/'export_verification_pass5.json').write_text(json.dumps(report,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    devices=[dict(name=d.name,type=d.type) for d in prefs.devices]
except Exception as ex:devices=[dict(error=str(ex))]
(SRC/'cycles_devices.json').write_text(json.dumps(devices,indent=2))
print('All pass-5 manifest FBX round-trips PASS; device inventory saved')
