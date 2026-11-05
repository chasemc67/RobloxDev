from pathlib import Path
import json,time,math
from PIL import Image,ImageDraw,ImageFont
s=Path('_src');root=Path('.');out=root/'previews/hero'
report=json.loads((out/'render_report.json').read_text())
assert len(report['renders'])==6 and report['renders'][-1]['shot']=='sunset_arch_from_crown'
assert 'RESULT: ALL PASS' in (s/'fitcheck_pass3_validated.txt').read_text()
for r in report['renders']:
 im=Image.open(root/r['path']);assert im.size==(1920,1080) and im.info['cycles.ViewLayer.samples']=='128'
man=json.loads((root/'manifest.json').read_text());before=json.loads((s/'manifest_before_pass3.json').read_text());lay=json.loads((root/'layout.json').read_text());lookup={p['id']:p for p in man['pieces']}
tris=sum(lookup[i['piece']]['tris'] for i in lay['instances']);lib=sum(p['tris'] for p in man['pieces'])
profile={'base_center':[80,18,-130],'radius':72,'height':110,'width_height_ratio':144/110,'formula':'y=18+110*sqrt(max(0,1-(r/72)^4)), r<=72','terrain_patch':'Replace old dome inside radius72; retain source heights outside. Builder must patch heightmap; rendered terrain uses same formula.'}
changed=[f for p in man['pieces'] if p['id'] in (s/'pass3_changed_ids.txt').read_text().split(',') for f in p['files']]
p3={'profile':profile,'palette':['#E8C9A1','#C68C59','#CC8D91','#AF7061'],'band_widths':[4,10,6,16],'roughness_map':'textures/strata_roughness.png','rebuilt_fbx':changed,'fitcheck':'_src/fitcheck_pass3_validated.txt','review_iterations':1,'render_only_exclusions':'Arch: terrain and all placed collections except far_arch_card; camera eye lowered to170 to frame +2 degree sun inside opening. No world pieces moved.','render_only_water':'Downstream spillway sheet; no water FBX.'}
man['name']='Sugarloaf Canyon world pieces (pass 3)';man['pass3']=p3;man['hero_renders']=report;man['totals'].update(placed_triangles=tris,library_triangles=lib,max_mesh_triangles=max(p['max_mesh_tris'] for p in man['pieces']))
man['strata']='Vista palette deviation from course.md per Game Art Bot: cream, ochre, rose, muted terracotta; widths4/10/6/16 studs, soft edges; UV V=world y/36. SurfaceAppearance ColorMap textures/strata.png + RoughnessMap textures/strata_roughness.png; rose .48, others .84.'
lookup['old_sugarloaf_shell']['notes']=profile['formula']+'; 4 curved sectors + summit cactus, world-y bands.'
for p in man['pieces']:
 for part in p['parts']:
  for m in part['meshes']:
   if m['material']=='Strata':m['roughness_map']='textures/strata_roughness.png'
lay['pass3']=p3
(root/'manifest.json').write_text(json.dumps(man,indent=1));(root/'layout.json').write_text(json.dumps(lay,indent=1))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
hero=Image.new('RGB',(1600,1520),'#211a21');d=ImageDraw.Draw(hero);d.text((16,10),'SUGARLOAF CANYON / PASS 3 / CYCLES OPTIX / 128 SAMPLES',font=font,fill='white')
for k,r in enumerate(report['renders']):
 x=k%2*800;y=52+k//2*488;hero.paste(Image.open(root/r['path']).convert('RGB').resize((800,450)),(x,y));d.text((x+12,y+453),r['shot'],font=font,fill='white')
