#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from urllib.parse import urljoin
import json,os,sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'; C=ROOT/'content/public'
from nsc_model import project_view,expanded_quests,expanded_claims_doc,public_registry,capabilities
errs=[]; load=lambda p:json.loads(p.read_text())
project=project_view(); missions=load(C/'missions.json'); sources=load(C/'sources.json'); contributions=load(C/'contributions.json'); forges=load(C/'forges.json'); formulas=load(C/'formulas.json'); simulations=load(C/'simulations.json'); benchmarks=load(C/'reference_benchmarks.json'); actions=load(C/'actions.json'); scaling=load(C/'scaling_model.json'); quests={'schema':load(C/'quests.json').get('schema','nsc-quests-v1'),'quests':expanded_quests()}; ladder=load(C/'task_ladder.json'); claims=expanded_claims_doc(); governance=load(C/'governance.json'); taxonomy=load(C/'taxonomy.json'); sprint=load(C/'founding_sprint.json'); reviews=load(C/'reviews.json'); public_ssot=load(ROOT/'PUBLIC_SSOT.json'); authority=load(C/'authority_map.json'); relpol=load(C/'release_policy.json'); reg=public_registry()
checks={
 'frontier':({'project':project['project_id'],'generated_from_public_content':True,'missions':None},P/'data/frontier.json'),
 'sources':(sources,P/'data/sources.json'),'project_metadata':(project,P/'data/project.json'),'contributions':(contributions,P/'data/contributions.json'),'forges':(forges,P/'data/forges.json'),'scaling_model':(scaling,P/'data/scaling-model.json'),'formulas':(formulas,P/'data/formulas.json'),'simulations':(simulations,P/'data/simulations.json'),'reference_benchmarks':(benchmarks,P/'data/reference-benchmarks.json'),'actions':(actions,P/'data/actions.json'),'quests':(quests,P/'data/quests.json'),'task_ladder':(ladder,P/'data/task-ladder.json'),'taxonomy':(taxonomy,P/'data/taxonomy.json'),'claims':(claims,P/'data/claims.json'),'reviews':(reviews,P/'data/reviews.json'),'governance':(governance,P/'data/governance.json'),'founding_sprint':(sprint,P/'data/founding-sprint.json'),'public_ssot':(public_ssot,P/'data/public-ssot.json'),'authority_map':(authority,P/'data/authority-map.json'),'release_policy':(relpol,P/'data/release-policy.json'),'capabilities':({'schema':'nsc-capabilities-v1','capabilities':capabilities()},P/'data/capabilities.json')}
# Every structured endpoint has one canonical address in public_registry.
for key,(expected,path) in checks.items():
    if key not in reg['machine_endpoints']: errs.append(f'machine endpoint missing from public registry: {key}'); continue
    if not path.exists(): errs.append(f'machine endpoint output missing: {path.relative_to(P)}'); continue
    got=load(path)
    if key=='frontier':
        if {m['id'] for m in got.get('missions',[])}!={m['id'] for m in missions}: errs.append('frontier mission IDs differ from canonical missions')
    elif got!=expected: errs.append(f'machine endpoint {key} differs from canonical/derived model')
# Stable protocol minimum: keys are an interface contract; URLs are not duplicated here.
required_keys={'frontier','sources','project_metadata','quests','claims','simulations','capabilities','public_ssot','authority_map','agent_start','agent_skill','llms_index','llms_full','actions','reference_benchmarks'}
if required_keys-set(reg['machine_endpoints']): errs.append('public registry lacks required cold-start endpoint classes')
disc_path='.well-known/commons.json'; disc=load(P/disc_path)
def projected_ref(from_path,target):
    out=os.path.relpath(target.lstrip('/'),start=str(Path(from_path).parent)).replace(os.sep,'/')
    return out+'/' if target.endswith('/') and not out.endswith('/') else out
for k,v in reg['machine_endpoints'].items():
    expected=projected_ref(disc_path,v)
    if disc.get(k)!=expected: errs.append(f'discovery projection differs from registry for {k}')
for k,v in reg['human_routes'].items():
    expected=projected_ref(disc_path,v)
    if disc.get('human_'+k)!=expected: errs.append(f'human route projection differs from registry for {k}')
base='https://example.test/navier-stokes-commons-public/'
disc_url=urljoin(base,disc_path)
for k in list(reg['machine_endpoints'])+[f'human_{x}' for x in reg['human_routes']]:
    ref=disc.get(k,'')
    if ref.startswith('/'): errs.append(f'discovery reference is origin-root-relative and unsafe on project Pages: {k}')
    resolved=urljoin(disc_url,ref)
    if not resolved.startswith(base): errs.append(f'discovery reference escapes project Pages base: {k} -> {resolved}')
frontier_url=urljoin(base,'data/frontier.json')
for m in load(P/'data/frontier.json').get('missions',[]):
    u=m.get('url','')
    if u.startswith('/') or not u.endswith('/'): errs.append(f'{m.get("id")}: invalid project-relative agent URL')
    resolved=urljoin(frontier_url,u)
    if not resolved.startswith(base+'en/missions/'): errs.append(f'{m.get("id")}: frontier URL does not resolve under project base')
    if set(m.get('source_ids',[]))-{s['id'] for s in sources}: errs.append(f'{m.get("id")}: unknown source in machine frontier')
for f in ['start.md','SKILL.md','AGENTS.md','llms.txt','llms-full.txt']:
    path=P/f
    if not path.exists(): errs.append(f'missing public agent artifact {f}'); continue
    txt=path.read_text().lower()
    for bad in ['/'+'mnt'+'/','/'+'dev'+'/'+'shm'+'/','local'+'host','127.'+'0.0.1']:
        if bad in txt: errs.append(f'{f}: local/internal reference {bad}')
if errs:
    print('AGENT_ENDPOINT_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; sys.exit(1)
print(f'AGENT_ENDPOINT_AUDIT_PASS missions={len(missions)} sources={len(sources)} contributions={len(contributions)} endpoints={len(reg["machine_endpoints"])} forge_adapters={len(forges.get("adapters",[]))}')
