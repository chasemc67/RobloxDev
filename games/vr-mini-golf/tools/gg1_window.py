"""Stage gg1: list on-screen windows / capture one window to a PNG (no clicks, no keys).
  uv run --with pyobjc-framework-Quartz python3 tools/gg1_window.py list
  uv run --with pyobjc-framework-Quartz python3 tools/gg1_window.py grab OWNER_SUBSTRING OUT.png [TITLE_SUBSTRING]
"""
import subprocess, sys
import Quartz


def windows():
    opts = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    out = []
    for w in Quartz.CGWindowListCopyWindowInfo(opts, Quartz.kCGNullWindowID):
        b = w.get('kCGWindowBounds', {})
        out.append(dict(id=w['kCGWindowNumber'], owner=w.get('kCGWindowOwnerName', ''), title=w.get('kCGWindowName', '') or '',
                        layer=w.get('kCGWindowLayer', 0), x=b.get('X'), y=b.get('Y'), w=b.get('Width'), h=b.get('Height')))
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        for w in windows():
            print(w)
    elif sys.argv[1] == 'grab':
        owner, out = sys.argv[2], sys.argv[3]
        title = sys.argv[4] if len(sys.argv) > 4 else ''
        cand = [w for w in windows() if owner.lower() in w['owner'].lower() and title.lower() in w['title'].lower()
                and w['layer'] == 0 and (w['w'] or 0) > 300]
        cand.sort(key=lambda w: -(w['w'] * w['h']))
        if not cand:
            raise SystemExit('no window for %s' % owner)
        subprocess.run(['screencapture', '-x', '-o', '-l%d' % cand[0]['id'], out], check=True)
        print('saved', out, cand[0])
