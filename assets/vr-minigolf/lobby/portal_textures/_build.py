import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob
N=1024; t=np.linspace(0,2*np.pi,N,endpoint=False); X,Y=np.meshgrid(t,t)
def field(seed,oct=6):
    r=np.random.default_rng(seed); f=np.zeros((N,N))
    for k in range(oct):
        for _ in range(4):
            a,b=r.integers(-(k+1),k+2,2)
            if a==0 and b==0: continue
            f+=np.sin(a*X+b*Y+r.uniform(0,6.28))/(k+1)
    return f
def warp(seed,ribbon=False):
    # domain warp with integer-frequency periodic offsets -> seamless
    w1=field(seed); w2=field(seed+1)
    u=X+0.9*w1/3; v=Y+0.9*w2/3
    if ribbon: s=np.sin(3*v+2*np.sin(u)+w1*0.6)   # vertical-ish bands
    else: s=np.sin(2*u+3*np.sin(v+np.sin(2*u)))*np.cos(2*v-np.sin(u))+0.5*np.sin(4*u+w2)
    s=(s-s.min())/(s.max()-s.min())
    return s
def colorize(s,stops):
    xs=[p for p,_ in stops]; out=np.zeros((N,N,3))
    for c in range(3): out[...,c]=np.interp(s,xs,[col[c] for _,col in stops])
    return out
H=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
sets={
 'portal_lantern_grove':(11,False,[(0,H('#3A1A08')),(.35,H('#C9473A')),(.6,H('#E58A3A')),(.82,H('#FFC867')),(1,H('#FFF6D8'))]),
 'portal_sugarloaf':(23,False,[(0,H('#5A1E3A')),(.35,H('#D9714A')),(.6,H('#F6A6C8')),(.82,H('#F2C9A0')),(1,H('#FFF4EC'))]),
 'portal_aurora':(37,True,[(0,H('#0B1030')),(.3,H('#4A2C9B')),(.5,H('#9B6BFF')),(.7,H('#2FB3A0')),(.86,H('#5BE3A0')),(1,H('#E8FFF6'))]),
}
outs=[]
for name,(seed,rib,stops) in sets.items():
    s=warp(seed,rib); s=s**1.3  # cores small and bright
    img=Image.fromarray(colorize(s,stops).clip(0,255).astype(np.uint8))
    # wrap-safe soft blur: tile 3x3, blur, crop center
    big=Image.new('RGB',(3*N,3*N))
    for i in range(3):
        for j in range(3): big.paste(img,(i*N,j*N))
    img=big.filter(ImageFilter.GaussianBlur(3)).crop((N,N,2*N,2*N))
    img.save(name+'.png'); outs.append((name,img))
# rim glow 512 transparent: soft rounded-rect ring
R=512; a=Image.new('L',(R,R),0); d=ImageDraw.Draw(a)
d.rounded_rectangle([40,40,R-41,R-41],60,outline=255,width=26)
a=a.filter(ImageFilter.GaussianBlur(22)); arr=np.array(a,float); arr=(arr/arr.max()*110)
rim=Image.new('RGBA',(R,R),(255,244,220,0)); rim.putalpha(Image.fromarray(arr.astype(np.uint8))); rim.save('portal_rim_glow.png')
# preview: each texture tiled 2x2 (seam check) + rim over dark
F=ImageFont.truetype(glob.glob('/usr/share/fonts/truetype/sand-box/google/Lilita One/*.ttf')[0],28)
P=Image.new('RGB',(4*530+10,620),(25,25,30)); dr=ImageDraw.Draw(P)
for k,(n,im) in enumerate(outs):
    t2=Image.new('RGB',(2*N,2*N)); [t2.paste(im,(i*N,j*N)) for i in range(2) for j in range(2)]
    P.paste(t2.resize((512,512)),(10+k*530,60)); dr.text((10+k*530,15),n+' (2x2 tiled)',font=F,fill=(255,230,170))
bg=Image.new('RGBA',(512,512),(40,30,60,255)); bg.alpha_composite(rim); P.paste(bg.convert('RGB'),(10+3*530,60))
dr.text((10+3*530,15),'portal_rim_glow',font=F,fill=(255,230,170)); P.save('preview_sheet.jpg',quality=90)
