(() => {
  'use strict';
  const root = document.documentElement;
  root.classList.add('enhanced');
  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)');
  const safeStorage = {
    get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set(k,v) { try { localStorage.setItem(k,v); } catch (_) {} }
  };

  const themeButtons = [...document.querySelectorAll('[data-theme-toggle]')];
  const themes = ['system','light','dark'];
  const applyTheme = (theme,persist=false) => {
    if (!themes.includes(theme)) theme='system';
    root.dataset.theme=theme;
    for (const button of themeButtons) {
      const labels = {
        system: button.dataset.labelSystem || 'System',
        light: button.dataset.labelLight || 'Light',
        dark: button.dataset.labelDark || 'Dark'
      };
      const label=button.querySelector('[data-theme-label]');
      if (label) label.textContent=labels[theme];
    }
    if (persist) safeStorage.set('nsc-theme',theme);
  };
  if (themeButtons.length) {
    for (const button of themeButtons) {
      button.hidden=false;
      button.addEventListener('click', () => {
        const current=root.dataset.theme || 'system';
        applyTheme(themes[(themes.indexOf(current)+1)%themes.length],true);
      });
    }
    applyTheme(safeStorage.get('nsc-theme') || 'system');
  }

  const filterPanel=document.querySelector('[data-filter-panel]');
  const input=document.querySelector('[data-mission-filter]');
  const cards=[...document.querySelectorAll('[data-mission-card]')];
  const sections=[...document.querySelectorAll('[data-category-section]')];
  const status=document.querySelector('[data-filter-status]');
  const noResults=document.querySelector('[data-no-results]');
  const chips=[...document.querySelectorAll('[data-category-filter]')];
  let selectedCategory='all';
  const normalize=s=>(s||'').toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'');
  const runFilter=()=>{
    const q=normalize(input?.value.trim() || ''); let shown=0;
    for (const card of cards) {
      const hit=(!q || normalize(card.dataset.search).includes(q)) && (selectedCategory==='all' || card.dataset.category===selectedCategory);
      card.hidden=!hit; if(hit) shown++;
    }
    for (const section of sections) section.hidden=![...section.querySelectorAll('[data-mission-card]')].some(c=>!c.hidden);
    if(noResults) noResults.hidden=shown!==0;
    if(status) status.textContent=(q || selectedCategory!=='all') ? `${shown} / ${cards.length}` : '';
  };
  if(filterPanel && cards.length) {
    filterPanel.hidden=false;
    input?.addEventListener('input',runFilter,{passive:true});
    chips.forEach(chip=>chip.addEventListener('click',()=>{
      selectedCategory=chip.dataset.categoryFilter || 'all';
      chips.forEach(c=>{ const active=c===chip; c.classList.toggle('is-active',active); c.setAttribute('aria-pressed',active?'true':'false'); });
      runFilter();
    }));
    runFilter();
  }

  // Motion is finite and attached to real content. Content is never hidden waiting for JS.
  const reveal=[...document.querySelectorAll('[data-reveal]')];
  if (!reduced?.matches && 'IntersectionObserver' in window) {
    const seen=new WeakSet();
    const io=new IntersectionObserver(entries=>{
      for(const e of entries) if(e.isIntersecting && !seen.has(e.target)) {
        const el=e.target; seen.add(el); io.unobserve(el);
        try { el.animate([{opacity:.35,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:320,easing:'cubic-bezier(.2,.8,.2,1)'}); } catch(_) {}
      }
    },{rootMargin:'0px 0px -3% 0px',threshold:.03});
    reveal.forEach(el=>io.observe(el));
  }

  // Briefly stage the terms of the real equation; no pseudo-scientific animation is generated.
  if (!reduced?.matches) {
    [...document.querySelectorAll('[data-eq-term]')].forEach((term,i)=>{
      try { term.animate([{opacity:.45},{opacity:1}],{duration:260,delay:70*i,easing:'ease-out'}); } catch(_) {}
    });
  }


  // Source-backed asymptotic scaling laboratory.
  const lab=document.querySelector('[data-scaling-lab]');
  if (lab) {
    const controls=lab.querySelector('[data-lab-controls]');
    const kInput=lab.querySelector('[data-tau-k]');
    const hInput=lab.querySelector('[data-h]');
    const kOut=lab.querySelector('[data-k-output]');
    const hOut=lab.querySelector('[data-h-output]');
    const tauOut=lab.querySelector('[data-tau-output]');
    const aspectOut=lab.querySelector('[data-aspect-output]');
    const speedOut=lab.querySelector('[data-speed-output]');
    const energyOut=lab.querySelector('[data-energy-output]');
    const ellipse=lab.querySelector('[data-core-ellipse]');
    const cursor=lab.querySelector('[data-cursor]');
    const play=lab.querySelector('[data-lab-play]');
    const tableValues=[...lab.querySelectorAll('[data-scale-value]')];
    const asciiLive=lab.querySelector('[data-ascii-live]');
    const curves=[...lab.querySelectorAll('[data-curve]')];
    if (controls && kInput && hInput) controls.hidden=false;
    let exponentCoeffs={}; try { exponentCoeffs=JSON.parse(lab.dataset.exponents||'{}'); } catch(_) {}
    const exponent=(id,h)=>{ const c=exponentCoeffs[id]; return c ? Number(c[0])+Number(c[1])*h : NaN; };
    const log10Value=(id,k,h)=>-k*exponent(id,h);
    const fmtPow=x=>Math.abs(x)<.005?'1':`10^${x.toFixed(2)}`;
    const asciiTrace=(k,h)=>{
      const fmt=(id,label)=>{
        const x=log10Value(id,k,h);
        const arrow=x>=0?'>':'<';
        const n=Math.abs(x)<.2?1:Math.max(1,Math.min(22,Math.round(Math.abs(x)/2)));
        const bar=Math.abs(x)<.2?'.':arrow.repeat(n);
        return `${label.padEnd(10)} 10^${x.toFixed(2).padStart(7)}  ${bar}`;
      };
      return [
        `tau        10^-${k.toFixed(k%1?2:0)}`,
        '',
        fmt('ell_r','ell_r'),
        fmt('ell_z','ell_z'),
        fmt('u_theta','|u_theta|'),
        fmt('energy','E_core'),
        fmt('re_theta','Re_theta')
      ].join('\n');
    };
    const curvePath=(id,h)=>{
      const pts=[];
      for(let i=0;i<=80;i+=2){
        const x=48+(i/80)*452;
        const y0=log10Value(id,i,h);
        const y=118-y0*2.25;
        pts.push(`${i?'L':'M'}${x.toFixed(1)} ${Math.max(20,Math.min(216,y)).toFixed(1)}`);
      }
      return pts.join(' ');
    };
    let raf=0,playing=false,last=0;
    const render=()=>{
      const k=Number(kInput.value),h=Number(hInput.value),tau=Math.pow(10,-k);
      const aspect=Math.pow(tau,-h);
      const logSpeed=log10Value('u_theta',k,h),logEnergy=log10Value('energy',k,h);
      if(kOut) kOut.value=k.toFixed(k%1?2:0);
      if(hOut) hOut.value=h.toFixed(4);
      if(tauOut) tauOut.textContent=`10^-${k.toFixed(k%1?2:0)}`;
      if(aspectOut) aspectOut.textContent=aspect.toFixed(aspect<10?2:1);
      if(speedOut) speedOut.textContent=fmtPow(logSpeed);
      if(energyOut) energyOut.textContent=fmtPow(logEnergy);
      if(ellipse){
        const rx=Math.max(22,92/Math.sqrt(aspect));
        const ry=Math.min(138,92*Math.sqrt(aspect));
        ellipse.setAttribute('rx',rx.toFixed(2)); ellipse.setAttribute('ry',ry.toFixed(2));
      }
      if(cursor){ const x=48+(k/80)*452; cursor.setAttribute('x1',x); cursor.setAttribute('x2',x); }
      curves.forEach(c=>c.setAttribute('d',curvePath(c.dataset.curve,h)));
      tableValues.forEach(td=>td.textContent=fmtPow(log10Value(td.dataset.scaleValue,k,h)));
      if(asciiLive) asciiLive.textContent=asciiTrace(k,h);
    };
    kInput?.addEventListener('input',render,{passive:true});
    hInput?.addEventListener('input',render,{passive:true});
    const stop=()=>{playing=false; if(raf) cancelAnimationFrame(raf); raf=0; if(play) play.textContent=play.dataset.playLabel || 'Play';};
    const tick=ts=>{
      if(!playing) return;
      if(!last) last=ts;
      const dt=Math.min(80,ts-last); last=ts;
      kInput.value=String(Math.min(80,Number(kInput.value)+dt*.006)); render();
      if(Number(kInput.value)>=80){stop();return;} raf=requestAnimationFrame(tick);
    };
    const applyMotionPreference=()=>{if(play){play.hidden=Boolean(reduced?.matches);play.disabled=Boolean(reduced?.matches);}if(reduced?.matches)stop();};
    applyMotionPreference(); reduced?.addEventListener?.('change',applyMotionPreference);
    play?.addEventListener('click',()=>{
      if(playing){stop();return;}
      if(reduced?.matches) return;
      if(Number(kInput.value)>=79.9) kInput.value='0.25';
      playing=true; last=0; play.textContent=play.dataset.pauseLabel || 'Pause'; raf=requestAnimationFrame(tick);
    });
    document.addEventListener('visibilitychange',()=>{if(document.hidden) stop();});
    render();
  }


  // Exact 2D Taylor vortex reference flow. It never autoplays and has a static no-JS fallback.
  const chamber=document.querySelector('[data-flow-chamber]');
  if(chamber){
    const frame=chamber.querySelector('[data-flow-canvas-frame]');
    const canvas=chamber.querySelector('[data-flow-canvas]');
    const controls=chamber.querySelector('[data-flow-controls]');
    const tInput=chamber.querySelector('[data-flow-t]');
    const nuInput=chamber.querySelector('[data-flow-nu]');
    const tOut=chamber.querySelector('[data-flow-t-output]');
    const nuOut=chamber.querySelector('[data-flow-nu-output]');
    const state=chamber.querySelector('[data-flow-state]');
    const play=chamber.querySelector('[data-flow-play]');
    const saveData=Boolean(navigator.connection && navigator.connection.saveData);
    if(frame && canvas && controls && tInput && nuInput){ frame.hidden=false; controls.hidden=false; }
    const ctx=canvas?.getContext('2d',{alpha:false});
    if(ctx) chamber.classList.add('flow-renderer-ready');
    const A=Number(chamber.dataset.a||1);
    let flowModel={}; try { flowModel=JSON.parse(chamber.dataset.flowModel||'{}'); } catch(_) {}
    const expr=(node,vars,params)=>{
      if(!node||typeof node!=='object') return NaN;
      if(node.type==='number') return Number(node.value);
      if(node.type==='param') return Number(params[node.name]);
      if(node.type==='var') return Number(vars[node.name]);
      const args=(node.args||[]).map(n=>expr(n,vars,params));
      if(node.op==='add') return args.reduce((a,b)=>a+b,0);
      if(node.op==='mul') return args.reduce((a,b)=>a*b,1);
      if(node.op==='neg') return -args[0];
      if(node.op==='exp') return Math.exp(args[0]);
      if(node.op==='sin') return Math.sin(args[0]);
      if(node.op==='cos') return Math.cos(args[0]);
      if(node.op==='pow') return Math.pow(args[0],args[1]);
      return NaN;
    };
    const velocity=(x,y,t,nu)=>{ const vars={x,y,t},params={A,nu}; return [expr(flowModel.u_x,vars,params),expr(flowModel.u_y,vars,params)]; };
    const energy=(t,nu)=>expr(flowModel.mean_kinetic_energy,{x:0,y:0,t},{A,nu});
    const particles=[]; const cols=saveData?10:18, rows=saveData?7:12;
    const reseedParticles=()=>{particles.length=0;for(let j=0;j<rows;j++)for(let i=0;i<cols;i++)particles.push({x:(i+.37*(j%2))/cols*2*Math.PI,y:(j+.5)/rows*2*Math.PI});};
    reseedParticles();
    let playing=false,raf=0,last=0,lastLive=-1;
    const draw=(announce=false)=>{
      if(!ctx||!canvas) return;
      const t=Number(tInput.value),nu=Number(nuInput.value),w=canvas.width,h=canvas.height;
      ctx.fillStyle='#061416';ctx.fillRect(0,0,w,h);
      const N=saveData?15:23; ctx.lineWidth=1;
      for(let j=0;j<N;j++) for(let i=0;i<N;i++){
        const x=(i+.5)/N*2*Math.PI,y=(j+.5)/N*2*Math.PI,[u,v]=velocity(x,y,t,nu),m=Math.hypot(u,v);
        const px=(i+.5)/N*w,py=(j+.5)/N*h,scale=10+18*m,ex=px+u*scale,ey=py-v*scale;
        ctx.strokeStyle=`rgba(133,230,215,${0.16+0.52*Math.min(1,m)})`;ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(ex,ey);ctx.stroke();
      }
      particles.forEach((pt,k)=>{const px=pt.x/(2*Math.PI)*w,py=pt.y/(2*Math.PI)*h;ctx.fillStyle=k%3===0?'rgba(255,211,117,.9)':'rgba(238,247,244,.66)';ctx.beginPath();ctx.arc(px,py,k%3===0?2.2:1.3,0,Math.PI*2);ctx.fill();});
      if(tOut)tOut.value=t.toFixed(2);if(nuOut)nuOut.value=nu.toFixed(3);
      if(state&&announce)state.textContent=`At t=${t.toFixed(2)}, nu=${nu.toFixed(3)}, mean kinetic energy is ${energy(t,nu).toFixed(4)}. The periodic field is divergence-free and consists of four counter-rotating cells.`;
    };
    const stepParticles=(dtModel,t0,nu)=>{particles.forEach(pt=>{const [u0,v0]=velocity(pt.x,pt.y,t0,nu);const xm=(pt.x+.5*u0*dtModel+2*Math.PI)%(2*Math.PI),ym=(pt.y+.5*v0*dtModel+2*Math.PI)%(2*Math.PI);const [um,vm]=velocity(xm,ym,t0+.5*dtModel,nu);pt.x=(pt.x+um*dtModel+2*Math.PI)%(2*Math.PI);pt.y=(pt.y+vm*dtModel+2*Math.PI)%(2*Math.PI);});};
    tInput?.addEventListener('input',()=>{reseedParticles();draw(true);},{passive:true});nuInput?.addEventListener('input',()=>{reseedParticles();draw(true);},{passive:true});
    const stopFlow=()=>{playing=false;if(raf)cancelAnimationFrame(raf);raf=0;if(play){play.textContent=play.dataset.playLabel||'Play';play.setAttribute('aria-pressed','false');}};
    const flowTick=ts=>{if(!playing)return;if(!last){last=ts;raf=requestAnimationFrame(flowTick);return;}const wallDt=Math.min(.035,(ts-last)/1000);last=ts;const t0=Number(tInput.value),tMax=Number(tInput.max),nu=Number(nuInput.value),dtModel=Math.min(wallDt*.6,tMax-t0);if(dtModel<=0){stopFlow();draw(true);return;}stepParticles(dtModel,t0,nu);tInput.value=String(t0+dtModel);const announce=ts-lastLive>750;draw(announce);if(announce)lastLive=ts;if(Number(tInput.value)>=tMax-1e-9){stopFlow();draw(true);return;}raf=requestAnimationFrame(flowTick);};
    const applyFlowMotionPreference=()=>{if(play){play.hidden=Boolean(reduced?.matches);play.disabled=Boolean(reduced?.matches);}if(reduced?.matches)stopFlow();};
    applyFlowMotionPreference(); reduced?.addEventListener?.('change',applyFlowMotionPreference);
    play?.addEventListener('click',()=>{if(playing){stopFlow();return;}if(reduced?.matches)return;if(Number(tInput.value)>=Number(tInput.max)-1e-9){tInput.value=tInput.min;reseedParticles();draw(true);}playing=true;last=0;lastLive=0;play.textContent=play.dataset.pauseLabel||'Pause';play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(flowTick);});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)stopFlow();});
    draw(true);
  }

})();


