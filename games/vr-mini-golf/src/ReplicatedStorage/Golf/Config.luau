-- Shared tuning values for the mini golf game.
-- Scale: 1 stud = 0.3 m (VR HeadScale 1), so everything below is life size.
return {
	BallRadius = 0.08, -- 4.8 cm ball (a real golf ball is 4.3 cm)
	CupDepth = 0.35, -- 10.5 cm deep cup (radius lives on each hole's Cup part)

	-- Ball rolling (applied on the owning client on top of Roblox physics). Tuned to the Walkabout Mini Golf
	-- footage in games/vr-mini-golf/walkabout-reference.md: deceleration = RollDecel + RollDrag * speed
	-- (0.15 m/s^2 + 0.25/s * v), i.e. very fast felt with a soft stop. workspace.Gravity is 32.7 (9.81 m/s^2).
	RollDecel = 0.5, -- studs/s^2 constant rolling resistance (0.15 m/s^2)
	RollDrag = 0.25, -- 1/s speed-proportional term
	-- Roblox's own contact already slows a rolling ball by about this much (studs/s^2, measured with the
	-- rollout scenario), so the script applies RollDecel minus this.
	EngineRollLoss = 0.2,
	StopSpeed = 0.2, -- below this speed (and on a gentle slope) the ball is considered stopped
	RestTime = 0.5, -- seconds below StopSpeed before the ball is "at rest"
	MaxBallSpeed = 42,
	MaxRollTime = 25, -- safety: force the ball to rest after this many seconds
	-- Cup capture: a ball over the cup slower than this (studs/s) drops in instead of skimming across.
	-- 1.6 m/s is about the fastest a centred putt can be and still drop in real golf.
	CupCaptureSpeed = 1.6 / 0.3,

	-- Walls, bumpers and obstacles (CourseBuilder sets these as CustomPhysicalProperties; their weights beat
	-- the ball's, so these values decide every bounce). Measured result: see games/vr-mini-golf/status.md.
	WallElasticity = 0.63, -- measures ~0.6 normal restitution (Walkabout: 0.55-0.65)
	WallFriction = 0.05, -- low: the ball keeps its spin through the hit...
	BumperElasticity = 0.65, -- the round red posts
	-- ...then skids: after an obstacle hit the ball's spin still matches SpinKeep of its old rolling velocity,
	-- and sliding friction (SlideFriction * gravity) brakes the slip until it rolls again (Walkabout's
	-- "loses traction, then kicks slightly in the direction of its old spin").
	SpinKeep = 0.5,
	SlideFriction = 0.3,

	-- Touch / mouse controls
	TouchMaxSpeed = 26, -- ball speed at 100% power
	TouchPowerCurve = 1.3,

	-- VR putter
	VRHitMultiplier = 1.7, -- ball speed = putter face speed * this (a light ball off a heavy putter)
	VRTangentialTransfer = 0.1,
	VRMinHitSpeed = 0.3, -- studs/s; slower contacts are ignored
	VRMoveSpeed = 6.5, -- thumbstick walk speed, studs/s (~2 m/s)
	VRSnapTurnDegrees = 30,
	VRStanceDistance = 1.5, -- warp-to-ball puts your head this far from the ball (45 cm)
	-- Club mount: the shaft runs PARALLEL to the controller handle and comes out of its bottom end, as if the
	-- controller were the top of a putter grip. Hand UserCFrame axes on Quest Touch (aim pose): -Z = aim/laser ray,
	-- +Y = top of the controller (face buttons), +X = controller right. The handle runs down from the top along -Y,
	-- raked back toward +Z (the bottom of the grip sits down and back toward your wrist, like a pistol grip).
	-- Shaft direction in hand space = CFrame.Angles(rad(-90 - VRClubGripPitch), 0, 0) * yaw * roll applied to -Z,
	-- i.e. -Y tilted VRClubGripPitch degrees toward +Z. Starts VRClubButtOffset studs along that axis from the hand
	-- origin (the bottom of the handle). Pitch is about hand X, so it is the same for both hands; yaw/roll are
	-- mirrored for the left hand. Unverified on a real Quest: see games/vr-mini-golf/playtesting.md.
	VRClubGripPitch = 35, -- degrees, + rakes the handle bottom back toward the wrist (+Z)
	VRClubGripYaw = 0, -- degrees, + swings the shaft toward the controller's right (+X); mirrored for the left hand
	VRClubGripRoll = 0, -- degrees about the shaft (turns the putter face); mirrored for the left hand
	VRClubButtOffset = 0.25, -- 7.5 cm from the hand origin to the bottom of the handle
	-- Legacy mount (v9, before 2026-10-09): the shaft came out of the controller TIP along the aim ray (LookVector),
	-- which ends up ~perpendicular to the handle on a real Quest. Kept only for before/after comparisons.
	VRClubLegacyAim = false,
	VRClubAngle = 0, -- legacy only: degrees of pitch from the aim ray (+ toward the controller's top)
	VRClubTipOffset = 0.2, -- legacy only: 6 cm in front of the hand origin
	VRPlaneRange = 12, -- within this many studs of the ball, the putter head and your floor use the ball's plane
	-- (felt parts tagged GolfSurface); further away they follow the GolfSurface under them. Walls never count.
	VRGripToPutt = false, -- Walkabout's optional mode: putter is only solid while you hold grip

	-- Rules
	MaxStrokes = 8,
	PenaltyStrokes = 1,
	HoleTransitionTime = 3.5,
}
