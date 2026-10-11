# VR Mini Golf, round 4 playtest (v116), Playtest Bot
2026-10-11, about 10:45–11:40 PT. Claude Code (Opus 5.5) on the Mac Mini, Studio MCP, place 87725688219952.
Read-only: nothing was saved or published, no `src/` edits or pushes, and no agreement pop-ups appeared. Studio was left in Edit mode with
the workspace attributes it started with (`SimulateVR=false, GolfTestMode=false, SavedAtm=0.32`). `SkipMenu` and `R4Marker` were removed.
The temporary changes I made (unbinding the golf camera render step to frame the screenshots, firing `HoleComplete` and `SaveSettings`) only lived in Play sessions
that have since been stopped.

## Summary
| # | Check | Result |
|---|---|---|
| 1 | Camera near walls (483 round-3 spots × 12 yaws) | **PASS. 0 bad poses of 5796** (round 3: 178 severe spots of 516). The camera never sits < 3 studs from the ball: min distance 5.99 at every spot. Blockers fade to `LocalTransparencyModifier` **0.7** (`CameraOcclusion.FADE`), confirmed on all 9 worst spots. Two polish issues, see below |
| 2 | Slopes | 17 felt pieces tilt > 1.5°. **All 17 have the `SlopeFelt` Texture**, and no slope was missed. The texture key matches the computed part-local downhill on all 14 non-tied pieces. **But the mask is a symmetric zigzag, so it shows the slope axis and not which way is down** (see below) |
| 3 | Hole-out audio | Plunk + reaction for all 7 results measured (SoundId, Volume, TimeLength, speed, delay 0.27 s, overlap 0.25 s). Peak/RMS only for the 2 downloadable assets: no clipping. **Nobody has listened to any of it** |
| 4 | Front end | Title, course picker (Lantern Grove + 2 "Coming soon"), Settings, How to play, results scorecard and Play again all render on desktop, phone and VR. 0 console errors. Polish gaps listed below |
| 5 | Personal best | Studio path (PBInStudio off) stays in memory: 0 DataStore calls and 0 errors. Logic correct (keeps the lower total, isNew/prev right). Settings are clamped and unknown keys dropped. A raw Studio DataStore call fails with `502 … Studio access to APIs is not allowed` |
| 6 | Block rate (24 shots) | **H7 log 12/24 = 50.0%** (touched 14) PASS at the top edge. **H8 root door 12/24 = 50.0%** (touched 12) PASS at the top edge. **H9 pendulum 8/24 = 33.3%** (touched 12) still below 38%, but up from 8.3% |
| 7 | Lanterns / glow / firefly | 212 visible props, **178 lit (84%)**. All rail lanterns are lit now (crook 39/39, stake 6/6, hook pair 16/16) and so are all H8 glow props. Unlit: 24 sky_lantern, 8 mere_lantern_boat, old_lantern_tower and lantern_falls_curtain (world backdrop, neon only) |
| 8 | Regression | clubviz: identical to round 3 (flip on: shaft leaves the top, 0° to the mount axis, head 0.011 above the plane, both hands). smoke desktop PASS, smoke iphone_17_pro PASS. 0 server/client errors or warnings in every run |

## 1. Camera (`camprobe/`, `camera/`)
`python3 tools/camprobe.py --spots playtests/round3/camprobe.json --out playtests/round4/camprobe` → `camprobe/summary.md`, `camprobe_after.json`.
I also ran an extra probe over the same spots → `camprobe/camdist.json`. For each spot it records the min camera distance under `passThrough`, the old `resolve` (round-3 behaviour) on today's geometry, and the number of faded parts.

| Hole | Spots | R3 severe spots (cam < 3 studs) | R4 spots with a bad pose | R4 bad poses / all | R4 min cam dist | Old `resolve` < 3 studs on v116 geometry | Faded parts per pose, mean / max |
|---|---|---|---|---|---|---|---|
| 1 | 31 | 4 | 0 | 0 / 372 | 5.99 | 1 | 3.2 / 18 |
| 2 | 38 | 15 | 0 | 0 / 456 | 5.99 | 17 | 3.5 / 18 |
| 3 | 69 | 26 | 0 | 0 / 828 | 5.99 | 26 | 4.7 / 17 |
| 4 | 55 | 18 | 0 | 0 / 660 | 5.99 | 17 | 3.5 / 19 |
| 5 | 42 | 16 | 0 | 0 / 504 | 5.99 | 21 | 4.8 / 19 |
| 6 | 56 | 17 | 0 | 0 / 672 | 5.99 | 16 | 4.1 / 19 |
| 7 | 49 | 21 | 0 | 0 / 588 | 5.99 | 14 | 3.5 / 23 |
| 8 | 57 | 18 | 0 | 0 / 684 | 5.99 | 19 | 18.0 / 55 |
| 9 | 86 | 43 | 0 | 0 / 1032 | 5.99 | 35 | 38.9 / 51 |
| all | 483 | **178** | **0** | **0 / 5796** | 5.99 | 166 | |