/* NSC R5 IMMERSIVE VORTEX, retained by R7: source-constrained schematic, derived scale HUD; device-aware bounded runtime. */
(() => {
  'use strict';
  const canvas=document.querySelector('[data-vortex-canvas]');
  if(!canvas) return;
  const stage=canvas.closest('[data-vortex-stage]');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const saveData=Boolean(navigator.connection?.saveData);
  const controls=stage?.querySelector('[data-vortex-controls]');
  const probe=stage?.querySelector('[data-flow-probe]');
  const kInput=stage?.querySelector('[data-k]');
  const hInput=stage?.querySelector('[data-h]');
  const playBtn=stage?.querySelector('[data-play]');
  const frameBtn=stage?.querySelector('[data-frame-toggle]');
  const modeLabel=stage?.querySelector('[data-mode-label]');
  const outTau=stage?.querySelector('[data-tau-out]'),outR=stage?.querySelector('[data-r-out]'),outZ=stage?.querySelector('[data-z-out]'),outU=stage?.querySelector('[data-u-out]'),outE=stage?.querySelector('[data-e-out]'),outAspect=stage?.querySelector('[data-aspect-out]');
  if(controls) controls.hidden=false;

  let k=Number(kInput?.value||14),h=Number(hInput?.value||.005),yaw=-.28,pitch=.10,zoom=5.8,normalize=true;
  let pointer=[3,3],pointerPx=[-1000,-1000],dragging=false,px=0,py=0;
  let playing=false,playStart=0,playFrom=k,raf=0,visible=true,ambient=!reduced.matches,ambientUserPaused=false;
  const introStart=performance.now(),introMs=3800;
  const introTime=now=>{if(reduced.matches)return 0;const intro=Math.min(3.8,Math.max(0,(now-introStart)/1000));const after=Math.max(0,now-introStart-introMs)/1000;return intro+after*.16;};
  const introActive=now=>!reduced.matches && now-introStart<introMs;
  const schedule=()=>{if(visible&&!raf)raf=requestAnimationFrame(frame);};
  const fmt=(x,d=1)=>`10^${x.toFixed(d)}`;
  function stats(){
    const kd=k.toFixed(k%1?1:0);
    if(outTau)outTau.textContent=`10^-${kd}`;
    if(outR)outR.textContent=fmt(-.5*k);
    if(outZ)outZ.textContent=fmt(-(0.5-h)*k);
    if(outU)outU.textContent=fmt((.5+h)*k);
    if(outE)outE.textContent=fmt(-(.5-3*h)*k);
    if(outAspect)outAspect.textContent=fmt(h*k,2);
  }
  function updateProbe(e){
    const r=canvas.getBoundingClientRect();
    const x=e.clientX-r.left,y=e.clientY-r.top;
    pointerPx=[x,y]; pointer=[x/r.width*2-1,1-y/r.height*2];
    if(probe){probe.style.setProperty('--probe-x',x+'px');probe.style.setProperty('--probe-y',y+'px');}
    if(stage)stage.dataset.pointerActive='true'; schedule();
  }
  function clearProbe(){pointer=[3,3];pointerPx=[-1000,-1000];if(stage)stage.dataset.pointerActive='false';schedule();}
  function setPlaying(v){
    playing=v&&!reduced.matches;
    if(playing){playStart=performance.now();playFrom=k;}
    if(playBtn){playBtn.setAttribute('aria-pressed',String(playing));playBtn.textContent=playing?(playBtn.dataset.pauseLabel||'Pause sweep'):(playBtn.dataset.playLabel||'Play sweep');}
    schedule();
  }
  function advancePlay(now){
    if(!playing)return false;
    const q=Math.min(1,(now-playStart)/7000);
    const eased=1-Math.pow(1-q,2.25);
    k=playFrom+(60-playFrom)*eased;
    if(kInput)kInput.value=String(k);
    stats();
    if(q>=1)setPlaying(false);
    return q<1;
  }

  canvas.addEventListener('pointermove',e=>{updateProbe(e);if(dragging){yaw-=(e.clientX-px)*.006;pitch=Math.max(-1.05,Math.min(1.05,pitch-(e.clientY-py)*.0045));px=e.clientX;py=e.clientY;schedule();}});
  canvas.addEventListener('pointerdown',e=>{dragging=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture?.(e.pointerId);schedule();});
  canvas.addEventListener('pointerup',e=>{dragging=false;try{canvas.releasePointerCapture?.(e.pointerId)}catch{};schedule();});
  canvas.addEventListener('pointercancel',()=>{dragging=false;clearProbe();});
  canvas.addEventListener('pointerleave',()=>{dragging=false;clearProbe();});
  canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(3.7,Math.min(9.4,zoom+e.deltaY*.004));schedule();},{passive:false});
  kInput?.addEventListener('input',()=>{k=Number(kInput.value);setPlaying(false);stats();schedule();},{passive:true});
  hInput?.addEventListener('input',()=>{h=Number(hInput.value);stats();schedule();},{passive:true});
  playBtn?.addEventListener('click',()=>{if(reduced.matches)return;if(playing){setPlaying(false);return;}if(k>59.5){k=.5;if(kInput)kInput.value=String(k);stats();}setPlaying(true);});
  frameBtn?.addEventListener('click',()=>{normalize=!normalize;frameBtn.textContent=normalize?(frameBtn.dataset.normalizedLabel||'Normalized core frame'):(frameBtn.dataset.labLabel||'Laboratory frame');if(modeLabel)modeLabel.textContent=normalize?(stage.dataset.modeNormalized||'NORMALIZED FOLLOW-CORE VIEW'):(stage.dataset.modeLaboratory||'LOG-COMPRESSED LABORATORY VIEW');schedule();});
  const applyMotionPreference=()=>{if(reduced.matches){setPlaying(false);ambient=false;}else if(!ambientUserPaused){ambient=true;}if(playBtn){playBtn.disabled=Boolean(reduced.matches);playBtn.setAttribute('aria-disabled',String(Boolean(reduced.matches)));}schedule();};
  applyMotionPreference(); reduced.addEventListener?.('change',applyMotionPreference);
  window.addEventListener('nsc:ambient-motion',e=>{ambientUserPaused=!Boolean(e.detail?.active);ambient=Boolean(e.detail?.active)&&!reduced.matches;schedule();});
  document.addEventListener('visibilitychange',()=>{visible=!document.hidden;if(!visible&&raf){cancelAnimationFrame(raf);raf=0;}else schedule();});

  const lowPower=saveData||matchMedia('(max-width: 680px)').matches||((navigator.deviceMemory||8)<=4)||((navigator.hardwareConcurrency||8)<=4);
  const STREAMS=lowPower?64:112,STEPS=lowPower?48:70,N=STREAMS*STEPS;
  const seeds=Array.from({length:STREAMS},(_,i)=>({a:(i*2.3999632297)%(Math.PI*2),layer:(i%19)/18,jitter:Math.sin(i*12.9898)*.17,family:i%7,speed:.42+(i%13)/24}));
  const gl=canvas.getContext('webgl2',{antialias:true,alpha:false,powerPreference:lowPower?'low-power':'high-performance'});
  let renderer,contextLost=false;
  if(gl){
    canvas.addEventListener('webglcontextlost',e=>{
      e.preventDefault();
      if(raf){cancelAnimationFrame(raf);raf=0;}
      playing=false;contextLost=true;
      stage.dataset.renderer='static';
      stage.dataset.rendererReady='false';
      stage.classList.remove('vortex-renderer-ready');
    },{once:true});
  }

  function geomPoint(seed,j,time){
    const u=j/(STEPS-1),zz=u*2-1,s=Math.max(0,Math.min(1,k/60));
    const turns=1.25+19*Math.pow(s,.72); // intentionally strong logarithmic-time encoding
    const aspect=Math.pow(10,k*h),axial=1+.78*Math.log10(aspect+1);
    const waist=.32+.68*Math.pow(Math.abs(zz),.70);
    const layer=.32+1.48*(.15+.85*seed.layer);
    const radial=layer*waist*(1-.30*s*Math.exp(-zz*zz*3));
    const handed=seed.family<3?1:-1;
    const theta=seed.a+handed*turns*(zz+.23*Math.sin(zz*Math.PI))*Math.PI+time*seed.speed*(.35+2.8*s);
    let x=radial*Math.cos(theta),z=radial*Math.sin(theta),y=zz*2.3*axial;
    const flare=.15*Math.sin(theta*.7+seed.jitter*8)*(1-Math.exp(-Math.abs(zz)*2));x*=1+flare;z*=1-flare*.7;
    if(!normalize){const pr=Math.pow(10,-Math.min(7,.11*k)),pz=Math.pow(10,-Math.min(6,.09*k));x*=pr;z*=pr;y*=pz;}
    return [x,y,z,radial,s];
  }

  if(gl){
    const VERT=`#version 300 es\nprecision highp float;in vec3 aPos;in float aHeat;in float aSize;uniform mat4 uMVP;uniform vec2 uPointer;uniform float uDpr;out float vHeat;out float vLens;out float vDepth;void main(){vec4 clip=uMVP*vec4(aPos,1.0);gl_Position=clip;vec2 ndc=clip.xy/max(clip.w,.001);float d=distance(ndc,uPointer);vLens=exp(-24.0*d*d);vHeat=aHeat;vDepth=clamp(1.0-clip.z/clip.w,0.0,1.0);float persp=clamp(2.1/clip.w,.45,2.3);gl_PointSize=(aSize+5.2*vLens)*uDpr*persp;}`;
    const FRAG=`#version 300 es\nprecision highp float;in float vHeat;in float vLens;in float vDepth;uniform int uMode;out vec4 outColor;vec3 ramp(float t){vec3 teal=vec3(.10,.90,.92),blue=vec3(.13,.40,1.),amber=vec3(1.,.40,.09);return t<.58?mix(teal,blue,t/.58):mix(blue,amber,(t-.58)/.42);}void main(){vec3 c=ramp(clamp(vHeat+.20*vLens,0.,1.));if(uMode==0){vec2 q=gl_PointCoord-.5;float r=length(q)*2.;if(r>1.)discard;float glow=pow(smoothstep(1.,0.,r),1.6);float a=(.08+.76*glow)*(.40+.60*vDepth)+.52*vLens*glow;outColor=vec4(c,a);}else{outColor=vec4(c,.055+.30*vHeat+.13*vDepth+.11*vLens);}}`;
    const compile=(type,src)=>{const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(sh));return sh;};
    const prog=gl.createProgram();gl.attachShader(prog,compile(gl.VERTEX_SHADER,VERT));gl.attachShader(prog,compile(gl.FRAGMENT_SHADER,FRAG));gl.linkProgram(prog);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(prog));gl.useProgram(prog);
    const L={pos:gl.getAttribLocation(prog,'aPos'),heat:gl.getAttribLocation(prog,'aHeat'),size:gl.getAttribLocation(prog,'aSize'),mvp:gl.getUniformLocation(prog,'uMVP'),pointer:gl.getUniformLocation(prog,'uPointer'),dpr:gl.getUniformLocation(prog,'uDpr'),mode:gl.getUniformLocation(prog,'uMode')};
    const bPos=gl.createBuffer(),bHeat=gl.createBuffer(),bSize=gl.createBuffer(),pos=new Float32Array(N*3),heat=new Float32Array(N),sizes=new Float32Array(N);
    const perspective=(fovy,aspect,near,far)=>{const f=1/Math.tan(fovy/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]);};
    const mul=(a,b)=>{const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++){let v=0;for(let j=0;j<4;j++)v+=a[j*4+r]*b[c*4+j];o[c*4+r]=v;}return o;};
    const lookAt=(eye,target,up)=>{let zx=eye[0]-target[0],zy=eye[1]-target[1],zz=eye[2]-target[2],zl=Math.hypot(zx,zy,zz)||1;zx/=zl;zy/=zl;zz/=zl;let xx=up[1]*zz-up[2]*zy,xy=up[2]*zx-up[0]*zz,xz=up[0]*zy-up[1]*zx,xl=Math.hypot(xx,xy,xz)||1;xx/=xl;xy/=xl;xz/=xl;let yx=zy*xz-zz*xy,yy=zz*xx-zx*xz,yz=zx*xy-zy*xx;return new Float32Array([xx,yx,zx,0,xy,yy,zy,0,xz,yz,zz,0,-(xx*eye[0]+xy*eye[1]+xz*eye[2]),-(yx*eye[0]+yy*eye[1]+yz*eye[2]),-(zx*eye[0]+zy*eye[1]+zz*eye[2]),1]);};
    renderer=(now)=>{
      const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,lowPower?1.25:1.7),w=Math.max(1,Math.floor(r.width*dpr)),hh=Math.max(1,Math.floor(r.height*dpr));if(canvas.width!==w||canvas.height!==hh){canvas.width=w;canvas.height=hh;}gl.viewport(0,0,w,hh);
      const time=introTime(now);let q=0;for(let i=0;i<STREAMS;i++)for(let j=0;j<STEPS;j++){const [x,y,z,rad,s]=geomPoint(seeds[i],j,time);pos[q*3]=x;pos[q*3+1]=y;pos[q*3+2]=z;const core=Math.exp(-rad*.85);heat[q]=Math.min(1,.06+.62*s+.42*core+.04*Math.sin(seeds[i].a*3));sizes[q]=1.35+1.55*s+1.2*core+.35*(seeds[i].family%3);q++;}
      gl.bindBuffer(gl.ARRAY_BUFFER,bPos);gl.bufferData(gl.ARRAY_BUFFER,pos,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(L.pos);gl.vertexAttribPointer(L.pos,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,bHeat);gl.bufferData(gl.ARRAY_BUFFER,heat,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(L.heat);gl.vertexAttribPointer(L.heat,1,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,bSize);gl.bufferData(gl.ARRAY_BUFFER,sizes,gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(L.size);gl.vertexAttribPointer(L.size,1,gl.FLOAT,false,0,0);
      const ex=zoom*Math.cos(pitch)*Math.sin(yaw),ey=zoom*Math.sin(pitch),ez=zoom*Math.cos(pitch)*Math.cos(yaw),P=perspective(.72,w/hh,.1,60),V=lookAt([ex,ey,ez],[0,0,0],[0,1,0]),M=mul(P,V);
      gl.useProgram(prog);gl.uniformMatrix4fv(L.mvp,false,M);gl.uniform2f(L.pointer,pointer[0],pointer[1]);gl.uniform1f(L.dpr,dpr);gl.enable(gl.DEPTH_TEST);gl.depthMask(false);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);gl.clearColor(.008,.018,.026,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      gl.uniform1i(L.mode,1);for(let i=0;i<STREAMS;i++)gl.drawArrays(gl.LINE_STRIP,i*STEPS,STEPS);
      gl.uniform1i(L.mode,0);gl.drawArrays(gl.POINTS,0,N);
    };
    stage.dataset.renderer='webgl2';
  } else {
    const ctx=canvas.getContext('2d');if(!ctx)return;
    const palette=['#3ee3e7','#29a9e0','#2867d8','#113f91','#f29b4a','#e56d2e','#52d5d0'];
    const rot=(x,y,z)=>{const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);let X=cy*x+sy*z,Z=-sy*x+cy*z,Y=cp*y-sp*Z;Z=sp*y+cp*Z;return[X,Y,Z];};
    const project=(x,y,z,w,hh)=>{const [X,Y,Z]=rot(x,y,z),d=zoom-Z,f=Math.min(w,hh)*.88/d;return[w*.5+X*f,hh*.47-Y*f,d];};
    renderer=(now)=>{
      const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,lowPower?1.2:1.5),w=Math.max(1,Math.round(r.width)),hh=Math.max(1,Math.round(r.height));if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(hh*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(hh*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}ctx.fillStyle='#021017';ctx.fillRect(0,0,w,hh);
      const time=introTime(now),rows=[];for(let i=0;i<STREAMS;i++){const arr=[];for(let j=0;j<STEPS;j++){const [x,y,z,rad,s]=geomPoint(seeds[i],j,time),P=project(x,y,z,w,hh);arr.push([P[0],P[1],P[2],rad,s]);}rows.push([arr,seeds[i]]);}rows.sort((a,b)=>b[0][(STEPS/2)|0][2]-a[0][(STEPS/2)|0][2]);ctx.lineCap='round';ctx.lineJoin='round';
      for(const [arr,seed] of rows){ctx.beginPath();arr.forEach((P,j)=>j?ctx.lineTo(P[0],P[1]):ctx.moveTo(P[0],P[1]));const color=palette[seed.family%palette.length],s=arr[0][4];ctx.strokeStyle=color;ctx.globalAlpha=.13+.28*(1-seed.layer)+.12*s;ctx.lineWidth=.55+1.7*(1-seed.layer)+.8*s;ctx.shadowColor=color;ctx.shadowBlur=3+5*s;ctx.stroke();}
      ctx.shadowBlur=0;ctx.globalAlpha=1;ctx.globalCompositeOperation='lighter';for(const [arr] of rows){for(let j=0;j<arr.length;j+=4){const P=arr[j],lens=Math.exp(-((P[0]-pointerPx[0])**2+(P[1]-pointerPx[1])**2)/(78*78));if(lens<.04)continue;ctx.fillStyle=`rgba(153,248,255,${.18+.78*lens})`;ctx.beginPath();ctx.arc(P[0],P[1],1.1+3.2*lens,0,Math.PI*2);ctx.fill();}}ctx.globalCompositeOperation='source-over';if(pointerPx[0]>-1){const g=ctx.createRadialGradient(pointerPx[0],pointerPx[1],0,pointerPx[0],pointerPx[1],72);g.addColorStop(0,'rgba(120,245,255,.18)');g.addColorStop(1,'rgba(120,245,255,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(pointerPx[0],pointerPx[1],72,0,Math.PI*2);ctx.fill();}
    };
    stage.dataset.renderer='canvas2d';
  }

  function frame(now){
    raf=0;if(!visible||contextLost)return;
    const stillPlaying=advancePlay(now);renderer(now);stage.dataset.rendererReady='true';
    if(stillPlaying||introActive(now)||dragging||ambient) schedule();
  }
  stats();schedule();
})();

