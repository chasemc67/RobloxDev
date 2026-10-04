-- Shared tuning values for the mini golf game.
-- Scale: 1 stud = 0.3 m (VR HeadScale 1), so everything below is life size.
return {
	BallRadius = 0.08, -- 4.8 cm ball (a real golf ball is 4.3 cm)
	CupDepth = 0.35, -- 10.5 cm deep cup (radius lives on each hole's Cup part)

	-- Ball rolling (applied on the owning client on top of Roblox physics)
	RollDecel = 3.6, -- studs/s^2 of rolling resistance on felt (~1.1 m/s^2: slow mini-golf carpet)
	StopSpeed = 0.2, -- below this speed (and on a gentle slope) the ball is considered stopped
	RestTime = 0.3, -- seconds below StopSpeed before the ball is "at rest"
	MaxBallSpeed = 42,
	MaxRollTime = 25, -- safety: force the ball to rest after this many seconds

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
	VRClubAngle = 0, -- degrees to tilt the shaft away from the controller's pointing direction
	VRGripToPutt = false, -- Walkabout's optional mode: putter is only solid while you hold grip

	-- Rules
	MaxStrokes = 8,
	PenaltyStrokes = 1,
	HoleTransitionTime = 3.5,
}
