# blender.exe -b --factory-startup out/start_ship_v3.blend --python export_v3.py -- <fbx_dir>
# Same export conventions as source_scripts/export_from_blend.py: FBX axis_forward -Z, axis_up Y, scale 1, embedded textures, face smoothing.
# start_ship_b2_visual.fbx = Visual meshes + Ramps + Props + anchor empties; start_ship_b2_col.fbx = 190 COL boxes; 3 ramp FBXs on their own origin.
# The blend is NOT saved (ramp locations are restored after each own-origin export anyway).
import bpy, sys, os
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
C = bpy.data.collections
order = ['Hull', 'DeckCabin', 'Rigging', 'RampFlight1', 'RampLanding', 'RampFlight2', 'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow']
vis = [o for o in C['Visual'].objects if o.type == 'MESH'] + [o for o in C['Ramps'].objects]
vis.sort(key=lambda o: order.index(o.name))
props = sorted([o for o in C['Props'].objects if o.type == 'MESH'], key=lambda o: o.name)
emp = [o for o in C['Visual'].objects if o.type == 'EMPTY']
cob = list(C['Collision'].objects)
def export(path, objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH', 'EMPTY'}, axis_forward='-Z', axis_up='Y', global_scale=1,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True,
                             mesh_smooth_type='FACE', add_leaf_bones=False)
    print('EXPORTED', path, len(objs))
export(os.path.join(OUT, 'start_ship_b2_visual.fbx'), vis + props + emp)
export(os.path.join(OUT, 'start_ship_b2_col.fbx'), cob)
for ob in vis:
    if ob.name.startswith('Ramp'):
        loc = ob.location.copy(); ob.location = (0, 0, 0); export(os.path.join(OUT, ob.name + '_own_origin.fbx'), [ob]); ob.location = loc
print('EXPORT_OK')
