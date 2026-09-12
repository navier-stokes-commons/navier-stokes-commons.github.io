#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'/'public'

def load_json(path:Path):
    return json.loads(path.read_text())

def quest(qid:str):
    doc=load_json(CONTENT/'quests.json')
    for q in doc.get('quests',[]):
        if q.get('id')==qid:
            return q
    raise SystemExit(f'PROVE2ME_BRIDGE_FAIL unknown NSC problem {qid}')

def export_candidate(qid:str)->dict:
    q=quest(qid)
    return {
      'schema':'nsc-prove2me-export-candidate-v2',
      'executor_id':'prove2me',
      'nsc_problem_id':q['id'],
      'nsc_program_id':q['mission_id'],
      'plain_mathematical_statement':q.get('task',''),
      'proposed_formal_statement_or_formalization_request':None,
      'source_locators':q.get('source_ids',[]),
      'definition_ledger':[],
      'intended_semantics':q.get('summary',''),
      'semantic_review_requirement':q.get('review',{}),
      'candidate_environment':None,
      'parent_frontier_effect_if_successful':'Must be stated and reviewed before export.',
      'parent_frontier_non_implications':['Kernel checking does not establish informal semantic fidelity.','Kernel checking does not automatically resolve the parent PDE problem.'],
      'existing_platform_search':{'required':True,'policy':'search-and-reuse-before-create','known_overlap':'Existing public Prove2Me Navier-Stokes mission formalizes Fefferman statement A; do not duplicate it.','minimum_queries':['Navier-Stokes','Fefferman','exact theorem names/source titles']},
      'export_state':'candidate'
    }

def statement_digest(text:str)->str:
    return 'sha256:'+hashlib.sha256(text.encode()).hexdigest()

def validate_import(path:Path)->dict:
    d=load_json(path)
    required=['nsc_problem_id','prove2me_mission_or_theorem_url','formal_statement','lean_environment','external_status','observed_at']
    miss=[k for k in required if not d.get(k)]
    if miss: raise SystemExit('PROVE2ME_BRIDGE_FAIL missing '+','.join(miss))
    if not re.fullmatch(r'NS-Q\d{3}',d['nsc_problem_id']): raise SystemExit('PROVE2ME_BRIDGE_FAIL invalid problem id')
    if not str(d['prove2me_mission_or_theorem_url']).startswith('https://prove2.me/'): raise SystemExit('PROVE2ME_BRIDGE_FAIL external URL must be prove2.me')
    if d['external_status'] not in {'unknown','open','proved','disproved','deprecated'}: raise SystemExit('PROVE2ME_BRIDGE_FAIL invalid external status')
    out={
      'schema':'nsc-formalization-link-v1',
      'nsc_problem_id':d['nsc_problem_id'],
      'executor_id':'prove2me',
      'external_url':d['prove2me_mission_or_theorem_url'],
      'prove2me_theorem_id':d.get('prove2me_theorem_id'),
      'formal_statement_digest':statement_digest(d['formal_statement']),
      'lean_environment':d['lean_environment'],
      'external_status':d['external_status'],
      'artifact_locator':d.get('proof_or_disproof_artifact_locator'),
      'observed_at':d['observed_at'],
      'nsc_import_state':'unreviewed-external-evidence',
      'semantic_mapping_review_id':None,
      'automatic_parent_claim_transition':False,
      'note':'External formal evidence only. Semantic correspondence and domain implications require separate NSC review.'
    }
    return out

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd',required=True)
    e=sub.add_parser('export-candidate'); e.add_argument('problem_id'); e.add_argument('--output')
    i=sub.add_parser('validate-import'); i.add_argument('record'); i.add_argument('--output')
    a=ap.parse_args()
    out=export_candidate(a.problem_id) if a.cmd=='export-candidate' else validate_import(Path(a.record))
    text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    target=getattr(a,'output',None)
    if target: Path(target).write_text(text)
    else: sys.stdout.write(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
