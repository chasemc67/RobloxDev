# kit_v2_5: texture-only. Recolour the tan (Sandy, SandyDk) cells of cave_v2_2/cave_cliff_lower.png to rock (115,100,92).
import json,sys,hashlib,numpy as np
from PIL import Image
M='..'
src=M+'/../cave_v2_2/cave_cliff_lower.png';PAL=json.load(open(M+'/../cave_v2_2/work/palette.json'));names=list(PAL)
im=np.array(Image.open(src).convert('RGB'))
ROCK=(115,100,92);ch={}
for n in ('Sandy','SandyDk'):
    i=names.index(n);x,y=i%8,i//8;c=im[y*32:(y+1)*32,x*32:(x+1)*32]
    assert (c==np.array(PAL[n])).all();ch[n]=(i,PAL[n]);c[:]=ROCK
Image.fromarray(im).save(M+'/cave_cliff_lower_rock/cave_cliff_lower.png',optimize=True);print(ch)
