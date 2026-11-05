"""Full endpoint audit, including pins the original timeout-only fuzz missed."""
import math
import numpy as np
import sim as S

@S.njit(cache=True, parallel=True)
def audit_batch(P,W,nW,MP,nMP,MB,nMB,TP,nTP,HZ,nHZ,CUP,PH,X,Z,Y,A,V,T):
    n=len(A)
    oc=np.zeros(n,np.int64)
    ends=np.zeros((n,3))
    pins=np.zeros(n,np.int64)
    for i in S.prange(n):
        dummy=np.zeros((1,3))
        r=S.sim_shot(P,W,nW,MP,nMP,MB,nMB,TP,nTP,HZ,nHZ,CUP,PH,
                     X[i],Z[i],Y[i],V[i]*math.cos(A[i]),V[i]*math.sin(A[i]),T[i],False,dummy)
        oc[i]=int(r[3]); ends[i,0]=r[0]; ends[i,1]=r[2]; ends[i,2]=r[1]
        if int(r[3])==0:
            rt=np.empty(9); rw=np.empty(9); cen=np.empty(3)
            for k in range(nMB):
                S.blocker_pose(MP,MB,k,T[i]+r[4],rt,rw,cen)
                pen,_,_=S.sphere_box(r[0],r[2]+PH[7],r[1],cen[0],cen[1],cen[2],
                                    MB[k,4]+.03,MB[k,5]+.03,MB[k,6]+.03,rw,PH[7])
                if MP[int(MB[k,0]),0]==4:
                    pen=S.lip_swept_contact(MP,MB,k,r[0],r[2],r[1],PH[7])
                if pen>1e-9: pins[i]=1
    return oc,ends,pins
