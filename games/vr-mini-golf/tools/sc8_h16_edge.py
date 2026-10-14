"""Stage sc8: H16 sinkhole edge test in Play (Server), extended from sc5_h16_edge.py.
Ball-sized physics spheres (r 0.08, the sc5 test ball) on the deck around the sinkhole:
  * opening: measured with down-rays (0.005 steps) along the 4 axes and 4 diagonals (felt edge = first felt hit)
  * the sc5 set: 4 axis rolls + 4 diagonal rolls (one at a time), rest 0.9 (drop) / 1.3 (stay)
  * rest scan: balls set at rest at distance d (axis +x,-x,+z,-z; and the 4 corners at d on both axes), d 0.80..1.30
    -> the drop/stay threshold for the current opening
  * slow angled putts at the frame edge: balls rolled along chords that pass between the frame's inner edge and the
    old 1.2 opening (offset o from the centre line, angle a to the edge, speed v). Each records whether it dropped and
    where its centre was when it fell below the felt (Chebyshev distance in the frame's local axes). A drop counts as
    "outside the frame" when that point is beyond the frame's inner edge (the GeodeRim inner half-width).
  PYTHONPATH=tools python3 tools/sc8_h16_edge.py OUT.json [frameInner]
"""
import json, sys, time, os
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
from run_playtests import Studio

LUA = r'''
local FRAME_INNER=__INNER__
local course=workspace.CourseSugarloaf
local rim=course.Hole16.StageAFVisuals.h16_sinkhole_rim
local rimFlags={} for _,p in rim:GetDescendants() do if p:IsA('BasePart') then table.insert(rimFlags,{p.Name,p.CanCollide,p.CanQuery,p.CanTouch}) end end
local frame for _,p in rim:GetDescendants() do if p.Name:match('GeodeRim') then frame=p end end
local c=frame.Position
local F=CFrame.new(c)*frame.CFrame.Rotation -- local axes of the square
local balls=Instance.new('Folder') balls.Name='SC8EdgeBalls' balls.Parent=workspace
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances={rim,balls}
local hf=workspace:Raycast(Vector3.new(c.X+1.6,c.Y+3,c.Z),Vector3.new(0,-6,0),rp)
local feltY=hf.Position.Y
-- measured opening along 8 directions
local opening={}
for _,d in {{1,0},{-1,0},{0,1},{0,-1},{1,1},{-1,-1},{1,-1},{-1,1}} do
 local dir=(F.Rotation*Vector3.new(d[1],0,d[2]))
 local edge
 for i=0,300 do local t=0.4+i*0.005 local q=Vector3.new(c.X,feltY+1,c.Z)+dir*t
  local h=workspace:Raycast(q,Vector3.new(0,-1.2,0),rp) if h and math.abs(h.Position.Y-feltY)<0.02 then edge=t break end end
 table.insert(opening,{dir=d,edgeAlongAxisOrCheb=edge})
end
local up=Vector3.new(0,0.08+0.01,0)
local tests={}
local function ball(pos,vel,name,extra)
 local b=Instance.new('Part') b.Shape=Enum.PartType.Ball b.Size=Vector3.new(0.16,0.16,0.16) b.Name='SC8EdgeBall_'..name
 b.CustomPhysicalProperties=PhysicalProperties.new(1,0.35,0.3) b.Anchored=false b.CanCollide=true b.CFrame=CFrame.new(pos)
 b.Parent=workspace b.AssemblyLinearVelocity=vel
 local t={name=name,part=b,start=pos,lastAbove=pos,extra=extra} table.insert(tests,t) return t
end
local hb=game:GetService('RunService').Heartbeat:Connect(function()
 for _,t in tests do if t.part.Parent and not t.fell then local p=t.part.Position
  if p.Y<feltY-0.05 then t.fell=true t.fallAt=t.lastAbove else t.lastAbove=p end end end end)
local function clear() for _,t in tests do if t.part.Parent then t.endPos=t.part.Position t.part.Parent=nil end end end
local function L(x,z) return (F*CFrame.new(x,0,z)).Position end
local function at(x,z) local w=L(x,z) return Vector3.new(w.X,feltY,w.Z)+up end
local function dirW(x,z) return (F.Rotation*Vector3.new(x,0,z)) end
-- sc5 set
for _,d in {{1,0},{-1,0},{0,1},{0,-1}} do
 ball(at(d[1]*1.8,d[2]*1.8),-dirW(d[1],d[2])*1.2,string.format('roll_%d_%d',d[1],d[2]),{set='sc5'}) task.wait(3) clear() end
for _,d in {{1,1},{-1,-1},{1,-1},{-1,1}} do local u=Vector3.new(d[1],0,d[2]).Unit
 ball(at(u.X*1.8,u.Z*1.8),-dirW(u.X,u.Z)*1.2,string.format('diag_alone_%d_%d',d[1],d[2]),{set='sc5'}) task.wait(3) clear() end
for _,r in {0.9,1.3} do for _,d in {{1,0},{0,-1}} do ball(at(d[1]*r,d[2]*r),Vector3.zero,string.format('rest_%.1f_%d_%d',r,d[1],d[2]),{set='sc5'}) end end
task.wait(3) clear()
-- rest scan (one distance per batch; 4 axis balls + 4 corner balls far apart)
for i=0,20 do local r=0.80+i*0.025
 for _,d in {{1,0},{-1,0},{0,1},{0,-1}} do ball(at(d[1]*r,d[2]*r),Vector3.zero,string.format('scan_axis_%.3f_%d_%d',r,d[1],d[2]),{set='scanAxis',d=r}) end
 task.wait(1.6)
 for _,d in {{1,1},{-1,-1},{1,-1},{-1,1}} do ball(at(d[1]*r,d[2]*r),Vector3.zero,string.format('scan_corner_%.3f_%d_%d',r,d[1],d[2]),{set='scanCorner',d=r}) end
 task.wait(1.6)
 clear()
end
-- slow angled putts across the frame edge: chord at offset o (local z = side*o), heading angle a from the +x/-x axis
-- two at a time on opposite sides, moving in opposite directions (paths >= 1.9 apart)
for _,o in {0.97,1.0,1.05,1.1,1.15,1.2} do for _,a in {0,15,30} do for _,v in {0.6,1.2} do
 for _,side in {1,-1} do
  local ar=math.rad(a) local dx,dz=side*math.cos(ar),-side*math.sin(ar) -- heading along +-x, angled toward the hole
  -- the path crosses local (0, side*o); start 2.2 back along the heading
  local sx,sz=-dx*2.2,side*o-dz*2.2
  ball(at(sx,sz),dirW(dx,dz)*v,string.format('putt_s%d_o%.2f_a%d_v%.1f',side,o,a,v),{set='putt',o=o,a=a,v=v,side=side})
 end
 task.wait(4.5)
 clear()
end end end
task.wait(1)
hb:Disconnect()
local out={centre={c.X,c.Y,c.Z},feltY=feltY,frameInner=FRAME_INNER,opening=opening,rim=rimFlags,results={}}
for _,t in tests do local p=t.endPos or t.part.Position
 local fl=t.fallAt and F:PointToObjectSpace(t.fallAt)
 local cheb=fl and math.max(math.abs(fl.X),math.abs(fl.Z))
 table.insert(out.results,{name=t.name,set=t.extra.set,d=t.extra.d,o=t.extra.o,a=t.extra.a,v=t.extra.v,dropped=t.fell==true or p.Y<feltY-0.3,endY=p.Y,
  endDist=(Vector3.new(p.X,0,p.Z)-Vector3.new(c.X,0,c.Z)).Magnitude,fallLocal=fl and {fl.X,fl.Z},fallCheb=cheb,
  outsideFrame=cheb~=nil and cheb>FRAME_INNER})
 t.part:Destroy() end
balls:Destroy()
return game.HttpService:JSONEncode(out)
'''