(516 spots were probed in round 3. `camprobe.json` keeps the 483 that had any push, so 483 is the set replayed here.)
- The fix comes from the pass-through camera, not from geometry changes: the old push-in logic would still collapse at 166 of these spots today. No Terrain intrudes at any spot (that is the only thing that can still pull the camera in).
- Worst remaining fill is 0.31, under the 0.4 limit (H3 148.1,44.5,26.1 yaw 180 and H9 -82.8,41.5,19.6 yaw 240: rail backing + rail4).
- **Fade confirmed:** at each of the 9 round-3 worst spots every occluder had `LocalTransparencyModifier = 0.70` (counts: H1 6, H2 4, H3 4, H4 7, H5 12, H6 10, H7 4, H8 56, H9 40) → `camera/shots.json`.
- Screenshots: `camera/h{1..9}_cam_<x>_<y>_<z>_yaw<deg>.png`, same names as round 3. The magenta sphere is the ball spot. The camera was posed by script (golf render step unbound, same pitch 30 / dist 6 / `passThrough` / `fade`), so the HUD still says Hole 1. The ball is visible in all 9.
- **Polish 1 (H8/H9):** H8 and H9 sit inside the hollow tree. A hit on `hollow_tree_world_shell` fades the whole 35-part shell, so 39–56 parts go 70% transparent at most poses there. It works, but the tree around the player turns ghostly. H8 rails also bloom white/overexposed in `h8_cam_…png` and `slopes/h8_*`.
- **Polish 2 (frame edges):** only the sight line, a ±10°×±8° cone and parts within 0.45 studs of the camera fade. Big decor just off-axis stays opaque:
  - `h6_cam_…png`: the Hole 6 tee sign and a cream wall panel cover about 40% of the frame.
  - `slopes/h9_heart_slope_3.4deg_d6.png`: the H9 lantern pendulum (Neon glow, LTM 0) sits about 0.6 studs in front of the lens and washes the view yellow. This depends on the pendulum's phase.

## 2. Slopes (`slopes/`)
Every `GolfSurface`/Felt/Ramp part (88; the 9 CupPlates are unions, flat). For each, the tilt comes from the most upward face normal, downhill = −Y projected onto that face, and that is compared with the `SlopeFelt` Texture and its mask key. Full table: `slopes/slopes_table.md`. Raw data: `slopes/slopes.json`.

| Hole | Piece | Tilt | Chevron texture | Texture downhill axis matches actual |
|---|---|---|---|---|
| 1 | ramp | 4.8° | yes | yes (+Z) |
| 3 | bank1 / bank2 | 45° / 45° | yes / yes | yes / yes |
| 4 | ramp | 4.3° | yes | yes |
| 5 | root1 / root2 | 3.5° / 3.5° | yes / yes | yes / yes |
| 6 | ramp | 2.4° | yes | yes |
| 7 | t3_slope | 2.5° | yes | yes |
| 8 | c2 | 6.1° | yes | yes |
| 8 | alcove_bank | 21° | yes | yes |
| 8 | bank1 / bank2 | 45° / 45° | yes / yes | tie: the Top and Right faces are both at 45°. The texture is on Top, keyed from Top. Consistent, but I didn't check which face the player sees |
| 9 | heart_slope | 3.4° | yes | yes |
| 9 | ramp | 5.7° | yes | yes |
| 9 | tunnel_in / tunnel_out | 7.6° / 7.6° | yes / yes | yes / yes |
| 9 | bank1 | 45° | yes | tie, as for H8 |

