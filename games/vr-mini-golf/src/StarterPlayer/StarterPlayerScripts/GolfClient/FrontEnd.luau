-- FrontEnd: title screen, course picker, settings, how to play and the end-of-round results.
--   * The round is already set up behind it (the server starts hole 1 on Remotes.Ready); the menu is an overlay.
--   * Built once per page into a fixed 900x520 design frame, mounted in a ScreenGui (phone/desktop, scaled to the
--     safe area) or a SurfaceGui on a floating panel in front of your head (VR, laser-pointer clickable).
--   * Not shown at startup when workspace GolfTestMode or SkipMenu is true (Studio harness / smoke runs).
--   * While open, Ball.menuOpen is true: TouchControls ignores pointer input, and in VR the putter can't hit.
--   * Reopen: HUD "Menu" button (phone/desktop), click the left thumbstick (VR).
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Remotes = Golf:WaitForChild("Remotes")
local Config = require(Golf:WaitForChild("Config"))

local player = Players.LocalPlayer

local FrontEnd = {}

local W, H = 900, 520 -- design size of every page
local VR_SCALE = 1.6 -- SurfaceGui canvas = design size * this (sharper text)
local VR_PANEL = Vector3.new(4.2, 4.2 * H / W, 0.05) -- 1.26 m wide
local VR_DISTANCE = 4 -- studs in front of the head (1.2 m)

local FONT = Enum.Font.FredokaOne
local BODY = Enum.Font.GothamMedium
local C = {
	navy = Color3.fromRGB(14, 22, 38),
	panel = Color3.fromRGB(18, 30, 36),
	amber = Color3.fromRGB(255, 179, 71),
	amberDeep = Color3.fromRGB(214, 128, 40),
	cream = Color3.fromRGB(255, 238, 206),
	dim = Color3.fromRGB(184, 196, 186),
	good = Color3.fromRGB(130, 235, 150),
	bad = Color3.fromRGB(255, 150, 125),
	secondary = Color3.fromRGB(30, 46, 70),
}

local HUD, Ball, VR, Explore
local isVR = false

local screenGui, bgGui, bgImage, bgDim -- phone/desktop
local vrPart, vrGui, vrBg -- VR
local root, rootScale, content, toastLabel
local page = nil -- nil when closed: "title" | "courses" | "settings" | "howto" | "results"
local roundFinished = false
local lastResult = nil -- { scores, result } of the last CourseComplete
local clickSound

local settings = table.clone(Config.DefaultSettings)
local settingsEdited = false
local saveToken = 0

---------------------------------------------------------------------------- ui helpers
local function new(className, props, parent)
	local inst = Instance.new(className)
	for k, v in props do
		inst[k] = v
	end
	inst.Parent = parent
	return inst
end

local function corner(parent, r)
	new("UICorner", { CornerRadius = UDim.new(0, r or 14) }, parent)
end

local function stroke(parent, color, thickness, transparency)
	return new("UIStroke", { Color = color or C.amber, Thickness = thickness or 2, Transparency = transparency or 0, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, parent)
end

local function label(props, parent)
	props.BackgroundTransparency = 1
	props.Font = props.Font or FONT
	props.TextColor3 = props.TextColor3 or C.cream
	if props.TextScaled == nil then
		props.TextScaled = true
	end
	local maxSize = props.MaxTextSize
	props.MaxTextSize = nil
	local l = new("TextLabel", props, parent)
	if maxSize then
		new("UITextSizeConstraint", { MaxTextSize = maxSize }, l)
	end
	return l
end

local function panelFrame(props, parent)
	props.BackgroundColor3 = props.BackgroundColor3 or C.panel
	props.BackgroundTransparency = props.BackgroundTransparency or 0.12
	props.BorderSizePixel = 0
	local f = new("Frame", props, parent)
	corner(f, 18)
	stroke(f, C.amber, 2, 0.55)
	return f
end

-- style: "primary" (amber) | "secondary" (navy, amber outline) | "danger"
local function button(text, props, parent, onClick, style)
	style = style or "secondary"
	props.Text = text
	props.Font = FONT
	props.TextScaled = true
	props.AutoButtonColor = true
	props.BorderSizePixel = 0
	props.BackgroundColor3 = props.BackgroundColor3 or (style == "primary" and C.amber or (style == "danger" and Color3.fromRGB(150, 60, 50) or C.secondary))
	props.TextColor3 = style == "primary" and C.navy or C.cream
	local b = new("TextButton", props, parent)
	corner(b, 14)
	stroke(b, style == "primary" and C.cream or C.amber, 2, style == "primary" and 0.6 or 0.25)
	new("UIPadding", { PaddingTop = UDim.new(0, 8), PaddingBottom = UDim.new(0, 8), PaddingLeft = UDim.new(0, 12), PaddingRight = UDim.new(0, 12) }, b)
	new("UITextSizeConstraint", { MaxTextSize = 30 }, b)
	b.Activated:Connect(function()
		if clickSound then
			clickSound:Play()
		end
		onClick()
	end)
	return b
end

local function header(text, onBack)
	label({ Text = text, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 14), Size = UDim2.new(0, 520, 0, 50), TextColor3 = C.amber, TextStrokeTransparency = 0.4, TextStrokeColor3 = C.navy }, content)
	if onBack then
		button("< Back", { Name = "Back", Position = UDim2.fromOffset(16, 14), Size = UDim2.fromOffset(130, 52) }, content, onBack)
	end
