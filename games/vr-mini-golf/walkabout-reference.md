# Walkabout Mini Golf reference notes (ball physics + UX)

Reference library for tuning `games/vr-mini-golf` to feel like **Walkabout Mini Golf** (Mighty Coconut).
Built 2026-10-03. Clips, frame sequences, ball tracks, contact sheets and tools live in `assets/vr-mini-golf/walkabout-refs/` (gitignored: `clips/`, `frames/`, `videos/`, all `*.mp4`). The full source videos (~860 MB) were **not** copied to the Mac; they're on the agent box at `/workspace/walkabout-refs/videos/`, or you can re-download them from the URLs in section 1 (`yt-dlp -f 'bv*[height<=720]+ba' <url>`). Source-video transcripts are in `walkabout-refs/videos/*.transcript.txt`.

Method: I couldn't watch the video directly, so every observation comes from extracted frame images/contact sheets and OpenCV ball tracking on static-camera shots. No video-description model was used.

> **Read this first.** Every number below comes from tracking the ball in YouTube footage, or it's quoted from a public source.
> Pixel measurements are turned into metres by assuming the in-game ball is a regulation **42.7 mm** golf ball, using the ball's own on-screen diameter at that spot as the ruler.
> A gravity cross-check (section 3.1) suggests that scale is about right, give or take ~15%.
> Anything marked **(est.)** is an estimate from one or two shots. Treat it as a starting point, not a spec.
> Recordings are 60 fps containers with mostly 30 fps unique content, so timing resolution is about ±1/60 to ±1/30 s.

---

## 1. Sources

