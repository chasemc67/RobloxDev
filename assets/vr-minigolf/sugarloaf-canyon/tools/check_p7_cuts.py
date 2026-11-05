#!/usr/bin/env python3
"""Focused closed-pocket and synchronized quay-lip regression shots."""
import argparse, json, math, os
import numpy as np
import sim as S
course=json.load(open(os.path.join(S.HERE,'..','holes.json')))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',default=os.path.join(S.HERE,'out','p7-cuts-regressions.json'))
opts=parser.parse_args()
h11=next(h for h in course['holes'] if h['number']==11)
parts={m['id']:m for m in h11['moving_parts']}
schedule=parts['lock_lift_deck']['schedule']
flush=parts['quay_lip']['schedule']['flush']
top=schedule['release'];rise=schedule['rise'];descend=schedule['return_']
PH=S.ph_array();path=np.zeros((1800,3));results=[]
for n in (96,120):
 h=next(h for h in course['holes'] if h['number']==11);ha=S.HoleArrays(h)
 cases=[]
 period=S.cycle_period(h['moving_parts'][0])
 for k in range(n):
  t0=k*period/n
  for x in (-1.86,-1.4,0,1.4,1.86):
   for speed in (4.,S.V_MAX):
    # Start immediately north of lip, so down/mid-travel impact is unambiguous.
    r=S.sim_shot(*ha.args(),PH,x,-25.9,4.,0.,speed,t0,True,path)
    # Full-cycle shots can legally cross while lip is flush. Independently freeze its
    # closed pose to test every down/mid phase, including the 0.15 end clearances.
    frozen=S.HoleArrays(h)
    jl=[m["id"] for m in h["moving_parts"]].index("quay_lip")
    frozen.MP[jl,0]=1;frozen.MP[jl,8]=1;frozen.MP[jl,9:11]=0;frozen.MP[jl,12]=0
    rf=S.sim_shot(*frozen.args(),PH,x,-25.9,4.,0.,speed,t0,True,path)
    used=path[:int(rf[6])]
    crossed=not(flush[0]<=t0<flush[1]) and bool(np.any((used[:,2]>-25.3)&(used[:,1]>3.5)&(np.abs(used[:,0])<1.75)))  # central deck gap; side shoulder parking remains on quay
    cases.append(dict(t0=round(t0,4),x=x,speed=speed,outcome=int(r[3]),crossed=crossed))
 results.append(dict(hole=11,phases=n,shots=len(cases),escapes=sum(c['outcome']==3 for c in cases),timeouts=sum(c['outcome']==4 for c in cases),crossed=sum(c['crossed'] for c in cases),failures=[c for c in cases if c['outcome'] in (3,4) or c['crossed']][:10]))
for n in (96,120):
 h=next(h for h in course['holes'] if h['number']==11);ha=S.HoleArrays(h);jd=[m['id'] for m in h['moving_parts']].index('lock_lift_deck');out=[]
 for k in range(n):
  t=k*S.cycle_period(h['moving_parts'][0])/n;height=S.part_state(ha.MP,jd,t)[0]
  r=S.sim_shot(*ha.args(),PH,0,-23.325,height,0,-3,t,True,path)
  out.append(r)
 results.append(dict(hole=11,part='lift_ride_release',phases=n,shots=n,escapes=sum(r[3]==3 for r in out),timeouts=sum(r[3]==4 for r in out),released=sum(r[2]>=3.99 and r[1]<-26 for r in out)))
 assert all(r[2]>=3.99 and r[1]<-26 for r in out)
# Physical deck-to-quay crossing: retain moving solids/felt, disable all transport.
import rest_audit as RA
hh=S.HoleArrays(next(h for h in course['holes'] if h['number']==11));args=list(hh.args());args[8]=0
for n in (96,120):
    starts=[(x,t,v) for t in np.linspace(top[0],top[1],n,endpoint=False) for x in (-1.4,0.,1.4) for v in (2.,6.,S.V_MAX)]
    X=np.array([c[0] for c in starts]);T=np.array([c[1] for c in starts]);V=np.array([c[2] for c in starts]);N=len(starts)
    oc,ends,pins=RA.audit_batch(*args,PH,X,np.full(N,-24.9),np.full(N,4.),np.full(N,-math.pi/2),V,T)
    arrivals=[]
    for x,t,v in starts:
        rr=S.sim_shot(*args,PH,x,-24.9,4.,0.,-v,t,True,path)
        used=path[:int(rr[6])]
        arrivals.append(bool(rr[3]==1 or np.any((used[:,2]<-25.7)&(used[:,1]>=3.99))))
        if not arrivals[-1]:
            resumed=S.sim_shot(*hh.args(),PH,rr[0],rr[1],rr[2],0.,0.,t+rr[4],True,path)
            assert resumed[3] not in (3,4) and resumed[2]>=3.99 and resumed[1]<-25.7,('late safe return failed next ride',t,resumed)

    # Only slow departures immediately before descent may miss the closing lip.
    # They must return on the deck, never settle unsupported in the clearance.
    for i,c in enumerate(starts):
        if not arrivals[i]:
            assert c[2]==2. and c[1]>=descend[0]-.1 and abs(ends[i,1])<1e-8 and abs(ends[i,0])<=1.6 and -25<=ends[i,2]<=-21.65,(c,ends[i])
    assert all(arrivals[i] for i,c in enumerate(starts) if c[1]<descend[0]-.1 or c[2]>=6.)
    results.append(dict(hole=11,part='physical_ride_off_without_transport',phases=n,shots=N,quay_arrivals=sum(arrivals),arrival_by_speed=[dict(speed=v,shots=sum(c[2]==v for c in starts),arrivals=sum(arrivals[i] for i,c in enumerate(starts) if c[2]==v)) for v in (2.,6.,S.V_MAX)],nonarrival_examples=[dict(x=c[0],phase=c[1],speed=c[2],end=ends[i].tolist()) for i,c in enumerate(starts) if not arrivals[i]][:20],escapes=int(np.sum(oc==3)),timeouts=int(np.sum(oc==4)),pinned_rests=int(np.sum(pins)),failures=[dict(x=starts[i][0],phase=starts[i][1],speed=starts[i][2],outcome=int(oc[i]),end=ends[i].tolist()) for i in range(N) if oc[i] in (3,4) or pins[i]][:10]))
    assert not np.any(pins)
