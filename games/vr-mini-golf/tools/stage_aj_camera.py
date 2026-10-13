"""Repeat Playtest Bot's actual Explore camera/jump test near Trading Post."""
import json,time,sys
from pathlib import Path
from run_playtests import Studio
st=Studio();out=Path('playtests/stage-aj')
try:
 existing='--existing-play' in sys.argv
 assert st.mode()[0]!='Edit' if existing else st.mode()[0]=='Edit'
 if not existing:st.start_play()
 for _ in range(30):
  ready=st.luau('return game.Players.LocalPlayer and game.Players.LocalPlayer.PlayerScripts:FindFirstChild("GolfExploreDebug")~=nil','Client')
  if ready=='true':break
  time.sleep(1)
 print(st.luau(Path('logs/stages/aj-inputs/camera-jump-test.luau').read_text(encoding='utf-8-sig'),'Client'),flush=True)
 for _ in range(60):
  if st.luau('return _G.QCCamera and _G.QCCamera.done','Client')=='true':break
  time.sleep(1)
 info=json.loads(st.luau('local r={} for _,t in _G.QCCamera.tests do local q=table.clone(t) q.samples=nil table.insert(r,q) end return game.HttpService:JSONEncode({done=_G.QCCamera.done,tests=r})','Client'))
 raw=st.luau('_G.StageAjCameraJson=game.HttpService:JSONEncode(_G.QCCamera) return #_G.StageAjCameraJson','Client')
 chunks=[st.luau('return string.sub(_G.StageAjCameraJson,%d,%d)'%(i,i+44999),'Client') for i in range(1,int(raw)+1,45000)]
 (out/'camera-samples.json').write_text(''.join(chunks)+'\n')
 info['console']={dm:st.problems(dm) for dm in ['Server','Client']}
 (out/'camera-summary.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info),flush=True)
finally:
 if not existing:st.stop_play()
 st.m.p.terminate()
