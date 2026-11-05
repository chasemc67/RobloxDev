"""Plain Python mesh helpers; Y-up, pivot-relative, no Blender imports."""
import math
import numpy as np

class Mesh:
    def __init__(self): self.groups={}
    def add(self,m,vs,fs):
        g=self.groups.setdefault(m,dict(verts=[],faces=[])); off=len(g['verts'])
        g['verts'].extend([list(v) for v in vs]); g['faces'].extend([[i+off for i in f] for f in fs])
    def sphere(self,m,c,size,n=12,steps=5):
        c=np.array(c); r=np.array(size)/2
        vs=[(c+[0,-r[1],0]).tolist()]
        for j in range(1,steps):
            a=-math.pi/2+math.pi*j/steps
            for i in range(n):
                t=math.tau*i/n; vs.append((c+r*[math.cos(a)*math.cos(t),math.sin(a),math.cos(a)*math.sin(t)]).tolist())
        vs.append((c+[0,r[1],0]).tolist()); top=len(vs)-1
        fs=[[0,1+(i+1)%n,1+i] for i in range(n)]
        for j in range(steps-2):
            a=1+j*n; b=a+n
            fs.extend([[a+i,a+(i+1)%n,b+(i+1)%n,b+i] for i in range(n)])
        fs.extend([[top,1+(steps-2)*n+i,1+(steps-2)*n+(i+1)%n] for i in range(n)])
        self.add(m,vs,fs)
    def tube(self,m,a,b,r0,r1=None,n=5):
        a=np.array(a,float);b=np.array(b,float);d=b-a;d/=np.linalg.norm(d)
        u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [1,0,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
        rings=[[(c+r*(u*math.cos(math.tau*i/n)+v*math.sin(math.tau*i/n))).tolist() for i in range(n)] for c,r in [(a,r0),(b,r0 if r1 is None else r1)]]
        self.loft(m,rings)
    def loft(self,m,rings,caps=True):
        n=len(rings[0]);fs=[]
        for j in range(len(rings)-1): fs.extend([[j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i] for i in range(n)])
        if caps:fs.extend([list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))])
        self.add(m,[v for ring in rings for v in ring],fs)
    def box(self,m,c,size):
        c=np.array(c);s=np.array(size)/2
        self.add(m,[(c+[x,y,z]).tolist() for y in [-s[1],s[1]] for x,z in [(-s[0],-s[2]),(s[0],-s[2]),(s[0],s[2]),(-s[0],s[2])]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])

def components(g):
    adj=[set() for _ in g['verts']]
    for f in g['faces']:
        for i in f:adj[i].update(f)
    seen=set()
    for i in range(len(adj)):
        if i in seen:continue
        todo=[i];ids=set()
        while todo:
            j=todo.pop()
            if j in ids:continue
            ids.add(j);todo.extend(adj[j]-ids)
        seen.update(ids);ii=sorted(ids);lookup={v:j for j,v in enumerate(ii)}
        yield dict(verts=[g['verts'][j] for j in ii],faces=[[lookup[j] for j in f] for f in g['faces'] if f[0] in ids])

def count(groups):return sum(len(f)-2 for g in groups.values() for f in g['faces'])
