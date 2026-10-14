"""Read-only stage-au5 dependency and repeatable camera evidence."""
import base64,io,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from run_playtests import Studio
OUT=Path('playtests/stage-au5')
s=Studio();assert s.mode()[0]=='Edit'
if sys.argv[1]=='dependencies':
 code='''
local c=workspace.CourseAurora local b=assert(c:FindFirstChild('Blockout'))
local r={parts={},scripts={},references={},protectedNames={}}
for _,v in b:GetDescendants() do
 if v:IsA('LuaSourceContainer') then table.insert(r.scripts,v:GetFullName()) end
 if v:IsA('BasePart') then table.insert(r.parts,{path=v:GetFullName(),class=v.ClassName,collide=v.CanCollide,query=v.CanQuery,touch=v.CanTouch,tags=v:GetTags()}) end
 if v:IsA('SpawnLocation') or v.Name:lower():find('respawn') then table.insert(r.protectedNames,v:GetFullName()) end
end
for _,v in game:GetDescendants() do
 if v:IsA('LuaSourceContainer') then
  local n=0 for line in v.Source:gmatch('[^\\n]+') do n+=1
   if line:find('Blockout',1,true) or line:find('h10_bank',1,true) or line:find('h05_rail',1,true) or line:find('h12_rail',1,true) or line:find('h15_rail',1,true) then table.insert(r.references,{path=v:GetFullName(),line=n,text=line}) end
  end
 elseif v:IsA('ObjectValue') and v.Value and v.Value:IsDescendantOf(b) then table.insert(r.references,{path=v:GetFullName(),target=v.Value:GetFullName()})
 elseif v:IsA('JointInstance') or v:IsA('WeldConstraint') then
  for _,p in {v.Part0,v.Part1} do if p and p:IsDescendantOf(b) then table.insert(r.references,{path=v:GetFullName(),target=p:GetFullName()}) end end
 end
end
return game.HttpService:JSONEncode(r)
'''
 r=json.loads(s.luau(code));(OUT/'blockout-dependencies.json').write_text(json.dumps(r,indent=2)+'\n')
 print('blockout parts',len(r['parts']),'scripts',len(r['scripts']),'refs',r['references'])
else:
 phase=sys.argv[1];images=[]
 for hole,pos,target in [(10,[530,171,100],[493,151,63]),(2,[-55,89,515],[-96,65,480])]:
  r=s.m.req('tools/call',{'name':'screen_capture','arguments':{'studio_id':s.id,'capture_id':f'au5-h{hole}-{phase}','camera_position':pos,'look_at_position':target}})
  raw=next(c for c in r['result']['content'] if c.get('type')=='image')
  im=Image.open(io.BytesIO(base64.b64decode(raw['data']))).convert('RGB');im.save(OUT/f'h{hole}-{phase}.png')
  images.append((hole,im))
 width=max(im.width for _,im in images);height=sum(im.height+30 for _,im in images)
 board=Image.new('RGB',(width,height),'#131820');d=ImageDraw.Draw(board);y=0
 for hole,im in images:
  d.text((12,y+7),f'Aurora H{hole} | stage au5 {phase}',fill='white');board.paste(im,(0,y+30));y+=im.height+30
 board.save(f'logs/stages/au5-{phase}.png');print('saved',phase)
