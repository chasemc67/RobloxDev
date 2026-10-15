-- HUD: screen UI for phone/desktop, world-space UI for VR, plus the shared scorecard.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local ContentProvider = game:GetService("ContentProvider")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Remotes = Golf:WaitForChild("Remotes")
local Config = require(Golf:WaitForChild("Config"))
local Courses = require(Golf:WaitForChild("Courses"))
local VRPointer = require(script.Parent:WaitForChild("VRPointer"))

local player = Players.LocalPlayer

local HUD = {}
HUD.isVR = false

local completedWristHole = nil
local FONT = Enum.Font.FredokaOne
local gui: ScreenGui
local uiScale: UIScale
local info, golfButtons, exploreBar, flyButtons, teleportMenu, sprintButton, flyButton
local Explore -- GolfClient.Explore (phone/desktop only), see HUD.attachExplore
local FrontEnd -- GolfClient.FrontEnd (title / menus / results), see HUD.attachFrontEnd
local aimGui
local closeTeleportMenu
local infoTitle, infoSub, powerFrame, powerFill, powerLabel, pullLine, pullDot, messageLabel, toastLabel, scorecard, hint
local vrMessagePart, vrMessageBB, vrMessageLabel, vrCardPart, vrCardGui
local wrist -- VR wrist card: { part, gui, group, alpha, shown, labels... } (see buildWrist)
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
	b.Activated:Connect(VRPointer.bind(b, onClick))
	return b
end

---------------------------------------------------------------------------- scorecard
-- the holes of the course this player is on (stage w: Lantern Grove or Sugarloaf Canyon)
local function holeList()
	return Courses.holes(Courses.of(player))
end

