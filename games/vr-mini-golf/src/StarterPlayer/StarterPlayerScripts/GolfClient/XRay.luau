-- XRay: keeps your ball (and the VR putter head) visible through whatever blocks them (stage p, Chase's VR playtest).
--   * A Highlight with DepthMode AlwaysOnTop (subtle amber fill, soft white outline) on each target, shown only while
--     a ray from the eye (VR head, or the phone/desktop camera) to it hits something. Flat-screen views fade; VR tracks occlusion immediately each frame.
--   * The ball's outline uses the same gate as the occluder fade (Ball.seeThrough: ball at rest and the player aiming /
--     lining up a swing), so it never shows while the ball rolls (round 7). The club outline only needs occlusion.
--   * Works with CameraOcclusion's fade: faded parts (LocalTransparencyModifier 0.7) still count as blocking, so the
--     outline shows through a faded rail or tunnel too.
--   * The rays use CameraOcclusion's GolfCamera group, so walls, rails, movers, Terrain and the visible decor block;
--     balls, characters, the club and mostly see-through parts don't.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CameraOcclusion = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("CameraOcclusion"))

local player = Players.LocalPlayer

local XRay = {}

local FILL = Color3.fromHex("FFB040")
local OUTLINE = Color3.fromHex("FFF2D6")
local FILL_T = 0.72 -- subtle fill
local OUTLINE_T = 0.1
local FADE = 12 -- 1/s
local CHECK_EVERY = 1 / 20 -- s between ray checks

local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Exclude
rayParams.CollisionGroup = CameraOcclusion.CAMERA_GROUP
rayParams.IgnoreWater = true

-- Is anything opaque between `eye` and `target` (stopping `margin` short of it)?
local function blocked(eye: Vector3, target: Vector3, margin: number): boolean
	local d = target - eye
	local len = d.Magnitude - margin
	if len <= 0.05 then
		return false
	end
	local filter = { workspace.CurrentCamera, player.Character }
	local balls = workspace:FindFirstChild("Balls")
	if balls then
		table.insert(filter, balls)
	end
	for _ = 1, 8 do
		rayParams.FilterDescendantsInstances = filter
		local hit = workspace:Raycast(eye, d.Unit * len, rayParams)
		if not hit then
			return false
		end
		local p = hit.Instance
		if p:IsA("Terrain") or (p:IsA("BasePart") and p.Transparency < 0.95) then
			return true
		end
		table.insert(filter, p)
	end
	return false
end
XRay.blocked = blocked

type Target = { get: () -> BasePart?, margin: number, hl: Highlight, on: boolean, alpha: number }

local targets: { [string]: Target } = {}
local BallRef -- BallController (for the harness' state())

local function makeHighlight(name: string): Highlight
	local h = Instance.new("Highlight")
	h.Name = name
	h.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
	h.FillColor = FILL
	h.OutlineColor = OUTLINE
	h.FillTransparency = 1
	h.OutlineTransparency = 1
	h.Enabled = false
	h.Parent = workspace.CurrentCamera
	return h
end

-- eye: () -> Vector3 (the viewpoint). clubHead: the VR putter head part, or nil (phone/desktop have no club).
function XRay.start(Ball, eye: () -> Vector3, clubHead: BasePart?)
	BallRef = Ball
	targets.ball = { get = function()
		return Ball.ball
	end, margin = 0.12, hl = makeHighlight("BallXRay"), on = false, alpha = 0 }
	if clubHead then
		targets.club = { get = function()
			return clubHead
		end, margin = 0.1, hl = makeHighlight("ClubXRay"), on = false, alpha = 0 }
	end

	-- Studio hook for the harness (an MCP require() gets its own copy of this module)
	if RunService:IsStudio() then
		local hook = Instance.new("BindableFunction")
		hook.Name = "GolfXRayDebug"
		hook.OnInvoke = function()
			return XRay.state()
		end
		hook.Parent = player:WaitForChild("PlayerScripts")
	end

	local lastCheck = 0
	-- (last, after every camera writer: the golf / VR cameras and the Studio harness' screenshot cameras)
	RunService:BindToRenderStep("GolfXRay", Enum.RenderPriority.Last.Value, function(dt)
		local now = os.clock()
		local vr = clubHead ~= nil
		local check = vr or now - lastCheck >= CHECK_EVERY
		if check then
			lastCheck = now
		end
		local from = eye()
		local off = Ball.exploring and Ball.exploring()
		for _, t in targets do
			local part = t.get()
			if not part or not part.Parent or off or (t == targets.ball and not Ball.seeThrough) then
				t.on = false
			elseif check then
				t.on = blocked(from, part.Position, t.margin)
			end
			if t.hl.Adornee ~= part then
				t.hl.Adornee = part
			end
			local target = t.on and 1 or 0
			-- Rotating spokes must match this rendered frame, including disappearance.
			if vr then
				t.alpha = target
			else
				t.alpha += (target - t.alpha) * math.min(1, dt * FADE)
			end
			if math.abs(target - t.alpha) < 0.01 then
				t.alpha = target
			end
			t.hl.Enabled = t.alpha > 0
			t.hl.FillTransparency = 1 - (1 - FILL_T) * t.alpha
			t.hl.OutlineTransparency = 1 - (1 - OUTLINE_T) * t.alpha
		end
	end)
end

-- Studio harness: which targets are showing.
function XRay.state()
	local out = {}
	for k, t in targets do
		out[k] = { on = t.on, alpha = t.alpha, gate = k ~= "ball" or (BallRef and BallRef.seeThrough == true) }
	end
	return out
end

return XRay
