"""Stage z smoke checks for the place split (lobby place + one place per course). Called by
`run_playtests.py smoke`, which picks these by the open place's workspace PlaceRole:
  lobby: spawn in the lobby with no ball, menu on the title, Menu button at the TOP RIGHT and the only one; close (X),
         walk, reopen (Menu button, M); a course card fires its teleport request (loading screen up, then the Studio
         "skipped" takes it down); walking into each arch portal fires that course's teleport request; the leaderboard
         wall renders rows from LeaderboardMock and "No rounds yet" without.
  course (lantern_grove / sugarloaf_canyon): hole 1 started on arrival (Course attribute, ball on the H1 tee, menu
         closed), the single top-right Menu button, Menu > Lobby fires the lobby teleport request, and a finished
         round shows the results countdown and fires the lobby request by itself (GolfServer's GolfFinishDebug hook).
In Studio, PlaceTeleport records each request in the server's workspace attribute LastTeleportRequest
("<player>|<dest>|<reason>|<placeId>") instead of teleporting.
"""
import json
import time

MENU_STATE = """local me = game:GetService('Players').LocalPlayer
local GuiService = game:GetService('GuiService')
GuiService.SelectedObject = nil
task.wait(0.4)
local pg = me.PlayerGui
local vp = workspace.CurrentCamera.ViewportSize
local inset = GuiService:GetGuiInset()
local menu = me.PlayerScripts.GolfMenuDebug:Invoke('state')
local btn = pg:FindFirstChild('GolfMenuButton') and pg.GolfMenuButton:FindFirstChild('MenuButton')
-- every visible button anywhere in PlayerGui that says / is called Menu (only one may exist)
local menus = {}
for _, d in pg:GetDescendants() do
  if d:IsA('GuiButton') and d.Name ~= 'BackToMenu' then
    local text = d:IsA('TextButton') and d.Text or ((d:FindFirstChild('Label') and d.Label.Text) or '')
    if string.lower(text) == 'menu' or d.Name == 'Menu' or d.Name == 'MenuButton' then
      local sg = d:FindFirstAncestorOfClass('ScreenGui')
      table.insert(menus, {path = d:GetFullName(), shown = d.Visible and (sg == nil or sg.Enabled)})
    end
  end
end
local hum = me.Character and me.Character:FindFirstChildOfClass('Humanoid')
local hrp = me.Character and me.Character:FindFirstChild('HumanoidRootPart')
local hud = pg:FindFirstChild('GolfHUD')
local out = {menuOpen = menu.open, menuPage = menu.page, menuButtonShown = menu.menuButton, menus = menus,
  viewport = {vp.X, vp.Y}, cam = tostring(workspace.CurrentCamera.CameraType),
  walkSpeed = hum and hum.WalkSpeed, jump = hum and (hum.UseJumpPower and hum.JumpPower or hum.JumpHeight),
  pos = hrp and {hrp.Position.X, hrp.Position.Y, hrp.Position.Z}, course = me:GetAttribute('Course'),
  golfHud = hud ~= nil and hud.Enabled, balls = workspace:FindFirstChild('Balls') and #workspace.Balls:GetChildren() or 0,
  loading = pg:FindFirstChild('GolfLoading') and pg.GolfLoading:GetAttribute('Destination') or nil}
if btn then
  -- AbsolutePosition is relative to the inset origin unless the ScreenGui ignores the inset (GolfMenuButton does)
  local x0 = btn.AbsolutePosition.X
  local x1 = x0 + btn.AbsoluteSize.X
  out.button = {x0 = x0, x1 = x1, y0 = btn.AbsolutePosition.Y, y1 = btn.AbsolutePosition.Y + btn.AbsoluteSize.Y,
    image = btn:IsA('ImageButton') and btn.Image or '', topbar = {GuiService.TopbarInset.Min.X, GuiService.TopbarInset.Max.X, GuiService.TopbarInset.Height}}
  -- screen space: the ScreenGui's own AbsolutePosition is relative to the inset origin too, so compare in that frame
  local sg = btn:FindFirstAncestorOfClass('ScreenGui')
  local top = btn.AbsolutePosition.Y + inset.Y
  out.button.screenTop = top
  out.button.screenRight = x1
  out.topRight = x1 > vp.X * 0.85 and x1 <= vp.X + 1 and top >= -1 and top < 58
end
local x = pg:FindFirstChild('GolfMenu') and pg.GolfMenu:FindFirstChild('CloseMenu', true)
out.closeImage = x and x:IsA('ImageButton') and x.Image or ''
local frame = pg:FindFirstChild('GolfMenu') and pg.GolfMenu.Root:FindFirstChild('Frame')
out.frame = frame and {image = frame.Image, slice = tostring(frame.SliceCenter), scale = tostring(frame.ScaleType)} or nil
return game:GetService('HttpService'):JSONEncode(out)"""

