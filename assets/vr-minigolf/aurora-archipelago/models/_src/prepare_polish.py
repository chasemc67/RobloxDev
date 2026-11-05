"""One-time backups and source edits. Plain Python; no Blender process."""
from pathlib import Path
import shutil,json,hashlib
S=Path(__file__).resolve().parent;D=S.parents[1]
def backup(p):
    q=p.with_name(p.stem+'_prepolish'+p.suffix)
    if p.exists() and not q.exists():shutil.copy2(p,q)
for b in ['props_batch1','props_batch3']:
    for p in (S/b).iterdir():
        if p.suffix in ['.py','.json','.md'] and '_prepolish' not in p.stem and 'polish' not in p.stem:backup(p)
for p in [D/'models/props_batch1_manifest.json',D/'models/props_batch3_manifest.json',D/'models/fitcheck_props_batch1.txt',D/'models/fitcheck_props_batch3.txt']:backup(p)
hashfile=S/'polish_fbx_baseline.json'
if not hashfile.exists():hashfile.write_text(json.dumps({str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (D/'models/fbx').rglob('*.fbx')},indent=2))
print('Backups and FBX baseline saved.')
