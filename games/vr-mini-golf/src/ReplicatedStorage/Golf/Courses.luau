-- Courses (stage w): more than one course in the place. Each course is built into its own workspace folder by
-- ServerStorage.CourseBuilder (Lantern Grove: workspace.Course; Sugarloaf Canyon: workspace.CourseSugarloaf, 5000
-- studs north). A player plays one course at a time: the server keeps it in the player attribute "Course" (a
-- Config.Courses id) and SelectCourse switches it (GolfServer).
-- Stage z: each course is its own place (Golf.Places); a course place builds only its own folder, the lobby none.
local Config = require(script.Parent:WaitForChild("Config"))
local Places = require(script.Parent:WaitForChild("Places"))

local Courses = {}

Courses.FOLDERS = {
	lantern_grove = "Course",
	sugarloaf_canyon = "CourseSugarloaf",
	aurora_archipelago = "CourseAurora",
}
Courses.DEFAULT = Places.course() or Config.CurrentCourse -- this place's course ("lantern_grove" in the lobby)

function Courses.folderName(id: string?): string
	return Courses.FOLDERS[id or Courses.DEFAULT] or "Course"
end

function Courses.folder(id: string?): Instance?
	return workspace:FindFirstChild(Courses.folderName(id))
end

-- Hole models of a course by number ({ [1] = Hole1, ... }). Stage gg2: bonus holes (attribute Bonus, e.g. Lantern
-- Grove's hidden "Hole 19") are not part of the round, so they are left out: the list stays 1..N and # works.
function Courses.holes(id: string?)
	local list = {}
	local course = Courses.folder(id)
	for _, h in course and course:GetChildren() or {} do
		local n = h:GetAttribute("HoleNumber")
		if n and not h:GetAttribute("Bonus") then
			list[n] = h
		end
	end
	return list
end

-- Stage gg2: the course's hidden bonus hole model (attribute Bonus), or nil.
function Courses.bonusHole(id: string?)
	local course = Courses.folder(id)
	for _, h in course and course:GetChildren() or {} do
		if h:GetAttribute("HoleNumber") and h:GetAttribute("Bonus") then
			return h
		end
	end
	return nil
end

-- The course a player is on (player attribute "Course", set by the server).
function Courses.of(player): string
	return player and player:GetAttribute("Course") or Courses.DEFAULT
end

function Courses.info(id: string?)
	for _, c in Config.Courses do
		if c.id == id then
			return c
		end
	end
	return nil
end

-- Built in this place (stage z: only a course's own place has its folder).
function Courses.here(id: string?): boolean
	return Courses.FOLDERS[id] ~= nil and Courses.folder(id) ~= nil
end

-- Playable = marked playable in Config and built here or reachable by teleport (it has a place).
function Courses.playable(id: string?): boolean
	local c = Courses.info(id)
	return c ~= nil and c.playable == true and (Courses.here(id) or Places.placeIdOf(id) ~= nil)
end

-- The course whose folder holds `inst`, or nil.
function Courses.courseOf(inst: Instance?): string?
	for id, name in Courses.FOLDERS do
		local f = workspace:FindFirstChild(name)
		if f and inst and inst:IsDescendantOf(f) then
			return id
		end
	end
	return nil
end

return Courses
