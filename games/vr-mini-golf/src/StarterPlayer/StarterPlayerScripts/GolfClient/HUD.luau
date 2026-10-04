-- HUD: screen UI for phone/desktop, world-space UI for VR, plus the shared scorecard.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Remotes = Golf:WaitForChild("Remotes")

local player = Players.LocalPlayer

local HUD = {}
HUD.isVR = false

local FONT = Enum.Font.FredokaOne
local gui: ScreenGui
local infoTitle, infoSub, powerFrame, powerFill, powerLabel, pullLine, pullDot, messageLabel, toastLabel, scorecard, hint
local vrMessagePart, vrMessageBB, vrMessageLabel, vrWrist, vrWristLabel, vrCardPart, vrCardGui
local cardParent -- where the scorecard is built: the ScreenGui, or a world-space panel in VR
local lastHeadCF = CFrame.new()
local finalCardOpen = false
local Ball

local function new(className, props, parent)
	local inst = Instance.new(className)
	for k, v in props do
		inst[k] = v
	end
	inst.Parent = parent
	return inst
end

local function corner(parent, r)
	new("UICorner", { CornerRadius = UDim.new(0, r or 12) }, parent)
end

local function panel(props, parent)
	local f = new("Frame", props, parent)
	f.BackgroundColor3 = props.BackgroundColor3 or Color3.fromRGB(20, 30, 25)
	f.BackgroundTransparency = props.BackgroundTransparency or 0.25
	corner(f)
	return f
end

local function label(props, parent)
	props.BackgroundTransparency = 1
	props.Font = props.Font or FONT
	props.TextColor3 = props.TextColor3 or Color3.new(1, 1, 1)
	return new("TextLabel", props, parent)
end

local function button(text, props, parent, onClick)
	local b = new("TextButton", props, parent)
	b.Text = text
	b.Font = FONT
	b.TextScaled = true
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = props.BackgroundColor3 or Color3.fromRGB(40, 140, 80)
	b.AutoButtonColor = true
	corner(b, 10)
	new("UIPadding", { PaddingTop = UDim.new(0, 6), PaddingBottom = UDim.new(0, 6), PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8) }, b)
	b.Activated:Connect(onClick)
	return b
end

---------------------------------------------------------------------------- scorecard
local function holeList()
	local list = {}
	for _, h in workspace.Course:GetChildren() do
		local n = h:GetAttribute("HoleNumber")
		if n then
			list[n] = h
		end
	end
	return list
end

local function scoresOf(p)
	local ok, data = pcall(HttpService.JSONDecode, HttpService, p:GetAttribute("Scores") or "[]")
	return ok and data or {}
end

local function closeScorecard()
	if scorecard then
		scorecard:Destroy()
		scorecard = nil
	end
	finalCardOpen = false
	if vrCardGui then
		vrCardGui.Enabled = false
	end
end

