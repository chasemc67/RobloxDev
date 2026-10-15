-- GolfMain: client entry point. Picks VR or touch/mouse controls.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local VRService = game:GetService("VRService")
local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")

local player = Players.LocalPlayer
local modules = script.Parent:WaitForChild("GolfClient")
local Remotes = ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Remotes")

local Places = require(ReplicatedStorage.Golf:WaitForChild("Places"))
local HUD = require(modules.HUD)

local playerModule = player:WaitForChild("PlayerScripts"):FindFirstChild("PlayerModule")
local controls = playerModule and require(playerModule):GetControls()

-- VR can take a moment to report as enabled at startup
local isVR = UserInputService.VREnabled or VRService.VREnabled
if not isVR then
	local t0 = os.clock()
	while os.clock() - t0 < 1 do
		if UserInputService.VREnabled or VRService.VREnabled then
			isVR = true
			break
		end
		task.wait()
	end
end
local simulateVR = not isVR and workspace:GetAttribute("SimulateVR") == true


-- (stage z, updated ad) The lobby has no golf ball/course. Desktop keeps LobbyRoam; real VR
-- (including the startup wait) and SimulateVR use our wrist HUD, putter, locomotion and menu.
-- TeleportScreen and the server's portal walk-in triggers work with either character controller.
if Places.isLobby() then
	pcall(function()
		StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false)
	end)
	local lobbyBall = { menuOpen = false, lobbyRoam = true }
	function lobbyBall.canHit() return false end
	function lobbyBall.exploring() return true end
	local VR, LobbyRoam
	if isVR or simulateVR then
		-- The HUD/VR contract, without BallController.init's course waits or any stroke remotes.
		lobbyBall.Placed = Instance.new("BindableEvent")
		lobbyBall.Teleported = Instance.new("BindableEvent")
		function lobbyBall.getHole() return nil end
		function lobbyBall.requestReset() end
		if controls then controls:Disable() end
		pcall(function() GuiService.TouchControlsEnabled = false end)
		HUD.init(true, lobbyBall)
		VR = require(modules.VRControls)
		VR.start(lobbyBall, HUD, simulateVR)
	else
		LobbyRoam = require(modules.LobbyRoam)
		LobbyRoam.start(lobbyBall, controls)
	end
	local FrontEnd = require(modules.FrontEnd)
	if VR then HUD.attachFrontEnd(FrontEnd) end
	FrontEnd.start({ HUD = HUD, Ball = lobbyBall, VR = VR, LobbyRoam = LobbyRoam, isVR = isVR or simulateVR, vrUser = isVR })
	require(modules.TeleportScreen).start({ notify = FrontEnd.toast })
	return
end

local Ball = require(modules.BallController)
workspace:WaitForChild(require(ReplicatedStorage.Golf:WaitForChild("Courses")).folderName())

-- Golf replaces walking: freeze the humanoid (works with any control scripts) and, if the classic
-- PlayerModule is present, disable its controls too. Also hide the touch thumbstick/jump button.
local Explore = require(modules.Explore)
local function freezeCharacter(char)
	if Explore.active or Ball.lobbyRoam then
		return -- Explore.applyCharacter / LobbyRoam set it up for walking
	end
	if controls then
		controls:Disable()
	end
	local hum = char:WaitForChild("Humanoid", 10)
	if hum then
		hum.WalkSpeed = 0
		hum.JumpPower = 0
		hum.JumpHeight = 0
		hum.AutoRotate = false
	end
end
if player.Character then
	task.spawn(freezeCharacter, player.Character)
end
player.CharacterAdded:Connect(freezeCharacter)
pcall(function()
	GuiService.TouchControlsEnabled = false
end)
pcall(function()
	StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack, false)
end)
-- the Roblox player list covered the Reset Ball button (Playtest Bot round 1); the scorecard lists every player
pcall(function()
	StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false)
end)


Ball.init()
HUD.init(isVR or simulateVR, Ball)

local VR
if isVR or simulateVR then
	VR = require(modules.VRControls)
	VR.start(Ball, HUD, simulateVR)
else
	require(modules.TouchControls).start(Ball, HUD)
	-- free-roam Explore mode (phone/desktop): HUD Explore button
	Explore.start(Ball, HUD, controls)
	HUD.attachExplore(Explore)
end

-- (stage y) phone/desktop: walk around the lobby with the default controls and camera until a course is picked
-- (VR walks with VRControls' left stick)
local LobbyRoam = not VR and require(modules.LobbyRoam) or nil
if LobbyRoam then
	LobbyRoam.start(Ball, controls)
end

-- ball (and VR putter head) outline through whatever blocks them
local XRay = require(modules.XRay)
local camera = workspace.CurrentCamera
XRay.start(Ball, VR and VR.getEye or function()
	return camera.CFrame.Position
end, VR and VR.putterHead or nil)

require(modules.H9Lighting).start(VR and VR.getEye or function()
	if Explore.active then
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		return root and root.Position
	end
	-- The flat camera can orbit far above/outside the hole; the active ball is the playing position.
	return Ball.ball and Ball.ball.Position
end)

-- each course's own sky (stage w): Sugarloaf Canyon's sunset while you're in its world box, Lantern Grove's otherwise
require(modules.CourseLighting).start(function()
	if VR and VR.getEye then
		return VR.getEye()
	end
	return camera.CFrame.Position
end)

-- title screen / menus / results (an overlay: the round is already set up behind it; skipped when
-- workspace GolfTestMode or SkipMenu is true)
local FrontEnd = require(modules.FrontEnd)
HUD.attachFrontEnd(FrontEnd)
FrontEnd.start({ HUD = HUD, Ball = Ball, VR = VR, Explore = not VR and Explore or nil, LobbyRoam = LobbyRoam, isVR = isVR or simulateVR })
require(modules.TeleportScreen).start({ notify = FrontEnd.toast })

-- Studio-only playtest harness (see games/vr-mini-golf/playtesting.md)
if RunService:IsStudio() and workspace:GetAttribute("GolfTestMode") == true then
	require(modules.GolfTest).start(Ball, HUD, VR, simulateVR)
end

Remotes.Ready:FireServer()
