#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'

def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':'nsc-source-watch/1','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=35) as r:
        data=r.read(8_000_000)
        return {'final_url':r.geturl(),'status':getattr(r,'status',200),'etag':r.headers.get('ETag'),'last_modified':r.headers.get('Last-Modified'),'content_type':r.headers.get('Content-Type'),'sha256':hashlib.sha256(data).hexdigest(),'bytes_observed':len(data)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sources',default=str(C/'sources.json'));ap.add_argument('--state',default=str(C/'source_watch.json'));ap.add_argument('--limit',type=int,default=0);a=ap.parse_args()
    sources=json.loads(Path(a.sources).read_text()); state_path=Path(a.state)
    old=json.loads(state_path.read_text()) if state_path.exists() else {'observations':{},'deltas':[]}
    observations=dict(old.get('observations',{})); deltas=[]; now=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
    rows=sources[:a.limit] if a.limit else sources
    failures=[]
    for s in rows:
        sid=s.get('id');url=s.get('url')
        if not sid or not url: continue
        try:new=request(url);new['observed_at']=now
        except Exception as e: failures.append({'source_id':sid,'url':url,'error':repr(e)});continue
        prev=observations.get(sid)
        # Mutable HTML often contains irrelevant build noise. Prefer validators when a source supplies them;
        # use the observed payload hash only when validators are unavailable.
        keys=['final_url']
        if new.get('etag') or new.get('last_modified'): keys += ['etag','last_modified']
        else: keys += ['sha256']
        new['comparison_keys']=keys
        changed=(not prev) or any(prev.get(k)!=new.get(k) for k in keys)
        if prev and changed:
            allkeys=['final_url','etag','last_modified','sha256']
            deltas.append({'source_id':sid,'url':url,'detected_at':now,'comparison_keys':keys,'previous':{k:prev.get(k) for k in allkeys},'current':{k:new.get(k) for k in allkeys},'required_effect':'review-candidate-only'})
        if changed: observations[sid]=new
    doc={'schema':'nsc-source-watch-v1','policy':'detect-only-never-auto-elevate','observations':observations,'deltas':deltas,'failures':failures}
    old_doc=json.loads(state_path.read_text()) if state_path.exists() else {}
    stable=lambda d:{'schema':d.get('schema'),'policy':d.get('policy'),'observations':d.get('observations',{}),'deltas':d.get('deltas',[])}
    changed_file=stable(doc)!=stable(old_doc)
    if changed_file: state_path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
    print(f'SOURCE_WATCH_PASS observed={len(rows)-len(failures)} deltas={len(deltas)} failures={len(failures)} changed={str(changed_file).lower()} automatic_claim_changes=0')
    return 0 if not failures else 3
if __name__=='__main__': raise SystemExit(main())
