import json,shutil
from pathlib import Path
S=Path(__file__).resolve().parent;D=S.parents[2]
P=json.loads((S/'parts.json').read_text());R=json.loads((S/'preflight_fitcheck_report.json').read_text());by={r['id']:r for r in R['parts']};sk=json.loads((S/'skipped.json').read_text())
reasons={
'h09_conch_exit':'Exact source occluder x11.25..13.75,z-69.25..-66.75 lies wholly in green x-16..14,z-70..-56 at y0..4. Raised static shell violates mandatory 8-stud head volume; teleport exit unchanged.',
'h09_coral_spit':'Exact 3x13 deck skirt x+-1.5,z-35..-22 touches rail1 inner face at x1.5,z-22.5..-22: zero clearance. Cannot retain full source skirt and independent .1 rail gate.',
'h10_snow_walls':'Source snow occluder x.5..6.5,z-28..-20 crosses run_rail11 and playable S-run near x2.5,z-20..-24.55. Raised snow mass would cover run felt. Exact tall-wall skins still built.',
'h11_floe_frame':'Exact east post source x3.7..4.3,z-28.3..-27.7 intersects pocket_e23 x3.68..4.18,z-28.97..-27.03 and slide swept volume. Posts cannot be shifted away from exact anchors.',
'h15_lip_ice':'Exact 7x4x1 curtain at z-20 spans z-20.5..-19.5,y-4..0 over reachable basin felt z-20..-34 and touches basin_rail10 at x3.5 (zero gap). Ragged curtain violates head volume and .1 rail gate.',
'h17_crystal_piers':'Exact north pier/deck/rail end joins green_rail15 at z-42, x-.5..-1.5; source shared joint gives overlap/zero independent rail clearance. Full exact 9-stud deck and rail lengths cannot meet .1 gate. Source blockout kept for context.',
'h17_ice_bridge':'Exact bridge_rail11 intersects green_rail16 at z-42 and x8.25; shared endpoints have zero independent rail clearance. Exact source deck/rails cannot meet .1 gate. Source blockout kept for context.',
'h17_span_lamp':'Exact static base [-2.4,0,-15] is inside rim felt x-6..8,z-16..-12. Required 2.4-high lamp violates 8-stud head volume. Source pivot cannot move.'}
(S/'raw_parts.json').write_text(json.dumps(P));(S/'preflight_fitcheck_report.json').write_text(json.dumps(R,indent=2))
for p in P:
 if p['id'] in reasons:
  r=by[p['id']];assert r['status']=='FAIL';sk.append(dict(id=p['id'],hole=p['hole'],reason=reasons[p['id']],evidence=r))
P=[p for p in P if p['id'] not in reasons];(S/'parts.json').write_text(json.dumps(P));(S/'skipped.json').write_text(json.dumps(sk,indent=2))
back=S/'_backup';back.mkdir(exist_ok=True)
for p in [D/'models/README.md']:
 if p.exists() and not (back/p.name).exists():shutil.copy2(p,back/p.name)
print('Selected',len(P),'built pieces;',len(sk),'individual skips')
