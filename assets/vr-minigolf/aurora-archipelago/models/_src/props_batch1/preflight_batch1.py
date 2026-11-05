"""Reproduce source-level contradictions without changing geometry or starting Blender."""
import hashlib
import json
import math
from pathlib import Path

DIR = Path(__file__).resolve().parents[3]
raw = (DIR / 'holes.json').read_bytes()
assert hashlib.md5(raw).hexdigest() == '20c4e3f92f8100bfb9da07732e622199'
holes = {h['number']: h for h in json.loads(raw)['holes']}
anchor = next(a for a in holes[5]['decoration_anchors'] if a['name'] == 'steamwhistle_geyser')
felt = next(f for f in holes[5]['felt'] if f['id'] == 'upper')
occluder = anchor['occluders'][0]
felt_x = [felt['center'][0] - felt['size'][0]/2, felt['center'][0] + felt['size'][0]/2]
felt_z = [felt['center'][2] - felt['size'][1]/2, felt['center'][2] + felt['size'][1]/2]
occ_x = [occluder['center'][0] - occluder['size'][0]/2, occluder['center'][0] + occluder['size'][0]/2]
occ_z = [occluder['center'][2] - occluder['size'][2]/2, occluder['center'][2] + occluder['size'][2]/2]
overlap_x = min(felt_x[1], occ_x[1]) - max(felt_x[0], occ_x[0])
overlap_z = min(felt_z[1], occ_z[1]) - max(felt_z[0], occ_z[0])
assert overlap_x > 0 and overlap_z > 0
assert felt_x[0] < anchor['position'][0] < felt_x[1]
assert felt_z[0] < anchor['position'][2] < felt_z[1]
assert anchor['position'][1] == felt['center'][1]
boulder = next(w for w in holes[1]['walls'] if w['id'] == 'boulder')
rail = next(w for w in holes[1]['walls'] if w['id'] == 'rail1')
angle = math.radians(boulder['yaw'])
extent = abs(math.cos(angle))*boulder['size'][0]/2 + abs(math.sin(angle))*boulder['size'][2]/2
west_x = boulder['center'][0] - extent
clearance = west_x - (rail['center'][0] + rail['size'][0]/2)
assert 0 < clearance < 0.1
print(json.dumps({
    'source_md5': hashlib.md5(raw).hexdigest(),
    'h05_steamwhistle_geyser': {
        'status': 'FAIL', 'anchor': anchor['position'],
        'upper_felt_x': felt_x, 'upper_felt_z': felt_z,
        'forbidden_y_open_interval': [4, 12],
        'occluder_x': occ_x, 'occluder_z': occ_z,
        'occluder_y': [4, 11],
        'occluder_felt_overlap_xz': [overlap_x, overlap_z],
        'reason': 'Required static cone occupies upper felt head-clearance volume.'
    },
    'h01_snow_boulder': {
        'status': 'FAIL', 'nearest_other_wall': 'rail1',
        'exact_footprint_west_x': west_x,
        'clearance_studs': clearance, 'required_studs': 0.1,
        'reason': 'Exact collider-covering base cannot meet clearance from another rail.'
    },
    'all_pass': False
}, indent=2))
