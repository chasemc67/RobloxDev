-- FrontEnd: title screen, course picker, settings, how to play and the end-of-round results.
--   * The round is already set up behind it (the server starts hole 1 on Remotes.Ready); the menu is an overlay.
--   * Built once per page into a fixed 900x520 design frame, mounted in a ScreenGui (phone/desktop: a centred window
--     about 60% of the screen, so the 3D lobby/course stays visible around it; no full-screen backdrop) or a SurfaceGui on a floating panel in front of your head (VR: GolfClient.VRPointer's laser from
--     either controller, trigger = click).
--   * Not shown at startup when workspace GolfTestMode or SkipMenu is true (Studio harness / smoke runs).
--   * While open, Ball.menuOpen is true: TouchControls ignores pointer input, and in VR the putter can't hit.
--   * Close: the X in the panel's top-right corner (every page but the results). In the lobby that hands the character
--     to GolfClient.LobbyRoam (walk/jump/camera with the default controls) until a course is picked.
--   * Reopen: the top-left "Menu" button in the Roblox top bar row or the M key (phone/desktop, stage y), the HUD
--     "Menu" button on a course, the MENU button on the VR wrist card (turn your other wrist up and
--     point at it). Clicking the left thumbstick still toggles it in VR, but nothing asks you to.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")
local GuiService = game:GetService("GuiService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Remotes = Golf:WaitForChild("Remotes")
local Config = require(Golf:WaitForChild("Config"))
local Courses = require(Golf:WaitForChild("Courses"))
local VRPointer = require(script.Parent:WaitForChild("VRPointer"))

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

local screenGui, menuButtonGui, menuButton -- phone/desktop
local vrPart, vrGui -- VR
local panelBg, panelWash -- the panel's own title-art background (both)
local LobbyRoam
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

-- UITextSizeConstraint caps the on-screen (post-UIScale) size, so on the VR panel's canvas (UIScale VR_SCALE) the caps
-- scale up with it; without that every capped label and button there drew at a third of its size (round 4).
local function maxTextSize(design: number): number
	return math.floor(design * (isVR and VR_SCALE or 1) + 0.5)
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
		new("UITextSizeConstraint", { MaxTextSize = maxTextSize(maxSize) }, l)
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
	if props.TextScaled == nil then
		props.TextScaled = true
	end
	props.AutoButtonColor = true
	props.BorderSizePixel = 0
	props.BackgroundColor3 = props.BackgroundColor3 or (style == "primary" and C.amber or (style == "danger" and Color3.fromRGB(150, 60, 50) or C.secondary))
	props.TextColor3 = style == "primary" and C.navy or C.cream
	local b = new("TextButton", props, parent)
	corner(b, 14)
	stroke(b, style == "primary" and C.cream or C.amber, 2, style == "primary" and 0.6 or 0.25)
	new("UIPadding", { PaddingTop = UDim.new(0, 8), PaddingBottom = UDim.new(0, 8), PaddingLeft = UDim.new(0, 12), PaddingRight = UDim.new(0, 12) }, b)
	new("UITextSizeConstraint", { MaxTextSize = maxTextSize(30) }, b)
	b.Activated:Connect(VRPointer.bind(b, function()
		if clickSound then
			clickSound:Play()
		end
		onClick()
	end))
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
-- (stage w) holes of a course (default: the one this player is on)
local function holeList(courseId)
	return Courses.holes(courseId or Courses.of(player))
end

local function parTotal(courseId)
	local t = 0
	for _, h in holeList(courseId) do
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

-- (stage x) a fresh join waits in the lobby with no course (no "Course" attribute) until one is picked here
local function inLobby()
	return player:GetAttribute("Course") == nil
end

local function roundInProgress()
	if roundFinished or inLobby() then
		return false
	end
	return Ball ~= nil and Ball.ball ~= nil -- the H1 tee is already an active round, even at zero strokes
end

-- An active round with at least one stroke taken. Before that the course card offers "Play", not "Restart round"
-- (stage v, round 7 #9): there is nothing to restart yet.
local function roundStarted()
	if not roundInProgress() then
		return false
	end
	if (player:GetAttribute("Strokes") or 0) > 0 or (player:GetAttribute("Hole") or 1) > 1 then
		return true
	end
	local ok, scores = pcall(HttpService.JSONDecode, HttpService, player:GetAttribute("Scores") or "[]")
	if ok and type(scores) == "table" then
		for _, s in scores do
			if type(s) == "number" and s > 0 then
				return true
			end
		end
	end
	return false
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
		-- title_preview_v2: L1 ~900 px wide, 40 px from the top of a 1920x1080 screen
		Position = UDim2.new(0.5, 0, 40 / 1080, 0),
		Size = UDim2.new(900 / 1920, 0, 900 / 1920 * W / H * 768 / 2048, 0),
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
	if Explore and not isVR and not inLobby() then
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

	local foot
	if isVR then
		foot = "Point with either controller, pull the trigger to click.  Menu later: look at your other wrist or click the left stick."
	elseif inLobby() then
		foot = "Close (X) to walk around the lobby.  The Menu button (top left) or M brings this back."
	else
		foot = "The Menu button (top left) or M brings you back here."
	end
	label({ Text = foot, Font = BODY, AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -14), Size = UDim2.fromOffset(760, 26), TextColor3 = C.cream, TextStrokeTransparency = 0.3, TextStrokeColor3 = C.navy, MaxTextSize = 20 }, content)
end

local function startCourse(courseId)
	local fresh = not roundStarted() and not roundFinished
	if Explore and Explore.active then
		Explore.setActive(false) -- (SetExplore off reaches the server before the restart)
	end
	FrontEnd.close()
	if courseId and (inLobby() or courseId ~= Courses.of(player)) then
		-- another course (stage w), or the first pick from the lobby: the server moves this player to its hole 1 with a
		-- fresh round
		roundFinished = false
		Remotes:WaitForChild("SelectCourse"):FireServer(courseId)
		return
	end
	if not fresh then
		roundFinished = false
		Remotes.PlayAgain:FireServer(true)
	end
end

-- Course picker: Lantern Grove, Sugarloaf Canyon (stage w) and a "coming soon" card.
local function buildCourses()
	header("Choose a course", function()
		show("title")
	end)
	local row = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 82), Size = UDim2.fromOffset(860, 420) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 26), SortOrder = Enum.SortOrder.LayoutOrder }, row)
	for i, course in Config.Courses do
		local playable = course.playable and Courses.playable(course.id)
		course = table.clone(course)
		course.playable = playable
		local par = parTotal(course.id)
		local current = course.id == Courses.of(player)
		local card = new("Frame", { Name = course.id, LayoutOrder = i, BackgroundColor3 = C.panel, BackgroundTransparency = 0.1, Size = UDim2.fromOffset(264, 412) }, row)
		corner(card, 18)
		stroke(card, course.playable and C.amber or C.dim, course.playable and 3 or 2, course.playable and 0 or 0.6)
		local img = new("ImageButton", {
			Name = "Image",
			Image = Config.UI[course.image] or "",
			BackgroundColor3 = C.navy,
			AutoButtonColor = course.playable,
			Position = UDim2.fromOffset(32, 12),
			Size = UDim2.fromOffset(200, 200),
			ScaleType = Enum.ScaleType.Crop,
		}, card)
		corner(img, 14)
		label({ Text = course.name, Position = UDim2.fromOffset(10, 222), Size = UDim2.new(1, -20, 0, 34), TextColor3 = course.playable and C.amber or C.dim }, card)
		local onClick
		if course.playable then
			local best = bestOf(course.id)
			local nHoles = 0
			for _ in holeList(course.id) do
				nHoles += 1
			end
			label({ Text = string.format("%d holes  -  Par %d", nHoles, par), Font = BODY, Position = UDim2.fromOffset(10, 260), Size = UDim2.new(1, -20, 0, 24), TextColor3 = C.cream, MaxTextSize = 20 }, card)
			label({
				Name = "Best",
				Text = best and string.format("Best: %d  (%s)", best, relText(best - par)) or "No best yet",
				Font = BODY,
				Position = UDim2.fromOffset(10, 286),
				Size = UDim2.new(1, -20, 0, 24),
				TextColor3 = best and C.good or C.dim,
				MaxTextSize = 20,
			}, card)
			-- course mode (SRV-139): Peaceful = balls pass through each other, PVP = balls bump (GolfServer/BallGroups)
			local modeButton
			modeButton = button("Mode: " .. settings.CourseMode, { Name = "CourseMode", Position = UDim2.fromOffset(22, 316), Size = UDim2.new(1, -44, 0, 40) }, card, function()
				settings.CourseMode = settings.CourseMode == "PVP" and "Peaceful" or "PVP"
				modeButton.Text = "Mode: " .. settings.CourseMode
				toast(settings.CourseMode == "PVP" and "PVP: balls bump into each other" or "Peaceful: balls pass through each other")
				saveSettings()
			end)
			onClick = function()
				startCourse(course.id)
			end
			-- (only the course you're on has a round to restart)
			local playText = not current and "Play" or (roundStarted() and "Restart round" or (roundFinished and "Play again" or "Play"))
			button(playText, { Name = "PlayCourse", Position = UDim2.fromOffset(22, 362), Size = UDim2.new(1, -44, 0, 46) }, card, onClick, "primary")
		else
			label({ Text = "Coming soon", Font = BODY, Position = UDim2.fromOffset(10, 260), Size = UDim2.new(1, -20, 0, 24), TextColor3 = C.dim, MaxTextSize = 20 }, card)
			onClick = function()
				toast(course.name .. " is coming soon!")
			end
		end
		img.Activated:Connect(VRPointer.bind(img, onClick))
	end
end

-- Settings: volumes, camera sensitivity, VR handedness. Steppers (big targets, laser-pointer friendly).
local function buildSettings()
	header("Settings", function()
		show("title")
	end)
	if VR and VR.isLeftHanded then
		settings.Handedness = VR.isLeftHanded() and "Left" or "Right"
	end
	local list = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 86), Size = UDim2.fromOffset(780, 400) }, content)
	new("UIListLayout", { Padding = UDim.new(0, isVR and 8 or 14), SortOrder = Enum.SortOrder.LayoutOrder }, list)

	local function row(order, title, note)
		local r = panelFrame({ LayoutOrder = order, Size = UDim2.new(1, 0, 0, isVR and 76 or 80) }, list)
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

	local r = row(4, "VR club hand", "Choose your club hand here")
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
	if isVR and VR and VR.beginClubSetup then
		local setup = row(5, "Club setup", "Stand as if putting, then fit your grip")
		button("Set up", { Name = "ClubSetup", AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -184, 0.5, 0), Size = UDim2.fromOffset(156, 56) }, setup, function()
			FrontEnd.close()
			VR.beginClubSetup()
		end)
		button("Reset fit", { Name = "ResetClubSetup", AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -18, 0.5, 0), Size = UDim2.fromOffset(156, 56) }, setup, function()
			VR.resetClubSetup()
		end)
	end