end

local toastToken = 0
local function toast(text)
	if not toastLabel then
		return
	end
	toastToken += 1
	local token = toastToken
	toastLabel.Text = text
	toastLabel.Visible = true
	toastLabel.TextTransparency = 0
	toastLabel.BackgroundTransparency = 0.15
	task.delay(2.2, function()
		if token == toastToken then
			TweenService:Create(toastLabel, TweenInfo.new(0.4), { TextTransparency = 1, BackgroundTransparency = 1 }):Play()
		end
	end)
end

---------------------------------------------------------------------------- course data
local function holeList()
	local list = {}
	local course = workspace:FindFirstChild("Course")
	for _, h in course and course:GetChildren() or {} do
		local n = h:GetAttribute("HoleNumber")
		if n then
			list[n] = h
		end
	end
	return list
end

local function parTotal()
	local t = 0
	for _, h in holeList() do
		t += h:GetAttribute("Par") or 0
	end
	return t
end

local function relText(d)
	if d == 0 then
		return "E"
	end
	return (d > 0 and "+" or "") .. tostring(d)
end

local function bestOf(courseId)
	return player:GetAttribute("Best_" .. courseId)
end

local function roundInProgress()
	if roundFinished then
		return false
	end
	return (player:GetAttribute("Hole") or 1) > 1 or (player:GetAttribute("Strokes") or 0) > 0
end

---------------------------------------------------------------------------- settings
local function applySettings()
	HUD.soundGroup("Music").Volume = settings.MusicVolume
	HUD.soundGroup("SFX").Volume = settings.SFXVolume
	player:SetAttribute("CameraSensitivity", settings.CameraSensitivity)
	if VR and VR.setLeftHanded then
		VR.setLeftHanded(settings.Handedness == "Left")
	end
end

local function saveSettings()
	settingsEdited = true
	applySettings()
	saveToken += 1
	local token = saveToken
	task.delay(0.8, function()
		if token == saveToken then
			Remotes:WaitForChild("SaveSettings"):FireServer(table.clone(settings))
		end
	end)
end

-- the server publishes the saved settings as player attributes, then SettingsLoaded = true
local function loadSettingsFromAttributes()
	if settingsEdited or not player:GetAttribute("SettingsLoaded") then
		return
	end
	for k in Config.DefaultSettings do
		local v = player:GetAttribute(k)
		if v ~= nil then
			settings[k] = v
		end
	end
	applySettings()
end

---------------------------------------------------------------------------- pages
local show -- (pageName)

local function clear()
	if content then
		content:Destroy()
	end
	content = new("Frame", { Name = "Content", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1) }, root)
end

