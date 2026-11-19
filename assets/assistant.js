/* FreeCalcNow assistant — rule-based, context-aware, runs 100% in the browser.
   Knows the current page/tool (window.FCN_PAGE), solves sums, converts units,
   finds tools, explains the current result, and guides the user. No server, no cost. */
(function(){
  "use strict";
  var PAGE = window.FCN_PAGE || {toolId:null, toolName:null, category:null, slug:""};
  var INDEX = null, INDEX_LOADING = null;
  function el(html){ var d=document.createElement("div"); d.innerHTML=html.trim(); return d.firstChild; }
  function esc(s){ return String(s==null?"":s).replace(/[&<>\"']/g,function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
  function loadIndex(){
    if(INDEX) return Promise.resolve(INDEX);
    if(INDEX_LOADING) return INDEX_LOADING;
    try{
      if(typeof fetch==="undefined") throw new Error("no fetch");
      INDEX_LOADING = fetch("/assets/tools-index.json").then(function(r){ return r.json(); }).then(function(j){ INDEX=j; return j; }).catch(function(){ INDEX=[]; return INDEX; });
    }catch(e){ INDEX=[]; INDEX_LOADING=Promise.resolve(INDEX); }
    return INDEX_LOADING;
  }
  function searchTools(q, n){
    n = n || 3;
    if(!INDEX || !INDEX.length) return [];
    var words = q.toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return w.length>2; });
    if(!words.length) return [];
    var scored = INDEX.map(function(t){
      var hay=(t.name+" "+(t.blurb||"")+" "+t.cat).toLowerCase(), s=0;
      words.forEach(function(w){ if(t.name.toLowerCase().indexOf(w)>=0) s+=3; else if(hay.indexOf(w)>=0) s+=1; });
      return {t:t, s:s};
    }).filter(function(x){ return x.s>0; }).sort(function(a,b){ return b.s-a.s; });
    return scored.slice(0,n).map(function(x){ return x.t; });
  }
  /* ---------- sums ---------- */
  function trySum(q){
    var m;
    // "15% of 240", "what is 20% of 500"
    m = q.match(/(-?[\d.,]+)\s*%\s*of\s*(-?[\d.,]+)/);
    if(m){ var p=parseFloat(m[1].replace(/,/g,"")), v=parseFloat(m[2].replace(/,/g,"")); if(isFinite(p)&&isFinite(v)) return {text: p+"% of "+fmtN(v)+" = "+fmtN(v*p/100)+".", done:true}; }
    // "240 + 15%" style: value plus percent
    m = q.match(/(-?[\d.,]+)\s*([+\-*/x×÷])\s*(-?[\d.,]+)\s*%?$/);
    if(m && /[\d]/.test(q)){
      var a=parseFloat(m[1].replace(/,/g,"")), b=parseFloat(m[3].replace(/,/g,"")), op=m[2];
      if(isFinite(a)&&isFinite(b)){
        var r = op==="+"?a+b : op==="-"?a-b : (op==="*"||op==="x"||op==="×")?a*b : (op==="/"||op==="÷")? (b===0?null:a/b) : null;
        if(r!==null && isFinite(r)) return {text: fmtN(a)+" "+op+" "+fmtN(b)+" = "+fmtN(r)+".", done:true};
        if(r===null) return {text:"I can't divide by zero.", done:true};
      }
    }
    return null;
  }
  function fmtN(x){
    if(!isFinite(x)) return "—";
    return Number(x).toLocaleString("en-US",{maximumFractionDigits:4});
  }
  /* ---------- conversions ---------- */
  var ALIASES = {mile:["mile","miles","mi"], kilometre:["kilometre","kilometer","kilometres","kilometers","km"], centimetre:["centimetre","centimeter","centimetres","centimeters","cm"], inch:["inch","inches","in"], kilogram:["kilogram","kilograms","kg","kilo","kilos"], pound:["pound","pounds","lb","lbs"], gram:["gram","grams","g"], litre:["litre","liter","litres","liters","l"], gallon:["gallon","gallons","gal"], metre:["metre","meter","metres","meters","m"], foot:["foot","feet","ft"], yard:["yard","yards","yd"], ounce:["ounce","ounces","oz"], celsius:["celsius","c","°c"], fahrenheit:["fahrenheit","f","°f"], hour:["hour","hours","hr","hrs"], minute:["minute","minutes","min"], second:["second","seconds","sec","s"], day:["day","days"], week:["week","weeks"], month:["month","months"], year:["year","years"], dollar:["dollar","dollars","usd","$"], euro:["euro","euros","eur","€"], poundsterling:["pound sterling","gbp","£"]};
  function unitName(word){
    word=(word||"").toLowerCase();
    for(var k in ALIASES){ if(ALIASES[k].indexOf(word)>=0) return k; }
    return word;
  }
  function tryConvert(q){
    var m = q.match(/(-?[\d.,]+)\s*([a-z°%$€£]+)\s*(?:to|in|as|=)\s*([a-z°%$€£]+)/);
    if(!m) return null;
    var val=parseFloat(m[1].replace(/,/g,"")), from=unitName(m[2]), to=unitName(m[3]);
    if(!isFinite(val)) return null;
    if(typeof resolveConv!=="function") return {text:"Conversions load with the page engine — please try again in a moment.", done:true};
    // find converter tool by unit names
    var tools = INDEX || [];
    var cand = tools.filter(function(t){ return t.id.indexOf("conv-")===0; });
    var hit = null;
    cand.forEach(function(t){
      var name=t.name.toLowerCase();
      // direction matters: "Miles to Kilometres" converts miles→km, not the reverse
      var fi=name.indexOf(from), ti=name.indexOf(to);
      if(fi>=0 && ti>=0 && fi<ti && name.indexOf(" to ")>=0 && !hit) hit=t;
    });
    if(!hit) cand.forEach(function(t){
      var name=t.name.toLowerCase();
      if(name.indexOf(from)>=0 && name.indexOf(to)>=0 && !hit) hit=t;
    });
    if(!hit) return {text:"I couldn't find a "+from+" to "+to+" converter here. Try naming the units differently, or open the Conversion category.", done:true};
    var r = resolveConv(hit.id);
    if(!r) return {text:"I couldn't run that conversion.", done:true};
    var out = r.fromBase(r.toBase(val));
    var big = (window.fmtV? fmtV(out) : fmtN(out));
    return {text: fmtN(val)+" "+from+" = "+big+" "+to+".", done:true, link:hit};
  }
  /* ---------- answers ---------- */
  function toolLink(t){ return '<a href="/'+t.id+'/">'+esc(t.name)+'</a>'; }
  function answer(q){
    var ql=q.toLowerCase().trim();
    // explain current result
    if(/explain|what does this mean|what is this result|my result/.test(ql) && PAGE.toolId){
      var big=document.querySelector("#result-big"), sub=document.querySelector("#result-sub"), formula=document.querySelector(".formula");
      var txt="You are using the "+PAGE.toolName+".";
      if(big && big.textContent.trim()) txt+="\n\nYour current answer is "+big.textContent.trim()+".";
      if(sub && sub.textContent.trim()) txt+="\n"+sub.textContent.trim();
      if(formula) txt+="\n\nThe formula is: "+formula.textContent.trim();
      txt+="\n\nChange any number above and the answer updates instantly.";
      return {text:txt, done:true};
    }
    // sums first
    var s=trySum(ql); if(s) return s;
    // conversions
    if(/ to | in |convert/.test(ql)){ var c=tryConvert(ql); if(c) return c; }
    // what is this tool / how to use
    if(/how (do i|to) use|how does this work|what (is|does) this/.test(ql) && PAGE.toolId){
      return {text:"This is the "+PAGE.toolName+".\n\n1. Type your numbers in the boxes above.\n2. Tap Calculate (or just type — the answer updates as you go).\n3. Read the big answer and the breakdown table below it.\n\nThe worked example under the tool shows real numbers so you can check the maths.", done:true};
    }
    // site map / categories
    if(/site map|sitemap|what.*on this site|all (tools|calculators)|categories/.test(ql)){
      return {text:"FreeCalcNow has 15,390 free calculators in 14 categories: Finance, Math, Statistics, Health, Everyday life, Conversion, Physics, Chemistry, Biology, Construction, Food, Sports, Ecology and Other — plus the Daily Number game and 50+ mini games.\n\nUse the search box at the top, or browse the A–Z list on the home page.", done:true, link:{id:"", name:"Browse all tools"}};
    }
    // games
    if(/game|play|daily number/.test(ql)){
      return {text:"Play the Daily Number game — guess today's 4-digit number in 6 tries — or try any of the 50+ mini games. No sign-up, free forever.", done:true, link:{id:"games/daily-number", name:"Play Daily Number"}};
    }
    // how many tools / what's new
    if(/how many|what.*new|newest/.test(ql)){
      return {text:"There are 15,390 free calculators on FreeCalcNow right now, plus the Daily Number game and 50+ mini games. Every tool shows its working, and your numbers never leave your browser.", done:true};
    }
    // find a tool by keywords
    return loadIndex().then(function(){
      var hits=searchTools(ql,3);
      if(hits.length){
        var txt="Here is what I found:";
        return {text:txt, done:true, links:hits};
      }
      var ctx = PAGE.toolId ? " You are on the "+PAGE.toolName+" page right now — I can explain its result, or find another tool for you." : "";
      return {text:"I couldn't find a tool for that."+ctx+"\n\nTry naming the job — for example “mortgage”, “BMI”, “miles to km” — or type a sum like “15% of 240”.", done:true};
    });
  }
  /* ---------- UI ---------- */
  var panel, msgs, input, micBtn, rec=null, listening=false;
  function addMsg(text, who, links){
    var d=document.createElement("div");
    d.className="ask-msg"+(who==="user"?" user":"");
    d.textContent=text;
    if(links && links.length){
      links.forEach(function(t){
        var a=document.createElement("a");
        a.href = t.id ? "/"+t.id+"/" : "/";
        a.textContent = t.name;
        d.appendChild(document.createElement("br"));
        d.appendChild(a);
      });
    }
    msgs.appendChild(d);
    msgs.scrollTop=msgs.scrollHeight;
  }
  function send(q){
    q=(q||"").trim(); if(!q) return;
    addMsg(q,"user");
    input.value="";
    var res=answer(q);
    if(res && typeof res.then==="function"){ res.then(function(r){ addMsg(r.text,"bot", r.links || (r.link?[r.link]:null)); }); }
    else if(res){ addMsg(res.text,"bot", res.links || (res.link?[res.link]:null)); }
  }
  function toggleMic(){
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SR){
      addMsg("Voice input isn't supported in this browser — please type your question instead. (Chrome and Edge on Android/desktop support voice.)","bot");
      return;
    }
    if(listening){ try{ rec.stop(); }catch(e){} return; }
    rec=new SR(); rec.lang="en-US"; rec.interimResults=false; rec.maxAlternatives=1;
    rec.onresult=function(e){
      var txt=e.results[0][0].transcript;
      input.value=txt; send(txt);
    };
    rec.onend=function(){ listening=false; micBtn.classList.remove("on"); micBtn.textContent="🎤"; };
    rec.onerror=function(){ listening=false; micBtn.classList.remove("on"); micBtn.textContent="🎤"; addMsg("I couldn't hear that — please try again or type instead.","bot"); };
    try{ rec.start(); listening=true; micBtn.classList.add("on"); micBtn.textContent="●"; }catch(e){ addMsg("Voice input couldn't start — please type instead.","bot"); }
  }
  function build(){
    if(document.querySelector(".ask-fab")) return;
    var fab=el('<button class="ask-fab" type="button">Ask FreeCalcNow</button>');
    panel=el('<div class="ask-panel" hidden>'
      +'<div class="ask-head"><span>Ask FreeCalcNow</span><button type="button" id="ask-close" aria-label="Close">✕</button></div>'
      +'<div class="ask-msgs" id="ask-msgs"></div>'
      +'<div class="ask-chips">'
      +'<button type="button" data-q="Explain this result">Explain this result</button>'
      +'<button type="button" data-q="How do I use this tool?">How do I use this?</button>'
      +'<button type="button" data-q="Daily Number game">Play Daily Number</button>'
      +'</div>'
      +'<div class="ask-input"><button type="button" class="ask-mic" id="ask-mic" title="Ask by voice">🎤</button><input id="ask-in" type="text" placeholder="Ask a sum, a conversion, or name a tool…" autocomplete="off"><button type="button" id="ask-send">Send</button></div>'
      +'</div>');
    document.body.appendChild(fab);
    document.body.appendChild(panel);
    msgs=panel.querySelector("#ask-msgs");
    input=panel.querySelector("#ask-in");
    micBtn=panel.querySelector("#ask-mic");
    var open=function(){
      panel.hidden=false; loadIndex();
      if(!msgs.children.length){
        var hello="Hi! I know all 15,390 FreeCalcNow calculators";
        if(PAGE.toolName) hello+=" — and you are on the "+PAGE.toolName+" page right now, so I can explain its result too";
        hello+=".\n\nAsk a sum (“15% of 240”), a conversion (“10 miles to km”), or name a tool (“mortgage”). You can also tap the microphone and ask by voice.";
        addMsg(hello,"bot");
      }
      input.focus();
    };
    fab.addEventListener("click",function(){ if(panel.hidden){ open(); } else { panel.hidden=true; } });
    panel.querySelector("#ask-close").addEventListener("click",function(){ panel.hidden=true; });
    panel.querySelector("#ask-send").addEventListener("click",function(){ send(input.value); });
    input.addEventListener("keydown",function(e){ if(e.key==="Enter") send(input.value); });
    micBtn.addEventListener("click",toggleMic);
    panel.querySelectorAll(".ask-chips button").forEach(function(b){
      b.addEventListener("click",function(){ send(b.getAttribute("data-q")); });
    });
  }
  if(document.readyState==="loading"){ document.addEventListener("DOMContentLoaded",build); } else { build(); }
})();
