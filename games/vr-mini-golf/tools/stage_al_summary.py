#!/usr/bin/env python3
"""Summarize Stage al evidence only (no Studio calls, no inferred missing passes).

Run from any directory; defaults resolve relative to this script's game directory.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]


def shot_flags(shot):
    return [f for f in shot.get('flags', []) if isinstance(f, dict)]


def shot_counts(shots):
    counts = dict(stuck=0, escapes=0, native_timeouts=0, harness_timeouts=0)
    for shot in shots:
        flags = shot_flags(shot)
        counts['stuck'] += int(shot.get('outcome') in ('stuck', 'wedged', 'timeout') or any(f.get('kind') in ('stuck', 'stuck-3s', 'stuck-timeout', 'offsurface', 'forcedrest') for f in flags))
        counts['escapes'] += int(shot.get('outcome') == 'escape' or any(f.get('kind') in ('escape', 'escaped') for f in flags))
        counts['native_timeouts'] += int(bool(shot.get('nativeTimeout')) or any(f.get('reason') == 'timeout' and f.get('kind') == 'autoreset' for f in flags))
        counts['harness_timeouts'] += int(shot.get('outcome') == 'timeout')
    counts['timeouts'] = sum(int(s.get('outcome') == 'timeout' or s.get('nativeTimeout') or any(f.get('reason') == 'timeout' for f in shot_flags(s))) for s in shots)
    return counts


def build(root, holes_path):
    missing, problems = [], []
    def read(rel, fallback):
        path = root / rel
        if not path.exists():
            missing.append(rel)
            return fallback
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError) as e:
            problems.append(f'{rel}: {e}')
            return fallback
    results = read('sweep/results.json', {})
    console = read('console.json', {})
    friction = read('h15-friction-summary.json', {})
    coplanar = read('final-coplanar.json', None)
    definitions = json.loads(holes_path.read_text())['holes']
    mover_holes = [h['number'] for h in definitions if h.get('moving_parts')]
    rows, details = [], []
    for n in range(1, 19):
        d = results.get(f'h{n}', {}).get('default', {})
        row = dict(hole=n, course=d.get('course'), expected_slow=6 if n in mover_holes else 0,
                   cups_attempted=0, cups_sunk=0, random=0, slow=0, stuck=0, escapes=0,
                   native_timeouts=0, harness_timeouts=0, timeouts=0)
        if not d:
            problems.append(f'H{n}: missing default result')
        if d.get('error'):
            problems.append(f'H{n}: scenario error {d["error"]}')
        if d.get('course') != 'sugarloaf_canyon':
            problems.append(f'H{n}: wrong or missing course {d.get("course")!r}')
        cup = d.get('cupdrop', {})
        tries = cup.get('tries', [])
        row['cups_attempted'] = len(tries)
        row['cups_sunk'] = sum(t.get('outcome') in ('cup', 'sunk') for t in tries)
        if cup.get('sunk') != row['cups_sunk'] or cup.get('n') != len(tries):
            problems.append(f'H{n}: cupdrop aggregate/tries mismatch')
        if len(tries) != 3 or row['cups_sunk'] != 3:
            problems.append(f'H{n}: cupdrop {row["cups_sunk"]}/{len(tries)}, expected 3/3')
        for key, count_key, expected in [('fuzz', 'random', 8), ('slow', 'slow', row['expected_slow'])]:
            block = d.get(key, {})
            shots = block.get('allShots', [])
            row[count_key] = len(shots)
            if len(shots) != expected or block.get('shots', 0) != len(shots):
                problems.append(f'H{n}: {key} expected {expected}, records {len(shots)}, aggregate {block.get("shots", 0)}')
            if any(s.get('outcome') == 'refused' for s in shots):
                problems.append(f'H{n}: {key} contains refused shots')
            counts = shot_counts(shots)
            # Preserve aggregate findings even when individual records omit flags.
            for metric in ('stuck', 'escapes', 'timeouts'):
                counts[metric] = max(counts[metric], int(block.get(metric, 0)))
            for metric, count in counts.items():
                row[metric] += count
            for shot in shots:
                if any(shot_counts([shot]).values()):
                    details.append(dict(hole=n, group=key, shot=shot))
        for metric in ('stuck', 'escapes'):
            row[metric] = max(row[metric], int(d.get(metric, 0)))
        row['issues'] = len(d.get('issues', []))
        rows.append(row)
    console_entries = [dict(side=k, entry=v) for k, values in console.items() if isinstance(values, list) for v in values]
    errors, warnings, unknown = [], [], []
    for entry in console_entries:
        value = entry['entry']
        severity = str(value if isinstance(value, str) else value.get('type', value.get('messageType', value.get('level', '')))).upper()
        if 'ERROR' in severity:
            errors.append(entry)
        elif 'WARN' in severity:
            warnings.append(entry)
        else:
            unknown.append(entry)
    if not any(k.lower() == 'server' for k in console) or not any(k.lower() == 'client' for k in console):
        problems.append('Console evidence must cover Server and Client')
    if unknown:
        problems.append('Console entries have unrecognized severity; inspect manually')
    if not isinstance(coplanar, list):
        problems.append('final-coplanar.json must be the scan result list')
    for run in ('before', 'after'):
        c = friction.get('counts', {}).get(run, {})
        if c.get('shots') != 80 or sum(c.get(k, 0) for k in ('wedge_seam', 'crawl_lean', 'timeout', 'rest', 'sunk')) != 80:
            problems.append(f'H15 {run}: expected 80 classified shots')
    if friction.get('paired_manifest_identical') is not True:
        problems.append('H15 paired manifest equality not verified')
    metrics = ('cups_attempted', 'cups_sunk', 'random', 'slow', 'stuck', 'escapes', 'native_timeouts', 'harness_timeouts', 'timeouts', 'issues')
    totals = {key: sum(r[key] for r in rows) for key in metrics}
    totals.update(coplanar_left=len(coplanar) if isinstance(coplanar, list) else None,
                  console_errors=len(errors), console_warnings=len(warnings), console_unknown=len(unknown))
    status = 'PASS' if not missing and not problems and not errors and totals['coplanar_left'] == 0 and not any(totals[k] for k in ('stuck', 'escapes', 'timeouts')) else 'PARTIAL'
    return dict(status=status, scope='Evidence validation; does not assert local save/close/commit', summary=totals,
                expected=dict(holes=18, cupdrop=54, random=144, slow=6 * len(mover_holes), mover_holes=mover_holes),
                missing_inputs=missing, validation_problems=problems, holes=rows, flagged_shots=details,
                console=dict(errors=errors, warnings=warnings, unknown=unknown), h15_friction=friction,
                holes_input=dict(path=str(holes_path), sha256=hashlib.sha256(holes_path.read_bytes()).hexdigest()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=GAME / 'playtests/stage-al')
    parser.add_argument('--holes', type=Path, default=GAME.parents[1] / 'assets/vr-mini-golf/sugarloaf-canyon/holes.json')
    args = parser.parse_args()
    result = build(args.root, args.holes)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / 'verification-summary.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.root / 'verification-per-hole.json').write_text(json.dumps(result['holes'], indent=2) + '\n')
    with (args.root / 'verification-per-hole.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(result['holes'][0]))
        writer.writeheader()
        writer.writerows(result['holes'])
    print(json.dumps({k: result[k] for k in ('status', 'summary', 'expected', 'missing_inputs', 'validation_problems')}, indent=2))


if __name__ == '__main__':
    main()
