"""Read-only public metadata lookup; never creates or uploads assets."""
import concurrent.futures,json,urllib.request
from pathlib import Path
rows=[x for x in json.loads(Path('playtests/stage-af/audit.json').read_text())['meshes'] if 'StageAFVisuals' in x['name']]
def get(m):
 aid=m['MeshId'].split('//')[-1]
 try:
  with urllib.request.urlopen('https://economy.roblox.com/v2/assets/'+aid+'/details',timeout=20) as f:d=json.load(f)
  return {'id':aid,'name':m['name'],'creator':d.get('Creator'),'created':d.get('Created'),'type':d.get('AssetTypeId')}
 except Exception as e:return {'id':aid,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:r=list(pool.map(get,rows))
Path('playtests/stage-af/asset-metadata.json').write_text(json.dumps(r,indent=2)+'\n')
print('meshes',len(r),'MetavrseBuilder',sum(x.get('creator',{}).get('Id')==1818120139 for x in r),'errors',[x for x in r if 'error' in x])
