-- LobbyServer (stage z): the lobby place's server. Does nothing in a course place (GolfServer runs those).
--   * No golf ball here: players walk around, open the menu and pick a course (course card -> RequestTeleport) or walk
--     into a portal (workspace.Lobby.Portals.Portal_<courseId>, 10x10x3 inside each arch; LobbyBuilder.BuildPortals).
--     Both go through PlaceTeleport (TeleportService to that course's place).
--   * Settings and personal bests load as on a course (PersonalBest), so the menu's settings and course cards work.
--   * Leaderboard wall (workspace.Lobby.Leaderboard, LobbyBuilder.BuildLeaderboard): top totals per course from the
--     OrderedDataStores the course places write (ServerScriptService.Leaderboard), refreshed every 60 s. A player's
--     saved personal bests are back-filled into those stores when they join.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserService = game:GetService("UserService")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Places = require(Golf:WaitForChild("Places"))
if not Places.isLobby() then
	return
end

local Config = require(Golf:WaitForChild("Config"))
local Remotes = Golf:WaitForChild("Remotes")
-- (stage ad) Our lobby VR controls load/save the same club fit as the course places.
require(script.Parent:WaitForChild("GolfServer"):WaitForChild("ClubSetup")).init(Remotes)
local PersonalBest = require(script.Parent:WaitForChild("GolfServer"):WaitForChild("PersonalBest"))
local PlaceTeleport = require(script.Parent:WaitForChild("PlaceTeleport"))
local Leaderboard = require(script.Parent:WaitForChild("Leaderboard"))

local REFRESH = 60 -- seconds between leaderboard reads
local ROWS = 8

---------------------------------------------------------------------------- players: settings + personal bests
local SaveSettings = Remotes:FindFirstChild("SaveSettings") or Instance.new("RemoteEvent")
SaveSettings.Name = "SaveSettings"
SaveSettings.Parent = Remotes
SaveSettings.OnServerEvent:Connect(function(player, settings)
	if type(settings) == "table" then
		PersonalBest.setSettings(player, settings)
	end
end)

local function backfill(player)
	for _, c in Config.Courses do
		local best = player:GetAttribute("Best_" .. c.id)
		if type(best) == "number" then
			Leaderboard.submit(player.UserId, c.id, best)
		end
	end
end

local function onPlayerAdded(player)
	PersonalBest.load(player)
	if player:GetAttribute("SettingsLoaded") then
		backfill(player)
	else
		local conn
		conn = player:GetAttributeChangedSignal("SettingsLoaded"):Connect(function()
			conn:Disconnect()
			backfill(player)
		end)
	end
end
Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in Players:GetPlayers() do
	task.spawn(onPlayerAdded, p)
end
Players.PlayerRemoving:Connect(function(player)
	PersonalBest.unload(player)
end)
game:BindToClose(function()
	PersonalBest.flushAll()
end)

---------------------------------------------------------------------------- portals
local lobby = workspace:WaitForChild("Lobby")
local portals = lobby:FindFirstChild("Portals")
if portals then
	for _, portal in portals:GetChildren() do
		local courseId = portal:GetAttribute("CourseId")
		if portal:IsA("BasePart") and courseId then
			portal.Touched:Connect(function(hit)
				local char = hit:FindFirstAncestorOfClass("Model")
				local player = char and Players:GetPlayerFromCharacter(char)
				if player and hit.Name == "HumanoidRootPart" then
					PlaceTeleport.send(player, courseId, "portal")
				end
			end)
		end
	end
else
	warn("[LobbyServer] workspace.Lobby.Portals is missing (LobbyBuilder.BuildPortals)")
end

---------------------------------------------------------------------------- leaderboard wall
local names = {} -- [userId] = display name
local function resolveNames(ids)
	local missing = {}
	for _, id in ids do
		if not names[id] and id > 0 then
			table.insert(missing, id)
		end
	end
	if #missing > 0 then
		local ok, infos = pcall(function()
			return UserService:GetUserInfosByUserIdsAsync(missing)
		end)
		if ok then
			for _, info in infos do
				names[info.Id] = info.DisplayName ~= "" and info.DisplayName or info.Username
			end
		end
		for _, id in missing do
			if not names[id] then
				local ok2, n = pcall(function()
					return Players:GetNameFromUserIdAsync(id)
				end)
				names[id] = ok2 and n or nil
			end
		end
	end
end

local board = lobby:FindFirstChild("Leaderboard")
local function refreshBoard()
	local gui = board and board:FindFirstChild("Board")
	if not gui then
		return
	end
	local status = {}
	for _, c in Config.Courses do
		local col = gui:FindFirstChild("Col_" .. c.id, true)
		if col then
			local list, err = Leaderboard.top(c.id, ROWS)
			if list then
				local ids = {}
				for _, e in list do
					table.insert(ids, e.userId)
				end
				resolveNames(ids)
			end
			for i = 1, ROWS do
				local row = col:FindFirstChild("Row" .. i)
				if row then
					local e = list and list[i]
					row.Rank.Text = e and (i .. ".") or ""
					row.Player.Text = e and (e.name or names[e.userId] or ("Player " .. e.userId)) or ""
					row.Total.Text = e and tostring(e.total) or ""
				end
			end
			local note = col:FindFirstChild("Note")
			if note then
				note.Text = (not list and "Scores unavailable right now") or (#list == 0 and "No rounds yet - be the first!") or ""
			end
			status[c.id] = list and #list or ("error: " .. tostring(err))
		end
	end
	board:SetAttribute("LastRefresh", os.time())
	board:SetAttribute("RefreshStatus", game:GetService("HttpService"):JSONEncode(status))
end

if board then
	task.spawn(function()
		while board.Parent do
			local ok, err = pcall(refreshBoard)
			if not ok then
				warn("[LobbyServer] leaderboard refresh: " .. tostring(err))
			end
			task.wait(REFRESH)
		end
	end)
	-- (Studio smoke tests: refresh now instead of waiting for the next 60 s tick)
	if game:GetService("RunService"):IsStudio() then
		local hook = Instance.new("BindableFunction")
		hook.Name = "LeaderboardRefresh"
		hook.OnInvoke = function()
			refreshBoard()
			return board:GetAttribute("RefreshStatus")
		end
		hook.Parent = script
	end
else
	warn("[LobbyServer] workspace.Lobby.Leaderboard is missing (LobbyBuilder.BuildLeaderboard)")
end
