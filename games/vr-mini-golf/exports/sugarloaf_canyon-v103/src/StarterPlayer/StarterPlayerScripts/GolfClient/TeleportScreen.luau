-- TeleportScreen (stage z): the loading screen for trips between places (ServerScriptService.PlaceTeleport).
--   * Remotes.TeleportStatus "start" (dest): show that place's loading art (Config.UI.Loading*, or the title art for
--     the lobby) and hand the same ScreenGui to TeleportService:SetTeleportGui, so it stays up while the next place
--     loads (ReplicatedFirst.ArrivalScreen takes it down there).
--   * "skipped" (Studio playtests can't teleport) / "failed": take it down and show the message.
local Players = game:GetService("Players")
local TeleportService = game:GetService("TeleportService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))
local Courses = require(Golf:WaitForChild("Courses"))

local player = Players.LocalPlayer
local TeleportScreen = { showing = nil :: string? }

local gui: ScreenGui? = nil
local token = 0
local notify = function(_text: string) end

local function build(dest: string): ScreenGui
	local info = Courses.info(dest)
	local image = info and info.loading and Config.UI[info.loading] or ""
	if image == "" then
		image = Config.UI.TitleBackground
	end
	local g = Instance.new("ScreenGui")
	g.Name = "GolfLoading"
	g.IgnoreGuiInset = true
	g.DisplayOrder = 100
	g.ResetOnSpawn = false
	pcall(function()
		g.ScreenInsets = Enum.ScreenInsets.None
	end)
	local bg = Instance.new("ImageLabel")
	bg.Name = "Art"
	bg.BackgroundColor3 = Color3.fromRGB(14, 22, 38)
	bg.BorderSizePixel = 0
	bg.Size = UDim2.fromScale(1, 1)
	bg.Image = image
	bg.ScaleType = Enum.ScaleType.Crop
	bg.Parent = g
	local text = Instance.new("TextLabel")
	text.Name = "Caption"
	text.BackgroundTransparency = 1
	text.AnchorPoint = Vector2.new(0.5, 1)
	text.Position = UDim2.new(0.5, 0, 1, -24)
	text.Size = UDim2.new(0.8, 0, 0, 36)
	text.Font = Enum.Font.FredokaOne
	text.TextScaled = true
	text.TextColor3 = Color3.fromRGB(255, 238, 206)
	text.TextStrokeTransparency = 0.4
	text.Text = dest == "lobby" and "Back to the lobby..." or ("Heading to " .. (info and info.name or dest) .. "...")
	text.Parent = bg
	g:SetAttribute("Destination", dest)
	return g
end

local function hide()
	token += 1
	TeleportScreen.showing = nil
	if gui then
		local g = gui
		gui = nil
		local art = g:FindFirstChild("Art")
		if art then
			TweenService:Create(art, TweenInfo.new(0.3), { ImageTransparency = 1, BackgroundTransparency = 1 }):Play()
			TweenService:Create(art.Caption, TweenInfo.new(0.3), { TextTransparency = 1, TextStrokeTransparency = 1 }):Play()
		end
		task.delay(0.35, function()
			g:Destroy()
		end)
	end
end

local function show(dest: string)
	hide()
	token += 1
	local my = token
	TeleportScreen.showing = dest
	gui = build(dest)
	pcall(function()
		TeleportService:SetTeleportGui(gui)
	end)
	gui.Parent = player:WaitForChild("PlayerGui")
	-- (a teleport that never happens shouldn't leave the screen up)
	task.delay(30, function()
		if token == my and gui then
			hide()
			notify("The teleport timed out. Try again.")
		end
	end)
end

function TeleportScreen.start(opts)
	if opts and opts.notify then
		notify = opts.notify
	end
	Golf:WaitForChild("Remotes"):WaitForChild("TeleportStatus").OnClientEvent:Connect(function(state, dest, message)
		if state == "start" then
			show(dest)
		else
			hide()
			if message then
				notify(message)
			end
		end
	end)
end

return TeleportScreen
