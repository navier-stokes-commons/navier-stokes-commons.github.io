#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];errs=[]
for p in [R/'scripts/prove2me_reuse_gate.py',R/'content/public/external_executors.json']:
    if not p.is_file():errs.append('missing '+p.relative_to(R).as_posix())
if not errs:
    p=subprocess.run([sys.executable,'scripts/prove2me_reuse_gate.py','--selftest'],cwd=R,text=True,capture_output=True)
    if p.returncode or 'SELFTEST_PASS' not in p.stdout:errs.append('reuse gate selftest failed '+p.stdout+p.stderr)
    d=json.loads((R/'content/public/external_executors.json').read_text())['executors'][0]
    if 'search-before-create' not in d.get('catalog_policy',''):errs.append('external executor lacks search-before-create policy')
    if d.get('known_overlap',{}).get('title')!='Formalize Navier-Stokes Open Problem':errs.append('known statement-A mission missing')
if errs:
    print('R15_PROVE2ME_REUSE_AUDIT_FAIL',file=sys.stderr)
    [print(' - '+x,file=sys.stderr) for x in errs]
    raise SystemExit(1)
print('R15_PROVE2ME_REUSE_AUDIT_PASS existing_A_reuse=true search_before_create=true')
