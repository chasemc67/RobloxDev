"""Stage au7 before/after captures of the H7 mogul trim and H18 ramp lantern cage (Studio MCP screen_capture).
  python3 tools/au7_shots.py before|after   -> playtests/stage-au7/{h7,h18}-<tag>.png + logs/stages/au7-<tag>.png (composite)
"""
import base64, io, sys
from pathlib import Path
from PIL import Image
from run_playtests import Studio

VIEWS = {  # camera, look-at (world studs); pivots H7 (365,112,308), H18 (-243.9,224.9,-265)
    'h7': ([377.0, 121.0, 288.0], [365.0, 112.5, 306.0]),
    'h18': ([-235.5, 233.5, -257.5], [-243.9, 230.0, -265.0]),
}

def main():
    tag = sys.argv[1]
    out = Path('playtests/stage-au7'); out.mkdir(parents=True, exist_ok=True)
    s = Studio(); assert s.mode()[0] == 'Edit'
    assert s.luau('return workspace:GetAttribute("PlaceRole")') == 'aurora_archipelago'
    imgs = []
    for name, (pos, at) in VIEWS.items():
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {
            'studio_id': s.id, 'capture_id': 'au7-%s-%s' % (name, tag), 'camera_position': pos, 'look_at_position': at}})
        img = next(c for c in r['result']['content'] if c.get('type') == 'image')
        im = Image.open(io.BytesIO(base64.b64decode(img['data']))).convert('RGB')
        im.save(out / ('%s-%s.png' % (name, tag))); imgs.append(im)
    h = max(i.height for i in imgs)
    comp = Image.new('RGB', (sum(i.width for i in imgs), h))
    x = 0
    for i in imgs:
        comp.paste(i, (x, 0)); x += i.width
    comp.save('logs/stages/au7-%s.png' % tag)
    print('saved', tag, comp.size)

if __name__ == '__main__':
    main()
