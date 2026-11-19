/* FreeCalcNow site.js — tool-page boot, header search, feedback, share/print.
   Depends on /assets/engine.js (helpers, FAMS, resolveConv) loaded before this file. */
(function(){
  "use strict";
  function $(s, r){ return (r||document).querySelector(s); }
  function esc(s){ return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function cap(s){ s=String(s||""); return s ? s.charAt(0).toUpperCase()+s.slice(1) : s; }
  /* ---------- header + home search ---------- */
  /* ---------- header + home search ----------
     FAST ON SLOW CONNECTIONS: nothing is fetched on page load — no index
     prefetch at all. Typing shows instant results from the built-in
     POPULAR list (zero network wait); the small per-letter shard(s) for
     the query load in the background and the list is re-rendered with the
     full results when they arrive. If a shard is slow or fails, the
     POPULAR results stay on screen. */
  var CAT_LABEL={finance:"Finance",health:"Health",math:"Math",everyday:"Everyday life",other:"Other",conversion:"Conversion",physics:"Physics",chemistry:"Chemistry",biology:"Biology",statistics:"Statistics",construction:"Construction",food:"Food",sports:"Sports",ecology:"Ecology"};
  function catLabel(c){ return CAT_LABEL[String(c||"").toLowerCase()]||cap(c||""); }
  /* Instant results with zero network wait: the most-used tools. Every id
     here is a real tool page (verified against the full tool list). */
  var POPULAR=[
    {id:"mortgage",name:"Mortgage Calculator",cat:"finance"},
    {id:"compound",name:"Compound Interest Calculator",cat:"finance"},
    {id:"loan",name:"Loan / EMI Calculator",cat:"finance"},
    {id:"bmi",name:"BMI Calculator",cat:"health"},
    {id:"sip-calculator",name:"SIP Calculator",cat:"finance"},
    {id:"percentage",name:"Percentage Calculator",cat:"everyday"},
    {id:"tip",name:"Tip & Bill Split Calculator",cat:"everyday"},
    {id:"age",name:"Age Calculator",cat:"everyday"},
    {id:"gpa",name:"GPA Calculator",cat:"everyday"},
    {id:"salary-hourly",name:"Salary ↔ Hourly Calculator",cat:"finance"},
    {id:"income-tax",name:"Income Tax Calculator (US Federal)",cat:"finance"},
    {id:"retirement",name:"Retirement Calculator",cat:"finance"},
    {id:"savings-goal",name:"Savings Goal Calculator",cat:"finance"},
    {id:"inflation",name:"Inflation Calculator",cat:"finance"},
    {id:"roi",name:"Investment Return (ROI) Calculator",cat:"finance"},
    {id:"calorie",name:"Calorie (TDEE) Calculator",cat:"health"},
    {id:"discount",name:"Discount Calculator",cat:"everyday"},
    {id:"password-gen",name:"Password Generator & Strength Checker",cat:"other"},
    {id:"qr",name:"QR Code Generator",cat:"other"},
    {id:"json",name:"JSON Formatter & Validator",cat:"other"},
    {id:"debt-payoff",name:"Debt Payoff Calculator",cat:"finance"},
    {id:"ppf",name:"PPF Calculator",cat:"finance"},
    {id:"vat",name:"VAT / Sales Tax Calculator",cat:"finance"},
    {id:"take-home",name:"Take-Home Pay Calculator",cat:"finance"}
  ];
  /* Searchable pool: POPULAR plus every shard loaded so far. */
  var POOL={}, POOL_LIST=null;
  POPULAR.forEach(function(t){ POOL[t.id]=t; });
  var POPULAR_IDS={};
  POPULAR.forEach(function(t){ POPULAR_IDS[t.id]=1; });
  function currentPool(){
    if(POOL_LIST) return POOL_LIST;
    POOL_LIST=Object.keys(POOL).map(function(k){ return POOL[k]; });
    return POOL_LIST;
  }
  /* Shards: /assets/search/<letter>.json (plus <letter>2.json, <letter>3.json
     for the big letters), listed in /assets/search/manifest.json. The
     manifest is fetched only on the first search, never on page load. */
  var SHARD_CACHE={}, SHARD_P={}, MANIFEST_P=null;
  function shardParts(letter){
    if(!MANIFEST_P){
      MANIFEST_P=fetch("/assets/search/manifest.json").then(function(r){ return r.json(); }).catch(function(){ return {}; });
    }
    return MANIFEST_P.then(function(m){ return (m && m[letter]) || [letter]; });
  }
  function loadShard(letter){
    if(SHARD_CACHE[letter]) return Promise.resolve(SHARD_CACHE[letter]);
    if(SHARD_P[letter]) return SHARD_P[letter];
    SHARD_P[letter]=shardParts(letter).then(function(parts){
      return Promise.all(parts.map(function(p){
        return fetch("/assets/search/"+p+".json").then(function(r){ return r.json(); }).catch(function(){ return []; });
      }));
    }).then(function(chunks){
      var out=[], seen={}, i, j, e;
      for(i=0;i<chunks.length;i++){
        var arr=chunks[i]||[];
        for(j=0;j<arr.length;j++){
          e=arr[j];
          if(!e || !e[0] || seen[e[0]]) continue;
          seen[e[0]]=1;
          out.push({id:e[0], name:e[1], cat:e[2]||""});
        }
      }
      SHARD_CACHE[letter]=out;
      return out;
    }).catch(function(){ SHARD_CACHE[letter]=[]; return []; });
    return SHARD_P[letter];
  }
  /* Synonyms: what people type -> the words tool names actually use. */
  var SYN={
    emi:["emi","loan"], loan:["loan","emi"],
    home:["home","mortgage"], house:["house","mortgage","home"],
    car:["car","auto","vehicle"], auto:["auto","car"],
    salary:["salary","paycheck","pay"], pay:["pay","salary","paycheck"],
    paycheck:["paycheck","salary"], income:["income","salary"],
    weight:["weight","bmi"], bmi:["bmi","weight"],
    age:["age","dob"], dob:["dob","age"],
    percent:["percent","percentage"], percentage:["percentage","percent"],
    interest:["interest","compound"],
    tax:["tax","vat","gst"], vat:["vat","tax","gst"], gst:["gst","tax","vat"],
    grade:["grade","gpa"], gpa:["gpa","grade","cgpa"],
    sip:["sip"], fd:["fd","fixed"], rd:["rd","recurring"], ppf:["ppf"],
    tip:["tip"], discount:["discount"]
  };
  /* Generic words: they match nearly every tool, so they never trigger a
     shard fetch (they still count in scoring). */
  var GENERIC={calculator:1,converter:1,generator:1,checker:1,estimator:1,planner:1,finder:1,tracker:1,counter:1,maker:1,tool:1,tools:1,free:1,online:1,the:1,and:1,or:1,for:1,of:1,vs:1,per:1,to:1,in:1,on:1,with:1,by:1,a:1,an:1};
  function normWords(q){
    return String(q||"").toLowerCase().replace(/%/g," percent ").replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return w.length>1; });
  }
  function shardLetters(q){
    var words=normWords(q), letters=[], seen={}, i, j, w, alts, c, L;
    for(i=0;i<words.length;i++){
      w=words[i];
      if(GENERIC[w]) continue;
      alts=SYN[w]||[w];
      for(j=0;j<alts.length;j++){
        c=alts[j].charAt(0);
        L=(c>="a"&&c<="z")?c:((c>="0"&&c<="9")?"0-9":null);
        if(L && !seen[L]){ seen[L]=1; letters.push(L); }
      }
    }
    return letters;
  }
  /* Levenshtein distance. Only ever called for words of 4+ letters whose
     lengths differ by at most 1, so this stays cheap per keystroke. */
  function lev(a, b){
    var m=a.length, n=b.length, i, j, prev=[], cur=[], c, t;
    if(Math.abs(m-n)>1) return 2;
    for(j=0;j<=n;j++) prev[j]=j;
    for(i=1;i<=m;i++){
      cur[0]=i;
      for(j=1;j<=n;j++){
        c=(a.charCodeAt(i-1)===b.charCodeAt(j-1))?0:1;
        cur[j]=Math.min(prev[j]+1, cur[j-1]+1, prev[j-1]+c);
      }
      t=prev; prev=cur; cur=t;
    }
    return prev[n];
  }
  /* Best match score of one query word (or synonym) against one tool.
     5 exact word, 4 prefix, 3 substring or 1-typo, 1 category. */
  function wordScore(alt, nameWords, catLower, idLower){
    var best=0, i, nw;
    for(i=0;i<nameWords.length;i++){
      nw=nameWords[i];
      if(nw===alt) return 5;
      if(alt.length>=2 && nw.indexOf(alt)===0) best=Math.max(best,4);
      else if(nw.length>=4 && alt.length>=4 && alt.indexOf(nw)===0) best=Math.max(best,4);
      else if(alt.length>=2 && nw.indexOf(alt)>0) best=Math.max(best,3);
    }
    if(best>=4) return best;
    if(idLower===alt) return 4;
    if(best===0 && alt.length>=4){
      for(i=0;i<nameWords.length;i++){
        nw=nameWords[i];
        if(nw.length>=4 && nw.charAt(0)===alt.charAt(0) && Math.abs(nw.length-alt.length)<=1 && lev(nw,alt)<=1){ best=3; break; }
      }
    }
    if(best===0 && catLower && catLower.indexOf(alt)>=0) best=1;
    return best;
  }
  function scoreTools(q, n){
    var words=normWords(q);
    if(!words.length) return [];
    var list=currentPool(), out=[], k, i, j, t, nameLower, nameWords, catLower, idLower, s, matched, best, sc, alts;
    for(k=0;k<list.length;k++){
      t=list[k];
      nameLower=t.name.toLowerCase();
      nameWords=nameLower.replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return !!w; });
      catLower=(t.cat||"").toLowerCase();
      idLower=(t.id||"").toLowerCase();
      s=0; matched=0;
      for(i=0;i<words.length;i++){
        alts=SYN[words[i]]||[words[i]];
        best=0;
        for(j=0;j<alts.length;j++){
          sc=wordScore(alts[j], nameWords, catLower, idLower);
          if(sc>best) best=sc;
          if(best>=5) break;
        }
        if(best>0) matched++;
        s+=best;
      }
      if(matched===0) continue;
      if(matched===words.length) s+=6; /* every word matched: rank first */
      /* Name starts with the query's first word (or one of its synonyms). */
      if(nameLower.indexOf(words[0])===0) s+=2;
      else {
        alts=SYN[words[0]]||[words[0]];
        for(j=0;j<alts.length;j++){
          if(nameLower.indexOf(alts[j])===0){ s+=1; break; }
        }
      }
      out.push({t:t, s:s});
    }
    out.sort(function(a,b){
      if(b.s!==a.s) return b.s-a.s;
      /* Same score: the most-used tools first, then the shortest name. */
      var ap=POPULAR_IDS[a.t.id]?0:1, bp=POPULAR_IDS[b.t.id]?0:1;
      if(ap!==bp) return ap-bp;
      var al=a.t.name.length, bl=b.t.name.length;
      if(al!==bl) return al-bl;
      return a.t.name<b.t.name?-1:(a.t.name>b.t.name?1:0);
    });
    return out.slice(0, n||6);
  }
  function renderHits(box, hits){
    if(!hits.length){ box.innerHTML='<a href="/tools/">No match — browse the A–Z list</a>'; box.hidden=false; return; }
    box.innerHTML=hits.map(function(x){
      var t=x.t;
      return '<a href="/'+t.id+'/">'+esc(t.name)+'<small>'+esc(t.blurb ? t.blurb : catLabel(t.cat))+'</small></a>';
    }).join("");
    box.hidden=false;
  }
  /* Tools whose name starts with one letter, shortest name first.
     Used for single-letter queries, which the normal scorer can't handle
     because it drops 1-letter words. */
  function prefixHits(letter, n){
    var list=currentPool(), out=[], i, t;
    for(i=0;i<list.length;i++){
      t=list[i];
      if(t.name && t.name.toLowerCase().charAt(0)===letter) out.push({t:t, s:0});
    }
    out.sort(function(a,b){
      /* Most-used tools first, then the shortest name. */
      var ap=POPULAR_IDS[a.t.id]?0:1, bp=POPULAR_IDS[b.t.id]?0:1;
      if(ap!==bp) return ap-bp;
      var al=a.t.name.length, bl=b.t.name.length;
      if(al!==bl) return al-bl;
      return a.t.name<b.t.name?-1:(a.t.name>b.t.name?1:0);
    });
    return out.slice(0, n||6);
  }
  /* Run a search. go=true means the user pressed Search/Enter: a single clear
     match (or an exact name match) opens straight away, using whatever
     results are already available — it never waits on a shard. */
  function runSearch(input, box, go){
    var q=input.value.trim();
    if(!q.length){ box.hidden=true; box.innerHTML=""; return; }
    if(q.length===1){
      /* Single letter: show tools starting with it. Instant results from
         the loaded pool if any, otherwise a loading line — then the full
         letter shard refines the list when it arrives. */
      var L=q.toLowerCase();
      if(!/^[a-z]$/.test(L)){ box.hidden=true; box.innerHTML=""; return; }
      var first=prefixHits(L, 6);
      if(first.length){ renderHits(box, first); }
      else { box.innerHTML='<div class="search-loading">Loading tools starting with “'+L.toUpperCase()+'”…</div>'; box.hidden=false; }
      loadShard(L).then(function(entries){
        var added=false, i;
        for(i=0;i<entries.length;i++){
          if(!POOL[entries[i].id]){ POOL[entries[i].id]=entries[i]; added=true; }
        }
        if(added) POOL_LIST=null;
        if(input.value.trim()===q && !box.hidden) renderHits(box, prefixHits(L, 6));
      });
      return;
    }
    /* 1. Instant results from the loaded pool (POPULAR at minimum). */
    var hits=scoreTools(q, 6);
    if(go){
      var exact=null;
      hits.forEach(function(x){ if(x.t.name.toLowerCase()===q.toLowerCase()) exact=x; });
      if(exact){ location.href="/"+exact.t.id+"/"; return; }
      if(hits.length===1){ location.href="/"+hits[0].t.id+"/"; return; }
      if(hits.length>1 && hits[0].s>=10 && hits[0].s>=hits[1].s+3){ location.href="/"+hits[0].t.id+"/"; return; }
    }
    renderHits(box, hits);
    /* 2. In parallel, fetch the shard(s) for the query and refine. */
    var letters=shardLetters(q);
    letters.forEach(function(L){
      if(SHARD_CACHE[L]) return;
      loadShard(L).then(function(entries){
        var added=false, i;
        for(i=0;i<entries.length;i++){
          if(!POOL[entries[i].id]){ POOL[entries[i].id]=entries[i]; added=true; }
        }
        if(added) POOL_LIST=null;
        if(input.value.trim()===q && !box.hidden) renderHits(box, scoreTools(q, 6));
      });
    });
    try{ box.scrollIntoView({block:"nearest"}); }catch(e){}
  }
  function wireSearch(input, box){
    if(!input || !box) return;
    var timer=null;
    input.setAttribute("enterkeyhint","search");
    input.addEventListener("input", function(){
      clearTimeout(timer);
      var q=input.value.trim();
      if(!q.length){ box.hidden=true; box.innerHTML=""; return; }
      timer=setTimeout(function(){ runSearch(input, box, false); }, 180);
    });
    input.addEventListener("keydown", function(e){
      if(e.key==="Enter"){ e.preventDefault(); runSearch(input, box, true); }
    });
    /* The visible Search button next to the input runs the search too. */
    var btn = input.parentElement ? input.parentElement.querySelector("button") : null;
    if(btn) btn.addEventListener("click", function(e){ e.preventDefault(); runSearch(input, box, true); });
    document.addEventListener("click", function(e){ if(!box.contains(e.target) && e.target!==input) box.hidden=true; });
  }
  wireSearch($("#head-search"), $("#head-results"));
  wireSearch($("#home-search"), $("#home-results"));


  /* ---------- homepage: daily streak, recently used, share, PWA ---------- */
  (function home(){
    var streakEl = document.getElementById("daily-streak");
    if(streakEl){
      var n = 0;
      try{
        var st = JSON.parse(localStorage.getItem("fcn_daily_streak_v2") || "null");
        n = (st && st.n) || 0;
        if(!n){
          var old = JSON.parse(localStorage.getItem("fcn_daily_streak") || "null");
          n = (old && old.n) || 0;
        }
      }catch(e){}
      streakEl.textContent = n > 0 ? ("🔥 " + n + "-day streak — keep it alive!") : "No streak yet — play today to start one!";
    }
    var recentBox = document.getElementById("recent-list");
    var recentSec = document.getElementById("recent-sec");
    if(recentBox && recentSec){
      var items = [];
      try{ items = JSON.parse(localStorage.getItem("fcn-recent") || "[]") || []; }catch(e){}
      if(items.length){
        recentSec.hidden = false;
        recentBox.innerHTML = items.slice(0, 6).map(function(t){
          return '<div class="rel-card"><a href="/' + esc(t.id) + '/">' + esc(t.name) + '</a></div>';
        }).join("");
      }
    }
    document.querySelectorAll("[data-share-home]").forEach(function(b){
      b.addEventListener("click", function(){
        var url = "https://freecalcnow.github.io/";
        var text = "FreeCalcNow — 15,394 free calculators, 78 games and a new puzzle every day. " + url;
        if(navigator.share){ navigator.share({title: document.title, text: text, url: url}).catch(function(){}); }
        else if(navigator.clipboard){ navigator.clipboard.writeText(text).then(function(){ b.textContent = "Link copied!"; setTimeout(function(){ b.textContent = "Share FreeCalcNow"; }, 2000); }); }
      });
    });
    document.querySelectorAll("[data-share-home-wa]").forEach(function(b){
      b.addEventListener("click", function(){
        var text = encodeURIComponent("FreeCalcNow — 15,394 free calculators, 78 games and a new puzzle every day. https://freecalcnow.github.io/");
        window.open("https://wa.me/?text=" + text, "_blank", "noopener");
      });
    });
    if("serviceWorker" in navigator){
      window.addEventListener("load", function(){
        navigator.serviceWorker.register("/sw.js").catch(function(){});
      });
    }
  })();

  /* ---------- tool page ---------- */
  var T = window.TOOLDATA;
  if(!T) return; // not a tool page
  var compute=null, computeErr=null;
  try{
    var src=(T.computeSrc||"").replace(/^compute\s*\(/, "function(");
    if(!src){ compute=null; }
    else if(T.id.indexOf("conv-")===0 && typeof resolveConv==="function"){
      var r=resolveConv(T.id);
      if(!r) throw new Error("converter not resolved");
      compute=new Function("a","b","fam","toBase","fromBase","factor","return ("+src+")")(r.a, r.b, r.fam, r.toBase, r.fromBase, r.factor);
    } else if(typeof resolveConvD==="function" && resolveConvD(T.id)){
      var d=resolveConvD(T.id);
      compute=new Function("units","keys","noteText","return ("+src+")")(d.units, d.keys, d.noteText);
    } else if(typeof resolveB5Conv==="function" && resolveB5Conv(T.id)){
      var b5=resolveB5Conv(T.id);
      compute=new Function("units","unitWord","return ("+src+")")(b5.units, b5.unitWord);
    } else {
      compute=new Function("return ("+src+")")();
    }
  }catch(e){ compute=null; computeErr=e.message; }
  function values(){
    var v={};
    (T.fields||[]).forEach(function(f){
      var el=document.getElementById("f_"+f.id);
      if(!el) return;
      if(f.type==="select") v[f.id]=el.value;
      else if(f.type==="number" || !f.type){
        var n=parseFloat(el.value);
        v[f.id]=isFinite(n)? n : f.def;
      } else v[f.id]=el.value;
    });
    return v;
  }
  /* Remember the numbers the user typed, so they are still there next visit. */
  var VALS_KEY="fcn-vals-"+T.id, saveTimer=null;
  function saveVals(){
    if(!compute) return;
    try{
      var v=values();
      var cur=document.getElementById("cur-sel");
      v._cur = cur ? cur.value : null;
      localStorage.setItem(VALS_KEY, JSON.stringify(v));
    }catch(e){}
  }
  function restoreVals(){
    if(!compute) return;
    var saved=null;
    try{ saved=JSON.parse(localStorage.getItem(VALS_KEY)||"null"); }catch(e){}
    if(!saved) return;
    (T.fields||[]).forEach(function(f){
      var el=document.getElementById("f_"+f.id);
      if(!el || saved[f.id]==null) return;
      el.value=saved[f.id];
    });
    var cur=document.getElementById("cur-sel");
    if(cur && saved._cur){ cur.value=saved._cur; try{ window.CUR=saved._cur; }catch(e){} }
  }
  /* Shareable result links: ?price=320000&r=6.5 reads straight into the form,
     so a shared link re-opens with the same numbers and the same answer.
     URL params win over saved values. */
  function applyUrlParams(){
    if(!compute) return;
    var q;
    try{ q = new URLSearchParams(location.search); }catch(e){ return; }
    var changed = false;
    (T.fields||[]).forEach(function(f){
      if(!q.has(f.id)) return;
      var el=document.getElementById("f_"+f.id);
      if(!el) return;
      var raw = q.get(f.id);
      if(f.type==="select"){ el.value=raw; changed=true; return; }
      var n=parseFloat(raw);
      if(isFinite(n)){ el.value=n; changed=true; }
      else if(raw!==""){ el.value=raw; changed=true; }
    });
    if(changed) saveVals();
  }
  /* The result link: every field, so the recipient sees exactly the same
     numbers and answer the sender saw. */
  function resultUrl(){
    var base = location.origin + location.pathname;
    var parts = [];
    (T.fields||[]).forEach(function(f){
      var el=document.getElementById("f_"+f.id);
      if(!el) return;
      var v = el.value;
      if(v==="" || v==null) return;
      parts.push(encodeURIComponent(f.id) + "=" + encodeURIComponent(v));
    });
    return parts.length ? base + "?" + parts.join("&") : base;
  }
  function bigResultText(){
    var big = document.getElementById("result-big");
    var text = document.title.replace(" — FreeCalcNow", "");
    if(big && big.textContent && big.textContent !== "—") text += ": " + big.textContent.trim();
    return text;
  }
  /* Recently used tools, for the homepage row (localStorage only). */
  function recordRecent(){
    try{
      var key = "fcn-recent";
      var items = JSON.parse(localStorage.getItem(key) || "[]") || [];
      items = items.filter(function(t){ return t.id !== T.id; });
      items.unshift({id: T.id, name: (window.FCN_PAGE && window.FCN_PAGE.toolName) || T.id, ts: Date.now()});
      localStorage.setItem(key, JSON.stringify(items.slice(0, 12)));
    }catch(e){}
  }
  function renderChart(chart){
    var box=$("#result-chart"); if(!box) return;
    box.innerHTML="";
    if(!chart || !chart.values || !chart.values.length) return;
    var vals=chart.values, max=Math.max.apply(null, vals.map(Math.abs).concat([1]));
    var bars=document.createElement("div"); bars.className="bar-wrap";
    vals.forEach(function(x){
      var b=document.createElement("div"); b.className="bar";
      b.style.height=Math.max(3, Math.round(Math.abs(x)/max*100))+"%";
      b.title=String(x);
      bars.appendChild(b);
    });
    box.appendChild(bars);
    if(chart.labels){ var labs=document.createElement("div"); labs.className="bar-labels"; chart.labels.forEach(function(l){ var sp=document.createElement("span"); sp.textContent=l; labs.appendChild(sp); }); box.appendChild(labs); }
    if(chart.cap){ var c=document.createElement("p"); c.className="bar-cap"; c.textContent=chart.cap; box.appendChild(c); }
  }
  function renderRows(rows){
    var box=$("#result-rows"); if(!box) return;
    box.innerHTML="";
    if(!rows || !rows.length) return;
    var tbl=document.createElement("table");
    rows.forEach(function(row){
      var tr=document.createElement("tr");
      row.forEach(function(cell, i){
        var td=document.createElement(i===0?"th":"td");
        td.textContent=String(cell);
        tr.appendChild(td);
      });
      tbl.appendChild(tr);
    });
    box.appendChild(tbl);
  }
  function run(){
    var big=$("#result-big"), sub=$("#result-sub"), note=$("#result-note");
    if(!compute) return; // custom tools (gpa/password-gen/json/qr) own their result area
    var out;
    try{ out=compute(values()); }catch(e){ if(big) big.textContent="—"; if(sub) sub.textContent="Check your numbers and try again."; return; }
    if(!out) return;
    if(big) big.textContent = out.big==null ? "—" : String(out.big);
    if(sub) sub.textContent = out.sub || "";
    if(note) note.textContent = out.note || "";
    renderRows(out.rows);
    renderChart(out.chart);
  }
  var form=$("#tool-form");
  if(form){
    form.addEventListener("input", function(){
      run();
      clearTimeout(saveTimer); saveTimer=setTimeout(saveVals, 400);
    });
    form.addEventListener("submit", function(e){ e.preventDefault(); run(); });
    var calc=$("#btn-calc"); if(calc) calc.addEventListener("click", function(e){ e.preventDefault(); run(); });
    var clr=$("#btn-clear"); if(clr) clr.addEventListener("click", function(){
      (T.fields||[]).forEach(function(f){
        var el=document.getElementById("f_"+f.id);
        if(el) el.value = (f.def==null?"":f.def);
      });
      try{ localStorage.removeItem(VALS_KEY); }catch(e){}
      run();
    });
  }
  var cur=$("#cur-sel");
  if(cur) cur.addEventListener("change", function(){
    try{ window.CUR=cur.value; }catch(e){}
    run(); saveVals();
  });
  restoreVals();
  applyUrlParams();
  recordRecent();
  run();

  /* ---------- feedback widget ---------- */
  document.querySelectorAll(".feedback").forEach(function(box){
    var slug=box.getAttribute("data-slug");
    var key="fcn-fb-"+slug;
    var saved=null;
    try{ saved=JSON.parse(localStorage.getItem(key)||"null"); }catch(e){}
    var stars=box.querySelectorAll(".stars button"), picked=saved?saved.stars:0;
    function paint(n){ stars.forEach(function(b,i){ b.classList.toggle("on", i<n); b.textContent = i<n ? "★" : "☆"; }); }
    stars.forEach(function(b,i){
      b.addEventListener("click", function(){ picked=i+1; paint(picked); });
    });
    paint(picked);
    var thanks=box.querySelector(".thanks"), formEl=box.querySelector(".fb-form");
    if(saved && thanks){ thanks.hidden=false; if(formEl) formEl.hidden=true; thanks.textContent="Thanks — you rated this "+saved.stars+" out of 5."; }
    var send=box.querySelector(".fb-send");
    if(send) send.addEventListener("click", function(){
      var comment=(box.querySelector(".fb-comment")||{}).value||"";
      try{ localStorage.setItem(key, JSON.stringify({stars:picked||5, comment:comment, ts:Date.now()})); }catch(e){}
      if(formEl) formEl.hidden=true;
      if(thanks){ thanks.hidden=false; thanks.textContent="Thanks for your feedback!"; }
    });
  });

  /* ---------- share / print ---------- */
  document.querySelectorAll("[data-share]").forEach(function(b){
    b.addEventListener("click", function(){
      var url=resultUrl(), title=document.title, text=bigResultText();
      if(navigator.share){ navigator.share({title:title, text:text, url:url}).catch(function(){}); }
      else if(navigator.clipboard){ navigator.clipboard.writeText(url).then(function(){ b.textContent="Link copied!"; setTimeout(function(){ b.textContent="Share this calculation"; }, 2000); }); }
      else { prompt("Copy this link:", url); }
    });
  });
  document.querySelectorAll("[data-share-wa]").forEach(function(b){
    b.addEventListener("click", function(){
      var text = bigResultText() + " — try it: " + resultUrl();
      window.open("https://wa.me/?text=" + encodeURIComponent(text), "_blank", "noopener");
    });
  });
  document.querySelectorAll("[data-copy-link]").forEach(function(b){
    b.addEventListener("click", function(){
      var url = resultUrl();
      function done(ok){ b.textContent = ok ? "Result link copied!" : "Copy failed — long-press the address bar"; setTimeout(function(){ b.textContent = "Copy result link"; }, 2500); }
      if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(url).then(function(){ done(true); }).catch(function(){ done(false); }); }
      else { prompt("Copy this link:", url); }
    });
  });
  document.querySelectorAll("[data-print]").forEach(function(b){
    b.addEventListener("click", function(){ window.print(); });
  });

  /* ---------- save this result (for the /saved/ page) ---------- */
  (function(){
    var sr=document.querySelector(".share-row");
    if(!sr) return;
    var btn=document.createElement("button");
    btn.type="button"; btn.className="btn btn-ghost";
    btn.textContent="\u{1F4BE} Save result";
    btn.addEventListener("click", function(){
      try{
        var key="fcn-saved-v1";
        var items=JSON.parse(localStorage.getItem(key)||"[]")||[];
        var url=resultUrl();
        items=items.filter(function(it){ return it.url!==url; });
        items.unshift({name:(window.FCN_PAGE&&window.FCN_PAGE.toolName)||document.title.replace(" — FreeCalcNow",""), url:url, result:bigResultText(), ts:Date.now()});
        localStorage.setItem(key, JSON.stringify(items.slice(0,50)));
        btn.textContent="\u2713 Saved — see /saved/";
        setTimeout(function(){ btn.textContent="\u{1F4BE} Save result"; }, 2500);
      }catch(e){ btn.textContent="Could not save on this device"; }
    });
    sr.appendChild(btn);
  })();
})();

