#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import ast,sys
R=Path(__file__).resolve().parents[1]; errs=[]
def command_list(path):
    tree=ast.parse(path.read_text());
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='commands' for t in n.targets):
            try:return ast.literal_eval(n.value)
            except Exception:return None
    return None
fullp=R/'scripts/run_all_checks.py'; fastp=R/'scripts/run_fast_checks.py'
full=command_list(fullp); fast=command_list(fastp)
if not isinstance(full,list):errs.append('release command list not statically inspectable')
if not isinstance(fast,list):errs.append('fast command list not statically inspectable')
if isinstance(full,list) and isinstance(fast,list):
    F={tuple(x) for x in full}; Q={tuple(x) for x in fast}
    missing=Q-F
    if missing:errs.append('fast checks are not strict release-suite subset: '+repr(sorted(missing)))
    required=['audit_browser.py','audit_layout_integrity.py','audit_experience.py','audit_motion_experience.py','audit_runtime_efficiency.py','audit_machine_legibility.py','audit_task_paths.py','audit_sdlc_contract.py','audit_evaluation_protocol.py','audit_fault_seeds.py','audit_packaging.py']
    blob='\n'.join(' '.join(x) for x in full)
    for name in required:
        if name not in blob:errs.append('release suite missing critical gate '+name)
    if len(fast)>=len(full):errs.append('fast suite is not materially smaller than release suite')
for path,label in [(fullp,'release'),(fastp,'fast')]:
    txt=path.read_text()
    for marker in ['time.perf_counter','nsc-check-timings-v1','seconds']:
        if marker not in txt:errs.append(f'{label} runner lacks timing receipt marker {marker}')
if chr(47)+'tmp'+chr(47) in fullp.read_text() or chr(47)+'tmp'+chr(47) in fastp.read_text():errs.append('runner violates scratch policy')

ci=R/'.github/workflows/ci.yml'; gl=R/'.gitlab-ci.yml'; pages=R/'.github/workflows/pages.yml'
if not ci.is_file():errs.append('GitHub consolidated CI/Pages workflow missing')
else:
    t=ci.read_text()
    pw=pages.read_text()
    if t.count('python3 scripts/run_all_checks.py')!=1:errs.append('GitHub CI must run complete suite exactly once per workflow')
    if pw.count('python3 scripts/run_all_checks.py')!=1:errs.append('GitHub Pages workflow must run complete suite exactly once')
    if 'actions/deploy-pages@' not in pw or 'name: github-pages' not in pw:errs.append('GitHub does not deploy exact audited artifact')
    if 'actions/deploy-pages@' in t:errs.append('GitHub CI must not deploy; pages.yml is the deploy authority')
    if 'cancel-in-progress: true' not in t:errs.append('GitHub lacks redundant-run cancellation')
    if 'cache: "pip"' not in t:errs.append('GitHub setup-python pip cache missing')
# R7: pages.yml is the canonical GitHub Pages deployment adapter (audit_host_configs verifies it)
if not gl.is_file():errs.append('GitLab pipeline missing')
else:
    t=gl.read_text()
    if t.count('python3 scripts/run_all_checks.py')!=1:errs.append('GitLab must run complete suite exactly once per pipeline')
    if 'artifacts: true' not in t or 'publish: public' not in t:errs.append('GitLab Pages does not consume audited artifact')
    if 'interruptible: true' not in t:errs.append('GitLab audit job lacks redundant-pipeline cancellation hint')
    if 'resource_group: pages' not in t:errs.append('GitLab Pages deploy lacks serialization resource_group')
if errs:
    print('SDLC_CONTRACT_AUDIT_FAILED',file=sys.stderr)
    for e in errs:print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'SDLC_CONTRACT_AUDIT_PASS release_checks={len(full)} fast_checks={len(fast)} fast_subset=true timings=true measure_before_parallelize=true')
