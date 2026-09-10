#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RELEASE_TIMEOUT=int(os.getenv('NSC_RELEASE_GATE_TIMEOUT_SECONDS','900'))
def run(cmd):
    print('+',' '.join(cmd),flush=True); subprocess.run(cmd,cwd=ROOT,check=True,timeout=RELEASE_TIMEOUT)
def tree_digest():
    h=hashlib.sha256(); n=0
    for p in sorted((ROOT/'public').rglob('*')):
        if p.is_file():
            n+=1; rel=p.relative_to(ROOT/'public').as_posix(); d=hashlib.sha256(p.read_bytes()).hexdigest(); h.update(rel.encode()+b'\0'+d.encode()+b'\n')
    return h.hexdigest(),n
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--class',dest='klass',choices=['open-beta','claim-elevation','institutional-1.0'],default='open-beta'); a=ap.parse_args()
    if a.klass!='open-beta':
        print(json.dumps({'release_class':a.klass,'status':'EXTERNAL_EVIDENCE_REQUIRED','reason':'This class depends on artifact-specific or independent human/external review and is not machine-certifiable by the repository alone.'},indent=2)); return 3
    run(['python3','scripts/run_all_checks.py']); run(['python3','scripts/audit_launch.py'])
    a1,n1=tree_digest(); run(['python3','scripts/build_site.py']); a2,n2=tree_digest()
    if a1!=a2 or n1!=n2: print('OPEN_BETA_RELEASE_GATE_FAILED nondeterministic public tree',file=sys.stderr); return 1
    out={'schema':'nsc-release-gate-v1','release_class':'open-beta','status':'PASS','public_tree_sha256':a2,'public_files':n2,'external_certification_claimed':False}
    (ROOT/'OPEN_BETA_RELEASE_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
    run(['python3','scripts/make_manifest.py']); run(['python3','scripts/audit_manifest.py'])
    print(json.dumps(out,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
