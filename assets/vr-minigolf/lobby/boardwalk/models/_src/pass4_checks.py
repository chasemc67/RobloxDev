import bpy,json,os,sys
from mathutils import Vector
SRC=os.path.dirname(__file__);sys.path.insert(0,SRC)
import bwlib as L
COURSES=('lantern_grove','sugarloaf_canyon','aurora_archipelago')
def intersects(poly,mn,mx):
    # Sutherland-Hodgman clipping against all six box planes. Includes triangle interiors.
    for axis in range(3):
        for bound,sgn in ((mn[axis],1),(mx[axis],-1)):
            out=[]
            for a,b in zip(poly,poly[1:]+poly[:1]):
                da=(a[axis]-bound)*sgn;db=(b[axis]-bound)*sgn
                if da>=0:out.append(a)
                if (da>=0)!=(db>=0):out.append(a.lerp(b,da/(da-db)))
            poly=out
            if not poly:return False
    return bool(poly)
def clearance(objs,mn,mx):
    for o in objs:
        for f in o.data.polygons:
            pts=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
            if intersects(pts,mn,mx):return False
    return True
def run(root,kit=False,fit=False):
    if fit:
        valid=os.path.join(root,'_src','fitcheck_pass4_validated.txt')
        if os.path.exists(valid):os.remove(valid)
    man=json.load(open(os.path.join(root,'manifest.json')));lines=[];fail=[]
    def check(ok,label):
        lines.append(('PASS ' if ok else 'FAIL ')+label)
        if not ok:fail.append(label)
    entries=[e for e in man['props'] if kit or e['name'].startswith(('bw_arch_','bw_portal_','bw_scn_'))]
    for e in entries:
        L.reset_scene()
        bpy.ops.import_scene.fbx(filepath=os.path.join(root,e['fbx']),axis_forward='-Z',axis_up='Y',global_scale=1)
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update()
        mn,mx=L.bbox_blender(objs);size,center=L.to_roblox_bbox(mn,mx)
        check(all(abs(a-b)<.015 for a,b in zip(size,e['bbox_size_studs'])),e['name']+' bbox '+str(size))
        check(all(abs(a-b)<.015 for a,b in zip(center,e['bbox_center_from_pivot'])),e['name']+' orientation/frame and centre '+str(center))
        check(L.tri_count(objs)==e['triangles'],e['name']+' triangles '+str(L.tri_count(objs)))
        check(len({m.name for o in objs for m in o.data.materials})==len(e['materials']),e['name']+' materials')
        check(all(o.location.length<.001 and all(abs(v-1)<.001 for v in o.scale) for o in objs),e['name']+' shared origin and scale 1')
        if kit and e['pivot']=='base centre':
            check(abs(mn.z)<.002 and abs(mn.x+mx.x)<.002 and abs(mn.y+mx.y)<.002,e['name']+' measured base-centre pivot')
        if kit and e['pivot']=='top centre':check(abs(mx.z)<.002,e['name']+' measured top pivot')
        if fit and e.get('anchor_position_arch_local'):
            anchor=e['anchor_position_arch_local']
            for o in objs:o.location=Vector((anchor[0],-anchor[2],anchor[1]))
            bpy.context.view_layer.update()
            mn,mx=L.bbox_blender(objs)
            check(all(abs(v)<.001 for v in e['bbox_max_roblox'][1:2]),e['name']+' hinge at top of cord')
        if fit and e['name'].startswith('bw_arch_') and not e['name'].endswith('nameplate') and not e['name'].startswith('bw_arch_lantern_grove_lantern_'):
            check(mn.x>=-8.001 and mx.x<=8.001 and mn.y>=-2.001 and mx.y<=2.001 and mn.z>=-.001 and mx.z<=18.001,e['name']+' 16x18x4 envelope')
            check(clearance(objs,(-4.999,-2.001,.001),(4.999,2.001,11.999)),e['name']+' opening triangle-volume clearance')
            check(clearance(objs,(-4.999,-1.499,.001),(4.999,1.499,9.999)),e['name']+' trigger triangle-volume clearance')
        if e['name'].startswith('bw_portal_surface_'):
            uv=[u.uv for o in objs for u in o.data.uv_layers.active.data]
            check(e['triangles']==2 and all(abs(v.y+1.5)<.001 for o in objs for v in (o.matrix_world@v.co for v in o.data.vertices)),e['name']+' quad at Roblox Z=1.5')
            check(all(min(u[k] for u in uv)<.001 and max(u[k] for u in uv)>.999 for k in (0,1)),e['name']+' full UV 0-1')
            check(all((o.matrix_world.to_3x3()@f.normal).y<-.99 for o in objs for f in o.data.polygons),e['name']+' front normal Roblox +Z')
        check(e['triangles']<=e['tris_max'],e['name']+' individual budget')
    if fit:
        from scenery_checks import run_scenery
        run_scenery(root,man,check)
        for c,limit in zip(COURSES,(15000,8000,10000)):
            total=sum(e['triangles'] for e in entries if e['name'].startswith('bw_arch_'+c) or e['name']=='bw_portal_surface_'+c)
            check(.8*limit<=total<=.95*limit,c+' aggregate moving+static budget '+str(total))
            arch=next(e for e in entries if e['name']=='bw_arch_'+c)
            check([b['center'] for b in arch['collision']]==[[-6.5,9,0],[6.5,9,0],[0,14,0]],c+' exact collision centers')
            check(len(arch['collision'])==3 and [b['size'] for b in arch['collision']]==[[3,18,4],[3,18,4],[10,4,4]],c+' three prescribed collision boxes')
            check(arch['portal_trigger']['center']==[0,5,0] and arch['portal_trigger']['size']==[10,10,3] and not arch['portal_trigger']['modelled'],c+' unmodelled trigger metadata')
    lines.append('RESULT: '+('ALL PASS' if not fail else str(len(fail))+' FAIL'))
    name='fitcheck_pass4_validated.txt' if fit and not fail else 'fitcheck_pass4_failed.txt' if fit else 'reimport_check_pass4.txt'
    out=os.path.join(root,'_src',name);open(out,'w').write('\n'.join(lines)+'\n');print('\n'.join(lines))
    if fail:raise RuntimeError(str(fail))

