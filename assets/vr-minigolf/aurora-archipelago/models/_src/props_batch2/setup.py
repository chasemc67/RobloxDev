from pathlib import Path
import shutil
S=Path('models/_src/props_batch2');B=S.parent/'props_batch1'
for name in ['gen_batch1.py','build_batch1.py','fitcheck_batch1.py','verify_batch1.py']:
 dest=S/name.replace('batch1','batch2')
 if dest.exists():
  (S/'_backup').mkdir(exist_ok=True);shutil.copy2(dest,S/'_backup'/dest.name)
 t=(B/name).read_text().replace('props_batch1','props_batch2').replace('batch=1','batch=2').replace('[1,2,3,5,7,8]','[9,10,11,12,13,15,16,17]')
 dest.write_text(t)
t=(S/'gen_batch2.py').read_text();t=t[:t.index('# H1: silhouette')]
(S/'geometry.py').write_text(t)
