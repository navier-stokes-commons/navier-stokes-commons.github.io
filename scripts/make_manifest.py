#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.name=='MANIFEST.sha256' or '__pycache__' in p.parts or '.git' in p.parts:
        continue
    rows.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}')
(ROOT/'MANIFEST.sha256').write_text('\n'.join(rows)+'\n')
print(f'MANIFEST_WRITTEN files={len(rows)}')