-- Title: logo + Resume (mid-round) / Play, Explore, Settings, How to play.
local function buildTitle()
	new("ImageLabel", {
		Name = "Logo",
		BackgroundTransparency = 1,
		Image = Config.UI.Logo,
		ScaleType = Enum.ScaleType.Fit,
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 0),
		Size = UDim2.fromOffset(640, 240),
	}, content)

	local row1 = new("Frame", { Name = "Main", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 250), Size = UDim2.fromOffset(640, 76) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 20), SortOrder = Enum.SortOrder.LayoutOrder }, row1)
	if roundInProgress() then
		button("Resume", { Name = "Resume", LayoutOrder = 1, Size = UDim2.fromOffset(280, 76) }, row1, FrontEnd.close, "primary")
		button("Play", { Name = "Play", LayoutOrder = 2, Size = UDim2.fromOffset(280, 76) }, row1, function()
			show("courses")
		end)
	else
		button("Play", { Name = "Play", LayoutOrder = 1, Size = UDim2.fromOffset(340, 76) }, row1, function()
			show("courses")
		end, "primary")
	end

	local row2 = new("Frame", { Name = "More", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 346), Size = UDim2.fromOffset(700, 62) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 16), SortOrder = Enum.SortOrder.LayoutOrder }, row2)
	if Explore and not isVR then
		button("Explore", { Name = "Explore", LayoutOrder = 1, Size = UDim2.fromOffset(210, 62) }, row2, function()
			FrontEnd.close()
			if not Explore.active then
				Explore.setActive(true)
			end
		end)
	end
	button("Settings", { Name = "Settings", LayoutOrder = 2, Size = UDim2.fromOffset(210, 62) }, row2, function()
		show("settings")
	end)
	button("How to play", { Name = "HowToPlay", LayoutOrder = 3, Size = UDim2.fromOffset(210, 62) }, row2, function()
		show("howto")
	end)

	local foot = isVR and "Click the left thumbstick to open this menu.  Explore mode is phone / desktop only."
		or "The Menu button (top right) brings you back here."
	label({ Text = foot, Font = BODY, AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -14), Size = UDim2.fromOffset(760, 26), TextColor3 = C.cream, TextStrokeTransparency = 0.3, TextStrokeColor3 = C.navy, MaxTextSize = 20 }, content)
end

local function startCourse()
	local fresh = not roundInProgress() and not roundFinished
	if Explore and Explore.active then
		Explore.setActive(false) -- (SetExplore off reaches the server before the restart)
	end
	FrontEnd.close()
	if not fresh then
		roundFinished = false
		Remotes.PlayAgain:FireServer(true)
	end
end

-- Course picker: Lantern Grove + two "coming soon" cards.
local function buildCourses()
	header("Choose a course", function()
		show("title")
	end)
	local row = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 82), Size = UDim2.fromOffset(860, 420) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 26), SortOrder = Enum.SortOrder.LayoutOrder }, row)
	local par = parTotal()
	for i, course in Config.Courses do
		local card = new("Frame", { Name = course.id, LayoutOrder = i, BackgroundColor3 = C.panel, BackgroundTransparency = 0.1, Size = UDim2.fromOffset(264, 412) }, row)
		corner(card, 18)
		stroke(card, course.playable and C.amber or C.dim, course.playable and 3 or 2, course.playable and 0 or 0.6)
		local img = new("ImageButton", {
			Name = "Image",
			Image = Config.UI[course.image] or "",
			BackgroundColor3 = C.navy,
			AutoButtonColor = course.playable,
			Position = UDim2.fromOffset(12, 12),
			Size = UDim2.fromOffset(240, 240),
			ScaleType = Enum.ScaleType.Crop,
		}, card)
		corner(img, 14)
		label({ Text = course.name, Position = UDim2.fromOffset(10, 262), Size = UDim2.new(1, -20, 0, 34), TextColor3 = course.playable and C.amber or C.dim }, card)
		local onClick
		if course.playable then
			local best = bestOf(course.id)
			label({ Text = string.format("9 holes  -  Par %d", par), Font = BODY, Position = UDim2.fromOffset(10, 300), Size = UDim2.new(1, -20, 0, 24), TextColor3 = C.cream, MaxTextSize = 20 }, card)
			label({
				Name = "Best",
				Text = best and string.format("Best: %d  (%s)", best, relText(best - par)) or "No best yet",
				Font = BODY,
				Position = UDim2.fromOffset(10, 326),
				Size = UDim2.new(1, -20, 0, 24),
				TextColor3 = best and C.good or C.dim,
				MaxTextSize = 20,
			}, card)
			onClick = startCourse
			local playText = roundInProgress() and "Restart round" or (roundFinished and "Play again" or "Play")
			button(playText, { Name = "PlayCourse", Position = UDim2.fromOffset(22, 356), Size = UDim2.new(1, -44, 0, 46) }, card, onClick, "primary")
		else
			label({ Text = "Coming soon", Font = BODY, Position = UDim2.fromOffset(10, 300), Size = UDim2.new(1, -20, 0, 24), TextColor3 = C.dim, MaxTextSize = 20 }, card)
			onClick = function()
				toast(course.name .. " is coming soon!")
			end
		end
		img.Activated:Connect(onClick)
	end
