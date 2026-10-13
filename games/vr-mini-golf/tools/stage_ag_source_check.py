"""Verify all local Luau sources equal the open local place before saving."""
import json,sys
from pathlib import Path
from run_playtests import Studio,long_string
s=Studio();assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient")')=='true'
rows=[]
for p in sorted(Path('src').rglob('*.luau')):
 parts=list(p.relative_to('src').parts)
 for suffix in ['.server.luau','.client.luau','.luau']:
  if parts[-1].endswith(suffix):parts[-1]=parts[-1][:-len(suffix)];break
 code='local p=game for _,n in {'+','.join(json.dumps(x) for x in parts)+'} do p=p and p:FindFirstChild(n) end return p~=nil and p.Source=='+long_string(p.read_text())
 ok=s.luau(code)=='true';rows.append({'path':str(p),'equal':ok})
Path(sys.argv[1]).write_text(json.dumps(rows,indent=2))
assert all(r['equal'] for r in rows),[r for r in rows if not r['equal']]
print('source equality',len(rows),'/',len(rows))
