#!/usr/bin/env python3
# Summarize a cursor-agent stream-json log: tool calls (name + short args), assistant text, errors.
import json,sys
f=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 40
out=[]
for l in open(f, errors='replace'):
    try: j=json.loads(l)
    except: 
        if l.strip(): out.append('RAW: '+l.strip()[:300])
        continue
    t=j.get('type'); st=j.get('subtype')
    if t=='tool_call':
        tc=j.get('tool_call',{}); k=next(iter(tc),'?'); v=tc.get(k,{})
        a=v.get('args',{})
        if st=='started':
            if 'command' in a: d=a['command']
            elif k=='mcpToolCall' or 'toolName' in a: d=f"{a.get('providerIdentifier','')}/{a.get('toolName',a.get('name',''))} {json.dumps(a.get('args',''))}"
            else: d=json.dumps(a)
            out.append(f"> {k}: {d[:220]}")
        else:
            r=json.dumps(v.get('result',''))
            if any(w in r.lower() for w in ['error','approval','rejected','denied','refused']): out.append(f"  <{k} result: {r[:300]}")
    elif t=='assistant':
        txt=''.join(c.get('text','') for c in j.get('message',{}).get('content',[]) if isinstance(c,dict))
        if txt.strip(): out.append('ASSISTANT: '+txt.strip()[:600])
    elif t=='result':
        out.append('RESULT: '+json.dumps(j)[:1500])
print('\n'.join(out[-n:]))
