import numpy as np
from PIL import Image, ImageDraw, ImageFont
T='/workspace/RobloxDev/assets/vr-minigolf/lantern-grove/textures'; F=T+'/../models/textures/felt.png'
felt=np.asarray(Image.open(F).convert('RGB')).astype(float)
N=512; y,x=np.mgrid[0:N,0:N]/N   # v=y grows downward (+V)
def shade(mask,strength):  # mask 0..1 darkening, periodic
    m=mask[...,None]; return np.clip(felt*(1-strength*m),0,255).astype(np.uint8)
# A: chevrons pointing toward +V. 4 across, 4 down -> period 0.25 both ways (seamless)
px=4; py=4
u=(x*px)%1; tri=np.abs(u-0.5)          # 0 at column centre, .5 at edge
ph=(y*py + tri*0.9)%1                   # column centre sits lowest -> V tip points toward +V
band=np.clip(1-np.abs(ph-0.25)/0.09,0,1)**0.8
A=shade(band,0.28); Image.fromarray(A).save(T+'/slope_felt_A.png')
# B: sawtooth stripes: dark sharp edge on downhill side, fading uphill + small chevron notch
ph2=(y*6 + tri*0.35)%1
saw=np.where(ph2<0.8,ph2/0.8,np.clip((1-ph2)/0.2,0,1))**2.2
B=shade(saw,0.26); Image.fromarray(B).save(T+'/slope_felt_B.png')

# C: strictly one-directional arrowheads. Per 128px cell: sharp bright leading V edge at the +V tip,
# dark fill behind it with a long gradient tail fading upslope (-V). Front of the edge stays plain felt.
cu=(x*4)%1; cv=(y*4)%1; half=np.abs(cu-0.5)
d=cv-(0.62-half*0.75)                      # 0 on the leading V edge (tip at cell centre, lowest), <0 behind (upslope)
d=(d+0.5)%1-0.5                            # wrap so tails continue across cells seamlessly
wmask=np.clip((0.42-half)/0.06,0,1)        # arrowhead width, soft sides
tail=np.where(d<0,np.exp(d/0.22),0)*wmask  # long fade upslope
edge=np.clip(1-np.abs(d+0.012)/0.018,0,1)*wmask   # sharp bright tip line
C=felt*(1-0.42*tail[...,None]); C=C+edge[...,None]*np.array([95,120,60])
C=np.clip(C,0,255).astype(np.uint8); Image.fromarray(C).save(T+'/slope_felt_C.png')
for n,arr in [('A',A),('B',B),('C',C)]:
    t=np.tile(arr,(2,2,1)); Image.fromarray(t).save(f'{T}/slope_felt_{n}_tile2x2.png')
    # seam metric: edge diff vs interior adjacent diff
    e=np.abs(arr[0].astype(int)-arr[-1].astype(int)).mean(); e2=np.abs(arr[:,0].astype(int)-arr[:,-1].astype(int)).mean()
    i=np.abs(arr[1:].astype(int)-arr[:-1].astype(int)).mean(); print(n,'seam V',round(e,2),'seam U',round(e2,2),'interior',round(i,2))
s=Image.new('RGB',(4*540+20,540+580+40),'#222'); d=ImageDraw.Draw(s)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
except: f=ImageFont.load_default()
row=[('flat felt.png (current)',Image.open(F).convert('RGB')),('slope_felt_A  (arrows = +V downhill)',Image.fromarray(A)),('slope_felt_B',Image.fromarray(B)),('slope_felt_C (one-way, tip = +V)',Image.fromarray(C))]
for i,(l,im) in enumerate(row): s.paste(im,(20+i*540,50)); d.text((20+i*540,12),l,fill='white',font=f)
for i,n in enumerate(['A','B','C']):
    im=Image.open(f'{T}/slope_felt_{n}_tile2x2.png').resize((512,512)); s.paste(im,(20+(i+1)*540,620)); d.text((20+(i+1)*540,582),f'{n} 2x2 tile check',fill='white',font=f)
d.text((20,620),'V+ (downhill) ->  down the image',fill='white',font=f)
s.save(T+'/slope_sheet.jpg',quality=90)

# tilted-plane test render with downhill arrow
def coeffs(dst,src):
    M=[];B=[]
    for (X,Y),(u,v) in zip(dst,src):
        M+= [[X,Y,1,0,0,0,-u*X,-u*Y],[0,0,0,X,Y,1,-v*X,-v*Y]]; B+=[u,v]
    return np.linalg.solve(np.array(M,float),np.array(B,float)).tolist()
tile=Image.open(T+'/slope_felt_C_tile2x2.png')
W,H=1280,720; dst=[(470,90),(810,90),(1180,690),(100,690)]   # far(top)=uphill, near(bottom)=downhill
r=Image.new('RGB',(W,H),(30,34,48)); pl=tile.transform((W,H),Image.PERSPECTIVE,coeffs(dst,[(0,0),(1024,0),(1024,1024),(0,1024)]),Image.BICUBIC)
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(dst,fill=255); r.paste(pl,(0,0),m)
dd=ImageDraw.Draw(r); dd.line([(1230,140),(1230,620)],fill=(255,200,60),width=10); dd.polygon([(1205,600),(1255,600),(1230,660)],fill=(255,200,60))
dd.text((20,20),'slope_felt_C: far = uphill (V=0), near = downhill (+V); yellow arrow = downhill',fill='white',font=f)
r.save(T+'/slope_felt_C_test_render.png')
