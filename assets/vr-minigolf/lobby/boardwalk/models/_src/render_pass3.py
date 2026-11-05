"""Export-based previews using the established render library and camera conventions."""
import bpy,sys,os,json,math
from mathutils import Vector
SRC=os.path.dirname(__file__);sys.path.insert(0,SRC)
import bwlib as L
import render_lib as R
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
kit='--kit' in args
root=args[0] if kit else os.path.dirname(SRC)
man=json.load(open(os.path.join(root,'manifest.json')))
dest=os.path.join(root,'previews') if kit else os.path.join(root,'previews','portals');os.makedirs(dest,exist_ok=True)
entries=man['props'] if kit else [p for p in man['props'] if p['name'] in ['bw_arch_'+c for c in ('lantern_grove','sugarloaf_canyon','aurora_archipelago')]]
for p in entries:
    sc=L.reset_scene();R.setup_cycles(sc,samples=24,res=(640,640))
    # GPU OptiX preferred; explicit Eevee fallback when unavailable.
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if not any(d.use and d.type=='OPTIX' for d in prefs.devices):sc.render.engine='CYCLES' if any(d.use and d.type=='CUDA' for d in prefs.devices) else 'BLENDER_EEVEE'
    R.world(sc,'#E9C9AE',.8)
    col=bpy.data.collections.new('preview');sc.collection.children.link(col)
    R.sun(col,(.55,.75,-.6),'#FFD2A0',3,6)
    R.plane(col,'ground',(300,300),(0,0,-.12),R.flat_mat('ground','#B5835A'))
    objs=R.import_fbx(os.path.join(root,p['fbx']),col)
    if kit and p['name']=='kit_leaderboard_frame':
        for i in (1,2,3):objs+=R.import_fbx(os.path.join(root,'fbx','kit_leaderboard_panel_'+str(i)+'.fbx'),col)
    if kit and p['pivot']=='top centre':
        mn0,mx0=L.bbox_blender(objs)
        for o in objs:o.location.z-=mn0.z
        bpy.context.view_layer.update()
    if not kit:
        c=p['name'].removeprefix('bw_arch_')
        for q in man['props']:
            if q['name'].startswith(p['name']+'_'):
                more=R.import_fbx(os.path.join(root,q['fbx']),col)
                if q.get('anchor_position_arch_local'):
                    a=q['anchor_position_arch_local']
                    for o in more:o.location=(a[0],-a[2],a[1])
                objs+=more
        for asset,loc in (('bw_arch_nameplate',(0,-2.25,13.5)),('bw_coming_soon_sign',(0,-2.25,11.7)),('bw_portal_apron',(0,-4,0))):
            if asset=='bw_coming_soon_sign' and c=='lantern_grove':continue
            more=R.import_fbx(os.path.join(root,'fbx',asset+'.fbx'),col)
            for o in more:o.location=loc
        # Display surface preview material only: exported quad remains runtime-neutral.
        surf=R.import_fbx(os.path.join(root,'fbx','bw_portal_surface_'+c+'.fbx'),col)
        mat=R.flat_mat('portal_preview',{'lantern_grove':'#FFC867','sugarloaf_canyon':'#F6A6C8','aurora_archipelago':'#5BE3A0'}[c],emit=.6)
        nt=mat.node_tree;b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=2
        ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*L.lin({'lantern_grove':'#E58A3A','sugarloaf_canyon':'#F2A57E','aurora_archipelago':'#9B6BFF'}[c]),1)
        ramp.color_ramp.elements[1].color=(*L.lin({'lantern_grove':'#FFC867','sugarloaf_canyon':'#F6A6C8','aurora_archipelago':'#5BE3A0'}[c]),1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],b.inputs['Base Color']);nt.links.new(ramp.outputs[0],b.inputs['Emission Color'])
        for o in surf:o.data.materials.clear();o.data.materials.append(mat)
    R.fix_imported_materials(2)
    if kit:
        for o in objs:
            for m in o.data.materials:
                if m.name.startswith('BW_Neon'):
                    rgb=L.lin(next((q['color'] for q in p.get('parts',[]) if q.get('color')),'#FFC867'))
                    b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Emission Color'].default_value=(*rgb,1);b.inputs['Emission Strength'].default_value=.8
    # FBX emission wiring is not portable; restore the manifest's runtime Neon colour for previews.
    if not kit:
        for o in col.objects:
            if o.type!='MESH':continue
            for m in o.data.materials:
                if m.name.startswith('BW_Neon'):
                    rgb=L.lin('#9FE6F2' if c=='aurora_archipelago' and o.name.startswith(p['name']+'__') else '#F6A6C8' if c=='sugarloaf_canyon' and o.name.startswith(p['name']+'__') else '#FFC867')
                    b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Emission Color'].default_value=(*rgb,1);b.inputs['Emission Strength'].default_value=.8
    mn,mx=L.bbox_blender(objs);center=(mn+mx)/2;ext=mx-mn
    cap=R.capsule(col,(0,-2.6,0) if not kit else (mx.x+1.5,0,0))
    cam=R.camera(col,fov_deg=65 if not kit else 48)
    name=p['name'] if kit else p['name'].removeprefix('bw_arch_')
    for view in ('eye','34'):
        cap.hide_render=view=='34'
        front=Vector((0,1 if kit else -1,0))
        if view=='eye':
            distance=20 if not kit else max(10,ext.x*1.4,ext.z*1.8)
            cam.location=Vector((center.x,center.y,5))+front*distance
            R.look_at(cam,(center.x,center.y,center.z if not kit else max(2,center.z)))
        else:
            d=max(8,ext.length*(1.15 if kit else .9))
            cam.location=center+front*d+Vector((-d*.65,0,d*.55));R.look_at(cam,center)
        sc.render.filepath=os.path.join(dest,name+'_'+view+'.png');bpy.ops.render.render(write_still=True)
    L.log('Rendered pass3 '+name+' engine '+sc.render.engine)
