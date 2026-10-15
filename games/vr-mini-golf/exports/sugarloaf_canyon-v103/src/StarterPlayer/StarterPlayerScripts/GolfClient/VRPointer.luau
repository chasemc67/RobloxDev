-- VRPointer: Walkabout-style laser pointer for the VR menus (stage p, Chase's VR playtest: he never found the
-- thumbstick-click menu hint).
--   * Every world-space VR panel (FrontEnd menu, VR scorecard, wrist card) registers its part + SurfaceGui here.
--   * A ray from the pointing controller's aim pose (hand CFrame LookVector) is intersected with each enabled panel's
--     Front face; the hit becomes a canvas point (dot) and the smallest visible button under it is hovered (glow).
--   * Trigger (either hand) = click. The hand that pulls the trigger becomes the pointing hand; the club hand points
--     by default. A trigger that clicks nothing while a modal panel (menu, scorecard) is up is still eaten, so it
--     never warps you to the ball from a menu.
--   * The beam only shows while a modal panel is up, or while it is actually on a non-modal panel (the wrist card's
--     buttons). During play it's hidden.
-- Buttons are bound with VRPointer.bind(button, fn), which returns a debounced fn to connect to Activated as well
-- (the core Roblox VR pointer, if it ever clicks the same button, can't double-fire it).
local HapticService = game:GetService("HapticService")
local StarterGui = game:GetService("StarterGui")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Config"))

local VRPointer = {}

local MAX_RANGE = 40 -- studs
local IDLE_LENGTH = 6 -- beam length when a menu is up but the ray misses every panel
local DOT_STUDS = 0.09 -- pointer dot diameter on the panel (2.7 cm)
local GLOW_PAD = 20 -- hover glow reaches this many design px past the button on each side
local DEBOUNCE = 0.3

local BEAM = Color3.fromHex("FFB040")
local CORE = Color3.fromHex("FFE4A0")

type Panel = { part: BasePart, gui: SurfaceGui, modal: boolean, scale: number, enabled: (() -> boolean)?, dot: ImageLabel?, glow: ImageLabel? }

local panels: { Panel } = {}
local handlers: { [GuiButton]: () -> () } = {} -- [GuiButton] = debounced fn (not weak: Roblox can drop an
-- Instance's Lua proxy while the Instance lives on, which empties weak keys; cleared on Destroying instead)
local simulate = false
local pointHand: Enum.UserCFrame? = nil -- nil = the club hand
local clubHand = Enum.UserCFrame.RightHand
local hands: { [Enum.UserCFrame]: CFrame } = {}

-- what the pointer is on right now (VRPointer.state())
local current = { panel = nil :: Panel?, button = nil :: GuiButton?, point = nil :: Vector3?, pixel = nil :: Vector2?, beam = false }

local beamPart, a0, a1, beamMain, beamCore

local function new(className, props, parent)
	local inst = Instance.new(className)
	for k, v in props do
		inst[k] = v
	end
	inst.Parent = parent
	return inst
end

local function ensureBeam()
	if beamPart and beamPart.Parent then
		return
	end
	beamPart = new("Part", { Name = "VRPointerBeam", Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false, Transparency = 1, Size = Vector3.one * 0.05 }, workspace.CurrentCamera)
	a0 = new("Attachment", { Name = "From" }, beamPart)
	a1 = new("Attachment", { Name = "To" }, beamPart)
	-- additive amber glow with a pale core, a little more see-through at the tip
	beamMain = new("Beam", {
		Name = "Glow",
		Attachment0 = a0,
		Attachment1 = a1,
		Color = ColorSequence.new(BEAM),
		LightEmission = 1,
		LightInfluence = 0,
		FaceCamera = true,
		Segments = 1,
		Width0 = 0.04,
		Width1 = 0.03,
		Transparency = NumberSequence.new(0.15, 0.3),
		Enabled = false,
	}, beamPart)
	beamCore = new("Beam", {
		Name = "Core",
		Attachment0 = a0,
		Attachment1 = a1,
		Color = ColorSequence.new(CORE),
		LightEmission = 1,
		LightInfluence = 0,
		FaceCamera = true,
		Segments = 1,
		Width0 = 0.012,
		Width1 = 0.01,
		Transparency = NumberSequence.new(0, 0.2),
		Enabled = false,
	}, beamPart)
end

local function haptic(hand: Enum.UserCFrame, strength: number, duration: number)
	if simulate then
		return
	end
	local motor = hand == Enum.UserCFrame.RightHand and Enum.VibrationMotor.RightHand or Enum.VibrationMotor.LeftHand
	pcall(function()
		HapticService:SetMotor(Enum.UserInputType.Gamepad1, motor, strength)
	end)
	task.delay(duration, function()
		pcall(function()
			HapticService:SetMotor(Enum.UserInputType.Gamepad1, motor, 0)
		end)
	end)
end

-- Register a world-space panel. opts: modal (menu/scorecard: beam always on, trigger eaten), scale (canvas px per
-- design px, for the glow padding), enabled (extra gate, e.g. the wrist card only while it's faded in).
function VRPointer.register(part: BasePart, gui: SurfaceGui, opts)
	opts = opts or {}
	local p: Panel = { part = part, gui = gui, modal = opts.modal == true, scale = opts.scale or 1, enabled = opts.enabled }
	table.insert(panels, p)
	return p
end

-- Bind a button's click. Returns the debounced click fn (connect Activated to it too).
function VRPointer.bind(button: GuiButton, fn: () -> ())
	local last = 0
	local function fire()
		local now = os.clock()
		if now - last < DEBOUNCE then
			return
		end
		last = now
		fn()
	end
	handlers[button] = fire
	button.Destroying:Connect(function()
		handlers[button] = nil
	end)
	return fire
end

local function panelOn(p: Panel): boolean
	if not (p.gui.Enabled and p.gui.Parent and p.part.Parent) then
		return false
	end
	return p.enabled == nil or p.enabled()
end

local function modalOpen(): boolean
	for _, p in panels do
		if p.modal and panelOn(p) then
			return true
		end
	end
	return false
end
VRPointer.modalOpen = modalOpen

local function visibleChain(g: GuiObject, gui: SurfaceGui): boolean
	local o: Instance? = g
	while o and o ~= gui do
		if o:IsA("GuiObject") and not o.Visible then
			return false
		end
		o = o.Parent
	end
	return o == gui
end

-- The smallest visible, bound button under canvas pixel `px` on panel `p`.
local function buttonAt(p: Panel, px: Vector2): GuiButton?
	local best, bestArea = nil, math.huge
	for _, d in p.gui:GetDescendants() do
		if d:IsA("GuiButton") and handlers[d] and d.Active ~= false then
			local pos, size = d.AbsolutePosition, d.AbsoluteSize
			if px.X >= pos.X and px.X <= pos.X + size.X and px.Y >= pos.Y and px.Y <= pos.Y + size.Y then
				local area = size.X * size.Y
				if area < bestArea and visibleChain(d, p.gui) then
					best, bestArea = d, area
				end
			end
		end
	end
	return best
end

-- Shared face basis for rendering and pointer targets: Front panels and Top wrist face.
local function faceBasis(p: Panel)
	local cf, size = p.part.CFrame, p.part.Size
	if p.gui.Face == Enum.NormalId.Top then
		return cf.Position + cf.UpVector * size.Y / 2, cf.UpVector, cf.LookVector, cf.RightVector, size.Z, size.X
	end
	return cf.Position + cf.LookVector * size.Z / 2, cf.LookVector, -cf.RightVector, -cf.UpVector, size.X, size.Y
end

local function hitPanel(p: Panel, origin: Vector3, dir: Vector3): (Vector3?, Vector2?, number?)
	local centre, n, right, down, w, h = faceBasis(p)
	local denom = dir:Dot(n)
	if denom > -1e-3 then return nil end
	local t = (centre - origin):Dot(n) / denom
	if t <= 0 or t > MAX_RANGE then return nil end
	local hit = origin + dir * t
	local delta = hit - centre
	local x, y = delta:Dot(right), delta:Dot(down)
	if math.abs(x) > w / 2 or math.abs(y) > h / 2 then return nil end
	local canvas = p.gui.AbsoluteSize
	if canvas.X < 1 then canvas = p.gui.CanvasSize end
	return hit, Vector2.new((0.5 + x / w) * canvas.X, (0.5 + y / h) * canvas.Y), t
end

local function aimOf(hand: Enum.UserCFrame): (Vector3?, Vector3?)
	local cf = hands[hand]
	if not cf then
		return nil
	end
	return cf.Position, cf.LookVector
end

-- Nearest panel hit for `hand`: panel, world point, canvas pixel, button.
local function probe(hand: Enum.UserCFrame)
	local origin, dir = aimOf(hand)
	if not origin then
		return nil
	end
	local bestP, bestHit, bestPx, bestT = nil, nil, nil, math.huge
	for _, p in panels do
		if panelOn(p) then
			local hit, px, t = hitPanel(p, origin, dir)
			if hit and t < bestT then
				bestP, bestHit, bestPx, bestT = p, hit, px, t
			end
		end
	end
	if not bestP then
		return nil
	end
	return bestP, bestHit, bestPx, buttonAt(bestP, bestPx)
end

local function ensureDecor(p: Panel)
	if not (p.dot and p.dot.Parent) then
		local canvas = p.gui.CanvasSize
		local dotPx = math.max(12, DOT_STUDS / p.part.Size.X * canvas.X)
		p.dot = new("ImageLabel", {
			Name = "PointerDot",
			BackgroundTransparency = 1,
			Image = Config.UI.PointerDot,
			AnchorPoint = Vector2.new(0.5, 0.5),
			Size = UDim2.fromOffset(dotPx, dotPx),
			ZIndex = 1001,
			Visible = false,
		}, p.gui)
	end
	if not (p.glow and p.glow.Parent) then
		p.glow = new("ImageLabel", {
			Name = "HoverGlow",
			BackgroundTransparency = 1,
			Image = Config.UI.HoverGlow,
			ScaleType = Enum.ScaleType.Slice,
			SliceCenter = Rect.new(40, 40, 88, 88),
			SliceScale = p.scale * 0.5,
			ZIndex = 1000,
			Visible = false,
		}, p.gui)
	end
end

local function hideDecor(except: Panel?)
	for _, p in panels do
		if p ~= except then
			if p.dot then
				p.dot.Visible = false
			end
			if p.glow then
				p.glow.Visible = false
			end
		end
	end
end

local function activeHand(): Enum.UserCFrame
	return pointHand or clubHand
end

-- Every frame (VRControls): world CFrames of both hands, the club hand.
function VRPointer.update(handCFs: { [Enum.UserCFrame]: CFrame }, club: Enum.UserCFrame)
	hands = handCFs
	clubHand = club
	ensureBeam()
	local modal = modalOpen()
	if not modal then
		pointHand = nil -- back to the club hand for the next menu
	end
	local hand = activeHand()
	local p, hit, px, button = probe(hand)
	-- the other hand pointing at a menu while this one points nowhere takes the beam over
	if modal and not p then
		local other = hand == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
		local op, ohit, opx, obutton = probe(other)
		if op then
			pointHand = other
			hand, p, hit, px, button = other, op, ohit, opx, obutton
		end
	end
	-- non-modal panels (the wrist card) only take the pointer when it's on one of their buttons
	if p and not p.modal and not button then
		p, hit, px, button = nil, nil, nil, nil
	end
	local prevButton = current.button
	current.panel, current.point, current.pixel, current.button = p, hit, px, button
	if button ~= prevButton and button then
		haptic(hand, 0.15, 0.03)
	end

	local origin, dir = aimOf(hand)
	local show = origin ~= nil and (modal or p ~= nil)
	current.beam = show
	beamMain.Enabled = show
	beamCore.Enabled = show
	if show then
		local tip = hit or (origin + dir * IDLE_LENGTH)
		a0.WorldPosition = origin
		a1.WorldPosition = tip
	end

	hideDecor(p)
	if p then
		ensureDecor(p)
		p.dot.Visible = true
		p.dot.Position = UDim2.fromOffset(px.X, px.Y)
		if button then
			local pad = GLOW_PAD * p.scale
			local pos, size = button.AbsolutePosition, button.AbsoluteSize
			p.glow.Position = UDim2.fromOffset(pos.X - pad, pos.Y - pad)
			p.glow.Size = UDim2.fromOffset(size.X + pad * 2, size.Y + pad * 2)
			p.glow.Visible = true
		else
			p.glow.Visible = false
		end
	end
end

-- Trigger pulled on `hand`. Returns true if the pointer used it (VRControls then skips its own trigger action).
function VRPointer.press(hand: Enum.UserCFrame): boolean
	local modal = modalOpen()
	if modal and hand ~= activeHand() then
		pointHand = hand -- the other hand takes over pointing; this pull also clicks with it
	end
	local p, _, _, button = probe(hand)
	if button and (modal or (p and not p.modal)) then
		local fn = handlers[button]
		if fn then
			haptic(hand, 0.35, 0.05)
			fn()
		end
		return true
	end
	return modal
end

-- Studio harness: what the pointer is on.
function VRPointer.state()
	return {
		hand = activeHand().Name,
		modal = modalOpen(),
		beam = current.beam,
		panel = current.panel and current.panel.part.Name or nil,
		button = current.button and current.button.Name or nil,
		buttonText = current.button and current.button:IsA("TextButton") and current.button.Text or nil,
		pixel = current.pixel and { math.floor(current.pixel.X + 0.5), math.floor(current.pixel.Y + 0.5) } or nil,
	}
end

-- Studio harness: world point at the centre of every clickable button on the open panels.
function VRPointer.targets()
	local out = {}
	for _, p in panels do
		if panelOn(p) then
			local canvas = p.gui.AbsoluteSize
			if canvas.X < 1 then
				canvas = p.gui.CanvasSize
			end
			local size = p.part.Size
			for _, d in p.gui:GetDescendants() do
				if d:IsA("GuiButton") and handlers[d] and visibleChain(d, p.gui) then
					local c = d.AbsolutePosition + d.AbsoluteSize / 2
					local centre, _, right, down, width, height = faceBasis(p)
					local w = centre + right * (c.X / canvas.X - 0.5) * width + down * (c.Y / canvas.Y - 0.5) * height
					table.insert(out, { panel = p.part.Name, name = d.Name, text = d:IsA("TextButton") and d.Text or "", world = w })
				end
			end
		end
	end
	return out
end

function VRPointer.start(isSimulated: boolean)
	simulate = isSimulated
	-- our pointer replaces Roblox's own VR laser pointer (no double clicks, no second beam)
	pcall(function()
		StarterGui:SetCore("VRLaserPointerMode", "Disabled")
	end)
	pcall(function()
		StarterGui:SetCore("VRLaserPointerMode", 0)
	end)
	ensureBeam()
end

return VRPointer
