#!/usr/bin/env python3
"""Run one H15 friction pass, persisting a heartbeat and rows every 30s. LOCAL ONLY.
Usage: python3 tools/stage_al_h15_run.py before [--manifest-only]
The caller pushes src first and changes physics only between completed paired runs.
"""
import argparse
import csv
import json
import time
from pathlib import Path
from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api, fetch_log, GAME_DIR


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run', choices=['before', 'after'])
    ap.add_argument('--manifest-only', action='store_true')
    a = ap.parse_args()
    out = Path(GAME_DIR) / 'playtests/stage-al' / ('h15-' + a.run + ('-manifest' if a.manifest_only else ''))
    out.mkdir(parents=True, exist_ok=True)
    st = Studio()
    st.stop_play()
    assert st.luau("return tostring(game.PlaceId) .. ':' .. tostring(game:FindFirstChildOfClass('NetworkClient') == nil)").strip() == '0:true', 'Local offline edit place required'
    opts = {'course': 'sugarloaf_canyon', 'seed': 20261013, 'h15ManifestOnly': a.manifest_only}
    set_edit_attrs(st, {'GolfTestMode': True, 'SimulateVR': False, 'GolfTestOpts': json.dumps(opts)})
    try:
        st.start_play()
        wait_api(st)
        assert st.api('start', 'h15friction', '') == 'started'
        started = last_flush = time.monotonic()
        while True:
            time.sleep(5)
            status = json.loads(st.api('status'))
            if time.monotonic() - last_flush >= 30 or not status.get('running'):
                lines, cursor = [], 1
                target = status.get('lines', 0)
                while cursor <= target:
                    text = st.api('log', cursor, 60000)
                    head, _, body = text.partition('\n')
                    if body: lines.extend(body.splitlines())
                    nxt = int(head)
                    if nxt <= cursor: break
                    cursor = nxt
                (out / 'h15friction.jsonl').write_text('\n'.join(lines) + '\n')
                rows = [v for line in lines if (v := json.loads(line)).get('event') == 'h15-friction-row']
                (out / 'shots-progress.json').write_text(json.dumps(rows, indent=1) + '\n')
                with (out / 'shots-progress.csv').open('w', newline='') as f:
                    fields = ['run', 'shot', 'start_x', 'start_y', 'start_z', 'speed', 'direction', 'outcome', 'stop_time_s', 'crawl_location_x', 'crawl_location_y', 'crawl_location_z', 'category']
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()
                    for r in rows:
                        row = {k: r.get(k, '') for k in ['shot', 'speed', 'outcome', 'stop_time_s', 'category']}
                        row.update(run=a.run, direction=json.dumps(r['direction']))
                        for prefix, values in [('start', r['start']), ('crawl_location', r.get('crawl_location') or ['', '', ''])]:
                            row.update({prefix + '_' + axis: v for axis, v in zip('xyz', values)})
                        writer.writerow(row)
                print(json.dumps({'run': a.run, 'shots_complete': len(rows), 'elapsed_s': round(time.monotonic()-started), 'status': status}), flush=True)
                last_flush = time.monotonic()
            if not status.get('running'):
                break
            if time.monotonic() - started > 3180:
                raise TimeoutError('H15 experiment exceeded 3180s; partial rows preserved')
        length = int(st.luau("_G.StageALResult=game.ReplicatedStorage.GolfTestAPI:Invoke('result','h15friction') return #_G.StageALResult", 'Client'))
        raw = ''.join(st.luau(f'return _G.StageALResult:sub({i+1},{i+45000})', 'Client') for i in range(0, length, 45000))
        result = json.loads(raw)
        st.luau('_G.StageALResult=nil return true', 'Client')
        (out / 'results.json').write_text(json.dumps({'h15friction': {'default': result}}, indent=1) + '\n')
        problems = {'server': st.problems('Server'), 'client': st.problems('Client')}
        (out / 'problems.json').write_text(json.dumps(problems, indent=1) + '\n')
        assert not result.get('error'), result.get('error')
        if not a.manifest_only:
            assert len(result.get('shots', [])) == 80
        assert not any(str(m).startswith('ERROR') for messages in problems.values() for m in messages), problems
        print('PASS ' + str(out), flush=True)
    finally:
        st.stop_play()
        clear_test_attrs(st)


if __name__ == '__main__':
    main()
