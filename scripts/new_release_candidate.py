#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CFG=ROOT/'audit/review-system-v2'; CDIR=CFG/'candidates'
def product_digest(public:Path):
    h=hashlib.sha256();files=sorted(p for p in public.rglob('*') if p.is_file())
    if not files:raise SystemExit('public tree empty; build first')
    for p in files:
      rel=p.relative_to(public).as_posix().encode();data=p.read_bytes();h.update(len(rel).to_bytes(4,'big'));h.update(rel);h.update(len(data).to_bytes(8,'big'));h.update(data)
    return h.hexdigest()
def git_head():
    try:s=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except Exception:raise SystemExit('cannot resolve git HEAD; pass --base-source-sha')
    return s
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--objective',required=True);ap.add_argument('--change',action='append',default=[]);ap.add_argument('--known-unresolved',action='append',default=[]);ap.add_argument('--carry-evidence',action='append',default=[]);ap.add_argument('--invalidate-evidence',action='append',default=[]);ap.add_argument('--supersede-reason');ap.add_argument('--trigger-evidence',action='append',default=[]);ap.add_argument('--base-source-sha');ap.add_argument('--public-dir',default=str(ROOT/'public'));a=ap.parse_args()
    if len(a.objective)<20:raise SystemExit('--objective must describe the user-facing objective, >=20 chars')
    CDIR.mkdir(parents=True,exist_ok=True); ptr=CFG/'ACTIVE_CANDIDATE.json'; parent=None
    if ptr.exists():
      oldptr=json.loads(ptr.read_text());parent=oldptr.get('candidate_id')
      if not a.supersede_reason or not a.trigger_evidence:raise SystemExit('active candidate exists: --supersede-reason and --trigger-evidence are required')
      op=CDIR/f'{parent}.json'
      if not op.exists():raise SystemExit(f'active parent record missing: {op}')
      old=json.loads(op.read_text());old['status']='superseded';old['supersession']={'reason':a.supersede_reason,'trigger_evidence':a.trigger_evidence};op.write_text(json.dumps(old,indent=2)+'\n')
    day=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d');existing=[]
    for p in CDIR.glob(f'RC-{day}-*.json'):
      try:existing.append(int(p.stem.rsplit('-',1)[1]))
      except:pass
    cid=f'RC-{day}-{(max(existing,default=0)+1):03d}';dig=product_digest(Path(a.public_dir));sha=a.base_source_sha or git_head()
    if not re.fullmatch(r'[0-9a-f]{40}',sha):raise SystemExit('base source SHA must be 40 lowercase hex chars')
    rec={'schema':'nsc-release-candidate-v2','candidate_id':cid,'parent_candidate_id':parent,'status':'active','created_at_utc':datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'base_source_sha':sha,'product_digest_sha256':dig,'objective':a.objective,'material_changes':a.change,'known_unresolved':a.known_unresolved,'evidence_carried_forward':a.carry_evidence,'evidence_invalidated':a.invalidate_evidence,'supersession':{'reason':None,'trigger_evidence':[]}}
    (CDIR/f'{cid}.json').write_text(json.dumps(rec,indent=2)+'\n');ptr.write_text(json.dumps({'schema':'nsc-active-candidate-v2','candidate_id':cid,'product_digest_sha256':dig},indent=2)+'\n')
    print(f'NEW_RELEASE_CANDIDATE_PASS candidate={cid} product_digest={dig} parent={parent or "none"}')
if __name__=='__main__':main()
