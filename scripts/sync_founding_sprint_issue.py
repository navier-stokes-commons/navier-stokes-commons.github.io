#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SENTINEL='<!-- NSC-GENERATED:FOUNDING-SPRINT-INDEX -->'

def load():
    sprint=json.loads((ROOT/'content/public/founding_sprint.json').read_text())
    quests_doc=json.loads((ROOT/'content/public/quests.json').read_text())
    project=json.loads((ROOT/'content/public/project.json').read_text())
    quests={q['id']:q for q in quests_doc['quests']}
    return sprint,quests,project

def render(repository: str | None=None) -> tuple[str,str]:
    sprint,quests,project=load()
    missing=[qid for qid in sprint['quest_ids'] if qid not in quests]
    if missing:
        raise SystemExit('FOUNDING_SPRINT_SYNC_FAILED missing quest ids: '+', '.join(missing))
    repo=repository or project['repository_url'].removeprefix('https://github.com/').rstrip('/')
    title=f"{sprint['title']}: start here - {len(sprint['quest_ids'])} launch quests, parallel attempts welcome"
    lines=[
        SENTINEL,
        f"# {project['name']} {sprint['title']}",
        '',
        sprint['purpose'],
        '',
        'Attempts are non-exclusive. Opening an attempt never reserves a problem, and independent reproductions are useful evidence.',
        '',
        '## Launch quests',
        '',
    ]
    for qid in sprint['quest_ids']:
        q=quests[qid]
        lines.append(f"- `{qid}` {q['rung']}: {q['title']}")
    lines += [
        '',
        '## Canonical contracts',
        '',
        '- Quest specifications: `content/public/quests.json`',
        '- Task ladder: `content/public/task_ladder.json`',
        '- Review semantics: `REVIEW_POLICY.md`',
        '- Governance: `GOVERNANCE.md`',
        '- Human start: `start.md`',
        '- Agent start: `SKILL.md` and `AGENTS.md`',
        '- Machine actions: `content/public/actions.json`',
        '',
        '## How to join',
        '',
        'Pick any quest that matches your current capability and open an attempt through the repository contribution protocol. You do not need permission to start. Humans, autonomous agents, and human-agent teams are all welcome. Evidence requirements are the same regardless of contributor type.',
        '',
        'Negative results, falsifications, exact gap statements, source corrections, reproductions, formal audits, numerical work, visualization, accessibility work, agent benchmarks, localization review, and governance analysis can all be legitimate contributions when they satisfy the quest acceptance criteria.',
        '',
        f"Repository: https://github.com/{repo}",
        '',
        '_This issue is a generated projection of the canonical Initial Independent Review Portfolio and quest catalog. Edit the canonical JSON, not this issue body._',
        '',
    ]
    return title,'\n'.join(lines)

def api(method:str,url:str,token:str,payload:dict|None=None):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url,data=data,method=method,headers={
        'Accept':'application/vnd.github+json',
        'Authorization':f'Bearer {token}',
        'X-GitHub-Api-Version':'2022-11-28',
        'User-Agent':'navier-stokes-commons-forge-sync/1',
        'Content-Type':'application/json',
    })
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors='replace')
        raise SystemExit(f'FOUNDING_SPRINT_SYNC_FAILED HTTP {e.code}: {body[:1000]}')

def apply(repository:str, token:str):
    title,body=render(repository)
    base=f'https://api.github.com/repos/{repository}'
    issues=api('GET',base+'/issues?state=all&per_page=100',token)
    matches=[i for i in issues if not i.get('pull_request') and SENTINEL in (i.get('body') or '')]
    if len(matches)>1:
        raise SystemExit(f'FOUNDING_SPRINT_SYNC_FAILED duplicate generated index issues: {[i["number"] for i in matches]}')
    payload={'title':title,'body':body,'state':'open'}
    if not matches:
        out=api('POST',base+'/issues',token,payload)
        action='created'
    else:
        issue=matches[0]
        if issue.get('title')==title and issue.get('body')==body and issue.get('state')=='open':
            print(f'FOUNDING_SPRINT_SYNC_PASS action=unchanged issue={issue["number"]}')
            return 0
        out=api('PATCH',base+f'/issues/{issue["number"]}',token,payload)
        action='updated'
    print(f'FOUNDING_SPRINT_SYNC_PASS action={action} issue={out["number"]}')
    return 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--render',action='store_true')
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--repository')
    a=ap.parse_args()
    if a.render == a.apply:
        ap.error('choose exactly one of --render or --apply')
    if a.render:
        title,body=render(a.repository)
        print(title); print(); print(body); return 0
    repository=a.repository or os.getenv('GITHUB_REPOSITORY','').strip()
    token=os.getenv('GITHUB_TOKEN','').strip()
    if not repository or not token:
        print('FOUNDING_SPRINT_SYNC_FAILED --apply requires repository plus GITHUB_TOKEN',file=sys.stderr); return 2
    return apply(repository,token)
if __name__=='__main__': raise SystemExit(main())
