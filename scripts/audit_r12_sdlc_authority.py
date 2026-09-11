#!/usr/bin/env python3
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1]; errs=[]
ci=(R/'.github/workflows/ci.yml').read_text(); pages=(R/'.github/workflows/pages.yml').read_text(); gl=(R/'.gitlab-ci.yml').read_text()
# GitHub PR CI may audit, but only Pages workflow may deploy or run on main push.
if re.search(r'(?m)^\s*push:\s*$',ci): errs.append('ci.yml must not trigger on push; pages.yml is the sole GitHub main-push release authority')
if 'actions/deploy-pages@' in ci or re.search(r'(?m)^\s+deploy:\s*$',ci): errs.append('ci.yml must not deploy Pages')
if ci.count('python3 scripts/run_all_checks.py')!=1: errs.append('ci.yml must run canonical suite exactly once')
if pages.count('python3 scripts/run_all_checks.py')!=1: errs.append('pages.yml must run canonical suite exactly once')
if pages.count('actions/deploy-pages@')!=1: errs.append('pages.yml must deploy exactly once')
if 'push:' not in pages or 'branches: ["main"]' not in pages: errs.append('pages.yml must remain the sole main-push GitHub release workflow')
if gl.count('python3 scripts/run_all_checks.py')!=1: errs.append('GitLab must run canonical suite exactly once before Pages deployment')
if errs:
 print('R12_SDLC_AUTHORITY_AUDIT_FAIL',file=sys.stderr)
 for e in errs: print(' - '+e,file=sys.stderr)
 raise SystemExit(1)
print('R12_SDLC_AUTHORITY_AUDIT_PASS github_main_full_suite=1 github_deploy=1 gitlab_full_suite=1')
