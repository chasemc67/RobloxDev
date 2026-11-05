"""Exact triangle/OBB SAT gates, with conservative L-infinity clearance lower bounds.
Source skin volumes exempt only their own footprint. Sweep union is exact for vertical translation.
"""
import json,math
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent;D=S.parents[2]
H={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
P=json.loads((S/'parts.json').read_text())
def ry(y):
    a=math.radians(y);c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def hit(T,c,size,yaw=0,inflate=0):
    q=(T-np.array(c))@ry(yaw);half=np.array(size)/2+inflate
    edges=np.roll(q,-1,axis=1)-q
    axes=[np.tile(np.eye(3)[i],(len(T),1)) for i in range(3)]
    axes.append(np.cross(edges[:,0],edges[:,1]))
    for i in range(3):
        for j in range(3):axes.append(np.cross(edges[:,i],np.eye(3)[j]))
    overlaps=np.ones(len(T),dtype=bool)
    for ax in axes:
        proj=np.einsum('tvi,ti->tv',q,ax);radius=np.abs(ax)@half
        overlaps &= (proj.min(axis=1)<=radius+1e-8)&(proj.max(axis=1)>=-radius-1e-8)
    return overlaps
CACHE=json.loads((S/"triangles.json").read_text()) if (S/"triangles.json").exists() else None
def triangles(p):
    if CACHE is not None and p['id'] in CACHE:return np.array(CACHE[p['id']])+p['anchor']
    ts=[]
    for g in p['groups'].values():
        for f in g['faces']:
            for i in range(1,len(f)-1):ts.append([g['verts'][f[0]],g['verts'][f[i]],g['verts'][f[i+1]]])
    return np.array(ts)+p['anchor']
def clearance(T,w):
    if hit(T,w['center'],w['size'],w.get('yaw',0),-.000001).any():return -1.0
    lo,hi=0.,100.
    for _ in range(27):
        mid=(lo+hi)/2
        if hit(T,w['center'],w['size'],w.get('yaw',0),mid).any():hi=mid
        else:lo=mid
    return lo
def in_foot(T,w):
    q=(T-w['center'])@ry(w.get('yaw',0));return (np.abs(q[:,:,0])<=w['size'][0]/2+.001)&(np.abs(q[:,:,2])<=w['size'][2]/2+.001)
