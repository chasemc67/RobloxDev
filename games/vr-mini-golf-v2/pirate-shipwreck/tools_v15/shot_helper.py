# localhost-only: GET /shot?name=X.png runs shoot14.sh X.png synchronously and returns its output
import http.server, subprocess, urllib.parse, os
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = os.path.basename(q.get("name", ["x.png"])[0])
        r = subprocess.run([os.path.expanduser("~/stage/shoot14.sh"), name], capture_output=True, text=True)
        b = (r.stdout + r.stderr).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", 8767), H).serve_forever()
