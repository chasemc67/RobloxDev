#!/usr/bin/env python3
"""Write the Lantern Grove world Terrain into Studio from the world map's 4-stud grid (terrain-4stud.json).

  python3 tools/world_terrain.py            # clear the world region, write all 200 rows, carve the holes, check
  python3 tools/world_terrain.py --carve    # only re-carve the holes + clearance check (after a course rebuild)
  python3 tools/world_terrain.py --check    # only the clearance check

Rows go in chunks through ServerStorage.WorldBuilder.WriteTerrainRows (Terrain:WriteVoxels at 4-stud resolution).
Then WorldBuilder.CarveHoles clears the Terrain over every felt piece (+0.6, felt bottom to 6.5 above) and fills the
water hazards, and CheckClearance raycasts every felt piece on a 0.5-stud grid for Terrain above the felt top.
Studio must be in Edit mode with the course already built in the world layout (tools/world_to_lua.py --push --build).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_playtests as rp  # noqa: E402
from holes_to_lua import REPO  # noqa: E402

GRID = os.path.join(REPO, "assets", "vr-mini-golf", "lantern-grove", "world", "terrain-4stud.json")
WB = "require(game.ServerStorage.WorldBuilder:Clone())"


def fmt(v):
    if v is None:
        return "_"
    r = "%.2f" % v
    return r.rstrip("0").rstrip(".")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=GRID)
    ap.add_argument("--rows", type=int, default=10, help="rows per WriteVoxels call")
    ap.add_argument("--carve", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    st = rp.Studio()
    if st.mode()[0] != "Edit":
        raise SystemExit("stop play first")
    if not (args.carve or args.check):
        g = json.load(open(args.grid))
        meta = "{cols=%d, cell=%d, x0=%s, z0=%s}" % (g["cols"], g["cell"], g["x0"], g["z0"])
        x1 = g["x0"] + g["cols"] * g["cell"]
        z1 = g["z0"] + g["rows"] * g["cell"]
        print(st.luau("workspace.Terrain:FillBlock(CFrame.new(%s, 74, %s), Vector3.new(%s, 172, %s), Enum.Material.Air) return 'cleared'"
                      % ((g["x0"] + x1) / 2, (g["z0"] + z1) / 2, x1 - g["x0"] + 8, z1 - g["z0"] + 8), "Edit", timeout=300))
        t0 = time.time()
        for j0 in range(0, g["rows"], args.rows):
            n = min(args.rows, g["rows"] - j0)
            hs = ",".join(fmt(v) for row in g["height"][j0:j0 + n] for v in row)
            ws = ",".join(fmt(v) for row in g["water"][j0:j0 + n] for v in row)
            ms = ",".join(str(v) for row in g["mat"][j0:j0 + n] for v in row)
            r = st.luau("return %s.WriteTerrainRows(%s, %d, %d, %s, %s, %s)" % (WB, meta, j0 + 1, n, json.dumps(hs), json.dumps(ws), json.dumps(ms)),
                        "Edit", timeout=300)
            print("rows %d-%d: %s (%.0fs)" % (j0, j0 + n - 1, r, time.time() - t0), flush=True)
    if not args.check:
        print("carve:", st.luau("return %s.CarveHoles()" % WB, "Edit", timeout=300))
    print("clearance:", st.luau("return %s.CheckClearance()" % WB, "Edit", timeout=300))


if __name__ == "__main__":
    main()
