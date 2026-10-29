"""Stage gg2/gg3 harness sweeps (GolfTestMode): bonus hole 10 (routes, intended lines, cup drop, fuzz) and the H9 golden
egg (deliberate putts, accidental rate over fuzz + played routes, bonus-hole slow putts).
  PYTHONPATH=tools python3 tools/gg2_sweeps.py OUT_DIR [h10] [egg]
"""
import json
import sys
from pathlib import Path

import time

from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
which = sys.argv[2:] or ['h10', 'egg']
SEED = 20261028
# deliberate putts at the egg from the heart green where a ball lands after the chamber drop (H9 local x, z, y, aim, speed)
EGG_SHOTS = [[x, z, -0.7, aim, v] for (x, z) in ((22.0, -42.5), (24.0, -43.0)) for aim in (6, 9, 12) for v in (5.5, 6.5, 7.5)]
SEARCH = ([[31.3, -46.5, -0.8, a, v] for a in (85, 90, 95) for v in (4, 5, 6, 7)] +
          [[24.0, -43.0, -0.7, a, v] for a in (20, 30, 40) for v in (7, 8.5, 10)] +
          [[29.6, -47.0, -0.8, a, v] for a in (70, 75, 80) for v in (5, 6, 7)])
RUNS = {
    'slow': ('gg2egg', {'course': 'lantern_grove', 'slow10': 45, 'seed': SEED}),
    'eggsearch': ('gg2egg', {'course': 'lantern_grove', 'eggShots': SEARCH, 'seed': SEED}),
    'h10': ('h10', {'course': 'lantern_grove', 'parts': 'routes,intended,cupdrop,fuzz', 'fuzz': 72, 'tries': 5, 'seed': SEED}),
    'egg': ('gg2egg', {'course': 'lantern_grove', 'eggShots': EGG_SHOTS, 'eggFuzz': 80, 'eggRoutes': 6, 'slow10': 45, 'seed': SEED}),
}


def run(name, seconds):
    # (the result can be > the 100k MCP reply cap: fetch it in chunks)
    assert s.api("start", name, "") == "started"
    t0 = time.time()
    while time.time() - t0 < seconds:
        time.sleep(3)
        st = s.api("status")
        if st.startswith("{") and not json.loads(st).get("running"):
            break
    n = int(s.luau("local f = game.ReplicatedStorage:FindFirstChild('GolfTestAPI') _G.GG2Res = f:Invoke('result', %s) return #_G.GG2Res" % json.dumps(name), "Client"))
    raw = "".join(json.loads(s.luau("return game.HttpService:JSONEncode(_G.GG2Res:sub(%d, %d))" % (i + 1, i + 40000), "Client"))
                  for i in range(0, n, 40000))
    (out / (name + "-result.json")).write_text(raw + "\n")
    print(name, "%.0fs" % (time.time() - t0), len(raw), flush=True)
    return json.loads(raw)


s = Studio()
assert s.mode()[0] == 'Edit'
set_edit_attrs(s, {'GolfTestMode': True, 'SimulateVR': False, 'GolfTestOpts': json.dumps(RUNS[which[0]][1])})
s.start_play()
wait_api(s)
results = {}
try:
    for k in which:
        name, opts = RUNS[k]
        s.luau('workspace:SetAttribute("GolfTestOpts", ' + json.dumps(json.dumps(opts)) + ')', 'Client')
        results[k] = run(name, 2400)
        (out / 'results.json').write_text(json.dumps(results, indent=1) + '\n')
        print('COMPLETED', k, flush=True)
    (out / 'console.json').write_text(json.dumps({dm: s.problems(dm) for dm in ['Server', 'Client']}, indent=1) + '\n')
finally:
    s.stop_play()
    clear_test_attrs(s)
