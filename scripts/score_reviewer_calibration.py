#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CFG=ROOT/'audit/review-system-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract-id',required=True);ap.add_argument('--predictions',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 contract=json.loads((CFG/'contracts'/f'{a.contract_id}.json').read_text());suitep=CFG/'calibration/SEED_SUITE.json';suite=json.loads(suitep.read_text());pred=json.loads(Path(a.predictions).read_text())
 answers=pred.get('answers',{});owners={x['criterion_id'] for x in contract.get('evidence_requirements',[])};tp=fp=fn=scope_ok=scope_n=correct=0
 details=[]
 for c in suite['cases']:
  expected=c['oracle']['expected_owner_response'] if c['criterion_id'] in owners else c['oracle']['expected_nonowner_response'];got=answers.get(c['id'],'MISSING');ok=got==expected;correct+=int(ok)
  if expected=='ALARM':tp+=int(got=='ALARM');fn+=int(got!='ALARM')
  elif got=='ALARM':fp+=1
  if expected=='ABSTAIN':scope_n+=1;scope_ok+=int(got=='ABSTAIN')
  details.append({'case_id':c['id'],'expected':expected,'got':got,'correct':ok})
 recall=tp/(tp+fn) if tp+fn else 1.0;precision=tp/(tp+fp) if tp+fp else 1.0;scope=scope_ok/scope_n if scope_n else 1.0;accuracy=correct/len(suite['cases']);floor=contract['calibration'];passed=recall>=floor['minimum_recall'] and precision>=floor['minimum_precision'] and scope>=0.9 and len(answers)>=floor['seeded_cases']
 out={'schema':'nsc-reviewer-calibration-v2','contract_id':a.contract_id,'suite_id':'SEED_SUITE_V2','suite_sha256':sha(suitep),'seeded_cases':len(suite['cases']),'recall':round(recall,6),'precision':round(precision,6),'scope_accuracy':round(scope,6),'overall_accuracy':round(accuracy,6),'passed':passed,'predictions_sha256':sha(Path(a.predictions)),'details':details}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(('REVIEWER_CALIBRATION_PASS' if passed else 'REVIEWER_CALIBRATION_FAIL')+f' contract={a.contract_id} recall={recall:.4f} precision={precision:.4f} scope={scope:.4f} cases={len(suite["cases"])}')
 raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
