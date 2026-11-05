#!/usr/bin/env python3
"""Validate real mover apertures and reject the same geometry with its lip removed."""
import copy
import json
import os
import sim as S
course=json.load(open(os.path.join(S.HERE,'..','holes.json')))
for n in (6,11):
    h=next(h for h in course['holes'] if h['number']==n)
    issues=S.validate(h)
    assert not [i for i in issues if i[0]=='ERROR'],(n,issues)
    print(f'PASS H{n} phase-aware geometry validation: {len(issues)} findings')
h=copy.deepcopy(next(h for h in course['holes'] if h['number']==11))
h['moving_parts']=[m for m in h['moving_parts'] if m['id']!='quay_lip']
errors=[e for e in S.validate(h) if e[0]=='ERROR']
assert any('quay' in message and 'edge' in message for _,message in errors),errors
print(f'PASS missing lip rejected: {len(errors)} enclosure errors')
