#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys

def run(*args,check=True):
    p=subprocess.run(args,text=True,capture_output=True)
    if check and p.returncode: raise RuntimeError(' '.join(args)+': '+(p.stderr or p.stdout))
    return p.stdout.strip()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--remote',default='gitlab');ap.add_argument('--branch',default='main');ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    try:
        head=run('git','rev-parse',a.branch)
        status=run('git','status','--porcelain')
        if status: raise RuntimeError('working tree is not clean')
        remote_line=run('git','ls-remote',a.remote,f'refs/heads/{a.branch}',check=False)
        remote_sha=remote_line.split()[0] if remote_line else None
        if remote_sha:
            # Fetch explicitly so ancestry test is local and race-aware.
            run('git','fetch','--quiet',a.remote,f'{a.branch}:refs/remotes/{a.remote}/{a.branch}')
            ff=subprocess.run(['git','merge-base','--is-ancestor',f'{a.remote}/{a.branch}',a.branch]).returncode==0
            if not ff: raise RuntimeError(f'FORGE_DIVERGENCE GitLab {remote_sha} is not an ancestor of canonical {head}; explicit reconciliation required')
        if not a.apply:
            print(f'GITLAB_MIRROR_CHECK_PASS canonical={head} remote={remote_sha or "absent"} fast_forward_safe=true');return 0
        # --force is intentionally forbidden.
        run('git','push',a.remote,f'{head}:refs/heads/{a.branch}')
        after=run('git','ls-remote',a.remote,f'refs/heads/{a.branch}').split()[0]
        if after!=head: raise RuntimeError(f'post-push mirror mismatch {after} != {head}')
        print(f'GITLAB_MIRROR_APPLY_PASS sha={head}');return 0
    except Exception as e:
        print('GITLAB_MIRROR_FAIL '+str(e),file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
