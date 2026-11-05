_H17_GAPS=None
def h17_design_gaps():
    """Exact holes.json geometry: each placed hour-stone box vs the four shadow-arm blocker boxes, swept 0.5 deg over 360."""
    global _H17_GAPS
    if _H17_GAPS is None:
        sa=next(m for m in HOLES[16]['moving_parts'] if m['id']=='shadow_arm');piv=np.array(sa['pivot'],float);_H17_GAPS={}
        for e in [x for x in REG if x['id'].startswith('h17_hour_stone_')]:
            S=box_poly(e['box']['center'],e['box']['size'],0);best=(np.inf,None)
            for a in np.arange(0,360,.5):
                R=Ry(a)
                for b in sa['blockers']:
                    g=poly_gap(box_poly(R@np.array(b['center'])+piv,b['size'],b['yaw']+a),S)
                    if g<best[0]:best=(g,float(a))
            _H17_GAPS[e['hour']]=dict(gap=best[0],angle=best[1])
    return _H17_GAPS
def _rest(pid):return [comp_poly(c,[0,0,0],pid,'') for c in COMP[pid]]
def _verts(pid):return np.vstack([c['verts'] for c in COMP[pid]])
def _mpart(h,i):return next(m for m in HOLES[h]['moving_parts'] if m['id']==i)
def _strip_polys():
    out=[]
    for b in _mpart(8,'windpump')['blockers']:
        r=b.get('roll',0);out.append(box_poly(Rz(r)@np.array(b['center']),b['size'],0,r))
    return out
def cover_p5(rep,parts_rest,mp):
    blk=_mpart(8,'windpump')['blockers']
    pts=np.vstack([box_samples(b['center'],b['size'],0,0,(5,9,3))@Rz(b.get('roll',0)).T for b in blk])  # roll turns the strip about the hub
    vis=_rest('h09_windpump_vanes');col=_rest('h09_windpump_vanes_collision');sp=_strip_polys()
    rv=max(np.hypot(*np.array(c['verts'])[:,:2].T).max() for c in COMP['h09_windpump_vanes'] if c['material'].startswith('Lip'))
    cv=_verts('h09_windpump_vanes_collision')
    rep['h09_windpump_vanes']=dict(strip_samples=len(pts),covered=int(inside(pts,vis).sum()),visual_tip_radius=float(rv),
        note='visual (r .6..4.1, CanCollide off) covers all 48 p9b collision strips (r .6..4.06); the extra .04 visual tip is art-only')
    rep['h09_windpump_vanes_collision']=dict(samples=len(pts),covered=int(inside(pts,col).sum()),visual_within_exact_boxes=bool(inside(cv,sp,1e-5).all()),
        outer_radius=float(np.hypot(cv[:,0],cv[:,1]).max()),inner_radius=float(min(np.hypot(*np.array(c['verts'])[:,:2].T).min() for c in COMP['h09_windpump_vanes_collision'])),
        components=len(COMP['h09_windpump_vanes_collision']),note='collision mesh == the 48 holes.json strips (every strip sample inside the mesh, every mesh vertex inside a strip)')
    ob=_mpart(13,'ore_bucket');b0=ob['blockers'][0];foot=ob['blockers'][1:]
    p0=box_samples(b0['center'],b0['size'],n=(7,7,7));p1=np.vstack([box_samples(b['center'],b['size'],n=(3,9,3)) for b in foot])
    fp=_rest('h14_ore_bucket_foot_collision');fpoly=[box_poly(b['center'],b['size'],b.get('yaw',0)) for b in foot]
    bucket=_rest('h14_ore_bucket')
    # skid vs strips at rest: per strip column, skid underside at the column edges/centre minus the strip bottom
    import gen_p5_profile as GP
    prof=GP.skid_profile(foot);devs=[]
    for b in foot:
        x0=b['center'][0]-b['size'][0]/2;x1=x0+b['size'][0];bot=b['center'][1]-b['size'][1]/2
        for x in (x0+1e-9,(x0+x1)/2,x1-1e-9):devs.append(GP.underside(prof,x)-bot)
    skidv=np.vstack([c['verts'] for c in COMP['h14_ore_bucket'] if c['material']=='Iron' and max(v[1] for v in c['verts'])<=-9.95+1e-6])
    rep['h14_ore_bucket']=dict(body_samples=len(p0),body_covered=int(inside(p0,bucket).sum()),
        skid_vertices=len(skidv),skid_inside_strip_union=bool(inside(skidv,fpoly,1e-5).all()),skid_above_strip_bottom_min=float(min(devs)),skid_above_strip_bottom_max=float(max(devs)),
        visual_within_exact_boxes=bool(inside(skidv,fpoly,1e-5).all()) and min(devs)>=-1e-6,
        note='Iron skid follows the strip underside (low centre, chamfered raised outer corners): every skid vertex lies inside the union of the 14 strip boxes, so it is never lower than the collider at any swing angle')
    rep['h14_ore_bucket_foot_collision']=dict(samples=len(p1),covered=int(inside(p1,fp).sum()),visual_within_exact_boxes=bool(inside(_verts('h14_ore_bucket_foot_collision'),fpoly,1e-5).all()),
        components=len(COMP['h14_ore_bucket_foot_collision']),note='collision mesh == the 14 holes.json / p9-report foot strips')
