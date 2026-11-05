# kit_v2_7_2: PIL edit of kit_v2_7_1/kit_hut_leanto.png: Straw->(230,192,112), StrawDk->(196,158,90), StrawLt->(245,215,155). Nothing else.
import json,numpy as np
from PIL import Image
names=list(json.load(open('../kit_v2_4/work/palette.json')))
im=np.array(Image.open('../kit_v2_7_1/kit_hut_leanto.png').convert('RGB'))
for n,c in(('Straw',(230,192,112)),('StrawDk',(196,158,90)),('StrawLt',(245,215,155))):
    i=names.index(n);x,y=i%8*32,i//8*32;im[y:y+32,x:x+32]=c
Image.fromarray(im).save('kit_hut_leanto.png',optimize=True)
