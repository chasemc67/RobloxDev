"""Parse builder_Lobby.luau props{} -> list of dicts (id, asset, size, position, yaw, + extras)."""
import re, json, os
SRC = os.path.dirname(os.path.abspath(__file__))
KV = re.compile(r"^\s*(\w+) = (\{.*\}|\"[^\"]*\"|-?[\d.]+|true|false),?\s*$")


def parse(path=os.path.join(SRC, "builder_Lobby.luau")):
    lines = open(path, encoding="utf-8").read().splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.startswith("\tprops = {"))
    out, cur, depth = [], None, 0
    for l in lines[i0 + 1:]:
        if l.startswith("\t},"):
            break
        if l == "\t\t{":
            cur = {}
            continue
        if l.startswith("\t\t},") or l == "\t\t}":
            if cur is not None and "assetName" in cur:
                cur["asset"] = cur["assetName"].replace(".fbx", "")
                out.append(cur)
            cur = None
            continue
        if cur is None or not l.startswith("\t\t\t") or l.startswith("\t\t\t\t"):
            continue
        m = KV.match(l)
        if not m:
            continue
        k, v = m.groups()
        if v.startswith("{"):
            nums = re.findall(r"-?\d+(?:\.\d+)?", v)
            cur[k] = [float(x) for x in nums] if "=" not in v else v
        elif v.startswith('"'):
            cur[k] = v[1:-1]
        elif v in ("true", "false"):
            cur[k] = v == "true"
        else:
            cur[k] = float(v)
    return out


if __name__ == "__main__":
    P = parse()
    print(len(P))
    from collections import Counter
    print(Counter(p["asset"] for p in P))
    for p in P:
        if not p["asset"].startswith(("bw_deck", "bw_railing", "bw_pier", "bw_lantern_post", "bw_bench")):
            print(json.dumps({k: v for k, v in p.items() if k != "assetName"}))
