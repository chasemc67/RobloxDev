"""H8 crease update (holes.json 19:10): regenerate H8 clay-brick edging with the pass-6 rules (sc_dress_pass6.bricks)."""
import json, sys, os
sys.argv = [sys.argv[0]]
import sc_dress_pass6 as P
P.load_existing()
h = next(x for x in P.HOLES if x['id'] == 'h08')
out, sk = P.bricks(h)
json.dump(dict(bricks=out, skipped=sk), open(os.path.join(P.CACHE, 'h08_bricks_v2.json'), 'w'), indent=0)
print(len(out), sk)
