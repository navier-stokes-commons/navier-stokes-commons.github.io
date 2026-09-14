#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CFG=ROOT/'audit/review-system-v2'; HEX40=re.compile(r'^[0-9a-f]{40}$'); HEX64=re.compile(r'^[0-9a-f]{64}$'); CID=re.compile(r'^RC-\d{8}-\d{3}$')
def product_digest(public:Path):
    h=hashlib.sha256(); files=sorted(p for p in public.rglob('*') if p.is_file())
    if not files: raise ValueError('public tree has no files')
    for p in files:
        rel=p.relative_to(public).as_posix().encode(); data=p.read_bytes()
        h.update(len(rel).to_bytes(4,'big'));h.update(rel);h.update(len(data).to_bytes(8,'big'));h.update(data)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--public-dir',default=str(ROOT/'public'));ap.add_argument('--skip-product-digest',action='store_true');a=ap.parse_args();errs=[]
    cdir=CFG/'candidates'; ptr=CFG/'ACTIVE_CANDIDATE.json'
    if not ptr.is_file():errs.append('ACTIVE_CANDIDATE.json missing')
    recs={}
    if cdir.is_dir():
      for p in sorted(cdir.glob('RC-*.json')):
        try:r=json.loads(p.read_text())
        except Exception as e:errs.append(f'{p.name}: invalid JSON {e}');continue
        cid=r.get('candidate_id');
        if not cid or not CID.fullmatch(str(cid)):errs.append(f'{p.name}: invalid candidate_id {cid}');continue
        if cid in recs:errs.append(f'duplicate candidate id {cid}')
        recs[cid]=(p,r)
        if r.get('schema')!='nsc-release-candidate-v2':errs.append(f'{cid}: bad schema')
        if r.get('status') not in {'active','superseded','rejected','released'}:errs.append(f'{cid}: bad status')
        if not HEX40.fullmatch(str(r.get('base_source_sha',''))):errs.append(f'{cid}: invalid base_source_sha')
        if not HEX64.fullmatch(str(r.get('product_digest_sha256',''))):errs.append(f'{cid}: invalid product digest')
        if len(str(r.get('objective','')))<20:errs.append(f'{cid}: objective underspecified')
        for k in ['material_changes','known_unresolved','evidence_carried_forward','evidence_invalidated']:
            if not isinstance(r.get(k),list):errs.append(f'{cid}: {k} must be list')
        sup=r.get('supersession')
        if not isinstance(sup,dict) or 'reason' not in sup or not isinstance(sup.get('trigger_evidence'),list):errs.append(f'{cid}: malformed supersession')
        if r.get('status')=='superseded' and (not sup or not sup.get('reason') or not sup.get('trigger_evidence')):errs.append(f'{cid}: superseded without reason + trigger evidence')
    active=[cid for cid,(_,r) in recs.items() if r.get('status')=='active']
    if len(active)!=1:errs.append(f'exactly one active candidate required, found {active}')
    pdoc=None
    if ptr.is_file():
      try:pdoc=json.loads(ptr.read_text())
      except Exception as e:errs.append(f'ACTIVE_CANDIDATE.json invalid: {e}')
    if pdoc:
      cid=pdoc.get('candidate_id');dig=pdoc.get('product_digest_sha256')
      if cid not in recs:errs.append(f'active pointer references missing candidate {cid}')
      else:
        r=recs[cid][1]
        if r.get('status')!='active':errs.append(f'pointer candidate {cid} not active')
        if dig!=r.get('product_digest_sha256'):errs.append('active pointer digest differs from candidate record')
        if active and cid!=active[0]:errs.append(f'active pointer {cid} != unique active {active[0]}')
        if not a.skip_product_digest:
          try:actual=product_digest(Path(a.public_dir))
          except Exception as e:errs.append(f'cannot compute public product digest: {e}')
          else:
            if actual!=dig:errs.append(f'active candidate stale: {dig} != current public digest {actual}')
      # Parent lineage must be acyclic and refer to existing preserved records.
      seen=set();cur=cid
      while cur:
        if cur in seen:errs.append(f'candidate lineage cycle at {cur}');break
        seen.add(cur); rr=recs.get(cur,(None,{}))[1]; par=rr.get('parent_candidate_id')
        if par and par not in recs:errs.append(f'{cur}: parent candidate missing {par}');break
        cur=par
    if errs:
      print('CANDIDATE_LINEAGE_V2_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];return 1
    print(f'CANDIDATE_LINEAGE_V2_PASS active={active[0]} product_digest={recs[active[0]][1]["product_digest_sha256"]} preserved={len(recs)}')
    return 0
if __name__=='__main__':raise SystemExit(main())
