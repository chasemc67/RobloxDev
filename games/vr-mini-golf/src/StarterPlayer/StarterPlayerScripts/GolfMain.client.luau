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

local Ball = require(modules.BallController)
local HUD = require(modules.HUD)

workspace:WaitForChild("Course")

-- Golf replaces walking: freeze the humanoid (works with any control scripts) and, if the classic
-- PlayerModule is present, disable its controls too. Also hide the touch thumbstick/jump button.
local playerModule = player:WaitForChild("PlayerScripts"):FindFirstChild("PlayerModule")
local controls = playerModule and require(playerModule):GetControls()
local function freezeCharacter(char)
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

-- VR can take a moment to report as enabled at startup
local isVR = UserInputService.VREnabled or VRService.VREnabled
if not isVR then
	local t0 = os.clock()
	while os.clock() - t0 < 1 do
		if UserInputService.VREnabled then
			isVR = true
			break
		end
		task.wait()
	end
end
local simulateVR = not isVR and workspace:GetAttribute("SimulateVR") == true

Ball.init()
HUD.init(isVR or simulateVR, Ball)

local VR
if isVR or simulateVR then
	VR = require(modules.VRControls)
	VR.start(Ball, HUD, simulateVR)
else
	require(modules.TouchControls).start(Ball, HUD)
end

-- Studio-only playtest harness (see games/vr-mini-golf/playtesting.md)
if RunService:IsStudio() and workspace:GetAttribute("GolfTestMode") == true then
	require(modules.GolfTest).start(Ball, HUD, VR, simulateVR)
end

Remotes.Ready:FireServer()
