#!/usr/bin/env python3
"""Print a markdown stats table from tools/out/sim-<tag>.json.   python3 tools/summarize.py p1 [p2 ...]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def table(tag):
    d = json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))
    rows = ["| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tp = tg = ta = 0
    for h in d["holes"]:
        if "stats" not in h:
            continue
        g, a = h["stats"]["good"], h["stats"]["average"]
        hs = h.get("hio_search") or {}
        hits = f"{hs.get('hits', 0)}/{hs.get('shots', 0)}" if hs.get("hits") else (
            f"refine {hs.get('refine_hits', 0)}/{hs.get('refine_shots', 0)}" if hs.get("refined") else "-")
        tp += h["par"]; tg += g["avg"]; ta += a["avg"]
        rows.append(f"| {h['id'][1:].lstrip('0')} | {h['name']} | {h['par']} | {g['avg']:.2f} | {g['hio'] * 100:.1f}% | "
                    f"{g['capped'] * 100:.1f}% | {a['avg']:.2f} | {a['hio'] * 100:.1f}% | {a['capped'] * 100:.1f}% | "
                    f"{a['hazard_per_play']:.2f} | {hits} | {', '.join(h.get('flags', [])) or 'ok'} |")
    rows.append(f"| | **Total** | **{tp}** | **{tg:.2f}** | | | **{ta:.2f}** | | | | | |")
    return "\n".join(rows)


if __name__ == "__main__":
    for t in sys.argv[1:]:
        print(f"### {t}\n" + table(t) + "\n")
