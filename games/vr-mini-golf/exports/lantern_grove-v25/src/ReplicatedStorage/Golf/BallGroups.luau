-- BallGroups: course modes (Chase's design, SRV-139). Every player plays at their own pace; the mode only decides
-- whether golf balls touch each other.
--   * Peaceful (default): the ball stays in GolfBall, which never collides with itself, so balls pass through.
--   * PVP: the ball moves to GolfBallPVP, which collides with other PVP balls (and with everything GolfBall
--     collides with), but never with Peaceful balls, so a PVP player can't knock a Peaceful player's ball.
local PhysicsService = game:GetService("PhysicsService")

local BallGroups = {}

BallGroups.PEACEFUL = "GolfBall"
BallGroups.PVP = "GolfBallPVP"
BallGroups.MODES = { "Peaceful", "PVP" }

function BallGroups.groupFor(mode)
	return mode == "PVP" and BallGroups.PVP or BallGroups.PEACEFUL
end

-- Server: register GolfBallPVP as a copy of GolfBall's row in the collision matrix (idempotent). Call it before
-- anything else that walks the registered groups (CameraOcclusion.setupGroups, the Explore walls).
function BallGroups.setup()
	local base, pvp = BallGroups.PEACEFUL, BallGroups.PVP
	for _, g in { base, pvp } do
		if not PhysicsService:IsCollisionGroupRegistered(g) then
			PhysicsService:RegisterCollisionGroup(g)
		end
	end
	for _, g in PhysicsService:GetRegisteredCollisionGroups() do
		if g.name ~= base and g.name ~= pvp then
			PhysicsService:CollisionGroupSetCollidable(pvp, g.name, PhysicsService:CollisionGroupsAreCollidable(base, g.name))
		end
	end
	PhysicsService:CollisionGroupSetCollidable(base, base, false)
	PhysicsService:CollisionGroupSetCollidable(pvp, pvp, true)
	PhysicsService:CollisionGroupSetCollidable(base, pvp, false)
end

return BallGroups
