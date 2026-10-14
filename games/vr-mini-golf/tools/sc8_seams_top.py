import json, sys, numpy as np
tris=json.load(open('/tmp/sc8/tris.json'))
probe=json.load(open('/Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtests/stage-sc8/probe.json'))
pos={p['path'].split('.')[-1]:np.array(p['pos']) for p in probe['seams']}
shift=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
STEP=0.05
def world(key):
    T=np.array(tris[key]); c=(T.reshape(-1,3).min(0)+T.reshape(-1,3).max(0))/2
    return T-c+pos[key]
def raster(tile):
    H={}
    for key in tris:
        if not key.startswith(tile+'__'): continue
        T=world(key); T[:,:,1]+=shift.get(tile,0)
        for t in T:
            n=np.cross(t[1]-t[0],t[2]-t[0]); 
            if abs(n[1])<1e-9 or n[1]/np.linalg.norm(n)<0.2: continue
            x0,x1=t[:,0].min(),t[:,0].max(); z0,z1=t[:,2].min(),t[:,2].max()
            for i in range(int(np.floor(x0/STEP)),int(np.ceil(x1/STEP))+1):
                for j in range(int(np.floor(z0/STEP)),int(np.ceil(z1/STEP))+1):
                    px,pz=i*STEP,j*STEP
                    a,b,c=t
                    d=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
                    if abs(d)<1e-12: continue
                    l1=((b[2]-c[2])*(px-c[0])+(c[0]-b[0])*(pz-c[2]))/d
                    l2=((c[2]-a[2])*(px-c[0])+(a[0]-c[0])*(pz-c[2]))/d
                    l3=1-l1-l2
                    if min(l1,l2,l3)<-1e-9: continue
                    y=l1*a[1]+l2*b[1]+l3*c[1]
                    k=(i,j)
                    if k not in H or y>H[k]: H[k]=y
    return H
pairs=[('h16_ground_s03','h17_ground_s20'),('h13_ground_s04','h14_ground_s00'),('h09_ground_s00','h09_ground_s01')]
R={}
cache={}
for a,b in pairs:
    A=cache.setdefault(a,raster(a)); B=cache.setdefault(b,raster(b))
    sh=[k for k in A if k in B]
    if not sh: R[a+'|'+b]={'shared':0}; continue
    g=np.array([A[k]-B[k] for k in sh])
    i=int(np.argmin(np.abs(g))); k=sh[i]
    R[a+'|'+b]={'sharedCells':len(sh),'minAbsGap':float(abs(g[i])),'at':[k[0]*STEP,round(A[k],3),k[1]*STEP],'aHigherCells':int((g>0).sum()),'bHigherCells':int((g<0).sum()),
      'cellsUnder0.02':int((np.abs(g)<0.02).sum()),'cellsUnder0.05':int((np.abs(g)<0.05).sum()),'meanGapAminusB':float(g.mean())}
print(json.dumps(R,indent=1))
