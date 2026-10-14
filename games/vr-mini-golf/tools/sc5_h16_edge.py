"""Stage sc5: H16 sinkhole edge check in Play (Server). Ball-sized physics spheres (r 0.08) are rolled slowly over
the square sinkhole edge from 4 sides and (one ball at a time) 4 diagonals, and set at rest just inside / just outside the edge; each is
reported as dropped (fell below the felt) or not. The visual h16_sinkhole_rim must not stop anything (collide off).
  PYTHONPATH=tools python3 tools/sc5_h16_edge.py
"""
import json, time
from sc5_util import OUT
import os
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
from run_playtests import Studio

LUA = r'''
local course=workspace:FindFirstChild('CourseSugarloaf')
local rim=course.Hole16.StageAFVisuals.h16_sinkhole_rim
local rimFlags={} for _,p in rim:GetDescendants() do if p:IsA('BasePart') then table.insert(rimFlags,{p.Name,p.CanCollide,p.CanQuery,p.CanTouch}) end end
-- sinkhole centre from the GeodeRim frame; felt top by ray at 1.6 studs out
local frame for _,p in rim:GetDescendants() do if p.Name:match('GeodeRim') then frame=p end end
local c=frame.Position
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Exclude rp.FilterDescendantsInstances={rim}
local hf=workspace:Raycast(Vector3.new(c.X+1.6,c.Y+3,c.Z),Vector3.new(0,-6,0),rp)
local feltY=hf and hf.Position.Y or c.Y
local hc=workspace:Raycast(Vector3.new(c.X,c.Y+3,c.Z),Vector3.new(0,-6,0),rp)
local tests={}
local function ball(pos,vel,name)
 local b=Instance.new('Part') b.Shape=Enum.PartType.Ball b.Size=Vector3.new(0.16,0.16,0.16) b.Name='SC5EdgeBall_'..name
 b.CustomPhysicalProperties=PhysicalProperties.new(1,0.35,0.3) b.Anchored=false b.CanCollide=true b.CFrame=CFrame.new(pos)
 b.Parent=workspace b.AssemblyLinearVelocity=vel
 table.insert(tests,{name=name,part=b,start=pos})
end
local up=Vector3.new(0,0.08+0.01,0)
for _,d in {Vector3.new(1,0,0),Vector3.new(-1,0,0),Vector3.new(0,0,1),Vector3.new(0,0,-1)} do
 local start=Vector3.new(c.X,feltY,c.Z)+d*1.8+up
 ball(start,-d*1.2,string.format('roll_%d_%d',d.X*10,d.Z*10))
end
task.wait(4)
-- diagonals one at a time (two balls on one diagonal meet at the centre)
for _,d in {Vector3.new(1,0,1).Unit,Vector3.new(-1,0,-1).Unit,Vector3.new(1,0,-1).Unit,Vector3.new(-1,0,1).Unit} do
 local start=Vector3.new(c.X,feltY,c.Z)+d*1.8+up
 ball(start,-d*1.2,string.format('diag_alone_%d_%d',math.round(d.X*10),math.round(d.Z*10)))
 local t=tests[#tests] local p0=t.part
 task.wait(3) t.mid=p0.Position
end
for _,r in {0.9,1.3} do for _,d in {Vector3.new(1,0,0),Vector3.new(0,0,-1)} do
 ball(Vector3.new(c.X,feltY,c.Z)+d*r+up,Vector3.zero,string.format('rest_%.1f_%d_%d',r,d.X,d.Z)) end end
task.wait(4)
local out={centre={c.X,c.Y,c.Z},feltY=feltY,centreHit=hc and hc.Instance:GetFullName() or 'none',rim=rimFlags,results={}}
for _,t in tests do local p=t.part.Position
 table.insert(out.results,{name=t.name,dropped=p.Y<feltY-0.3,endY=p.Y,endDist=(Vector3.new(p.X,0,p.Z)-Vector3.new(c.X,0,c.Z)).Magnitude})
 t.part:Destroy() end
return game.HttpService:JSONEncode(out)
'''

if __name__ == '__main__':
    s = Studio()
    s.start_play(); time.sleep(5)
    try:
        r = json.loads(s.luau(LUA, 'Server', timeout=120))
    finally:
        s.stop_play()
    (OUT / 'h16-edge.json').write_text(json.dumps(r, indent=1) + '\n')
    print('feltY', r['feltY'], 'centreHit', r['centreHit']); print('rim flags', r['rim'])
    for x in r['results']: print(x)
