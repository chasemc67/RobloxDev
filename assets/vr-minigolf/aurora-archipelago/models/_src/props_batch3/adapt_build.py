"""Copy the batch2 Blender pipeline; this helper never imports or launches Blender."""
from pathlib import Path
S=Path(__file__).resolve().parent
s=(S.parent/'props_batch2/build_batch2.py').read_text().replace('props_batch2','props_batch3').replace('batch=2','batch=3').replace('[9,10,11,12,13,15,16,17]','[4,6,14,18]').replace('resolution_x=1280','resolution_x=1024').replace('resolution_y=960','resolution_y=768').replace('1280/960','1024/768')
s=s.replace("(D/'models/props_batch3_manifest.json')", "(D/'props_batch3_manifest.json')")
s=s.replace("sc=bpy.context.scene;sc.unit_settings.system='NONE'", "assert bpy.app.version[:2]==(5,2), 'Requires Blender 5.2'\nsc=bpy.context.scene;sc.unit_settings.system='NONE'")
s=s.replace("if k=='Ice':b.inputs['Transmission Weight'].default_value=.3;b.inputs['IOR'].default_value=1.31", "b.inputs['Alpha'].default_value=1-alpha\n    if k=='Ice':b.inputs['Transmission Weight'].default_value=.3;b.inputs['IOR'].default_value=1.31")
s=s.replace("motion=p['motion'],notes=p['notes'],can_collide=False", "motion=p['motion'],notes=p['notes'],override_boxes=p['override_boxes'],can_collide=False,can_query=False,can_touch=False")
s=s.replace("def render(path,objs):", "def render(path,objs,view='34',hole=None):")
s=s.replace("cam.location=center+Vector((.8,-1.3,1.2)).normalized()*150;", "cam.data.type='ORTHO';cam.location=center+Vector((0,-1,.18) if view=='front' else (.8,-1.3,1.2)).normalized()*150;")
s=s.replace("sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)", "if view=='eye':\n        cam.data.type='PERSP';cam.data.lens=22;cam.location=B([H[hole]['tee']['position'][0],H[hole]['tee']['position'][1]+5.5,H[hole]['tee']['position'][2]+2]);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()\n    sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)")
s=s.replace("render(PV/(p['id']+'_34.png'),visible)", "for view in ['front','34','eye']:render(PV/(p['id']+'_'+view+'.png'),visible,view,p['hole'])")
# Root holds its hole-local pivot; exported geometry remains asset-relative.
# Disable hardware rendering explicitly: Cycles device CPU is inherited.
(S/'build_batch3.py').write_text(s)
print('Wrote build_batch3.py; Blender NOT run')
