# Box-only: flat black silhouettes (top-down XZ and side ZY, front=-Z to the left) for all models at one scale.
import json,numpy as np,sys
from PIL import Image,ImageDraw
g=json.load(open(sys.argv[1]));PX=60;W=6*PX;out=Image.new('RGB',(len(g)*W,2*W+60),'white');d=ImageDraw.Draw(out)
for i,(k,v) in enumerate(g.items()):
    for row,(ax) in enumerate(((0,2),(2,1))):
        for o in v['objects']:
            V=np.array(o['verts'])
            for t in o['tris']:
                p=V[t][:,ax]
                if row==0: pts=[(i*W+W/2+x*PX,W/2+z*PX) for x,z in p]
                else: pts=[(i*W+W/2+z*PX,2*W-10-y*PX) for z,y in p]
                d.polygon(pts,fill='black')
    d.text((i*W+10,2*W+15),k,fill='black')
d.line([(0,W),(out.width,W)],fill=(200,200,200))
out.save(sys.argv[2])
