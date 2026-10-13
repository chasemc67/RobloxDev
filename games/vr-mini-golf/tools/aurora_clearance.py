#!/usr/bin/env python3
"""Offline checks against the original Aurora spec (not a physics simulation)."""
import itertools
import json
import math
from pathlib import Path
from holes_to_lua import REPO


def box_distance(point, box):
    a = math.radians(box.get('yaw', 0))
    x, z = point[0]-box['center'][0], point[2]-box['center'][2]
    x, z = x*math.cos(a)-z*math.sin(a), x*math.sin(a)+z*math.cos(a)
    return math.hypot(max(abs(x)-box['size'][0]/2, 0), max(abs(z)-box['size'][2]/2, 0))


def lower_corner(m, b, angle):
    # Aurora wheel and pendulum rotate about local Z; blocker yaw precedes axle rotation.
    yaw = math.radians(b.get('yaw', 0)); a=math.radians(angle+b.get('roll', 0))
    values=[]
    for sx,sy,sz in itertools.product([-1,1], repeat=3):
        x=sx*b['size'][0]/2; z=sz*b['size'][2]/2
        x=x*math.cos(yaw)+z*math.sin(yaw)+b['center'][0]
        y=sy*b['size'][1]/2+b['center'][1]
        values.append(m['pivot'][1]+x*math.sin(a)+y*math.cos(a))
    return min(values)


def main():
    data=json.loads((Path(REPO)/'assets/vr-mini-golf/aurora-archipelago/holes.json').read_text())
    rows=[]
    for h in data['holes']:
        c=h['cup']['position']
        near=[(box_distance(c,w),w['id']) for w in h['walls']
              if w['center'][1]+w['size'][1]/2>c[1] and w['center'][1]-w['size'][1]/2<c[1]+0.16]
        dist,wall=min(near,default=(float('inf'),'none'))
        movers=[]
        for m in h['moving_parts']:
            item={'id':m['id'],'type':m['type'],'blockers':len(m['blockers']), 'range':m.get('range')}
            if m['type'] in ['rotate','swing'] and m['axis']==[0,0,1]:
                lo,hi=m.get('range') or [0,360]
                gap=min(lower_corner(m,b,lo+(hi-lo)*i/3600) for i in range(3601) for b in m['blockers'])
                item.update(min_floor_clearance=round(gap,6),passes_006_015=0.06-0.0002<=gap<=0.15+0.0002,
                            method='3601 angle samples, all 8 corners per exact blocker, flat felt y=0')
            else:
                item['clearance_status']='requires engine sweep; no universal floor-gap test for slides, horizontal carousel, or toggle'
            if m['type']=='toggle': item['animation']='STATIC_SOLID (unsupported profile)'
            else: item['animation']='existing constraint driver'
            movers.append(item)
        rows.append({'hole':h['number'],'cup_wall_clearance':round(dist,6),'nearest_wall':wall,
                     'cup_2_2_pass':dist>=2.2-0.0001,'movers':movers})
    out={'method':'Spec-space cup centre to oriented wall boxes at ball height; wheel/pendulum corner sweep. Does not prove all dynamic pinch clearances.', 'holes':rows}
    Path('playtests/stage-ac2/spec-clearance.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
