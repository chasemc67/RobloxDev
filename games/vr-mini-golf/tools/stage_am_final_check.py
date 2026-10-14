"""Final read-only local Edit validation and targeted screenshots; never save/publish."""
import json,base64,hashlib
from pathlib import Path
from holes_to_lua import to_lua
from run_playtests import Studio,long_string
OUT=Path('playtests/stage-am')
s=Studio();assert s.mode()[0]=='Edit'
pre=json.loads(s.luau('return game.HttpService:JSONEncode({PlaceId=game.PlaceId,GameId=game.GameId,NetworkClient=game:FindFirstChildOfClass("NetworkClient")~=nil,PlaceRole=workspace:GetAttribute("PlaceRole"),GolfTestMode=workspace:GetAttribute("GolfTestMode"),SimulateVR=workspace:GetAttribute("SimulateVR")})'))
assert pre['PlaceId']==0 and not pre['NetworkClient'] and pre['PlaceRole']=='aurora_archipelago'
checks={}
for p in sorted(Path('src').rglob('*.luau')):
 names=list(p.relative_to('src').with_suffix('').parts)
 names[-1]=names[-1].removesuffix('.server').removesuffix('.client')
 code='local p=game for _,n in '+to_lua(names)+' do p=assert(p:FindFirstChild(n),n) end return p.Source=='+long_string(p.read_text())
 checks[str(p)]=s.luau(code)=='true'
print('mismatches',[k for k,v in checks.items() if not v],flush=True)
assert all(checks.values())
(OUT/'final-source-check.json').write_text(json.dumps({'state':pre,'sources':checks},indent=2)+'\n')
print('source equality',len(checks),flush=True)
