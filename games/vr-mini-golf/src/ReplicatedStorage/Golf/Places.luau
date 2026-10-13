-- Places (stage z): the game is one universe with three places, all running the same scripts (copied from src/, see
-- games/vr-mini-golf/places.json "sync"):
--   * Lobby (the start place): walk around, pick a course on the menu or walk through an arch; no golf ball.
--   * Lantern Grove / Sugarloaf Canyon: one course each. Hole 1 starts on arrival; finishing the course or
--     Menu > Back to Lobby teleports back to the lobby.
-- What a place is comes from the workspace attribute PlaceRole ("lobby" | a Config.Courses id), saved in each place
-- file; game.PlaceId is the fallback (a local .rbxl copy has PlaceId 0, so the attribute is the one that counts).
local Places = {}

Places.UNIVERSE = 10769274294
Places.LOBBY = 87725688219952
-- course id -> place id (games/vr-mini-golf/places.json)
Places.COURSES = {
	lantern_grove = 91438142503824,
	sugarloaf_canyon = 124440050576723,
	aurora_archipelago = 0, -- local blockout only; no cloud place
}

function Places.role(): string
	local r = workspace:GetAttribute("PlaceRole")
	if type(r) == "string" and r ~= "" then
		return r
	end
	for id, placeId in Places.COURSES do
		if placeId ~= 0 and game.PlaceId == placeId then
			return id
		end
	end
	return "lobby"
end

function Places.isLobby(): boolean
	return Places.role() == "lobby"
end

-- The course this place hosts, or nil in the lobby.
function Places.course(): string?
	local r = Places.role()
	if r ~= "lobby" and Places.COURSES[r] ~= nil then
		return r
	end
	return nil
end

-- "lobby" or a course id -> place id (nil if unknown)
function Places.placeIdOf(dest: string): number?
	if dest == "lobby" then
		return Places.LOBBY
	end
	local id = Places.COURSES[dest]
	return id ~= 0 and id or nil
end

return Places
