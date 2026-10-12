#!/usr/bin/env python3
"""Round 5: repro wrist SCORES after MENU -> Resume (it didn't hover in r5_wrist.py). Dumps the wrist state per step."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from ui_shots import capture  # noqa: E402
from menu_shots import pointer  # noqa: E402
from wrist_sim import LEVEL_HEAD  # noqa: E402
from r5_wrist import click, SWING  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
st = Studio()
st.stop_play()
set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": True})
res = []
def note(label, extra=None):
    s = pointer(st, "state")
    r = {"label": label, "wrist": {k: s["wrist"].get(k) for k in ("shown", "alpha", "blocked", "faceDeg", "gazeDeg")}, "pointer": s["pointer"], "extra": extra}
    res.append(r); print(json.dumps(r))
try:
    st.start_play(); time.sleep(12)
    st.luau(LEVEL_HEAD, "Client"); time.sleep(0.5)
    click(st, "Play"); click(st, "PlayCourse"); time.sleep(2)
    print(st.luau(SWING % ("4.0", "0"), "Client", timeout=90))
    for trial in range(3):
        st.luau(LEVEL_HEAD, "Client"); time.sleep(0.5)
        note("t%d before" % trial)
        r = click(st, "WristScores", wrist=True); note("t%d scores (no menu first)" % trial, r)
        capture(st, os.path.join(out, "scores_direct_t%d.png" % trial))
        r = click(st, "Close", "LeftHand"); note("t%d close" % trial, r)
        r = click(st, "WristMenu", wrist=True); note("t%d menu" % trial, r)
        r = click(st, "Resume"); note("t%d resume" % trial, r)
        # now SCORES with step-by-step state
        pointer(st, "wrist", True)
        for dt in (0.3, 0.6, 1.0, 1.6):
            time.sleep(dt if dt == 0.3 else 0.4 if dt == 0.6 else 0.4 if dt == 1.0 else 0.6)
            note("t%d wrist up after resume +%.1fs" % (trial, dt))
        capture(st, os.path.join(out, "scores_after_resume_wristup_t%d.png" % trial))
        pointer(st, "wrist", False); time.sleep(1.0)
        r = click(st, "WristScores", wrist=True); note("t%d scores after resume" % trial, r)
        if r.get("page") == "scorecard":
            click(st, "Close", "LeftHand")
    print(json.dumps({"server": st.problems("Server"), "client": st.problems("Client")}))
finally:
    json.dump(res, open(os.path.join(out, "scores_repro.json"), "w"), indent=1)
    st.stop_play()
    set_edit_attrs(st, {"SimulateVR": False})