end

-- Settings: volumes, camera sensitivity, VR handedness. Steppers (big targets, laser-pointer friendly).
local function buildSettings()
	header("Settings", function()
		show("title")
	end)
	if VR and VR.isLeftHanded then
		settings.Handedness = VR.isLeftHanded() and "Left" or "Right" -- (X swaps hands in game)
	end
	local list = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 86), Size = UDim2.fromOffset(780, 400) }, content)
	new("UIListLayout", { Padding = UDim.new(0, 14), SortOrder = Enum.SortOrder.LayoutOrder }, list)

	local function row(order, title, note)
		local r = panelFrame({ LayoutOrder = order, Size = UDim2.new(1, 0, 0, 80) }, list)
		label({ Text = title, Position = UDim2.fromOffset(20, 10), Size = UDim2.fromOffset(330, 34), TextXAlignment = Enum.TextXAlignment.Left }, r)
		if note then
			label({ Text = note, Font = BODY, Position = UDim2.fromOffset(20, 46), Size = UDim2.fromOffset(330, 22), TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = C.dim, MaxTextSize = 18 }, r)
		end
		return r
	end

	-- [-] [ bar value ] [+]
	local function stepper(order, title, note, key, step, lo, hi, format, onChange)
		local r = row(order, title, note)
		local bar = new("Frame", { AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -96, 0.5, 0), Size = UDim2.fromOffset(240, 50), BackgroundColor3 = C.navy }, r)
		corner(bar, 12)
		local fill = new("Frame", { BackgroundColor3 = C.amberDeep, Size = UDim2.fromScale(0, 1), BorderSizePixel = 0 }, bar)
		corner(fill, 12)
		local value = label({ Size = UDim2.fromScale(1, 1), Text = "", ZIndex = 3, TextStrokeTransparency = 0.4, TextStrokeColor3 = C.navy, MaxTextSize = 28 }, bar)
		new("UIPadding", { PaddingTop = UDim.new(0, 8), PaddingBottom = UDim.new(0, 8) }, value)
		local function refresh()
			local v = settings[key]
			fill.Size = UDim2.fromScale(math.clamp((v - lo) / (hi - lo), 0, 1), 1)
			fill.Visible = v > lo
			value.Text = format(v)
		end
		local function change(dir)
			local v = math.clamp(math.floor((settings[key] + dir * step) / step + 0.5) * step, lo, hi)
			settings[key] = v
			refresh()
			saveSettings()
			if onChange then
				onChange()
			end
		end
		button("-", { Name = key .. "Down", AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -346, 0.5, 0), Size = UDim2.fromOffset(64, 56) }, r, function()
			change(-1)
		end)
		button("+", { Name = key .. "Up", AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -18, 0.5, 0), Size = UDim2.fromOffset(64, 56) }, r, function()
			change(1)
		end)
		refresh()
	end

	local function pct(v)
		return string.format("%d%%", math.floor(v * 100 + 0.5))
	end
	stepper(1, "Music volume", nil, "MusicVolume", 0.1, 0, 1, pct)
	stepper(2, "Sound effects", "Cup, crowd and putt sounds", "SFXVolume", 0.1, 0, 1, pct, function()
		HUD.playSfx("CupPlunk", 0.5, 0.9)
	end)
	local lo, hi = Config.CameraSensitivityRange[1], Config.CameraSensitivityRange[2]
	stepper(3, "Camera sensitivity", "Phone / desktop camera drag", "CameraSensitivity", 0.25, lo, hi, function(v)
		local t = string.gsub(string.format("%.2f", v), "0+$", "")
		t = string.gsub(t, "%.$", "")
		return t .. "x"
	end)

	local r = row(4, "VR club hand", "Also: press X in VR to swap")
	local toggles = {}
	local function refreshHand()
		for hand, b in toggles do
			local on = settings.Handedness == hand
			b.BackgroundColor3 = on and C.amber or C.secondary
			b.TextColor3 = on and C.navy or C.cream
		end
	end
	for i, hand in { "Left", "Right" } do
		toggles[hand] = button(hand, { Name = "Hand" .. hand, AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, i == 1 and -184 or -18, 0.5, 0), Size = UDim2.fromOffset(156, 56) }, r, function()
			settings.Handedness = hand
			refreshHand()
			saveSettings()
		end)
	end
	refreshHand()
