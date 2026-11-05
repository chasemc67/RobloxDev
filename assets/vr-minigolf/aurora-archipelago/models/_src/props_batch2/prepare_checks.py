from pathlib import Path
S=Path(__file__).resolve().parent
b=(S/'fitcheck_batch2.py').read_text();b=b[:b.index("lines=['Aurora")]
(S/'checks.py').write_text(b)
