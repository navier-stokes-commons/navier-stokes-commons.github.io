#!/usr/bin/env python3
from __future__ import annotations
import json,shutil,subprocess,sys
from pathlib import Path
from scratch import scratch_dir, ScratchPolicyError
ROOT=Path(__file__).resolve().parents[1]
try:
    SCRATCH=scratch_dir('fault-seeds')
except ScratchPolicyError as e:
    print('FAULT_SEED_AUDIT_FAILED scratch policy: '+str(e),file=sys.stderr); raise SystemExit(2)
def clone(name):
    d=SCRATCH/name
    if d.exists(): shutil.rmtree(d)
    shutil.copytree(ROOT,d,ignore=shutil.ignore_patterns('.git','__pycache__'))
    return d
def run(d,script,*args):
    p=subprocess.run(['python3',script,*args],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
    return p.returncode,p.stdout
def load(p): return json.loads(p.read_text())
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows=[]
def expect_detect(name,auditor,mutate,pre=None):
    d=clone(name)
    if pre: pre(d)
    mutate(d)
    rc,out=run(d,auditor)
    rows.append({'case':name,'auditor':auditor,'detected':rc!=0,'returncode':rc,'excerpt':'\n'.join(out.splitlines()[:8])})
    shutil.rmtree(d)

def projection(d):
    n=len(load(d/'content/public/quests.json')['quests'])
    p=d/'README.md'; text=p.read_text(); needle=f'**Bounded work units:** {n} quests'
    if needle not in text: raise RuntimeError('projection seed could not locate current derived quest count')
    p.write_text(text.replace(needle,'**Bounded work units:** 999 quests',1))
expect_detect('projection-drift','scripts/reconcile.py',projection)
# reconcile needs --check, special case patch result because default would fix it.
rows.pop(); d=clone('projection-drift'); projection(d); rc,out=run(d,'scripts/reconcile.py','--check'); rows.append({'case':'projection-drift','auditor':'scripts/reconcile.py --check','detected':rc!=0,'returncode':rc,'excerpt':'\n'.join(out.splitlines()[:8])}); shutil.rmtree(d)

def reverse(d):
    p=d/'content/public/quests.json'; x=load(p); x['quests'][0]['founding_sprint']=True; dump(p,x)
expect_detect('writable-reverse-relation','scripts/audit_authority.py',reverse)
def lic(d):
    p=d/'content/public/locales/en.json'; x=load(p); x.setdefault('footer',{})['license']='MIT'; dump(p,x)
expect_detect('duplicated-license-state','scripts/audit_authority.py',lic)
def claim(d):
    p=d/'content/public/claims.json'; x=load(p); x['claims'][0]['status']='independently-reviewed'; dump(p,x)
expect_detect('manual-claim-elevation','scripts/audit_authority.py',claim)
def schema(d):
    p=d/'content/public/quests.json'; x=load(p); x['quests'][0]['unexpected_contract_field']=True; dump(p,x)
expect_detect('schema-contract-drift','scripts/audit_schemas.py',schema)
def route(d):
    p=d/'content/public/public_registry.json'; x=load(p); old=x['machine_endpoints']['actions']; stem,dot,ext=old.rpartition('.'); x['machine_endpoints']['actions']=(stem+'-v2'+dot+ext) if dot else old+'-v2'; dump(p,x)
expect_detect('route-projection-drift','scripts/audit_agent_endpoints.py',route)
def sim(d):
    p=d/'content/public/simulations.json'; x=load(p)
    # Corrupt the first numeric 2 in u_x while preserving schema shape.
    def mutate(n):
        if isinstance(n,dict):
            if n.get('type')=='number' and n.get('value')==2: n['value']=3; return True
            return any(mutate(v) for v in n.values())
        if isinstance(n,list): return any(mutate(v) for v in n)
        return False
    assert mutate(x['simulations'][0]['fields']['u_x']); dump(p,x)
    subprocess.run(['python3','scripts/build_site.py'],cwd=d,check=True,stdout=subprocess.DEVNULL,timeout=30)
expect_detect('simulation-semantic-drift','scripts/audit_flow_chamber.py',sim)
def benchmark(d):
    p=d/'content/public/quests.json'; x=load(p); q=next(q for q in x['quests'] if q['id']=='NS-Q036'); q.pop('benchmark_set_id',None); dump(p,x)
expect_detect('benchmark-unbound','scripts/audit_benchmarks.py',benchmark)
failed=[r for r in rows if not r['detected']]
out={'schema':'nsc-fault-seed-audit-v1','scratch_policy':'ephemeral-approved','cases':rows,'detected':len(rows)-len(failed),'total':len(rows),'pass':not failed}
res=ROOT/'audit/open-beta/fault_seed_results.json'; res.parent.mkdir(parents=True,exist_ok=True); res.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
shutil.rmtree(SCRATCH,ignore_errors=True)
if failed:
    print('FAULT_SEED_AUDIT_FAILED',file=sys.stderr)
    for r in failed: print(' - undetected '+r['case'],file=sys.stderr)
    raise SystemExit(1)
print(f'FAULT_SEED_AUDIT_PASS detected={len(rows)}/{len(rows)} scratch_policy=ephemeral-approved')
