#!/usr/bin/env python3
from pathlib import Path
from png_metric import mad_png
from playwright.sync_api import sync_playwright
import re,shutil
R=Path(__file__).resolve().parents[1];P=R/'public';css=(R/'assets/style.css').read_text();js=(R/'assets/site.js').read_text();h=(P/'en/index.html').read_text();h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1);h=re.sub(r'<link rel="stylesheet"[^>]*>',lambda _:'<style>'+css+'</style>',h,count=1);h=re.sub(r'<script src="[^"]+" defer></script>',lambda _:'<script>'+js+'</script>',h,count=1)
exe=shutil.which('chromium') or shutil.which('chromium-browser') or ''
def mad(a,b):return mad_png(a,b)
with sync_playwright() as p:
 o={'headless':True,'args':['--no-sandbox','--disable-gpu']};
 if exe:o['executable_path']=exe
 b=p.chromium.launch(**o)
 # Ordinary users: rich surface remains alive after the finite intro, pointer changes it, global pause freezes it.
 c=b.new_context(viewport={'width':1100,'height':760},reduced_motion='no-preference');g=c.new_page();g.set_content(h,wait_until='domcontentloaded');st=g.locator('[data-vortex-stage]');amb=g.locator('[data-ambient-field]');g.wait_for_timeout(4200);a=st.screenshot();aa=amb.screenshot();g.wait_for_timeout(500);bb=st.screenshot();ab=amb.screenshot();vortex_live=mad(a,bb);ambient_live=mad(aa,ab)
 box=amb.bounding_box();g.mouse.move(box['x']+box['width']*.18,box['y']+box['height']*.28);g.wait_for_timeout(160);p0=amb.screenshot();g.mouse.move(box['x']+box['width']*.82,box['y']+box['height']*.68);g.wait_for_timeout(160);p1=amb.screenshot();pointer=mad(p0,p1)
 toggle=g.locator('.r14-global-motion');toggle.click();g.wait_for_timeout(120);s0=st.screenshot();x0=amb.screenshot();g.wait_for_timeout(500);s1=st.screenshot();x1=amb.screenshot();paused=max(mad(s0,s1),mad(x0,x1));c.close()
 # Reduced motion: automatic motion is static while manual scientific control remains usable.
 c=b.new_context(viewport={'width':1100,'height':760},reduced_motion='reduce');g=c.new_page();g.set_content(h,wait_until='domcontentloaded');st=g.locator('[data-vortex-stage]');amb=g.locator('[data-ambient-field]');g.wait_for_timeout(120);r0=st.screenshot();q0=amb.screenshot();g.wait_for_timeout(500);r1=st.screenshot();q1=amb.screenshot();reduced_static=max(mad(r0,r1),mad(q0,q1));kin=g.locator('[data-k]');before=float(kin.input_value());kin.evaluate("e=>{e.value='30';e.dispatchEvent(new Event('input',{bubbles:true}))}");after=float(kin.input_value());global_hidden=g.locator('.r14-global-motion').is_hidden();play_disabled=g.locator('[data-vortex-controls] [data-play]').is_disabled();c.close();b.close()
print(f'R14_MOTION_METRICS vortex_live={vortex_live:.5f} ambient_live={ambient_live:.5f} pointer={pointer:.5f} paused={paused:.5f} reduced={reduced_static:.5f} manual_delta={after-before:.1f}')
if vortex_live<.0005 or ambient_live<.0005 or pointer<.0007 or paused>.003 or reduced_static>.003 or after==before or not global_hidden or not play_disabled:raise SystemExit('R14_MOTION_EXPERIENCE_AUDIT_FAILED')
print('R14_MOTION_EXPERIENCE_AUDIT_PASS ambient_default=true pointer_response=true pause=true reduced_motion_static=true manual_control=true')
