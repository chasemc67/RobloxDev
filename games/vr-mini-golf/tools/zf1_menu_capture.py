"""Capture the actual loaded menu, preserving simulator viewport evidence."""
import sys,json,io,base64
from pathlib import Path
from PIL import Image
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Play'
code='''local g=game.Players.LocalPlayer.PlayerGui:WaitForChild('GolfMenu',30)
game.ContentProvider:PreloadAsync({g})
local r={viewport={workspace.CurrentCamera.ViewportSize.X,workspace.CurrentCamera.ViewportSize.Y},frames={},aurora={}}
for _,p in g:GetDescendants() do
 if p:IsA('ImageLabel') or p:IsA('ImageButton') then
  if p.Name=='Frame' then table.insert(r.frames,{image=p.Image,loaded=p.IsLoaded,slice=tostring(p.SliceCenter),scale=p.SliceScale,size={p.AbsoluteSize.X,p.AbsoluteSize.Y}}) end
  if p.Image=='rbxassetid://119746292850007' then table.insert(r.aurora,{path=p:GetFullName(),loaded=p.IsLoaded,size={p.AbsoluteSize.X,p.AbsoluteSize.Y}}) end
 end
end return game.HttpService:JSONEncode(r)'''
raw=s.luau(code,'Client',timeout=90);r=json.loads(raw);print(raw)
assert len(r['frames'])==1 and r['frames'][0]['loaded']
name=sys.argv[1];Path('playtests/stage-zf1/'+name+'.json').write_text(raw+'\n')
out=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':'zf1-'+name}})
i=next(x for x in out['result']['content'] if x.get('type')=='image')
Image.open(io.BytesIO(base64.b64decode(i['data']))).save('logs/stages/zf1-'+name+'.png')
