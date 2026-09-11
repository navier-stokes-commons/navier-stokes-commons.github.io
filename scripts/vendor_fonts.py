#!/usr/bin/env python3
"""Vendor the exact production webfonts into assets/fonts without runtime CDN use.

Scratch/cache is restricted to the policy-managed RAM-backed scratch root. This
node_modules or npm cache in the repository.
"""
from __future__ import annotations
import os, shutil, subprocess, tarfile
from scratch import ScratchPolicyError, scratch_dir
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'fonts'
VERSION='5.3.0'
PACKAGES={
  '@fontsource-variable/newsreader':('newsreader-latin-standard-normal.woff2','newsreader-latin-standard-normal.woff2'),
  '@fontsource-variable/geist':('geist-latin-wght-normal.woff2','geist-latin-wght-normal.woff2'),
  '@fontsource-variable/geist-mono':('geist-mono-latin-wght-normal.woff2','geist-mono-latin-wght-normal.woff2'),
}

def main()->int:
    try:
        scratch=scratch_dir('font-vendor')
    except ScratchPolicyError as e:
        raise SystemExit('FONT_VENDOR_FAILED '+str(e))
    scratch.mkdir(parents=True,exist_ok=True)
    cache=scratch/'npm-cache'; cache.mkdir()
    OUT.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy(); env['npm_config_cache']=str(cache); env['npm_config_update_notifier']='false'; env['npm_config_fund']='false'; env['npm_config_audit']='false'
    try:
      for pkg,(needle,dest) in PACKAGES.items():
        before=set(scratch.glob('*.tgz'))
        subprocess.run(['npm','pack',f'{pkg}@{VERSION}','--pack-destination',str(scratch),'--silent'],cwd=scratch,env=env,check=True)
        tgzs=list(set(scratch.glob('*.tgz'))-before)
        if len(tgzs)!=1: raise SystemExit(f'FONT_VENDOR_FAILED pack ambiguity for {pkg}: {tgzs}')
        unpack=scratch/(pkg.split('/')[-1].replace('@','')+'-unpack'); unpack.mkdir()
        with tarfile.open(tgzs[0],'r:gz') as tf: tf.extractall(unpack,filter='data')
        matches=list(unpack.rglob(needle))
        if len(matches)!=1: raise SystemExit(f'FONT_VENDOR_FAILED expected {needle} once in {pkg}, found {len(matches)}')
        shutil.copy2(matches[0],OUT/dest)
        lic=list(unpack.rglob('LICENSE'))+list(unpack.rglob('OFL.txt'))+list(unpack.rglob('OFL-1.1.txt'))
        if lic:
            ldir=OUT/'licenses'; ldir.mkdir(exist_ok=True)
            shutil.copy2(lic[0],ldir/(pkg.split('/')[-1]+'-OFL-1.1.txt'))
      missing=[dest for _,dest in PACKAGES.values() if not (OUT/dest).is_file()]
      if missing: raise SystemExit('FONT_VENDOR_FAILED missing='+','.join(missing))
      print('FONT_VENDOR_PASS version='+VERSION+' files='+','.join(dest for _,dest in PACKAGES.values()))
      return 0
    finally:
      shutil.rmtree(scratch,ignore_errors=True)

if __name__=='__main__': raise SystemExit(main())
