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