end

-- How to play: VR / phone / desktop columns (from VRControls' and TouchControls' real controls).
local HOWTO = {
	{
		"VR",
		"Hold the controller like a putter grip, handle down, and swing through the ball.\n"
			.. "Trigger: warp to your ball\n"
			.. "Right stick: left/right snap turn, forward to teleport, back to rewind your last shot\n"
			.. "Left stick: walk\n"
			.. "Settings: choose club hand and Club setup\n"
			.. "Off-hand X / A: wrist card    B / Y: scorecard\n"
			.. "Menus: point, trigger.  Look at wrist: score + MENU",
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

-- One platform at a time (tabs), so the text can be big: Playtest round 4 found the three-column page about 6 px on a
-- phone. HOWTO_TEXT design px x the phone's root scale (0.60 on the iPhone 17 Pro emulator) is 18.6 pt; in VR it is
-- 0.145 studs tall at 4 studs (~2.1 deg). 31 is the most the longest (VR) tab fits.
local HOWTO_TEXT = 31
local howtoTab: number? = nil

local function defaultHowToTab(): number
	if isVR then
		return 1
	end
	if UserInputService.TouchEnabled then -- (same test as the HUD's touch hint)
		return 2
	end
	return 3
end

local function buildHowTo()
	header("How to play", function()
		show("title")
	end)
	howtoTab = howtoTab or defaultHowToTab()
	local tabs = new("Frame", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 76), Size = UDim2.fromOffset(640, 48) }, content)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center, Padding = UDim.new(0, 14), SortOrder = Enum.SortOrder.LayoutOrder }, tabs)
	for i, section in HOWTO do
		button(section[1], { Name = "Tab" .. section[1], LayoutOrder = i, Size = UDim2.fromOffset(200, 48), TextScaled = false, TextSize = 28 }, tabs, function()
			howtoTab = i
			show("howto")
		end, i == howtoTab and "primary" or nil)
	end
	local panel = panelFrame({ Name = "HowToBody", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 134), Size = UDim2.fromOffset(840, 376) }, content)
	label({
		Name = "Text",
		Text = HOWTO[howtoTab][2] .. string.format("\nSink the ball in as few strokes as you can. %d strokes max per hole; out of bounds or water costs +%d.", Config.MaxStrokes, Config.PenaltyStrokes),
		Font = BODY,
		TextScaled = false,
		TextSize = HOWTO_TEXT,
		TextWrapped = true,
		TextXAlignment = Enum.TextXAlignment.Left,
		TextYAlignment = Enum.TextYAlignment.Top,
		Position = UDim2.fromOffset(22, 16),
		Size = UDim2.new(1, -44, 1, -28),
	}, panel)
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
	label({ Text = (Courses.info(Courses.of(player)) or { name = "Lantern Grove" }).name, Font = BODY, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 66), Size = UDim2.fromOffset(400, 24), TextColor3 = C.dim, MaxTextSize = 20 }, card)

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
	local best = result.best or bestOf(Courses.of(player))
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
	-- title art behind every page except the results (a plain navy panel on screen; nothing in VR, over the course)
	if panelBg then
		panelBg.ImageTransparency = results and 1 or 0
		panelWash.BackgroundTransparency = results and 0.2 or 0.5
		panelBg.Visible = not (results and isVR)
	end
	BUILDERS[name]()
	-- (stage y) close (X): every page but the results, which have their own buttons
	if not results then
		local x = button("X", { Name = "CloseMenu", AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -16, 0, 14), Size = UDim2.fromOffset(60, 52), ZIndex = 5 }, content, FrontEnd.close, "danger")
		x.TextXAlignment = Enum.TextXAlignment.Center
	end
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
	-- (stage y) a window about 60% of the screen; on short (phone landscape) screens most of the height, so the
	-- buttons stay finger-sized, which still leaves the lobby showing at the sides
	local frac = size.Y < 400 and 0.92 or 0.62
	rootScale.Scale = math.clamp(math.min(size.X * frac / W, size.Y * frac / H), 0.4, 1.6)
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
	-- the panel's own background: title art under a navy wash, rounded, amber rim
	panelBg = new("ImageLabel", { Name = "Background", BackgroundColor3 = C.navy, BorderSizePixel = 0, Image = Config.UI.TitleBackground, ScaleType = Enum.ScaleType.Crop, Size = UDim2.fromScale(1, 1), ZIndex = 0 }, root)
	corner(panelBg, 24)
	panelWash = new("Frame", { Name = "Wash", BackgroundColor3 = C.navy, BackgroundTransparency = 0.5, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1) }, panelBg)
	corner(panelWash, 24)
	stroke(panelBg, C.amber, 3, 0.3)