def cover_p5_static(rep,boxcov):
    pt=next(q for q in HOLES[6]['player_teleport_points'] if q['id']=='bridge2_exit')
    rep['h07_teleport_pad_exit']=dict(boxcov('h07_teleport_pad_exit',[dict(center=[0,pt['size'][1]/2,0],size=pt['size'])],[0,0,0]),note='p9: full 3 x .02 x 2 pad (cup notch removed), pivot = pad base centre [5.15,0,-59]')
    rs=next(e for e in REG if e['id']=='h07_island_respawn_stone');sx,sy,sz=rs['size']
    pts=box_samples([0,sy/2,0],rs['size'],n=(17,3,17));pts=pts[np.abs(pts[:,0])+np.abs(pts[:,2])<=sx/2+sz/2-.12-1e-9]
    rep['h07_island_respawn_stone']=dict(samples=len(pts),covered=int(inside(pts,_rest('h07_island_respawn_stone')).sum()),
        visual_within_exact_boxes=bool(inside(_verts('h07_island_respawn_stone'),[box_poly([0,sy/2,0],rs['size'])],1e-5).all()),
        note='chamfered octagon inside the holes.json .8 x .02 x .8 marker box; samples = octagon interior')
    for e in [x for x in REG if x['id'].startswith('h17_hour_stone_')]:
        s=e['box']['size']
        rep[e['id']]=dict(boxcov(e['id'],[dict(center=[0,(s[1]-.02)/2,0],size=[s[0],s[1]-.02,s[2]])],[0,0,0]),
            visual_within_exact_boxes=bool(inside(_verts(e['id']),[box_poly([0,s[1]/2,0],s)],1e-5).all()),
            pivot=e['pivot'],collidable=e['collidable'],note='solid body y 0..0.78 + numeral relief 0.78..0.80, all inside the exact 1.2 x .8 x 1.2 box; pivot = base centre')
def _sweep_min(pid,angles,axis,piv_y,sel=None):
    V=_verts(pid) if sel is None else sel;best=(np.inf,None)
    for a in angles:
        y=(V@Raxis(axis,a).T)[:,1].min()+piv_y
        if y<best[0]:best=(float(y),float(a))
    return best
