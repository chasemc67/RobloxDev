"""Pass 3: five original plus parametric quay lip; SRV-132 H6/H11 props; source-derived pivots."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
HOLES=json.loads((BASE/'in/holes_rev.json').read_text())['holes']
REG=[dict(id='h06_sluice_gate',hole=5,pivot=HOLES[5]['moving_parts'][0]['pivot'],moving=True),
dict(id='h06_sluice_frame',hole=5,pivot=[0,0,-28],moving=False),
dict(id='h11_lock_gate',hole=10,pivot=HOLES[10]['moving_parts'][0]['pivot'],moving=True),
dict(id='h11_lock_lift',hole=10,pivot=HOLES[10]['moving_parts'][1]['pivot'],moving=True),
dict(id='h11_lock_chamber',hole=10,pivot=[0,0,-23],moving=False)]
def motion(name,t):
    if name=='h06_sluice_gate':
        q=t%(3.2+14/3)
        return (0 if q<1.2 else -3*(q-1.2) if q<1.2+7/3 else -7 if q<3.2+7/3 else -7+3*(q-3.2-7/3)),0
    q=t%10.6
    if name=='h11_quay_lip':
        return (0 if q<7.4 else -10*(q-7.4) if q<7.5 else -1 if q<7.65 else -1+10*(q-7.65) if q<7.75 else 0),0
    if name=='h11_lock_gate': return (-1.3 if q<4.85 else -1.3+2*(q-4.85) if q<5.5 else 0 if q<9.95 else -2*(q-9.95)),0
    if name=='h11_lock_lift':
        if q<5.5:return 0,0
        if q<7.5:return 2*(q-5.5),0
        if q<7.65:return 4,4*(q-7.5)/.15
        if q>=9.15:return 0,0
        return 4*(1-(q-7.65)/1.5),4*max(0,1-(q-7.65)/.15)
    return 0,0

# Requested provisional geometry, pending Game Art Bot holes.json revision.
LIP_PARAMS=dict(width=3.6,depth=.2,height=1.5,position=[0,3.5,-25.45])
REG.append(dict(id='h11_quay_lip',hole=10,pivot=LIP_PARAMS['position'],moving=True,params=LIP_PARAMS.copy()))
