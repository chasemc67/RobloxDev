assert(game.PlaceId==0, "LOCAL ONLY")
assert(not game.ServerStorage:FindFirstChild("QA_SC"), "QA_SC already exists")
local root=Instance.new("Folder") root.Name="QA_SC" root.Parent=game.ServerStorage
local src=game.StarterPlayer.StarterPlayerScripts.GolfClient.BallController.Source
src=src:gsub('local Remotes = Golf:WaitForChild%("Remotes"%)',[[local Remotes={}
for _,name in {"Stroke","BallRest","RequestReset"} do Remotes[name]={FireServer=function() if name=="RequestReset" then script:SetAttribute("ResetRequested",true) end end} end]])
src=src:gsub("function Ball.getHole%(%)\n.-\nend",[[function Ball.getHole() return workspace.CourseSugarloaf["Hole"..script:GetAttribute("Hole")] end]],1)
src=src:gsub("function Ball.isOwner%(%)\n.-\nend","function Ball.isOwner() return true end",1)
local a=assert(src:find("function Ball.init()",1,true))
src=src:sub(1,a-1)..[[
function Ball.init(ball)
 Ball.ball=ball rayParams.FilterDescendantsInstances={workspace.Balls}
 Ball.connection=RunService.PreSimulation:Connect(step)
end
function Ball.qaPlace(pos)
 local b=Ball.ball b.Anchored=true b.CFrame=CFrame.new(pos)
 b.AssemblyLinearVelocity=Vector3.zero b.AssemblyAngularVelocity=Vector3.zero
 b.Anchored=false b:SetNetworkOwner(nil)
 slowTime,rollTime,stillTime,pinTime,seamHops,parkTime,strokeTime,stuckTime=0,0,0,0,0,0,0,0
 riding,rollVel,lastVel,stuckAnchor=nil,nil,nil,nil teleportCooldown=0
 script:SetAttribute("ResetRequested",false) Ball.setState("ready")
end
return Ball
]]
local m=Instance.new("ModuleScript") m.Name="ControllerTemplate" m.Source=src m.Parent=root
return #src