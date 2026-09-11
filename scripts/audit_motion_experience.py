#!/usr/bin/env python3
from pathlib import Path
from png_metric import mad_png
from playwright.sync_api import sync_playwright
import re,shutil
R=Path(__file__).resolve().parents[1];P=R/'public';css=(R/'assets/style.css').read_text();js=(R/'assets/site.js').read_text();h=(P/'en/index.html').read_text();h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1);h=re.sub(r'<link rel="stylesheet"[^>]*>', lambda _:'<style>'+css+'</style>',h,count=1);h=re.sub(r'<script src="[^"]+" defer></script>', lambda _:'<script>'+js+'</script>',h,count=1)
def mad(a,b): return mad_png(a,b)
exe=shutil.which('chromium') or shutil.which('chromium-browser') or ''
def one(pref):
 with sync_playwright() as p:
  o={'headless':True,'args':['--no-sandbox','--disable-gpu']};
  if exe:o['executable_path']=exe
  b=p.chromium.launch(**o);c=b.new_context(viewport={'width':1000,'height':720},reduced_motion=pref);g=c.new_page();g.set_content(h,wait_until='domcontentloaded');st=g.locator('[data-vortex-stage]')
  if pref=='reduce':
   g.wait_for_timeout(100);a=st.screenshot();g.wait_for_timeout(550);bb=st.screenshot();d=mad(a,bb);play_disabled=g.locator('[data-vortex-controls] [data-play]').is_disabled();before=float(g.locator('[data-k]').input_value());g.locator('[data-k]').evaluate("e=>{e.value='30';e.dispatchEvent(new Event('input',{bubbles:true}))}");after=float(g.locator('[data-k]').input_value());c.close();b.close();return d,before,after,play_disabled
  g.wait_for_timeout(4100);a=st.screenshot();g.wait_for_timeout(450);bb=st.screenshot();d=mad(a,bb);c.close();b.close();return d,None,None,None
settled,_,_,_=one('no-preference');red,before,after,play_disabled=one('reduce');print(f'EXPERIENCE_MOTION_METRICS settled_mad={settled:.5f} reduced_mad={red:.5f} reduced_manual_delta={after-before:.1f} play_disabled={play_disabled}')
if settled>.003 or red>.003 or after==before or not play_disabled: raise SystemExit('EXPERIENCE_MOTION_AUDIT_FAILED')
print('EXPERIENCE_MOTION_AUDIT_PASS finite_intro=true settles=true reduced_motion_static=true manual_control=true play_disabled=true')