end

-- How to play: VR / phone / desktop columns (from VRControls' and TouchControls' real controls).
local HOWTO = {
	{
		"VR",
		"Hold the controller like a putter grip, handle down, and swing through the ball.\n"
			.. "Trigger: warp to your ball\n"
			.. "Right stick: left/right snap turn, forward to teleport, back to rewind your last shot\n"
			.. "Left stick: walk\n"
			.. "A: re-fit the club (hold it straight down first)\n"
			.. "X: swap hands    B / Y: scorecard\n"
			.. "Click the left stick: this menu",
	},
	{
		"Phone",
		"Touch near the ball and pull back. Distance sets the power, sideways sets the aim. Let go to putt; slide back to the ball to cancel.\n"
			.. "Drag anywhere else to look around, pinch to zoom.\n"
			.. "Buttons: Reset Ball, Scorecard, Explore, Menu.\n"
			.. "Explore: thumbstick to walk, plus Sprint, Fly and Teleport buttons.",
	},
	{
		"Desktop",
		"Click near the ball and drag back. Distance sets the power, sideways sets the aim. Release to putt.\n"
			.. "Drag elsewhere (or hold right mouse) to look around, scroll to zoom. R resets the ball.\n"
			.. "Explore: WASD walk, Space jump, Shift sprint, F fly (Space/E up, Q down), T teleport.",
	},
}

local function buildHowTo()
	header("How to play", function()
		show("title")
	end)
	local row = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 80), Size = UDim2.fromOffset(870, 374) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 14), SortOrder = Enum.SortOrder.LayoutOrder }, row)
	for i, section in HOWTO do
		local col = panelFrame({ LayoutOrder = i, Size = UDim2.fromOffset(280, 374) }, row)
		label({ Text = section[1], Position = UDim2.fromOffset(14, 10), Size = UDim2.new(1, -28, 0, 36), TextColor3 = C.amber }, col)
		label({
			Text = section[2],
			Font = BODY,
			TextWrapped = true,
			TextXAlignment = Enum.TextXAlignment.Left,
			TextYAlignment = Enum.TextYAlignment.Top,
			Position = UDim2.fromOffset(16, 54),
			Size = UDim2.new(1, -32, 1, -66),
			MaxTextSize = 19,
		}, col)
	end
	label({
		Text = string.format("Sink the ball in as few strokes as you can.  %d strokes max per hole; out of bounds or water costs +%d.", Config.MaxStrokes, Config.PenaltyStrokes),
		Font = BODY,
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -16),
		Size = UDim2.fromOffset(820, 24),
		TextStrokeTransparency = 0.3,
		TextStrokeColor3 = C.navy,
		MaxTextSize = 19,
	}, content)
end

