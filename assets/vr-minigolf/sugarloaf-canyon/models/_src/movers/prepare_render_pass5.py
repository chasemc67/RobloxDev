from pathlib import Path
s=Path('out/src');t=(s/'render_pc.py').read_text().replace('fitcheck_movers_pass4_validated','fitcheck_movers_pass5_validated')
t=t.replace("        if e['hole']!=hi:continue", "        if e['hole']!=hi or e.get('collision_only'):continue")
(s/'render_pc_pass5.py').write_text(t)
