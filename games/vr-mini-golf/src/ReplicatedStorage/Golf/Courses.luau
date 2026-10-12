-- Courses (stage w): more than one course in the place. Each course is built into its own workspace folder by
-- ServerStorage.CourseBuilder (Lantern Grove: workspace.Course; Sugarloaf Canyon: workspace.CourseSugarloaf, 5000
-- studs north). A player plays one course at a time: the server keeps it in the player attribute "Course" (a
-- Config.Courses id) and SelectCourse switches it (GolfServer).
local Config = require(script.Parent:WaitForChild("Config"))

local Courses = {}

Courses.FOLDERS = {
	lantern_grove = "Course",
	sugarloaf_canyon = "CourseSugarloaf",
}
Courses.DEFAULT = Config.CurrentCourse -- "lantern_grove"

function Courses.folderName(id: string?): string
	return Courses.FOLDERS[id or Courses.DEFAULT] or "Course"
end

function Courses.folder(id: string?): Instance?
	return workspace:FindFirstChild(Courses.folderName(id))
end

-- Hole models of a course by number ({ [1] = Hole1, ... }).
function Courses.holes(id: string?)
	local list = {}
	local course = Courses.folder(id)
	for _, h in course and course:GetChildren() or {} do
		local n = h:GetAttribute("HoleNumber")
		if n then
			list[n] = h
		end
	end
	return list
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

-- Playable = marked playable in Config and built in this place.
function Courses.playable(id: string?): boolean
	local c = Courses.info(id)
	return c ~= nil and c.playable == true and Courses.FOLDERS[id] ~= nil and Courses.folder(id) ~= nil
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
