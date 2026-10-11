# Hole-out audio (v116), measured 2026-10-11

Source: HUD.holeOutAudio (client). Sounds are pooled in PlayerScripts.GolfClient.HUD.Sfx_*, SoundGroup SoundService.SFX (Volume = SFX setting, default 0.8). Effective level = Sound.Volume x 0.8.
Timeline: Remotes.HoleComplete fired from the Server DM for each result, client sampled IsPlaying every frame (os.clock from event arrival).

| Result | Sounds (SoundId) | Volume (eff.) | PlaybackSpeed | TimeLength | Start after plunk | Stops at | Overlap with plunk |
|---|---|---|---|---|---|---|---|
| all except max | CupPlunk 9117183624 | 0.50 (0.40) | 0.9 | 0.467 s (0.519 s at 0.9x) | 0 | 0.53-0.55 s | - |
| hole-in-one (1 on par 2) | CheerBig 125361506894319 + Applause 7367718809 | 0.70 (0.56) + 0.45 (0.36) | 1.0 | 7.11 s / 6.74 s | 0.27-0.28 s | fade from 4.0 s, stop 5.47-5.50 s | 0.25 s |
| eagle (2 on par 4) | same as hole-in-one | same | 1.0 | same | 0.27 s | 5.47 s | 0.25 s |
| birdie (2 on par 3) | Birdie 105154404054447 | 0.65 (0.52) | 1.0 | 3.70 s | 0.27 s | 3.98 s | 0.25 s |
| par (2 on par 2) | Par 72098222084567 | 0.55 (0.44) | 1.0 | 4.00 s | 0.27 s | 4.25 s | 0.25 s |
| bogey (3 on par 2) | Bogey 9114762131 | 0.60 (0.48) | 1.0 | 2.90 s | 0.27 s | 3.15 s | 0.25 s |
| double bogey+ (4 on par 2) | Aww 77211275419736 | 0.60 (0.48) | 1.0 | 1.72 s | 0.27 s | 1.97 s | 0.25 s |
| max strokes (8, maxed) | Aww only, no plunk | 0.60 (0.48) | 1.0 | 1.72 s | 0.02 s (no delay) | 1.72 s | - |

Config.ReactionDelay = 0.25 (measured 0.267-0.282 s, frame quantised), ReactionFadeAfter = 4 (1.2 s Sine tween to 0, then Stop).
HoleTransitionTime = 3.5 s, so CheerBig/Applause play ~2 s into the fade/next tee.
The plunk fires when the server's HoleComplete remote arrives, not on the ball's physical drop (network latency adds to it in a live server).

## File analysis (peak / RMS / clipping)
Only the two Roblox-owned ProSoundEffects assets download without a login (assetdelivery). The other five need an authenticated
Roblox session to download; not analysed (not feasible without using Chase's cookie, which I didn't). No loopback audio device
on the Mini (only "Mac mini Speakers"), so recording Studio's output wasn't feasible either.

| Sound | sr / ch | Duration | Peak | RMS | Max 50 ms RMS | Clipped samples | Crest |
|---|---|---|---|---|---|---|---|
| CupPlunk | 48 kHz mono | 0.467 s | 0.744 (-2.6 dBFS) | -21.2 dBFS | -11.5 dBFS | 0 | 18.6 dB |
| Bogey | 48 kHz mono | 2.900 s | 0.511 (-5.8 dBFS) | -29.1 dBFS | -19.3 dBFS | 0 | 23.2 dB |

Nobody has listened to any of this. Levels, the 0.25 s gap and the mix balance are unverified by ear.
