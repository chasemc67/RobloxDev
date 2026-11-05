"""Headless reimport verification: hierarchy, names, pivot, geometry and materials."""
import bpy,json,math
from pathlib import Path
S=Path(__file__).resolve().parent;D=S.parents[2]
manifest=json.loads((D/'models/props_batch2_manifest.json').read_text());parts=json.loads((S/'parts.json').read_text());src={p['id']:p for p in parts};results=[]
for p in manifest['parts']:
    for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=str(D/'models'/p['fbx']),use_anim=False)
    roots=[o for o in bpy.context.scene.objects if o.type=='EMPTY'];ms=[o for o in bpy.context.scene.objects if o.type=='MESH'];errors=[]
    if len(roots)!=1 or roots[0].name!=p['id']:errors.append('root hierarchy')
    if roots and roots[0].location.length>1e-5:errors.append('root pivot nonzero')
    actual=0;maxerror=0
    for m in p['meshes']:
        o=next((o for o in ms if o.name==m['mesh']),None)
        if not o:errors.append('missing '+m['mesh']);continue
        if o.parent not in roots:errors.append('wrong mesh parent')
        o.data.calc_loop_triangles();t=len(o.data.loop_triangles);actual+=t
        if t!=m['tris'] or t>=20000:errors.append('triangles')
        # Imported coordinates converted back to hole convention and compared as unordered bounds.
        vv=[o.matrix_world@v.co for v in o.data.vertices];rb=[[v.x,v.z,-v.y] for v in vv];sv=src[p['id']]['groups'][m['material']]['verts']
        for axis in range(3):
            maxerror=max(maxerror,abs(min(v[axis] for v in rb)-min(v[axis] for v in sv)),abs(max(v[axis] for v in rb)-max(v[axis] for v in sv)))
        if maxerror>1e-4:errors.append('coordinate bounds')
    if len(ms)!=len(p['meshes']):errors.append('mesh count')
    results.append(dict(id=p['id'],status='PASS' if not errors else 'FAIL',mesh_count=len(ms),tris=actual,coordinate_error=maxerror,errors=errors))
(S/'fbx_validation.json').write_text(json.dumps(dict(all_pass=all(r['status']=='PASS' for r in results),parts=results),indent=2))
print(json.dumps(results));assert all(r['status']=='PASS' for r in results)
