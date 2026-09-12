#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];p=R/'content/public/intake.json';d=json.loads(p.read_text());errs=[]
if d.get('schema')!='nsc-unified-intake-v1':errs.append('wrong intake schema')
seen=set()
for x in d.get('items',[]):
 for k in ['id','forge','kind','repository','native_id','url','title','fingerprint']:
  if k not in x:errs.append('item missing '+k)
 if x.get('id') in seen:errs.append('duplicate intake id '+str(x.get('id')))
 seen.add(x.get('id'))
 if x.get('status')=='accepted':errs.append('intake may not encode scientific acceptance directly')
 if '<script' in str(x).lower():errs.append('untrusted script text present')
if errs:
 print('R14_INTAKE_AUDIT_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print(f'R14_INTAKE_AUDIT_PASS items={len(d.get("items",[]))} accepted_direct=0')
