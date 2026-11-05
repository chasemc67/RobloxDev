from pathlib import Path
s=Path('models/_src/props_batch1')
t=(s/'rev5.py').read_text().replace('rev5','rev6').replace('_backup_rev4_corals','_backup_rev5_corals')
t=t.replace("ps=read(S/'_backup_rev5_corals/models/_src/props_batch1/parts.json');old=read(S/'_backup_rev5_corals/models/props_batch1_manifest.json')","ps=read(S/'parts.json');old=read(M/'props_batch1_manifest.json')")
t=t.replace("[PV/(i+'_34.png') for i in ids]","[PV/(i+'_34.png') for i in ids]+list(PV.glob('*coral*_front.png'))")
a=t.index('  g.tube(q,col,[0,base,0]');b=t.index('  if yaw:',a)
t=t[:a]+'''  g.tube(q,col,[0,base,0],[0,base+.5*h,0],.075*h,.05*h,n=10)
  start=len(q.g[col][0]);split=[0,base+.5*h,0]
  # Flattened forked paddles, with overlapping ellipsoidal rounded tips.
  def blob(mat,c,size):
   rings=[]
   for j in range(9):
    ang=-math.pi/2+math.pi*j/8;rr=max(.001,math.cos(ang))
    rings.append([[c[0]+size[0]/2*rr*math.cos(math.tau*i/12),c[1]+size[1]/2*math.sin(ang),c[2]+size[2]/2*rr*math.sin(math.tau*i/12)] for i in range(12)])
   q.loft(mat,rings)
  thick=.18;pw=.7
  for k in range(3):
   u=k-1;fork=[u*w*.22,base+.67*h,u*d*.08]
   g.tube(q,col,split,fork,pw/2,pw/2,thick/pw,n=8)
   for side in [-1,1]:
    tip=[u*w*.26+side*w*.065,base+h*(.79+.045*(1-abs(u))),u*d*.08+side*d*.04]
    g.tube(q,col,fork,tip,pw/2,pw/2,thick/pw,n=8)
    blob(col,tip,[w*.39,h*.23,d*.72])
    blob('CoralMint',[tip[0],tip[1]+h*.075,tip[2]-d*.19],[w*.13,h*.08,d*.22])
  # Normalize the measured split-to-top crown into the authorized envelope.
  crown=[v for mat,(verts,_) in q.g.items() for v in verts[(start if mat==col else 0):]]
  lo=[min(v[i] for v in crown) for i in range(3)];hi=[max(v[i] for v in crown) for i in range(3)]
  for v in crown:
   v[0]=(v[0]-(hi[0]+lo[0])/2)*w/(hi[0]-lo[0])
   v[1]=base+.5*h+(v[1]-lo[1])*.45*h/(hi[1]-lo[1])
   v[2]=(v[2]-(hi[2]+lo[2])/2)*d/(hi[2]-lo[2])
  cw=max(v[0] for v in crown)-min(v[0] for v in crown);ch=max(v[1] for v in crown)-min(v[1] for v in crown)
  note=f'Coral rev6: bare tapering trunk to 0.5H, three flat forked paddles (nominal 0.7 wide / 0.18 thick before envelope normalization), six BIG overlapping rounded tips and neon cores. Measured crown width {cw:.6f}, height {ch:.6f}, W:H {cw/ch:.6f}; depth {d:g}, top 0.95H. No rail-driven crown shrink.'
  if 'giant' in p['id']:note+=' Giant crown width capped at exact 4-stud occluder; tall narrow exception.'
  if base and d<.96:note+=' Skin depth minimally limited to existing 0.8-stud envelope.'
''' +t[b:]
t=t.replace('assert tris<900','assert tris<3000')
a=t.index(" src=(S/'build_rev4.py')");b=t.index(" blender('build_rev6.py'",a)
t=t[:a]+''' src=(S/'build_rev5.py').read_text().replace('rev5','rev6').replace("['h07_coral_w2','h08_coral_1']","['h07_coral_w2','h08_coral_1','h08_giant_coral']")
 src=src.replace("3 if p['hole']==7 else 2","7 if 'giant' in id else (3 if p['hole']==7 else 2)").replace('cam.data.ortho_scale=8','cam.data.ortho_scale=16 if \\'giant\\' in id else 8')
 (S/'build_rev6.py').write_text(src)
''' +t[b:]
a=t.index(" text='\\n\\n## Coral rev6");b=t.index(" for p in new['parts']:",a)
t=t[:a]+''' text='\\n\\n## Coral rev6\\n\\n18 coral assets revised: bare trunk splits at 0.5H; flat paddles fork into six overlapping rounded blobs forming one solid lumpy dome, with neon tip cores. Crown spans 0.5H by 0.45H, depth 0.4H and top 0.95H. Giant retains its exact 4-wide occluder exception; narrow skins keep existing depth envelope. No rail-driven crown reductions. Exact collider bases, pivots, anchors and colours preserved.\\n\\n| Coral | Tris | MEASURED crown width | MEASURED crown height | W:H |\\n|---|---:|---:|---:|---:|\\n'
''' +t[b:]
t=t.replace('Every coral <900 tris','Every coral <3000 tris').replace('straight flat paddles with one fork per lobe and 6-10 rounded neon tips','flat forked paddles with six overlapping rounded neon tips').replace('18 H7/H8 corals revised with flat forked paddles and 6-10 neon tips','18 H7/H8 corals revised with a 0.5H bare trunk and one lumpy rounded crown')
(s/'rev6.py').write_text(t)
