#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys,time,json,os
if not os.environ.get('GITHUB_REPOSITORY') and not os.environ.get('CI_PROJECT_URL') and not os.environ.get('COMMONS_FORGE_URL'):
    os.environ['GITHUB_REPOSITORY']='navier-stokes-commons/navier-stokes-commons.github.io'
from scratch import ScratchPolicyError,scratch_dir
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commands=[
 ['python3','scripts/reconcile.py','--check'],
 ['python3','scripts/audit_authority.py'],
 ['python3','scripts/audit_evidence.py'],
 ['python3','scripts/audit_schemas.py'],
 ['python3','scripts/catalog.py','validate'],
 ['python3','scripts/audit_sdlc_contract.py'],
 ['python3','scripts/audit_evaluation_protocol.py'],
 ['python3','scripts/audit_r11_schemas.py'],
 ['python3','scripts/audit_r11_status.py'],
 ['python3','scripts/audit_r11_frontier_graph.py'],
 ['python3','scripts/audit_r12_sdlc_authority.py'],
 ['python3','scripts/build_site.py'],
 ['python3','scripts/audit_r14_product_boundary.py'],
 ['python3','scripts/audit_r14_prove2me_bridge.py'],
 ['python3','scripts/audit_r14_experience_policy.py'],
 ['python3','scripts/audit_r16_fluid_hero.py'],
 ['python3','scripts/audit_r14_forge_topology.py'],
 ['python3','scripts/audit_github_identity.py'],
 ['python3','scripts/audit_r14_intake.py'],
 ['python3','scripts/audit_r14_source_watch.py'],
 ['python3','scripts/audit_r15_prove2me_reuse.py'],
 ['python3','scripts/audit_r11_agent_packets.py'],
 ['python3','scripts/audit_r13_math_view.py'],
 ['python3','scripts/audit_content.py'],
 ['python3','scripts/leak_scan.py'],
 ['python3','scripts/audit_fonts.py'],
 ['python3','scripts/audit_runtime_efficiency.py'],
 ['python3','scripts/audit_contrast.py'],
 ['python3','scripts/audit_css_syntax.py'],
 ['python3','scripts/audit_site.py'],
 ['python3','scripts/audit_i18n.py'],
 ['python3','scripts/audit_release_consistency.py'],
 ['python3','scripts/audit_community_trust.py'],
 ['python3','scripts/audit_onboarding.py'],
 ['python3','scripts/audit_lifecycle_copy.py'],
 ['python3','scripts/audit_capabilities.py'],
 ['python3','scripts/audit_progressive.py'],
 ['python3','scripts/audit_motion.py'],
 ['python3','scripts/audit_performance.py'],
 ['python3','scripts/audit_design_system.py'],
 ['python3','scripts/audit_agent_endpoints.py'],
 ['python3','scripts/audit_machine_legibility.py'],
 ['python3','scripts/audit_agent_cold_start.py'],
 ['python3','scripts/audit_task_paths.py'],
 ['python3','scripts/audit_r11_expert_surface.py'],
 ['python3','scripts/audit_host_configs.py'],
 ['python3','scripts/audit_visual_integrity.py'],
 ['python3','scripts/audit_scaling_model.py'],
 ['python3','scripts/audit_math_representation.py'],
 ['python3','scripts/audit_flow_chamber.py'],
 ['python3','scripts/audit_actions.py'],
 ['python3','scripts/audit_benchmarks.py'],
 ['python3','scripts/audit_no_em_dash.py'],
 ['python3','scripts/audit_forges.py'],
 ['python3','scripts/audit_forge_sync.py'],
 ['python3','scripts/audit_contributions.py'],
 ['python3','scripts/audit_launch.py'],
 ['python3','scripts/audit_fault_seeds.py'],
 ['python3','scripts/audit_packaging.py'],
 ['python3','scripts/audit_browser.py'],
 ['python3','scripts/audit_layout_integrity.py'],
 ['python3','scripts/audit_experience.py'],
 ['python3','scripts/audit_motion_experience.py'],
]
PER_CHECK_TIMEOUT_SECONDS=180
timings=[]; started=time.perf_counter()
try: timing_path=Path(os.getenv('NSC_CHECK_TIMINGS',str(scratch_dir('check-timings')/'timings.json')))
except ScratchPolicyError as e: print('CHECK_TIMINGS_UNAVAILABLE '+str(e),file=sys.stderr);raise SystemExit(2)
def persist(status):
    timing_path.parent.mkdir(parents=True,exist_ok=True)
    timing_path.write_text(json.dumps({'schema':'nsc-check-timings-v1','mode':'release','status':status,'checks':timings,'total_seconds':round(time.perf_counter()-started,4)},indent=2)+'\n')
for c in commands:
    print('+',' '.join(c),flush=True); t=time.perf_counter(); status='pass'
    try: subprocess.run(c,cwd=ROOT,check=True,timeout=PER_CHECK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        status='timeout'; timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':status});persist('timeout')
        print('PUBLIC_RELEASE_CHECK_TIMEOUT',' '.join(c),f'after={PER_CHECK_TIMEOUT_SECONDS}s',file=sys.stderr); raise SystemExit(124)
    except subprocess.CalledProcessError:
        status='fail'; timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':status});persist('fail');raise
    timings.append({'command':c,'seconds':round(time.perf_counter()-t,4),'status':status})
# Rebuild once after all mutation-capable audit receipts are written so public/ is the clean canonical projection.
t=time.perf_counter(); subprocess.run(['python3','scripts/build_site.py'],cwd=ROOT,check=True,timeout=PER_CHECK_TIMEOUT_SECONDS);timings.append({'command':['python3','scripts/build_site.py','<final-projection>'],'seconds':round(time.perf_counter()-t,4),'status':'pass'})
persist('pass')
slow=sorted(timings,key=lambda x:x['seconds'],reverse=True)[:5]
print('SLOWEST_PUBLIC_CHECKS '+json.dumps([{'command':' '.join(x['command']),'seconds':x['seconds']} for x in slow],separators=(',',':')))
print('ALL_PUBLIC_RELEASE_CHECKS_PASS experience_gate=realtime+direct-manipulation+large-text+rtl+motion+fonts meta_assurance=sdlc+runtime+machine+taskpaths timings='+str(timing_path))