-- End of round: per-hole strokes vs par, totals, personal best. (The frame is named "Scorecard": the Studio
-- harness' progress scenario looks for it and its "9" / par-total cells.)
local function buildResults()
	local scores = lastResult and lastResult.scores or {}
	local result = lastResult and lastResult.result or {}
	local holes = holeList()
	local card = new("Frame", { Name = "Scorecard", BackgroundColor3 = C.panel, BackgroundTransparency = 0.06, Size = UDim2.fromScale(1, 1), BorderSizePixel = 0 }, content)
	corner(card, 22)
	stroke(card, C.amber, 3, 0.2)
	label({ Text = "Course Complete!", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 14), Size = UDim2.fromOffset(520, 52), TextColor3 = C.amber }, card)
	label({ Text = "Lantern Grove", Font = BODY, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 66), Size = UDim2.fromOffset(400, 24), TextColor3 = C.dim, MaxTextSize = 20 }, card)

	-- grid: Hole / Par / You
	local n = #holes
	local labelW, totalW = 110, 90
	local cellW = math.floor((820 - labelW - totalW) / math.max(n, 1))
	local grid = new("Frame", { Name = "Grid", BackgroundColor3 = C.navy, BackgroundTransparency = 0.25, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 104), Size = UDim2.fromOffset(labelW + cellW * n + totalW + 20, 3 * 46 + 16) }, card)
	corner(grid, 14)
	local function cell(r, c, text, color, font)
		local x, w
		if c == 0 then
			x, w = 10, labelW
		elseif c > n then
			x, w = 10 + labelW + cellW * n, totalW
		else
			x, w = 10 + labelW + cellW * (c - 1), cellW
		end
		label({
			Text = text,
			Font = font or FONT,
			TextColor3 = color or C.cream,
			Position = UDim2.fromOffset(x, 8 + (r - 1) * 46),
			Size = UDim2.fromOffset(w - 4, 40),
			TextXAlignment = c == 0 and Enum.TextXAlignment.Left or Enum.TextXAlignment.Center,
			MaxTextSize = 28,
		}, grid)
	end
	cell(1, 0, "Hole", C.dim)
	cell(2, 0, "Par", C.dim)
	cell(3, 0, "You", C.amber)
	local par, total = 0, 0
	for i, h in holes do
		local p = h:GetAttribute("Par") or 0
		par += p
		cell(1, i, tostring(i), C.dim)
		cell(2, i, tostring(p), C.dim)
		local s = scores[i]
		if type(s) == "number" and s > 0 then
			total += s
			cell(3, i, tostring(s), s < p and C.good or (s > p and C.bad or C.cream))
		else
			cell(3, i, "-")
		end
	end
	cell(1, n + 1, "Tot", C.dim)
	cell(2, n + 1, tostring(par), C.dim)
	cell(3, n + 1, tostring(total), C.amber)

	local d = total - par
	label({
		Name = "Total",
		Text = string.format("Total %d   (%s)", total, relText(d)),
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 268),
		Size = UDim2.fromOffset(600, 48),
		TextColor3 = d < 0 and C.good or (d > 0 and C.bad or C.cream),
	}, card)
	local best = result.best or bestOf(Config.CurrentCourse)
	local bestText
	if result.counted == false then
		bestText = best and string.format("Personal best: %d  (this round doesn't count)", best) or "This round doesn't count toward a personal best"
	elseif best then
		bestText = string.format("Par %d   -   Personal best: %d  (%s)", par, best, relText(best - par))
		if result.newBest and result.previousBest then
			bestText ..= string.format("   -   was %d", result.previousBest)
		end
	else
		bestText = string.format("Par %d", par)
	end
	label({ Name = "Best", Text = bestText, Font = BODY, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 322), Size = UDim2.fromOffset(760, 28), MaxTextSize = 22 }, card)

	if result.newBest then
		local banner = new("Frame", { Name = "NewBest", BackgroundColor3 = C.amber, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(770, 44), Size = UDim2.fromOffset(190, 52), Rotation = 6 }, card)
		corner(banner, 26)
		stroke(banner, C.cream, 3, 0)
		label({ Text = "New best!", Size = UDim2.fromScale(1, 1), TextColor3 = C.navy }, banner)
		local s = new("UIScale", { Scale = 0.4 }, banner)
		TweenService:Create(s, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end

	local btns = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -24), Size = UDim2.fromOffset(640, 70) }, card)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 24), SortOrder = Enum.SortOrder.LayoutOrder }, btns)
	button(isVR and "Play again  (B / Y)" or "Play again", { Name = "PlayAgain", LayoutOrder = 1, Size = UDim2.fromOffset(290, 70) }, btns, function()
		FrontEnd.playAgain()
	end, "primary")
	button("Back to menu", { Name = "BackToMenu", LayoutOrder = 2, Size = UDim2.fromOffset(290, 70) }, btns, function()
		show("title")
	end)
end

local BUILDERS = { title = buildTitle, courses = buildCourses, settings = buildSettings, howto = buildHowTo, results = buildResults }

show = function(name)
	page = name
	clear()
	local results = name == "results"
	-- title art behind every page except the results (shown over the course)
	if bgImage then
		bgImage.Visible = not results
		bgDim.BackgroundTransparency = results and 0.45 or 0.55
	end
	if vrBg then
		vrBg.Visible = not results
	end
	BUILDERS[name]()
end

---------------------------------------------------------------------------- mounting
local function rescaleScreen()
	if not (screenGui and rootScale) then
		return
	end
	local size = screenGui.AbsoluteSize
	if size.X < 1 or size.Y < 1 then
		return
	end
	rootScale.Scale = math.clamp(math.min((size.X - 16) / W, (size.Y - 12) / H), 0.4, 1.6)
end

