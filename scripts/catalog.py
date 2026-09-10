#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'

def load(name): return json.loads((C/name).read_text())
def ids(pattern,items):
    out=[]
    for x in items:
        m=re.fullmatch(pattern,x['id'])
        if m: out.append(int(m.group(1)))
    return out

def validate():
    missions=load('missions.json'); qdoc=load('quests.json'); quests=qdoc['quests']; sources=load('sources.json'); claims=load('claims.json'); ladder=load('task_ladder.json')
    mids={m['id'] for m in missions}; qids={q['id'] for q in quests}; sids={s['id'] for s in sources}; cids={c['id'] for c in claims['claims']}; rungs={x['id'] for x in ladder['rungs']}; errs=[]
    if len(mids)!=len(missions): errs.append('duplicate mission IDs')
    if len(qids)!=len(quests): errs.append('duplicate quest IDs')
    for q in quests:
        if q['mission_id'] not in mids: errs.append(f"{q['id']}: unknown mission {q['mission_id']}")
        if q['rung'] not in rungs: errs.append(f"{q['id']}: unknown rung {q['rung']}")
        if set(q.get('source_ids',[]))-sids: errs.append(f"{q['id']}: unknown source IDs")
        if set(q.get('dependencies',[]))-qids: errs.append(f"{q['id']}: unknown dependencies")
        if set(q.get('claim_ids',[]))-cids: errs.append(f"{q['id']}: unknown claim IDs")
        if not q.get('non_exclusive'): errs.append(f"{q['id']}: must be non-exclusive")
        if not q.get('acceptance') or not q.get('deliverables'): errs.append(f"{q['id']}: missing acceptance/deliverables")
    for m in missions:
        expected={q['id'] for q in quests if q['mission_id']==m['id']}
        if not expected: errs.append(f"{m['id']}: no bounded quest")
    if errs:
        print('CATALOG_INVALID',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; return 1
    print(f'CATALOG_VALID missions={len(missions)} quests={len(quests)} sources={len(sources)} claims={len(cids)} rungs={len(rungs)}'); return 0

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    sp.add_parser('validate'); sp.add_parser('next-quest-id'); sp.add_parser('next-mission-id')
    a=ap.parse_args(); missions=load('missions.json'); quests=load('quests.json')['quests']
    if a.cmd=='validate': return validate()
    if a.cmd=='next-quest-id': print(f"NS-Q{max(ids(r'NS-Q(\\d{3})',quests),default=0)+1:03d}"); return 0
    if a.cmd=='next-mission-id': print(f"NS-M{max(ids(r'NS-M(\\d{2})',missions),default=0)+1:02d}"); return 0
if __name__=='__main__': raise SystemExit(main())
