/* FreeCalcNow shared compute engine — helpers + unit data extracted from the verified FreeCalcNow catalogue (build v36). No DOM access at load. */
var CUR="USD"; var fmtCache={};
function fmtV(x){ if(!isFinite(x)) return "\u2014"; if(x===0) return "0"; if(Math.abs(x)>=1e15||Math.abs(x)<1e-4) return x.toExponential(5); return num(x,Math.abs(x)>=100?2:Math.abs(x)>=1?4:6); }
function fmtF(f){ if(!isFinite(f)) return "\u2014"; if(f!==0&&(Math.abs(f)>=1e15||Math.abs(f)<1e-7)) return f.toExponential(4); return String(parseFloat(f.toPrecision(8))); }
function slug(s){ return String(s).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,""); }
function U(n,s,f){ return {n:n,s:s,f:f}; }
function UF(n,s,to,from){ return {n:n,s:s,to:to,from:from}; }
function money(v,dec){
  if(!isFinite(v)) return "—";
  try{
    const k=CUR+(dec===0?"0":"2");
    if(!fmtCache[k]) fmtCache[k]=new Intl.NumberFormat("en-US",{style:"currency",currency:CUR,minimumFractionDigits:dec===0?0:2,maximumFractionDigits:dec===0?0:2});
    return fmtCache[k].format(v);
  }catch(e){ return "$"+Number(v).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}); }
}
function num(v,dec){ if(!isFinite(v)) return "—"; return Number(v).toLocaleString("en-US",{minimumFractionDigits:dec||0,maximumFractionDigits:dec===undefined?2:dec}); }
function pct(v,dec){ return num(v,dec===undefined?2:dec)+"%"; }
function pmtCalc(P,annualRate,n){ const r=annualRate/100/12; if(n<=0) return 0; if(r===0) return P/n; const f=Math.pow(1+r,n); return P*r*f/(f-1); }
function fvCalc(P,pmt,annualRate,years){ const i=annualRate/100/12, n=Math.round(years*12); if(n<=0) return P; if(i===0) return P+pmt*n; const f=Math.pow(1+i,n); return P*f+pmt*((f-1)/i); }
function icon(name){ return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+(IC[name]||IC.chart)+'</svg>'; }
function cardHTML(t){
  return '<button class="tool-card" data-tool="'+t.id+'" data-cat="'+t.cat+'"><span class="tool-ic">'+icon(t.icon)+'</span><span><h3>'+esc(t.name)+'</h3><p>'+esc(t.blurb)+'</p></span></button>';
}
function bindCards(){
  document.querySelectorAll(".tool-card").forEach(b=>b.addEventListener("click",()=>openTool(b.dataset.tool)));
}
function renderCats(){
  $("#cat-rows").innerHTML=CATS.map(c=>{
    const n=TOOLS.filter(t=>t.cat===c.id).length;
    return '<button class="cat-row" data-cat-open="'+c.id+'" data-cat="'+c.id+'"><span class="tool-ic">'+icon(c.icon||"chart")+'</span><span><h3>'+esc(c.name)+'</h3><p>'+esc(c.sub)+'</p></span><span class="cnt">'+n+' calculators</span><span class="chev" aria-hidden="true">›</span></button>';
  }).join("");
  document.querySelectorAll("[data-cat-open]").forEach(b=>b.addEventListener("click",()=>openCategory(b.dataset.catOpen)));
}
function singWord(w){ if(w.length>3&&/(ches|shes|sses|xes)$/.test(w)) return w.slice(0,-2); if(w.length>2&&w.charAt(w.length-1)==="s"&&w.slice(-2)!=="ss") return w.slice(0,-1); return w; }
function searchTools(raw){
  const phrase=String(raw||"").trim().toLowerCase();
  if(!phrase) return [];
  let tokens=phrase.split(/[^a-z0-9µ°]+/).filter(Boolean).filter(w=>!/^\d+(\.\d+)?$/.test(w)&&!SEARCH_STOP[w]);
  if(!tokens.length) tokens=phrase.split(/[^a-z0-9µ°]+/).filter(Boolean);
  if(!tokens.length) return [];
  const toksN=tokens.map(singWord), joined=toksN.join(" ");
  const scored=[];
  for(const t of TOOLS){
    if(!t._hay){
      const words=(t.name+" "+t.blurb+" "+t.q).toLowerCase().split(/[^a-z0-9µ°]+/).filter(Boolean);
      t._hay=" "+words.map(singWord).join(" ")+" ";
      t._nameN=" "+t.name.toLowerCase().split(/[^a-z0-9µ°]+/).filter(Boolean).map(singWord).join(" ")+" ";
      t._qRaw=(t.q||"").toLowerCase();
    }
    let ok=true, score=0, allInName=true;
    for(const tok of toksN){ if(t._hay.indexOf(" "+tok+" ")===-1&&t._hay.indexOf(tok)===-1){ ok=false; break; } }
    if(!ok) continue;
    if(t._nameN.indexOf(" "+joined+" ")!==-1) score+=120;
    else if(t._hay.indexOf(" "+joined+" ")!==-1) score+=50;
    const nameTrim=t._nameN.trim();
    if(nameTrim===joined||nameTrim===joined+" calculator") score+=200;
    const nw=nameTrim.split(" ");
    if(nw.length>=3&&nw[1]==="to"&&toksN.length>=2){
      const fromOk=nw[0]===toksN[0]||(SEARCH_SYM[tokens[0]]&&singWord(SEARCH_SYM[tokens[0]].split(" ")[0])===nw[0]);
      const lastRaw=tokens[tokens.length-1];
      const toOk=nw[2]===toksN[toksN.length-1]||(SEARCH_SYM[lastRaw]&&singWord(SEARCH_SYM[lastRaw].split(" ")[0])===nw[2]);
      if(fromOk&&toOk) score+=150;
    }
    for(let i=0;i<toksN.length;i++){
      const tok=toksN[i];
      let inName=t._nameN.indexOf(" "+tok+" ")!==-1;
      if(!inName&&SEARCH_SYM[tokens[i]]){ const ex=SEARCH_SYM[tokens[i]]; inName=ex.split(" ").every(w=>t._nameN.indexOf(" "+singWord(w)+" ")!==-1); }
      if(inName) score+=10;
      else{ allInName=false; score+=(t._qRaw.indexOf(tokens[i])!==-1||t._qRaw.indexOf(tok)!==-1)?4:1; }
    }
    if(allInName) score+=40;
    scored.push({t:t,s:score});
  }
  scored.sort((a,b)=>b.s-a.s||a.t.name.localeCompare(b.t.name));
  return scored.map(x=>x.t);
}
function renderGrid(){
  const term=searchTerm.trim().toLowerCase();
  const searching=term.length>0;
  $("#cat-rows").classList.toggle("hidden",searching);
  const bh=$("#browse-head"); if(bh) bh.classList.toggle("hidden",searching);
  $("#search-results").classList.toggle("hidden",!searching);
  const moreEl=$("#search-more");
  if(!searching){ $("#tool-sections").innerHTML=""; if(moreEl) moreEl.classList.add("hidden"); return; }
  const list=searchTools(searchTerm);
  $("#search-title").textContent=list.length?("Results for “"+searchTerm.trim()+"” — "+list.length+" found"):"No results";
  const shown=list.slice(0,SEARCH_CAP);
  $("#tool-sections").innerHTML=shown.length?'<div class="grid">'+shown.map(cardHTML).join("")+'</div>':"";
  if(moreEl){
    if(list.length>shown.length){ moreEl.textContent="Showing the best "+shown.length+" of "+list.length+" matches — keep typing to narrow it down, or ask the assistant below."; moreEl.classList.remove("hidden"); }
    else moreEl.classList.add("hidden");
  }
  $("#no-results").classList.toggle("hidden",list.length>0);
  bindCards();
}
function openCategory(id){
  const c=CATS.find(x=>x.id===id); if(!c) return;
  const list=TOOLS.filter(t=>t.cat===id);
  $("#home-view").classList.add("hidden"); $("#tool-view").classList.add("hidden"); $("#game-view").classList.add("hidden"); $("#settings-view").classList.add("hidden"); $("#chat-view").classList.add("hidden"); $("#cat-view").classList.remove("hidden");
  $("#cat-title").textContent=c.name+" calculators";
  $("#cat-count").textContent=list.length+" calculators";
  $("#cat-sub").textContent=c.sub;
  $("#cat-grid").innerHTML='<div class="grid">'+list.slice(0,96).map(cardHTML).join("")+'</div>';
  const cm=$("#cat-more");
  if(cm){
    if(list.length>96){ cm.textContent="Showing the first 96 of "+list.length+" tools in this shelf — use the search box on the home page (or ask the assistant) to jump straight to any tool."; cm.classList.remove("hidden"); }
    else cm.classList.add("hidden");
  }
  bindCards();
  window.scrollTo({top:0,behavior:"instant"});
}
function fieldHTML(f){
  const hint=f.hint?' <span class="hint">'+esc(f.hint)+'</span>':"";
  if(f.type==="select"){
    return '<div class="field"><label for="f-'+f.id+'">'+esc(f.label)+hint+'</label><select id="f-'+f.id+'" data-fid="'+f.id+'">'
      +f.options.map(o=>'<option value="'+esc(o.v)+'"'+(String(f.def)===String(o.v)?" selected":"")+'>'+esc(o.t)+'</option>').join("")+'</select></div>';
  }
  if(f.type==="date"){
    return '<div class="field"><label for="f-'+f.id+'">'+esc(f.label)+hint+'</label><input type="date" id="f-'+f.id+'" data-fid="'+f.id+'" value="'+esc(f.def||"")+'"></div>';
  }
  if(f.type==="textarea"){
    return '<div class="field"><label for="f-'+f.id+'">'+esc(f.label)+hint+'</label><textarea id="f-'+f.id+'" data-fid="'+f.id+'" placeholder="'+esc(f.ph||"")+'">'+esc(f.def||"")+'</textarea></div>';
  }
  if(f.type==="text"){
    return '<div class="field"><label for="f-'+f.id+'">'+esc(f.label)+hint+'</label><input type="text" id="f-'+f.id+'" data-fid="'+f.id+'" value="'+esc(f.def||"")+'" placeholder="'+esc(f.ph||"")+'"></div>';
  }
  return '<div class="field"><label for="f-'+f.id+'">'+esc(f.label)+hint+'</label><input type="number" inputmode="decimal" id="f-'+f.id+'" data-fid="'+f.id+'" value="'+esc(f.def)+'" step="'+(f.step||"any")+'"></div>';
}
function resultHTML(r){
  if(!r) return "";
  let h="";
  if(r.big!==undefined) h+='<div class="result-big num">'+esc(r.big)+'</div>';
  if(r.sub) h+='<p class="result-sub">'+esc(r.sub)+'</p>';
  if(r.rows&&r.rows.length) h+='<table class="breakdown"><tbody>'+r.rows.map(row=>'<tr><td>'+esc(row[0])+'</td><td class="num">'+esc(row[1])+'</td></tr>').join("")+'</tbody></table>';
  if(r.chart&&r.chart.values.length>1){
    const max=Math.max.apply(null,r.chart.values.concat([1]));
    h+='<div class="bar-wrap" aria-hidden="true">'+r.chart.values.map(v=>'<div class="bar" style="height:'+Math.max(3,Math.round(v/max*100))+'%"></div>').join("")+'</div>';
    if(r.chart.labels) h+='<div class="bar-labels" aria-hidden="true">'+r.chart.labels.map(l=>'<span>'+esc(l)+'</span>').join("")+'</div>';
    if(r.chart.cap) h+='<p class="bar-cap">'+esc(r.chart.cap)+'</p>';
  }
  if(r.table){
    h+='<div class="table-scroll" style="margin-top:14px"><table><thead><tr>'+r.table.head.map(x=>'<th>'+esc(x)+'</th>').join("")+'</tr></thead><tbody>'
      +r.table.rows.map(row=>'<tr>'+row.map(c=>'<td class="num">'+esc(c)+'</td>').join("")+'</tr>').join("")+'</tbody></table></div>';
  }
  if(r.note) h+='<p class="note">'+esc(r.note)+'</p>';
  if(r.extra) h+=r.extra;
  return h;
}
function openTool(id){
  const t=toolById(id); if(!t) return;
  const calc=CALCS[id];
  $("#home-view").classList.add("hidden"); $("#game-view").classList.add("hidden"); $("#cat-view").classList.add("hidden"); $("#settings-view").classList.add("hidden"); $("#chat-view").classList.add("hidden"); $("#tool-view").classList.remove("hidden");
  $("#tool-title").textContent=t.name;
  $("#tool-intro").textContent=calc.intro;
  $("#tool-formula").textContent=calc.formula;
  $("#tool-example").textContent=calc.example;
  const etx=$("#tool-example-top"); if(etx) etx.textContent=calc.example;
  $("#tool-faqs").innerHTML=calc.faqs.map(f=>'<details class="faq"><summary>'+esc(f[0])+'</summary><p>'+esc(f[1])+'</p></details>').join("");
  $("#tool-related").innerHTML=calc.related.map(r=>'<button data-rel="'+r+'">'+esc(toolById(r).name.replace(" Calculator",""))+'</button>').join("");
  document.querySelectorAll("#tool-related button").forEach(b=>b.addEventListener("click",()=>openTool(b.dataset.rel)));
  const body=$("#tool-body");
  if(calc.custom){ calc.custom(body); currentCalc=null; }
  else{
    currentCalc=calc;
    body.innerHTML='<div class="calc-layout"><section class="panel"><h2><span class="step-badge" aria-hidden="true">1</span>Type your numbers</h2><div id="calc-fields">'
      +calc.fields.map(fieldHTML).join("")+'</div><p class="err" id="calc-err"></p><p class="prefill-note">The boxes start filled with the example above — just change the numbers to yours.</p><button class="btn btn-ghost" id="calc-reset" type="button">Put the example numbers back</button></section>'
      +'<section class="panel result-panel" aria-live="polite"><h2><span class="step-badge" aria-hidden="true">2</span>Your answer</h2><div id="calc-result"></div>'
      +'<div class="copyrow"><button class="btn btn-ghost" id="calc-copy">Copy result</button><button class="btn btn-ghost" id="calc-dl" type="button">Download result</button><button class="btn btn-ghost" id="calc-wa" type="button">Share on WhatsApp</button></div><p id="calc-copied" style="color:var(--accent-dark);font-weight:600;min-height:1.2em"></p></section></div>';
    document.querySelectorAll("#calc-fields [data-fid]").forEach(el=>{ el.addEventListener("input",runCalc); el.addEventListener("change",runCalc); });
    $("#calc-copy").addEventListener("click",()=>{
      const r=$("#calc-result").innerText.trim();
      if(navigator.clipboard) navigator.clipboard.writeText(t.name+"\n"+r).then(()=>{$("#calc-copied").textContent="Copied ✓";});
    });
    const rst=$("#calc-reset"); if(rst) rst.addEventListener("click",()=>openTool(id));
    const dlb=$("#calc-dl"); if(dlb) dlb.addEventListener("click",()=>{
      const r=$("#calc-result").innerText.trim(); if(!r) return;
      try{
        const blob=new Blob([t.name+" — FreeCalcNow\n\n"+r+"\n"],{type:"text/plain"});
        const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=id+"-result.txt";
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(()=>URL.revokeObjectURL(a.href),4000);
        $("#calc-copied").textContent="Downloaded ✓ — a small text file with your result.";
      }catch(e){ $("#calc-copied").textContent="Download is not available here — use Copy result instead."; }
    });
    const wab=$("#calc-wa"); if(wab) wab.addEventListener("click",()=>{
      const r=$("#calc-result").innerText.trim(); if(!r) return;
      window.open("https://wa.me/?text="+encodeURIComponent(t.name+" — worked out on FreeCalcNow:\n"+r),"_blank");
    });
    runCalc();
  }
  window.scrollTo({top:0,behavior:"instant"});
}
function collectValues(){
  const v={};
  document.querySelectorAll("#calc-fields [data-fid]").forEach(el=>{
    const f=currentCalc.fields.find(x=>x.id===el.dataset.fid);
    if(!f) return;
    if(f.type==="select"||f.type==="date"||f.type==="text"||f.type==="textarea") v[f.id]=el.value;
    else v[f.id]=parseFloat(el.value);
  });
  return v;
}
function runCalc(){
  if(!currentCalc) return;
  const v=collectValues();
  const errEl=$("#calc-err");
  const bad=currentCalc.fields.find(f=>f.type!=="select"&&f.type!=="date"&&f.type!=="text"&&f.type!=="textarea"&&(isNaN(v[f.id])||v[f.id]<(f.min!==undefined?f.min:-Infinity)||(f.max!==undefined&&v[f.id]>f.max)));
  if(bad){ errEl.textContent="Please enter a valid value for “"+bad.label+"”"+(bad.min!==undefined?" (minimum "+bad.min+")":"")+"."; $("#calc-result").innerHTML=""; return; }
  errEl.textContent="";
  try{ $("#calc-result").innerHTML=resultHTML(currentCalc.compute(v)); }
  catch(e){ errEl.textContent="Something in those numbers cannot be calculated — check for a zero or negative value where one cannot work."; }
}
function goHome(){ $("#tool-view").classList.add("hidden"); $("#game-view").classList.add("hidden"); $("#cat-view").classList.add("hidden"); $("#settings-view").classList.add("hidden"); const cv0=$("#chat-view"); if(cv0){ cv0.classList.add("hidden"); cv0.style.cssText=""; } document.body.classList.remove("in-chat"); $("#home-view").classList.remove("hidden"); window.scrollTo({top:0,behavior:"instant"}); }
function payoff(pay){ if(pay<=0) return null; if(r>0&&pay<=v.bal*r) return null; let b=v.bal,m=0,ti=0; while(b>0&&m<1200){ const i=b*r; ti+=i; b=b+i-pay; m++; } return {months:m,interest:ti,total:v.bal+ti}; }
function pool(){
    let p="";
    if($("#pg-upper").checked)p+="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if($("#pg-lower").checked)p+="abcdefghijklmnopqrstuvwxyz";
    if($("#pg-digits").checked)p+="0123456789";
    if($("#pg-symbols").checked)p+="!@#$%^&*()-_=+[]{}<>?";
    if($("#pg-noambig").checked)p=p.replace(/[0O1lI]/g,"");
    return p;
  }
function gen(){
    const box=$("#qr-box"); box.innerHTML=""; $("#qr-err").textContent="";
    const text=$("#qr-in").value.trim(), size=parseInt($("#qr-size").value,10);
    if(!text){ $("#qr-err").textContent="Enter a link or some text first."; $("#qr-dl").classList.add("hidden"); return; }
    if(typeof QRCode==="undefined"){ $("#qr-err").textContent="The QR library could not load (network). Your text is fine — reconnect and try again."; return; }
    new QRCode(box,{text:text,width:size,height:size,correctLevel:QRCode.CorrectLevel.M});
    setTimeout(()=>{ const c=box.querySelector("canvas"); if(c){ const a=$("#qr-dl"); a.href=c.toDataURL("image/png"); a.classList.remove("hidden"); } },60);
  }
function parse(){ const raw=$("#js-in").value; try{ return {ok:true,val:JSON.parse(raw)}; }catch(e){ return {ok:false,err:e.message}; } }
function show(res,mode){
    const errEl=$("#js-err"), okEl=$("#js-ok");
    if(!res.ok){ errEl.textContent="Invalid JSON — "+res.err; okEl.textContent=""; if(mode!=="validate") $("#js-out").value=""; return; }
    errEl.textContent=""; okEl.textContent="✓ Valid JSON";
    if(mode==="format") $("#js-out").value=JSON.stringify(res.val,null,2);
    if(mode==="min") $("#js-out").value=JSON.stringify(res.val);
  }
function gradeOpts(sel){ return Object.keys(PTS).map(g=>'<option value="'+g+'"'+(g===sel?" selected":"")+'>'+g+' ('+PTS[g].toFixed(1)+')</option>').join(""); }
function levelOpts(sel){ return [["reg","Regular"],["hon","Honours (+0.5)"],["ap","AP / IB (+1.0)"]].map(o=>'<option value="'+o[0]+'"'+(o[0]===sel?" selected":"")+'>'+o[1]+'</option>').join(""); }
function render(){
    $("#gpa-rows").innerHTML=courses.map((c,i)=>'<div class="gpa-row">'
     +'<div class="field" style="margin:0"><label for="gpa-g-'+i+'">Grade</label><select id="gpa-g-'+i+'" data-i="'+i+'" data-k="g">'+gradeOpts(c.g)+'</select></div>'
     +'<div class="field" style="margin:0"><label for="gpa-c-'+i+'">Credits</label><input type="number" inputmode="decimal" id="gpa-c-'+i+'" data-i="'+i+'" data-k="c" value="'+c.c+'" min="0" step="0.5"></div>'
     +'<div class="field" style="margin:0"><label for="gpa-l-'+i+'">Level</label><select id="gpa-l-'+i+'" data-i="'+i+'" data-k="l">'+levelOpts(c.l)+'</select></div>'
     +'<button class="btn btn-ghost" type="button" data-del="'+i+'" aria-label="Remove course '+(i+1)+'" style="min-height:2.9rem;padding:0 12px">✕</button></div>').join("");
    document.querySelectorAll("#gpa-rows [data-k]").forEach(el=>{
      el.addEventListener("input",()=>{ const c=courses[+el.dataset.i]; if(el.dataset.k==="c") c.c=parseFloat(el.value)||0; else c[el.dataset.k]=el.value; calc(); });
      el.addEventListener("change",()=>{ const c=courses[+el.dataset.i]; if(el.dataset.k==="c") c.c=parseFloat(el.value)||0; else c[el.dataset.k]=el.value; calc(); });
    });
    document.querySelectorAll("#gpa-rows [data-del]").forEach(b=>b.addEventListener("click",()=>{ courses.splice(+b.dataset.del,1); if(!courses.length) courses.push({g:"A",c:3,l:"reg"}); render(); }));
    calc();
  }
function calc(){
    let credits=0,points=0,wpoints=0;
    courses.forEach(c=>{ const cr=Math.max(0,c.c||0), base=PTS[c.g]||0, bonus=base>0?(c.l==="hon"?0.5:c.l==="ap"?1.0:0):0;
      credits+=cr; points+=base*cr; wpoints+=Math.min(5,base+bonus)*cr; });
    const box=$("#gpa-result");
    if(credits<=0){ box.innerHTML='<p class="result-sub">Add at least one course with credits above zero.</p>'; return; }
    const gpa=points/credits, wgpa=wpoints/credits;
    box.innerHTML='<div class="result-big num">'+gpa.toFixed(2)+'</div><p class="result-sub">unweighted GPA on the 4.0 scale, across '+num(credits,1)+' credits and '+courses.length+' course'+(courses.length===1?"":"s")+'.</p>'
     +'<table class="breakdown"><tbody><tr><td>Unweighted GPA</td><td class="num">'+gpa.toFixed(2)+'</td></tr>'
     +'<tr><td>Weighted GPA (Honours / AP)</td><td class="num">'+wgpa.toFixed(2)+'</td></tr>'
     +'<tr><td>Total credits</td><td class="num">'+num(credits,1)+'</td></tr>'
     +'<tr><td>Total grade points</td><td class="num">'+num(points,1)+'</td></tr></tbody></table>';
  }
