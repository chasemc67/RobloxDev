-- ArrivalScreen (stage z): after a teleport between the game's places, keep the loading screen the previous place
-- handed to TeleportService:SetTeleportGui (GolfClient.TeleportScreen) up until this place has loaded, then fade it.
local TeleportService = game:GetService("TeleportService")
local ReplicatedFirst = game:GetService("ReplicatedFirst")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")

local gui = TeleportService:GetArrivingTeleportGui()
if not gui then
	return
end
ReplicatedFirst:RemoveDefaultLoadingScreen()
gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
if not game:IsLoaded() then
	game.Loaded:Wait()
end
task.wait(1.5) -- (the server starts hole 1 and the camera settles)
local art = gui:FindFirstChild("Art")
if art then
	TweenService:Create(art, TweenInfo.new(0.5), { ImageTransparency = 1, BackgroundTransparency = 1 }):Play()
	local caption = art:FindFirstChild("Caption")
	if caption then
		TweenService:Create(caption, TweenInfo.new(0.5), { TextTransparency = 1, TextStrokeTransparency = 1 }):Play()
	end
end
task.wait(0.6)
gui:Destroy()