SELECT = """local GuiService = game:GetService('GuiService')
local me = game:GetService('Players').LocalPlayer
GuiService.SelectedObject = %s
task.wait(0.2)
return tostring(GuiService.SelectedObject)"""

LAST_REQ = "return tostring(workspace:GetAttribute('LastTeleportRequest'))"
CLEAR_REQ = "workspace:SetAttribute('LastTeleportRequest', nil) return 'ok'"


def key(st, *actions):
    st.call("user_keyboard_input", {"actions": list(actions), "datamodel_type": "Client"})


def press(st, path):
    sel = st.luau(SELECT % path, "Client")
    key(st, {"action": "keyPress", "key_code": "Return"})
    return sel


def menu_state(st):
    return json.loads(st.luau(MENU_STATE, "Client"))


def wait_request(st, expect_dest, timeout=8):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = st.luau(LAST_REQ, "Server")
        if r and r != "nil" and ("|%s|" % expect_dest) in r:
            return r
        time.sleep(0.5)
    return st.luau(LAST_REQ, "Server")


def single_top_right(m):
    shown = [x for x in m["menus"] if x["shown"]]
    return len(m["menus"]) == 1 and len(shown) <= 1 and bool(m.get("topRight"))


def loading_cycle(st, log):
    """The client's loading screen goes up on 'start' and comes down on the Studio 'skipped'."""
    up = st.luau("""local pg = game:GetService('Players').LocalPlayer.PlayerGui
local t0 = os.clock()
while os.clock() - t0 < 3 and not pg:FindFirstChild('GolfLoading') do task.wait(0.05) end
local g = pg:FindFirstChild('GolfLoading')
return g and (g:GetAttribute('Destination') .. '|' .. g.Art.Image) or 'none'""", "Client")
    down = st.luau("""local pg = game:GetService('Players').LocalPlayer.PlayerGui
local t0 = os.clock()
while os.clock() - t0 < 6 and pg:FindFirstChild('GolfLoading') do task.wait(0.1) end
return pg:FindFirstChild('GolfLoading') and 'still up' or 'gone'""", "Client")
    return {"up": up, "down": down}