end

-- (stage y) the top-left Menu button that reopens the menu while it's closed: in the Roblox top bar row, right of
-- its own buttons (GuiService.TopbarInset), touch-sized; under the top bar at the left edge if there's no inset
local function placeMenuButton()
	local inset = GuiService.TopbarInset
	if inset.Width > 0 and inset.Height > 0 then
		local h = math.max(44, inset.Height - 8)
		menuButton.Position = UDim2.fromOffset(inset.Min.X + 8, inset.Min.Y + (inset.Height - h) / 2)
		menuButton.Size = UDim2.fromOffset(104, h)
	else
		menuButton.Position = UDim2.fromOffset(12, GuiService:GetGuiInset().Y + 8)
		menuButton.Size = UDim2.fromOffset(104, 48)
	end
end

local function mountMenuButton(playerGui)
	menuButtonGui = new("ScreenGui", { Name = "GolfMenuButton", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 19, Enabled = false }, playerGui)
	pcall(function()
		menuButtonGui.ScreenInsets = Enum.ScreenInsets.None
	end)
	menuButton = button("Menu", { Name = "MenuButton" }, menuButtonGui, function()
		FrontEnd.open("title")
	end, "primary")
	placeMenuButton()
	GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(placeMenuButton)
end

local function mountScreen(playerGui)
	mountMenuButton(playerGui)
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
	VRPointer.register(vrPart, vrGui, { modal = true, scale = VR_SCALE })