local function buildRoot(parent)
	root = new("Frame", { Name = "Root", BackgroundTransparency = 1, Size = UDim2.fromOffset(W, H), Active = true }, parent)
	rootScale = new("UIScale", { Scale = isVR and VR_SCALE or 1 }, root)
	toastLabel = new("TextLabel", {
		Name = "Toast",
		AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, -70),
		Size = UDim2.fromOffset(460, 48),
		BackgroundColor3 = C.navy,
		BackgroundTransparency = 1,
		TextTransparency = 1,
		Font = FONT,
		TextScaled = true,
		TextColor3 = C.amber,
		Text = "",
		ZIndex = 50,
		Visible = false,
	}, root)
	corner(toastLabel, 14)
	new("UIPadding", { PaddingTop = UDim.new(0, 8), PaddingBottom = UDim.new(0, 8) }, toastLabel)
end

local function mountScreen(playerGui)
	bgGui = new("ScreenGui", { Name = "GolfMenuBg", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 20, Enabled = false }, playerGui)
	pcall(function()
		bgGui.ScreenInsets = Enum.ScreenInsets.None
	end)
	bgImage = new("ImageLabel", { Name = "Background", BackgroundColor3 = C.navy, BorderSizePixel = 0, Image = Config.UI.TitleBackground, ScaleType = Enum.ScaleType.Crop, Size = UDim2.fromScale(1, 1), Active = true }, bgGui)
	-- (a navy wash so the menu reads on top of the busy art)
	bgDim = new("Frame", { Name = "Dim", BackgroundColor3 = C.navy, BackgroundTransparency = 0.55, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1), Active = true }, bgGui)
	new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(0.5, 0.2), NumberSequenceKeypoint.new(1, 0) }) }, bgDim)

	screenGui = new("ScreenGui", { Name = "GolfMenu", ResetOnSpawn = false, DisplayOrder = 21, ZIndexBehavior = Enum.ZIndexBehavior.Sibling, Enabled = false }, playerGui)
	pcall(function()
		screenGui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets -- below the top bar, clear of notches
	end)
	buildRoot(screenGui)
	root.AnchorPoint = Vector2.new(0.5, 0.5)
	root.Position = UDim2.fromScale(0.5, 0.5)
	screenGui:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescaleScreen)
	rescaleScreen()
end

local function mountVR(playerGui)
	-- same approach as HUD's VR panels: an invisible, non-colliding, non-queryable part in the camera with a
	-- SurfaceGui in PlayerGui adorned to it (input-capable: the VR laser pointer clicks its buttons)
	vrPart = new("Part", { Name = "GolfMenuPanel", Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false, Transparency = 1, Size = VR_PANEL }, workspace.CurrentCamera)
	vrGui = new("SurfaceGui", {
		Name = "GolfMenu",
		Adornee = vrPart,
		Face = Enum.NormalId.Front,
		CanvasSize = Vector2.new(W * VR_SCALE, H * VR_SCALE),
		AlwaysOnTop = false, -- (true doesn't draw an adorned SurfaceGui here; same as HUD's VR panels)
		LightInfluence = 0,
		ResetOnSpawn = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		Enabled = false,
	}, playerGui)
	buildRoot(vrGui)
	vrBg = new("ImageLabel", { Name = "Background", BackgroundColor3 = C.navy, BorderSizePixel = 0, Image = Config.UI.TitleBackground, ScaleType = Enum.ScaleType.Crop, Size = UDim2.fromScale(1, 1), ZIndex = 0 }, root)
	corner(vrBg, 24)
	local wash = new("Frame", { BackgroundColor3 = C.navy, BackgroundTransparency = 0.5, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1) }, vrBg)
	corner(wash, 24)
	stroke(vrBg, C.amber, 3, 0.3)
end

-- VR: float the panel in front of the head at eye height; re-place it if you warp/teleport away while it's open.
local placedFrom: Vector3? = nil
local function placeVRPanel(force)
	if not vrPart then
		return
	end
	local head = HUD.getHeadCF()
	local look = Vector3.new(head.LookVector.X, 0, head.LookVector.Z)
	look = look.Magnitude > 0.1 and look.Unit or Vector3.new(0, 0, -1)
	if not force and placedFrom and (head.Position - placedFrom).Magnitude < 2.5 then
		-- lazy follow: stay put until it's well out of view (more than 70 degrees off where the head faces)
		local toPanel = Vector3.new(vrPart.Position.X - head.Position.X, 0, vrPart.Position.Z - head.Position.Z)
		if toPanel.Magnitude < 0.1 or look:Dot(toPanel.Unit) > math.cos(math.rad(70)) then
			return
		end
	end
	placedFrom = head.Position
	local pos = head.Position + look * VR_DISTANCE - Vector3.new(0, 0.3, 0)
	vrPart.CFrame = CFrame.lookAt(pos, Vector3.new(head.Position.X, pos.Y, head.Position.Z))
