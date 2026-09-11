#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];errs=[]
protocol=R/'docs/EVALUATION_PROTOCOL.md';basis=R/'docs/EVALUATION_EVIDENCE_BASIS.md';ops=R/'docs/OPERATIONS_AND_FIELD_MEASUREMENT.md';tool=R/'scripts/pareto_review.py'
for p in [protocol,basis,ops,tool]:
    if not p.is_file():errs.append('missing evaluation artifact '+str(p.relative_to(R)))
if protocol.is_file():
    s=protocol.read_text().lower()
    for tok in ['measured pareto frontier','synthetic','human','field evidence','strict local-preflight subset']:
        if tok not in s:errs.append('evaluation protocol missing '+tok)
if basis.is_file():
    s=basis.read_text()
    for tok in ['ISO 9241-210:2019','10.1145/1879831.1879836','arXiv:2406.07791','arXiv:2607.26348','OpenAPI Specification 3.1.2','RFC 8615']:
        if tok not in s:errs.append('evaluation evidence basis missing '+tok)
if ops.is_file():
    s=ops.read_text()
    for tok in ['change lead time','deployment frequency','change fail rate','LCP <= 2.5 s','INP <= 200 ms','CLS <= 0.1','attempt -> result conversion']:
        if tok not in s:errs.append('operations/field plan missing '+tok)
if tool.is_file():
    s=tool.read_text()
    for tok in ['wilson','dominates','synthetic_interval_scope','candidate_stop_signal','holdout_policy','min_holdout_families']:
        if tok not in s:errs.append('Pareto review tool missing '+tok)
quests=json.loads((R/'content/public/quests.json').read_text()).get('quests',[])
q={x.get('id'):x for x in quests}.get('NS-Q036')
if not q:errs.append('pre-registered comparative design quest NS-Q036 missing')
elif not q.get('benchmark_set_id'):errs.append('NS-Q036 lost pre-registered benchmark set')
if errs:
    print('EVALUATION_PROTOCOL_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];raise SystemExit(1)
print('EVALUATION_PROTOCOL_AUDIT_PASS measured_pareto=true synthetic_human_boundary=true preregistered_comparison=true')