def spec_checks(results):
    out={}
    wp=_mpart(8,'windpump');py=wp['pivot'][1];rot=np.arange(0,360,.5)
    c=_sweep_min('h09_windpump_vanes_collision',rot,wp['axis'],py);v=_sweep_min('h09_windpump_vanes',rot,wp['axis'],py)
    cf=_sweep_min('h09_windpump_vanes_collision',np.arange(c[1]-.5,c[1]+.5,.001),wp['axis'],py)
    down=_sweep_min('h09_windpump_vanes_collision',[0.0],wp['axis'],py)
    lower=[]
    for a in rot:
        R=Raxis(wp['axis'],a);lower.append(float((_verts('h09_windpump_vanes_collision')@R.T)[:,1].min()-(_verts('h09_windpump_vanes')@R.T)[:,1].min()))
    out['H9 collision tip to felt']=dict(min=c[0],angle_deg=c[1],fine_min=cf[0],fine_angle_deg=cf[1],at_vane_straight_down=down[0],expected=0.06,felt_y=0.0,
        status='PASS' if abs(c[0]-.06)<=1e-3 and c[0]>=.05 else 'FAIL',note='sweep 0.5 deg/360 + 0.001 deg refine; min occurs when a strip tip corner (r 4.06) is straight down')
    out['H9 visual tip to felt']=dict(min=v[0],angle_deg=v[1],expected=0.02,art_only=True,visual_minus_collision_lowest_max=max(lower),
        status='PASS' if v[0]>=.02-1e-3 else 'FAIL',note='visual r 4.1 tip (CanCollide off) dips up to %.4f below the collider: the only allowed visual-below-collider case'%max(lower))
    ob=_mpart(13,'ore_bucket');py=ob['pivot'][1];sw=np.arange(-9,9.00001,.05);fv=_verts('h14_ore_bucket_foot_collision')
    cen=fv[np.abs(fv[:,0])<=.9+1e-6];outer=fv[(np.abs(np.abs(fv[:,0])-1.05)<1e-6)&(fv[:,1]<-10.0)]
    cm=_sweep_min(None,sw,ob['axis'],py,cen);om=_sweep_min(None,sw,ob['axis'],py,outer)
    rest_c=float(cen[:,1].min()+py);rest_o=float(outer[:,1].min()+py)
    worst_c=sorted(((float((cen@Raxis(ob['axis'],a).T)[:,1].min()+py),float(a)) for a in sw))[:3]
    worst_o=sorted(((float((outer@Raxis(ob['axis'],a).T)[:,1].min()+py),float(a)) for a in sw))[:3]
    vb=_verts('h14_ore_bucket');lower=max(float((fv@Raxis(ob['axis'],a).T)[:,1].min()-(vb@Raxis(ob['axis'],a).T)[:,1].min()) for a in sw)
    out['H14 centre strips (|x|<=0.9) to felt']=dict(min=cm[0],angle_deg=cm[1],rest=rest_c,worst3=worst_c,expected_min=0.06,expected_rest=0.0613,
        status='PASS' if abs(cm[0]-.06)<=1e-3 and abs(rest_c-.0613)<=1e-3 and cm[0]>=.05 else 'FAIL')
    out['H14 outer corners (x=+-1.05) to felt']=dict(min=om[0],angle_deg=om[1],rest=rest_o,worst3=worst_o,expected_min=0.1502,expected_rest=0.2044,
        status='PASS' if om[0]>=.15-1e-6 and abs(rest_o-.2044)<=1e-3 else 'FAIL')
    out['H14 visual never lower than foot collider']=dict(max_visual_below_collider=lower,status='PASS' if lower<=1e-6 else 'FAIL',note='per swing angle: lowest collider point minus lowest visual point (<=0 means the visual is never lower)')
    # H7 respawn stone + pads
    rs=next(e for e in REG if e['id']=='h07_island_respawn_stone');sp=parts_of(rs);gaps={}
    for pid in ('h07_teleport_pads','h07_teleport_pad_exit'):
        e=next(x for x in REG if x['id']==pid)
        for inst in e['instances']:gaps[inst['id']]=min(poly_gap(P,Q) for P in sp for Q in parts_of(e,inst['pivot']))
    rails={k:v['clearance'] for k,v in results['h07_island_respawn_stone'].items() if v['kind']=='rail/wall'}
    rmin=min(rails.items(),key=lambda kv:kv[1])
    out['H7 respawn stone gaps']=dict(to_pads=gaps,min_pad=min(gaps.values()),to_nearest_rail=dict(rail=rmin[0],gap=rmin[1]),overlaps_island_pad=gaps['bridge1_island']<=0,
        status='PASS' if min(gaps.values())>=.15 and rmin[1]>=.15 and gaps['bridge1_island']>0 else 'FAIL')
    cup=HOLES[6]['cup'];pe=next(x for x in REG if x['id']=='h07_teleport_pad_exit');pv=_verts('h07_teleport_pad_exit')+np.array(pe['pivot'])
    lo=pv.min(0);hi=pv.max(0);cx,cz=cup['position'][0],cup['position'][2]
    d=math.hypot(max(lo[0]-cx,0,cx-hi[0]),max(lo[2]-cz,0,cz-hi[2]))-cup['radius']
    out['H7 exit pad to cup rim']=dict(gap=d,expected=0.15,status='PASS' if d>=.15-1e-6 else 'FAIL')
    # H17 hour stones vs arms+heads sweep
    dg=h17_design_gaps();stones={}
    for pid in ['h17_shadow_arms']+[f'h17_shadow_arm_head_{y}' for y in (0,90,180,270)]:
        for name,b in results[pid].items():
            if not name.startswith('h17_hour_stone_'):continue
            sid=name.rsplit('_',1)[0]
            if b['clearance']<stones.get(sid,{}).get('gap',np.inf):stones[sid]=dict(gap=b['clearance'],angle_deg=b['angle'],mover=pid,status=b['status'])
    for sid,v in stones.items():
        e=next(x for x in REG if x['id']==sid);v.update(collidable=e['collidable'],holes_json_design_gap=dg[e['hour']]['gap'],holes_json_design_angle=dg[e['hour']]['angle'])
    rail=[v['gap'] for k,v in stones.items() if v['collidable']]
    out['H17 hour stones vs arm+head sweep']=dict(stones=stones,rail_stone_min=min(rail),rail_expected=0.26,decorative_min=min(v['gap'] for v in stones.values() if not v['collidable']),
        status='PASS' if abs(min(rail)-.26)<=2e-3 and all(v['status']!='FAIL' for v in stones.values()) else 'FAIL',
        note='rail stones (collision ON) clear the sweep by the holes.json 0.26; decorative stones (collision OFF) inherit the exact holes.json box gap (spec question raised)')
    return out
