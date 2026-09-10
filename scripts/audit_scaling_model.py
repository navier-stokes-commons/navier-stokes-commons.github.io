#!/usr/bin/env python3
from pathlib import Path
import json, math, os, sys
from nsc_model import public_registry
ROOT=Path(__file__).resolve().parents[1]
model=json.loads((ROOT/'content/public/scaling_model.json').read_text())
errs=[]
if model.get('schema')!='nsc-scaling-model-v1': errs.append('unexpected scaling model schema')
if model.get('source_id')!='openai-paper': errs.append('scaling model must cite openai-paper')
h=model.get('parameters',{}).get('h',{}).get('range_open')
if h != [0,0.01]: errs.append(f'h open range must be [0, 0.01], got {h!r}')
expected={
 'ell_r':(0.5,0), 'ell_z':(0.5,-1), 'u_theta':(-0.5,-1), 'u_z':(-0.5,-1),
 'u_r':(-0.5,0), 'volume':(1.5,-1), 'energy':(0.5,-3), 're_theta':(0,-1), 'aspect':(0,-1)
}
qs={q['id']:q for q in model.get('quantities',[])}
for qid,(c,hc) in expected.items():
    q=qs.get(qid)
    if not q: errs.append(f'missing quantity {qid}'); continue
    e=q.get('exponent',{})
    if e.get('constant')!=c or e.get('h')!=hc: errs.append(f'wrong exponent for {qid}: {e}')
# Derived sanity checks at admissible points.
for hv in (0.0005,0.005,0.0095):
    if not (0<hv<0.01): errs.append('test h outside source range')
    if not 0.5-3*hv>0: errs.append('energy exponent must stay positive over allowed h range')
    for tau in (1e-2,1e-20,1e-60):
        er=tau**(0.5)
        ez=tau**(0.5-hv)
        sp=tau**(-0.5-hv)
        en=tau**(0.5-3*hv)
        if not (0<er<=1 and 0<ez<=1 and sp>=1 and 0<en<=1): errs.append('derived normalized monotonicity failure')
# Public artifacts must expose the model and both interactive and no-JS representations.
for loc in ('en','es','ar','zh-Hans'):
    p=ROOT/'public'/loc/'index.html'
    if not p.exists(): errs.append(f'missing home page {loc}'); continue
    s=p.read_text()
    for token in ('data-scaling-lab','data-tau-k','data-h','data-ascii-live','ascii-sequence','scaling-table','openai-paper'):
        if token not in s: errs.append(f'{loc} home missing {token}')
    if not __import__('re').search(r'<input[^>]+min="0\.25"[^>]+data-tau-k',s): errs.append(f'{loc} tau control must stay inside open interval tau < 1')
    for qid in ('ell_r','ell_z','u_theta','energy'):
        if not __import__('re').search(rf'data-curve=\"{qid}\"[^>]*d=\"[^\"]+',s): errs.append(f'{loc} home missing precomputed no-JS curve {qid}')
registry=public_registry(); scaling_route=registry['machine_endpoints']['scaling_model']; discovery_route=registry['machine_endpoints']['discovery']
endpoint=ROOT/'public'/scaling_route.lstrip('/')
if not endpoint.exists(): errs.append('public scaling model endpoint missing')
else:
    if json.loads(endpoint.read_text()) != model: errs.append('public scaling model endpoint differs from canonical content')
disc=json.loads((ROOT/'public'/discovery_route.lstrip('/')).read_text())
expected_disc=os.path.relpath(scaling_route.lstrip('/'),start='.well-known').replace(os.sep,'/')
if disc.get('scaling_model')!=expected_disc: errs.append('discovery endpoint missing deployment-relative scaling_model link')
if errs:
    print('SCALING_MODEL_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'SCALING_MODEL_AUDIT_PASS quantities={len(qs)} locales_checked=4')
