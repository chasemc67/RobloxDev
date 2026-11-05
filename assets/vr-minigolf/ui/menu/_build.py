import numpy as np, glob, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
WOOD,DARK,POST=H('#B5835A'),H('#7A4E2D'),H('#8A5A34')
BR,BRH,BRS=H('#C9A04A'),H('#E8C979'),H('#8C6A2A')
PARCH,INK=H('#F1E2BE'),H('#4A2F1A')
W,Hh,C,B=1200,800,64,44   # border band 44px inside 64px slice
rng=np.random.default_rng(3)
def band(n):  # per-row grain profile across band thickness
    p=np.ones(n); p+= rng.normal(0,.06,n); p[::11]*=.78; return np.clip(p,.6,1.2)
prof=band(B)
img=np.zeros((Hh,W,4),np.float32)
yy,xx=np.mgrid[0:Hh,0:W]
d=np.minimum.reduce([xx,yy,W-1-xx,Hh-1-yy])  # distance to edge
# which edge is nearest -> grain profile index = d
inb=d<B
col=np.array(WOOD,np.float32)*prof[np.clip(d,0,B-1)][...,None]
# shading: lighter outer, darker inner
sh=1-0.25*(d/B)
col=col*sh[...,None]
img[inb,:3]=col[inb]; img[inb,3]=255
# outer dark rim 4px and brass trim at 36-44
rim=d<4; img[rim,:3]=DARK
br=(d>=B-9)&(d<B-3); img[br,:3]=BR
brh=(d==B-9); img[brh,:3]=BRH
brs=(d>=B-3)&(d<B); img[brs,:3]=BRS
# miter line at corners
m=(inb)&((np.abs(xx-yy)<1.2)|(np.abs((W-1-xx)-yy)<1.2)|(np.abs(xx-(Hh-1-yy))<1.2)|(np.abs((W-1-xx)-(Hh-1-yy))<1.2))&(d>=4)&(d<B-9)&(np.minimum(xx,W-1-xx)<C)&(np.minimum(yy,Hh-1-yy)<C)
img[m,:3]=DARK
# center fill parchment semi-opaque
cen=~inb; img[cen,:3]=PARCH; img[cen,3]=235
im=Image.fromarray(img.clip(0,255).astype(np.uint8),'RGBA')
# rounded outer corners (radius 18) and brass corner rivets inside 64px corners
mask=Image.new('L',(W,Hh),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,W-1,Hh-1],18,fill=255)
a=np.array(im); a[...,3]=np.minimum(a[...,3],np.array(mask)); im=Image.fromarray(a)
dr=ImageDraw.Draw(im)
for cx,cy in [(20,20),(W-21,20),(20,Hh-21),(W-21,Hh-21)]:
    dr.ellipse([cx-11,cy-11,cx+11,cy+11],fill=BRS); dr.ellipse([cx-9,cy-10,cx+8,cy+7],fill=BR); dr.ellipse([cx-6,cy-7,cx-1,cy-2],fill=BRH)
im.save('menu_frame.png')
def badge(draw_icon,name):
    S=512; b=Image.new('RGBA',(S,S),(0,0,0,0)); g=ImageDraw.Draw(b)
    g.ellipse([16,28,S-16,S-4],fill=(40,22,10,110))  # shadow
    g.ellipse([16,12,S-16,S-20],fill=DARK)
    g.ellipse([34,30,S-34,S-38],fill=BR); g.ellipse([46,42,S-46,S-50],fill=BRS)
    g.ellipse([54,50,S-54,S-58],fill=WOOD)
    for y in range(80,S-80,46): g.line([(70,y),(S-70,y)],fill=POST,width=6)
    inner=Image.new('L',(S,S),0); ImageDraw.Draw(inner).ellipse([54,50,S-54,S-58],fill=255)
    bg=b.copy(); g2=ImageDraw.Draw(b)
    draw_icon(g2,S)
    b=b.resize((128,128),Image.LANCZOS); b.save(name)
def xicon(g,S):
    c=S//2;o=100
    for col,w,dy in [(DARK,96,8),(PARCH,64,0)]:
        g.line([(c-o,c-o-4+dy),(c+o,c+o-4+dy)],fill=col,width=w); g.line([(c+o,c-o-4+dy),(c-o,c+o-4+dy)],fill=col,width=w)
def flag(g,S):
    # bold hamburger: 3 parchment bars with dark outline
    for y in (170,246,322):
        g.rounded_rectangle([140,y-30,372,y+30],30,fill=DARK)
        g.rounded_rectangle([150,y-21,362,y+21],21,fill=PARCH)
badge(xicon,'close_x.png'); badge(flag,'menu_button.png')
# preview
F=glob.glob('/usr/share/fonts/truetype/sand-box/google/Lilita One/*.ttf')[0]
def nine(src,w,h,c=C):
    s=Image.open(src); sw,shh=s.size; o=Image.new('RGBA',(w,h))
    xs=[(0,c,0,c),(c,sw-c,c,w-c),(sw-c,sw,w-c,w)]; ys=[(0,c,0,c),(c,shh-c,c,h-c),(shh-c,shh,h-c,h)]
    for a0,a1,b0,b1 in xs:
        for c0,c1,d0,d1 in ys:
            o.paste(s.crop((a0,c0,a1,c1)).resize((b1-b0,d1-d0)),(b0,d0))
    return o
P=Image.new('RGB',(2700,1400),H('#3E8FB0')); 
for i,(w,h) in enumerate([(1600,900),(900,1200)]):
    f=nine('menu_frame.png',w,h); d=ImageDraw.Draw(f)
    d.text((90,90),"Settings",font=ImageFont.truetype(F,80),fill=INK)
    d.text((90,200),"Music volume\nPVP mode: Peaceful\nLeaderboards",font=ImageFont.truetype(F,48),fill=INK,spacing=24)
    for k,ic in enumerate(['close_x.png','menu_button.png']):
        f.alpha_composite(Image.open(ic).resize((64,64),Image.LANCZOS),(w-90-80*k,80))
    P.paste(f,(50+i*1700,50),f)
D=ImageDraw.Draw(P); D.text((1700,1300),"icons @64px:",font=ImageFont.truetype(F,40),fill=(255,255,255))
P.paste(Image.open('close_x.png').resize((64,64)),(1960,1290),Image.open('close_x.png').resize((64,64)))
P.paste(Image.open('menu_button.png').resize((64,64)),(2040,1290),Image.open('menu_button.png').resize((64,64)))
P.save('menu_preview.png')
