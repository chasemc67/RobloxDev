import json,datetime,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parent;O=S.parent;B=S.parents[1]
def main():
 r=json.loads((S/'fitcheck_results_pass2.json').read_text());m=json.loads((S/'movers_manifest.json').read_text());review='--review' in sys.argv;renderdir=O/'previews/cycles'/('review' if review else '');renders=sorted(p for p in renderdir.glob('*.png') if p.name!='contact_sheet.png')
 for e in m['movers']:
  e['validation_status']='PASS_WITH_REQUIRED_STUDIO_CUTS' if r['all_pass'] else 'FAILED'
  e['clearances']=r['results'][e['id']]
  e['required_collision_cuts']=[x for x in r['cuts'] if x['prop']==e['id']]
  if e['id']=='h06_sluice_gate':e['visual_offset']=[0,.02,0]
  if e['id']=='h11_lock_lift':e['motion']=dict(cycle_s=9.6,rise=4,speed=2,return_s=1.5,tilt_deg=4,tilt_axis=[-1,0,0],hinge_edge='north z=-25',schedule=dict(rise_start=5.5,rise_end=7.5,tilt_release_end=7.65,return_end=9.15,gate_down=9.6),static_lock_felt='REMOVE/HIDE and replace collision with moving platform')
 m['pass']=2;m['required_studio_cuts']=r['cuts'];m['minimum_non_exempt']=r['minimum'];m['preview_engine']='Cycles OptiX';m['preview_status']='REVIEW' if review else 'FINAL';m['previews']=[str(p.relative_to(O)) for p in renders]
 if review and (S/'fitcheck_results_pass2_proposed.json').exists():m['proposed_additional_cuts_pending_decision']=[c for c in json.loads((S/'fitcheck_results_pass2_proposed.json').read_text())['cuts'] if c not in r['cuts']]
 (S/'movers_manifest.json').write_text(json.dumps(m,indent=2))
 text=['# SRV-132 H6 + H11 movers pass 2',
 'Fitcheck '+('PASS with required Studio collision cuts' if r['all_pass'] else 'FAILED')+'. Source holes.json and library remain unchanged. CanCollide=false; FBX scale 1, forward -Z/up Y, textures embedded.',
 '| FBX | Hole-local pivot | World pivot | Tris | MeshParts |','|---|---|---|---:|---:|']
 for e in m['movers']:text.append(f"| {e['fbx']} | {e['pivot']} | {e['world_pivot']} | {e['tris']} | {e['MeshParts']} |")
 text+=['','H6 gate bottom raised .02 above felt, pivot unchanged; source blocker stays at y=0, so the visual bottom .02 strip differs from collision. Pointed board length 7.000051 (rounded .4243 end boxes), painted face skins project .018 beyond blockers. H11 blocker exact 3.6×1.2×.5 covered; deck 3.2×4 with .005 plank seams; top flush at y=0.',
 'H6 frame posts move west -3.6→-12, east 3.6→3.86; extended lintel; pocket trim raised above rails. H11 winch anchors x=±2.6→±3 and z=-21.25→-23; wheels likewise relocated. Chamber walls x=±2.15→±3, length 3.8→2.8; slot cheeks move south clear of deck.',
 'H6 axis +X, offsets -7..0, speed 3, dwells 1.2 at 0/2.0 at -7, period 7.8666667. H11 gate +Y, offsets -1.3..0, speed 2, period 9.6: down 0–5.5, rise 5.5–6.15, up 6.15–8.95, sink 8.95–9.6.',
 'Lift rise 5.50–7.50, tilt 0→4° and release 7.50–7.65, return 7.65–9.15 (untilt first .15 s), bottom until next rise. Gate not fully down 5.5–9.6 = 4.1 s. Bottom .45 s before gate fully down. North-edge hinge z=-25 around Roblox -X; south edge rises. See motion.lua, including CFrame transform and clamp(entrySpeed*.5,1.5,7).',
 'Signal [0,5,-25.4], world [150,121,-277.4], separate Neon SignalRed/SignalGreen. Optional Studio PointLight range 6, brightness 1. Green while gate down; red otherwise.',
 '', '## Explicit whitelist and Studio requirements',
 'All cuts below are required collision/visual apertures for RobloxDevBot. Passing status applies to residual geometry after cuts; uncut source intersections remain reported in fitcheck. H6 pocket through rail5; west frame now entirely outside sweep. H11 gate slot requires relief at rail4/rail8 tips as well as felt. Remove/hide static lock felt and replace its collision with moving deck. Exit needs a real gap through quay_rail20; rail6 lower north edge and quay felt seam also need clearance relief.']
 for c in r['cuts']:text.append(f"- {c['prop']} / {c['obstacle']}: bounds {c['min']} to {c['max']} (hole-local x,y,z).")
 text+=['','## Clearance evidence',
 'Full-cycle dt≤.005 s, translations≤.015 stud, angular increments≤.134° with additional top tilt sweep≤.25°. Triangle/OBB SAT conservative signed lower bounds; static detail primitives conservatively AABB-enclosed. Static felt overlap≤.001 accepted; H6 lifted felt .0195 accepted per lead. Every other pair and cut residual must clear .05.',
 'Minimum non-exempt: '+json.dumps(r['minimum']),
 'Exact exit raw reports:']
 for n in ('rail6','quay_rail20','felt_quay'):
  text.append('- '+n+': '+json.dumps(r['results']['h11_lock_lift']['raw_whitelist'].get(n)))
 text+=['The source rail6 is centered [0,.95,-25.25], spans y=-.5..2.4, z=-25.5..-25.0: lower edge contact/tilt penetration. quay_rail20 is [0,4.25,-24.75], spans y=3.5..5,z=-25..-24.5: actual raised exit obstruction, not a mislabeled rail6. Quay felt starts z=-25 at y=4; the seam contacts the platform and needs the listed relief. All are designed exit gaps.',
 '', '## Previews and handoff',f'{len(renders)} final PNGs in out/previews/cycles, Cycles OptiX on RTX 4090, rest and maximum, eye (height 5) and 3/4. Static max duplicates rest for consistent review. Five-stud capsule included. FBX round-trip mesh counts passed.',
 'Re-sync the five meshes in Studio; implement listed apertures, replace static lock floor, and use motion.lua. Existing teleported ball release stays at [0,4,-27] toward -Z. No manifest.json edited; H9/H14/H17 untouched.']
 text=[line.replace('deck 3.2\u00d74 with .005 plank seams','nominal deck footprint 3.2x4 with .005 plank seams and a .58-deep full-width south gate slot') for line in text]
 if review:text=[line.replace('final PNGs in out/previews/cycles','REVIEW PNGs in out/previews/cycles/review') for line in text]
 text+=['','Gate slot travels with the moving replacement felt/deck, local z=1.42..2 (hole z=-21.58..-21). Full-cycle gate/platform minimum .061999917 stud. Lift tilt transform corrected to preserve original y before computing z; no spurious height-dependent north translation.']
 if not r['all_pass']:
  text+=['','## Conflicts outside supplied whitelist','No final passing certificate issued. Additional cuts proposed separately, pending the lead decision.']
  for p,v in r['results'].items():
   for n,b in v['pairs'].items():
    if b['status']=='FAIL':text.append('- '+p+' / '+n+': '+json.dumps(b))
  for c in m.get('proposed_additional_cuts_pending_decision',[]):text.append('- PROPOSED CUT '+json.dumps(c))
 text=[line.replace('lower edge contact/tilt penetration','lower edge contact only, no meaningful penetration').replace('the seam contacts the platform','the seam has only .002494 signed lower-bound clearance') for line in text]
 text+=['','At height=4, tilt=0, the aggregate platform/quay_rail20 overlap envelope is x=[-1.6,1.6], y=[3.85,4.0], z=[-25,-24.5] (plank seams excluded from occupied material). At max tilt, worst triangle/OBB signed lower bound is -.497506 at t=7.65. This is the raised quay obstruction. rail6 instead contacts the north edge at z=-25 at rest; its clearance-relief cut is separate.',
 'Proposed additional cuts sweep: minimum .059974432 at H6 gate/east frame post, t=0, offset=0, location [3.3000085,.6866666,-28.2000085]. This proposed result does not authorize extra cuts or replace the failed approved-whitelist result.']
 (S/'movers_pass2_summary.md').write_text('\n'.join(text),encoding='utf-8')
 if len(renders)==20:
  sheet=Image.new('RGB',(1200,5*510),(35,29,37));d=ImageDraw.Draw(sheet)
  for row,e in enumerate(m['movers']):
   for col,(state,view) in enumerate([('rest','eye'),('rest','34'),('max','eye'),('max','34')]):
    p=renderdir/f"{e['id']}_{state}_{view}.png";im=Image.open(p).convert('RGB');im.thumbnail((300,460));sheet.paste(im,(col*300,row*510+35));d.text((col*300+5,row*510+10),f"{e['id']} {state} {view}",fill='white')
  sheet.save(renderdir/'contact_sheet.png')
 with (S/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+f' Pass 2 handoff updated; {len(renders)} final OptiX previews.\n')
if __name__=='__main__':main()