- **Missed slopes: none.** The smallest tilt is 2.4°. Nothing sits between 1.5° and the builder's 2° threshold, and no wedge, union or mesh felt is sloped.
- The direction check relies on CourseBuilder's documented mapping (Top-face texture +U → part −X, +V → part −Z). I didn't verify that mapping independently, but the screenshots show the zigzag rows crossing the fall line on every ramp, which is right.
- **Readability issue (Game Art Bot):** `art/slope/slope_mask_r*.png` is a repeating zigzag. It looks the same rotated 180° (r0 ≈ r180, r90 ≈ r270, shifted half a period), so a player can see that the felt is sloped and along which axis, but not which way is downhill. The four rotations only matter for the axis. To show the direction it needs a one-sided chevron (a "V" with shading on one side) or arrows.
- Visibility: on the 2.4–7.6° ramps the tinted zigzag reads clearly from the putting camera (e.g. `h1_ramp_4.8deg_d6.png`, `h4_ramp`, `h7_t3_slope`). It is a big improvement on round 3.
- Screenshots: `slopes/h<N>_<piece>_<tilt>deg_d6.png` (putting camera, dist 6, pitch 30, looking downhill) and `_d14.png` (pulled back), for all 17 pieces.

## 3. Hole-out audio (`audio/audio.md`)
`HUD.holeOutAudio`: `CupPlunk` (vol 0.5, speed 0.9), then the reaction after `Config.ReactionDelay` 0.25 s. All play through `SoundService.SFX` (0.8 by default), so the effective level is vol × 0.8.
I fired `HoleComplete` for each result from the Server and timed `IsPlaying` on the client:

| Result | Reaction SoundId | Vol | TimeLength | Starts after plunk | Overlap with plunk (plunk is 0.52 s at 0.9x) | Ends |
|---|---|---|---|---|---|---|
| Hole-in-one | CheerBig 125361506894319 + Applause 7367718809 | 0.70 + 0.45 | 7.11 s / 6.74 s | 0.28 s | 0.25 s | fade at 4.0 s, stop 5.5 s |
| Eagle | same | same | same | 0.27 s | 0.25 s | 5.47 s |
| Birdie | Birdie 105154404054447 | 0.65 | 3.70 s | 0.27 s | 0.25 s | 3.98 s |
| Par | Par 72098222084567 | 0.55 | 4.00 s | 0.27 s | 0.25 s | 4.25 s |
| Bogey | Bogey 9114762131 | 0.60 | 2.90 s | 0.27 s | 0.25 s | 3.15 s |
| Double bogey+ | Aww 77211275419736 | 0.60 | 1.72 s | 0.27 s | 0.25 s | 1.97 s |
| Max strokes | Aww (no plunk, no delay) | 0.60 | 1.72 s | – | – | 1.72 s |

Plunk: `CupPlunk` 9117183624, vol 0.5, TimeLength 0.467 s, PlaybackSpeed 0.9. Every sound loaded (`IsLoaded`), and the live Config matches `src/`.
- File analysis: CupPlunk peak −2.6 dBFS, RMS −21.2 dBFS, 0 clipped. Bogey peak −5.8 dBFS, RMS −29.1 dBFS, 0 clipped.
  - **The other 5 assets need an authenticated download, so I didn't analyse them.** I didn't use Chase's cookie.
  - Recording Studio's output **isn't feasible**: the Mini has no loopback device (only "Mac mini Speakers") and no ffmpeg.
- Notes:
  - The plunk is tied to the server's `HoleComplete` remote, not to the ball physically dropping, so a live server adds network latency.
  - The big cheer runs about 2 s past `HoleTransitionTime` (3.5 s) into the next tee.
  - The Bogey file is about 8 dB quieter (RMS) than the plunk.
- **Nobody has listened to any of this.** Mix, loudness and timing are unverified by ear.

## 4. Front end (`ui/`, `ui-vr/`, `ui-phone/`)
I ran `menu_shots.py` for desktop, VR and `iphone_17_pro` (logs: `menu_*.log`), with 0 errors in each.

| Page | Desktop | Phone | VR |
|---|---|---|---|
| Title | OK: logo, Play, Explore, Settings, How to play, hint line | OK | OK (no Explore button in VR, correct) |
| Courses | OK: Lantern Grove (9 holes, Par 27, "No best yet", Play) + Sugarloaf Canyon and Aurora Archipelago greyed, "COMING SOON" | OK | OK |
| Settings | OK: Music 60%, SFX 80%, Camera 1x, VR club hand L/R | OK | OK |
| How to play | OK, 3 columns | text very small | text tiny at 4 studs |
| Results | OK: 9-hole scorecard (green under par, red over), Total 25 (−2), "New best!", "was 28", Play again, Back to menu | OK | OK ("Play again (B / Y)") |
| Golf HUD | OK | OK ("Pull back… pinch to zoom") | OK |

