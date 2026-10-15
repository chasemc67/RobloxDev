-- PlaceTeleport (stage z): moves a player between the game's places (ReplicatedStorage.Golf.Places) with
-- TeleportService:TeleportAsync + TeleportOptions. Used by the lobby (course cards, walk-in portals) and the course
-- places (Menu > Back to Lobby, course finished, picking another course).
--   * The client is told first (Remotes.TeleportStatus "start", dest): GolfClient.TeleportScreen shows that course's
--     loading screen and hands it to TeleportService:SetTeleportGui, so it stays up while the next place loads.
--   * Studio can't teleport: the request is logged (print) and recorded (workspace attribute LastTeleportRequest +
--     PlaceTeleport.requests) for the smoke tests, then the client gets "skipped" and the loading screen goes away.
--   * A failed teleport (TeleportAsync error or TeleportInitFailed) is retried twice, then "failed" to the client.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TeleportService = game:GetService("TeleportService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Places = require(Golf:WaitForChild("Places"))
local Remotes = Golf:WaitForChild("Remotes")

local PlaceTeleport = {}
PlaceTeleport.requests = {} -- (Studio) { { player, dest, reason, placeId, t } }

local function remote(name)
	local r = Remotes:FindFirstChild(name)
	if not r then
		r = Instance.new("RemoteEvent")
		r.Name = name
		r.Parent = Remotes
	end
	return r
end
local Status = remote("TeleportStatus") -- server -> client: (state "start" | "skipped" | "failed", dest, message?)

local COOLDOWN = 4 -- seconds between requests per player (portal re-touches, double clicks)
local RETRIES = 2
local last = {} -- [player] = os.clock()
local pending = {} -- [player] = { dest, reason, tries }

local function attempt(player, dest, placeId, reason)
	local opts = Instance.new("TeleportOptions")
	opts:SetTeleportData({ from = Places.role(), dest = dest, reason = reason })
	local ok, err = pcall(function()
		return TeleportService:TeleportAsync(placeId, { player }, opts)
	end)
	return ok, err
end

local function fail(player, dest, err)
	pending[player] = nil
	warn(string.format("[PlaceTeleport] %s -> %s failed: %s", player.Name, dest, tostring(err)))
	Status:FireClient(player, "failed", dest, "Couldn't reach " .. (dest == "lobby" and "the lobby" or "the course") .. ". Try again.")
end

local function retry(player)
	local p = pending[player]
	if not p or not player.Parent then
		pending[player] = nil
		return
	end
	if p.tries > RETRIES then
		fail(player, p.dest, p.err)
		return
	end
	p.tries += 1
	task.wait(1 + p.tries)
	if pending[player] ~= p or not player.Parent then
		return
	end
	local ok, err = attempt(player, p.dest, p.placeId, p.reason)
	if not ok then
		p.err = err
		retry(player)
	end
end

-- dest: "lobby" or a course id. Returns true if a teleport was started (or recorded, in Studio).
function PlaceTeleport.send(player: Player, dest: string, reason: string?): boolean
	if typeof(player) ~= "Instance" or not player:IsA("Player") or not player.Parent then
		return false
	end
	local placeId = Places.placeIdOf(dest)
	if not placeId or dest == Places.role() then
		return false
	end
	local now = os.clock()
	if now - (last[player] or -math.huge) < COOLDOWN then
		return false
	end
	last[player] = now
	Status:FireClient(player, "start", dest)
	if RunService:IsStudio() then
		-- (TeleportService doesn't work in Studio playtests: record the request and carry on in this place)
		table.insert(PlaceTeleport.requests, { player = player.Name, dest = dest, reason = reason, placeId = placeId, t = os.clock() })
		workspace:SetAttribute("LastTeleportRequest", string.format("%s|%s|%s|%d", player.Name, dest, tostring(reason), placeId))
		print(string.format("[PlaceTeleport] Studio: skipped teleport of %s to %s (place %d, %s)", player.Name, dest, placeId, tostring(reason)))
		task.delay(1.5, function()
			if player.Parent then
				Status:FireClient(player, "skipped", dest, "Studio test: teleport to " .. dest .. " skipped")
			end
		end)
		return true
	end
	local p = { dest = dest, placeId = placeId, reason = reason, tries = 0 }
	pending[player] = p
	task.spawn(function()
		task.wait(0.4) -- (the client puts the loading screen up first)
		if pending[player] ~= p then
			return
		end
		local ok, err = attempt(player, dest, placeId, reason)
		if not ok then
			p.err = err
			retry(player)
		end
	end)
	return true
end

TeleportService.TeleportInitFailed:Connect(function(player, result, message)
	local p = pending[player]
	if not p then
		return
	end
	p.err = tostring(result) .. " " .. tostring(message)
	if result == Enum.TeleportResult.Flooded or result == Enum.TeleportResult.Failure then
		task.spawn(retry, player)
	else
		fail(player, p.dest, p.err)
	end
end)

Players.PlayerRemoving:Connect(function(player)
	last[player] = nil
	pending[player] = nil
end)

-- client -> server: Menu > Back to Lobby, a course card ("lobby" or a course id)
remote("RequestTeleport").OnServerEvent:Connect(function(player, dest)
	if type(dest) == "string" then
		PlaceTeleport.send(player, dest, "menu")
	end
end)

return PlaceTeleport