function utcDateStr(d){ return d.toISOString().slice(0,10); }
function puzzleNumber(dateStr){
  const parts=dateStr.split("-").map(Number);
  const days=Math.floor(Date.UTC(parts[0],parts[1]-1,parts[2])/86400000);
  return days-20453; /* #1 = 1 Jan 2026 */
}
function dailyAnswer(dateStr){
  let h=2166136261>>>0; const s="daily-number-"+dateStr;
  for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619)>>>0; }
  let out="";
  for(let i=0;i<4;i++){ h^=(h<<13)>>>0; h>>>=0; h^=(h>>17); h^=(h<<5)>>>0; h>>>=0; out+=String(h%10); }
  return out;
}
function scoreGuess(guess,answer){
  const res=["grey","grey","grey","grey"], used=[false,false,false,false];
  for(let i=0;i<4;i++){ if(guess[i]===answer[i]){ res[i]="green"; used[i]=true; } }
  for(let i=0;i<4;i++){ if(res[i]==="green") continue; for(let j=0;j<4;j++){ if(!used[j]&&guess[i]===answer[j]){ res[i]="yellow"; used[j]=true; break; } } }
  return res;
}
function resetGameForToday(){
  const ds=utcDateStr(new Date());
  if(G.date===ds) return;
  G.date=ds; G.answer=dailyAnswer(ds); G.num=puzzleNumber(ds);
  G.guesses=[]; G.scores=[]; G.current=""; G.status="playing"; G.doneShown=false;
  renderGame();
}
function renderGame(){
  $("#game-num").textContent="#"+G.num+" · "+G.date+" (UTC)";
  const st=G.stats;
  $("#game-stats").innerHTML=
    '<div class="stat"><b class="num">'+st.played+'</b><span>Played</span></div>'
   +'<div class="stat"><b class="num">'+(st.played?Math.round(st.wins/st.played*100):0)+'%</b><span>Win rate</span></div>'
   +'<div class="stat"><b class="num">🔥 '+st.streak+'</b><span>Win streak</span></div>'
   +'<div class="stat"><b class="num">'+st.best+'</b><span>Best streak</span></div>'
   +'<div class="stat"><b class="num">'+G.freezes+'</b><span>Freezes banked</span></div>';
  let board="";
  for(let r=0;r<6;r++){
    board+='<div class="grow">';
    for(let c=0;c<4;c++){
      let ch="",cls="cell";
      if(r<G.guesses.length){ ch=G.guesses[r][c]; cls+=" "+G.scores[r][c]; }
      else if(r===G.guesses.length&&G.status==="playing"){ ch=G.current[c]||""; if(ch) cls+=" filled"; }
      board+='<div class="'+cls+'">'+esc(ch)+'</div>';
    }
    board+="</div>";
  }
  $("#board").innerHTML=board;
  const rank={green:3,yellow:2,grey:1};
  const keyState={};
  G.guesses.forEach((g,r)=>{ g.split("").forEach((d,i)=>{ const s=G.scores[r][i]; if(!keyState[d]||rank[s]>rank[keyState[d]]) keyState[d]=s; }); });
  const keys=["1","2","3","4","5","6","7","8","9","0"];
  $("#keypad").innerHTML=keys.map(k=>'<button data-key="'+k+'" class="'+(keyState[k]||"")+'" aria-label="Digit '+k+'">'+k+'</button>').join("")
   +'<button data-key="enter" class="wide">Enter</button><button data-key="del" class="wide">⌫ Delete</button>';
  document.querySelectorAll("#keypad button").forEach(b=>b.addEventListener("click",()=>gameKey(b.dataset.key)));
  if(G.status==="playing") $("#game-msg").textContent=G.guesses.length===0?"Type your first guess — 4 digits.":"Guess "+(G.guesses.length+1)+" of 6";
  if(G.status!=="playing"&&!G.doneShown){ G.doneShown=true; showGameDone(); }
  if(G.status==="playing") $("#game-done").classList.add("hidden");
}
function gameKey(k){
  if(G.status!=="playing") return;
  if(/^[0-9]$/.test(k)){ if(G.current.length<4){ G.current+=k; renderGame(); } return; }
  if(k==="del"){ G.current=G.current.slice(0,-1); renderGame(); return; }
  if(k==="enter"){
    if(G.current.length<4){ $("#game-msg").textContent="Your guess needs all 4 digits."; return; }
    const guess=G.current, score=scoreGuess(guess,G.answer);
    G.guesses.push(guess); G.scores.push(score); G.current="";
    if(guess===G.answer){
      G.status="won"; G.stats.played++; G.stats.wins++; G.stats.streak++; G.stats.best=Math.max(G.stats.best,G.stats.streak);
      G.stats.dist[G.guesses.length-1]++;
      if(G.stats.streak>0&&G.stats.streak%7===0&&G.freezes<1) G.freezes=1;
      $("#game-msg").textContent="🎉 Solved in "+G.guesses.length+(G.guesses.length===1?" try!":" tries!");
    } else if(G.guesses.length>=6){
      G.status="lost"; G.stats.played++; G.stats.streak=0;
      $("#game-msg").textContent="Out of tries — today’s number was "+G.answer+". A new puzzle lands at 00:00 UTC.";
    }
    renderGame();
  }
}
function shareText(){
  const emoji={green:"🟩",yellow:"🟨",grey:"⬛"};
  const grid=G.scores.map(row=>row.map(s=>emoji[s]).join("")).join("\n");
  const score=G.status==="won"?G.guesses.length+"/6":"X/6";
  return "Daily Number #"+G.num+" — "+score+" 🔢\n"+grid+"\n🔥 "+G.stats.streak+"-day streak · Play free on FreeCalcNow";
}
function showGameDone(){
  const won=G.status==="won";
  $("#game-done-title").textContent=won?"Solved in "+G.guesses.length+(G.guesses.length===1?" try 🎉":" tries 🎉"):"So close — it was "+G.answer;
  $("#share-grid").textContent=G.scores.map(row=>row.map(s=>({green:"🟩",yellow:"🟨",grey:"⬛"}[s])).join("")).join("\n");
  const txt=encodeURIComponent(shareText());
  $("#share-wa").href="https://wa.me/?text="+txt;
  $("#share-x").href="https://x.com/intent/post?text="+txt;
  $("#share-tg").href="https://t.me/share/url?url=&text="+txt;
  const max=Math.max.apply(null,G.stats.dist.concat([1]));
  $("#game-dist").innerHTML=G.stats.dist.map((n,i)=>'<div class="drow"><span style="width:14px;font-weight:700">'+(i+1)+'</span><span class="dbar" style="width:'+Math.max(8,n/max*100)+'%">'+n+'</span></div>').join("");
  $("#game-done").classList.remove("hidden");
}
function openGame(){
  $("#home-view").classList.add("hidden"); $("#tool-view").classList.add("hidden"); $("#cat-view").classList.add("hidden"); $("#settings-view").classList.add("hidden"); $("#chat-view").classList.add("hidden"); $("#game-view").classList.remove("hidden");
  resetGameForToday(); renderGame();
  window.scrollTo({top:0,behavior:"instant"});
}
function tickCountdown(){
  const now=new Date();
  const next=Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate()+1,0,0,0);
  let s=Math.max(0,Math.floor((next-now.getTime())/1000));
  const hh=String(Math.floor(s/3600)).padStart(2,"0"), mm=String(Math.floor(s%3600/60)).padStart(2,"0"), ss=String(s%60).padStart(2,"0");
  const str=hh+":"+mm+":"+ss;
  const a=$("#gb-countdown"); if(a) a.textContent=str;
  const b=$("#game-countdown2"); if(b) b.textContent=str;
  const ds=utcDateStr(now);
  const gb=$("#gb-today"); if(gb) gb.textContent="Puzzle #"+puzzleNumber(ds)+" · today";
  if(G.date&&G.date!==ds&&!$("#game-view").classList.contains("hidden")) resetGameForToday();
}
function S(id,cat,icon,name,blurb,q){ TOOLS.push({id:id,cat:cat,icon:icon,name:name,blurb:blurb,q:q||name.toLowerCase()}); }
function D(id,o){
  CALCS[id]={intro:o.intro,formula:o.formula,
   example:o.example||"The boxes are pre-filled with a worked example — change any number and the answer updates instantly, with the full breakdown shown next to it.",
   fields:o.fields,compute:o.compute,
   faqs:o.faqs||[["How is this calculated?","With the standard formula shown above — the same one used in textbooks and professional tools. Every input is labelled, so you can check the working yourself."],
    ["How exact is the result?","Exact for the numbers you enter. Real-world results can differ where fees, rounding, changing rates or measurement error apply — each tool states its main assumptions."]],
   related:o.related||TOOLS.filter(t=>t.cat===(toolById(id)||{}).cat&&t.id!==id).slice(0,3).map(t=>t.id)};
}
function FGCD(a,b){ a=Math.abs(Math.round(a)); b=Math.abs(Math.round(b)); while(b){ const t=a%b; a=b; b=t; } return a||1; }
function PNUMS(s){ return String(s||"").split(/[\s,;]+/).filter(x=>x!=="").map(Number).filter(x=>isFinite(x)); }
function FPACE(sec){ if(!isFinite(sec)||sec<0) return "—"; sec=Math.round(sec); return Math.floor(sec/60)+":"+String(sec%60).padStart(2,"0"); }
function FTIME(sec){ if(!isFinite(sec)||sec<0) return "—"; sec=Math.round(sec); const h=Math.floor(sec/3600),m=Math.floor(sec%3600/60),s=sec%60; return (h?h+":":"")+String(m).padStart(2,"0")+":"+String(s).padStart(2,"0"); }
function FPHI(z){ const t=1/(1+0.2316419*Math.abs(z)); const poly=0.31938153+t*(-0.356563782+t*(1.781477937+t*(-1.821255978+t*1.330274429))); const p=1-0.3989422804*Math.exp(-z*z/2)*poly*t; return z>=0?p:1-p; }
function applyTheme(m){
  themeMode=m;
  try{ localStorage.setItem("nd-theme",m); }catch(e){}
  if(m==="auto") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme",m);
  document.querySelectorAll("[data-theme-mode]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.themeMode===m)));
  const note=$("#theme-note");
  if(note) note.textContent=m==="auto"?"Auto is on — the theme follows your device setting.":(m==="dark"?"Dark mode is on — tap Auto to follow your device again.":"Light mode is on — tap Auto to follow your device again.");
}
function openSettings(){
  $("#home-view").classList.add("hidden"); $("#tool-view").classList.add("hidden"); $("#game-view").classList.add("hidden"); $("#cat-view").classList.add("hidden"); $("#chat-view").classList.add("hidden"); $("#settings-view").classList.remove("hidden");
  window.scrollTo({top:0,behavior:"instant"});
}
function fact(k){ let f=1; for(let i=2;i<=k;i++) f*=i; return f; }
function perm(n,r){ let f=1; for(let i=0;i<r;i++) f*=n-i; return f; }
function comb(n,r){ r=Math.min(r,n-r); let f=1; for(let i=0;i<r;i++) f=f*(n-i)/(i+1); return f; }
function fmt(t){ t=((t%1440)+1440)%1440; return String(Math.floor(t/60)).padStart(2,"0")+":"+String(t%60).padStart(2,"0"); }
function toRoman(n){ const T=[[1000,"M"],[900,"CM"],[500,"D"],[400,"CD"],[100,"C"],[90,"XC"],[50,"L"],[40,"XL"],[10,"X"],[9,"IX"],[5,"V"],[4,"IV"],[1,"I"]]; let s=""; for(const [v2,sy] of T){ while(n>=v2){ s+=sy; n-=v2; } } return s; }
function CONVD(id,name,blurb,q,units,defFrom,defVal,noteText){
  S(id,"conversion","swap",name,blurb,q);
  const keys=Object.keys(units);
  D(id,{intro:"Enter a value, pick the unit it is in, and every other unit is worked out at once — with exact conversion factors, not rounded rules of thumb.",
   formula:"All conversions go through the base unit with exact factors: "+keys.map(k=>k+" = "+units[k].f+" base").join(" · "),
   fields:[{id:"val",label:"Value",def:defVal},{id:"from",label:"From unit",type:"select",def:defFrom,options:keys.map(k=>({v:k,t:units[k].t}))}],
   compute(v){ const base=v.val*units[v.from].f;
    const rows=keys.map(k=>[units[k].t,num(base/units[k].f,4)+" "+k]);
    return {big:num(base/units[keys[0]].f,4)+" "+keys[0],sub:num(v.val)+" "+v.from+" converted — full table below.",
     rows:rows,note:noteText}; },
   related:["unit","cooking-conv","percentage"]});
}
function pv(i){ return i===0?v.pmt*v.n:v.pmt*(1-Math.pow(1+i,-v.n))/i; }
function sig(x,k){ if(x===0) return 0; const d=Math.ceil(Math.log10(Math.abs(x))); const f=Math.pow(10,k-d); return Math.round(x*f)/f; }
function digits(a){ const out=[]; a.forEach(x=>{ String(x).split("").forEach(d=>out.push(+d)); }); return out; }
function half(x){ return Math.round(x*2)/2; }
function isP(x){ if(x<2) return false; if(x%2===0) return x===2; for(let i=3;i*i<=x;i+=2) if(x%i===0) return false; return true; }
function smallestFactor(x){ if(x%2===0) return 2; for(let i=3;i*i<=x;i+=2) if(x%i===0) return i; return x; }
function C(k){ let r=1; for(let i=1;i<=k;i++) r=r*(k+i)/i; return r/(k+1); }
function pmf(x){ let f=1; for(let i=2;i<=x;i++) f*=i; return Math.exp(-lam)*Math.pow(lam,x)/f; }
function med(arr){ const m=Math.floor(arr.length/2); return arr.length%2?arr[m]:(arr[m-1]+arr[m])/2; }
function sim(ex){ let bal=v.p, interest=0, months=0; while(bal>0&&months<2400){ const i=bal*r; interest+=i; const princ=v.pay+ex-i; if(princ<=0) return {interest:Infinity,months:Infinity}; bal-=Math.min(bal,princ); months++; } return {interest:interest,months:months}; }
function two(x){ return x<20?ONES[x]:TENS[Math.floor(x/10)]+(x%10?"-"+ONES[x%10]:""); }
function three(x){ return (x>=100?ONES[Math.floor(x/100)]+" hundred"+(x%100?" ":""):"")+(x%100?two(x%100):""); }
function B5CONV(id,cat,name,blurb,q,intro,formula,example,units,defFrom,defTo,defVal,unitWord){
  S(id,cat,"swap",name,blurb,q);
  const opts=units.map(function(u){ return {v:u[0],t:u[1]}; });
  D(id,{intro:intro,formula:formula,example:example,
   fields:[{id:"val",label:"Amount",def:defVal},{id:"from",label:"From",type:"select",def:defFrom,options:opts},{id:"to",label:"To",type:"select",def:defTo,options:opts}],
   compute(v){ const F={}; units.forEach(function(u){ F[u[0]]=u[2]; });
    const out=v.val*F[v.from]/F[v.to];
    const rows=units.filter(function(u){ return u[0]!==v.to; }).slice(0,5).map(function(u){ return ["In "+u[1].toLowerCase(),num(v.val*F[v.from]/u[2],4)+" "+u[0]]; });
    return {big:num(out,4)+" "+v.to,sub:num(v.val)+" "+v.from+" converted to "+unitWord+".",rows:rows}; }});
}
function tr(x){ return x%1===0?num(x,0):num(x,1); }
function isoWeek(dt){ const t=new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate())); const day=(t.getUTCDay()+6)%7; t.setUTCDate(t.getUTCDate()-day+3); const first=new Date(Date.UTC(t.getUTCFullYear(),0,4)); const fday=(first.getUTCDay()+6)%7; first.setUTCDate(first.getUTCDate()-fday+3); return {week:1+Math.round((t-first)/(7*86400000)),year:t.getUTCFullYear()}; }
function weeksInYear(y){ const p=(y+Math.floor(y/4)-Math.floor(y/100)+Math.floor(y/400))%7; return p===4||( (y%4===0&&(y%100!==0||y%400===0)) && p===3 )?53:52; }
function sci(x){ if(x===0) return "0"; const ex=Math.floor(Math.log10(Math.abs(x))); return num(x/Math.pow(10,ex),3)+" × 10^"+ex; }
function p2(x){ return String(x).padStart(2,"0"); }
function syll(w){ w=w.toLowerCase().replace(/[^a-z]/g,""); if(!w) return 0; if(w.length<=3) return 1;
   w=w.replace(/(?:[^laeiouy]e|ed|es)$/,""); const m=w.match(/[aeiouy]+/g); return Math.max(1,m?m.length:1); }
function evalExpr(src){
  let s=String(src||"").toLowerCase()
    .replace(/,/g,"")
    .replace(/\bwhat is\b|\bcalculate\b|\bcompute\b|\bsolve\b|\bhow much is\b|\bplease\b/g," ")
    .replace(/square root of/g,"sqrt").replace(/sqrt of/g,"sqrt")
    .replace(/multiplied by/g,"*").replace(/divided by/g,"/").replace(/\btimes\b/g,"*")
    .replace(/\bplus\b/g,"+").replace(/\bminus\b/g,"-")
    .replace(/×/g,"*").replace(/÷/g,"/").replace(/\^/g,"^")
    .replace(/\bpercent\b/g,"%").replace(/\bof\b/g,"*")
    .replace(/\?/g," ").trim();
  if(!s||!/^[0-9.+\-*/%^() sqrt]+$/.test(s)) return null;
  if(!/\d/.test(s)) return null;
  const toks=[]; let i=0;
  while(i<s.length){
    const ch=s[i];
    if(ch===" "){ i++; continue; }
    if(/[0-9.]/.test(ch)){ let j=i; while(j<s.length&&/[0-9.]/.test(s[j])) j++; const n=parseFloat(s.slice(i,j)); if(!isFinite(n)) return null; toks.push({t:"n",v:n}); i=j; continue; }
    if(s.startsWith("sqrt",i)){ toks.push({t:"sqrt"}); i+=4; continue; }
    if("+-*/%^()".includes(ch)){ toks.push({t:ch}); i++; continue; }
    return null;
  }
  let pos=0;
  function peek(){ return toks[pos]; }
  function parseExpr(){ let v=parseTerm(); while(peek()&&(peek().t==="+"||peek().t==="-")){ const op=toks[pos++].t; const r=parseTerm(); v=op==="+"?v+r:v-r; } return v; }
  function parseTerm(){ let v=parseFactor(); while(peek()&&(peek().t==="*"||peek().t==="/")){ const op=toks[pos++].t; const r=parseFactor(); if(op==="/"&&r===0) throw new Error("div0"); v=op==="*"?v*r:v/r; } return v; }
  function parseFactor(){ let v=parseUnary(); if(peek()&&peek().t==="^"){ pos++; const r=parseFactor(); v=Math.pow(v,r); } return v; }
  function parseUnary(){ if(peek()&&peek().t==="-"){ pos++; return -parseUnary(); } return parsePostfix(); }
  function parsePostfix(){ let v=parsePrimary(); if(peek()&&peek().t==="%"){ pos++; v=v/100; } return v; }
  function parsePrimary(){
    const tk=peek(); if(!tk) throw new Error("eof");
    if(tk.t==="n"){ pos++; return tk.v; }
    if(tk.t==="("){ pos++; const v=parseExpr(); if(!peek()||peek().t!==")") throw new Error("paren"); pos++; return v; }
    if(tk.t==="sqrt"){ pos++; return Math.sqrt(parseUnary()); }
    throw new Error("tok");
  }
  try{ const out=parseExpr(); if(pos!==toks.length||!isFinite(out)) return null; return out; }
  catch(e){ return null; }
}
function peek(){ return toks[pos]; }
function parseExpr(){ let v=parseTerm(); while(peek()&&(peek().t==="+"||peek().t==="-")){ const op=toks[pos++].t; const r=parseTerm(); v=op==="+"?v+r:v-r; } return v; }
function parseTerm(){ let v=parseFactor(); while(peek()&&(peek().t==="*"||peek().t==="/")){ const op=toks[pos++].t; const r=parseFactor(); if(op==="/"&&r===0) throw new Error("div0"); v=op==="*"?v*r:v/r; } return v; }
function parseFactor(){ let v=parseUnary(); if(peek()&&peek().t==="^"){ pos++; const r=parseFactor(); v=Math.pow(v,r); } return v; }
function parseUnary(){ if(peek()&&peek().t==="-"){ pos++; return -parseUnary(); } return parsePostfix(); }
function parsePostfix(){ let v=parsePrimary(); if(peek()&&peek().t==="%"){ pos++; v=v/100; } return v; }
function parsePrimary(){
    const tk=peek(); if(!tk) throw new Error("eof");
    if(tk.t==="n"){ pos++; return tk.v; }
    if(tk.t==="("){ pos++; const v=parseExpr(); if(!peek()||peek().t!==")") throw new Error("paren"); pos++; return v; }
    if(tk.t==="sqrt"){ pos++; return Math.sqrt(parseUnary()); }
    throw new Error("tok");
  }
