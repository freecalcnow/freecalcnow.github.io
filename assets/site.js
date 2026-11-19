/* FreeCalcNow site.js — tool-page boot, header search, feedback, share/print.
   Depends on /assets/engine.js (helpers, FAMS, resolveConv) loaded before this file. */
(function(){
  "use strict";
  function $(s, r){ return (r||document).querySelector(s); }
  function esc(s){ return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  /* ---------- header + home search ---------- */
  var INDEX=null, INDEX_P=null;
  function loadIndex(){
    if(INDEX) return Promise.resolve(INDEX);
    if(INDEX_P) return INDEX_P;
    INDEX_P = fetch("/assets/tools-index.json").then(function(r){ return r.json(); }).then(function(j){ INDEX=j; return j; }).catch(function(){ INDEX=[]; return INDEX; });
    return INDEX_P;
  }
  function scoreTools(q, n){
    var words=q.toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return w.length>1; });
    if(!words.length) return [];
    return INDEX.map(function(t){
      var name=t.name.toLowerCase(), hay=(t.name+" "+(t.blurb||"")+" "+t.cat).toLowerCase(), s=0;
      words.forEach(function(w){ if(name.indexOf(w)>=0) s+=3; else if(hay.indexOf(w)>=0) s+=1; });
      return {t:t, s:s};
    }).filter(function(x){ return x.s>0; }).sort(function(a,b){ return b.s-a.s; }).slice(0,n||6).map(function(x){ return x.t; });
  }
  function wireSearch(input, box){
    if(!input || !box) return;
    var timer=null;
    input.addEventListener("input", function(){
      clearTimeout(timer);
      var q=input.value.trim();
      if(q.length<2){ box.hidden=true; box.innerHTML=""; return; }
      timer=setTimeout(function(){
        loadIndex().then(function(){
          var hits=scoreTools(q, 6);
          if(!hits.length){ box.innerHTML='<a href="/tools/">No match — browse the A–Z list</a>'; box.hidden=false; return; }
          box.innerHTML=hits.map(function(t){ return '<a href="/'+t.id+'/">'+esc(t.name)+'<small>'+esc(t.blurb||"")+'</small></a>'; }).join("");
          box.hidden=false;
        });
      }, 180);
    });
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
    form.addEventListener("input", run);
    form.addEventListener("submit", function(e){ e.preventDefault(); run(); });
    var calc=$("#btn-calc"); if(calc) calc.addEventListener("click", function(e){ e.preventDefault(); run(); });
    var clr=$("#btn-clear"); if(clr) clr.addEventListener("click", function(){
      (T.fields||[]).forEach(function(f){
        var el=document.getElementById("f_"+f.id);
        if(el) el.value = (f.def==null?"":f.def);
      });
      run();
    });
  }
  var cur=$("#cur-sel");
  if(cur) cur.addEventListener("change", function(){
    try{ window.CUR=cur.value; }catch(e){}
    run();
  });
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