h=next(h for h in course['holes'] if h['number']==6);ha=S.HoleArrays(h);ha.MP[0,8]=1;ha.MP[0,9:11]=0;ha.MP[0,12]=0
cases=[]
for x in (-2.8,0,2.8):
 for z in (-27.4,-28.6):
  for a in np.linspace(0,2*math.pi,120,endpoint=False):
   r=S.sim_shot(*ha.args(),PH,x,z,0,S.V_MAX*math.cos(a),S.V_MAX*math.sin(a),0,False,path)
   cases.append(int(r[3]))
results.append(dict(hole=6,gate='closed',shots=len(cases),escapes=cases.count(3),timeouts=cases.count(4)))
# Preserve and replay the rare 100k-fuzz failures and slower phase-edge regressions.
seedpath=os.path.join(S.HERE,'..','_work','p7-h11-failing-seeds.json')
if os.path.exists(seedpath):
    seeds=json.load(open(seedpath));hh=S.HoleArrays(next(h for h in course['holes'] if h['number']==11));failed=[]
    for seed in seeds:
        x,y,z=seed['start'];speed=seed['speed'];aim=seed['aim']
        for shift in (0.0,-.65):
            rr=S.sim_shot(*hh.args(),PH,x,z,y,speed*math.cos(aim),speed*math.sin(aim),seed['t0']+shift,True,path)
            if int(rr[3]) in (3,4):failed.append(dict(seed=seed,shift=shift,outcome=int(rr[3])))
    results.append(dict(hole=11,part='saved_failures',shots=len(seeds)*2,escapes=sum(f['outcome']==3 for f in failed),timeouts=sum(f['outcome']==4 for f in failed),failures=failed))
# Full-power p8 broad-fuzz regression: lip-end/side-rail pinch at the west corner.
# Keep the exact original start and absolute phase as reproducible evidence.
hh=S.HoleArrays(h11)
aim=math.radians(119.8036772147401);speed=12.43571800396576
rr=S.sim_shot(*hh.args(),PH,.334332458804512,-29.62569981505206,4.,speed*math.cos(aim),speed*math.sin(aim),283.0106763403176,True,path)
results.append(dict(hole=11,part='p8_lip_corner_full_power',shots=1,escapes=int(rr[3]==3),timeouts=int(rr[3]==4),outcome=int(rr[3]),elapsed=float(rr[4]),end=[float(rr[0]),float(rr[2]),float(rr[1])]))
# Late gate-top/sill riders remain supported and take the next full ride.
hh=S.HoleArrays(h11)
cases=[]
for t in (rise[0]+.4, rise[1], sum(top)/2, descend[0]+.2):
    for x in (-1.4,0.,1.4):
        rr=S.sim_shot(*hh.args(),PH,x,-21.49,1.2,0.,-1.,t,True,path)
        held=path[:int(rr[6])]
        retained=bool(np.any((np.abs(held[:,2]+21.49)<1e-8)&(np.abs(held[:,1]-1.2)<1e-8)&(np.abs(held[:,0])<=1.72)))
        cases.append(dict(t0=t,x=x,retained=retained,outcome=int(rr[3]),elapsed=float(rr[4]),released=bool(rr[2]>=3.99 and rr[1]<-25.7)))
results.append(dict(hole=11,part='gate_top_sill_retention',shots=len(cases),escapes=sum(c['outcome']==3 for c in cases),timeouts=sum(c['outcome']==4 for c in cases),failures=[c for c in cases if not c['retained'] or not c['released'] or c['outcome'] in (3,4)],cases=cases))
print(json.dumps(results,indent=2))
os.makedirs(os.path.dirname(os.path.abspath(opts.out)),exist_ok=True)
json.dump(results,open(opts.out,'w'),indent=2)
assert all(r['escapes']==r['timeouts']==r.get('crossed',0)==0 and not r.get('failures') for r in results)
