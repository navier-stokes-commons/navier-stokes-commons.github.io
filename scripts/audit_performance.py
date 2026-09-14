#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re,sys
ROOT=Path(__file__).resolve().parents[1];PUBLIC=ROOT/'public';CSS=ROOT/'assets/style.css';SITE=ROOT/'assets/site.js';R17=ROOT/'assets/r17-fluid.js';FONTS=ROOT/'assets/fonts';errs=[]
limits={'css':60*1024,'site_js':48*1024,'r17_js':27*1024,'rich_js_total':64*1024,'html':110*1024,'fonts_total':420*1024}
for key,path in [('css',CSS),('site_js',SITE),('r17_js',R17)]:
 if not path.exists():errs.append(f'missing asset {path.relative_to(ROOT)}')
 elif path.stat().st_size>limits[key]:errs.append(f'{key} {path.stat().st_size} > {limits[key]}')
if SITE.exists() and R17.exists() and SITE.stat().st_size+R17.stat().st_size>limits['rich_js_total']:errs.append(f'rich JS total {SITE.stat().st_size+R17.stat().st_size} > {limits["rich_js_total"]}')
css=CSS.read_text() if CSS.exists() else '';site=SITE.read_text() if SITE.exists() else '';r17=R17.read_text() if R17.exists() else ''
if re.search(r'@import\s',css,re.I):errs.append('CSS @import prohibited')
if re.search(r'url\(["\']?https?://',css,re.I):errs.append('remote CSS asset prohibited')
if re.search(r'transition\s*:\s*all\b',css,re.I):errs.append('transition: all prohibited')
if 'setInterval(' in site+r17:errs.append('setInterval prohibited for persistent decorative motion')
font_bytes=sum(p.stat().st_size for p in FONTS.glob('*.woff2')) if FONTS.exists() else 0
if font_bytes>limits['fonts_total']:errs.append(f'font WOFF2 total {font_bytes} > {limits["fonts_total"]}')
class P(HTMLParser):
 def __init__(self):super().__init__();self.remote=[];self.scripts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='script' and a.get('src'):
   self.scripts.append(a['src'])
   if urlsplit(a['src']).scheme:self.remote.append(('script',a['src']))
  if tag=='link' and a.get('rel')=='stylesheet' and a.get('href') and urlsplit(a['href']).scheme:self.remote.append(('stylesheet',a['href']))
max_html=(0,None);pages=0
for page in PUBLIC.rglob('*.html'):
 pages+=1;size=page.stat().st_size
 if size>max_html[0]:max_html=(size,page)
 if size>limits['html']:errs.append(f'{page.relative_to(PUBLIC)} HTML {size} > {limits["html"]}')
 p=P();p.feed(page.read_text())
 if p.remote:errs.append(f'{page.relative_to(PUBLIC)} remote runtime asset {p.remote[:2]}')
 rel=page.relative_to(PUBLIC).as_posix(); english_rich=(rel=='index.html' or (rel.startswith('en/') and rel!='en/math/index.html'))
 has_r17=any('r17-fluid.js' in x for x in p.scripts)
 if english_rich and not has_r17:errs.append(rel+' missing English R17 runtime')
 if not english_rich and has_r17:errs.append(rel+' loads R17 runtime outside English rich surface')
if errs:
 print('PERFORMANCE_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];sys.exit(1)
print(f'PERFORMANCE_AUDIT_PASS pages={pages} css_bytes={CSS.stat().st_size} site_js_bytes={SITE.stat().st_size} r17_js_bytes={R17.stat().st_size} rich_js_total={SITE.stat().st_size+R17.stat().st_size} font_bytes={font_bytes} max_html_bytes={max_html[0]}')
