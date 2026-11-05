"""Pass 6: choose the top panel of every cliff/slot stack in the pre-pass-6 layout and map it to its rounded-top
(cliffT_/slotT_) variant -> _cache/pass6_cliffs.json (applied by finalize_pass6_ext.py).   python _src/sc_cliffs_layout_pass6.py
"""
import json, re
from pathlib import Path
SRC = Path(__file__).resolve().parent
lay = json.loads((SRC / "backup_pass6" / "layout.json").read_text())
stacks = {}
for i in lay["instances"]:
    if i["piece"].startswith(("cliff_w24", "slot_w24")):
        m = re.search(r"cliff stack (\d+)", i.get("note", ""))
        key = m.group(1) if m else f"{i['pos'][0]},{i['pos'][2]}"
        stacks.setdefault(key, []).append(i)
swap = {}
for k, insts in stacks.items():
    top = max(insts, key=lambda i: i["pos"][1])
    key = "|".join([top["piece"]] + [str(v) for v in top["pos"]] + [str(top["yaw"])])
    swap[key] = top["piece"].replace("cliff_w24", "cliffT_w24").replace("slot_w24", "slotT_w24")
pieces = sorted({f"{a}_w24_h{h}_p{p}" for a in ("cliff", "cliffT") for h in (6, 12, 24, 48) for p in range(6)} |
                {f"{a}_w24_h{h}_p{p}" for a in ("slot", "slotT") for h in (24, 48) for p in range(6)} | {"rim_silhouette"})
out = dict(stacks=len(stacks), top_swaps=len(swap), pieces=pieces, swap=swap,
           design="pass-6 tower panels (sc_cliffs_pass6.py): one eroded tower per 24-wide panel with recessed edge gaps, "
                  "12-stud world-y stepped taper + cap-rock overhangs, wavy strata (0 at panel edges); stack tops use "
                  "the rounded-top T variants; same ids/placements/envelope as pass 5")
(SRC / "_cache" / "pass6_cliffs.json").write_text(json.dumps(out, indent=1))
print(len(stacks), "stacks", len(swap), "swaps")