local function buildScorecard(final)
	if scorecard then
		scorecard:Destroy()
	end
	finalCardOpen = final == true
	if vrCardGui then
		-- float the card in front of the player, a little below eye level
		if not vrCardGui.Enabled then
			local look = Vector3.new(lastHeadCF.LookVector.X, 0, lastHeadCF.LookVector.Z)
			look = look.Magnitude > 0.1 and look.Unit or Vector3.new(0, 0, -1)
			local pos = lastHeadCF.Position + look * 3.5 - Vector3.new(0, 0.6, 0)
			vrCardPart.CFrame = CFrame.lookAt(pos, lastHeadCF.Position)
		end
		vrCardGui.Enabled = true
	end
	local holes = holeList()
	local cols = #holes + 2
	local rows = #Players:GetPlayers() + 2
	scorecard = panel({
		Name = "Scorecard",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.new(0, math.min(620, 140 + cols * 64), 0, 90 + rows * 40 + (final and 60 or 0)),
		BackgroundTransparency = 0.08,
		ZIndex = 10,
	}, cardParent)
	new("UISizeConstraint", { MaxSize = Vector2.new(620, 520) }, scorecard)
	new("UIScale", { Scale = 1 }, scorecard)
	label({ Text = final and "Course Complete!" or "Scorecard", Size = UDim2.new(1, 0, 0, 44), TextScaled = true, ZIndex = 11, TextColor3 = Color3.fromRGB(255, 230, 120) }, scorecard)
	local grid = new("Frame", { BackgroundTransparency = 1, Position = UDim2.new(0, 14, 0, 50), Size = UDim2.new(1, -28, 0, rows * 40), ZIndex = 11 }, scorecard)
	local colW = 1 / (cols + 1)
	local function cell(r, c, text, color, wide)
		label({
			Text = text,
			TextScaled = true,
			TextColor3 = color or Color3.new(1, 1, 1),
			Position = UDim2.new(c == 0 and 0 or colW * (c + 1), 0, 0, (r - 1) * 40),
			Size = UDim2.new(wide and colW * 2 or colW, -4, 0, 34),
			TextXAlignment = c == 0 and Enum.TextXAlignment.Left or Enum.TextXAlignment.Center,
			ZIndex = 12,
		}, grid)
	end
	cell(1, 0, "Hole", Color3.fromRGB(180, 220, 190), true)
	cell(2, 0, "Par", Color3.fromRGB(180, 220, 190), true)
	local parTotal = 0
	for i, h in holes do
		cell(1, i, tostring(i), Color3.fromRGB(180, 220, 190))
		cell(2, i, tostring(h:GetAttribute("Par")), Color3.fromRGB(180, 220, 190))
		parTotal += h:GetAttribute("Par")
	end
	cell(1, #holes + 1, "Tot", Color3.fromRGB(180, 220, 190))
	cell(2, #holes + 1, tostring(parTotal), Color3.fromRGB(180, 220, 190))
	for r, p in Players:GetPlayers() do
		local scores = scoresOf(p)
		local total = 0
		cell(r + 2, 0, p.DisplayName, p == player and Color3.fromRGB(255, 230, 120) or nil, true)
		for i, h in holes do
			local s = scores[i]
			local color
			if s and s > 0 then
				total += s
				local par = h:GetAttribute("Par")
				color = s < par and Color3.fromRGB(120, 255, 140) or (s > par and Color3.fromRGB(255, 140, 120) or nil)
			end
			cell(r + 2, i, s and s > 0 and tostring(s) or "-", color)
		end
		cell(r + 2, #holes + 1, tostring(total))
	end
	if final then
		button(HUD.isVR and "Play Again  (B / Y)" or "Play Again", {
			Name = "PlayAgain",
			AnchorPoint = Vector2.new(0.5, 1),
			Position = UDim2.new(0.5, 0, 1, -12),
			Size = UDim2.new(0, HUD.isVR and 300 or 200, 0, 46),
			ZIndex = 12,
		}, scorecard, HUD.playAgain)
	elseif not HUD.isVR then
		button("X", {
			AnchorPoint = Vector2.new(1, 0),
			Position = UDim2.new(1, -8, 0, 8),
			Size = UDim2.new(0, 36, 0, 36),
			BackgroundColor3 = Color3.fromRGB(150, 50, 50),
			ZIndex = 12,
		}, scorecard, closeScorecard)
	end
end

function HUD.playAgain()
	Remotes.PlayAgain:FireServer()
	closeScorecard()
end

function HUD.isFinalCardOpen()
	return finalCardOpen
end

function HUD.toggleScorecard()
	if scorecard then
		closeScorecard()
	else
		buildScorecard(false)
	end
end

---------------------------------------------------------------------------- info
function HUD.refresh()
	if not Ball then
		return
	end
	local hole = Ball.getHole()
	if not hole then
		return
	end
	local n = hole:GetAttribute("HoleNumber")
	local title = string.format("Hole %d  -  %s", n, hole:GetAttribute("HoleName"))
	local sub = string.format("Par %d   |   Strokes %d", hole:GetAttribute("Par"), player:GetAttribute("Strokes") or 0)
	if infoTitle then
		infoTitle.Text = title
		infoSub.Text = sub
	end
	if vrWristLabel then
		vrWristLabel.Text = title .. "\n" .. sub .. "\nTrigger: go to ball   B/Y: scores\nStick: turn, up teleport, back rewind"
	end
	if scorecard and scorecard.Parent then
		buildScorecard(finalCardOpen)
	end
end

---------------------------------------------------------------------------- messages
local messageToken = 0
function HUD.message(text, color, duration)
	messageToken += 1
	local token = messageToken
	color = color or Color3.new(1, 1, 1)
	if HUD.isVR and vrMessageLabel then
		vrMessageLabel.Text = text
		vrMessageLabel.TextColor3 = color
		vrMessageBB.Enabled = true
	elseif messageLabel then
		messageLabel.Text = text
		messageLabel.TextColor3 = color
		messageLabel.TextTransparency = 0
		messageLabel.TextStrokeTransparency = 0.2
		messageLabel.Size = UDim2.new(0.9, 0, 0, 50)
		TweenService:Create(messageLabel, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.new(0.9, 0, 0, 80) }):Play()
	end
	task.delay(duration or 2.5, function()
		if token ~= messageToken then
			return
		end
		if vrMessageBB then
			vrMessageBB.Enabled = false
		end
		if messageLabel then
			TweenService:Create(messageLabel, TweenInfo.new(0.4), { TextTransparency = 1, TextStrokeTransparency = 1 }):Play()
		end
	end)
end

function HUD.toast(text)
	if not toastLabel then
		return
	end
	toastLabel.Text = text
	toastLabel.TextTransparency = 0
	task.delay(3, function()
		if toastLabel.Text == text then
			TweenService:Create(toastLabel, TweenInfo.new(0.5), { TextTransparency = 1 }):Play()
		end
	end)
end

-- Positions the VR message board in front of the player's head.
function HUD.placeVRMessage(headCF: CFrame)
	lastHeadCF = headCF
	if vrMessagePart then
		local look = Vector3.new(headCF.LookVector.X, 0, headCF.LookVector.Z)
		if look.Magnitude < 0.1 then
			look = Vector3.new(0, 0, -1)
		end
		local pos = headCF.Position + look.Unit * 5 + Vector3.new(0, 1.2, 0)
		vrMessagePart.CFrame = CFrame.lookAt(pos, headCF.Position)
	end
end

function HUD.placeVRWrist(handCF: CFrame, headPos: Vector3)
	if vrWrist then
		local pos = (handCF * CFrame.new(0, 0.3, 0.15)).Position
		vrWrist.CFrame = CFrame.lookAt(pos, headPos)
	end
end

---------------------------------------------------------------------------- power meter (touch)
function HUD.showPower(power, startPos: Vector2?, currentPos: Vector2?, color: Color3?)
	if not powerFrame then
		return
	end
	powerFrame.Visible = true
	powerFill.Size = UDim2.fromScale(power, 1)
	powerFill.BackgroundColor3 = color or Color3.fromRGB(90, 230, 90)
	powerLabel.Text = string.format("Power %d%%", math.floor(power * 100 + 0.5))
	if startPos and currentPos then
		local d = currentPos - startPos
		local mid = (startPos + currentPos) / 2
		pullLine.Visible = d.Magnitude > 4
		pullLine.Position = UDim2.fromOffset(mid.X, mid.Y)
		pullLine.Size = UDim2.fromOffset(d.Magnitude, 4)
		pullLine.Rotation = math.deg(math.atan2(d.Y, d.X))
		pullDot.Visible = true
		pullDot.Position = UDim2.fromOffset(startPos.X, startPos.Y)
	end
end

function HUD.hidePower()
	if powerFrame then
		powerFrame.Visible = false
		pullLine.Visible = false
		pullDot.Visible = false
	end
end

---------------------------------------------------------------------------- build
local function buildScreen()
	local info = panel({ Name = "Info", Position = UDim2.new(0, 12, 0, 12), Size = UDim2.new(0, 290, 0, 64) }, gui)
	infoTitle = label({ Size = UDim2.new(1, -20, 0, 30), Position = UDim2.new(0, 10, 0, 4), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left }, info)
	infoSub = label({ Size = UDim2.new(1, -20, 0, 22), Position = UDim2.new(0, 10, 0, 36), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = Color3.fromRGB(190, 230, 200) }, info)

	local btns = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -12, 0, 12), Size = UDim2.new(0, 120, 0, 104) }, gui)
	new("UIListLayout", { Padding = UDim.new(0, 8), HorizontalAlignment = Enum.HorizontalAlignment.Right }, btns)
	button("Reset Ball", { Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(60, 90, 150) }, btns, function()
		if Ball then
			Ball.requestReset()
		end
	end)
	button("Scorecard", { Size = UDim2.new(1, 0, 0, 44) }, btns, HUD.toggleScorecard)

	powerFrame = panel({ Name = "Power", AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -70), Size = UDim2.new(0, 300, 0, 34), Visible = false }, gui)
	local track = new("Frame", { Position = UDim2.new(0, 8, 0, 8), Size = UDim2.new(1, -16, 1, -16), BackgroundColor3 = Color3.fromRGB(0, 0, 0), BackgroundTransparency = 0.5 }, powerFrame)
	corner(track, 6)
	powerFill = new("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.fromRGB(90, 230, 90) }, track)
	corner(powerFill, 6)
	powerLabel = label({ Size = UDim2.fromScale(1, 1), TextScaled = true, Text = "", ZIndex = 3, TextStrokeTransparency = 0.5 }, track)

	-- the pull line is drawn in raw screen pixels, so it lives in its own unscaled ScreenGui
	local aimGui = new("ScreenGui", { Name = "GolfAim", ResetOnSpawn = false }, gui.Parent)
	pullLine = new("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.3, BorderSizePixel = 0, Visible = false }, aimGui)
	pullDot = new("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Size = UDim2.fromOffset(18, 18), BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.2, Visible = false }, aimGui)
	corner(pullDot, 9)

	messageLabel = label({
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.3),
		Size = UDim2.new(0.9, 0, 0, 80),
		TextScaled = true,
		Text = "",
		TextTransparency = 1,
		TextStrokeTransparency = 1,
		TextStrokeColor3 = Color3.fromRGB(20, 40, 25),
	}, gui)
	new("UITextSizeConstraint", { MaxTextSize = 64 }, messageLabel)

	toastLabel = label({ AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 14), Size = UDim2.new(0.5, 0, 0, 26), TextScaled = true, Text = "", TextTransparency = 1, TextStrokeTransparency = 0.5 }, gui)

	hint = label({
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -16),
		Size = UDim2.new(0.9, 0, 0, 22),
		TextScaled = true,
		Text = game:GetService("UserInputService").TouchEnabled
				and "Pull back from the ball to putt  -  drag elsewhere to look around  -  pinch to zoom"
			or "Drag back from the ball to putt  -  drag elsewhere to look around  -  scroll to zoom  -  R to reset",
		TextColor3 = Color3.fromRGB(235, 245, 235),
		TextStrokeTransparency = 0.5,
	}, gui)
	new("UITextSizeConstraint", { MaxTextSize = 20 }, hint)