def lobby(st, log):
    r = {}
    ok = True
    j = r["join"] = json.loads(st.luau("""local me = game:GetService('Players').LocalPlayer
local lobby = workspace:FindFirstChild('Lobby')
local cf, size = lobby:GetBoundingBox()
local hrp = me.Character and me.Character:FindFirstChild('HumanoidRootPart')
local lp = hrp and cf:PointToObjectSpace(hrp.Position)
local menu = me.PlayerScripts.GolfMenuDebug:Invoke('state')
local gui = me.PlayerGui:FindFirstChild('GolfMenu')
return game:GetService('HttpService'):JSONEncode({inLobby = lp ~= nil and math.abs(lp.X) <= size.X / 2 and math.abs(lp.Z) <= size.Z / 2,
  course = me:GetAttribute('Course'), balls = workspace:FindFirstChild('Balls') ~= nil, menuOpen = menu.open, menuPage = menu.page,
  resume = gui ~= nil and gui:FindFirstChild('Resume', true) ~= nil, courseFolders = workspace:FindFirstChild('Course') ~= nil or workspace:FindFirstChild('CourseSugarloaf') ~= nil,
  golfHud = me.PlayerGui:FindFirstChild('GolfHUD') ~= nil, role = workspace:GetAttribute('PlaceRole')})""", "Client"))
    ok = ok and j["inLobby"] and j.get("course") is None and not j["balls"] and j["menuOpen"] and j["menuPage"] == "title" \
        and not j["resume"] and not j["courseFolders"] and not j["golfHud"]
    log("lobby join", json.dumps(j))
    # close with the real X, walk, Menu button (top right, the only one) reopens, M closes and reopens
    r["selClose"] = press(st, "me.PlayerGui.GolfMenu:FindFirstChild('CloseMenu', true)")
    c = r["closed"] = menu_state(st)
    ok = ok and not c["menuOpen"] and c["menuButtonShown"] and c["cam"] == "Enum.CameraType.Custom" and c["walkSpeed"] > 0
    r["menuButtonTopRight"] = single_top_right(c)
    ok = ok and r["menuButtonTopRight"]
    key(st, {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": 2000}, {"action": "keyUp", "key_code": "W"})
    w = menu_state(st)
    r["moved"] = round(((w["pos"][0] - c["pos"][0]) ** 2 + (w["pos"][2] - c["pos"][2]) ** 2) ** 0.5, 2)
    ok = ok and r["moved"] > 5
    r["selMenu"] = press(st, "me.PlayerGui.GolfMenuButton.MenuButton")
    o = r["reopened"] = menu_state(st)
    ok = ok and o["menuOpen"] and o["menuPage"] == "title" and not o["menuButtonShown"] and o["walkSpeed"] == 0
    key(st, {"action": "keyPress", "key_code": "M"})
    r["mClosed"] = not menu_state(st)["menuOpen"]
    key(st, {"action": "keyPress", "key_code": "M"})
    mo = menu_state(st)
    r["mReopened"] = mo["menuOpen"] and mo["menuPage"] == "title"
    ok = ok and r["mClosed"] and r["mReopened"]
    log("lobby menu", json.dumps({k: r[k] for k in ("moved", "menuButtonTopRight", "mClosed", "mReopened")}), json.dumps(c.get("button")))

    # course card -> teleport request + loading screen
    r["cards"] = {}
    for course in ("lantern_grove", "sugarloaf_canyon", "aurora_archipelago"):
        st.luau(CLEAR_REQ, "Server")
        st.luau("game:GetService('Players').LocalPlayer.PlayerScripts.GolfMenuDebug:Invoke('open', 'courses') task.wait(0.4) return 'ok'", "Client")
        info = st.luau("""local card = game:GetService('Players').LocalPlayer.PlayerGui.GolfMenu:FindFirstChild(%s, true)
local t = {}
for _, d in card:GetDescendants() do if d:IsA('TextLabel') or d:IsA('TextButton') then table.insert(t, d.Text) end end
return table.concat(t, ' / ')""" % json.dumps(course), "Client")
        sel = press(st, "me.PlayerGui.GolfMenu:FindFirstChild(%s, true):FindFirstChild('PlayCourse')" % json.dumps(course))
        cyc = loading_cycle(st, log)
        req = wait_request(st, course)
        good = ("|%s|menu|" % course) in req and cyc["up"].startswith(course + "|rbxassetid://") and cyc["down"] == "gone"
        r["cards"][course] = {"card": info, "selected": sel, "request": req, "loading": cyc, "ok": good}
        ok = ok and good
        time.sleep(4.2)  # (PlaceTeleport cooldown)
    log("lobby cards", json.dumps(r["cards"]))

    # walk into each arch portal (stand 8 studs in front facing it, hold W)
    st.luau("local me = game:GetService('Players').LocalPlayer me.PlayerScripts.GolfMenuDebug:Invoke('close') return 'ok'", "Client")
    r["portals"] = {}
    for course in ("lantern_grove", "sugarloaf_canyon", "aurora_archipelago"):
        st.luau(CLEAR_REQ, "Server")
        pos = st.luau("""local me = game:GetService('Players').LocalPlayer
local portal = workspace.Lobby.Portals:FindFirstChild('Portal_' .. %s)
local front = portal.Position + Vector3.new(0, -2, 8)
me.Character:PivotTo(CFrame.lookAt(front, Vector3.new(portal.Position.X, front.Y, portal.Position.Z)))
-- (a gamepad-style GUI selection left by the card presses would swallow W)
game:GetService('GuiService').SelectedObject = nil
-- (W walks where the camera looks: put the camera behind the character, facing the portal)
local cam = workspace.CurrentCamera
cam.CFrame = CFrame.lookAt(front + Vector3.new(0, 4, 10), Vector3.new(portal.Position.X, front.Y, portal.Position.Z))
task.wait(0.5)
return tostring(portal.Size) .. ' at ' .. tostring(portal.Position)""" % json.dumps(course), "Client")
        key(st, {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": 1500}, {"action": "keyUp", "key_code": "W"})
        walked = st.luau("return tostring(game:GetService('Players').LocalPlayer.Character.HumanoidRootPart.Position)", "Client")
        cyc = loading_cycle(st, log)
        req = wait_request(st, course)
        good = ("|%s|portal|" % course) in req and cyc["up"].startswith(course + "|")
        r["portals"][course] = {"portal": pos, "walkedTo": walked, "request": req, "loading": cyc, "ok": good}
        ok = ok and good
        # step back out so the next one starts clean
        st.luau("local me = game:GetService('Players').LocalPlayer me.Character:PivotTo(CFrame.new(-10, 3, 6100)) task.wait(0.3) return 'ok'", "Client")
        time.sleep(4.2)
    log("lobby portals", json.dumps(r["portals"]))

    # leaderboard wall: no scores -> the empty note; LeaderboardMock -> rows lowest first
    st.luau("workspace:SetAttribute('LeaderboardMock', nil) return 'ok'", "Server")
    empty = st.luau("return game:GetService('ServerScriptService').LobbyServer.LeaderboardRefresh:Invoke()", "Server")
    mock = {"lantern_grove": [[1, 31, "Ada"], [2, 27, "Bo"], [3, 29, "Cy"]], "sugarloaf_canyon": [[4, 60, "Di"]]}
    st.luau("workspace:SetAttribute('LeaderboardMock', %s) return 'ok'" % json.dumps(json.dumps(mock)), "Server")
    filled = st.luau("return game:GetService('ServerScriptService').LobbyServer.LeaderboardRefresh:Invoke()", "Server")
    time.sleep(1)
    rows = json.loads(st.luau("""local b = workspace.Lobby.Leaderboard.Board
local out = {}
for _, id in {'lantern_grove', 'sugarloaf_canyon'} do
  local col = b:FindFirstChild('Col_' .. id, true)
  local t = {}
  for i = 1, 3 do local r = col['Row' .. i]; table.insert(t, r.Rank.Text .. ' ' .. r.Player.Text .. ' ' .. r.Total.Text) end
  out[id] = {rows = t, note = col.Note.Text}
end
return game:GetService('HttpService'):JSONEncode(out)""", "Client"))
    st.luau("workspace:SetAttribute('LeaderboardMock', nil) return 'ok'", "Server")
    r["leaderboard"] = {"empty": empty, "filled": filled, "client": rows}
    lb_ok = rows["lantern_grove"]["rows"][0] == "1. Bo 27" and rows["lantern_grove"]["rows"][2] == "3. Ada 31" \
        and rows["sugarloaf_canyon"]["rows"][0] == "1. Di 60"
    r["leaderboardOk"] = lb_ok
    ok = ok and lb_ok
    log("lobby leaderboard", json.dumps(r["leaderboard"]))
    r["ok"] = bool(ok)
    return r


def course(st, role, log):
    r = {}
    folder = {"lantern_grove": "Course", "sugarloaf_canyon": "CourseSugarloaf", "aurora_archipelago": "CourseAurora"}[role]
    a = r["arrival"] = json.loads(st.luau("""local me = game:GetService('Players').LocalPlayer
local t0 = os.clock()
local ball
while os.clock() - t0 < 15 do
  ball = workspace:FindFirstChild('Balls') and workspace.Balls:FindFirstChild(tostring(me.UserId))
  if ball and not ball.Anchored and me:GetAttribute('Hole') == 1 then break end
  task.wait(0.2)
end
local h1 = workspace[%s]:FindFirstChild('Hole1')
return game:GetService('HttpService'):JSONEncode({course = me:GetAttribute('Course'), hole = me:GetAttribute('Hole'),
  ballToTee = ball and math.floor((ball.Position - h1.Tee.Position).Magnitude * 100) / 100, anchored = ball and ball.Anchored,
  lobby = workspace:FindFirstChild('Lobby') ~= nil, otherCourse = workspace:FindFirstChild(%s) ~= nil})""" % (
        json.dumps(folder), json.dumps("CourseSugarloaf" if folder == "Course" else "Course")), "Client"))
    ok = a["course"] == role and a["hole"] == 1 and (a["ballToTee"] or 99) < 1 and a["anchored"] is False and not a["lobby"] and not a["otherCourse"]
    m = r["menu"] = menu_state(st)
    r["menuClosedOnArrival"] = not m["menuOpen"] and m["menuButtonShown"]
    r["menuButtonTopRight"] = single_top_right(m)
    ok = ok and r["menuClosedOnArrival"] and r["menuButtonTopRight"] and m["golfHud"]
    log("course arrival", json.dumps(a), "menu", json.dumps({k: r[k] for k in ("menuClosedOnArrival", "menuButtonTopRight")}), json.dumps(m["menus"]))
    # Menu (top right) -> title -> Lobby
    st.luau(CLEAR_REQ, "Server")
    r["selMenu"] = press(st, "me.PlayerGui.GolfMenuButton.MenuButton")
    o = menu_state(st)
    r["selLobby"] = press(st, "me.PlayerGui.GolfMenu:FindFirstChild('BackToLobby', true)")
    cyc = loading_cycle(st, log)
    req = wait_request(st, "lobby")
    r["backToLobby"] = {"opened": o["menuOpen"] and o["menuPage"] == "title", "request": req, "loading": cyc}
    good = r["backToLobby"]["opened"] and "|lobby|menu|" in req and cyc["up"].startswith("lobby|") and cyc["down"] == "gone"
    ok = ok and good
    log("course menu > lobby", json.dumps(r["backToLobby"]))
    time.sleep(4.2)
    # finished round -> results (countdown) -> lobby request by itself
    st.luau(CLEAR_REQ, "Server")
    fin = st.luau("""local me = game:GetService('Players')
local p = me:GetPlayers()[1]
return game:GetService('ServerScriptService').GolfServer.GolfFinishDebug:Invoke(p, 4)""", "Server")
    res = st.luau("""local me = game:GetService('Players').LocalPlayer
task.wait(1.2)
local gui = me.PlayerGui:FindFirstChild('GolfMenu')
local cd = gui and gui:FindFirstChild('ReturnCountdown', true)
local menu = me.PlayerScripts.GolfMenuDebug:Invoke('state')
return game:GetService('HttpService'):JSONEncode({page = menu.page, countdown = cd and cd.Text or nil,
  lobbyButton = gui ~= nil and gui:FindFirstChild('BackToLobby', true) ~= nil})""", "Client")
    req2 = wait_request(st, "lobby", timeout=10)
    res = json.loads(res)
    r["finish"] = {"hook": fin, "results": res, "request": req2}
    good = fin == "ok" and res["page"] == "results" and (res["countdown"] or "").startswith("Back to the lobby in") and "|lobby|finished|" in req2
    ok = ok and good
    log("course finish > lobby", json.dumps(r["finish"]))
    time.sleep(2)
    # close the results and start a fresh round so the rest of the smoke run plays hole 1
    st.luau("local me = game:GetService('Players').LocalPlayer me.PlayerScripts.GolfMenuDebug:Invoke('close') "
            "game:GetService('ReplicatedStorage').Golf.Remotes.PlayAgain:FireServer() task.wait(2) return 'ok'", "Client")
    r["ok"] = bool(ok)
    return r
