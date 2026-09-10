#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
from urllib.parse import urljoin,urlparse
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'; errs=[]
# Deliberately consume only generated public artifacts. No content/public imports are allowed here.
SITE_BASE='https://example.test/navier-stokes-commons-public/'
def local_from_url(url):
    parsed=urlparse(url); base_path=urlparse(SITE_BASE).path
    if parsed.scheme!=urlparse(SITE_BASE).scheme or parsed.netloc!=urlparse(SITE_BASE).netloc or not parsed.path.startswith(base_path):
        raise ValueError('public reference escapes deployment base: '+url)
    rel=parsed.path[len(base_path):]
    p=P/rel
    if p.is_dir(): p=p/'index.html'
    return p
def get(ref,base_url):
    url=urljoin(base_url,ref); p=local_from_url(url)
    if not p.exists(): raise FileNotFoundError(url)
    return json.loads(p.read_text())
try:
    # Discover the bootstrap document from the published .well-known namespace rather than duplicating its configured route.
    candidates_discovery=[]
    for candidate in sorted((P/'.well-known').glob('*.json')):
        try:
            obj=json.loads(candidate.read_text())
        except Exception:
            continue
        if all(k in obj for k in ['quests','task_ladder','actions','frontier','sources']):
            candidates_discovery.append((candidate,obj))
    if len(candidates_discovery)!=1:
        raise RuntimeError(f'expected exactly one Commons discovery document, found {len(candidates_discovery)}')
    discovery_path,discovery=candidates_discovery[0]
    discovery_url=urljoin(SITE_BASE,discovery_path.relative_to(P).as_posix())
    quests=get(discovery['quests'],discovery_url)['quests']
    ladder=get(discovery['task_ladder'],discovery_url)['rungs']
    actions=get(discovery['actions'],discovery_url)['operations']
    frontier=get(discovery['frontier'],discovery_url)['missions']
    sources=get(discovery['sources'],discovery_url)
except Exception as e:
    print('AGENT_COLD_START_AUDIT_FAILED public discovery traversal: '+str(e),file=sys.stderr); raise SystemExit(1)
starter={r['id'] for r in ladder if r.get('starter')}
candidates=[q for q in quests if q.get('status')=='open' and q.get('rung') in starter and not q.get('dependencies')]
if not candidates: errs.append('no open dependency-free starter quest reachable from public discovery')
selected=sorted(candidates,key=lambda q:q['id'])[0] if candidates else None
if selected:
    mids={m['id'] for m in frontier}; sids={s['id'] for s in sources}
    if selected['mission_id'] not in mids: errs.append('selected quest parent mission not reachable')
    if set(selected.get('source_ids',[]))-sids: errs.append('selected quest sources not reachable')
ops={o['id']:o for o in actions}
for oid in ['claim_quest','submit_result','request_review']:
    if oid not in ops: errs.append('missing transaction '+oid)
if 'claim_quest' in ops and 'never grants exclusivity' not in ops['claim_quest'].get('invariants',[]): errs.append('claim operation lacks non-exclusivity invariant')
if 'submit_result' in ops and 'submission is not acceptance' not in ops['submit_result'].get('invariants',[]): errs.append('result transaction collapses submission into acceptance')
for key in ['agent_start','agent_skill','agent_index','llms_index']:
    route=discovery.get(key)
    if not route:
        errs.append('discovery missing agent context route '+key); continue
    try: p=local_from_url(urljoin(discovery_url,route))
    except Exception as e: errs.append('agent context escapes deployment base '+key+': '+str(e)); continue
    if not p.exists() or not p.read_text().strip(): errs.append('agent context missing '+key)
if errs:
    print('AGENT_COLD_START_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; raise SystemExit(1)
out={'schema':'nsc-agent-cold-start-v1','start':discovery_path.relative_to(P).as_posix(),'synthetic_deployment_base':SITE_BASE,'private_context_used':False,'starter_rungs':sorted(starter),'candidate_count':len(candidates),'selected_quest':selected['id'],'parent_mission':selected['mission_id'],'transactions_verified':['claim_quest','submit_result','request_review'],'pass':True}
res=ROOT/'audit/open-beta/agent_cold_start.json'; res.parent.mkdir(parents=True,exist_ok=True); res.write_text(json.dumps(out,indent=2)+'\n')
print(f'AGENT_COLD_START_AUDIT_PASS public_only=true candidates={len(candidates)} selected={selected["id"]} transactions=3')
