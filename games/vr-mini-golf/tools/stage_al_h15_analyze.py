#!/usr/bin/env python3
"""Write paired H15 CSV and summary from h15friction run directories (no Studio calls).

python3 tools/stage_al_h15_analyze.py playtests/stage-al/h15-before playtests/stage-al/h15-after --out playtests/stage-al
"""
import argparse
import collections
import csv
import json
from pathlib import Path


def read_run(path):
    result = json.loads((path / 'results.json').read_text())['h15friction']
    result = result.get('default', next(iter(result.values())))
    if result.get('error'):
        raise ValueError(result['error'])
    if len(result.get('shots', [])) != 80:
        raise ValueError(f'{path}: expected 80 shots')
    if any(s['outcome'] == 'refused' for s in result['shots']):
        raise ValueError(f'{path}: refused shots do not count')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('before', type=Path)
    ap.add_argument('after', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    runs = {'before': read_run(a.before), 'after': read_run(a.after)}
    if runs['before']['manifest'] != runs['after']['manifest']:
        raise ValueError('BEFORE/AFTER shot manifests differ; comparison is invalid')
    a.out.mkdir(parents=True, exist_ok=True)
    fields = ['run', 'shot', 'start_x', 'start_y', 'start_z', 'speed', 'direction',
              'direction_x', 'direction_y', 'direction_z', 'outcome', 'stop_time_s',
              'crawl_location_x', 'crawl_location_y', 'crawl_location_z', 'category', 'group', 'native_timeout', 'native_flags']
    summary = {'seed': runs['before']['seed'], 'paired_manifest_identical': True,
               'classification': runs['before']['classification'], 'counts': {}}
    with (a.out / 'h15-friction-log.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, run in runs.items():
            counts = collections.Counter(s['category'] for s in run['shots'])
            summary['counts'][name] = {k: counts[k] for k in ['wedge_seam', 'crawl_lean', 'timeout', 'rest', 'sunk']}
            summary['counts'][name]['raw_timeouts'] = sum(s['outcome'] == 'timeout' or s.get('nativeTimeout', False) for s in run['shots'])
            summary['counts'][name]['escapes'] = sum(s['outcome'] == 'escape' for s in run['shots'])
            summary['counts'][name]['shots'] = len(run['shots'])
            for shot in run['shots']:
                row = {k: shot.get(k, '') for k in ['shot', 'speed', 'outcome', 'stop_time_s', 'category', 'group']}
                row['run'] = name
                row['native_timeout'] = bool(shot.get('nativeTimeout') or shot.get('outcome') == 'timeout')
                row['native_flags'] = ';'.join(f.get('kind', '') + ':' + f.get('reason', '') for f in shot.get('flags', []))
                row['direction'] = json.dumps(shot['direction'], separators=(',', ':'))
                for key, values in [('start', shot['start']), ('direction', shot['direction']),
                                    ('crawl_location', shot.get('crawl_location') or ['', '', ''])]:
                    row.update({key + '_' + axis: v for axis, v in zip('xyz', values)})
                w.writerow(row)
    (a.out / 'h15-friction-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (a.out / 'h15-friction-manifest.json').write_text(json.dumps(runs['before']['manifest'], indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
