# box-side: lay the flat emission pass (Flame/Core/Glow parts, transparent bg, everything else black) over the lit Workbench render
import sys
from PIL import Image
import numpy as np
base,emit,out=sys.argv[1:4]
b=Image.open(base).convert('RGB');e=Image.open(emit).convert('RGBA');ea=np.array(e);ba=np.array(b)
m=(ea[:,:,3]>0)&(ea[:,:,:3].sum(2)>6)
# render script passes raw /255 values to diffuse_color (a LINEAR field), so the flat pass came out sRGB-encoded (255,194,124 for 255,140,50); decode back so the preview shows the exact Neon colours
rgb=ea[:,:,:3].astype(float)/255;lin=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4);ea[:,:,:3]=np.round(lin*255).astype(np.uint8)
ba[m]=ea[:,:,:3][m];Image.fromarray(ba).save(out)
