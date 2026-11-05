# Box-only: black silhouettes of the edge kit (side row: X/Y; top row: X/Z), common scale, ring/river excluded.
import json,numpy as np,sys
from PIL import Image,ImageDraw
g=json.load(open(sys.argv[1]));ks=[k for k in g if k not in('ground_ring','river_ext')];PX=14
ws=[max(12,int((np.ptp(np.vstack([o['verts'] for o in g[k]['objects']])[:,0])+3)*PX)) for k in ks]
H=int(23*PX);out=Image.new('RGB',(sum(ws),2*H+30),'white');d=ImageDraw.Draw(out);x0=0
for k,w in zip(ks,ws):
    for o in g[k]['objects']:
        V=np.array(o['verts'])
        for t in o['tris']:
            p=V[t];d.polygon([(x0+w/2+a*PX,H-8-b*PX) for a,b in p[:,[0,1]]],fill='black');d.polygon([(x0+w/2+a*PX,H+H/2+c*PX) for a,c in p[:,[0,2]]],fill='black')
    d.text((x0+4,2*H+10),k,fill='black');x0+=w
d.line([(0,H),(out.width,H)],fill=(200,200,200));out.save(sys.argv[2])
