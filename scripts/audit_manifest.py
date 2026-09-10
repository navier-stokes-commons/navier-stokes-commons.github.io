#!/usr/bin/env python3
from __future__ import annotations
import hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; M=ROOT/'MANIFEST.sha256'; errs=[]; listed={}
if not M.exists():
    print('MANIFEST_AUDIT_FAILED missing MANIFEST.sha256',file=sys.stderr); raise SystemExit(1)
for line in M.read_text().splitlines():
    m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
    if not m: errs.append('malformed manifest line'); continue
    if m.group(2) in listed: errs.append('duplicate manifest path '+m.group(2))
    listed[m.group(2)]=m.group(1)
actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts and '.git' not in p.parts}
if set(actual)!=set(listed):
    errs.append(f'coverage mismatch missing={sorted(set(actual)-set(listed))[:20]} extra={sorted(set(listed)-set(actual))[:20]}')
for rel,d in actual.items():
    if listed.get(rel)!=d: errs.append('hash mismatch '+rel)
if errs:
    print('MANIFEST_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'MANIFEST_AUDIT_PASS files={len(actual)}')
