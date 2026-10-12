#!/usr/bin/env python3
"""Stage s wrist regressions using simulated controller input. No planned/aimed golf shots.
One seeded random low-speed stroke validates TOTAL; fade gate uses synchronous local test states.
"""
import argparse
import json
import os
import time
from run_playtests import Studio, set_edit_attrs
from menu_shots import menu, pointer
from ui_shots import capture
from wrist_sim import LEVEL_HEAD
from stage_r_wrist import LOOK

GEOMETRY = r'''
local gui=game.Players.LocalPlayer.PlayerGui:FindFirstChild('VRWrist')
assert(gui and gui:IsA('SurfaceGui'),'missing wrist gui')
local rows={}
for _,d in gui:GetDescendants() do
 if d:IsA('TextLabel') or d:IsA('TextButton') then
  local strokes={}
  for _,v in d:GetChildren() do
   if v:IsA('UIStroke') and v.ApplyStrokeMode==Enum.ApplyStrokeMode.Contextual then
    table.insert(strokes,{thickness=v.Thickness*(d:FindFirstChildOfClass('UIScale') and d:FindFirstChildOfClass('UIScale').Scale or 1),color=v.Color:ToHex()})
   end
  end
  table.insert(rows,{name=d.Name,text=d.Text,size=d.TextSize*(d:FindFirstChildOfClass('UIScale') and d:FindFirstChildOfClass('UIScale').Scale or 1),scaled=d.TextScaled,fits=d.TextFits,
   color=d.TextColor3:ToHex(),font=d.Font.Name,button=d:IsA('TextButton'),strokes=strokes,
   position={d.Position.X.Offset,d.Position.Y.Offset},extent={d.Size.X.Offset,d.Size.Y.Offset}})
 end
end
return game.HttpService:JSONEncode({canvas={gui.CanvasSize.X,gui.CanvasSize.Y},face=gui.Face.Name,texts=rows})
'''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='playtests/stage-s/wrist-regression')
    args=ap.parse_args()
    os.makedirs(args.out,exist_ok=True)
    st=Studio()
    result={'steps':{},'pass':False}
    old=json.loads(st.luau("return game.HttpService:JSONEncode(workspace:GetAttributes())"))
    keys=('GolfTestMode','SimulateVR','SkipMenu','PBInStudio')
    def save():
        with open(os.path.join(args.out,'stage_s_checks.json'),'w') as f:json.dump(result,f,indent=2)
    def wait(fn,label,seconds=8):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            r=fn()
            if r:return r
            time.sleep(.15)
        raise AssertionError(label)
    def state():return pointer(st,'regressionState')
    def page():
        r=menu(st,'state')
        return (json.loads(r) if isinstance(r,str) else r).get('page')
    def click(name,expected):
        target=wait(lambda:next((x for x in pointer(st,'targets') if x['name']==name),None),'missing '+name)
        pointer(st,'aim',{'hand':'RightHand','point':target['world']})
        wait(lambda:pointer(st,'state')['pointer'].get('button')==name,'not hovered '+name)
        pointer(st,'trigger','RightHand')
        wait(lambda:page()==expected,'wrong page '+name)
    def wrist_visible():return pointer(st,'state')['wrist'].get('shown')
    try:
        st.stop_play()
        set_edit_attrs(st,{'GolfTestMode':False,'SimulateVR':True,'SkipMenu':None,'PBInStudio':False})
        st.start_play();time.sleep(12)
        menu(st,'close');st.luau(LEVEL_HEAD,'Client')
        initial=state()
        assert initial.get('hole')==1 and initial.get('strokes',0)==0,initial
        pointer(st,'clubAway');pointer(st,'wrist',True)
        wait(wrist_visible,'watch card absent')
        click('WristMenu','title')
        click('Resume',None)
        after=state()
        assert after.get('hole')==1 and after.get('strokes',0)==0,after
        result['steps']['h1_zero_stroke_resume']={'pass':True,'before':initial,'after':after};save()

        pointer(st,'clubAway');pointer(st,'wrist',False);time.sleep(.9)
        pointer(st,'offHandToggle')
        wait(wrist_visible,'nonclub button did not show lowered wrist')
        result['steps']['button_lowered_pose']={'pass':True,'state':state()}
        pointer(st,'offHandToggle');pointer(st,'wrist',False);time.sleep(.9)
        pointer(st,'wristPalm')
        wait(wrist_visible,'palm-up watch pose absent')
        result['steps']['palm_up']={'pass':True,'state':state()}
        capture(st,os.path.join(args.out,'palm_up.png'))
        pointer(st,'wrist',True);time.sleep(.5)
        pointer(st,'offHandToggle');time.sleep(.8)
        assert not wrist_visible(),'button dismissal reopened in the same watch pose'
        pointer(st,'offHandToggle')
        wait(wrist_visible,'button did not reopen card')
        pointer(st,'offHandToggle');pointer(st,'wrist',False);time.sleep(.8)
        pointer(st,'wrist',True)
        wait(wrist_visible,'automatic pose display did not rearm after lowering')
        result['steps']['button_dismiss_rearm']={'pass':True}
        geometry=json.loads(st.luau(GEOMETRY,'Client'))
        failures=[]
        for row in geometry['texts']:
            minimum=64 if row['button'] else 120 if row['name'] in ('par','stroke','total','best') else 56
            ok=(row['size']>=minimum and not row['scaled'] and row['fits'] and row['color'].upper()=='3B2412'
                and row['font'] in ('FredokaOne','GothamBlack')
                and any(abs(v['thickness']-2)<.001 and v['color'].upper()=='FFF4DC' for v in row['strokes'])
                and row['position'][0]>=0 and row['position'][1]>=0
                and row['position'][0]+row['extent'][0]<=1024 and row['position'][1]+row['extent'][1]<=784)
            if not ok:failures.append(row['name'])
        result['steps']['text']={'pass':not failures and geometry['canvas']==[1024,784] and geometry['face']=='Top','failures':failures,'geometry':geometry}
        capture(st,os.path.join(args.out,'wrist_card.png'))
        st.luau(LOOK,'Client');st.luau('workspace.CurrentCamera.FieldOfView=22 return true','Client')
        time.sleep(.4);capture(st,os.path.join(args.out,'wrist_card_zoom.png'))
        st.luau('workspace.CurrentCamera.FieldOfView=70 return true','Client');st.luau(LEVEL_HEAD,'Client')
        pointer(st,'clubAway');pointer(st,'wrist',False);time.sleep(.8)
        result['steps']['fade_gate']=pointer(st,'fadeGateTest')
        stroke=pointer(st,'randomStroke',617)
        assert stroke['hit'],stroke
        wait(lambda:(state().get('strokes') or 0)>0,'stroke not counted')
        s=state()
        result['steps']['unfinished_total']={'pass':s['wrist']['total']=='E' and s.get('hole')==1 and not s.get('holed'),'randomStroke':stroke,'state':s}
        result['problems']={'server':st.problems('Server'),'client':st.problems('Client')}
        result['pass']=all(v.get('pass') for v in result['steps'].values()) and not result['problems']['server'] and not result['problems']['client']
        print(json.dumps(result,indent=2),flush=True)
    except Exception as exc:
        result['error']=str(exc)
        print('STAGE S CHECK FAILED:',exc,flush=True)
        raise
    finally:
        save();st.stop_play();set_edit_attrs(st,{k:old.get(k) for k in keys})

if __name__=='__main__':main()