if __name__ == '__main__':
    out = sys.argv[1]; inner = sys.argv[2] if len(sys.argv) > 2 else '1.0'
    s = Studio()
    s.start_play(); time.sleep(5)
    try:
        r = json.loads(s.luau(LUA.replace('__INNER__', inner), 'Server', timeout=600))
    finally:
        s.stop_play()
    res = r['results']
    def grp(st): return [x for x in res if x['set'] == st]
    summ = {'opening': r['opening'], 'feltY': r['feltY'], 'rimFlags': r['rim'],
            'sc5': {x['name']: x['dropped'] for x in grp('sc5')}}
    for st in ('scanAxis', 'scanCorner'):
        by = {}
        for x in grp(st): by.setdefault(round(x['d'], 3), []).append(x['dropped'])
        summ[st] = {str(k): '%d/%d' % (sum(v), len(v)) for k, v in sorted(by.items())}
        summ[st + 'MaxAllDrop'] = max([k for k, v in by.items() if all(v)], default=None)
        summ[st + 'MinAllStay'] = min([k for k, v in by.items() if not any(v)], default=None)
    p = grp('putt')
    summ['putts'] = len(p); summ['puttDrops'] = sum(x['dropped'] for x in p)
    summ['outsideDrops'] = sum(1 for x in p if x['dropped'] and x['outsideFrame'])
    summ['maxFallCheb'] = max([x['fallCheb'] for x in res if x.get('fallCheb')], default=None)
    summ['puttDropsByOffset'] = {}
    for x in p: k = '%.2f' % x['o']; d = summ['puttDropsByOffset'].setdefault(k, [0, 0]); d[0] += x['dropped']; d[1] += 1
    r['summary'] = summ
    Path = __import__('pathlib').Path
    Path(out).write_text(json.dumps(r, indent=1) + '\n')
    print(json.dumps(summ, indent=1))
