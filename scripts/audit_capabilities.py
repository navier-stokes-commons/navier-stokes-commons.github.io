#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
from nsc_model import ROOT,capabilities
P=ROOT/'public'; errs=[]; caps=capabilities()
for k,v in caps.items():
    if not v.get('satisfied'): errs.append(f'{k}: unsatisfied')
out=json.loads((P/'data/capabilities.json').read_text()) if (P/'data/capabilities.json').exists() else {}
if out.get('capabilities')!=caps: errs.append('generated capabilities endpoint does not equal derived capabilities')
guide=(ROOT/'docs/PRODUCT_GUIDE.md').read_text()
if '<!-- GENERATED:participation-capability:start -->' not in guide: errs.append('product guide participation claim is not a generated projection')
if caps['bounded_participation_ladder']['statement'] not in guide: errs.append('product guide lacks derived ladder statement')
if caps['student_entry_path']['statement'] not in guide: errs.append('product guide lacks evidence-derived student entry statement')
# Any positive student-entry claim must have actual dependency-free low-rung quest witnesses.
if caps['student_entry_path']['satisfied'] and len(caps['student_entry_path'].get('quest_ids',[]))<2: errs.append('student entry capability lacks witness quests')
if errs:
    print('CAPABILITY_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; sys.exit(1)
print('CAPABILITY_AUDIT_PASS '+' '.join(f'{k}=true' for k in caps))
