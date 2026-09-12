#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, html, urllib.parse, re, math
from pathlib import Path
from nsc_model import project_view, expanded_missions, expanded_quests, expanded_claims_doc, localized_license_line, counts, capabilities, public_registry, release_policy

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'/'public'
PUBLIC=ROOT/'public'
ASSETS=ROOT/'assets'
project=project_view()
registry=public_registry()
sources=json.loads((CONTENT/'sources.json').read_text())
missions=expanded_missions()
contributions=json.loads((CONTENT/'contributions.json').read_text()) if (CONTENT/'contributions.json').exists() else []
forges=json.loads((CONTENT/'forges.json').read_text()) if (CONTENT/'forges.json').exists() else {'adapters':[]}
scaling=json.loads((CONTENT/'scaling_model.json').read_text())
simulations_doc=json.loads((CONTENT/'simulations.json').read_text())
reference_benchmarks=json.loads((CONTENT/'reference_benchmarks.json').read_text())
actions_doc=json.loads((CONTENT/'actions.json').read_text())
research_context=json.loads((CONTENT/'research_context.json').read_text())
clay_problem_status=json.loads((CONTENT/'clay_problem_status.json').read_text())
frontier_graph=json.loads((CONTENT/'frontier_graph.json').read_text())
frontier_updates=json.loads((CONTENT/'frontier_updates.json').read_text())
formula_catalog=json.loads((CONTENT/'formulas.json').read_text())
quests=expanded_quests()
quests_doc={'schema':json.loads((CONTENT/'quests.json').read_text()).get('schema','nsc-quests-v1'),'quests':quests}
task_ladder=json.loads((CONTENT/'task_ladder.json').read_text())
claims_doc=expanded_claims_doc()
governance=json.loads((CONTENT/'governance.json').read_text())
founding_sprint=json.loads((CONTENT/'founding_sprint.json').read_text())
reviews=json.loads((CONTENT/'reviews.json').read_text()) if (CONTENT/'reviews.json').exists() else []
public_ssot=json.loads((ROOT/'PUBLIC_SSOT.json').read_text())
quest_by_id={q['id']:q for q in quests}
mission_by_id={m['id']:m for m in missions}
rung_by_id={r['id']:r for r in task_ladder['rungs']}
formula_by_id={f['id']:f for f in formula_catalog['formulas']}
source_by_id={s['id']:s for s in sources}
def break_hex(value):
    value=str(value)
    return '<wbr>'.join(value[i:i+8] for i in range(0,len(value),8)) if re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}',value) else esc(value)
def packet_submission():
    return {'actions':'../actions.json','attempt':'claim_quest','result':'submit_result','review':'request_review','reference_semantics':'Resolve relative to this packet document; operation IDs are listed in actions.json (claim_quest, submit_result, request_review).','rule':'An agent result is an artifact for review, never an automatic claim elevation.'}

def math_text_breaks(document):
    # Plain HTML has no overflow-wrap stylesheet. Add optional breaks only in
    # long visible tokens; keep attributes, link targets and copied text exact.
    head,body=document.split('<body>',1)
    def token_breaks(match):
        value=match.group().replace('/','/<wbr>')
        return re.sub(r'[A-Za-z]{12,}',lambda m:'<wbr>'.join(m[0][i:i+8] for i in range(0,len(m[0]),8)),value)
    parts=re.split(r'(<[^>]+>)',body)
    return head+'<body>'+''.join(part if part.startswith('<') else re.sub(r'\S{14,}',token_breaks,part) for part in parts)
