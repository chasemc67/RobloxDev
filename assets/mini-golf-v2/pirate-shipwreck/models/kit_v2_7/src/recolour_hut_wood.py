# kit_v2_7: PNG palette edit only (PIL). Hut texture = kit_v2_4 (== v2_5 == v2_6 == v2_6_1, md5 349ab76b...). Mesh untouched.
import json,numpy as np
from PIL import Image
T=np.array([120,82,50],float)
src='../kit_v2_4/kit_hut_leanto.png';dst='kit_hut_leanto.png'
pal=json.load(open('../kit_v2_4/work/palette.json'));names=list(pal)
im=np.array(Image.open(src).convert('RGB'))
cell=lambda n:(names.index(n)%8*32,names.index(n)//8*32)
def get(n): x,y=cell(n);return im[y+16,x+16].astype(float)
def put(n,c):
    x,y=cell(n);im[y:y+32,x:x+32]=np.clip(np.round(c),0,255).astype(np.uint8)
# post wood cells Wood1 (196 hut verts) and Wood2 (156): scale so their vertex-weighted mean = target
w1,w2=get('Wood1'),get('Wood2');mean=(w1*196+w2*156)/352;r=T/mean
out={'HutWoodDk':T}
for n in('Wood1','Wood2','Plank','PlankDk'): out[n]=get(n)*r
for n,c in out.items(): put(n,c)
Image.fromarray(im).save(dst,optimize=True);print('ratio',r,{n:np.round(c).tolist() for n,c in out.items()})
