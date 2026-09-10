#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
from nsc_model import public_registry
R=Path(__file__).resolve().parents[1]; p=R/'content/public/contributions.json'; orig=p.read_text(); missions=json.loads((R/'content/public/missions.json').read_text()); m=missions[0]
probe={'id':'AUDIT-PROBE-001','status':'accepted','mission_id':m['id'],'title':'Audit propagation probe','summary':'Disposable release-gate probe.','contribution_type':'replication','contributor':{'display_name':'Audit harness'},'artifact_url':'https://example.invalid/artifact','review_url':'https://example.invalid/review'}
try:
 p.write_text(json.dumps([probe],indent=2)+'\n'); subprocess.run(['python3','scripts/build_site.py'],cwd=R,check=True,stdout=subprocess.DEVNULL)
 contrib_endpoint=public_registry()['machine_endpoints']['contributions']
 checks=[R/f'public/en/missions/{m["slug"]}/index.html',R/'public/en/activity/index.html',R/'public'/contrib_endpoint.lstrip('/')]
 if not all('AUDIT' in x.read_text().upper() or 'Audit propagation probe' in x.read_text() for x in checks): raise SystemExit('accepted contribution did not propagate')
finally:
 p.write_text(orig); subprocess.run(['python3','scripts/build_site.py'],cwd=R,check=True,stdout=subprocess.DEVNULL)
print('CONTRIBUTION_PROPAGATION_PASS')
