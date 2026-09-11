#!/usr/bin/env python3
from __future__ import annotations
import hashlib,os,re,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Optional private deny-hashes are supplied at release time through the environment.
# They are never stored in the public repository.
DENY={x.strip().lower() for x in os.getenv('PUBLIC_RELEASE_PRIVATE_DENY_HASHES','').split(',') if x.strip()}
SKIP_DIRS={'.git','__pycache__'}
TEXT_EXT={'.md','.json','.py','.css','.js','.yml','.yaml','.toml','.txt','.html','.xml','.svg','.gitignore',''}
from nsc_model import project_view, public_registry
_project=project_view() if (ROOT/'content/public/project.json').exists() else {'locales':[]}
_registry=public_registry() if (ROOT/'content/public/public_registry.json').exists() else {'machine_endpoints':{}}
# Public internal URLs are derived from the route registry plus locale roots.
PUBLIC_WEB_PREFIXES=tuple(sorted(set(_registry['machine_endpoints'].values()) | {'/'+loc+'/' for loc in _project.get('locales',[])} | {'/data/','/en/'}))
secret_patterns=[
    re.compile(r'ghp_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----'),
    re.compile(r'Bearer\s+[A-Za-z0-9._-]{24,}',re.I),
]
def norm_token(s): return ''.join(ch.lower() for ch in s if ch.isalnum())
def digest(s): return hashlib.sha256(norm_token(s).encode()).hexdigest()
errs=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in SKIP_DIRS for x in p.parts): continue
    if p.suffix.lower() not in TEXT_EXT and p.name not in {'LICENSE','VERSION','SKILL.md','README.md','CONTRIBUTING.md','SECURITY.md'}: continue
    try: text=p.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    # Generic absolute filesystem path check. Explicit public web endpoints are allowed.
    for m in re.finditer(r'(?:^|[\s"\'`])(/(?!/)[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.\-]+)+)',text):
        candidate=m.group(1)
        if not candidate.startswith(PUBLIC_WEB_PREFIXES):
            errs.append(f'{p.relative_to(ROOT)}: absolute local-style path detected'); break
    if re.search(r'(?:^|[\s"\'`])[A-Za-z]:\\[A-Za-z0-9_.-]+\\',text):
        errs.append(f'{p.relative_to(ROOT)}: absolute local-style path detected')
    for rx in secret_patterns:
        if rx.search(text): errs.append(f'{p.relative_to(ROOT)}: credential-like material detected'); break
    if DENY:
        tokens=re.findall(r'[A-Za-z0-9_\-]{2,}',text)
        candidates=set(tokens)
        for t in tokens: candidates.update(re.split(r'[_\-]+',t))
        if any(len(norm_token(t))>=3 and digest(t) in DENY for t in candidates):
            errs.append(f'{p.relative_to(ROOT)}: blocked private identifier detected')
if errs:
    print('PUBLIC RELEASE LEAK SCAN FAILED',file=sys.stderr)
    for e in sorted(set(errs)): print(' - '+e,file=sys.stderr)
    sys.exit(1)
print('PUBLIC_RELEASE_LEAK_SCAN_PASS')
