-- SRV-132 pass 4. Elapsed seconds; hole-local Roblox studs / degrees. Source: in/holes.json (p8).
-- `pivot` arguments are the WORLD CFrame of the hole-local export pivot (hole world_yaw included),
-- so the axes below are hole-local axes.
local M = {}
function M.sluice(t)
 local q=t%(3.2+14/3)
 if q<1.2 then return 0 elseif q<1.2+7/3 then return -3*(q-1.2)
 elseif q<3.2+7/3 then return -7 else return -7+3*(q-3.2-7/3) end
end
-- H11 Floodgate Lock, p8 retune: 10.7 s cycle (Game Art Bot 8:25 PM PT, overrides pass-3 10.6 s timing).
M.LOCK_CYCLE=10.7
-- Gate offset (studs, +Y): open/down -1.3 for 0-5.5, rises 5.5-5.8, closed 0 for 5.8-10.4, lowers 10.4-10.7.
function M.lockGate(t)
 local q=t%M.LOCK_CYCLE
 local v=1.3/0.3
 if q<5.5 then return -1.3 elseif q<5.8 then return -1.3+v*(q-5.5)
 elseif q<10.4 then return 0 else return -v*(q-10.4) end
end
-- Deck (studs, +Y), hinge/export pivot [0,0,-25]: bottom until 6.1, rises 4 at 4 studs/s 6.1-7.1,
-- level at top 7.1-9.1 (release window), down 9.1-10.1. Deck stays level: tilt is always 0.
function M.lockLift(t)
 local q=t%M.LOCK_CYCLE
 if q<6.1 then return 0,0 elseif q<7.1 then return 4*(q-6.1),0
 elseif q<9.1 then return 4,0 elseif q<10.1 then return 4-4*(q-9.1),0
 else return 0,0 end
end
function M.liftCFrame(pivot,t)
 local height,tilt=M.lockLift(t)
 return pivot*CFrame.new(0,height,0)*CFrame.Angles(-math.rad(tilt),0,0)
end
-- Release onto the quay at [0,4,-27] toward -Z during 7.1-9.1.
function M.releaseSpeed(entrySpeed) return math.clamp(entrySpeed*0.5,1.5,7) end
-- Quay lip offset (studs, +Y). Export pivot [0,3.5,-25.45] (bottom centre, .75 below the holes.json centre pivot).
-- Raised top y=5 otherwise; speed 10: sinks 6.9-7.0, FLUSH (top y=4) 7.0-9.2, rises 9.2-9.3.
function M.quayLip(t)
 local q=t%M.LOCK_CYCLE
 if q<6.9 then return 0 elseif q<7.0 then return -10*(q-6.9)
 elseif q<9.2 then return -1 elseif q<9.3 then return -1+10*(q-9.2)
 else return 0 end
end
function M.quayLipCFrame(pivot,t)
 return pivot*CFrame.new(0,M.quayLip(t),0)
end
-- H9 windpump vanes: 20 deg/s about hole-local +Z through [0,4.12,-17.75], phase 0 (18 s turn).
function M.windpump(t) return (20*t)%360 end
function M.windpumpCFrame(pivot,t)
 return pivot*CFrame.fromAxisAngle(Vector3.new(0,0,1),math.rad(M.windpump(t)))
end
-- H14 ore bucket: angle = 9*sin(2*pi*t/4) deg about hole-local +Z through the hinge [0,10.35,-24].
function M.oreBucket(t) return 9*math.sin(2*math.pi*t/4) end
function M.oreBucketCFrame(pivot,t)
 return pivot*CFrame.fromAxisAngle(Vector3.new(0,0,1),math.rad(M.oreBucket(t)))
end
-- H17 shadow arms: 12 deg/s about hole-local +Y through [0,0,-36], phase 0 (30 s turn).
function M.shadowArm(t) return (12*t)%360 end
function M.shadowArmCFrame(pivot,t)
 return pivot*CFrame.fromAxisAngle(Vector3.new(0,1,0),math.rad(M.shadowArm(t)))
end
return M
