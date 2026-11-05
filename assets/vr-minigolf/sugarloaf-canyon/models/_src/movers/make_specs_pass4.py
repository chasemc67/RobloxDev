"""P4 step 1: every dimension used by pass 4, with its source path. holes.json (p8) wins all conflicts."""
import json,math,hashlib,datetime
from pathlib import Path
from registry_movers import HOLES,HOLES_PATH,REG,DAM,LIP_PARAMS,H11_CYCLE
SRC=Path(__file__).resolve().parent
def anchor(h,name):return next(a for a in HOLES[h]['decoration_anchors'] if a['name']==name)
def mp(h,mid):return next(m for m in HOLES[h]['moving_parts'] if m['id']==mid)
wp=mp(8,'windpump');ob=mp(13,'ore_bucket');sa=mp(16,'shadow_arm')
strips=wp['blockers']
tip=max(math.hypot(abs(b['center'][0])+b['size'][0]/2,abs(b['center'][1])+b['size'][1]/2) for b in strips)
inner=min(abs(b['center'][1])-b['size'][1]/2 for b in strips)
specs={'source':str(HOLES_PATH.relative_to(SRC.parents[1])),'source_round':'p8','source_sha256':hashlib.sha256(HOLES_PATH.read_bytes()).hexdigest(),
'generated':datetime.datetime.now().astimezone().isoformat(),
'conventions':{'units':'studs','axes':'Roblox hole-local, +Y up, play toward -Z; Blender = (x,-z,y)','fbx':'forward -Z, up Y, scale 1, embedded textures',
 'warning_bands':{'colors':{'LipRed':'#B83A35','LipCream':'#FFF0C9'},'band':0.6,'source':'holes[10].moving_parts[quay_lip].appearance (H11 pattern)','rule':'moving parts only'}},
'h09_windpump_vanes':{'pivot':{'value':wp['pivot'],'src':'holes[8].moving_parts[windpump].pivot'},'axis':{'value':wp['axis'],'src':'holes[8].moving_parts[windpump].axis'},
 'speed_deg_s':{'value':wp['speed'],'src':'holes[8].moving_parts[windpump].speed'},'phase':{'value':wp['phase'],'src':'holes[8].moving_parts[windpump].phase'},
 'vane_width':{'value':round(max(b['center'][0]+b['size'][0]/2 for b in strips)-min(b['center'][0]-b['size'][0]/2 for b in strips),6),'src':'holes[8].moving_parts[windpump].blockers (6 strips x 0.4)'},
 'radial_inner':{'value':round(inner,6),'src':'blockers center.y+size.y/2'},'tip_radius':{'value':round(tip,6),'src':'blocker outer corners (inscribed circle r 4.1, visual note)'},
 'depth':{'value':strips[0]['size'][2],'src':'blockers size.z'},'strips':{'value':strips,'src':'holes[8].moving_parts[windpump].blockers (24 = 6 x roll 0/90/180/270)'},
 'felt_clearance_design':{'value':0.02,'src':'holes[8].moving_parts[windpump].visual "clearance .02"'},'visual_note':{'value':wp['visual'],'src':'holes[8].moving_parts[windpump].visual'}},
'h09_windpump_hub':{'pivot':{'value':wp['pivot'],'src':'holes[8].moving_parts[windpump].pivot / anchors[windpump_wheel]'},'pump_house':{'value':anchor(8,'pump_house'),'src':'holes[8].decoration_anchors[pump_house]'},
 'tunnel_felt':{'value':next(f for f in HOLES[8]['felt'] if f['id']=='pump_tunnel'),'src':'holes[8].felt[pump_tunnel]'},'vane_sweep_clearance_min':{'value':0.15,'src':'brief_pass4 item 1'}},
'h14_ore_bucket':{'pivot':{'value':ob['pivot'],'src':'holes[13].moving_parts[ore_bucket].pivot'},'axis':{'value':ob['axis'],'src':'holes[13].moving_parts[ore_bucket].axis'},
 'amplitude_deg':{'value':ob['amplitude_deg'],'src':'holes[13].moving_parts[ore_bucket].amplitude_deg'},'period_s':{'value':ob['period_s'],'src':'holes[13].moving_parts[ore_bucket].period_s'},
 'formula':{'value':'angle = 9*sin(2*pi*t/4) deg about +Z through hinge','src':'brief_pass4 item 2 / holes amplitude+period+phase 0'},
 'bucket_blocker':{'value':ob['blockers'][0],'src':'holes[13].moving_parts[ore_bucket].blockers[0]'},'foot_blocker':{'value':ob['blockers'][1],'src':'holes[13].moving_parts[ore_bucket].blockers[1]'},
 'foot_visual':{'value':'SHOWN: dark Iron skid 2.1 x 0.4 x 0.15 envelope with rivets; bottom edge is an arc r=10.275 about the hinge (same 0.075 felt gap as the collider at rest, never lower in swing)','src':'Game Art Bot answer 8:22 PM PT'},
 'visual_note':{'value':ob['visual'],'src':'holes[13].moving_parts[ore_bucket].visual'}},
'h14_cableway_trestle':{'anchor':{'value':anchor(13,'cableway_trestle'),'src':'holes[13].decoration_anchors[cableway_trestle] (legs x +-5 outside rails, beam y 10.35..11.35)'},
 'rails':{'value':[w for w in HOLES[13]['walls'] if w['id'] in ('rail1','rail9')],'src':'holes[13].walls rail1/rail9'},
 'existing_world_trestle':{'value':'sc/sugarloaf-canyon/models cableway_trestle = world backdrop 6x30x6 (world.json backdrop.pieces cableway_trestles), not the H14 hole trestle','src':'models/manifest.json + props-full.md line 90'}},
'h17_shadow_arms':{'pivot':{'value':sa['pivot'],'src':'holes[16].moving_parts[shadow_arm].pivot'},'axis':{'value':sa['axis'],'src':'holes[16].moving_parts[shadow_arm].axis'},
 'speed_deg_s':{'value':sa['speed'],'src':'holes[16].moving_parts[shadow_arm].speed'},'blockers':{'value':sa['blockers'],'src':'holes[16].moving_parts[shadow_arm].blockers (r 8.2..11.5, 3.6 wide, 0.9 tall)'},
 'visual_bottom_y':{'value':0.051,'src':'derived: >=0.05 felt clearance (blocker bottom is y 0 = felt)'}},
'h17_plinth':{'rest_exclusion':{'value':HOLES[16]['rest_exclusion'],'src':'holes[16].rest_exclusion'},'strips':{'value':[w for w in HOLES[16]['walls'] if w['id'].startswith('gnomon_plinth_')],'src':'holes[16].walls gnomon_plinth_00..47'},
 'gnomon':{'value':anchor(16,'gnomon'),'src':'holes[16].decoration_anchors[gnomon]'},'plinth_anchor':{'value':anchor(16,'gnomon_plinth'),'src':'holes[16].decoration_anchors[gnomon_plinth] (top y 1.2)'}},
'h07':{'vr_comfort':{'value':HOLES[6]['vr_comfort'],'src':'holes[6].vr_comfort'},'player_teleport_points':{'value':HOLES[6]['player_teleport_points'],'src':'holes[6].player_teleport_points'},
 'pad_colour':{'value':'#D8FF6A sour-apple lime (PadLime) + #2F5D3A centre (PadCore)','src':'course.md palette "Teleport pads"; approved Game Art Bot 8:22 PM PT'},
 'rope_bridges_anchor':{'value':anchor(6,'rope_bridges'),'src':'holes[6].decoration_anchors[rope_bridges] (export pivot [0,0,-42])'},'gap_view_anchor':{'value':anchor(6,'gap_view'),'src':'holes[6].decoration_anchors[gap_view] (export pivot [0,-4.25,-42])'}},
'dam_crest_parapets':{'value':DAM,'pivot':{'value':[0,115.7,-305],'src':'deck centre, confirmed Game Art Bot 8:22 PM PT'},'src':'brief_pass4 + p7-report "VR comfort / world handoff" line 1741 + course.md line 197 (WORLD coords). holes.json has no world dam record; ~/sc/sugarloaf-canyon/world/world.json (older copy) has crest path y 116 from x -46..46 at z -305, consistent with deck top 116.0'},
'h11_p8':{'cycle_s':{'value':H11_CYCLE,'src':'holes[10].moving_parts[*].period_s'},
 'lock_gate':{'value':dict(pivot=mp(10,'lock_gate')['pivot'],range=mp(10,'lock_gate')['range'],speed=mp(10,'lock_gate')['speed'],dwell=mp(10,'lock_gate')['dwell'],windows=dict(open=[0,5.5],rise=[5.5,5.8],closed=[5.8,10.4],lower=[10.4,10.7])),'src':'holes[10].moving_parts[lock_gate] + p8-report Final H11 timing'},
 'lock_lift_deck':{'value':dict(pivot=mp(10,'lock_lift_deck')['pivot'],schedule=mp(10,'lock_lift_deck')['schedule'],blockers=mp(10,'lock_lift_deck')['blockers'],speed=mp(10,'lock_lift_deck')['speed']),'src':'holes[10].moving_parts[lock_lift_deck]'},
 'quay_lip':{'value':dict(pivot=mp(10,'quay_lip')['pivot'],blockers=mp(10,'quay_lip')['blockers'],schedule=mp(10,'quay_lip')['schedule'],speed=mp(10,'quay_lip')['speed'],export_pivot=LIP_PARAMS['position'],transitions=dict(sink=[6.9,7.0],rise=[9.2,9.3])),'src':'holes[10].moving_parts[quay_lip] (+ speed-10 transitions outside the flush window, p8-report engine requirement)'},
 'release':{'value':'clamp(entry*0.5,1.5,7) toward -Z from [0,4,-27] during 7.10-9.10','src':'holes[10].teleports[lock_lift] + p8-report'},
 'geometry_changes':{'value':'lane 11 wide (x+-5.5, z 2..-6); 12-wide approach from z -6; quay 4.4 wide with 0.4 side pockets','src':'p8-report option 3; holes[10].felt/walls'},
 'collision_cuts':{'value':HOLES[10]['collision_cuts'],'src':'holes[10].collision_cuts'}},
'h06':{'sluice_gate':{'value':HOLES[5]['moving_parts'][0],'src':'holes[5].moving_parts[sluice_gate]'},'collision_cuts':{'value':HOLES[5]['collision_cuts'],'src':'holes[5].collision_cuts'}},
'registry':[{k:v for k,v in e.items()} for e in REG]}
(SRC/'pass4_specs.json').write_text(json.dumps(specs,indent=1))
print('pass4_specs.json written; tip radius',tip,'inner',inner)
