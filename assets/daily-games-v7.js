/* FreeCalcNow v7 — 20 daily games (#1-20 of the 1000 ideas).
   Every game uses FCN_SEED (same puzzle for everyone, same day) and
   FCN_DAILY (one shared streak across all daily games). No sign-up,
   no server. All money prices are labelled estimates where they appear. */
(function(){
"use strict";
function $(id){ return document.getElementById(id); }
function el(tag, txt, cls){ var e=document.createElement(tag); if(txt!==undefined&&txt!==null) e.textContent=txt; if(cls) e.className=cls; return e; }
function today(){ try{ return window.FCN_DAILY ? FCN_DAILY.todayStr() : new Date().toISOString().slice(0,10); }catch(e){ return "2026-11-20"; } }
function rng(){ try{ return window.FCN_SEED.rngFor(today()); }catch(e){ var s=12345; return function(){ s=(s*1103515245+12345)%2147483648; return s/2147483648; }; } }
function niceDate(){ try{ var d=new Date(today()+"T12:00:00Z"); return d.toLocaleDateString("en-GB",{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}); }catch(e){ return today(); } }
function playedKey(id){ return "fcn-v7-"+id+"-"+today(); }
function wasPlayed(id){ try{ return localStorage.getItem(playedKey(id))==="1"; }catch(e){ return false; } }
function markPlayed(id){ try{ localStorage.setItem(playedKey(id),"1"); }catch(e){} }
function showStreak(){ try{ var s=$("streak"); if(s&&window.FCN_DAILY) s.textContent=FCN_DAILY.get().n; }catch(e){} }
function setScore(n){ try{ var s=$("score"); if(s) s.textContent=n; var b=$("best"); var k="fcn_best_"+window.__V7_ID; var best=0; try{ best=parseInt(localStorage.getItem(k)||"0")||0; }catch(e){} if(n>best){ best=n; try{ localStorage.setItem(k,String(best)); }catch(e){} } if(b) b.textContent=best; }catch(e){} }
function msg(t){ var m=$("msg"); if(m) m.textContent=t; }
/* Finish a game: record the shared streak once, show result + share. */
function finish(id, title, score, resultLine, url){
  var stk=0, first=!wasPlayed(id);
  try{ if(window.FCN_DAILY&&first){ stk=FCN_DAILY.record(id, score); } else if(window.FCN_DAILY){ stk=FCN_DAILY.get().n; } }catch(e){}
  markPlayed(id); setScore(score); showStreak();
  var line = resultLine + (stk? " "+stk+"-day streak!" : "");
  msg(line);
  var sb=$("shareBtn");
  if(sb){
    sb.style.display="block";
    sb.onclick=function(){
      var t="FreeCalcNow — "+title+" ("+niceDate()+")\n"+line+"\nPlay: "+url;
      try{ window.FCN_DAILY.copyText(t,function(ok){ msg(ok?"Result copied — paste it anywhere!":t); }); }catch(e){ msg(t); }
    };
  }
  return stk;
}
/* Generic 4-option quiz. q = {q, opts[4], answer (index), why}. */
function quiz4(box, q, id, title, url){
  box.appendChild(el("div", q.q, "q"));
  var grid=el("div","", "grid"); box.appendChild(grid);
  var done=false;
  q.opts.forEach(function(opt,i){
    var b=el("button", opt, "opt"); grid.appendChild(b);
    b.onclick=function(){
      if(done) return; done=true;
      var ok = (i===q.answer);
      b.style.background = ok ? "#166534" : "#dc2626"; b.style.color="#fff";
      var score = ok ? 100 : 0;
      finish(id, title, score, ok ? "Correct! "+q.why : "Not quite — "+q.why, url);
    };
  });
}
/* Generic number-guess game. spec = {prompt, answer, unit, scoreFn(guess,answer), hint}. */
function numGame(box, spec, id, title, url, tries){
  tries = tries || 3;
  box.appendChild(el("div", spec.prompt, "q"));
  var row=el("div","", "row"); box.appendChild(row);
  var inp=document.createElement("input"); inp.type="number"; inp.setAttribute("inputmode","decimal"); inp.placeholder="Your answer"; row.appendChild(inp);
  var btn=el("button","Check","btn"); btn.style.flex="0 0 110px"; row.appendChild(btn);
  var left=el("div","Tries left: "+tries,"small"); left.style.textAlign="center"; box.appendChild(left);
  var used=0, done=false;
  function check(){
    if(done) return;
    var g=parseFloat(inp.value);
    if(isNaN(g)){ msg("Type a number first."); return; }
    used++; left.textContent="Tries left: "+(tries-used);
    if(Math.abs(g-spec.answer)<0.0001){
      done=true;
      var score=Math.max(10, 100-(used-1)*30);
      finish(id, title, score, "Correct in "+used+" "+(used===1?"try":"tries")+"! Answer: "+spec.answer+(spec.unit?" "+spec.unit:"")+".", url);
    } else if(used>=tries){
      done=true;
      var s2=spec.scoreFn ? spec.scoreFn(g, spec.answer) : 0;
      finish(id, title, s2, "Out of tries — the answer was "+spec.answer+(spec.unit?" "+spec.unit:"")+". "+(spec.hint||""), url);
    } else {
      msg(g<spec.answer ? "Too low — try higher." : "Too high — try lower.");
      inp.value=""; inp.focus();
    }
  }
  btn.onclick=check;
  inp.addEventListener("keydown",function(e){ if(e.key==="Enter") check(); });
}
var GAMES={};
/* #1 Daily Maths Riddle — a seeded shop word-problem, 3 tries. */
GAMES["daily-maths-riddle"]=function(box,id,title,url){
  var r=rng();
  var kind=Math.floor(r()*4);
  var spec;
  if(kind===0){ var p=2+Math.floor(r()*9), n=3+Math.floor(r()*8), paid=[20,50,100][Math.floor(r()*3)];
    while(paid<=p*n) paid+=20;
    spec={prompt:"A shop sells pencils at $"+p+" each. You buy "+n+" pencils and pay with $"+paid+". How much change do you get? ($)", answer:paid-p*n, unit:"$", hint:"Change = paid − (price × how many)."}; }
  else if(kind===1){ var a2=25+Math.floor(r()*40), b2=5+Math.floor(r()*12), t2=2+Math.floor(r()*8);
    spec={prompt:"Sara had $"+a2+". She spent $"+b2+" on lunch and $"+t2+" on a bus ticket. How much does she have left? ($)", answer:a2-b2-t2, unit:"$", hint:"Left = start − lunch − ticket."}; }
  else if(kind===2){ var c=4+Math.floor(r()*12), m=2+Math.floor(r()*6);
    spec={prompt:"One notebook costs $"+c+". How much do "+m+" notebooks cost? ($)", answer:c*m, unit:"$", hint:"Total = price × how many."}; }
  else { var save=5+Math.floor(r()*15);
    spec={prompt:"Ali saves $"+save+" every week. How much will he save in 4 weeks? ($)", answer:save*4, unit:"$", hint:"4 weeks × weekly saving."}; }
  numGame(box, spec, id, title, url, 3);
};
/* #2 Daily Number Sequence — guess the next number, 4 options + why. */
GAMES["daily-number-sequence"]=function(box,id,title,url){
  var r=rng();
  var kind=Math.floor(r()*5), seq=[], next=0, why="";
  if(kind===0){ var a=2+Math.floor(r()*8), d=2+Math.floor(r()*6);
    for(var i=0;i<5;i++) seq.push(a+i*d); next=a+5*d; why="It goes up by "+d+" each time."; }
  else if(kind===1){ var a2=3+Math.floor(r()*6), m=2+Math.floor(r()*2);
    for(var j=0;j<5;j++) seq.push(a2*Math.pow(m,j)); next=a2*Math.pow(m,5); why="Each number is ×"+m+" the one before."; }
  else if(kind===2){ var s0=1+Math.floor(r()*4);
    for(var k=1;k<=5;k++) seq.push(s0+k*k); next=s0+36; why="It adds 1, 4, 9, 16, 25, 36 — square numbers."; }
  else if(kind===3){ var f=[1,1], n0=2+Math.floor(r()*3);
    seq=[n0,n0+1]; for(var l=2;l<5;l++) seq.push(seq[l-1]+seq[l-2]); next=seq[4]+seq[3]; why="Each number is the sum of the two before it."; }
  else { var b0=10+Math.floor(r()*20), st=3+Math.floor(r()*5);
    for(var p=0;p<5;p++) seq.push(b0+p*st-(p*p)); next=b0+5*st-25; why="Each step is 2 smaller than the one before."; }
  var opts=[next, next+1, next+2, next-1];
  /* shuffle options with the seeded rng */
  for(var q=opts.length-1;q>0;q--){ var jx=Math.floor(r()*(q+1)); var t=opts[q]; opts[q]=opts[jx]; opts[jx]=t; }
  quiz4(box, {q:"What comes next?  "+seq.join(", ")+", …", opts:opts.map(String), answer:opts.indexOf(next), why:why+" Next = "+next+"."}, id, title, url);
};

/* #3 Daily Estimation Challenge — guess a real-life money total, 1 guess, scored by closeness. */
GAMES["daily-estimation"]=function(box,id,title,url){
  var r=rng();
  var kind=Math.floor(r()*4), spec;
  function close(g,a){ var err=Math.abs(g-a)/a*100; return Math.max(0, Math.round(100-err)); }
  if(kind===0){
    var items=[["Bread",2,5],["Milk",2,6],["Rice (1 kg)",3,8],["Eggs (12)",3,7],["Apples (1 kg)",2,6]];
    var total=0, lines=[];
    items.forEach(function(it){ var pr=it[1]+Math.floor(r()*(it[2]-it[1]+1)); total+=pr; lines.push(it[0]+" — $"+pr); });
    spec={prompt:"Weekly shop — guess the total. Prices are typical (estimates):\n"+lines.join("\n")+"\nWhat is the total? ($)", answer:total, unit:"$", scoreFn:close, hint:"Add all 5 prices."};
  } else if(kind===1){
    var fare=2+Math.floor(r()*4), trips=20+Math.floor(r()*11);
    spec={prompt:"A bus ticket costs $"+fare+" (typical price, estimate). You ride "+trips+" times this month. Guess the monthly total. ($)", answer:fare*trips, unit:"$", scoreFn:close, hint:"Total = fare × rides."};
  } else if(kind===2){
    var ph=15+Math.floor(r()*26), net=20+Math.floor(r()*31);
    spec={prompt:"Your phone plan is $"+ph+"/month and home internet is $"+net+"/month (typical prices, estimates). Guess the yearly total for both. ($)", answer:(ph+net)*12, unit:"$", scoreFn:close, hint:"Add both, then × 12 months."};
  } else {
    var tk=8+Math.floor(r()*9), people=2+Math.floor(r()*4), snack=3+Math.floor(r()*6);
    spec={prompt:"A cinema ticket costs $"+tk+" (typical price, estimate). "+people+" friends go, and each buys a $"+snack+" snack. Guess the total. ($)", answer:people*(tk+snack), unit:"$", scoreFn:close, hint:"Each person pays ticket + snack."};
  }
  numGame(box, spec, id, title, url, 1);
};
/* #4 Daily Money Trivia — one 4-option money fact per day, with a one-line explainer. */
var TRIVIA=[
 {q:"What does the 50/30/20 rule suggest?", opts:["50% needs, 30% wants, 20% saving","50% saving, 30% needs, 20% wants","50% wants, 30% saving, 20% needs","50% needs, 50% saving"], a:0, why:"It is a simple guideline: half for needs, about a third for wants, a fifth for saving."},
 {q:"What is compound interest?", opts:["Interest paid only once","Interest on your money AND on past interest","A fee for late payment","Interest that never changes"], a:1, why:"Compound interest earns interest on past interest too, so money grows faster over time."},
 {q:"What is an emergency fund for?", opts:["Buying a new phone","Covering surprise costs like a broken fridge","Paying for holidays","Investing in stocks"], a:1, why:"It is cash set aside for surprise costs, so you do not need a loan."},
 {q:"What does inflation mean?", opts:["Prices fall over time","Money buys less over time","Banks pay more interest","Wages always rise"], a:1, why:"When prices rise, the same money buys less than before."},
 {q:"What does APR mean?", opts:["The yearly cost of borrowing","A bank account type","A tax refund","A savings bonus"], a:0, why:"APR is the yearly cost of a loan or credit card, shown as a percent."},
 {q:"Why pay more than the minimum on a credit card?", opts:["It looks good","You pay less interest and clear the debt faster","The bank asks you to","It raises your limit at once"], a:1, why:"Paying only the minimum means most of the payment goes to interest."},
 {q:"What is diversification?", opts:["Buying one stock","Spreading money across different things","Saving all cash at home","Borrowing from many banks"], a:1, why:"Spreading money means one bad result does not hurt everything."},
 {q:"What is a budget?", opts:["A plan for your money before you spend it","A bank statement","A loan","A shopping list"], a:0, why:"A budget is a plan: you decide where money goes before the month starts."},
 {q:"If you save $10 a week, how much in a year?", opts:["$120","$520","$1,000","$52"], a:1, why:"$10 × 52 weeks = $520. Small weekly amounts add up."},
 {q:"What is interest on a savings account?", opts:["Money the bank pays you for keeping money there","A tax","A fee for the account","Money you pay the bank"], a:0, why:"The bank pays you interest for keeping your savings with them."},
 {q:"What should you check before taking a loan?", opts:["Only the monthly payment","The total cost, rate and fees","Only the bank's name","Only how fast you get it"], a:1, why:"A low monthly payment can still mean a high total cost."},
 {q:"What does 'pay yourself first' mean?", opts:["Spend first, save what is left","Save a fixed amount as soon as you are paid","Pay all bills last","Buy what you want first"], a:1, why:"Saving first, right after payday, means the money is saved before it is spent."}
];
GAMES["daily-money-trivia"]=function(box,id,title,url){
  var r=rng();
  var t=TRIVIA[Math.floor(r()*TRIVIA.length)];
  quiz4(box, {q:t.q, opts:t.opts, answer:t.a, why:t.why}, id, title, url);
};
/* #5 Daily 60-Second Maths Sprint — fresh seeded questions, 60 seconds, beat your best. */
GAMES["daily-maths-sprint"]=function(box,id,title,url){
  var r=rng();
  box.appendChild(el("div","60 seconds. How many can you solve? A new set every day.", "q"));
  var timerEl=el("div","60","q"); box.appendChild(timerEl);
  var row=el("div","", "row"); box.appendChild(row);
  var qEl=el("div","Press Start when you are ready.","q"); box.appendChild(qEl);
  var inp=document.createElement("input"); inp.type="number"; inp.setAttribute("inputmode","numeric"); inp.placeholder="Answer"; inp.disabled=true; row.appendChild(inp);
  var startBtn=el("button","▶ Start","btn"); box.appendChild(startBtn);
  var correct=0, left=60, timer=null, over=false, cur=null;
  function newQ(){
    var kind=Math.floor(r()*4), a, b, ans, txt;
    if(kind===0){ a=11+Math.floor(r()*89); b=11+Math.floor(r()*89); ans=a+b; txt=a+" + "+b+" = ?"; }
    else if(kind===1){ a=20+Math.floor(r()*80); b=5+Math.floor(r()*a); ans=a-b; txt=a+" − "+b+" = ?"; }
    else if(kind===2){ a=2+Math.floor(r()*11); b=2+Math.floor(r()*11); ans=a*b; txt=a+" × "+b+" = ?"; }
    else { b=2+Math.floor(r()*11); ans=2+Math.floor(r()*11); a=b*ans; txt=a+" ÷ "+b+" = ?"; }
    cur=ans; qEl.textContent=txt; inp.value=""; inp.focus();
  }
  function end(){
    if(over) return; over=true;
    if(timer) clearInterval(timer);
    inp.disabled=true; startBtn.style.display="none";
    finish(id, title, correct, "⏱ Time! You solved "+correct+" in 60 seconds.", url);
  }
  startBtn.onclick=function(){
    startBtn.style.display="none"; inp.disabled=false; correct=0; left=60; over=false;
    timerEl.textContent="60"; newQ();
    timer=setInterval(function(){ left--; timerEl.textContent=String(left); if(left<=0) end(); },1000);
  };
  function check(){
    if(over||!cur&&cur!==0) return;
    var g=parseFloat(inp.value); if(isNaN(g)) return;
    if(g===cur){ correct++; setScore(correct); }
    newQ();
  }
  inp.addEventListener("keydown",function(e){ if(e.key==="Enter") check(); });
};

/* #6 Daily Logic Grid — 3 people, 3 pets, 4 clues. Pick each person's pet. */
GAMES["daily-logic-grid"]=function(box,id,title,url){
  var r=rng();
  var people=["Ava","Ben","Cara"], pets=["cat","dog","fish"];
  var assign={};
  var sh=FCN_SEED.shuffle(r, pets.slice());
  /* Ben must not own the dog (clue 2 needs it). */
  while(sh[1]==="dog"){ sh=FCN_SEED.shuffle(r, pets.slice()); }
  people.forEach(function(p,i){ assign[p]=sh[i]; });
  var notPet=pets.filter(function(x){ return x!==assign["Ava"]; })[Math.floor(r()*2)];
  var clues=[
    "The dog's owner drinks tea.",
    "Ben drinks coffee.",
    "Ava does not own the "+notPet+".",
    "Cara owns the "+assign["Cara"]+"."
  ];
  box.appendChild(el("div","Who owns which pet? Use the clues.", "q"));
  var cl=el("div","", ""); box.appendChild(cl);
  clues.forEach(function(c){ cl.appendChild(el("div","• "+c,"small")); });
  var sels={};
  people.forEach(function(p){
    var row=el("div","", "row"); box.appendChild(row);
    row.appendChild(el("span", p+" owns: ", ""));
    var s=document.createElement("select"); s.style.cssText="flex:1;padding:10px;font-size:16px;border:2px solid #cbd5e1;border-radius:10px";
    ["— pick —"].concat(pets).forEach(function(pt){ var o=document.createElement("option"); o.value=pt; o.textContent=pt; s.appendChild(o); });
    sels[p]=s; row.appendChild(s);
  });
  var btn=el("button","Check my answers","btn"); box.appendChild(btn);
  btn.onclick=function(){
    var ok=true;
    people.forEach(function(p){ if(sels[p].value!==assign[p]) ok=false; });
    if(ok){
      finish(id, title, 100, "Correct! Ava owns the "+assign["Ava"]+", Ben owns the "+assign["Ben"]+", Cara owns the "+assign["Cara"]+".", url);
    } else {
      msg("Not yet — read the clues again and try once more.");
    }
  };
};
/* #7 Daily Memory Match — 8 cards, 4 pairs, one layout per day. */
GAMES["daily-memory-match"]=function(box,id,title,url){
  var r=rng();
  var syms=["$","€","£","¥"];
  var deck=FCN_SEED.shuffle(r, syms.concat(syms));
  var grid=el("div","", "grid"); grid.style.gridTemplateColumns="repeat(4, 1fr)"; box.appendChild(grid);
  var open=[], matched=0, moves=0, lock=false, done=false;
  deck.forEach(function(sym,i){
    var c=el("button","?","tile"); grid.appendChild(c);
    c.onclick=function(){
      if(lock||done||c.textContent!== "?") return;
      c.textContent=sym;
      open.push({c:c, sym:sym});
      if(open.length===2){
        moves++; lock=true;
        var a=open[0], b=open[1]; open=[];
        if(a.sym===b.sym){
          matched+=2; lock=false;
          if(matched===8){
            done=true;
            var score=Math.max(10, 100-(moves-4)*5);
            finish(id, title, score, "All matched in "+moves+" moves!", url);
          }
        } else {
          setTimeout(function(){ a.c.textContent="?"; b.c.textContent="?"; lock=false; },700);
        }
      }
    };
  });
  box.appendChild(el("div","Flip two cards. Find all 4 pairs. Moves: count each pair you flip.","small"));
};
/* #8 Daily Spot the Difference — two 5×5 grids, 5 seeded differences. */
GAMES["daily-spot-difference"]=function(box,id,title,url){
  var r=rng();
  var syms=["★","◆","●","▲","■","✿","♦","♣"];
  var base=[], i;
  for(i=0;i<25;i++) base.push(syms[Math.floor(r()*syms.length)]);
  var diffPos=[];
  while(diffPos.length<5){ var p=Math.floor(r()*25); if(diffPos.indexOf(p)<0) diffPos.push(p); }
  var right=base.slice();
  diffPos.forEach(function(p){ var s; do{ s=syms[Math.floor(r()*syms.length)]; }while(s===base[p]); right[p]=s; });
  function drawGrid(arr, clickable){
    var g=el("div","", "grid"); g.style.gridTemplateColumns="repeat(5, 1fr)";
    arr.forEach(function(s,ix){
      var c=el("button",s,"tile"); c.style.minHeight="40px"; c.style.fontSize="18px"; g.appendChild(c);
      if(clickable){
        c.onclick=function(){
          if(done) return;
          if(diffPos.indexOf(ix)>=0){
            if(c.style.background==="rgb(22, 101, 52)") return;
            c.style.background="#166534"; c.style.color="#fff"; found++;
            if(found===5){ done=true; var sc=Math.max(10, 100-wrong*5); finish(id, title, sc, "You found all 5 differences!"+(wrong?" ("+wrong+" wrong taps)":""), url); }
            else msg("Found "+found+" of 5.");
          } else {
            wrong++; c.style.background="#fecaca";
            msg("That one is the same. Wrong taps: "+wrong+".");
          }
        };
      }
    });
    return g;
  }
  var found=0, wrong=0, done=false;
  box.appendChild(el("div","Left grid is the original. Tap the 5 changed squares in the right grid.","small"));
  box.appendChild(el("div","Original","small")); box.appendChild(drawGrid(base,false));
  box.appendChild(el("div","Changed — tap the 5 differences","small")); box.appendChild(drawGrid(right,true));
};
/* #9 Daily Word Ladder — change one letter at a time to reach the target word. */
var LADDERS=[
 ["COLD","CORD","CARD","WARD","WARM"],["TOP","POP","PUP","CUP","CUT","COT","COW","LOW"],["CAT","COT","DOT","DOG"],
 ["PIG","DIG","DOG","COG","COW"],["BOOK","COOK","COOL","FOOL","FOOD","GOOD","GOLD","GOAD","LOAD","LEAD","READ"],["LOVE","MOVE","MOTE","MATE","HATE"],
 ["SAND","SANK","RANK","RACK","ROCK"],["BALL","BALE","GALE","GAME"],["COIN","COIL","FOIL","FAIL","FALL","BALL","BILL"],
 ["RICH","RICE","RACE","RACK","ROCK","ROOK","BOOK","BOOR","POOR"],["LOAN","LOON","LOOK","LOCK","LACK","BACK","BANK"],["CASH","BASH","BASK","BANK"],
 ["HAND","LAND","LARD","LORD","FORD","FOOD","FOOT"],["SHIP","CHIP","CHOP","COOP","COOT","BOOT","BOAT"]
];
GAMES["daily-word-ladder"]=function(box,id,title,url){
  var r=rng();
  var lad=LADDERS[Math.floor(r()*LADDERS.length)];
  var allWords={}; LADDERS.forEach(function(L){ L.forEach(function(w){ allWords[w]=1; }); });
  var cur=lad[0], target=lad[lad.length-1], steps=0, done=false;
  var qEl=el("div","", "q"); box.appendChild(qEl);
  function show(){ qEl.textContent=cur+"  →  "+target+"  ("+steps+" steps)"; }
  show();
  box.appendChild(el("div","Change ONE letter at a time. Each step must be a real word.","small"));
  var row=el("div","", "row"); box.appendChild(row);
  var inp=document.createElement("input"); inp.type="text"; inp.maxLength=cur.length; inp.placeholder="Next word"; inp.style.textTransform="uppercase"; row.appendChild(inp);
  var btn=el("button","Go","btn"); btn.style.flex="0 0 90px"; row.appendChild(btn);
  function diff(a,b){ var n=0; for(var i=0;i<a.length;i++) if(a[i]!==b[i]) n++; return n; }
  function go(){
    if(done) return;
    var w=(inp.value||"").toUpperCase().replace(/[^A-Z]/g,"");
    if(w.length!==cur.length){ msg("That word must be "+cur.length+" letters."); return; }
    if(diff(w,cur)!==1){ msg("Change exactly ONE letter."); return; }
    if(!allWords[w]){ msg("That is not a word on the ladder path — try another."); return; }
    cur=w; steps++; show(); inp.value="";
    if(cur===target){
      done=true;
      var extra=Math.max(0, steps-(lad.length-1));
      var score=Math.max(10, 100-extra*10);
      finish(id, title, score, "You reached "+target+" in "+steps+" steps! (Shortest path: "+(lad.length-1)+" steps.)", url);
    } else msg("Good — keep going!");
  }
  btn.onclick=go;
  inp.addEventListener("keydown",function(e){ if(e.key==="Enter") go(); });
};
/* #10 Daily Anagram — unscramble today's money word. 3 tries. */
var ANAGRAM_WORDS=["MONEY","BANK","COIN","CASH","SAVE","RICH","LOAN","DEBT","PRICE","PROFIT","MARKET","WALLET","BUDGET","CREDIT","INCOME","SAVINGS","INTEREST","EXPENSE"];
GAMES["daily-anagram"]=function(box,id,title,url){
  var r=rng();
  var word=ANAGRAM_WORDS[Math.floor(r()*ANAGRAM_WORDS.length)];
  var letters=FCN_SEED.shuffle(r, word.split(""));
  var guard=0;
  while(letters.join("")===word && guard++<10){ letters=FCN_SEED.shuffle(r, word.split("")); }
  var tries=3, done=false;
  box.appendChild(el("div","Unscramble:  "+letters.join(" "), "q"));
  box.appendChild(el("div","A money word. 3 tries. After one wrong guess you get the first letter.","small"));
  var row=el("div","", "row"); box.appendChild(row);
  var inp=document.createElement("input"); inp.type="text"; inp.maxLength=word.length; inp.placeholder="Your answer"; inp.style.textTransform="uppercase"; row.appendChild(inp);
  var btn=el("button","Check","btn"); btn.style.flex="0 0 110px"; row.appendChild(btn);
  function go(){
    if(done) return;
    var g=(inp.value||"").toUpperCase().replace(/[^A-Z]/g,"");
    if(!g){ msg("Type your answer first."); return; }
    if(g===word){
      done=true;
      var score=tries===3?100:(tries===2?70:40);
      finish(id, title, score, "Correct! The word was "+word+".", url);
    } else {
      tries--;
      if(tries<=0){ done=true; finish(id, title, 0, "Out of tries — the word was "+word+". Come back tomorrow!", url); }
      else msg("Not that word. Hint: it starts with “"+word[0]+"”. Tries left: "+tries+".");
    }
    inp.value="";
  }
  btn.onclick=go;
  inp.addEventListener("keydown",function(e){ if(e.key==="Enter") go(); });
};

/* #11 Daily Odd One Out — four share something, one does not. */
var ODD_SETS=[
 {items:["2","4","6","8","9"], odd:4, why:"9 is odd — the rest are even numbers."},
 {items:["3","6","9","12","14"], odd:4, why:"14 is not a multiple of 3."},
 {items:["5","10","15","20","22"], odd:4, why:"22 is not a multiple of 5."},
 {items:["1","4","9","16","20"], odd:4, why:"20 is not a square number (1, 4, 9, 16 are)."},
 {items:["2","3","5","7","9"], odd:4, why:"9 is not a prime number."},
 {items:["10","20","30","40","45"], odd:4, why:"45 is not a multiple of 10."},
 {items:["7","14","21","28","30"], odd:4, why:"30 is not a multiple of 7."},
 {items:["100","200","300","400","450"], odd:4, why:"450 is not a round hundred."},
 {items:["1","2","4","8","12"], odd:4, why:"12 is not a power of 2."},
 {items:["11","22","33","44","45"], odd:4, why:"45 is the only one whose two digits are different."},
 {items:["6","12","18","24","25"], odd:4, why:"25 is not a multiple of 6."},
 {items:["50","60","70","80","85"], odd:4, why:"85 is not a multiple of 10."}
];
GAMES["daily-odd-one-out"]=function(box,id,title,url){
  var r=rng();
  var s=ODD_SETS[Math.floor(r()*ODD_SETS.length)];
  quiz4(box, {q:"Which one is the odd one out?  "+s.items.join("  ·  "), opts:s.items, answer:s.odd, why:s.why}, id, title, url);
};
/* #12 Daily Coin-Flip Prediction — predict 5 flips, then flip the coins. */
GAMES["daily-coin-flip"]=function(box,id,title,url){
  var r=rng();
  var flips=[]; for(var i=0;i<5;i++) flips.push(r()<0.5?"H":"T");
  var pred=[], done=false;
  box.appendChild(el("div","Predict the next 5 coin flips, then flip!", "q"));
  var slots=el("div","_ _ _ _ _","q"); box.appendChild(slots);
  var row=el("div","", "row"); box.appendChild(row);
  var hBtn=el("button","Heads","btn"); hBtn.style.flex="1"; row.appendChild(hBtn);
  var tBtn=el("button","Tails","btn amber"); tBtn.style.flex="1"; row.appendChild(tBtn);
  var flipBtn=el("button","Flip the coins","btn"); flipBtn.style.display="none"; box.appendChild(flipBtn);
  var resEl=el("div","", "q"); box.appendChild(resEl);
  function draw(){ slots.textContent=pred.concat(["_","_","_","_","_"]).slice(0,5).join(" "); }
  hBtn.onclick=function(){ if(done||pred.length>=5) return; pred.push("H"); draw(); if(pred.length===5){ flipBtn.style.display="block"; } };
  tBtn.onclick=function(){ if(done||pred.length>=5) return; pred.push("T"); draw(); if(pred.length===5){ flipBtn.style.display="block"; } };
  flipBtn.onclick=function(){
    if(done) return; done=true;
    var matches=0;
    for(var i=0;i<5;i++) if(pred[i]===flips[i]) matches++;
    resEl.textContent="Coins: "+flips.join("  ")+"  —  You: "+pred.join("  ");
    finish(id, title, matches*20, "You predicted "+matches+" of 5 flips right!", url);
  };
};
/* #13 Daily Dice Total Guess — guess the total of two dice, one try. */
GAMES["daily-dice-guess"]=function(box,id,title,url){
  var r=rng();
  var d1=1+Math.floor(r()*6), d2=1+Math.floor(r()*6), total=d1+d2;
  var faces=["⚀","⚁","⚂","⚃","⚄","⚅"];
  var done=false;
  box.appendChild(el("div","Two dice are about to roll. Guess their total (2–12).", "q"));
  var row=el("div","", "row"); box.appendChild(row);
  var inp=document.createElement("input"); inp.type="number"; inp.min="2"; inp.max="12"; inp.placeholder="2–12"; row.appendChild(inp);
  var btn=el("button","Roll the dice","btn"); btn.style.flex="0 0 110px"; row.appendChild(btn);
  var resEl=el("div","", "q"); box.appendChild(resEl);
  btn.onclick=function(){
    if(done) return;
    var g=parseInt(inp.value,10);
    if(isNaN(g)||g<2||g>12){ msg("Enter a number from 2 to 12."); return; }
    done=true;
    resEl.textContent=faces[d1-1]+" "+faces[d2-1]+"  =  "+total;
    var diff=Math.abs(g-total);
    var score= diff===0?100 : diff===1?70 : diff===2?40 : 10;
    finish(id, title, score, diff===0 ? "Exact! The total was "+total+"." : "The total was "+total+" — you were "+diff+" away.", url);
  };
};
/* #14 Daily Budget Puzzle — spend as much as you can without going over budget. */
GAMES["daily-budget-puzzle"]=function(box,id,title,url){
  var r=rng();
  var budget=0, items=[], tries=0;
  var names=["Notebook","Water bottle","Snacks","Pen set","Socks","Mug","Book","Cap","Charger","Tote bag","Puzzle","Plant"];
  function gen(){
    budget=30+Math.floor(r()*31);
    items=[];
    var pool=FCN_SEED.shuffle(r, names.slice());
    for(var i=0;i<6;i++) items.push({name:pool[i], price:3+Math.floor(r()*13)});
    /* check a winning subset exists (90%-100% of budget) */
    for(var m=0;m<64;m++){
      var s=0;
      for(var j=0;j<6;j++) if(m&(1<<j)) s+=items[j].price;
      if(s>=0.9*budget && s<=budget) return true;
    }
    return false;
  }
  while(!gen() && tries++<50){}
  box.appendChild(el("div","Budget: $"+budget+". Tick items to buy — spend at least 90% of it, but do NOT go over.", "q"));
  var checks=[];
  items.forEach(function(it){
    var lab=document.createElement("label");
    lab.style.cssText="display:flex;gap:10px;align-items:center;padding:10px;border:2px solid #e2e8f0;border-radius:10px;margin:6px 0;background:#fff;cursor:pointer";
    var cb=document.createElement("input"); cb.type="checkbox"; cb.style.cssText="width:20px;height:20px";
    lab.appendChild(cb); lab.appendChild(el("span", it.name+" — $"+it.price, ""));
    box.appendChild(lab); checks.push({cb:cb, price:it.price});
  });
  var totalEl=el("div","Total: $0","q"); box.appendChild(totalEl);
  var btn=el("button","Check my basket","btn"); box.appendChild(btn);
  function total(){ var s=0; checks.forEach(function(c){ if(c.cb.checked) s+=c.price; }); return s; }
  checks.forEach(function(c){ c.cb.onchange=function(){ totalEl.textContent="Total: $"+total(); }; });
  btn.onclick=function(){
    var t=total();
    if(t>budget){ msg("Over budget by $"+(t-budget)+" — remove something."); return; }
    if(t<0.9*budget){ msg("You spent $"+t+" — that is under 90% of $"+budget+". Add more items!"); return; }
    var score=Math.round(t/budget*100);
    finish(id, title, score, "You spent $"+t+" of $"+budget+" — "+score+"% of your budget, without going over!", url);
  };
};
/* #15 Daily Price Guess — guess one everyday price (typical prices = estimates). */
var PRICE_ITEMS=[
 ["A loaf of bread",2,4],["A litre of milk",1,2],["A cup of coffee in a café",3,6],
 ["A cinema ticket",8,15],["A city bus ticket",1,3],["1 kg of rice",2,5],
 ["A dozen eggs",3,6],["A plain T-shirt",8,20],["A haircut",10,25],
 ["A litre of petrol",1,2],["A 500 ml bottle of water",1,2],["A pair of socks",3,8]
];
GAMES["daily-price-guess"]=function(box,id,title,url){
  var r=rng();
  var it=PRICE_ITEMS[Math.floor(r()*PRICE_ITEMS.length)];
  var truePrice=it[1]+Math.floor(r()*(it[2]-it[1]+1));
  function close(g,a){ var err=Math.abs(g-a)/a*100; return Math.max(0, Math.round(100-err)); }
  numGame(box, {prompt:"Guess the typical price of "+it[0]+". (Typical prices are estimates — they vary by shop and country.) ($)", answer:truePrice, unit:"$", scoreFn:close, hint:"The typical price was $"+truePrice+"."}, id, title, url, 1);
};

/* #16 Daily Calendar Puzzle — what day of the week was this date? */
GAMES["daily-calendar-puzzle"]=function(box,id,title,url){
  var r=rng();
  var start=new Date(Date.UTC(2000,0,1)).getTime();
  var end=new Date(Date.UTC(2026,10,19)).getTime();
  var d=new Date(start+Math.floor(r()*(end-start)));
  var days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  var wd=d.getUTCDay();
  var dateStr=d.toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric",timeZone:"UTC"});
  var opts=FCN_SEED.shuffle(r, days.slice());
  quiz4(box, {q:"What day of the week was "+dateStr+"?", opts:opts, answer:opts.indexOf(days[wd]), why:dateStr+" was a "+days[wd]+"."}, id, title, url);
};
/* #17 Daily Percentage Puzzle — a real-life % problem, 4 options. */
GAMES["daily-percentage-puzzle"]=function(box,id,title,url){
  var r=rng();
  var kind=Math.floor(r()*4), q, ans, why;
  if(kind===0){ var p=20+Math.floor(r()*81), pc=[10,20,25,50][Math.floor(r()*4)];
    ans=p*(100-pc)/100; q="A jacket costs $"+p+". It is "+pc+"% off. What is the sale price? ($)"; why="Sale price = $"+p+" × "+(100-pc)+"% = $"+ans+"."; }
  else if(kind===1){ var b=20+Math.floor(r()*81), tp=[10,15,20][Math.floor(r()*3)];
    ans=b*tp/100; q="Your meal costs $"+b+". You leave a "+tp+"% tip. How much is the tip? ($)"; why="Tip = $"+b+" × "+tp+"% = $"+ans+"."; }
  else if(kind===2){ var s=(100+Math.floor(r()*900))*10, rp=[3,5,10][Math.floor(r()*3)];
    ans=s*(100+rp)/100; q="Your salary is $"+s+" a month. You get a "+rp+"% raise. What is your new salary? ($/month)"; why="New salary = $"+s+" × "+(100+rp)+"% = $"+ans+"."; }
  else { var pr=10+Math.floor(r()*91), tx=[5,10,20][Math.floor(r()*3)];
    ans=pr*(100+tx)/100; q="A book costs $"+pr+" before tax. Tax is "+tx+"%. What do you pay in total? ($)"; why="Total = $"+pr+" × "+(100+tx)+"% = $"+ans+"."; }
  var opts=[ans, ans+1, ans-1, ans+5];
  for(var i=opts.length-1;i>0;i--){ var j=Math.floor(r()*(i+1)); var t=opts[i]; opts[i]=opts[j]; opts[j]=t; }
  quiz4(box, {q:q, opts:opts.map(function(x){ return "$"+x; }), answer:opts.indexOf(ans), why:why}, id, title, url);
};
/* #18 Daily Pattern Puzzle — find the rule, pick the next number. */
var PATTERNS=[
 {seq:[3,7,15,31], next:63, rule:"Each number is ×2 + 1."},
 {seq:[5,9,17,33], next:65, rule:"Each number is ×2 − 1."},
 {seq:[2,5,10,13], next:26, rule:"The steps are +3, ×2, +3, ×2 …"},
 {seq:[10,12,15,20], next:27, rule:"The steps are +2, +3, +5, +7 (prime numbers)."},
 {seq:[4,10,28], next:82, rule:"Each number is ×3 − 2."},
 {seq:[1,2,4,7,11], next:16, rule:"The steps are +1, +2, +3, +4 …"},
 {seq:[100,90,81,73], next:66, rule:"The steps are −10, −9, −8, −7 …"},
 {seq:[1,3,6,10], next:15, rule:"Add 2, then 3, then 4, then 5 (triangle numbers)."}
];
GAMES["daily-pattern-puzzle"]=function(box,id,title,url){
  var r=rng();
  var p=PATTERNS[Math.floor(r()*PATTERNS.length)];
  var opts=[p.next, p.next+1, p.next-1, p.next+2];
  for(var i=opts.length-1;i>0;i--){ var j=Math.floor(r()*(i+1)); var t=opts[i]; opts[i]=opts[j]; opts[j]=t; }
  quiz4(box, {q:"What comes next?  "+p.seq.join(", ")+", …", opts:opts.map(String), answer:opts.indexOf(p.next), why:p.rule+" Next = "+p.next+"."}, id, title, url);
};
/* #19 Daily Money Myth — true or false, with a short explainer. */
var MYTHS=[
 {s:"You need a lot of money to start saving.", t:false, why:"Even $1 a week is a start — small amounts add up over a year."},
 {s:"Credit cards are free money.", t:false, why:"You must pay it back, with interest if you do not pay in full."},
 {s:"Renting is always throwing money away.", t:false, why:"Renting can be the right choice — it depends on prices, how long you stay, and other costs."},
 {s:"Saving about 10% of your pay is a good start.", t:true, why:"Many guides suggest around 10% as a first savings goal."},
 {s:"All debt is bad.", t:false, why:"A low-cost loan for study or a home can be useful. High-cost debt is the problem."},
 {s:"Compound interest only helps rich people.", t:false, why:"It helps anyone who starts early, even with small amounts."},
 {s:"Checking your bank balance often is a good habit.", t:true, why:"Checking often helps you spot mistakes and fraud early."},
 {s:"A higher salary always means more savings.", t:false, why:"If spending rises as fast as pay, savings do not grow."},
 {s:"Emergency funds are only for rich people.", t:false, why:"Even a small fund — $50 or $100 — helps when a surprise cost appears."},
 {s:"Investing is the same as gambling.", t:false, why:"Long-term diversified investing is not gambling, though all investing has risk."},
 {s:"Cash at home is always safer than a bank.", t:false, why:"Cash can be lost or stolen. A bank keeps it safe and usually pays interest."},
 {s:"Skipping one coffee a week saves nothing.", t:false, why:"One $4 coffee a week is over $200 a year."}
];
GAMES["daily-money-myth"]=function(box,id,title,url){
  var r=rng();
  var m=MYTHS[Math.floor(r()*MYTHS.length)];
  box.appendChild(el("div","True or false?", "q"));
  box.appendChild(el("div","“"+m.s+"”", "q"));
  var row=el("div","", "row"); box.appendChild(row);
  var done=false;
  function pick(v){
    if(done) return; done=true;
    var ok=(v===m.t);
    finish(id, title, ok?100:0, (ok?"Correct! ":"Not quite — ")+m.why, url);
  }
  var tb=el("button","TRUE","btn"); tb.style.flex="1"; row.appendChild(tb);
  var fb=el("button","FALSE","btn amber"); fb.style.flex="1"; row.appendChild(fb);
  tb.onclick=function(){ pick(true); };
  fb.onclick=function(){ pick(false); };
};
/* #20 Daily Savings Micro-Task — one tiny saving action, with a running total. */
var SAVE_TASKS=[
 ["Skip one takeaway coffee today",4],["Bring lunch from home today",5],["Walk instead of a short taxi ride",3],
 ["Skip one snack from a shop",2],["Use a free activity instead of a paid one",6],["Drink tap water instead of buying a bottle",1],
 ["Cook dinner at home tonight",7],["Skip one streaming rental",5],["Use a library book instead of buying one",8],
 ["Turn off lights you do not need",1],["Take the bus instead of a taxi",4],["Make coffee at home",3]
];
GAMES["daily-savings-task"]=function(box,id,title,url){
  var r=rng();
  var t=SAVE_TASKS[Math.floor(r()*SAVE_TASKS.length)];
  function total(){ try{ return parseFloat(localStorage.getItem("fcn-savings-total")||"0")||0; }catch(e){ return 0; } }
  box.appendChild(el("div","Today's tiny saving: "+t[0]+" — saves about $"+t[1]+".", "q"));
  var totEl=el("div","Total saved so far (on this device): $"+total(),"q"); box.appendChild(totEl);
  var btn=el("button","I did it today","btn"); box.appendChild(btn);
  var done=false;
  btn.onclick=function(){
    if(done) return; done=true;
    var first=!wasPlayed(id);
    var nt=total()+(first?t[1]:0);
    try{ localStorage.setItem("fcn-savings-total", String(nt)); }catch(e){}
    totEl.textContent="Total saved so far (on this device): $"+nt;
    finish(id, title, t[1], first ? "Nice! You saved about $"+t[1]+" today. Total so far: $"+nt+"." : "Done again — your total stays $"+nt+" (counted once per day).", url);
  };
};
/* Registry + mount. */
var META={
 "daily-maths-riddle":{title:"Daily Maths Riddle",url:"https://freecalcnow.github.io/games/daily-maths-riddle/"},
 "daily-number-sequence":{title:"Daily Number Sequence",url:"https://freecalcnow.github.io/games/daily-number-sequence/"},
 "daily-estimation":{title:"Daily Estimation Challenge",url:"https://freecalcnow.github.io/games/daily-estimation/"},
 "daily-money-trivia":{title:"Daily Money Trivia",url:"https://freecalcnow.github.io/games/daily-money-trivia/"},
 "daily-maths-sprint":{title:"Daily 60-Second Maths Sprint",url:"https://freecalcnow.github.io/games/daily-maths-sprint/"},
 "daily-logic-grid":{title:"Daily Logic Grid",url:"https://freecalcnow.github.io/games/daily-logic-grid/"},
 "daily-memory-match":{title:"Daily Memory Match",url:"https://freecalcnow.github.io/games/daily-memory-match/"},
 "daily-spot-difference":{title:"Daily Spot the Difference",url:"https://freecalcnow.github.io/games/daily-spot-difference/"},
 "daily-word-ladder":{title:"Daily Word Ladder",url:"https://freecalcnow.github.io/games/daily-word-ladder/"},
 "daily-anagram":{title:"Daily Anagram",url:"https://freecalcnow.github.io/games/daily-anagram/"},
 "daily-odd-one-out":{title:"Daily Odd One Out",url:"https://freecalcnow.github.io/games/daily-odd-one-out/"},
 "daily-coin-flip":{title:"Daily Coin-Flip Prediction",url:"https://freecalcnow.github.io/games/daily-coin-flip/"},
 "daily-dice-guess":{title:"Daily Dice Total Guess",url:"https://freecalcnow.github.io/games/daily-dice-guess/"},
 "daily-budget-puzzle":{title:"Daily Budget Puzzle",url:"https://freecalcnow.github.io/games/daily-budget-puzzle/"},
 "daily-price-guess":{title:"Daily Price Guess",url:"https://freecalcnow.github.io/games/daily-price-guess/"},
 "daily-calendar-puzzle":{title:"Daily Calendar Puzzle",url:"https://freecalcnow.github.io/games/daily-calendar-puzzle/"},
 "daily-percentage-puzzle":{title:"Daily Percentage Puzzle",url:"https://freecalcnow.github.io/games/daily-percentage-puzzle/"},
 "daily-pattern-puzzle":{title:"Daily Pattern Puzzle",url:"https://freecalcnow.github.io/games/daily-pattern-puzzle/"},
 "daily-money-myth":{title:"Daily Money Myth",url:"https://freecalcnow.github.io/games/daily-money-myth/"},
 "daily-savings-task":{title:"Daily Savings Micro-Task",url:"https://freecalcnow.github.io/games/daily-savings-task/"}
};
function mount(id){
  window.__V7_ID=id;
  var box=$("game"); if(!box||!GAMES[id]) return;
  showStreak();
  var sb=$("shareBtn"); if(sb) sb.style.display="none";
  if(wasPlayed(id)){
    var n=el("div","You already finished today's puzzle — play again for fun! A new puzzle comes tomorrow.","small");
    box.parentNode.insertBefore(n, box);
  }
  GAMES[id](box, id, META[id].title, META[id].url);
}
window.FCN_V7={mount:mount, games:GAMES, meta:META};
if(typeof module!=="undefined"&&module.exports){
  module.exports={GAMES:GAMES, META:META, TRIVIA:TRIVIA, LADDERS:LADDERS, ODD_SETS:ODD_SETS,
    PRICE_ITEMS:PRICE_ITEMS, ANAGRAM_WORDS:ANAGRAM_WORDS, MYTHS:MYTHS, SAVE_TASKS:SAVE_TASKS, PATTERNS:PATTERNS};
}
})();
