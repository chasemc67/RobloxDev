Stage aa, VR Mini Golf. The split is live (see places.json and z-notes.md). Sync one place at a time with run_playtests.py push. Keep only one place open at a time, and reconnect the MCP each time. Do these tasks in order:
1. Real UI art: the real loading cards (ui/loading/) and menu art (ui/menu/) have now been copied to assets/vr-mini-golf/ui/, so replace the placeholders, upload them, and update the Config IDs.
Next stage after split (z):
- P1 Sugarloaf cups H2,H4,H8,H9,H12,H13,H17: lower ground ~0.6 under every cup; cup-drop smoke for all 18 holes.
- H7 block rate into 38-50%.
- LG: remove hidden stone dup in H9 backing; ground floating H8 stone prop (1.66 up); recolor old cream #DDD3BE plain rails at H8.
- Sugarloaf Lighting preset (Game Art Bot): ClockTime 16.3 bearing 277 elev 25; Brightness 2.2, Ambient #6B4A52, OutdoorAmbient #B07A6A, ColorShift_Top #FFC890, EnvDiffuse 0.6, EnvSpec 0.4. Atmosphere Density .38 Offset .15 Color #FFB98A Decay #C2607A Glare .6 Haze 2.2. Sky plain/none, SunAngularSize 18. ColorCorrection Tint #FFE9D6 Sat .12 Contrast .08. SunRays .12/.6. Bloom .6/24/.95.
- Round 9 report: /workspace/writerbot/vr-minigolf-post/playtest-bot/round9/round9-findings-v235.md
- Import Sugarloaf pass 6 kit (scale 1, manifest.json instances, Studio-part collision, Neon per manifest, gondola motion per manifest) into Sugarloaf place; cup clearance confirmed (_src/cupclear_pass6.txt). Copy /workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/models to Mini first.
- Chase VR feedback 1:10 PM:
  * Wrist tracker/watch only on left hand -> works on both hands (either wrist).
  * Remove menu & score buttons from wrist display entirely (unclickable).
  * Don't open menu by clicking a thumbstick. Scorecard button opens scorecard; scorecard UI has a button to open settings/menu.
  * Club head offset setting: great. Remove thumbstick moving head on ground; thumbstick LEFT/RIGHT now rotates club head yaw relative to shaft (saved setting).
  * Club head stays parallel to ground only while touching/near ground; when lifted, rigid normal club orientation (blend smoothly).
Chase's VR items go into shared src/, which is pushed to all three places. In the lobby, check that default VR controls work.
Sugarloaf kit: it's now in assets/vr-mini-golf/sugarloaf-canyon/models/ (pass 6). Import it into the Sugarloaf place.
Tests: cup-drop on all 18 Sugarloaf holes must pass, plus a stuck-ball sweep on Sugarloaf, the Lantern Grove 9/9 regression, lobby smoke, and 0 console errors. Publish all three places, verify each in Version History, write aa-notes.md, and commit. If Studio hangs on quit after a publish, force-quit it.
End your output with: RESULT=PASS|FAIL LOBBY_VERSION=<n> LG=<v> SC=<v>


UPDATE: wrist card and scorecard gear are already live (LG v7, SC v5, Lobby v244, commit d459940). Do everything else above. Also remove the left-stick-click menu entirely (Chase: no thumbstick-click menu; menu only via scorecard gear). Also swap in the real ui/menu and ui/loading art. Also import lobby portals from assets/vr-mini-golf/lobby/boardwalk/models (crown Glow_Tips Neon #9FE6F2, low candy glow, lantern CastShadow off). Only one Studio place open at a time. End line: RESULT=… LOBBY_VERSION= LG= SC=
