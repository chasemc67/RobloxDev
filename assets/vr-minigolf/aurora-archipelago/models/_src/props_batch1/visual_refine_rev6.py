from pathlib import Path
p=Path('models/_src/props_batch1/rev6.py');t=p.read_text().replace('  start=len(q.g[col][0]);split=',"  g.tube(q,col,[0,base+.49*h,0],[0,base+.60*h,0],.05*h,.045*h,n=8)\n  start=len(q.g[col][0]);split=")
t=t.replace('def blob(mat,c,size):','def blob(mat,c,size,core=False):').replace("n=4 if mat=='CoralMint' else 8;steps=2 if mat=='CoralMint' else 4","n=4 if core else 8;steps=2 if core else 6").replace('tip[2]-d*.19','tip[2]+d*.27').replace('[w*.13,h*.08,d*.22])','[w*.13,h*.08,d*.22],core=True)').replace('Rev4 files backed up','Rev5 files backed up')
p.write_text(t)
