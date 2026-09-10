#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,os,sys
R=Path(__file__).resolve().parents[1]
forges=['github','gitlab','forgejo','codeberg','gitea','bitbucket','generic']

registry=json.loads((R/'content/public/forges.json').read_text())
ids=[x['id'] for x in registry.get('adapters',[])]
if ids != forges:
 raise SystemExit(f'forge registry mismatch: expected={forges} actual={ids}')
for f in forges:
 env=os.environ.copy(); env['COMMONS_FORGE_KIND']=f; env['COMMONS_FORGE_URL']='https://example.invalid/org/repo'
 subprocess.run(['python3','scripts/build_site.py'],cwd=R,env=env,check=True,stdout=subprocess.DEVNULL)
 html=(R/'public/en/contribute/index.html').read_text()
 if 'example.invalid' not in html: raise SystemExit(f'forge {f} not represented')
print('FORGE_AUDIT_PASS modes='+str(len(forges)))
