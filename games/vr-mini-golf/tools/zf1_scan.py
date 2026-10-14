"""Run zf1_zscan.luau and save its complete chunked JSON result."""
import json,sys
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
n=int(s.luau(Path('tools/zf1_zscan.luau').read_text(),timeout=300))
raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ZF1ScanJSON:sub(%d,%d))'%(i+1,i+40000))) for i in range(0,n,40000))
p=Path('playtests/stage-zf1/zscan-'+sys.argv[1]+'.json');p.write_text(raw+'\n');r=json.loads(raw);print(json.dumps({k:v for k,v in r.items() if k in ['counts','summary','placeholderCounts']},indent=2),flush=True)
