#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTROL_RE=re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
ID_RE=re.compile(r'NS-[QM]\d{2,3}',re.I)

def clean(v,maxlen=12000):
    if v is None:return ''
    s=CONTROL_RE.sub('',str(v)).replace('\r\n','\n').replace('\r','\n')
    return s[:maxlen]

def fetch_json(url, token=None, header='Authorization', prefix='Bearer '):
    headers={'Accept':'application/json','User-Agent':'nsc-unified-intake/1'}
    if token: headers[header]=prefix+token
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as r:return json.loads(r.read())

def kind(title,body,labels):
    text=(' '.join(labels)+' '+title+' '+body).lower()
    if 'review' in text:return 'review'
    if 'result' in text or 'artifact' in text:return 'result'
    if 'side quest' in text or 'problem proposal' in text:return 'problem-proposal'
    if 'attempt' in text or 'quest' in text:return 'attempt'
    return 'other'

def fingerprint(forge,repo,native,title,targets):
    payload='\0'.join([forge,repo,str(native),title.lower().strip(),','.join(sorted(targets))])
    return 'sha256:'+hashlib.sha256(payload.encode()).hexdigest()

def github_items(repo,token=None):
    url=f'https://api.github.com/repos/{repo}/issues?state=all&per_page=100&sort=updated&direction=desc'
    rows=fetch_json(url,token)
    out=[]
    for x in rows:
        if x.get('pull_request'): typ='code-change'
        else: typ=None
        title=clean(x.get('title'),500); body=clean(x.get('body'))
        labels=[clean(z.get('name'),100) for z in x.get('labels',[]) if isinstance(z,dict)]
        targets=sorted(set(z.upper() for z in ID_RE.findall(title+' '+body)))
        k=typ or kind(title,body,labels)
        out.append({'id':f'github:{repo}:issue:{x["number"]}','forge':'github','kind':k,'repository':repo,'native_id':x['number'],'url':x['html_url'],'author':clean((x.get('user')or{}).get('login'),200),'created_at':x.get('created_at'),'updated_at':x.get('updated_at'),'title':title,'target_ids':targets,'fingerprint':fingerprint('github',repo,x['number'],title,targets),'status':'closed' if x.get('state')=='closed' else 'open'})
    return out

def gitlab_items(project,token=None):
    encoded=urllib.parse.quote(project,safe='')
    base=f'https://gitlab.com/api/v4/projects/{encoded}'
    headers_token=token
    issues=fetch_json(base+'/issues?scope=all&state=all&per_page=100&order_by=updated_at&sort=desc',headers_token,'PRIVATE-TOKEN','')
    out=[]
    for x in issues:
        title=clean(x.get('title'),500); body=clean(x.get('description'))
        labels=[clean(z,100) for z in x.get('labels',[])]
        targets=sorted(set(z.upper() for z in ID_RE.findall(title+' '+body)))
        out.append({'id':f'gitlab:{project}:issue:{x["iid"]}','forge':'gitlab','kind':kind(title,body,labels),'repository':project,'native_id':x['iid'],'url':x['web_url'],'author':clean((x.get('author')or{}).get('username'),200),'created_at':x.get('created_at'),'updated_at':x.get('updated_at'),'title':title,'target_ids':targets,'fingerprint':fingerprint('gitlab',project,x['iid'],title,targets),'status':'closed' if x.get('state')=='closed' else 'open'})
    mrs=fetch_json(base+'/merge_requests?scope=all&state=all&per_page=100&order_by=updated_at&sort=desc',headers_token,'PRIVATE-TOKEN','')
    for x in mrs:
        title=clean(x.get('title'),500); body=clean(x.get('description')); targets=sorted(set(z.upper() for z in ID_RE.findall(title+' '+body)))
        out.append({'id':f'gitlab:{project}:mr:{x["iid"]}','forge':'gitlab','kind':'code-change','repository':project,'native_id':x['iid'],'url':x['web_url'],'author':clean((x.get('author')or{}).get('username'),200),'created_at':x.get('created_at'),'updated_at':x.get('updated_at'),'title':title,'target_ids':targets,'fingerprint':fingerprint('gitlab',project,'mr'+str(x['iid']),title,targets),'status':'closed' if x.get('state') in {'closed','merged'} else 'open'})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--github-repo',default=os.getenv('NSC_GITHUB_REPO','timperelman/navier-stokes-commons-public'));ap.add_argument('--gitlab-project',default=os.getenv('NSC_GITLAB_PROJECT','champia-labs-group/navier-stokes-commons-public'));ap.add_argument('--output',default=str(ROOT/'content/public/intake.json'));ap.add_argument('--github-only',action='store_true');ap.add_argument('--gitlab-only',action='store_true');a=ap.parse_args()
    items=[]; sources=[]
    try:
        if not a.gitlab_only:
            items+=github_items(a.github_repo,os.getenv('GITHUB_TOKEN'));sources.append({'forge':'github','repository':a.github_repo})
        if not a.github_only:
            items+=gitlab_items(a.gitlab_project,os.getenv('GITLAB_TOKEN'));sources.append({'forge':'gitlab','repository':a.gitlab_project})
    except Exception as e:
        print('UNIFIED_INTAKE_SYNC_FAIL '+repr(e),file=sys.stderr);return 2
    # Semantic duplicate candidates are flags, never merges.
    by_target={}
    for item in items:
        for t in item['target_ids']:by_target.setdefault(t,[]).append(item['id'])
    for item in items:
        peers=sorted(set(p for t in item['target_ids'] for p in by_target.get(t,[]) if p!=item['id']))
        if peers:item['possible_related_items']=peers[:30]
    # Registered-source deltas join the same operator queue but remain non-forge evidence events.
    sw=ROOT/'content/public/source_watch.json'
    if sw.exists():
        try:
            swd=json.loads(sw.read_text())
            for delta in swd.get('deltas',[]):
                sid=clean(delta.get('source_id'),200);ts=delta.get('detected_at');url=clean(delta.get('url'),2000)
                key='source-watch:'+sid+':'+str(ts)
                items.append({'id':key,'forge':'source-watch','kind':'source-delta','repository':'registered-sources','native_id':key,'url':url,'author':'automation','created_at':ts,'updated_at':ts,'title':'Source changed: '+sid,'target_ids':[],'fingerprint':'sha256:'+hashlib.sha256(key.encode()).hexdigest(),'status':'open','required_effect':'review-candidate-only'})
        except Exception as e:
            print('UNIFIED_INTAKE_SYNC_WARN source_watch='+repr(e),file=sys.stderr)
    items.sort(key=lambda x:(x.get('updated_at') or '',x['id']),reverse=True)
    p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True)
    old={}
    if p.exists():
        try:old=json.loads(p.read_text())
        except Exception:old={}
    stable={'schema':'nsc-unified-intake-v1','sources':sources,'items':items}
    old_stable={'schema':old.get('schema'),'sources':old.get('sources',[]),'items':old.get('items',[])}
    changed=stable!=old_stable
    if changed:
        doc={**stable,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')}
        p.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
    print(f'UNIFIED_INTAKE_SYNC_PASS items={len(items)} github={sum(i["forge"]=="github" for i in items)} gitlab={sum(i["forge"]=="gitlab" for i in items)} changed={str(changed).lower()}')
    return 0
if __name__=='__main__': raise SystemExit(main())
