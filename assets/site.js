/* FreeCalcNow site.js — tool-page boot, header search, feedback, share/print.
   Depends on /assets/engine.js (helpers, FAMS, resolveConv) loaded before this file. */
(function(){
  "use strict";
  function $(s, r){ return (r||document).querySelector(s); }
  function esc(s){ return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function cap(s){ s=String(s||""); return s ? s.charAt(0).toUpperCase()+s.slice(1) : s; }
  /* ---------- header + home search ---------- */
  var INDEX=null, INDEX_P=null;
  /* Instant fallback while the full index loads: the most-used tools. */
  var POPULAR=[
    {id:"mortgage",name:"Mortgage Calculator",cat:"Finance"},
    {id:"compound",name:"Compound Interest Calculator",cat:"Finance"},
    {id:"loan",name:"Loan / EMI Calculator",cat:"Finance"},
    {id:"bmi",name:"BMI Calculator",cat:"Health"},
    {id:"sip-calculator",name:"SIP Calculator",cat:"Finance"},
    {id:"emi-calculator",name:"EMI Calculator",cat:"Finance"},
    {id:"percentage-calculator",name:"Percentage Calculator",cat:"Math"},
    {id:"tip-calculator",name:"Tip Calculator",cat:"Everyday life"},
    {id:"age-calculator",name:"Age Calculator",cat:"Everyday life"},
    {id:"gpa-calculator",name:"GPA Calculator",cat:"Math"},
    {id:"salary-calculator",name:"Salary Calculator",cat:"Finance"},
    {id:"income-tax-calculator",name:"Income Tax Calculator",cat:"Finance"},
    {id:"salary-hourly",name:"Salary ↔ Hourly Calculator",cat:"Finance"},
    {id:"retirement",name:"Retirement Calculator",cat:"Finance"},
    {id:"savings-goal",name:"Savings Goal Calculator",cat:"Finance"},
    {id:"inflation",name:"Inflation Calculator",cat:"Finance"},
    {id:"roi",name:"Investment Return (ROI) Calculator",cat:"Finance"},
    {id:"calorie",name:"Calorie Calculator",cat:"Health"},
    {id:"tdee",name:"TDEE Calculator",cat:"Health"},
    {id:"discount",name:"Discount Calculator",cat:"Everyday life"},
    {id:"password-gen",name:"Password Generator",cat:"Other"},
    {id:"qr",name:"QR Code Generator",cat:"Other"},
    {id:"json",name:"JSON Formatter & Validator",cat:"Other"},
    {id:"debt-payoff",name:"Debt Payoff Calculator",cat:"Finance"}
  ];
  function loadIndex(){
    if(INDEX) return Promise.resolve(INDEX);
    if(INDEX_P) return INDEX_P;
    INDEX_P = fetch("/assets/tools-index.json").then(function(r){ return r.json(); }).then(function(j){ INDEX=j; return j; }).catch(function(){ INDEX=[]; return INDEX; });
    return INDEX_P;
  }
  /* Warm the search index shortly after the page loads, so typing is instant.
     Skipped when the user asked the browser to save data. */
  try{
    var saveData = navigator.connection && navigator.connection.saveData;
    if(!saveData) setTimeout(function(){ loadIndex(); }, 1500);
  }catch(e){}
  function scoreTools(q, n){
    var words=q.toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return w.length>1; });
    if(!words.length) return [];
    var list = (INDEX && INDEX.length) ? INDEX : POPULAR;
    return list.map(function(t){
      var name=t.name.toLowerCase(), hay=(t.name+" "+(t.blurb||"")+" "+t.cat).toLowerCase(), s=0;
      words.forEach(function(w){
        if(name.indexOf(w)>=0) s+=3;
        else if(hay.indexOf(w)>=0) s+=1;
      });
      return {t:t, s:s};
    }).filter(function(x){ return x.s>0; }).sort(function(a,b){ return b.s-a.s; }).slice(0,n||6);
  }
  function renderHits(box, hits){
    if(!hits.length){ box.innerHTML='<a href="/tools/">No match — browse the A–Z list</a>'; box.hidden=false; return; }
    box.innerHTML=hits.map(function(x){
      var t=x.t;
      return '<a href="/'+t.id+'/">'+esc(t.name)+'<small>'+esc(t.blurb ? t.blurb : cap(t.cat||""))+'</small></a>';
    }).join("");
    box.hidden=false;
  }
  /* Run a search. go=true means the user pressed Search/Enter: a single clear
     match (or an exact name match) opens straight away. */
  function runSearch(input, box, go){
    var q=input.value.trim();
    if(q.length<2){ box.hidden=true; box.innerHTML=""; return; }
    if(!INDEX){
      box.innerHTML='<div class="search-loading">Searching…</div>'; box.hidden=false;
      loadIndex().then(function(){ runSearch(input, box, go); });
      return;
    }
    var hits=scoreTools(q, 6);
    if(go){
      var exact=null;
      hits.forEach(function(x){ if(x.t.name.toLowerCase()===q.toLowerCase()) exact=x; });
      if(exact){ location.href="/"+exact.t.id+"/"; return; }
      if(hits.length===1){ location.href="/"+hits[0].t.id+"/"; return; }
      if(hits.length>1 && hits[0].s>=6 && hits[0].s>=hits[1].s+3){ location.href="/"+hits[0].t.id+"/"; return; }
    }
    renderHits(box, hits);
    try{ box.scrollIntoView({block:"nearest"}); }catch(e){}
  }
  function wireSearch(input, box){
    if(!input || !box) return;
    var timer=null;
    input.setAttribute("enterkeyhint","search");
    input.addEventListener("input", function(){
      clearTimeout(timer);
      var q=input.value.trim();
      if(q.length<2){ box.hidden=true; box.innerHTML=""; return; }
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
      var url=location.href, title=document.title;
      if(navigator.share){ navigator.share({title:title, url:url}).catch(function(){}); }
      else if(navigator.clipboard){ navigator.clipboard.writeText(url).then(function(){ b.textContent="Link copied!"; setTimeout(function(){ b.textContent="Share this calculation"; }, 2000); }); }
      else { prompt("Copy this link:", url); }
    });
  });
  document.querySelectorAll("[data-print]").forEach(function(b){
    b.addEventListener("click", function(){ window.print(); });
  });
})();