Bugs and polish gaps:
1. **`menu_shots.py --vr` frames nothing.** The simulated head is pitched 60° down, so all 6 `ui-vr/vr_*.png` show only the tee. I re-shot with the head levelled (`ui-vr/vr_level_*.png`, `menu_vr_level.log`): the panel renders 4.0 studs away, 4.2×2.43 studs. The tool should level the head itself.
2. VR panel position jumps between pages in the sim: title, courses and results sit right of centre, settings and how-to left of centre, with the same head pose.
3. How-to text is hard to read on phone (`ui-phone/phone_menu_howto.png`, about 6 px in the emulator capture) and in VR. The footer line is smaller still. VR legibility needs a headset.
4. Results card: a large empty band between the best line and the buttons (desktop).
5. HUD at the hole 1 tee: the tee sign is cropped top-left behind the "Hole 1 – Lantern Gate" label (desktop and phone).
6. Settings: the 1x camera-sensitivity bar is only about 1/3 full (range 0.5–2), which reads as "low". Cosmetic.
7. Settings round trip: firing `SaveSettings` directly updates the player attributes but not the SoundGroup volume. That is by design (FrontEnd applies volumes locally and reads attributes only at load), so it's not a bug.

## 5. Personal best
Module `ServerScriptService.GolfServer.PersonalBest`: store `VRMiniGolf_PB_v1`, key `u_<UserId>`, UpdateAsync keeps the lower total, 4 tries with backoff, settings writes batched over 6 s, flush on BindToClose.
- **Studio with `PBInStudio` unset (expected path):** `offline` is set at require time, so no DataStore request is made and nothing is logged. The player gets `SettingsLoaded=true` and the default settings.
- **Logic test:** a fresh module clone (offline, so no writes) gave:

  | Call | best | new | prev |
  |---|---|---|---|
  | recordRound 30 | 30 | true | nil |
  | recordRound 33 | 30 | false | 30 |
  | recordRound 26 | 26 | true | 30 |
  | recordRound 26 | 26 | false | 26 |

  After unload, the record is cleared (in memory only, so it's lost on rejoin in Studio, as expected).
- **Settings:** through the real `SaveSettings` remote, `{SFX 0.3, Left, Music 5, Camera 9, Bogus}` became `SFX 0.3, Left, Music 1 (clamped), Camera 2 (clamped)`, and Bogus was dropped.
- **DataStore limits in Studio:** a raw `GetAsync` from Studio returns `502: API Services rejected request … Studio access to APIs is not allowed` (error code 7). Real persistence can only be tested in a live server or with API access enabled. I did neither, and never set `PBInStudio`.
- I didn't test a real 9-hole counted round end to end in Studio: it takes a full normal round, and `GolfTestMode` rounds don't count.

## 6. Block rate (`blockrate/`)
`run_playtests.py run blockrate --no-vr --opts '{"blockShots":24}'`. The summary.md has no blockrate table, so the numbers below come from `results.json`.

| Hole | Mover | Period | Blocked / 24 | Rate | Touched | Touched but crossed | Round 3 |
|---|---|---|---|---|---|---|---|
| 7 | log | 9.35 s | 12 | **50.0%** | 14 | 2 | 45.8% |
| 8 | root door | 6.67 s | 12 | **50.0%** | 12 | 0 | 45.8% |
| 9 | lantern pendulum | 4.0 s | 8 | **33.3%** | 12 | 4 | 8.3% (5 touched) |

- Target is 38–50%. H7 and H8 are right at the top edge, and H9 is 2 shots short of 38%.
- All 72 shots came to rest. No stuck balls, escapes or issues, and 0 console errors.
- The 12 H8 flags are the unblocked shots (teleport flag via the firefly ring; not issues).

## 7. Lanterns, glow, fireflies (`lanterns/lanterns.json`)
I scanned the Workspace for props named *lantern*, *glow* or *firefly* and checked each for a PointLight, SpotLight or SurfaceLight descendant (Enabled, Brightness > 0, Range > 0).
- 201 matching lights, all enabled. 234 lights in Workspace overall.
- I excluded 12 invisible ForceField placeholders under `HoleN/Decor`, plus the `Lantern Falls` particle emitter. They are old spec markers, not visible props.
- `__Glow`/`ShroomGlow` neon trim sub-meshes on about 40 non-lantern props (cup flags, signs, trees, bridge) have no lights. That is neon only, and I don't count it as unlit lanterns.

| Prop | Count | Lit | Round 3 |
|---|---|---|---|
| lantern_post | 61 | 61 | |
| rail_lantern_crook | 39 | **39** | 28/39 |
| lantern_hook_pair | 16 | **16** | 13/16 |
| tee sign lanterns (tee_sign_h01–h09 LanternCore) | 9 | 9 | |
| glow_shroom_patch | 9 | 9 | 0 lights |
| lantern_string_poles | 8 | 8 | |
| rail_lantern_stake | 6 | **6** | 5/6 |
| cup_lantern_stake | 6 | 6 | |
| firefly_cluster_low | 5 | 5 | 0 lights |
| lantern_large_hanging | 3 | 3 | |
| glowing_mushrooms | 3 | 3 | |
| lantern_knot (H9 + world) | 2 | 2 | |
| glow_root_arch | 2 | 2 | 0 lights |
| firefly_swarm | 2 | 2 | 0 lights |
| firefly_ring_entry / exit, lantern_torii_gate, lantern_span, maple_tree_lanterns, lantern_string, Mover_lantern_pendulum | 7 | 7 | |
| **sky_lantern_1–24** (World.Pieces) | 24 | **0** | |
| **mere_lantern_boat_1–8** (World.Pieces) | 8 | **0** | |
| **old_lantern_tower** (World.Pieces) | 1 | **0** | |
| **lantern_falls_curtain** (World.Pieces) | 1 | **0** | |
| **Total** | **212** | **178** | |

All 34 unlit props are backdrop pieces with Neon glow parts. They are probably fine as a light budget, but the boats on the mere and the tower are close enough to read as "lanterns without light". Owner call.

## 8. Regression
- `clubviz/` (`clubviz.log`, 12 PNGs + `clubpose.json`): metrics identical to round 3.
  - Flip on: shaftOutOfTop = true, shaft vs mount axis 0°, shaft vs handle 180°, head 0.011 above the plane, headToTarget 0.001, club 2.54, both hands.
  - 0 problems.
- `smoke.log`: PASS. One stroke, then Explore and back: strokes 1 → 1, ball moved 0.000. 14 teleport buttons, fall respawn y=26, 3789 parts, 0 errors or warnings.
- `smoke_iphone_17_pro.log`: PASS with the same numbers. The HUD shows the touch hint.

## Owners
- **RobloxDevBot:**
  - (P2) H9 pendulum 33% → 38%+ (retime or widen).
  - (P2) H7/H8 at exactly 50%, the edge of the band.
  - (P3) Fade near-camera movers and large decor just off the sight line (H9 pendulum, H6 tee sign).
  - (P3) Whole hollow-tree shell fade on H8/H9.
  - (P3) `menu_shots.py --vr` should level the simulated head; VR panel position varies between pages.
- **Game Art Bot:**
  - Slope mask has no downhill direction (zigzag is symmetric). Use a one-sided chevron or arrows.
  - H8 rails bloom white.
  - How-to text size on phone/VR.
- **Sound (whoever owns audio):** someone has to listen. Check the cheer/applause level vs plunk, the 0.25 s gap, and the cheer running into the next tee.

## Not tested (honest list)
- **Nobody listened to any audio.** I couldn't capture Studio's audio output (no loopback device), and 5 of the 7 assets couldn't be downloaded for analysis.
- Real headset: VR panel legibility and laser clicks, club feel, comfort. VR was SimulateVR only.
- A real phone (emulator only).
- A counted 9-hole round end to end, and DataStore persistence on a live server (Studio API access is off; I didn't enable it).
- The front-end buttons were driven through `GolfMenuDebug`, not by clicks or taps. I didn't press Play again or Back to menu.
- Which face of the 45° banks (H8 bank1/2, H9 bank1) the player actually sees; I only checked that the texture matches its own face.
- The camera probe covers only the round-3 wall spots (ball 0.6 off a wall), not open-felt or mid-roll camera behaviour. The screenshots were scripted poses, not the live follow camera.
- Multiplayer: other players' hole-outs (toast only), shared server.
