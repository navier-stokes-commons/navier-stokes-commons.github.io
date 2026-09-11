#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
try:
    from jsonschema import Draft202012Validator, FormatChecker
except Exception as e:
    print(f'SCHEMA_AUDIT_UNAVAILABLE jsonschema={e}',file=sys.stderr); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; S=ROOT/'schemas'; errs=[]
load=lambda p:json.loads(p.read_text())
def check(name,schema_name,objects):
    schema=load(S/schema_name); v=Draft202012Validator(schema,format_checker=FormatChecker())
    for label,obj in objects:
        for e in sorted(v.iter_errors(obj),key=lambda x:list(x.path)):
            path='.'.join(str(x) for x in e.path) or '<root>'
            errs.append(f'{name}:{label}:{path}: {e.message}')
check('mission','mission.schema.json',[(x['id'],x) for x in load(C/'missions.json')])
check('quest','quest.schema.json',[(x['id'],x) for x in load(C/'quests.json')['quests']])
check('contribution','contribution.schema.json',[(x.get('id','?'),x) for x in load(C/'contributions.json')])
check('review','review.schema.json',[(x.get('id','?'),x) for x in load(C/'reviews.json').get('records',[])])
check('locale-review','locale-review.schema.json',[(p.name,load(p)) for p in sorted((C/'locale_reviews').glob('*.json'))])
check('actions','actions.schema.json',[('document',load(C/'actions.json'))])
check('reference-benchmarks','reference-benchmarks.schema.json',[('document',load(C/'reference_benchmarks.json'))])
check('research-context','research-context.schema.json',[('document',load(C/'research_context.json'))])
if errs:
    print('SCHEMA_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:300]: print(' - '+e,file=sys.stderr)
    if len(errs)>300: print(f' ... {len(errs)-300} more',file=sys.stderr)
    raise SystemExit(1)
print('SCHEMA_AUDIT_PASS mission=true quest=true contribution=true review=true locale_review=true actions=true reference_benchmarks=true research_context=true')
