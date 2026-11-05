import json,sys,math
from pathlib import Path
S=Path('models/_src/props_batch2').resolve();sys.path.insert(0,str(S));import geometry as g
pal=json.loads((S/'palette.json').read_text());pal['CoralPurple']=[pal['AuroraViolet'][0],'Slate',0,0,'Rev4 purple coral rock sides, existing violet colour without neon'];(S/'palette.json').write_text(json.dumps(pal,indent=2))
ps=json.loads((S/'parts.json').read_text());p=next(p for p in ps if p['id']=='h09_coral_spit');q=g.Part(p['id'],9,[0,0,0]);n=32;rings=[]
for yy,flare in [(0,.3),(.2,.22),(.55,.06),(.75,0)]:
 ring=[]
 for j in range(n):
  t=math.tau*j/n;cx=math.cos(t);sz=math.sin(t);variation=.035*math.sin(j*2.4) if yy<.75 else 0
  xx=(1.5+flare+min(0,variation))*math.copysign(abs(cx)**.22,cx);zz=(6.1+(min(flare,.18) if sz>0 else flare)+min(0,variation))*math.copysign(abs(sz)**.22,sz)
  ring.append([xx,yy+(abs(variation) if yy==0 else 0),zz])
 rings.append(ring)
q.loft('CoralPink',rings)
for side in [-1,1]:
 for k in range(13):
  z=-5.5+k*.91;g.mound(q,'CoralPurple' if k%3 else 'CoralPink',[side*(1.46+.03*(k%3)),.11+.025*(k%3),z],[.42,.44+.04*(k%3),.78],n=6)
 for k in range(19):
  z=-5.5+k*.6;g.bud(q,'CoralPink' if k%2 else 'CoralPurple',[side*1.67,.3+.04*(k%3),z],[.16,.18,.18])
p['groups']={m:dict(verts=v,faces=f) for m,(v,f) in q.g.items()};p['notes'].append('Rev4 visual finish: irregular skirt rim, overlapping pink/purple rock nodules with smaller polyp bumps; purple uses existing AuroraViolet hue as non-emissive rock.')
(S/'parts.json').write_text(json.dumps(ps,indent=2));print(sum(len(f)-2 for gg in p['groups'].values() for f in gg['faces']))
cache=json.loads((S/'triangles.json').read_text());cache.pop(p['id'],None);(S/'triangles.json').write_text(json.dumps(cache))
