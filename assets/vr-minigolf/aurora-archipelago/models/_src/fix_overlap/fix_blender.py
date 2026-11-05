"""One Blender job: approved FBX import, measurement, outward cladding, reimport, renders."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import json
import numpy as np
from mathutils import Vector
from common import S,D,FIX,records,sha,guard,write_json
from clearance import solids,measure,triangle_solid,FACES

def B(v): return Vector((v[0],-v[2],v[1]))
def R(v): return np.array([v.x,v.z,-v.y])
def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def imported(path,p):
    fresh();bpy.ops.import_scene.fbx(filepath=str(path))
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    roots=[o for o in bpy.context.scene.objects if o.type=='EMPTY' and o.parent is None]
    if len(roots)!=1 or np.linalg.norm(R(roots[0].matrix_world.translation))>1e-5: raise RuntimeError('Invalid root pivot')
    if sorted(o.name.split('__')[-1].split('.')[0] for o in objs)!=sorted(m['material'] for m in p['meshes']): raise RuntimeError('Mesh/material names differ')
    return objs,roots[0]
def triangles(objs,p):
    ts=[]
    for o in objs:
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles: ts.append([R(o.matrix_world@o.data.vertices[i].co)+p['anchor_local'] for i in t.vertices])
    return np.array(ts)
def cache(objs,p,stage,path):
    folder=S/'cache'/stage;folder.mkdir(parents=True,exist_ok=True)
    file=folder/(p['id']+'.npy');np.save(file,triangles(objs,p))
    write_json(file.with_suffix('.json'),dict(fbx_sha256=sha(path),source_sha256=p['source_sha256'],npy_sha256=sha(file),coordinates='hole-local Roblox',extraction='fresh FBX import'))
def components(o):
    adjacency={v.index:set() for v in o.data.vertices}
    for e in o.data.edges:
        a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    unseen=set(adjacency)
    while unseen:
        stack=[unseen.pop()];group=[]
        while stack:
            i=stack.pop();group.append(i)
            for j in adjacency[i]&unseen: unseen.remove(j);stack.append(j)
        yield group
def planes(box):
    v=box['vertices'];center=v.mean(0)
    for f in FACES:
        n=np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]);n/=np.linalg.norm(n)
        if n@(v[f[0]]-center)<0:n=-n
        yield n,float(n@v[f[0]])
def edit(objs,p,boxes):
    id=p['id'];lift=0.
    if id=='h06_respawn_stone':
        original=triangles(objs,p)
        def safe(y):
            return measure(original+[0,y,0], boxes, ('felt',))['felt']['clearance']>=.150001
        # Search the first safe vertical interval; then bisect its boundary.
        lo=0.;hi=0.
        if not safe(0):
            for k in range(1,20001):
                hi=k*.001
                if safe(hi): break
                lo=hi
            else: raise RuntimeError('No felt-clear lift within 20 studs')
            for _ in range(35):
                mid=(lo+hi)/2
                if safe(mid):hi=mid
                else:lo=mid
        lift=hi
        for o in objs:
            inv=o.matrix_world.inverted()
            for v in o.data.vertices: v.co=inv@(o.matrix_world@v.co+B([0,lift,0]))
        # Rails are intentionally not used to increase the felt-only lift.
        return lift
    if id!='h18_crystal_chute':
        raise RuntimeError('Asset is not authorized for editing: '+id)
    rebuild_chute(objs,p,boxes)
    return lift


def clip_polygon(poly,n,d):
    """Keep the n.x <= d halfspace, inserting exact edge intersections."""
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=float(a@n-d);db=float(b@n-d)
        if da<=0:out.append(a)
        if (da<0<db) or (db<0<da):out.append(a+(b-a)*(da/(da-db)))
    return out


def subtract_volume(poly,boundaries):
    # Partition a polygon into disjoint outside fragments. The remainder is
    # inside every plane and discarded; this clips edges as well as vertices.
    out=[];remaining=poly
    for n,d in boundaries:
        if len(remaining)<3:break
        outside=clip_polygon(remaining,-n,-d)
        if len(outside)>=3:out.append(outside)
        remaining=clip_polygon(remaining,n,d)
    return out


def footprint(box,margin=0.):
    return [(n,d+margin) for n,d in planes(box) if abs(n[1])<1e-8]


def lane_check(ts,boxes):
    # Infinite-height extrusion of the authored chute footprint is stronger
    # than a finite lane volume: no overhead intrusion is allowed either.
    lane=next(b for b in boxes if b['kind']=='felt' and b['id']=='chute')
    bounds=footprint(lane)
    points=ts.reshape(-1,3)
    inside=np.ones(len(points),dtype=bool)
    for n,d in bounds:inside &= points@n<d-1e-6
    if inside.any():raise RuntimeError('Chute vertex inside unchanged 1.6-wide lane')
    for t in ts:
        poly=list(t)
        for n,d in bounds:poly=clip_polygon(poly,n,d-1e-6)
        if len(poly)>=3 and np.linalg.norm(np.cross(poly[1]-poly[0],poly[2]-poly[0]))>1e-10:
            raise RuntimeError('Chute face crosses lane volume')
    return dict(width=1.6,vertices_inside=0,faces_crossing=0)


def rebuild_chute(objs,p,boxes):
    source=json.loads((D/'models/_src/props_batch3/parts_prepolish.json').read_text())
    skin_ids=next(q for q in source if q['id']==p['id'])['skin_ids']
    rails=[b for b in boxes if b['kind']=='rail']
    felts=[b for b in boxes if b['kind']=='felt']
    # Clipping against expanded rail halfspaces guarantees >= .30 Euclidean
    # distance. Felt footprints are conservatively excluded at every height,
    # so no new face covers a play surface, including either crystal bank.
    exclusions=[[(n,d+.30002) for n,d in planes(b)] for b in rails]
    exclusions += [footprint(b,.15002) for b in felts]
    groups={'Ice':([],[]),'IceCore':([],[])}
    for box in rails:
        if box['id'] not in skin_ids:continue
        for face,(n,d) in zip(FACES,planes(box)):
            if n[1]<-.5:continue  # no bottom skin
            quad=box['vertices'][list(face)]+n*.30004
            if abs(n[1])<.5:
                # Omit an entire side facing a play surface. Check tangential
                # overlap, so a remote felt does not suppress unrelated faces.
                tangent=np.array([-n[2],0,n[0]])
                if any((b['vertices'].mean(0)-quad.mean(0))@n>0 and
                       min((b['vertices']@tangent).max(),(quad@tangent).max())>
                       max((b['vertices']@tangent).min(),(quad@tangent).min())+1e-6
                       for b in felts):continue
            # Outward crystal apex and flat triangular facets; both approved
            # materials are retained without any inward-facing lane shell.
            apex=quad.mean(0)+n*.12
            for k in range(4):
                fragments=[[quad[k],quad[(k+1)%4],apex]]
                for volume in exclusions:
                    fragments=[piece for poly in fragments for piece in subtract_volume(poly,volume)]
                    if not fragments:break
                verts,faces=groups['IceCore' if k==0 else 'Ice']
                for poly in fragments:
                    for j in range(1,len(poly)-1):
                        tri=[poly[0],poly[j],poly[j+1]]
                        if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))<1e-10:continue
                        # Ensure outward winding even after clipping.
                        if np.cross(tri[1]-tri[0],tri[2]-tri[0])@n<0:tri.reverse()
                        i=len(verts);verts.extend(tri);faces.append((i,i+1,i+2))
    for o in objs:
        material=o.name.split('__')[-1].split('.')[0]
        verts,faces=groups[material]
        if not faces:raise RuntimeError('Empty cladding material: '+material)
        inv=o.matrix_world.inverted();me=bpy.data.meshes.new(o.name+'_cladding')
        me.from_pydata([inv@B(v-p['anchor_local']) for v in verts],[],faces)
        for mat in o.data.materials:me.materials.append(mat)
        me.update();o.data=me
    ts=triangles(objs,p)
    if len(ts)>=3000:raise RuntimeError('Cladding triangle budget exceeded')
    lane_check(ts,boxes)
    result=measure(ts,boxes)
    if result['rail']['clearance']<.30 or result['felt']['clearance']<.15:
        raise RuntimeError('Rebuilt cladding fails true mesh clearance: '+str(result))


def render(objs,p,boxes,result,path,close=False,focus=None):
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16
    sc.render.resolution_x=900;sc.render.resolution_y=700;sc.render.resolution_percentage=100
    for b in boxes:
        me=bpy.data.meshes.new(b['id']);me.from_pydata([B(v-p['anchor_local']) for v in b['vertices']],[],FACES)
        obj=bpy.data.objects.new(b['id'],me);sc.collection.objects.link(obj)
        mat=bpy.data.materials.new('contact_'+b['kind']);mat.diffuse_color=(1,.12,.04,1) if b['kind']=='rail' else (.05,.8,.25,1);me.materials.append(mat)
    ts=triangles(objs,p);lo=ts.reshape(-1,3).min(0);hi=ts.reshape(-1,3).max(0)
    target=(lo+hi)/2
    if close:
        contact=focus or min(result.values(),key=lambda x:x['clearance'])
        target=np.array(contact['solid_point'])
    cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam
    center=B(target-p['anchor_local']);cam.location=center+Vector((8,-12,9));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4 if close else float(np.linalg.norm(hi-lo)*1.15)
    sc.world=bpy.data.worlds.new('World');sc.world.color=(.35,.35,.35)
    sun=bpy.data.objects.new('Sun',bpy.data.lights.new('Sun','SUN'));sc.collection.objects.link(sun);sun.data.energy=3;sun.rotation_euler=(.4,-.3,-.6)
    path.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)

def main():
    guard('check');holes={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
    before={};validation=[];build=[]
    for p in records():
        path=D/p['source_fbx'];objs,root=imported(path,p);cache(objs,p,'before',path)
        ts=triangles(objs,p)
        if len(ts)!=p['tris']:raise RuntimeError('Approved FBX triangle count mismatch: '+p['id'])
        before[p['id']]=measure(ts,solids(holes[p['hole']]))
    write_json(S/'clearance_before.json',before)
    from clearance import main as clearance_main
    clearance_main('before')
    for p in records('after'):
        id=p['id'];objs,root=imported(D/p['source_fbx'],p);boxes=solids(holes[p['hole']]);original=triangles(objs,p)
        lift=edit(objs,p,boxes);expected=triangles(objs,p)
        out=D/f'models/fbx/props_fix_overlap/{id}.fbx';out.parent.mkdir(parents=True,exist_ok=True)
        for o in bpy.context.scene.objects:o.select_set(o in objs or o==root)
        bpy.context.view_layer.objects.active=root
        bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,add_leaf_bones=False)
        objs,root=imported(out,p);actual=triangles(objs,p);cache(objs,p,'after',out)
        errors=[]
        if actual.shape!=expected.shape or not np.allclose(actual,expected,atol=1e-4):errors.append('reimport geometry differs')
        if len(actual)>=3000:errors.append('triangle budget')
        if id=='h06_respawn_stone' and not np.allclose(actual-original,[0,lift,0],atol=1e-4):errors.append('stone changed beyond vertical translation')
        lane_validation=lane_check(actual,boxes) if id=='h18_crystal_chute' else None
        validation.append(dict(lane_validation=lane_validation,id=id,tris=len(actual),pass_validation=not errors,errors=errors,fbx_sha256=sha(out)))
        after=measure(actual,boxes)
        q=dict(p);q['meshes']=[dict(m, tris=next(len(o.data.loop_triangles) for o in objs if o.name.split('__')[-1].split('.')[0]==m['material'])) for m in p['meshes']];q['lane_validation']=lane_validation;q.update(fbx=f'fbx/props_fix_overlap/{id}.fbx',tris=len(actual),before=before[id],after=after,lift_y=lift,can_collide=False,can_query=False,can_touch=False)
        points=actual.reshape(-1,3);q['bbox_hole_local']=[points.min(0).tolist(),points.max(0).tolist()];q['bbox_asset_local']=[(points.min(0)-p['anchor_local']).tolist(),(points.max(0)-p['anchor_local']).tolist()];q['bbox']=q['bbox_asset_local'];q['dimensions']=(points.max(0)-points.min(0)).tolist()
        build.append(q)
        render(objs,p,boxes,after,D/f'models/previews/props_fix_overlap/{id}_34.png')
        # Fresh imports keep context and lights out of the exported assets.
        for stage,path,result in [('before',D/p['source_fbx'],before[id]),('after',out,after)]:
            objs,root=imported(path,p)
            render(objs,p,boxes,result,S/f'renders/{id}_{stage}.png',True,min(before[id].values(),key=lambda x:x['clearance']))
    write_json(S/'fbx_validation.json',dict(all_pass=all(r['pass_validation'] for r in validation),parts=validation,generated_by='fresh-scene FBX reimport'))
    write_json(S/'build_fix.json',build)
    if not all(r['pass_validation'] for r in validation):raise RuntimeError('FBX validation failed')
    guard('check')
if __name__=='__main__':main()
