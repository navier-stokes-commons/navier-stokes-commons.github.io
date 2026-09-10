#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]; errs=[]
for req in ['.github/workflows/ci.yml','.github/workflows/pages.yml','.github/ISSUE_TEMPLATE/open_attempt.yml','.github/ISSUE_TEMPLATE/side_quest.yml','.github/ISSUE_TEMPLATE/submit_result.yml','.github/ISSUE_TEMPLATE/review.yml','.gitlab-ci.yml']:
    if not (ROOT/req).exists(): errs.append(f'missing host configuration {req}')
for wf in [ROOT/'.github/workflows/ci.yml',ROOT/'.github/workflows/pages.yml']:
    if not wf.exists(): continue
    txt=wf.read_text()
    for line in txt.splitlines():
        m=re.search(r'uses:\s*([^\s#]+)',line)
        if m:
            ref=m.group(1)
            if '@' not in ref or not re.search(r'@[0-9a-f]{40}$',ref): errs.append(f'{wf.name}: action not pinned to full commit SHA: {ref}')
    if 'permissions:' not in txt: errs.append(f'{wf.name}: missing explicit permissions')
ci=(ROOT/'.github/workflows/ci.yml').read_text() if (ROOT/'.github/workflows/ci.yml').exists() else ''
if 'contents: read' not in ci: errs.append('CI must default to contents: read')
pages=(ROOT/'.github/workflows/pages.yml').read_text() if (ROOT/'.github/workflows/pages.yml').exists() else ''
for x in ['contents: read','pages: write','id-token: write']:
    if x not in pages: errs.append(f'Pages workflow missing permission {x}')
# All deployment/test paths must invoke the same canonical release gate; partial duplicated lists drift.
for label,txt in [('GitHub CI',ci),('GitHub Pages',pages)]:
    if 'python3 scripts/run_all_checks.py' not in txt:
        errs.append(f'{label}: must invoke canonical scripts/run_all_checks.py')
    if 'python3 scripts/bootstrap_audit_env.py' not in txt:
        errs.append(f'{label}: must invoke shared audit-environment bootstrap')
if 'steps.pages.outputs.base_url' not in pages or 'SITE_URL:' not in pages:
    errs.append('GitHub Pages: canonical SITE_URL must derive from configure-pages base_url')
if "github.event.repository.private == false" not in pages:
    errs.append('GitHub Pages: push deployment must be suppressed while repository is private')
if not re.search(r'(?ms)^  deploy:\n.*?^    needs: build\s*$', pages):
    errs.append('GitHub Pages: deploy job must depend on the build/upload job')
if not re.search(r'(?ms)^  deploy:\n.*?^    environment:\n      name: github-pages\s*$', pages):
    errs.append('GitHub Pages: deploy job must target the github-pages environment')
gitlab=(ROOT/'.gitlab-ci.yml').read_text() if (ROOT/'.gitlab-ci.yml').exists() else ''
if gitlab.count('python3 scripts/run_all_checks.py') < 2:
    errs.append('GitLab CI: test and deploy jobs must both invoke canonical scripts/run_all_checks.py')
if 'python3 scripts/bootstrap_audit_env.py' not in gitlab:
    errs.append('GitLab CI: shared audit-environment bootstrap missing')
if not (ROOT/'scripts/bootstrap_audit_env.py').exists():
    errs.append('shared audit-environment bootstrap missing')
pol=json.loads((ROOT/'content/public/release_policy.json').read_text())
if pol.get('turnkey_static_deployment_adapters'):
    errs.append('turnkey deployment adapters may not be claimed before live provider evidence is recorded')
configured={x.get('id'):x for x in pol.get('configured_static_deployment_adapters',[]) if isinstance(x,dict)}
for aid,cfg in [('github-pages','.github/workflows/pages.yml'),('gitlab-pages','.gitlab-ci.yml')]:
    if aid not in configured or configured[aid].get('config')!=cfg:
        errs.append(f'configured deployment adapter registry missing/mismatched: {aid}')
# Contribution templates may not solicit secrets or private system state.
for p in list((ROOT/'.github/ISSUE_TEMPLATE').glob('*.yml'))+list((ROOT/'.gitlab/issue_templates').glob('*.md')):
    txt=p.read_text().lower()
    for bad in ['password','api key','secret key','access token','private prompt','chain of thought','local path']:
        if bad in txt: errs.append(f'{p.relative_to(ROOT)} solicits prohibited information: {bad}')
if errs:
    print('HOST_CONFIG_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print('HOST_CONFIG_AUDIT_PASS github_actions_pinned=true contribution_templates_present=true')
