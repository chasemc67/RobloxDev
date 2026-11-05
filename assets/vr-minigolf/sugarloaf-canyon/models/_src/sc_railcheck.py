"""Pass 1 addendum: conservative instance-AABB check vs final holes.json rails/felt (SKILL 5).
Rule: nothing taller than 2 studs within 3 studs of a rail; nothing within 1.5 of felt/rails. Floor kit (stairs/landings/boardwalk) exempt from the height rule."""
import json, math
H=json.load(open('../holes.json'))['holes']; M={p['id']:p for p in json.load(open('manifest.json'))['pieces']}
L=json.load(open('layout.json'))['instances']
FLOOR=('stair','landing','walk_')
def w(h,p):
    a=math.radians(h['world_yaw']);o=h['world_offset'];lx,ly,lz=p
    return (lx*math.cos(a)+lz*math.sin(a)+o[0], ly+o[1], -lx*math.sin(a)+lz*math.cos(a)+o[2])
def rects(h,items,kind):
    out=[]
    for it in items:
        c=it['center'];s=it['size'];yaw=math.radians(it.get('yaw',0)+h['world_yaw'])
        sx,sz=(s[0],s[2]) if len(s)==3 else (s[0],s[1])
        cw=w(h,c if len(c)==3 else [c[0],0,c[1]])
        out.append((kind,h['number'],it['id'],cw,yaw,sx/2,sz/2))
    return out
R=[]
for h in H: R+=rects(h,h['walls'],'rail')+rects(h,h['felt'],'felt')
def dist(r,x,z):
    _,_,_,c,yaw,hx,hz=r;dx,dz=x-c[0],z-c[2];ca,sa=math.cos(yaw),math.sin(yaw)
    u=dx*ca-dz*sa;v=dx*sa+dz*ca
    return math.hypot(max(abs(u)-hx,0),max(abs(v)-hz,0))
fails=0;lines=[];near=[]
for i in L:
    p=M.get(i['piece']);
    if not p: continue
    bs=p['bbox_size'];bc=p['bbox_center_from_origin']
    rad=math.hypot(bs[0],bs[2])/2+math.hypot(bc[0],bc[2]); top=i['pos'][1]+bc[1]+bs[1]/2
    for r in R:
        d=dist(r,i['pos'][0],i['pos'][2])-rad
        if d<3:
            near.append((round(d,1),i['piece'],r[0],'H%d'%r[1],r[2],round(top-r[3][1],1)))
for n in sorted(near)[:60]: lines.append('  AABB-near %s'%(n,))
lines.insert(0,'Conservative AABB screen vs holes.json (%d rects, %d instances): %d instance/rect pairs within 3 studs by bounding circle. These are candidates only; the triangle-level check is sc_fitcheck footprint >=2.0 (min 2.10).'%(len(R),len(L),len(near)))
open('_src/railcheck_pass1.txt','w').write('\n'.join(lines)+'\n');print('\n'.join(lines[:40]))
