-- Read-only edit/play check; run after Stage am props/effects and source push.
local Math = require(game.ReplicatedStorage.Golf.MoverMath:Clone())
local course = assert(workspace:FindFirstChild("CourseAurora"))
local mover = assert(course.Hole17:FindFirstChild("Mover_aurora_span", true))
local profile = Math.fromModel(mover)
local rows = {}
for _, x in {{0,1,"fade_in",0},{0.3,0.5,"fade_in",0},{0.6,0,"solid",1},{6.599999,0,"solid",1},{6.6,0,"fade_out",0},{6.9,0.425,"fade_out",0},{7.2,1,"gone",0},{9,1,"fade_in",0},{9.6,0,"solid",1},{15.6,0,"fade_out",0}} do
	local alpha, state = Math.toggleVisual(profile, x[1])
	local solid = Math.value(profile, x[1])
	assert(math.abs(alpha-x[2]) < 1e-6 and state == x[3] and solid == x[4], "toggle boundary " .. x[1])
	table.insert(rows, {t=x[1],alpha=alpha,state=state,solid=solid})
end
local emitters = {}
for _, p in course:GetDescendants() do
	if p:IsA("ParticleEmitter") and (p.Name=="KettleSteam" or p.Name=="DimmingSparkles") then
		table.insert(emitters,{name=p.Name,path=p:GetFullName(),rate=p.Rate,speed={p.Speed.Min,p.Speed.Max},lifetime={p.Lifetime.Min,p.Lifetime.Max}})
	end
end
assert(#emitters==4, "expected kettle steam + 3 ribbon fray emitters")
local effects = {}
for _, ref in mover:GetChildren() do
	if ref:IsA("ObjectValue") then effects[ref.Name]=(effects[ref.Name] or 0)+1 end
end
assert((effects.ToggleLamp or 0)>0 and (effects.ToggleRibbon or 0)>0 and effects.ToggleSparkles==3)
return {boundaries=rows,emitters=emitters,references=effects}
