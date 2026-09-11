#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; errs=[]
load=lambda p:json.loads(p.read_text())
auth=load(C/'authority_map.json'); reg=load(C/'public_registry.json'); project=load(C/'project.json'); missions=load(C/'missions.json'); quests=load(C/'quests.json')['quests']; claims=load(C/'claims.json')['claims']; sprint=load(C/'founding_sprint.json'); locale_reg=load(C/'locale_registry.json')
# Authority-map structural closure.
facts=auth.get('facts',[]); ids=[x.get('id') for x in facts]
if len(ids)!=len(set(ids)): errs.append('authority map contains duplicate fact IDs')
allowed_classes=set(auth.get('classes',{}))
for f in facts:
    if f.get('class') not in allowed_classes: errs.append(f"{f.get('id')}: unknown authority class")
# Every simple file authority named before a JSON pointer/compound expression must exist.
for f in facts:
    a=f.get('authority','')
    if ' + ' in a or a.startswith('scripts/'): continue
    rel=a.split('#',1)[0]
    if '/' in rel or rel=='VERSION':
        exists = bool(list(ROOT.glob(rel))) if '*' in rel else (ROOT/rel).exists()
        if not exists: errs.append(f"{f.get('id')}: authority path missing {rel}")
# Release-critical facts may not have writable reverse copies.
for field in auth['forbidden_writable_reverse_fields']['content/public/project.json']:
    if field in project: errs.append(f'project.json illegally duplicates derived field {field}')
for m in missions:
    for field in auth['forbidden_writable_reverse_fields']['content/public/missions.json']:
        if field in m: errs.append(f"{m['id']}: illegal reverse field {field}")
for q in quests:
    for field in auth['forbidden_writable_reverse_fields']['content/public/quests.json']:
        if field in q: errs.append(f"{q['id']}: illegal reverse field {field}")
for c in claims:
    for field in auth['forbidden_writable_reverse_fields']['content/public/claims.json']:
        if field in c: errs.append(f"{c['id']}: illegal writable derived field {field}")
    if c.get('baseline_status') not in {'source-reported','primary-source-defined','derived-unreviewed'}:
        errs.append(f"{c['id']}: baseline status is not an admissible non-elevated state")
# Locale strings may translate labels, never duplicate license values.
for p in sorted((C/'locales').glob('*.json')):
    d=load(p)
    if 'license' in d.get('footer',{}): errs.append(f'{p.name}: writable license tuple duplicated')
# Known high-risk generated facts may not be literals in implementation runtime.
gen=(ROOT/'scripts/build_site.py').read_text(); js=(ROOT/'assets/site.js').read_text()
for value,label,noun in [(len(missions),'mission count','missions'),(len(quests),'quest count','quests'),(len(locale_reg['locales']),'locale count','locales'),(len(sprint['quest_ids']),'sprint quest count','quests')]:
    pat=rf'\b{value} {noun}\b'
    if re.search(pat,gen,re.I) or re.search(pat,js,re.I): errs.append(f'hardcoded derived {label} in runtime')
if re.search(r'const\s+names\s*=\s*\{',js): errs.append('theme/localization label dictionary duplicated in JS')
if re.search(r'const\s+exponents\s*=\s*\{',js): errs.append('scaling coefficient dictionary duplicated in JS')
for pat in [r'Math\.exp\(-2\*nu\*t\)',r'A\s+e\^\(-2\s+nu\s+t\)',r'Math\.sin\(x\)\*Math\.cos\(y\)']:
    if re.search(pat,gen) or re.search(pat,js): errs.append('exact-flow instance equation duplicated in renderer runtime')
if re.search(r'CATEGORY_ORDER\s*=\s*\[',gen): errs.append('taxonomy order duplicated in build runtime')
model=(ROOT/'scripts/nsc_model.py').read_text(); launch=(ROOT/'scripts/audit_launch.py').read_text()
if re.search(r'range\(6\)',model) or "{'L0','L1','L2','L3','L4','L5'}" in launch: errs.append('task-ladder shape duplicated as implementation snapshot')
# Public endpoint locations have exactly one writable registry.
if not reg.get('machine_endpoints') or len(reg['machine_endpoints'])!=len(set(reg['machine_endpoints'])): errs.append('machine endpoint registry missing/duplicate keys')
if len(reg['machine_endpoints'].values())!=len(set(reg['machine_endpoints'].values())): errs.append('machine endpoint registry has duplicate addresses')
# All top-level release/report projections must carry generated markers or be generated whole-file by reconcile.
reconcile=(ROOT/'scripts/reconcile.py').read_text()
for rel in ['RELEASE.json','PUBLIC_SSOT.json','CITATION.cff','RELEASE_NOTES.md','docs/FOUNDING_SPRINT.md']:
    if f"'{rel}'" not in reconcile: errs.append(f'{rel}: not owned by reconciliation controller')
