"""Read-only native collider profiles for local Aurora v3. Never saves/publishes."""
import hashlib
import json
from pathlib import Path

from holes_to_lua import to_lua
from run_playtests import Studio, long_string

GAME = Path(__file__).resolve().parents[1]
REPO = GAME.parents[1]
OUT = GAME / 'playtests/stage-ah'
SPEC = REPO / 'assets/vr-mini-golf/aurora-archipelago/holes.json'
PLACE = GAME / 'playtest/playtest-aurora-v3.rbxl'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text())
    selected = [h for h in spec['holes'] if h['number'] in (6, 18)]
    st = Studio()
    assert st.mode()[0] == 'Edit'
    preflight = json.loads(st.luau('''return game:GetService("HttpService"):JSONEncode({
      PlaceId=game.PlaceId,GameId=game.GameId,NetworkClient=game:FindFirstChildOfClass("NetworkClient")~=nil,
      PlaceRole=workspace:GetAttribute("PlaceRole"),Gravity=workspace.Gravity})'''))
    assert preflight['PlaceId'] == 0 and not preflight['NetworkClient']
    assert preflight['PlaceRole'] == 'aurora_archipelago'
    preflight['input_sha256'] = hashlib.sha256(PLACE.read_bytes()).hexdigest()
    preflight['spec_sha256'] = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    preflight['account_screenshot'] = 'CUA preflight visually showed Welcome, MetavrseBuilder'
    for rel in ['ServerStorage/CourseBuilder.luau', 'ServerStorage/CourseData/AuroraArchipelago.luau',
                'ReplicatedStorage/Golf/Config.luau',
                'StarterPlayer/StarterPlayerScripts/GolfClient/BallController.luau']:
        names = rel.removesuffix('.luau').split('/')
        code = 'local p=game for _,n in ' + to_lua(names) + ' do p=p:FindFirstChild(n) end return p.Source=='
        preflight.setdefault('source_equal', {})[rel] = st.luau(code + long_string((GAME/'src'/rel).read_text())) == 'true'
    assert all(preflight['source_equal'].values())
    (OUT/'preflight.json').write_text(json.dumps(preflight, indent=2)+'\n')
    (OUT/'authored-h6-h18.json').write_text(json.dumps(selected, indent=2)+'\n')
    probe = (Path(__file__).with_suffix('.luau')).read_text()
    for h in selected:
        length = int(st.luau('local spec=' + to_lua(h) + '\n' + probe, timeout=120))
        chunks = [st.luau(f'return string.sub(_G.StageAHProfileJSON,{i+1},{min(i+50000,length)})')
                  for i in range(0, length, 50000)]
        st.luau('_G.StageAHProfileJSON=nil return true')
        result = json.loads(''.join(chunks))
        (OUT/f'h{h["number"]}-profile.json').write_text(json.dumps(result, separators=(',', ':'))+'\n')
        print('wrote', h['number'], {k:len(v) for k,v in result['grids'].items()}, flush=True)
    st.m.p.terminate()


if __name__ == '__main__':
    main()
