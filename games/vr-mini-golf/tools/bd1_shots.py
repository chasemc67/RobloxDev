"""Stage bd1: paired screenshots (player view | top-down) into one PNG under logs/stages.
  BD1_ROLE=... PYTHONPATH=tools python3 tools/bd1_shots.py NAME  px,py,pz tx,ty,tz  qx,qy,qz ux,uy,uz
Saves logs/stages/NAME.png (left: camera p looking at t; right: camera q looking at u).
"""
import base64, io, os, sys
os.environ['FX1_ROLE'] = os.environ.get('BD1_ROLE', 'sugarloaf_canyon')
import fx1_stage
from PIL import Image


def grab(s, tag, pos, tgt):
    r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'bd1-' + tag,
                                                                      'camera_position': pos, 'look_at_position': tgt}})
    img = next(c for c in r['result']['content'] if c.get('type') == 'image')
    return Image.open(io.BytesIO(base64.b64decode(img['data']))).convert('RGB')


def main():
    name = sys.argv[1]
    v = [[float(x) for x in a.split(',')] for a in sys.argv[2:6]]
    s = fx1_stage.studio()
    a = grab(s, name + '-a', v[0], v[1]); b = grab(s, name + '-b', v[2], v[3])
    b = b.resize((int(b.width * a.height / b.height), a.height))
    out = Image.new('RGB', (a.width + b.width + 8, a.height), (255, 255, 255))
    out.paste(a, (0, 0)); out.paste(b, (a.width + 8, 0))
    out.save(fx1_stage.GAME / 'logs/stages' / (name + '.png'))
    print('saved', name, out.size)


if __name__ == '__main__':
    main()
