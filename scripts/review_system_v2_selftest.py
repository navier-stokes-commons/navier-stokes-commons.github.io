#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AUD=ROOT/'scripts/audit_review_system_v2.py';CFG=ROOT/'audit/review-system-v2'
def hbytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def h(s:str)->str:return hbytes(s.encode())
def run(*args):return subprocess.run([sys.executable,str(AUD),*args],cwd=ROOT,text=True,capture_output=True)
def tree_digest(public:Path)->str:
    hh=hashlib.sha256()
    for p in sorted(x for x in public.rglob('*') if x.is_file()):
        rel=p.relative_to(public).as_posix().encode();data=p.read_bytes();hh.update(len(rel).to_bytes(4,'big'));hh.update(rel);hh.update(len(data).to_bytes(8,'big'));hh.update(data)
    return hh.hexdigest()
def write_art(root:Path,rel:str,text:str):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return hbytes(p.read_bytes())
def make_run(contract:dict,digest:str,artifact_root:Path,*,verdict='PASS',vetoes=None,contradictions=None,only_screenshot_motion=False):
    cid=contract['id'];reqs=contract.get('evidence_requirements',[])
    if only_screenshot_motion:reqs=[{'criterion_id':'motion-autonomous-salience','modalities':['screenshot']}]
    modalities=sorted({m for x in reqs for m in x.get('modalities',[])})
    template_ref='prompts/template.md';rendered_ref=f'prompts/rendered-{cid}.txt';cal_ref=f'calibration/{cid}.json';raw_ref=f'raw/{cid}.txt'
    tsha=write_art(artifact_root,template_ref,'fixture template');rsha=write_art(artifact_root,rendered_ref,'fixture rendered '+cid);rawsha=write_art(artifact_root,raw_ref,'fixture raw '+cid)
    suitep=CFG/'calibration/SEED_SUITE.json';suite=json.loads(suitep.read_text());owners={x['criterion_id'] for x in contract.get('evidence_requirements',[])};details=[];tp=fp=fn=scope_ok=scope_n=0
    for case in suite['cases']:
        expected=case['oracle']['expected_owner_response'] if case['criterion_id'] in owners else case['oracle']['expected_nonowner_response'];got=expected;details.append({'case_id':case['id'],'got':got})
        if expected=='ALARM':tp+=1
        if expected=='ABSTAIN':scope_n+=1;scope_ok+=1
    recall=1.0;precision=1.0;scope=1.0
    cal_report={'schema':'nsc-reviewer-calibration-v2','contract_id':cid,'suite_id':'SEED_SUITE_V2','suite_sha256':hbytes(suitep.read_bytes()),'seeded_cases':len(suite['cases']),'recall':recall,'precision':precision,'scope_accuracy':scope,'overall_accuracy':1.0,'passed':True,'predictions_sha256':h('fixture predictions '+cid),'details':details}
    csha=write_art(artifact_root,cal_ref,json.dumps(cal_report))
    evidence=[]
    for i,m in enumerate(modalities):
        rel=f'evidence/{cid}-{m}.txt';sha=write_art(artifact_root,rel,f'{cid}:{m}')
        evidence.append({'id':f'E{i+1}','modality':m,'sha256':sha,'uri':'repo://'+rel,'local_ref':rel,'release_equivalent':True})
    bymod={e['modality']:e['id'] for e in evidence};obs=[]
    for i,req in enumerate(reqs):
        refs=[bymod[m] for m in req.get('modalities',[]) if m in bymod]
        obs.append({'id':f'O{i+1}','criterion_id':req['criterion_id'],'epistemic_type':'direct-observation','severity':'INFO','claim':'fixture direct observation','evidence_refs':refs,'confidence':0.99})
    floor=contract['calibration'];blind=contract['blindness']
    return {'schema':'nsc-review-run-v2','run_id':f'fixture-{cid}','candidate':{'candidate_id':'RC-20990101-001','source_sha':'0'*40,'version':'fixture','product_digest_sha256':digest},'evaluator':{'contract_id':cid,'model_provider':'fixture-provider','model_family':f'fixture-family-{cid[-1]}','model_version':'1','independence_group':contract['independence']['group'],'split':'development','blindness_attestation':{'prior_verdicts_exposed':False,'candidate_age_exposed':False,'author_rationale_exposed':False},'calibration':{'suite_id':'fixture-seeds','seeded_cases':len(suite['cases']),'recall':1.0,'precision':1.0,'passed':True,'evidence_ref':cal_ref,'evidence_sha256':csha}},'prompt':{'template_ref':template_ref,'template_sha256':tsha,'rendered_ref':rendered_ref,'rendered_sha256':rsha},'evidence':evidence,'observations':obs,'verdict':verdict,'vetoes':vetoes or [],'contradictions':contradictions or [],'unknowns':[],'raw_output':{'ref':raw_ref,'sha256':rawsha}}
def setup(td:Path):
    pub=td/'public';pub.mkdir();(pub/'index.html').write_text('<p>fixture</p>');runs=td/'runs';runs.mkdir();arts=td/'artifacts';arts.mkdir();return pub,runs,arts,tree_digest(pub)