| ID | Video | Channel | Length | Used for |
|---|---|---|---|---|
| 5Tka-zeFvA0 | [Relax with VR Mini Golf – Arizona Modern (no commentary)](https://www.youtube.com/watch?v=5Tka-zeFvA0) | SleepyGreens | 20:37, 720p60 | **Main physics source.** Has a static spectator camera after each putt, plus an orange ball that's easy to track |
| b26IAmDzziU | [Walkabout Mini Golf PSVR2 – Alfheim DLC gameplay (no commentary)](https://www.youtube.com/watch?v=b26IAmDzziU) | PSVR ZEST | 24:18, 720p60 | Cup drops, hole-in-one UI, putter ghosting through scenery |
| 7r7z1TUeBwk | [All Holes in One on Tourist Trap Easy](https://www.youtube.com/watch?v=7r7z1TUeBwk) | Blue Bowls | 3:54, 720p30 | Obstacle / bank shots into the cup |
| UGd5fsKtyqM | [You're Playing It Wrong! Walkabout Mini Golf](https://www.youtube.com/watch?v=UGd5fsKtyqM) | Gamer Reality | 6:29, 720p60 | Tutorial: obstacle spin/skid, lock ball, grip-to-putt, OOB reset, controls (has some facecam segments) |
| 0iPdQBGcZOg | [Walkabout Mini Golf Tips And Tricks – From Beginner To MASTER](https://www.youtube.com/watch?v=0iPdQBGcZOg) | VR Lowdown | 14:22, 720p24 | Tutorial: grip-to-putt ghost putter, club through walls, alignment, spin behaviour, settings |
| RtNfSVZzA4Y | [Walkabout Mini Golf Tutorial](https://www.youtube.com/watch?v=RtNfSVZzA4Y) | Infusion VR Arcade | 2:23, 720p60 | Teleport arc/ring, trigger-to-ball |

Transcripts for the three tutorials are in `videos/*.transcript.txt`.
`meta/settings.json` holds the Fandom wiki's settings page ([Game Settings](https://walkabout-mini-golf.fandom.com/wiki/Game_Settings)).

## 2. Clips

All clips are 720p H.264, re-cut from the sources. The time range is the timestamp in the source video.

| Clip | Source | Source time | What it shows |
|---|---|---|---|
| `clips/cup-drop-01.mp4` | [5Tka-zeFvA0](https://www.youtube.com/watch?v=5Tka-zeFvA0&t=88s) | 1:28.2–1:34.2 (6.0 s) | Arizona Modern: static spectator camera, straight putt rolls ~1 m and drops into cup at speed (no lip-out) |
| `clips/wall-bank-01.mp4` | [5Tka-zeFvA0](https://www.youtube.com/watch?v=5Tka-zeFvA0&t=355s) | 5:55.0–6:02.5 (7.5 s) | Arizona Modern: ball drops off upper tier, hops, misses cup, hits near wall almost head-on, rebounds past cup, rolls up slope, stops and rolls back |
| `clips/bounce-rollout-01.mp4` | [5Tka-zeFvA0](https://www.youtube.com/watch?v=5Tka-zeFvA0&t=561s) | 9:21.3–9:27.0 (5.7 s) | Arizona Modern: ball drops onto flat green from height, 3-4 decaying bounces, then rolls to a stop |
| `clips/rollout-stop-01.mp4` | [5Tka-zeFvA0](https://www.youtube.com/watch?v=5Tka-zeFvA0&t=195s) | 3:15.3–3:23.0 (7.7 s) | Arizona Modern: small hops onto green, rollout to stop in ~2 s, then very slow creep back down a gentle slope |
| `clips/ramp-bank-01.mp4` | [5Tka-zeFvA0](https://www.youtube.com/watch?v=5Tka-zeFvA0&t=1003s) | 16:43.5–16:52.0 (8.5 s) | Arizona Modern: ball rides a curved banked ramp down into a bowl around the cup |
| `clips/cup-drop-02.mp4` | [b26IAmDzziU](https://www.youtube.com/watch?v=b26IAmDzziU&t=354s) | 5:54.5–6:00.0 (5.5 s) | Alfheim (PSVR2): close-up of the ball rolling into and dropping in the cup |
| `clips/hole-in-one-ui-01.mp4` | [b26IAmDzziU](https://www.youtube.com/watch?v=b26IAmDzziU&t=852s) | 14:12.0–14:24.0 (12.0 s) | Alfheim hole 17: 'Hole In One!!!' floating banner after the ball drops |
| `clips/obstacle-hit-01.mp4` | [UGd5fsKtyqM](https://www.youtube.com/watch?v=UGd5fsKtyqM&t=118s) | 1:58.5–2:06.5 (8.0 s) | Tourist Trap: hit on a 45-degree wooden obstacle; trail shows deflection then skid/kick (narrated spin explanation) |
| `clips/obstacle-hit-02.mp4` | [7r7z1TUeBwk](https://www.youtube.com/watch?v=7r7z1TUeBwk&t=18s) | 0:18.5–0:26.0 (7.5 s) | Tourist Trap easy: putt deflects off a wooden block toward the cup |
| `clips/club-ghost-wall-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=196s) | 3:16.0–3:28.0 (12.0 s) | Putter shaft passes straight through wooden rails/walls with no collision |
| `clips/grip-to-putt-ghost-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=179s) | 2:59.0–3:15.0 (16.0 s) | Grip To Putt: settings panel, translucent (non-colliding) putter until grip is held, then solid |
| `clips/putter-alignment-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=537s) | 8:57.0–9:17.0 (20.0 s) | Squaring the putter face behind the ball, first-person over the ball |
| `clips/spin-kick-after-wall-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=687s) | 11:27.0–11:47.0 (20.0 s) | Narrated: after an angled bounce the ball slides frictionless then regains traction and kicks with prior spin |
| `clips/settings-putter-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=728s) | 12:08.0–12:28.0 (20.0 s) | Settings panel: putter strength / putter angle |
| `clips/settings-lock-ball-01.mp4` | [0iPdQBGcZOg](https://www.youtube.com/watch?v=0iPdQBGcZOg&t=790s) | 13:10.0–13:26.0 (16.0 s) | Settings panel: Lock Ball Position and movement options |
| `clips/ball-oob-grip-hold-01.mp4` | [UGd5fsKtyqM](https://www.youtube.com/watch?v=UGd5fsKtyqM&t=187s) | 3:07.5–3:18.5 (11.0 s) | Holding grip lets the ball keep bouncing out of bounds without auto-reset (practice mode) |
| `clips/teleport-to-ball-01.mp4` | [RtNfSVZzA4Y](https://www.youtube.com/watch?v=RtNfSVZzA4Y&t=118s) | 1:58.0–2:16.0 (18.0 s) | Teleport arc/ring targeting, trigger teleports you to your ball |
| `clips/controls-overview-01.mp4` | [UGd5fsKtyqM](https://www.youtube.com/watch?v=UGd5fsKtyqM&t=206s) | 3:26.0–3:46.0 (20.0 s) | Narrated controls: trigger teleport, stick teleport/smooth locomotion, snap turn, B replay, A map view |

### Frame sequences (10 fps) and ball tracks

| Folder | Frames | Ball track |
|---|---|---|
| `frames/cup-drop-01/` | 60 | `ball_track_60fps.csv` (source 89.0–91.0 s) |
| `frames/wall-bank-01/` | 75 | `ball_track_60fps.csv` (source 356.45–362.5 s) |
| `frames/bounce-rollout-01/` | 57 | `ball_track_60fps.csv` (source 561.5–566.5 s) |
| `frames/rollout-stop-01/` | 77 | `ball_track_60fps.csv` (source 195.4–203.0 s) |

- `f_0001.jpg` is clip time 0.0 s, and `f_NNNN` ≈ clip time (NNNN−1)/10 s. Source time = clip start (table above) + clip time.
- Each CSV is a per-frame ball centroid in 1280×720 pixels, with columns `source_time_s, clip_time_s, x_px, y_px, blob_w_px`. `blob_w_px` is roughly the ball diameter, but motion blur inflates it at high speed.
- The camera is static in all four of these clips, so no camera-motion correction was needed.
- Tracking scripts are in `tools/`. `track_seg.py` is an HSV ball tracker, `track_bg.py` is a background-subtraction tracker, and `fit_decel.py` fits constant-decel and exponential models to a track.

---

## 3. Ball physics observations

### 3.1 Ground bounce (restitution off the green)

This uses the ratio of successive airtime between ground contacts. That ratio equals the normal restitution *e* and doesn't depend on scale.

| Clip | Contacts (source s) | Airtimes | Ratio |
|---|---|---|---|
| bounce-rollout-01 | 562.217 → 562.867 → 563.250 → 563.500 | 0.650 s, 0.383 s, 0.250 s | **0.59, 0.65** |
| rollout-stop-01 | 195.550 → 195.750 → 195.883 | 0.200 s, 0.133 s | **0.67** |

- **Ground restitution ≈ 0.6–0.65 (est.).** With ±1 frame of error, each ratio could be off by about ±0.05–0.1.
- Hops die out fast after that. Once the airtime drops below ~0.1 s (impact speed ≈ g·t/2 ≈ 0.5 m/s, est.), the next contact turns into rolling, with no long chatter of micro-bounces.
- **Gravity / scale check.** Apex height from bounce-rollout-01 is ≈ 10 ball diameters for the 0.65 s hop and ≈ 3.9 ball diameters for the 0.383 s hop. That works out to g ≈ 8.1 and 9.2 m/s² *if* the ball is 42.7 mm. So the game is consistent with **Earth gravity on a roughly real-size ball** (±15%).
- **Tangential speed loss per bounce.** On rollout-stop-01, ground speed went 15.6 → 13.5 → 10.9 → ~8 ball-diameters/s across the hops. That's a **~15–25% loss per bounce (est.)**, which fits friction spinning the ball up at each impact. This number ignores motion toward or away from the camera.

### 3.2 Wall rebound (wall-bank-01)

The ball hits the near wall almost head-on. In the image, the outgoing direction is the exact reverse of the incoming one, and in perspective that only happens for a near-normal hit.

I compared speeds at the **same image location** before and after the hit, so the perspective scale cancels. Speed is in ball diameters per second:

| | Time (source) | Speed |
|---|---|---|
| incoming | 356.95–357.12 | ≈ 60–62 bd/s (≈ 2.6 m/s est.), roughly steady |
| impact | ≈ 357.22 | ball partly hidden by wall top |
| outgoing, +0.03 s | 357.25 | ≈ 40 bd/s → ratio ≈ **0.65** |
| outgoing, +0.10 s | 357.32 | ≈ 35 bd/s → ratio ≈ **0.57** |
| outgoing, +0.30 s | 357.52 | ≈ 21 bd/s → ratio ≈ 0.34 |

- **Wall restitution (normal) ≈ 0.6 (est., range 0.55–0.65).** This is from a single clean impact.
- **The ball skids hard right after the rebound.** Speed fell from ~40 to ~21 bd/s in 0.27 s, which is ≈ 3 m/s² (est.), or μ_slide ≈ 0.3·g.
  - That's what you'd expect if the ball **keeps its forward topspin through the wall hit**, so the spin fights the new direction until friction brings it back to pure rolling.
  - About 0.3 s after impact, the ball is carrying only about **⅓ of its incoming speed**.
- This matches what players describe publicly (section 5): after a bounce the ball first moves "as if there were no friction or spin", then "regains traction" and "kicks slightly in the direction of the spin that was on the ball before it hit".
  - Gamer Reality also shows a 45° obstacle where the ball "takes a moment to spin as it's changing direction and then it skids".
  - So the exit angle is the mirror reflection at first, then it bends.
- Geometry note: in `obstacle-hit-01` the trail off the 45° block looks close to a mirror reflection right at impact, then curves slightly.

### 3.3 Rolling friction and stopping time

| Clip / run | Speed range (est.) | Decel (est.) | Model fit |
|---|---|---|---|
| cup-drop-01 (flat, dark green) | 0.87 → 0.47 m/s over 1.6 s, ~1.0 m | **0.29 m/s²** | Constant decel fits better than exponential (rms 2.4 vs 3.7 mm). Speed falls ~linearly |
| rollout-stop-01 (gentle slope) | 0.41 → 0 m/s in **2.05 s**, ~0.36 m | 0.35 m/s² early → 0.1–0.2 m/s² late (mean ≈ 0.2) | Exponential fits better here. The slope affects the tail |
| bounce-rollout-01 tail | 0.20 → 0 m/s in ~1.2 s, ~0.13 m | ≈ 0.15 m/s² | Both fits are about equal |

- **Rolling deceleration ≈ 0.15–0.35 m/s², central ≈ 0.25 m/s² (est.).** That's an equivalent rolling-resistance coefficient of ~0.025.
  - Projected path lengths undercount any motion toward or away from the camera, so the true values could be up to ~30% higher.
  - Either way, the surface is **very fast**: about 4× slower deceleration than our current `RollDecel = 3.6 studs/s²` (1.1 m/s²).
  - It's also faster than a real putting green. A Stimpmeter-equivalent of ~20 ft (est.) vs 8–12 ft on real greens.
- A single model that roughly fits all three runs: **a(v) ≈ 0.15 m/s² + 0.25 s⁻¹ · v (est.)**. That's a constant rolling friction plus a gentle speed-proportional term.
- **Stopping time:** typical short putts (0.4–0.9 m/s) roll for **~2–3.5 s**. The stop is soft, with a long low-speed tail rather than a sudden halt.
- **Creep on gentle slopes.** In rollout-stop-01 the ball "stops" at ~198.1 s, then keeps creeping back downhill at about 0.5–1 cm/s for more than 4 s. wall-bank-01 shows the same thing.
  - So Walkabout does not seem to snap a slow ball to rest on a slight slope. Slope gravity still wins at very low speed.

### 3.4 Slides vs rolls

- Off the putter, the ball **rolls**. VR Lowdown (7:55): you can't put side spin, top spin or back spin on the ball. The only spin comes from rolling along surfaces and bouncing off objects. The game only uses the swing at the moment of contact (Gamer Reality 1:48).
- After wall or obstacle impacts and bounces, there's a **short skid phase** (see 3.2). The ball keeps its spin through the collision, then friction re-couples it.

### 3.5 Ramps and slopes

- `ramp-bank-01`: on the Arizona Modern banked bowl, the ball rides up the curved bank and its trail arcs smoothly back down into the bowl. There's no visible hop where the bank meets the flat.
- `wall-bank-01`: after the wall rebound, the ball rolls up a sand-dune undulation, stops at ~359.6 s, rolls back ~60 px and settles at ~361.5 s. At low speed, slope gravity dominates.
- `bounce-rollout-01` / `rollout-stop-01`: a ball dropped from an upper tier lands with 2–4 visible hops, then rolls. Drops aren't dead (see 3.1).

### 3.6 Cup

- `cup-drop-01`: the ball reaches the cup at **≈ 0.47 m/s (est.)** and is captured immediately. It's gone within ~0.2 s, with no rim rattle, orbit or lip-out visible.
- `cup-drop-02` (Alfheim close-up): the ball rolls in and drops within one or two 10 fps frames, again with no lip-out.
- Cup diameter looks like ≈ 2.3–2.8 ball diameters (rough, from pixel widths), close to a regulation 108 mm cup with a 42.7 mm ball (2.53).

---

## 4. UX details observed

**Putter and hands**

- **One controller.** There's one putter hand and no off-hand model (Gamer Reality 0:44). Players are told to steady the controller with the free hand.
- The **putter shaft extends from the controller tip.** Its length is continuously variable: crouch and the shaft gets short, stand tall and it gets long. The **head stays at ball-contact height above the ground**. This comes from a Steam thread answer that a developer marked as correct, and matches our `VRPlaneRange` behaviour.
- **The club goes through geometry.** The putter never collides with walls, rails or scenery, so you can putt with the shaft passing through a wall (`club-ghost-wall-01`, Alfheim clips; UploadVR review: "Your putter can't collide with the environment… you can just putt right through it").
- **Grip To Putt** (`grip-to-putt-ghost-01`): the putter is drawn translucent/teal and can't hit anything until you hold grip, then it turns solid. This lets you take practice swings right through the ball. Recommended on by every tutorial.
- **Putter settings** (wiki / `settings-putter-01`):
  - **Strength** (swing → ball-speed multiplier)
  - **Angle** (head angle relative to the controller)
  - **Custom Grip** calibration (tilt/rotation/position, for golf-club attachments)
  - **Invert Hands**
  - **Putter Tracking Guard** (disables the head when tracking is poor)
- **Alignment.** Players square the putter face to the target line (`putter-alignment-01`). There are faint dots on the green that help with lining up (Gamer Reality 1:26).
- The putter head **detects the hit from the swing's face motion at contact.** Flicking or pushing is called out as producing off-line shots.

**Movement**

- **Trigger = warp to your ball.** The whole game is playable with just the trigger (Lucas Martell interview).
- **Lock Ball Position** puts the ball at the centre of your real play area every time you warp. Related settings: **Distance To Ball**, **Auto Teleport** (warps you to the ball once it stops), turning speed, and locomotion speed.
- **Teleport** uses an arc with a **blue ring** target (`teleport-to-ball-01`). There's smooth locomotion, snap or smooth turn, and **flying**: aim the teleport straight up, push forward, and after a second you lift off.
- **A = giant/map view.** It shows the scorecard and you can teleport anywhere from it. **B = replay your last shot.** Pulling the stick down collects lost balls/clues.

**Ball handling**

- **Out of bounds:** the ball auto-resets after going OOB. **Holding grip stops the reset** so the ball can keep bouncing (`ball-oob-grip-hold-01`; Gamer Reality 3:13).
- **Practice mode:** click or press back on the thumbstick to redo the shot or hole.
- **Stroke limit:** the last allowed stroke is scored as a triple bogey, and a miss is a quadruple bogey (wiki).

**Feedback**

- **Ball trail:** a white streak behind the ball. You can turn it off.
- **Ball locator:** small yellow arrows at the edge of your vision, shown **only when the ball is off-screen**.
- **Sonar rings:** concentric rings show the ball when it's hidden, for example in a chute (Lucas Martell).
- **Hole in one** (`hole-in-one-ui-01`): a pill-shaped dark floating label **"Hole In One!!!"** appears in view for ~3–4 s, with applause/fireworks sounds (wiki). There are optional Birdie/Eagle notifications too.
- **Wristwatch** shows hole, strokes, par and time when you look at it.
- **Sound:** a distinct "click" on the hit and recorded rolling/bounce sounds per surface (Lucas Martell).

---

## 5. Public info on Walkabout's physics

**Lucas Martell, creator** ([Voices of VR #1560, May 2025](https://voicesofvr.com/1560-walkabout-mini-golfs-incredible-fusion-of-worldbuilding-gameplay-social-dynamics-dlc-experimentation/)):
- "a huge amount that we've done on the physics side… to really dial that in."
- The physics stays the same across courses: "we try at all costs to avoid cheating the physics… it's okay to cheat the physics if it helps the player."
- The only exception he mentions is **Upside Town, where they reduced the bounciness of the greens** ("like some might have really thick carpet and some might have thinner carpet").
- Mini mode and low-gravity modes change gravity so it feels right at the new scale.

**Other Mighty Coconut sources**
- [Meow Wolf dev blog](https://www.mightycoconut.com/blog/mw-bts): "a lot of custom physics we are running under the hood to have our golf ball behave as realistically as possible". Each Multi-Ball runs the same custom ball physics system.
- [PSVR2 interview, The VR Dimension](https://thevrdimension.com/walkabout-mini-golf-the-playstation-vr2-interview-2/): Lucas "originally created the putting physics put a lot of time and effort into getting it right."

**Club ghosting and staying on the plane**
- [UploadVR review](https://www.uploadvr.com/walkabout-mini-golf-review/): "Your putter can't collide with the environment so you don't have to worry about your ball being too close to a barrier – you can just putt right through it."
- [Steam thread, developer-marked answer](https://steamcommunity.com/app/1408230/discussions/1/4038101970208904819/): "The putter length is continuously variable… the putter head stays at the proper ball contact height above the ground while you control the other two dimensions." A Mighty Coconut staffer adds it "should be auto-adjusting".

**Spin after bounces**
- [VR Lowdown tips](https://vrlowdown.com/walkabout-mini-golf-tips/) (video 11:27): the ball "initially loses traction… bounce[s] off the object as if there were no friction or spin… after a short distance the ball regains traction… kick[s] slightly in the direction of the spin that was on the ball before it hit the object."
- Also from VR Lowdown (7:55): "The only way to generate spin… is by letting it roll along surfaces and bounce off objects."
- Gamer Reality (2:11): "when the ball hits the obstacle it takes a moment to spin as it's changing direction and then it skids", so aim slightly off-centre to account for the skid.

**Settings reference**
- [Fandom wiki: Game Settings](https://walkabout-mini-golf.fandom.com/wiki/Game_Settings) covers putter, movement, visuals and options as listed in section 4.

**Not verified**
- A Reddit thread, "Will hitting the ball high or low affect spin" (r/WalkaboutMiniGolf), came up in search with a summary saying faster shots skid more after bounces. Reddit blocked direct fetching, so treat that as unverified.

---

## 6. Suggested Roblox starting parameters

Current project scale is **1 stud = 0.3 m** (`Golf/Config.luau`). Conversions below use that.

| Parameter | Current | Suggested start | Basis |
|---|---|---|---|
| Gravity felt by the ball | `workspace.Gravity` (check; Roblox default 196.2 = **6× Earth** at this scale) | **≈ 32.7 studs/s²** (9.81 m/s²), or apply an equivalent per-ball force | 3.1 gravity check: WMG behaves like Earth gravity at real scale |
| `RollDecel` (constant rolling resistance) | 3.6 studs/s² (1.1 m/s²) | **≈ 0.8 studs/s² (0.25 m/s²)**; tune range 0.5–1.2 | 3.3. Putts should roll ~2–3.5 s and ~4× farther than now for the same launch speed |
| Optional speed-proportional drag | none | **0.5 studs/s² + 0.25 s⁻¹ · v** instead of a pure constant | 3.3 combined fit. Use it if a pure constant feels too floaty at high speed or too abrupt at the end |
| Wall `Elasticity` | 0.8 (weight 100) | **0.6** (range 0.55–0.65), keep weight 100 so it dominates | 3.2 |
| Wall `Friction` | 0.02 | keep low (0.02–0.05) | So the ball keeps its spin through the hit (the "no friction at impact" feel) |
| Post-impact skid | ball spin reset to pure roll each step (`BallController` sets `AssemblyAngularVelocity = n:Cross(along)/R`) | After a wall or obstacle hit, **keep the pre-impact spin** and brake the slip at **μ_slide ≈ 0.3 → ≈ 9.8 studs/s²** until v = ωR, then go back to rolling | 3.2 skid (~3 m/s² for ~0.3 s), plus the public "regains traction and kicks" descriptions |
| Felt / green `Elasticity` | 0 | **≈ 0.6** for real drops, plus a script **bounce threshold**: zero the normal velocity if impact normal speed < **~1.5 studs/s (≈ 0.45 m/s)** | 3.1. Drops bounce 2–4 times, and small hops die out quickly |
| Tangential loss per bounce | felt friction 0.35 | keep ~0.3–0.4; aim for 15–25% ground-speed loss per hop | 3.1 |
| Cup capture | (per hole) | Capture without lip-out at entry speeds of at least **~1.6 studs/s (0.47 m/s)**; err generous | 3.6. No lip-outs seen |
| `StopSpeed` / `RestTime` | 0.2 studs/s (6 cm/s) / 0.3 s | On slopes, let gravity keep the ball creeping (WMG creeps at 0.5–1 cm/s). Only declare rest on near-flat ground, or after a longer `RestTime` (~0.5–1 s) | 3.3 creep |
| Ball size | 4.8 cm | fine as is. WMG looks close to regulation (42.7 mm) | 3.1 / 3.6 |
| Putter collision | n/a | The putter should only ever collide with the ball, never with scenery. `VRGripToPutt` should render a translucent putter while it's off | section 4 |

**Tuning targets to check in playtests** (scale-free where possible):
- A ~0.9 m/s putt on flat felt should still be doing ~0.47 m/s after ~1.6 s / ~1 m (cup-drop-01).
- A 0.4 m/s roll should stop in ~2 s over ~35 cm (rollout-stop-01).
- A drop that hops for 0.65 s should follow with hops of ~0.38 s and ~0.25 s (bounce-rollout-01).
- A head-on wall hit should leave at ~0.6× speed, then shed to ~⅓ of the incoming speed within 0.3 s (wall-bank-01).

## 7. Caveats

- Every metric conversion assumes a 42.7 mm ball. If WMG's ball is bigger, scale all m/s and m/s² values up proportionally. Restitution and timing ratios don't depend on this.
- Track paths undercount any motion toward or away from the camera, so decelerations are likely underestimated (up to ~30%).
- The physics numbers come from the Arizona Modern course only (felt plus sand-dune undulations). Lucas says physics stays consistent across courses, Upside Town aside.
- The wall restitution comes from one clean impact. More impacts would tighten the range.
