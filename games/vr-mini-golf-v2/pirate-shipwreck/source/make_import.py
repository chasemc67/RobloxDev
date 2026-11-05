#!/usr/bin/env python3
"""Build import/import_world.luau (and a mock-test variant in /tmp) from data/*."""
import json, os, base64, sys, math
import numpy as np, zstandard as z
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
Q = 16
def lua(v, ind=0):
    if isinstance(v, bool): return 'true' if v else 'false'
    if v is None: return 'nil'
    if isinstance(v, (int, float)): return repr(float(v)) if isinstance(v, float) else str(v)
    if isinstance(v, str): return json.dumps(v, ensure_ascii=True)
    if isinstance(v, list): return '{' + ', '.join(lua(x) for x in v) + '}'
    if isinstance(v, dict): return '{' + ', '.join(f'[{json.dumps(k)}] = {lua(x)}' for k, x in v.items()) + '}'
    raise TypeError(type(v))
def chunks(b, n=3000):
    s = base64.b64encode(b).decode()
    return '{\n' + ''.join(f'\t"{s[i:i+n]}",\n' for i in range(0, len(s), n)) + '}'
def blobs(compress=True):
    h = np.asarray(Image.open(f'{ROOT}/data/heightmap.png')).astype(np.int64) // Q
    d = np.diff(h, axis=1, prepend=0).astype('<i2').tobytes()
    m = np.asarray(Image.open(f'{ROOT}/data/materialmap.png')).astype(np.uint8).tobytes()
    if compress:
        c = z.ZstdCompressor(level=19); return c.compress(d), c.compress(m)
    return d, m
world = json.load(open(f'{ROOT}/data/world.json')); world['height']['quant'] = Q
P = json.load(open(f'{ROOT}/data/placements.json'))
P_small = {k: v for k, v in P.items() if k not in ('trail',)}
L = json.load(open(f'{ROOT}/data/lighting.json'))
tmpl = open(f'{HERE}/import_template.luau').read()
def data_block(compress):
    hz, mz = blobs(compress)
    return (f'-- embedded data: heightmap = int16 row-delta of (stud height quantised to {Q}/65535 of the range), material map = u8 ids; both zstd + base64\n'
            f'local WORLD = {lua(world)}\nlocal PLACEMENTS = {lua(P_small)}\nlocal LIGHTING = {lua(L)}\n'
            f'local HEIGHT_Z = {chunks(hz)}\nlocal MATERIAL_Z = {chunks(mz)}\n')
out = tmpl.replace('--@@DATA@@', data_block(True))
os.makedirs(f'{ROOT}/import', exist_ok=True)
open(f'{ROOT}/import/import_world.luau', 'w').write(out)
print('import_world.luau', len(out), 'chars')
# test variant: uncompressed blobs + mocks (see source/mock_prelude.luau)
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    pre = open(f'{HERE}/mock_prelude.luau').read()
    open('/tmp/import_test.luau', 'w').write(pre + '\n' + tmpl.replace('--@@DATA@@', data_block(False)))
