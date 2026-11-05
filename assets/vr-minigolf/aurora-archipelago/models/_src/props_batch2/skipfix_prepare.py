import json, shutil, sys, hashlib
from pathlib import Path
S=Path(__file__).resolve().parent; D=S.parents[2]; M=D/'models'
assert hashlib.md5((D/'holes.json').read_bytes()).hexdigest()=='2f1402fe19fc98a303c4e58dae680be9'
for b in (1,2):
 s=M/f'_src/props_batch{b}'; dest=s/'_backup_pre_skipfix'; dest.mkdir(exist_ok=True)
 files=[p for p in s.iterdir() if p.is_file()]+list((M/f'fbx/props_batch{b}').glob('*'))+list((M/f'previews/props_batch{b}').glob('*'))+[M/f'props_batch{b}_manifest.json',M/f'fitcheck_props_batch{b}.txt',M/'README.md',M/'_src/PROGRESS.md']
 for p in files:
  if p.exists():
   q=dest/p.relative_to(M);q.parent.mkdir(parents=True,exist_ok=True)
   if not q.exists():shutil.copy2(p,q)
sys.path.insert(0,str(S));from geometry import *
src=(S/'gen_batch2.py').read_text()
exec(src[src.index('def relative_add'):src.index('# Spiral shell')])
# Reuse the established shell and ship silhouettes at the new source boxes.
shell=src[src.index('for name,n in'):src.index('# Underwater lagoon')].replace("[('conch_entry',9),('conch_exit',9)]","[('conch_exit',9)]")
exec(shell)
ship=src[src.index("p=part(12,'icebreaker')"):src.index("m=H[12]['moving_parts'][0]")]
ship='\n'.join(l for l in ship.splitlines() if not l.startswith('skip(') and not l.startswith('p.notes.append'))
exec(ship)
ship=P[-1]
for o in a(12,'icebreaker')['occluders']:
 c=o['center']; sz=o['size'];box(ship,'HullTeal',[c[0],.555,c[2]],[sz[0],1.11,sz[2]])
ship.notes.append('Two shrunk lower hull blocks integrated; no separate hull_face_skins. Exact new occluder footprints.')
for n,name in [(5,'cliff_face_w'),(5,'cliff_face_e')]:
 p=part(n,name);x,y,z=p.anchor;w,h,d=a(n,name)['approx_size'];box(p,'Basalt',[x,h/2,z],[w,h,d])
 for k in range(6):
  xx=x-w/2+.7+k*(w-1.4)/5
  rounded(p,'Rock',[xx,.1,z+d/2-.055],[1.1,h-.2,.1]);rounded(p,'Snow',[xx,h*.58,z+d/2-.025],[.13,h*.35,.04])
 for yy in [.5,1.4,2.3,3.1]:box(p,'Brass',[x+(w/2-.12)*(1 if x<0 else -1),yy,z+d/2-.025],[.09,.09,.04])
 p.notes.append('Source 10.85x3.35x0.5 basalt slab, inset frost and shaft-side brass rivets; 0.15 source rail gap.')
for name in ['snow_walls_w','snow_walls_e']:
 p=part(10,name);x,y,z=p.anchor;w,h,d=a(10,name)['approx_size'];rounded(p,'SnowShadow',[x,y,z],[w,h,d]);rounded(p,'Snow',[x,y+h*.84,z],[w*.65,h*.16,d*.96])
for name in ['floe_frame_w','floe_frame_e']:
 p=part(11,name);x,y,z=p.anchor;tube(p,'Timber',[x,y,z],[x,y+2.8,z],.23);rounded(p,'Snow',[x,y+2.8,z],[.5,.2,.5])
for name in ['crescent_spout_w','crescent_spout_e']:
 p=part(16,name);x,y,z=p.anchor;sgn=1 if x<0 else -1
 rings=[]
 for yy,dx,rr in [(0,0,.6),(.6,-.1,.7),(1.5,-.2,.52),(2.3,0,.3),(3,.55,.015)]:
  rings.append([[x+sgn*dx+rr*math.cos(i*math.tau/8)-p.anchor[0],yy,z+rr*math.sin(i*math.tau/8)-p.anchor[2]] for i in range(8)])
 p.loft('Moonstone',rings);p.notes.append('Faceted tapering crescent horn in exact 1.5x3x1.5 source envelope.')
