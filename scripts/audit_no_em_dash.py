#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
scan_roots=[ROOT/'content',ROOT/'assets',ROOT/'scripts',ROOT/'docs',ROOT/'public']
scan_files=[ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'SKILL.md',ROOT/'start.md',ROOT/'ACCESSIBILITY.md',ROOT/'I18N.md',ROOT/'PUBLIC_CONTENT_POLICY.md',ROOT/'SECURITY.md',ROOT/'LICENSE_POLICY.md',ROOT/'RELEASE_NOTES.md']
errors=[]
EM_DASH=chr(0x2014)
seen=set()
for base in scan_roots:
    if not base.exists(): continue
    for p in base.rglob('*'):
        if p.is_file(): scan_files.append(p)
for p in scan_files:
    if not p.exists() or p in seen: continue
    seen.add(p)
    if any(x in p.parts for x in ('__pycache__','.git')): continue
    try: s=p.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    if EM_DASH in s:
        for i,line in enumerate(s.splitlines(),1):
            if EM_DASH in line: errors.append(f'{p.relative_to(ROOT)}:{i}: U+2014')
if errors:
    print('NO_EM_DASH_AUDIT_FAILED',file=sys.stderr)
    for e in errors[:100]: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'NO_EM_DASH_AUDIT_PASS files={len(seen)}')
