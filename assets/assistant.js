/* FreeCalcNow assistant — rule-based, context-aware, runs 100% in the browser.
   Knows the current page/tool (window.FCN_PAGE), solves sums, converts units,
   finds tools, explains the current result, answers "what is" questions in plain
   English, chats, and guides the user. No server, no cost. Never a dead end. */
(function(){
  "use strict";
  var PAGE = window.FCN_PAGE || {toolId:null, toolName:null, category:null, slug:""};
  var INDEX = null, INDEX_LOADING = null;
  function el(html){ var d=document.createElement("div"); d.innerHTML=html.trim(); return d.firstChild; }
  function esc(s){ return String(s==null?"":s).replace(/[&<>\"']/g,function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
  /* ---------- name memory ---------- */
  var USER_NAME=null;
  try{ USER_NAME=localStorage.getItem("fcn-name")||null; }catch(e){}
  function setName(n){
    n=(n||"").trim().toLowerCase().replace(/[^a-z ]/g,"").trim();
    if(!n || n.length>20) return false;
    n=n.charAt(0).toUpperCase()+n.slice(1);
    USER_NAME=n;
    try{ localStorage.setItem("fcn-name", n); }catch(e){}
    return true;
  }
  function greetWord(){
    var h=new Date().getHours();
    if(h<12) return "Good morning";
    if(h<17) return "Good afternoon";
    return "Good evening";
  }
  /* ---------- index + search ---------- */
  var POPULAR=[
    {id:"mortgage",name:"Mortgage Calculator",cat:"Finance"},
    {id:"bmi",name:"BMI Calculator",cat:"Health"},
    {id:"loan",name:"Loan / EMI Calculator",cat:"Finance"},
    {id:"compound",name:"Compound Interest Calculator",cat:"Finance"},
    {id:"sip-calculator",name:"SIP Calculator",cat:"Finance"},
    {id:"percentage",name:"Percentage Calculator",cat:"Math"},
    {id:"tip",name:"Tip & Bill Split Calculator",cat:"Everyday life"},
    {id:"age",name:"Age Calculator",cat:"Everyday life"},
    {id:"salary-hourly",name:"Salary ↔ Hourly Calculator",cat:"Finance"},
    {id:"calorie",name:"Calorie (TDEE) Calculator",cat:"Health"},
    {id:"discount",name:"Discount Calculator",cat:"Everyday life"},
    {id:"games/daily-number",name:"Daily Number game",cat:"Games"}
  ];
  function loadIndex(){
    if(INDEX) return Promise.resolve(INDEX);
    if(INDEX_LOADING) return INDEX_LOADING;
    try{
      if(typeof fetch==="undefined") throw new Error("no fetch");
      INDEX_LOADING = fetch("/assets/tools-index.json").then(function(r){ return r.json(); }).then(function(j){ INDEX=j; return j; }).catch(function(){ INDEX=[]; return INDEX; });
    }catch(e){ INDEX=[]; INDEX_LOADING=Promise.resolve(INDEX); }
    return INDEX_LOADING;
  }
  /* Common words people type, mapped to the words our tools actually use. */
  var SYNONYMS={
    "emi":["loan"], "home loan":["mortgage"], "house payment":["mortgage"],
    "car loan":["loan"], "student loan":["loan"], "weight":["bmi"],
    "height":["bmi"], "salary":["salary","hourly"], "pay":["salary","hourly"],
    "take home":["salary"], "per hour":["salary","hourly"],
    "how old":["age"], "grade":["gpa"], "grade point":["gpa"],
    "qr":["qr"], "password":["password"], "tip":["tip"],
    "discount":["discount"], "calorie":["calorie"], "tdee":["calorie"],
    "inflation":["inflation"], "roi":["roi"], "return on investment":["roi"],
    "sip":["sip"], "mutual fund":["sip"], "monthly payment":["mortgage","loan"],
    "body mass":["bmi"], "interest":["compound","loan"], "savings":["compound"],
    "invest":["compound","sip"], "retire":["retirement"], "pension":["retirement"]
  };
  function expandWords(words){
    var out=words.slice();
    var joined=" "+words.join(" ")+" ";
    for(var k in SYNONYMS){
      if(joined.indexOf(" "+k+" ")>=0){
        SYNONYMS[k].forEach(function(w){ if(out.indexOf(w)<0) out.push(w); });
      }
    }
    return out;
  }
  function lev(a,b){
    if(Math.abs(a.length-b.length)>1) return 2;
    var d=[], i, j;
    for(i=0;i<=a.length;i++) d[i]=[i];
    for(j=0;j<=b.length;j++) d[0][j]=j;
    for(i=1;i<=a.length;i++) for(j=1;j<=b.length;j++){
      d[i][j]=Math.min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));
    }
    return d[a.length][b.length];
  }
  function searchTools(q, n){
    n = n || 3;
    var raw = q.toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).filter(function(w){ return w.length>2; });
    if(!raw.length) return [];
    var words = expandWords(raw);
    var list = (INDEX && INDEX.length) ? INDEX : POPULAR;
    var scored = list.map(function(t){
      var name=t.name.toLowerCase(), hay=(name+" "+(t.blurb||"")+" "+t.cat).toLowerCase(), s=0;
      words.forEach(function(w){
        if(name.indexOf(w)>=0) s+=3;
        else if(hay.indexOf(w)>=0) s+=1;
        else {
          /* prefix or one-letter typo, e.g. "mortage", "bmii", "lon" */
          var nameWords=name.split(/[^a-z]+/);
          for(var i=0;i<nameWords.length;i++){
            var nw=nameWords[i];
            if(nw.length<3 || w.length<3) continue;
            if(nw.indexOf(w)===0 || w.indexOf(nw)===0){ s+=2; break; }
            if(w.length>=4 && nw.charAt(0)===w.charAt(0) && lev(nw,w)<=1){ s+=2; break; }
          }
        }
      });
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
  /* ---------- plain-English concept answers ---------- */
  var CONCEPTS=[
    {re:/mortgage|home loan/, text:"A mortgage is a long loan you take to buy a home. You pay it back every month for many years — part of each payment is interest, part pays off the loan itself. Early on, most of each payment is interest.", link:{id:"mortgage", name:"Mortgage Calculator"}},
    {re:/\bbmi\b|body mass/, text:"BMI (Body Mass Index) is a number from your weight and height. It tells you if you are underweight, healthy, overweight, or obese. It is a rough guide — muscle and age also matter.", link:{id:"bmi", name:"BMI Calculator"}},
    {re:/\bloan\b|emi\b/, text:"A loan is money you borrow and pay back in monthly parts (EMI = Equated Monthly Instalment). Each part covers some interest plus a bit of the amount you borrowed. The calculator shows your monthly payment, total interest, and payoff plan.", link:{id:"loan", name:"Loan / EMI Calculator"}},
    {re:/compound interest|compound/, text:"Compound interest means you earn interest on your interest. Your money grows faster over time because each year's interest is added to the amount, and next year earns interest on the bigger amount.", link:{id:"compound", name:"Compound Interest Calculator"}},
    {re:/\bsip\b|mutual fund/, text:"A SIP (Systematic Investment Plan) is a small fixed amount you invest every month. Over years it can grow a lot, because your returns also earn returns. The calculator shows what a monthly plan could become.", link:{id:"sip-calculator", name:"SIP Calculator"}},
    {re:/income tax|\btax\b/, text:"Income tax is money the government takes from what you earn. The amount depends on your income and your country's tax bands. The calculator works out your tax and what you keep.", link:{id:"income-tax", name:"Income Tax Calculator (US Federal)"}},
    {re:/\btip\b/, text:"A tip is extra money you give for good service — often 10%, 15% or 20% of the bill. The calculator splits the bill and the tip, even between several people.", link:{id:"tip", name:"Tip & Bill Split Calculator"}},
    {re:/\bgpa\b|grade point/, text:"GPA (Grade Point Average) is the average of your course grades. Each grade is worth points (A = 4, B = 3, and so on), weighted by how many credits each course is worth.", link:{id:"gpa", name:"GPA Calculator"}},
    {re:/qr code|\bqr\b/, text:"A QR code is a square picture that a phone camera can read — it can hold a link, some text, or Wi-Fi details. The generator makes one for free, right in your browser.", link:{id:"qr", name:"QR Code Generator"}},
    {re:/json/, text:"JSON is a way of writing data that computers share with each other — lists and named values inside { } brackets. The formatter tidies messy JSON and checks if it is valid.", link:{id:"json", name:"JSON Formatter & Validator"}},
    {re:/password/, text:"A strong password is long and random — a mix of letters, numbers and symbols that nobody can guess. The generator makes one for you, and never sends it anywhere.", link:{id:"password-gen", name:"Password Generator & Strength Checker"}},
    {re:/calorie/, text:"A calorie is a unit of energy in food. Your body burns a number of calories every day just to stay alive, and more when you move. The calculator works out how many you need.", link:{id:"calorie", name:"Calorie (TDEE) Calculator"}},
    {re:/tdee/, text:"TDEE (Total Daily Energy Expenditure) is the total calories you burn in a day — your body at rest, plus moving, plus exercise. It is the starting point for losing, gaining, or keeping weight.", link:{id:"calorie", name:"Calorie (TDEE) Calculator"}},
    {re:/inflation/, text:"Inflation is how prices rise over time — so the same money buys less later. $100 today will not buy the same things in 10 years. The calculator shows what money from another year is worth now.", link:{id:"inflation", name:"Inflation Calculator"}},
    {re:/\broi\b|return on investment/, text:"ROI (Return on Investment) shows how much money you made compared with what you put in. If you invest $100 and get back $120, your ROI is 20%.", link:{id:"roi", name:"Investment Return (ROI) Calculator"}},
    {re:/salary|hourly|per hour/, text:"Your hourly rate is your yearly salary divided by the hours you work. $50,000 a year is about $24 an hour on a 40-hour week. The calculator works it out both ways.", link:{id:"salary-hourly", name:"Salary ↔ Hourly Calculator"}},
    {re:/percentage|percent/, text:"A percentage is a part out of 100. 25% of 200 is 50. The calculator works out percentages, percentage change, and “what percent is X of Y”.", link:{id:"percentage", name:"Percentage Calculator"}},
    {re:/discount/, text:"A discount is money taken off a price. A 20% discount on $50 means you pay $40. The calculator shows the discount and the price you actually pay.", link:{id:"discount", name:"Discount Calculator"}},
    {re:/\bage\b|how old/, text:"Your age is the time from your date of birth until today — in years, months and days. The calculator works it out exactly, including leap years.", link:{id:"age", name:"Age Calculator"}},
    {re:/retire|pension/, text:"Retirement saving means putting money aside now so you have it when you stop working. Small monthly savings, grown over many years with interest, can become a large amount.", link:{id:"retirement", name:"Retirement Calculator"}}
  ];
  function tryConcept(ql){
    if(!/what is|what'?s|what does|mean|explain|tell me about|^about |^define /.test(ql)) return null;
    for(var i=0;i<CONCEPTS.length;i++){
      if(CONCEPTS[i].re.test(ql)){
        return {text: CONCEPTS[i].text + "\n\nWant the number? Open the tool and type your own figures.", done:true, link: CONCEPTS[i].link};
      }
    }
    return null;
  }
  /* ---------- answers ---------- */
  function toolLink(t){ return '<a href="/'+t.id+'/">'+esc(t.name)+'</a>'; }
  function suggestLinks(){
    return [POPULAR[0], POPULAR[1], POPULAR[2]];
  }
  function answer(q){
    var ql=q.toLowerCase().trim();
    /* name capture: "hi i m arslan", "my name is arslan" */
    var nm = ql.match(/(?:i'?m|i m|i am|my name is|this is|mera naam)\s+([a-z]{2,20})/);
    var nameGiven = nm ? setName(nm[1]) : false;
    /* greetings */
    if(/^(hi+|hello|hey|hii+|salam|aoa|salaam|assalamu alaikum|good morning|good afternoon|good evening)\b/.test(ql) || nameGiven){
      var hello = greetWord() + (USER_NAME ? ", " + USER_NAME : "") + "! ";
      if(nameGiven) hello = "Hi " + USER_NAME + "! Great to meet you. ";
      hello += "I can solve sums, convert units, find any of the 15,390 calculators, or explain a result. Try “15% of 240”, “10 miles to km”, or “mortgage”.";
      return {text: hello, done:true, links: suggestLinks()};
    }
    /* small talk */
    if(/how are you|how'?s it going|how do you feel/.test(ql)){
      return {text:"I'm doing great — ready to calculate! What shall we work out" + (USER_NAME ? ", " + USER_NAME : "") + "? A sum, a conversion, or a tool like “mortgage” or “BMI”?", done:true, links: suggestLinks()};
    }
    if(/who are you|your name|what are you/.test(ql)){
      return {text:"I'm Ask FreeCalcNow — the helper built into this site. I know all 15,390 calculators, I solve sums and conversions, and I explain results. Everything runs in your browser, free, no sign-up.", done:true};
    }
    if(/\bhelp\b|what can you do/.test(ql)){
      return {text:"Here's what I can do:\n• Solve a sum — “15% of 240”, “120 + 35”\n• Convert units — “10 miles to km”, “5 kg to lb”\n• Find a tool — “mortgage”, “BMI”, “tip”\n• Explain things — “what is a mortgage?”\n• Explain the calculator you are using — “explain this result”\n\nJust type or tap the microphone and ask by voice.", done:true, links: suggestLinks()};
    }
    if(/thank|shukran|thanks/.test(ql)){
      return {text:"You're welcome" + (USER_NAME ? ", " + USER_NAME : "") + "! Anything else to work out?", done:true, links: suggestLinks()};
    }
    if(/\bbye\b|goodbye|see you/.test(ql)){
      return {text:"Goodbye" + (USER_NAME ? ", " + USER_NAME : "") + "! Come back any time — the calculators and games are always here.", done:true};
    }
    if(/joke/.test(ql)){
      return {text:"Why was 6 afraid of 7? Because 7, 8, 9!\n\nWant another one — or shall we calculate something?", done:true, links: suggestLinks()};
    }
    if(/what(?:'?s| is) the time|what time is it|today'?s date|what day is it|what'?s the date/.test(ql)){
      var now=new Date();
      return {text:"Right now it is " + now.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit"}) + " on " + now.toLocaleDateString("en-US",{weekday:"long", year:"numeric", month:"long", day:"numeric"}) + ".", done:true};
    }
    /* concept answers ("what is a mortgage?") */
    var concept = tryConcept(ql);
    if(concept) return concept;
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
      return {text:"FreeCalcNow has 15,390 free calculators in 14 categories: Finance, Math, Statistics, Health, Everyday life, Conversion, Physics, Chemistry, Biology, Construction, Food, Sports, Ecology and Other — plus the Daily Number game and 78 mini games.\n\nUse the search box at the top, or browse the A–Z list on the home page.", done:true, link:{id:"tools", name:"Browse all tools"}};
    }
    // games
    if(/game|play|daily number/.test(ql)){
      return {text:"Play the Daily Number game — guess today's 4-digit number in 6 tries — or try any of the 78 mini games. No sign-up, free forever.", done:true, link:{id:"games/daily-number", name:"Play Daily Number"}};
    }
    // how many tools / what's new
    if(/how many|what.*new|newest/.test(ql)){
      return {text:"There are 15,390 free calculators on FreeCalcNow right now, plus the Daily Number game and 78 mini games. Every tool shows its working, and your numbers never leave your browser.", done:true};
    }
    // find a tool by keywords — never a dead end
    return loadIndex().then(function(){
      var hits=searchTools(ql,3);
      if(hits.length){
        return {text:"Here is what I found for you:", done:true, links:hits};
      }
      var ctx = PAGE.toolId ? " You are on the "+PAGE.toolName+" page right now — I can explain its result, or find another tool for you." : "";
      return {text:"I don't have an exact match for that yet."+ctx+"\n\nHere are three tools people use most — or tell me what you want to work out, for example “mortgage”, “BMI”, a sum like “15% of 240”, or a conversion like “10 miles to km”.", done:true, links: suggestLinks()};
    });
  }
  /* Test hook (also handy for the /ask/ page): window.FCN_ask("hi") */
  window.FCN_ask = answer;
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
      panel.hidden=false; fab.style.display="none"; loadIndex();
      if(!msgs.children.length){
        var hello="Hi" + (USER_NAME ? " " + USER_NAME : "") + "! I know all 15,390 FreeCalcNow calculators";
        if(PAGE.toolName) hello+=" — and you are on the "+PAGE.toolName+" page right now, so I can explain its result too";
        hello+=".\n\nAsk a sum (“15% of 240”), a conversion (“10 miles to km”), or name a tool (“mortgage”). You can also tap the microphone and ask by voice.";
        addMsg(hello,"bot");
      }
      input.focus();
    };
    fab.addEventListener("click",function(){ if(panel.hidden){ open(); } else { panel.hidden=true; fab.style.display=""; } });
    panel.querySelector("#ask-close").addEventListener("click",function(){ panel.hidden=true; fab.style.display=""; });
    panel.querySelector("#ask-send").addEventListener("click",function(){ send(input.value); });
    input.addEventListener("keydown",function(e){ if(e.key==="Enter") send(input.value); });
    micBtn.addEventListener("click",toggleMic);
    panel.querySelectorAll(".ask-chips button").forEach(function(b){
      b.addEventListener("click",function(){ send(b.getAttribute("data-q")); });
    });
  }
  if(document.readyState==="loading"){ document.addEventListener("DOMContentLoaded",build); } else { build(); }
})();
