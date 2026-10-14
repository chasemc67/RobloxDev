#!/usr/bin/env python3
"""Native Stage am visual/timing evidence. LOCAL Play only; no save, publish, or raycasts."""
import base64
import json
import time
from pathlib import Path
from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'playtests/stage-am'
SCHEDULE = r'''
local RunService=game:GetService("RunService")
local Math=require(game.ReplicatedStorage.Golf.MoverMath:Clone())
local m=workspace.CourseAurora.Hole17:FindFirstChild("Mover_aurora_span",true)
local p=Math.fromModel(m)
local refs={TogglePart={},ToggleRibbon={},ToggleLamp={},ToggleLight={},ToggleSparkles={}}
local skins={}
for _,r in m:GetChildren() do if r:IsA("ObjectValue") and refs[r.Name] and r.Value then table.insert(refs[r.Name],r.Value) end end
for _,v in m:GetDescendants() do if v:IsA("BasePart") and v:GetAttribute("ToggleVisual") then table.insert(skins,v) end end
local out={samples={},durationRequested=20,alphaTolerance=0.04,profile=p,counts={},mismatches={}}
for k,v in refs do out.counts[k]=#v end out.counts.spanSkins=#skins
assert(#skins>0 and #refs.TogglePart>0 and #refs.ToggleRibbon>0 and #refs.ToggleLamp>0 and #refs.ToggleSparkles==3)
local begin=workspace:GetServerTimeNow()
repeat
 RunService.PostSimulation:Wait()
 local t=workspace:GetServerTimeNow()
 local alpha,state=Math.toggleVisual(p,t)
 local solid=Math.value(p,t)==1
 local row={elapsed=t-begin,time=t,phase=(t+(p.phase or 0))%p.period,state=state,solid=solid,alpha=alpha,colliders={},span={},ribbon={},lamps={},lights={},sparkles={}}
 local function bad(kind,name,actual,expected) table.insert(out.mismatches,{elapsed=t-begin,phase=row.phase,kind=kind,name=name,actual=actual,expected=expected}) end
 for _,v in refs.TogglePart do
  table.insert(row.colliders,{v.CanCollide,v.CanQuery,v.CanTouch})
  if v.CanCollide~=solid or v.CanQuery~=solid or v.CanTouch~=solid then bad("collider",v.Name,{v.CanCollide,v.CanQuery,v.CanTouch},solid) end
 end
 local function checkVisual(v,list)
  local base=v:GetAttribute("ManifestTransparency") or 0
  local expected=base+(1-base)*alpha
  table.insert(list,{name=v.Name,actual=v.Transparency,base=base,expected=expected})
  if math.abs(v.Transparency-expected)>0.04 then bad("alpha",v.Name,v.Transparency,expected) end
 end
 for _,v in skins do checkVisual(v,row.span) end
 for _,v in refs.ToggleRibbon do checkVisual(v,row.ribbon) end
 for _,v in refs.ToggleLamp do
  local color={v.Color.R,v.Color.G,v.Color.B}
  table.insert(row.lamps,{name=v.Name,color=color,material=v.Material.Name,transparency=v.Transparency})
  if solid and ((Vector3.new(v.Color.R,v.Color.G,v.Color.B)-Vector3.new(92/255,1,176/255)).Magnitude>0.01 or v.Material~=Enum.Material.Neon) then bad("mintLamp",v.Name,color,{92/255,1,176/255}) end
 end
 for _,v in refs.ToggleLight do
  local expected=state=="gone" and 0 or (solid and 1.5 or 0.6*(1-alpha))
  table.insert(row.lights,{name=v.Name,brightness=v.Brightness,expected=expected,color={v.Color.R,v.Color.G,v.Color.B}})
  if math.abs(v.Brightness-expected)>0.04 then bad("lampBrightness",v.Name,v.Brightness,expected) end
 end
 for _,v in refs.ToggleSparkles do
  table.insert(row.sparkles,v.Enabled)
  if v.Enabled~=(state=="fade_out") then bad("sparkles",v.Name,v.Enabled,state=="fade_out") end
 end
 table.insert(out.samples,row)
 task.wait(0.04)
until workspace:GetServerTimeNow()-begin>=20
out.elapsed=workspace:GetServerTimeNow()-begin
out.pass=#out.mismatches==0
_G.StageAMVisualJSON=game.HttpService:JSONEncode(out)
return #_G.StageAMVisualJSON
'''
AUDIT = r'''
local cs=game:GetService("CollectionService")
local out={models={},violations={},parts=0,weldErrors={}}
for _,m in workspace.CourseAurora:GetDescendants() do
 if m:IsA("Model") and (m:GetAttribute("StageAIVisual") or m:GetAttribute("StageAMVisual") or m:GetAttribute("AuroraVisual") or cs:HasTag(m,"StageAIVisual") or cs:HasTag(m,"StageAMVisual") or cs:HasTag(m,"AuroraVisual")) then
  local row={name=m.Name,path=m:GetFullName(),revision=m:GetAttribute("Revision"),parts=0}
  local mover=m.Parent.Name:sub(1,6)=="Mover_" and m.Parent or nil
  for _,v in m:GetDescendants() do if v:IsA("BasePart") then
   row.parts+=1 out.parts+=1
   if v.CanCollide or v.CanQuery or v.CanTouch or not v:GetAttribute("VisualQueryDisabled") then table.insert(out.violations,{path=v:GetFullName(),collide=v.CanCollide,query=v.CanQuery,touch=v.CanTouch,disabled=v:GetAttribute("VisualQueryDisabled")}) end
   if mover and mover:GetAttribute("Type")~="toggle" then
    local w=v:FindFirstChildOfClass("WeldConstraint")
    if v.Anchored or not w or w.Part0~=mover.MoverRoot or w.Part1~=v then table.insert(out.weldErrors,v:GetFullName()) end
   end
  end end
  table.insert(out.models,row)
 end
end
out.modelCount=#out.models
out.pass=out.modelCount==97 and #out.violations==0 and #out.weldErrors==0
return game.HttpService:JSONEncode(out)
'''
CAMERA = r'''
local h=workspace.CourseAurora.Hole6
local cf=CFrame.new(h:GetAttribute("HoleOrigin"))*CFrame.Angles(0,math.rad(h:GetAttribute("HoleYaw") or 0),0)
local camera=workspace.CurrentCamera
local eye=h.Tee.Position+Vector3.new(0,5,0)
local focus=__CUP__
workspace:SetAttribute("GolfTestCamera","look")
workspace:SetAttribute("GolfTestCamPos",eye)
workspace:SetAttribute("GolfTestFocus",focus)
workspace:SetAttribute("GolfTestFOV",60)
task.wait(0.5)
local function vec(v) return {v.X,v.Y,v.Z} end
local function projection(v) local p,on=camera:WorldToViewportPoint(v) return {point=vec(p),onScreen=on} end
local steam=h:FindFirstChild("KettleSteam",true)
assert(steam and steam.Parent:IsA("Attachment"))
local origin=steam.Parent.WorldPosition
local life=steam.Lifetime.Max
local radius=0
for _,k in steam.Size.Keypoints do radius=math.max(radius,k.Value/2) end
local maxRise=steam.Speed.Max*life+math.max(0,steam.Acceleration.Y)*life*life/2+radius
local horizontal=steam.Speed.Max*life+radius
local envelope={}
for _,x in {-1,1} do for _,y in {-radius,maxRise} do for _,z in {-1,1} do table.insert(envelope,projection(origin+Vector3.new(x*horizontal,y,z*horizontal))) end end end
return game.HttpService:JSONEncode({raycasts=0,method="camera projection + conservative particle envelope, visual screenshot required",tee=vec(h.Tee.Position),eye=vec(eye),camera=vec(camera.CFrame.Position),focus=vec(focus),fov=camera.FieldOfView,viewport={camera.ViewportSize.X,camera.ViewportSize.Y},cup=projection(focus),steam={origin=vec(origin),maxRise=maxRise,maxWorldY=origin.Y+maxRise,eyeWorldY=eye.Y,belowEye=origin.Y+maxRise<eye.Y,rate=steam.Rate,speed={steam.Speed.Min,steam.Speed.Max},lifetime={steam.Lifetime.Min,steam.Lifetime.Max},envelope=envelope}})
'''

