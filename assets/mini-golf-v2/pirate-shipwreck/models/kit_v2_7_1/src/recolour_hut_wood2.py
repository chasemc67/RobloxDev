# kit_v2_7_1: PIL edit of kit_v2_7/kit_hut_leanto.png: Wood1 -> (100,72,50), Wood2 -> (122,90,64). Nothing else.
import json,numpy as np
from PIL import Image
names=list(json.load(open('../kit_v2_4/work/palette.json')))
im=np.array(Image.open('../kit_v2_7/kit_hut_leanto.png').convert('RGB'))
for n,c in(('Wood1',(100,72,50)),('Wood2',(122,90,64))):
    i=names.index(n);x,y=i%8*32,i//8*32;im[y:y+32,x:x+32]=c
Image.fromarray(im).save('kit_hut_leanto.png',optimize=True)