local function relText(d)
	if d == 0 then
		return "E"
	end
	return (d > 0 and "+" or "") .. tostring(d)
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
	-- only players on the same course share the card
	local mates = {}
	for _, p in Players:GetPlayers() do
		if Courses.of(p) == Courses.of(player) then
			table.insert(mates, p)
		end
	end
	local rows = #mates + 2
	-- compact on narrow / short screens (Playtest Bot round 1): fit the card to the screen, shorter rows, and scroll
	-- the player rows when there are many
	local vp = workspace.CurrentCamera.ViewportSize
	local scale = (not HUD.isVR and uiScale) and uiScale.Scale or 1
	-- (an 18-hole card is wider on a flat screen)
	local maxW = HUD.isVR and 620 or math.min(#holes > 9 and 960 or 620, vp.X / scale - 24)
	local maxH = HUD.isVR and 520 or math.min(520, vp.Y / scale - 70)
	local compact = maxW < 560 or maxH < 420
	local rowH = compact and 30 or 40
	local closeSize = HUD.isVR and 56 or 36
	local headerH = math.max(compact and 44 or 56, final and 0 or closeSize + 16)
	local headerReserve = final and 52 or 60 + closeSize
	local footer = final and 60 or 0
	local gridH = math.min(rows * rowH, maxH - headerH - footer)
	scorecard = panel({
		Name = "Scorecard",
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.new(0, math.min(maxW, math.max(360, 140 + cols * 64)), 0, headerH + gridH + footer),
		BackgroundTransparency = 0.08,
		ZIndex = 10,
	}, cardParent)
	new("UIScale", { Scale = 1 }, scorecard)
	label({ Name = "Title", Text = final and "Course Complete!" or "Scorecard", Position = UDim2.fromOffset(14, 0), Size = UDim2.new(1, -14 - headerReserve, 0, compact and 32 or 44), TextScaled = true, ZIndex = 11, TextColor3 = Color3.fromRGB(255, 230, 120) }, scorecard)
	local grid = new("ScrollingFrame", {
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		Position = UDim2.new(0, 14, 0, headerH),
		Size = UDim2.new(1, -28, 0, gridH),
		CanvasSize = UDim2.new(0, 0, 0, rows * rowH),
		ScrollBarThickness = rows * rowH > gridH and 6 or 0,
		ScrollingDirection = Enum.ScrollingDirection.Y,
		ZIndex = 11,
	}, scorecard)
	local colW = 1 / (cols + 1)
	local function cell(r, c, text, color, wide)
		label({
			Text = text,
			TextScaled = true,
			TextColor3 = color or Color3.new(1, 1, 1),
			Position = UDim2.new(c == 0 and 0 or colW * (c + 1), 0, 0, (r - 1) * rowH),
			Size = UDim2.new(wide and colW * 2 or colW, -4, 0, rowH - 6),
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
	for r, p in mates do
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
	-- settings gear: a round badge hanging off the card's top-right corner (clear of the grid); opens Settings
	-- (64 canvas px everywhere: ~38 px on a phone after the HUD's UIScale, still a fair touch target)
	local gs = 64
	local gear = new("ImageButton", {
		Name = "SettingsButton",
		Image = Config.UI.SettingsButton,
		PressedImage = Config.UI.SettingsButtonPressed,
		BackgroundTransparency = 1,
		AutoButtonColor = false,
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.new(1, -12, 0, 8),
		Size = UDim2.fromOffset(gs, gs),
		ZIndex = 13,
	}, scorecard)
	gear.Activated:Connect(VRPointer.bind(gear, function()
		if FrontEnd then
			closeScorecard()
			FrontEnd.openSettings()
		end
	end))
	if final then
		button(HUD.isVR and "Play Again  (B / Y)" or "Play Again", {
			Name = "PlayAgain",
			AnchorPoint = Vector2.new(0.5, 1),
			Position = UDim2.new(0.5, 0, 1, -12),
			Size = UDim2.new(0, HUD.isVR and 300 or 200, 0, 46),
			ZIndex = 12,
		}, scorecard, HUD.playAgain)
	else
		-- (VR: a bigger target for the laser pointer; B / Y closes it too)
		local s = closeSize
		button("X", {
			Name = "Close",
			AnchorPoint = Vector2.new(1, 0),
			Position = UDim2.new(1, -(20 + gs / 2), 0, 8), -- (left of the gear)
			Size = UDim2.new(0, s, 0, s),
			BackgroundColor3 = Color3.fromRGB(150, 50, 50),
			ZIndex = 12,
		}, scorecard, closeScorecard)
	end
end

function HUD.playAgain()
	if FrontEnd and FrontEnd.isResultsOpen() then
		FrontEnd.playAgain()
		return
	end
	Remotes.PlayAgain:FireServer()
	closeScorecard()
end

-- (the end-of-round results screen counts as the final card: VR B/Y = Play again)
function HUD.isFinalCardOpen()
	return finalCardOpen or (FrontEnd ~= nil and FrontEnd.isResultsOpen())
end

-- (stage ab, Studio checks) whether the (non-final) scorecard is up
function HUD.isScorecardOpen(): boolean
	return scorecard ~= nil
end

function HUD.toggleScorecard()
	if FrontEnd and FrontEnd.isOpen() then
		return
	end
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
		if Ball.lobbyRoam and wrist then
			wrist.hole.Text, wrist.name.Text = "LOBBY", "VR Mini Golf"
			wrist.par.Text, wrist.stroke.Text = "-", "-"
			wrist.total.Text, wrist.best.Text = "-", "-"
		end
		return
	end
	local n = hole:GetAttribute("HoleNumber")
	local title = string.format("Hole %d  -  %s", n, hole:GetAttribute("HoleName"))
	local sub = string.format("Par %d   |   Strokes %d", hole:GetAttribute("Par"), player:GetAttribute("Strokes") or 0)
	if infoTitle then
		infoTitle.Text = title
		infoSub.Text = sub
		if Explore and Explore.active then
			infoSub.Text = "Exploring  -  your ball waits on hole " .. n
		end
	end
	if wrist then
		local par = hole:GetAttribute("Par") or 0
		wrist.hole.Text = "HOLE " .. tostring(n)
		wrist.name.Text = hole:GetAttribute("HoleName") or ""
		wrist.par.Text = tostring(par)
		wrist.stroke.Text = tostring(player:GetAttribute("Strokes") or 0)
		-- total vs par over the holes finished so far; personal best for the course vs its par
		local scores, d, parSum = scoresOf(player), 0, 0
		for i, h in holeList() do
			local hp = h:GetAttribute("Par") or 0
			parSum += hp
			local sc = scores[i]
			if type(sc) == "number" and sc > 0 and (i < n or (i == n and (player:GetAttribute("HoleHoled") == true or i == completedWristHole))) then
				d += sc - hp
			end
		end
		wrist.total.Text = relText(d)
		local best = player:GetAttribute("Best_" .. Courses.of(player))
		wrist.best.Text = best and relText(best - parSum) or "-"
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

-- Last head pose from VRControls (the front end places its VR panel from it).
function HUD.getHeadCF()
	return lastHeadCF
end

-- Wrist (Walkabout style): 3D Model Bot's bracer (ReplicatedStorage.Golf.WristBracer) on either wrist (stage ab) with the
-- card on its WristFace, both hidden in normal play. They show only while you actively look at the wrist: the back
-- of the wrist faces your eyes (Config.WristShowDeg) AND it's near your gaze centre (WristGazeDeg), held
-- WristShowHold s; they hide WristHideHold s after either goes out (WristHideDeg / WristGazeHideDeg). Never mid-swing
-- or in a putting stance (VRControls passes the putter head speed and the stance flag).
-- On the aim pose of a Quest controller held normally, the back of the hand is -X on the left hand and +X on the
-- right, and the wrist is behind (+Z) and below (-Y) the controller origin.
local WRIST_OFFSET = Vector3.new(0, -0.12, 0.33) -- controller origin -> wrist centre (3.6 cm down, 10 cm back)
local FACE_LIFT = 0.256 -- Preserve the approved look-at-wrist gate reference point.
local WRIST_RANGE = 4 -- studs from the eyes (1.2 m)
local WRIST_NEAR_FACE = 2.5 -- studs (0.75 m): the off hand raised toward the face (pose log event "nearFace")
local WRIST_FADE = 12 -- 1/s
local WRIST_LOG_MAX = 200
local function wristLog(kind, why)
	local e = { t = os.clock(), event = kind, why = why }
	table.insert(wrist.events, e)
	if #wrist.events > WRIST_LOG_MAX then
		table.remove(wrist.events, 1)
	end
	if wrist.logPrint then
		print(string.format("[wrist] %s (%s)", kind, why))
	end
end

-- The look test for one wrist: where its face is and how squarely it faces / sits in the gaze of the eyes.
local function wristGeom(handCF: CFrame, headCF: CFrame, leftHand: boolean)
	local back = handCF.RightVector * (leftHand and -1 or 1)
	local rawBack = back
	-- Either side of the wrist is accepted; turn the readable face toward the eye.
	if back:Dot(headCF.Position - handCF.Position) < 0 then back = -back end
	local pivot = handCF:PointToWorldSpace(WRIST_OFFSET)
	local facePos = pivot + back * FACE_LIFT
	local toEye = headCF.Position - facePos
	local dist = toEye.Magnitude
	local faceDeg, gazeDeg = 180, 180
	if dist > 1e-3 then
		faceDeg = math.deg(math.acos(math.clamp(back:Dot(toEye / dist), -1, 1)))
		gazeDeg = math.deg(math.acos(math.clamp(headCF.LookVector:Dot(-toEye / dist), -1, 1)))
	end
	return back, rawBack, pivot, facePos, toEye, dist, faceDeg, gazeDeg
end

-- (stage ab, Chase: the watch works on either wrist) How well `handCF`'s wrist meets the look test: lower is better,
-- math.huge when out of range. VRControls compares both hands while the card is hidden and puts it on the better one.
function HUD.wristLookScore(handCF: CFrame, headCF: CFrame, leftHand: boolean): number
	local _, _, _, _, _, dist, faceDeg, gazeDeg = wristGeom(handCF, headCF, leftHand)
	if dist >= WRIST_RANGE then
		return math.huge
	end
	return faceDeg / Config.WristShowDeg + gazeDeg / Config.WristGazeDeg
end

function HUD.isWristShown(): boolean
	return wrist ~= nil and (wrist.shown or wrist.alpha > 0)
end

-- opts: { clubSpeed = studs/s, stance = boolean }
function HUD.placeVRWrist(handCF: CFrame, headCF: CFrame, leftHand: boolean, opts)
	if not wrist then
		return
	end
	opts = opts or {}
	local now = os.clock()
	local dt = math.min(now - (wrist.t or now), 0.1)
	wrist.t = now
	if wrist.leftHand ~= nil and wrist.leftHand ~= leftHand then
		wrist.inSince, wrist.outSince = nil, nil -- moved to the other wrist: the show hold starts over
	end
	wrist.leftHand = leftHand
	local back, rawBack, pivot, facePos, toEye, dist, faceDeg, gazeDeg = wristGeom(handCF, headCF, leftHand)
	local fingers = handCF.LookVector
	-- bracer frame: +Y = back of the wrist, +X = toward the fingers, pivot at the wrist centre
	local bracerCF = CFrame.fromMatrix(pivot, fingers, back)
	wrist.faceDeg, wrist.gazeDeg = faceDeg, gazeDeg
	local headset = game:GetService("VRService").VREnabled
	-- pose samples for tuning the thresholds (ServerScriptService.WristPoseLog): every 10 s, plus one per event
	local function sendPose(event)
		local remote = headset and Remotes:FindFirstChild("WristPose")
		if remote then remote:FireServer({ faceDeg = faceDeg, gazeDeg = gazeDeg,
			backDeg = math.deg(math.acos(math.clamp(rawBack:Dot(toEye.Unit), -1, 1))),
			distance = dist, speed = opts.clubSpeed or 0, shown = wrist.shown == true,
			manual = wrist.manual == true, hand = leftHand and "left" or "right", event = event }) end
	end
	if headset and now - (wrist.poseAt or 0) >= 10 then
		wrist.poseAt = now
		sendPose(nil)
	end
	if (opts.clubSpeed or 0) > Config.WristMaxClubSpeed then
		wrist.swingAt = now
	end
	local blocked = (Ball and Ball.menuOpen and "menu") or (finalCardOpen and "final card") or (opts.stance and not wrist.manual and "stance")
		or (wrist.swingAt and now - wrist.swingAt < Config.WristSwingQuiet and "swing") or nil
	local near = dist < WRIST_RANGE
	if wrist.manualDismissed and (not near or faceDeg > Config.WristHideDeg or gazeDeg > Config.WristGazeHideDeg) then
		wrist.manualDismissed = false
	end
	blocked = blocked or (wrist.manualDismissed and "controller off")
	wrist.blocked = blocked
	if blocked then
		wrist.inSince, wrist.outSince = nil, nil
		if wrist.shown then
			wrist.shown = false
			wristLog("hide", blocked)
		end
	elseif wrist.manual then
		wrist.shown = true
		wrist.inSince, wrist.outSince = nil, nil
	elseif not wrist.shown then
		wrist.outSince = nil
		if near and faceDeg <= Config.WristShowDeg and gazeDeg <= Config.WristGazeDeg then
			wrist.inSince = wrist.inSince or now
			if now - wrist.inSince >= Config.WristShowHold then
				wrist.shown = true
				wristLog("show", string.format("face %.0f deg, gaze %.0f deg", faceDeg, gazeDeg))
			end
		else
			wrist.inSince = nil
		end
	else
		wrist.inSince = nil
		if near and faceDeg <= Config.WristHideDeg and gazeDeg <= Config.WristGazeHideDeg then
			wrist.outSince = nil
		else
			wrist.outSince = wrist.outSince or now
			if now - wrist.outSince >= Config.WristHideHold then
				wrist.shown = false
				wristLog("hide", string.format("face %.0f deg, gaze %.0f deg", faceDeg, gazeDeg))
			end
		end
	end
	-- event samples (stage t): card open/close, the X/A toggle, and the off hand held near the face while the card
	-- stays closed (the "I looked but nothing showed" case). At most one per 1.5 s; near-face at most every 15 s.
	local event = wrist.pendingEvent
	wrist.pendingEvent = nil
	if not event and wrist.prevShown ~= nil and wrist.shown ~= wrist.prevShown then
		event = wrist.shown and "open" or "close"
	end
	wrist.prevShown = wrist.shown
	if not event and not wrist.shown and not blocked and dist < WRIST_NEAR_FACE and now - (wrist.nearFaceAt or -math.huge) >= 15 then
		event = "nearFace"
		wrist.nearFaceAt = now
	end
	if event and now - (wrist.eventAt or -math.huge) >= 1.5 then
		wrist.eventAt = now
		wristLog("pose", event)
		sendPose(event)
	end
	local target = wrist.shown and 1 or 0
	wrist.alpha += (target - wrist.alpha) * math.min(1, dt * WRIST_FADE)
	if math.abs(target - wrist.alpha) < 0.01 then
		wrist.alpha = target
	end
	wrist.group.GroupTransparency = 1 - wrist.alpha
	wrist.gui.Enabled = wrist.alpha > 0
	local visible = wrist.alpha > 0
	if visible or wrist.bracerVisible then
		for _, b in wrist.bracer do
			b.part.Transparency = visible and 1 - wrist.alpha * (1 - b.base) or 1
		end
		wrist.bracerVisible = visible
	end
	if visible then
		if #wrist.bracer > 0 then
			local parts, cfs = {}, {}
			for _, b in wrist.bracer do
				table.insert(parts, b.part)
				table.insert(cfs, bracerCF * b.offset)
			end
			workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
		end
		-- card on the face: text reads toward the fingers on the left wrist (away from them on the right), so it's
		-- upright with the forearm across the body; the pointer strip fits within the face
		local read = leftHand and fingers or -fingers
		-- Top canvas spans local Z by X; rotate it upright and retain the approved rim clearance.
		wrist.part.CFrame = CFrame.fromMatrix(facePos, -read, back) * CFrame.Angles(0, math.pi / 2, 0)
	end
end

function HUD.toggleWrist()
	if not wrist then return end
	wrist.manual = not (wrist.manual or wrist.shown)
	-- A button dismissal stays closed until the wrist leaves the watch pose.
	wrist.manualDismissed = not wrist.manual
	wrist.shown = false
	wrist.inSince, wrist.outSince = nil, nil
	wrist.pendingEvent = "button"
	wristLog("toggle", wrist.manual and "controller on" or "controller off")
end

-- Studio harness: the wrist show/hide log ({t, event, why}) since `since` (os.clock), and console printing.
function HUD.wristEvents(since: number?, printing: boolean?)
	if not wrist then
		return {}
	end
	if printing ~= nil then
		wrist.logPrint = printing
	end
	local out = {}
	for _, e in wrist.events do
		if not since or e.t >= since then
			table.insert(out, e)
		end
	end
	return out
end

-- Studio harness: the wrist card's state.
function HUD.wristState()
	if not wrist then
		return nil
	end
	return { hand = wrist.leftHand and "LeftHand" or "RightHand", shown = wrist.shown == true, alpha = wrist.alpha, faceDeg = wrist.faceDeg, gazeDeg = wrist.gazeDeg, blocked = wrist.blocked, bracer = #wrist.bracer, hole = wrist.hole.Text, name = wrist.name.Text, par = wrist.par.Text, stroke = wrist.stroke.Text, total = wrist.total.Text, best = wrist.best.Text }
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
	info = panel({ Name = "Info", Position = UDim2.new(0, 12, 0, 12), Size = UDim2.new(0, 290, 0, 64) }, gui)
	infoTitle = label({ Size = UDim2.new(1, -20, 0, 30), Position = UDim2.new(0, 10, 0, 4), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left }, info)
	infoSub = label({ Size = UDim2.new(1, -20, 0, 22), Position = UDim2.new(0, 10, 0, 36), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = Color3.fromRGB(190, 230, 200) }, info)

	-- (the Roblox player list is hidden by GolfMain, so the top-right corner is ours; the scorecard lists everyone)
	local btns = new("Frame", { Name = "GolfButtons", BackgroundTransparency = 1, AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -12, 0, 12), Size = UDim2.new(0, 120, 0, 156) }, gui)
	golfButtons = btns
	new("UIListLayout", { Padding = UDim.new(0, 8), HorizontalAlignment = Enum.HorizontalAlignment.Right, SortOrder = Enum.SortOrder.LayoutOrder }, btns)
	button("Reset Ball", { Name = "ResetBall", LayoutOrder = 1, Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(60, 90, 150) }, btns, function()
		if Ball then
			Ball.requestReset()
		end
	end)
	-- (named ScorecardButton so the harness' FindFirstChild("Scorecard", true) only finds the card itself)
	button("Scorecard", { Name = "ScorecardButton", LayoutOrder = 2, Size = UDim2.new(1, 0, 0, 44) }, btns, HUD.toggleScorecard)
	button("Explore", { Name = "Explore", LayoutOrder = 3, Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(210, 120, 40) }, btns, function()
		if Explore then
			Explore.setActive(true)
		end
	end)
	-- (stage z) no Menu button here: FrontEnd's top-right Menu button is the only one (lobby and course)

	-- Explore mode bar (replaces the golf buttons while exploring)
	exploreBar = new("Frame", { Name = "ExploreBar", BackgroundTransparency = 1, AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -12, 0, 12), Size = UDim2.new(0, 150, 0, 260), Visible = false }, gui)
	new("UIListLayout", { Padding = UDim.new(0, 8), HorizontalAlignment = Enum.HorizontalAlignment.Right, SortOrder = Enum.SortOrder.LayoutOrder }, exploreBar)
	button("Back to golf", { Name = "BackToGolf", LayoutOrder = 1, Size = UDim2.new(1, 0, 0, 50), BackgroundColor3 = Color3.fromRGB(40, 140, 80) }, exploreBar, function()
		closeTeleportMenu()
		if Explore then
			Explore.setActive(false)
		end
	end)
	button("Teleport", { Name = "Teleport", LayoutOrder = 2, Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(110, 80, 170) }, exploreBar, function()
		HUD.toggleTeleportMenu()
	end)
	sprintButton = button("Sprint: off", { Name = "Sprint", LayoutOrder = 3, Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(60, 90, 150) }, exploreBar, function()
		if Explore then
			Explore.setSprint(not Explore.isSprinting())
		end
	end)
	flyButton = button("Fly: off", { Name = "Fly", LayoutOrder = 4, Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = Color3.fromRGB(60, 90, 150) }, exploreBar, function()
		if Explore then
			Explore.setFly(not Explore.isFlying())
		end
	end)
	-- hold to climb / sink while flying (keyboard: Space/E and Q/Ctrl). Bottom right, left of the touch jump button.
	flyButtons = new("Frame", { Name = "FlyButtons", BackgroundTransparency = 1, AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, -250, 1, -52), Size = UDim2.new(0, 184, 0, 84), Visible = false }, gui)
	new("UIListLayout", { Padding = UDim.new(0, 12), FillDirection = Enum.FillDirection.Horizontal, SortOrder = Enum.SortOrder.LayoutOrder }, flyButtons)
	local holdUp, holdDown = false, false
	for i, spec in { { "Down", false }, { "Up", true } } do
		local b = button(spec[1], { Name = spec[1], LayoutOrder = i, Size = UDim2.new(0, 84, 0, 84), BackgroundColor3 = Color3.fromRGB(80, 120, 170), BackgroundTransparency = 0.25 }, flyButtons, function() end)
		b.MouseButton1Down:Connect(function()
			if spec[2] then holdUp = true else holdDown = true end
			if Explore then Explore.setFlyVertical(holdUp, holdDown) end
		end)
		local function release()
			if spec[2] then holdUp = false else holdDown = false end
			if Explore then Explore.setFlyVertical(holdUp, holdDown) end
		end
		b.MouseButton1Up:Connect(release)
		b.MouseLeave:Connect(release)
	end

	powerFrame = panel({ Name = "Power", AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -70), Size = UDim2.new(0, 300, 0, 34), Visible = false }, gui)
	local track = new("Frame", { Position = UDim2.new(0, 8, 0, 8), Size = UDim2.new(1, -16, 1, -16), BackgroundColor3 = Color3.fromRGB(0, 0, 0), BackgroundTransparency = 0.5 }, powerFrame)
	corner(track, 6)
	powerFill = new("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.fromRGB(90, 230, 90) }, track)
	corner(powerFill, 6)
	powerLabel = label({ Size = UDim2.fromScale(1, 1), TextScaled = true, Text = "", ZIndex = 3, TextStrokeTransparency = 0.5 }, track)

	-- the pull line is drawn in raw screen pixels, so it lives in its own unscaled ScreenGui
	aimGui = new("ScreenGui", { Name = "GolfAim", ResetOnSpawn = false }, gui.Parent)
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
		TextWrapped = true,
		Text = "",
		TextColor3 = Color3.fromRGB(235, 245, 235),
		TextStrokeTransparency = 0.5,
	}, gui)
	new("UITextSizeConstraint", { MaxTextSize = 20 }, hint)
end

local TOUCH = game:GetService("UserInputService").TouchEnabled
local HINTS = {
	golf = TOUCH and "Pull back from the ball to putt  -  drag elsewhere to look around  -  pinch to zoom"
		or "Drag back from the ball to putt  -  drag elsewhere to look around  -  scroll to zoom  -  R to reset",
	explore = TOUCH and "Thumbstick to walk  -  jump button  -  Sprint / Fly buttons  -  Teleport to any hole or view"
		or "WASD walk  -  Space jump  -  hold Shift sprint  -  F fly (Space/E up, Q down)  -  T teleport",
}

-- Bottom help line: wraps onto two lines on narrow screens (phones, small windows) instead of shrinking to nothing.
local function layoutHint()
	if not hint then
		return
	end
	local vp = workspace.CurrentCamera.ViewportSize
	local w = vp.X / (uiScale and uiScale.Scale or 1)
	hint.Text = (Explore and Explore.active) and HINTS.explore or HINTS.golf
	local narrow = w < 1000
	hint.Size = UDim2.new(narrow and 0.62 or 0.9, 0, 0, narrow and 40 or 22)
	-- on phones, keep it clear of the touch thumbstick (left) and jump button (right) while exploring
	hint.Position = UDim2.new(0.5, 0, 1, narrow and -8 or -16)
end

-- Roblox chat sits in the top-left corner; slide the hole/par/strokes panel below it while it's open. On desktop,
-- always (new-message notices pop up there even with the window closed); on phones only while it's open.
local TextChatService = game:GetService("TextChatService")
local function chatBottom()
	local cfg = TextChatService:FindFirstChildOfClass("ChatWindowConfiguration")
	if not cfg or not cfg.Enabled then
		return nil
	end
	local ok, open = pcall(function()
		return game:GetService("StarterGui"):GetCore("ChatActive")
	end)
	if ok and open == false and TOUCH then
		return nil
	end
	local ok2, pos, size = pcall(function()
		return cfg.AbsolutePosition, cfg.AbsoluteSize
	end)
	if not ok2 or not size or size.Y < 1 then
		return nil
	end
	return pos.Y + size.Y, pos.X + size.X
end

local function layoutInfo()
	if not info or not gui then
		return
	end
	local scale = uiScale and uiScale.Scale or 1
	local y = 12
	local bottom, right = chatBottom()
	if bottom and right and right > gui.AbsolutePosition.X + 12 then
		-- (chat rects are in screen pixels; the HUD is scaled and starts under the top bar)
		y = math.max(12, (bottom - gui.AbsolutePosition.Y) / scale + 8)
	end
	info.Position = UDim2.new(0, 12, 0, y)
end

closeTeleportMenu = function()
	if teleportMenu then
		teleportMenu:Destroy()
		teleportMenu = nil
	end
end

-- Explore teleport menu: H1..H9 tee views + scenic viewpoints.
function HUD.toggleTeleportMenu()
	if teleportMenu then
		closeTeleportMenu()
		return
	end
	if not (Explore and Explore.active and gui) then
		return
	end
	local dests = Explore.destinations()
	local holesList, views = {}, {}
	for _, d in dests do
		table.insert(d.kind == "hole" and holesList or views, d)
	end
	local vp = workspace.CurrentCamera.ViewportSize
	local scale = uiScale and uiScale.Scale or 1
	local w = math.min(560, vp.X / scale - 40)
	local h = math.min(420, vp.Y / scale - 40)
	teleportMenu = panel({ Name = "TeleportMenu", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.new(0, w, 0, h), BackgroundTransparency = 0.08, ZIndex = 20 }, gui)
	label({ Text = "Teleport", Size = UDim2.new(1, -60, 0, 36), Position = UDim2.new(0, 14, 0, 6), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 21, TextColor3 = Color3.fromRGB(255, 230, 120) }, teleportMenu)
	button("X", { AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, -8, 0, 8), Size = UDim2.new(0, 36, 0, 36), BackgroundColor3 = Color3.fromRGB(150, 50, 50), ZIndex = 22 }, teleportMenu, closeTeleportMenu)
	local body = new("ScrollingFrame", { BackgroundTransparency = 1, BorderSizePixel = 0, Position = UDim2.new(0, 12, 0, 50), Size = UDim2.new(1, -24, 1, -60), ScrollBarThickness = 6, AutomaticCanvasSize = Enum.AutomaticSize.Y, CanvasSize = UDim2.new(), ZIndex = 21 }, teleportMenu)
	new("UIListLayout", { Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder }, body)
	local function section(title, list, perRow, color, order)
		label({ Text = title, Size = UDim2.new(1, 0, 0, 24), TextScaled = true, TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = Color3.fromRGB(180, 220, 190), ZIndex = 21, LayoutOrder = order }, body)
		local grid = new("Frame", { BackgroundTransparency = 1, Size = UDim2.new(1, -8, 0, 0), AutomaticSize = Enum.AutomaticSize.Y, ZIndex = 21, LayoutOrder = order + 1 }, body)
		new("UIGridLayout", { CellPadding = UDim2.fromOffset(8, 8), CellSize = UDim2.new(1 / perRow, -8, 0, 44), SortOrder = Enum.SortOrder.LayoutOrder }, grid)
		for i, d in list do
			local b = button(d.name, { Name = d.name, BackgroundColor3 = color, ZIndex = 22, LayoutOrder = i }, grid, function()
				closeTeleportMenu()
				Explore.teleport(d)
			end)
			b.Size = UDim2.new(0, 0, 0, 44)
		end
	end
	section("Holes (tee view)", holesList, w < 400 and 3 or 5, Color3.fromRGB(40, 140, 80), 1)
	section("Scenic views", views, w < 400 and 2 or 3, Color3.fromRGB(110, 80, 170), 3)
