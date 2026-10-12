-- LobbyRoam (stage y): phone/desktop free walking in the lobby (stage z: the lobby place; VR too, with Roblox's VR controls).
--   * In the lobby (no "Course" attribute) Ball.lobbyRoam is true, so TouchControls hands over the camera and input
--     (Ball.exploring()), and the default Roblox camera follows the character.
--   * Menu closed: the default character controls (WASD/arrows + jump + mouse camera, the touch thumbstick and jump
--     button) at the StarterPlayer walk speed and jump. Menu open: standing still (the menu is a window over the lobby).
--   * Once a course is picked it hands everything back to the golf controls (frozen character, Scriptable camera).
--   * VR doesn't use this: VRControls' left stick already walks the rig whenever the menu is closed.
local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
local StarterPlayer = game:GetService("StarterPlayer")

local player = Players.LocalPlayer

local LobbyRoam = { active = false, walking = false }

local Ball, controls

-- (stage z) the lobby is its own place (Golf.Places); course places never roam
local Places = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("Places"))
local function inLobby()
	return Places.isLobby()
end

local function humanoid()
	local char = player.Character
	return char, char and char:FindFirstChildOfClass("Humanoid")
end

local function setWalking(hum, on)
	if controls then
		if on then
			controls:Enable()
		else
			controls:Disable()
		end
	end
	pcall(function()
		GuiService.TouchControlsEnabled = on
	end)
	if on then
		hum.WalkSpeed = StarterPlayer.CharacterWalkSpeed
		hum.UseJumpPower = StarterPlayer.CharacterUseJumpPower
		hum.JumpPower = StarterPlayer.CharacterJumpPower
		hum.JumpHeight = StarterPlayer.CharacterJumpHeight
		hum.AutoRotate = true
	else
		hum.WalkSpeed = 0
		hum.JumpPower = 0
		hum.JumpHeight = 0
		hum.AutoRotate = false
	end
end

function LobbyRoam.refresh()
	if not Ball then
		return
	end
	local roam = inLobby()
	local walk = roam and not Ball.menuOpen
	local was = LobbyRoam.active
	LobbyRoam.active, LobbyRoam.walking = roam, walk
	Ball.lobbyRoam = roam
	local char, hum = humanoid()
	local cam = workspace.CurrentCamera
	if roam then
		if hum then
			setWalking(hum, walk)
			hum.PlatformStand = false
			cam.CameraSubject = hum
		end
		cam.CameraType = Enum.CameraType.Custom
		if char then
			-- (TouchControls fades your own character near the golf camera)
			for _, d in char:GetDescendants() do
				if d:IsA("BasePart") or d:IsA("Decal") then
					d.LocalTransparencyModifier = 0
				end
			end
		end
	elseif was then
		-- a course was picked: back to golf (TouchControls stands the character beside the ball when it's ready)
		if hum then
			setWalking(hum, false)
		end
		cam.CameraType = Enum.CameraType.Scriptable
	end
end

function LobbyRoam.start(ballController, controlModule)
	Ball, controls = ballController, controlModule
	player:GetAttributeChangedSignal("Course"):Connect(LobbyRoam.refresh)
	player.CharacterAdded:Connect(function(char)
		char:WaitForChild("Humanoid", 10)
		LobbyRoam.refresh()
	end)
	LobbyRoam.refresh()
end

return LobbyRoam
