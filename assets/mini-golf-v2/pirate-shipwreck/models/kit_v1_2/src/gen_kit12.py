# kit_v1_2: kit_rock_s/m/l regenerated from kit_v1_1 (identical bodies, jitter, rng stream, pivots) with moss caps. Run: /workspace/.geo/bin/python src/gen_kit12.py work
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit_lib import *
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
def nz(u,s): return 0.5*math.sin(2.7*u[0]+s)+0.3*math.sin(3.9*u[2]+2*s)+0.2*math.sin(5.1*u[1]+1.7*s)
def jitter(m,c,jit,s):
    V=m.vertices.copy();d=V-np.array(c,float);u=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    k=np.array([1+jit*nz(x,s) for x in u])[:,None];m.vertices=np.array(c,float)+d*k;return m
def caprings(rx,ry,rz,tmax,lon,lat):
    rings=[]
    for t in np.linspace(0.04,tmax,lat+1):
        rr=math.sin(t);rings.append([(rx*rr*math.cos(2*math.pi*k/lon),ry*math.cos(t),rz*rr*math.sin(2*math.pi*k/lon)) for k in range(lon)])
    return rings
def yawm(m,deg,pos): m=m.copy();m.apply_transform(Rm((0,1,0),deg));m.apply_translation(pos);return m
def tuft(P,pos,n,L,seed,cols=('Fern','FernDk','FernLt'),w=0.7,seg=4):
    rg=np.random.default_rng(seed)
    for k in range(n):
        a=math.radians(k*360/n+rg.uniform(-18,18));dd=V3(math.cos(a),0,math.sin(a));l=L*rg.uniform(0.8,1.15);p0=V3(*pos)+dd*0.25
        P.add(blade(p0,p0+dd*l*0.35+V3(0,l*0.9,0),p0+dd*l*0.95+V3(0,l*rg.uniform(0.1,0.5),0),w,0.2,seg),cols[k%len(cols)])
SANDY={('kit_rock_m',5),('kit_rock_l',6)}   # a little sand: one small rock's lowest band on m and l
GREEN=['LeafLt','LeafGreen','LeafDk'];ROCK=['Rock','RockLt','RockDk']
def rockset(i,R,n,rx0,seed,lon,lat,nferns,fl):
    rg=np.random.default_rng(seed);P=Part(i)
    rg.uniform(0,90)
    tops=[];P.nfern=0
    for k in range(n):
        rx=rx0*(1-0.72*k/n)*rg.uniform(0.9,1.1);ry=rx*rg.uniform(0.8,1.25);rz=rx*rg.uniform(0.8,1.1)
        a=k*2.4;rr=0 if k==0 else R*rg.uniform(0.35,0.85)-rx*0.2;pos=(rr*math.cos(a),-ry*0.3,rr*math.sin(a));yaw=rg.uniform(0,360);sd=seed+k*1.3
        lo,la=(lon,lat) if k<3 else (8,3)
        b=dome(rx,ry,rz,(0,0,0),lo,la);jitter(b,(0,0,0),0.16,sd);P.add(yawm(b,yaw,pos),['Rock','RockDk','RockLt'][k%3])
        rings=caprings(rx*1.05,ry*1.05,rz*1.05,0.95,lo,max(la-1,2));nr=len(rings)
        kk=nr-2   # rings[:kk+1] = moss on the upper part of the cap, rings[kk:] = lowest band (rock, or a little sand)
        top=ring_solid(rings[:kk+1]);low=ring_solid(rings[kk:])
        for m in(top,low): jitter(m,(0,0,0),0.16,sd)
        P.add(yawm(top,yaw,pos),GREEN[k%3])
        P.add(yawm(low,yaw,pos),'SandTopLt' if (i,k) in SANDY else ROCK[(k+1)%3])
        tops.append((k,rx,ry,rz,pos,a))
    P.nbody=len(P.items)
    # fern tufts on the shoulders of the smaller rocks (inside the footprint, below the highest top)
    for q in range(nferns):
        k,rx,ry,rz,pos,a=tops[1+q%(n-1)]
        ang=math.atan2(-pos[2],-pos[0])+(0.5 if q%2 else -0.5)*(1+0.3*q);f=0.55
        x=pos[0]+f*rx*math.cos(ang);z=pos[2]+f*rz*math.sin(ang);y=pos[1]+ry*math.sqrt(1-f*f)*0.93
        tuft(P,(x,y,z),4,fl,seed*7+q,cols=[('Fern','FernDk','FernLt'),('FernLt','Fern','FernDk')][q%2])
    return P
SPEC={'kit_rock_s':(6.5,5,3.4,21,10,4,2,2.0),'kit_rock_m':(11,8,5.6,22,12,4,3,1.9),'kit_rock_l':(19,11,9.6,23,14,5,5,2.8)}
os.makedirs(os.path.join(OUT,'geom'),exist_ok=True);report={};ref=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','kit_v1_1','work','box_report.json')))
for i,(R,n,rx0,seed,lon,lat,nf,fl) in SPEC.items():
    P=rockset(i,R,n,rx0,seed,lon,lat,nf,fl)
    V0=np.concatenate([m.vertices for m,_,_ in P.items[:P.nbody]]);mn,mx=V0.min(0),V0.max(0)
    sh=np.array([-(mn[0]+mx[0])/2,0,-(mn[2]+mx[2])/2])      # same 'buried' settle as v1_1
    g=P.merged();V=np.array(g['verts'])+sh;g['verts']=np.round(V,4).tolist()
    # fern-free bbox must match v1_1 exactly: compute bbox of the bodies+caps only
    json.dump({i:dict(objects=[dict(name=i,verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])])},open(os.path.join(OUT,'geom',i+'.json'),'w'))
    Vb=np.array(g['verts']);print([(Vb[:,a].min()-V0[:,a].min()-sh[a],Vb[:,a].max()-V0[:,a].max()-sh[a]) for a in range(3)]);assert Vb[:,0].min()>=V0[:,0].min()+sh[0]-0.02 and Vb[:,0].max()<=V0[:,0].max()+sh[0]+0.02 and Vb[:,2].min()>=V0[:,2].min()+sh[2]-0.02 and Vb[:,2].max()<=V0[:,2].max()+sh[2]+0.02 and Vb[:,1].max()<=V0[:,1].max()+0.02,'fern outside body bbox'
    bb=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist());sz=np.round(V.max(0)-V.min(0),2).tolist()
    print(i,len(g['tris']),sz,'v1_1:',ref[i]['size'],bb['min'][1],ref[i]['bbox']['min'][1])
    assert np.allclose(sz,ref[i]['size'],atol=0.02) and abs(bb['min'][1]-ref[i]['bbox']['min'][1])<0.02,'bbox changed'
    report[i]=dict(tris=len(g['tris']),bbox=bb,size=sz,v1_1_tris=ref[i]['tris'],v1_1_size=ref[i]['size'])
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
