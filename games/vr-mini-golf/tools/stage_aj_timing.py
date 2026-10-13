#!/usr/bin/env python3
"""Run supplied H8 80-plan physics and a fixed-seed H15 seam stress test locally.
Usage: python3 tools/stage_aj_timing.py [--hole 8|15|both]
Requires the already-authorized local fix1 place in Edit. Starts/stops Play; never saves.
"""
import argparse
import json
import math
import statistics
import time
from pathlib import Path
from run_playtests import Studio

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'playtests/stage-aj'



def read_json_chunks(st, build_payload):
    """Snapshot server JSON once, then fetch below the MCP response size limit."""
    length = int(st.luau(build_payload + '\n_G.StageAjExport=payload return #payload', 'Server'))
    try:
        chunks = [st.luau(f'return string.sub(_G.StageAjExport,{start+1},{min(start+45000,length)})', 'Server')
                  for start in range(0, length, 45000)]
        raw = ''.join(chunks)
        assert len(raw.encode('utf-8')) == length, 'MCP JSON export was truncated'
        return json.loads(raw)
    finally:
        st.luau('_G.StageAjExport=nil return true', 'Server')


def summary(data):
    shots = sorted(data['shots'], key=lambda row: row['index'])
    values = sorted(row['stop_seconds'] for row in shots if 'stop_seconds' in row)
    def flagged(row, kind):
        return any(e['kind'] == kind for e in row['events'])
    return dict(hole=data['hole'], seed=data['seed'], approach=data.get('approach',False), total=len(shots), expected=80,
                definition=data['stop_definition'], rest_samples=len(values),
                median=statistics.median(values) if values else None,
                p90=values[math.ceil(.9*len(values))-1] if values else None,
                over_1_5=[r for r in shots if r.get('stop_seconds', 0)>1.5],
                forced_rest=[r for r in shots if flagged(r, 'forced_rest')],
                wedged=[r for r in shots if any(e['kind']=='forced_rest' and e['detail']=='wedged' for e in r['events'])],
                timeouts=[r for r in shots if r.get('outcome')=='timeout' or any(e['kind']=='auto_reset' and e['detail']=='timeout' for e in r['events'])],
                other_outcomes=[r for r in shots if r.get('outcome')!='stopped'], errors=data['errors'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hole', choices=['8','15','both'],default='both')
    parser.add_argument('--approach', action='store_true', help='Separate H15 approach-side test; requires --hole 15, preserves seam evidence')
    args=parser.parse_args()
    if args.approach and args.hole!='15': parser.error('--approach requires --hole 15')
    OUT.mkdir(parents=True,exist_ok=True)
    st=Studio()
    assert st.mode()[0]=='Edit', 'Must start in Edit'
    pre=json.loads(st.luau('return game:GetService("HttpService"):JSONEncode({place=game.PlaceId,network=game:FindFirstChildOfClass("NetworkClient")~=nil,role=workspace:GetAttribute("PlaceRole")})'))
    assert pre['place']==0 and not pre['network'] and pre['role']=='sugarloaf_canyon', pre
    try:
        st.start_play()
        for hole in ([8,15] if args.hole=='both' else [int(args.hole)]):
            prefix=f'h{hole}' + ('-approach' if args.approach else '')
            print(st.luau((HERE/'stage_aj_qa_setup.luau').read_text(),'Server'),flush=True)
            st.luau(f'game.ServerStorage.QA_SC:SetAttribute("Hole",{hole}) game.ServerStorage.QA_SC:SetAttribute("Approach",{str(args.approach).lower()}) return true','Server')
            print(st.luau((HERE/'stage_aj_timing.luau').read_text(),'Server'),flush=True)
            deadline=time.monotonic()+900
            while True:
                status=json.loads(st.luau('local r=game:GetService("HttpService"):JSONDecode(game.ServerStorage.QA_SC.Results.Value) return game:GetService("HttpService"):JSONEncode({done=r.done,shots=#r.shots,errors=#r.errors})','Server'))
                print(hole,status,flush=True)
                if status['done']==4: break
                if time.monotonic()>deadline: raise TimeoutError(status)
                time.sleep(10)
            data=read_json_chunks(st, 'local payload=game.ServerStorage.QA_SC.Results.Value')
            (OUT/f'{prefix}-timing.json').write_text(json.dumps(data,indent=2)+'\n')
            report=summary(data)
            (OUT/f'{prefix}-timing-summary.json').write_text(json.dumps(report,indent=2)+'\n')
            traces=read_json_chunks(st, 'local t={} for _,v in game.ServerStorage.QA_SC:GetChildren() do if v:IsA("StringValue") and v.Name:match("^Trace") then t[v.Name]=game:GetService("HttpService"):JSONDecode(v.Value) end end local payload=game:GetService("HttpService"):JSONEncode(t)')
            (OUT/f'{prefix}-timing-traces.json').write_text(json.dumps(traces)+'\n')
            print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()}),flush=True)
            st.luau('game.ServerStorage.QA_SC:Destroy() return true','Server')
        (OUT/('timing-approach-console.json' if args.approach else 'timing-console.json')).write_text(json.dumps({dm:st.problems(dm) for dm in ['Server','Client']},indent=2)+'\n')
    finally:
        st.stop_play()
        st.m.p.terminate()

if __name__=='__main__': main()
