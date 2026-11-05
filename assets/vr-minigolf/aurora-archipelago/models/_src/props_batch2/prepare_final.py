from pathlib import Path
S=Path(__file__).resolve().parent;p=S/'finalize_batch2.py';t=p.read_text();t=t.replace('Static rail minimum .1; mover minimum .05 per explicit batch 2 ruling.', 'Static rail minimum .1; mover minimum .05 per explicit batch 2 ruling; all nearby dressing >=.15.')
t=t.replace('Run gen_batch2.py -> select_batch2.py', 'Run gen_batch2.py -> select_batch2.py (source-conflict list and measured raw preflight evidence are saved in preflight_fitcheck_report.json)')
t=t.replace('Static red/cream requested', 'H10 tall-wall source boxes are fully filled with snow wall bodies, a glacier-ice lip and a white snow cap; all skin footprints match the source, including the S-run rails.\n- Static red/cream requested')
t=t.replace('neon aperture rim and internal tapered spiral ridge','neon aperture rim, internal tapered spiral ridge and a visible exterior side spiral')
p.write_text(t)
