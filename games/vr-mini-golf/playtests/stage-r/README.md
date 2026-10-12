# Stage r validation

Final evidence:
- `wrist-final/wrist-regression.json`: 23 real simulated-controller pointer actions, MENU/Resume/SCORES x3, switched-hand MENU/SCORES, authoritative Best -2. Both-hand PNGs visually verified.
- `vr-smoke-final/`: all-nine-hole smoke and simulated swing. See results.json and summary.md.
- `xray/h6_wheel_live.json`: independent live-target rays sampled after XRay for 600 frames; both logical and rendered state checked. Ball223 blocked/377 clear; club177 blocked/423 clear; zero misses and false shows.
- `wrist-sim/`: deliberate looks plus glance/swing/stance/head-motion suppression, seed7.
- `desktop-smoke.log`, `iphone-smoke.log`: normal gameplay smoke.
- `h9-sweep/`: 20 random shots, seed118, fuzz-only. No route/planner/par/HIO work.

`wrist-baseline/` and `*-debug.png` preserve diagnosis evidence, not final acceptance. The baseline fixture cleared only the synthetic Best attribute; the final fixture seeds the actual in-memory server record. Initial blank/rotated/cropped bracer debug images were corrected before final screenshots.

The supplied FBX still measured a .32x.20 face. Studio fitted it to .37x.28328125 at the exact 1024/784 canvas aspect. Actual WristFace Top is used, with Top axes corrected, existing .256 runtime rim clearance, and unchanged visibility gates. See `tools/prepare_wrist_bracer.luau` and `logs/stages/e-report.md` for the full report and published version.
