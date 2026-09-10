#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from nsc_model import ROOT,C,locale_codes,locale_content_digest,locale_statuses,claim_digest,claims
errs=[]; hex64=re.compile(r'^[0-9a-f]{64}$'); https=re.compile(r'^https://')
def reviewer_ok(x): return isinstance(x,dict) and bool(x.get('id')) and bool(x.get('display_name')) and bool(https.match(str(x.get('profile_url',''))))
for p in sorted((C/'locale_reviews').glob('*.json')):
    try:r=json.loads(p.read_text())
    except Exception as e: errs.append(f'{p.name}: invalid JSON {e}'); continue
    required={'schema','review_id','locale','review_role','reviewer','reviewed_at','content_digest_sha256','review_artifact_url','independence_statement','verdict'}
    if r.get('schema')!='nsc-locale-review-v2': errs.append(f'{p.name}: unsupported receipt schema')
    if required-set(r): errs.append(f'{p.name}: missing fields {sorted(required-set(r))}')
    if r.get('locale') not in locale_codes(): errs.append(f'{p.name}: unknown locale')
    if r.get('review_role') not in {'native-language','subject-domain'}: errs.append(f'{p.name}: bad review role')
    if not reviewer_ok(r.get('reviewer')): errs.append(f'{p.name}: reviewer public identity incomplete')
    if not https.match(str(r.get('review_artifact_url',''))): errs.append(f'{p.name}: review artifact must be public HTTPS')
    if len(str(r.get('independence_statement','')))<20: errs.append(f'{p.name}: independence statement too short')
    if r.get('verdict') not in {'pass','fail'}: errs.append(f'{p.name}: bad verdict')
    if not hex64.fullmatch(str(r.get('content_digest_sha256',''))): errs.append(f'{p.name}: invalid content digest')
for loc,status in locale_statuses().items():
    if status!='scientific-reviewed': continue
    digest=locale_content_digest(loc); rs=[]
    for p in sorted((C/'locale_reviews').glob('*.json')):
        r=json.loads(p.read_text())
        if r.get('locale')==loc and r.get('content_digest_sha256')==digest: rs.append(r)
    passes=[r for r in rs if r.get('verdict')=='pass']; roles={r.get('review_role') for r in passes}; ids={r['reviewer']['id'] for r in passes if reviewer_ok(r.get('reviewer'))}
    if roles!={'native-language','subject-domain'} or len(ids)<2 or any(r.get('verdict')=='fail' for r in rs): errs.append(f'{loc}: invalid scientific-reviewed witness set')
ledger=json.loads((C/'reviews.json').read_text()); recs=ledger.get('records',[]); cby={c['id']:c for c in claims()}; seen=set()
for i,r in enumerate(recs):
    rid=r.get('id',f'index-{i}')
    if rid in seen: errs.append(f'duplicate review id {rid}')
    seen.add(rid)
    required={'id','target_id','target_digest_sha256','review_class','reviewer','independence','conflicts','checks','verdict','residual_uncertainty','evidence_url','reviewed_at'}
    if required-set(r): errs.append(f'{rid}: missing review fields {sorted(required-set(r))}'); continue
    if not reviewer_ok(r.get('reviewer')): errs.append(f'{rid}: reviewer public identity incomplete')
    indep=r.get('independence') or {}
    if not isinstance(indep,dict) or not isinstance(indep.get('independent'),bool) or len(str(indep.get('basis','')))<10: errs.append(f'{rid}: malformed independence evidence')
    if not isinstance(r.get('checks'),list) or not r['checks']: errs.append(f'{rid}: no checks')
    if r.get('verdict') not in {'accept','request-changes','reject','unable-to-assess'}: errs.append(f'{rid}: invalid verdict')
    if not https.match(str(r.get('evidence_url',''))): errs.append(f'{rid}: evidence URL must be public HTTPS')
    if not hex64.fullmatch(str(r.get('target_digest_sha256',''))): errs.append(f'{rid}: invalid target digest')
    if r.get('target_id') in cby and r.get('target_digest_sha256')!=claim_digest(cby[r['target_id']]): errs.append(f'{rid}: stale/wrong claim content digest')
if errs:
    print('EVIDENCE_BINDING_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; raise SystemExit(1)
print(f'EVIDENCE_BINDING_AUDIT_PASS locale_receipts={len(list((C/"locale_reviews").glob("*.json")))} reviews={len(recs)} exact_content_binding=true')
