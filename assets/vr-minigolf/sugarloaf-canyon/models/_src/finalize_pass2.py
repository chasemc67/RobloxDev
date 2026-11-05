"""Update review artifacts after successful hero render and fitcheck."""
import json, math, time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
SRC=Path(__file__).resolve().parent; MODELS=SRC.parent
def main():
    man=json.loads((MODELS/'manifest.json').read_text()); lay=json.loads((MODELS/'layout.json').read_text())
    report=json.loads((MODELS/'previews/hero/render_report.json').read_text()); p2=lay['pass2']
    assert report['resolution']==[1920,1080] and len(report['renders'])==6
    assert report['renders'][-1]['shot']=='sunset_arch_from_crown'
    assert 'RESULT: ALL PASS' in (SRC/'fitcheck_pass2_validated.txt').read_text()
    for r in report['renders']:
        with Image.open(MODELS/r['path']) as im:
            assert im.size==(1920,1080)
            assert im.info.get('cycles.ViewLayer.samples')=='128'
    lookup={p['id']:p for p in man['pieces']}
    for p in man['pieces']:
        p['instances']=[{k:i[k] for k in ('pos','yaw','scale','src','note') if k in i} for i in lay['instances'] if i['piece']==p['id']]
        p['previews']=[s.replace('\\','/') for s in p['previews']]
    tris=sum(lookup[i['piece']]['tris'] for i in lay['instances'])
    man['generated']=time.strftime('%Y-%m-%d %H:%M:%S')
    man['totals'].update(placed_triangles=tris,library_triangles=sum(p['tris'] for p in man['pieces']),max_mesh_triangles=max(p['max_mesh_tris'] for p in man['pieces']))
    man['pass2']={'rim_stretches':p2['rim_covered'],'rim_triangles':p2['rim_covered']*lookup['rim_silhouette']['tris'],'scatter_removed':p2['removed_unique'],'removed_per_hole':p2['removed_per_hole'],'rebuilt_fbx':['fbx/rim_silhouette.fbx'],'fitcheck':'_src/fitcheck_pass2_validated.txt'}
    man['hero_renders']=report
    (MODELS/'manifest.json').write_text(json.dumps(man,indent=1))
    # Six labelled final shots, then the existing per-piece previews.
    fontpath=Path('C:/Windows/Fonts/segoeui.ttf')
    font=ImageFont.truetype(str(fontpath),20) if fontpath.exists() else ImageFont.load_default()
    small=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default()
    hero=Image.new('RGB',(1600,1520),'#211a21'); d=ImageDraw.Draw(hero)
    d.text((20,12),'SUGARLOAF CANYON  /  PASS 2  /  CYCLES OPTIX  /  128 SAMPLES',font=font,fill='#ffe7cc')
    for k,r in enumerate(report['renders']):
        x=(k%2)*800;y=52+(k//2)*488
        hero.paste(Image.open(MODELS/r['path']).convert('RGB').resize((800,450)),(x,y))
        d.text((x+14,y+458),r['shot'].replace('_',' ').title(),font=font,fill='#ffe7cc')
    hero.save(MODELS/'previews/hero/contact_sheet.png')
    previews=[]
    for p in man['pieces']:
        candidates=[MODELS/s for s in p['previews'] if (MODELS/s).exists()]
        if not candidates:
            candidates=list((MODELS/'previews').glob(p['id']+'_*.png'))
        if candidates: previews.append((p['id'],candidates[-1],p['tris']))
    root=Image.new('RGB',(1600,1520+math.ceil(len(previews)/5)*218),'#211a21'); root.paste(hero,(0,0)); d=ImageDraw.Draw(root)
    for k,(name,path,t) in enumerate(previews):
        x=(k%5)*320;y=1520+(k//5)*218
        thumb=ImageOps.contain(Image.open(path).convert('RGB'),(316,188)); root.paste(thumb,(x+(320-thumb.width)//2,y))
        d.text((x+6,y+191),f'{name} / {t:,} tris',font=small,fill='#ffe7cc')
    root.save(MODELS/'contact_sheet.png')
    rows='\n'.join(f"| [{r['shot']}](../{r['path']}) | {r['samples']} | {r['seconds']:.2f} s |" for r in report['renders'])
    summary=f'''# SRV-131 pass 2: completed on Windows

100 pieces / 105 FBX / 818 placed instances / {tris:,} placed triangles. Library: {man['totals']['library_triangles']:,} triangles; max mesh {man['totals']['max_mesh_triangles']:,} (<20k). Added one 12-triangle rim asset, 80 placements, 960 placed triangles. Existing FBX files were retained; only `fbx/rim_silhouette.fbx` was built in Blender 5.2.2 LTS.

## A. Visible outer rim

80 of 80 candidate 64-stud stretches were visible from at least one of 363 tee/walkway observer samples (eyes +5). Crest visibility tests sampled endpoints/centre and traced the 16-bit heightfield at <=2-stud intervals. Walkway observer spacing <=16 studs. Full per-stretch observer evidence: `layout.json pass2.rim_coverage`. Added short low-poly striped silhouette blades, buried 12 studs beneath the sampled crest, with irregular tops; CastShadow false. No outer rim cliff kit. Existing interior cliff kit retained.

## B. Scatter sightlines

Checked every member in all six scatter clusters, using final holes.json world_offset/world_yaw and the specified transform, tee eye +5 to cup+7.5 and cup+1, with a 1.5-stud corridor. Conservative seed-expanded variant bounds and an independent final exported triangle-bounds check both found zero intersections. Removed counts: H1-H18 **0 each**; unique removals **0**. Existing footprint keep-outs already clear these lines. No scatter FBX rebuild was required. Stable member seeds are stored for reproducible future filtering.

## C. Validation and artifacts

`sc_fitcheck.py`: **ALL PASS**; results in [fitcheck_pass2_validated.txt](fitcheck_pass2_validated.txt). All 18 footprints clear >=2 studs (minimum 2.10); all 71 walkway segments clear (minimum overhead 9.25); all 36 scatter sightline corridors clear. Far cards + sky including rim: 2,598 placed triangles, CastShadow off. The original H3 rail/footbridge conservative lower-bound note (2.9 studs) remains in pass1 validation.

Updated layout assumptions/counts, manifest placements/totals, README, contact_sheet.png, and reproducible pass2 rules integrated into sc_layout.py. Fixed deprecated material blend API access for Blender 5.2. Paths resolve from script directories. NumPy, Pillow and Matplotlib are installed in system Python; Blender supplies bpy/NumPy. The Windows launcher checks Get-Process blender before each launch, waits/polls 60 seconds if occupied, launches hidden, and waits for exit. No SSH or external messages.

## D. Hero stills

Cycles / OptiX / NVIDIA GeForce RTX 4090 / denoise / 1920x1080 / 128 samples. Terrain from the 16-bit source heightmap, sampled every 2 studs with boundary vertices at -640..640; y=gray/65535*260. Brown-sugar sand, peach mesa sand and six-band sandstone follow course.md. Water/lake/stream/fall surfaces use world.json levels. All placed FBX assets are assembled as shared instances. Render-only cards use geometric alpha cutouts and native node materials. Vista omits distant cards/clouds; Crown omits overlapping mesa/butte cards. Warm rose/tangerine sky and bounce illumination keep below-horizon dusk readable.

Sun lamp and disc: **hardcoded compass bearing 277°, elevation -3°**; world.json sun is ignored. The disc is on that ray from Crown (-370,196,165), 2,500 studs away. Terrain and rim can obscure the below-horizon disc in the Crown shot; near Sunset Arch and the far arch retain their source placements. Source spillway/deck geometry similarly obscures portions of the waterfall from crest eye height. No scene geometry was moved to force visibility.

Render script: [render_hero.py](render_hero.py). Packed reusable scene: [sugarloaf_canyon_hero.blend](../previews/hero/sugarloaf_canyon_hero.blend). Shot definitions are stored in the scene; `--reuse` reloads it. All six images were visually inspected; PNG metadata independently confirms Cycles 128 samples. Final render order ends with sunset_arch_from_crown. No flythrough.

| Render | Samples | Render time |
|---|---:|---:|
{rows}

Scene assembly plus final six renders: {report['scene_and_render_seconds']:.2f} s; rendering total {sum(r['seconds'] for r in report['renders']):.2f} s. Detailed eyes/targets/FOV/timings in [render_report.json](../previews/hero/render_report.json). [Hero contact sheet](../previews/hero/contact_sheet.png); [full piece and hero contact sheet](../contact_sheet.png).

Reproduce from models directory:
```powershell
python _src/pass2_rules.py
& _src/run_blender.ps1 -Script _src/sc_build.py -ScriptArgs '--only','rim_silhouette' -Log build_pass2.log
python _src/sc_fitcheck.py
& _src/run_blender.ps1 -Script _src/render_hero.py -Log hero_final.log
python _src/finalize_pass2.py
```
'''
    # Segment count is taken from validated report, rather than assumed.
    import re
    fit=(SRC/'fitcheck_pass2_validated.txt').read_text()
    n=re.search(r'(\d+) walkway segments checked',fit).group(1)
    summary=summary.replace('all 71 walkway segments',f'all {n} walkway segments')
    (SRC/'pass2_summary.md').write_text(summary,encoding='utf-8')
    readme=(MODELS/'README.md').read_text(encoding='utf-8').replace('(SRV-131, pass 1)','(SRV-131, pass 2)')
    if '## Pass 2' in readme: readme=readme.split('## Pass 2')[0]
    readme+='''\n## Pass 2 (Windows, Blender 5.2)\n\n100 pieces, 105 FBX, 818 placements, 309,074 placed triangles. Added 80 visibility-tested low-poly outer-rim silhouettes (960 triangles); set CastShadow off. All 18 holes already clear both scatter sightline corridors, so no scatter removals. Validation: [_src/fitcheck_pass2_validated.txt](_src/fitcheck_pass2_validated.txt), ALL PASS.\n\nSix 1920x1080 Cycles OptiX hero stills (128 samples, denoised): [previews/hero/contact_sheet.png](previews/hero/contact_sheet.png). Reusable packed [hero scene](previews/hero/sugarloaf_canyon_hero.blend), [_src/render_hero.py](_src/render_hero.py), and [render details](previews/hero/render_report.json). Hardcoded dusk sun: bearing 277°, elevation -3°. Crown sunset shot rendered last.\n\nUse [_src/run_blender.ps1](_src/run_blender.ps1) for every Blender launch; it waits for existing Blender jobs. Full changes, counts, paths, timings and scene visibility notes: [_src/pass2_summary.md](_src/pass2_summary.md).\n'''
    (MODELS/'README.md').write_text(readme,encoding='utf-8')
    with (SRC/'PROGRESS.md').open('a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S')+' Pass2 complete: ALL PASS, six final Cycles/OptiX PNG metadata checks (1920x1080, 128 samples), packed scene saved; manifest/layout/README/contact sheets/summary updated.\n')
    print('Finalized pass2 artifacts; all six PNG metadata checks passed.')
if __name__=='__main__': main()
