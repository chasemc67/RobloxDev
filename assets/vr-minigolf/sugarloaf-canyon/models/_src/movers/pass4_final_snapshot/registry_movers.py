"""Pass 4: SRV-132 movers. Source of truth in/holes.json (p8). H6/H11 entries kept from pass 3
(H11 retimed to the p8 10.7 s cycle); pass-4 entries for H7/H9/H14/H17 and the world dam crest.
motion(name,t) -> (offset_studs, angle_deg). Translations use offset; rotors/swing use angle."""
import json,math
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
HOLES_PATH=BASE/'in/holes.json'
HOLES=json.loads(HOLES_PATH.read_text())['holes']
def _mp(hole,mid):return next(m for m in HOLES[hole]['moving_parts'] if m['id']==mid)
H6_PERIOD=3.2+14/3
H11_CYCLE=_mp(10,'lock_gate')['period_s']  # 10.7
REG=[dict(id='h06_sluice_gate',hole=5,pivot=HOLES[5]['moving_parts'][0]['pivot'],moving=True,kind='slide',axis=[1,0,0]),
dict(id='h06_sluice_frame',hole=5,pivot=[0,0,-28],moving=False,kind='static'),
dict(id='h11_lock_gate',hole=10,pivot=_mp(10,'lock_gate')['pivot'],moving=True,kind='slide',axis=[0,1,0]),
dict(id='h11_lock_lift',hole=10,pivot=_mp(10,'lock_lift_deck')['pivot'],moving=True,kind='slide',axis=[0,1,0]),
dict(id='h11_lock_chamber',hole=10,pivot=[0,0,-23],moving=False,kind='static')]
# Quay lip: 3.6 x 1.5 x .2 (holes.json quay_lip blocker); FBX pivot is the bottom centre, .75 below the spec centre pivot.
_lip=_mp(10,'quay_lip');LIP_PARAMS=dict(width=_lip['blockers'][0]['size'][0],depth=_lip['blockers'][0]['size'][2],height=_lip['blockers'][0]['size'][1],
 position=[_lip['pivot'][0],_lip['pivot'][1]-_lip['blockers'][0]['size'][1]/2,_lip['pivot'][2]])
REG.append(dict(id='h11_quay_lip',hole=10,pivot=LIP_PARAMS['position'],moving=True,kind='slide',axis=[0,1,0],params=LIP_PARAMS.copy()))
# ---- pass 4 ----
def _pad_hits_cup(p,clear=.15):
    c=HOLES[6]['cup'];dx=max(abs(c['position'][0]-p['position'][0])-p['size'][0]/2,0);dz=max(abs(c['position'][2]-p['position'][2])-p['size'][2]/2,0)
    return math.hypot(dx,dz)<c['radius']+clear
