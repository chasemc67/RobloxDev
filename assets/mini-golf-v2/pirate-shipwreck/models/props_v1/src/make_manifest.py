import json,math,os,hashlib
R='/workspace/RobloxDev/games/vr-mini-golf-v2/pirate-shipwreck/data/placements.json'
pl=json.load(open(R));dump=json.load(open('previews_props_v1/dump.json'))
IDS={'prop_cannon':('gag02_backward_cannon',"Cannon pointing back at the ship. Muzzle faces +Z: set yaw so the model's +Z points at the wreck (the placement's yawDeg is the gag's heading; footprint x14/z7 in placements assumed the long axis on x, but the model's long axis is Z)."),
 'prop_coconut':('gag07_coconut_casualty','Leaning palm with a plain-hat skeleton flat under it, hit by a coconut. Cute, no gore.'),
 'prop_flytrap':('gag10_flytrap_burp','Flytrap that swallowed a pirate: only striped socks and boots stick out of its mouth; a plain hat lies on the ground. Mouth faces +Z.'),
 'prop_croc':('gag11_croc_nap',"Napping croc in a plain captain's hat on a mud patch, with a cutlass beside it. Head toward +Z."),
 'prop_captain':('gag13_captains_last_nap',"Skeleton captain asleep on a gold pile (in a chair, plain hat over closed eyes, parrot on the chair). Faces +Z.")}
def clear(pos,yaw,sz,pt,rad):
    a=math.radians(yaw);ex=(math.cos(a),-math.sin(a));ez=(math.sin(a),math.cos(a))
    dx,dz=pt[0]-pos[0],pt[2]-pos[2];lx=dx*ex[0]+dz*ex[1];lz=dx*ez[0]+dz*ez[1]
    ox=max(abs(lx)-sz[0]/2,0);oz=max(abs(lz)-sz[1]/2,0);return math.hypot(ox,oz)-rad
out={'name':'props_v1','scene':'pirate-shipwreck','units':'studs (1 stud = 1 unit)','status':'ready for review; scenery only',
 'conventions':{'pivot':'base centre at ground level (min Y = 0, bbox centre X/Z = 0)','front':'+Z','up':'+Y','colour':'palette texture (props_palette.png, 8x8 cells, 56 colours, no vertex colours), one mesh object per FBX','fbx_export':"axis_forward=-Z, axis_up=Y, global_scale=1, face-smoothed"},
 'gameplay':'Scenery only. No prop is a putting surface; set CanCollide=false / CanQuery=false (or collide only for blocking) and keep clear of felt. Amber PointLight (cannon, etc.) is added in Studio; cannon smoke is a particle emitter, not mesh.',
 'props':[],'palette':'props_palette.png (also embedded as <id>.png)','generators':['src/props_lib.py','src/gen_props.py','src/build_props.py','src/render_props.py','src/make_manifest.py','mkjob.sh'],
 'previews':['previews_props_v1/3q_<prop>.png (x5)','previews_props_v1/lineup.png (5-stud figure beside each prop)','previews_props_v1/contact_sheet.png'],
 'deviations':[
  'Plain tricorn-style hats with a brass band on cannon scene, flytrap, croc, coconut skeleton and captain; no skull and crossbones, no flags anywhere (sheet sketches show skull-and-crossbones hats; replaced).',
  'Actual footprints differ from the placements estimates: cannon 14.9x20.7 (long axis Z, with ramrod/scorch/ball stack) vs 14x7; croc 27x40 incl. mud patch vs 40x16 (rotate yaw so Z is the long axis); coconut 21.7x20.8 incl. palm crown vs 16x16; flytrap 20.4x26.6 incl. leaves and hat vs 20x20; captain 24.7x23.3 vs 24x24.',
  'Extras added to make the gags read: cannon hat, ramrod, scorch disc, ball stack; croc cutlass and mud; captain parrot, chest, coins, gems.',
  'Tri counts are below the sheet targets for cannon (2.0k vs 2.5k+balls) but within the 2-8k aim for the rest apart from cannon/croc/flytrap being ~1.8-2.2k.',
  'Previews: Workbench renders on a flat sand-tone slab; the ground slab is not part of any FBX.']}
for pid,(gid,note) in IDS.items():
    d=dump[pid];mn,mx=d['roblox_min'],d['roblox_max'];size=[round(mx[i]-mn[i],2) for i in range(3)]
    hp=[h for h in pl['heroProps'] if h['id']==gid][0];rad=math.hypot(size[0],size[2])/2
    cl=sorted([(round(clear(p['pos'],p['yawDeg'],p['artClearSize'],hp['anchor'],rad),1),p['id']) for p in pl['pads']])[:2]
    out['props'].append({'id':pid,'fbx':pid+'.fbx','palette_png':pid+'.png','preview':f'previews_props_v1/3q_{pid}.png','tris':d['tris'],'size_studs':{'x':size[0],'y':size[1],'z':size[2]},
      'bbox_min':mn,'bbox_max':mx,'uv':d['uv'],'objects':len(d['objects']),'placement':{'gag':gid,'where':hp['where'],'anchor':hp['anchor'],'yawDeg':hp['yawDeg'],'placements_footprint':hp['footprint']},
      'note':note,'nearest_pad_art_clear_gap_studs':[{'pad':p,'gap':g} for g,p in cl],'clearance_check':'gap = anchor-to-art-clear-rectangle distance minus prop circumscribed radius; >= 8 satisfies emptySpaceAroundPad' if cl[0][0]>=0 else 'overlaps art-clear area of nearest pad; see gap'})
json.dump(out,open('manifest.json','w'),indent=1)
for p in out['props']: print(p['id'],p['tris'],p['size_studs'],p['nearest_pad_art_clear_gap_studs'])
