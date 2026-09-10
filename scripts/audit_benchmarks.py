#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; errs=[]
b=json.loads((C/'reference_benchmarks.json').read_text()); qd=json.loads((C/'quests.json').read_text()); reg=json.loads((C/'public_registry.json').read_text())
refs=b.get('references',[]); ids=[x.get('id') for x in refs]; urls=[x.get('url') for x in refs]
if len(refs)<20: errs.append('reference corpus unexpectedly small')
if len(ids)!=len(set(ids)): errs.append('duplicate benchmark reference IDs')
if len(urls)!=len(set(urls)): errs.append('duplicate benchmark URLs')
if not b.get('claim_policy',{}).get('universal_superiority_forbidden'): errs.append('universal superiority guard missing')
required_roles={'research-collaboration','visual-craft','scientific-interaction','simulation-pedagogy','accessibility-resilience','resource-efficiency'}
roles={r for x in refs for r in x.get('roles',[])}
if required_roles-roles: errs.append('benchmark role coverage missing: '+','.join(sorted(required_roles-roles)))
q=next((x for x in qd['quests'] if x['id']=='NS-Q036'),None)
if not q or q.get('benchmark_set_id')!=b.get('id'): errs.append('NS-Q036 not bound to canonical benchmark set')
digest=hashlib.sha256(json.dumps(b,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
out=ROOT/'public'/reg['machine_endpoints']['reference_benchmarks'].lstrip('/')
if not out.exists() or json.loads(out.read_text())!=b: errs.append('public benchmark projection missing or stale')
page=ROOT/'public'/reg['human_routes']['benchmarks'].lstrip('/')/'index.html'
if not page.exists() or b['id'] not in page.read_text(): errs.append('human benchmark page missing canonical set ID')
if errs:
 print('BENCHMARK_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; raise SystemExit(1)
print(f'BENCHMARK_AUDIT_PASS set={b["id"]} references={len(refs)} sha256={digest}')
