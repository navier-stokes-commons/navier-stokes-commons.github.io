#!/usr/bin/env python3
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1]; css=(R/'assets/style.css').read_text(); errs=[]
required={
 'newsreader-latin-standard-normal.woff2':('Newsreader Variable','newsreader-OFL-1.1.txt'),
 'geist-latin-wght-normal.woff2':('Geist Variable','geist-OFL-1.1.txt'),
 'geist-mono-latin-wght-normal.woff2':('Geist Mono Variable','geist-mono-OFL-1.1.txt'),
}
font_bytes=0
for fn,(fam,license_name) in required.items():
 p=R/'assets/fonts'/fn
 if not p.is_file() or p.stat().st_size<10000: errs.append(f'missing/implausible font asset {fn}')
 elif p.read_bytes()[:4]!=b'wOF2': errs.append(f'{fn} is not a WOFF2 payload')
 else: font_bytes += p.stat().st_size
 if fam not in css or f'fonts/{fn}' not in css: errs.append(f'CSS does not bind {fam} to {fn}')
 pub=R/'public'/'assets'/'fonts'/fn
 if p.is_file() and not pub.is_file(): errs.append(f'built public tree missing font {fn}')
 lic=R/'assets/fonts/licenses'/license_name
 if not lic.is_file() or lic.stat().st_size<1000: errs.append(f'missing font license {license_name}')
if re.search(r'@import\s+url\([^)]*https?://',css,re.I) or re.search(r'@font-face\s*\{[^}]*https?://',css,re.I|re.S): errs.append('remote runtime font dependency present')
if 'font-optical-sizing:auto' not in css: errs.append('Newsreader optical-size axis is vendored but optical sizing is not enabled')
if font_bytes>260*1024: errs.append(f'Latin flagship font payload {font_bytes} exceeds 260 KiB budget')
for page_rel in ['index.html','en/index.html']:
 page=R/'public'/page_rel
 if not page.is_file(): errs.append(f'missing flagship page for font preload audit: {page_rel}'); continue
 txt=page.read_text()
 for fn in ['newsreader-latin-standard-normal.woff2','geist-latin-wght-normal.woff2']:
  if not re.search(r'<link[^>]+rel="preload"[^>]+as="font"[^>]+href="[^"]*'+re.escape(fn)+r'"[^>]*crossorigin',txt):
   errs.append(f'{page_rel} does not preload first-viewport font {fn}')

if errs:
 print('FONT_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];raise SystemExit(1)
print(f'FONT_AUDIT_PASS display=NewsreaderVariable(opsz+wght) sans=GeistVariable mono=GeistMonoVariable licenses=present runtime_remote=false bytes={font_bytes}')
