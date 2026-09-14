#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'audit/review-system-v2'
HEX40=re.compile(r'^[0-9a-f]{40}$'); HEX64=re.compile(r'^[0-9a-f]{64}$'); CID=re.compile(r'^RC-\d{8}-\d{3}$')
SEVERITY={'P0':0,'P1':1,'P2':2,'P3':3,'INFO':4}

class AuditError(Exception): pass

def jload(p:Path):
    try:return json.loads(p.read_text())
    except Exception as e:raise AuditError(f'{p}: invalid JSON: {e}')

def sha256_file(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def safe_local(root:Path, ref:str):
    if not isinstance(ref,str) or not ref or ref.startswith('/') or '://' in ref:return None
    p=(root/ref).resolve()
    try:p.relative_to(root.resolve())
    except ValueError:return None
    return p

def product_digest(public:Path):
    if not public.is_dir():raise AuditError(f'public tree missing: {public}')
    h=hashlib.sha256();files=sorted(p for p in public.rglob('*') if p.is_file())
    if not files:raise AuditError('public tree has no files')
    for p in files:
        rel=p.relative_to(public).as_posix().encode();data=p.read_bytes()
        h.update(len(rel).to_bytes(4,'big'));h.update(rel);h.update(len(data).to_bytes(8,'big'));h.update(data)
    return h.hexdigest()

def load_contracts(cfg:Path):
    d=cfg/'contracts';cs={}
    for p in sorted(d.glob('*.json')):
        x=jload(p);cid=x.get('id')
        if not cid:raise AuditError(f'{p}: missing id')
        if cid in cs:raise AuditError(f'duplicate contract id {cid}')
        cs[cid]=x
    return cs

def static_validate(policy,contracts,cfg:Path):
    errs=[]
    for required in ['EVALUATOR_CONTRACT.schema.json','REVIEW_RUN.schema.json','RELEASE_CANDIDATE.schema.json','PANEL_POLICY.json','prompts/REVIEW_TEMPLATE.md']:
        if not (cfg/required).is_file():errs.append('missing review-system artifact '+required)
    if policy.get('schema')!='nsc-synthetic-review-policy-v2':errs.append('bad policy schema')
    gr=policy.get('global_rules',{})
    must_true=['no_composite_score_laundering','minority_veto_preserved','abstain_never_counts_as_pass','missing_required_evidence_blocks','unresolved_contradiction_blocks','direct_observation_beats_author_claim','blind_lanes_must_not_receive_prior_scores_or_release_claims','review_prompt_and_raw_output_must_be_hash_bound','reviewer_model_identity_must_be_recorded','synthetic_pass_does_not_certify_human_preference','synthetic_fail_can_block_release']
    for k in must_true:
        if gr.get(k) is not True:errs.append(f'global rule not enforced: {k}')
    minfamilies=int(policy.get('minimum_model_families_when_multi_reviewer',2))
    if minfamilies<2:errs.append('minimum_model_families_when_multi_reviewer must be >=2')
    if not contracts:errs.append('no evaluator contracts')
    for cid,c in contracts.items():
        if c.get('schema')!='nsc-evaluator-contract-v2':errs.append(f'{cid}: bad schema')
        for k in ['kind','role','mission','competence','epistemic_scope','blindness','observation_protocol','failure_sensitivities','evidence_requirements','adversarial_tasks','veto_conditions','output_contract','independence','calibration']:
            if k not in c:errs.append(f'{cid}: missing {k}')
        oc=c.get('output_contract',{})
        for k in ['must_separate_observation_inference','must_cite_evidence_ids','must_report_unknowns','must_preserve_vetoes','forbidden_global_score']:
            if oc.get(k) is not True:errs.append(f'{cid}: output contract weak on {k}')
        cal=c.get('calibration',{})
        if cal.get('required_before_pass_evidence') is not True:errs.append(f'{cid}: calibration not required before PASS evidence')
        if not isinstance(cal.get('seeded_cases'),int) or cal.get('seeded_cases',0)<4:errs.append(f'{cid}: seeded calibration suite too small/missing')
        if not 0.5<=float(cal.get('minimum_recall',0))<=1:errs.append(f'{cid}: invalid minimum recall')
        if not 0.5<=float(cal.get('minimum_precision',0))<=1:errs.append(f'{cid}: invalid minimum precision')
        if len(c.get('observation_protocol',[]))<3:errs.append(f'{cid}: observation protocol underspecified')
        if len(c.get('adversarial_tasks',[]))<2:errs.append(f'{cid}: adversarial tasks underspecified')
        if not c.get('independence',{}).get('group'):errs.append(f'{cid}: independence group missing')
    criteria=policy.get('critical_criteria',[]);ids=set()
    for q in criteria:
        qid=q.get('id')
        if not qid or qid in ids:errs.append(f'duplicate/missing criterion {qid}')
        ids.add(qid);owners=[]
        for cid,c in contracts.items():
            req={x.get('criterion_id'):set(x.get('modalities',[])) for x in c.get('evidence_requirements',[])}
            if qid in req:owners.append((cid,c,req[qid]))
        expert=sum(1 for _,c,_ in owners if c.get('kind')=='expert');users=sum(1 for _,c,_ in owners if c.get('kind')=='synthetic-user-stratum')
        if expert<q.get('min_expert_reviewers',0):errs.append(f'{qid}: expert coverage {expert} < {q.get("min_expert_reviewers",0)}')
        if users<q.get('min_blind_user_strata',0):errs.append(f'{qid}: user-stratum coverage {users} < {q.get("min_blind_user_strata",0)}')
        covered=set().union(*(mods for _,_,mods in owners)) if owners else set();missing=set(q.get('required_modalities',[]))-covered
        if missing:errs.append(f'{qid}: contract modality coverage missing {sorted(missing)}')
        for cid in q.get('required_contracts_any',[]):
            if cid not in contracts:errs.append(f'{qid}: required contract absent {cid}')
        if qid not in {'runtime-motion-authority','anti-goodhart-counterexample'} and not any(c.get('blindness',{}).get('blind_to_prior_verdicts') for _,c,_ in owners):errs.append(f'{qid}: no blind reviewer')
    if 'G01' not in contracts or contracts['G01'].get('kind')!='hostile-red-team':errs.append('hostile Goodhart red-team contract G01 missing')
    if 'ARB01' not in contracts or contracts['ARB01'].get('kind')!='arbiter':errs.append('contradiction arbiter ARB01 missing')
    return errs

def check_bound_file(artifact_root:Path,ref,expected_hash,label,errs):
    p=safe_local(artifact_root,ref)
    if not p:errs.append(f'{label}: ref must be safe repo-relative path, got {ref!r}');return
    if not p.is_file():errs.append(f'{label}: bound artifact missing {ref}');return
    if not HEX64.fullmatch(str(expected_hash or '')):errs.append(f'{label}: invalid sha256');return
    got=sha256_file(p)
    if got!=expected_hash:errs.append(f'{label}: sha256 mismatch {got} != {expected_hash}')

def validate_calibration_report(contract:dict, cal:dict, artifact_root:Path, label:str, errs:list[str]):
    ref=cal.get('evidence_ref'); p=safe_local(artifact_root,ref) if ref else None
    if not p or not p.is_file(): return
    try: report=json.loads(p.read_text())
    except Exception as e: errs.append(f'{label}: calibration report invalid JSON: {e}'); return
    if report.get('schema')!='nsc-reviewer-calibration-v2':errs.append(f'{label}: bad calibration report schema')
    if report.get('contract_id')!=contract.get('id'):errs.append(f'{label}: calibration contract mismatch')
    suitep=CFG/'calibration/SEED_SUITE.json'
    if not suitep.is_file():errs.append(f'{label}: calibration seed suite missing');return
    suite=jload(suitep); suite_hash=sha256_file(suitep)
    if report.get('suite_sha256')!=suite_hash:errs.append(f'{label}: calibration suite hash mismatch')
    details={x.get('case_id'):x for x in report.get('details',[]) if isinstance(x,dict)}
    owners={x.get('criterion_id') for x in contract.get('evidence_requirements',[])}
    tp=fp=fn=scope_ok=scope_n=correct=0
    for case in suite.get('cases',[]):
        cid=case.get('id'); d=details.get(cid)
        if not d:errs.append(f'{label}: calibration missing seed {cid}');continue
        expected=case['oracle']['expected_owner_response'] if case.get('criterion_id') in owners else case['oracle']['expected_nonowner_response']
        got=d.get('got');correct+=int(got==expected)
        if expected=='ALARM':tp+=int(got=='ALARM');fn+=int(got!='ALARM')
        elif got=='ALARM':fp+=1
        if expected=='ABSTAIN':scope_n+=1;scope_ok+=int(got=='ABSTAIN')
    n=len(suite.get('cases',[])); recall=tp/(tp+fn) if tp+fn else 1.0; precision=tp/(tp+fp) if tp+fp else 1.0; scope=scope_ok/scope_n if scope_n else 1.0
    vals={'seeded_cases':n,'recall':recall,'precision':precision,'passed': recall>=float(contract['calibration']['minimum_recall']) and precision>=float(contract['calibration']['minimum_precision']) and scope>=0.9 and n>=int(contract['calibration']['seeded_cases'])}
    for k,v in vals.items():
        cv=cal.get(k);rv=report.get(k)
        if isinstance(v,float):
            try:
                if abs(float(cv)-v)>1e-5 or abs(float(rv)-v)>1e-5:errs.append(f'{label}: calibration {k} not reproducible')
            except Exception:errs.append(f'{label}: calibration {k} malformed')
        elif cv!=v or rv!=v:errs.append(f'{label}: calibration {k} not reproducible')

def validate_run_shape(r,contracts,path,artifact_root:Path,criterion_ids:set[str]):
    errs=[];req=['schema','run_id','candidate','evaluator','prompt','evidence','observations','verdict','vetoes','contradictions','unknowns','raw_output']
    for k in req:
        if k not in r:errs.append(f'{path.name}: missing {k}')
    if r.get('schema')!='nsc-review-run-v2':errs.append(f'{path.name}: bad run schema')
    cand=r.get('candidate',{})
    if not CID.fullmatch(str(cand.get('candidate_id',''))):errs.append(f'{path.name}: candidate_id missing/invalid')
    if not HEX40.fullmatch(str(cand.get('source_sha',''))):errs.append(f'{path.name}: source_sha must be 40 hex chars')
    if not cand.get('version'):errs.append(f'{path.name}: candidate version missing')
    if not HEX64.fullmatch(str(cand.get('product_digest_sha256',''))):errs.append(f'{path.name}: product digest missing/invalid')
    ev=r.get('evaluator',{});cid=ev.get('contract_id');contract=contracts.get(cid,{})
    if cid not in contracts:errs.append(f'{path.name}: unknown contract {cid}')
    for k in ['model_provider','model_family','model_version','independence_group','split','blindness_attestation','calibration']:
        if k not in ev or ev.get(k) in [None,'']:errs.append(f'{path.name}: missing evaluator {k}')
    if ev.get('split') not in {'development','holdout','incident'}:errs.append(f'{path.name}: invalid evaluator split')
    expected_group=contract.get('independence',{}).get('group')
    if expected_group and ev.get('independence_group')!=expected_group:errs.append(f'{path.name}: independence group {ev.get("independence_group")} != contract {expected_group}')
    ba=ev.get('blindness_attestation',{})
    if not isinstance(ba,dict):errs.append(f'{path.name}: blindness_attestation must be object');ba={}
    blind=contract.get('blindness',{})
    checks=[('blind_to_prior_verdicts','prior_verdicts_exposed'),('blind_to_candidate_age','candidate_age_exposed'),('blind_to_author_rationale','author_rationale_exposed')]
    for requirement,exposed in checks:
        if blind.get(requirement) is True and ba.get(exposed) is not False:errs.append(f'{path.name}: blind lane violated: {exposed} must be false')
    cal=ev.get('calibration',{})
    if not isinstance(cal,dict):errs.append(f'{path.name}: calibration must be object');cal={}
    for k in ['suite_id','seeded_cases','recall','precision','passed','evidence_ref','evidence_sha256']:
        if k not in cal:errs.append(f'{path.name}: calibration missing {k}')
    if contract:
        floor=contract.get('calibration',{})
        try:
            if int(cal.get('seeded_cases',-1))<int(floor.get('seeded_cases',0)):errs.append(f'{path.name}: calibration seeded_cases below contract floor')
            if float(cal.get('recall',-1))<float(floor.get('minimum_recall',1)):errs.append(f'{path.name}: calibration recall below contract floor')
            if float(cal.get('precision',-1))<float(floor.get('minimum_precision',1)):errs.append(f'{path.name}: calibration precision below contract floor')
        except Exception:errs.append(f'{path.name}: malformed calibration metrics')
    if cal.get('passed') is not True:errs.append(f'{path.name}: evaluator calibration did not pass')
    if cal.get('evidence_ref'):check_bound_file(artifact_root,cal.get('evidence_ref'),cal.get('evidence_sha256'),f'{path.name} calibration',errs)
    if contract and cal.get('evidence_ref'):validate_calibration_report(contract,cal,artifact_root,f'{path.name} calibration',errs)
    pr=r.get('prompt',{})
    for k in ['template_ref','template_sha256','rendered_ref','rendered_sha256']:
        if not pr.get(k):errs.append(f'{path.name}: missing prompt {k}')
    if pr.get('template_ref'):check_bound_file(artifact_root,pr.get('template_ref'),pr.get('template_sha256'),f'{path.name} prompt template',errs)
    if pr.get('rendered_ref'):check_bound_file(artifact_root,pr.get('rendered_ref'),pr.get('rendered_sha256'),f'{path.name} rendered prompt',errs)
    evid=r.get('evidence',[]);evid_ids=set();evid_by_id={}
    if not isinstance(evid,list) or not evid:errs.append(f'{path.name}: no evidence')
    for e in evid if isinstance(evid,list) else []:
        eid=e.get('id')
        if not eid or eid in evid_ids:errs.append(f'{path.name}: duplicate/missing evidence id {eid}')
        evid_ids.add(eid);evid_by_id[eid]=e
        for k in ['modality','sha256','uri','release_equivalent']:
            if k not in e:errs.append(f'{path.name}: evidence {eid} missing {k}')
        if not HEX64.fullmatch(str(e.get('sha256',''))):errs.append(f'{path.name}: evidence {eid} bad sha256')
        if e.get('release_equivalent') is True:
            if not e.get('local_ref'):errs.append(f'{path.name}: release-equivalent evidence {eid} missing local_ref')
            else:check_bound_file(artifact_root,e.get('local_ref'),e.get('sha256'),f'{path.name} evidence {eid}',errs)
    obs=r.get('observations',[])
    if not isinstance(obs,list) or not obs:errs.append(f'{path.name}: no observations')
    for o in obs if isinstance(obs,list) else []:
        for k in ['id','criterion_id','epistemic_type','severity','claim','evidence_refs','confidence']:
            if k not in o:errs.append(f'{path.name}: observation missing {k}')
        if o.get('criterion_id') not in criterion_ids:errs.append(f'{path.name}: unknown criterion {o.get("criterion_id")}')
        if o.get('epistemic_type') not in {'direct-observation','derived-inference','hypothesis'}:errs.append(f'{path.name}: bad epistemic_type')
        if o.get('severity') not in SEVERITY:errs.append(f'{path.name}: bad severity')
        try:
            conf=float(o.get('confidence'))
            if not 0<=conf<=1:errs.append(f'{path.name}: confidence outside [0,1]')
        except Exception:errs.append(f'{path.name}: malformed confidence')
        refs=set(o.get('evidence_refs',[]) if isinstance(o.get('evidence_refs'),list) else [])
        if o.get('epistemic_type')=='direct-observation' and not refs:errs.append(f'{path.name}: direct observation {o.get("id")} lacks evidence refs')
        missing=refs-evid_ids
        if missing:errs.append(f'{path.name}: observation {o.get("id")} cites missing evidence {sorted(missing)}')
    if r.get('verdict') not in {'PASS','FAIL','ABSTAIN','CONTRADICTION'}:errs.append(f'{path.name}: invalid verdict')
    if not isinstance(r.get('vetoes'),list):errs.append(f'{path.name}: vetoes must be list')
    if not isinstance(r.get('contradictions'),list):errs.append(f'{path.name}: contradictions must be list')
    if not isinstance(r.get('unknowns'),list):errs.append(f'{path.name}: unknowns must be list')
    ro=r.get('raw_output',{})
    if not ro.get('ref') or not HEX64.fullmatch(str(ro.get('sha256',''))):errs.append(f'{path.name}: raw output provenance missing')
    elif ro.get('ref'):check_bound_file(artifact_root,ro.get('ref'),ro.get('sha256'),f'{path.name} raw output',errs)
    return errs

def active_candidate(cfg:Path):
    p=cfg/'ACTIVE_CANDIDATE.json'
    if not p.is_file():return None
    x=jload(p);return x

def release_validate(policy,contracts,runs_dir,artifact_root:Path,expected_product_digest=None,expected_candidate_id=None):
    errs=[];runs=[];criterion_ids={q['id'] for q in policy.get('critical_criteria',[])}
    for p in sorted(runs_dir.glob('*.json')):
        r=jload(p);errs.extend(validate_run_shape(r,contracts,p,artifact_root,criterion_ids));runs.append((p,r))
    if not runs:errs.append(f'no review runs in {runs_dir}')
    if expected_product_digest or expected_candidate_id:
        for p,r in runs:
            cand=r.get('candidate',{});got=cand.get('product_digest_sha256');cid=cand.get('candidate_id')
            if expected_product_digest and got!=expected_product_digest:errs.append(f'{p.name}: stale product digest {got} != {expected_product_digest}')
            if expected_candidate_id and cid!=expected_candidate_id:errs.append(f'{p.name}: candidate_id {cid} != active {expected_candidate_id}')
    # A critical FAIL is an alarm/veto, not a vote to average away. Same-candidate contradictions also block.
    for p,r in runs:
        if r.get('verdict')=='FAIL':errs.append(f'{p.name}: critical reviewer FAIL is release-blocking for this candidate')
        if r.get('contradictions'):errs.append(f'{p.name}: unresolved contradictions {r.get("contradictions")}')
        if r.get('verdict')=='CONTRADICTION':errs.append(f'{p.name}: contradiction verdict')
        if r.get('vetoes'):errs.append(f'{p.name}: active vetoes {r.get("vetoes")}')
    by_criterion={q['id']:[] for q in policy.get('critical_criteria',[])}
    for p,r in runs:
        criteria={o.get('criterion_id') for o in r.get('observations',[]) if isinstance(o,dict)}
        for qid in criteria:
            if qid in by_criterion:by_criterion[qid].append((p,r))
    minfamilies=int(policy.get('minimum_model_families_when_multi_reviewer',2))
    for q in policy.get('critical_criteria',[]):
        qid=q['id'];rs=by_criterion.get(qid,[]);mods=set()
        for _,r in rs:
            mods|={e.get('modality') for e in r.get('evidence',[]) if e.get('release_equivalent') is True}
        missing=set(q.get('required_modalities',[]))-mods
        if missing:errs.append(f'{qid}: missing release-equivalent evidence modalities {sorted(missing)}')
        passing=[]
        for p,r in rs:
            if r.get('verdict')!='PASS':continue
            if not any(o.get('criterion_id')==qid and o.get('epistemic_type')=='direct-observation' for o in r.get('observations',[]) if isinstance(o,dict)):continue
            passing.append((p,r))
        expert_ids=set();user_ids=set();groups=set();families=set()
        for _,r in passing:
            cid=r.get('evaluator',{}).get('contract_id');c=contracts.get(cid,{})
            groups.add(r.get('evaluator',{}).get('independence_group'));families.add(r.get('evaluator',{}).get('model_family'))
            if c.get('kind')=='expert':expert_ids.add(cid)
            if c.get('kind')=='synthetic-user-stratum':user_ids.add(cid)
        if len(expert_ids)<q.get('min_expert_reviewers',0):errs.append(f'{qid}: passing expert reviews {sorted(expert_ids)} < {q.get("min_expert_reviewers",0)}')
        if len(user_ids)<q.get('min_blind_user_strata',0):errs.append(f'{qid}: passing user strata {sorted(user_ids)} < {q.get("min_blind_user_strata",0)}')
        needed=q.get('min_expert_reviewers',0)+q.get('min_blind_user_strata',0)
        if needed>1 and len({x for x in groups if x})<2:errs.append(f'{qid}: insufficient reviewer independence groups {sorted(x for x in groups if x)}')
        if needed>1 and len({x for x in families if x})<minfamilies:errs.append(f'{qid}: model-family diversity {sorted(x for x in families if x)} < {minfamilies}')
    return errs,runs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--static',action='store_true');ap.add_argument('--release',action='store_true');ap.add_argument('--runs-dir',default=str(CFG/'runs'));ap.add_argument('--public-dir',default=str(ROOT/'public'));ap.add_argument('--product-digest');ap.add_argument('--candidate-id');ap.add_argument('--artifact-root',default=str(ROOT));ap.add_argument('--config-dir',default=str(CFG));args=ap.parse_args()
    try:
        cfg=Path(args.config_dir);policy=jload(cfg/'PANEL_POLICY.json');contracts=load_contracts(cfg);errs=static_validate(policy,contracts,cfg)
        if errs:
            print('SYNTHETIC_REVIEW_V2_STATIC_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];return 1
        if args.static and not args.release:
            print(f'SYNTHETIC_REVIEW_V2_STATIC_PASS contracts={len(contracts)} criteria={len(policy.get("critical_criteria",[]))} hostile=G01 arbiter=ARB01');return 0
        if args.release:
            actual_digest=product_digest(Path(args.public_dir));ac=active_candidate(cfg);cid=args.candidate_id;digest=args.product_digest or actual_digest
            if ac and not cid:cid=ac.get('candidate_id')
            if ac and not args.product_digest:
                claimed=ac.get('product_digest_sha256')
                if claimed!=actual_digest:
                    print(f'SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED\n - active candidate product digest stale {claimed} != {actual_digest}',file=sys.stderr);return 2
                digest=claimed
            if not cid:
                print('SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED\n - no active candidate id; create candidate before release review',file=sys.stderr);return 2
            if ac:
                cp=cfg/'candidates'/f'{cid}.json'
                if not cp.is_file():
                    print('SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED\n - active candidate record missing '+str(cp),file=sys.stderr);return 2
                cr=jload(cp); unresolved=cr.get('known_unresolved',[])
                if unresolved:
                    print('SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED\n - active candidate has known unresolved defects: '+json.dumps(unresolved),file=sys.stderr);return 2
            rerrs,runs=release_validate(policy,contracts,Path(args.runs_dir),Path(args.artifact_root),digest,cid)
            if rerrs:
                print('SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in rerrs];print(' product_digest='+digest,file=sys.stderr);return 2
            print(f'SYNTHETIC_REVIEW_V2_RELEASE_PASS runs={len(runs)} candidate={cid} product_digest={digest} synthetic_pass_scope=defect-discovery-not-human-preference');return 0
        print('SYNTHETIC_REVIEW_V2_STATIC_PASS');return 0
    except AuditError as e:
        print('SYNTHETIC_REVIEW_V2_AUDIT_ERROR '+str(e),file=sys.stderr);return 3
if __name__=='__main__':raise SystemExit(main())