end

-- Explore mode on/off: swap the golf buttons for the explore bar and update the help text.
local function onExploreChanged(active)
	if golfButtons then
		golfButtons.Visible = not active
		exploreBar.Visible = active
		flyButtons.Visible = active and Explore.isFlying()
		sprintButton.Text = Explore.isSprinting() and "Sprint: ON" or "Sprint: off"
		sprintButton.BackgroundColor3 = Explore.isSprinting() and Color3.fromRGB(210, 120, 40) or Color3.fromRGB(60, 90, 150)
		flyButton.Text = Explore.isFlying() and "Fly: ON" or "Fly: off"
		flyButton.BackgroundColor3 = Explore.isFlying() and Color3.fromRGB(210, 120, 40) or Color3.fromRGB(60, 90, 150)
	end
	if not active then
		closeTeleportMenu()
		HUD.hidePower()
	end
	layoutHint()
	HUD.refresh()
end

function HUD.attachFrontEnd(frontEnd)
	FrontEnd = frontEnd
end

-- While the front-end menu is up: hide the screen HUD (phone/desktop) and any open scorecard. The VR wrist and
-- message panels stay.
function HUD.setMenuHidden(hidden)
	if hidden then
		closeScorecard()
		closeTeleportMenu()
		HUD.hidePower()
	end
	if not HUD.isVR and gui then
		gui.Enabled = not hidden
		if aimGui then
			aimGui.Enabled = not hidden
		end
	end
