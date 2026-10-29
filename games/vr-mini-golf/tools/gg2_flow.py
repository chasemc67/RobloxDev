"""Stage gg2: the hidden bonus hole flow in a NORMAL playtest (GolfTestMode off), desktop or SimulateVR.
  PYTHONPATH=tools python3 tools/gg2_flow.py OUT.json [--vr]
Starts on hole 9 (workspace DebugStartHole = 9 for this Play only; cleared after, so the round is not counted and
nothing reaches the personal best / leaderboard). Real remotes drive the strokes (Remotes.Stroke / BallRest /
LeaveBonus / PlayAgain from the client); the server moves the (server-owned for that moment) ball into the egg
trigger and into the cups, so GolfServer's own Heartbeat does the egg entry and the sinks.
Steps: enter (toast, HUD/wrist "Hole 19", head at the goose tee) -> 2 strokes -> sink (Honk! message, HoleComplete 19)
-> back on hole 9 (strokes kept, head back) -> enter again -> "Back to Hole 9" (LeaveBonus) -> enter again -> max
strokes -> back -> enter again -> restart round (PlayAgain true) clears the bonus -> holes 1-8 sunk without strokes,
sink hole 9 -> CourseComplete: 9 holes, par 27, bonus not in the totals. Console problems on both sides.
"""
import json
import sys
import time

from run_playtests import Studio, set_edit_attrs

SRV_ME = "local p = game.Players:GetPlayers()[1] local ball = workspace.Balls:FindFirstChild(tostring(p.UserId)) "

STATE = """local p = game.Players.LocalPlayer
local pg = p.PlayerGui
local texts = {}
for _, d in pg:GetDescendants() do
  if d:IsA('TextLabel') and d.Visible and (d.Text:match('^Hole') or d.Text:match('Honk') or d.Text:match('hidden') or d.Text:match('Par %d')) then
    table.insert(texts, d.Text)
  end
end
local ball = workspace.Balls:FindFirstChild(tostring(p.UserId))
local cam = workspace.CurrentCamera.CFrame.Position
local h19 = workspace.Course:FindFirstChild('Hole19')
local h9 = workspace.Course:FindFirstChild('Hole9')
local function d(a, b) return math.floor((a - b).Magnitude * 100) / 100 end
local wrist
local hook = p.PlayerScripts:FindFirstChild('GolfPointerDebug')
if hook then local ok, r = pcall(function() return hook:Invoke('regressionState') end) if ok then wrist = r.wrist end end
return game:GetService('HttpService'):JSONEncode({hole = p:GetAttribute('Hole'), bonus = p:GetAttribute('BonusHole'),
  strokes = p:GetAttribute('Strokes'), scores = p:GetAttribute('Scores'), holed = p:GetAttribute('HoleHoled'),
  ballToH19Tee = ball and h19 and d(ball.Position, h19.Tee.Position), ballToH9Return = ball and d(ball.Position, h9.Secret.EggTrigger:GetAttribute('ReturnWorld')),
  camToBall = ball and d(cam, ball.Position), camToH19Tee = h19 and d(cam, h19.Tee.Position), texts = texts, wrist = wrist,
  last = _G.GG2Last, complete = _G.GG2Complete})"""

LISTEN = """local R = game.ReplicatedStorage.Golf.Remotes
_G.GG2Last = {}
R.HoleComplete.OnClientEvent:Connect(function(who, n, s, par, maxed) if who == game.Players.LocalPlayer then _G.GG2Last.holeComplete = {n, s, par, maxed} end end)
R.Notice.OnClientEvent:Connect(function(text, kind) _G.GG2Last.notice = {text, kind} end)
R.BallPlaced.OnClientEvent:Connect(function(pos, reason, n) _G.GG2Last.placed = {reason, n} end)
R.CourseComplete.OnClientEvent:Connect(function(scores, result) _G.GG2Complete = {scores = scores, result = result} end)
return 'ok'"""


