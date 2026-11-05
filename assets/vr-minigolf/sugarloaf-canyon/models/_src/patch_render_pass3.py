from pathlib import Path
import json
s=Path('_src')
p=s/'sc_textures.py';t=p.read_text().replace('b = np.floor(v * bands).astype(int) % 6','b = np.searchsorted(np.cumsum(BAND_WIDTHS)/36, (v*bands/4)%1, side="right")%4').replace('base = cols[b]','base = cols[b]');p.write_text(t)
p=s/'render_hero.py';t=p.read_text();t=t.replace('heights=hm[np.ix_(idx,idx)]; n=len(idx); X,Z=np.meshgrid(coords,coords)','heights=hm[np.ix_(idx,idx)]; n=len(idx); X,Z=np.meshgrid(coords,coords)\n    q=np.hypot(X-80,Z+130)/72\n    heights=np.where(q<1,18+110*np.sqrt(np.maximum(0,1-q**4)),heights)')
a=t.index("    colors=W['terrain']['strata']['colors']");b=t.index("    links.new(mod.outputs[0],ramp.inputs[0])",a)
t=t[:a]+'''    colors=['#E8C9A1','#C68C59','#CC8D91','#AF7061']
    ramp.color_ramp.interpolation='LINEAR'
    stops=[(0,0),(.105,0),(.117,1),(.382,1),(.394,2),(.549,2),(.561,3),(.99,3),(1,0)]
    for i,(pos,k) in enumerate(stops):
        e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos)
        e.position=pos;e.color=(*[L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(colors[k])],1)
''' + t[b:]
t=t.replace('bearing,elevation=math.radians(277),math.radians(-3)','bearing,elevation=math.radians(270),math.radians(25)').replace("light.energy=2; light.color=(1,.55,.30)","light.energy=3; light.color=(1,.66,.47)").replace("fill.color=(1,.73,.62)","fill.color=(.63,.57,1)").replace("sc.view_settings.exposure=1","sc.view_settings.exposure=.35")
t=t.replace("ramp.color_ramp.elements[0].color=(.65,.28,.15,1)","ramp.color_ramp.elements[0].color=(1,.38,.10,1)").replace("(.32,.12,.22,1)","(.36,.13,.38,1)")
t=t.replace("terrain(); water(); assets()","terrain(); water(); assets()\n        # Rose-band sheen, shared by every imported strata mesh.\n        mat=L.lglib.get_mat('Strata');nt=mat.node_tree\n        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(MODELS/'textures/strata_roughness.png'));tex.image.colorspace_settings.name='Non-Color'\n        nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Roughness'])")
t=t.replace("(80,130,-130)","(80,88,-130)").replace("(42,121,-302),(-12,111,-299),85","(65,131,-245),(0,73,-296),75").replace("(75,18,545),(55,30,410),125","(115,55,560),(30,20,440),92").replace("(-900,172,180),85","(-900,217,100),70")
# Render-only spillway on downstream (south) face.
t=t.replace("def assets():",'''    mesh('Pass3 render-only downstream spillway', [[-10,108,-289.7],[10,108,-289.7],[10,19,-286],[-10,19,-286]],[(0,1,2,3)],foam)

def assets():''')
needle="        cam.location=rb(eye);"
t=t.replace(needle,'''        bearing,elevation=(277,2) if name=='sunset_arch_from_crown' else (270,25)
        br,el=math.radians(bearing),math.radians(elevation)
        direction=Vector((math.sin(br)*math.cos(el),math.cos(br)*math.cos(el),math.sin(el)))
        sun=next(o for o in sc.objects if o.type=='LIGHT' and o.data.type=='SUN')
        sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        disc=next(o for o in sc.objects if o.name.startswith('Sun disc:'))
        disc.location=rb(eye)+direction*2500;disc.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        if name=='sunset_arch_from_crown':
            for obj in sc.objects:
                if obj.name.startswith('Heightmap terrain') or obj.name.startswith('rim_silhouette_') or obj.name.startswith('sunset_arch_'):obj.hide_render=True
            log('Crown render-only exclusions: heightmap terrain, rim silhouettes, near sunset_arch; reveal far arch without moving world pieces')
''' + needle)
t=t.replace("'sun':{'bearing':277,'elevation':-3}","'sun':{'bearing':270,'elevation':25,'arch_bearing':277,'arch_elevation':2}")
p.write_text(t)
man=json.loads(Path('manifest.json').read_text());ids=[p['id'] for p in man['pieces'] if 'Strata' in p['materials'] or any(x in p['materials'] for x in ['CardMesa','CardButte','CardArch','CardTwins'])];(s/'pass3_changed_ids.txt').write_text(','.join(ids))
