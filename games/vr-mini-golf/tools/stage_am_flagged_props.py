"""Write every source-real and built prop-class clearance finding for stage am.
Safe to run before capture: missing built evidence is explicitly marked pending.
"""
import json
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'playtests/stage-am'
ASSET = GAME.parents[1] / 'assets/vr-mini-golf/aurora-archipelago'
sys.path.insert(0, str(ASSET / 'tools'))
import deco_clearance as dc


def write_report():
    source = json.loads((OUT / 'deco_clearance.json').read_text())
    real = [r for r in source if dc.is_real(r)]
    source_ids = {(r['hole'], r['anchor']) for r in real}
    lines = [
        '# Stage am flagged props', '',
        'Gap is the signed XZ separating-axis gap in studs used by the checker: negative means bounds overlap, zero means touching. Wall/prop clearance target is 0.15 studs; felt checks use its -0.4 to +8 stud vertical headroom region. These are bounds findings, not triangle-confirmed intersections.', '',
        '## Source checker — real findings', '',
        f'{len(source)} raw findings; **{len(real)} real findings on {len(source_ids)} unique props**. Every real finding is listed below; non-prop dressing, flat, envelope and accepted-exception findings are retained in deco_clearance.json.', '',
        '| Hole | Flagged prop | Class | Gap (studs) | Too close to |',
        '|---|---|---|---:|---|',
    ]
    for r in real:
        lines.append(f"| {r['hole']} | {r['anchor']} | {r['cls']} | {r['sep']:.5f} | {r['kind']}: {r['other']} |")
    lines += ['', '## Built-place audit — prop class', '']
    path = OUT / 'built-clearance.json'
    summary = {'source_real_findings': len(real), 'source_unique_props': len(source_ids), 'source_props': [{'hole': h, 'name': n} for h, n in sorted(source_ids)]}
    if not path.exists():
        lines += ['Pending the final Studio bounds capture; no built-place result is claimed.']
        summary['built_status'] = 'pending'
    else:
        built = json.loads(path.read_text())
        rows = [r for r in built['props'] + built['anchors'] if r['cls'] == 'prop' and r['hits']]
        n = sum(len(r['hits']) for r in rows)
        nr = sum(bool(h['real']) for r in rows for h in r['hits'])
        built_ids = {(r['hole'], r['anchor']) for r in rows}
        lines += [
            built['summary']['method'], '',
            f'**{n} prop-class findings on {len(built_ids)} unique props** ({nr} findings pass the source checker real-finding rule). Every prop-class finding is listed, including hits against loose envelopes/decals excluded by that rule. Unique props use (hole, authored anchor), so imported and retained anchor representations do not inflate the count.', '',
            '| Hole | Built prop | Class | Gap (studs) | Too close to | Real | Meshes |',
            '|---|---|---|---:|---|---|---|',
        ]
        for r in rows:
            for hit in r['hits']:
                lines.append(f"| {r['hole']} | {r['id']} | {r['cls']} | {hit['sep']:.5f} | {hit['kind']}: {hit['other']} | {'yes' if hit['real'] else 'no'} | {', '.join(sorted(set(hit['meshes'])))} |")
        union = source_ids | built_ids
        summary.update(built_status='complete', built_prop_class_findings=n, built_real_findings=nr, built_unique_props=len(built_ids), unique_flagged_props=len(union), built_props=[{'hole': h, 'name': a} for h, a in sorted(built_ids)])
        lines += ['', f'Combined source/built **FLAGGED={len(union)} unique props**; counts are not the number of overlap pairs.']
    (OUT / 'flagged-props.md').write_text('\n'.join(lines) + '\n')
    (OUT / 'flagged-props-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))
    return summary


if __name__ == '__main__':
    write_report()
