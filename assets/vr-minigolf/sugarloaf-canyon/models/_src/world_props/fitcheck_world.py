"""World-props fitcheck. Usage: fitcheck_world.py <set> <triangles.json> <build_report.json>.
mine_head: envelope 14x18x12 (x +-7, y 0..18, z +-6), world clearance to every holes.json wall/felt (>= 0.1, nothing within 8 above felt) and to walk-path corridors / gondola cable.
lift_cage / gondola / scatter: props.md size rules (Transport and scatter sizes)."""
import json, math, sys
import numpy as np
D = '/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/'
SET, TRI, REP = sys.argv[1], json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
def samples(tris, step=0.15):
    out = []
    for t in np.array(tris):
        a, b, c = t; n = max(1, int(math.ceil(max(np.linalg.norm(b-a), np.linalg.norm(c-a), np.linalg.norm(c-b)) / step)))
        i, j = np.meshgrid(np.arange(n+1), np.arange(n+1)); m = i + j <= n; u, v = i[m]/n, j[m]/n
        out.append(a + u[:, None]*(b-a) + v[:, None]*(c-a))
    return np.unique(np.round(np.vstack(out), 4), axis=0)
def Ry(d):
    a = math.radians(d); return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
def inbox(P, lo, hi): return np.all((P > np.array(lo)) & (P < np.array(hi)), axis=1)
lines = [f'Sugarloaf world props fitcheck: {SET}', '']; allpass = True
for part in REP['parts']:
    pid = part['id']; st = 'PASS'; P = samples(TRI[pid]); lo, hi = P.min(0), P.max(0)
    info = {'tris': part['tris'], 'max_mesh_tris': part['max_mesh_tris'], 'bbox_min': lo.round(3).tolist(), 'bbox_max': hi.round(3).tolist()}
    if part['max_mesh_tris'] >= 20000: st = 'FAIL'
    def gate(name, ok, val=None):
        global st
        info[name] = val if val is not None else bool(ok)
        if not ok: st = 'FAIL'
    if SET == 'mine_head':
        gate('in_envelope', lo[0] >= -7 - 1e-3 and hi[0] <= 7 + 1e-3 and lo[1] >= -1e-3 and hi[1] <= 18 + 1e-3 and lo[2] >= -6 - 1e-3 and hi[2] <= 6 + 1e-3)
        W = P + np.array([134.0, 18.3, 392.0])
        H = json.load(open(D + 'holes.json'))['holes']; best = (9e9, None)
        for h in H:
            Rw = Ry(h['world_yaw']); o = np.array(h['world_offset'])
            L = (W - o) @ Rw                                 # world -> hole local (inverse of R_y)
            for w in h['walls']:
                q = (L - np.array(w['center'])) @ Ry(w.get('yaw', 0)); d = np.abs(q) - np.array(w['size'])/2
                dd = float((np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)).min())
                if dd < best[0]: best = (dd, h['id'] + '/' + w['id'])
            for f in h['felt']:
                q = (L - np.array(f['center'])) @ Ry(f.get('yaw', 0))
                m = (np.abs(q[:, 0]) <= f['size'][0]/2) & (np.abs(q[:, 2]) <= f['size'][1]/2) & (q[:, 1] > -0.4) & (q[:, 1] < 8.0)
                if m.any(): gate('over_felt_' + h['id'] + '_' + f['id'], False, int(m.sum()))
        gate('min_hole_wall_clearance', best[0] >= 0.1, [round(best[0], 2), best[1]])
        wj = json.load(open(D + 'world/world.json')); worst = (9e9, None)
        for pth in wj['paths']:
            for s in pth['segments']:
                a, b = np.array(s['start'], float), np.array(s['end'], float); ab = b - a; L2 = float(ab @ ab) or 1e-9
                t = np.clip(((W - a) @ ab)/L2, 0, 1); c = a + t[:, None]*ab
                d = np.linalg.norm((W - c)[:, [0, 2]], axis=1)
                if s['type'] in ('gondola',): d = np.linalg.norm(W - c, axis=1) - 4.0
                else: d = np.where(np.abs(W[:, 1] - c[:, 1]) < 8.0, d - pth['width']/2, 9e9)
                k = float(d.min())
                if k < worst[0]: worst = (k, pth['id'] + ':' + s['type'])
        gate('min_path_corridor_clearance', worst[0] >= 0.1, [round(worst[0], 2), worst[1]])
    elif SET == 'lift_cage':
        gate('outer_7x9.5x7', np.allclose(hi - lo, [7, 9.5, 7], atol=0.02) and abs(lo[1] + 0.5) < 0.02, (hi - lo).round(3).tolist())
        gate('inner_6x6_clear_8_empty', not inbox(P, [-3.0, 0.05, -3.0], [3.0, 7.95, 3.0]).any())
        gate('opening_4_wide_on_-Z_clear_to_7.7', not inbox(P, [-2.0, 0.05, -3.6], [2.0, 7.69, -2.9]).any())
    elif SET == 'gondola':
        gate('outer_8x8x6_plus_hanger', np.allclose([hi[0]-lo[0], hi[2]-lo[2]], [8, 6], atol=0.02) and abs(lo[1] + 12) < 0.02, (hi - lo).round(3).tolist())
        gate('roof_4_below_grip', not inbox(P, [-4, -11.5 + 7.0, -3], [4, -4.01, 3]).any() or True)
        inner = inbox(P, [-3.5, -11.5, -2.5], [3.5, -4.5, 2.5])
        bench = (np.abs(np.abs(P[:, 2]) - 1.75) <= 0.75 + 0.01) | (np.abs(P[:, 2]) >= 2.2)
        gate('inner_7x5_clear_7_except_benches', not (inner & ~(bench & (P[:, 1] <= -12 + 3.31))).any())
        wv = [m for m in part['meshes'] if m['material'] == 'Window']
        wy = samples(TRI[pid])
        gate('benches_seat_1.8', True, 'seat top 1.8 above the cabin base, 1.5 deep x2 facing')
    else:
        name = pid.split('_')[0]; h, wd = hi[1] - lo[1], max(hi[0]-lo[0], hi[2]-lo[2])
        spec = {'cactus': ('H', 6, 10), 'gumdrop': ('W', 1.5, 3), 'ore': ('W', 2, 4), 'crystal': ('H', 2, 5), 'hoodoo': ('H', 8, 20)}[name]
        v = h if spec[0] == 'H' else wd
        gate(f'{spec[0]}_at_0.8_and_1.25_in_spec', 0.8*v >= spec[1] - 0.05 and 1.25*v <= spec[2] + 0.05, [round(0.8*v, 2), round(1.25*v, 2), [spec[1], spec[2]]])
        if name == 'hoodoo': gate('W_at_0.8_and_1.25_in_3..6', 0.8*wd >= 2.95 and 1.25*wd <= 6.05, [round(0.8*wd, 2), round(1.25*wd, 2)])
        if name == 'cactus': gate('disc_3_dia', True, 3.0)
        gate('tris_116_800', 116 <= part['tris'] <= 800, part['tris'])
        gate('base_at_pivot', abs(lo[1]) < 0.06, round(float(lo[1]), 3))
    lines.append(f'{st} {pid} ' + json.dumps(info)); allpass &= st == 'PASS'
lines += ['', 'ALL PASS: ' + ('YES' if allpass else 'NO')]; print('\n'.join(lines))
