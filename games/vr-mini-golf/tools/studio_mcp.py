import json, subprocess, sys, threading, queue, time
class StudioMCP:
    def __init__(self, cmd="/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"):
        self.p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.q = queue.Queue(); self.id = 0
        threading.Thread(target=self._rd, daemon=True).start()
        self.req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "golf-harness", "version": "1"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"); self.p.stdin.flush()
    def _rd(self):
        for line in self.p.stdout:
            try: self.q.put(json.loads(line))
            except Exception: pass
    def req(self, method, params, timeout=300):
        self.id += 1; i = self.id
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params}) + "\n"); self.p.stdin.flush()
        t = time.time() + timeout
        while time.time() < t:
            try: m = self.q.get(timeout=1)
            except queue.Empty: continue
            if m.get("id") == i: return m
        raise TimeoutError(method)
    def call(self, name, args=None, timeout=300):
        r = self.req("tools/call", {"name": name, "arguments": args or {}}, timeout)
        if "error" in r: return "ERROR: " + json.dumps(r["error"])
        return "\n".join(c.get("text", "[%s]" % c.get("type")) for c in r["result"].get("content", []))
if __name__ == "__main__":
    s = StudioMCP()
    if sys.argv[1] == "tools":
        r = s.req("tools/list", {}); print("\n".join(t["name"] + ": " + json.dumps(t.get("inputSchema", {}).get("properties", {}))[:300] for t in r["result"]["tools"]))
    else:
        print(s.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}))
