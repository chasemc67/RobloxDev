from pathlib import Path
import datetime
S=Path(__file__).resolve().parent
brief='''# SRV-132 movers pass 2
Apply lead decisions; preserve source files and gameplay pivots. H6 gate visual bottom y=.02. West frame post x=-12, east x=3.86; extended lintel; pocket trim above source rails. H11 walls x=±3, length 2.8; winches shift x=±2.6 to ±3 and z=-21.25 to -23. Slot cheeks south of lift sweep.
Gate cycle: down 0–5.5, rise 5.5–6.15, up 6.15–8.95, sink 8.95–9.6. Lift: rise 5.5–7.5, tilt/release 7.5–7.65, return 7.65–9.15, bottom 9.15–5.5 next cycle. North hinge z=-25, -X tilt, max 4 degrees.
Explicit designed apertures: H6 rail5 pocket/track; H11 gate slot through felt and entrance rail tips; replace static lock felt with moving deck; H11 exit opening through quay_rail20 and clearance at rail6/quay edge. Report raw overlaps and residual geometry. Static felt contact <=.001 accepted; H6 lifted felt gap .0195 is approved exception to .05.
Run full-cycle fine sweep and all non-exempt clearances >=.05; final Cycles OptiX rest/max eye/3/4 previews, one Blender at a time; leave no Blender running.
'''
(S/'brief_pass2.md').write_text(brief)
with (S/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Pass 2 lead decisions applied. '+brief.replace('\n',' ')+'\n')
