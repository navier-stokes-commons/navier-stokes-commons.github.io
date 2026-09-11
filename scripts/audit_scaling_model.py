#!/usr/bin/env python3
from pathlib import Path
import json, math, os, sys, re
from nsc_model import public_registry
ROOT=Path(__file__).resolve().parents[1]
model=json.loads((ROOT/'content/public/scaling_model.json').read_text())
errs=[]
if model.get('schema')!='nsc-scaling-model-v1': errs.append('unexpected scaling model schema')
if model.get('source_id')!='openai-paper': errs.append('scaling model must cite openai-paper')
h=model.get('parameters',{}).get('h',{}).get('range_open')
if h != [0,0.01]: errs.append(f'h open range must be [0, 0.01], got {h!r}')
expected={'ell_r':(0.5,0),'ell_z':(0.5,-1),'u_theta':(-0.5,-1),'u_z':(-0.5,-1),'u_r':(-0.5,0),'volume':(1.5,-1),'energy':(0.5,-3),'re_theta':(0,-1),'aspect':(0,-1)}
qs={q['id']:q for q in model.get('quantities',[])}
for qid,(c,hc) in expected.items():
    q=qs.get(qid)
    if not q: errs.append(f'missing quantity {qid}'); continue
    e=q.get('exponent',{})
    if e.get('constant')!=c or e.get('h')!=hc: errs.append(f'wrong exponent for {qid}: {e}')
for hv in (0.0005,0.005,0.0095):
    if not 0<hv<0.01: errs.append('test h outside source range')
    if not 0.5-3*hv>0: errs.append('energy exponent must stay positive')
    for tau in (1e-2,1e-20,1e-60):
        er=tau**.5; ez=tau**(.5-hv); sp=tau**(-.5-hv); en=tau**(.5-3*hv); aspect=tau**(-hv)
        if not (0<er<=1 and 0<ez<=1 and sp>=1 and 0<en<=1 and aspect>=1): errs.append('derived monotonicity failure')
# The human representation is now the immersive source-constrained vortex chamber. No redundant ASCII wall is required.
for loc in ('en','es','ar','zh-Hans'):
    p=ROOT/'public'/loc/'index.html'
    if not p.exists(): errs.append(f'missing home {loc}'); continue
    s=p.read_text()
    required=['data-vortex-stage','data-representation-status="schematic"','data-quantitative-status="derived-leading-exponents"','data-vortex-static','data-vortex-canvas','data-k','data-h','data-r-out','data-z-out','data-u-out','data-e-out']
    for token in required:
        if token not in s: errs.append(f'{loc} home missing immersive-stage token {token}')
    if 'data-ascii-live' in s or 'ascii-sequence' in s or 'data-mechanism-atlas' in s:
        errs.append(f'{loc} home retained obsolete flagship representation')
    if not re.search(r'<input[^>]+data-k[^>]+min="\.5"[^>]+max="60"|<input[^>]+min="\.5"[^>]+max="60"[^>]+data-k',s):
        errs.append(f'{loc} k control has unexpected range')
# Ambient ASCII trace is intentionally only an identity hook; it must be finite/optional and is not the no-JS oracle.
root=(ROOT/'public/index.html').read_text()
if 'data-scale-trace' not in root: errs.append('root finite ambient scale trace missing')
for token in ('data-vortex-stage','data-vortex-static','data-vortex-canvas','data-representation-status="schematic"','data-quantitative-status="derived-leading-exponents"'):
    if token not in root: errs.append('root flagship missing '+token)
registry=public_registry(); scaling_route=registry['machine_endpoints']['scaling_model']; discovery_route=registry['machine_endpoints']['discovery']
endpoint=ROOT/'public'/scaling_route.lstrip('/')
if not endpoint.exists(): errs.append('public scaling model endpoint missing')
elif json.loads(endpoint.read_text()) != model: errs.append('public scaling model endpoint differs from canonical content')
disc=json.loads((ROOT/'public'/discovery_route.lstrip('/')).read_text())
expected_disc=os.path.relpath(scaling_route.lstrip('/'),start='.well-known').replace(os.sep,'/')
if disc.get('scaling_model')!=expected_disc: errs.append('discovery endpoint missing deployment-relative scaling_model link')
if errs:
    print('SCALING_MODEL_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'SCALING_MODEL_AUDIT_PASS quantities={len(qs)} locales_checked=4 representation=immersive-source-constrained-vortex')