_wp=_mp(8,'windpump');_ob=_mp(13,'ore_bucket');_sa=_mp(16,'shadow_arm')
P4=[dict(id='h09_windpump_vanes',hole=8,pivot=_wp['pivot'],moving=True,kind='rotate',axis=_wp['axis'],speed=_wp['speed'],phase=_wp['phase'],source='holes[8].moving_parts[windpump]'),
dict(id='h09_windpump_hub',hole=8,pivot=_wp['pivot'],moving=False,kind='static',source='holes[8] windpump pivot / decoration_anchors pump_house'),
dict(id='h14_ore_bucket',hole=13,pivot=_ob['pivot'],moving=True,kind='swing',axis=_ob['axis'],amplitude=_ob['amplitude_deg'],period=_ob['period_s'],phase=_ob['phase'],source='holes[13].moving_parts[ore_bucket]'),
dict(id='h14_cableway_trestle',hole=13,pivot=next(a for a in HOLES[13]['decoration_anchors'] if a['name']=='cableway_trestle')['position'],moving=False,kind='static',realizes_anchor='cableway_trestle',source='holes[13].decoration_anchors[cableway_trestle]'),
dict(id='h17_shadow_arms',hole=16,pivot=_sa['pivot'],moving=True,kind='rotate',axis=_sa['axis'],speed=_sa['speed'],phase=_sa['phase'],source='holes[16].moving_parts[shadow_arm]'),
*[dict(id=f'h17_shadow_arm_head_{y}',hole=16,pivot=_sa['pivot'],moving=True,kind='rotate',axis=_sa['axis'],speed=_sa['speed'],phase=_sa['phase'],head_yaw=y,source=f'holes[16].moving_parts[shadow_arm].blockers[yaw {y}] leading end (pass 4b split)') for y in (0,90,180,270)],
dict(id='h17_plinth',hole=16,pivot=HOLES[16]['rest_exclusion']['center'],moving=False,kind='static',realizes=[w['id'] for w in HOLES[16]['walls'] if w['id'].startswith('gnomon_plinth_')],realizes_anchor='gnomon',source='holes[16].rest_exclusion + walls gnomon_plinth_* + anchor gnomon'),
dict(id='h07_bridge_parapets',hole=6,pivot=[0,0,-42],moving=False,kind='static',realizes=['rope_rail6','rope_rail7','rope_rail12','rope_rail13'],source='holes[6].vr_comfort.boxes solid_parapet'),
dict(id='h07_bridge_skirts',hole=6,pivot=[0,0,-42],moving=False,kind='static',realizes_vr=['bridge1_skirt_west','bridge1_skirt_east','bridge2_skirt_west','bridge2_skirt_east'],source='holes[6].vr_comfort.boxes solid_side_skirt'),
dict(id='h07_gap_floor_mist',hole=6,pivot=[0,-4.25,-42],moving=False,kind='static',realizes_vr=['gap_comfort_floor','gap_mist'],source='holes[6].vr_comfort gap_comfort_floor + mist'),
dict(id='h07_teleport_pads',hole=6,pivot=HOLES[6]['player_teleport_points'][0]['position'],moving=False,kind='static',instances=[dict(id=p['id'],pivot=p['position'],yaw=p['yaw']) for p in HOLES[6]['player_teleport_points'] if not _pad_hits_cup(p)],source='holes[6].player_teleport_points'),
dict(id='h07_teleport_pad_exit',hole=6,pivot=next(p for p in HOLES[6]['player_teleport_points'] if _pad_hits_cup(p))['position'],moving=False,kind='static',instances=[dict(id=p['id'],pivot=p['position'],yaw=p['yaw']) for p in HOLES[6]['player_teleport_points'] if _pad_hits_cup(p)],source='holes[6].player_teleport_points[bridge2_exit]; notched .65 round the cup (holes.json pad overlaps cup [3,0,-60])'),
dict(id='dam_crest_parapets',hole=None,pivot=[0,115.7,-305],moving=False,kind='static',world=True,source='p7-report VR comfort / world handoff; course.md dam crest (world coords)')]
REG.extend(P4)
DAM=dict(deck=dict(center=[0,115.7,-305],size=[92,.6,8]),parapets=[dict(center=[0,117.75,-309.3],size=[92,3.5,.6]),dict(center=[0,117.75,-300.7],size=[92,3.5,.6])],
 skirts=[dict(center=[0,112,-309.3],size=[92,8,.6]),dict(center=[0,112,-300.7],size=[92,8,.6])])
def _h11(name,t):
    q=t%H11_CYCLE
    if name=='h11_lock_gate':
        v=13/3  # 1.3 studs in .3 s
        return (-1.3 if q<5.5 else -1.3+v*(q-5.5) if q<5.8 else 0 if q<10.4 else -v*(q-10.4)),0
    if name=='h11_lock_lift':
        return (0 if q<6.1 else 4*(q-6.1) if q<7.1 else 4 if q<9.1 else 4-4*(q-9.1) if q<10.1 else 0),0
    if name=='h11_quay_lip':
        # speed 10: finish sinking by 7.0, flush (top y 4) through 9.2, raised again (top y 5) at 9.3.
        return (0 if q<6.9 else -10*(q-6.9) if q<7.0 else -1 if q<9.2 else -1+10*(q-9.2) if q<9.3 else 0),0
def motion(name,t):
    if name=='h06_sluice_gate':
        q=t%H6_PERIOD
        return (0 if q<1.2 else -3*(q-1.2) if q<1.2+7/3 else -7 if q<3.2+7/3 else -7+3*(q-3.2-7/3)),0
    if name.startswith('h11_') and name!='h11_lock_chamber':return _h11(name,t)
    e=next((x for x in REG if x['id']==name),None)
    if e and e['kind']=='rotate':return 0,(e['speed']*t+e['phase'])%360
    if e and e['kind']=='swing':return 0,e['amplitude']*math.sin(2*math.pi*t/e['period']+math.radians(e['phase']))
    return 0,0
def period(name):
    e=next(x for x in REG if x['id']==name)
    if e['hole']==5:return H6_PERIOD
    if e['hole']==10:return H11_CYCLE
    if e['kind']=='rotate':return 360/e['speed']
    if e['kind']=='swing':return e['period']
    return 0