end

---------------------------------------------------------------------------- audio
-- SoundService.SFX / SoundService.Music (created if missing); the Settings volumes set their Volume.
function HUD.soundGroup(name)
	local g = SoundService:FindFirstChild(name)
	if not (g and g:IsA("SoundGroup")) then
		g = new("SoundGroup", { Name = name, Volume = 1 }, SoundService)
	end
	return g
end

local sfxSounds = {} -- [Config.Sounds key] = Sound
local sfxTokens = {}
local sfxTweens = {}
-- Plays a pooled SFX; sounds longer than Config.ReactionFadeAfter fade out from then on.
function HUD.playSfx(key, volume, speed)
	local s = sfxSounds[key]
	if not s then
		return
	end
	sfxTokens[key] = (sfxTokens[key] or 0) + 1
	local token = sfxTokens[key]
	if sfxTweens[key] then
		sfxTweens[key]:Cancel()
		sfxTweens[key] = nil
	end
	s.Volume = volume or 0.5
	s.PlaybackSpeed = speed or 1
	s.TimePosition = 0
	s:Play()
	local fadeAfter = Config.ReactionFadeAfter or 4
	if s.TimeLength == 0 or s.TimeLength / s.PlaybackSpeed > fadeAfter + 0.5 then
		task.delay(fadeAfter, function()
			if sfxTokens[key] ~= token or not s.IsPlaying then
				return
			end
			local tw = TweenService:Create(s, TweenInfo.new(1.2, Enum.EasingStyle.Sine), { Volume = 0 })
			sfxTweens[key] = tw
			tw.Completed:Connect(function(state)
				if state == Enum.PlaybackState.Completed and sfxTokens[key] == token then
					s:Stop()
				end
			end)
			tw:Play()
		end)
	end
