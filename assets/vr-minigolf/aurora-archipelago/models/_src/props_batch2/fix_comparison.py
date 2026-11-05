from pathlib import Path
import shutil
S=Path(__file__).resolve().parent;D=S.parents[2];bk=S/'_backup_comparison';bk.mkdir(exist_ok=True)
for p in [S/'summary.md',D/'models/README.md']:
 if p.exists():shutil.copy2(p,bk/p.name)
for p in (D/'models/previews/props_batch2').glob('silhouette_compare*'):shutil.copy2(p,bk/p.name)
p=S/'finalize_batch2.py';t=p.read_text().replace('scale=source.width/1600','scale=source.height/1134');p.write_text(t)
