from pathlib import Path
p=Path('out/src/apply_addendum.py')
t=p.read_text().replace("needle=\"\\ndef _sweep_min\"", "needle=\"\\ndef _sweep_min\"")
# Historical one-shot migration is archived to avoid reapplying obsolete initial checks.
p.rename(p.with_suffix('.py.applied'))
import json
s=Path('out/src');m=json.loads((s/'movers_manifest.json').read_text());v=json.loads((s/'export_verification_pass5.json').read_text())
assert len(m['movers'])==len(v)
assert (s/'fitcheck_movers_pass5_validated.txt').read_text().strip().endswith('ALL PASS: YES')
assert (Path('out/previews/cycles/pass5/contact_sheet_pass5.png')).exists()
assert 'Steps 1-2 + first fitcheck: Claude Code claude-opus-5-5; remainder: Codex' in (s/'movers_pass5_summary.md').read_text()
print(len(v),'exports verified; final artifacts present')