def release(runs,pub,arts):return run('--release','--runs-dir',str(runs),'--public-dir',str(pub),'--artifact-root',str(arts),'--candidate-id','RC-20990101-001')
# Static architecture must pass.
r=run('--static')
if r.returncode!=0:print(r.stdout);print(r.stderr,file=sys.stderr);raise SystemExit('STATIC_CONTROL_FAILED')
contracts={p.stem:json.loads(p.read_text()) for p in (CFG/'contracts').glob('*.json')}
# Full structural positive control.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td))
    for cid,c in sorted(contracts.items()):
        if c.get('kind')=='arbiter':continue
        (runs/f'{cid}.json').write_text(json.dumps(make_run(c,digest,arts)))
    rp=release(runs,pub,arts)
    if rp.returncode!=0 or 'SYNTHETIC_REVIEW_V2_RELEASE_PASS' not in rp.stdout:print(rp.stdout);print(rp.stderr,file=sys.stderr);raise SystemExit('RELEASE_STRUCTURE_POSITIVE_CONTROL_FAILED')
# Empty runs block.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td));r2=release(runs,pub,arts)
    if r2.returncode==0 or 'SYNTHETIC_REVIEW_V2_RELEASE_BLOCKED' not in r2.stderr:raise SystemExit('EMPTY_RUN_NEGATIVE_CONTROL_FAILED')
# Legacy summary blocks.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td));legacy={'auditor_id':'A22','role':'Motion design / creative-technology auditor','synthetic_only':True,'verdict':'machine_no_blocker_external_required','adversarial_finding':'Motion is coherent in screenshots.'};(runs/'legacy.json').write_text(json.dumps(legacy));r3=release(runs,pub,arts)
    if r3.returncode==0 or 'missing prompt' not in r3.stderr or 'no evidence' not in r3.stderr or 'raw output provenance missing' not in r3.stderr:print(r3.stderr);raise SystemExit('LEGACY_NEGATIVE_CONTROL_FAILED')
# Screenshot alone cannot certify motion.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td));(runs/'A22.json').write_text(json.dumps(make_run(contracts['A22'],digest,arts,only_screenshot_motion=True)));r4=release(runs,pub,arts)
    if r4.returncode==0 or "motion-autonomous-salience: missing release-equivalent evidence modalities ['live-interaction', 'timed-frames']" not in r4.stderr:print(r4.stderr);raise SystemExit('SCREENSHOT_MOTION_NEGATIVE_CONTROL_FAILED')
# One minority veto blocks an otherwise passing panel.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td))
    for cid,c in sorted(contracts.items()):
        if c.get('kind')=='arbiter':continue
        veto=[{'severity':'P1','criterion_id':'motion-autonomous-salience','statement':'seeded minority veto'}] if cid=='A22' else []
        (runs/f'{cid}.json').write_text(json.dumps(make_run(c,digest,arts,vetoes=veto)))
    r5=release(runs,pub,arts)
    if r5.returncode==0 or 'active vetoes' not in r5.stderr:print(r5.stderr);raise SystemExit('MINORITY_VETO_NEGATIVE_CONTROL_FAILED')
# A plain FAIL also blocks; it is not averaged away.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td))
    for cid,c in sorted(contracts.items()):
        if c.get('kind')=='arbiter':continue
        (runs/f'{cid}.json').write_text(json.dumps(make_run(c,digest,arts,verdict='FAIL' if cid=='U01' else 'PASS')))
    r6=release(runs,pub,arts)
    if r6.returncode==0 or 'critical reviewer FAIL is release-blocking' not in r6.stderr:print(r6.stderr);raise SystemExit('MINORITY_FAIL_NEGATIVE_CONTROL_FAILED')
# Contradiction blocks.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td))
    for cid,c in sorted(contracts.items()):
        if c.get('kind')=='arbiter':continue
        contradiction=[{'criterion_id':'motion-autonomous-salience','statement':'machine PASS but direct perception FAIL'}] if cid=='G01' else []
        (runs/f'{cid}.json').write_text(json.dumps(make_run(c,digest,arts,contradictions=contradiction)))
    r7=release(runs,pub,arts)
    if r7.returncode==0 or 'unresolved contradictions' not in r7.stderr:print(r7.stderr);raise SystemExit('CONTRADICTION_NEGATIVE_CONTROL_FAILED')
# Fabricated hash/reference blocks.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td));rr=make_run(contracts['A22'],digest,arts);rr['raw_output']['sha256']='f'*64;(runs/'A22.json').write_text(json.dumps(rr));r8=release(runs,pub,arts)
    if r8.returncode==0 or 'raw output: sha256 mismatch' not in r8.stderr:print(r8.stderr);raise SystemExit('HASH_BINDING_NEGATIVE_CONTROL_FAILED')
# Calibration below the evaluator contract floor blocks.
with tempfile.TemporaryDirectory() as td:
    pub,runs,arts,digest=setup(Path(td));rr=make_run(contracts['A22'],digest,arts);rr['evaluator']['calibration']['recall']=0.1;(runs/'A22.json').write_text(json.dumps(rr));r9=release(runs,pub,arts)
    if r9.returncode==0 or 'calibration recall below contract floor' not in r9.stderr:print(r9.stderr);raise SystemExit('CALIBRATION_NEGATIVE_CONTROL_FAILED')
print('SYNTHETIC_REVIEW_V2_SELFTEST_PASS static=true release-structure=true empty-runs-blocked=true legacy-summary-blocked=true screenshot-motion-blocked=true minority-veto-blocked=true minority-fail-blocked=true contradiction-blocked=true hash-binding-blocked=true calibration-blocked=true')
