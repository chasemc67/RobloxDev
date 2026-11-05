# Pass 8 brief (Playtest round 2 + Game Art Bot lighting direction). Work in models/.
FIRST read _src/pass8_progress.md (resume if it exists), _src/pass7b_progress.md, _src/pass7_summary.md, _src/brief_pass7.md (rules), dressing_world.py, fitcheck.py, fitcheck_pass7b.py, manifest.json.
Rules: same as brief_pass7.md (no edits to holes.json/world/fly files; kill only your own PIDs; nohup long jobs and WAIT for them to finish before ending your turn; checkpoint _src/pass8_progress.md each step + one line per step in _src/PROGRESS.md prefixed "pass8"). Snapshot manifest to _src/manifest_before_pass8.json.
If pass 7b is unfinished (no _src/pass7b_summary.md, or tee renders/contact sheet/README not updated), finish it first.
Tasks:
1) H9: reuse the existing lantern prop (paper lantern). Add 3 hanging paper lanterns evenly spaced over the middle of the green and the corridor, ~8 studs above the felt (bottom of lantern ~8 studs above local felt height). A hanging-chain/cord variant (new prop, <20k tris) is OK if needed to attach to canopy. Add manifest lights[] entries for each: PointLight, Color3 (255,169,87) (amber ~2700K), Range 16, sensible Brightness, position at lantern centre.
2) H7 lower tiers and H8 hollow: small rail lanterns about every 10 studs along BOTH rails (same amber; lights[] entries, Range ~10). Must stay off the putting surface/line, not clip rails (exact geometry), respect plant/tall-prop rules and budgets.
3) H8: noticeably raise emissive strength of glowing mushrooms and fireflies (materials + exported textures/emission as applicable) and raise their lights[] Brightness accordingly.
4) Add fitcheck rules: hanging lanterns height above felt (7-9 studs) and inside the H9 green/corridor footprint; rail lanterns no rail clip, not over felt, spacing ~10 (8-12); every new lantern has a lights[] entry with the amber colour. Negative tests. Run fitcheck: must be ALL PASS; save _src/fitcheck_pass8_validated.txt.
5) Re-render H7, H8, H9 tee views (32 spp) + rebuild tee_contact_sheet.png (and contact_sheet.png if props changed). Look at the renders: H9 should read as lantern-lit, H8 magical, H7 lower tiers lit.
6) Update manifest.json, README.md. Write _src/pass8_summary.md: exactly what RobloxDevBot must pull in (changed/new FBX paths, texture paths, lights[] entries with positions/colour/range/brightness, emissive changes), fitcheck count, open issues.
Then add "pass8 DONE" line to PROGRESS.md.

## Pass 8 addendum (18:46 PT) — holes.json Round 7 is FINAL (Game Art Bot). Do this after the steps above (resume via pass8_progress.md):
- Read Round 7 details in props.md and playtest-log.md (find them under /workspace/RobloxDev games/ or assets/ for vr-minigolf/lantern-grove).
- Rebuild matching meshes: H7 log 6 studs long with pointed ends; H8 root door 3.6 studs long; H9 pendulum bob 1.6x1.8x1.6, rotated 30 deg. Keep pivots exactly per props.md.
- H9 hanging decoration lanterns: use positions from props.md if they differ (keep lights[] in sync).
- Re-place nearby dressing against the final holes.json, fitcheck ALL PASS (Round-7 drift fails must be resolved), export FBX, re-render H7/H8/H9 tee + contact sheet, note all of this in pass8_summary.md.
