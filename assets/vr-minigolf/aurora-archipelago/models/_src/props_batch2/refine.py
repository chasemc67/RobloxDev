from pathlib import Path
S=Path(__file__).resolve().parent
p=S/'gen_batch2.py';t=p.read_text()
t=t.replace("[4,4.2,4]","[3.75,4.2,4]").replace("(-2.3,4.2),(0,7),(2.3,4.2)],-2.3,2.3","(-1.85,4.2),(0,7),(1.85,4.2)],-2,2").replace("for dx in [-1.85,1.85]","for dx in [-1.7,1.7]")
t=t.replace("relative_add(p,q,[x,0,z],90)\nbox(p,'Timber',[x,1.1", "relative_add(p,q,[x,0,z],90)\n# constrain tent depth to rear of pocket wall inside source envelope\nfor mat,(vs,fs) in p.g.items():\n for v in vs:v[2]*=.5\nbox(p,'Timber',[x,1.1")
t=t.replace("z+1.48],[.6,2.2,.04]","z+.73],[.6,2.2,.04]").replace("[.55,.2,2.8]","[.55,.2,1.4]")
t=t.replace("[w,h,d]);crystal(p,[x,.3,z-d*.35]","[w-.2,h,d]);crystal(p,[x,.3,z-d*.35]")
# source revision: world envelope is a view cue; static body behind circular open mouth
start=t.index(" rounded(p,'CoralPink',[c[0],c[1]-h/2,c[2]],[w,h,d],12)")
end=t.index(" p.notes.append",start)
t=t[:start]+''' rings=[]
 for zoff,rr,cy in [(-d/2,.15,c[1]),(-d*.3,w*.4,c[1]),(0,w*.5,c[1]),(d*.25,w*.4,c[1]-.4),(d/2-.12,w*.24,c[1]-h*.25)]:
  rings.append([[c[0]+rr*math.cos(i*math.tau/16)-p.anchor[0],cy+rr*math.sin(i*math.tau/16)-p.anchor[1],c[2]+zoff-p.anchor[2]] for i in range(16)])
 p.loft('CoralPink',rings,cap0=True,cap1=False)
 # luminous faceted rim around the open aperture, entirely behind the playable spit
 rr=w*.24;cy=c[1]-h*.25;zz=c[2]+d/2-.12
 for k in range(16):
  t=k*math.tau/16;u=(k+1)*math.tau/16
  tube(p,'CoralMint',[c[0]+rr*math.cos(t),cy+rr*math.sin(t),zz],[c[0]+rr*math.cos(u),cy+rr*math.sin(u),zz],.05,n=4)
 # concentric tapered spiral ridge on the rear half, not across the mouth
 for k in range(20):
  t=k/20*math.pi*4;u=(k+1)/20*math.pi*4;rr=w*.35*(1-k/24);rr2=w*.35*(1-(k+1)/24)
  tube(p,'CoralOrange',[c[0]+rr*math.cos(t),c[1]+rr*math.sin(t),c[2]-d*.15],[c[0]+rr2*math.cos(u),c[1]+rr2*math.sin(u),c[2]-d*.15],.08,n=5)
''' +t[end:]
p.write_text(t)
# movers use >=.05 clearance, as batch2 explicit brief
p=S/'fitcheck_batch2.py';t=p.read_text().replace("if minimum[0]<.1-1e-5:","if minimum[0]<( .05 if p['motion'] else .1)-1e-5:");p.write_text(t)
