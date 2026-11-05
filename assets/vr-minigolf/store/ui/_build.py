import numpy as np, os
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, ImageEnhance
U='/workspace/RobloxDev/assets/vr-minigolf/store/ui'; R=U+'/_raw'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=lambda s: ImageFont.truetype(FB,s) if os.path.exists(FB) else ImageFont.load_default(s)
# logos
for n in ['L1','L2','L3']:
    a=np.asarray(Image.open(f'{R}/{n}.png').convert('RGB')).astype(float)
    r,g,b=a[...,0],a[...,1],a[...,2]
    m=np.clip((np.minimum(r,b)-g)/255,0,1)            # magenta-ness
    alpha=np.clip(1-(m-0.25)/0.45,0,1)                 # soft edge
    # despill: pull magenta out of edge pixels
    sp=np.minimum(r,b)-g; fix=np.clip(sp,0,None)*(1-alpha)
    out=a.copy(); out[...,0]-=fix; out[...,2]-=fix
    rgba=np.dstack([np.clip(out,0,255),alpha*255]).astype(np.uint8)
    im=Image.fromarray(rgba,'RGBA'); bb=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox(); im=im.crop(bb)
    im.thumbnail((2048-96,768-64),Image.LANCZOS); c=Image.new('RGBA',(2048,768),(0,0,0,0)); c.paste(im,((2048-im.width)//2,(768-im.height)//2),im)
    c.save(f'{U}/{n}_logo.png')
    A=np.asarray(c)[...,3]; print(n,c.size,'transparent%',round((A==0).mean()*100,1),'partial%',round(((A>0)&(A<255)).mean()*100,2))
    # check on dark+light bg
# cards
def tag(im,text):
    d=ImageDraw.Draw(im); f=font(84); w=d.textlength(text,font=f)
    ov=Image.new('RGBA',im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle(((1024-w)/2-40,840,(1024+w)/2+40,960),30,fill=(20,20,28,215),outline=(255,200,110,255),width=5)
    im=Image.alpha_composite(im.convert('RGBA'),ov); ImageDraw.Draw(im).text((512,900),text,font=f,fill=(255,225,160),anchor='mm'); return im.convert('RGB')
for src,name in [('C_LG1','card_lanterngrove_A'),('C_LG2','card_lanterngrove_B')]:
    ImageOps.fit(Image.open(f'{R}/{src}.png').convert('RGB'),(1024,1024),Image.LANCZOS).save(f'{U}/{name}.png')
for src,name in [('C_CC','card_soon_sugarloafcanyon'),('C_FF','card_soon_auroraarchipelago')]:
    im=ImageOps.fit(Image.open(f'{R}/{src}.png').convert('RGB'),(1024,1024),Image.LANCZOS)
    im.save(f'{U}/{name}_color_clean.png')
    gr=ImageEnhance.Brightness(ImageOps.grayscale(im).convert('RGB')).enhance(0.55)
    gr=Image.blend(gr,Image.new('RGB',gr.size,(40,44,60)),0.25); gr.save(f'{U}/{name}_grey_clean.png')
    tag(gr,'COMING SOON').save(f'{U}/{name}_grey_tag.png')
ImageOps.fit(Image.open(f'{R}/BG.png').convert('RGB'),(1920,1080),Image.LANCZOS).save(f'{U}/title_bg.png')
# sheet
items=[(f'{n}_logo.png',n) for n in ['L1','L2','L3']]
s=Image.new('RGB',(3*700+80,2*260+60+3*(260+60)+20),'#333'); d=ImageDraw.Draw(s); f=font(30)
for i,(fn,l) in enumerate(items):
    lg=Image.open(f'{U}/{fn}').resize((680,255),Image.LANCZOS)
    for j,bgc in enumerate([(25,30,45),(230,230,230)]):
        x=20+i*700; y=50+j*270; t=Image.new('RGB',(680,255),bgc)
        chk=Image.new('RGB',(680,255)); 
        t.paste(lg,(0,0),lg); s.paste(t,(x,y))
    d.text((20+i*700,10),l+' (on dark / light = alpha check)',fill='white',font=f)
cards=['card_lanterngrove_A','card_lanterngrove_B','card_soon_sugarloafcanyon_color_clean','card_soon_sugarloafcanyon_grey_clean','card_soon_sugarloafcanyon_grey_tag','card_soon_auroraarchipelago_color_clean','card_soon_auroraarchipelago_grey_clean','card_soon_auroraarchipelago_grey_tag','title_bg']
lab=['C1 LG-A','C2 LG-B','C3 Canyon color','C3 grey clean','C3 grey tag','C4 Aurora color','C4 grey clean','C4 grey tag','BG title']
y0=600
for k,(c,l) in enumerate(zip(cards,lab)):
    im=Image.open(f'{U}/{c}.png'); im.thumbnail((420 if c!='title_bg' else 460,260))
    x=20+(k%5)*430; y=y0+(k//5)*320; s.paste(im,(x,y+40)); d.text((x,y),l,fill='white',font=f)
s=s.crop((0,0,s.width,y0+640)); s.save(f'{U}/ui_sheet.jpg',quality=88)
