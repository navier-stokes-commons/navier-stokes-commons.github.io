#!/usr/bin/env python3
from pathlib import Path
import sys,re
css=(Path(__file__).resolve().parents[1]/'assets/style.css').read_text()
# Remove comments and quoted strings before delimiter balance checks.
t=re.sub(r'/\*.*?\*/','',css,flags=re.S)
t=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','""',t)
errs=[]
for op,cl,name in [('{','}','braces'),('(',')','parentheses'),('[',']','brackets')]:
    n=0
    for ch in t:
        if ch==op:n+=1
        elif ch==cl:
            n-=1
            if n<0: errs.append(f'unbalanced {name}: premature {cl}'); break
    if n!=0: errs.append(f'unbalanced {name}: delta={n}')
for bad in [r'var\([^)]*$',r'color-mix\([^;{}]*var\([^)]*[,;}]']:
    if re.search(bad,t,re.M): errs.append('suspicious unterminated CSS function')
if '.equation-object' not in css or '.language-grid' not in css: errs.append('alpha3 cascade sentinels missing')
if errs:
 print('CSS_SYNTAX_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; sys.exit(1)
print('CSS_SYNTAX_AUDIT_PASS')
