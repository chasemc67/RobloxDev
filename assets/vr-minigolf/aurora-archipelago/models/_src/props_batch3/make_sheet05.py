"""PIL triangle rasterization: concept | front silhouette | side silhouette | 3/4."""
import sys as _gs
from pathlib import Path as _gp
_gs.path.insert(0,str(_gp(__file__).resolve().parent.parent))
from polish_guard import start_guard
_PROTECTED_VERIFY=start_guard()

import json,math
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
S=Path(__file__).resolve().parent;D=S.parents[2];P=json.loads((S/'parts.json').read_text());PAL=json.loads((S/'palette.json').read_text())
def render(n,view,shade=False):
 tris=[]
 for p in P:
  if p['hole']!=n:continue
  for m,g in p['groups'].items():
   for f in g['faces']:
    for j in range(1,len(f)-1):tris.append((np.array([g['verts'][i] for i in [f[0],f[j],f[j+1]]])+p['anchor'],m))
 if view=='front':basis=np.array([[1,0,0],[0,1,0],[0,0,1]])
 elif view=='side':basis=np.array([[0,0,1],[0,1,0],[-1,0,0]])
 else:
  right=np.array([.85,0,-.53]);up=np.array([-.28,.85,-.45]);basis=np.stack([right,up,np.cross(right,up)])
 projected=[(t@basis.T,m) for t,m in tris];allv=np.concatenate([t for t,m in projected]);lo=allv[:,:2].min(0);hi=allv[:,:2].max(0);scale=min(360/max(hi[0]-lo[0],.01),270/max(hi[1]-lo[1],.01));im=Image.new('RGB',(400,320),'#E5E8F2');dr=ImageDraw.Draw(im)
 # Pixel depth buffer avoids painter-sort errors on long water and ice surfaces.
 pixels=np.full((320,400,3),[229,232,242],dtype=np.uint8);depth=np.full((320,400),-np.inf)
 for t,m in projected:
  xy=np.array([(200+(v[0]-(lo[0]+hi[0])/2)*scale,160-(v[1]-(lo[1]+hi[1])/2)*scale) for v in t])
  xmin=max(0,int(np.floor(xy[:,0].min())));xmax=min(399,int(np.ceil(xy[:,0].max())))
  ymin=max(0,int(np.floor(xy[:,1].min())));ymax=min(319,int(np.ceil(xy[:,1].max())))
  if xmin>xmax or ymin>ymax:continue
  xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
  aa,bb,cc=xy;den=(bb[1]-cc[1])*(aa[0]-cc[0])+(cc[0]-bb[0])*(aa[1]-cc[1])
  if abs(den)<1e-9:continue
  u=((bb[1]-cc[1])*(xx-cc[0])+(cc[0]-bb[0])*(yy-cc[1]))/den
  v=((cc[1]-aa[1])*(xx-cc[0])+(aa[0]-cc[0])*(yy-cc[1]))/den;w=1-u-v
  dd=u*t[0,2]+v*t[1,2]+w*t[2,2];sl=depth[ymin:ymax+1,xmin:xmax+1];mask=(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)&(dd>sl)
  if shade:
   col=np.array([int(PAL[m][0][i:i+2],16) for i in [1,3,5]],float)
   normal=np.cross(t[1]-t[0],t[2]-t[0]);norm=np.linalg.norm(normal)
   light=.68+.32*abs(np.dot(normal/(norm or 1),np.array([.3,.6,.74])))
   col=np.clip(col*light,0,255).astype(np.uint8)
  else:col=[34,34,51]
  pixels[ymin:ymax+1,xmin:xmax+1][mask]=col;sl[mask]=dd[mask]
 im=Image.fromarray(pixels)
 return im
out=Image.new('RGB',(1600,1880),'#222233');dr=ImageDraw.Draw(out)
import hashlib
B=json.loads((S/'build_report.json').read_text()) if (S/'build_report.json').exists() else None
current=bool(B and B.get('parts_sha256')==hashlib.sha256((S/'parts.json').read_bytes()).hexdigest())
exported_time=datetime.fromisoformat(B['exported_utc'].replace('Z','+00:00')).timestamp() if current else None
headers=['Concept crop','Front silhouette','Side silhouette','3/4 preview (provenance below)']
def preview(n):
 context=D/f'models/previews/props_batch3_polish/h{n:02}_34.png'
 if current:
  if context.exists() and context.stat().st_mtime>=exported_time:
   return ImageOps.fit(Image.open(context).convert('RGB'),(400,320)),['Blender hole context (current build)']
  assets=[(p['id'],D/f"models/previews/props_batch3_polish/{p['id']}_34.png") for p in P if p['hole']==n]
  fresh=sorted([(ident,path) for ident,path in assets if path.exists() and path.stat().st_mtime>=exported_time],key=lambda item:item[1].stat().st_mtime,reverse=True)
  if fresh:
   panel=Image.new('RGB',(400,320),'#E5E8F2')
   cols=math.ceil(math.sqrt(len(fresh)));rows=math.ceil(len(fresh)/cols)
   for i,(ident,path) in enumerate(fresh):
    w=400//cols;h=320//rows
    panel.paste(ImageOps.contain(Image.open(path).convert('RGB'),(w,h)),((i%cols)*w,(i//cols)*h))
   return panel,['Blender asset previews (current build)']+[ident for ident,path in fresh]
  if context.exists():
   return ImageOps.fit(Image.open(context).convert('RGB'),(400,320)),['Blender hole context (earlier build)']
 return render(n,'34',True),['Preflight shaded geometry (PIL)']
for j,title in enumerate(headers):dr.text((j*400+12,12),title,fill='white')
for row,n in enumerate([4,6,14,18]):
 y=40+row*460;im=Image.open(D/f'h{n:02}-concept.png').convert('RGB');out.paste(ImageOps.fit(im,(400,320)),(0,y))
 out.paste(render(n,'front'),(400,y));out.paste(render(n,'side'),(800,y))
 image,labels=preview(n)
 out.paste(image,(1200,y))
 print(f'H{n:02}: '+ '; '.join(labels))
 dr.text((12,y+327),f'H{n:02} - all assets shown in silhouettes',fill='white');
 ids=[p['id'] for p in P if p['hole']==n]
 for j,ident in enumerate(ids):dr.text((12+(j%3)*530,y+350+(j//3)*22),ident,fill='white')
 for j,label in enumerate(labels):dr.text((1210,y+327+j*14),label,fill='white')
(D/'silhouettes').mkdir(exist_ok=True);path=D/'silhouettes/sheet05-batch3-h04-h06-h14-h18.png';out.save(path);print(path)
