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

  const speedInput=stage?.querySelector('[data-speed]'),speedOut=stage?.querySelector('[data-speed-out]');
  let savedSpeed=1;try{const s=parseFloat(localStorage.getItem('nsc-vortex-speed'));if(Number.isFinite(s)&&s>=Number(speedInput?.min||.25)&&s<=Number(speedInput?.max||3))savedSpeed=s;}catch(_){}
  if(speedInput&&savedSpeed!==1)speedInput.value=String(savedSpeed);
  const sweepMs=Math.max(1000,Number(stage?.dataset.sweepMs)||7000);
  let k=Number(kInput?.value||14),h=Number(hInput?.value||.005),yaw=-.28,pitch=.10,zoom=5.8,normalize=true;
  let pointer=[3,3],pointerPx=[-1000,-1000],dragging=false,px=0,py=0;
  let playing=!reduced.matches,playStart=0,playFrom=k,raf=0,visible=true,ambient=!reduced.matches,ambientUserPaused=false;
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
  function updateSpeedLabel(){if(speedOut)speedOut.textContent=`${Number(speedInput?.value||1).toFixed(2).replace(/\.?0+$/,'')}×`}
  function advancePlay(now){
    if(!playing)return false;
    const dur=sweepMs/Number(speedInput?.value||1);
    let raw=(now-playStart)/dur;
    if(playStart&&raw<0){playStart=now;raw=0;}
    const q=raw%1;
    const eased=1-Math.pow(1-q,2.25);
    k=.5+59.5*eased;
    if(kInput)kInput.value=String(k);
    stats();
    return true;
  }

  canvas.addEventListener('pointermove',e=>{updateProbe(e);if(dragging){yaw-=(e.clientX-px)*.006;pitch=Math.max(-1.05,Math.min(1.05,pitch-(e.clientY-py)*.0045));px=e.clientX;py=e.clientY;schedule();}});
  canvas.addEventListener('pointerdown',e=>{dragging=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture?.(e.pointerId);setPlaying(false);schedule();});
  canvas.addEventListener('pointerup',e=>{dragging=false;try{canvas.releasePointerCapture?.(e.pointerId)}catch{};schedule();});
  canvas.addEventListener('pointercancel',()=>{dragging=false;clearProbe();});
  canvas.addEventListener('pointerleave',()=>{dragging=false;clearProbe();});
  canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(3.7,Math.min(9.4,zoom+e.deltaY*.004));schedule();},{passive:false});
  kInput?.addEventListener('input',()=>{k=Number(kInput.value);setPlaying(false);stats();schedule();},{passive:true});
  hInput?.addEventListener('input',()=>{h=Number(hInput.value);stats();schedule();},{passive:true});
  speedInput?.addEventListener('input',()=>{try{localStorage.setItem('nsc-vortex-speed',String(Number(speedInput.value)));}catch(_){}if(playing){playStart=performance.now()-(k-.5)/59.5*(sweepMs/Number(speedInput.value));}updateSpeedLabel();schedule();},{passive:true});
  playBtn?.addEventListener('click',()=>{if(reduced.matches)return;if(playing){setPlaying(false);return;}playFrom=.5;k=.5;if(kInput)kInput.value=String(k);stats();setPlaying(true);advancePlay(performance.now());schedule();});
  frameBtn?.addEventListener('click',()=>{normalize=!normalize;frameBtn.textContent=normalize?(frameBtn.dataset.normalizedLabel||'Normalized core frame'):(frameBtn.dataset.labLabel||'Laboratory frame');if(modeLabel)modeLabel.textContent=normalize?(stage.dataset.modeNormalized||'NORMALIZED FOLLOW-CORE VIEW'):(stage.dataset.modeLaboratory||'LOG-COMPRESSED LABORATORY VIEW');schedule();});
  const applyMotionPreference=()=>{if(reduced.matches){playing=false;ambient=false;}else{if(!ambientUserPaused)ambient=true;if(!playing){playing=true;playStart=performance.now();playFrom=.5;}}if(playBtn){playBtn.disabled=Boolean(reduced.matches);playBtn.setAttribute('aria-disabled',String(Boolean(reduced.matches)));playBtn.setAttribute('aria-pressed',String(playing));playBtn.textContent=playing?(playBtn.dataset.pauseLabel||'Pause sweep'):(playBtn.dataset.playLabel||'Play sweep');}updateSpeedLabel();stats();schedule();};
  applyMotionPreference(); reduced.addEventListener?.('change',applyMotionPreference);
  window.addEventListener('nsc:ambient-motion',e=>{ambientUserPaused=!Boolean(e.detail?.active);ambient=Boolean(e.detail?.active)&&!reduced.matches;if(!e.detail?.active){if(playing)setPlaying(false);}else if(!reduced.matches&&!playing&&playBtn&&!playBtn.disabled){setPlaying(true);}schedule();});
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
  const glyphs=['.','.',':',';','+','=','x','X','#','@'];
  const lowPower=saveData||matchMedia('(max-width:680px)').matches||((navigator.deviceMemory||8)<=4)||((navigator.hardwareConcurrency||8)<=4);
  const minDt=1000/(lowPower?14:24);
  const toggle=document.createElement('button');
  toggle.type='button'; toggle.className='r14-motion-toggle r14-global-motion';
  const label=()=>{toggle.textContent=active?'Pause motion':'Resume motion';toggle.setAttribute('aria-pressed',String(!active));};
  label(); document.body.appendChild(toggle); notify();
  function notify(){window.dispatchEvent(new CustomEvent('nsc:ambient-motion',{detail:{active}}));}
  function setActive(v,persist=true){userPaused=!v;active=Boolean(v)&&!reduced.matches;if(persist){try{localStorage.setItem(storageKey,userPaused?'1':'0');}catch(_){}}label();notify();schedule();}
  toggle.addEventListener('click',()=>setActive(!active));
  addEventListener('pointermove',e=>{pointer.tx=e.clientX/Math.max(1,innerWidth);pointer.ty=e.clientY/Math.max(1,innerHeight);pointer.inside=true;schedule();},{passive:true});
  addEventListener('pointerout',e=>{if(!e.relatedTarget)pointer.inside=false;},{passive:true});
  function resize(){const dpr=Math.min(devicePixelRatio||1,lowPower?1:1.35),w=Math.max(1,Math.round(innerWidth*dpr)),h=Math.max(1,Math.round(innerHeight*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;canvas.style.width=innerWidth+'px';canvas.style.height=innerHeight+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}}
  addEventListener('resize',()=>{resize();schedule();},{passive:true});
  function field(x,y,t){const sx=x*Math.PI*2,sy=y*Math.PI*2;let u=Math.sin(sx+t*.34)*Math.cos(sy*.92-t*.11);let v=-Math.cos(sx+t*.34)*Math.sin(sy*.92-t*.11);const dx=x-pointer.x,dy=y-pointer.y,r2=dx*dx+dy*dy,inf=pointer.inside?Math.exp(-r2/.028):0;u+=-dy*inf*3.6;v+=dx*inf*3.6;return[u,v,inf];}
  function draw(now){resize();const w=innerWidth,h=innerHeight;ctx.clearRect(0,0,w,h);pointer.x+=(pointer.tx-pointer.x)*.11;pointer.y+=(pointer.ty-pointer.y)*.11;const gap=lowPower?48:34,cols=Math.ceil(w/gap)+1,rows=Math.ceil(h/gap)+1;phase=now/1000+scrollY/Math.max(800,h)*.7;ctx.font=(lowPower?'10px':'11px')+' "Geist Mono Variable", ui-monospace, monospace';ctx.textAlign='center';ctx.textBaseline='middle';for(let j=0;j<rows;j++){for(let i=0;i<cols;i++){const px=i*gap+(j%2)*gap*.5,py=j*gap,x=px/Math.max(1,w),y=py/Math.max(1,h),f=field(x,y,phase),u=f[0],v=f[1],inf=f[2],mag=Math.hypot(u,v),level=Math.max(0,Math.min(glyphs.length-1,Math.floor(mag*glyphs.length*1.8))),alpha=.08+.09*Math.min(1,mag)+.2*inf;ctx.fillStyle='rgba(110,220,211,'+alpha.toFixed(3)+')';ctx.fillText(glyphs[level],px,py);}}}
  function schedule(){if(visible&&!raf)raf=requestAnimationFrame(frame);}
  function frame(now){raf=0;if(!visible)return;if(!last||now-last>=minDt){last=now;draw(now);}if(active||pointer.inside)schedule();}
  function motionChange(){if(reduced.matches){active=false;}else if(!userPaused){active=true;}toggle.hidden=reduced.matches;label();notify();schedule();}
  reduced.addEventListener?.('change',motionChange);
  document.addEventListener('visibilitychange',()=>{visible=!document.hidden;if(!visible&&raf){cancelAnimationFrame(raf);raf=0;}else schedule();});
  resize();draw(performance.now());toggle.hidden=reduced.matches;notify();schedule();
})();

