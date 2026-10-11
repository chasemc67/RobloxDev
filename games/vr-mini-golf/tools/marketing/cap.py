import sys, json, base64, os
sys.path.insert(0, os.path.expanduser("~/src/RobloxDev/games/vr-mini-golf/tools"))
from studio_mcp import StudioMCP
SID = "ee2e1446-53b6-4363-937f-9e22188c182f"
_m = None
def m():
    global _m
    if _m is None: _m = StudioMCP()
    return _m
def luau(code):
    return m().call("execute_luau", {"studio_id": SID, "datamodel_type": "Edit", "code": code})
def capture(path, cam, look):
    r = m().req("tools/call", {"name": "screen_capture", "arguments": {"studio_id": SID, "capture_id": os.path.basename(path), "camera_position": cam, "look_at_position": look}})
    img = [c for c in r["result"]["content"] if c.get("type") == "image"][0]
    open(path, "wb").write(base64.b64decode(img["data"]))
    return path
if __name__ == "__main__":
    print(luau("workspace.CurrentCamera.FieldOfView = %s; return workspace.CurrentCamera.FieldOfView" % sys.argv[1]))
    capture(sys.argv[2], [190, 30, 180], [190, 26, 150])
    print(luau("return workspace.CurrentCamera.FieldOfView .. ' ' .. tostring(workspace.CurrentCamera.ViewportSize)"))