end

local function buildVR()
	-- world-space UI: invisible panel parts in the camera that turn to face the head each frame, with
	-- SurfaceGuis in PlayerGui adorned to them (the standard, input-capable way to do VR UI)
	local playerGui = gui.Parent
	local function vrPanel(name, size, canvas)
		local part = new("Part", { Name = name, Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false, Transparency = 1, Size = size }, workspace.CurrentCamera)
		local sg = new("SurfaceGui", { Name = name, Adornee = part, Face = Enum.NormalId.Front, CanvasSize = canvas, AlwaysOnTop = false, LightInfluence = 0, ResetOnSpawn = false }, playerGui)
		return part, sg
	end
	vrMessagePart, vrMessageBB = vrPanel("VRMessage", Vector3.new(9, 1.6, 0.05), Vector2.new(1800, 320))
	vrMessageBB.Enabled = false
	vrMessageLabel = label({ Size = UDim2.fromScale(1, 1), TextScaled = true, Text = "", TextStrokeTransparency = 0.2 }, vrMessageBB)

	-- scorecard panel (1.3 m wide), placed in front of you when opened
	vrCardPart, vrCardGui = vrPanel("VRScorecard", Vector3.new(4.4, 3.6, 0.05), Vector2.new(660, 540))
	vrCardGui.Enabled = false
	cardParent = vrCardGui

	local wb
	vrWrist, wb = vrPanel("VRWrist", Vector3.new(0.95, 0.62, 0.05), Vector2.new(380, 248))
	local bg = new("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromRGB(20, 30, 25), BackgroundTransparency = 0.25 }, wb)
	corner(bg, 10)
	vrWristLabel = label({ Size = UDim2.new(1, -8, 1, -6), Position = UDim2.fromOffset(4, 3), TextScaled = true, Text = "" }, bg)
end

local function scoreName(strokes, par)
	if strokes == 1 then
		return "HOLE IN ONE!", Color3.fromRGB(255, 220, 60)
	end
	local d = strokes - par
	if d <= -3 then
		return "Albatross!", Color3.fromRGB(255, 220, 60)
	elseif d == -2 then
		return "Eagle!", Color3.fromRGB(255, 220, 60)
	elseif d == -1 then
		return "Birdie!", Color3.fromRGB(120, 255, 140)
	elseif d == 0 then
		return "Par", Color3.new(1, 1, 1)
	elseif d == 1 then
		return "Bogey", Color3.fromRGB(255, 190, 140)
	elseif d == 2 then
		return "Double Bogey", Color3.fromRGB(255, 160, 120)
	end
	return "+" .. d, Color3.fromRGB(255, 140, 120)
end

function HUD.init(isVR, ballController)
	HUD.isVR = isVR
	Ball = ballController
	gui = new("ScreenGui", { Name = "GolfHUD", ResetOnSpawn = false, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, player:WaitForChild("PlayerGui"))
	-- shrink the HUD on small (phone) screens
	local uiScale = new("UIScale", {}, gui)
	local function rescale()
		local vp = workspace.CurrentCamera.ViewportSize
		uiScale.Scale = math.clamp(math.min(vp.X, vp.Y) / 620, 0.6, 1.15)
	end
	rescale()
	workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
	cardParent = gui
	if isVR then
		buildVR()
	else
		buildScreen()
	end

	player:GetAttributeChangedSignal("Strokes"):Connect(HUD.refresh)
	player:GetAttributeChangedSignal("Hole"):Connect(HUD.refresh)
	Ball.Placed.Event:Connect(function(_, reason)
		HUD.refresh()
		if reason == "hole" then
			local hole = Ball.getHole()
			HUD.message(string.format("Hole %d  -  Par %d", hole:GetAttribute("HoleNumber"), hole:GetAttribute("Par")), Color3.fromRGB(255, 230, 120), 2.2)
		end
	end)

	local cupSound = new("Sound", { SoundId = "rbxasset://sounds/electronicpingshort.wav", Volume = 0.8 }, script)
	Remotes.HoleComplete.OnClientEvent:Connect(function(who, holeNum, strokes, par, maxed)
		local name, color = scoreName(strokes, par)
		if who == player then
			if not maxed then
				cupSound:Play()
			end
			HUD.message(maxed and ("Max strokes  -  " .. strokes) or name, color, 3)
		else
			HUD.toast(string.format("%s: %s on hole %d", who.DisplayName, maxed and tostring(strokes) or name, holeNum))
		end
		HUD.refresh()
	end)
	Remotes.Notice.OnClientEvent:Connect(function(text, kind)
		HUD.message(text, kind == "bad" and Color3.fromRGB(255, 120, 100) or Color3.new(1, 1, 1), 2)
	end)
	Remotes.CourseComplete.OnClientEvent:Connect(function()
		buildScorecard(true)
	end)
	for _, p in Players:GetPlayers() do
		p:GetAttributeChangedSignal("Scores"):Connect(function()
			if scorecard then
				HUD.refresh()
			end
		end)
	end
	Players.PlayerAdded:Connect(function(p)
		p:GetAttributeChangedSignal("Scores"):Connect(function()
			if scorecard then
				HUD.refresh()
			end
		end)
	end)
	HUD.refresh()
end

return HUD
