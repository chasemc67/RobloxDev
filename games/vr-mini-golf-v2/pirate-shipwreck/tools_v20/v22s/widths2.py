# v22 trail widths along the actual route: BFS path through trail cells (Sandstone 8 + Sand 1) pad a -> pad b,
# 5 points at 20/35/50/65/80 % of the path; width = (a) v21 perpendicular run (PCA normal), (b) min chord over 36 directions
import re,math,collections,sys
s=open('/Users/chase-mini/stage/matpatch20.luau').read()
d=re.search(r'local DATA = "(.*?)"',s,re.S).group(1)
cells=[tuple(map(int,t.split(','))) for t in d.split(';') if t]
S=set((g,h) for g,h,m in cells if m in (8,1))
def isS(x,z): return (int((x+2048)//4),int((z+1280)//4)) in S
W=lambda k:(-2048+4*k[0]+2,-1280+4*k[1]+2)
cent=[W(k) for k in S]
pads={1:(-511.5,245.8),2:(-379.5,244.5),3:(-97.5,310.5),4:(178.5,349.5),5:(451.5,382.5),6:(739.5,415.5),7:(934.5,337.5),8:(910.5,136.5),9:(733.5,-58.5),10:(394.5,160.5),11:(181.5,-10.5),12:(-127.5,-94.5),13:(-367.5,-175.5),14:(-595.5,-370.5),15:(-358.5,-550.5),16:(109.5,-514.5),17:(394.5,-349.5),18:(583.5,-481.5)}
def run_through(x,z,nx,nz):
  if not isS(x,z): return 0
  a=0
  while isS(x-nx*(a+0.25),z-nz*(a+0.25)) and a<60: a+=0.25
  b=0
  while isS(x+nx*(b+0.25),z+nz*(b+0.25)) and b<60: b+=0.25
  return a+b
def pca(x,z):
  pts=[(a,b) for a,b in cent if math.hypot(a-x,b-z)<24]
  mx=sum(p[0] for p in pts)/len(pts); mz=sum(p[1] for p in pts)/len(pts)
  sxx=sum((p[0]-mx)**2 for p in pts); szz=sum((p[1]-mz)**2 for p in pts); sxz=sum((p[0]-mx)*(p[1]-mz) for p in pts)
  th=0.5*math.atan2(2*sxz,sxx-szz); return -math.sin(th),math.cos(th)
def minchord(x,z):
  return min(run_through(x,z,math.cos(math.radians(a)),math.sin(math.radians(a))) for a in range(0,180,5))
def nearest(p): return min(S,key=lambda k:(W(k)[0]-p[0])**2+(W(k)[1]-p[1])**2)
def bfs(a,b):
  prev={a:None}; q=collections.deque([a])
  while q:
    c=q.popleft()
    if c==b: break
    for dg in (-1,0,1):
      for dh in (-1,0,1):
        n=(c[0]+dg,c[1]+dh)
        if n in S and n not in prev: prev[n]=c; q.append(n)
  if b not in prev: return None
  p=[b]
  while prev[p[-1]] is not None: p.append(prev[p[-1]])
  return p[::-1]
res=[]; allmin=[]
for i in range(1,18):
  path=bfs(nearest(pads[i]),nearest(pads[i+1]))
  if not path: print(f"leg {i}->{i+1}: NO PATH"); continue
  L=len(path); pts=[path[int(L*t)] for t in (0.2,0.35,0.5,0.65,0.8)]
  a=[run_through(*W(k),*pca(*W(k))) for k in pts]; b=[minchord(*W(k)) for k in pts]
  allmin+=[(w,i) for w in b]
  print(f"leg {i:2d}->{i+1:2d} ({L} cells): perp "+' '.join(f'{w:5.1f}' for w in a)+" | minchord "+' '.join(f'{w:5.1f}' for w in b)+f" | min {min(b):.1f} | at "+' '.join(str(W(k)) for k in pts))
print("overall minchord min %.1f; legs with a point < 8: %s"%(min(allmin)[0],sorted(set(i for w,i in allmin if w<8))))
