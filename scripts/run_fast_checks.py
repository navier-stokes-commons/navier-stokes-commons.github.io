#!/usr/bin/env python3
"""Fast local preflight. Strict subset of run_all_checks.py; never release authority."""
from __future__ import annotations
import subprocess,sys,time,json,os
from scratch import ScratchPolicyError,scratch_dir
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commands=[
 ['python3','scripts/reconcile.py','--check'],
 ['python3','scripts/audit_authority.py'],
 ['python3','scripts/audit_schemas.py'],
 ['python3','scripts/catalog.py','validate'],
 ['python3','scripts/audit_sdlc_contract.py'],
 ['python3','scripts/audit_evaluation_protocol.py'],
 ['python3','scripts/audit_r11_schemas.py'],
 ['python3','scripts/audit_r11_status.py'],
 ['python3','scripts/audit_r11_frontier_graph.py'],
 ['python3','scripts/audit_r11_agent_packets.py'],
 ['python3','scripts/audit_r12_sdlc_authority.py'],
 ['python3','scripts/build_site.py'],
 ['python3','scripts/audit_r17_fluid_system.py'],
 ['python3','scripts/audit_deployment_ssot.py'],
 ['python3','scripts/audit_no_play_sweep.py'],
 ['python3','scripts/audit_content.py'],
 ['python3','scripts/leak_scan.py'],
 ['python3','scripts/audit_fonts.py'],
 ['python3','scripts/audit_runtime_efficiency.py'],
 ['python3','scripts/audit_css_syntax.py'],
 ['python3','scripts/audit_site.py'],
 ['python3','scripts/audit_i18n.py'],
 ['python3','scripts/audit_release_consistency.py'],
 ['python3','scripts/audit_community_trust.py'],
 ['python3','scripts/audit_onboarding.py'],
 ['python3','scripts/audit_lifecycle_copy.py'],
 ['python3','scripts/audit_capabilities.py'],
 ['python3','scripts/audit_progressive.py'],
 ['python3','scripts/audit_agent_endpoints.py'],
 ['python3','scripts/audit_machine_legibility.py'],
 ['python3','scripts/audit_actions.py'],
 ['python3','scripts/audit_launch.py'],
]
PER_CHECK_TIMEOUT_SECONDS=120
timings=[];started=time.perf_counter();
try: out=Path(os.getenv('NSC_FAST_CHECK_TIMINGS',str(scratch_dir('fast-check-timings')/'timings.json')))
except ScratchPolicyError as e: print('FAST_CHECK_TIMINGS_UNAVAILABLE '+str(e),file=sys.stderr);raise SystemExit(2)
def persist(status):
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'schema':'nsc-check-timings-v1','mode':'fast','status':status,'checks':timings,'total_seconds':round(time.perf_counter()-started,4)},indent=2)+'\n')
for c in commands:
    print('+',' '.join(c),flush=True);t=time.perf_counter()
    try:subprocess.run(c,cwd=ROOT,check=True,timeout=PER_CHECK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':'timeout'});persist('timeout');print('FAST_CHECK_TIMEOUT',' '.join(c),file=sys.stderr);raise SystemExit(124)
    except subprocess.CalledProcessError:
        timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':'fail'});persist('fail');raise
    timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':'pass'})
persist('pass')
slow=sorted(timings,key=lambda x:x['seconds'],reverse=True)[:5]
print('SLOWEST_FAST_CHECKS '+json.dumps([{'command':' '.join(x['command']),'seconds':x['seconds']} for x in slow],separators=(',',':')))
print('FAST_PUBLIC_CHECKS_PASS checks='+str(len(commands))+' timings='+str(out))