for rel,marker in [('README.md','release-summary'),('README.md','license-summary'),('README.md','sprint-id'),('README.md','agent-entrypoints'),('docs/PRODUCT_GUIDE.md','participation-capability'),('docs/LAUNCH_ANNOUNCEMENT.md','launch-counts'),('LICENSE_POLICY.md','license-policy'),('CONTENT_LICENSE.md','content-license-summary'),('start.md','agent-fastest-path'),('SKILL.md','agent-discovery'),('SKILL.md','claims-endpoint'),('AGENTS.md','agent-start-order'),('docs/WCAG_SELF_ASSESSMENT.md','locale-assurance-status')]:
    txt=(ROOT/rel).read_text()
    if f'<!-- GENERATED:{marker}:start -->' not in txt or f'<!-- GENERATED:{marker}:end -->' not in txt: errs.append(f'{rel}: generated projection marker missing: {marker}')
# LICENSE is derived from the selected software SPDX identifier and a reusable exact text template.
software=project['license']['software']; license_template=ROOT/'references'/'licenses'/f'{software}.txt'
if not license_template.exists(): errs.append(f'license text template missing for {software}')
elif (ROOT/'LICENSE').read_bytes()!=license_template.read_bytes(): errs.append('LICENSE drifted from canonical selected SPDX template')
# Core agent docs may mention endpoint addresses only inside reconciled generated blocks.
for rel in ['start.md','SKILL.md','AGENTS.md','README.md']:
    txt=(ROOT/rel).read_text()
    stripped=re.sub(r'<!-- GENERATED:[^:]+:start -->.*?<!-- GENERATED:[^:]+:end -->','',txt,flags=re.S)
    for address in reg['machine_endpoints'].values():
        if address in stripped: errs.append(f'{rel}: writable prose duplicates machine endpoint {address}')
# Runtime code must resolve endpoint addresses through public_registry, not carry address snapshots.
for rp in sorted((ROOT/'scripts').glob('*.py')):
    if rp.name in {'reconcile.py','audit_authority.py'}: continue
    txt=rp.read_text()
    for address in reg['machine_endpoints'].values():
        if address in txt: errs.append(f'{rp.relative_to(ROOT)}: runtime duplicates machine endpoint address {address}')
# Browser assurance must be public and release-authoritative, while each host
# executes the expensive full suite exactly once per pipeline.
runner=(ROOT/'scripts/run_all_checks.py').read_text(); ci=(ROOT/'.github/workflows/ci.yml').read_text(); pages_wf=(ROOT/'.github/workflows/pages.yml').read_text(); gl=(ROOT/'.gitlab-ci.yml').read_text()
if 'scripts/audit_browser.py' not in runner: errs.append('public canonical suite omits browser audit')
if 'python3 scripts/bootstrap_audit_env.py' not in ci: errs.append('GitHub CI shared portable audit bootstrap missing')
if ci.count('python3 scripts/run_all_checks.py')!=1: errs.append('GitHub workflow must execute complete suite exactly once')
if 'actions/deploy-pages@' not in pages_wf or 'name: github-pages' not in pages_wf: errs.append('GitHub Pages workflow does not deploy exact audited artifact')
if 'actions/deploy-pages@' in ci: errs.append('GitHub CI must not deploy; pages.yml is the sole deploy authority')
if 'cancel-in-progress: true' not in ci: errs.append('GitHub CI lacks redundant-run cancellation')
if 'cache: "pip"' not in ci: errs.append('GitHub CI pip cache missing')
# R7: pages.yml is the canonical GitHub Pages deployment adapter; see audit_host_configs.py
if 'python3 scripts/bootstrap_audit_env.py' not in gl: errs.append('GitLab shared portable audit bootstrap missing')
if gl.count('python3 scripts/run_all_checks.py')!=1: errs.append('GitLab pipeline must execute complete suite exactly once')
if 'artifacts: true' not in gl or 'publish: public' not in gl: errs.append('GitLab Pages does not consume exact audited public artifact')
if 'interruptible: true' not in gl: errs.append('GitLab audit job lacks redundant-pipeline cancellation hint')
if 'resource_group: pages' not in gl: errs.append('GitLab Pages deploy lacks serialization')
if errs:
    print('AUTHORITY_INVARIANT_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; raise SystemExit(1)
print(f'AUTHORITY_INVARIANT_AUDIT_PASS facts={len(facts)} endpoints={len(reg["machine_endpoints"])} writable_reverse_relations=0 browser_gate=public')
