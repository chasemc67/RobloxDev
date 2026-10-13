#!/usr/bin/env python3
"""Stage ab VR checks (SimulateVR playtest in the open place, Studio hooks GolfPointerDebug / GolfMenuDebug):
  - club setup: the stick turns the putter head (saved headYaw) and no longer moves the ground target
  - putter head: level on the ground, blended when slightly raised, rigid with the club when lifted
  - wrist card: shows on the off-hand wrist AND on the club-hand wrist
  - the left-stick click (ButtonL3) no longer opens the menu; B / Y still opens the scorecard
  - 0 console warnings/errors
  python3 tools/stage_ab_vr.py --out playtests/stage-ab/vr-lg
"""
import argparse
import json
import os
import time

from run_playtests import Studio, set_edit_attrs, clear_test_attrs, GAME_DIR
from menu_shots import menu, pointer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-ab", "vr"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True, "GolfTestCamera": ""})
    res = {}
    try:
        st.start_play()
        t0 = time.time()
        while time.time() - t0 < 60:
            r = st.luau("local p = game.Players.LocalPlayer; return (p and p:FindFirstChild('PlayerScripts') and "
                        "p.PlayerScripts:FindFirstChild('GolfPointerDebug')) and 'ok' or 'wait'", "Client")
            if r == "ok":
                break
            time.sleep(1)
        time.sleep(4)

        def button(key):
            return st.luau("game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.%s, false); task.wait(0.05); "
                           "game.ReplicatedStorage.VRDebug.Button:Fire(Enum.KeyCode.%s, true); return 'ok'" % (key, key), "Client")

        res["clubSetup"] = pointer(st, "clubSetupTest")
        res["headBlend"] = pointer(st, "headBlend")

        def wrist_after(arg, wait=1.6):
            pointer(st, "wrist", arg)
            time.sleep(wait)
            return pointer(st, "state")["wrist"]

        pointer(st, "clubAway")
        time.sleep(0.5)
        w = {"offHand": wrist_after(True), "lowered": wrist_after("down"), "clubHand": wrist_after("club"),
             "loweredAgain": wrist_after("down")}
        dominant = pointer(st, "clubSetup", {"action": "state"}).get("hand")
        w["dominant"] = dominant
        w["pass"] = (w["offHand"]["shown"] and w["offHand"]["hand"] != dominant and not w["lowered"]["shown"]
                     and w["clubHand"]["shown"] and w["clubHand"]["hand"] == dominant and not w["loweredAgain"]["shown"])
        res["wrist"] = w

        before = pointer(st, "state")["menuOpen"]
        button("ButtonL3")
        time.sleep(0.8)
        after_l3 = pointer(st, "state")["menuOpen"]
        button("ButtonY")
        time.sleep(0.8)
        sc = pointer(st, "state")["scorecard"]
        button("ButtonY")
        time.sleep(0.5)
        sc_closed = not pointer(st, "state")["scorecard"]
        res["menu"] = {"menuOpenBefore": before, "menuOpenAfterL3": after_l3, "scorecardAfterY": sc, "scorecardClosedAfterY": sc_closed}
        res["menu"]["pass"] = (not before) and (not after_l3) and sc and sc_closed
        res["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
        clear_test_attrs(st)
    res["pass"] = bool(res.get("clubSetup", {}).get("pass") and res.get("headBlend", {}).get("pass")
                       and res.get("wrist", {}).get("pass") and res.get("menu", {}).get("pass")
                       and not res["console"]["server"] and not res["console"]["client"])
    with open(os.path.join(args.out, "stage_ab_vr.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
