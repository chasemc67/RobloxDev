"""Local stage-al edit snapshots and original Playtest Bot coplanar scan."""
import json,time,sys
from pathlib import Path
from run_playtests import Studio
s=Studio();out=Path('playtests/stage-al');out.mkdir(exist_ok=True)
label=sys.argv[1]
assert s.mode()[0]=='Edit'
pre=json.loads(s.luau('return game.HttpService:JSONEncode({placeId=game.PlaceId,gameId=game.GameId,networkClient=game:FindFirstChildOfClass("NetworkClient")~=nil,role=workspace:GetAttribute("PlaceRole")})'))
assert pre['placeId']==0 and not pre['networkClient']
(out/(label+'-preflight.json')).write_text(json.dumps(pre,indent=2))
code='''local rows={} for _,p in workspace.CourseSugarloaf:GetDescendants() do if p:IsA("BasePart") and p.CanCollide then
 local phys=p.CurrentPhysicalProperties
 table.insert(rows,{path=p:GetFullName(),wall=p:GetAttribute("WallId"),piece=p:GetAttribute("PieceId"),cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},physics={phys.Density,phys.Friction,phys.Elasticity,phys.FrictionWeight,phys.ElasticityWeight}})
end end _G.ALExport=game.HttpService:JSONEncode(rows) return #_G.ALExport'''
n=int(s.luau(code));raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ALExport:sub(%d,%d))'%(a+1,a+45000))) for a in range(0,n,45000))
(out/(label+'-colliders.json')).write_text(raw)
s.luau(Path('logs/stages/al-inputs/scan-all-rail-tops.luau').read_text())
for _ in range(100):
 if s.luau('return _G.RailAllFaces.done')=='true':break
 time.sleep(.2)
n=int(s.luau('_G.ALExport=game.HttpService:JSONEncode(_G.RailAllFaces.rows) return #_G.ALExport'))
raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ALExport:sub(%d,%d))'%(a+1,a+45000))) for a in range(0,n,45000))
(out/(label+'-coplanar.json')).write_text(raw)
print(label,'coplanar',len(json.loads(raw)))
s.luau('_G.ALExport=nil _G.RailAllFaces=nil _G.RailAllPairs=nil return "cleared"')
