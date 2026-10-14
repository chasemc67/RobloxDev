"""Stage au7 evidence helpers (copy of au6_stage). All writes are scoped to the selected course."""
import base64,io,json,sys
from pathlib import Path
from run_playtests import Studio

def fetch(s,code,var):
 n=int(s.luau(code,timeout=600))
 return ''.join(json.loads(s.luau('return game.HttpService:JSONEncode(%s:sub(%d,%d))'%(var,i+1,i+40000))) for i in range(0,n,40000))

def main():
 action,course=sys.argv[1:3]; folder={'aurora':'CourseAurora','lg':'Course'}[course]
 out=Path('playtests/stage-au7');out.mkdir(parents=True,exist_ok=True)
 s=Studio();assert s.mode()[0]=='Edit'
 assert s.luau('return workspace:GetAttribute("PlaceRole")')=={'aurora':'aurora_archipelago','lg':'lantern_grove'}[course]
 if action=='scan':
  raw=fetch(s,Path('tools/zf1_zscan.luau').read_text(),'_G.ZF1ScanJSON');r=json.loads(raw)
  (out/('zscan-'+sys.argv[3]+'.json')).write_text(raw+'\n')
  hits=out/'model-bot-mesh-hits.json'; prior=json.loads(hits.read_text()) if hits.exists() else {}
  prior[sys.argv[3]]=r['modelBotMeshHits'];hits.write_text(json.dumps(prior)+'\n');print(r['counts']);print(r['reviewCounts'])
 elif action=='apply':
  raw=fetch(s,'local r=require(game.ServerStorage.CourseBuilder:Clone()).ApplyVisualSeparation(workspace.'+folder+') _G.ZF2Fix=game.HttpService:JSONEncode(r) return #_G.ZF2Fix','_G.ZF2Fix')
  (out/'fixes.json').write_text(raw+'\n');r=json.loads(raw);print({k:len(v) if isinstance(v,list) else v for k,v in r.items()})
 elif action=='inventory':
  code=Path('tools/zf1_capture_state.py').read_text().split("code='''",1)[1].split("'''",1)[0]
  code=code.replace('material=p.Material.Name,', 'material=p.Material.Name,group=p.CollisionGroup,anchored=p.Anchored,customPhysics=p.CustomPhysicalProperties and {p.CustomPhysicalProperties.Density,p.CustomPhysicalProperties.Friction,p.CustomPhysicalProperties.Elasticity,p.CustomPhysicalProperties.FrictionWeight,p.CustomPhysicalProperties.ElasticityWeight} or false,')
  raw=fetch(s,code,'_G.ZF1Inventory');(out/('inventory-'+sys.argv[3]+'.json')).write_text(raw+'\n');print('inventory saved')
 elif action=='verify':
  a=json.loads((out/'inventory-before.json').read_text());b=json.loads((out/'inventory-after.json').read_text())
  keys=('path','cf','size','collide','query','touch','physics','group','anchored','customPhysics')
  def canon(r):return sorted(json.dumps({k:p[k] for k in keys},sort_keys=True) for p in r['parts'] if p['collide'] or p['query'] or p['touch'] or any(t.startswith('Golf') for t in p.get('tags',[])))
  assert canon(a)==canon(b),'collider mismatch'
  assert sorted(x['path'] for x in a['placeholders'])==sorted(x['path'] for x in b['placeholders']),'placeholder mismatch'
  r={'identicalColliders':sum(p['collide'] for p in a['parts']),'identicalGameplayParts':sum(p['collide'] or p['query'] or p['touch'] or any(t.startswith('Golf') for t in p.get('tags',[])) for p in a['parts']),'placeholdersBefore':len(a['placeholders']),'placeholdersAfter':len(b['placeholders'])};(out/'collider-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
 elif action=='screen':
  from PIL import Image
  views=out/'camera.json'
  if not views.exists():
   scan=json.loads((out/'zscan-before.json').read_text());hits=[h for h in scan['hits']['coplanarFaces'] if h['reviewClass']=='exposed-planar-candidate'];h=max(hits,key=lambda h:h['minOverlap']);target=h['centerA'];pos=[target[0]+12,target[1]+10,target[2]+15];views.write_text(json.dumps({'pos':pos,'target':target,'hit':h},indent=2))
  v=json.loads(views.read_text());r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':'zf2-'+course+'-'+sys.argv[3],'camera_position':v['pos'],'look_at_position':v['target']}})
  img=next(c for c in r['result']['content'] if c.get('type')=='image');Image.open(io.BytesIO(base64.b64decode(img['data']))).save('logs/stages/au7-'+sys.argv[3]+'.png')
if __name__=='__main__':main()
