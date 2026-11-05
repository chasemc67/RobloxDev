# v22 final trail width table: v21 perpendicular method on the generator trail cells (Sandstone/Sand), 5 points per leg spread by route length;
# plus the same perpendicular on the terrain top map counting clear ground (Sand/Sandstone/Rock/Slate), and the cross-slope over that run
exec(open('/Users/chase-mini/stage/v22s/widths_terr.py').read().split('allw=[]')[0])
TY={}
for e in open('/Users/chase-mini/stage/v22_diag/topmap_v22.txt').read().split(';'):
  g,h,m,y=e.split(','); TY[(int(g),int(h))]=(m,float(y))
def clear(x,z): return TY.get((int((x+2048)//4),int((z+1280)//4)),('-',0))[0] in ('S','T','R','s')
def run_c(x,z,nx,nz):
  a=0
  while clear(x-nx*(a+0.25),z-nz*(a+0.25)) and a<30: a+=0.25
  b=0
  while clear(x+nx*(b+0.25),z+nz*(b+0.25)) and b<30: b+=0.25
  return a+b
add=set(tuple(map(int,e.split(","))) for e in open("/Users/chase-mini/stage/v22s/widen.txt").read().split(";")); S|=add
rows=[]; under=[]
for i in range(1,18):
  j=i+1
  p,R=path(nearest(pads[i]),nearest(pads[j]))
  acc=[0]
  for k in range(1,len(p)): acc.append(acc[-1]+math.hypot(W(p[k])[0]-W(p[k-1])[0],W(p[k])[1]-W(p[k-1])[1]))
  ks=[p[min(range(len(p)),key=lambda k:abs(acc[k]-acc[-1]*t))] for t in (0.2,0.35,0.5,0.65,0.8)]
  wc=[];wcl=[];notes=[]
  for k in ks:
    x,z=W(k); nx,nz=pca(x,z); w=run_through(x,z,nx,nz); c=run_c(x,z,nx,nz); wc.append(w); wcl.append(c)
    if w<8:
      side=[TY.get((int((x+nx*s+2048)//4),int((z+nz*s+1280)//4)),('-',0))[0] for s in (-8,-6,-4,4,6,8)]
      notes.append(f"({x},{z}) cells {w:.1f} clear {c:.1f} sides {''.join(side)}")
      under.append((i,j,x,z,w,c))
  # dense: every 4th path cell, cells-method
  dense=[run_through(*W(k),*pca(*W(k))) for k in p[::2]]
  med=sorted(dense)[len(dense)//2]
  frac8=100*sum(1 for w in dense if w>=8)/len(dense)
  print(f"leg {i:2d}->{j:2d} | cells "+' '.join(f'{w:5.1f}' for w in wc)+f" | min {min(wc):5.1f} | clear "+' '.join(f'{w:5.1f}' for w in wcl)+f" | dense median {med:.1f}, >=8 at {frac8:.0f}% of {len(dense)} pts"+(" | "+'; '.join(notes) if notes else ""))
print("points under 8 (cells):",len(under))
