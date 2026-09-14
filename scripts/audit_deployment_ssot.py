#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = '0.4.0-beta.8'
EXPECTED_RELEASE = 'public-web-v' + EXPECTED_VERSION
EXPECTED = {
    'github-pages': ('.github/workflows/pages.yml', 'configured-live-path-exercised'),
    'gitlab-pages': ('.gitlab-ci.yml', 'configured-live-path-exercised'),
}
STALE = {'configured-live-smoke-pending', 'configured-unexercised'}
errs: list[str] = []

def load(rel: str):
    p = ROOT / rel
    if not p.exists():
        errs.append(f'missing {rel}')
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        errs.append(f'{rel}: invalid JSON: {e}')
        return {}

version = (ROOT/'VERSION').read_text(encoding='utf-8').strip() if (ROOT/'VERSION').exists() else ''
if version != EXPECTED_VERSION:
    errs.append(f'VERSION expected {EXPECTED_VERSION}, got {version!r}')
release = load('RELEASE.json')
policy = load('content/public/release_policy.json')
ssot = load('PUBLIC_SSOT.json')
forge = load('content/public/forge_topology.json')

for label, doc in [('RELEASE.json', release), ('release_policy.json', policy)]:
    adapters = {x.get('id'): x for x in doc.get('configured_static_deployment_adapters', []) if isinstance(x, dict)}
    for aid, (config, status) in EXPECTED.items():
        a = adapters.get(aid)
        if not a:
            errs.append(f'{label}: missing adapter {aid}')
            continue
        if a.get('config') != config:
            errs.append(f'{label}: {aid} config expected {config}, got {a.get("config")!r}')
        if a.get('status') != status:
            errs.append(f'{label}: {aid} status expected {status}, got {a.get("status")!r}')
        if a.get('status') in STALE:
            errs.append(f'{label}: stale adapter state survives for {aid}: {a.get("status")}')
    if doc.get('turnkey_static_deployment_adapters') != []:
        errs.append(f'{label}: turnkey adapters must remain empty until canonical provider-evidence certification exists')
    notes = str(doc.get('notes', ''))
    for phrase in ['both configured static deployment paths have been exercised', 'same-source parity', 'turnkey_static_deployment_adapters']:
        if phrase.lower() not in notes.lower():
            errs.append(f'{label}: notes missing terminal SSOT qualifier: {phrase}')

if release.get('version') != EXPECTED_VERSION or release.get('release') != EXPECTED_RELEASE or release.get('release_id') != EXPECTED_RELEASE:
    errs.append('RELEASE.json release identity is not beta.8-consistent')
if ssot.get('release') != EXPECTED_RELEASE:
    errs.append('PUBLIC_SSOT.json release is not beta.8-consistent')

# Validate the repository's actual canonical topology schema (nsc-forge-topology-v1).
# The previous terminal addendum incorrectly expected a plural `mirrors` array.
canonical = forge.get('canonical_source', {})
mirror = forge.get('mirror', {})
pages = forge.get('public_pages', {})
if forge.get('schema') != 'nsc-forge-topology-v1':
    errs.append(f'forge_topology schema mismatch: {forge.get("schema")!r}')
if canonical.get('forge') != 'github' or canonical.get('repository') != 'navier-stokes-commons/navier-stokes-commons.github.io' or canonical.get('branch') != 'main':
    errs.append('forge_topology canonical source mismatch')
if mirror.get('forge') != 'gitlab' or mirror.get('project_path') != 'champia-labs-group/navier-stokes-commons-public' or mirror.get('branch') != 'main' or mirror.get('policy') != 'fast-forward-only' or mirror.get('force_push_forbidden') is not True:
    errs.append('forge_topology GitLab mirror mismatch')
if pages.get('github') != 'https://navier-stokes-commons.github.io/':
    errs.append('forge_topology GitHub Pages URL mismatch')
if pages.get('gitlab') != 'https://champia-labs-group.gitlab.io/navier-stokes-commons-public/':
    errs.append('forge_topology GitLab Pages URL mismatch')
if 'same canonical release source' not in str(forge.get('source_mirror_invariant','')):
    errs.append('forge_topology same-source terminal invariant missing')

for rel in ['RELEASE.json', 'content/public/release_policy.json']:
    txt = (ROOT/rel).read_text(encoding='utf-8') if (ROOT/rel).exists() else ''
    for stale in STALE:
        if stale in txt:
            errs.append(f'{rel}: stale literal remains: {stale}')

if errs:
    print('R17_DEPLOYMENT_SSOT_AUDIT_FAILED', file=sys.stderr)
    for e in errs:
        print(' - ' + e, file=sys.stderr)
    raise SystemExit(1)
print('R17_DEPLOYMENT_SSOT_AUDIT_PASS adapters=exercised turnkey=uncertified topology_schema=v1-singular-mirror same_source_gate=retained')
