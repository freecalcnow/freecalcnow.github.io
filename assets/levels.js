/* FreeCalcNow levels — shared level system for games. localStorage only.
   No server, no sign-up. Progress: fcn-levels-v1 {gameId:{unlocked, done:[]}}.
   Daily skips: fcn-skips-v1 {date, left} — 2 per day, resets at midnight. */
(function(){
  var KEY='fcn-levels-v1', SKIP_KEY='fcn-skips-v1';
  function load(){ try{ return JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(e){ return {}; } }
  function save(d){ try{ localStorage.setItem(KEY, JSON.stringify(d)); }catch(e){} }
  function today(){ try{ return new Date().toISOString().slice(0,10); }catch(e){ return '2026-11-19'; } }
  function skips(){
    var s=null; try{ s=JSON.parse(localStorage.getItem(SKIP_KEY)||'null'); }catch(e){}
    if(!s || s.date!==today()){ s={date:today(), left:2}; try{ localStorage.setItem(SKIP_KEY, JSON.stringify(s)); }catch(e){} }
    return s;
  }
  /* Level tables: params(lv) returns the difficulty knobs for that level. */
  var LEVELS={
    'word-guess':{ total:30, name:'Word Guess',
      params:function(lv){ return { len:4+Math.min(2,Math.floor((lv-1)/10)), tries:6-Math.floor((lv-1)/10) }; },
      label:function(lv){ var p=this.params(lv); return p.len+' letters · '+p.tries+' tries'; } },
    'sudoku-mini':{ total:30, name:'Sudoku Mini',
      params:function(lv){ return { hide:Math.min(6+Math.floor((lv-1)/3), 12) }; },
      label:function(lv){ return '4×4 · '+this.params(lv).hide+' hidden'; } },
    'memory-cards':{ total:20, name:'Memory Cards',
      params:function(lv){ return { pairs:Math.min(4+Math.floor((lv-1)/2), 12) }; },
      label:function(lv){ return this.params(lv).pairs+' pairs'; } },
    'minesweeper-mini':{ total:20, name:'Minesweeper Mini',
      params:function(lv){ var size=5+Math.floor((lv-1)/7); if(size>8)size=8;
        return { size:size, mines:Math.min(4+Math.floor((lv-1)*0.7), size*size-10) }; },
      label:function(lv){ var p=this.params(lv); return p.size+'×'+p.size+' · '+p.mines+' mines'; } },
    'breakout-mini':{ total:20, name:'Breakout Mini',
      params:function(lv){ return { rows:3+Math.floor((lv-1)/5), interval:Math.max(14, 35-lv) }; },
      label:function(lv){ var p=this.params(lv); return p.rows+' rows · speed '+(35-p.interval+1); } },
    'block-drop':{ total:20, name:'Block Drop',
      params:function(lv){ return { target:10+lv, ms:Math.max(60, 220-lv*6) }; },
      label:function(lv){ return 'Tower of '+this.params(lv).target; } },
    '2048':{ total:10, name:'2048',
      params:function(lv){ return { target:128*Math.pow(2, lv-1) }; },
      label:function(lv){ return 'Reach '+this.params(lv).target; } },
    'simon-says':{ total:20, name:'Simon Says',
      params:function(lv){ return { targetLen:lv+2, delay:Math.max(250, 500-lv*10) }; },
      label:function(lv){ return 'Pattern of '+this.params(lv).targetLen; } },
    'reaction-test':{ total:15, name:'Reaction Test',
      params:function(lv){ return { targetAvg:460-lv*10, rounds:5 }; },
      label:function(lv){ return 'Average under '+this.params(lv).targetAvg+' ms'; } },
    'math-sprint':{ total:20, name:'Math Sprint',
      params:function(lv){ return { ops:lv<=5?['+','-']:(lv<=12?['+','-','×']:['+','-','×','÷']),
        maxNum:10+lv*5, seconds:Math.max(20, 60-lv), questions:5+Math.min(10, lv) }; },
      label:function(lv){ var p=this.params(lv); return p.questions+' questions · '+p.seconds+'s'; } },
    'balloon-pop':{ total:20, name:'Balloon Pop',
      params:function(lv){ return { balloons:8+lv*2, seconds:Math.max(15, 45-lv), bad:Math.min(3+Math.floor(lv/4), 8) }; },
      label:function(lv){ var p=this.params(lv); return 'Pop '+p.balloons+' in '+p.seconds+'s'; } },
    'colour-sort':{ total:20, name:'Colour Sort',
      params:function(lv){ return { colours:3+Math.floor((lv-1)/4), tubes:2+Math.floor((lv-1)/4) }; },
      label:function(lv){ var p=this.params(lv); return p.colours+' colours · '+p.tubes+' spare tubes'; } }
  };
  function total(gameId){ return (LEVELS[gameId]||{total:1}).total; }
  function highest(gameId){ var d=load(); return (d[gameId]&&d[gameId].unlocked)||1; }
  function doneList(gameId){ var d=load(); return (d[gameId]&&d[gameId].done)||[]; }
  function current(gameId){
    var q=null; try{ q=new URLSearchParams(location.search).get('level'); }catch(e){}
    var hi=highest(gameId), tot=total(gameId);
    var lv=parseInt(q||'',10);
    if(lv>=1 && lv<=Math.min(hi,tot)) return lv;
    return Math.min(hi,tot);
  }
  function params(gameId, lv){ var L=LEVELS[gameId]; if(!L) return {}; return L.params(lv||current(gameId)); }
  function win(gameId){
    var d=load(); var g=d[gameId]||{unlocked:1, done:[]};
    var lv=current(gameId), tot=total(gameId);
    if(g.done.indexOf(lv)<0) g.done.push(lv);
    if(lv<tot && g.unlocked<lv+1) g.unlocked=lv+1;
    d[gameId]=g; save(d);
    return { level:lv, next:Math.min(lv+1, tot), unlocked:g.unlocked, allDone:g.done.length>=tot };
  }
  function skip(gameId){
    var s=skips(); if(s.left<=0) return { ok:false, left:0 };
    s.left--; try{ localStorage.setItem(SKIP_KEY, JSON.stringify(s)); }catch(e){}
    var d=load(); var g=d[gameId]||{unlocked:1, done:[]};
    var lv=current(gameId), tot=total(gameId);
    if(lv<tot && g.unlocked<lv+1) g.unlocked=lv+1;
    d[gameId]=g; save(d);
    return { ok:true, left:s.left, next:g.unlocked };
  }
  function progress(gameId){ var d=load(); var g=d[gameId]||{unlocked:1, done:[]};
    return { unlocked:g.unlocked, done:g.done.length, total:total(gameId), current:current(gameId) }; }
  /* Level bar UI — renders into #level-bar. */
  function bar(gameId, opts){
    var host=document.getElementById('level-bar'); if(!host) return;
    var L=LEVELS[gameId]; if(!L) return;
    var p=progress(gameId), lv=p.current, left=skips().left;
    var accent=(opts&&opts.accent)||'#0B1F3A';
    var html='<div style="background:#fff;border:2px solid '+accent+';border-radius:14px;padding:12px 14px;margin-bottom:12px">'
      +'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
      +'<span style="background:'+accent+';color:#fff;font-weight:800;border-radius:20px;padding:4px 12px;font-size:15px"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="vertical-align:-2px"><path fill="currentColor" d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17.2 5.9 20.6l1.4-6.8L2.2 9.1l6.9-.8L12 2Z"/></svg> Level '+lv+'</span>'
      +'<span style="font-weight:700">'+L.label(lv)+'</span>'
      +'<span style="margin-left:auto;font-size:13px;color:#475569">'+p.done+' of '+p.total+' levels done</span></div>'
      +'<div style="height:10px;background:#e2e8f0;border-radius:6px;margin:10px 0 8px;overflow:hidden"><div style="height:100%;width:'+Math.round(p.done/p.total*100)+'%;background:linear-gradient(90deg,'+accent+',#F59E0B);border-radius:6px"></div></div>'
      +'<div style="display:flex;gap:6px;flex-wrap:wrap">';
    for(var i=1;i<=p.total;i++){
      var done=p.done.indexOf(i)>=0, un=i<=p.unlocked;
      if(done) html+='<a href="?level='+i+'" style="min-width:30px;text-align:center;padding:4px 6px;border-radius:8px;background:#FEF3C7;color:#92400E;font-weight:800;text-decoration:none;font-size:13px" title="Replay level '+i+'">✓'+i+'</a>';
      else if(un) html+='<a href="?level='+i+'" style="min-width:30px;text-align:center;padding:4px 6px;border-radius:8px;background:'+accent+';color:#fff;font-weight:800;text-decoration:none;font-size:13px">▶'+i+'</a>';
      else html+='<span style="min-width:30px;text-align:center;padding:4px 6px;border-radius:8px;background:#f1f5f9;color:#94a3b8;font-weight:700;font-size:13px"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" style="vertical-align:-2px"><path fill="currentColor" d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5Zm-3 7V7a3 3 0 1 1 6 0v2H9Z"/></svg>'+i+'</span>';
    }
    html+='</div>';
    if(lv<p.total){
      html+='<div style="margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
        +'<button type="button" id="lvl-skip" style="padding:8px 14px;border-radius:10px;border:0;background:#F59E0B;color:#0F172A;font-weight:800;cursor:pointer" '+(left<=0?'disabled style="padding:8px 14px;border-radius:10px;border:0;background:#e2e8f0;color:#94a3b8;font-weight:800"':'')+'>Skip this level ('+left+' left today)</button>'
        +'<span style="font-size:13px;color:#475569">You get 2 free level-skips every day — they reset at midnight.</span></div>';
    } else {
      html+='<div style="margin-top:10px;font-weight:700;color:'+accent+'"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="vertical-align:-2px"><path fill="currentColor" d="M6 2h12v2h3v3a5 5 0 0 1-5 5h-.4A6 6 0 0 1 13 16.9V19h3v2H8v-2h3v-2.1A6 6 0 0 1 8.4 12H8a5 5 0 0 1-5-5V4h3V2ZM5 6v1a3 3 0 0 0 3 3V6H5Zm14 0h-3v4a3 3 0 0 0 3-3V6Z"/></svg> All '+p.total+' levels done — replay any level above!</div>';
    }
    html+='</div>';
    host.innerHTML=html;
    var sk=document.getElementById('lvl-skip');
    if(sk) sk.onclick=function(){
      var r=skip(gameId);
      if(r.ok){ location.href='?level='+r.next; }
      else { sk.disabled=true; sk.textContent='No skips left today — come back tomorrow!'; }
    };
  }
  window.FCN_LEVELS={ LEVELS:LEVELS, total:total, highest:highest, doneList:doneList,
    current:current, params:params, win:win, skip:skip, skipsLeft:function(){ return skips().left; },
    progress:progress, bar:bar };
})();
