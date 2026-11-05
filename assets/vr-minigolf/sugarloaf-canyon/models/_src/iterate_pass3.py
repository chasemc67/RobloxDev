from pathlib import Path
p=Path('_src/render_hero.py');t=p.read_text().replace('(65,131,-245),(0,73,-296),75','(80,185,-240),(0,80,-299),65').replace("(-370,196,165),(-900,217,100),70","(-370,170,165),(-1250,155,60),52")
t=t.replace("or obj.name.startswith('sunset_arch_')","or (obj.instance_type=='COLLECTION' and obj.instance_collection.name!='asset_far_arch_card')")
t=t.replace("nt.links.new(sep.outputs['Z'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bg.inputs['Color']); bg.inputs['Strength'].default_value=.7","mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=-.45;mapping.inputs['From Max'].default_value=.45;nt.links.new(sep.outputs['Z'],mapping.inputs['Value']);nt.links.new(mapping.outputs[0],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bg.inputs['Color']); bg.inputs['Strength'].default_value=.35")
# Camera rays receive saturated sunset; illumination receives lavender ambient.
t=t.replace('bpy.context.scene.world=world',"path=nt.nodes.new('ShaderNodeLightPath');ambient=nt.nodes.new('ShaderNodeBackground');ambient.inputs['Color'].default_value=(.38,.28,.6,1);ambient.inputs['Strength'].default_value=.25;mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(ambient.outputs[0],mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes['World Output'].inputs['Surface']);bpy.context.scene.world=world")
# restore terrain for every next shot (arch remains last)
p.write_text(t)
