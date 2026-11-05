from pathlib import Path
p=Path('models/_src/props_batch1/rev6.py');t=p.read_text().replace('  thick=.18;pw=.7',"  if 'giant' in p['id']:\n   g.tube(q,col,split,[0,base+.76*h,0],.05*h,w*.3,.075/(w*.3),n=4)\n  thick=.18;pw=.7")
p.write_text(t)
p=Path('models/_src/props_batch1/complete_rev6.py');t=p.read_text().replace('from scipy.ndimage import label,binary_fill_holes','''from collections import deque
def label(mask):
 labs=np.zeros(mask.shape,dtype=np.int32);n=0
 for y,x in zip(*np.where(mask)):
  if labs[y,x]:continue
  n+=1;labs[y,x]=n;todo=deque([(y,x)])
  while todo:
   a,b=todo.popleft()
   for c,e in [(a-1,b),(a+1,b),(a,b-1),(a,b+1)]:
    if 0<=c<mask.shape[0] and 0<=e<mask.shape[1] and mask[c,e] and not labs[c,e]:labs[c,e]=n;todo.append((c,e))
 return labs,n
def binary_fill_holes(mask):
 labs,n=label(~mask);outside=set(labs[0,:])|set(labs[-1,:])|set(labs[:,0])|set(labs[:,-1]);outside.discard(0)
 return mask|((labs>0)&~np.isin(labs,list(outside)))''')
p.write_text(t)
