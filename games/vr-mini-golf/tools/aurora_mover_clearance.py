#!/usr/bin/env python3
"""Sample exact mover OBBs against every spec wall; run with uv run --with numpy.
SAT separation is a lower bound, not Euclidean closest distance. Subtract a motion
bound between samples to certify clearance across the continuous sweep.
"""
import json
from pathlib import Path
import numpy as np
from holes_to_lua import REPO


def rotation(axis, angles):
    axis=np.asarray(axis,dtype=float);axis/=np.linalg.norm(axis)
    x,y,z=axis
    cross=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    a=np.radians(np.atleast_1d(angles))
    return np.cos(a)[:,None,None]*np.eye(3)+(1-np.cos(a))[:,None,None]*np.outer(axis,axis)+np.sin(a)[:,None,None]*cross


def main():
    data=json.loads((Path(REPO)/'assets/vr-mini-golf/aurora-archipelago/holes.json').read_text())
    rows=[]
    for hole in data['holes']:
        for m in hole['moving_parts']:
            row={'hole':hole['number'],'id':m['id'],'type':m['type']}
            if not m['blockers']:
                row['status']='STATIC_SOLID; no moving blockers in spec';rows.append(row);continue
            n=3601
            lo,hi=m.get('range') or [0,360]
            values=np.linspace(lo,hi,n)
            slide=m['type']=='slide'
            moves=np.repeat(np.eye(3)[None,:,:],n,axis=0) if slide else rotation(m['axis'],values)
            pivot=np.array(m['pivot'])
            shifts=values[:,None]*np.array(m['axis']) if slide else np.zeros((n,3))
            best=(float('inf'),None,None,None)
            radius=0
            certified=float("inf")
            for bi,b in enumerate(m['blockers']):
                roll=rotation(m['axis'],[b.get('roll',0)])[0]
                local_rot=roll @ rotation([0,1,0],[b.get('yaw',0)])[0]
                rotations=moves @ local_rot
                centers=pivot+(moves @ (roll @ np.array(b['center']))[...,None])[...,0]+shifts
                half=np.array(b['size'])/2
                radius=max(radius,float(np.linalg.norm(b['center'])+np.linalg.norm(half)))
                aa=np.transpose(rotations,(0,2,1))
                for w in hole['walls']:
                    wr=rotation([0,1,0],[w.get('yaw',0)])[0]
                    wa=np.repeat(wr.T[None,:,:],n,axis=0)
                    crosses=np.cross(aa[:,:,None,:],wa[:,None,:,:]).reshape(n,9,3)
                    axes=np.concatenate([aa,wa,crosses],axis=1)
                    norm=np.linalg.norm(axes,axis=2)
                    valid=norm>1e-8
                    axes/=np.where(valid,norm,1)[:,:,None]
                    d=np.abs(np.einsum('nij,nj->ni',axes,centers-np.array(w['center'])))
                    ra=np.sum(np.abs(axes @ rotations)*half,axis=2)
                    rb=np.sum(np.abs(axes @ wr)*(np.array(w['size'])/2),axis=2)
                    margins=np.max(np.where(valid,d-ra-rb,-np.inf),axis=1)
                    index=int(np.argmin(margins));value=float(margins[index])
                    motion=(hi-lo)/(n-1)/2*(1 if slide else np.pi/180*(np.linalg.norm(b['center'])+np.linalg.norm(half)))
                    bound=value-motion
                    if not slide:
                        # Rotation preserves projection onto its own axle: this separating plane is exact at all phases.
                        axis=np.array(m['axis'],dtype=float);axis/=np.linalg.norm(axis)
                        fixed=abs(np.dot(centers[0]-np.array(w['center']),axis))-np.sum(np.abs(axis @ rotations[0])*half)-np.sum(np.abs(axis @ wr)*(np.array(w['size'])/2))
                        bound=max(bound,float(fixed))
                    certified=min(certified,bound)
                    if value<best[0]:best=(value,w['id'],bi+1,float(values[index]))
            gap_bound=(hi-lo)/(n-1)/2*(1 if slide else np.pi/180*radius)
            row.update(samples=n,min_sampled_separating_plane_gap=round(best[0],6),wall=best[1],blocker=best[2],pose=best[3],
                       between_sample_motion_bound=round(gap_bound,6),continuous_lower_bound=round(certified,6),
                       clearance_006_certified=bool(certified>=0.06-0.0001))
            rows.append(row)
            print(row,flush=True)
    Path('playtests/stage-ac2/mover-clearance.json').write_text(json.dumps({'method':__doc__,'movers':rows},indent=2)+'\n')

if __name__=='__main__':main()
