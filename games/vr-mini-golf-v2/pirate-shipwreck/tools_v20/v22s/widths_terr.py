# v22 trail widths on the RENDERED terrain top material (Sand / Sandstone from a raycast map), v21 perpendicular method,
# 5 points per leg spread along the route (BFS through the generator trail cells, gaps bridged only to find the route)
exec(open('/Users/chase-mini/stage/v22s/widths2.py').read().split('res=[]')[0])
import collections
T={}
for e in open('/Users/chase-mini/stage/v22_diag/topmap_v22.txt').read().split(';'):
  g,h,m,y=e.split(','); T[(int(g),int(h))]=m
def isT(x,z): return T.get((int((x+2048)//4),int((z+1280)//4))) in ('S','T')
def run_t(x,z,nx,nz):
  if not isT(x,z): return 0
  a=0
  while isT(x-nx*(a+0.25),z-nz*(a+0.25)) and a<60: a+=0.25
  b=0
  while isT(x+nx*(b+0.25),z+nz*(b+0.25)) and b<60: b+=0.25
  return a+b
def bfsR(a,b,R):
  prev={a:None}; q=collections.deque([a])
  offs=sorted([(dg,dh) for dg in range(-R,R+1) for dh in range(-R,R+1) if (dg,dh)!=(0,0)],key=lambda o:o[0]**2+o[1]**2)
  while q:
    c=q.popleft()
    if c==b: break
    for dg,dh in offs:
      n=(c[0]+dg,c[1]+dh)
      if n in S and n not in prev: prev[n]=c; q.append(n)
  if b not in prev: return None
  p=[b]
  while prev[p[-1]] is not None: p.append(prev[p[-1]])
  return p[::-1]
def path(a,b):
  for R in (1,2,3,4,6,8,12):
    p=bfsR(a,b,R)
    if p: return p,R
  return None,None
allw=[]
for i in range(1,18):
  j=i+1
  p,R=path(nearest(pads[i]),nearest(pads[j]))
  if not p: print(f"leg {i}->{j}: NO PATH"); continue
  # spread the 5 points by path LENGTH (not index)
  acc=[0]
  for k in range(1,len(p)): acc.append(acc[-1]+math.hypot(W(p[k])[0]-W(p[k-1])[0],W(p[k])[1]-W(p[k-1])[1]))
  ks=[p[min(range(len(p)),key=lambda k:abs(acc[k]-acc[-1]*t))] for t in (0.2,0.35,0.5,0.65,0.8)]
  wc=[run_through(*W(k),*pca(*W(k))) for k in ks]
  wt=[run_t(*W(k),*pca(*W(k))) for k in ks]
  allw+=[(w,i,j,W(k)) for w,k in zip(wt,ks)]
  print(f"leg {i:2d}->{j:2d} route {acc[-1]:4.0f} st (gap<={R}): terrain "+' '.join(f'{w:5.1f}' for w in wt)+f" | min {min(wt):5.1f} | cells "+' '.join(f'{w:5.1f}' for w in wc)+" | "+' '.join(str(W(k)) for k in ks))
print("TERRAIN overall min %.1f ; points < 8: %s"%(min(allw)[0],[(i,j,w,xy) for w,i,j,xy in allw if w<8]))
