-- VR-only guided grip fitting. The thumbstick moves a world-space ground target;
-- the current controller pose and target solve a hand-space shaft rotation.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Setup = {}
function Setup.new(api, Config, HUD)
	local self = { active = false, saving = false, stick = Vector2.zero, fits = {}, target = nil }
	local remote = ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Remotes"):WaitForChild("ClubSetup")
	local art = Config.UI.ClubSetup or {}
	local marker, card, cardGui
	local function hide()
		if cardGui then cardGui:Destroy(); cardGui = nil end
		if marker then marker:Destroy(); marker = nil end
		if card then card:Destroy(); card = nil end
	end
	local function part(name, size)
		local p = Instance.new("Part")
		p.Name, p.Size = name, size
		p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.CastShadow = true, false, false, false, false
		p.Parent = workspace.CurrentCamera
		return p
	end
	local function visuals()
		hide()
		marker = part("ClubSetupGroundMarker", Vector3.new(0.6, 0.015, 0.6))
		marker.Material, marker.Color = Enum.Material.Neon, Color3.fromRGB(250,196,70)
		marker.Transparency = art.ground_marker and 1 or 0.35
		if art.ground_marker then
			local decal = Instance.new("Decal"); decal.Face = Enum.NormalId.Top; decal.Texture = art.ground_marker; decal.Parent = marker
		end
		card = part("ClubSetupCard", Vector3.new(3.2, 2.45, 0.01)); card.Transparency = 1
		local gui = Instance.new("SurfaceGui")
		gui.Name, gui.Face, gui.CanvasSize = "ClubSetupExplainer", Enum.NormalId.Front, Vector2.new(1024,784)
		-- Match the working VR wrist/menu rendering path: PlayerGui + explicit Adornee,
		-- depth-rendered. Parenting an overlay SurfaceGui in CurrentCamera was unreliable.
		gui.Adornee, gui.AlwaysOnTop, gui.LightInfluence = card, false, 0
		gui.ResetOnSpawn, gui.SizingMode = false, Enum.SurfaceGuiSizingMode.FixedSize
		gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
		cardGui = gui
		local bg = Instance.new("ImageLabel")
		bg.Name = "InstructionsBackground"
		bg.Size, bg.BackgroundColor3 = UDim2.fromScale(1,1), Color3.fromRGB(250,232,198)
		bg.Image, bg.ScaleType, bg.Parent = art.howto_card_bg or "", Enum.ScaleType.Fit, gui
		local words = { "STAND LIKE YOU'RE\nPUTTING", "NUDGE THE HEAD\nWITH EITHER STICK", "PULL CLUB TRIGGER\nTO SAVE" }
		for i, key in { "step1_stance", "step2_stick", "step3_trigger" } do
			local icon = Instance.new("ImageLabel")
			icon.Size, icon.Position = UDim2.fromOffset(140,140), UDim2.fromOffset(112,100+(i-1)*222)
			icon.BackgroundTransparency, icon.Image, icon.Parent = 1, art[key] or "", bg
			icon.Name = key
			local text = Instance.new("TextLabel")
			text.Name = "Step" .. i
			text.BackgroundTransparency = 1
			text.Position, text.Size = UDim2.fromOffset(284,80+(i-1)*222), UDim2.fromOffset(655,175)
			text.Font, text.TextSize, text.TextScaled = Enum.Font.FredokaOne, 56, false
			text.TextColor3, text.Text, text.Parent = Color3.fromRGB(59,36,18), words[i], bg
		end
		local hint = Instance.new("TextLabel")
		hint.Size, hint.Position = UDim2.fromOffset(820,48), UDim2.fromOffset(100,725)
		hint.BackgroundTransparency, hint.TextColor3 = 1, Color3.fromRGB(59,36,18)
		hint.Font, hint.TextSize, hint.Text = Enum.Font.FredokaOne, 36, "B / Y: reset default     Menu: cancel"
		hint.Parent = bg
		local eye = api.eye()
		-- Keep the entire card in the upper central view at entry, even when looking down.
		-- The old 2.3-stud side offset put its centre ~30 degrees off-axis and could
		-- push the whole explainer beyond the headset/sim viewport.
		local pos = eye.Position + eye.LookVector * 4 + eye.UpVector * 0.9 + eye.RightVector * 0.2
		card.CFrame = CFrame.lookAt(pos, eye.Position)
	end
	function self:applySaved()
		local fit = self.fits[api.hand()]
		if fit then api.apply(CFrame.fromOrientation(unpack(fit.angles)), fit.length) else api.defaults() end
	end
	function self:cancel()
		self.active, self.stick = false, Vector2.zero
		api.active(false)
		hide()
		self:applySaved()
	end
	function self:begin()
		if self.saving then return end
		self.active, self.stick = true, Vector2.zero
		api.active(true)
		local pos = api.headPosition()
		local hand = api.pose()
		if Vector3.new(pos.X-hand.X,0,pos.Z-hand.Z).Magnitude > 2 then
			local eye = api.eye(); pos = hand.Position + Vector3.new(eye.LookVector.X,0,eye.LookVector.Z) * 0.6
		end
		self.target = Vector3.new(pos.X, api.ground(pos) + 0.065, pos.Z)
		visuals()
	end
	function self:solve()
		local hand = api.pose()
		local butt = hand:PointToWorldSpace(api.butt())
		local delta = self.target - butt
		if delta.Magnitude < 1.2 or delta.Magnitude > 4 then return nil end
		local back = -delta.Unit
		local face = hand:VectorToWorldSpace(api.rotation().RightVector)
		local right = face - back * face:Dot(back)
		if right.Magnitude < 0.05 then right = Vector3.xAxis - back * back.X end
		if right.Magnitude < 0.05 then right = Vector3.zAxis - back * back.Z end
		right = right.Unit
		local rot = hand.Rotation:Inverse() * CFrame.fromMatrix(Vector3.zero,right,back:Cross(right),back)
		local x,y,z = rot:ToOrientation()
		return { angles = {x,y,z}, length = delta.Magnitude }, rot
	end
	function self:update(dt)
		if not self.active then return end
		local eye = api.eye()
		local forward = Vector3.new(eye.LookVector.X,0,eye.LookVector.Z)
		forward = forward.Magnitude > 0.01 and forward.Unit or Vector3.new(0,0,-1)
		if self.stick.Magnitude > 0.15 then
			local move = (forward*self.stick.Y + forward:Cross(Vector3.yAxis)*self.stick.X) * math.min(dt,0.05)*0.55
			local proposed = self.target + move
			local h = api.pose().Position
			if Vector3.new(proposed.X-h.X,0,proposed.Z-h.Z).Magnitude <= 2.5 then self.target = proposed end
		end
		self.target = Vector3.new(self.target.X,api.ground(self.target)+0.065,self.target.Z)
		marker.CFrame = CFrame.new(self.target-Vector3.new(0,0.05,0))
		local fit, rotation = self:solve()
		if fit then api.apply(rotation,fit.length) end
	end
	function self:save(reset)
		if self.saving then return end
		local fit = not reset and self:solve() or nil
		if not reset and not fit then HUD.message("Move the marker closer to your feet", Color3.fromRGB(255,200,120),3); return end
		self.saving = true
		local hand = api.hand()
		task.spawn(function()
			local ok, result = pcall(function() return remote:InvokeServer(reset and "reset" or "save",hand,fit) end)
			self.saving = false
			if ok and result.ok then
				self.fits[hand] = fit
				self:cancel()
				HUD.message(reset and "Default club fit restored" or (result.sessionOnly and "Club fit saved for this Studio session" or "Club fit saved"), Color3.fromRGB(255,230,170),3)
			else
				HUD.message(ok and result.message or "Save failed; try again",Color3.fromRGB(255,200,120),4)
			end
		end)
	end
	task.spawn(function()
		local ok,result = pcall(function() return remote:InvokeServer("load") end)
		if ok and result.ok then self.fits = result.fits or {}; if not self.active then self:applySaved() end end
	end)
	return self
end
return Setup