end

---------------------------------------------------------------------------- open / close
local function setOpen(on)
	Ball.menuOpen = on
	HUD.setMenuHidden(on)
	if screenGui then
		screenGui.Enabled = on
		bgGui.Enabled = on
	end
	if vrGui then
		if on and not vrGui.Enabled then
			placeVRPanel(true)
		end
		vrGui.Enabled = on
	end
end

function FrontEnd.isOpen()
	return page ~= nil
end

function FrontEnd.isResultsOpen()
	return page == "results"
end

function FrontEnd.open(name)
	setOpen(true)
	placeVRPanel(true) -- in front of where the player is looking now
	show(name or "title")
end

function FrontEnd.close()
	page = nil
	setOpen(false)
end

function FrontEnd.playAgain()
	roundFinished = false
	Remotes.PlayAgain:FireServer()
	FrontEnd.close()
end

-- Remotes.CourseComplete (via HUD): scores = strokes per hole, result = GolfServer's round summary (may be nil)
function FrontEnd.showResults(scores, result)
	roundFinished = true
	lastResult = { scores = type(scores) == "table" and scores or {}, result = type(result) == "table" and result or {} }
	FrontEnd.open("results")
end

function FrontEnd.start(opts)
	HUD, Ball, VR, Explore = opts.HUD, opts.Ball, opts.VR, opts.Explore
	isVR = opts.isVR == true
	local playerGui = player:WaitForChild("PlayerGui")
	clickSound = new("Sound", { Name = "MenuClick", SoundId = "rbxasset://sounds/clickfast.wav", Volume = 0.35, SoundGroup = HUD.soundGroup("SFX") }, script)

	if isVR then
		mountVR(playerGui)
		-- the putter can't hit while the menu is up (BallController.hit and VRControls both ask Ball.canHit)
		local canHit = Ball.canHit
		Ball.canHit = function()
			if Ball.menuOpen then
				return false
			end
			return canHit()
		end
		RunService.RenderStepped:Connect(function()
			if vrGui.Enabled then
				placeVRPanel(false)
			end
		end)
		-- left thumbstick click (unused by VRControls) opens / closes the menu
		UserInputService.InputBegan:Connect(function(input)
			if input.KeyCode ~= Enum.KeyCode.ButtonL3 then
				return
			end
			if page == nil then
				FrontEnd.open("title")
			elseif page ~= "results" then
				FrontEnd.close()
			end
		end)
	else
		mountScreen(playerGui)
	end

	-- settings: defaults now, the saved ones once the server has read them
	applySettings()
	loadSettingsFromAttributes()
	player:GetAttributeChangedSignal("SettingsLoaded"):Connect(loadSettingsFromAttributes)
	player:GetAttributeChangedSignal("Best_" .. Config.CurrentCourse):Connect(function()
		if page == "courses" then
			show("courses")
		end
	end)

	local skip = workspace:GetAttribute("GolfTestMode") == true or workspace:GetAttribute("SkipMenu") == true
	if not skip then
		FrontEnd.open("title")
	end

	-- Studio-only hook for tools/ui_shots.py (an MCP require() gets its own copy of this module):
	-- Invoke("open", page) / ("close") / ("results", {scores, result}) / ("state")
	if RunService:IsStudio() then
		local hook = Instance.new("BindableFunction")
		hook.Name = "GolfMenuDebug"
		hook.OnInvoke = function(cmd, arg)
			if cmd == "open" then
				FrontEnd.open(arg)
			elseif cmd == "close" then
				FrontEnd.close()
			elseif cmd == "results" then
				FrontEnd.showResults(arg and arg.scores, arg and arg.result)
			end
			return { page = page, open = Ball.menuOpen == true }
		end
		hook.Parent = player:WaitForChild("PlayerScripts")
	end
end

return FrontEnd
