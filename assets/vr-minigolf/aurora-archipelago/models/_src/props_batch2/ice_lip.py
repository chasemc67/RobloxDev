from pathlib import Path
import shutil
S=Path(__file__).resolve().parent;D=S.parents[2];bk=S/'_backup_ice_lip';bk.mkdir(exist_ok=True)
for p in [S/'parts.json',S/'triangles.json',S/'build_report.json',S/'props_batch2.blend',D/'models/props_batch2_manifest.json']:
 if p.exists():shutil.copy2(p,bk/p.name)
for sub in ['fbx/props_batch2','previews/props_batch2']:shutil.copytree(D/'models'/sub,bk/sub,dirs_exist_ok=True)
p=S/'gen_batch2.py';t=p.read_text();t=t.replace("c=w['center'];sz=w['size'];box(p,mat,c,sz,w.get('yaw',0))", """c=w['center'];sz=w['size']
  if n==10:
   bottom=c[1]-sz[1]/2;top=c[1]+sz[1]/2
   box(p,mat,[c[0],(bottom+top-.3)/2,c[2]],[sz[0],sz[1]-.3,sz[2]],w.get('yaw',0))
   box(p,'Ice',[c[0],top-.215,c[2]],[sz[0],.17,sz[2]],w.get('yaw',0))
   box(p,'Snow',[c[0],top-.065,c[2]],[sz[0],.13,sz[2]],w.get('yaw',0))
  else:box(p,mat,c,sz,w.get('yaw',0))""");p.write_text(t)
p=S/'fitcheck_batch2.py';t=p.read_text().replace("if dressing and dressing[0][0]<.05-1e-5:fail.append('mover to dressing full sweep <0.05')", "if dressing and dressing[0][0]<.15-1e-5:fail.append('mover to dressing full sweep <0.15')");p.write_text(t)
p=S/'build_batch2.py';t=p.read_text().replace("r['lights']=[]", "r['lights']=[]\n    if p['motion']:\n        ax=p['motion']['axis'];r['motion_axis_world']=[ax[0]*math.cos(ang)+ax[2]*math.sin(ang),ax[1],-ax[0]*math.sin(ang)+ax[2]*math.cos(ang)]\n    if p['id']=='h17_aurora_ribbon':r['runtime_signal']=dict(controller='aurora_span',profile=H[17]['moving_parts'][0]['profile'],gradient_materials=['AuroraMint','AuroraViolet'])")
p.write_text(t)