def main():
    out = sys.argv[1]
    vr = '--vr' in sys.argv
    s = Studio()
    s.stop_play()
    set_edit_attrs(s, {'GolfTestMode': False, 'SimulateVR': vr, 'DebugStartHole': 9})
    log = {'vr': vr, 'steps': []}

    def state(tag):
        r = json.loads(s.luau(STATE, 'Client'))
        r['step'] = tag
        log['steps'].append(r)
        print(tag, json.dumps({k: v for k, v in r.items() if k not in ('texts',)})[:600], r['texts'][:4], flush=True)
        return r

    def stroke(n=1):
        for _ in range(n):
            s.luau("local p = game.Players.LocalPlayer local b = workspace.Balls[tostring(p.UserId)] "
                   "game.ReplicatedStorage.Golf.Remotes.Stroke:FireServer(b.Position) return 'ok'", 'Client')
            time.sleep(0.45)

    def server_ball_to(expr, lift=0.0):
        return s.luau(SRV_ME + "local target = %s ball.Anchored = false ball:SetNetworkOwner(nil) "
                      "ball.AssemblyLinearVelocity = Vector3.zero ball.CFrame = CFrame.new(target + Vector3.new(0, %f, 0)) return 'ok'" % (expr, lift), 'Server')

    egg = "workspace.Course.Hole9.Secret.EggTrigger.Position"
    cup19 = "workspace.Course.Hole19.Cup.Position - Vector3.new(0, 0.25, 0)"
    cup9 = "workspace.Course.Hole9.Cup.Position - Vector3.new(0, 0.25, 0)"
    try:
        s.start_play()
        time.sleep(14)
        print(s.luau(LISTEN, 'Client'))
        state('start-h9')
        stroke(1)
        state('h9-1-stroke')
        # 1. enter through the egg
        server_ball_to(egg, 0.12)
        time.sleep(0.8)
        state('egg-entered')
        time.sleep(2.6)
        state('on-h19-tee')
        stroke(2)
        state('h19-2-strokes')
        server_ball_to(cup19)
        time.sleep(1.0)
        state('h19-sunk')
        time.sleep(4.0)
        state('back-on-h9')
        # 2. enter again, leave early
        server_ball_to(egg, 0.12)
        time.sleep(3.4)
        state('enter2')
        s.luau("game.ReplicatedStorage.Golf.Remotes.LeaveBonus:FireServer() return 'ok'", 'Client')
        time.sleep(1.5)
        state('left-early')
        # 3. enter again, max strokes
        server_ball_to(egg, 0.12)
        time.sleep(3.4)
        stroke(8)
        s.luau("game.ReplicatedStorage.Golf.Remotes.BallRest:FireServer() return 'ok'", 'Client')
        time.sleep(1.0)
        state('h19-maxed')
        time.sleep(4.0)
        state('back-after-max')
        # 4. enter again, restart the round from the menu (PlayAgain restart = true): bonus cleared, hole 1
        server_ball_to(egg, 0.12)
        time.sleep(3.4)
        state('enter4')
        s.luau("game.ReplicatedStorage.Golf.Remotes.PlayAgain:FireServer(true) return 'ok'", 'Client')
        time.sleep(1.5)
        state('restarted')
        # 5. play on to hole 9 and finish the round there:
        # sink holes 1..8 by moving the ball into each cup (no strokes: the round can never count)
        for n in range(1, 9):
            server_ball_to("workspace.Course.Hole%d.Cup.Position - Vector3.new(0, 0.25, 0)" % n)
            time.sleep(4.3)
        state('on-h9-again')
        stroke(1)
        server_ball_to(cup9)
        time.sleep(5.0)
        st = state('round-complete')
        log['courseComplete'] = st.get('complete')
        log['problems'] = {dm: s.problems(dm) for dm in ('Server', 'Client')}
    finally:
        s.stop_play()
        set_edit_attrs(s, {'GolfTestMode': False, 'SimulateVR': False})
        s.luau("workspace:SetAttribute('DebugStartHole', nil) return tostring(workspace:GetAttribute('DebugStartHole'))", 'Edit')
    open(out, 'w').write(json.dumps(log, indent=1) + '\n')
    print('problems', {k: len(v) for k, v in log['problems'].items()})


if __name__ == '__main__':
    main()
