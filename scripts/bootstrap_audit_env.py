#!/usr/bin/env python3
from __future__ import annotations
import os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(cmd):
    print('+',' '.join(map(str,cmd)),flush=True)
    subprocess.run(list(map(str,cmd)),check=True)

def ensure_zstd():
    if shutil.which('zstd'): return
    apt=shutil.which('apt-get')
    if not apt:
        raise SystemExit('AUDIT_ENV_SETUP_FAILED: zstd missing and apt-get unavailable')
    prefix=[] if hasattr(os,'geteuid') and os.geteuid()==0 else ([shutil.which('sudo')] if shutil.which('sudo') else None)
    if prefix is None:
        raise SystemExit('AUDIT_ENV_SETUP_FAILED: zstd missing and no privileged package installer available')
    run([*prefix,apt,'update'])
    run([*prefix,apt,'install','-y','--no-install-recommends','zstd'])

ensure_zstd()
run([sys.executable,'-m','pip','install','--disable-pip-version-check','-r',ROOT/'requirements-audit.txt'])
run([sys.executable,'-m','playwright','install','--with-deps','chromium'])
for mod in ['jsonschema','playwright']:
    __import__(mod)
if not shutil.which('zstd'):
    raise SystemExit('AUDIT_ENV_SETUP_FAILED: zstd unavailable after setup')
print('AUDIT_ENV_SETUP_PASS')
