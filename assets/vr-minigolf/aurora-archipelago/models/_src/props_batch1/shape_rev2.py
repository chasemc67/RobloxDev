from pathlib import Path
p=Path('models/_src/props_batch1/gen_batch1.py');s=p.read_text().replace('dx=u*w*.77','dx=u*w*.58').replace('y+h*(.82+.10*(1-abs(u)*2))','y+h*(.72+.03*(1-abs(u)*2))').replace('side*w*.075,end[1]+h*.045','side*w*.13,end[1]+h*.16').replace('rr=min(w*.12,h*.045)','rr=min(w*.075,h*.035)').replace("rounded(p,'Snow',[x,y+20,z],[18,1.3,18])","mound(p,'Snow',[x,y+21,z],[17.5,1.3,17.5],n=14)")
p.write_text(s)
