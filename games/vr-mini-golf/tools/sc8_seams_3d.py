import json, sys, numpy as np
tris=json.load(open('/tmp/sc8/tris.json'))
probe=json.load(open('/Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtests/stage-sc8/probe.json'))
pos={p['path'].split('.')[-1]:np.array(p['pos']) for p in probe['seams']}
shift=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
def tile(t):
    out=[]
    for key in tris:
        if key.startswith(t+'__'):
            T=np.array(tris[key]); c=(T.reshape(-1,3).min(0)+T.reshape(-1,3).max(0))/2
            W=T-c+pos[key]; W[:,:,1]+=shift.get(t,0); out.append(W)
    return np.concatenate(out)
def info(T):
    n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); a=np.linalg.norm(n,axis=1); ok=a>1e-9
    return T[ok], n[ok]/a[ok,None]
def pin(p,t):
    # p (k,3) points, t (3,3) triangle: barycentric in triangle plane
    v0=t[2]-t[0]; v1=t[1]-t[0]; v2=p-t[0]
    d00=v0@v0; d01=v0@v1; d11=v1@v1; d02=v2@v0; d12=v2@v1
    den=d00*d11-d01*d01
    u=(d11*d02-d01*d12)/den; v=(d00*d12-d01*d02)/den
    return (u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)
def check(a,b,lim=0.05):
    A,nA=info(tile(a)); B,nB=info(tile(b))
    cA=A.mean(1); cB=B.mean(1)
    res=[]
    for i in range(len(A)):
        dots=nB@nA[i]
        cand=np.where(np.abs(dots)>0.99)[0]
        if not len(cand): continue
        dist=np.abs((cB[cand]-cA[i])@nA[i])
        cand=cand[dist<lim]
        if not len(cand): continue
        # sample points of A (shrunk toward centroid) tested in each B triangle
        S=np.array([w0*A[i][0]+w1*A[i][1]+(1-w0-w1)*A[i][2] for w0 in np.linspace(0.01,0.98,9) for w1 in np.linspace(0.01,0.98,9) if w0+w1<=0.99])
        for j in cand:
            if pin(S,B[j]).any():
                res.append((float(abs((cB[j]-cA[i])@nA[i])),[round(x,3) for x in cA[i]],[round(x,3) for x in nA[i]],int(np.sign(dots[j]))))
    res.sort()
    return res
pairs=[('h16_ground_s03','h17_ground_s20'),('h13_ground_s04','h14_ground_s00'),('h09_ground_s00','h09_ground_s01')]
R={}
for a,b in pairs:
    r=check(a,b)+check(b,a)
    r.sort()
    R[a+'|'+b]={'overlappingParallelTriPairsUnder0.05':len(r),'minGap':r[0][0] if r else None,'worst':r[:4],
                'sameFacingUnder0.02':sum(1 for x in r if x[0]<0.02 and x[3]>0),'oppFacingUnder0.02':sum(1 for x in r if x[0]<0.02 and x[3]<0)}
print(json.dumps(R))
