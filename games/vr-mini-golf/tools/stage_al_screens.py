"""Final local Edit visual evidence. Images stay uncommitted."""
import base64,json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
out=Path('playtests/stage-al/screens');out.mkdir(exist_ok=True)
views={
 'h14-dock':'local m=workspace.CourseSugarloaf.Hole14.StageAJVisuals.h14_loading_dock local cf=m:GetBoundingBox() local target=cf.Position local c=workspace.CurrentCamera c.CFrame=CFrame.lookAt(target+Vector3.new(12,9,12),target) c.Focus=CFrame.new(target) return true',
 'h15-rails':'local h=workspace.CourseSugarloaf.Hole15 local cf=CFrame.new(h:GetAttribute("HoleOrigin"))*CFrame.Angles(0,math.rad(h:GetAttribute("HoleYaw")),0) local target=cf:PointToWorldSpace(Vector3.new(0,-1,-24)) local c=workspace.CurrentCamera c.CFrame=CFrame.lookAt(target+Vector3.new(17,16,-18),target) c.Focus=CFrame.new(target) return true'}
for name,code in views.items():
 s.luau(code)
 r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':'al-'+name}})
 img=next(c for c in r['result']['content'] if c.get('type')=='image')
 (out/(name+'.jpg')).write_bytes(base64.b64decode(img['data']))
 print(name)
