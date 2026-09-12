#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];errs=[]
t=json.loads((R/'content/public/forge_topology.json').read_text())
if t.get('canonical_source',{}).get('forge')!='github':errs.append('GitHub must be canonical source authority')
if t.get('mirror',{}).get('forge')!='gitlab':errs.append('GitLab mirror missing')
if t.get('mirror',{}).get('policy')!='fast-forward-only' or t.get('mirror',{}).get('force_push_forbidden') is not True:errs.append('mirror must be fast-forward-only and force forbidden')
for p in ['scripts/mirror_gitlab.py','scripts/sync_forge_intake.py','.github/workflows/mirror-gitlab.yml','.github/workflows/sync-intake.yml']:
 if not (R/p).exists():errs.append('missing '+p)
import re
if re.search(r'git[\'\"]?,?\s*[\'\"]push[\'\"]?.*--force', (R/'scripts/mirror_gitlab.py').read_text()):errs.append('mirror script contains forbidden force push')
if errs:
 print('R14_FORGE_TOPOLOGY_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print('R14_FORGE_TOPOLOGY_PASS canonical=github mirror=gitlab fast_forward_only=true dual_intake=true')
