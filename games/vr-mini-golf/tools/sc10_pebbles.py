"""Stage sc10 item 3: ray the two H3 pebble components (sc8 /tmp/sc8/h03c.json: 24 at world (-37.9,-4658.7), 26 at hole-local
(53.66, 9.21)) onto the ground under their base vertices. Run from games/vr-mini-golf: python3 tools/sc10_pebbles.py [true]
("true" = true render-mesh surface via sc10_place.trueground).
"""
import json,sys
sys.path.insert(0,'tools')
import sc10_place as P
from sc5_util import studio
d=json.load(open('/tmp/sc8/h03c.json'))
targets={'world(-37.9,-4658.7)':24,'world(-41.4,-4660.8)=hole-local(53.66,9.21)':26}
s=studio(); q=[]; meta={}
for label,k in targets.items():
    c=d[k]; base=c['base']; lo=c['lo'][1]
    pts=[[-95+b[0],18+lo+3,-4670+b[2]] for b in base]
    q.append({'id':k,'pts':pts}); meta[k]=dict(label=label,component=k,obj=c['obj'],n=c['n'],centreWorld=[-95+c['c'][0],18+c['c'][1],-4670+c['c'][2]],lowWorld=18+lo,base=base)
skip='{workspace.CourseSugarloaf.Kit.hole_dressing.h03_dress_props}'
G=P.ground(s,q,skip) if len(sys.argv)<2 else P.trueground(s,q,skip)
out=[]
for k,m in meta.items():
    hits=G[str(k)]
    gaps=[(18+b[1])-h[0] if h else None for b,h in zip(m['base'],hits)]
    fin=[g for g in gaps if g is not None]
    m.update(gaps=gaps,minGap=min(fin) if fin else None,ground=sorted({h[1] for h in hits if h}),floating=bool(fin) and min(fin)>0.3)
    out.append(m); print(m['label'],m['obj'],'low %.3f'%m['lowWorld'],'minGap',m['minGap'],'maxGap',max(fin) if fin else None,m['ground'],'FLOATING' if m['floating'] else 'not floating >0.3')
json.dump({'rule':'gap = base vertex y - ground below (ground = Terrain + visible non-dressing parts, excluding h03_dress_props); floating when every base point gap > 0.3',
           'pebbleMeshPart':'h03_dress_props__Pebble holds 8 pebble components (one merged MeshPart)','pebbles':out},open('playtests/stage-sc10/pebbles%s.json'%('' if len(sys.argv)<2 else '-truemesh'),'w'),indent=1)
