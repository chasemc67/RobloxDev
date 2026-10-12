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
	StrokeTimeout = 20, -- safety net: a stroke still moving after this many seconds resets to its last rest point
	PinNudgeTime = 1.5, -- a slow ball held against a moving part this long is hopped clear (Playtest Bot: 1.5 s)
	-- Holes with moving parts or teleports get an AutoResetStill attribute (CourseBuilder; default below, or the
	-- spec's per-hole `auto_reset_still`, false = off): a ball stuck that long goes back to the stroke start for free.
	AutoResetStill = 3,
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
	TouchMaxSpeed = 19.8, -- ball speed at 100% power: the Lantern Grove spec max putt (19.78 studs/s rolls 60 studs)
	TouchPowerCurve = 1.3,

	-- VR putter
	VRHitMultiplier = 1.7, -- ball speed = putter face speed * this (a light ball off a heavy putter)
	VRTangentialTransfer = 0.1,
	VRMinHitSpeed = 0.3, -- studs/s; slower contacts are ignored
	VRMoveSpeed = 6.5, -- thumbstick walk speed, studs/s (~2 m/s)
	VRSnapTurnDegrees = 30,
	VRStanceDistance = 1.5, -- warp-to-ball puts your head this far from the ball (45 cm)
	-- Club mount: the shaft runs PARALLEL to the controller handle. With VRClubFlip (default, v80) it comes out
	-- of the handle's TOP end; unflipped (v12-v79) it came out of the bottom, which Chase found pointing the wrong
	-- way in VR (2026-10-10 playtest of v79). Hand UserCFrame axes on Quest Touch (aim pose): -Z = aim/laser ray,
	-- +Y = top of the controller (face buttons), +X = controller right. The handle runs down from the top along -Y,
	-- raked back toward +Z (the bottom of the grip sits down and back toward your wrist, like a pistol grip).
	-- Shaft direction in hand space = CFrame.Angles(rad(-90 - VRClubGripPitch), 0, 0) * yaw * roll applied to -Z,
	-- i.e. -Y tilted VRClubGripPitch degrees toward +Z, when unflipped. VRClubFlip negates that vector (+Y tilted
	-- toward -Z, i.e. adds 180 deg about hand X and negates yaw). Starts VRClubButtOffset studs along the shaft
	-- from the hand origin (bottom of the handle unflipped, top when flipped). Pitch is about hand X, so it is the same for both hands; yaw/roll are
	-- mirrored for the left hand. Unverified on a real Quest: see games/vr-mini-golf/playtesting.md.
	VRClubFlip = true, -- shaft out of the handle's top (false = v12-v79 out-of-the-bottom mount)
	VRClubGripPitch = 35, -- degrees, + rakes the handle bottom back toward the wrist (+Z)
	VRClubGripYaw = 0, -- degrees, + swings the shaft toward the controller's right (+X); mirrored for the left hand
	VRClubGripRoll = 0, -- degrees about the shaft (turns the putter face); mirrored for the left hand
	VRClubButtOffset = 0.25, -- 7.5 cm from the hand origin to the shaft-side handle end
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

	-- Audio (all public, verified 2026-10-11). SFX play through SoundService.SFX, music through SoundService.Music.
	Sounds = {
		CupPlunk = "rbxassetid://9117183624", -- ProSoundEffects "Pacifier 1" comic plop, 0.47 s
		CheerBig = "rbxassetid://125361506894319", -- big crowd cheer, 7.1 s (hole-in-one / eagle or better)
		Applause = "rbxassetid://7367718809", -- applause, 6.7 s (layered under CheerBig)
		Birdie = "rbxassetid://105154404054447", -- small crowd cheering + clapping, 3.7 s
		Par = "rbxassetid://72098222084567", -- polite applause, 4.0 s
		Bogey = "rbxassetid://9114762131", -- ProSoundEffects slow hand claps, 2.9 s
		Aww = "rbxassetid://77211275419736", -- small "aww", 1.7 s (double bogey or worse, max strokes)
	},
	ReactionDelay = 0.25, -- seconds from the cup plunk to the crowd reaction
	ReactionFadeAfter = 4, -- long reactions fade out after this many seconds (before the next hole)

	-- Front-end art (uploaded 2026-10-11, assets/vr-mini-golf/store/ui)
	UI = {
		ClubSetup = { step1_stance = "rbxassetid://122984304115771", step2_stick = "rbxassetid://110561580015778", step3_trigger = "rbxassetid://124290294292343", howto_card_bg = "rbxassetid://71799829989383", ground_marker = "rbxassetid://113621422195787", icon_reset = "rbxassetid://107608940377791" },
		Logo = "rbxassetid://73526573447336", -- 2048x768 transparent
		TitleBackground = "rbxassetid://75624699940778", -- title_bg_v2.png 1920x1080 (stage q)
		CardLanternGrove = "rbxassetid://100112215630907", -- card_lanterngrove_v2.png 1024 square (stage q)
		CardSugarloaf = "rbxassetid://75996957007483", -- grey, "coming soon" tag baked in (unused since stage w)
		CardSugarloafPlay = "rbxassetid://71252934424990", -- card_sugarloafcanyon_v2.png 1024 square (stage w: playable)
		CardAurora = "rbxassetid://82146694601580", -- grey, "coming soon" tag baked in
		-- VR pointer + wrist card (stage p, store/ui/wrist, tools/stage_p_assets.json)
		PointerDot = "rbxassetid://124186475881466", -- 64x64
		HoverGlow = "rbxassetid://89859858365518", -- 128x128 9-slice, SliceCenter 40,40,88,88
		WristCard = "rbxassetid://73442368184232", -- 1024x640 parchment + brass, no text
		IconHole = "rbxassetid://89045323420740",
		IconPar = "rbxassetid://100554682607003",
		IconStroke = "rbxassetid://80712879947831",
		IconTotal = "rbxassetid://131506164236528",
		IconBest = "rbxassetid://101092439594881",
	},
	-- VR wrist (bracer + card on its face): hidden in normal play; it shows only while you actively look at the
	-- off-hand wrist (Walkabout style). Show: the back of the wrist faces your eyes within WristShowDeg AND the wrist
	-- is within WristGazeDeg of your gaze centre, held for WristShowHold s. Hide: once out past WristHideDeg /
	-- WristGazeHideDeg for WristHideHold s. Never while the putter head moves faster than WristMaxClubSpeed (and
	-- WristSwingQuiet s after), or in a putting stance (putter head within WristStanceRange of a hittable ball).
	WristShowDeg = 70,
	WristHideDeg = 85,
	WristGazeDeg = 55,
	WristGazeHideDeg = 70,
	WristShowHold = 0.25,
	WristHideHold = 0.4,
	WristMaxClubSpeed = 3, -- studs/s (0.9 m/s); a putt stroke is faster
	WristSwingQuiet = 0.5,
	WristStanceRange = 1.5, -- studs, flat, with the putter head low (within 0.8 of the ball)
	-- VR see-through: the occluder fade runs from the head to your ball while it's within this many studs
	VRFadeRange = 40,
	-- Courses on the picker. Only playable ones have a personal best (player attribute "Best_<id>").
	Courses = {
		{ id = "lantern_grove", name = "Lantern Grove", image = "CardLanternGrove", playable = true },
		{ id = "sugarloaf_canyon", name = "Sugarloaf Canyon", image = "CardSugarloafPlay", playable = true }, -- stage w
		{ id = "aurora_archipelago", name = "Aurora Archipelago", image = "CardAurora", playable = false },
	},
	CurrentCourse = "lantern_grove", -- the default course; each player's own is the player attribute "Course" (Golf.Courses)

	-- Player settings (saved with the personal best record). Volumes are 0..1, CameraSensitivity a multiplier.
	DefaultSettings = {
		MusicVolume = 0.6,
		SFXVolume = 0.8,
		Handedness = "Right", -- "Right" | "Left" (VR club hand)
		CameraSensitivity = 1,
		CourseMode = "Peaceful", -- "Peaceful" (balls pass through each other) | "PVP" (balls collide); BallGroups
	},
	CameraSensitivityRange = { 0.5, 2 },
}
