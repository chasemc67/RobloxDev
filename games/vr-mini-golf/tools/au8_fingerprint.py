"""Per-part FNV-1a fingerprints of an inventory json (au7 format), to compare with the
Luau fingerprint in au8 (same line format). Usage: au8_fingerprint.py inventory.json [studio_hashes.json]"""
import json, sys
def f(x): return "%.4f" % x
def line(p):
    cp = p.get("customPhysics")
    return "|".join([p["path"], p["class"], ",".join(map(f, p["cf"])), ",".join(map(f, p["size"])),
        "1" if p["collide"] else "0", "1" if p["query"] else "0", "1" if p["touch"] else "0",
        "1" if p["anchored"] else "0", p["group"], p["material"], f(p["transparency"]),
        ",".join(map(f, p["physics"])) if "physics" in p else "-", ",".join(map(f, cp)) if cp else "nil", ",".join(sorted(p["tags"]))])
def fnv(s):
    h = 2166136261
    for b in s.encode():
        h = ((h ^ b) * 16777619) & 0xffffffff
    return "%08x" % h
inv = json.load(open(sys.argv[1]))["parts"]
def gp(p): return p["collide"] or p["query"] or p["touch"]
allh = sorted(fnv(line(p)) for p in inv); gh = sorted(fnv(line(p)) for p in inv if gp(p))
if len(sys.argv) > 2:
    s = json.load(open(sys.argv[2]))
    print("all", len(allh), len(s["all"]), allh == sorted(s["all"]))
    print("gameplay", len(gh), len(s["gameplay"]), gh == sorted(s["gameplay"]))
    from collections import Counter
    d1 = Counter(allh) - Counter(s["all"]); d2 = Counter(s["all"]) - Counter(allh)
    print("only_inv", len(d1), "only_studio", len(d2))
    for p in inv:
        if fnv(line(p)) in d1: print("INV", line(p))
else:
    print(len(allh), len(gh)); print(line(inv[0]), fnv(line(inv[0])))
print("digest_all", fnv("".join(allh)), "digest_gameplay", fnv("".join(gh)))
from collections import defaultdict
grp = defaultdict(list)
for p in inv: grp[".".join(p["path"].split(".")[:3])].append(fnv(line(p)))
print(json.dumps({k: [len(v), fnv("".join(sorted(v)))] for k, v in sorted(grp.items())}))