/* NSC R16 fluid hero overlay.
 * UI-only exploratory field. Not the computed 2026 solution.
 * Motion invariant: only explicit pause or prefers-reduced-motion stops running intent.
 */
(() => {
  'use strict';
  const stage = document.querySelector('[data-vortex-stage]');
  const hero = document.querySelector('[data-r14-rich-hero]');
  if (!stage || !hero) return;

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const saveData = Boolean(navigator.connection?.saveData);
  const lowPower = saveData || matchMedia('(max-width:680px)').matches || ((navigator.deviceMemory || 8) <= 4) || ((navigator.hardwareConcurrency || 8) <= 4);

  // Canonical rich-home recruitment copy. Also patched into the generator for no-JS parity.
  const lede = hero.querySelector('.r14-hero-copy .lede');
  if (lede) lede.textContent = 'OpenAI claims C and D; independent review continues. A and B remain open. Bring mathematical skill, spare compute, or an inference subscription to the remaining frontier.';
  const actions = [...hero.querySelectorAll('.r14-actions a')];
  for (const a of actions) {
    const href = a.getAttribute('href') || '';
    if (href.includes('frontier/')) a.textContent = 'Take an open problem';
    else if (href.includes('agents/')) a.textContent = 'Put spare compute to work';
    else if (href.includes('math/')) a.textContent = 'Mathematics';
  }
  let participation = hero.querySelector('.r16-participation-line');
  if (!participation) {
    participation = document.createElement('p');
    participation.className = 'r16-participation-line';
    participation.textContent = 'Independent attempts welcome · negative results count · submissions do not become truth automatically.';
    hero.querySelector('.r14-hero-copy')?.appendChild(participation);
  }

  // Replace the wireframe renderer visually, but preserve the original static SVG for no-JS fallback.
  const oldCanvas = stage.querySelector('[data-vortex-canvas]');
  const oldControls = stage.querySelector('[data-vortex-controls]');
  const oldProbe = stage.querySelector('[data-flow-probe]');
  const oldHelp = stage.querySelector('.stage-help');
  const oldNote = stage.querySelector('.stage-note');
  const oldBoundary = stage.querySelector('.visual-boundary');

  const canvas = document.createElement('canvas');
  canvas.className = 'r16-fluid-canvas';
  canvas.setAttribute('data-vortex-canvas', '');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.dataset.r16FluidCanvas = '';
  stage.insertBefore(canvas, oldCanvas || stage.firstChild);
  stage.classList.add('r16-fluid-ready');
  stage.dataset.r16MotionRunning = reduced.matches ? 'false' : 'true';
  stage.dataset.r16UserPaused = 'false';
  stage.dataset.r16Response = 'balanced';

  if (oldCanvas) {
    oldCanvas.hidden = true;
    oldCanvas.removeAttribute('data-vortex-canvas');
  }
  if (oldControls) oldControls.hidden = true;
  if (oldProbe) oldProbe.hidden = true;
  if (oldHelp) oldHelp.hidden = true;
  if (oldNote) oldNote.hidden = true;
  if (oldBoundary) {
    oldBoundary.innerHTML = '<strong>Interactive exploratory flow field.</strong> UI response field - not the computed 2026 solution. Source-derived quantitative readouts remain separate from the pointer-driven interface response.';
  }

  const label = document.createElement('div');
  label.className = 'r16-field-label';
  label.innerHTML = '<strong>INTERACTIVE EXPLORATORY FLOW FIELD</strong><span>UI response field · not the computed 2026 solution</span>';
  stage.appendChild(label);

  const controls = document.createElement('div');
  controls.className = 'r16-fluid-controls';
  controls.innerHTML = `
    <button type="button" data-r16-motion aria-pressed="false">Pause motion</button>
    <fieldset class="r16-response" aria-label="Flow response">
      <legend>Flow response</legend>
      <button type="button" data-r16-response="light" aria-pressed="false">Light</button>
      <button type="button" data-r16-response="balanced" aria-pressed="true">Balanced</button>
      <button type="button" data-r16-response="viscous" aria-pressed="false">Viscous</button>
    </fieldset>
    <button type="button" data-r16-reset>Reset view</button>
    <details class="r16-derived"><summary>Explore derived parameters</summary></details>`;
  stage.appendChild(controls);
  const derived = controls.querySelector('.r16-derived');
  if (derived && oldControls) derived.appendChild(oldControls);
  if (derived) derived.open = true;
  if (oldControls) oldControls.hidden = false;

  const pauseBtn = controls.querySelector('[data-r16-motion]');
  const resetBtn = controls.querySelector('[data-r16-reset]');
  const responseBtns = [...controls.querySelectorAll('[data-r16-response]')];

  const ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });
  if (!ctx) return;

  const modes = {
    light:    { pointerGain: 1.35, memory: 0.82, smooth: 0.22, radius: 0.105, drift: 1.18 },
    balanced: { pointerGain: 1.00, memory: 0.91, smooth: 0.13, radius: 0.135, drift: 1.00 },
    viscous:  { pointerGain: 0.72, memory: 0.965, smooth: 0.075, radius: 0.19, drift: 0.78 }
  };

  const motion = {
    userPaused: false,
    visible: !document.hidden,
    reduced: reduced.matches,
    runningIntent: !reduced.matches,
    effective() { return this.runningIntent && !this.userPaused && !this.reduced && this.visible; }
  };

  let response = 'balanced';
  let raf = 0, last = 0, accumulator = 0;
  let viewAngle = 0, viewScale = 1;
  let dragging = false, dragX = 0, dragY = 0;
  const pointer = { x: .64, y: .46, tx: .64, ty: .46, vx: 0, vy: 0, rawVx: 0, rawVy: 0, inside: false, energy: 0 };

  const count = lowPower ? 720 : 1900;
  const particles = Array.from({ length: count }, (_, i) => ({
    x: (i * 0.61803398875) % 1,
    y: ((i * 0.41421356237) + (i % 7) * .017) % 1,
    px: 0, py: 0,
    age: (i % 180) / 180,
    life: .65 + (i % 37) / 37 * 1.5,
    seed: (i * 12.9898) % 1
  }));

  function resize() {
    const r = stage.getBoundingClientRect();
    const dpr = Math.min(devicePixelRatio || 1, lowPower ? 1.15 : 1.55);
    const w = Math.max(1, Math.round(r.width * dpr));
    const h = Math.max(1, Math.round(r.height * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w; canvas.height = h;
      canvas.style.width = r.width + 'px'; canvas.style.height = r.height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = '#020b10'; ctx.fillRect(0, 0, r.width, r.height);
    }
    return { w: r.width, h: r.height };
  }

  function reseed(p, edge = false) {
    if (edge) {
      p.x = Math.random() < .7 ? -0.02 : Math.random();
      p.y = Math.random();
    } else {
      p.x = Math.random(); p.y = Math.random();
    }
    p.px = p.x; p.py = p.y; p.age = 0;
    p.life = .7 + Math.random() * 1.7;
  }

  function baseField(x, y, t) {
    // A stable, divergence-looking exploratory UI field with several coherent cells.
    // This is not claimed to be a physical Navier–Stokes solution.
    const qx = x - .5, qy = y - .5;
    let u = .20 + .095 * Math.sin((y * 2.1 + t * .055) * Math.PI * 2);
    let v = .055 * Math.sin((x * 1.6 - t * .041) * Math.PI * 2);
    const centers = [
      [.29 + .035*Math.sin(t*.17), .34,  .20],
      [.67, .43 + .03*Math.cos(t*.13), -.25],
      [.48 + .025*Math.cos(t*.11), .72, .17]
    ];
    for (const [cx, cy, s] of centers) {
      const dx = x - cx, dy = y - cy, r2 = dx*dx + dy*dy + .0028;
      const g = Math.exp(-r2 / .075);
      u += -dy / Math.sqrt(r2) * s * g;
      v +=  dx / Math.sqrt(r2) * s * g;
    }
    // gentle central breathing/shear avoids a rigid repeating lattice
    u += .035 * Math.cos((qx - qy) * 8 + t*.21);
    v += .028 * Math.sin((qx + qy) * 9 - t*.18);
    const ca = Math.cos(viewAngle), sa = Math.sin(viewAngle);
    return [(u*ca - v*sa) * viewScale, (u*sa + v*ca) * viewScale];
  }

  function uiPerturb(x, y) {
    if (!pointer.inside || motion.reduced) return [0, 0];
    const m = modes[response];
    const dx = x - pointer.x, dy = y - pointer.y;
    const r2 = dx*dx + dy*dy;
    const g = Math.exp(-r2 / (m.radius*m.radius));
    const speed = Math.min(.045, Math.hypot(pointer.vx, pointer.vy));
    const swirl = m.pointerGain * pointer.energy * .048;
    const drag = m.pointerGain * .74;
    const push = m.pointerGain * speed * .45;
    const inv = 1 / Math.max(.018, Math.sqrt(r2));
    return [
      (-dy * swirl + pointer.vx * drag + dx * inv * push) * g,
      ( dx * swirl + pointer.vy * drag + dy * inv * push) * g
    ];
  }

  function step(dt, t, dims) {
    const m = modes[response];
    pointer.x += (pointer.tx - pointer.x) * m.smooth;
    pointer.y += (pointer.ty - pointer.y) * m.smooth;
    pointer.vx += (pointer.rawVx - pointer.vx) * m.smooth;
    pointer.vy += (pointer.rawVy - pointer.vy) * m.smooth;
    pointer.rawVx *= .84; pointer.rawVy *= .84;
    pointer.energy = pointer.energy * m.memory + Math.min(1, Math.hypot(pointer.vx, pointer.vy) * 42) * (1-m.memory);

    // translucent persistence creates smooth flow trails instead of line-forest geometry
    ctx.fillStyle = motion.reduced ? '#020b10' : 'rgba(2,11,16,0.075)';
    ctx.fillRect(0, 0, dims.w, dims.h);
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';

    const scale = dt * m.drift;
    for (let i=0; i<particles.length; i++) {
      const p = particles[i];
      p.px = p.x; p.py = p.y;
      const b = baseField(p.x, p.y, t);
      const q = uiPerturb(p.x, p.y);
      p.x += (b[0] + q[0]) * scale;
      p.y += (b[1] + q[1]) * scale;
      p.age += dt;
      if (p.x < -.06 || p.x > 1.06 || p.y < -.06 || p.y > 1.06 || p.age > p.life) { reseed(p, true); continue; }

      const x0 = p.px * dims.w, y0 = p.py * dims.h;
      const x1 = p.x * dims.w, y1 = p.y * dims.h;
      const speed = Math.min(1, Math.hypot(x1-x0,y1-y0)/6);
      const hue = 184 + 24 * p.seed + 18 * speed;
      const alpha = lowPower ? .13 + .20*speed : .10 + .24*speed;
      ctx.strokeStyle = `hsla(${hue.toFixed(0)},88%,62%,${alpha.toFixed(3)})`;
      ctx.lineWidth = lowPower ? .65 : .72 + .45*speed;
      ctx.beginPath(); ctx.moveTo(x0,y0); ctx.lineTo(x1,y1); ctx.stroke();
      if (!lowPower && i % 17 === 0) {
        ctx.fillStyle = `hsla(${(hue+18).toFixed(0)},92%,70%,${(.16+.18*speed).toFixed(3)})`;
        ctx.beginPath(); ctx.arc(x1,y1,1.05+.8*speed,0,Math.PI*2); ctx.fill();
      }
    }

    if (pointer.inside && !motion.reduced) {
      const gx = pointer.x*dims.w, gy = pointer.y*dims.h;
      const grad = ctx.createRadialGradient(gx,gy,0,gx,gy,Math.min(dims.w,dims.h)*m.radius*1.3);
      grad.addColorStop(0, `rgba(89,235,224,${(.08+.12*pointer.energy).toFixed(3)})`);
      grad.addColorStop(1, 'rgba(89,235,224,0)');
      ctx.fillStyle = grad; ctx.fillRect(0,0,dims.w,dims.h);
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  function updateState() {
    const active = motion.effective();
    stage.dataset.r16MotionRunning = String(active);
    stage.dataset.r16UserPaused = String(motion.userPaused);
    if (pauseBtn) {
      pauseBtn.textContent = motion.userPaused ? 'Resume motion' : 'Pause motion';
      pauseBtn.setAttribute('aria-pressed', String(motion.userPaused));
      pauseBtn.disabled = motion.reduced;
      pauseBtn.hidden = motion.reduced;
    }
    // Keep legacy ambient/R5 controllers aligned, but do not let their internal state define R16 intent.
    window.dispatchEvent(new CustomEvent('nsc:ambient-motion', { detail: { active: active } }));
  }

  function schedule() { if (!raf && motion.visible) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0;
    const dims = resize();
    const minDt = 1000/(lowPower ? 18 : 36);
    if (!last) last = now;
    const elapsed = Math.min(65, now-last);
    if (elapsed >= minDt) {
      last = now;
      const dt = Math.min(.045, elapsed/1000);
      if (motion.effective()) step(dt, now/1000, dims);
      else if (motion.reduced) {
        // draw a stable reference frame once in reduced mode
        if (accumulator < 1) { step(0, 0, dims); accumulator = 1; }
      }
    }
    if (motion.effective() || pointer.inside) schedule();
  }

  function onPointerMove(e) {
    if (e.target.closest?.('button,input,summary,details,a')) return;
    const r = stage.getBoundingClientRect();
    const nx = (e.clientX-r.left)/Math.max(1,r.width), ny = (e.clientY-r.top)/Math.max(1,r.height);
    const dx = nx-pointer.tx, dy = ny-pointer.ty;
    pointer.rawVx = dx; pointer.rawVy = dy;
    pointer.tx = nx; pointer.ty = ny; pointer.inside = nx>=0&&nx<=1&&ny>=0&&ny<=1;
    pointer.energy = Math.min(1, pointer.energy + Math.hypot(dx,dy)*5.5);
    schedule();
    if (dragging) {
      viewAngle += (e.clientX-dragX)*.0026;
      dragX=e.clientX; dragY=e.clientY;
    }
  }

  stage.addEventListener('pointermove', onPointerMove, { passive: true });
  stage.addEventListener('pointerenter', e => { if(!e.target.closest?.('button,input,summary,details,a')) pointer.inside=true; schedule(); }, { passive:true });
  stage.addEventListener('pointerleave', () => { pointer.inside=false; dragging=false; schedule(); }, { passive:true });
  stage.addEventListener('pointerdown', e => {
    if (e.target.closest?.('button,input,summary,details,a')) return;
    dragging=true; dragX=e.clientX; dragY=e.clientY; pointer.energy=Math.min(1,pointer.energy+.3);
    // Deliberately DO NOT stop automatic motion.
    schedule();
  });
  stage.addEventListener('pointerup', () => { dragging=false; schedule(); }, { passive:true });
  stage.addEventListener('wheel', e => {
    if (e.target.closest?.('input,details')) return;
    e.preventDefault(); viewScale = Math.max(.65, Math.min(1.45, viewScale - e.deltaY*.00045)); schedule();
  }, { passive:false });

  pauseBtn?.addEventListener('click', () => {
    motion.userPaused = !motion.userPaused;
    motion.runningIntent = !motion.userPaused;
    accumulator = 0; updateState(); schedule();
  });
  document.querySelector('.r14-global-motion')?.addEventListener('click', () => {
    motion.userPaused = !motion.userPaused;
    motion.runningIntent = !motion.userPaused;
    accumulator = 0; updateState(); schedule();
  });
  resetBtn?.addEventListener('click', () => {
    viewAngle=0; viewScale=1; response='balanced'; stage.dataset.r16Response=response;
    responseBtns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.r16Response===response)));
    particles.forEach(p=>reseed(p));
    pointer.energy=0; schedule();
  });
  responseBtns.forEach(b => b.addEventListener('click', () => {
    response = b.dataset.r16Response || 'balanced'; stage.dataset.r16Response=response;
    responseBtns.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
    // Deliberately preserve running intent.
    schedule();
  }));

  // Legacy derived parameters remain exploratory and MUST NOT stop R16 automatic motion.
  for (const input of stage.querySelectorAll('[data-k],[data-h],[data-speed]')) {
    input.addEventListener('input', () => { motion.runningIntent = !motion.userPaused && !motion.reduced; updateState(); schedule(); }, { passive:true });
  }

  document.addEventListener('visibilitychange', () => {
    motion.visible = !document.hidden;
    if (!motion.visible && raf) { cancelAnimationFrame(raf); raf=0; }
    else { last=0; schedule(); }
    updateState();
  });
  reduced.addEventListener?.('change', () => {
    motion.reduced = reduced.matches;
    motion.runningIntent = !motion.reduced && !motion.userPaused;
    accumulator=0; updateState(); schedule();
  });
  addEventListener('resize', () => { accumulator=0; schedule(); }, { passive:true });

  // Disable the legacy semantic stop behavior by keeping its public play button out of the primary UI.
  // The legacy derived controls still work inside the disclosure; R16 owns the visible motion state.
  updateState(); resize();
  ctx.fillStyle='#020b10'; ctx.fillRect(0,0,stage.clientWidth,stage.clientHeight);
  if (!motion.reduced) schedule(); else { accumulator=0; schedule(); }
})();
