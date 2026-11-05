from pathlib import Path
import json,shutil,time
s=Path('_src'); m=Path('.')
for n in ['manifest','layout']: shutil.copy2(m/(n+'.json'),s/(n+'_before_pass3.json'))
def edit(n,a,b):
 p=s/n;t=p.read_text();assert a in t,(n,a[:60]);p.write_text(t.replace(a,b))
edit('sc_pieces.py','peak, rad = 190.0, 72.0','peak, rad = 110.0, 72.0')
edit('sc_pieces.py','c = math.sqrt(max(0.0, min(1.0, (y - 18.0) / peak)))\n        return rad * (2 / math.pi) * math.acos(c)','t = max(0.0, min(1.0, (y - 18.0) / peak))\n        return rad * max(0.0, 1-t*t)**0.25')
edit('sc_pieces.py','band_rows(3.0, 189.6','band_rows(0.0, 109.9')
edit('sc_pieces.py','190.6)))','110.6)))')
edit('sc_pieces.py','T(0, 0, 189.8)','T(0, 0, 109.8)')
# Preserve extension keys (including concurrent movers) when building.
edit('sc_build.py','json.dump(man, open(mp, "w"), indent=1)','existing=json.load(open(mp)) if os.path.exists(mp) else {}\n    existing.update(man)\n    json.dump(existing, open(mp, "w"), indent=1)')
p=s/'sc_textures.py';t=p.read_text();start=t.index('def strata():');end=t.index('\ndef tinted',start)
t=t[:start]+'''BAND_WIDTHS = [4, 10, 6, 16]
STRATA = ['#E8C9A1','#C68C59','#CC8D91','#AF7061']
def strata():
    y,x=yy_xx(); v=1-(y+.5)/N
    band=np.searchsorted(np.cumsum(BAND_WIDTHS)/36,v,side='right')%4
    cols=np.stack([hexc(c) for c in STRATA])
    shade=1+(noise(12,beta=.8)-.5)*.08+(noise(13,beta=2.2)-.5)*.10
    im=Image.fromarray((np.clip(cols[band]*shade[...,None],0,1)*255).astype('uint8'))
    save('strata',im.filter(ImageFilter.GaussianBlur(2)))
    rough=np.where(band==2,.48,.84)
    save('strata_roughness',Image.fromarray((rough*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2)),mode='L')
''' + t[end:]
# cards share variable widths with muted haze confined to distant cards
start=t.index('def hazed_strata');print(t[start:start+600]);p.write_text(t)
with (s/'PROGRESS.md').open('a') as f:f.write(time.strftime('%Y-%m-%d %H:%M:%S')+' Pass3 steps 0-2: vistas reviewed; snapshots saved; cream/ochre/rose/terracotta maps and radius72 height110 rounded dome implemented.\n')