end

-- VR: float the panel in front of the head at eye height. One fixed world anchor per menu session (Playtest round 4:
-- it jumped left/right between pages): placed when the menu opens, and again only if a teleport carries the head
-- more than VR_REANCHOR studs away while it's open.
local VR_REANCHOR = 6
local placedFrom: Vector3? = nil
local function placeVRPanel(force)
	if not vrPart then
		return
	end
	local head = HUD.getHeadCF()
	local look = Vector3.new(head.LookVector.X, 0, head.LookVector.Z)
	look = look.Magnitude > 0.1 and look.Unit or Vector3.new(0, 0, -1)
	if not force and placedFrom and (head.Position - placedFrom).Magnitude < VR_REANCHOR then
		return
	end
	placedFrom = head.Position
	local pos = head.Position + look * VR_DISTANCE - Vector3.new(0, 0.3, 0)
	vrPart.CFrame = CFrame.lookAt(pos, Vector3.new(head.Position.X, pos.Y, head.Position.Z))
end

---------------------------------------------------------------------------- open / close
local function setOpen(on)
	Ball.menuOpen = on
	-- (stage y) the golf HUD stays hidden in the lobby too: there's no hole or ball yet
	HUD.setMenuHidden(on or inLobby())
	if screenGui then
		screenGui.Enabled = on
		menuButtonGui.Enabled = not on
	end
	if vrGui then
		if on and not vrGui.Enabled then
			placeVRPanel(true)
		end
		vrGui.Enabled = on
	end
	if LobbyRoam then
		LobbyRoam.refresh()
	end
