# Pass 9 progress (H9 pendulum plinth)
- step 0 (12:3x PT): started; manifest snapshot -> _src/manifest_before_pass9.json; no prior pass9 progress.
- step 1: plinth added to props_moving.lantern_pendulum (blocker 2 from holes.json, Iron); building pendulum + root beam (/tmp/p9/build1.log)
- step 2: build OK (pendulum 1820 tris, root beam at hinge x 21.2); fitcheck_pass9.py + union-blocker updates in fitcheck.py/fitcheck_pass6.py; fitcheck run 1 (/tmp/p9/fc1.log)
- step 3: fitcheck 1: all pass-9 checks PASS; 1 FAIL = root beam legs on a rail (beam followed the Round-8 hinge to x 21.2) -> beam body offset +0.8 to its anchor x 22, bracket stays at hinge; rebuilt
- step 4: fitcheck ALL PASS (218) -> fitcheck_pass9_validated.txt; rendering H9 tee (/tmp/p9/asm1.log)
- step 5: H9 tee re-rendered (32 spp, pendulum + plinth in view at right); pass9_readme.md; README + tee_contact_sheet rebuilt
- step 6 (12:38 PT): pass9_summary.md written. PASS 9 DONE.
