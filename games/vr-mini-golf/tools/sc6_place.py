"""Stage sc6: TRADING POST board restore (from place v23) and H16 sinkhole rim crystals -> Neon.
  PYTHONPATH=tools python3 tools/sc6_place.py v23            (game:GetObjects of place version 23 -> _G.SC6V23)
  PYTHONPATH=tools python3 tools/sc6_place.py board          (restore trading_post_deck__MintWhite/__PepRed, rail1 check)
  PYTHONPATH=tools python3 tools/sc6_place.py rim            (h16_sinkhole_rim__GeodeRim Neon, crystal_cue colour)
Board: mesh/texture template = v23 ServerStorage.SugarloafKit.trading_post_deck parts; Workspace pose/size =
the v23 Workspace inventory (playtests/stage-sc5/inventory-before.json), checked against live deck pivot * v23
library CFrame. Visual only (collide/query/touch off). The library copy gets the v23 library parts too.
"""
import json, sys
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc6'

V23 = r'''
local res=game:GetObjects('https://assetdelivery.roblox.com/v1/asset/?id=124440050576723&version=23')
_G.SC6V23=res local n=0 for _,x in res do if x.ClassName=='ServerStorage' then n=#x:GetChildren() end end
_G.SC5Out='v23 roots '..#res..' ServerStorage children '..n return #_G.SC5Out
'''

BOARD = r'''
local rows=__ROWS__
local ss for _,x in assert(_G.SC6V23,'load v23 first') do if x.ClassName=='ServerStorage' then ss=x end end
local lib23=ss.SugarloafKit.trading_post_deck
local deck=workspace.CourseSugarloaf.Kit.hole_dressing.trading_post_deck
local inner=deck:FindFirstChild('trading_post_deck') or deck
local lib=game.ServerStorage.SugarloafKit.trading_post_deck
local ref for _,p in inner:GetChildren() do if p:IsA('BasePart') then ref=p break end end
local rep={placed={},library={},rail={}}
for _,r in rows do
 local name=r.path:match('([^%.]+)$')
 assert(not inner:FindFirstChild(name),'already present '..name)
 local t=assert(lib23:FindFirstChild(name),'v23 template missing '..name)
 local p=t:Clone() for _,c in p:GetChildren() do if not c:IsA('SurfaceAppearance') then c:Destroy() end end
 p.CFrame=CFrame.new(table.unpack(r.cf)) p.Size=Vector3.new(table.unpack(r.size))
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
 if ref then p.CollisionGroup=ref.CollisionGroup for k,v in ref:GetAttributes() do if k:sub(1,3)~='ZF1' and k~='SC5Source' then p:SetAttribute(k,v) end end end
 p:SetAttribute('SC6Source','place v23 SugarloafKit.trading_post_deck.'..name)
 -- pose check: v23 world pose = live deck pivot * v23 library CFrame (library pivot is the origin)
 local expect=inner:GetPivot()*t.CFrame
 p.Parent=inner
 table.insert(rep.placed,{path=p:GetFullName(),cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},texture=p.TextureID,mesh=p.MeshId,
  poseDeltaVsPivot=(p.Position-expect.Position).Magnitude,rotMatches=p.CFrame.Rotation:FuzzyEq(expect.Rotation,1e-3)})
 -- library copy (persistence): v23 library part as is
 if not lib:FindFirstChild(name) then local q=t:Clone() q.CanCollide=false q.CanQuery=false q.CanTouch=false q.Parent=lib
  table.insert(rep.library,q:GetFullName()) end
end
-- H1 rail1 clearance: sample each board part's box (5x5x3 grid) against Rail_rail1 / RailCap_rail1 boxes
local rails={} for _,q in workspace.CourseSugarloaf.Hole1:GetDescendants() do if q:IsA('BasePart') and q.Name:match('rail1$') then table.insert(rails,q) end end
local function boxDist(pt,q) local l=q.CFrame:PointToObjectSpace(pt) local h=q.Size/2
 local d=Vector3.new(math.max(math.abs(l.X)-h.X,0),math.max(math.abs(l.Y)-h.Y,0),math.max(math.abs(l.Z)-h.Z,0)) return d.Magnitude end
for _,r in rep.placed do local p=inner:FindFirstChild(r.path:match('([^%.]+)$')) local best,bq=math.huge,nil
 for ix=0,4 do for iy=0,2 do for iz=0,4 do
  local pt=p.CFrame*Vector3.new((ix/4-0.5)*p.Size.X,(iy/2-0.5)*p.Size.Y,(iz/4-0.5)*p.Size.Z)
  for _,q in rails do local d=boxDist(pt,q) if d<best then best,bq=d,q end end end end end
 table.insert(rep.rail,{part=p.Name,minDist=best,rail=bq and bq:GetFullName(),rails=#rails})
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

RIM = r'''
local pink=Color3.new(__PINK__)
local rep={parts={}}
local targets={workspace.CourseSugarloaf.Hole16.StageAFVisuals.h16_sinkhole_rim, game.ServerStorage.StageAFProps.h16_sinkhole_rim}
for _,m in targets do local p=m:FindFirstChild('h16_sinkhole_rim__GeodeRim')
 local before={material=p.Material.Name,color={p.Color.R,p.Color.G,p.Color.B}}
 p.Material=Enum.Material.Neon p.Color=pink p.CastShadow=false
 p.CanCollide=false p.CanQuery=false p.CanTouch=false
 if m:IsDescendantOf(workspace) then assert(p:GetAttribute('VisualQueryDisabled')==true,'VisualQueryDisabled missing') end
 p:SetAttribute('SC6Neon','placeholders_ph1 crystal_cue NeonPink')
 local flags={} for _,q in m:GetDescendants() do if q:IsA('BasePart') then table.insert(flags,{q.Name,q.CanCollide,q.CanQuery,q.CanTouch,q:GetAttribute('VisualQueryDisabled')}) end end
 table.insert(rep.parts,{path=p:GetFullName(),before=before,after={material=p.Material.Name,color={p.Color.R,p.Color.G,p.Color.B}},flags=flags})
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'v23':
        print(fetch(s, '_G.SC5Out', V23, timeout=600))
    elif a == 'board':
        rows = json.load(open('/tmp/sc6/board_v23.json'))
        raw = fetch(s, '_G.SC5Out', BOARD.replace('__ROWS__', to_lua(rows)))
        (OUT / 'board.json').write_text(raw + '\n'); print(json.dumps(json.loads(raw), indent=1))
    elif a == 'rim':
        man = json.load(open('/tmp/sc5/inspect_ph.json'))['crystal_cue']['meshes']
        pink = next(m['cols'][0] for m in man if m['name'] == 'crystal_cue__NeonPink')
        raw = fetch(s, '_G.SC5Out', RIM.replace('__PINK__', ','.join(str(v) for v in pink)))
        (OUT / 'h16-rim.json').write_text(raw + '\n'); print(json.dumps(json.loads(raw), indent=1))
