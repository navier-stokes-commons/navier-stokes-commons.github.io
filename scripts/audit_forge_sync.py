#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; errs=[]
sprint=json.loads((ROOT/'content/public/founding_sprint.json').read_text())
quests={q['id']:q for q in json.loads((ROOT/'content/public/quests.json').read_text())['quests']}
script=ROOT/'scripts/sync_founding_sprint_issue.py'; workflow=ROOT/'.github/workflows/sync-founding-sprint.yml'; doc=ROOT/'docs/FORGE_SYNC.md'
for p in [script,workflow,doc]:
    if not p.exists(): errs.append('missing '+p.relative_to(ROOT).as_posix())
if not errs:
    spec=importlib.util.spec_from_file_location('nsc_forge_sync',script); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
    title,body=mod.render('example/nsc')
    if mod.SENTINEL not in body: errs.append('rendered issue missing machine sentinel')
    if str(len(sprint['quest_ids'])) not in title: errs.append('rendered title does not derive sprint count')
    for qid in sprint['quest_ids']:
        if body.count(f'`{qid}`')!=1: errs.append(f'rendered body must contain sprint quest exactly once: {qid}')
        if quests[qid]['title'] not in body: errs.append(f'rendered body missing current quest title: {qid}')
    if re.search(r'/issues/\d+',script.read_text()): errs.append('sync script hardcodes an issue number')
    wt=workflow.read_text()
    for token in ['contents: read','issues: write','python3 scripts/sync_founding_sprint_issue.py --apply']:
        if token not in wt: errs.append('workflow missing '+token)
    for line in wt.splitlines():
        m=re.search(r'uses:\s*([^\s#]+)',line)
        if m and not re.search(r'@[0-9a-f]{40}$',m.group(1)): errs.append('workflow action not pinned: '+m.group(1))
if errs:
    print('FORGE_SYNC_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'FORGE_SYNC_AUDIT_PASS sprint_quests={len(sprint["quest_ids"])} hardcoded_issue_number=false reconciliation=push-main')