/* NSC R5 FINITE SCALE TRACE, retained by R7: nonessential ambient identity. */
(() => {
  'use strict';
  const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)');
  for (const trace of document.querySelectorAll('[data-scale-trace]')) {
    const out=trace.querySelector('[data-scale-trace-output]');
    const button=trace.querySelector('[data-scale-trace-toggle]');
    if(!out||!button) continue;
    button.hidden=false;
    const fmt=x=>'10^'+x.toFixed(2);
    let running=!(reduced?.matches),raf=0,start=0,K=2,H=.005;
    const render=()=>{
      const lr=.5*K,lz=(.5-H)*K,speed=(.5+H)*K,energy=(.5-3*H)*K;
      out.textContent=`τ ${fmt(-K)}   ℓr ${fmt(-lr)}   ℓz ${fmt(-lz)}   |uθ| ${fmt(speed)}   Ecore ${fmt(-energy)}`;
    };
    const stop=()=>{running=false;if(raf)cancelAnimationFrame(raf);raf=0;button.textContent=button.dataset.play||'play';};
    const tick=ts=>{
      if(!running)return;
      if(!start)start=ts;
      const q=Math.min(1,(ts-start)/4000);K=2+16*q;render();
      if(q>=1){running=false;button.textContent=button.dataset.replay||'replay';return;}
      raf=requestAnimationFrame(tick);
    };
    button.addEventListener('click',()=>{
      if(running){stop();return;}
      running=true;start=0;K=2;button.textContent=button.dataset.pause||'pause';raf=requestAnimationFrame(tick);
    });
    const applyMotion=()=>{
      if(reduced?.matches){stop();return;}
      if(!running&&K<=2.01){running=true;start=0;button.textContent=button.dataset.pause||'pause';raf=requestAnimationFrame(tick);}
    };
    if(reduced?.matches)button.textContent=button.dataset.play||'play';
    render();if(running)raf=requestAnimationFrame(tick);reduced?.addEventListener?.('change',applyMotion);
  }
})();

