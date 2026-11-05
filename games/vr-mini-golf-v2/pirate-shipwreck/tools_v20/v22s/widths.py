# v22 trail widths: v20c/v21 perpendicular run on the generator trail cells (Sandstone 8 + Sand 1), 5 points per leg
import re,math
s=open('/Users/chase-mini/stage/matpatch20.luau').read()
d=re.search(r'local DATA = "(.*?)"',s,re.S).group(1)
cells=[tuple(map(int,t.split(','))) for t in d.split(';') if t]
S=set((g,h) for g,h,m in cells if m in (8,1))
def isS(x,z): return (int((x+2048)//4),int((z+1280)//4)) in S
cent=[(-2048+4*g+2,-1280+4*h+2) for g,h in S]
pads={1:(-511.5,245.8),2:(-379.5,244.5),3:(-97.5,310.5),4:(178.5,349.5),5:(451.5,382.5),6:(739.5,415.5),7:(934.5,337.5),8:(910.5,136.5),9:(733.5,-58.5),10:(394.5,160.5),11:(181.5,-10.5),12:(-127.5,-94.5),13:(-367.5,-175.5),14:(-595.5,-370.5),15:(-358.5,-550.5),16:(109.5,-514.5),17:(394.5,-349.5),18:(583.5,-481.5)}
def width(x,z):
  pts=[(a,b) for a,b in cent if math.hypot(a-x,b-z)<24]
  mx=sum(p[0] for p in pts)/len(pts); mz=sum(p[1] for p in pts)/len(pts)
  sxx=sum((p[0]-mx)**2 for p in pts); szz=sum((p[1]-mz)**2 for p in pts); sxz=sum((p[0]-mx)*(p[1]-mz) for p in pts)
  th=0.5*math.atan2(2*sxz,sxx-szz); tx,tz=math.cos(th),math.sin(th); nx,nz=-tz,tx
  run=[t*0.5 for t in range(-60,61) if isS(x+nx*t*0.5,z+nz*t*0.5)]
  if not run: return 0
  runs=[];cur=[run[0]]
  for a in run[1:]:
    if a-cur[-1]<=0.51: cur.append(a)
    else: runs.append(cur);cur=[a]
  runs.append(cur)
  r=[q for q in runs if q[0]<=0<=q[-1]] or [max(runs,key=len)]
  r=r[0]; return r[-1]-r[0]+0.5
allw=[]; under=[]
legs=[(i,i+1) for i in range(1,18)]
for a,b in legs:
  (x0,z0),(x1,z1)=pads[a],pads[b]; L=math.hypot(x1-x0,z1-z0)
  ws=[];where=[]
  for t in (0.2,0.35,0.5,0.65,0.8):
    px,pz=x0+(x1-x0)*t,z0+(z1-z0)*t
    c=min(cent,key=lambda p:(p[0]-px)**2+(p[1]-pz)**2); off=math.hypot(c[0]-px,c[1]-pz)
    w=width(*c); ws.append(w); where.append(f"({c[0]},{c[1]})" + (f"off{off:.0f}" if off>12 else ""))
  allw+=[(w,a,b) for w in ws]
  if min(ws)<8: under.append((a,b,min(ws)))
  print(f"leg {a:2d}->{b:2d}: "+' '.join(f"{w:5.1f}" for w in ws)+f" | min {min(ws):.1f} mean {sum(ws)/5:.1f} | at "+' '.join(where))
print("overall min %.1f ; legs with a point under 8: %s"%(min(allw)[0],under))