def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')

def screenshot(st, name):
    r=st.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':st.id,'capture_id':name}})
    img=next(c for c in r['result']['content'] if c.get('type')=='image')
    suffix='.png' if img.get('mimeType')=='image/png' else '.jpg'
    path=OUT/'screens'/(name+suffix)
    path.write_bytes(base64.b64decode(img['data']))
    return str(path)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'screens').mkdir(exist_ok=True)
    st=Studio()
    assert st.mode()[0]=='Edit'
    assert st.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
    spec=json.loads((HERE.parents[2]/'assets/vr-mini-golf/aurora-archipelago/holes.json').read_text())
    try:
        set_edit_attrs(st,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'aurora_archipelago'})})
        st.start_play();wait_api(st)
        length=int(st.luau(SCHEDULE,'Server',timeout=90))
        raw=''.join(st.luau(f'return string.sub(_G.StageAMVisualJSON,{i+1},{i+45000})','Server') for i in range(0,length,45000))
        schedule=json.loads(raw);save('h17-visual-schedule.json',schedule)
        st.luau('_G.StageAMVisualJSON=nil return true','Server')
        audit={dm:json.loads(st.luau(AUDIT,dm)) for dm in ['Server','Client']}
        save('visual-flags-play.json',audit)
        st.api('place',6,'')
        cup=spec['holes'][5]['cup']['position']
        focus='cf:PointToWorldSpace(Vector3.new('+','.join(str(v) for v in cup)+'))'
        camera=json.loads(st.luau(CAMERA.replace('__CUP__',focus),'Client'))
        camera['screenshot']=screenshot(st,'am-h06-tee-eye5')
        save('h6-steam-camera.json',camera)
        print('H6 evidence',camera['screenshot'],'below eye',camera['steam']['belowEye'],flush=True)
        views=[]
        for n in [14,18]:
            st.api('place',n,'')
            st.luau(f'''local h=workspace.CourseAurora.Hole{n}
local cf=CFrame.new(h:GetAttribute("HoleOrigin"))*CFrame.Angles(0,math.rad(h:GetAttribute("HoleYaw") or 0),0)
workspace:SetAttribute("GolfTestCamPos",cf:PointToWorldSpace(Vector3.new(20,22,3)))
workspace:SetAttribute("GolfTestFocus",cf:PointToWorldSpace(Vector3.new(0,3,-27)))
workspace:SetAttribute("GolfTestFOV",60) workspace:SetAttribute("GolfTestCamera","look") return true''','Client')
            time.sleep(0.5);views.append(screenshot(st,f'am-h{n:02d}-props'))
        console={dm:st.problems(dm) for dm in ['Server','Client']}
        summary={'schedulePass':schedule['pass'],'samples':len(schedule['samples']),'duration':schedule['elapsed'],'mismatchCount':len(schedule['mismatches']),'auditPass':all(v['pass'] for v in audit.values()),'modelCounts':{dm:v['modelCount'] for dm,v in audit.items()},'steamBelowEye':camera['steam']['belowEye'],'screenshots':[camera['screenshot']]+views,'console':console}
        save('visual-summary.json',summary);print(json.dumps(summary),flush=True)
    finally:
        try:
            if st.mode()[0]!='Edit':
                st.luau('for _,n in {"GolfTestCamera","GolfTestCamPos","GolfTestFocus","GolfTestFOV"} do workspace:SetAttribute(n,nil) end return true','Client')
        finally:
            st.stop_play();clear_test_attrs(st);st.m.p.terminate()

if __name__=='__main__':main()