function matchTools(q){
  const words=String(q||"").toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(Boolean);
  const expanded=new Set(words);
  words.forEach(w=>{ if(SYNONYMS[w]) SYNONYMS[w].split(" ").forEach(x=>expanded.add(x)); });
  const scored=TOOLS.map(t=>{
    const name=t.name.toLowerCase(), hay=(t.name+" "+t.blurb+" "+t.q).toLowerCase();
    let s=0;
    expanded.forEach(w=>{ if(w.length<3) return; if(name.includes(w)) s+=3; else if(hay.includes(w)) s+=1; });
    if(t.name.toLowerCase().includes(String(q).toLowerCase().trim())&&String(q).trim().length>3) s+=6;
    return {t:t,s:s};
  }).filter(x=>x.s>0).sort((a,b)=>b.s-a.s);
  return scored.slice(0,3).map(x=>x.t);
}
function levDist(a,b){
  if(Math.abs(a.length-b.length)>2) return 99;
  const dp=[]; for(let i=0;i<=a.length;i++) dp.push([i]); for(let j=1;j<=b.length;j++) dp[0][j]=j;
  for(let i=1;i<=a.length;i++) for(let j=1;j<=b.length;j++) dp[i][j]=Math.min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+(a[i-1]===b[j-1]?0:1));
  return dp[a.length][b.length];
}
function fuzzyTools(q){
  const words=String(q||"").toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(w=>w.length>=4);
  if(!words.length) return [];
  const scored=TOOLS.map(t=>{
    const nameWords=t.name.toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/);
    let best=99;
    words.forEach(w=>{ nameWords.forEach(nw=>{ if(nw.length>=4){ const d=levDist(w,nw); if(d<best) best=d; } }); });
    return {t:t,d:best};
  }).filter(x=>x.d<=2).sort((a,b)=>a.d-b.d);
  return scored.slice(0,3).map(x=>x.t);
}
function fp(sec){ sec=Math.round(sec); return Math.floor(sec/60)+":"+String(sec%60).padStart(2,"0"); }
function ft(sec){ sec=Math.round(sec); const h=Math.floor(sec/3600),m=Math.floor(sec%3600/60),s=sec%60; return (h?h+":":"")+String(m).padStart(2,"0")+":"+String(s).padStart(2,"0"); }
function startFlow(id){ aFlow={def:FLOWS[id],step:0,data:{}}; aFlowData=aFlow.data; }
function parseDateStr(s){
  let m=/(\d{4})-(\d{2})-(\d{2})/.exec(s);
  if(m) return Date.UTC(+m[1],+m[2]-1,+m[3]);
  m=/(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*,?\s*(\d{4})?/.exec(s);
  if(m){ const now=new Date(); let y=m[3]?+m[3]:now.getUTCFullYear(); let t=Date.UTC(y,MONTHS[m[2]],+m[1]); if(!m[3]&&t<Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate())) t=Date.UTC(y+1,MONTHS[m[2]],+m[1]); return t; }
  m=/(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})?/.exec(s);
  if(m){ const now=new Date(); let y=m[3]?+m[3]:now.getUTCFullYear(); let t=Date.UTC(y,MONTHS[m[1]],+m[2]); if(!m[3]&&t<Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate())) t=Date.UTC(y+1,MONTHS[m[1]],+m[2]); return t; }
  return null;
}
function fmtDate(t){
  const d=new Date(t), days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], mo=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return d.getUTCDate()+" "+mo[d.getUTCMonth()]+" "+d.getUTCFullYear()+" ("+days[d.getUTCDay()]+")";
}
function todayUTC(){ const n=new Date(); return Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate()); }
function normUnits(s){
  const keys=Object.keys(UALIAS).sort((a,b)=>b.length-a.length);
  keys.forEach(k=>{ s=s.replace(new RegExp("\\b"+k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"\\b","g"),UALIAS[k]); });
  return s;
}
function fmtN(v,dp){ const p=Math.pow(10,dp===undefined?4:dp); const r=Math.round(v*p)/p; return r.toLocaleString("en-US",{minimumFractionDigits:0,maximumFractionDigits:dp===undefined?4:dp}); }
function sing(name,v){ return v===1&&/s$/.test(name)?name.replace(/s$/,""):name; }
function tryConvert(rawQ){
  const s=normUnits(" "+String(rawQ||"").toLowerCase().replace(/,/g,"")+" ");
  const dn={c:"°C",f:"°F",k:"K"};
  const tm=/(-?\d+\.?\d*)\s*°?\s*(c|f|k)\b[^a-z0-9]+(?:to|in)\s*°?\s*(c|f|k)\b/.exec(s);
  if(tm){ const v=parseFloat(tm[1]), from=tm[2], to=tm[3];
    const c=from==="c"?v:from==="f"?(v-32)*5/9:v-273.15;
    const out=to==="c"?c:to==="f"?c*9/5+32:c+273.15;
    return {text:fmtN(v,2)+" "+dn[from]+" = "+fmtN(out,2)+" "+dn[to]+".",buttons:[{label:"Open the Unit Converter",act:"tool",id:"unit"}]}; }
  const m=/(\d[\d]*\.?\d*)\s*([a-z/]+)\s+(?:to|in|=)\s+([a-z/]+)\b/.exec(s);
  if(m){ const v=parseFloat(m[1]), a=m[2], b=m[3];
    for(let di=0;di<UDIMS.length;di++){ const d=UDIMS[di];
      if(d.u[a]!==undefined&&d.u[b]!==undefined){ const out=v*d.u[a]/d.u[b];
        return {text:fmtN(v)+" "+sing(d.names[a]||a,v)+" = "+fmtN(out)+" "+(d.names[b]||b)+".",buttons:[{label:"Open the Unit Converter",act:"tool",id:"unit"}]}; } } }
  const hm=/how many\s+([a-z/]+)\s+(?:are\s+)?in\s+(?:an?\s+)?(\d[\d]*\.?\d*)?\s*([a-z/]+)\b/.exec(s);
  if(hm){ const b=hm[1], a=hm[3], v=hm[2]?parseFloat(hm[2]):1;
    for(let di=0;di<UDIMS.length;di++){ const d=UDIMS[di];
      if(d.u[a]!==undefined&&d.u[b]!==undefined){ const out=v*d.u[a]/d.u[b];
        return {text:"There are "+fmtN(out)+" "+(d.names[b]||b)+" in "+fmtN(v)+" "+sing(d.names[a]||a,v)+".",buttons:[{label:"Open the Unit Converter",act:"tool",id:"unit"}]}; } } }
  return null;
}
function assistAnswer(raw){
  const q=String(raw||"").trim(), ql=q.toLowerCase();
  if(aFlow){
    if(/^(cancel|stop|quit|never mind|nevermind)$/.test(ql)){ aFlow=null; return {text:"No problem — flow cancelled. Ask me for any tool, or give me a sum to solve.",suggest:["Calculate my mortgage","What is 15% of 240?","Show me the finance tools"]}; }
    const m=/(-?\d[\d,]*\.?\d*)/.exec(q.replace(/,/g,""));
    if(!m) return {text:"I need a number for that one — "+aFlow.def.steps[aFlow.step].ask};
    const val=parseFloat(m[1]);
    aFlow.data[aFlow.def.steps[aFlow.step].k]=val;
    aFlow.step++;
    if(aFlow.step<aFlow.def.steps.length) return {text:aFlow.def.steps[aFlow.step].ask};
    const def=aFlow.def, data=aFlow.data; aFlow=null;
    const ans=def.done(data); lastToolId=def.tool;
    ans.suggest=["Open the "+def.label,"Calculate my mortgage","What else can you do?"];
    return ans;
  }
  return assistRoute(q,ql);
}
function popButtons(){ return POPULAR.map(p=>({label:p[1],act:"tool",id:p[0]})); }
function openChat(){
  ["#home-view","#tool-view","#game-view","#cat-view","#settings-view"].forEach(s=>{ const el=$(s); if(el) el.classList.add("hidden"); });
  const cv=$("#chat-view"); if(cv){
    /* the chat must live directly under <body>: inside the padded page
       column some phone webviews clip fixed panels and push the input bar
       off-screen — as a body child nothing can contain or offset it */
    if(cv.parentNode!==document.body){ document.body.appendChild(cv); }
    document.body.classList.add("in-chat");
    cv.classList.remove("hidden");
    /* belt-and-braces: pin the chat over the full screen with inline styles too,
       so no stale or partial stylesheet can ever leave it as a floating card
       with the page showing behind it or the Send button pushed off-screen */
    cv.style.cssText="position:fixed;top:0;right:0;bottom:0;left:0;width:100%;height:100dvh;z-index:120;display:flex;flex-direction:column;overflow:hidden;background:var(--bg);padding-top:env(safe-area-inset-top)";
    /* JS pixel-height pin: some phone webviews drop dvh or mis-measure the
       viewport, which is what left the input bar and Send button floating
       mid-screen or cut off. Setting an explicit pixel height from
       window.innerHeight always applies, and it tracks keyboard resizes. */
    var pinH=function(){ if(!cv.classList.contains("hidden")){ cv.style.height=window.innerHeight+"px"; } };
    pinH();
    if(!cv._pinBound){ cv._pinBound=true;
      window.addEventListener("resize",pinH);
      if(window.visualViewport) window.visualViewport.addEventListener("resize",pinH);
    }
  }
  window.scrollTo({top:0,behavior:"instant"});
  const inp=$("#assist-input"); if(inp&&window.innerWidth>760){ try{ inp.focus(); }catch(e){} }
}
function renderSuggest(list){
    if(!sugg) return; sugg.innerHTML="";
    (list&&list.length?list:DEFAULT_SUGGEST).forEach(s=>{
      const b=document.createElement("button"); b.type="button"; b.textContent=s;
      b.addEventListener("click",()=>{ input.value=s; submitText(); });
      sugg.appendChild(b);
    });
  }
function scrollChat(){ requestAnimationFrame(()=>{ msgs.scrollTop=msgs.scrollHeight; }); }
function addMsg(text,who,buttons){
    const d=document.createElement("div"); d.className="msg "+who; d.textContent=text;
    if(buttons&&buttons.length){
      const row=document.createElement("div"); row.className="mrow";
      buttons.forEach(b=>{
        const el=document.createElement("button"); el.type="button"; el.className="mbtn"; el.textContent=b.label;
        el.addEventListener("click",()=>{
          if(b.act==="tool"){ openTool(b.id); }
          else if(b.act==="game"){ openGame(); }
          else if(b.act==="settings"){ openSettings(); }
          else if(b.act==="home"){ goHome(); }
          else if(b.act==="sponsor"){ goHome(); setTimeout(()=>{ const s=$("#sponsor"); if(s) s.scrollIntoView({behavior:"smooth"}); },60); }
          else if(b.act==="email"){ const a=document.createElement("a"); a.href="mailto:malikarslan032154@gmail.com?subject=Sponsorship%20enquiry%20%E2%80%94%20FreeCalcNow"; document.body.appendChild(a); a.click(); a.remove(); }
        });
        row.appendChild(el);
      });
      d.appendChild(row);
    }
    if(who==="bot"){
      const w=document.createElement("div"); w.className="msg-wrap";
      const a=document.createElement("span"); a.className="chat-ava-msg"; a.innerHTML=AVA;
      w.appendChild(a); w.appendChild(d); msgs.appendChild(w);
    } else msgs.appendChild(d);
    scrollChat();
  }
function showTyping(){
    const w=document.createElement("div"); w.className="msg-wrap";
    const a=document.createElement("span"); a.className="chat-ava-msg"; a.innerHTML=AVA;
    const d=document.createElement("div"); d.className="msg bot typing"; d.innerHTML="<i></i><i></i><i></i>";
    w.appendChild(a); w.appendChild(d); msgs.appendChild(w); scrollChat();
    return w;
  }
function submitText(){
    const text=input.value.trim(); if(!text) return;
    addMsg(text,"user"); input.value="";
    let ans;
    try{ ans=assistAnswer(text); }catch(e){ ans={text:"Something glitched on that one — but I am still here. Try again, or name a tool and I will open it for you.",buttons:popButtons()}; }
    const fb=(ans.buttons||[]).filter(b=>b.act==="tool")[0];
    if(fb) lastToolId=fb.id; else if(ans.tool) lastToolId=ans.tool;
    const buttons=ans.buttons?ans.buttons.slice():[];
    if(ans.tool) buttons.push({label:"Open the full "+(toolById(ans.tool)?toolById(ans.tool).name.replace(" Calculator",""):"")+" tool",act:"tool",id:ans.tool});
    const typing=showTyping();
    const delay=Math.max(320,Math.min(320+String(ans.text||"").length*2,1250));
    setTimeout(()=>{
      typing.remove();
      addMsg(ans.text,"bot",buttons.length?buttons:null);
      renderSuggest(ans.suggest);
      if(ans.autoOpen){ const id=ans.autoOpen; setTimeout(()=>openTool(id),450); }
      if(window.innerWidth>760){ try{ input.focus(); }catch(e){} }
    },delay);
  }
function npv(r){ let s=-v.init; cf.forEach(function(x,t){ s+=x/Math.pow(1+r,t+1); }); return s; }
function npvI(r){ let s=-v.cost; cf.forEach(function(c,i){ s+=c/Math.pow(1+r,i+1); }); return s; }
function f(mins){ return mins>=1440?num(mins/1440,2)+" days":mins>=60?num(mins/60,2)+" hours":mins>=1?num(mins,1)+" minutes":num(mins*60,0)+" seconds"; }
function hm(m){ return m>=90?num(Math.floor(m/60),0)+" h "+num(Math.round(m%60),0)+" min":num(m,0)+" min"; }
function loadable(w){ if(w<=v.bar) return v.bar; return Math.round((w-v.bar)/inc)*inc+v.bar; }
function map(str,M,rev){ const arr=String(str).toLowerCase().split("").map(function(ch){ return M[ch]!==undefined?M[ch]:ch; }); return rev?arr.reverse().join(""):arr.join(""); }
function fromJD(J){ const a=J+32044, b=Math.floor((4*a+3)/146097), c=a-Math.floor(146097*b/4), d=Math.floor((4*c+3)/1461), e=c-Math.floor(1461*d/4), m=Math.floor((5*e+2)/153);
   const day=e-Math.floor((153*m+2)/5)+1, month=m+3-12*Math.floor(m/10), year=100*b+d-4800+Math.floor(m/10);
   return {y:year,m:month,d:day}; }