end

-- Hole-out for the local player: a soft cup plunk, then a crowd reaction by strokes vs par.
local function holeOutAudio(strokes, par, maxed)
	local d = strokes - (par or strokes)
	local plays
	if maxed or d >= 2 then
		plays = { { "Aww", 0.6 } }
	elseif strokes == 1 or d <= -2 then
		plays = { { "CheerBig", 0.7 }, { "Applause", 0.45 } }
	elseif d == -1 then
		plays = { { "Birdie", 0.65 } }
	elseif d == 0 then
		plays = { { "Par", 0.55 } }
	else
		plays = { { "Bogey", 0.6 } }
	end
	if not maxed then
		HUD.playSfx("CupPlunk", 0.5, 0.9)
	end
	task.delay(maxed and 0 or (Config.ReactionDelay or 0.25), function()
		for _, p in plays do
			HUD.playSfx(p[1], p[2])
		end
	end)
end

local function setupAudio()
	local sfxGroup = HUD.soundGroup("SFX")
	HUD.soundGroup("Music")
	local list = {}
	for key, id in Config.Sounds or {} do
		local s = new("Sound", { Name = "Sfx_" .. key, SoundId = id, Volume = 0.5, SoundGroup = sfxGroup }, script)
		sfxSounds[key] = s
		table.insert(list, s)
	end
	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync(list)
		end)
	end)
	-- route the other client sounds (BallController's putt click, the teleport ring ping) through SFX too
	local function route(d)
		if d:IsA("Sound") and d.SoundGroup == nil then
			d.SoundGroup = sfxGroup
		end
	end
	for _, d in script.Parent:GetDescendants() do
		route(d)
	end
	script.Parent.DescendantAdded:Connect(route)
	workspace.CurrentCamera.DescendantAdded:Connect(route)
end

function HUD.attachExplore(explore)
	Explore = explore
	Explore.Changed.Event:Connect(onExploreChanged)
	onExploreChanged(Explore.active)
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

	VRPointer.register(vrCardPart, vrCardGui, { modal = true })

	-- WristFace Top: wrist_card_bg_nobuttons.png (1024x784, symmetric, so the same art on either wrist) with the
	-- text drawn live on top (zones from assets/vr-mini-golf/ui/README_wrist_scorecard.md). No buttons: the scorecard is
	-- B / Y, and settings (and from there the menu) are the gear on the scorecard.
	local CW, CH = 1024, 784
	local FACE_W = 0.37
	local part, gui = vrPanel("VRWrist", Vector3.new(FACE_W, FACE_W * CH / CW, 0.002), Vector2.new(CW, CH))
	gui.Enabled = false
	-- the bracer: a client copy in the camera, every part non-colliding, non-queryable, massless; moved as one
	local bracer = {}
	local face
	local src = Golf:FindFirstChild("WristBracer")
	if src then
		local model = src:Clone()
		local pivot = model:GetPivot()
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") then
				d.Anchored, d.CanCollide, d.CanQuery, d.CanTouch, d.Massless, d.CastShadow = true, false, false, false, true, false
				table.insert(bracer, { part = d, offset = pivot:ToObjectSpace(d.CFrame), base = d.Transparency })
				d.Transparency = 1
				if d.Name == "WristFace" then face = d end
			end
		end
		model.Parent = workspace.CurrentCamera
	end
	if face then
		part:Destroy()
		part = face
	else
		part.Name = "WristFace"
	end
	-- 15.625% wider, with exact canvas aspect (nominal 0.37 x 0.28 studs).
	part.Size = Vector3.new(FACE_W * CH / CW, 0.001, FACE_W)
	gui.Adornee = part
	gui.Face = Enum.NormalId.Top
	-- Adorned CanvasGroups need depth rendering here. The existing .256 lift clears the .252 rim.
	gui.AlwaysOnTop = false
	local group = new("CanvasGroup", { Name = "Card", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), GroupTransparency = 1 }, gui)
	new("ImageLabel", { Name = "Background", BackgroundTransparency = 1, Image = Config.UI.WristCardBg, Size = UDim2.fromScale(1, 1) }, group)
	local VALUE, LABEL = Color3.fromHex("4A240E"), Color3.fromHex("9C5218")
	-- (x, y) = the text's left (or right) edge and vertical centre on the canvas
	local function text(name, x, y, w, size, color, align)
		local right = align == Enum.TextXAlignment.Right
		-- (TextScaled capped at the design size, so a long hole name shrinks to fit instead of spilling)
		local t = label({ Name = name, Text = "", Font = FONT, TextScaled = true, TextColor3 = color, TextXAlignment = align or Enum.TextXAlignment.Left, AnchorPoint = Vector2.new(right and 1 or 0, 0.5), Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(w, size + 8) }, group)
		new("UITextSizeConstraint", { MaxTextSize = size }, t)
		return t
	end
	local function icon(name, x, y, s)
		new("ImageLabel", { Name = name, BackgroundTransparency = 1, Image = Config.UI[name], Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(s, s) }, group)
	end
	wrist = { part = part, gui = gui, group = group, alpha = 0, shown = false, bracer = bracer, events = {} }
	-- header zone 80,72-944,212: flag, "HOLE n", hole name on the right
	icon("IconHole", 94, 92, 100)
	wrist.hole = text("Hole", 210, 142, 330, 76, VALUE)
	wrist.name = text("HoleName", 916, 142, 370, 40, LABEL, Enum.TextXAlignment.Right)
	-- 2x2 zones (418x223): icon in the zone's circle, label over value
	for _, z in { { "par", "PAR", "IconPar", 80, 236 }, { "stroke", "STROKE", "IconStroke", 526, 236 }, { "total", "TOTAL", "IconTotal", 80, 481 }, { "best", "BEST", "IconBest", 526, 481 } } do
		local x, y = z[4], z[5]
		icon(z[3], x + 30, y + 63, 96)
		text(z[2] .. "Label", x + 160, y + 78, 238, 38, LABEL).Text = z[2]
		wrist[z[1]] = text(z[1], x + 160, y + 144, 238, 78, VALUE)
	end
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
	uiScale = new("UIScale", {}, gui)
	local function rescale()
		local vp = workspace.CurrentCamera.ViewportSize
		uiScale.Scale = math.clamp(math.min(vp.X, vp.Y) / 620, 0.6, 1.15)
		layoutHint()
		layoutInfo()
	end
	cardParent = gui
	if isVR then
		buildVR()
	else
		buildScreen()
	end
	rescale()
	workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
	if not isVR then
		task.spawn(function()
			while gui.Parent do
				layoutInfo()
				task.wait(0.5)
			end
		end)
	end

	player:GetAttributeChangedSignal("Strokes"):Connect(HUD.refresh)
	player:GetAttributeChangedSignal("Hole"):Connect(function() completedWristHole = nil; HUD.refresh() end)
	player:GetAttributeChangedSignal("Strokes"):Connect(function() if player:GetAttribute("Strokes") == 0 then completedWristHole = nil end end)
	-- (the VR wrist card shows the round total and the personal best)
	player:GetAttributeChangedSignal("Scores"):Connect(HUD.refresh)
	player:GetAttributeChangedSignal("HoleHoled"):Connect(HUD.refresh)
	for _, c in Config.Courses do
		player:GetAttributeChangedSignal("Best_" .. c.id):Connect(HUD.refresh)
	end
	player:GetAttributeChangedSignal("Course"):Connect(HUD.refresh)

	-- Hole-to-hole travel (Walkabout style): after holing out, fade to black just before the server moves the ball
	-- to the next tee, and fade back in once you've been put there (VR: warped beside the ball; desktop/phone: the
	-- camera cuts to it). A camera ColorCorrection tint, so it also covers the headset view (ScreenGuis don't).
	local fade = new("ColorCorrectionEffect", { Name = "GolfFade", TintColor = Color3.new(1, 1, 1) }, workspace.CurrentCamera)
	local fadeToken = 0
	local function setFade(black, seconds)
		fadeToken += 1
		HUD.faded = black
		TweenService:Create(fade, TweenInfo.new(seconds, Enum.EasingStyle.Sine), {
			TintColor = black and Color3.new(0, 0, 0) or Color3.new(1, 1, 1),
			Brightness = black and -0.5 or 0,
		}):Play()
		return fadeToken
	end
	HUD.setFade = setFade
	local FADE_OUT = 0.45
	Remotes.HoleComplete.OnClientEvent:Connect(function(who, holeNum)
		if who ~= player or holeNum >= #holeList() then
			return
		end
		task.delay(math.max(0, Config.HoleTransitionTime - FADE_OUT - 0.05), function()
			local token = setFade(true, FADE_OUT)
			-- never leave the screen black if the placement doesn't come
			task.delay(FADE_OUT + 3, function()
				if fadeToken == token and HUD.faded then
					setFade(false, 0.5)
				end
			end)
		end)
	end)

	Ball.Placed.Event:Connect(function(_, reason)
		HUD.refresh()
		if HUD.faded then
			task.delay(0.15, function()
				setFade(false, 0.6)
			end)
		end
		if reason == "hole" then
			local hole = Ball.getHole()
			HUD.message(string.format("Hole %d  -  Par %d", hole:GetAttribute("HoleNumber"), hole:GetAttribute("Par")), Color3.fromRGB(255, 230, 120), 2.2)
		end
	end)

	-- teleport rings (H8 firefly ring, H9 secret Lantern Knot)
	Ball.Teleported.Event:Connect(function(id)
		if id == "lantern_knot" then
			HUD.message("Secret!  The Lantern Knot", Color3.fromHex("FFB347"), 2)
		else
			HUD.toast("Whoosh!  Firefly ring")
		end
	end)

	setupAudio()
	Remotes.HoleComplete.OnClientEvent:Connect(function(who, holeNum, strokes, par, maxed)
		local name, color = scoreName(strokes, par)
		if who == player then
			completedWristHole = holeNum
			holeOutAudio(strokes, par, maxed)
			HUD.message(maxed and ("Max strokes  -  " .. strokes) or name, color, 3)
		else
			HUD.toast(string.format("%s: %s on hole %d", who.DisplayName, maxed and tostring(strokes) or name, holeNum))
		end
		HUD.refresh()
	end)
	Remotes.Notice.OnClientEvent:Connect(function(text, kind)
		HUD.message(text, kind == "bad" and Color3.fromRGB(255, 120, 100) or Color3.new(1, 1, 1), 2)
	end)
	-- (scores, result): result = { course, total, par, best, previousBest, newBest, counted } from GolfServer
	Remotes.CourseComplete.OnClientEvent:Connect(function(scores, result)
		if FrontEnd then
			FrontEnd.showResults(scores, result)
		else
			buildScorecard(true)
		end
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
