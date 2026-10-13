"""Compare stage ah native samples with authored planes and solid felt slabs."""
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'playtests/stage-ah'


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def slab(f, x, z):
    """Vertical ray/OBB intersection from spec, including bank slab side faces.

    Same documented slab convention as CourseBuilder: size is horizontal top
    footprint, center is top center, thickness extrudes along negative normal.
    This independently intersects the resulting solid, without using live CFrames.
    """
    sl = f.get('slope') or {}
    axis, rise = sl.get('axis'), sl.get('rise', 0)
    sx, sz = f['size']
    theta = math.atan2(rise, sx if axis == 'x' else sz)
    c, s = math.cos(theta), math.sin(theta)
    if axis == 'x':
        basis = [(c, s, 0), (-s, c, 0), (0, 0, 1)]
        sx = math.hypot(sx, rise)
    elif axis == 'z':
        basis = [(1, 0, 0), (0, c, -s), (0, s, c)]
        sz = math.hypot(sz, rise)
    else:
        basis = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    yaw = math.radians(f.get('yaw', 0))
    cy, sy = math.cos(yaw), math.sin(yaw)
    basis = [(cy*a+sy*d, b, -sy*a+cy*d) for a, b, d in basis]
    t = f.get('thickness', .4)
    if axis and not f.get('overlay') and not (f.get('kind') == 'bridge' or f.get('solid') is False):
        t += abs(rise)
    center = [v-n*t/2 for v, n in zip(f['center'], basis[1])]
    rel = [a-b for a, b in zip([x, 10, z], center)]
    near, far = -math.inf, math.inf
    for b, extent in zip(basis, [sx/2, t/2, sz/2]):
        o, d = dot(rel, b), -b[1]
        if abs(d) < 1e-10:
            if abs(o) > extent+1e-7:
                return None
        else:
            ends = sorted([(-extent-o)/d, (extent-o)/d])
            near, far = max(near, ends[0]), min(far, ends[1])
    return 10-near if near <= far+1e-7 else None


def top(f, x, z):
    a = math.radians(f.get('yaw', 0))
    dx, dz = x-f['center'][0], z-f['center'][2]
    u, w = math.cos(a)*dx-math.sin(a)*dz, math.sin(a)*dx+math.cos(a)*dz
    if abs(u) > f['size'][0]/2+1e-7 or abs(w) > f['size'][1]/2+1e-7:
        return None
    sl = f.get('slope')
    return f['center'][1] + (sl['rise']*(u/f['size'][0] if sl['axis']=='x' else w/f['size'][1]) if sl else 0)


def main():
    summary = {'method': '0.1-stud native collidable GolfSurface rays; seam +/-0.001 and +/-0.01 probes. '
               'Independent authored plane/solid-box comparison; bank sides distinguished from ramp seam. '
               'Cup interior excluded: CSG ray collision representation does not establish physical cup entry.'}
    for spec in json.loads((OUT/'authored-h6-h18.json').read_text()):
        number = spec['number']
        data = json.loads((OUT/f'h{number}-profile.json').read_text())
        report = {'grids': {}, 'hazards': data['hazards']}
        for name, rows in data['grids'].items():
            errors, sidehits, misses, excluded = [], [], [], 0
            lookup = {(round(x, 5), round(z, 5)): hit for x, z, hit in rows}
            changes = []
            for x, z, hit in rows:
                cup = spec['cup']['position']
                if math.hypot(x-cup[0], z-cup[2]) < spec['cup']['radius']+.001:
                    excluded += 1
                    continue
                boxes = [(v, f['id']) for f in spec['felt'] if (v := slab(f, x, z)) is not None]
                planes = [(v, f['id']) for f in spec['felt'] if (v := top(f, x, z)) is not None]
                expected = max(boxes) if boxes else None
                authored = max(planes) if planes else None
                if expected and hit:
                    errors.append([abs(hit[0]-expected[0]), x, z, hit[0], expected[0]])
                    if authored and abs(expected[0]-authored[0]) > .001:
                        sidehits.append([x, z, hit[0], hit[1], authored[0], expected[0]])
                elif expected and not hit:
                    misses.append([x, z, expected])
                for dx, dz in [(0.1, 0), (0, 0.1)]:
                    other = lookup.get((round(x+dx, 5), round(z+dz, 5)))
                    if hit and other and abs(hit[0]-other[0]) > .02:
                        changes.append([x, z, x+dx, z+dz, abs(hit[0]-other[0]), hit[1], other[1]])
            report['grids'][name] = {
                'samples': len(rows), 'cup_interior_excluded': excluded,
                'max_solid_height_error': max((r[0] for r in errors), default=0),
                'worst_solid_height_errors': sorted(errors, reverse=True)[:5],
                'top_footprint_vs_slab_side_hits': len(sidehits),
                'side_examples': sidehits[:5],
                'expected_hit_but_missed': misses,
                'neighbor_height_changes_over_0_02': len(changes),
                'max_neighbor_height_change': max((r[4] for r in changes), default=0),
                'largest_neighbor_changes': sorted(changes, key=lambda r:r[4], reverse=True)[:5],
            }
        if number == 18:
            feet = [r for r in data['seams'] if abs(r['z']+28.001)<1e-7]
            report['ramp_foot'] = {
                'probed_x_range': [-17.4, -9.6], 'cross_sections': len(feet),
                'max_extrapolated_ramp_intercept_error': max(abs(r['ramp'][0]-.00008) for r in feet),
                'missing_ramp_support_at_minus_0_001': sum(not r['ramp'] for r in feet),
                'missing_joint_support': sum(not r['all'] for r in data['seams']),
                'expected_rise_per_0_1_stud': .008,
            }
        else:
            east = next(r for r in data['seams'] if r['axis']=='x' and abs(r['x']-.6)<1e-7 and r['z']==-54)
            report['east_pad_lip'] = {'native':east['pad'][0]-east['shelf'][0],
                                      'authored':-top(next(f for f in spec['felt'] if f['id']=='shelf'), .6, -54)}
        summary[f'h{number}'] = report
    summary['stop_rules'] = {'RollDecel': .5, 'RollDrag': .25, 'EngineRollLoss': .2,
                            'StopSpeed': .2, 'RestTime': .5,
                            'gentle_slope_max_degrees':math.degrees(math.asin(.5/32.7))}
    for key, grade in [('h18_ramp', .08), ('h6_shelf', .3331/23), ('h18_bank', 1)]:
        summary['stop_rules'][key] = {'grade':grade,'degrees':math.degrees(math.atan(grade)),
                                      'slopeAccel':32.7*grade/math.sqrt(1+grade*grade)}
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    for key in ['h6','h18']:
        print(key, json.dumps({k:{'samples':v['samples'], 'error':v['max_solid_height_error'],
             'side_hits':v['top_footprint_vs_slab_side_hits'], 'misses':len(v['expected_hit_but_missed'])}
             for k,v in summary[key]['grids'].items()}))


if __name__ == '__main__':
    main()