function loanLoop(P,annualRate,months,pay){ const r=annualRate/100/12; let bal=P,totInt=0,m=0; if(pay<=bal*r&&r>0) return {months:Infinity,interest:Infinity}; while(bal>0.005&&m<3600){ const i=bal*r; totInt+=i; bal=bal+i-Math.min(pay,bal+i); m++; } return {months:m,interest:totInt}; }
function fmtD(t){ const d=new Date(t); return d.getUTCDate()+" "+["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.getUTCMonth()]+" "+d.getUTCFullYear(); }
function parseD(s){ const p=String(s||"").split("-").map(Number); if(p.length!==3||!p[0]) return null; return Date.UTC(p[0],p[1]-1,p[2]); }
function todayUTC7(){ const n=new Date(); return Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate()); }
function med7(a){ const s=a.slice().sort((x,y)=>x-y), n=s.length; return n%2?s[(n-1)/2]:(s[n/2-1]+s[n/2])/2; }
function q7(a){ const s=a.slice().sort((x,y)=>x-y), n=s.length, mid=Math.floor(n/2); const lo=s.slice(0,mid), hi=n%2?s.slice(mid+1):s.slice(mid); return {q1:med7(lo),med:med7(s),q3:med7(hi)}; }
function offsetMs(tz,utc){ const parts=new Intl.DateTimeFormat("en-US",{timeZone:tz,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).formatToParts(new Date(utc));
   const o={}; parts.forEach(p=>{ o[p.type]=p.value; }); const asUTC=Date.UTC(+o.year,+o.month-1,+o.day,(+o.hour)%24,+o.minute,+o.second); return asUTC-Math.floor(utc/1000)*1000; }
function dec(s){ s=s.replace(/-/g,"+").replace(/_/g,"/"); while(s.length%4) s+="="; return JSON.parse(decodeURIComponent(escape(atob(s)))); }
function buildAZ(){
    if(azBuilt||!az||typeof TOOLS==="undefined") return; azBuilt=true;
    const sorted=TOOLS.slice().sort((a,b)=>a.name.localeCompare(b.name));
    az.innerHTML=sorted.map(function(t){ return '<button type="button" class="az-link" data-az="'+t.id+'">'+esc(t.name.replace(/ Calculator$/,""))+'</button>'; }).join("");
    az.querySelectorAll("[data-az]").forEach(function(b){ b.addEventListener("click",function(){ openTool(b.dataset.az); }); });
  }
function prof(p){ const i2=v.type==="call"?Math.max(0,p-v.strike):Math.max(0,v.strike-p); return money((i2-v.premium)*100*v.contracts,0); }
function betacf(a,b,x){ const FPMIN=1e-300; let c=1,d=1-(a+b)*x/(a+1); if(Math.abs(d)<FPMIN)d=FPMIN; d=1/d; let h=d;
   for(let m=1;m<=200;m++){ const m2=2*m; let aa=m*(b-m)*x/((a-1+m2)*(a+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN)d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN)c=FPMIN; d=1/d; h*=d*c;
    aa=-(a+m)*(a+b+m)*x/((a+m2)*(a+1+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN)d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN)c=FPMIN; d=1/d; const del=d*c; h*=del; if(Math.abs(del-1)<3e-12) break; } return h; }
function ibeta(x,a,b){ if(x<=0) return 0; if(x>=1) return 1; const bt=Math.exp(lgam(a+b)-lgam(a)-lgam(b)+a*Math.log(x)+b*Math.log(1-x));
   return x<(a+1)/(a+b+2)?bt*betacf(a,b,x)/a:1-bt*betacf(b,a,1-x)/b; }
function at(w){ const m=words/w; return num(Math.floor(m),0)+" min "+num(Math.round((m%1)*60),0)+" s"; }
function verdict(x){ return x<limit?"within the usual limit for "+(v.sex==="female"?"women":"men")+" (under "+limit+" ms)":x<=500?"above the usual limit — prolonged":"markedly prolonged (over 500 ms at any sex)"; }
function bags(yield_){ return Math.ceil(total/yield_); }
function out(text,label){ return {big:label,sub:"converted — copy it below.",extra:'<div class="pwd-out" style="white-space:pre-wrap;text-align:left;word-break:break-all">'+esc(text)+'</div>',rows:[["Output size",num(text.length,0)+" characters"]]}; }
function pig(w){ const lw=w.toLowerCase(); if(/^[aeiou]/.test(lw)) return lw+"way";
   const m=/^([^aeiou]*qu|[^aeiou]+)(.*)$/.exec(lw); if(!m) return lw+"ay"; return m[2]+m[1]+"ay"; }
function eigvec(lam){ if(Math.abs(v.b)>1e-12) return "("+num(v.b,3)+", "+num(lam-v.a,3)+")"; if(Math.abs(v.c)>1e-12) return "("+num(lam-v.d,3)+", "+num(v.c,3)+")"; return lam===v.a?"(1, 0)":"(0, 1)"; }
function pstr(cs){ const dg=cs.length-1; if(!cs.length) return "0";
   return cs.map((coef,i)=>{ const pw=dg-i; if(coef===0&&cs.length>1) return ""; const term=pw===0?num(Math.abs(coef),4):pw===1?num(Math.abs(coef),4)+"x":num(Math.abs(coef),4)+"x^"+pw; return (i===0?(coef<0?"−":""):(coef<0?" − ":" + "))+term; }).join("").trim()||"0"; }
function human(s){ if(s<1) return "instantly"; if(s<60) return num(s,1)+" seconds"; if(s<3600) return num(s/60,1)+" minutes"; if(s<86400) return num(s/3600,1)+" hours"; if(s<31557600) return num(s/86400,1)+" days"; const y=s/31557600; if(y<1000) return num(y,1)+" years"; if(y<1e6) return num(y/1000,2)+" thousand years"; if(y<1e9) return num(y/1e6,2)+" million years"; if(y<1.4e10) return num(y/1e9,2)+" billion years"; return "longer than the age of the universe"; }
function LGAMMA(x){ const c=[0.99999999999980993,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-0.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7]; if(x<0.5) return Math.log(Math.PI/Math.sin(Math.PI*x))-LGAMMA(1-x); x-=1; let a=c[0]; const t=x+7.5; for(let i=1;i<c.length;i++) a+=c[i]/(x+i); return 0.5*Math.log(2*Math.PI)+(x+0.5)*Math.log(t)-t+Math.log(a); }
function BETACF(a,b,x){ const MAXIT=200,EPS=3e-12,FPMIN=1e-300; const qab=a+b,qap=a+1,qam=a-1; let c=1,d=1-qab*x/qap; if(Math.abs(d)<FPMIN)d=FPMIN; d=1/d; let h=d; for(let m=1;m<=MAXIT;m++){ const m2=2*m; let aa=m*(b-m)*x/((qam+m2)*(a+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN)d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN)c=FPMIN; d=1/d; h*=d*c; aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2)); d=1+aa*d; if(Math.abs(d)<FPMIN)d=FPMIN; c=1+aa/c; if(Math.abs(c)<FPMIN)c=FPMIN; d=1/d; const del=d*c; h*=del; if(Math.abs(del-1)<EPS) break; } return h; }
function IBETA(x,a,b){ if(x<=0)return 0; if(x>=1)return 1; const bt=Math.exp(LGAMMA(a+b)-LGAMMA(a)-LGAMMA(b)+a*Math.log(x)+b*Math.log(1-x)); if(x<(a+1)/(a+b+2)) return bt*BETACF(a,b,x)/a; return 1-bt*BETACF(b,a,1-x)/b; }
function FCDF(f,df1,df2){ if(f<=0)return 0; const x=(df1*f)/(df1*f+df2); return IBETA(x,df1/2,df2/2); }
function PD(s){ const p=String(s||"").split("-"); return Date.UTC(+p[0],(+p[1]||1)-1,+p[2]||1); }
function FD(t){ const d=new Date(t),mo=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],dy=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]; return d.getUTCDate()+" "+mo[d.getUTCMonth()]+" "+d.getUTCFullYear()+" ("+dy[d.getUTCDay()]+")"; }
function DAYMS(n){ return n*86400000; }
function nCr(nn,rr){ rr=Math.min(rr,nn-rr); if(rr<0)return 0; let out=1; for(let i=0;i<rr;i++) out=out*(nn-i)/(i+1); return out; }
function fmtR(x){ if(x>=1e6) return num(x/1e6,3)+" MΩ"; if(x>=1000) return num(x/1000,3)+" kΩ"; return num(x,2)+" Ω"; }
function s2b(sg){ return (((182.4601*sg-775.6821)*sg+1262.7794)*sg-669.5622); }
function be(startAge,bStart,laterAge,bLater){ const given=bStart*(laterAge-startAge)*12, extra=bLater-bStart; if(extra<=0) return null; return laterAge+given/extra/12; }
function priceAt(y){ let p=0; for(let t=1;t<=n;t++) p+=(cpn+(t===n?v.callprice:0))/Math.pow(1+y,t); return p; }
function B12Z(p){ if(p<=0||p>=1) return NaN; const a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00], b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,6.680131188771972e+01,-1.328068155288572e+01], c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,-2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00], d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00]; const pl=0.02425; let q,x;
 if(p<pl){ q=Math.sqrt(-2*Math.log(p)); x=(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1); }
 else if(p<=1-pl){ q=p-0.5; const r=q*q; x=(((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1); }
 else { q=Math.sqrt(-2*Math.log(1-p)); x=-(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1); } return x; }
function B12TP(t,df){ const x=df/(df+t*t); return IBETA(x,df/2,0.5); }
function crit(p){ let lo=0, hi=100; for(let k=0;k<80;k++){ const mid=(lo+hi)/2; if(B12TP(mid,v.df)>1-p) lo=mid; else hi=mid; } return (lo+hi)/2; }
function ranks(a){ const idx=a.map((val,i)=>[val,i]).sort((p,q)=>p[0]-q[0]); const r=new Array(a.length); let i=0;
   while(i<idx.length){ let j=i; while(j+1<idx.length&&idx[j+1][0]===idx[i][0]) j++; const avg=(i+j)/2+1; for(let k=i;k<=j;k++) r[idx[k][1]]=avg; i=j+1; } return r; }
function smn(s,H,f){ return s*(H-f)/(H+s-2*f); }
function shutterFor(N){ const t=N*N/Math.pow(2,ev100); return t>=1?num(t,1)+" s":"1/"+num(1/t,0)+" s"; }
function d(h){ return Math.sqrt(2*R*h+h*h)/1000; }
function red(n){ while(n>9&&n!==11&&n!==22&&n!==33){ n=String(n).split("").reduce((a,c)=>a+(+c),0); } return n; }
function parseGroup(end){ const counts={}; 
   while(i<s.length&&s[i]!==end){ const ch=s[i];
    if(ch==="("||ch==="["){ i++; const inner=parseGroup(ch==="("?")":"]"); i++; let num=""; while(i<s.length&&/\d/.test(s[i])) num+=s[i++]; const mult=num?+num:1; if(!inner) return null; for(const k in inner) counts[k]=(counts[k]||0)+inner[k]*mult; }
    else if(/[A-Z]/.test(ch)){ let el=ch; i++; if(i<s.length&&/[a-z]/.test(s[i])) el+=s[i++]; if(!(el in AW)) return {err:el}; let num=""; while(i<s.length&&/\d/.test(s[i])) num+=s[i++]; counts[el]=(counts[el]||0)+(num?+num:1); }
    else if(ch===")"||ch==="]"){ break; }
    else { i++; } }
   return counts; }
function supN(n){ return String(n).split("").map(c=>sup[c]).join(""); }
function build(z){ const parts=[]; let left=z; for(const o of order){ if(left<=0) break; const take=Math.min(o[1],left); parts.push([o[0],take]); left-=take; } return parts; }
function fieldSet(str,min,max){ const set=new Set();
   str.split(",").forEach(tok=>{ let step=1; const sp=tok.split("/"); if(sp.length===2){ step=parseInt(sp[1],10); if(!step||step<1) throw 0; }
    const base=sp[0]; let lo,hi;
    if(base==="*"){ lo=min; hi=max; } else if(base.indexOf("-")>0){ const ab=base.split("-"); lo=+ab[0]; hi=+ab[1]; }
    else if(base.indexOf("-")===0){ throw 0; } else { lo=+base; hi=+base; }
    if(isNaN(lo)||isNaN(hi)||lo<min||hi>max||lo>hi) throw 0;
    for(let x=lo;x<=hi;x+=step) set.add(x); });
   return set; }
function describe(str,i){ if(str==="*") return "every "+names[i]; if(str.indexOf("*/")===0) return "every "+str.slice(2)+" "+names[i]+"s";
   if(str.indexOf("-")>0&&str.indexOf(",")<0) return names[i]+"s "+str.replace("-", " to "); if(str.indexOf(",")>0) return names[i]+"s "+str.replace(/,/g,", "); return names[i]+" "+str; }
function fromRoman(s){ const V={I:1,V:5,X:10,L:50,C:100,D:500,M:1000}; let tot=0; for(let i=0;i<s.length;i++){ const cur=V[s[i]], nxt=V[s[i+1]]||0; tot+=cur<nxt?-cur:cur; } return tot; }
function cupUp(cups,cup,d){ const i=cups.indexOf(cup); const j=Math.max(0,Math.min(cups.length-1,i+d)); return cups[j]; }
function interp(x,xi,yi){ if(x>=A[0][xi]) return A[0][yi]; for(let i=0;i<A.length-1;i++){ const a=A[i], b=A[i+1]; if(x<=a[xi]&&x>=b[xi]){ const t=(x-b[xi])/((a[xi]-b[xi])||1); return b[yi]+t*(a[yi]-b[yi]); } } return A[A.length-1][yi]; }
function combN(n,k){ if(k<0||k>n) return 0; k=Math.min(k,n-k); let r=1; for(let i=0;i<k;i++) r=r*(n-i)/(i+1); return r; }
function erf(x){ const s=x<0?-1:1; x=Math.abs(x); const t=1/(1+0.3275911*x); const y=1-((((1.061405429*t-1.453152027)*t+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-x*x); return s*y; }
function ncdf(z){ return 0.5*(1+erf(z/Math.SQRT2)); }
function mmss(mins){ const t=Math.round(mins*60), m=Math.floor(t/60), s=t%60; return m+":"+(s<10?"0":"")+s; }
function row(name,base){ return [name,num(base,0)+" ms · dotted "+num(base*1.5,0)+" · triplet "+num(base*2/3,0)]; }
function catName(id){ var c=(typeof CATS!=="undefined")?CATS.find(function(x){return x.id===id;}):null; return c?c.name:id; }
function locText(t){ return "The "+t.name+" is in the "+catName(t.cat)+" category. On this site the button below IS its link — tap it and the tool opens here, no new page to hunt for:"; }
function tbtn(id){ var t=(typeof toolById==="function")?toolById(id):null; return t?{label:t.name.replace(" Calculator",""),act:"tool",id:id}:null; }
function btns(ids){ return ids.map(tbtn).filter(Boolean); }
function numList(q){ var m=String(q).match(/[\d,]+(?:\.\d+)?/g); return m?m.map(function(x){ return parseFloat(x.replace(/,/g,"")); }).filter(function(x){ return isFinite(x); }):[]; }
function powerAt(s){ return 0.5*rho*cda*Math.pow(s,3)+crr*m*g*s+m*g*gr*s; }
function hAt(t){ t=Math.max(0,Math.min(6,t)); const w=Math.min(5,Math.floor(t)), f=t-w, tw=cum[w]+(cum[w+1]-cum[w])*f; return v.dir==="rising"?v.low+range*tw/12:v.high-range*tw/12; }
function nums(q){ var m=String(q).match(/[\d,]+(?:\.\d+)?/g); return m?m.map(function(x){ return parseFloat(x.replace(/,/g,"")); }).filter(function(x){ return isFinite(x); }):[]; }
function syl(w){ w=w.toLowerCase().replace(/[^a-z]/g,""); if(!w) return 0; if(w.length<=3) return 1; w=w.replace(/(?:[^laeiouy]e|ed|es)$/,"").replace(/^y/,""); const m=w.match(/[aeiouy]{1,2}/g); return Math.max(1,m?m.length:1); }
function cd13(t){ let s=0; for(let i=0;i<12;i++) s+=(+t[i])*(i%2?3:1); return String((10-s%10)%10); }
function cd10(t){ let s=0; for(let i=0;i<9;i++) s+=(+t[i])*(10-i); const c=(11-s%11)%11; return c===10?"X":String(c); }
function bestTool(ql){
    var STOP={the:1,a:1,an:1,is:1,are:1,do:1,does:1,i:1,me:1,my:1,to:1,of:1,for:1,in:1,on:1,how:1,what:1,where:1,which:1,can:1,you:1,calculator:1,tool:1,please:1,find:1,show:1,open:1,use:1,used:1,step:1,steps:1,by:1,guide:1,walk:1,through:1};
    var ws=ql.replace(/[^a-z0-9\s]/g," ").split(/\s+/).filter(function(w){ return w.length>2&&!STOP[w]; });
    if(!ws.length||typeof TOOLS==="undefined") return null;
    var scored=TOOLS.map(function(tt){ var nm=(tt.name||"").toLowerCase(), hay=(tt.name+" "+(tt.blurb||"")+" "+(tt.q||"")).toLowerCase(), sc=0; ws.forEach(function(w){ if(nm.indexOf(w)>=0) sc+=2; else if(hay.indexOf(w)>=0) sc++; }); return {t:tt,sc:sc}; }).filter(function(x){ return x.sc>=3; }).sort(function(a,b){ return b.sc-a.sc; });
    return scored.length?scored[0].t:null;
  }
function price(r){ let s=0; for(let t=1;t<=n;t++) s+=c/Math.pow(1+r,t); return s+v.face/Math.pow(1+r,n); }
function add(d,n){ const x=new Date(d); x.setDate(x.getDate()+n); return x; }
function fs(b){ return b>=1e9?num(b/1e9,2)+" GB":b>=1e6?num(b/1e6,2)+" MB":num(b/1e3,1)+" KB"; }
function pace(minPer){ const m=Math.floor(minPer), s=Math.round((minPer-m)*60); return m+":"+String(s).padStart(2,"0"); }
function buildPairs(fam,pairs){
    pairs.forEach(function(p,idx){
      var a=p.a, b=p.b;
      var factor=a.f/b.f;
      var rel=[pairs.filter(function(m){ return m.a===b&&m.b===a; })[0].id];
      var n1=pairs[(idx+1)%pairs.length], n2=pairs[(idx+7)%pairs.length];
      if(n1&&rel.indexOf(n1.id)<0) rel.push(n1.id);
      if(n2&&rel.indexOf(n2.id)<0) rel.push(n2.id);
      S(p.id,"conversion","swap",a.n+" to "+b.n+" Converter","Convert "+a.n.toLowerCase()+" to "+b.n.toLowerCase()+" instantly — the exact rate, shown both ways.","convert "+a.n.toLowerCase()+" to "+b.n.toLowerCase()+" · "+a.s+" to "+b.s+" · "+a.n.toLowerCase()+" in "+b.n.toLowerCase()+" · "+fam.key+" converter");
      ND32_PAIRS.push(p.id);
      D(p.id,{
       intro:"Convert "+a.n.toLowerCase()+" to "+b.n.toLowerCase()+" with the exact definition: 1 "+a.n.toLowerCase()+" = "+fmtF(factor)+" "+b.n.toLowerCase()+". Type any amount — the answer updates as you type, and the reverse rate is in the table so you can check the working both ways.",
       formula:"Result = amount in "+a.n.toLowerCase()+" × "+fmtF(factor)+"  ·  1 "+a.s+" = "+fmtF(factor)+" "+b.s+"  ·  1 "+b.s+" = "+fmtF(1/factor)+" "+a.s,
       fields:[{id:"val",label:"Amount in "+a.n.toLowerCase(),hint:a.s,def:fam.def}],
       compute:function(v){
         var out=v.val*factor;
         var rows=[];
         rows.push(["1 "+a.n+" ("+a.s+")",fmtV(factor)+" "+b.s]);
         rows.push(["1 "+b.n+" ("+b.s+")",fmtV(1/factor)+" "+a.s]);
         rows.push([num(fam.def,0)+" "+a.n,fmtV(fam.def*factor)+" "+b.s]);
         rows.push(["100 "+a.n,fmtV(100*factor)+" "+b.s]);
         return {big:fmtV(out)+" "+b.s,sub:num(v.val,4)+" "+a.n.toLowerCase()+" = "+fmtV(out)+" "+b.n.toLowerCase()+".",rows:rows,note:fam.note};
       },
       related:rel});
    });
  }
function allPairs(fam){
    var us=fam.units, made=[];
    us.forEach(function(a){ us.forEach(function(b){ if(a!==b) made.push({a:a,b:b,id:"conv-"+fam.key+"-"+slug(a.n)+"-to-"+slug(b.n)}); }); });
    return made;
  }
function extPairs(fam){
    var made=[];
    fam.units.forEach(function(a){ fam.units.forEach(function(b){
      if(a===b) return;
      var aNew=fam.fresh.indexOf(a)>=0, bNew=fam.fresh.indexOf(b)>=0;
      if(!aNew&&!bNew) return;
      made.push({a:a,b:b,id:"conv-"+fam.key+"-"+slug(a.n)+"-to-"+slug(b.n)});
    }); });
    return made;
  }
function s(x){ return [x>>>24,(x>>>16)&255,(x>>>8)&255,x&255].join("."); }
function t(p){ return Math.round(v.rest+p/100*res); }
function convCount(){ return TOOLS.filter(function(t){return t.cat==="conversion";}).length; }
function fmtE(x){ if(x!==0&&Math.abs(x)<1e-3) return x.toExponential(3); return num(x,4); }
function lsGet(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
function lsSet(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
function lsDel(k){ try{ localStorage.removeItem(k); }catch(e){} }
function lsJSON(k){ try{ var v=JSON.parse(lsGet(k)||"null"); return Array.isArray(v)?v:[]; }catch(e){ return []; } }
function setMsg(sel,t){ var m=$(sel); if(m) m.textContent=t; }
function ndT(k){ var l=lsGet("nd-lang")||"en"; return (I18N[l]&&I18N[l][k])||(I18N.en&&I18N.en[k])||k; }
function applyLang(l){
    if(!I18N[l]) l="en";
    document.querySelectorAll("[data-i18n]").forEach(function(el){
      var k=el.getAttribute("data-i18n"); if(!k) return;
      if(el.getAttribute("data-en")===null) el.setAttribute("data-en",el.textContent);
      el.textContent=(l==="en")?el.getAttribute("data-en"):((I18N[l]&&I18N[l][k])||el.getAttribute("data-en"));
    });
    document.querySelectorAll("[data-i18n-ph]").forEach(function(el){
      var k=el.getAttribute("data-i18n-ph"); if(!k) return;
      if(el.getAttribute("data-en")===null) el.setAttribute("data-en",el.getAttribute("placeholder")||"");
      el.setAttribute("placeholder",(l==="en")?el.getAttribute("data-en"):((I18N[l]&&I18N[l][k])||el.getAttribute("data-en")));
    });
    document.documentElement.setAttribute("lang",l);
    if(l==="ar") document.documentElement.setAttribute("dir","rtl"); else document.documentElement.removeAttribute("dir");
    var sel=$("#lang-select"); if(sel) sel.value=l;
    lsSet("nd-lang",l);
    refreshFavBtn();
  }
function isFav(id){ return favs.indexOf(id)>-1; }
function refreshFavBtn(){
    var b=$("#fav-btn"); if(!b||!curTool) return;
    var f=isFav(curTool);
    b.setAttribute("aria-pressed",String(f));
    b.textContent=ndT(f?"pinDone":"pinAdd");
  }
function placePersonal(mode){
    var wrap=$("#home-personal"), home=$("#home-view");
    if(!wrap||!home||wrap.parentNode!==home) return;
    if(mode==="standard"){
      var az=$("#az"); if(az&&az.parentNode===home&&az.nextSibling!==wrap) home.insertBefore(wrap,az.nextSibling);
    }else{
      var hero=home.querySelector(".hero"); if(hero&&hero.nextSibling!==wrap) home.insertBefore(wrap,hero.nextSibling);
    }
  }
function renderPersonal(){
    var wrap=$("#home-personal"); if(!wrap) return;
    function fill(gridSel,blockSel,ids){
      var g=$(gridSel), bl=$(blockSel); if(!g||!bl) return 0;
      var tools=ids.map(function(id){ return (typeof toolById==="function")?toolById(id):null; }).filter(Boolean);
      bl.classList.toggle("hidden",!tools.length);
      if(tools.length&&typeof cardHTML==="function") g.innerHTML=tools.map(cardHTML).join("");
      return tools.length;
    }
    var nf=fill("#fav-grid","#fav-block",favs);
    var nr=fill("#recent-grid","#recent-block",recents);
    wrap.classList.toggle("hidden",!(nf||nr));
    if((nf||nr)&&typeof bindCards==="function") bindCards();
    var fc=$("#fav-count"); if(fc) fc.textContent=favs.length;
    var rc=$("#recent-count"); if(rc) rc.textContent=recents.length;
    placePersonal(lsGet("nd-home")||"standard");
  }
function fill(gridSel,blockSel,ids){
      var g=$(gridSel), bl=$(blockSel); if(!g||!bl) return 0;
      var tools=ids.map(function(id){ return (typeof toolById==="function")?toolById(id):null; }).filter(Boolean);
      bl.classList.toggle("hidden",!tools.length);
      if(tools.length&&typeof cardHTML==="function") g.innerHTML=tools.map(cardHTML).join("");
      return tools.length;
    }
function segSync(attr,val){
    document.querySelectorAll("["+attr+"]").forEach(function(b){ b.setAttribute("aria-pressed",String((b.getAttribute(attr)||"")===val)); });
  }
function segWire(attr,fn){
    document.querySelectorAll("["+attr+"]").forEach(function(b){ b.addEventListener("click",function(){ fn(b.getAttribute(attr)||""); }); });
  }
function applyAccent(v){ if(v) document.documentElement.setAttribute("data-accent",v); else document.documentElement.removeAttribute("data-accent"); lsSet("nd-accent",v); segSync("data-accent-pick",v); }
function applyFont(v){ if(v) document.documentElement.setAttribute("data-font",v); else document.documentElement.removeAttribute("data-font"); lsSet("nd-font",v); segSync("data-font-pick",v); }
function applyDensity(v){ if(v) document.documentElement.setAttribute("data-density",v); else document.documentElement.removeAttribute("data-density"); lsSet("nd-density",v); segSync("data-density-pick",v); }
function applyHomeLayout(v){
    if(!v) v="standard";
    document.documentElement.setAttribute("data-home",v); lsSet("nd-home",v);
    var s=$("#home-layout"); if(s) s.value=v;
    renderPersonal();
  }
function resetAll(){
    ["nd-theme","nd-accent","nd-font","nd-density","nd-home","nd-lang","nd-cur","nd-favs","nd-recent"].forEach(lsDel);
    favs=[]; recents=[];
    if(typeof applyTheme==="function") applyTheme("auto");
    applyAccent(""); applyFont(""); applyDensity(""); applyHomeLayout("standard"); applyLang("en");
    ["currency","currency-2","currency-3"].forEach(function(id){ var el=document.getElementById(id); if(el) el.value="USD"; });
    try{ CUR="USD"; }catch(e){}
    renderPersonal();
    setMsg("#settings-msg",ndT("resetDone"));
  }
function gotoGame(panelId){
    if(typeof openGame==="function") openGame();
    setTimeout(function(){ var p=document.getElementById(panelId); if(p&&p.scrollIntoView) p.scrollIntoView({behavior:"smooth",block:"start"}); },80);
  }
function ri(min,max){ return min+Math.floor(Math.random()*(max-min+1)); }
function sprintUpd(){ setMsg("#sprint-score",String(sprint.score)); setMsg("#sprint-time",String(sprint.time)); }
function sprintQ(){
    var ops=["+","−","×","÷"], op=ops[Math.floor(Math.random()*ops.length)], a=0, b=0;
    if(op==="+"){ a=ri(3,99); b=ri(3,99); sprint.ans=a+b; }
    else if(op==="−"){ a=ri(10,99); b=ri(3,a); sprint.ans=a-b; }
    else if(op==="×"){ a=ri(2,12); b=ri(2,12); sprint.ans=a*b; }
    else { b=ri(2,12); sprint.ans=ri(2,12); a=b*sprint.ans; }
    setMsg("#sprint-q",a+" "+op+" "+b+" = ?");
  }
function endSprint(){
    if(sprint.timer){ clearInterval(sprint.timer); sprint.timer=0; }
    sprint.on=false;
    var inp=$("#sprint-in"); if(inp) inp.disabled=true;
    setMsg("#sprint-q",ndT("sprintReady"));
    if(sprint.score>sprint.best){ sprint.best=sprint.score; lsSet("nd-sprint-best",String(sprint.best)); setMsg("#sprint-best",String(sprint.best)); }
    setMsg("#sprint-msg",ndT("sprintOver").replace("{n}",sprint.score));
  }
function initSprint(){
    var st=$("#sprint-start"), inp=$("#sprint-in"); if(!st||!inp) return;
    setMsg("#sprint-best",String(sprint.best));
    st.addEventListener("click",function(){
      if(sprint.timer){ clearInterval(sprint.timer); sprint.timer=0; }
      sprint.on=true; sprint.score=0; sprint.time=60; sprintUpd();
      inp.disabled=false; inp.value=""; sprintQ(); if(inp.focus) inp.focus();
      setMsg("#sprint-msg",ndT("sprintGo"));
      st.textContent=ndT("sprintRestart");
      sprint.timer=setInterval(function(){
        sprint.time--; setMsg("#sprint-time",String(Math.max(0,sprint.time)));
        if(sprint.time<=0) endSprint();
      },1000);
    });
    inp.addEventListener("input",function(){
      if(!sprint.on) return;
      if(inp.value!==""&&parseFloat(inp.value)===sprint.ans){ sprint.score++; sprintUpd(); inp.value=""; sprintQ(); }
    });
  }
function pracNew(){
    prac.target=""; for(var i=0;i<4;i++) prac.target+=String(Math.floor(Math.random()*10));
    prac.row=0; prac.cur=""; prac.over=false;
    var board=$("#p-board"); if(!board) return;
    var h="";
    for(var r=0;r<8;r++){ h+='<div class="grow">'; for(var c=0;c<4;c++) h+='<div class="cell" id="pc-'+r+"-"+c+'"></div>'; h+="</div>"; }
    board.innerHTML=h;
    setMsg("#p-msg","");
  }
function pracRender(){
    for(var c=0;c<4;c++){
      var cell=document.getElementById("pc-"+prac.row+"-"+c);
      if(cell){ cell.textContent=prac.cur[c]||""; cell.classList.toggle("filled",!!prac.cur[c]); }
    }
  }
function pracScore(){
    var g=prac.cur, t=prac.target, res=["grey","grey","grey","grey"], used=[false,false,false,false], i, j;
    for(i=0;i<4;i++){ if(g[i]===t[i]){ res[i]="green"; used[i]=true; } }
    for(i=0;i<4;i++){ if(res[i]==="green") continue; for(j=0;j<4;j++){ if(!used[j]&&g[i]===t[j]){ res[i]="yellow"; used[j]=true; break; } } }
    for(i=0;i<4;i++){
      var cell=document.getElementById("pc-"+prac.row+"-"+i);
      if(cell){ cell.textContent=g[i]; cell.classList.add(res[i]); }
      var btn=document.getElementById("pk-"+g[i]);
      if(btn){
        var rank={grey:1,yellow:2,green:3}, curR=parseInt(btn.getAttribute("data-r")||"0",10);
        if(rank[res[i]]>curR){ btn.setAttribute("data-r",String(rank[res[i]])); btn.classList.remove("green","yellow","grey"); btn.classList.add(res[i]); }
      }
    }
    if(g===t){ prac.over=true; setMsg("#p-msg",ndT("practiceWin").replace("{n}",String(prac.row+1))); return; }
    prac.row++; prac.cur="";
    if(prac.row>=8){ prac.over=true; setMsg("#p-msg",ndT("practiceLose").replace("{t}",t)); }
  }
function pracKey(k){
    if(prac.over) return;
    if(k==="back"){ prac.cur=prac.cur.slice(0,-1); pracRender(); return; }
    if(k==="enter"){ if(prac.cur.length<4){ setMsg("#p-msg",ndT("practiceShort")); return; } pracScore(); return; }
    if(/^\d$/.test(k)&&prac.cur.length<4){ prac.cur+=k; pracRender(); }
  }
function initPractice(){
    var kp=$("#p-keypad"); if(!kp) return;
    var keys=["1","2","3","4","5","6","7","8","9","back","0","enter"];
    kp.innerHTML=keys.map(function(k){
      if(k==="back") return '<button type="button" data-pk="back" aria-label="Delete last digit">⌫</button>';
      if(k==="enter") return '<button type="button" data-pk="enter" class="wide">Enter</button>';
      return '<button type="button" data-pk="'+k+'" id="pk-'+k+'">'+k+"</button>";
    }).join("");
    kp.querySelectorAll("[data-pk]").forEach(function(b){ b.addEventListener("click",function(){ pracKey(b.getAttribute("data-pk")); }); });
    var nw=$("#p-new");
    if(nw) nw.addEventListener("click",function(){
      kp.querySelectorAll("button").forEach(function(b){ b.classList.remove("green","yellow","grey"); b.removeAttribute("data-r"); });
      pracNew();
    });
    pracNew();
  }
function tbtn35(id){ var t=(typeof toolById==="function")?toolById(id):null; return t?{label:t.name.replace(" Calculator",""),act:"tool",id:id}:null; }
function btns35(ids){ return ids.map(tbtn35).filter(Boolean); }
function esc(s){ return String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
var FAMS=[{"key":"length","base":"metres","def":5,"note":"Surveying, travel and science all meet here: the international inch is exactly 25.4 mm by treaty (1959), so every imperial length below is exact, not approximate."},{"key":"mass","base":"kilograms","def":10,"note":"The pound and ounce here are the international avoirdupois weights (1 lb = exactly 0.45359237 kg). A troy ounce — used for gold — is different (31.1035 g); the gold tools on this site handle that."},{"key":"volume","base":"litres","def":2,"note":"US measures are the customary liquid ones (1 US gallon = exactly 231 cubic inches). A US cup is 236.588 ml for cooking; the metric cup (250 ml) used in Australia differs — check the label on yours."},{"key":"area","base":"square metres","def":100,"note":"Marla and kanal are the South Asian land units (1 marla = 272.25 sq ft exactly under the standard definition; local variants exist in some districts). A cent is 1/100 of an acre, used in South India."},{"key":"speed","base":"metres per second","def":60,"note":"Mach depends on the speed of sound, which changes with altitude and temperature — the figure here is the sea-level standard (340.29 m/s at 20 °C). Knots are nautical miles per hour, exact by definition."},{"key":"pressure","base":"pascals","def":1,"note":"Standard atmosphere (atm) is exactly 101,325 Pa. Tyre gauges in psi read gauge pressure (above atmospheric); weather maps use hPa, which is 100 Pa — the same as a millibar."},{"key":"energy","base":"joules","def":100,"note":"Food 'calories' are kilocalories (kcal). A kilowatt-hour is exactly 3.6 megajoules — the unit your electricity bill counts. The electronvolt is the particle-physics unit, tiny by design."},{"key":"power","base":"watts","def":1,"note":"Mechanical horsepower (hp) is 745.7 W; the metric horsepower (PS, used for cars in Europe) is 735.5 W. Both are here — check which one a spec sheet means before comparing."},{"key":"time","base":"seconds","def":90,"note":"A 'month' here is the average month (30.44 days = a year of 365.25 days divided by 12) and a year is 365.25 days, counting leap years. Calendar months vary — for exact date maths use the Date Calculator."},{"key":"data","base":"bytes","def":500,"note":"KB, MB, GB here are decimal (powers of 1000) — how storage is sold and how networks count. KiB, MiB, GiB are binary (powers of 1024) — how operating systems usually report. The gap reaches 7% at gigabyte scale."},{"key":"angle","base":"degrees","def":180,"note":"Radians are the mathematician's unit (a full turn is 2π). Gradians (400 per turn) survive in European surveying. Arcminutes and arcseconds are how astronomers and navigators slice degrees."},{"key":"force","base":"newtons","def":100,"note":"A kilogram-force is the weight of a 1 kg mass under standard gravity (9.80665 m/s²) — your bathroom scale quietly measures force and reports it as mass. The dyne is the old cgs unit."},{"key":"torque","base":"newton-metres","def":50,"note":"Torque is force × distance — the same energy unit as the joule on paper, but never call torque 'joules'. Car specs quote N·m or lb-ft; the conversion is a favourite source of rounded errors."},{"key":"frequency","base":"hertz","def":60,"note":"Hertz is cycles per second, so revolutions per minute divides by 60. Radio bands (kHz to GHz) and processor clocks both live on this scale."},{"key":"density","base":"kilograms per cubic metre","def":1,"note":"Water is 1000 kg/m³ = 1 g/cm³ — the anchor of the whole scale. Anything below water's density floats in it; the rows make that check instant."},{"key":"flow","base":"litres per second","def":10,"note":"Flow conversions catch people out because time hides inside them: a cubic metre per hour sounds large but is only 0.28 litres per second. Shower heads run about 0.13–0.2 L/s."},{"key":"voltage","base":"volts","def":230,"note":"Voltage is electrical pressure. Mains is 230 V in most of the world, 120 V in North America; electronics live at 3.3–48 V; transmission lines run at hundreds of kilovolts."},{"key":"current","base":"amperes","def":5,"note":"Current is electrical flow. A phone charges at 1–3 A, a kettle draws 10–13 A, and the microamp range is where sensors and medical devices live."},{"key":"resistance","base":"ohms","def":100,"note":"Resistance links voltage and current through Ohm's law (V = I × R). Kiloohms are the everyday electronics range; megaohms measure insulation."},{"key":"temperature","base":"degrees Celsius","def":20,"note":"Temperature scales are offsets, not ratios — doubling 20 °C does not double the heat. Kelvin starts at absolute zero (−273.15 °C), where all thermal motion stops."},{"key":"fuel-economy","base":"kilometres per litre","def":8,"note":"Fuel economy flips between 'distance per fuel' (mpg, km/L) and 'fuel per distance' (L/100 km) — so a bigger mpg is better, but a bigger L/100 km is worse. US and UK gallons differ, so their mpg figures differ by 20% on the same car."},{"key":"data-rate","def":100,"note":"Data rates are bits per second; file sizes are bytes — the factor of 8 between them is why a '100 Mbps' line downloads at about 12.5 MB/s at best. Rates here are decimal (1000-based), as network engineers count."},{"key":"illuminance","def":500,"note":"Illuminance is light landing on a surface: a bright office is about 500 lux, full daylight 10,000+, moonlight under 1. The foot-candle is the US unit — one lumen per square foot."},{"key":"magnetic","def":1,"note":"Magnetic flux density: the tesla is the SI unit (an MRI scanner runs at 1.5–3 T; Earth's field is about 50 µT). The gauss is the older cgs unit, still printed on magnet specs — 1 T = 10,000 G exactly."},{"key":"dose-equivalent","def":1,"note":"Dose equivalent weights absorbed dose by radiation type — the sievert is the SI unit, the rem the older US one (1 Sv = 100 rem). A chest X-ray is about 0.1 mSv; natural background is roughly 2–3 mSv a year. Reference figures only — not medical advice."},{"key":"absorbed-dose","def":1,"note":"Absorbed dose is energy deposited per kilogram: the gray is the SI unit, the rad the older one (1 Gy = 100 rad). Radiotherapy doses are prescribed in gray. Reference figures only — not medical advice."},{"key":"activity","def":1000,"note":"Radioactivity is decays per second: the becquerel is the SI unit. The curie — the activity of 1 g of radium — is enormous (37 GBq), which is why millicuries and microcuries are the working units. Reference figures only."},{"key":"typography","def":12,"note":"Type sizes: the point is 1/72 inch exactly in digital publishing, the pica is 12 points, and the pixel here is the CSS pixel (96 per inch). Em and twip depend on context, so this family sticks to the fixed units."},{"key":"capacitance","def":10,"note":"Capacitance in farads — the farad is huge, so real capacitors live in microfarads and picofarads. The unit printed on the part is the one to convert from; guessing a prefix wrong is a 1000× error."},{"key":"inductance","def":10,"note":"Inductance in henries: power chokes are millihenries, RF coils microhenries. The henry is 1 volt-second per ampere."},{"key":"charge","def":1,"note":"Electric charge: the coulomb is the SI unit; battery capacity in amp-hours and milliamp-hours is charge in disguise (1 Ah = 3,600 C) — which is why a 5,000 mAh phone battery holds 18,000 coulombs."},{"key":"luminance","def":100,"note":"Luminance is how bright a surface looks: a phone screen is 200–500 cd/m², an overcast sky about 3,000, the Sun about 1.6 billion. The nit is the same as cd/m²; the lambert and foot-lambert survive in cinema and aviation."},{"key":"magnetic-flux","def":1,"note":"Magnetic flux: the weber is the SI unit; the maxwell is the cgs unit still printed on older magnet and loudspeaker specs (1 Wb = 100 million Mx)."},{"key":"electric-field","def":100,"note":"Electric field strength: mains wiring creates fields of a few V/m at arm's length; a thunderstorm's ground field can reach thousands of V/m before lightning. Reference figures only."},{"key":"molar-concentration","def":1,"note":"Molarity in mol/L is the chemist's everyday unit; blood and water tests usually report the milli- and micromole rows. 1 mol/L = 1,000 mol/m³."},{"key":"mass-concentration","def":100,"note":"Mass concentration: water-quality and lab results live in mg/L and µg/L. For water-like liquids, 1 mg/L is about 1 part per million by mass."},{"key":"dynamic-viscosity","def":1,"note":"Dynamic viscosity: water is about 1 mPa·s (1 centipoise) at 20 °C, honey several thousand. The poise is the cgs unit — 1 Pa·s = 10 P exactly."},{"key":"kinematic-viscosity","def":1,"note":"Kinematic viscosity (viscosity divided by density): engine oils are graded in centistokes at 100 °C — a 30-grade oil is about 9–12 cSt hot. 1 St = 1 cm²/s exactly."},{"key":"acceleration","def":10,"note":"Acceleration: standard gravity (1 g = 9.80665 m/s²) is the reference everything is compared against — a family car braking hard reaches about 0.8 g; the gal is the geophysicist's unit (1 cm/s²)."},{"key":"angular-velocity","def":10,"note":"Angular velocity: a vinyl LP spins at 33⅓ rpm (about 3.49 rad/s), a washing-machine spin cycle near 1,400 rpm. Radians per second is the unit physics formulas expect."},{"key":"moment-of-inertia","def":1,"note":"Moment of inertia — rotational mass: flywheels, pulleys and robot arms are specified in these units. Double the radius and the same mass counts four times as much."},{"key":"thermal-conductivity","def":1,"note":"Thermal conductivity: copper is about 400 W/(m·K), brick about 0.7, insulation foam about 0.03 — lower insulates better. The BTU unit is per hour, foot and degree Fahrenheit."},{"key":"specific-heat","def":1000,"note":"Specific heat capacity: water is 4,186.8 J/(kg·K) — the highest of any common liquid, which is why coasts have mild climates and why heating water dominates energy bills."},{"key":"surface-tension","def":1,"note":"Surface tension: pure water is about 72.8 mN/m at 20 °C; soap cuts it, which is why bubbles form and grease lifts. 1 dyn/cm = 1 mN/m exactly."},{"key":"radiation-exposure","def":1,"note":"Exposure (ionisation in air): the roentgen is the historic unit, the coulomb per kilogram the SI one. Reference figures only — not medical or safety advice."},{"key":"heat-flux","def":1000,"note":"Heat flux density: noon sunlight at the ground is about 1,000 W/m²; a house wall in winter leaks roughly 10–50 W/m² through each square metre."},{"key":"resistivity","def":1,"note":"Electrical resistivity: copper is 1.68×10⁻⁸ Ω·m, seawater about 0.2 Ω·m, and good insulators run to 10¹⁵. The circular-mil-ohm per foot is the US wire trade's unit."},{"key":"conductance","def":1,"note":"Conductance is the siemens — the reciprocal of resistance. The mho (ohm spelled backwards) is the same unit under its old name, still seen on older instruments."},{"key":"dose-rate","def":1,"note":"Dose rate: natural background is roughly 0.1–0.3 µSv/h in most places; a chest CT delivers its dose in minutes at a far higher rate. Reference figures only — not medical or safety advice."},{"key":"wavenumber","def":100,"note":"Wavenumber counts waves per unit length — spectroscopy's favourite axis: infrared spectra are plotted in cm⁻¹ (kayser), and a bigger wavenumber always means a shorter wavelength and a higher frequency."},{"key":"area-density","def":200,"note":"Area density is mass per area: paper and fabric are sold by it (copy paper is 80 gsm), and roof and floor loads are quoted in kg/m². The pound-per-square-foot and ounce-per-square-yard rows are the US paper and textile forms."},{"key":"linear-density","def":100,"note":"Linear density is how yarn and fibre are sized: tex is grams per kilometre, denier is grams per 9,000 metres (stockings are 10–20 denier), and decitex is the label unit on most modern yarn."},{"key":"magnetic-field-strength","def":80,"note":"Field strength H: the ampere per metre is the SI unit; the oersted is the cgs unit still printed on magnet and motor datasheets (1 Oe ≈ 79.577 A/m). Not the same as flux density (tesla) — H is the magnetising push, B is the resulting field."},{"key":"specific-volume","def":1,"note":"Specific volume is volume per unit mass — the reciprocal of density, and the number steam tables are built on: dry steam at atmospheric pressure is about 1.67 m³/kg."},{"key":"heat-capacity","def":100,"note":"Heat capacity is the energy to warm a whole object by one degree — a kettle of water is roughly 8,400 J/K, which is why it takes minutes to boil. Per-kilogram values live in the specific-heat family."},{"key":"electric-displacement","def":1,"note":"Electric displacement D measures charge per area on capacitor plates and in dielectrics — the quantity that stays continuous across a material boundary, where the field E jumps."}];
var FAM_UNITS={};
FAM_UNITS["length"]=[{n:"Millimetre",s:"mm",f:0.001},{n:"Centimetre",s:"cm",f:0.01},{n:"Metre",s:"m",f:1},{n:"Kilometre",s:"km",f:1000},{n:"Inch",s:"in",f:0.0254},{n:"Foot",s:"ft",f:0.3048},{n:"Yard",s:"yd",f:0.9144},{n:"Mile",s:"mi",f:1609.344},{n:"Nautical Mile",s:"nmi",f:1852},{n:"Fathom",s:"ftm",f:1.8288},{n:"Furlong",s:"fur",f:201.168},{n:"Light-Year",s:"ly",f:9460700000000000},{n:"Micrometre",s:"µm",f:0.000001},{n:"Nanometre",s:"nm",f:1e-9},{n:"Angstrom",s:"Å",f:1e-10},{n:"Chain",s:"ch",f:20.1168},{n:"Rod",s:"rd",f:5.0292},{n:"League",s:"lea",f:4828.032},{n:"Astronomical Unit",s:"AU",f:149597870700},{n:"Parsec",s:"pc",f:30856775810000000},{n:"Planck Length",s:"lP",f:1.616255e-35},{n:"Bohr Radius",s:"a0",f:5.29177210903e-11},{n:"Cubit",s:"cubit",f:0.4572},{n:"Hand",s:"hand",f:0.1016},{n:"Span",s:"span",f:0.2286},{n:"Digit",s:"digit",f:0.01905},{n:"Barleycorn",s:"bc",f:0.008466666666666667},{n:"Earth Radius",s:"R⊕",f:6371000},{n:"Lunar Distance",s:"LD",f:384400000},{n:"Light-Minute",s:"lmin",f:17987547480},{n:"Light-Hour",s:"lhr",f:1079252848800},{n:"Solar Radius",s:"R☉",f:695700000},{n:"Mil",s:"mil",f:0.0000254},{n:"Microinch",s:"µin",f:2.54e-8},{n:"Point",s:"pt",f:0.00035277777777777776},{n:"Cable Length",s:"cable",f:185.2},{n:"Roman Mile",s:"mi Roman",f:1479.5},{n:"Verst",s:"verst",f:1066.8},{n:"Arshin",s:"arshin",f:0.7112},{n:"Chinese Li",s:"li",f:500},{n:"Japanese Ri",s:"ri",f:3927.272727272727},{n:"Stadion",s:"stadion",f:185},{n:"Palm",s:"palm",f:0.0762},{n:"Finger",s:"finger",f:0.022225},{n:"Link",s:"lnk",f:0.201168},{n:"Ell",s:"ell",f:1.143},{n:"Pace",s:"pace",f:0.762},{n:"Light-Second",s:"ls",f:299792458},{n:"Light-Day",s:"ld",f:25902068371200},{n:"Megametre",s:"Mm",f:1000000},{n:"Gigametre",s:"Gm",f:1000000000},{n:"Smoot",s:"smoot",f:1.7018},{n:"Kiloparsec",s:"kpc",f:30856775814913670000},{n:"Megaparsec",s:"Mpc",f:3.085677581491367e+22}];
FAM_UNITS["mass"]=[{n:"Milligram",s:"mg",f:0.000001},{n:"Gram",s:"g",f:0.001},{n:"Kilogram",s:"kg",f:1},{n:"Tonne",s:"t",f:1000},{n:"Ounce",s:"oz",f:0.028349523125},{n:"Pound",s:"lb",f:0.45359237},{n:"Stone",s:"st",f:6.35029318},{n:"US Ton",s:"ton",f:907.18474},{n:"Grain",s:"gr",f:0.00006479891},{n:"Carat",s:"ct",f:0.0002},{n:"Dram",s:"dr",f:0.0017718451953125},{n:"Microgram",s:"µg",f:1e-9},{n:"Troy Ounce",s:"ozt",f:0.0311034768},{n:"Troy Pound",s:"lbt",f:0.3732417216},{n:"Pennyweight",s:"dwt",f:0.00155517384},{n:"UK Hundredweight",s:"cwt UK",f:50.80234544},{n:"US Hundredweight",s:"cwt US",f:45.359237},{n:"Quarter",s:"qr",f:12.70058636},{n:"Tola",s:"tola",f:0.0116638038},{n:"UK Ton",s:"UK ton",f:1016.0469088},{n:"Slug",s:"slug",f:14.5939029372},{n:"Atomic Mass Unit",s:"u",f:1.6605390666e-27},{n:"Electron Mass",s:"me",f:9.1093837015e-31},{n:"Planck Mass",s:"mP",f:2.176434e-8},{n:"Earth Mass",s:"M⊕",f:5.9722e+24},{n:"Solar Mass",s:"M☉",f:1.98847e+30},{n:"Quintal",s:"q",f:100},{n:"Megatonne",s:"Mt",f:1000000000},{n:"Gigatonne",s:"Gt",f:1000000000000},{n:"Nanogram",s:"ng",f:1e-12},{n:"Picogram",s:"pg",f:1e-15},{n:"Attogram",s:"ag",f:1e-21},{n:"Baht",s:"baht",f:0.015244},{n:"Tael",s:"tael",f:0.03779936375},{n:"Jin",s:"jin",f:0.5},{n:"Masha",s:"masha",f:0.000972},{n:"Ratti",s:"ratti",f:0.0001215},{n:"Monme",s:"monme",f:0.00375},{n:"Kwan",s:"kwan",f:3.75},{n:"Shekel",s:"shekel",f:0.0114},{n:"Mina",s:"mina",f:0.42857142857142855},{n:"Wey",s:"wey",f:114.30527724}];
FAM_UNITS["volume"]=[{n:"Millilitre",s:"ml",f:0.001},{n:"Litre",s:"L",f:1},{n:"Cubic Metre",s:"m³",f:1000},{n:"US Teaspoon",s:"tsp",f:0.00492892159375},{n:"US Tablespoon",s:"tbsp",f:0.01478676478125},{n:"US Fluid Ounce",s:"fl oz",f:0.0295735295625},{n:"US Cup",s:"cup",f:0.2365882365},{n:"US Pint",s:"pt",f:0.473176473},{n:"US Quart",s:"qt",f:0.946352946},{n:"US Gallon",s:"gal",f:3.785411784},{n:"UK Gallon",s:"gal UK",f:4.54609},{n:"Cubic Inch",s:"in³",f:0.016387064},{n:"UK Fluid Ounce",s:"fl oz UK",f:0.0284130625},{n:"UK Pint",s:"pt UK",f:0.56826125},{n:"UK Quart",s:"qt UK",f:1.1365225},{n:"Cubic Foot",s:"ft³",f:28.316846592},{n:"Cubic Yard",s:"yd³",f:764.554857984},{n:"Board Foot",s:"bf",f:2.359737216},{n:"Acre-Foot",s:"ac·ft",f:1233481.83754752},{n:"Cubic Centimetre",s:"cm³",f:0.001},{n:"Drop",s:"drop",f:0.00005},{n:"US Minim",s:"min",f:0.000061611519921875},{n:"US Gill",s:"gi",f:0.11829411825},{n:"UK Gill",s:"gi UK",f:0.1420653125},{n:"US Peck",s:"pk",f:8.80976754172},{n:"US Bushel",s:"bu",f:35.23907016688},{n:"UK Bushel",s:"bu UK",f:36.36872},{n:"Oil Barrel",s:"bbl",f:158.987294928},{n:"US Liquid Barrel",s:"bbl US",f:119.240471196},{n:"Hogshead",s:"hhd",f:238.480942392},{n:"Cord",s:"cord",f:3624.556363776},{n:"Cubic Kilometre",s:"km³",f:1000000000000},{n:"Cubic Millimetre",s:"mm³",f:0.000001},{n:"Cubic Decimetre",s:"dm³",f:1},{n:"Microlitre",s:"µL",f:0.000001},{n:"Nanolitre",s:"nL",f:1e-9},{n:"Hectolitre",s:"hL",f:100},{n:"Decilitre",s:"dL",f:0.1},{n:"Centilitre",s:"cL",f:0.01},{n:"UK Teaspoon",s:"tsp UK",f:0.005919388020833333},{n:"UK Tablespoon",s:"tbsp UK",f:0.0177581640625},{n:"Dessertspoon",s:"dstspn",f:0.01},{n:"Metric Teaspoon",s:"tsp metric",f:0.005},{n:"Acre-Inch",s:"ac·in",f:102790.15312896},{n:"Shot",s:"shot",f:0.04436029434375}];
FAM_UNITS["area"]=[{n:"Square Centimetre",s:"cm²",f:0.0001},{n:"Square Metre",s:"m²",f:1},{n:"Square Kilometre",s:"km²",f:1000000},{n:"Hectare",s:"ha",f:10000},{n:"Acre",s:"ac",f:4046.8564224},{n:"Square Inch",s:"in²",f:0.00064516},{n:"Square Foot",s:"ft²",f:0.09290304},{n:"Square Yard",s:"yd²",f:0.83612736},{n:"Square Mile",s:"mi²",f:2589988.110336},{n:"Marla",s:"marla",f:25.29285264},{n:"Kanal",s:"kanal",f:505.85704528},{n:"Cent",s:"cent",f:40.468564224},{n:"Bigha",s:"bigha",f:2508.38208},{n:"Guntha",s:"guntha",f:101.17141056},{n:"Katha",s:"katha",f:126.441762304},{n:"Ground",s:"ground",f:222.96744},{n:"Square Chain",s:"ch²",f:404.68564224},{n:"Rood",s:"rood",f:1011.7141056},{n:"Barn",s:"b",f:1e-28},{n:"Square Millimetre",s:"mm²",f:0.000001},{n:"Dunam",s:"dunam",f:1000},{n:"Township",s:"twp",f:93239571.972},{n:"Ankanam",s:"ankanam",f:6.68902848},{n:"Square Micrometre",s:"µm²",f:1e-12},{n:"Square Nanometre",s:"nm²",f:1e-18},{n:"Square Megametre",s:"Mm²",f:1000000000000},{n:"Circular Mil",s:"cmil",f:5.067074790974977e-10},{n:"Section",s:"section",f:2589988.110336},{n:"Square Perch",s:"perch²",f:25.29285264},{n:"Square Link",s:"li²",f:0.040468564224},{n:"Are",s:"a",f:100},{n:"Centiare",s:"ca",f:1},{n:"Square Furlong",s:"fur²",f:40468.564224},{n:"Tsubo",s:"tsubo",f:3.305785123966942},{n:"Arpent",s:"arpent",f:3418.873925}];
FAM_UNITS["speed"]=[{n:"Metre per Second",s:"m/s",f:1},{n:"Kilometre per Hour",s:"km/h",f:0.2777777777777778},{n:"Mile per Hour",s:"mph",f:0.44704},{n:"Knot",s:"kn",f:0.5144444444444445},{n:"Foot per Second",s:"ft/s",f:0.3048},{n:"Centimetre per Second",s:"cm/s",f:0.01},{n:"Mach",s:"Mach",f:340.29},{n:"Speed of Light",s:"c",f:299792458},{n:"Speed of Sound",s:"sound",f:343},{n:"Inch per Second",s:"in/s",f:0.0254},{n:"Mile per Minute",s:"mi/min",f:26.8224},{n:"Kilometre per Second",s:"km/s",f:1000},{n:"Metre per Minute",s:"m/min",f:0.016666666666666666},{n:"Kilometre per Minute",s:"km/min",f:16.666666666666668},{n:"Kilometre per Day",s:"km/day",f:0.011574074074074073},{n:"Mile per Second",s:"mi/s",f:1609.344},{n:"Foot per Minute",s:"ft/min",f:0.00508},{n:"Foot per Hour",s:"ft/h",f:0.00008466666666666667},{n:"Inch per Minute",s:"in/min",f:0.0004233333333333333},{n:"Yard per Second",s:"yd/s",f:0.9144},{n:"Metre per Hour",s:"m/h",f:0.0002777777777777778}];
FAM_UNITS["pressure"]=[{n:"Pascal",s:"Pa",f:1},{n:"Kilopascal",s:"kPa",f:1000},{n:"Megapascal",s:"MPa",f:1000000},{n:"Bar",s:"bar",f:100000},{n:"Atmosphere",s:"atm",f:101325},{n:"Pound per Square Inch",s:"psi",f:6894.757293168},{n:"Millimetre of Mercury",s:"mmHg",f:133.322387415},{n:"Inch of Mercury",s:"inHg",f:3386.38815789},{n:"Torr",s:"Torr",f:133.32236842105263},{n:"Millibar",s:"mbar",f:100},{n:"Kilopound per Square Inch",s:"ksi",f:6894757.293168},{n:"Inch of Water",s:"inH2O",f:249.08891},{n:"Centimetre of Mercury",s:"cmHg",f:1333.22387415},{n:"Barye",s:"Ba",f:0.1},{n:"Technical Atmosphere",s:"at",f:98066.5},{n:"Gigapascal",s:"GPa",f:1000000000},{n:"Hectopascal",s:"hPa",f:100},{n:"Decapascal",s:"daPa",f:10},{n:"Pound per Square Foot",s:"psf",f:47.88025898033584},{n:"Kip per Square Foot",s:"ksf",f:47880.25898033584},{n:"Ton per Square Foot",s:"tsf",f:95760.51796067168},{n:"Metre of Water",s:"mH2O",f:9806.65},{n:"Centimetre of Water",s:"cmH2O",f:98.0665}];
FAM_UNITS["energy"]=[{n:"Joule",s:"J",f:1},{n:"Kilojoule",s:"kJ",f:1000},{n:"Calorie",s:"cal",f:4.184},{n:"Kilocalorie",s:"kcal",f:4184},{n:"Watt-Hour",s:"Wh",f:3600},{n:"Kilowatt-Hour",s:"kWh",f:3600000},{n:"British Thermal Unit",s:"BTU",f:1055.05585262},{n:"Foot-Pound",s:"ft·lbf",f:1.3558179483314003},{n:"Electronvolt",s:"eV",f:1.602176634e-19},{n:"Erg",s:"erg",f:1e-7},{n:"Therm",s:"thm",f:105480400},{n:"Quad",s:"quad",f:1055055852620000000},{n:"Tonne of Oil Equivalent",s:"toe",f:41868000000},{n:"Megaelectronvolt",s:"MeV",f:1.602176634e-13},{n:"Hartree",s:"Ha",f:4.3597447222071e-18},{n:"Litre-Atmosphere",s:"L·atm",f:101.325},{n:"Gigajoule",s:"GJ",f:1000000000},{n:"Megajoule",s:"MJ",f:1000000},{n:"Microjoule",s:"µJ",f:0.000001},{n:"Nanojoule",s:"nJ",f:1e-9},{n:"Tonne of Coal Equivalent",s:"tce",f:29288000000},{n:"Million BTU",s:"MMBtu",f:1055055852.62},{n:"Rydberg",s:"Ry",f:2.1798723611035e-18},{n:"Celsius Heat Unit",s:"CHU",f:1899.100534716},{n:"Foot-Poundal",s:"ft·pdl",f:0.0421401100938048},{n:"Inch-Pound Force",s:"in·lbf",f:0.1129848290276167}];
FAM_UNITS["power"]=[{n:"Watt",s:"W",f:1},{n:"Kilowatt",s:"kW",f:1000},{n:"Megawatt",s:"MW",f:1000000},{n:"Horsepower",s:"hp",f:745.699872},{n:"Metric Horsepower",s:"PS",f:735.49875},{n:"BTU per Hour",s:"BTU/h",f:0.29307107017},{n:"Foot-Pound per Second",s:"ft·lbf/s",f:1.3558179483314003},{n:"Gigawatt",s:"GW",f:1000000000},{n:"Ton of Refrigeration",s:"TR",f:3516.8528420667},{n:"Kilocalorie per Hour",s:"kcal/h",f:1.1622222222222223},{n:"Erg per Second",s:"erg/s",f:1e-7},{n:"Boiler Horsepower",s:"bhp",f:9809.5},{n:"Terawatt",s:"TW",f:1000000000000},{n:"Petawatt",s:"PW",f:1000000000000000},{n:"Milliwatt",s:"mW",f:0.001},{n:"Microwatt",s:"µW",f:0.000001},{n:"Nanowatt",s:"nW",f:1e-9},{n:"Pound-Foot per Minute",s:"lb·ft/min",f:0.02259696580552334},{n:"BTU per Minute",s:"BTU/min",f:17.584264210333334},{n:"Kilocalorie per Minute",s:"kcal/min",f:69.73333333333333}];
FAM_UNITS["time"]=[{n:"Millisecond",s:"ms",f:0.001},{n:"Second",s:"s",f:1},{n:"Minute",s:"min",f:60},{n:"Hour",s:"h",f:3600},{n:"Day",s:"d",f:86400},{n:"Week",s:"wk",f:604800},{n:"Month (Average)",s:"mo",f:2629746},{n:"Year (365.25 Days)",s:"yr",f:31557600},{n:"Decade",s:"dec",f:315576000},{n:"Fortnight",s:"fn",f:1209600},{n:"Century",s:"century",f:3155760000},{n:"Millennium",s:"millennium",f:31557600000},{n:"Sidereal Day",s:"sidereal d",f:86164.0905},{n:"Tropical Year",s:"tropical yr",f:31556925.216},{n:"Shake",s:"shake",f:1e-8},{n:"Planck Time",s:"tP",f:5.391247e-44},{n:"Microsecond",s:"µs",f:0.000001},{n:"Nanosecond",s:"ns",f:1e-9},{n:"Picosecond",s:"ps",f:1e-12},{n:"Kilosecond",s:"ks",f:1000},{n:"Megasecond",s:"Ms",f:1000000},{n:"Gigasecond",s:"Gs",f:1000000000},{n:"Sidereal Year",s:"sidereal yr",f:31558149.8},{n:"Anomalistic Year",s:"anomalistic yr",f:31558432.538},{n:"Lunar Month",s:"lunar mo",f:2551442.976},{n:"Jiffy",s:"jiffy",f:0.016666666666666666}];
FAM_UNITS["data"]=[{n:"Bit",s:"bit",f:0.125},{n:"Byte",s:"B",f:1},{n:"Kilobyte",s:"KB",f:1000},{n:"Megabyte",s:"MB",f:1000000},{n:"Gigabyte",s:"GB",f:1000000000},{n:"Terabyte",s:"TB",f:1000000000000},{n:"Kibibyte",s:"KiB",f:1024},{n:"Mebibyte",s:"MiB",f:1048576},{n:"Gibibyte",s:"GiB",f:1073741824},{n:"Nibble",s:"nibble",f:0.5},{n:"Kilobit",s:"kbit",f:125},{n:"Megabit",s:"Mbit",f:125000},{n:"Gigabit",s:"Gbit",f:125000000},{n:"Terabit",s:"Tbit",f:125000000000},{n:"Petabit",s:"Pbit",f:125000000000000},{n:"Petabyte",s:"PB",f:1000000000000000},{n:"Exabyte",s:"EB",f:1000000000000000000},{n:"Pebibyte",s:"PiB",f:1125899906842624},{n:"Exbibyte",s:"EiB",f:1152921504606847000},{n:"Zettabyte",s:"ZB",f:1e+21},{n:"Yottabyte",s:"YB",f:1e+24},{n:"Zettabit",s:"Zbit",f:125000000000000000000},{n:"Yottabit",s:"Ybit",f:1.25e+23},{n:"Zebibyte",s:"ZiB",f:1.1805916207174113e+21},{n:"Yobibyte",s:"YiB",f:1.2089258196146292e+24},{n:"Kibibit",s:"Kibit",f:128},{n:"Mebibit",s:"Mibit",f:131072},{n:"Gibibit",s:"Gibit",f:134217728},{n:"Tebibit",s:"Tibit",f:137438953472},{n:"Word",s:"word",f:2},{n:"Double Word",s:"dword",f:4},{n:"Quad Word",s:"qword",f:8}];
FAM_UNITS["angle"]=[{n:"Degree",s:"°",f:1},{n:"Radian",s:"rad",f:57.29577951308232},{n:"Gradian",s:"grad",f:0.9},{n:"Turn",s:"turn",f:360},{n:"Arcminute",s:"′",f:0.016666666666666666},{n:"Arcsecond",s:"″",f:0.0002777777777777778},{n:"Milliradian",s:"mrad",f:0.05729577951308232},{n:"Quadrant",s:"quadrant",f:90},{n:"Sextant",s:"sextant",f:60},{n:"Sign",s:"sign",f:30},{n:"Point",s:"point",f:11.25},{n:"Milliarcsecond",s:"mas",f:2.777777777777778e-7},{n:"Microarcsecond",s:"µas",f:2.777777777777778e-10},{n:"Binary Degree",s:"brad",f:1.40625},{n:"Hour Angle",s:"HA",f:15},{n:"Octant",s:"octant",f:45},{n:"NATO Mil",s:"mil",f:0.05625}];
FAM_UNITS["force"]=[{n:"Newton",s:"N",f:1},{n:"Kilonewton",s:"kN",f:1000},{n:"Dyne",s:"dyn",f:0.00001},{n:"Pound-Force",s:"lbf",f:4.4482216152605},{n:"Kilogram-Force",s:"kgf",f:9.80665},{n:"Poundal",s:"pdl",f:0.138254954376},{n:"Kip",s:"kip",f:4448.2216152605},{n:"Ton-Force",s:"tf",f:8896.443230521},{n:"Ounce-Force",s:"ozf",f:0.2780138509537812},{n:"Gram-Force",s:"gf",f:0.00980665},{n:"Sthene",s:"sn",f:1000},{n:"Meganewton",s:"MN",f:1000000},{n:"Millinewton",s:"mN",f:0.001},{n:"Micronewton",s:"µN",f:0.000001},{n:"Nanonewton",s:"nN",f:1e-9},{n:"Decanewton",s:"daN",f:10},{n:"Long Ton-Force",s:"LTf",f:9964.016418170471}];
FAM_UNITS["torque"]=[{n:"Newton-Metre",s:"N·m",f:1},{n:"Pound-Foot",s:"lb·ft",f:1.3558179483314003},{n:"Pound-Inch",s:"lb·in",f:0.1129848290276167},{n:"Kilogram-Metre",s:"kgf·m",f:9.80665},{n:"Ounce-Inch",s:"oz·in",f:0.007061551814},{n:"Newton-Centimetre",s:"N·cm",f:0.01},{n:"Dyne-Centimetre",s:"dyn·cm",f:1e-7},{n:"Kilogram-Centimetre",s:"kgf·cm",f:0.0980665},{n:"Kilonewton-Metre",s:"kN·m",f:1000},{n:"Meganewton-Metre",s:"MN·m",f:1000000},{n:"Newton-Millimetre",s:"N·mm",f:0.001},{n:"Gram-Force Centimetre",s:"gf·cm",f:0.0000980665},{n:"Ounce-Foot",s:"oz·ft",f:0.0847386220276167}];
FAM_UNITS["frequency"]=[{n:"Hertz",s:"Hz",f:1},{n:"Kilohertz",s:"kHz",f:1000},{n:"Megahertz",s:"MHz",f:1000000},{n:"Gigahertz",s:"GHz",f:1000000000},{n:"Terahertz",s:"THz",f:1000000000000},{n:"Revolutions per Minute",s:"rpm",f:0.016666666666666666},{n:"Revolutions per Second",s:"rps",f:1},{n:"Frames per Second",s:"fps",f:1},{n:"Petahertz",s:"PHz",f:1000000000000000},{n:"Exahertz",s:"EHz",f:1000000000000000000},{n:"Millihertz",s:"mHz",f:0.001},{n:"Microhertz",s:"µHz",f:0.000001},{n:"Beat per Minute",s:"bpm",f:0.016666666666666666}];
FAM_UNITS["density"]=[{n:"Kilogram per Cubic Metre",s:"kg/m³",f:1},{n:"Gram per Cubic Centimetre",s:"g/cm³",f:1000},{n:"Gram per Millilitre",s:"g/mL",f:1000},{n:"Pound per Cubic Foot",s:"lb/ft³",f:16.01846337396014},{n:"Pound per US Gallon",s:"lb/gal",f:119.82642731689666},{n:"Gram per Litre",s:"g/L",f:1},{n:"Kilogram per Litre",s:"kg/L",f:1000},{n:"Ounce per Cubic Inch",s:"oz/in³",f:1729.994044},{n:"Pound per Cubic Inch",s:"lb/in³",f:27679.9047102},{n:"Tonne per Cubic Metre",s:"t/m³",f:1000},{n:"Milligram per Litre",s:"mg/L",f:0.001},{n:"Microgram per Litre",s:"µg/L",f:0.000001},{n:"Pound per Cubic Yard",s:"lb/yd³",f:0.5932764212577823},{n:"Ounce per US Gallon",s:"oz/gal",f:7.48915170730604},{n:"Gram per Cubic Metre",s:"g/m³",f:0.001},{n:"Slug per Cubic Foot",s:"slug/ft³",f:515.378818393}];
FAM_UNITS["flow"]=[{n:"Litre per Second",s:"L/s",f:1},{n:"Litre per Minute",s:"L/min",f:0.016666666666666666},{n:"Litre per Hour",s:"L/h",f:0.0002777777777777778},{n:"Cubic Metre per Hour",s:"m³/h",f:0.2777777777777778},{n:"US Gallon per Minute",s:"gpm",f:0.063090196403},{n:"Cubic Foot per Second",s:"ft³/s",f:28.316846592},{n:"Cubic Metre per Second",s:"m³/s",f:1000},{n:"Cubic Foot per Minute",s:"cfm",f:0.4719474432},{n:"UK Gallon per Minute",s:"gpm UK",f:0.07576816666666666},{n:"Millilitre per Second",s:"mL/s",f:0.001},{n:"Barrel per Day",s:"bbl/d",f:0.0018401307283333332},{n:"Cubic Inch per Second",s:"in³/s",f:0.016387064},{n:"Cubic Yard per Hour",s:"yd³/h",f:0.21237634944928271},{n:"Million Gallons per Day",s:"MGD",f:43.8126364},{n:"US Gallon per Day",s:"gal/d",f:0.00004381263638055556},{n:"US Gallon per Hour",s:"gal/h",f:0.0010515032735555557},{n:"Oil Barrel per Hour",s:"bbl/h",f:0.04416376645333333}];
FAM_UNITS["voltage"]=[{n:"Millivolt",s:"mV",f:0.001},{n:"Volt",s:"V",f:1},{n:"Kilovolt",s:"kV",f:1000},{n:"Megavolt",s:"MV",f:1000000},{n:"Statvolt",s:"statV",f:299.792458},{n:"Abvolt",s:"abV",f:1e-8},{n:"Gigavolt",s:"GV",f:1000000000},{n:"Nanovolt",s:"nV",f:1e-9},{n:"Picovolt",s:"pV",f:1e-12},{n:"Planck Voltage",s:"Vp",f:1.04295e+27}];
FAM_UNITS["current"]=[{n:"Microampere",s:"µA",f:0.000001},{n:"Milliampere",s:"mA",f:0.001},{n:"Ampere",s:"A",f:1},{n:"Kiloampere",s:"kA",f:1000},{n:"Statampere",s:"statA",f:3.335641e-10},{n:"Abampere",s:"abA",f:10},{n:"Megaampere",s:"MA",f:1000000},{n:"Nanoampere",s:"nA",f:1e-9},{n:"Picoampere",s:"pA",f:1e-12},{n:"Coulomb per Second",s:"C/s",f:1}];
FAM_UNITS["resistance"]=[{n:"Milliohm",s:"mΩ",f:0.001},{n:"Ohm",s:"Ω",f:1},{n:"Kiloohm",s:"kΩ",f:1000},{n:"Megaohm",s:"MΩ",f:1000000},{n:"Abohm",s:"abΩ",f:1e-9},{n:"Statohm",s:"statΩ",f:898755178736.8176},{n:"Gigaohm",s:"GΩ",f:1000000000},{n:"Microohm",s:"µΩ",f:0.000001},{n:"Nanoohm",s:"nΩ",f:1e-9},{n:"Picohm",s:"pΩ",f:1e-12}];
FAM_UNITS["temperature"]=[{n:"Celsius",s:"°C",to:function(v){return v;},from:function(v){return v;}},{n:"Fahrenheit",s:"°F",to:function(v){return (v-32)*5/9;},from:function(v){return v*9/5+32;}},{n:"Kelvin",s:"K",to:function(v){return v-273.15;},from:function(v){return v+273.15;}}];
FAM_UNITS["fuel-economy"]=[{n:"Kilometres per Litre",s:"km/L",to:function(v){return v;},from:function(v){return v;}},{n:"Litres per 100 km",s:"L/100km",to:function(v){return v>0?100/v:NaN;},from:function(v){return v>0?100/v:NaN;}},{n:"Miles per US Gallon",s:"mpg US",f:0.4251437074911184},{n:"Miles per UK Gallon",s:"mpg UK",f:0.35400618993569183}];
FAM_UNITS["data-rate"]=[{n:"Bit per Second",s:"bps",f:0.125},{n:"Kilobit per Second",s:"kbps",f:125},{n:"Megabit per Second",s:"Mbps",f:125000},{n:"Gigabit per Second",s:"Gbps",f:125000000},{n:"Terabit per Second",s:"Tbps",f:125000000000},{n:"Byte per Second",s:"B/s",f:1},{n:"Kilobyte per Second",s:"KB/s",f:1000},{n:"Megabyte per Second",s:"MB/s",f:1000000},{n:"Gigabyte per Second",s:"GB/s",f:1000000000}];
FAM_UNITS["illuminance"]=[{n:"Lux",s:"lx",f:1},{n:"Kilolux",s:"klx",f:1000},{n:"Millilux",s:"mlx",f:0.001},{n:"Foot-Candle",s:"fc",f:10.763910416709722},{n:"Phot",s:"ph",f:10000},{n:"Nox",s:"nx",f:0.001}];
FAM_UNITS["magnetic"]=[{n:"Tesla",s:"T",f:1},{n:"Millitesla",s:"mT",f:0.001},{n:"Microtesla",s:"µT",f:0.000001},{n:"Gauss",s:"G",f:0.0001},{n:"Milligauss",s:"mG",f:1e-7}];
FAM_UNITS["dose-equivalent"]=[{n:"Sievert",s:"Sv",f:1},{n:"Millisievert",s:"mSv",f:0.001},{n:"Microsievert",s:"µSv",f:0.000001},{n:"Rem",s:"rem",f:0.01},{n:"Millirem",s:"mrem",f:0.00001}];
FAM_UNITS["absorbed-dose"]=[{n:"Gray",s:"Gy",f:1},{n:"Milligray",s:"mGy",f:0.001},{n:"Kilogray",s:"kGy",f:1000},{n:"Rad",s:"rad",f:0.01},{n:"Millirad",s:"mrad",f:0.00001}];
FAM_UNITS["activity"]=[{n:"Becquerel",s:"Bq",f:1},{n:"Kilobecquerel",s:"kBq",f:1000},{n:"Megabecquerel",s:"MBq",f:1000000},{n:"Gigabecquerel",s:"GBq",f:1000000000},{n:"Curie",s:"Ci",f:37000000000},{n:"Millicurie",s:"mCi",f:37000000},{n:"Microcurie",s:"µCi",f:37000}];
FAM_UNITS["typography"]=[{n:"Point",s:"pt",f:0.00035277777777777776},{n:"Pica",s:"pc",f:0.004233333333333333},{n:"Inch",s:"in",f:0.0254},{n:"Pixel",s:"px",f:0.00026458333333333336},{n:"Twip",s:"twip",f:0.00001763888888888889}];
FAM_UNITS["capacitance"]=[{n:"Farad",s:"F",f:1},{n:"Millifarad",s:"mF",f:0.001},{n:"Microfarad",s:"µF",f:0.000001},{n:"Nanofarad",s:"nF",f:1e-9},{n:"Picofarad",s:"pF",f:1e-12}];
FAM_UNITS["inductance"]=[{n:"Henry",s:"H",f:1},{n:"Millihenry",s:"mH",f:0.001},{n:"Microhenry",s:"µH",f:0.000001}];
FAM_UNITS["charge"]=[{n:"Coulomb",s:"C",f:1},{n:"Millicoulomb",s:"mC",f:0.001},{n:"Microcoulomb",s:"µC",f:0.000001},{n:"Ampere-Hour",s:"Ah",f:3600},{n:"Milliampere-Hour",s:"mAh",f:3.6}];
FAM_UNITS["luminance"]=[{n:"Candela per Square Metre",s:"cd/m²",f:1},{n:"Nit",s:"nt",f:1},{n:"Stilb",s:"sb",f:10000},{n:"Lambert",s:"L",f:3183.098861837907},{n:"Foot-Lambert",s:"fL",f:3.4262590996353905},{n:"Apostilb",s:"asb",f:0.3183098861837907}];
FAM_UNITS["magnetic-flux"]=[{n:"Weber",s:"Wb",f:1},{n:"Milliweber",s:"mWb",f:0.001},{n:"Microweber",s:"µWb",f:0.000001},{n:"Maxwell",s:"Mx",f:1e-8},{n:"Tesla Square Metre",s:"T·m²",f:1}];
FAM_UNITS["electric-field"]=[{n:"Volt per Metre",s:"V/m",f:1},{n:"Kilovolt per Metre",s:"kV/m",f:1000},{n:"Volt per Centimetre",s:"V/cm",f:100},{n:"Millivolt per Metre",s:"mV/m",f:0.001},{n:"Statvolt per Centimetre",s:"statV/cm",f:29979.2458}];
FAM_UNITS["molar-concentration"]=[{n:"Mole per Litre",s:"mol/L",f:1},{n:"Millimole per Litre",s:"mmol/L",f:0.001},{n:"Micromole per Litre",s:"µmol/L",f:0.000001},{n:"Nanomole per Litre",s:"nmol/L",f:1e-9},{n:"Mole per Cubic Metre",s:"mol/m³",f:0.001}];
FAM_UNITS["mass-concentration"]=[{n:"Gram per Litre",s:"g/L",f:1},{n:"Milligram per Litre",s:"mg/L",f:0.001},{n:"Microgram per Litre",s:"µg/L",f:0.000001},{n:"Kilogram per Cubic Metre",s:"kg/m³",f:1},{n:"Pound per US Gallon",s:"lb/gal",f:119.82642731689666}];
FAM_UNITS["dynamic-viscosity"]=[{n:"Pascal-Second",s:"Pa·s",f:1},{n:"Millipascal-Second",s:"mPa·s",f:0.001},{n:"Poise",s:"P",f:0.1},{n:"Centipoise",s:"cP",f:0.001},{n:"Pound per Foot-Second",s:"lb/(ft·s)",f:1.488163943569554}];
FAM_UNITS["kinematic-viscosity"]=[{n:"Square Metre per Second",s:"m²/s",f:1},{n:"Square Centimetre per Second",s:"cm²/s",f:0.0001},{n:"Stokes",s:"St",f:0.0001},{n:"Centistokes",s:"cSt",f:0.000001},{n:"Square Foot per Second",s:"ft²/s",f:0.09290304}];
FAM_UNITS["acceleration"]=[{n:"Metre per Second Squared",s:"m/s²",f:1},{n:"Standard Gravity",s:"g",f:9.80665},{n:"Foot per Second Squared",s:"ft/s²",f:0.3048},{n:"Inch per Second Squared",s:"in/s²",f:0.0254},{n:"Gal",s:"Gal",f:0.01},{n:"Kilometre per Hour per Second",s:"km/h/s",f:0.2777777777777778}];
FAM_UNITS["angular-velocity"]=[{n:"Radian per Second",s:"rad/s",f:1},{n:"Revolution per Second",s:"rev/s",f:6.283185307179586},{n:"Revolution per Minute",s:"rev/min",f:0.10471975511965977},{n:"Degree per Second",s:"°/s",f:0.017453292519943295},{n:"Revolution per Day",s:"rev/d",f:0.0000727220521664304}];
FAM_UNITS["moment-of-inertia"]=[{n:"Kilogram Square Metre",s:"kg·m²",f:1},{n:"Gram Square Centimetre",s:"g·cm²",f:1e-7},{n:"Pound Square Foot",s:"lb·ft²",f:0.0421401100938048},{n:"Pound Square Inch",s:"lb·in²",f:0.0002926396534501608},{n:"Slug Square Foot",s:"slug·ft²",f:1.3558179618907014}];
FAM_UNITS["thermal-conductivity"]=[{n:"Watt per Metre-Kelvin",s:"W/(m·K)",f:1},{n:"Kilowatt per Metre-Kelvin",s:"kW/(m·K)",f:1000},{n:"BTU per Hour-Foot-Fahrenheit",s:"BTU/(h·ft·°F)",f:1.73073466637139},{n:"Calorie per Second-Centimetre-Celsius",s:"cal/(s·cm·°C)",f:418.68}];
FAM_UNITS["specific-heat"]=[{n:"Joule per Kilogram-Kelvin",s:"J/(kg·K)",f:1},{n:"Kilojoule per Kilogram-Kelvin",s:"kJ/(kg·K)",f:1000},{n:"Calorie per Gram-Celsius",s:"cal/(g·°C)",f:4186.8},{n:"BTU per Pound-Fahrenheit",s:"BTU/(lb·°F)",f:4186.8}];
FAM_UNITS["surface-tension"]=[{n:"Newton per Metre",s:"N/m",f:1},{n:"Millinewton per Metre",s:"mN/m",f:0.001},{n:"Dyne per Centimetre",s:"dyn/cm",f:0.001},{n:"Pound-Force per Foot",s:"lbf/ft",f:14.593902937206}];
FAM_UNITS["radiation-exposure"]=[{n:"Coulomb per Kilogram",s:"C/kg",f:1},{n:"Roentgen",s:"R",f:0.000258},{n:"Milliroentgen",s:"mR",f:2.58e-7}];
FAM_UNITS["heat-flux"]=[{n:"Watt per Square Metre",s:"W/m²",f:1},{n:"Kilowatt per Square Metre",s:"kW/m²",f:1000},{n:"BTU per Hour-Square Foot",s:"BTU/(h·ft²)",f:3.154590745},{n:"Calorie per Second-Square Centimetre",s:"cal/(s·cm²)",f:41868}];
FAM_UNITS["resistivity"]=[{n:"Ohm-Metre",s:"Ω·m",f:1},{n:"Ohm-Centimetre",s:"Ω·cm",f:0.01},{n:"Microohm-Metre",s:"µΩ·m",f:0.000001},{n:"Ohm-Inch",s:"Ω·in",f:0.0254},{n:"Circular Mil Ohm per Foot",s:"Ω·cmil/ft",f:1.6624261136597537e-8}];
FAM_UNITS["conductance"]=[{n:"Siemens",s:"S",f:1},{n:"Kilosiemens",s:"kS",f:1000},{n:"Millisiemens",s:"mS",f:0.001},{n:"Microsiemens",s:"µS",f:0.000001},{n:"Mho",s:"mho",f:1}];
FAM_UNITS["dose-rate"]=[{n:"Sievert per Hour",s:"Sv/h",f:1},{n:"Millisievert per Hour",s:"mSv/h",f:0.001},{n:"Microsievert per Hour",s:"µSv/h",f:0.000001},{n:"Rem per Hour",s:"rem/h",f:0.01},{n:"Sievert per Second",s:"Sv/s",f:3600}];
FAM_UNITS["wavenumber"]=[{n:"Inverse Metre",s:"m⁻¹",f:1},{n:"Inverse Centimetre",s:"cm⁻¹",f:100},{n:"Inverse Millimetre",s:"mm⁻¹",f:1000},{n:"Inverse Micrometre",s:"µm⁻¹",f:1000000},{n:"Inverse Nanometre",s:"nm⁻¹",f:1000000000}];
FAM_UNITS["area-density"]=[{n:"Gram per Square Metre",s:"gsm",f:1},{n:"Kilogram per Square Metre",s:"kg/m²",f:1000},{n:"Milligram per Square Centimetre",s:"mg/cm²",f:10},{n:"Pound per Square Foot",s:"lb/ft²",f:4882.427636383051},{n:"Ounce per Square Yard",s:"oz/yd²",f:33.905747474968756}];
FAM_UNITS["linear-density"]=[{n:"Tex",s:"tex",f:1},{n:"Decitex",s:"dtex",f:0.1},{n:"Denier",s:"den",f:0.1111111111111111},{n:"Kilotex",s:"ktex",f:1000},{n:"Grain per Yard",s:"gr/yd",f:70.859863}];
FAM_UNITS["magnetic-field-strength"]=[{n:"Ampere per Metre",s:"A/m",f:1},{n:"Kiloampere per Metre",s:"kA/m",f:1000},{n:"Milliampere per Metre",s:"mA/m",f:0.001},{n:"Oersted",s:"Oe",f:79.57747154594767}];
FAM_UNITS["specific-volume"]=[{n:"Cubic Metre per Kilogram",s:"m³/kg",f:1},{n:"Cubic Centimetre per Gram",s:"cm³/g",f:0.001},{n:"Litre per Kilogram",s:"L/kg",f:0.001},{n:"Cubic Foot per Pound",s:"ft³/lb",f:0.06242796057614471},{n:"US Gallon per Pound",s:"gal/lb",f:0.008345404452019296}];
FAM_UNITS["heat-capacity"]=[{n:"Joule per Kelvin",s:"J/K",f:1},{n:"Kilojoule per Kelvin",s:"kJ/K",f:1000},{n:"Calorie per Kelvin",s:"cal/K",f:4.184},{n:"Kilocalorie per Kelvin",s:"kcal/K",f:4184},{n:"BTU per Fahrenheit",s:"BTU/°F",f:1899.100534716}];
FAM_UNITS["electric-displacement"]=[{n:"Coulomb per Square Metre",s:"C/m²",f:1},{n:"Millicoulomb per Square Metre",s:"mC/m²",f:0.001},{n:"Microcoulomb per Square Metre",s:"µC/m²",f:0.000001},{n:"Coulomb per Square Centimetre",s:"C/cm²",f:10000},{n:"Microcoulomb per Square Centimetre",s:"µC/cm²",f:0.01}];

var FAM_EXTS={"freshBatch":{"length":{"millimetre":0,"centimetre":0,"metre":0,"kilometre":0,"inch":0,"foot":0,"yard":0,"mile":0,"nautical-mile":0,"fathom":0,"furlong":0,"light-year":0,"micrometre":1,"nanometre":1,"angstrom":1,"chain":1,"rod":1,"league":1,"astronomical-unit":1,"parsec":1,"planck-length":2,"bohr-radius":2,"cubit":2,"hand":2,"span":2,"digit":2,"barleycorn":2,"earth-radius":2,"lunar-distance":2,"light-minute":2,"light-hour":2,"solar-radius":2,"mil":3,"microinch":3,"point":3,"cable-length":3,"roman-mile":3,"verst":3,"arshin":3,"chinese-li":3,"japanese-ri":3,"stadion":3,"palm":3,"finger":3,"link":3,"ell":3,"pace":3,"light-second":3,"light-day":3,"megametre":3,"gigametre":3,"smoot":3,"kiloparsec":3,"megaparsec":3},"mass":{"milligram":0,"gram":0,"kilogram":0,"tonne":0,"ounce":0,"pound":0,"stone":0,"us-ton":0,"grain":0,"carat":0,"dram":0,"microgram":1,"troy-ounce":1,"troy-pound":1,"pennyweight":1,"uk-hundredweight":1,"us-hundredweight":1,"quarter":1,"tola":2,"uk-ton":2,"slug":2,"atomic-mass-unit":2,"electron-mass":2,"planck-mass":2,"earth-mass":2,"solar-mass":2,"quintal":3,"megatonne":3,"gigatonne":3,"nanogram":3,"picogram":3,"attogram":3,"baht":3,"tael":3,"jin":3,"masha":3,"ratti":3,"monme":3,"kwan":3,"shekel":3,"mina":3,"wey":3},"volume":{"millilitre":0,"litre":0,"cubic-metre":0,"us-teaspoon":0,"us-tablespoon":0,"us-fluid-ounce":0,"us-cup":0,"us-pint":0,"us-quart":0,"us-gallon":0,"uk-gallon":0,"cubic-inch":0,"uk-fluid-ounce":1,"uk-pint":1,"uk-quart":1,"cubic-foot":1,"cubic-yard":1,"board-foot":1,"acre-foot":1,"cubic-centimetre":2,"drop":2,"us-minim":2,"us-gill":2,"uk-gill":2,"us-peck":2,"us-bushel":2,"uk-bushel":2,"oil-barrel":2,"us-liquid-barrel":2,"hogshead":2,"cord":2,"cubic-kilometre":3,"cubic-millimetre":3,"cubic-decimetre":3,"microlitre":3,"nanolitre":3,"hectolitre":3,"decilitre":3,"centilitre":3,"uk-teaspoon":3,"uk-tablespoon":3,"dessertspoon":3,"metric-teaspoon":3,"acre-inch":3,"shot":3},"area":{"square-centimetre":0,"square-metre":0,"square-kilometre":0,"hectare":0,"acre":0,"square-inch":0,"square-foot":0,"square-yard":0,"square-mile":0,"marla":0,"kanal":0,"cent":0,"bigha":1,"guntha":1,"katha":1,"ground":1,"square-chain":1,"rood":1,"barn":1,"square-millimetre":2,"dunam":2,"township":2,"ankanam":2,"square-micrometre":3,"square-nanometre":3,"square-megametre":3,"circular-mil":3,"section":3,"square-perch":3,"square-link":3,"are":3,"centiare":3,"square-furlong":3,"tsubo":3,"arpent":3},"speed":{"metre-per-second":0,"kilometre-per-hour":0,"mile-per-hour":0,"knot":0,"foot-per-second":0,"centimetre-per-second":0,"mach":0,"speed-of-light":2,"speed-of-sound":2,"inch-per-second":2,"mile-per-minute":2,"kilometre-per-second":2,"metre-per-minute":2,"kilometre-per-minute":3,"kilometre-per-day":3,"mile-per-second":3,"foot-per-minute":3,"foot-per-hour":3,"inch-per-minute":3,"yard-per-second":3,"metre-per-hour":3},"pressure":{"pascal":0,"kilopascal":0,"megapascal":0,"bar":0,"atmosphere":0,"pound-per-square-inch":0,"millimetre-of-mercury":0,"inch-of-mercury":0,"torr":2,"millibar":2,"kilopound-per-square-inch":2,"inch-of-water":2,"centimetre-of-mercury":2,"barye":2,"technical-atmosphere":2,"gigapascal":3,"hectopascal":3,"decapascal":3,"pound-per-square-foot":3,"kip-per-square-foot":3,"ton-per-square-foot":3,"metre-of-water":3,"centimetre-of-water":3},"energy":{"joule":0,"kilojoule":0,"calorie":0,"kilocalorie":0,"watt-hour":0,"kilowatt-hour":0,"british-thermal-unit":0,"foot-pound":0,"electronvolt":0,"erg":2,"therm":2,"quad":2,"tonne-of-oil-equivalent":2,"megaelectronvolt":2,"hartree":2,"litre-atmosphere":2,"gigajoule":3,"megajoule":3,"microjoule":3,"nanojoule":3,"tonne-of-coal-equivalent":3,"million-btu":3,"rydberg":3,"celsius-heat-unit":3,"foot-poundal":3,"inch-pound-force":3},"power":{"watt":0,"kilowatt":0,"megawatt":0,"horsepower":0,"metric-horsepower":0,"btu-per-hour":0,"foot-pound-per-second":0,"gigawatt":2,"ton-of-refrigeration":2,"kilocalorie-per-hour":2,"erg-per-second":2,"boiler-horsepower":2,"terawatt":3,"petawatt":3,"milliwatt":3,"microwatt":3,"nanowatt":3,"pound-foot-per-minute":3,"btu-per-minute":3,"kilocalorie-per-minute":3},"time":{"millisecond":0,"second":0,"minute":0,"hour":0,"day":0,"week":0,"month-average":0,"year-365-25-days":0,"decade":0,"fortnight":2,"century":2,"millennium":2,"sidereal-day":2,"tropical-year":2,"shake":2,"planck-time":2,"microsecond":3,"nanosecond":3,"picosecond":3,"kilosecond":3,"megasecond":3,"gigasecond":3,"sidereal-year":3,"anomalistic-year":3,"lunar-month":3,"jiffy":3},"data":{"bit":0,"byte":0,"kilobyte":0,"megabyte":0,"gigabyte":0,"terabyte":0,"kibibyte":0,"mebibyte":0,"gibibyte":0,"nibble":2,"kilobit":2,"megabit":2,"gigabit":2,"terabit":2,"petabit":2,"petabyte":2,"exabyte":2,"pebibyte":2,"exbibyte":2,"zettabyte":3,"yottabyte":3,"zettabit":3,"yottabit":3,"zebibyte":3,"yobibyte":3,"kibibit":3,"mebibit":3,"gibibit":3,"tebibit":3,"word":3,"double-word":3,"quad-word":3},"angle":{"degree":0,"radian":0,"gradian":0,"turn":0,"arcminute":0,"arcsecond":0,"milliradian":2,"quadrant":2,"sextant":2,"sign":2,"point":2,"milliarcsecond":3,"microarcsecond":3,"binary-degree":3,"hour-angle":3,"octant":3,"nato-mil":3},"force":{"newton":0,"kilonewton":0,"dyne":0,"pound-force":0,"kilogram-force":0,"poundal":0,"kip":2,"ton-force":2,"ounce-force":2,"gram-force":2,"sthene":2,"meganewton":3,"millinewton":3,"micronewton":3,"nanonewton":3,"decanewton":3,"long-ton-force":3},"torque":{"newton-metre":0,"pound-foot":0,"pound-inch":0,"kilogram-metre":0,"ounce-inch":0,"newton-centimetre":2,"dyne-centimetre":2,"kilogram-centimetre":2,"kilonewton-metre":3,"meganewton-metre":3,"newton-millimetre":3,"gram-force-centimetre":3,"ounce-foot":3},"frequency":{"hertz":0,"kilohertz":0,"megahertz":0,"gigahertz":0,"terahertz":0,"revolutions-per-minute":0,"revolutions-per-second":2,"frames-per-second":2,"petahertz":3,"exahertz":3,"millihertz":3,"microhertz":3,"beat-per-minute":3},"density":{"kilogram-per-cubic-metre":0,"gram-per-cubic-centimetre":0,"gram-per-millilitre":0,"pound-per-cubic-foot":0,"pound-per-us-gallon":0,"gram-per-litre":2,"kilogram-per-litre":2,"ounce-per-cubic-inch":2,"pound-per-cubic-inch":2,"tonne-per-cubic-metre":2,"milligram-per-litre":3,"microgram-per-litre":3,"pound-per-cubic-yard":3,"ounce-per-us-gallon":3,"gram-per-cubic-metre":3,"slug-per-cubic-foot":3},"flow":{"litre-per-second":0,"litre-per-minute":0,"litre-per-hour":0,"cubic-metre-per-hour":0,"us-gallon-per-minute":0,"cubic-foot-per-second":0,"cubic-metre-per-second":2,"cubic-foot-per-minute":2,"uk-gallon-per-minute":2,"millilitre-per-second":2,"barrel-per-day":2,"cubic-inch-per-second":3,"cubic-yard-per-hour":3,"million-gallons-per-day":3,"us-gallon-per-day":3,"us-gallon-per-hour":3,"oil-barrel-per-hour":3},"voltage":{"millivolt":0,"volt":0,"kilovolt":0,"megavolt":0,"statvolt":2,"abvolt":2,"gigavolt":3,"nanovolt":3,"picovolt":3,"planck-voltage":3},"current":{"microampere":0,"milliampere":0,"ampere":0,"kiloampere":0,"statampere":2,"abampere":2,"megaampere":3,"nanoampere":3,"picoampere":3,"coulomb-per-second":3},"resistance":{"milliohm":0,"ohm":0,"kiloohm":0,"megaohm":0,"abohm":2,"statohm":2,"gigaohm":3,"microohm":3,"nanoohm":3,"picohm":3},"temperature":{"celsius":0,"fahrenheit":0,"kelvin":0},"fuel-economy":{"kilometres-per-litre":0,"litres-per-100-km":0,"miles-per-us-gallon":0,"miles-per-uk-gallon":0},"data-rate":{"bit-per-second":0,"kilobit-per-second":0,"megabit-per-second":0,"gigabit-per-second":0,"terabit-per-second":0,"byte-per-second":0,"kilobyte-per-second":0,"megabyte-per-second":0,"gigabyte-per-second":0},"illuminance":{"lux":0,"kilolux":0,"millilux":0,"foot-candle":0,"phot":0,"nox":0},"magnetic":{"tesla":0,"millitesla":0,"microtesla":0,"gauss":0,"milligauss":0},"dose-equivalent":{"sievert":0,"millisievert":0,"microsievert":0,"rem":0,"millirem":0},"absorbed-dose":{"gray":0,"milligray":0,"kilogray":0,"rad":0,"millirad":0},"activity":{"becquerel":0,"kilobecquerel":0,"megabecquerel":0,"gigabecquerel":0,"curie":0,"millicurie":0,"microcurie":0},"typography":{"point":0,"pica":0,"inch":0,"pixel":0,"twip":0},"capacitance":{"farad":0,"millifarad":0,"microfarad":0,"nanofarad":0,"picofarad":0},"inductance":{"henry":0,"millihenry":0,"microhenry":0},"charge":{"coulomb":0,"millicoulomb":0,"microcoulomb":0,"ampere-hour":0,"milliampere-hour":0},"luminance":{"candela-per-square-metre":0,"nit":0,"stilb":0,"lambert":0,"foot-lambert":0,"apostilb":0},"magnetic-flux":{"weber":0,"milliweber":0,"microweber":0,"maxwell":0,"tesla-square-metre":0},"electric-field":{"volt-per-metre":0,"kilovolt-per-metre":0,"volt-per-centimetre":0,"millivolt-per-metre":0,"statvolt-per-centimetre":0},"molar-concentration":{"mole-per-litre":0,"millimole-per-litre":0,"micromole-per-litre":0,"nanomole-per-litre":0,"mole-per-cubic-metre":0},"mass-concentration":{"gram-per-litre":0,"milligram-per-litre":0,"microgram-per-litre":0,"kilogram-per-cubic-metre":0,"pound-per-us-gallon":0},"dynamic-viscosity":{"pascal-second":0,"millipascal-second":0,"poise":0,"centipoise":0,"pound-per-foot-second":0},"kinematic-viscosity":{"square-metre-per-second":0,"square-centimetre-per-second":0,"stokes":0,"centistokes":0,"square-foot-per-second":0},"acceleration":{"metre-per-second-squared":0,"standard-gravity":0,"foot-per-second-squared":0,"inch-per-second-squared":0,"gal":0,"kilometre-per-hour-per-second":0},"angular-velocity":{"radian-per-second":0,"revolution-per-second":0,"revolution-per-minute":0,"degree-per-second":0,"revolution-per-day":0},"moment-of-inertia":{"kilogram-square-metre":0,"gram-square-centimetre":0,"pound-square-foot":0,"pound-square-inch":0,"slug-square-foot":0},"thermal-conductivity":{"watt-per-metre-kelvin":0,"kilowatt-per-metre-kelvin":0,"btu-per-hour-foot-fahrenheit":0,"calorie-per-second-centimetre-celsius":0},"specific-heat":{"joule-per-kilogram-kelvin":0,"kilojoule-per-kilogram-kelvin":0,"calorie-per-gram-celsius":0,"btu-per-pound-fahrenheit":0},"surface-tension":{"newton-per-metre":0,"millinewton-per-metre":0,"dyne-per-centimetre":0,"pound-force-per-foot":0},"radiation-exposure":{"coulomb-per-kilogram":0,"roentgen":0,"milliroentgen":0},"heat-flux":{"watt-per-square-metre":0,"kilowatt-per-square-metre":0,"btu-per-hour-square-foot":0,"calorie-per-second-square-centimetre":0},"resistivity":{"ohm-metre":0,"ohm-centimetre":0,"microohm-metre":0,"ohm-inch":0,"circular-mil-ohm-per-foot":0},"conductance":{"siemens":0,"kilosiemens":0,"millisiemens":0,"microsiemens":0,"mho":0},"dose-rate":{"sievert-per-hour":0,"millisievert-per-hour":0,"microsievert-per-hour":0,"rem-per-hour":0,"sievert-per-second":0},"wavenumber":{"inverse-metre":0,"inverse-centimetre":0,"inverse-millimetre":0,"inverse-micrometre":0,"inverse-nanometre":0},"area-density":{"gram-per-square-metre":0,"kilogram-per-square-metre":0,"milligram-per-square-centimetre":0,"pound-per-square-foot":0,"ounce-per-square-yard":0},"linear-density":{"tex":0,"decitex":0,"denier":0,"kilotex":0,"grain-per-yard":0},"magnetic-field-strength":{"ampere-per-metre":0,"kiloampere-per-metre":0,"milliampere-per-metre":0,"oersted":0},"specific-volume":{"cubic-metre-per-kilogram":0,"cubic-centimetre-per-gram":0,"litre-per-kilogram":0,"cubic-foot-per-pound":0,"us-gallon-per-pound":0},"heat-capacity":{"joule-per-kelvin":0,"kilojoule-per-kelvin":0,"calorie-per-kelvin":0,"kilocalorie-per-kelvin":0,"btu-per-fahrenheit":0},"electric-displacement":{"coulomb-per-square-metre":0,"millicoulomb-per-square-metre":0,"microcoulomb-per-square-metre":0,"coulomb-per-square-centimetre":0,"microcoulomb-per-square-centimetre":0}},"extMeta":{"length":[{"batch":1,"def":5,"note":"The newcomers: the ångström and nanometre are the units of atoms and chip-making; the chain and rod are the surveyor's old units (a cricket pitch is one chain); a league is roughly an hour's walk; the astronomical unit and parsec are how space is measured.","fresh":["micrometre","nanometre","angstrom","chain","rod","league","astronomical-unit","parsec"]},{"batch":2,"def":5,"note":"The newcomers span the whole scale of length: the Planck length and Bohr radius at the atomic end, the surveyor's and tailor's old units (cubit, hand, span, digit, barleycorn) in the middle, and the Earth radius, lunar distance, light-minute, light-hour and solar radius for space.","fresh":["planck-length","bohr-radius","cubit","hand","span","digit","barleycorn","earth-radius","lunar-distance","light-minute","light-hour","solar-radius"]},{"batch":3,"def":5,"note":"The newcomers complete the scale: microinches and mils for machining, points for print, the surveyor's link, the tailor's palm, finger, ell and pace, the sea's cable length, the Roman mile, verst and arshin, China's li and Japan's ri, the smoot of the Harvard bridge prank — and the astronomer's light-second, light-day, kiloparsec and megaparsec.","fresh":["mil","microinch","point","cable-length","roman-mile","verst","arshin","chinese-li","japanese-ri","stadion","palm","finger","link","ell","pace","light-second","light-day","megametre","gigametre","smoot","kiloparsec","megaparsec"]}],"mass":[{"batch":1,"def":10,"note":"The newcomers are the precious-metal and market weights: the troy ounce (31.1035 g) is how gold and silver are priced — heavier than the everyday ounce; the pennyweight is the jeweller's unit; hundredweights and the quarter survive in UK and US wholesale trade.","fresh":["microgram","troy-ounce","troy-pound","pennyweight","uk-hundredweight","us-hundredweight","quarter"]},{"batch":2,"def":10,"note":"The newcomers: the tola of South Asian gold trade (11.6638 g), the UK long ton, the slug of imperial engineering, and the masses of physics — the atomic mass unit, the electron, and the Earth and Sun themselves.","fresh":["tola","uk-ton","slug","atomic-mass-unit","electron-mass","planck-mass","earth-mass","solar-mass"]},{"batch":3,"def":10,"note":"The newcomers: the quintal of grain trade, megatonnes and gigatonnes for emissions and industry, the nanogram-to-attogram ladder for laboratories, and the market weights of Asia — Thailand's baht, the Hong Kong tael, China's jin, India's masha and ratti, Japan's monme and kwan — plus the ancient shekel and mina and the English wey.","fresh":["quintal","megatonne","gigatonne","nanogram","picogram","attogram","baht","tael","jin","masha","ratti","monme","kwan","shekel","mina","wey"]}],"volume":[{"batch":1,"def":2,"note":"The newcomers are the imperial and bulk measures: UK pints and gallons are about 20% larger than US ones (the classic transatlantic trap), the cubic foot and yard are how concrete and soil are sold, a board foot is the lumber trade's unit, and an acre-foot is how reservoirs are counted.","fresh":["uk-fluid-ounce","uk-pint","uk-quart","cubic-foot","cubic-yard","board-foot","acre-foot"]},{"batch":2,"def":2,"note":"The newcomers are the apothecary's and the farm's measures: drops and minims for medicine, gills, pecks and bushels for grain, the oil barrel (exactly 42 US gallons), the hogshead, and the cord of firewood.","fresh":["cubic-centimetre","drop","us-minim","us-gill","uk-gill","us-peck","us-bushel","uk-bushel","oil-barrel","us-liquid-barrel","hogshead","cord"]},{"batch":3,"def":2,"note":"The newcomers: the cubic kilometre of reservoirs and ice caps, microlitres and nanolitres for laboratory work, hectolitres for brewing and wine, the UK teaspoon and tablespoon (bigger than the US ones — a classic recipe trap), the dessertspoon, the metric teaspoon, the acre-inch of irrigation, and the shot.","fresh":["cubic-kilometre","cubic-millimetre","cubic-decimetre","microlitre","nanolitre","hectolitre","decilitre","centilitre","uk-teaspoon","uk-tablespoon","dessertspoon","metric-teaspoon","acre-inch","shot"]}],"area":[{"batch":1,"def":100,"note":"The newcomers are the land units people actually buy and sell in: the bigha, katha and guntha of South Asia (sizes vary by district — the standard values are used here and the tool says so), the South Indian ground, and the surveyor's square chain and rood.","fresh":["bigha","guntha","katha","ground","square-chain","rood","barn"]},{"batch":2,"def":100,"note":"The newcomers: the square millimetre for small work, the dunam of the Middle East (exactly 1,000 m²), the US survey township (36 square miles), and the ankanam of Andhra Pradesh and Telangana (72 square feet).","fresh":["square-millimetre","dunam","township","ankanam"]},{"batch":3,"def":100,"note":"The newcomers: square micro- and nanometres for chips and cells, the circular mil of wire sizing, the US section (a square mile of survey grid), perch and link from the surveyor's chain, the metric are and centiare, the square furlong, Japan's tsubo (the unit flats are let by) and the French arpent.","fresh":["square-micrometre","square-nanometre","square-megametre","circular-mil","section","square-perch","square-link","are","centiare","square-furlong","tsubo","arpent"]}],"speed":[{"batch":2,"def":60,"note":"Mach in this library uses the sea-level standard (340.29 m/s). The newcomers add the two speeds everything is compared against — light (exact, 299,792,458 m/s) and sound in air at 20 °C (about 343 m/s) — plus workshop and road units.","fresh":["speed-of-light","speed-of-sound","inch-per-second","mile-per-minute","kilometre-per-second","metre-per-minute"]},{"batch":3,"def":60,"note":"The newcomers fill the slow and the fast ends: metres per hour and feet per hour for creep and conveyor work, feet and inches per minute for machining feeds, kilometres per minute and per day, yards per second — and the mile per second that orbital mechanics lives in.","fresh":["kilometre-per-minute","kilometre-per-day","mile-per-second","foot-per-minute","foot-per-hour","inch-per-minute","yard-per-second","metre-per-hour"]}],"pressure":[{"batch":2,"def":1,"note":"The newcomers: the torr (a millimetre of mercury by another name), the millibar of weather maps (the same as a hectopascal), ksi for structural steel, inches of water for ventilation, and the barye and technical atmosphere of older engineering.","fresh":["torr","millibar","kilopound-per-square-inch","inch-of-water","centimetre-of-mercury","barye","technical-atmosphere"]},{"batch":3,"def":1,"note":"The newcomers: the gigapascal of materials science, the hectopascal of weather reports (the same as the millibar), pounds and kips per square foot for floor loads and foundations, and metres and centimetres of water — how fans, pumps and medical pressures are still quoted.","fresh":["gigapascal","hectopascal","decapascal","pound-per-square-foot","kip-per-square-foot","ton-per-square-foot","metre-of-water","centimetre-of-water"]}],"energy":[{"batch":2,"def":100,"note":"The newcomers run from the erg and the Hartree at atomic scale up to the therm, the tonne of oil equivalent and the quad — the unit national energy statistics are written in (1 quad ≈ a quadrillion BTU).","fresh":["erg","therm","quad","tonne-of-oil-equivalent","megaelectronvolt","hartree","litre-atmosphere"]},{"batch":3,"def":100,"note":"The newcomers: megajoules and gigajoules for industry, micro- and nanojoules for sensors and physics, the tonne of coal equivalent and million BTU of energy statistics, the Rydberg of atomic spectra, the Celsius heat unit, and the foot-poundal and inch-pound of older engineering.","fresh":["gigajoule","megajoule","microjoule","nanojoule","tonne-of-coal-equivalent","million-btu","rydberg","celsius-heat-unit","foot-poundal","inch-pound-force"]}],"power":[{"batch":2,"def":1,"note":"The newcomers: the gigawatt of power stations, the ton of refrigeration (the heat a ton of melting ice absorbs — how air conditioners are sized), and boiler horsepower from the steam age.","fresh":["gigawatt","ton-of-refrigeration","kilocalorie-per-hour","erg-per-second","boiler-horsepower"]},{"batch":3,"def":1,"note":"The newcomers: terawatts and petawatts for grids and lasers, the milli-to-nano ladder for electronics, pound-feet per minute from older shaft ratings, and BTU and kilocalories per minute from heating and exercise equipment.","fresh":["terawatt","petawatt","milliwatt","microwatt","nanowatt","pound-foot-per-minute","btu-per-minute","kilocalorie-per-minute"]}],"time":[{"batch":2,"def":90,"note":"The newcomers: the fortnight, century and millennium of everyday speech, the sidereal day (Earth's true spin, 23 h 56 m), the tropical year (the season cycle the calendar chases), the physicist's shake, and the Planck time — the smallest interval physics can describe.","fresh":["fortnight","century","millennium","sidereal-day","tropical-year","shake","planck-time"]},{"batch":3,"def":90,"note":"The newcomers: the micro-to-picosecond ladder of electronics, kilo-, mega- and gigaseconds, the sidereal and anomalistic years astronomers actually use (both differ slightly from the calendar year), the lunar month of tides and calendars, and the jiffy — a real unit: one cycle of mains electricity.","fresh":["microsecond","nanosecond","picosecond","kilosecond","megasecond","gigasecond","sidereal-year","anomalistic-year","lunar-month","jiffy"]}],"data":[{"batch":2,"def":500,"note":"The newcomers complete both ladders: bits up to petabits for networks, and bytes up to exabytes — plus the binary pebibyte and exbibyte, and the nibble (half a byte, one hex digit). Decimal units are powers of 1000; the -bi- units are powers of 1024.","fresh":["nibble","kilobit","megabit","gigabit","terabit","petabit","petabyte","exabyte","pebibyte","exbibyte"]},{"batch":3,"def":500,"note":"The newcomers complete both ladders to the top: zettabytes and yottabytes and their binary twins the zebibyte and yobibyte, the bit-level units networks quote (kibibits to tebibits), and the machine words — a word is 2 bytes, a double word 4, a quad word 8. Decimal units are powers of 1000; the -bi- units are powers of 1024.","fresh":["zettabyte","yottabyte","zettabit","yottabit","zebibyte","yobibyte","kibibit","mebibit","gibibit","tebibit","word","double-word","quad-word"]}],"angle":[{"batch":2,"def":180,"note":"The newcomers are the surveyor's and navigator's slices of a turn: the quadrant (a right angle), the sextant and the sign of the zodiac, the compass point (11.25° — 'north-north-east' is two points from north), and the milliradian of optics and artillery.","fresh":["milliradian","quadrant","sextant","sign","point"]},{"batch":3,"def":180,"note":"The newcomers: milli- and microarcseconds (how telescopes and Gaia measure the sky), the binary degree of computing (256 to a turn), the hour angle of astronomy (the sky turns 15° an hour), the octant (an eighth of a turn), and the NATO mil — 6,400 to a turn, the artillery unit.","fresh":["milliarcsecond","microarcsecond","binary-degree","hour-angle","octant","nato-mil"]}],"force":[{"batch":2,"def":100,"note":"The newcomers: the kip (a kilopound — how US structural loads are quoted), the ton-force, and the gram-force and ounce-force of small mechanisms and springs.","fresh":["kip","ton-force","ounce-force","gram-force","sthene"]},{"batch":3,"def":100,"note":"The newcomers: the meganewton of rockets and cranes, the milli-to-nano ladder of precision instruments and micro-robotics, the decanewton of climbing and rigging ratings, and the long ton-force of British engineering.","fresh":["meganewton","millinewton","micronewton","nanonewton","decanewton","long-ton-force"]}],"torque":[{"batch":2,"def":50,"note":"The newcomers are the small-torque units: newton-centimetres for electronics and bikes, kilogram-centimetres on Asian spec sheets, and the dyne-centimetre of laboratory instruments.","fresh":["newton-centimetre","dyne-centimetre","kilogram-centimetre"]},{"batch":3,"def":50,"note":"The newcomers: kilonewton- and meganewton-metres for turbines and ship shafts, newton-millimetres and gram-force centimetres for model motors and instruments, and the ounce-foot of small mechanisms.","fresh":["kilonewton-metre","meganewton-metre","newton-millimetre","gram-force-centimetre","ounce-foot"]}],"frequency":[{"batch":2,"def":60,"note":"The newcomers count the same cycles in different clothes: revolutions per second is the hertz by definition, and frames per second is how film and games quote the same rate.","fresh":["revolutions-per-second","frames-per-second"]},{"batch":3,"def":60,"note":"The newcomers: petahertz and exahertz (where light itself oscillates), milli- and microhertz for the slowest cycles in geophysics, and the beat per minute — a frequency, exactly one sixtieth of a hertz each.","fresh":["petahertz","exahertz","millihertz","microhertz","beat-per-minute"]}],"density":[{"batch":2,"def":1,"note":"The newcomers are the lab and workshop forms: grams per litre (the same number as kg/m³), kilograms per litre, and the per-cubic-inch densities machinists use — steel is about 0.284 lb/in³.","fresh":["gram-per-litre","kilogram-per-litre","ounce-per-cubic-inch","pound-per-cubic-inch","tonne-per-cubic-metre"]},{"batch":3,"def":1,"note":"The newcomers: milligrams and micrograms per litre (how water quality is reported), pounds per cubic yard for aggregates and soil, ounces per US gallon, grams per cubic metre for air and gases, and slugs per cubic foot from imperial engineering.","fresh":["milligram-per-litre","microgram-per-litre","pound-per-cubic-yard","ounce-per-us-gallon","gram-per-cubic-metre","slug-per-cubic-foot"]}],"flow":[{"batch":2,"def":10,"note":"The newcomers: the cubic metre per second of rivers and flood reports, cubic feet per minute (cfm — how fans and HVAC are rated), UK gallons per minute, millilitres per second for lab pumps, and barrels per day from oil fields.","fresh":["cubic-metre-per-second","cubic-foot-per-minute","uk-gallon-per-minute","millilitre-per-second","barrel-per-day"]},{"batch":3,"def":10,"note":"The newcomers: cubic inches per second and cubic yards per hour for pumps and concrete, the million gallons per day that water utilities plan in, US gallons per day and per hour for wells and filters, and barrels per hour from the oil field.","fresh":["cubic-inch-per-second","cubic-yard-per-hour","million-gallons-per-day","us-gallon-per-day","us-gallon-per-hour","oil-barrel-per-hour"]}],"voltage":[{"batch":2,"def":230,"note":"The newcomers are the cgs units still found in older physics texts: the statvolt (about 300 V) and the abvolt (a hundred-millionth of a volt).","fresh":["statvolt","abvolt"]},{"batch":3,"def":230,"note":"The newcomers: the gigavolt of cosmic rays and the largest accelerators, nanovolts and picovolts at the limit of measurement, and the Planck voltage — the voltage scale of quantum gravity, about 10²⁷ volts.","fresh":["gigavolt","nanovolt","picovolt","planck-voltage"]}],"current":[{"batch":2,"def":5,"note":"The newcomers are the cgs units: the abampere (exactly 10 A) and the statampere, tiny enough for electrostatics.","fresh":["statampere","abampere"]},{"batch":3,"def":5,"note":"The newcomers: the megaampere of lightning and fusion experiments, nanoamperes and picoamperes at the edge of what instruments can sense, and the coulomb per second — the ampere's own definition, one coulomb flowing past a point each second.","fresh":["megaampere","nanoampere","picoampere","coulomb-per-second"]}],"resistance":[{"batch":2,"def":100,"note":"The newcomers are the cgs extremes: the abohm (a nanoohm — a short piece of wire) and the statohm (nearly a trillion ohms — an insulator's territory).","fresh":["abohm","statohm"]},{"batch":3,"def":100,"note":"The newcomers: the gigaohm of high-voltage insulation, and the micro-, nano- and picohm of precision shunts and superconductor research.","fresh":["gigaohm","microohm","nanoohm","picohm"]}],"temperature":[],"fuel-economy":[],"data-rate":[],"illuminance":[],"magnetic":[],"dose-equivalent":[],"absorbed-dose":[],"activity":[],"typography":[],"capacitance":[],"inductance":[],"charge":[],"luminance":[],"magnetic-flux":[],"electric-field":[],"molar-concentration":[],"mass-concentration":[],"dynamic-viscosity":[],"kinematic-viscosity":[],"acceleration":[],"angular-velocity":[],"moment-of-inertia":[],"thermal-conductivity":[],"specific-heat":[],"surface-tension":[],"radiation-exposure":[],"heat-flux":[],"resistivity":[],"conductance":[],"dose-rate":[],"wavenumber":[],"area-density":[],"linear-density":[],"magnetic-field-strength":[],"specific-volume":[],"heat-capacity":[],"electric-displacement":[]}};

function resolveConv(id){
  var rest=id.slice(5), best=null;
  for(var i=0;i<FAMS.length;i++){ var k=FAMS[i].key; if(rest.indexOf(k+'-')===0 && (!best || k.length>best.key.length)) best=FAMS[i]; }
  if(!best) return null;
  var mid=rest.slice(best.key.length+1), ti=mid.indexOf('-to-');
  if(ti<0) return null;
  var sa=mid.slice(0,ti), sb=mid.slice(ti+4);
  var units=FAM_UNITS[best.key], a=null, b=null;
  for(var j=0;j<units.length;j++){ if(slug(units[j].n)===sa) a=units[j]; if(slug(units[j].n)===sb) b=units[j]; }
  if(!a||!b) return null;
  var fam=best, cb=0, fx=FAM_EXTS.freshBatch[best.key];
  if(fx){ cb=Math.max(fx[sa]||0, fx[sb]||0); }
  if(cb>0){
    var exts=FAM_EXTS.extMeta[best.key]||[];
    for(var e=0;e<exts.length;e++){ if(exts[e].batch===cb){ fam={key:best.key, base:best.base, def:exts[e].def, note:exts[e].note}; break; } }
  }
  var toBase=a.to?a.to:function(x){ return x*a.f; };
  var fromBase=b.from?b.from:function(x){ return x/b.f; };
  var factor=(a.f&&b.f)?a.f/b.f:null;
  return {fam:fam, a:a, b:b, toBase:toBase, fromBase:fromBase, factor:factor};
}
var CONVD_DATA={"speed-conv":{"units":{"m/s":{"f":1,"t":"Metres per second"},"km/h":{"f":0.277778,"t":"Kilometres per hour"},"mph":{"f":0.44704,"t":"Miles per hour"},"ft/s":{"f":0.3048,"t":"Feet per second"},"knots":{"f":0.514444,"t":"Knots"}},"defFrom":"km/h","defVal":100,"noteText":"The knot is one nautical mile per hour, still the standard at sea and in aviation. Highway limits: 100 km/h ≈ 62 mph."},"data-conv":{"units":{"bit":{"f":0.125,"t":"Bits"},"B":{"f":1,"t":"Bytes"},"KB":{"f":1024,"t":"Kibibytes (1024 B)"},"MB":{"f":1048576,"t":"Mebibytes (1024 KB)"},"GB":{"f":1073741824,"t":"Gibibytes (1024 MB)"},"TB":{"f":1099511627776,"t":"Tebibytes (1024 GB)"}},"defFrom":"MB","defVal":500,"noteText":"Computers count in 1024s (binary); disk and network marketing counts in 1000s (SI) — which is why a “500 GB” drive shows about 465 GiB in your operating system."},"pressure-conv":{"units":{"Pa":{"f":1,"t":"Pascals"},"kPa":{"f":1000,"t":"Kilopascals"},"bar":{"f":100000,"t":"Bar"},"psi":{"f":6894.757,"t":"Pounds per square inch"},"atm":{"f":101325,"t":"Atmospheres"},"mmHg":{"f":133.3224,"t":"Millimetres of mercury"}},"defFrom":"psi","defVal":32,"noteText":"Car tyres live around 30–35 psi (about 2.2 bar); sea-level air pressure is 1 atm = 101,325 Pa = 760 mmHg."},"energy-conv":{"units":{"J":{"f":1,"t":"Joules"},"kJ":{"f":1000,"t":"Kilojoules"},"cal":{"f":4.184,"t":"Calories (small)"},"kcal":{"f":4184,"t":"Kilocalories (food calories)"},"kWh":{"f":3600000,"t":"Kilowatt-hours"},"BTU":{"f":1055.056,"t":"British thermal units"},"ft-lb":{"f":1.355818,"t":"Foot-pounds"}},"defFrom":"kcal","defVal":500,"noteText":"Food “Calories” are kilocalories. One kWh — one unit on an electricity bill — is 3.6 million joules, or about 860 kcal."},"angle-conv":{"units":{"deg":{"f":1,"t":"Degrees"},"rad":{"f":57.29578,"t":"Radians"},"grad":{"f":0.9,"t":"Gradians"},"turn":{"f":360,"t":"Full turns"},"arcmin":{"f":0.016666666666666666,"t":"Arcminutes"},"arcsec":{"f":0.0002777777777777778,"t":"Arcseconds"}},"defFrom":"deg","defVal":180,"noteText":"Radians are the mathematician’s unit: a full turn is 2π rad, and π rad is exactly 180°. Gradians (400 per turn) survive in surveying."},"time-conv":{"units":{"s":{"f":1,"t":"Seconds"},"min":{"f":60,"t":"Minutes"},"h":{"f":3600,"t":"Hours"},"day":{"f":86400,"t":"Days"},"week":{"f":604800,"t":"Weeks"},"year":{"f":31557600,"t":"Years (365.25 days)"}},"defFrom":"h","defVal":24,"noteText":"A year here is 365.25 days — the Julian year, which accounts for leap years. A million seconds is about 11.6 days; a billion seconds is about 31.7 years."},"power-conv":{"units":{"W":{"f":1,"t":"Watts"},"kW":{"f":1000,"t":"Kilowatts"},"hp":{"f":745.7,"t":"Horsepower (mechanical)"},"PS":{"f":735.5,"t":"Metric horsepower (PS)"},"BTU/h":{"f":0.293071,"t":"BTU per hour"}},"defFrom":"hp","defVal":100,"noteText":"One mechanical horsepower is 745.7 W — James Watt’s marketing figure for his steam engines. A human sustains roughly 75–100 W; a kettle uses 2,000–3,000 W."},"viscosity-conv":{"units":{"cP":{"f":1,"t":"Centipoise (cP)"},"Pa·s":{"f":1000,"t":"Pascal-second (Pa·s)"},"mPa·s":{"f":1,"t":"Millipascal-second (mPa·s)"},"P":{"f":100,"t":"Poise (P)"},"cSt":{"f":1,"t":"Centistokes (cSt) — equals cP only at density 1.0 g/ml"},"xWater":{"f":1.002,"t":"× the viscosity of water at 20 °C"}},"defFrom":"cP","defVal":1,"noteText":"Dynamic viscosity converts exactly between cP, mPa·s, Pa·s and poise (1 cP = 1 mPa·s). Kinematic viscosity (cSt) needs the fluid's density: cSt = cP ÷ density in g/ml — the cSt row here assumes density 1.0 (water-like fluids); for a light oil at 0.87 g/ml, divide the cP figure by 0.87 instead. Landmarks: water 1 cP · olive oil ≈ 56 · honey ≈ 10,000 · blood ≈ 3–4."},"magnetic-conv":{"units":{"T":{"f":1,"t":"Tesla (T)"},"mT":{"f":0.001,"t":"Millitesla (mT)"},"µT":{"f":0.000001,"t":"Microtesla (µT)"},"G":{"f":0.0001,"t":"Gauss (G)"},"A/m":{"f":0.0000012566370614,"t":"Amps per metre (A/m) — as B in free space"},"Oe":{"f":0.0001,"t":"Oersted (Oe) — as B in free space"}},"defFrom":"T","defVal":0.00005,"noteText":"In free space, B and H units interconvert exactly: 1 T = 10,000 gauss, and 1 Oe corresponds to 1 gauss in vacuum (an H of 79.577 A/m). Earth's field is about 25–65 µT depending on location; a fridge magnet is ~5 mT at its surface; an MRI runs 1.5–3 T."},"data-rate":{"units":{"Mbps":{"f":1,"t":"Megabits per second (Mbps)"},"MB/s":{"f":8,"t":"Megabytes per second (MB/s)"},"Gbps":{"f":1000,"t":"Gigabits per second (Gbps)"},"Kbps":{"f":0.001,"t":"Kilobits per second (Kbps)"}},"defFrom":"Mbps","defVal":100,"noteText":"The trap this converter exists for: internet speeds are sold in megaBITS, files are measured in megaBYTES — divide by 8. So 100 Mbps downloads at most 12.5 MB/s, and a 1 GB file (8,000 megabits) takes about 80 seconds at full speed."}};

function resolveConvD(id){
  var d=CONVD_DATA[id]; if(!d) return null;
  return {units:d.units, keys:Object.keys(d.units), noteText:d.noteText};
}
var B5CONV_DATA={"mass-conv":{"units":[["g","Grams",1],["kg","Kilograms",1000],["oz","Ounces",28.349523125],["lb","Pounds",453.59237],["stone","Stone",6350.29318],["tonne","Tonnes (metric)",1000000],["uston","US tons",907184.74]],"defFrom":"stone","defTo":"kg","defVal":1,"unitWord":"kilograms"},"length-conv":{"units":[["mm","Millimetres",0.001],["cm","Centimetres",0.01],["m","Metres",1],["km","Kilometres",1000],["in","Inches",0.0254],["ft","Feet",0.3048],["yd","Yards",0.9144],["mi","Miles",1609.344],["nmi","Nautical miles",1852]],"defFrom":"mi","defTo":"km","defVal":1,"unitWord":"kilometres"},"torque-conv":{"units":[["Nm","Newton-metres",1],["lbft","Pound-feet",1.35582],["lbin","Pound-inches",0.112985],["kgm","Kilogram-metres",9.80665]],"defFrom":"Nm","defTo":"lbft","defVal":100,"unitWord":"pound-feet"},"frequency-conv":{"units":[["Hz","Hertz",1],["kHz","Kilohertz",1000],["MHz","Megahertz",1000000],["GHz","Gigahertz",1000000000],["rpm","Revolutions per minute",0.016666666666666666]],"defFrom":"Hz","defTo":"rpm","defVal":60,"unitWord":"revolutions per minute"}};

function resolveB5Conv(id){
  var d=B5CONV_DATA[id]; if(!d) return null;
  return {units:d.units, unitWord:d.unitWord};
}