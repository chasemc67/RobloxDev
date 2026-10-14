#!/usr/bin/env python3
"""Native H17 solid crossings and mistimed hazard returns; local Play only, never saves."""
import json
import time
from pathlib import Path
from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api, long_string

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'playtests/stage-am'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    st=Studio()
    assert st.mode()[0]=='Edit'
    assert st.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
    source=(HERE/'stage_am_h17.luau').read_text()
    plans=[dict(kind='timed',phase=p,speed=8) for p in [1,1.5,2,2.5,3,3.5]]
    plans += [dict(kind='mistimed',phase=p,speed=8) for p in [6.8,7.1,7.4]]
    rows=[]
    try:
        set_edit_attrs(st,{'GolfTestMode':True,'SimulateVR':False,'GolfTestOpts':json.dumps({'course':'aurora_archipelago'})})
        st.start_play(); wait_api(st)
        for index,plan in enumerate(plans,1):
            plan['index']=index
            code=source.replace('__PLAN__',json.dumps(json.dumps(plan)))
            # A normal LocalScript shares the gameplay module cache; MCP does not.
            wrapper='''local result=game.ReplicatedStorage:WaitForChild("StageAMH17Result")
local ok,value=xpcall(function()
'''+code+'''
end,debug.traceback)
result.Value=ok and value or game:GetService("HttpService"):JSONEncode({error=value})
'''
            cleanup='''local p=game.Players.LocalPlayer.PlayerScripts:FindFirstChild("StageAMH17Probe") if p then p:Destroy() end
local r=game.ReplicatedStorage:FindFirstChild("StageAMH17Result") if r then r:Destroy() end return true'''
            try:
                response=st.luau('''local p=Instance.new("LocalScript") p.Name="StageAMH17Probe"
local r=Instance.new("StringValue") r.Name="StageAMH17Result" r.Parent=game.ReplicatedStorage
p.Source='''+long_string(wrapper)+''' p.Parent=game.Players.LocalPlayer.PlayerScripts return true''','Client')
                if response!='true':
                    (OUT/'h17-diagnostic.txt').write_text(response)
                    raise RuntimeError(response)
                deadline=time.monotonic()+60
                while True:
                    response=st.luau('return #game.ReplicatedStorage.StageAMH17Result.Value','Client')
                    if not response.isdigit():
                        (OUT/'h17-diagnostic.txt').write_text(response)
                        raise RuntimeError(response)
                    length=int(response)
                    if length: break
                    if time.monotonic()>deadline: raise TimeoutError(f'H17 shot {index} did not finish')
                    time.sleep(1)
                raw=''.join(st.luau(f'return string.sub(game.ReplicatedStorage.StageAMH17Result.Value,{i+1},{i+45000})','Client') for i in range(0,length,45000))
                row=json.loads(raw)
                if 'error' in row:
                    (OUT/'h17-local-script-error.json').write_text(json.dumps(row,indent=2)+'\n')
                    raise RuntimeError(row['error'])
                rows.append(row)
            finally:
                st.luau(cleanup,'Client')
            (OUT/'h17-shots.json').write_text(json.dumps(rows,indent=2)+'\n')
            print(json.dumps({k:v for k,v in row.items() if k!='trace'}),flush=True)
        timed=[r for r in rows if r['plan']['kind']=='timed']
        missed=[r for r in rows if r['plan']['kind']=='mistimed']
        report={'timed_pass':sum(bool(r['pass']) for r in timed),'timed_total':len(timed),
                'fall_respawn_pass':sum(bool(r['pass']) for r in missed),'fall_respawn_total':len(missed),
                'pass':all(r['pass'] for r in rows),'console':{dm:st.problems(dm) for dm in ['Server','Client']}}
        (OUT/'h17-summary.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report),flush=True)
    finally:
        st.stop_play(); clear_test_attrs(st)
        st.m.p.terminate()

if __name__=='__main__': main()
