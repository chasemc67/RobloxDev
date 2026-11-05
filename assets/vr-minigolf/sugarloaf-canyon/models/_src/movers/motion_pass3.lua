-- SRV-132 pass 3. Elapsed seconds; hole-local Roblox studs.
local M = {}
function M.sluice(t)
 local q=t%(3.2+14/3)
 if q<1.2 then return 0 elseif q<1.2+7/3 then return -3*(q-1.2)
 elseif q<3.2+7/3 then return -7 else return -7+3*(q-3.2-7/3) end
end
function M.lockGate(t)
 local q=t%10.6
 if q<4.85 then return -1.3 elseif q<5.5 then return -1.3+2*(q-4.85)
 elseif q<9.95 then return 0 else return -2*(q-9.95) end
end
function M.lockLift(t)
 local q=t%10.6
 if q<5.5 then return 0,0 elseif q<7.5 then return 2*(q-5.5),0
 elseif q<7.65 then return 4,4*(q-7.5)/0.15
 elseif q<9.15 then return 4*(1-(q-7.65)/1.5),4*math.max(0,1-(q-7.65)/0.15)
 else return 0,0 end
end
function M.liftCFrame(pivot,t)
 local height,tilt=M.lockLift(t)
 return pivot*CFrame.new(0,height,0)*CFrame.Angles(-math.rad(tilt),0,0)
end
function M.releaseSpeed(entrySpeed) return math.clamp(entrySpeed*0.5,1.5,7) end
-- North hinge/export pivot [0,0,-25]. Release interval [7.5,7.65), toward -Z.
-- Return ends 9.15; gate starts lowering 9.95, fully down 10.6.
-- Lip export pivot [0,3.5,-25.45], 0.75 below spec centre pivot.
-- Speed 10: sink 7.4-7.5, top y=4 during [7.5,7.65), rise 7.65-7.75.
function M.quayLip(t)
 local q=t%10.6
 if q<7.4 then return 0 elseif q<7.5 then return -10*(q-7.4)
 elseif q<7.65 then return -1 elseif q<7.75 then return -1+10*(q-7.65)
 else return 0 end
end
function M.quayLipCFrame(pivot,t)
 return pivot*CFrame.new(0,M.quayLip(t),0)
end
return M