/* Offline banner — shows whenever the browser reports offline, and hides
   again when the connection returns. Simple English, no fake data. */
(function(){
  function lastRatesWhen(){
    try{
      var best=null;
      for(var i=0;i<localStorage.length;i++){
        var k=localStorage.key(i);
        if(k && k.indexOf('fcn-rates-')===0){
          var v=JSON.parse(localStorage.getItem(k)||'null');
          if(v && v.fetchedAt && (!best || v.fetchedAt>best)) best=v.fetchedAt;
        }
      }
      if(!best) return '';
      var d=new Date(best);
      if(isNaN(d)) return '';
      return d.toLocaleString('en-GB',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
    }catch(e){ return ''; }
  }
  function banner(){
    var off=(typeof navigator!=='undefined' && navigator.onLine===false);
    var b=document.getElementById('fcn-offline');
    if(!off){ if(b) b.hidden=true; return; }
    if(!b){
      b=document.createElement('div');
      b.id='fcn-offline'; b.className='offline-banner'; b.setAttribute('role','status');
      var m=document.querySelector('main');
      if(m && m.parentNode) m.parentNode.insertBefore(b, m);
      else if(document.body) document.body.insertBefore(b, document.body.firstChild);
    }
    var when=lastRatesWhen();
    b.textContent=when
      ? ('You are offline — showing last prices from '+when+'. Calculators still work.')
      : 'You are offline — calculators still work. Live prices need internet.';
    b.hidden=false;
  }
  window.addEventListener('online', banner);
  window.addEventListener('offline', banner);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', banner);
  else banner();
})();

/* Daily reminder — opt-in only. If the user turned it on (localStorage
   fcn-remind=1) and today's daily puzzles are not all done yet, show one
   browser notification when they open the site. No server, no push:
   a website cannot notify while it is closed. Fires at most once a day. */
(function(){
  function todayStr(){ try{ return new Date().toISOString().slice(0,10); }catch(e){ return ""; } }
  function allDone(){
    try{
      var sc=JSON.parse(localStorage.getItem("fcn-daily-scores-v1")||"null");
      if(!sc || sc.date!==todayStr()) return false;
      var n=0; ["daily-number","word-guess","sudoku-mini"].forEach(function(g){ if(sc.scores && sc.scores[g]!==undefined) n++; });
      return n>=3;
    }catch(e){ return false; }
  }
  function fire(){
    try{
      if(localStorage.getItem("fcn-remind")!=="1") return;
      if(!("Notification" in window) || Notification.permission!=="granted") return;
      if(allDone()) return;
      var t=todayStr();
      if(localStorage.getItem("fcn-remind-shown")===t) return;
      localStorage.setItem("fcn-remind-shown", t);
      var title="FreeCalcNow — your daily puzzles are waiting";
      var opts={body:"Daily Number, Word Guess and Sudoku are ready. Keep your streak alive!", tag:"fcn-daily"};
      if(navigator.serviceWorker && navigator.serviceWorker.getRegistration){
        navigator.serviceWorker.getRegistration().then(function(reg){
          if(reg && reg.showNotification) reg.showNotification(title, opts);
          else new Notification(title, opts);
        }).catch(function(){ try{ new Notification(title, opts); }catch(e){} });
      } else new Notification(title, opts);
    }catch(e){}
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", fire);
  else fire();
})();
