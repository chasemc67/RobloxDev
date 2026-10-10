-- GolfTestServer: server half of the Studio playtest harness. Only required by GolfServer when
-- RunService:IsStudio() and workspace.GolfTestMode == true. The client half (GolfClient.GolfTest) runs the
-- scenarios, because the ball is simulated by its owner's client; this module only places the ball
-- deterministically and keeps the round logic (strokes, transitions) out of the way.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))

local GolfTestServer = {}

-- A long, flat, wall-less felt strip off to the side of the course for rollout tests. The felt is a clone
-- of hole 1's felt so it has the same material, physical properties and tags.
local LANE_X, LANE_Z0, LANE_Z1, LANE_W, SURFACE_Y = -40, -10, 80, 10, 1

local function buildLane()
	local old = workspace:FindFirstChild("GolfTestLane")
	if old then
		old:Destroy()
	end
	local lane = Instance.new("Model")
	lane.Name = "GolfTestLane"
	lane:SetAttribute("HoleNumber", 0)
	lane:SetAttribute("HoleName", "Test Lane")
	lane:SetAttribute("Par", 0)
	lane:SetAttribute("KillY", SURFACE_Y - 0.5)
	local geo = Instance.new("Folder")
	geo.Name = "Geometry"
	geo.Parent = lane

	local source = workspace.Course.Hole1.Geometry:FindFirstChild("Felt")
	local felt = source:Clone()
	felt.Size = Vector3.new(LANE_W, 1, LANE_Z1 - LANE_Z0)
	felt.CFrame = CFrame.new(LANE_X, SURFACE_Y - 0.5, (LANE_Z0 + LANE_Z1) / 2)
	felt.Parent = geo

	local function marker(name, cf, size)
		local p = Instance.new("Part")
		p.Name = name
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Transparency = 1
		p.Size = size or Vector3.new(0.2, 0.2, 0.2)
		p.CFrame = cf
		p.Parent = lane
		return p
	end
	-- the cup is far past the end of the lane, so nothing ever sinks here
	marker("Cup", CFrame.new(LANE_X, SURFACE_Y, LANE_Z1 + 500)):SetAttribute("Radius", 0.21)
	marker("AimTarget", CFrame.new(LANE_X, SURFACE_Y, LANE_Z1))
	marker("Tee", CFrame.new(LANE_X, SURFACE_Y + 0.011, LANE_Z0 + 2))
	marker("Bounds", CFrame.new(LANE_X, SURFACE_Y + 10, (LANE_Z0 + LANE_Z1) / 2), Vector3.new(LANE_W + 4, 30, LANE_Z1 - LANE_Z0 + 6))
	lane.Parent = workspace
	return lane
end

function GolfTestServer.init(ctx)
	local lane = buildLane()

	local remote = Instance.new("RemoteFunction")
	remote.Name = "GolfTestRemote"
	remote.Parent = Golf

	remote.OnServerInvoke = function(player, cmd, args)
		local st = ctx.states[player]
		if not st then
			return false, "no state"
		end
		if cmd == "place" then
			-- args: { hole = 0 (test lane) | 1..9, pos = Vector3 }
			if args.hole == 0 then
				st.testHole = lane
			else
				st.testHole = nil
				st.hole = math.clamp(args.hole, 1, #ctx.holes)
			end
			st.started = true
			st.sunk = false
			st.finished = false
			st.resetting = false
			st.transitionToken = {} -- cancels any pending "next hole" after a test sink
			st.strokes[st.hole] = 0
			ctx.publish(player, st)
			ctx.placeBall(player, st, args.pos, "test")
			return true
		elseif cmd == "ballRadius" then
			return Config.BallRadius
		elseif cmd == "spec" then
			-- the hole's spec (tee, cup, cup_from, waypoints, HIO line, movers, teleports) for the client scenarios
			local data = require(game:GetService("ServerStorage").CourseData.LanternGrove)
			local h = data.holes[args.hole]
			if not h then
				return false, "no hole " .. tostring(args.hole)
			end
			return game:GetService("HttpService"):JSONEncode({
				number = h.number,
				name = h.name,
				par = h.par,
				tee = h.tee,
				cup = h.cup,
				cup_from = h.cup_from,
				ai_waypoints = h.ai_waypoints,
				hio = h.hio,
				moving_parts = h.moving_parts,
				teleports = h.teleports,
				hazards = h.hazards,
				felt = h.felt,
				walls = h.walls,
				max_putt = data.physics.max_putt_speed_studs_s,
			})
		elseif cmd == "movers" then
			-- every mover's constraint value vs the spec at server time, and each blocker's world position vs the
			-- spec formula (pivot + Rot(axis, angle) * centre / pivot + centre + axis * offset), studs
			local t = workspace:GetServerTimeNow()
			local out = {}
			for model, s in ctx.movers.active do
				local cur, err, rate = ctx.movers.state(model, t)
				local want = ctx.movers.value(model, t)
				local pivot = model:GetAttribute("PivotWorld")
				local axis = model:GetAttribute("AxisWorld")
				local base = model:FindFirstChild("MoverBase")
				local maxPosErr = 0
				for _, blk in model:GetChildren() do
					if blk.Name == "Blocker" then
						local rest = blk:GetAttribute("RestCFrame")
						if rest then
							local expect
							if s.rotate then
								expect = (CFrame.new(pivot) * CFrame.fromAxisAngle(axis, math.rad(want)) * CFrame.new(-pivot) * rest).Position
							else
								expect = rest.Position + axis * want
							end
							maxPosErr = math.max(maxPosErr, (blk.Position - expect).Magnitude)
						end
					end
				end
				table.insert(out, {
					id = model:GetAttribute("MoverId"),
					hole = model.Parent and model.Parent.Parent and model.Parent.Parent.Name,
					type = model:GetAttribute("Type"),
					value = cur,
					want = want,
					err = err,
					rate = rate,
					blockerPosErr = maxPosErr,
					networkOwnerServer = s.root:GetNetworkOwner() == nil,
					anchored = s.root.Anchored,
					baseOk = base ~= nil,
				})
			end
			return game:GetService("HttpService"):JSONEncode({ t = t, movers = out })
		end
		return false, "unknown command " .. tostring(cmd)
	end

	print("GOLFTEST|server|ready")
end

return GolfTestServer
