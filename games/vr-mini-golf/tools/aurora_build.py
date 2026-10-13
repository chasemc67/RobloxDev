#!/usr/bin/env python3
"""Build Aurora in an already-open LOCAL file. Saving is deliberately left to Studio's local File menu."""
from run_playtests import Studio

CODE = '''
assert(game.PlaceId == 0 and not game:FindFirstChildOfClass("NetworkClient"), "LOCAL ONLY")
local old=workspace:FindFirstChild("CourseSugarloaf") if old then old:Destroy() end
local prior=workspace:FindFirstChild("CourseAurora")
local visual=prior and prior:FindFirstChild("Blockout")
if visual then visual.Parent=game.ServerStorage end
workspace.Terrain:Clear()
workspace:SetAttribute("PlaceRole", "aurora_archipelago")
workspace.Gravity=32.7
pcall(function() game:GetService("StudioDeviceSimulatorService"):StopSimulationAsync() end)
local ss=game.ServerStorage
local result=require(ss.CourseBuilder:Clone()).Build(require(ss.CourseData.AuroraArchipelago:Clone()),
 require(ss.CourseData.AuroraLayout:Clone()),{folder="CourseAurora",courseId="aurora_archipelago",blockout=true})
if visual then visual.Parent=workspace.CourseAurora end
local tee=workspace.CourseAurora.Hole1.Tee
workspace.SpawnLocation.CFrame=tee.CFrame+Vector3.new(0,0.5,3)
workspace.SpawnLocation.CanCollide=false
workspace.SpawnLocation.CanQuery=false
workspace.SpawnLocation.CanTouch=false
workspace.SpawnLocation.Transparency=1
workspace.CurrentCamera.CFrame=CFrame.lookAt(tee.Position+Vector3.new(8,18,22),tee.Position+Vector3.new(0,0,-16))
workspace.CurrentCamera.Focus=CFrame.new(tee.Position+Vector3.new(0,0,-16))
return result
'''
if __name__ == '__main__':
    s=Studio()
    assert s.mode()[0]=='Edit', 'Stop Play first'
    print(s.luau(CODE,timeout=600))
