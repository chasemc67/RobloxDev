# quick numpy/PIL flat-shaded painter's preview (box only, for iterating before the real Blender Workbench renders)
import numpy as np,pickle,sys,math
from PIL import Image,ImageDraw
sys.path.insert(0,'.')
from wreck_lib import PAL
def render(parts,path,eye,tgt,size=(1400,900),fov=40,ortho=None,bg=(150,170,190),sand=True):
    V=[];F=[];C=[]
    for p in parts:
        v=np.array(p['verts']);f=np.array(p['tris']);o=len(V) and sum(len(x) for x in V)
        V.append(v);F.append(f+ (sum(len(x) for x in V[:-1])));C+= [PAL[c] for c in p['face_mat']]
    V=np.concatenate(V);F=np.concatenate(F);C=np.array(C,float)
    eye=np.array(eye,float);tgt=np.array(tgt,float);fw=tgt-eye;fw/=np.linalg.norm(fw);up=np.array([0,1.0,0])
    if abs(fw[1])>0.99: up=np.array([0,0,-1.0])
    rt=np.cross(fw,up);rt/=np.linalg.norm(rt);u=np.cross(rt,fw)
    rel=V-eye;x=rel@rt;y=rel@u;z=rel@fw
    W,H=size;asp=W/H
    if ortho: sx=x/ortho*H+W/2;sy=-y/ortho*H+H/2
    else:
        f=1/math.tan(math.radians(fov)/2);sx=x/np.maximum(z,0.1)*f/1*H/2+W/2;sy=-y/np.maximum(z,0.1)*f*H/2+H/2
    tri=F;a=V[tri[:,0]];b=V[tri[:,1]];c=V[tri[:,2]];n=np.cross(b-a,c-a);n/=np.maximum(np.linalg.norm(n,axis=1),1e-9)[:,None]
    L=np.array([0.4,0.8,0.45]);L/=np.linalg.norm(L);sh=0.45+0.55*np.abs(n@L)*1.0
    depth=(z[tri[:,0]]+z[tri[:,1]]+z[tri[:,2]])/3;order=np.argsort(-depth)
    im=Image.new('RGB',size,bg);d=ImageDraw.Draw(im)
    if sand:
        g=np.array([[-400,0,-400],[400,0,-400],[400,0,400],[-400,0,400]],float);r=g-eye;gx=r@rt;gy=r@u;gz=r@fw
        if ortho: pts=[(gx[i]/ortho*H+W/2,-gy[i]/ortho*H+H/2) for i in range(4)]
        else:
            f=1/math.tan(math.radians(fov)/2);pts=[(gx[i]/max(gz[i],0.1)*f*H/2+W/2,-gy[i]/max(gz[i],0.1)*f*H/2+H/2) for i in range(4)]
        if all(gz>0.1): d.polygon(pts,fill=(226,184,128))
    for i in order:
        if z[tri[i,0]]<0.1 or z[tri[i,1]]<0.1 or z[tri[i,2]]<0.1: continue
        col=tuple(int(min(255,v*sh[i])) for v in C[i])
        d.polygon([(sx[tri[i,k]],sy[tri[i,k]]) for k in range(3)],fill=col)
    im.save(path)
if __name__=='__main__':
    D=pickle.load(open(sys.argv[1],'rb'));parts=[D[k] for k in D if isinstance(D[k],dict) and 'verts' in D[k]]
    render(parts,'/tmp/pv_34.png',(200,110,230),(0,40,0))
    render(parts,'/tmp/pv_side.png',(420,40,0),(0,40,0),ortho=170)
    render(parts,'/tmp/pv_top.png',(0,500,0.01),(0,0,0),ortho=290)
