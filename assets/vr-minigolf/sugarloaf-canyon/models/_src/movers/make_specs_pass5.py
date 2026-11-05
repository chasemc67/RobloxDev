"""P5 step 1: every dimension used by pass 5 (holes.json p9b), with its source path. holes.json wins all conflicts."""
import json,math,hashlib,datetime
from pathlib import Path
from registry_movers import HOLES,HOLES_PATH,REG,HOUR_STONES
SRC=Path(__file__).resolve().parent
def anchor(h,name):return next(a for a in HOLES[h]['decoration_anchors'] if a['name']==name)
def mp(h,mid):return next(m for m in HOLES[h]['moving_parts'] if m['id']==mid)
wp=mp(8,'windpump');ob=mp(13,'ore_bucket');sa=mp(16,'shadow_arm')
strips=wp['blockers']
tip=max(math.hypot(abs(b['center'][0])+b['size'][0]/2,abs(b['center'][1])+b['size'][1]/2) for b in strips)
inner=min(abs(b['center'][1])-b['size'][1]/2 for b in strips)
foot=ob['blockers'][1:]
P5IDS=['h07_teleport_pads','h07_teleport_pad_exit','h07_island_respawn_stone','h09_windpump_vanes_collision','h14_ore_bucket','h14_ore_bucket_foot_collision']+['h17_hour_stone_'+s['hour'] for s in HOUR_STONES]
specs={'source':str(HOLES_PATH.relative_to(SRC.parents[1])).replace(chr(92),'/'),'source_abs':str(HOLES_PATH),'source_round':'p9b','source_sha256':hashlib.sha256(HOLES_PATH.read_bytes()).hexdigest(),
'secondary_source':'in/p9-report.md (H9/H14/H7/H17 tables)','generated':datetime.datetime.now().astimezone().isoformat(),
'conventions':{'units':'studs','axes':'Roblox hole-local, +Y up, play toward -Z; Blender = (x,-z,y)','fbx':'forward -Z, up Y, scale 1, embedded textures','tris_per_mesh_max':20000,
 'clearance_rules':{'general':0.05,'mover_vs_static_prop':0.15,'design_override':'0.06 accepted for the H9 and H14 BLOCKING collision surfaces only (Game Art Bot); H9 visual tip .02 art-only'},
 'warning_bands':{'colors':{'LipRed':'#B83A35','LipCream':'#FFF0C9'},'rule':'moving parts only'}},
'rebuilt_props':P5IDS,
'h07':{'player_teleport_points':{'value':HOLES[6]['player_teleport_points'],'src':'holes[6].player_teleport_points'},
 'cup':{'value':HOLES[6]['cup'],'src':'holes[6].cup'},
 'exit_pad_west_edge_to_cup_rim':{'value':round((5.15-1.5)-(3.0+0.5),6),'src':'derived: pad x 5.15 - 1.5 vs cup x 3.0 + r 0.5'},
 'island_respawn_stone':{'value':anchor(6,'island_respawn_stone'),'src':'holes[6].decoration_anchors[island_respawn_stone]'},
 'respawn_point':{'value':next(z for z in HOLES[6]['hazards'] if z['id']=='taffy_gap')['respawn'],'src':'holes[6].hazards[taffy_gap].respawn'},
 'island_pad_to_stone_gap_x':{'value':round((4.5-1.5)-(0+0.4),6),'src':'derived: pad x 4.5 - 1.5 vs stone half 0.4'}},
'h09_windpump_vanes':{'pivot':{'value':wp['pivot'],'src':'holes[8].moving_parts[windpump].pivot'},'axis':{'value':wp['axis'],'src':'.axis'},'speed_deg_s':{'value':wp['speed'],'src':'.speed'},
 'period_s':{'value':360/wp['speed'],'src':'360/speed'},'phase':{'value':wp['phase'],'src':'.phase'},
 'visual_radial':{'value':[0.6,4.1],'src':'holes[8].moving_parts[windpump].visual "visual radius 0.6..4.1" (kept from pass 4)'},
 'visual_tip_felt_clearance':{'value':round(wp['pivot'][1]-4.1,6),'src':'pivot y 4.12 - 4.1 (art only, no collision)'},
 'visual_note':{'value':wp['visual'],'src':'holes[8].moving_parts[windpump].visual'}},
'h09_windpump_vanes_collision':{'pivot':{'value':wp['pivot'],'src':'holes[8].moving_parts[windpump].pivot'},'strips':{'value':strips,'src':'holes[8].moving_parts[windpump].blockers (48 = 12 x roll 0/90/180/270)'},
 'strip_count':{'value':len(strips),'src':'len(blockers)'},'vane_width':{'value':round(max(b['center'][0]+b['size'][0]/2 for b in strips)-min(b['center'][0]-b['size'][0]/2 for b in strips),6),'src':'blockers x extent'},
 'strip_width':{'value':round(strips[0]['size'][0],6),'src':'blockers size.x'},'depth':{'value':strips[0]['size'][2],'src':'blockers size.z'},
 'radial_inner':{'value':round(inner,6),'src':'blockers center.y+size.y/2'},'outer_radius':{'value':round(tip,6),'src':'blocker outer corners'},
 'tip_felt_clearance':{'value':round(wp['pivot'][1]-tip,6),'src':'pivot y - outer radius (p9-report: 0.06)'},
 'manifest':{'value':'collision-only: Transparency 1, CanCollide true, CollisionFidelity PreciseConvexDecomposition; visual h09_windpump_vanes CanCollide false','src':'brief_pass5 item 3'}},
'h14_ore_bucket':{'pivot':{'value':ob['pivot'],'src':'holes[13].moving_parts[ore_bucket].pivot'},'axis':{'value':ob['axis'],'src':'.axis'},'amplitude_deg':{'value':ob['amplitude_deg'],'src':'.amplitude_deg'},
 'period_s':{'value':ob['period_s'],'src':'.period_s'},'formula':{'value':'angle = 9*sin(2*pi*t/4) deg about +Z through hinge','src':'unchanged'},
 'bucket_blocker':{'value':ob['blockers'][0],'src':'holes[13].moving_parts[ore_bucket].blockers[0]'},
 'skid_visual':{'value':'Iron skid x -1.05..1.05, z +-0.075, top y -9.95 (inside bucket); underside piecewise-linear through the strip boundaries at max(adjacent strip bottoms), so never below a strip; outer ends raised 0.03 above the outer strip bottoms (chamfered corners)','src':'brief_pass5 item 4 + p9-report skid note'},
 'visual_note':{'value':ob['visual'],'src':'holes[13].moving_parts[ore_bucket].visual'}},
'h14_ore_bucket_foot_collision':{'pivot':{'value':ob['pivot'],'src':'holes[13].moving_parts[ore_bucket].pivot'},'strips':{'value':foot,'src':'holes[13].moving_parts[ore_bucket].blockers[1..14] == p9-report Foot strip boxes table'},
 'strip_count':{'value':len(foot),'src':'len(blockers)-1'},'strip_size_xz':{'value':[0.15,0.15],'src':'blockers size x/z'},
 'strip_top_local_y':{'value':sorted({round(b['center'][1]+b['size'][1]/2,6) for b in foot}),'src':'derived'},
 'strip_bottom_local_y':{'value':[round(b['center'][1]-b['size'][1]/2,6) for b in foot],'src':'derived'},
 'expected':{'value':dict(centre_min=0.06,centre_rest=0.0613,outer_corner_min=0.1502,outer_rest=0.2044),'src':'p9-report H14'}},
'h17_hour_stones':{'ring':{'value':{k:v for k,v in HOLES[16]['hour_stones'].items() if k!='stones'},'src':'holes[16].hour_stones'},
 'stones':{'value':HOLES[16]['hour_stones']['stones'],'src':'holes[16].hour_stones.stones (placed + dropped)'},
 'rail_walls':{'value':[w for w in HOLES[16]['walls'] if w['id'].startswith('hour_stone_')],'src':'holes[16].walls hour_stone_*'},
 'pivot_rule':{'value':'base centre = [cx, centre_y - 0.4 (=0, felt), cz]','src':'brief_pass5 item 2'},
 'numerals':{'value':'raised relief .02 on top (body y 0..0.78, numerals 0.78..0.80, all inside the exact 1.2x0.8x1.2 box), glyph up = radially outward (readable from the dial centre)','src':'holes.json anchor notes: roman numeral on top'},
 'arm_blockers':{'value':sa['blockers'],'src':'holes[16].moving_parts[shadow_arm].blockers'},'arm_to_rail_stone_gap':{'value':0.26,'src':'p9-report H17'}},
'registry':[e for e in REG if e['id'] in P5IDS]}
(SRC/'pass5_specs.json').write_text(json.dumps(specs,indent=1))
print('pass5_specs.json written; vane collision outer r',tip,'inner',inner,'strips',len(strips),'foot',len(foot))