hero.save(out/'contact_sheet.png')
old=Image.open(root/'contact_sheet.png').convert('RGB');old.paste(hero,(0,0));old.save(root/'contact_sheet.png')
pairs=[('old_sugarloaf_skyline','V1-hub-tee1'),('narrows_crystal_walls','V2-slot-canyon'),('junction_town','V3-rope-bridge-mesa'),('sunset_arch_from_crown','V4-sunset-arch'),('dam_crest_walk','V4b-dam-reservoir')]
compare=Image.new('RGB',(1600,5*480),'#211a21');d=ImageDraw.Draw(compare)
for k,(n,v) in enumerate(pairs):
 for x,path in [(0,out/(n+'.png')),(800,Path('../world/vistas')/(v+'.png'))]:compare.paste(Image.open(path).convert('RGB').resize((800,450)),(x,k*480))
 d.text((12,k*480+450),n+'  |  Reference: '+v,font=font,fill='white')
compare.save(out/'compare_vs_vistas.png')
text=f'''# SRV-131 pass 3 completed on Windows

Steps 1-7 executed; fitcheck ALL PASS; six Cycles OptiX 1920x1080 / 128 sample renders, arch LAST. One self-review iteration corrected flat orange sky, warm ambient, dam occlusion and arch camera/sun alignment.

Palette deviation from course.md per Game Art Bot: cream #E8C9A1, ochre #C68C59, rose #CC8D91, muted terracotta #AF7061; 4/10/6/16 stud bands, blurred edges. Shared strata color map applies to all cliff/slot variants, rim, hoodoos, dome, arch, rocks/clusters; regenerated far-card textures. Roblox SurfaceAppearance: ColorMap + RoughnessMap; rose roughness .48, others .84.

Old Sugarloaf: base (80,18,-130), radius72, height110, width144/height110=1.309. Rounded dome with flattened top: {profile['formula']}. Replace old terrain heights inside radius72 with this formula; retain original outside. Render terrain already patched; builder must apply heightmap patch. Footprint and walkway clearance validated after export.

Golden-hour west key bearing270/elevation25; warm peach key, lavender ambient/fill, saturated sunset gradient. No global volumetric haze; distant cards retain baked atmospheric tint. Arch only: bearing277/elevation+2, eye(-370,170,165), target(-1250,155,60), FOV52. Render-only hide terrain and other placements to reveal far arch; no source pieces moved. Dam camera raised to show downstream sheet; Junction river visible.

Rebuilt {len(changed)} affected FBX across 63 pieces; other FBX retained. Placed tris {before['totals']['placed_triangles']:,} -> {tris:,} ({tris-before['totals']['placed_triangles']:+,}); library {before['totals']['library_triangles']:,} -> {lib:,}. Render-only terrain/card tessellation/water excluded from shipping totals.

Renders: '''+', '.join(r['path'] for r in report['renders'])+'''.
Contact: previews/hero/contact_sheet.png; comparison: previews/hero/compare_vs_vistas.png; packed scene: previews/hero/sugarloaf_canyon_hero.blend. Detailed cameras/timings: previews/hero/render_report.json.

Remaining gaps vs vistas: source layout is sparse and angular, without golf greens/per-hole props; cards are flat silhouettes, terrain and kit seams remain visible; spillway is a simple sheet without spray or foam detail. Vista illustrations have richer vegetation, clouds, surface detail and staged compositions. Palette/light improved within existing low-poly assets; not a full illustration match.
'''
(s/'pass3_summary.md').write_text(text)
readme=(root/'README.md').read_text();readme+='\n## Pass 3\n\n'+text.split('\n\n',1)[1]+'\n| Strata material | Vista colour | Roughness |\n|---|---|---|\n| Cream | #E8C9A1 | .84 |\n| Ochre | #C68C59 | .84 |\n| Rose | #CC8D91 | .48 |\n| Muted terracotta | #AF7061 | .84 |\n';(root/'README.md').write_text(readme)
with (s/'PROGRESS.md').open('a') as f:f.write(time.strftime('%Y-%m-%d %H:%M:%S')+' Pass3 steps3-7 complete: one review iteration, all six final metadata verified, ALL PASS, manifest/layout/README/counts/contact/compare/summary updated.\n')
print('Final artifacts verified')
