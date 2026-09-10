#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; errs=[]
a=json.loads((C/'actions.json').read_text()); reg=json.loads((C/'public_registry.json').read_text()); ops=a.get('operations',[]); ids=[x.get('id') for x in ops]
required={'discover','claim_quest','open_mission_attempt','submit_result','request_review','propose_side_quest','accept_record'}
if required-set(ids): errs.append('required operations missing: '+','.join(sorted(required-set(ids))))
if len(ids)!=len(set(ids)): errs.append('duplicate action IDs')
for op in ops:
 for key in ('github_template','gitlab_template'):
  rel=op.get(key)
  if rel and not (ROOT/rel).exists(): errs.append(f"{op['id']}: missing {key} {rel}")
 if op['id']!='discover' and not op.get('invariants'): errs.append(f"{op['id']}: transaction invariants missing")
op=next(x for x in ops if x['id']=='submit_result')
if 'submission is not acceptance' not in ' '.join(op.get('invariants',[])).lower(): errs.append('submit_result acceptance boundary missing')
out=ROOT/'public'/reg['machine_endpoints']['actions'].lstrip('/')
if not out.exists() or json.loads(out.read_text())!=a: errs.append('public action-contract projection missing or stale')
if errs:
 print('ACTION_CONTRACT_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; raise SystemExit(1)
print(f'ACTION_CONTRACT_AUDIT_PASS operations={len(ops)} protocol={a["protocol"]}')
