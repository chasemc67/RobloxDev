#!/usr/bin/env python3
"""Print a markdown stats table from tools/out/sim-<tag>.json.   python3 tools/summarize.py p1 [p2 ...]
Adapted from Lantern Grove: adds the skill gap, par-or-better rates and escapes/timeouts (traps) per hole."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def table(tag):
    d = json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))
    rows = ["| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | "
            "Escapes / timeouts | HIO-search hits | Flags |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tp = tg = ta = 0
    for h in d["holes"]:
        if "stats" not in h:
            continue
        g, a = h["stats"]["good"], h["stats"]["average"]
        par = h["par"]
        pg, pa = sum(g["dist"][:par]) / g["n"], sum(a["dist"][:par]) / a["n"]
        hs = h.get("hio_search") or {}
        hits = f"{hs.get('hits', 0)}/{hs.get('shots', 0)}" if hs.get("hits") else (
            f"refine {hs.get('refine_hits', 0)}/{hs.get('refine_shots', 0)}" if hs.get("refined") else "-")
        tp += par; tg += g["avg"]; ta += a["avg"]
        esc = g["escapes"] + a["escapes"] + h.get("fuzz_escapes", 0)
        to = g["timeouts"] + a["timeouts"]
        rows.append(f"| {h['id'][1:].lstrip('0')} | {h['name']} | {par} | {g['avg']:.2f} | {g['hio'] * 100:.1f}% | {pg * 100:.0f}% | "
                    f"{g['capped'] * 100:.1f}% | {a['avg']:.2f} | {a['hio'] * 100:.1f}% | {pa * 100:.0f}% | {a['capped'] * 100:.1f}% | "
                    f"{a['avg'] - g['avg']:+.2f} | {a['hazard_per_play']:.2f} | {esc} / {to} | {hits} | {', '.join(h.get('flags', [])) or 'ok'} |")
    rows.append(f"| | **Total** | **{tp}** | **{tg:.2f}** | | | | **{ta:.2f}** | | | | | | | | |")
    return "\n".join(rows)


def targets(tag):
    """per-hole check against the course targets (Lantern Grove bands)"""
    d = json.load(open(os.path.join(HERE, "out", f"sim-{tag}.json")))
    out = []
    for h in d["holes"]:
        if "stats" not in h:
            continue
        g, a = h["stats"]["good"], h["stats"]["average"]
        par = h["par"]
        hs = h.get("hio_search") or {}
        fails = []
        if not (0.002 <= g["hio"] <= 0.10):
            fails.append(f"good HIO {g['hio'] * 100:.1f}%")
        if not hs.get("line"):
            fails.append("no ace line")
        if not (par - 0.7 <= g["avg"] <= par + 1.0):
            fails.append(f"good avg {g['avg']:.2f} vs [{par - 0.7:.1f},{par + 1:.1f}]")
        if a["avg"] - g["avg"] < 0.3:
            fails.append(f"gap {a['avg'] - g['avg']:+.2f}")
        if a["avg"] > par + 1.5:
            fails.append(f"avg avg {a['avg']:.2f} > {par + 1.5:.1f}")
        if g["capped"] > 0.01 or a["capped"] > 0.01:
            fails.append(f"capped {g['capped'] * 100:.1f}/{a['capped'] * 100:.1f}%")
        if g["escapes"] + a["escapes"] + h.get("fuzz_escapes", 0):
            fails.append("escapes")
        if g["timeouts"] + a["timeouts"]:
            fails.append(f"timeouts {g['timeouts'] + a['timeouts']}")
        if any(s == "ERROR" for s, _ in h.get("issues", [])):
            fails.append("validator")
        out.append(f"H{int(h['id'][1:])} {h['name']}: " + ("OK" if not fails else "; ".join(fails)))
    return "\n".join(out)


if __name__ == "__main__":
    for t in sys.argv[1:]:
        print(f"### {t}\n" + table(t) + "\n")
        print(targets(t) + "\n")
