from pathlib import Path
S=Path(__file__).resolve().parent
# Build/export and render stages can be re-run independently without touching exports.
p=S/'build_batch2.py';t=p.read_text().replace("sc.cycles.samples=16","sc.cycles.samples=12")
t=t.replace("# Exact source blockout context", "if '--export-only' in sys.argv:\n print('DONE_EXPORT',flush=True);raise SystemExit(0)\n# Exact source blockout context")
p.write_text(t)