p=part(9,'coral_spit',felt_skins=['spit']);x,y,z=p.anchor;w,h,d=a(9,'coral_spit')['approx_size'];box(p,'CoralPink',[x,y+h/2,z],[w,h,d]);box(p,'IceCore',[x,-.025,z],[w-.2,.05,d-.2])
p=part(9,'conch_exit_ring',felt_skins=[f['id'] for f in H[9]['felt']]);
for j in range(32):
 t=j*math.tau/32;u=(j+1)*math.tau/32
 vs=[[rr*math.cos(tt),yy,rr*math.sin(tt)] for yy in [-.01,0] for rr,tt in [(.52,t),(.7,t),(.7,u),(.52,u)]]
 p.add('Lime',vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
p=part(15,'lip_ice',felt_skins=['lip_lane']);x,y,z=p.anchor;w,h,d=a(15,'lip_ice')['approx_size'];poly=[[-w/2,h],[w/2,h],[w/2,.6]]+[[ -w/2+i*w/14,0 if i%2 else .6] for i in range(14,-1,-1)]
vs=[[xx,yy,zz] for zz in [-d/2,d/2] for xx,yy in poly];cnt=len(poly);p.add('Ice',vs,[list(range(cnt-1,-1,-1)),list(range(cnt,2*cnt))]+[[i,(i+1)%cnt,(i+1)%cnt+cnt,i+cnt] for i in range(cnt)])
p=part(15,'ice_parapet');x,y,z=p.anchor;w,h,d=a(15,'ice_parapet')['approx_size'];box(p,'Ice',[x,h/2,z],[w,h,d]);box(p,'Snow',[x,h-.035,z],[w,.07,d]);p.notes.append('NOTE: intentional PlayerGuard parapet across lip; CanCollide false for ball. Near-invisible ice.')
p=part(15,'steps');x,y,z=p.anchor;w,h,d=a(15,'steps')['approx_size'];
# Five treads over authoritative z -12..-19.35; 1.5 nominal tread truncated at landing end.
for k in range(5):
 z0=-12-k*1.5;z1=max(-19.35,z0-1.5);top=-k*.8;box(p,'Timber',[x,(-4+top)/2,(z0+z1)/2],[w,top+4,z0-z1])
for k in range(6):
 zz=max(-19.25,-12-k*1.5);yy=-min(k,5)*.8;tube(p,'Timber',[-9.35,yy,zz],[-9.35,yy+3.5,zz],.08)
for k in range(5):tube(p,'Timber',[-9.35,-k*.8+3.5,-12-k*1.5],[-9.35,-(k+1)*.8+3.5,max(-19.25,-12-(k+1)*1.5)],.08)
for name in ['crystal_piers','ice_bridge']:
 ids=[w['id'] for w in H[17]['walls'] if w['id'].startswith('pier_') or (name=='ice_bridge' and w['id'].startswith('bridge_'))]
 if name=='ice_bridge':ids=[w['id'] for w in H[17]['walls'] if w['id'].startswith('bridge_')]
 p=part(17,name,skins=ids,felt_skins=['pier_s','pier_n'] if name=='crystal_piers' else ['ice_bridge'])
 for zz,ww,dd in ([(-20.75,3,8.2),(-37.25,3,8.2)] if name=='crystal_piers' else [(-29,4,24.7)]):
  xx=0 if name=='crystal_piers' else 6;box(p,'Ice',[xx,-.3,zz],[ww,.6,dd]);box(p,'IceCore',[xx,-.04,zz],[ww-.4,.05,dd-.2])
  if name=='crystal_piers':crystal(p,[xx,-3,zz],[2.7,2.4,2.5])
 for wall in H[17]['walls']:
  if wall['id'] in ids:
   sz=list(wall['size']);c=list(wall['center']);lo=max(c[2]-sz[2]/2,-41.35);hi=min(c[2]+sz[2]/2,-16.65);c[2]=(lo+hi)/2;sz[2]=hi-lo;box(p,'Ice' if name=='crystal_piers' else 'Timber',c,sz,wall['yaw'])
 p.notes.append('NOTE: intentionally covers its own railed felt; ends z -16.65..-41.35, 0.15 from rim rails.')
p=part(17,'span_lamp');x,y,z=p.anchor;tube(p,'Brass',[x,y,z],[x,y+1.5,z],.12);crystal(p,[x,y+1.4,z],[.6,1,.6],'AuroraMint')
new=[dict(id=p.name,hole=p.hole,anchor=list(p.anchor),yaw_local=0,groups={m:dict(verts=v,faces=f) for m,(v,f) in p.g.items()},skin_ids=p.skin_ids,felt_skins=p.felt_skins,motion=p.motion,notes=p.notes) for p in P]
for b in (1,2):
 s=M/f'_src/props_batch{b}';np=[p for p in new if (p['hole']==5)==(b==1)];ids={p['id'] for p in np};old=json.loads((s/'parts.json').read_text());old=[p for p in old if p['id'] not in ids];parts=old+np
 sk=json.loads((s/'skipped.json').read_text());obsolete={'h10_snow_walls','h11_floe_frame','h16_crescent_spout','h12_hull_face_skins'}
 sk=[p for p in sk if p['id'] not in ids|obsolete]
 (s/'parts.json').write_text(json.dumps(parts));(s/'skipped.json').write_text(json.dumps(sk,indent=2));(s/'skipfix_ids.json').write_text(json.dumps(sorted(ids)))
 print('Batch',b,'changed',len(np),'total',len(parts))
 # Keep existing actual triangles for untouched assets; invalidate only changed entries.
 cache=json.loads((s/'triangles.json').read_text());cache={k:v for k,v in cache.items() if k not in ids};(s/'triangles.json').write_text(json.dumps(cache))
 # Derive selective exporter from original, retaining full scene for context renders.
 build=(s/f'build_batch{b}.py').read_text()
 build=build.replace('ROOTS={};TRI={};rep=[]',"CHANGED=set(json.loads((S/'skipfix_ids.json').read_text())); OLD=json.loads((D/'models/props_batch"+str(b)+"_manifest.json').read_text()); OLDREP={p['id']:p for p in OLD['parts']}; ROOTS={};TRI={};rep=[]")
 line=next(l for l in build.splitlines() if 'bpy.ops.export_scene.fbx(' in l)
 build=build.replace(line,"    if p['id'] in CHANGED:\n    "+line)
 build=build.replace('rep.append(r);ROOTS',"rep.append(r if p['id'] in CHANGED else OLDREP[p['id']]);ROOTS")
 build=build.replace('for n in [1,2,3,5,7,8]:\n    visible=', 'for n in [5]:\n    visible=')
 build=build.replace('for n in [9,10,11,12,13,15,16,17]:\n    visible=', 'for n in [9,10,11,12,15,16,17]:\n    visible=')
 build=build.replace('for p in P:\n    visible=ROOTS',"for p in P:\n    if p['id'] not in CHANGED:continue\n    visible=ROOTS")
 build=build.replace('sc.cycles.samples=16','sc.cycles.samples=12')
 (s/'build_skipfix.py').write_text(build)
