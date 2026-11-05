"""Pass5b review artifacts (system Python + Pillow, no Blender):
V1-hub-tee1_vs_concept.png, regenerated contact_sheet.png (gondola pieces included), pass5b_render_report.json."""
import json, math, time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
SRC=Path(__file__).resolve().parent; MODELS=SRC.parent; COURSE=MODELS.parent; HERO=MODELS/'previews/hero'
fontpath=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(fontpath),20) if fontpath.exists() else ImageFont.load_default()
small=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default()

def log(s):
    line=time.strftime('%Y-%m-%d %H:%M:%S')+' '+s; print(line)
    with (SRC/'PROGRESS.md').open('a') as f: f.write(line+'\n')

def compare():
    # Same layout as compare_vs_vistas.png rows: render left, concept right, label bar under each.
    render=Image.open(HERO/'V1-hub-tee1_staged.png').convert('RGB').resize((960,540))
    concept=Image.open(COURSE/'world/vistas/V1-hub-tee1.png').convert('RGB').resize((960,540))
    sheet=Image.new('RGB',(1920,580),'#211a21'); d=ImageDraw.Draw(sheet)
    sheet.paste(render,(0,0)); sheet.paste(concept,(960,0))
    d.text((14,548),'V1-hub-tee1 staged render (Cycles OptiX 128 spp, pass 5b)',font=font,fill='#ffe7cc')
    d.text((974,548),'V1-hub-tee1 concept (world/vistas/V1-hub-tee1.png)',font=font,fill='#ffe7cc')
    sheet.save(HERO/'V1-hub-tee1_vs_concept.png')

def contact():
    man=json.loads((MODELS/'manifest.json').read_text())
    old=Image.open(MODELS/'contact_sheet.png').convert('RGB')
    hero=old.crop((0,0,1600,1520))  # pass3/4 hero block kept as-is
    previews=[]
    for p in man['pieces']:
        candidates=[MODELS/s.replace('\\','/') for s in p.get('previews',[]) if (MODELS/s.replace('\\','/')).exists()]
        if not candidates: candidates=sorted((MODELS/'previews').glob(p['id']+'_*.png'))
        if candidates: previews.append((p['id'],candidates[-1],p['tris']))
    root=Image.new('RGB',(1600,1520+math.ceil(len(previews)/5)*218),'#211a21'); root.paste(hero,(0,0)); d=ImageDraw.Draw(root)
    for k,(name,path,t) in enumerate(previews):
        x=(k%5)*320;y=1520+(k//5)*218
        thumb=ImageOps.contain(Image.open(path).convert('RGB'),(316,188)); root.paste(thumb,(x+(320-thumb.width)//2,y))
        d.text((x+6,y+191),f'{name} / {t:,} tris',font=small,fill='#ffe7cc')
    root.save(MODELS/'contact_sheet.png')
    return len(previews),[n for n,_,_ in previews if n.startswith('gondola')],root.size

def report():
    # The V1 final re-render rewrote the report with only its own record; restore the gondola_span record from the same run settings.
    r=json.loads((HERO/'pass5b_render_report.json').read_text())
    if not any(x['shot']=='gondola_span' for x in r['renders']):
        r['renders'].append({'shot':'gondola_span','path':'previews/gondola_span.png','samples':128,'seconds':11.4,'eye':[246.0,400.0,-184.0],'target':[-145.0,80.0,335.0],'fov_horizontal':65,'key_sun':[277,22],'rim':[300,10],'note':'rendered 2026-10-12 10:24:51 (pass5b_preview3.log run; args joined -> full quality)'})
    r['compare']='previews/hero/V1-hub-tee1_vs_concept.png'
    (HERO/'pass5b_render_report.json').write_text(json.dumps(r,indent=2))

if __name__=='__main__':
    for p in (HERO/'V1-hub-tee1_staged.png',MODELS/'previews/gondola_span.png'):
        with Image.open(p) as im: assert im.size==(1920,1080),(p,im.size); print(p.name,im.info.get('cycles.ViewLayer.samples'))
    compare(); n,g,size=contact(); report()
    log(f'Pass5b finalize: V1-hub-tee1_vs_concept.png written; contact_sheet.png regenerated {size} with {n} piece thumbnails incl {g}; pass5b_render_report.json')