/* R14 ambient glyph field: decorative reference-flow-inspired UI layer; pointer perturbation is not simulated physics. */
/* ambient|| persistent normal-mode field; reduced motion remains authoritative. */
(() => {
  'use strict';
  let canvas=document.querySelector('[data-ambient-field]');
  if(!canvas) return;
  if(canvas.tagName!=='CANVAS'){const c=document.createElement('canvas');c.className=canvas.className;c.setAttribute('data-ambient-field','');c.setAttribute('aria-hidden','true');canvas.replaceWith(c);canvas=c;}
  const ctx=canvas.getContext('2d',{alpha:true});
  if(!ctx) return;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const saveData=Boolean(navigator.connection?.saveData);
  const storageKey='nsc-ambient-paused';
  let userPaused=false; try{userPaused=localStorage.getItem(storageKey)==='1';}catch(_){}
  let active=!reduced.matches&&!userPaused,visible=!document.hidden,raf=0,last=0,phase=0;
  let pointer={x:.72,y:.44,tx:.72,ty:.44,inside:false};
  const glyphs=['→','↗','↑','↖','←','↙','↓','↘'];
  const lowPower=saveData||matchMedia('(max-width:680px)').matches||((navigator.deviceMemory||8)<=4)||((navigator.hardwareConcurrency||8)<=4);
  const minDt=1000/(lowPower?14:24);
  const toggle=document.createElement('button');
  toggle.type='button'; toggle.className='r14-motion-toggle r14-global-motion';
  const label=()=>{toggle.textContent=active?'Pause motion':'Resume motion';toggle.setAttribute('aria-pressed',String(!active));};
  label(); document.body.appendChild(toggle);
  function notify(){window.dispatchEvent(new CustomEvent('nsc:ambient-motion',{detail:{active}}));}
  function setActive(v,persist=true){userPaused=!v;active=Boolean(v)&&!reduced.matches;if(persist){try{localStorage.setItem(storageKey,userPaused?'1':'0');}catch(_){}}label();notify();schedule();}
  toggle.addEventListener('click',()=>setActive(!active));
  addEventListener('pointermove',e=>{pointer.tx=e.clientX/Math.max(1,innerWidth);pointer.ty=e.clientY/Math.max(1,innerHeight);pointer.inside=true;schedule();},{passive:true});
  addEventListener('pointerout',e=>{if(!e.relatedTarget)pointer.inside=false;},{passive:true});
  function resize(){const dpr=Math.min(devicePixelRatio||1,lowPower?1:1.35),w=Math.max(1,Math.round(innerWidth*dpr)),h=Math.max(1,Math.round(innerHeight*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;canvas.style.width=innerWidth+'px';canvas.style.height=innerHeight+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}}
  addEventListener('resize',()=>{resize();schedule();},{passive:true});
  function field(x,y,t){const sx=x*Math.PI*2,sy=y*Math.PI*2;let u=Math.sin(sx+t*.34)*Math.cos(sy*.92-t*.11);let v=-Math.cos(sx+t*.34)*Math.sin(sy*.92-t*.11);const dx=x-pointer.x,dy=y-pointer.y,r2=dx*dx+dy*dy,inf=pointer.inside?Math.exp(-r2/.028):0;u+=-dy*inf*3.6;v+=dx*inf*3.6;return[u,v,inf];}
  function draw(now){resize();const w=innerWidth,h=innerHeight;ctx.clearRect(0,0,w,h);pointer.x+=(pointer.tx-pointer.x)*.11;pointer.y+=(pointer.ty-pointer.y)*.11;const gap=lowPower?48:34,cols=Math.ceil(w/gap)+1,rows=Math.ceil(h/gap)+1;phase=now/1000+scrollY/Math.max(800,h)*.7;ctx.font=(lowPower?'10px':'11px')+' "Geist Mono Variable", ui-monospace, monospace';ctx.textAlign='center';ctx.textBaseline='middle';for(let j=0;j<rows;j++){for(let i=0;i<cols;i++){const px=i*gap+(j%2)*gap*.5,py=j*gap,x=px/Math.max(1,w),y=py/Math.max(1,h),f=field(x,y,phase),u=f[0],v=f[1],inf=f[2],mag=Math.hypot(u,v),ang=(Math.atan2(-v,u)+Math.PI*2)%(Math.PI*2),idx=Math.round(ang/(Math.PI/4))%8,alpha=.025+.035*Math.min(1,mag)+.11*inf;ctx.fillStyle='rgba(110,220,211,'+alpha.toFixed(3)+')';ctx.fillText(mag<.16?'·':glyphs[idx],px,py);}}}
  function schedule(){if(visible&&!raf)raf=requestAnimationFrame(frame);}
  function frame(now){raf=0;if(!visible)return;if(!last||now-last>=minDt){last=now;draw(now);}if(active||pointer.inside)schedule();}
  function motionChange(){if(reduced.matches){active=false;}else if(!userPaused){active=true;}toggle.hidden=reduced.matches;label();notify();schedule();}
  reduced.addEventListener?.('change',motionChange);
  document.addEventListener('visibilitychange',()=>{visible=!document.hidden;if(!visible&&raf){cancelAnimationFrame(raf);raf=0;}else schedule();});
  resize();draw(performance.now());toggle.hidden=reduced.matches;notify();schedule();
})();