end

function FrontEnd.isOpen()
	return page ~= nil
end

function FrontEnd.isResultsOpen()
	return page == "results"
end

function FrontEnd.openFromWrist()
	FrontEnd.open("title")
end

function FrontEnd.open(name)
	if VR and VR.cancelClubSetup then VR.cancelClubSetup() end
	setOpen(true) -- (anchors the VR panel in front of the head if the menu was closed; page changes keep it)
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
	HUD, Ball, VR, Explore, LobbyRoam = opts.HUD, opts.Ball, opts.VR, opts.Explore, opts.LobbyRoam
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
		-- left thumbstick click (unused by VRControls) still opens / closes the menu (the wrist card's MENU button is
		-- the way in now; this is just a shortcut)
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
		-- (stage y) M opens / closes the menu on desktop (not over the results)
		UserInputService.InputBegan:Connect(function(input, gameProcessed)
			if gameProcessed or input.KeyCode ~= Enum.KeyCode.M then
				return
			end
			if page == nil then
				FrontEnd.open("title")
			elseif page ~= "results" then
				FrontEnd.close()
			end
		end)
	end
	-- lobby -> course (or back): the golf HUD shows only on a course
	player:GetAttributeChangedSignal("Course"):Connect(function()
		HUD.setMenuHidden(Ball.menuOpen == true or inLobby())
	end)

	-- settings: defaults now, the saved ones once the server has read them
	applySettings()
	loadSettingsFromAttributes()
	player:GetAttributeChangedSignal("SettingsLoaded"):Connect(loadSettingsFromAttributes)
	for _, c in Config.Courses do
		player:GetAttributeChangedSignal("Best_" .. c.id):Connect(function()
			if page == "courses" then
				show("courses")
			end
		end)
	end

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
			return { page = page, open = Ball.menuOpen == true, menuButton = menuButtonGui ~= nil and menuButtonGui.Enabled }
		end
		hook.Parent = player:WaitForChild("PlayerScripts")
	end
end

return FrontEnd
