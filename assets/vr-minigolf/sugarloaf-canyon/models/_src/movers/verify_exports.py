import bpy,json
from pathlib import Path
SRC=Path(__file__).resolve().parent;OUT=SRC.parent
report=[]
for e in json.loads((SRC/'movers_manifest.json').read_text())['movers']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(OUT/e['fbx']))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    image_nodes=[n for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    item=dict(id=e['id'],MeshParts=len(meshes),tris=tris,texture_images=sorted({n.image.name for n in image_nodes}),origins=[list(o.location) for o in meshes],pass_mesh_counts=len(meshes)==e['MeshParts'] and tris==e['tris'])
    report.append(item)
    if not item['pass_mesh_counts']:raise RuntimeError('Export mesh mismatch '+e['id'])
(SRC/'export_verification.json').write_text(json.dumps(report,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    devices=[dict(name=d.name,type=d.type) for d in prefs.devices]
except Exception as ex:devices=[dict(error=str(ex))]
(SRC/'cycles_devices.json').write_text(json.dumps(devices,indent=2))
print('All five FBX round-trip counts PASS; device inventory saved')
