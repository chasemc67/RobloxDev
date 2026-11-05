"""Derive fitcheck_pass5.py from fitcheck_pass4.py (pass-4 logic unchanged) + pass-5 additions in fitcheck_p5_parts.py."""
from pathlib import Path
SRC=Path(__file__).resolve().parent
s=(SRC/'fitcheck_pass4.py').read_text()
def rep(a,b):
    global s
    assert a in s,a
    s=s.replace(a,b,1)
rep('"""SRV-132 pass 4 fitcheck against in/holes.json (p8) incl. approved collision_cuts.','"""Sugarloaf movers pass 5 fitcheck against in/holes.json (p9b) incl. approved collision_cuts (derived from fitcheck_pass4).')
rep("Sweeps: rotors 0.5 deg over 360; bucket 0.25 deg over +-9 plus","Sweeps: rotors 0.5 deg over 360; bucket 0.05 deg over +-9 plus")
rep("out=[(None,0.0,float(a)) for a in np.arange(-9,9.0001,.25)]","out=[(None,0.0,float(a)) for a in np.arange(-9,9.00001,.05)]")
rep("def threshold(e,P):\n    if P['kind']=='static prop':return .15","def threshold(e,P):\n    if P['kind']=='static prop':return .15\n    if e['id']=='h07_island_respawn_stone' and P['kind']=='rail/wall':return .15")
rep("        if status is None and not e['moving'] and P['kind']=='anchor envelope':status='INFO (unbuilt landmark envelope)'",
"""        if status is None and not e['moving'] and P['kind']=='anchor envelope':status='INFO (unbuilt landmark envelope)'
        if status is None and e['moving'] and P['kind']=='static prop' and name.startswith('h17_hour_stone_'):
            sid=name.rsplit('_',1)[0];se=next(x for x in REG if x['id']==sid);dg=h17_design_gaps()[se['hour']]['gap']
            b['holes_json_design_gap']=dg
            if not se['collidable'] and g>=-TOL and g>=dg-1e-4:status='HOLES.JSON INHERITED (decorative stone, collision off; exact holes.json box vs blocker sweep gap %.4f)'%dg""")
for a,b in (("fitcheck_movers_pass4_","fitcheck_movers_pass5_"),("fitcheck_results_pass4.json","fitcheck_results_pass5.json"),("fitcheck_pass4: ALL PASS","fitcheck_pass5: ALL PASS")):s=s.replace(a,b)
rep("lines=['SRV-132 PASS 4 FITCHECK vs in/holes.json (p8) incl. approved collision_cuts. Generated '","lines=['SUGARLOAF MOVERS PASS 5 FITCHECK vs in/holes.json (p9b) incl. approved collision_cuts. Generated '")
rep("'Sweeps: rotors 0.5 deg over 360 deg (720 states); ore bucket 0.25 deg over -9..+9 plus period sampling dt .01 s;","'Sweeps: rotors 0.5 deg over 360 deg (720 states); ore bucket (visual + foot collision) 0.05 deg over -9..+9 (361 states) plus period sampling dt .01 s;")
rep("H9 vanes vs felt >=.02 (holes.json windpump visual \"clearance .02\").',",
"H9 VISUAL vanes vs felt >=.02 (art-only tip, holes.json p9b windpump visual). Design override (Game Art Bot): .06 accepted for the H9/H14 BLOCKING collision surfaces (both also clear the .05 general rule).',\n    'Decorative hour stones (collision OFF) vs the arm sweep: HOLES.JSON INHERITED when the visual gap equals the exact holes.json box-vs-blocker gap (both meshes verified inside their exact boxes).',")
a=s.index("    vp=parts_rest('h09_windpump_vanes')");b=s.index("    # Pass 4b: arms")
s=s[:a]+"    cover_p5(rep,parts_rest,mp)\n"+s[b:]
a=s.index("    pt=next(q for q in HOLES[6]['player_teleport_points'] if q['id']=='bridge2_exit')");b=s.index("    rep['dam_crest_parapets']")
s=s[:a]+"    cover_p5_static(rep,boxcov)\n"+s[b:]
rep("    pairs=moving_pairs();cov=coverage()","    pairs=moving_pairs();cov=coverage();spec=spec_checks(results)")
rep("    lines.append('\\nOVERALL MIN (all PASS pairs) '+json.dumps(overall[1]))","""    lines.append('\\nPASS-5 SPEC MEASUREMENTS')
    for k,v in spec.items():
        lines.append(f"{v['status']} {k} "+json.dumps(v,default=float));ok&=v['status']=='PASS'
    lines.append('\\nOVERALL MIN (all PASS pairs) '+json.dumps(overall[1]))""")
rep("moving_pairs={f'{a}/{c}':b for (a,c),b in pairs.items()},coverage=cov,","moving_pairs={f'{a}/{c}':b for (a,c),b in pairs.items()},coverage=cov,pass5_spec=spec,")
# pass-5 helpers inserted before main()
rep("def main():","# ================================================================ pass 5 additions\n"+(SRC/'fitcheck_p5_parts.py').read_text()+"\ndef main():")
(SRC/'fitcheck_pass5.py').write_text(s)
print('fitcheck_pass5.py written')
