import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
from collections import deque
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
 return mask|((labs>0)&~np.isin(labs,list(outside)))
s=Path(__file__).resolve().parent;d=s.parents[2];m=d/'models';pv=m/'previews/props_batch1'
assert hashlib.md5((d/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
audit=json.loads((s/'rev6_audit.json').read_text());assert audit['all_pass']
assert json.loads((s/'fitcheck_report.json').read_text())['all_pass']
assert json.loads((s/'fbx_validation.json').read_text())['all_pass']
manifest=json.loads((m/'props_batch1_manifest.json').read_text());ids=set(audit['changed']);parts=[p for p in manifest['parts'] if p['id'] in ids]
assert len(parts)==18 and all(p['tris']<3000 for p in parts)
for p in parts:
 assert (m/p['fbx']).exists() and (pv/(p['id']+'_34.png')).exists()
for p,h in json.loads((s/'rev6_unchanged.json').read_text()).items():assert hashlib.sha256((d/p).read_bytes()).hexdigest()==h
front=[]
for id in ['h07_coral_w2','h08_coral_1','h08_giant_coral']:
 mask=np.asarray(Image.open(pv/(id+'_front.png')).convert('RGBA'))[:,:,3]>127
 labs,n=label(mask);sizes=np.bincount(labs.ravel())[1:];large=sum(sizes>5)
 holes=int((binary_fill_holes(mask)&~mask).sum())
 assert large==1,(id,'disconnected outline',sizes.tolist())
 assert holes<10,(id,'see-through holes',holes)
 front.append(dict(id=id,connected_components=int(large),interior_hole_pixels=holes))
for n in [7,8]:assert (pv/f'h{n:02d}_34.png').exists() and (pv/f'silhouette_compare_h{n:02d}.jpg').exists()
for p in [m/'README.md',s/'summary.md']:assert 'Coral rev6' in p.read_text(encoding='utf-8')
assert 'ALL PASS: YES' in (m/'fitcheck_props_batch1.txt').read_text()
audit['front_silhouette_checks']=front;audit['tris_range']=[min(p['tris'] for p in parts),max(p['tris'] for p in parts)]
(s/'rev6_audit.json').write_text(json.dumps(audit,indent=2))
(s/'done_rev6.flag').write_text('Coral rev6 COMPLETE: 18 exports, previews and documentation updated. Fitcheck and FBX reimport ALL PASS. Front silhouettes connected with no see-through holes. Unrelated FBX and manifest records preserved. holes.json MD5 verified. See rev6_audit.json and summary.md.\n')
print(json.dumps(dict(done=True,tris_range=audit['tris_range'],front=front)))
