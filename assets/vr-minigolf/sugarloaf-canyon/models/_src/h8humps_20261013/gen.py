import json,sys,numpy as np,math
sys.path.insert(0,'.')
sys.argv=[sys.argv[0]]
import sc_dress_pass6 as P
TEE=np.array([360.0,70.0,55.0])
B=json.load(open('_cache/h08_bricks_v3.json'))['bricks']
bricks=[]
for b in B:
    T=P.brick_tris(b['pos'],b['yaw'],b['len'])-TEE
    bricks.append(T.tolist())
# spec profile
starts=[-8,-18.467,-28.933,-39.4]
def prof(z):
    for s in starts:
        if s-0.3<=z<=s: return 0.12*(s-z)/0.3
        if s-0.6<=z<s-0.3: return 0.12*(z-(s-0.6))/0.3
    return 0.0
knots=set(np.round(np.arange(-8,-40.0001,-0.5),4))
for s in starts: knots|={s,round(s-0.3,4),round(s-0.6,4)}
Z=sorted(knots,reverse=True)
X0,X1=4.5,4.56; YB,YT=-0.05,0.55
groups={'PepRed':[],'MintWhite':[]}
def quad(a,b,c,d,out,n):
    for t in ([a,b,c],[a,c,d]):
        T=np.array(t,float); nn=np.cross(T[1]-T[0],T[2]-T[0])
        out.append(t if np.dot(nn,n)>0 else [t[0],t[2],t[1]])
for sgn in (-1,1):
    xi,xo=sgn*X0,sgn*X1
    for i,(za,zb) in enumerate(zip(Z,Z[1:])):
        # stripe colour by 0.5-stud cell of the midpoint (diagonal-ish taffy stripes alternate)
        cell=int(math.floor((-(za+zb)/2-8)/0.5))
        m='PepRed' if cell%2==0 else 'MintWhite'
        ya,yb=prof(za),prof(zb); o=groups[m]
        A=lambda x,y,z:[x,y,z]
        quad(A(xo,YB+ya,za),A(xo,YB+yb,zb),A(xo,YT+yb,zb),A(xo,YT+ya,za),o,[sgn,0,0])
        quad(A(xi,YT+ya,za),A(xi,YT+yb,zb),A(xo,YT+yb,zb),A(xo,YT+ya,za),o,[0,1,0])
        if i==0: quad(A(xi,YB+ya,za),A(xo,YB+ya,za),A(xo,YT+ya,za),A(xi,YT+ya,za),o,[0,0,1])
        if i==len(Z)-2: quad(A(xi,YB+yb,zb),A(xo,YB+yb,zb),A(xo,YT+yb,zb),A(xi,YT+yb,zb),o,[0,0,-1])
json.dump(dict(bricks=bricks,trim=groups,trim_spec=dict(x=[X0,X1],y_offset=[YB,YT],z=[Z[0],Z[-1]])),open('/workspace/h08job/h08_geom.json','w'))
print(len(bricks)*len(bricks[0]),{k:len(v) for k,v in groups.items()})
