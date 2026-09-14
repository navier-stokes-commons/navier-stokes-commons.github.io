#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CFG=ROOT/'audit/review-system-v2'
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract-id',required=True);ap.add_argument('--candidate',required=True);ap.add_argument('--evidence-manifest',required=True);ap.add_argument('--output',required=True);ap.add_argument('--informed-second-pass',action='store_true');a=ap.parse_args()
 template=(CFG/'prompts/REVIEW_TEMPLATE.md').read_text();contract=json.loads((CFG/'contracts'/f'{a.contract_id}.json').read_text());cand=json.loads(Path(a.candidate).read_text());evid=json.loads(Path(a.evidence_manifest).read_text())
 allowed={m for x in contract.get('evidence_requirements',[]) for m in x.get('modalities',[])};items=[x for x in evid.get('items',[]) if x.get('modality') in allowed]
 blind=contract.get('blindness',{});must_blind=blind.get('blind_to_prior_verdicts') or blind.get('blind_to_candidate_age') or blind.get('blind_to_author_rationale')
 if must_blind and not a.informed_second_pass:
  exposed={k:contract[k] for k in ['id','kind','role','mission','epistemic_scope','blindness','observation_protocol','evidence_requirements','output_contract']}
  candidate_view={'product_digest_sha256':cand.get('product_digest_sha256')};phase='blind'
 else:
  exposed=contract;candidate_view={'candidate_id':cand.get('candidate_id'),'product_digest_sha256':cand.get('product_digest_sha256'),'objective':cand.get('objective'),'known_unresolved':cand.get('known_unresolved',[])};phase='informed'
 rendered=template+'\n\n## Review phase\n'+phase+'\n\n## Evaluator contract\n```json\n'+json.dumps(exposed,indent=2)+'\n```\n\n## Candidate binding\n```json\n'+json.dumps(candidate_view,indent=2)+'\n```\n\n## Authorized evidence manifest\n```json\n'+json.dumps({'candidate_id':evid.get('candidate_id'),'items':items},indent=2)+'\n```\n'
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(rendered)
 print(json.dumps({'phase':phase,'template_ref':'audit/review-system-v2/prompts/REVIEW_TEMPLATE.md','template_sha256':sha_text(template),'rendered_ref':out.relative_to(ROOT).as_posix() if ROOT in out.resolve().parents else str(out),'rendered_sha256':sha_text(rendered),'contract_id':a.contract_id,'evidence_ids':[x['id'] for x in items]},indent=2))
if __name__=='__main__':main()