locales={loc:json.loads((CONTENT/'locales'/f'{loc}.json').read_text()) for loc in project['locales']}
mi18n={loc:json.loads((CONTENT/'mission_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}
taxonomy={loc:json.loads((CONTENT/'taxonomy_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}
source_i18n={loc:json.loads((CONTENT/'source_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}

SITE_URL=os.getenv('SITE_URL','').rstrip('/')
GH_REPO=os.getenv('GITHUB_REPOSITORY','').strip()
GL_URL=os.getenv('CI_PROJECT_URL','').strip().rstrip('/')
FORGE_KIND=os.getenv('COMMONS_FORGE_KIND','').strip().lower()
FORGE_URL=os.getenv('COMMONS_FORGE_URL','').strip().rstrip('/')
if not FORGE_KIND:
    FORGE_KIND='github' if GH_REPO else ('gitlab' if GL_URL else 'generic')
if not FORGE_URL:
    FORGE_URL=(f'https://github.com/{GH_REPO}' if GH_REPO else GL_URL)
REPO_URL=FORGE_URL
HOST=FORGE_KIND

CATEGORY_ORDER=json.loads((CONTENT/'taxonomy.json').read_text())['category_order']

SECURITY_META="""<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"><meta name="referrer" content="no-referrer">"""

def deployed_ref(from_public_path:str, logical_site_path:str)->str:
    """Relative URL from a generated public file to one logical site-root path."""
    out=os.path.relpath(logical_site_path.lstrip('/'), start=str(Path(from_public_path).parent)).replace(os.sep,'/')
    return out+'/' if logical_site_path.endswith('/') and not out.endswith('/') else out


def esc(x): return html.escape(str(x), quote=True)
def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def rel(page:Path,target:str)->str:
    return os.path.relpath(PUBLIC/target, page.parent).replace(os.sep,'/')
def logical_target(loc:str,kind:str,slug:str|None=None)->str:
    if kind=='home': return f'{loc}/index.html'
    if kind=='mission': return f'{loc}/missions/{slug}/index.html'
    return f'{loc}/{kind}/index.html'
def repo_issue(template:str,title:str='')->str:
    if not REPO_URL:
        return ''
    kind={'claim_quest.yml':'attempt','open_attempt.yml':'attempt','side_quest.yml':'side_quest','submit_result.yml':'result','review.yml':'review'}.get(template,'contribution')
    if HOST=='github':
        q={'template':template}
        if title:q['title']=title
        return f'{REPO_URL}/issues/new?{urllib.parse.urlencode(q)}'
    if HOST=='gitlab':
        return f'{REPO_URL}/-/work_items/new?{urllib.parse.urlencode({"description_template":kind})}'
    if HOST in {'forgejo','gitea','codeberg'}:
        body=f'Contribution type: {kind}\n\nPlease include the relevant mission ID, exact claim, evidence, limitations, and reproduction instructions.'
        return f'{REPO_URL}/issues/new?{urllib.parse.urlencode({"title":title or kind,"body":body})}'
    # Bitbucket and unknown forges intentionally fall back to the repository root;
    # CONTRIBUTING.md + the public manifest schema remain the portable channel.
    return REPO_URL

def forge_label():
    return {'github':'GitHub','gitlab':'GitLab','forgejo':'Forgejo','codeberg':'Codeberg','gitea':'Gitea','bitbucket':'Bitbucket','generic':'Git repository'}.get(HOST,HOST.title())

def cat_label(loc,cat): return taxonomy[loc]['categories'].get(cat,cat)
def level_label(loc,level): return taxonomy[loc]['levels'].get(level,level)
def contrib_label(loc,name): return taxonomy[loc]['contributors'].get(name,name)

def locale_is_preview(loc:str)->bool:
    return project.get('locale_status',{}).get(loc)=='interface-preview'

def canonical_english_attrs(loc:str)->str:
    return ' lang="en" dir="ltr"' if locale_is_preview(loc) else ''

def locale_preview_notice(loc:str)->str:
    if not locale_is_preview(loc):
        return ''
    text=locales[loc].get('preview_notice','').strip()
    if not text:
        return ''
    return f'<aside class="locale-preview-notice" role="note" lang="en" dir="ltr"><div class="container"><strong>Interface preview</strong><span>{esc(text)}</span></div></aside>'

def source_links(ids, page:Path):
    out=[]
    for sid in ids:
        s=source_by_id[sid]
        out.append(f'<a class="source-inline" lang="en" dir="ltr" href="{esc(s["url"])}">{esc(s["title"])}</a>')
    return ', '.join(out)

def source_card(page:Path,loc:str,s,heading=2):
    L=locales[loc]; S=L['source_meta']
    immutable=s.get('reference_type')=='immutable-git-commit'
    ref_label=S['immutable'] if immutable else S['mutable']
    version=(f'<span><strong>{esc(S["version"])}:</strong> <code>{esc(s["version"][:12])}</code></span>' if s.get('version') else '')
    claims='; '.join(source_i18n[loc].get(s['id'],{}).get('claims_supported',s.get('claims_supported',[])))
    return f'''<article class="source-record"><div class="source-record-top"><span class="signal-dot" aria-hidden="true"></span><span class="micro">{esc(S['record'])}</span><span class="source-ref-type">{esc(ref_label)}</span></div><h{heading} lang="en" dir="ltr"><a href="{esc(s['url'])}">{esc(s['title'])}</a></h{heading}><p><strong>{esc(L['sources']['publisher'])}:</strong> {esc(s['publisher'])}</p><p lang="en" dir="ltr"><strong>{esc(L['sources']['supports'])}:</strong> {esc(claims)}</p><div class="source-record-meta"><span><strong>{esc(S['retrieved'])}:</strong> {esc(s.get('retrieved_at',';'))}</span>{version}</div></article>'''

def alternates(page:Path,kind:str,slug=None):
    bits=[]
    for loc in project['locales']:
        href=rel(page,logical_target(loc,kind,slug))
        bits.append(f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(href)}">')
    bits.append(f'<link rel="alternate" hreflang="x-default" href="{esc(rel(page,"index.html"))}">')
    return '\n'.join(bits)

def brand(page,loc):
    return f'''<a class="brand" href="{esc(rel(page,logical_target(loc,'home')))}"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 40 40" focusable="false"><path d="M5 21c5-12 20-16 29-6"/><path d="M7 28c9 6 22 3 27-7"/><path d="M12 13c7-3 17-1 21 6"/><circle cx="20" cy="21" r="2.5"/></svg></span><span class="brand-lockup"><strong>Navier–Stokes</strong><small>Commons</small></span></a>'''

def lang_switch(page:Path,loc:str,kind:str,slug=None):
    L=locales[loc]
    items=[]
    for x in project['locales']:
        if x!=loc and not (PUBLIC/logical_target(x,kind,slug)).exists():
            continue
        lx=locales[x]
        current=' aria-current="true"' if x==loc else ''
        target=rel(page,logical_target(x,kind,slug))
        items.append(f'<a lang="{esc(x)}" dir="{esc(lx["dir"])}" href="{esc(target)}"{current}>{esc(lx["name"])}</a>')
    return f'''<details class="language-switcher"><summary><span aria-hidden="true">◎</span><span>{esc(L['language'])}</span></summary><div class="language-menu">{''.join(items)}</div></details>'''

def nav(page:Path,loc:str,current:str,kind:str,slug=None):
    L=locales[loc]
    links=[
        ('missions',L['nav']['missions'],'missions'),
        ('guide',L['nav'].get('guide','Guide'),'guide'),
        ('activity',L['nav'].get('activity','Contributions'),'activity'),
        ('contribute',L['nav']['contribute'],'contribute'),
        ('sources',L['nav']['sources'],'sources'),
        ('agents',L['nav']['agents'],'agents'),
    ]
    if loc=='en': links.insert(0,('math','Mathematics','math'))
    n=[]
    for key,label,target_kind in links:
        aria=' aria-current="page"' if current==key else ''
        n.append(f'<a class="nav-link" href="{esc(rel(page,logical_target(loc,target_kind)))}"{aria}>{esc(label)}</a>')
    n.insert(1,f'<a class="nav-link" lang="en" dir="ltr" href="{esc(rel(page,"en/quests/index.html"))}">Research problems</a>')
    theme=f'<button class="theme-toggle enhance-only" type="button" data-theme-toggle data-label-system="{esc(L["system"])}" data-label-light="{esc(L["light"])}" data-label-dark="{esc(L["dark"])}" hidden aria-label="{esc(L["theme"])}"><span class="theme-glyph" aria-hidden="true">◐</span><span data-theme-label>{esc(L["system"])}</span></button>'
    items=''.join(n)+theme+lang_switch(page,loc,kind,slug)
    # Two responsive projections from the same generated navigation model. CSS exposes exactly one.
    mobile_items=''.join(n)+theme+lang_switch(page,loc,kind,slug)
    return f'''<header class="site-header"><div class="container header-row">{brand(page,loc)}<nav class="nav-wrap nav-desktop" aria-label="{esc(L['menu'])}">{items}</nav><details class="mobile-nav"><summary>{esc(L['menu'])}</summary><nav class="nav-wrap nav-mobile-panel" aria-label="{esc(L['menu'])}">{mobile_items}</nav></details></div></header>'''

def footer(page,loc):
    L=locales[loc]
    lic_attrs=canonical_english_attrs(loc)
    return f'''<footer class="site-footer"><div class="container footer-grid"><div>{brand(page,loc)}<p>{esc(L['tagline'])}</p></div><div><strong>{esc(L['footer']['public'])}</strong><p>{esc(L['footer']['privacy'])}</p></div><div><a href="{esc(rel(page,logical_target(loc,'accessibility')))}">{esc(L['nav']['accessibility'])}</a><p{lic_attrs}>{esc(localized_license_line(loc,L))}</p></div></div></footer>'''

def shell(page:Path,loc:str,current:str,kind:str,title:str,description:str,body:str,slug=None, extra_head='', overrides_alternates=False):
    L=locales[loc]; direction=L['dir']
    asset_css=rel(page,'assets/style.css'); asset_js=rel(page,'assets/site.js')
    alt='' if overrides_alternates else alternates(page,kind,slug)
    canonical=''
    if SITE_URL:
        relurl=logical_target(loc,kind,slug).replace('index.html','')
        canonical=f'<link rel="canonical" href="{esc(SITE_URL+"/"+relurl)}">'
    return f'''<!doctype html>
<html lang="{esc(loc)}" dir="{esc(direction)}" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · Navier–Stokes Commons</title>
<meta name="description" content="{esc(description)}">
{SECURITY_META}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#071d20" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f4f7f4" media="(prefers-color-scheme: light)">
{canonical}
{alt}
<link rel="describedby" href="{esc(rel(page,"llms.txt"))}" type="text/markdown"><link rel="stylesheet" href="{esc(asset_css)}">
{extra_head}
</head>
<body data-page-kind="{esc(kind)}">
<a class="skip-link" href="#main">{esc(L['skip'])}</a>
{nav(page,loc,current,kind,slug)}
{locale_preview_notice(loc)}
<main id="main">{body}</main>
{footer(page,loc)}
<script src="{esc(asset_js)}" defer></script>
</body></html>'''

def write(path:str,text:str):
    p=PUBLIC/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')

def mission_text(loc,m):
    tr=mi18n[loc].get(m['id'],{})
    return {k:tr.get(k,m[k]) for k in ('title','summary','question')}

def formula_value(qid,tau,h):
    q=next(q for q in scaling['quantities'] if q['id']==qid)
    e=q['exponent']['constant']+q['exponent']['h']*h
    return tau**e

def ascii_core_frame(tau,h,width=23,height=11):
    aspect=formula_value('aspect',tau,h)
    inner_w=max(3,min(width-4,int(round((width-4)/(aspect**0.5)))))
    inner_h=max(3,min(height-2,int(round((height-2)*(aspect**0.5)))))
    if inner_h%2==0: inner_h-=1
    if inner_w%2==0: inner_w-=1
    canvas=[[' ']*width for _ in range(height)]
    cx,cy=width//2,height//2
    rx=max(1,inner_w//2); ry=max(1,inner_h//2)
    for y in range(height):
        for x in range(width):
            dx=(x-cx)/rx; dy=(y-cy)/ry
            v=dx*dx+dy*dy
            if 0.72 <= v <= 1.35: canvas[y][x]='#'
            elif v<0.72 and (x==cx or y==cy): canvas[y][x]='+'
    art='\n'.join(''.join(row).rstrip() for row in canvas)
    def exp_line(qid,symbol):
        value=formula_value(qid,tau,h)
        logv=math.log10(value) if value > 0 else 0
        arrow='>' if logv >= 0 else '<'
        bar=arrow*max(1,min(22,int(round(abs(logv)/2)))) if abs(logv) >= 0.2 else '.'
        return f'{symbol:<10} 10^{logv:>7.2f}  {bar}'
    return art+'\n\n'+\
        exp_line('ell_r','ell_r')+'\n'+\
        exp_line('ell_z','ell_z')+'\n'+\
        exp_line('u_theta','|u_theta|')+'\n'+\
        exp_line('energy','E_core')+'\n'+\
        exp_line('re_theta','Re_theta')

def curve_path_server(qid,h):
    q=next(q for q in scaling['quantities'] if q['id']==qid)
    e=q['exponent']['constant'] + q['exponent']['h']*h
    pts=[]
    for k in range(0,81,2):
        logv=-k*e
        x=48+(k/80)*452
        y=max(20,min(216,118-logv*2.25))
        pts.append(f'{"L" if k else "M"}{x:.1f} {y:.1f}')
    return ' '.join(pts)

def formula_tex(node):
    typ=node['type']
    if typ=='row': return ' '.join(formula_tex(x) for x in node['children']).replace(' ,',',')
    if typ=='identifier': return {'ν':r'\nu'}.get(node['value'],node['value'])
    if typ=='number': return node['value']
    if typ=='operator': return {'∂':r'\partial','·':r'\cdot','∇':r'\nabla','Δ':r'\Delta','−':'-'}.get(node['value'],node['value'])
    if typ=='subscript': return f"{formula_tex(node['base'])}_{{{formula_tex(node['sub'])}}}"
    if typ=='group': return r'\left(' + ' '.join(formula_tex(x) for x in node['children']) + r'\right)'
    if typ=='space': return r'\qquad'
    raise ValueError(f'unsupported formula node type {typ}')

def formula_mathml(node):
    typ=node['type']
    if typ=='row': return '<mrow>'+''.join(formula_mathml(x) for x in node['children'])+'</mrow>'
    if typ=='identifier': return f'<mi>{esc(node["value"])}</mi>'
    if typ=='number': return f'<mn>{esc(node["value"])}</mn>'
    if typ=='operator': return f'<mo>{esc(node["value"])}</mo>'
    if typ=='subscript': return '<msub>'+formula_mathml(node['base'])+formula_mathml(node['sub'])+'</msub>'
    if typ=='group': return '<mrow><mo>(</mo>'+''.join(formula_mathml(x) for x in node['children'])+'<mo>)</mo></mrow>'
    if typ=='space': return f'<mspace width="{float(node.get("em",1)):.1f}em"/>'
    raise ValueError(f'unsupported formula node type {typ}')

def formula_speech(node):
    typ=node['type']
    if typ=='row': return ' '.join(x for x in (formula_speech(c) for c in node['children']) if x)
    if typ=='identifier': return {'ν':'nu','u':'u','p':'p','f':'f','t':'t'}.get(node['value'],node['value'])
    if typ=='number': return node['value']
    if typ=='operator': return {'∂':'partial','·':'dot','∇':'grad','Δ':'laplacian','−':'minus','+':'plus','=':'equals',',':''}.get(node['value'],node['value'])
    if typ=='subscript': return formula_speech(node['base'])+' '+formula_speech(node['sub'])
    if typ=='group': return formula_speech({'type':'row','children':node['children']})
    if typ=='space': return ''
    raise ValueError(f'unsupported formula node type {typ}')

def equation_block():
    formula=formula_by_id['incompressible-navier-stokes-forced']
    ast=formula['ast']
    tex=formula_tex(ast)
    mathml=formula_mathml(ast)
    speech=formula_speech(ast)
    return f'''<div class="equation-line equation-object" data-formula-id="{esc(formula['id'])}" data-equation-tex="{esc(tex)}"><math display="block" aria-label="{esc(speech)}"><semantics>{mathml}<annotation encoding="application/x-tex">{esc(tex)}</annotation></semantics></math></div>'''
def scaling_lab(page,loc):
    O=locales[loc]['observatory']
    h=float(scaling['parameters']['h']['default'])
    default_k=40.0
    default_tau=10**(-default_k)
    frames=[]
    for k in (2,20,60):
        tau=10**(-k)
        frame=ascii_core_frame(tau,h)
        frames.append(f'''<div class="ascii-frame"><div class="ascii-head">tau = 10^-{k}</div><pre aria-label="{esc(O['core_aspect'])}, tau 10^-{k}">{esc(frame)}</pre></div>''')
    symbol={'ell_r':'ell_r','ell_z':'ell_z','u_theta':'|u_theta|','energy':'E_core','re_theta':'Re_theta'}
    vals=[]
    for qid in ('ell_r','ell_z','u_theta','energy','re_theta'):
        q=next(q for q in scaling['quantities'] if q['id']==qid)
        value=formula_value(qid,default_tau,h)
        logv=math.log10(value) if value > 0 else 0
        display='1' if abs(logv) < 0.005 else f'10^{logv:.2f}'
        vals.append(f'''<tr><th scope="row"><code>{esc(symbol[qid])}</code></th><td><code>{esc(q['relation'])} {esc(q['formula'])}</code></td><td data-scale-value="{esc(qid)}">{esc(display)}</td></tr>''')
    source=source_by_id.get('openai-paper')
    src=f'<a href="{esc(source["url"])}">{esc(O["paper_section"])}</a>' if source else esc(O['paper_section'])
    default_aspect=formula_value('aspect',default_tau,h)
    default_speed=math.log10(formula_value('u_theta',default_tau,h))
    default_energy=math.log10(formula_value('energy',default_tau,h))
    dirv=locales[loc].get('dir','ltr')
    coeffs={q['id']:[q['exponent']['constant'],q['exponent']['h']] for q in scaling['quantities']}
    coeff_json=json.dumps(coeffs,separators=(',',':'))
    return f'''<section class="scaling-lab" data-scaling-lab data-source="openai-paper" data-exponents="{esc(coeff_json)}" lang="{esc(loc)}" dir="{esc(dirv)}"><div class="lab-copy"><span class="micro">{esc(O['scale_kicker'])}</span><h2>{esc(O['scale_title'])}</h2><p>{esc(O['scale_body'])}</p><p class="source-line">{src}</p>{equation_block()}<div class="lab-controls enhance-only" data-lab-controls hidden><label>{esc(O['time_decades'])} <output data-k-output>{default_k:.0f}</output><input type="range" min="0.25" max="80" value="{default_k:.0f}" step="0.25" data-tau-k aria-label="{esc(O['time_decades'])}"></label><label>{esc(O['h_param'])} <output data-h-output>{h:.4f}</output><input type="range" min="0.0005" max="0.0095" value="{h}" step="0.0001" data-h aria-label="{esc(O['h_param'])}"></label><button type="button" data-lab-play data-play-label="{esc(O['play'])}" data-pause-label="{esc(O['pause'])}">{esc(O['play'])}</button></div></div><div class="lab-stage"><div class="core-viz" aria-labelledby="core-viz-title"><h3 id="core-viz-title">{esc(O['core_aspect'])}</h3><svg viewBox="0 0 420 340" role="img" aria-labelledby="core-svg-title core-svg-desc"><title id="core-svg-title">{esc(O['core_aspect'])}</title><desc id="core-svg-desc">{esc(O['table_caption'])}</desc><line x1="210" y1="24" x2="210" y2="316" class="core-axis"/><line x1="54" y1="170" x2="366" y2="170" class="core-axis"/><ellipse cx="210" cy="170" rx="{92/math.sqrt(default_aspect):.2f}" ry="{min(138,92*math.sqrt(default_aspect)):.2f}" class="core-ellipse" data-core-ellipse/><circle cx="210" cy="170" r="5" class="core-origin"/></svg><div class="core-meters"><div><span>tau</span><strong data-tau-output>10^-{default_k:.0f}</strong></div><div><span>ell_z / ell_r</span><strong data-aspect-output>{default_aspect:.2f}</strong></div><div><span>{esc(O['speed'])}</span><strong data-speed-output>10^{default_speed:.2f}</strong></div><div><span>{esc(O['energy'])}</span><strong data-energy-output>10^{default_energy:.2f}</strong></div></div></div><div class="lab-plot"><h3>{esc(O['log_trajectories'])}</h3><svg viewBox="0 0 520 250" role="img" aria-labelledby="plot-title plot-desc"><title id="plot-title">{esc(O['log_trajectories'])}</title><desc id="plot-desc">{esc(O['table_caption'])}</desc><line x1="48" y1="20" x2="48" y2="216" class="plot-axis"/><line x1="48" y1="216" x2="500" y2="216" class="plot-axis"/><path data-curve="ell_r" class="curve curve-r" d="{curve_path_server('ell_r',h)}"/><path data-curve="ell_z" class="curve curve-z" d="{curve_path_server('ell_z',h)}"/><path data-curve="u_theta" class="curve curve-u" d="{curve_path_server('u_theta',h)}"/><path data-curve="energy" class="curve curve-e" d="{curve_path_server('energy',h)}"/><line data-cursor x1="274" y1="20" x2="274" y2="216" class="plot-cursor"/><g class="plot-key"><text x="60" y="36">{esc(O['radial'])}</text><text x="170" y="36">{esc(O['axial'])}</text><text x="290" y="36">{esc(O['speed'])}</text><text x="390" y="36">{esc(O['energy'])}</text></g></svg></div></div><div class="lab-fallback"><div class="ascii-live"><span class="micro">ASCII SCALE TRACE</span><pre data-ascii-live>{esc(ascii_core_frame(default_tau,h))}</pre></div><div class="ascii-sequence">{''.join(frames)}</div><table class="scaling-table"><caption>{esc(O['table_caption'])}</caption><thead><tr><th>{esc(O['quantity'])}</th><th>{esc(O['published_scaling'])}</th><th>{esc(O['normalized_value'])}</th></tr></thead><tbody>{''.join(vals)}</tbody></table></div></section>'''
def sim_expr_eval(node, variables, parameters):
    typ=node['type']
    if typ=='number': return float(node['value'])
    if typ=='param': return float(parameters[node['name']])
    if typ=='var': return float(variables[node['name']])
    if typ!='op': raise ValueError('unsupported simulation expression node '+str(typ))
    name=node['op']; args=[sim_expr_eval(a,variables,parameters) for a in node.get('args',[])]
    if name=='add': return sum(args)
    if name=='mul': return math.prod(args)
    if name=='neg': return -args[0]
    if name=='exp': return math.exp(args[0])
    if name=='sin': return math.sin(args[0])
    if name=='cos': return math.cos(args[0])
    if name=='pow': return args[0]**args[1]
    raise ValueError('unsupported simulation expression op '+str(name))

def sim_expr_text(node):
    typ=node['type']
    if typ=='number': return str(node['value'])
    if typ in {'param','var'}: return node['name']
    name=node['op']; a=node.get('args',[])
    if name=='add': return '('+' + '.join(sim_expr_text(z) for z in a)+')'
    if name=='mul': return ' '.join(sim_expr_text(z) for z in a)
    if name=='neg': return '-('+sim_expr_text(a[0])+')'
    if name in {'exp','sin','cos'}: return name+'('+sim_expr_text(a[0])+')'
    if name=='pow': return '('+sim_expr_text(a[0])+')^('+sim_expr_text(a[1])+')'
    raise ValueError('unsupported simulation expression op '+str(name))

def flow_velocity(sim,x,y,t,A,nu):
    env={'x':x,'y':y,'t':t}; pars={'A':A,'nu':nu}; f=sim['fields']
    return sim_expr_eval(f['u_x'],env,pars),sim_expr_eval(f['u_y'],env,pars)

def flow_ascii(sim,t=0.0,A=1.0,nu=0.035,nx=21,ny=11):
    glyphs=['→','↗','↑','↖','←','↙','↓','↘']; rows=[]
    for j in range(ny):
        y=2*math.pi*j/(ny-1); row=[]
        for i in range(nx):
            x=2*math.pi*i/(nx-1); u,v=flow_velocity(sim,x,y,t,A,nu); mag=math.hypot(u,v)
            if mag<0.04*max(A,1e-12): row.append('·'); continue
            ang=(math.atan2(-v,u)%(2*math.pi)); row.append(glyphs[int(round(ang/(math.pi/4)))%8])
        rows.append(''.join(row))
    return '\n'.join(rows)

def flow_chamber(page,loc):
    if loc!='en': return ''
    sim=simulations_doc['simulations'][0]; params=sim['parameters']; A=params['A']['default']; nu=params['nu']['default']; t=params['t']['default']
    env={'x':0.0,'y':0.0,'t':t}; pars={'A':A,'nu':nu}; energy=sim_expr_eval(sim['fields']['mean_kinetic_energy'],env,pars)
    source=source_by_id[sim['source_ids'][0]]; fallback=flow_ascii(sim,t,A,nu); model_json=json.dumps(sim['fields'],separators=(',',':'))
    ux=sim_expr_text(sim['fields']['u_x']); uy=sim_expr_text(sim['fields']['u_y']); ee=sim_expr_text(sim['fields']['mean_kinetic_energy'])
    return f'''<section id="flow-chamber" class="section flow-chamber-section" lang="en" dir="ltr"><div class="container flow-chamber" data-flow-chamber data-simulation-id="{esc(sim['id'])}" data-flow-model="{esc(model_json)}" data-a="{A}" data-nu="{nu}" data-t="{t}"><div class="flow-copy"><span class="eyebrow">EXACT REFERENCE FLOW</span><h2>Watch an equation become a velocity field.</h2><p class="lede small">This chamber is an analytic two-dimensional periodic Navier-Stokes solution, rendered directly from its canonical expression tree. It is a reference flow, not a reconstruction of the 2026 three-dimensional singularity.</p><p class="flow-tracer-note" data-flow-tracer-note>The arrow field and reported energy are exact evaluations of the canonical solution. Animated dots, when enabled, are numerically integrated passive tracers for orientation only and are not proof data.</p><p class="source-line"><a href="{esc(source['url'])}">{esc(source['title'])}</a></p><div class="flow-formulas"><code>u_x = {esc(ux)}</code><code>u_y = {esc(uy)}</code><code>E_mean = {esc(ee)}</code></div><div class="flow-controls enhance-only" data-flow-controls hidden><label for="flow-time">Time <output data-flow-t-output>{t:.2f}</output><input id="flow-time" type="range" min="{params['t']['min']}" max="{params['t']['max']}" value="{t}" step="{params['t']['step']}" data-flow-t></label><label for="flow-nu">Viscosity nu <output data-flow-nu-output>{nu:.3f}</output><input id="flow-nu" type="range" min="{params['nu']['min']}" max="{params['nu']['max']}" value="{nu}" step="{params['nu']['step']}" data-flow-nu></label><button type="button" data-flow-play data-play-label="Play" data-pause-label="Pause">Play</button></div><p class="flow-state" data-flow-state aria-live="polite">At t={t:.2f}, nu={nu:.3f}, the mean kinetic energy is {energy:.4f}. The field has {esc(sim['qualitative_default'])}; {esc(sim['invariants'][0])}.</p></div><div class="flow-visual"><div class="flow-canvas-frame enhance-only" data-flow-canvas-frame hidden><canvas width="720" height="460" data-flow-canvas aria-hidden="true"></canvas><div class="flow-axis-label x">x from 0 to 2pi</div><div class="flow-axis-label y">y</div></div><figure class="flow-static"><figcaption>Static no-JavaScript velocity-direction field at the default state</figcaption><pre data-flow-static>{esc(fallback)}</pre></figure></div></div><div class="container flow-integrity"><span>Canonical expression AST</span><span>Periodic domain</span><span>No autoplay</span><span>Static fallback</span><span>Independent residual oracle</span></div></section>'''

def _mechanism_copy(loc:str):
    copies={
      'en':{
        'boundary_kicker':'THE BOUNDARY THAT MATTERS',
        'boundary_title':'A forced finite-time blowup is claimed. The unforced problem remains distinct.',
        'cd':'OpenAI reports a smooth forcing for which velocity becomes unbounded while kinetic energy remains bounded.',
        'ab':'The corresponding unforced alternatives are logically distinct and remain a separate frontier.',
        'status':'SOURCE-REPORTED · INDEPENDENT REVIEW OPEN',
        'trace':'LIVE SCALE TRACE','trace_pause':'pause','trace_play':'play','trace_replay':'replay',
        'kicker':'PHYSICAL DESCRIPTION · PAPER §§2–2.2',
        'title':'One construction. Four different jobs.',
        'intro':'This explorable separates the mechanism instead of turning it into one decorative vortex. The first three panels summarize the inner-core geometry and leading scales. The fourth shows why the annular oscillations are necessary. It is an explanatory schematic tied to the paper, not a numerical reconstruction of the full solution.',
        'approach':'Approach the singular time','decades':'decades','h':'Scale parameter h','play':'Play scale sweep','pause':'Pause sweep','replay':'Replay scale sweep','motion_disabled':'Motion disabled',
        'p1k':'01 · TOP VIEW','p1t':'Inward spiral','p1b':'Radial inflow carries angular momentum toward smaller radii. The trajectories are qualitative guide curves; the changing envelope uses the published radial scale.',
        'p2k':'02 · SIDE VIEW','p2t':'Axial escape','p2b':'Incoming fluid cannot accumulate near the axis. Opposite axial outflow above and below the dividing layer permits continued inward motion and spin-up.','inflow':'inflow','outflow':'outflow',
        'p3k':'03 · LEADING SCALES','p3t':'Shrink and diverge','p3b':'Radius contracts, characteristic angular speed diverges, and the core energy scale still tends to zero for 0 < h < 1/100. Anisotropy is shown directly as ell_z / ell_r.',
        'p4k':'04 · ANNULUS','p4t':'Cancel the singular residual','p4b':'The background core alone leaves an unbounded residual in the annulus. Two localized oscillatory pulse families are arranged so their averaged quadratic momentum flux supplies the missing leading stress.','annulus':'ANNULUS','core':'CORE',
        'laws':'Published leading-order inner-core scaling relations represented by this explorable.',
        'scope':'Representation status','scope_text':'Panels 1, 2 and 4 are explanatory schematics. Panel 3 and the numeric readouts are derived directly from the recorded leading exponents. None is a full-field reconstruction.',
        'reference':'Open the independently checkable exact 2-D reference flow',
        'steps':[
          ('01 TRANSPORT','Spin-up is a balance.','Inward angular-momentum transport competes with viscous loss; it is not a frictionless conservation cartoon.'),
          ('02 INCOMPRESSIBILITY','The core cannot simply implode.','Axial outflow carries mass away from the concentrating central region.'),
          ('03 CONCENTRATION','Large speed does not imply large total energy.','The support volume collapses fast enough that the core energy scale tends to zero.'),
          ('04 CORRECTION','The pulses are not decoration.','They are the device used to cancel the singular annular momentum residual while keeping the external forcing smooth.'),
        ],
      },
      'es':{
        'boundary_kicker':'EL LÍMITE QUE IMPORTA',
        'boundary_title':'Se afirma blowup forzado en tiempo finito. El problema sin fuerza sigue siendo distinto.',
        'cd':'OpenAI informa una fuerza suave para la cual la velocidad se hace no acotada mientras la energía cinética permanece acotada.',
        'ab':'Las alternativas correspondientes sin fuerza son lógicamente distintas y siguen siendo una frontera separada.',
        'status':'INFORMADO POR LA FUENTE · REVISIÓN INDEPENDIENTE ABIERTA',
        'trace':'TRAZA DE ESCALA EN VIVO','trace_pause':'pausar','trace_play':'reproducir','trace_replay':'repetir',
        'kicker':'DESCRIPCIÓN FÍSICA · ARTÍCULO §§2–2.2',
        'title':'Una construcción. Cuatro trabajos distintos.',
        'intro':'Este explorable separa el mecanismo en vez de convertirlo en un único vórtice decorativo. Los tres primeros paneles resumen la geometría del núcleo interior y sus escalas principales. El cuarto muestra por qué hacen falta las oscilaciones del anillo. Es un esquema explicativo vinculado al artículo, no una reconstrucción numérica de la solución completa.',
        'approach':'Acercarse al instante singular','decades':'décadas','h':'Parámetro de escala h','play':'Reproducir barrido','pause':'Pausar barrido','replay':'Repetir barrido','motion_disabled':'Movimiento desactivado',
        'p1k':'01 · VISTA SUPERIOR','p1t':'Espiral hacia adentro','p1b':'La entrada radial transporta momento angular hacia radios menores. Las trayectorias son curvas guía cualitativas; la envolvente cambiante usa la escala radial publicada.',
        'p2k':'02 · VISTA LATERAL','p2t':'Escape axial','p2b':'El fluido entrante no puede acumularse cerca del eje. La salida axial en sentidos opuestos por encima y por debajo de la capa divisoria permite que continúen la entrada y la aceleración del giro.','inflow':'entrada','outflow':'salida',
        'p3k':'03 · ESCALAS PRINCIPALES','p3t':'Contraerse y divergir','p3b':'El radio se contrae, la velocidad angular característica diverge y la escala de energía del núcleo sigue tendiendo a cero para 0 < h < 1/100. La anisotropía se muestra directamente como ell_z / ell_r.',
        'p4k':'04 · ANILLO','p4t':'Cancelar el residuo singular','p4b':'El núcleo de fondo por sí solo deja un residuo no acotado en el anillo. Se disponen dos familias de pulsos oscilatorios localizados para que su flujo cuadrático medio de momento aporte el esfuerzo principal faltante.','annulus':'ANILLO','core':'NÚCLEO',
        'laws':'Relaciones de escala principales publicadas para el núcleo interior representadas por este explorable.',
        'scope':'Estado de la representación','scope_text':'Los paneles 1, 2 y 4 son esquemas explicativos. El panel 3 y las lecturas numéricas se derivan directamente de los exponentes principales registrados. Ninguno reconstruye el campo completo.',
        'reference':'Abrir el flujo de referencia 2-D exacto e independientemente verificable',
        'steps':[
          ('01 TRANSPORTE','La aceleración del giro es un balance.','El transporte de momento angular hacia adentro compite con la pérdida viscosa; no es una caricatura sin fricción.'),
          ('02 INCOMPRESIBILIDAD','El núcleo no puede simplemente implosionar.','La salida axial aleja masa de la región central que se concentra.'),
          ('03 CONCENTRACIÓN','Gran velocidad no implica gran energía total.','El volumen de soporte colapsa suficientemente rápido para que la escala de energía del núcleo tienda a cero.'),
          ('04 CORRECCIÓN','Los pulsos no son decoración.','Son el dispositivo usado para cancelar el residuo singular de momento en el anillo manteniendo suave el forzamiento externo.'),
        ],
      },
    }
    return copies.get(loc,copies['en']), ('' if loc in copies else ' lang="en" dir="ltr"')


def scale_trace(loc:str='en')->str:
    C,attrs=_mechanism_copy(loc)
    return f'''<section class="scale-trace-strip" data-scale-trace{attrs}><div class="container scale-trace-row"><span class="micro">{esc(C['trace'])}</span><pre data-scale-trace-output>τ 10^-2.00   ℓr 10^-1.00   ℓz 10^-0.99   |uθ| 10^1.01   Ecore 10^-0.97</pre><button class="enhance-only" type="button" data-scale-trace-toggle hidden data-pause="{esc(C['trace_pause'])}" data-play="{esc(C['trace_play'])}" data-replay="{esc(C['trace_replay'])}">{esc(C['trace_pause'])}</button></div></section>'''


def reference_flow_page():
    page=PUBLIC/'en/reference-flow/index.html'
    body='''<section class="page-hero compact-hero"><div class="container narrow"><span class="eyebrow">EXACT REFERENCE FLOW · SEPARATE FROM THE 2026 BLOWUP</span><h1>One exact field for testing the visualization machinery.</h1><p class="lede">This two-dimensional periodic Taylor-vortex solution is independently checkable against the Navier–Stokes equations. It is retained as a reference implementation and is not a reconstruction of the 2026 three-dimensional singular construction.</p></div></section>'''+flow_chamber(page,'en')
    write('en/reference-flow/index.html',canonical_shell(page,'guide','reference-flow','Exact 2-D reference flow','An independently checkable exact Navier–Stokes field used to test scientific visualization machinery.',body))



def r5_font_preloads(page):
    """Preload only the two first-viewport Latin faces; mono remains demand-loaded."""
    news=rel(page,'assets/fonts/newsreader-latin-standard-normal.woff2')
    geist=rel(page,'assets/fonts/geist-latin-wght-normal.woff2')
    return (f'<link rel="preload" as="font" type="font/woff2" href="{esc(news)}" crossorigin>'
            f'<link rel="preload" as="font" type="font/woff2" href="{esc(geist)}" crossorigin>')

def _r5_copy(loc:str):
    copies={
      'en':{
        'title':'Navier–Stokes, made explorable.',
        'lede':'OpenAI published a finite-time blowup construction for the smoothly forced C/D formulation. Here the geometry, scale laws, proof artifacts and open questions become one manipulable research surface.',
        'sub':'The 3-D object is an explicitly schematic, source-constrained explainer. It does not claim to reconstruct the complete velocity field.',
        'explore':'Explore the mechanism','quest':'Pick a bounded quest',
        'stage':'SCHEMATIC 3-D CORE','normalized':'NORMALIZED FOLLOW-CORE VIEW','laboratory':'LOG-COMPRESSED LABORATORY VIEW',
        'help':'move = flow probe · drag = orbit · wheel = zoom',
        'boundary':'Geometry is an explanatory schematic, not the computed 3-D solution. Scale readouts are derived from the published leading-order laws. Here k means τ = 1 − t = 10⁻ᵏ: k=1 gives τ=10⁻¹, while k=60 gives τ=10⁻⁶⁰. Move the cursor to interrogate nearby guide trajectories; the probe does not perturb the model.',
        'k':'distance to singular time · k = −log₁₀(τ), τ = 1 − t','h':'scaling parameter h',
        'play':'Play sweep','pause':'Pause sweep','frame':'Normalized core frame','frame_lab':'Laboratory frame',
        'mechanism_kicker':'THE MECHANISM','mechanism_title':'Four coupled ideas.',
        'mechanism_intro':'Do not reduce the proof to a decorative tornado. The physical picture is a sequence: inward angular-momentum transport, axial escape imposed by incompressibility, anisotropic concentration with diverging characteristic speed, and annular oscillatory corrections that cancel the singular residual while the external force remains smooth.',
      },
      'es':{
        'title':'Navier–Stokes, para explorar.',
        'lede':'OpenAI publicó una construcción de blowup en tiempo finito para la formulación C/D con forzamiento suave. Aquí la geometría, las leyes de escala, los artefactos de prueba y las preguntas abiertas se convierten en una superficie de investigación manipulable.',
        'sub':'El objeto 3-D es un esquema explicativo restringido por las fuentes. No pretende reconstruir el campo de velocidades completo.',
        'explore':'Explorar el mecanismo','quest':'Elegir una quest acotada',
        'stage':'NÚCLEO 3-D ESQUEMÁTICO','normalized':'VISTA NORMALIZADA DEL NÚCLEO','laboratory':'VISTA DE LABORATORIO LOG-COMPRIMIDA',
        'help':'mover = sonda · arrastrar = orbitar · rueda = zoom',
        'boundary':'La geometría es un esquema explicativo, no la solución 3-D calculada. Las lecturas de escala se derivan de las leyes principales publicadas. Aquí k significa τ = 1 − t = 10⁻ᵏ: k=1 da τ=10⁻¹ y k=60 da τ=10⁻⁶⁰. Mueve el cursor para interrogar trayectorias guía cercanas; la sonda no perturba el modelo.',
        'k':'distancia al instante singular · k = −log₁₀(τ), τ = 1 − t','h':'parámetro de escala h',
        'play':'Reproducir barrido','pause':'Pausar barrido','frame':'Vista normalizada','frame_lab':'Vista de laboratorio',
        'mechanism_kicker':'EL MECANISMO','mechanism_title':'Cuatro ideas acopladas.',
        'mechanism_intro':'No reduzcas la prueba a un tornado decorativo. La imagen física es una secuencia: transporte de momento angular hacia adentro, escape axial impuesto por la incomprensibilidad, concentración anisotrópica con velocidad característica divergente y correcciones oscilatorias anulares que cancelan el residuo singular mientras la fuerza externa permanece suave.',
      }
    }
    if loc in copies: return copies[loc],''
    return copies['en'],' lang="en" dir="ltr"'


def r5_sprint_copy(loc:str):
    if loc=='es':
        return {'button':'Ver el portafolio de revisión inicial','kicker':'PORTAFOLIO INDEPENDIENTE DE REVISIÓN INICIAL','title':'No te limites a leerlo. Elige una quest acotada y mejora el registro público.','body':'El Commons está abierto a intentos no exclusivos. Empieza con verificación de fuentes, reproducción en Lean, matemáticas, trabajo numérico, accesibilidad, pruebas de navegador, evaluación de agentes o revisión de gobernanza.','all':f'Las {len(quests)} quests'},''
    if loc=='en':
        return {'button':'View the Initial Review Portfolio','kicker':'INDEPENDENT REVIEW PORTFOLIO','title':'Do not just read it. Pick one bounded quest and make the public record better.','body':'The Commons is open for non-exclusive attempts. Start with source checks, Lean reproduction, mathematics, numerical work, accessibility, browser testing, agent evaluation, or governance review.','all':f'All {len(quests)} quests'},''
    return {'button':'View the Initial Review Portfolio','kicker':'INDEPENDENT REVIEW PORTFOLIO','title':'Do not just read it. Pick one bounded quest and make the public record better.','body':'The Commons is open for non-exclusive attempts. Start with source checks, Lean reproduction, mathematics, numerical work, accessibility, browser testing, agent evaluation, or governance review.','all':f'All {len(quests)} quests'},' lang="en" dir="ltr"'

def _r5_static_vortex_svg()->str:
    def project(x,y,z,yaw=-.28,pitch=.10,zoom=5.8,w=1000,h=650):
        cy,sy=math.cos(yaw),math.sin(yaw); cp,sp=math.cos(pitch),math.sin(pitch)
        X=cy*x+sy*z; Z=-sy*x+cy*z; Y=cp*y-sp*Z; Z=sp*y+cp*Z
        d=zoom-Z; f=min(w,h)*.88/d
        return w*.5+X*f,h*.47-Y*f
    paths=[]; k=14.0; H=.005; s=k/60; turns=1.25+19*s**.72; aspect=10**(k*H); axial=1+.78*math.log10(aspect+1)
    for i in range(32):
        a=(i*2.3999632297)%(2*math.pi); layer=(i%19)/18; family=i%7; pts=[]
        for j in range(46):
            u=j/45; zz=u*2-1; waist=.32+.68*abs(zz)**.70; lay=.32+1.48*(.15+.85*layer); radial=lay*waist*(1-.30*s*math.exp(-zz*zz*3)); handed=1 if family<3 else -1
            th=a+handed*turns*(zz+.23*math.sin(zz*math.pi))*math.pi
            x=radial*math.cos(th); z=radial*math.sin(th); y=zz*2.3*axial
            flare=.15*math.sin(th*.7+math.sin(i*12.9898)*.17*8)*(1-math.exp(-abs(zz)*2)); x*=1+flare; z*=1-flare*.7
            pts.append(project(x,y,z))
        d=' '.join(('M' if j==0 else 'L')+f'{x:.1f},{y:.1f}' for j,(x,y) in enumerate(pts))
        cls='vortex-static-teal' if family<3 else ('vortex-static-orange' if family in (4,5) else 'vortex-static-blue')
        paths.append(f'<path d="{d}" class="{cls}"/>')
    return f'''<svg class="vortex-static" data-vortex-static viewBox="0 0 1000 650" role="img" aria-label="Static three-dimensional schematic of inward-spiraling and axially extended guide trajectories"><g>{''.join(paths)}</g><text x="28" y="620">STATIC NO-JAVASCRIPT SCHEMATIC · quantitative scale laws remain available below</text></svg>'''

def r5_vortex_stage(page:Path,loc:str)->str:
    C,attrs=_r5_copy(loc); h=float(scaling['parameters']['h']['default']); k=14.0
    lr=-.5*k; lz=-(.5-h)*k; speed=(.5+h)*k; energy=-(.5-3*h)*k; aspect=10**(h*k)
    return f'''<figure class="vortex-stage" data-vortex-stage data-representation-status="schematic" data-quantitative-status="derived-leading-exponents" data-mode-normalized="{esc(C['normalized'])}" data-mode-laboratory="{esc(C['laboratory'])}"{attrs}>{_r5_static_vortex_svg()}<canvas data-vortex-canvas aria-hidden="true"></canvas><div class="flow-probe" data-flow-probe aria-hidden="true"><span class="flow-probe-ring"></span><span class="flow-probe-tag">flow probe</span></div><div class="stage-note">{esc(C['stage'])} · <span data-mode-label>{esc(C['normalized'])}</span></div><div class="stage-help">{esc(C['help'])}</div><div class="visual-boundary">{esc(C['boundary'])}</div><div class="stage-hud"><div class="hud-stats" aria-label="Derived leading-order scale readouts"><div class="hud-stat"><span>τ = 10⁻ᵏ</span><b data-tau-out>10^-14</b></div><div class="hud-stat"><span>ℓr</span><b data-r-out>10^{lr:.1f}</b></div><div class="hud-stat"><span>ℓz</span><b data-z-out>10^{lz:.1f}</b></div><div class="hud-stat"><span>|uθ|</span><b data-u-out>10^{speed:.1f}</b></div><div class="hud-stat"><span>Ecore</span><b data-e-out>10^{energy:.1f}</b></div><div class="hud-stat"><span>ℓz / ℓr</span><b data-aspect-out>10^{math.log10(aspect):.2f}</b></div></div><div class="vortex-controls enhance-only" data-vortex-controls hidden><div class="controls"><label>{esc(C['k'])}<input data-k type="range" min=".5" max="60" value="14" step=".5" aria-label="{esc(C['k'])}"></label><label>{esc(C['h'])}<input data-h type="range" min=".0005" max=".0095" value="{h}" step=".0005" aria-label="{esc(C['h'])}"></label></div><div class="hud-buttons"><button type="button" data-play data-play-label="{esc(C['play'])}" data-pause-label="{esc(C['pause'])}" aria-pressed="false">{esc(C['play'])}</button><button type="button" data-frame-toggle data-normalized-label="{esc(C['frame'])}" data-lab-label="{esc(C['frame_lab'])}">{esc(C['frame'])}</button></div></div></div><figcaption class="vortex-caption">{esc(C['sub'])}</figcaption></figure>'''

def r5_claim_strip(page:Path,loc:str)->str:
    C0,attrs=_mechanism_copy(loc); src=source_links(['openai-announcement','clay-formulation'],page)
    return f'''<section class="truth-strip"{attrs}><div class="container truth-grid"><strong>{esc(C0['boundary_kicker'])}</strong><p>{esc(C0['cd'])} {esc(C0['ab'])}</p><span class="truth-source">{src}</span></div></section>'''

def r5_mechanism_section(page:Path,loc:str)->str:
    C,attrs=_r5_copy(loc); C0,_=_mechanism_copy(loc); source=source_by_id.get('openai-paper'); src=f'<a href="{esc(source["url"])}">{esc(source["title"])}</a>' if source else 'OpenAI 2026 paper'
    steps=''.join(f'<article class="mechanism-step"><span class="micro">{esc(k0)}</span><h3>{esc(t)}</h3><p>{esc(b)}</p></article>' for k0,t,b in C0['steps'])
    return f'''<section id="mechanism" class="section mechanism-explanation-section"{attrs}><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(C['mechanism_kicker'])}</span><h2>{esc(C['mechanism_title'])}</h2></div><div><p>{esc(C['mechanism_intro'])}</p><p class="source-line">{src}</p></div></div><div class="r5-equation-anchor"><span class="micro">CANONICAL EQUATION OBJECT</span>{equation_block()}</div><div class="mechanism-steps">{steps}</div></div></section>'''

def _r6_entry_copy(loc:str):
    copies={
      'en':{
        'kicker':'CHOOSE YOUR WAY IN','title':'You do not need to believe the announcement to contribute.',
        'intro':'Pick the smallest public task that matches your competence. Every route has an explicit evidence contract; negative results and corrections count when they close uncertainty.',
        'routes':[
          ('PDE / analysis','Interrogate the mathematical claim, assumptions, scaling arguments, and open analytical consequences.','claims','Inspect claims'),
          ('Lean / formal methods','Rebuild, audit axioms, check theorem correspondence, or make a formal artifact easier to understand.','quests','Find formal-verification work'),
          ('Numerics / CFD / sciviz','Test numerical consequences, V&V assumptions, or the honesty and usefulness of scientific visualizations.','missions','Open computational-research programs'),
          ('Student / newcomer','Start with a bounded source, reproduction, browser, accessibility, or explanation task before attempting frontier mathematics.','sprint','Start with a bounded review problem'),
          ('Skeptic / reviewer','Audit the claim, lineage, attribution, provenance accounts, governance, or the Commons itself. Falsification is welcome.','context','Context / credit'),
          ('AI agent / tool builder','Use the machine endpoints, choose one bounded research problem, disclose model/tool provenance, and return an inspectable artifact.','agents','Open the agent interface'),
        ]
      },
      'es':{
        'kicker':'ELIGE CÓMO ENTRAR','title':'No tienes que creer el anuncio para contribuir.',
        'intro':'Elige la tarea pública más pequeña que encaje con tu competencia. Cada ruta tiene un contrato explícito de evidencia; los resultados negativos y las correcciones cuentan cuando reducen incertidumbre.',
        'routes':[
          ('EDP / análisis','Interroga la afirmación matemática, los supuestos, las escalas y las consecuencias analíticas abiertas.','claims','Inspeccionar afirmaciones'),
          ('Lean / métodos formales','Reproduce, audita axiomas, comprueba correspondencia de teoremas o mejora la legibilidad de un artefacto formal.','quests','Buscar trabajo formal'),
          ('Numérico / CFD / sciviz','Prueba consecuencias numéricas, supuestos de V&V o la honestidad de las visualizaciones científicas.','missions','Abrir misiones numéricas/sciviz'),
          ('Estudiante / recién llegado','Empieza por fuentes, reproducción, navegador, accesibilidad o explicación antes de intentar matemática de frontera.','sprint','Entrar al portafolio de revisión inicial'),
          ('Escéptico / revisor','Audita la afirmación, el linaje, la atribución, las versiones públicas de procedencia, la gobernanza o el propio Commons.','context','Leer contexto / crédito'),
          ('Agente de IA / herramientas','Usa los endpoints, elige una quest acotada, declara procedencia de modelo/herramienta y devuelve un artefacto inspeccionable.','agents','Abrir interfaz de agentes'),
        ]
      }
    }
    if loc in copies:return copies[loc],''
    return copies['en'],' lang="en" dir="ltr"'


def r6_community_entry_section(page:Path,loc:str)->str:
    C,attrs=_r6_entry_copy(loc)
    links={
      'claims':'en/claims/index.html',
      'quests':'en/quests/index.html',
      'missions':logical_target(loc,'missions'),
      'sprint':'en/sprint/index.html',
      'context':'en/context/index.html',
      'agents':logical_target(loc,'agents'),
    }
    cards=[]
    for i,(title,body,key,cta) in enumerate(C['routes'],1):
        href=rel(page,links[key])
        cards.append(f'''<article class="entry-route"><span class="micro">{i:02d}</span><h3>{esc(title)}</h3><p>{esc(body)}</p><a class="text-link strong" href="{esc(href)}">{esc(cta)} <span aria-hidden="true">↗</span></a></article>''')
    return f'''<section class="section community-entry-section"{attrs}><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(C['kicker'])}</span><h2>{esc(C['title'])}</h2></div><p>{esc(C['intro'])}</p></div><div class="entry-route-grid">{''.join(cards)}</div></div></section>'''


def r6_global_context_strip(page:Path)->str:
    href=rel(page,'en/context/index.html')
    return f'''<section class="r6-context-strip"><div class="container r6-context-row"><strong>INDEPENDENT COMMONS</strong><span>Not affiliated with OpenAI, Anthropic or Clay · source-reported C/D blowup · independent review open · unforced A/B remains distinct</span><a class="text-link strong" href="{esc(href)}">Context / credit <span aria-hidden="true">↗</span></a></div></section>'''


def r6_context_page():
    page=PUBLIC/'en/context/index.html'; ctx=research_context
    lineage=''.join(f'''<article class="context-record"><span class="micro">LINEAGE</span><h2>{esc(', '.join(x['people']))}</h2><p>{esc(x['note'])}</p><a class="text-link" href="{esc(x['url'])}">{esc(x['title'])} <span aria-hidden="true">↗</span></a></article>''' for x in ctx['lineage'])
    accounts=''.join(f'''<article class="context-record"><span class="micro">PUBLIC ACCOUNT · {esc(x['party'])}</span><h2>{esc(x['title'])}</h2><p>{esc(x['summary'])}</p><a class="text-link" href="{esc(x['url'])}">Read the attributed source <span aria-hidden="true">↗</span></a></article>''' for x in ctx['concurrent_accounts'])
    policy=''.join(f'<li>{esc(x)}</li>' for x in ctx['commons_policy'])
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">CONTEXT · CREDIT · PROVENANCE</span><h1>Keep the mathematics, verification, lineage, and dispute as separate records.</h1><p class="lede">This independent Commons is not affiliated with OpenAI, Anthropic, the Clay Mathematics Institute, or the cited researchers. It exists because the 2026 result arrived during a live argument about credit and research provenance. Public accounts are attributed; unresolved allegations are not turned into mathematical facts.</p></div><aside class="context-status"><span class="micro">CURRENT COMMONS STATUS</span><strong>Independent review open</strong><p>{esc(ctx['claim_status']['scope'])}</p><p>{esc(ctx['claim_status']['unforced_boundary'])}</p><p>{esc(ctx['claim_status']['institutional_acceptance'])}</p></aside></div></section><section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">RESEARCH LINEAGE</span><h2>Credit the route, not only the last artifact.</h2></div><p>The prior published program is relevant whether or not one accepts either side's account of the later concurrent-work dispute.</p></div><div class="context-grid">{lineage}</div></div></section><section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">CONCURRENT PUBLIC ACCOUNTS</span><h2>Link both accounts. Do not silently adjudicate.</h2></div><p>The accounts materially disagree. Readers should inspect the primary public statements directly.</p></div><div class="context-grid">{accounts}</div></div></section><section class="section"><div class="container split-layout"><div><span class="eyebrow">COMMONS POLICY</span><h2>Participation should improve the public record, not manufacture volume.</h2><ul class="plain-list">{policy}</ul></div><aside class="plain-aside"><h2>Review without endorsement</h2><p>You can contribute by disproving, reproducing, correcting, contextualizing, or narrowing a claim. Participation does not require endorsing OpenAI, Anthropic, AI-generated mathematics, or the theorem itself.</p><div class="actions"><a class="button" href="{esc(rel(page,'en/quests/index.html'))}">Find a review quest</a><a class="button secondary" href="{esc(rel(page,'en/sources/index.html'))}">Public sources</a></div></aside></div></section>'''
    write('en/context/index.html',canonical_shell(page,'guide','context','Context, credit, and provenance','Public research lineage, verification status, and attributed accounts surrounding the 2026 Navier-Stokes result.',body))

def science_visual(loc,compact=False):
    if not compact:
        return ''
    return f'''<figure class="equation-object compact"><div class="equation-kicker">INCOMPRESSIBLE NAVIER-STOKES</div>{equation_block()}<figcaption>Exact equation form used by this site's public model.</figcaption></figure>'''

def mission_card(page,loc,m,heading=3):
    L=locales[loc]; t=mission_text(loc,m)
    search=' '.join([t['title'],t['summary'],t['question'],m['category'],cat_label(loc,m['category']),m['level']]+[contrib_label(loc,x) for x in m['contributors']])
    href=rel(page,logical_target(loc,'mission',m['slug']))
    people=' · '.join(contrib_label(loc,x) for x in m['contributors'][:2])
    en_attrs=canonical_english_attrs(loc)
    return f'''<article class="mission-entry" data-mission-card data-category="{esc(m['category'])}" data-search="{esc(search)}" data-reveal><a class="mission-entry-link" href="{esc(href)}"><span class="mission-entry-id">{esc(m['id'])}</span><span class="mission-entry-main"{en_attrs}><span class="mission-entry-title">{esc(t['title'])}</span><span class="mission-entry-summary">{esc(t['summary'])}</span></span><span class="mission-entry-meta"{en_attrs}><span>{esc(cat_label(loc,m['category']))}</span><span>{esc(level_label(loc,m['level']))}</span><span>{esc(people)}</span></span><span class="mission-entry-arrow" aria-hidden="true">↗</span></a></article>'''

def canonical_shell(page:Path,current:str,kind:str,title:str,description:str,body:str):
    loc='en'; L=locales['en']; asset_css=rel(page,'assets/style.css'); asset_js=rel(page,'assets/site.js')
    links=[
      ('home','Home','en/index.html'),('missions','Missions','en/missions/index.html'),('quests','Quests','en/quests/index.html'),
      ('sprint','Initial Review Portfolio','en/sprint/index.html'),('activity','Contributions','en/activity/index.html'),
      ('contribute','Contribute','en/contribute/index.html'),('governance','Governance','en/governance/index.html'),('agents','For AI agents','en/agents/index.html')]
    navlinks=''.join(f'<a class="nav-link" href="{esc(rel(page,target))}"'+(' aria-current="page"' if current==key else '')+f'>{esc(label)}</a>' for key,label,target in links)
    root_href=rel(page,'index.html')
    canon_items=navlinks+f'<a class="nav-link" href="{esc(root_href)}">Languages</a>'
    header=f'''<header class="site-header"><div class="container header-row">{brand(page,'en')}<nav class="nav-wrap nav-desktop" aria-label="Main menu">{canon_items}</nav><details class="mobile-nav"><summary>Main menu</summary><nav class="nav-wrap nav-mobile-panel" aria-label="Main menu">{canon_items}</nav></details></div></header>'''
    canonical=''
    if SITE_URL:
        relurl=page.relative_to(PUBLIC).as_posix().replace('index.html','')
        canonical=f'<link rel="canonical" href="{esc(SITE_URL+"/"+relurl)}">'
    return f'''<!doctype html><html lang="en" dir="ltr" data-theme="system"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>{esc(title)} · Navier-Stokes Commons</title><meta name="description" content="{esc(description)}">{SECURITY_META}<meta name="color-scheme" content="light dark">{canonical}<link rel="describedby" href="{esc(rel(page,"llms.txt"))}" type="text/markdown"><link rel="stylesheet" href="{esc(asset_css)}"></head><body data-page-kind="{esc(kind)}"><a class="skip-link" href="#main">Skip to main content</a>{header}<main id="main">{body}</main>{footer(page,'en')}<script src="{esc(asset_js)}" defer></script></body></html>'''

def quest_issue_url(q):
    return repo_issue('claim_quest.yml',f'[Quest attempt] {q["id"]} {q["title"]}')

def quest_card(page,q,heading=3,compact=False):
    rung=rung_by_id[q['rung']]; href=rel(page,f'en/quests/{q["id"].lower()}/index.html')
    flags=[]
    if q.get('founding_sprint'): flags.append('Review Portfolio')
    if q.get('priority')=='launch': flags.append('launch priority')
    flag=' · '.join(flags)
    meta=f'''<span>{esc(q['rung'])} {esc(rung['name'])}</span><span>{esc(rung['effort'])}</span><span>{esc(q['review']['class'])}</span>'''
    extra=f'<span class="quest-flag">{esc(flag)}</span>' if flag else ''
    summary='' if compact else f'<p>{esc(q["summary"])}</p>'
    return f'''<article class="quest-card" data-quest-card data-rung="{esc(q['rung'])}" data-mission="{esc(q['mission_id'])}"><div class="quest-card-top"><code>{esc(q['id'])}</code>{extra}</div><h{heading}><a href="{esc(href)}">{esc(q['title'])}</a></h{heading}>{summary}<div class="quest-meta">{meta}</div></article>'''

def mission_quests(page,m):
    rows=[q for q in quests if q['mission_id']==m['id'] and q['status']=='open']
    if not rows: return '<p class="empty-record" lang="en" dir="ltr">No bounded quest is currently open for this mission.</p>'
    return '<div class="quest-grid" lang="en" dir="ltr">'+''.join(quest_card(page,q,heading=3,compact=True) for q in rows)+'</div>'

def quests_page():
    page=PUBLIC/'en/quests/index.html'; groups=[]
    for rung in task_ladder['rungs']:
        qs=[q for q in quests if q['status']=='open' and q['rung']==rung['id']]
        cards=''.join(quest_card(page,q) for q in qs)
        groups.append(f'''<section class="quest-rung" id="{esc(rung['id'].lower())}"><div class="quest-rung-head"><div><span class="eyebrow">{esc(rung['id'])} · {esc(rung['name'])}</span><h2>{esc(rung['effort'])}</h2><p>{esc(rung['scope'])}</p></div><p class="section-side-note">{len(qs)} open</p></div><div class="quest-grid">{cards}</div></section>''')
    sprint_href=rel(page,registry['human_routes']['founding_sprint'].lstrip('/'))
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">OPEN RESEARCH · {len(quests)} BOUNDED PROBLEMS</span><h1>Choose a problem whose result can survive review.</h1><p class="lede">Bounded research problems turn the {len(missions)} programs into independently checkable units, from a source verification to frontier mathematics. Attempts are non-exclusive.</p><div class="actions"><a class="button" href="{esc(sprint_href)}">Initial review portfolio</a><a class="button secondary" href="#l0">Browse from L0</a></div></div><aside class="plain-aside"><h2>Six-rung ladder</h2><p>Difficulty is an expected scope estimate, not a prestige score. Pick the smallest problem that genuinely advances its research program.</p><p><strong>Acceptance first:</strong> read the deliverables, acceptance checks, dependencies, and reviewer requirements before starting.</p></aside></div></section><section class="section"><div class="container">{''.join(groups)}</div></section>'''
    write('en/quests/index.html',canonical_shell(page,'quests','quests','Open research problems','Bounded public Navier–Stokes research problems for humans and agents.',body))

def quest_page(q):
    page=PUBLIC/f'en/quests/{q["id"].lower()}/index.html'; m=mission_by_id[q['mission_id']]; rung=rung_by_id[q['rung']]
    deliver=''.join(f'<li>{esc(x)}</li>' for x in q['deliverables']); accept=''.join(f'<li><span class="check-box" aria-hidden="true">□</span><span>{esc(x)}</span></li>' for x in q['acceptance'])
    deps=''.join(f'<li><a href="{esc(rel(page,f"en/quests/{d.lower()}/index.html"))}"><code>{esc(d)}</code> {esc(quest_by_id[d]["title"])}</a></li>' for d in q.get('dependencies',[])) or '<li>None.</li>'
    src=source_links(q['source_ids'],page) if q.get('source_ids') else 'No external source is required for the task as scoped.'
    claim_links=', '.join(f'<code>{esc(c)}</code>' for c in q.get('claim_ids',[])) or 'None directly.'
    benchmark_html=''
    if q.get('benchmark_set_id'):
        bhref=rel(page,registry['human_routes']['benchmarks'].lstrip('/')+'index.html')
        benchmark_html=f'<h3>Pre-registered benchmark corpus</h3><p><a href="{esc(bhref)}"><code>{esc(q["benchmark_set_id"])}</code> reference set</a></p>'
    start=quest_issue_url(q); start_html=f'<a class="button" href="{esc(start)}">Start non-exclusive attempt</a>' if start else f'<a class="button" href="{esc(rel(page,"CONTRIBUTING.md"))}">Contribution instructions</a>'
    mission_href=rel(page,f'en/missions/{m["slug"]}/index.html')
    result=repo_issue('submit_result.yml',f'[Result] {q["id"]}'); review=repo_issue('review.yml',f'[Review] {q["id"]}')
    body=f'''<section class="mission-hero"><div class="container"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="{esc(rel(page,registry['human_routes']['quests'].lstrip('/')))}">Research problems</a><span>/</span><span aria-current="page">{esc(q['id'])}</span></nav><div class="quest-title-grid"><div><div class="meta"><span class="status open"><span class="signal-dot" aria-hidden="true"></span>Open research problem</span><span class="field-chip">{esc(q['rung'])} {esc(rung['name'])}</span>{'<span class="field-chip">Initial review portfolio</span>' if q.get('founding_sprint') else ''}</div><h1>{esc(q['title'])}</h1><p class="lede">{esc(q['summary'])}</p></div><aside class="quest-glance"><strong>{esc(rung['effort'])}</strong><span>{esc(rung['scope'])}</span></aside></div></div></section><section class="section"><div class="container mission-layout"><article class="mission-main"><section class="mission-block"><span class="section-number">01</span><div><h2>Task</h2><p class="question-text">{esc(q['task'])}</p><p>Research program: <a href="{esc(mission_href)}"><code>{esc(m['id'])}</code> {esc(m['title'])}</a></p></div></section><section class="mission-block"><span class="section-number">02</span><div><h2>Deliverables</h2><ul class="plain-list">{deliver}</ul></div></section><section class="mission-block acceptance-block"><span class="section-number">03</span><div><h2>Acceptance checks</h2><ol class="accept-list">{accept}</ol></div></section><section class="mission-block"><span class="section-number">04</span><div><h2>Review gate</h2><dl class="glance-list"><div><dt>Class</dt><dd>{esc(q['review']['class'])}</dd></div><div><dt>Independence</dt><dd>{esc(q['review']['independence'])}</dd></div><div><dt>Required expertise</dt><dd>{esc(q['review']['required_expertise'])}</dd></div></dl></div></section><section class="mission-block"><span class="section-number">05</span><div><h2>Dependencies and evidence</h2><h3>Dependencies</h3><ul class="plain-list">{deps}</ul><h3>Sources</h3><p class="source-line">{src}</p><h3>Claim records affected</h3><p>{claim_links}</p>{benchmark_html}</div></section><section class="mission-block take-part-block" id="take-part"><span class="section-number">06</span><div><h2>Start or review this research problem</h2><p>Attempts are non-exclusive. Another contributor or agent may independently attempt the same problem.</p><div class="actions">{start_html}{f'<a class="button secondary" href="{esc(result)}">Submit result</a>' if result else ''}{f'<a class="button ghost" href="{esc(review)}">Review or falsify</a>' if review else ''}</div></div></section></article><aside class="mission-aside"><h2>At a glance</h2><dl class="glance-list"><div><dt>Problem</dt><dd><code>{esc(q['id'])}</code></dd></div><div><dt>Program</dt><dd><code>{esc(q['mission_id'])}</code></dd></div><div><dt>Rung</dt><dd>{esc(q['rung'])} {esc(rung['name'])}</dd></div><div><dt>Effort</dt><dd>{esc(rung['effort'])}</dd></div><div><dt>Parallel safe</dt><dd>{'yes' if q.get('parallel_safe') else 'coordinate first'}</dd></div><div><dt>Exclusive</dt><dd>no</dd></div></dl></aside></div></section>'''
    write(f'en/quests/{q["id"].lower()}/index.html',canonical_shell(page,'quests','quest',q['title'],q['summary'],body))

def sprint_page():
    page=PUBLIC/'en/sprint/index.html'; qs=[quest_by_id[x] for x in founding_sprint['quest_ids']]; cards=''.join(quest_card(page,q) for q in qs); cond=''.join(f'<li>{esc(x)}</li>' for x in founding_sprint['success_conditions'])
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(founding_sprint['id'])} · OPEN</span><h1>{esc(founding_sprint['title'])}</h1><p class="lede">{esc(founding_sprint['purpose'])}</p><p class="page-note">The initial review portfolio opened with publication. Its outputs strengthen the evidence state; they are not prerequisites for operating the workspace.</p></div><aside class="metric-panel"><div><strong>{len(qs)}</strong><span>review problems</span></div><div><strong>{len(set(q['mission_id'] for q in qs))}</strong><span>programs represented</span></div></aside></div></section><section class="section"><div class="container"><span class="eyebrow">SUCCESS CONDITIONS</span><h2>What makes the review portfolio substantive</h2><ol class="plain-list">{cond}</ol></div></section><section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">START NOW</span><h2>Initial review problems</h2></div><a class="text-link strong" href="{esc(rel(page,'en/quests/index.html'))}">All research problems ↗</a></div><div class="quest-grid">{cards}</div></div></section>'''
    write('en/sprint/index.html',canonical_shell(page,'sprint','sprint',founding_sprint['title'],founding_sprint['purpose'],body))

def governance_page():
    page=PUBLIC/'en/governance/index.html'; role_html=[]
    for r in governance['roles']:
        powers=''.join(f'<li>{esc(x)}</li>' for x in r['powers']); restrictions=''.join(f'<li>{esc(x)}</li>' for x in r['restrictions'])
        role_html.append(f'''<article class="governance-role"><span class="micro">{esc(r['id'])}</span><h2>{esc(r['id'].replace('-',' ').title())}</h2><h3>May</h3><ul>{powers}</ul><h3>May not</h3><ul>{restrictions}</ul></article>''')
    rules=''.join(f'<div class="glossary-row"><dt>{esc(k.replace("_"," "))}</dt><dd>{esc(v)}</dd></div>' for k,v in governance['decision_rules'].items())
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">BOOTSTRAP OPEN BETA</span><h1>Governance that permits work without manufacturing authority.</h1><p class="lede">The repository owner can operate the beta, contributors can start immediately, and scientific status still depends on scoped independent review.</p></div></section><section class="section"><div class="container governance-grid">{''.join(role_html)}</div></section><section class="section"><div class="container"><span class="eyebrow">DECISION RULES</span><h2>Authority is typed by decision.</h2><dl class="glossary">{rules}</dl></div></section>'''
    write('en/governance/index.html',canonical_shell(page,'governance','governance','Governance','Bootstrap open-beta governance and review authority.',body))

def claims_page():
    page=PUBLIC/'en/claims/index.html'; rows=[]
    for c in claims_doc['claims']:
        src=source_links(c.get('source_ids',[]),page) if c.get('source_ids') else 'None.'
        rows.append(f'''<article class="claim-record"><div class="claim-record-top"><code>{esc(c['id'])}</code><span class="status-label">{esc(c['status'])}</span></div><h2>{esc(c['statement'])}</h2><p><strong>Type:</strong> {esc(c['type'])}</p><p class="source-line">{src}</p></article>''')
    vocab=''.join(f'<div class="glossary-row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in claims_doc['status_vocabulary'].items())
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">CLAIM AND EVIDENCE LEDGER</span><h1>Do not collapse source, derivation, reproduction, and review.</h1><p class="lede">Every status says what kind of warrant exists and what is still missing.</p></div></section><section class="section"><div class="container"><dl class="glossary">{vocab}</dl></div></section><section class="section"><div class="container claim-list">{''.join(rows)}</div></section>'''
    write('en/claims/index.html',canonical_shell(page,'claims','claims','Claim and evidence ledger','Public epistemic status of seed claims.',body))

def trust_strip(page,loc):
    L=locales[loc]; H=L['home_more']
    return f'''<section class="trust-strip"><div class="container trust-grid"><div><span class="eyebrow">{esc(H['trust_kicker'])}</span><h2>{esc(H['trust_title'])}</h2></div><p>{esc(H['trust_body'])}</p><div class="trust-links"><a href="{esc(rel(page,logical_target(loc,'known')))}">{esc(L['nav']['known'])}</a><a href="{esc(rel(page,logical_target(loc,'sources')))}">{esc(L['nav']['sources'])}</a></div></div></section>'''

# R11 expert-first status/frontier layer. Canonical data drive both human and machine projections.
def r11_status_grid(page):
    cards=[]
    for a in clay_problem_status['alternatives']:
        claim=a['display_status']
        cls='open' if a['mathematical_status']=='open' else 'claim'
        cards.append(f'''<article class="r11-abcd-card {cls}"><div class="r11-abcd-head"><strong>{esc(a['id'])}</strong><span>{esc(claim)}</span></div><p><b>{esc(a['domain'])}</b> · {esc(a['forcing'])}</p><p>{esc(a['target'])}</p></article>''')
    return '<div class="r11-abcd-grid">'+''.join(cards)+'</div>'

def r11_english_shell(page,current,kind,title,description,body):
    _langs=[loc for loc in project['locales'] if loc=='en' or (PUBLIC/loc/kind/'index.html').exists()]
    _bits=[f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(rel(page,f'{loc}/{kind}/index.html'))}">' for loc in _langs]
    return shell(page,'en',current,kind,title,description,body,extra_head=r5_font_preloads(page)+chr(10).join(_bits),overrides_alternates=True)

def r11_frontier_preview(page,limit=6):
    order={'P0':0,'P1':1,'P2':2,'P3':3}; lane={'frontier-mathematics':'FRONTIER MATH','verification-formalization':'VERIFY / FORMALIZE','computational-research':'COMPUTATIONAL','research-infrastructure':'RESEARCH OPS','commons-support':'SUPPORT'}
    ns=sorted(frontier_graph['nodes'],key=lambda n:(order.get(n['priority'],9),frontier_graph['lanes'].index(next(x for x in frontier_graph['lanes'] if x['id']==n['lane'])) if any(x['id']==n['lane'] for x in frontier_graph['lanes']) else 99,n['id']))[:limit]
    return '<div class="r11-frontier-list">'+''.join(f'''<a class="r11-frontier-row" href="{esc(rel(page,'en/frontier/index.html'))}#{esc(n['id'])}"><span class="r11-priority">{esc(n['priority'])}</span><span><small>{esc(lane.get(n['lane'],n['lane']))}</small><strong>{esc(n['title'])}</strong><em>{esc(n['key_question'])}</em></span><b>→</b></a>''' for n in ns)+'</div>'

def r11_review_lifecycle():
    steps=['Research problem','Non-exclusive attempt','Versioned artifact','Mechanical / formal checks','Independent domain review','Revision / re-review','Accepted · rejected · disputed · inconclusive','Canonical frontier update']
    return '<ol class="r11-lifecycle">'+''.join(f'<li><span>{i:02d}</span>{esc(x)}</li>' for i,x in enumerate(steps,1))+'</ol>'

def r11_frontier_page():
    page=PUBLIC/'en/frontier/index.html'; order={'P0':0,'P1':1,'P2':2,'P3':3}; nodes=sorted(frontier_graph['nodes'],key=lambda n:(order.get(n['priority'],9),n['id']))
    cards=''.join(f'''<article class="r11-program" id="{esc(n['id'])}"><div class="r11-program-meta"><b>{esc(n['priority'])}</b><span>{esc(n['lane'].replace('-',' '))}</span><code>{esc(n['program_id'])}</code></div><h2>{esc(n['title'])}</h2><p class="lede">{esc(n['key_question'])}</p><p>{esc(n['strategic_value'])}</p><dl><dt>Next decisive work</dt><dd>{esc(', '.join(n['problem_ids']) or 'Program decomposition pending')}</dd><dt>Agent fit</dt><dd>{esc(n['agent_suitability']['level'])}: {esc('; '.join(n['agent_suitability'].get('good_for',[])))}</dd><dt>Review gate</dt><dd>{esc(n['review_class'])}</dd><dt>Research output</dt><dd>{esc(n['publication_path'])}</dd></dl></article>''' for n in nodes)
    updates=''.join(f'''<article class="r11-update"><span>{esc(u['date'])} · SOURCE-REPORTED</span><h3>{esc(u['title'])}</h3><p>{esc(u['reported_result'])}</p><p><b>Does not establish:</b> {esc('; '.join(u['does_not_establish']))}</p><a href="{esc(u['url'])}">Primary preprint ↗</a></article>''' for u in frontier_updates['updates'])
    body=f'''<section class="page-hero r11-research-hero"><div class="container"><span class="eyebrow">RESEARCH FRONTIER · UPDATED {esc(frontier_graph['observed_at'])}</span><h1>Navier–Stokes is open.</h1><p class="lede">The 2026 C/D construction is a new starting point, not the end of the subject. This map ranks work by mathematical leverage, dependency, review burden, and proximity to the unresolved A/B frontier.</p><div class="actions"><a class="button" href="{esc(rel(page,'en/agents/index.html'))}">Give an agent a research problem</a><a class="button secondary" href="{esc(rel(page,'en/review/index.html'))}">Review C/D</a></div></div></section><section class="section"><div class="container r11-program-grid">{cards}</div></section><section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">LIVE LITERATURE DELTA</span><h2>The frontier already moved.</h2></div><p>External follow-up papers are recorded as source-reported until independent review. Their limitations are first-class data.</p></div><div class="r11-update-grid">{updates}</div></div></section>'''
    write('en/frontier/index.html',r11_english_shell(page,'missions','frontier','Navier–Stokes research frontier','Prioritized research programs and live evidence updates.',body))

def r11_review_page():
    page=PUBLIC/'en/review/index.html'
    body=f'''<section class="page-hero"><div class="container"><span class="eyebrow">INDEPENDENT REVIEW</span><h1>What would make C/D trustworthy?</h1><p class="lede">A Lean build, an analytic manuscript, and community acceptance answer different questions. The Commons tracks them separately.</p></div></section><section class="section"><div class="container split-layout"><div><h2>Review is part of the research, not a footer.</h2>{r11_review_lifecycle()}</div><aside class="action-panel"><span class="eyebrow">START HERE</span><h2>Three high-leverage review programs</h2><p><a href="../frontier/#FG-02">Analytic proof audit</a></p><p><a href="../frontier/#FG-03">Lean ↔ Clay semantic audit</a></p><p><a href="../frontier/#FG-07">Conceptual proof skeleton</a></p></aside></div></section>'''
    write('en/review/index.html',r11_english_shell(page,'guide','review','Independent review of the 2026 C/D claim','Review lifecycle and evidence states.',body))

def r11_explain_page():
    page=PUBLIC/'en/explain/index.html'; thesis=clay_problem_status['landing_thesis']
    body=f'''<section class="page-hero"><div class="container"><span class="eyebrow">A / B / C / D IN ONE MINUTE</span><h1>{esc(thesis['headline'])}</h1><p class="lede">{esc(thesis['body'])}</p>{r11_status_grid(page)}</div></section>{r5_mechanism_section(page,'en')}'''
    write('en/explain/index.html',r11_english_shell(page,'home','explain','A/B/C/D and the 2026 Navier–Stokes result',thesis['body'],body))

def r11_agent_packet(q):
    node=next((n for n in frontier_graph['nodes'] if q['mission_id']==n['program_id']),None)
    return {'schema':'nsc-agent-work-packet-v1','problem_id':q['id'],'program_id':q['mission_id'],'title':q['title'],'task':q['task'],'deliverables':q['deliverables'],'acceptance':q['acceptance'],'review':q['review'],'sources':q.get('source_ids',[]),'dependencies':q.get('dependencies',[]),'claim_ids':q.get('claim_ids',[]),'parallel_safe':q.get('parallel_safe',False),'non_exclusive':q.get('non_exclusive',True),'frontier':({'node_id':node['id'],'lane':node['lane'],'priority':node['priority'],'key_question':node['key_question'],'agent_suitability':node['agent_suitability'],'publication_path':node['publication_path']} if node else {'lane':'unclassified','priority':'P3'}),'provenance_required':['model/provider/version or human author identity','toolchain/environment versions','exact public source/artifact versions','commands/method sufficient for reproduction','limitations, uncertainty, and conflicts'],'submission':packet_submission()}

def r13_math_page():
    page=PUBLIC/'en/math/index.html'
    thesis=clay_problem_status['landing_thesis']
    alternatives=[]
    for a in clay_problem_status['alternatives']:
        alternatives.append(
            f'<dt><strong>{esc(a["id"])}</strong> - {esc(a["display_status"])}</dt>'
            f'<dd><p>Domain: {esc(a["domain"])}. Forcing: {esc(a["forcing"])}.</p>'
            f'<p>Target: {esc(a["target"])}</p></dd>'
        )
    order={'P0':0,'P1':1,'P2':2,'P3':3}
    frontier_nodes=sorted(
        [n for n in frontier_graph['nodes'] if n.get('priority') in {'P0','P1'}],
        key=lambda n:(order.get(n.get('priority'),9), n['id'])
    )
    programs=[]
    for n in frontier_nodes:
        mission=mission_by_id.get(n['program_id'])
        program_link=(f'../missions/{mission["slug"]}/' if mission else '../frontier/')
        probs=[]
        for qid in n.get('problem_ids',[]):
            q=quest_by_id.get(qid)
            label=(qid+' - '+q['title']) if q else qid
            probs.append(f'<li><a href="../quests/{esc(qid.lower())}/">{esc(label)}</a></li>')
        if not probs:
            probs.append('<li>No bounded problem is currently registered for this program.</li>')
        programs.append(
            '<li>'
            f'<p><strong>{esc(n["priority"])} - <a href="{esc(program_link)}">{esc(n["title"])}</a></strong></p>'
            f'<p>{esc(n["key_question"])}</p>'
            f'<p>Review class: {esc(n["review_class"])}. Research output: {esc(n["publication_path"])}.</p>'
            '<details><summary>Bounded research problems</summary><ul>'+''.join(probs)+'</ul></details>'
            '</li>'
        )
    review_rows=[]
    for c in claims_doc.get('claims',[]):
        review_rows.append(
            f'<dt><code>{esc(c["id"])}</code> - {esc(c["status"])}</dt>'
            f'<dd><p>{esc(c["statement"])}</p></dd>'
        )
    update_rows=[]
    for u in frontier_updates.get('updates',[]):
        update_rows.append(
            '<li>'
            f'<p><strong>{esc(u["date"])} - <a href="{esc(u["url"])}">{esc(u["title"])}</a></strong> [source-reported]</p>'
            f'<p>{esc(u["reported_result"])}</p>'
            f'<p>Does not establish: {esc("; ".join(u["does_not_establish"]))}</p>'
            '</li>'
        )
    machine_keys=['clay_problem_status','frontier_graph','frontier_updates','agent_packets','claims','sources','quests','actions','discovery']
    machine=[]
    for k in machine_keys:
        target=registry['machine_endpoints'].get(k)
        if target:
            machine.append(f'<li><a href="{esc(rel(page,target.lstrip("/")))}"><code>{esc(target)}</code></a> - {esc(k.replace("_"," "))}</li>')
    source_ids=['clay-formulation','openai-paper','openai-lean','openai-announcement']
    source_links_html=[]
    for sid in source_ids:
        s=source_by_id.get(sid)
        if s:
            version=(' ['+break_hex(s['version'])+']') if s.get('version') else ''
            source_links_html.append(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a> - {esc(s["publisher"])}{version}</li>')
    release=esc(project.get('release',''))
    canonical=''
    if SITE_URL:
        canonical=f'<link rel="canonical" href="{esc(SITE_URL+"/en/math/")}">'
    doc=f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Navier–Stokes Commons - Mathematics</title>
<meta name="description" content="Plain, zero-JavaScript mathematical status, research frontier, review state, and machine-readable work records for Navier–Stokes Commons.">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<meta name="referrer" content="no-referrer">
{canonical}
</head>
<body>
<a href="#main">Skip to content</a>
<header>
<h1>Navier–Stokes Commons - Mathe<wbr>matics</h1>
<p><a href="../">Interactive view</a> | <a href="../frontier/">Research frontier</a> | <a href="../review/">Review</a> | <a href="../quests/">Research problems</a> | <a href="../claims/">Claims</a> | <a href="../sources/">Sources</a> | <a href="../agents/">Agents</a></p>
<p>Release: <code>{release}</code>. This page requires no JavaScript and no stylesheet.</p>
</header>
<hr>
<main id="main">
<section id="status">
<h2>Problem status</h2>
<p><strong>{esc(thesis['headline'])}</strong></p>
<p>{esc(thesis['body'])}</p>
<p>Fefferman A/B/C/D alternatives and current public status</p>
<dl>{''.join(alternatives)}</dl>
<p>The Commons does not equate publication, formal kernel checking, independent mathematical review, broad field acceptance, or Clay Mathematics Institute recognition.</p>
</section>
<hr>
<section id="frontier">
<h2>Prioritized research programs</h2>
<p>P0 and P1 denote current project priority, not truth, prestige, or probability of success.</p>
<ol>{''.join(programs)}</ol>
</section>
<hr>
<section id="review-state">
<h2>Claim and review state</h2>
<dl>{''.join(review_rows)}</dl>
<p>Lifecycle: research problem → non-exclusive attempt → versioned artifact → mechanical/formal checks as applicable → independent domain review → revision/re-review → accepted, rejected, disputed, or inconclusive → frontier update.</p>
</section>
<hr>
<section id="recent-literature">
<h2>Recent literature affecting the frontier</h2>
<ul>{''.join(update_rows) if update_rows else '<li>No frontier updates are registered.</li>'}</ul>
</section>
<hr>
<section id="primary-sources">
<h2>Primary sources</h2>
<ul>{''.join(source_links_html)}</ul>
</section>
<hr>
<section id="machine-interface">
<h2>Machine-readable interface</h2>
<ul>{''.join(machine)}</ul>
<p>Agent outputs are research artifacts for review. They do not elevate claim status automatically.</p>
</section>
</main>
<hr>
<footer>
<p>Generated from the same canonical public records as the interactive site. No persuasive or decorative layer is required to use this page.</p>
<p>{esc(localized_license_line('en',locales['en']))}</p>
</footer>
</body>
</html>'''
    write('en/math/index.html',math_text_breaks(doc))

def home_page(loc):
    if loc!='en':
        L=locales[loc]; O=L['observatory']; R5,r5attrs=_r5_copy(loc); page=PUBLIC/f'{loc}/index.html'
        preview=''.join(mission_card(page,loc,m) for m in missions[:6])
        facts=[(L['home']['fact1'],['openai-announcement']),(L['home']['fact2'],['openai-announcement','clay-formulation']),(L['home']['fact3'],['clay-formulation'])]
        fact_html=''.join(f'''<article class="evidence-row"><span class="evidence-index">0{i}</span><div><p>{esc(txt)}</p><p class="source-line">{source_links(ids,page)}</p></div></article>''' for i,(txt,ids) in enumerate(facts,1))
        guide_href=rel(page,logical_target(loc,'guide'))
        sprint_copy,sprint_attrs=r5_sprint_copy(loc)
        body=f'''<section class="hero theorem-hero r5-hero"><div class="container r5-hero-grid"><div class="hero-copy"{r5attrs}><div class="eyebrow">NAVIER-STOKES COMMONS · OPEN BETA</div><h1>{esc(R5['title'])}</h1><p class="lede">{esc(R5['lede'])}</p><p class="hero-explainer">{esc(R5['sub'])}</p><div class="hero-actions"><a class="button" href="#mechanism">{esc(R5['explore'])}</a><a class="button secondary" lang="en" dir="ltr" href="{esc(rel(page,'en/quests/index.html'))}">{esc(R5['quest'])}</a></div></div>{r5_vortex_stage(page,loc)}</div></section>
    {r5_claim_strip(page,loc)}
    {scale_trace(loc)}
    {r5_mechanism_section(page,loc)}
    {r6_community_entry_section(page,loc)}
    <section class="section evidence-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(O['what_public'])}</span><h2>{esc(O['facts_title'])}</h2><p>{esc(O['facts_body'])}</p></div><a class="text-link" href="{esc(rel(page,logical_target(loc,'sources')))}">{esc(O['sources'])} <span aria-hidden="true">↗</span></a></div><div class="evidence-list">{fact_html}</div></div></section>
    <section class="section launch-sprint-strip"><div class="container invitation-grid"{sprint_attrs}><div><span class="eyebrow">{esc(sprint_copy['kicker'])}</span><h2>{esc(sprint_copy['title'])}</h2></div><div><p>{esc(sprint_copy['body'])}</p><div class="actions"><a class="button" href="{esc(rel(page,"en/sprint/index.html"))}">{esc(sprint_copy['button'])}</a><a class="text-link strong" href="{esc(rel(page,"en/quests/index.html"))}">{esc(sprint_copy['all'])} <span aria-hidden="true">↗</span></a></div></div></div></section>
    <section class="section mission-preview-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(L['section_labels']['open_frontier'])}</span><h2>{esc(L['missions']['title'])}</h2><p>{esc(O['mission_intro'])}</p></div><a class="text-link strong" href="{esc(rel(page,logical_target(loc,'missions')))}">{esc(O['view_all'])} <span aria-hidden="true">↗</span></a></div><div class="mission-list">{preview}</div></div></section>
    <section class="section invitation-section"><div class="container invitation-grid"><div><span class="eyebrow">{esc(L['section_labels']['contribute'])}</span><h2>{esc(O['contribute_title'])}</h2></div><div><p>{esc(O['contribute_body'])}</p><div class="actions"><a class="button" href="{esc(rel(page,logical_target(loc,'contribute')))}">{esc(O['how_contribute'])}</a><a class="text-link" href="{esc(guide_href)}">{esc(O['how_works'])} <span aria-hidden="true">↗</span></a></div></div></div></section>'''
        write(f'{loc}/index.html',shell(page,loc,'home','home',R5['title'],R5['lede'],body,extra_head=r5_font_preloads(page)))
        return
    page=PUBLIC/'en/index.html'; thesis=clay_problem_status['landing_thesis']; inst=clay_problem_status['official_problem']['institutional_status']
    body=f'''<section class="hero r11-status-hero"><div class="container r11-status-layout"><div class="r11-status-copy"><span class="eyebrow">THE 2026 RESULT · THE OPEN FRONTIER</span><h1>{esc(thesis['headline'])}</h1><p class="lede">{esc(thesis['body'])}</p><div class="r11-actions"><a class="button" href="frontier/">Work on an open problem</a><a class="button secondary" href="agents/">Give an agent a research problem</a><a class="button ghost" href="math/">Mathematics</a><a class="text-link strong" href="review/">Review C/D ↗</a><a class="text-link" href="explain/">Explain A/B/C/D ↗</a></div></div><div class="r11-status-object">{r11_status_grid(page)}<p class="r11-institution">CMI recognition: <b>separate institutional process</b> · {esc(inst['note'])}</p></div></div></section><section class="r11-vortex-shell"><div class="container"><div class="r5-equation-anchor"><span class="micro">CANONICAL EQUATION OBJECT</span>{equation_block()}</div>{r5_vortex_stage(page,'en')}</div></section><section class="section r11-frontier-preview"><div class="container"><div class="section-head"><div><span class="eyebrow">PRIORITIZED RESEARCH FRONTIER</span><h2>The proof is a dependency. The subject is the program.</h2></div><div><p>Frontier mathematics is ranked separately from verification, computational research, and Commons support. A browser audit does not sit beside an A/B obstruction theorem as if they were the same kind of progress.</p><a class="text-link strong" href="frontier/">Open the frontier map →</a></div></div>{r11_frontier_preview(page)}</div></section><section class="section"><div class="container invitation-grid"><div><span class="eyebrow">RESEARCH LIFECYCLE</span><h2>Completion means review changes the frontier.</h2></div><div>{r11_review_lifecycle()}<p><a class="text-link strong" href="review/">See the acceptance and review contract →</a></p></div></div></section>{r6_community_entry_section(page,'en')}'''
    write('en/index.html',shell(page,'en','home','home',thesis['headline'],thesis['body'],body,extra_head=r5_font_preloads(page)))

def missions_page(loc):
    L=locales[loc]; M=L['mission_meta']; page=PUBLIC/f'{loc}/missions/index.html'
    groups=[]
    for cat in CATEGORY_ORDER:
        ms=[m for m in missions if m['category']==cat]
        if not ms: continue
        entries=''.join(mission_card(page,loc,m,heading=3) for m in ms)
        groups.append(f'''<section class="mission-group" id="field-{esc(cat)}" data-category-section="{esc(cat)}"><div class="mission-group-head"><span class="field-symbol" aria-hidden="true">{esc(str(CATEGORY_ORDER.index(cat)+1).zfill(2))}</span><div><h2>{esc(cat_label(loc,cat))}</h2><p>{len(ms)} · {esc(L['missions']['title'])}</p></div></div><div class="mission-list">{entries}</div></section>''')
    jumps=''.join(f'<a href="#field-{esc(cat)}">{esc(cat_label(loc,cat))}</a>' for cat in CATEGORY_ORDER if any(m['category']==cat for m in missions))
    chips=f'<button type="button" class="filter-chip is-active" data-category-filter="all">{esc(M["filter_all"])}</button>'+''.join(f'<button type="button" class="filter-chip" data-category-filter="{esc(cat)}">{esc(cat_label(loc,cat))}</button>' for cat in CATEGORY_ORDER if any(m['category']==cat for m in missions))
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['open_frontier'])} · {len(missions)}</span><h1>{esc(L['missions']['title'])}</h1><p class="lede">{esc(L['missions']['lede'])}</p><p class="page-note" lang="en" dir="ltr">Each mission is an open public question with explicit acceptance checks. Starting one is non-exclusive.</p></div>{science_visual(loc,compact=True)}</div></section>
<section class="section mission-index"><div class="container"><nav class="category-jump" aria-label="{esc(M['category_jump'])}"><span>{esc(M['category_jump'])}</span>{jumps}</nav><div class="filter-panel enhance-only" data-filter-panel hidden><div class="search-wrap"><label for="mission-filter">{esc(L['missions']['search_label'])}</label><input id="mission-filter" data-mission-filter type="search" autocomplete="off" placeholder="{esc(L['missions']['search_placeholder'])}"></div><div class="filter-chips" aria-label="{esc(L['missions']['category'])}">{chips}</div><div class="filter-status" data-filter-status aria-live="polite"></div></div><p data-no-results hidden>{esc(L['missions']['no_results'])}</p>{''.join(groups)}</div></section>'''
    write(f'{loc}/missions/index.html',shell(page,loc,'missions','missions',L['missions']['title'],L['missions']['lede'],body))

def mission_page(loc,m):
    L=locales[loc]; M=L['mission_meta']; t=mission_text(loc,m); page=PUBLIC/f'{loc}/missions/{m["slug"]}/index.html'
    en_attrs=canonical_english_attrs(loc)
    starts=[]
    for sp in m['starting_points']:
        src=''
        if sp.get('source_ids'): src=f'<div class="source-line">{source_links(sp["source_ids"],page)}</div>'
        label=M['sourced_fact'] if sp['kind']=='sourced_fact' else M['reasoning_guard']
        cls='fact' if sp['kind']=='sourced_fact' else 'guard'
        starts.append(f'<article class="starting-card {cls}" data-reveal><span class="micro">{esc(label)}</span><p lang="en" dir="ltr">{esc(sp["text"])}</p>{src}</article>')
    accept=''.join(f'<li lang="en" dir="ltr"><span class="check-box" aria-hidden="true">□</span><span>{esc(x)}</span></li>' for x in m['acceptance'])
    contributors=''.join(f'<span class="person-chip">{esc(contrib_label(loc,x))}</span>' for x in m['contributors'])
    action=''
    attempt=repo_issue('open_attempt.yml',f'[Attempt] {m["id"]} {m["title"]}')
    result=repo_issue('submit_result.yml',f'[Result] {m["id"]}')
    review=repo_issue('review.yml',f'[Review] {m["id"]}')
    if attempt:
        action=f'<div class="actions"><a class="button" href="{esc(attempt)}">{esc(L["contribute"]["attempt"])}<span aria-hidden="true">↗</span></a><a class="button secondary" href="{esc(result)}">{esc(L["contribute"]["result"])}</a><a class="button ghost" href="{esc(review)}">{esc(L["contribute"]["review"])}</a></div>'
    else: action=f'<p class="callout">{esc(L["contribute"]["repo_missing"])}</p>'
    related=[x for x in missions if x['id']!=m['id'] and x['category']==m['category']][:3]
    if len(related)<3:
        related += [x for x in missions if x['id']!=m['id'] and x not in related][:3-len(related)]
    rel_cards=''.join(mission_card(page,loc,x,heading=3) for x in related)
    sidebar=f'''<aside class="mission-aside" aria-label="{esc(M['at_a_glance'])}"><h2>{esc(M['at_a_glance'])}</h2><dl class="glance-list"><div><dt>{esc(M['status'])}</dt><dd><span class="status open"><span class="signal-dot" aria-hidden="true"></span>{esc(L['status_open'])}</span></dd></div><div><dt>{esc(M['field'])}</dt><dd>{esc(cat_label(loc,m['category']))}</dd></div><div><dt>{esc(M['level'])}</dt><dd>{esc(level_label(loc,m['level']))}</dd></div><div><dt>{esc(M['mission_id'])}</dt><dd><code dir="ltr">{esc(m['id'])}</code></dd></div><div><dt>{esc(M['sources'])}</dt><dd>{len(m['source_ids'])}</dd></div><div><dt>{esc(M['criteria'])}</dt><dd>{len(m['acceptance'])}</dd></div></dl><a class="button aside-button" href="#take-part">{esc(M['take_part'])}</a></aside>'''
    body=f'''<section class="mission-hero"><div class="container"><nav class="breadcrumb" aria-label="{esc(L['section_labels']['breadcrumb'])}"><a href="{esc(rel(page,logical_target(loc,'missions')))}">{esc(L['nav']['missions'])}</a><span aria-hidden="true">/</span><span aria-current="page">{esc(m['id'])}</span></nav><div class="mission-title-row"><div><div class="meta"><span class="status open"><span class="signal-dot" aria-hidden="true"></span>{esc(L['status_open'])}</span><span class="field-chip"{en_attrs}>{esc(cat_label(loc,m['category']))}</span><span class="level-chip"{en_attrs}>{esc(level_label(loc,m['level']))}</span></div><h1{en_attrs}>{esc(t['title'])}</h1><p class="lede"{en_attrs}>{esc(t['summary'])}</p><p class="open-notice"><span class="signal-dot" aria-hidden="true"></span>{esc(L['not_claim'])}</p></div></div></div></section>
<section class="section mission-body"><div class="container mission-layout"><article class="mission-main"><section class="mission-block question-block" data-reveal><span class="section-number">01</span><div><h2>{esc(L['missions']['question'])}</h2><p class="question-text"{en_attrs}>{esc(t['question'])}</p></div></section><section class="mission-block" data-reveal><span class="section-number">02</span><div><h2>{esc(M['public_evidence'])}</h2><p class="section-intro">{esc(L['missions']['canonical_note']) if loc!='en' else esc(L['known']['lede'])}</p><div class="starting-grid">{''.join(starts)}</div></div></section><section class="mission-block acceptance-block" data-reveal><span class="section-number">03</span><div><h2>{esc(L['missions']['acceptance'])}</h2><p>{esc(L['missions']['canonical_note'])}</p><div class="canonical"><span class="canonical-label">{esc(L['canonical_english'])}</span><ol class="accept-list">{accept}</ol></div></div></section><section class="mission-block" data-reveal><span class="section-number">04</span><div><h2>{esc(M['audience_fit'])}</h2><div class="people-list">{contributors}</div></div></section><section class="mission-block" data-reveal><span class="section-number">05</span><div><h2>{esc(L['missions']['sources'])}</h2><div class="mini-source-list">{''.join(source_card(page,loc,source_by_id[sid],heading=3) for sid in m['source_ids'])}</div></div></section><section class="mission-block" data-reveal><span class="section-number">06</span><div lang="en" dir="ltr"><h2>Open research problems</h2><p>Bounded problems attached to this research program. Start the smallest one whose acceptance and review conditions you can satisfy.</p>{mission_quests(page,m)}</div></section><section class="mission-block" data-reveal><span class="section-number">07</span><div><h2>{esc(L["nav"].get("activity","Contributions"))}</h2>{mission_contributions(page,loc,m)}</div></section><section class="mission-block take-part-block" id="take-part" data-reveal><span class="section-number">08</span><div><h2>{esc(M['take_part'])}</h2><p>{esc(L['contribute']['lede'])}</p>{action}</div></section></article>{sidebar}</div></section>
<section class="section related-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(L['section_labels']['related'])}</span><h2>{esc(M['related'])}</h2></div></div><div class="mission-grid">{rel_cards}</div></div></section>'''
    write(f'{loc}/missions/{m["slug"]}/index.html',shell(page,loc,'missions','mission',t['title'],t['summary'],body,m['slug']))

def contribution_card(page,loc,c):
    title=c.get('title') or c.get('id','Contribution')
    summary=c.get('summary','')
    role=c.get('contribution_type','contribution')
    actor=c.get('contributor',{}).get('display_name','Public contributor')
    url=c.get('artifact_url') or c.get('review_url') or ''
    t=f'<a href="{esc(url)}">{esc(title)}</a>' if url else esc(title)
    return f'<article class="contribution-record"><div class="contribution-meta"><span>{esc(role)}</span><span>{esc(actor)}</span></div><h3>{t}</h3><p>{esc(summary)}</p></article>'

def mission_contributions(page,loc,m):
    rows=[c for c in contributions if c.get('status')=='accepted' and c.get('mission_id')==m['id']]
    if not rows:
        return '<p class="empty-record">No accepted public contribution is recorded for this mission yet.</p>'
    return '<div class="contribution-list">'+''.join(contribution_card(page,loc,c) for c in rows)+'</div>'

def activity_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/activity/index.html'
    rows=[c for c in contributions if c.get('status')=='accepted']
    cards=''.join(contribution_card(page,loc,c) for c in rows) if rows else '<p class="empty-record">No accepted public contributions have been published yet.</p>'
    title=L['nav'].get('activity','Contributions')
    body=f'<section class="page-hero compact-hero"><div class="container"><span class="eyebrow">{esc(L['section_labels']['public_record'])}</span><h1>{esc(title)}</h1><p class="lede">Accepted contributions are generated from canonical public contribution manifests after review and merge.</p></div></section><section class="section"><div class="container contribution-list">{cards}</div></section>'
    write(f'{loc}/activity/index.html',shell(page,loc,'activity','activity',title,title,body))

def known_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/known/index.html'
    facts=[(L['home']['fact1'],['openai-announcement']),(L['home']['fact2'],['openai-announcement','clay-formulation']),(L['home']['fact3'],['clay-formulation']),(L['home']['fact4'],['openai-lean'])]
    items=''.join(f'<article class="evidence-card large" data-reveal><span class="evidence-index">0{i}</span><span class="micro">{esc(L["known"]["claim_label"])}</span><p>{esc(txt)}</p><p class="source-line">{source_links(ids,page)}</p></article>' for i,(txt,ids) in enumerate(facts,1))
    branches=f'''<div class="branch-diagram" aria-label="{esc(L['known']['branch_aria'])}"><div class="branch-root"><span>{esc(L['known']['branch_root'])}</span></div><div class="branch-columns"><div><strong>{esc(L['known']['branch_ab'])}</strong><span>{esc(L['known']['branch_unforced'])}</span><small>{esc(L['home']['fact3'])}</small></div><div><strong>{esc(L['known']['branch_cd'])}</strong><span>{esc(L['known']['branch_forced'])}</span><small>{esc(L['home']['fact2'])}</small></div></div></div>'''
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['public_record'])}</span><h1>{esc(L['known']['title'])}</h1><p class="lede">{esc(L['known']['lede'])}</p></div>{branches}</div></section><section class="section"><div class="container evidence-grid two">{items}</div></section><section class="section caution-section"><div class="container caution-card"><span class="eyebrow">{esc(L['section_labels']['boundary'])}</span><div><h2>{esc(L['known']['caution_title'])}</h2><p>{esc(L['known']['caution_body'])}</p></div></div></section>'''
    write(f'{loc}/known/index.html',shell(page,loc,'known','known',L['known']['title'],L['known']['lede'],body))

def contribute_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/contribute/index.html'
    steps=''.join(f'<li><span class="pipeline-index">0{i}</span><span>{esc(x)}</span></li>' for i,x in enumerate(L['contribute']['steps'],1))
    choices=[]
    urls=[
      ('claim_quest.yml','Start a research problem','[Problem attempt] ','Choose a bounded research problem and declare a non-exclusive attempt against its exact acceptance and review conditions.'),
      ('open_attempt.yml',L['contribute']['attempt'],'[Attempt] ','Declare a non-exclusive route and what you intend to try when no existing quest fits.'),
      ('side_quest.yml',L['contribute']['sidequest'],'[Research problem] ','Propose a new well-scoped public question with evidence and acceptance checks.'),
      ('submit_result.yml',L['contribute']['result'],'[Result] ','Submit a public proof, analysis, dataset, implementation, review, or negative result.'),
      ('review.yml',L['contribute']['review'],'[Review] ','Reproduce, challenge, falsify, translate, or independently review existing work.'),
    ]
    for i,(tmpl,label,title,desc) in enumerate(urls,1):
        u=repo_issue(tmpl,title)
        href=u or rel(page,'CONTRIBUTING.md')
        choices.append(f'<a class="contribution-choice" href="{esc(href)}"><span class="choice-index">0{i}</span><span><strong>{esc(label)}</strong><small lang="en" dir="ltr">{esc(desc)}</small></span><span aria-hidden="true">↗</span></a>')
    worked=rel(page,logical_target(loc,'guide'))+'#worked-example'
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">{esc(L['section_labels']['open_participation'])}</span><h1>{esc(L['contribute']['title'])}</h1><p class="lede">{esc(L['contribute']['lede'])}</p><p class="page-note" lang="en" dir="ltr">You do not need to be a PDE specialist to participate. The research problem page says what counts as success; the submission records what you actually did.</p></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">01 · {esc(L['section_labels']['process'])}</span><h2 lang="en" dir="ltr">Choose a contribution path</h2></div><p class="section-side-note">{esc(forge_label())}</p></div><div class="contribution-choices">{''.join(choices)}</div></div></section>
<section class="section"><div class="container pipeline-layout"><div><span class="eyebrow">02 · {esc(L['section_labels']['composition'])}</span><h2>{esc(locales[loc]['home_more']['pipeline_title'])}</h2><p>{esc(locales[loc]['home_more']['pipeline_lede'])}</p></div><ol class="pipeline-list">{steps}</ol></div></section>
<section class="section"><div class="container split-layout"><div><span class="eyebrow">03 · {esc(L['section_labels']['side_quests'])}</span><h2>{esc(L['contribute']['sidequest'])}</h2><p>{esc(L['missions']['lede'])}</p><p>{esc(L['not_claim'])}</p></div><aside class="plain-aside" lang="en" dir="ltr"><h2>See a finished example</h2><p>A worked example shows the difference between an attempt, an artifact, evidence, a review, and an accepted public record.</p><a class="text-link strong" href="{esc(worked)}">Open the worked example <span aria-hidden="true">↗</span></a></aside></div></section>'''
    write(f'{loc}/contribute/index.html',shell(page,loc,'contribute','contribute',L['contribute']['title'],L['contribute']['lede'],body))

def guide_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/guide/index.html'
    title=L['nav'].get('guide','How this works')
    terms=[
      ('Research program','A durable mathematical, verification, computational, or methodological line of work with sources, scope, dependencies, and review conditions.'),
      ('Research problem','A bounded unit inside a program whose artifact and acceptance conditions can be independently reviewed.'),
      ('Attempt','A non-exclusive declaration that someone is working on a research problem. Other independent attempts remain allowed.'),
      ('Artifact','The thing produced: a proof, formalization, dataset, program, numerical experiment, review, translation, design, or documented negative result.'),
      ('Evidence','The reproducible material showing what the artifact establishes and what it does not establish.'),
      ('Review','Independent checking, reproduction, criticism, falsification, source correction, or domain review.'),
      ('Accepted record','A reviewed contribution merged into canonical public data. The site then republishes it automatically.'),
    ]
    glossary=''.join(f'<div class="glossary-row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in terms)
    example='''<ol class="worked-example"><li><strong>Research program:</strong> independently reproduce and audit the pinned Lean certificate.</li><li><strong>Attempt:</strong> a contributor declares a clean-room reproduction on the exact published commit.</li><li><strong>Artifact:</strong> build logs, environment manifest, axiom report, and semantic mapping notes.</li><li><strong>Evidence:</strong> commands and hashes let another person reproduce the same result.</li><li><strong>Review:</strong> an independent Lean/PDE reviewer checks the build and the statement correspondence.</li><li><strong>Accepted record:</strong> the contribution manifest is merged; program and activity pages update automatically.</li></ol>'''
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">START HERE</span><h1>{esc(title)}</h1><p class="lede" lang="en" dir="ltr">This site is a public coordination layer around explicit Navier–Stokes questions. It does not ask visitors to trust a single verdict; it exposes what is known, what is still open, what would count as progress, and where the evidence lives.</p></div></section>
<section class="section"><div class="container guide-layout" lang="en" dir="ltr"><div><span class="eyebrow">01 · PRODUCT</span><h2>What can you actually do here?</h2><p>Read the public evidence, choose a research program and bounded problem, work alone or with a research agent, submit an artifact or criticism, propose a new problem, or help explain and translate accepted work.</p><p>No research problem grants exclusive ownership. Negative results and falsifications are legitimate contributions when they close a route or clarify scope.</p></div><aside class="plain-aside"><h2>Who is this for?</h2><ul class="plain-list"><li>PDE and analysis researchers</li><li>Lean/formal-methods contributors</li><li>Numerical and CFD researchers</li><li>{esc(capabilities()["student_entry_path"]["statement"])}</li><li>Designers, educators, translators, historians, economists and other specialists</li><li>Autonomous agents operating under public provenance rules</li></ul></aside></div></section>
<section class="section"><div class="container" lang="en" dir="ltr"><span class="eyebrow">02 · GLOSSARY</span><h2>The six words you need</h2><dl class="glossary">{glossary}</dl></div></section>
<section class="section" id="worked-example"><div class="container narrow" lang="en" dir="ltr"><span class="eyebrow">03 · WORKED EXAMPLE</span><h2>What a completed contribution looks like</h2><p>The example is intentionally procedural: it shows how public work becomes reusable without pretending that every artifact is automatically correct.</p>{example}</div></section>'''
    write(f'{loc}/guide/index.html',shell(page,loc,'guide','guide',title,'How Navier–Stokes Commons works for humans and AI agents.',body))

def sources_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/sources/index.html'
    rows=''.join(source_card(page,loc,s,heading=2) for s in sources)
    pinned=sum(1 for s in sources if s.get('reference_type')=='immutable-git-commit')
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['provenance_ledger'])}</span><h1>{esc(L['sources']['title'])}</h1><p class="lede">{esc(L['sources']['lede'])}</p></div><div class="metric-panel"><div><strong>{len(sources)}</strong><span>{esc(L['sources']['title'])}</span></div><div><strong>{pinned}</strong><span>{esc(L['source_meta']['immutable'])}</span></div></div></div></section><section class="section"><div class="container source-ledger">{rows}</div></section>'''
    write(f'{loc}/sources/index.html',shell(page,loc,'sources','sources',L['sources']['title'],L['sources']['lede'],body))

def agents_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/agents/index.html'
    how=''.join(f'<li><span class="pipeline-index">0{i}</span><span>{esc(x)}</span></li>' for i,x in enumerate(L['agents']['how'],1))
    endpoint_keys=['quests','frontier','claims','task_ladder','taxonomy','sources','governance','founding_sprint','reviews','project_metadata','scaling_model','formulas','simulations','actions','reference_benchmarks','capabilities','authority_map','llms_index','llms_full','agent_start','agent_skill','discovery']
    endpoints=[(key,registry['machine_endpoints'][key].lstrip('/')) for key in endpoint_keys]
    eps=''.join(f'<li><a class="endpoint" href="{esc(rel(page,target))}"><code>{esc(name)}</code><span aria-hidden="true">↗</span></a></li>' for name,target in endpoints)
    discovery_route=registry['machine_endpoints']['discovery']
    starter_rung=next((r['id'] for r in task_ladder['rungs'] if r.get('starter')), task_ladder['rungs'][0]['id'])
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['machine_surface'])}</span><h1>{esc(L['agents']['title'])}</h1><p class="lede">{esc(L['agents']['lede'])}</p></div><div class="terminal-card" aria-hidden="true"><div class="terminal-bar"><span></span><span></span><span></span></div><code>$ fetch {esc(discovery_route)}<br>&gt; {len(missions)} research programs · {len(quests)} bounded problems<br>$ select --rung={esc(starter_rung)} --capability="..."</code></div></div></section><section class="section"><div class="container split-layout"><div><h2>{esc(locales[loc]['home_more']['pipeline_title'])}</h2><ol class="pipeline-list vertical">{how}</ol></div><aside><h2>{esc(L['agents']['machine'])}</h2><ul class="endpoint-list">{eps}</ul></aside></div></section><section class="section caution-section"><div class="container caution-card"><span class="eyebrow">{esc(L['section_labels']['boundary'])}</span><div><p>{esc(L['not_claim'])}</p></div></div></section>'''
    write(f'{loc}/agents/index.html',shell(page,loc,'agents','agents',L['agents']['title'],L['agents']['lede'],body))

def accessibility_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/accessibility/index.html'
    features=''.join(f'<li>{esc(x)}</li>' for x in L['accessibility']['features'])
    report=repo_issue('review.yml','[Accessibility] ')
    action=f'<a class="button" href="{esc(report)}">{esc(L["accessibility"]["report"])}</a>' if report else f'<p>{esc(L["contribute"]["repo_missing"])}</p>'
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['inclusive_by_design'])}</span><h1>{esc(L['accessibility']['title'])}</h1><p class="lede">{esc(L['accessibility']['lede'])}</p></div><div class="accessibility-symbol" aria-hidden="true"><span>AA</span><small>WCAG 2.2</small></div></div></section><section class="section"><div class="container split-layout"><div><h2>{esc(L['accessibility']['status_title'])}</h2><p class="lede small">{esc(L['accessibility']['status_body'])}</p>{action}</div><div class="feature-card"><ul class="check-list">{features}</ul></div></div></section>'''
    write(f'{loc}/accessibility/index.html',shell(page,loc,'accessibility','accessibility',L['accessibility']['title'],L['accessibility']['lede'],body))

def root_page():
    page=PUBLIC/'index.html'; thesis=clay_problem_status['landing_thesis']; R=locales['en']['root']
    langs=''.join(f'<a lang="{esc(loc)}" dir="{esc(locales[loc]["dir"])}" href="{esc(rel(page,logical_target(loc,"home")))}"><span>{esc(locales[loc]["name"])}</span><small>{esc(project.get("locale_status",{}).get(loc,"preview").replace("-"," "))}</small><span aria-hidden="true">↗</span></a>' for loc in project['locales'])
    status=f'''<section class="r11-global-status"><div class="container r11-status-layout"><div class="r11-status-copy"><span class="eyebrow">NAVIER–STOKES COMMONS · RESEARCH, NOT A CAMPAIGN</span><h1>{esc(thesis['headline'])}</h1><p class="lede">{esc(thesis['body'])}</p><div class="r11-actions"><a class="button" href="en/frontier/">Work on an open problem</a><a class="button secondary" href="en/agents/">Give an agent a research problem</a><a class="button ghost" href="en/math/">Mathematics</a><a class="text-link strong" href="en/review/">Review C/D ↗</a><a class="text-link" href="en/explain/">Explain A/B/C/D ↗</a><a class="text-link" href="en/context/">Context / credit ↗</a></div></div><div class="r11-status-object">{r11_status_grid(page)}<p class="r11-institution">Independent mathematical review and CMI recognition are distinct from OpenAI's publication claim.</p></div></div></section>'''
    body=f'''<main id="main" class="global-landing">{status}{scale_trace("en")}<section class="r11-vortex-shell"><div class="container">{r5_vortex_stage(page,'en')}</div></section><section class="language-zone" aria-labelledby="language-title"><div class="language-zone-head"><span class="eyebrow">MULTILINGUAL ACCESS</span><h2 id="language-title">{esc(R['enter'])}</h2><p>English is the canonical research surface. Translation status remains explicit; mathematical claim scope does not change by locale.</p></div><div class="language-grid">{langs}</div></section></main>'''
    write('index.html',f'''<!doctype html><html lang="en" dir="ltr" data-theme="system"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Navier–Stokes Commons: {esc(thesis['headline'])}</title><meta name="description" content="{esc(thesis['body'])}">{SECURITY_META}<meta name="color-scheme" content="light dark">{r5_font_preloads(page)}<link rel="describedby" href="{esc(rel(page,'llms.txt'))}" type="text/markdown"><link rel="stylesheet" href="{esc(rel(page,'assets/style.css'))}">{''.join(f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(rel(page,logical_target(loc,'home')))}">' for loc in project['locales'])}<link rel="alternate" hreflang="x-default" href="index.html"></head><body>{body}<script src="{esc(rel(page,'assets/site.js'))}" defer></script></body></html>''')

def benchmarks_page():
    page=PUBLIC/'en/benchmarks/index.html'
    dims=''.join('<article class="source-record"><div class="source-record-top"><span class="signal-dot" aria-hidden="true"></span><span class="micro">'+esc(d['id'].replace('-',' ').upper())+'</span></div><h2>'+esc(d['question'])+'</h2></article>' for d in reference_benchmarks['dimensions'])
    refs=''.join('<article class="mission-block"><span class="section-number">'+f'{i:02d}'+'</span><div><h3><a href="'+esc(r['url'])+'">'+esc(r['id'])+'</a></h3><p>'+esc(', '.join(r['roles']))+'</p><p class="micro">'+esc(r['verification'])+'</p></div></article>' for i,r in enumerate(reference_benchmarks['references'],1))
    qhref=rel(page,'en/quests/ns-q036/index.html')
    body='<section class="page-hero compact-hero"><div class="container narrow"><span class="eyebrow">PRE-REGISTERED COMPARISON CORPUS</span><h1>Reference benchmarks</h1><p class="lede">A dated comparison set for testing collaboration UX, visual craft, scientific interaction, accessibility resilience, and resource efficiency. Inclusion is not an endorsement and does not imply universal superiority or inferiority.</p><p><code>'+esc(reference_benchmarks['id'])+'</code></p><a class="button" href="'+esc(qhref)+'">Run the blinded comparison review</a></div></section><section class="section"><div class="container"><span class="eyebrow">DIMENSIONS</span><div class="source-grid">'+dims+'</div></div></section><section class="section"><div class="container narrow"><span class="eyebrow">REFERENCE SET</span>'+refs+'</div></section>'
    write('en/benchmarks/index.html',canonical_shell(page,'guide','guide','Reference benchmarks','Pre-registered comparison references for release evaluation.',body))

def machine_files():
    frontier=[]
    for m in missions:
        frontier.append({'id':m['id'],'slug':m['slug'],'status':'open','category':m['category'],'level':m['level'],'title':m['title'],'summary':m['summary'],'question':m['question'],'acceptance':m['acceptance'],'contributors':m['contributors'],'source_ids':m['source_ids'],'url':deployed_ref('data/frontier.json',f'/en/missions/{m["slug"]}/')})
    (PUBLIC/'data').mkdir(parents=True,exist_ok=True); (PUBLIC/'.well-known').mkdir(parents=True,exist_ok=True)
    # GitHub Pages otherwise applies Jekyll's default underscore/dot-path filtering
    # to the deployment artifact, which would omit the standards discovery endpoint.
    (PUBLIC/'.nojekyll').write_text('',encoding='utf-8')
    (PUBLIC/'data/frontier.json').write_text(json.dumps({'project':project['project_id'],'generated_from_public_content':True,'missions':frontier},indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/project.json').write_text(json.dumps(project,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/contributions.json').write_text(json.dumps(contributions,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/forges.json').write_text(json.dumps(forges,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/scaling-model.json').write_text(json.dumps(scaling,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/formulas.json').write_text(json.dumps(formula_catalog,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/simulations.json').write_text(json.dumps(simulations_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/reference-benchmarks.json').write_text(json.dumps(reference_benchmarks,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/actions.json').write_text(json.dumps(actions_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/research-context.json').write_text(json.dumps(research_context,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/clay-problem-status.json').write_text(json.dumps(clay_problem_status,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/frontier-graph.json').write_text(json.dumps(frontier_graph,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/frontier-updates.json').write_text(json.dumps(frontier_updates,indent=2,ensure_ascii=False)+'\n')
    packet_dir=PUBLIC/'data/agent-packets'; packet_dir.mkdir(parents=True,exist_ok=True); packet_index=[]
    for q in quests:
        pkt=r11_agent_packet(q); fn=q['id']+'.json'; (packet_dir/fn).write_text(json.dumps(pkt,indent=2,ensure_ascii=False)+'\n'); packet_index.append({'problem_id':q['id'],'program_id':q['mission_id'],'title':q['title'],'frontier_priority':pkt['frontier'].get('priority','P3'),'url':fn})
    (packet_dir/'index.json').write_text(json.dumps({'schema':'nsc-agent-packet-index-v1','reference_semantics':'URLs resolve relative to this index document.','packets':packet_index},indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/quests.json').write_text(json.dumps(quests_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/task-ladder.json').write_text(json.dumps(task_ladder,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/taxonomy.json').write_text((CONTENT/'taxonomy.json').read_text())
    (PUBLIC/'data/claims.json').write_text(json.dumps(claims_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/governance.json').write_text(json.dumps(governance,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/founding-sprint.json').write_text(json.dumps(founding_sprint,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/reviews.json').write_text(json.dumps(reviews,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/public-ssot.json').write_text(json.dumps(public_ssot,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/authority-map.json').write_text((CONTENT/'authority_map.json').read_text())
    (PUBLIC/'data/release-policy.json').write_text((CONTENT/'release_policy.json').read_text())
    caps=capabilities(); (PUBLIC/'data/capabilities.json').write_text(json.dumps({'schema':'nsc-capabilities-v1','capabilities':caps},indent=2,ensure_ascii=False)+'\n')
    discovery={'schema':'commons-discovery-v4','project':project['project_id'],'name':project['name'],'reference_semantics':'Resolve every relative reference against this discovery document URL.','discovery_contract':registry.get('discovery_contract',{}),**{k:deployed_ref('.well-known/commons.json',v) for k,v in registry['machine_endpoints'].items()},**{f'human_{k}':deployed_ref('.well-known/commons.json',v) for k,v in registry['human_routes'].items()}}
    openapi_paths={}
    for key,logical in registry['machine_endpoints'].items():
        suffix=Path(logical).suffix.lower()
        mime='application/json' if suffix=='.json' else ('text/markdown' if suffix=='.md' else 'text/plain')
        openapi_paths[logical]={'get':{'operationId':'get_'+re.sub(r'[^a-zA-Z0-9_]+','_',key),'summary':'Read public Commons resource: '+key,'responses':{'200':{'description':'Static public resource','content':{mime:{}}}}}}
    openapi_doc={'openapi':'3.1.2','info':{'title':'Navier-Stokes Commons public machine surface','version':project['release'],'description':'Read-only static discovery and research-coordination resources. Collaboration transactions are forge-mediated.'},'servers':[{'url':SITE_URL or '.'}],'paths':openapi_paths}
    openapi_out=PUBLIC/registry['machine_endpoints']['openapi'].lstrip('/')
    openapi_out.parent.mkdir(parents=True,exist_ok=True); openapi_out.write_text(json.dumps(openapi_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'.well-known/commons.json').write_text(json.dumps(discovery,indent=2)+'\n')
    skill=(ROOT/'SKILL.md')
    if skill.exists(): shutil.copy2(skill,PUBLIC/'SKILL.md')
    start=(ROOT/'start.md')
    if start.exists(): shutil.copy2(start,PUBLIC/'start.md')
    contrib=(ROOT/'CONTRIBUTING.md')
    if contrib.exists(): shutil.copy2(contrib,PUBLIC/'CONTRIBUTING.md')
    for name in ['AGENTS.md','GOVERNANCE.md','REVIEW_POLICY.md','MISSION_POLICY.md','COMMUNITY_STANDARDS.md','DCO.md','ROADMAP.md','PUBLIC_SSOT.json']:
        src=ROOT/name
        if src.exists(): shutil.copy2(src,PUBLIC/name)
    for dirname in ['schemas','references']:
        src=ROOT/dirname; dst=PUBLIC/dirname
        if src.exists(): shutil.copytree(src,dst,dirs_exist_ok=True)
    # Agent-context projections are generated from the same public source tree on every build.
    ep={k:v.lstrip('/') for k,v in registry['machine_endpoints'].items()}
    index_lines=[
      '# Navier-Stokes Commons agent index','',
      f'Release: {project["release"]}',
      f'Research programs: {len(missions)}; bounded problems: {len(quests)}; initial review portfolio: {len(founding_sprint["quest_ids"])}.','',
      f"- Start: {ep['agent_start']} - minimal cold-start protocol",
      f"- Skill: {ep['agent_skill']} - execution and evidence contract",
      f"- Discovery: {ep['discovery']} - machine endpoint registry",
      f"- OpenAPI: {ep['openapi']} - standard description of static GET resources",
      f"- Research problems: {ep['quests']} - bounded reviewable work units (legacy endpoint name retained)",
      f"- Claims: {ep['claims']} - evidence/status records and derived quest links",
      f"- Sources: {ep['sources']} - public source registry",
      f"- Capabilities: {ep['capabilities']} - derived collaboration capabilities",
      f"- Authority map: {ep['authority_map']} - canonical vs derived vs independent-oracle facts",
      f"- Simulations: {ep['simulations']} - declared scientific interaction models",
      f"- Actions: {ep['actions']} - forge-mediated collaboration transactions",
      f"- Benchmarks: {ep['reference_benchmarks']} - pre-registered comparison corpus",
      f"- Research context: {ep['research_context']} - claim scope, lineage, and attributed provenance accounts",
      f"- Clay A/B/C/D status: {ep['clay_problem_status']} - exact branch semantics and publication/recognition state",
      f"- Research frontier graph: {ep['frontier_graph']} - prioritized programs, dependencies, review classes",
      f"- Agent work packets: {ep['agent_packets']} - bounded problem packets derived from canonical work records",
      f"- Governance: {ep['governance']} - roles and decision rules",
      f"- Initial review portfolio: {ep['founding_sprint']} - bootstrap independent-evidence set (legacy endpoint retained)",'',
      f"Never infer a stronger claim status than {ep['claims']}. Attempts are non-exclusive. Negative results and falsifications are valid when they satisfy the quest acceptance contract."
    ]
    (PUBLIC/'llms.txt').write_text('\n'.join(index_lines)+'\n')
    full_parts=['\n'.join(index_lines)]
    for rel in ['start.md','SKILL.md','AGENTS.md','GOVERNANCE.md','MISSION_POLICY.md','REVIEW_POLICY.md','CONTRIBUTING.md','PUBLIC_SSOT.json']:
        src=PUBLIC/rel
        if src.exists(): full_parts.append(f'\n\n# FILE: {rel}\n\n'+src.read_text())
    for rel in ['data/capabilities.json','data/claims.json','data/quests.json','data/sources.json','data/founding-sprint.json','data/authority-map.json','data/simulations.json','data/actions.json','data/reference-benchmarks.json','data/research-context.json','data/clay-problem-status.json','data/frontier-graph.json','data/frontier-updates.json','data/agent-packets/index.json']:
        src=PUBLIC/rel; full_parts.append(f'\n\n# FILE: {rel}\n\n'+src.read_text())
    (PUBLIC/'llms-full.txt').write_text(''.join(full_parts))
    if SITE_URL:
        sm=[]
        for hp in sorted(PUBLIC.rglob('*.html')):
            rp=hp.relative_to(PUBLIC).as_posix()
            route=rp[:-10] if rp.endswith('index.html') else rp
            sm.append(SITE_URL+'/'+route)
        xml='<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n'+''.join('<url><loc>'+html.escape(u)+'</loc></url>\n' for u in sm)+'</urlset>\n'
        (PUBLIC/'sitemap.xml').write_text(xml)
        (PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE_URL+'/sitemap.xml\n')
    else:
        (PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\n')

def main():
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    (PUBLIC/'assets').mkdir()
    shutil.copy2(ASSETS/'style.css',PUBLIC/'assets/style.css'); shutil.copy2(ASSETS/'site.js',PUBLIC/'assets/site.js')
    if (ASSETS/'fonts').is_dir(): shutil.copytree(ASSETS/'fonts',PUBLIC/'assets/fonts',dirs_exist_ok=True)
    root_page()
    for loc in project['locales']:
        home_page(loc); missions_page(loc); guide_page(loc); known_page(loc); contribute_page(loc); activity_page(loc); sources_page(loc); agents_page(loc); accessibility_page(loc)
        for m in missions: mission_page(loc,m)
    quests_page()
    for q in quests: quest_page(q)
    sprint_page(); governance_page(); claims_page(); benchmarks_page(); reference_flow_page(); r6_context_page(); r11_frontier_page(); r11_review_page(); r11_explain_page(); r13_math_page()
    machine_files()
    print(f'Built {sum(1 for _ in PUBLIC.rglob("*.html"))} HTML pages in {PUBLIC}')

if __name__=='__main__': main()
