# Blender: start_ship_v2_3.blend --python this -- W   -> W/reexport/*.fbx  (same export settings as src/build_ship.py)
import bpy,sys,os
W=sys.argv[sys.argv.index('--')+1];OUT=os.path.join(W,'reexport');os.makedirs(OUT,exist_ok=True)
C=bpy.data.collections
vis=[o for o in C['Visual'].objects if o.type=='MESH']+[o for o in C['Ramps'].objects];emp=[o for o in C['Visual'].objects if o.type=='EMPTY']
order=['Hull','DeckCabin','Rigging','RampFlight1','RampLanding','RampFlight2','Pier','RockBumper','Dressing','Dressing_Glow'];vis.sort(key=lambda o:order.index(o.name))
cob=list(C['Collision'].objects)
def export(path,objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    print('EXPORTED',path)
export(os.path.join(OUT,'start_ship_b2_visual.fbx'),vis+emp)
export(os.path.join(OUT,'start_ship_b2_col.fbx'),cob)
for ob in vis:
    if ob.name.startswith('Ramp'):
        loc=ob.location.copy();ob.location=(0,0,0);export(os.path.join(OUT,ob.name+'_own_origin.fbx'),[ob]);ob.location=loc
