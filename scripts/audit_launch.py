#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
from nsc_model import ROOT,C,project_view,locale_statuses,quest_ids_for_claim,capabilities,expanded_claims_doc
P=ROOT/'public'; errs=[]
def load(name): return json.loads((C/name).read_text())
project=project_view(); missions=load('missions.json'); qdoc=load('quests.json'); quests=qdoc['quests']; ladder=load('task_ladder.json'); claims=load('claims.json'); sprint=load('founding_sprint.json'); gov=load('governance.json')
mids={m['id'] for m in missions}; qids={q['id'] for q in quests}; rung_list=[r['id'] for r in ladder['rungs']]; rungs=set(rung_list); cids={c['id'] for c in claims['claims']}; sids={s['id'] for s in load('sources.json')}
if project.get('release_stage')!='open-beta': errs.append('release_stage must be open-beta')
if project.get('participation_status')!='open': errs.append('participation must be open')
if not rung_list or len(rung_list)!=len(rungs): errs.append('task ladder rung IDs must be nonempty and unique')
if not any(r.get('starter') for r in ladder['rungs']): errs.append('task ladder must explicitly identify at least one starter rung')
if len(quests)<len(missions): errs.append('quest catalog is too sparse')
for m in missions:
    if 'quest_ids' in m: errs.append(f"{m['id']}: reverse quest projection must not be canonical")
    if not any(q['mission_id']==m['id'] for q in quests): errs.append(f"{m['id']}: no quest")
for q in quests:
    if 'founding_sprint' in q: errs.append(f"{q['id']}: founding sprint membership duplicated on quest")
    if q['mission_id'] not in mids: errs.append(f"{q['id']}: unknown mission")
    if q['rung'] not in rungs: errs.append(f"{q['id']}: invalid rung")
    if not q.get('non_exclusive'): errs.append(f"{q['id']}: exclusive work forbidden")
    if not q.get('deliverables') or not q.get('acceptance'): errs.append(f"{q['id']}: untestable quest")
    if not q.get('review',{}).get('class'): errs.append(f"{q['id']}: no review class")
    if set(q.get('source_ids',[]))-sids: errs.append(f"{q['id']}: source reference failure")
    if set(q.get('dependencies',[]))-qids: errs.append(f"{q['id']}: dependency failure")
    if set(q.get('claim_ids',[]))-cids: errs.append(f"{q['id']}: claim reference failure")
for c in claims['claims']:
    if 'status' in c: errs.append(f"{c['id']}: elevated claim status must be evidence-derived, not canonical")
    if 'target_quest_ids' in c: errs.append(f"{c['id']}: reverse quest projection must not be canonical")
    if c.get('baseline_status') not in {'source-reported','primary-source-defined','derived-unreviewed'}: errs.append(f"{c['id']}: invalid baseline claim state")
    # Every claim is reachable from at least one verification/review quest.
    if not quest_ids_for_claim(c['id']): errs.append(f"{c['id']}: no quest can change/evaluate evidence state")
if set(sprint['quest_ids'])-qids: errs.append('founding sprint references unknown quest')
if len(set(sprint['quest_ids']))!=len(sprint['quest_ids']): errs.append('founding sprint duplicate quest ID')
if len(sprint['quest_ids'])<8: errs.append('founding sprint lacks breadth')
if not gov.get('decision_rules',{}).get('accept_scientific_artifact'): errs.append('scientific acceptance rule missing')
required_root=['PUBLIC_SSOT.json','GOVERNANCE.md','REVIEW_POLICY.md','MISSION_POLICY.md','COMMUNITY_STANDARDS.md','DCO.md','AGENTS.md','ROADMAP.md','CITATION.cff']
required_public=['data/authority-map.json','data/release-policy.json','data/quests.json','data/task-ladder.json','data/taxonomy.json','data/claims.json','data/governance.json','data/founding-sprint.json','data/reviews.json','data/public-ssot.json','data/capabilities.json','data/actions.json','data/reference-benchmarks.json','.well-known/commons.json','llms.txt','llms-full.txt','en/quests/index.html','en/sprint/index.html','en/governance/index.html','en/benchmarks/index.html']
for x in required_root:
    if not (ROOT/x).exists(): errs.append('missing '+x)
for x in required_public:
    if not (P/x).exists(): errs.append('missing public/'+x)
for q in quests:
    if not (P/f'en/quests/{q["id"].lower()}/index.html').exists(): errs.append(f'{q["id"]}: quest page missing')
derived_claims=expanded_claims_doc()
if json.loads((P/'data/claims.json').read_text())!=derived_claims: errs.append('public claim statuses/reverse links are not derived from evidence model')
allowed={'canonical','full-translation-review-pending','interface-preview','scientific-reviewed'}
if set(locale_statuses().values())-allowed: errs.append('unsupported locale review status')
for loc,status in locale_statuses().items():
    if status=='scientific-reviewed' and loc=='en': errs.append('canonical locale cannot use scientific-reviewed state')
for cid,c in capabilities().items():
    if not c['satisfied']: errs.append('launch capability unsatisfied: '+cid)
if errs:
    print('OPEN_BETA_LAUNCH_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:300]: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'OPEN_BETA_LAUNCH_AUDIT_PASS missions={len(missions)} quests={len(quests)} sprint={len(sprint["quest_ids"])} claims={len(cids)} locales={len(project["locales"])} canonical_relations=one-way capabilities=derived')
