Stage v: VR Mini Golf fix pass from Playtest Bot round 7 (findings in games/vr-mini-golf/logs/stages/round7-findings-v202.md, or playtest-bot/round7/ if present). Studio on this Mini currently has a local playtest-v202.rbxl open; close it without saving and open the live place 87725688219952 (MetavrseBuilder) in Edit mode. Confirm via Studio MCP before editing.
Fix (RobloxDevBot items only):
1. Guard ClubSetup and WristPoseLog DataStore calls like PersonalBest (pcall + no-op when DataStore unavailable/unpublished).
2+3. H8 root door: keep >=0.15 stud clearance to the alcove wall and stop it crushing/flinging a parked ball (door should not push a ball faster than ~2 studs/s or pin it; nudge it out gently). Keep door block rate in 38-50%.
4. VR club-head outline: show only at rest while aiming, hide while rolling and after sinking.
5/6. Outline fade-out on putt and fade-in on aim: make both <=0.1 s.
9. Course card: hide or disable "Restart round" before the first stroke.
Art (Game Art Bot): H9 rail wood colour #7A4E32 with Reflectance 0 so it reads darker than the felt under the H9 lantern; every bank face on Lantern Grove = 0.78x the felt colour (same hue, darker).
Test: re-run the relevant checks plus quick 20-shot random sweeps on H8 (incl. parked balls in the door path), zero console errors. Then File > Save to Roblox and File > Publish to Roblox, and verify in Version History that live is above v202; write LIVE_VERSION=vNNN. Then File > Save to File As ~/src/RobloxDev/games/vr-mini-golf/playtest-vNNN.rbxl and leave Studio open on the live place in Edit mode.
Append progress to v-notes.md, end with RESULT=PASS/FAIL and a summary. Commit and push (run ~/bin/unlock-keychain.sh first).
