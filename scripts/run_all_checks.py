#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commands=[
 ['python3','scripts/reconcile.py','--check'],
 ['python3','scripts/audit_authority.py'],
 ['python3','scripts/audit_evidence.py'],
 ['python3','scripts/audit_schemas.py'],
 ['python3','scripts/catalog.py','validate'],
 ['python3','scripts/build_site.py'],
 ['python3','scripts/audit_content.py'],
 ['python3','scripts/leak_scan.py'],
 ['python3','scripts/audit_contrast.py'],
 ['python3','scripts/audit_css_syntax.py'],
 ['python3','scripts/audit_site.py'],
 ['python3','scripts/audit_i18n.py'],
 ['python3','scripts/audit_release_consistency.py'],
 ['python3','scripts/audit_capabilities.py'],
 ['python3','scripts/audit_progressive.py'],
 ['python3','scripts/audit_motion.py'],
 ['python3','scripts/audit_performance.py'],
 ['python3','scripts/audit_design_system.py'],
 ['python3','scripts/audit_agent_endpoints.py'],
 ['python3','scripts/audit_agent_cold_start.py'],
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
]
PER_CHECK_TIMEOUT_SECONDS=180
for c in commands:
    print('+',' '.join(c),flush=True)
    try: subprocess.run(c,cwd=ROOT,check=True,timeout=PER_CHECK_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print('PUBLIC_RELEASE_CHECK_TIMEOUT',' '.join(c),f'after={PER_CHECK_TIMEOUT_SECONDS}s',file=sys.stderr); raise SystemExit(124)
subprocess.run(['python3','scripts/build_site.py'],cwd=ROOT,check=True,timeout=PER_CHECK_TIMEOUT_SECONDS)
print('ALL_PUBLIC_RELEASE_CHECKS_PASS')
