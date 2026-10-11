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
for n,arr in [('A',A),('B',B)]:
    t=np.tile(arr,(2,2,1)); Image.fromarray(t).save(f'{T}/slope_felt_{n}_tile2x2.png')
    # seam metric: edge diff vs interior adjacent diff
    e=np.abs(arr[0].astype(int)-arr[-1].astype(int)).mean(); e2=np.abs(arr[:,0].astype(int)-arr[:,-1].astype(int)).mean()
    i=np.abs(arr[1:].astype(int)-arr[:-1].astype(int)).mean(); print(n,'seam V',round(e,2),'seam U',round(e2,2),'interior',round(i,2))
s=Image.new('RGB',(3*540+20,540+580+40),'#222'); d=ImageDraw.Draw(s)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
except: f=ImageFont.load_default()
row=[('flat felt.png (current)',Image.open(F).convert('RGB')),('slope_felt_A  (arrows = +V downhill)',Image.fromarray(A)),('slope_felt_B',Image.fromarray(B))]
for i,(l,im) in enumerate(row): s.paste(im,(20+i*540,50)); d.text((20+i*540,12),l,fill='white',font=f)
for i,n in enumerate(['A','B']):
    im=Image.open(f'{T}/slope_felt_{n}_tile2x2.png').resize((512,512)); s.paste(im,(20+(i+1)*540,620)); d.text((20+(i+1)*540,582),f'{n} 2x2 tile check',fill='white',font=f)
d.text((20,620),'V+ (downhill) ->  down the image',fill='white',font=f)
s.save(T+'/slope_sheet.jpg',quality=90)
