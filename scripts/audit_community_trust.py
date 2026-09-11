#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from nsc_model import ROOT, public_registry
C=ROOT/'content/public'; P=ROOT/'public'; errs=[]
ctx=json.loads((C/'research_context.json').read_text())
if ctx.get('schema')!='nsc-research-context-v1': errs.append('research context schema mismatch')
for key in ['claim_status','affiliation_status','lineage','concurrent_accounts','commons_policy']:
    if not ctx.get(key): errs.append('research context missing '+key)
# Required attributed public accounts and lineage anchors.
blob=json.dumps(ctx,ensure_ascii=False)
for token in ['Diego Córdoba','Luis Martínez-Zoroa','Tristan Buckmaster','OpenAI','C and D','A/B']:
    if token not in blob: errs.append('research context missing '+token)
if 'does not know whether their data was used' not in blob: errs.append('Buckmaster uncertainty boundary missing')
if 'no specific user data was accessed' not in blob: errs.append('OpenAI attributed data-use account missing')
if ctx.get('affiliation_status',{}).get('independent') is not True or 'not affiliated' not in ctx.get('affiliation_status',{}).get('statement','').lower(): errs.append('independent affiliation boundary missing')
# Public context page must preserve status separation.
page=P/'en/context/index.html'
if not page.exists(): errs.append('public context page missing')
else:
    s=page.read_text()
    for token in ['Independent review open','not affiliated','RESEARCH LINEAGE','CONCURRENT PUBLIC ACCOUNTS','Review without endorsement','C/D','A/B']:
        if token not in s: errs.append('context page missing '+token)
    for bad in ['Clay accepted','Clay-certified solution','provenance dispute resolved']:
        if bad.lower() in s.lower(): errs.append('context page overstates status: '+bad)
# Canonical machine projection.
reg=public_registry(); route=reg['machine_endpoints'].get('research_context')
if not route: errs.append('research_context machine endpoint not registered')
else:
    out=P/route.lstrip('/')
    if not out.exists(): errs.append('research_context public endpoint missing')
    elif json.loads(out.read_text())!=ctx: errs.append('research_context endpoint drift')
# Intake must require prior-work/credit disclosure on both supported live forges.
required={
 '.github/ISSUE_TEMPLATE/claim_quest.yml':['Prior work and credit check','required: true'],
 '.github/ISSUE_TEMPLATE/open_attempt.yml':['Prior work and credit check','required: true'],
 '.github/ISSUE_TEMPLATE/submit_result.yml':['Prior work, lineage, and credit statement','required: true'],
 '.github/ISSUE_TEMPLATE/side_quest.yml':['Prior work, overlap, and novelty','required: true'],
 '.gitlab/issue_templates/attempt.md':['Prior work / credit check'],
 '.gitlab/issue_templates/result.md':['Prior work / lineage / credit statement'],
 '.gitlab/issue_templates/side_quest.md':['Prior work, overlap, and novelty'],
}
for rel,tokens in required.items():
    p=ROOT/rel
    if not p.exists(): errs.append('missing contribution template '+rel); continue
    s=p.read_text()
    for tok in tokens:
        if tok not in s: errs.append(f'{rel}: missing {tok}')
if errs:
    print('COMMUNITY_TRUST_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'COMMUNITY_TRUST_AUDIT_PASS lineage={len(ctx["lineage"])} accounts={len(ctx["concurrent_accounts"])} forge_intake=github+gitlab')
