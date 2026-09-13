#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]; d=json.loads((R/'content/public/clay_problem_status.json').read_text()); errs=[]
a={x['id']:x for x in d.get('alternatives',[])}
if set(a)!={'A','B','C','D'}: errs.append('alternatives must be exactly A/B/C/D')
for k in ['A','B']:
    if '0' not in a.get(k,{}).get('forcing','') and 'none' not in a.get(k,{}).get('forcing','').lower(): errs.append(k+' must encode unforced f=0')
    if a.get(k,{}).get('mathematical_status')!='open': errs.append(k+' must remain open')
    if a.get(k,{}).get('display_status')!='OPEN': errs.append(k+' display status drift')
for k in ['C','D']:
    if 'source-reported' not in a.get(k,{}).get('mathematical_status',''): errs.append(k+' OpenAI claim must remain source-reported')
    if a.get(k,{}).get('display_status')!='OPENAI CLAIM': errs.append(k+' display status must derive from source-reported claim state')
if d['official_problem']['institutional_status']['state'] not in {'not-yet-recognized-by-CMI','cmi-apparently-settled-evaluation-pending'}: errs.append('CMI institutional state conflated with publication claim')
if 'A and B remain open' not in d['landing_thesis']['headline']: errs.append('first-screen thesis must expose unresolved A/B')
if errs: print('R11_STATUS_AUDIT_FAIL'); print('\n'.join(errs)); raise SystemExit(1)
print('R11_STATUS_AUDIT_PASS abcd=true claim_vs_recognition_separate=true')
