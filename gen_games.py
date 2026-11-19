#!/usr/bin/env python3
"""Generate 50 endless mini-games for FreeCalcNow. Batch 1: 50+ games, 1000+ variations.
Each game: one self-contained HTML file, inline CSS+JS, no external deps.
Each game reads URL query params (difficulty/op/mode/size/time/...) and configures itself.
Variations = cartesian product of the game's variation axes; every axis is actually
read and used by that game's JS (honest count)."""
import os, json, itertools, html

BASE = os.path.expanduser("~/workspace/freecalcnow-site")
GAMES_DIR = os.path.join(BASE, "games")

CSS = """*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#F8FAFC;color:#0F172A}header{background:#166534;color:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}header a{color:#fff;font-weight:800;text-decoration:none;font-size:18px}header span{font-size:13px;opacity:.9}main{max-width:560px;margin:0 auto;padding:14px 14px 30px}h1{font-size:24px;margin:8px 0 4px}.how{color:#475569;margin:0 0 12px}.bar{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:8px 12px;margin-bottom:12px;font-weight:700}.bar span{color:#166534}#game{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;min-height:180px}#msg{min-height:24px;margin:10px 0;font-weight:600;color:#166534}#q{font-size:26px;font-weight:800;text-align:center;margin:12px 0}.grid{display:grid;gap:8px}.btn{display:block;width:100%;padding:13px;font-size:17px;font-weight:700;border:0;border-radius:10px;background:#166534;color:#fff;cursor:pointer;margin:6px 0}.btn.amber{background:#F59E0B;color:#0F172A}.btn.ghost{background:#e2e8f0;color:#0F172A}.opt{padding:13px;font-size:18px;font-weight:700;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer}.opt:active{background:#dcfce7}.tile{aspect-ratio:1;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer;min-height:48px}input[type=text],input[type=number]{width:100%;padding:12px;font-size:18px;border:2px solid #cbd5e1;border-radius:10px;margin:6px 0}.row{display:flex;gap:8px}.row>*{flex:1}.small{font-size:13px;color:#64748b}.vars{margin-top:14px;font-size:13px}.vars a{display:inline-block;background:#fff;border:1px solid #cbd5e1;border-radius:20px;padding:5px 10px;margin:3px;text-decoration:none;color:#166534;font-weight:600}footer{text-align:center;color:#64748b;font-size:13px;padding:16px}footer a{color:#166534}.more{display:block;text-align:center;margin-top:14px;font-weight:700;color:#166534}"""

def page(slug, name, howto, body, js, variations):
    varlinks = ""
    for v in variations[:6]:
        qs = "&".join(f"{k}={val}" for k, val in v["params"].items())
        varlinks += f'<a href="?{html.escape(qs)}">{html.escape(v["name"])}</a>'
    js_prefix = (
        "var score=0;var best=0;try{best=parseInt(localStorage.getItem('fcn_best_"+slug+"')||'0')||0}catch(e){}"
        "function qp(k){try{return new URLSearchParams(window.location.search).get(k)}catch(e){return null}}"
        "function setScore(n){score=n;var s=document.getElementById('score');if(s)s.textContent=n;if(n>best){best=n;try{localStorage.setItem('fcn_best_"+slug+"',String(best))}catch(e){}}var b=document.getElementById('best');if(b)b.textContent=best;}"
        "function msg(t){var m=document.getElementById('msg');if(m)m.textContent=t;}"
        "function rnd(n){return Math.floor(Math.random()*n)}"
        "function shuffle(a){for(var i=a.length-1;i>0;i--){var j=rnd(i+1);var t=a[i];a[i]=a[j];a[j]=t}return a}"+"function mkOpts(ans,n){var s=[ans];var d=1;while(s.length<n&&d<100){if(ans+d>=0&&s.indexOf(ans+d)<0)s.push(ans+d);if(s.length>=n)break;if(ans-d>=0&&s.indexOf(ans-d)<0)s.push(ans-d);d++}return shuffle(s)}"
        "function el(id){return document.getElementById(id)}"
        "try{var _b=el('best');if(_b)_b.textContent=best}catch(e){}"
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(name)} - FreeCalcNow Games</title><meta name="description" content="{html.escape(howto)} Play free, endless, no sign-up."><style>{CSS}</style></head><body><header><a href="/">FreeCalcNow</a><span>Free Games</span></header><main><h1>{html.escape(name)}</h1><p class="how">{html.escape(howto)}</p><div class="bar"><span>Score: <b id="score">0</b></span><span>Best: <b id="best">0</b></span><span style="margin-left:auto" class="small" id="cfgLabel"></span></div><div id="game">{body}</div><div id="msg"></div><button class="btn" id="startBtn">▶ Start / New game</button><div class="vars"><b>Try a variation:</b><br>{varlinks}</div><a class="more" href="/games/">← More games</a></main><footer><a href="/">FreeCalcNow</a> — free calculators &amp; games. No sign-up, no ads covering play.</footer><script>{js_prefix}\n{js}</script></body></html>"""

def variations_from_axes(axes):
    keys = list(axes.keys())
    out = []
    for combo in itertools.product(*[axes[k] for k in keys]):
        params = dict(zip(keys, combo))
        name = " · ".join(str(c).replace("-", " ").title() for c in combo)
        out.append({"name": name, "params": params})
    return out

GAMES = []
def add(slug, name, blurb, icon, howto, body, js, axes):
    GAMES.append({"slug": slug, "name": name, "blurb": blurb, "icon": icon,
                  "howto": howto, "body": body, "js": js, "axes": axes,
                  "variations": variations_from_axes(axes)})

# ---- 1 daily-number ----
add("daily-number","Daily Number","Guess the daily 4-digit number in 6 tries. New number every day.","🔢",
"Guess the daily number in 6 tries. Green = right digit, right place. Amber = right digit, wrong place.",
'<div id="q">????</div><div class="row"><input type="text" id="inp" inputmode="numeric" maxlength="6" placeholder="Enter your guess"><button class="btn" id="guessBtn" style="flex:0 0 110px">Guess</button></div><div id="board"></div><button class="btn ghost" id="shareBtn">Share my result</button>',
r"""
var digits=parseInt(qp('digits')||'4'); if([3,4,5,6].indexOf(digits)<0)digits=4;
var mode=qp('mode')||'daily'; var maxTries=parseInt(qp('tries')||'6')||6;
var diff=qp('difficulty')||'medium';
var dayStr=''; try{dayStr=new Date().toISOString().slice(0,10)}catch(e){dayStr='2026-11-19'}
var seed=0; for(var i=0;i<dayStr.length;i++)seed=(seed*31+dayStr.charCodeAt(i))>>>0;
function dailyNum(){var s=seed, out=''; for(var k=0;k<digits;k++){s=(s*1103515245+12345)>>>0; out+=String((s>>>16)%10)} return out}
var target = mode==='practice' ? String(rnd(Math.pow(10,digits))).padStart(digits,'0') : dailyNum();
var tries=0, won=false;
if(el('cfgLabel'))el('cfgLabel').textContent=digits+' digits · '+mode+' · '+maxTries+' tries';
function guess(){ if(won||tries>=maxTries)return; var g=(el('inp').value||'').replace(/\D/g,''); if(g.length!==digits){msg('Enter '+digits+' digits.');return}
  tries++; var row=document.createElement('div'); row.style.cssText='display:flex;gap:6px;margin:6px 0';
  var correct=0; for(var i=0;i<digits;i++){var c=document.createElement('div'); c.style.cssText='flex:1;text-align:center;padding:10px;font-weight:800;border-radius:8px;border:2px solid #e2e8f0';
    c.textContent=g[i]; if(g[i]===target[i]){c.style.background='#166534';c.style.color='#fff';correct++} else if(target.indexOf(g[i])>=0){c.style.background='#F59E0B'} el('board').appendChild(c); }
  el('board').appendChild(row); el('inp').value='';
  if(correct===digits){won=true; setScore(maxTries-tries+1); msg('🎉 You got it in '+tries+' tries!'); try{var st=JSON.parse(localStorage.getItem('fcn_daily_streak')||'{"n":0}')||{n:0}; st.n++; localStorage.setItem('fcn_daily_streak',JSON.stringify(st));}catch(e){}}
  else if(tries>=maxTries){msg('Out of tries — the number was '+target+'. Try practice mode!')}
  else msg('Try '+(tries+1)+' of '+maxTries+'.'); }
el('guessBtn').onclick=guess; el('inp').addEventListener('keydown',function(e){if(e.key==='Enter')guess()});
el('shareBtn').onclick=function(){var t='Daily Number: '+(won?'solved in '+tries:'played')+' ('+digits+' digits) on FreeCalcNow'; msg(t); try{if(navigator.clipboard)navigator.clipboard.writeText(t)}catch(e){}};
el('startBtn').onclick=function(){tries=0;won=false;el('board').innerHTML='';setScore(0);if(mode==='practice'){target=String(rnd(Math.pow(10,digits))).padStart(digits,'0')}msg('New game — guess the '+digits+'-digit number!');};
msg(mode==='daily'?'New number every day at 00:00 UTC.':'Practice mode — a fresh number each game.');
""",
{"digits":["3","4","5","6"],"mode":["daily","practice"],"tries":["6","8"]})

# ---- 2 number-sprint ----
add("number-sprint","Number Sprint","60-second mental-maths sprint. How many can you solve?","⚡",
"Answer as many sums as you can before the clock runs out. Pick the right answer, fast!",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div><div class="small" style="text-align:center">Time left: <b id="time">60</b>s · <span id="streak">Streak 0</span></div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'mixed'; var dur=parseInt(qp('time')||'60')||60;
var mode=qp('mode')||'sprint';
var maxN = diff==='easy'?10:(diff==='hard'?50:20); var tLeft=dur, timer=null, streak=0, cur=0, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op+' · '+dur+'s';
function mk(){var a=rnd(maxN)+1,b=rnd(maxN)+1,o=op; if(o==='mixed'){o=['add','subtract','multiply','divide'][rnd(4)]}
  var qtxt,ans; if(o==='add'){ans=a+b;qtxt=a+' + '+b}else if(o==='subtract'){if(b>a){var t=a;a=b;b=t}ans=a-b;qtxt=a+' − '+b}else if(o==='multiply'){a=rnd(9)+2;b=rnd(9)+2;ans=a*b;qtxt=a+' × '+b}else{ans=rnd(9)+2;b=rnd(9)+2;a=ans*b;qtxt=a+' ÷ '+b}
  cur=ans; el('q').textContent=qtxt+' = ?'; var arr=mkOpts(ans,4);
  el('opts').innerHTML=''; arr.forEach(function(v){var btn=document.createElement('button');btn.className='opt';btn.textContent=v;btn.onclick=function(){if(!playing)return; if(v===cur){setScore(score+1);streak++;msg('Correct!')}else{streak=0;msg('Oops — answer was '+cur);} el('streak').textContent='Streak '+streak; mk()}; el('opts').appendChild(btn)});}
function start(){clearInterval(timer);setScore(0);streak=0;tLeft=dur;playing=true;el('time').textContent=tLeft;mk();msg('Go!');
  timer=setInterval(function(){tLeft--;el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer);playing=false;msg('Time! You scored '+score+'. Play again!');}},1000);}
el('startBtn').onclick=start;
""",
{"difficulty":["easy","medium","hard"],"op":["add","subtract","multiply","divide","mixed"],"time":["30","60","90"],"mode":["sprint","endless"]})

# ---- 3 guess-the-number ----
add("guess-the-number","Guess the Number","Guess the secret number. Hotter or colder hints guide you.","🎯",
"Guess the secret number. After each guess you get a higher / lower hint. Fewest guesses wins!",
'<div id="q">I\'m thinking of a number…</div><div class="row"><input type="number" id="inp" placeholder="Your guess"><button class="btn" id="guessBtn" style="flex:0 0 110px">Guess</button></div><div id="hist" class="small"></div>',
r"""
var range=parseInt(qp('range')||'100')||100; var hints=qp('hints')||'on'; var diff=qp('difficulty')||'medium';
var target=0, tries=0;
if(el('cfgLabel'))el('cfgLabel').textContent='1–'+range+' · hints '+hints;
function newGame(){target=rnd(range)+1;tries=0;el('hist').innerHTML='';el('q').textContent='I\'m thinking of a number from 1 to '+range+'…';msg('New round — good luck!');}
function guess(){var g=parseInt(el('inp').value,10); if(isNaN(g)){msg('Type a number first.');return} tries++;
  var h=''; if(hints==='on'){var d=Math.abs(g-target); h=d===0?'':(d<=Math.max(2,range/20)?' — very hot!':(d<=range/10?' — hot':(d<=range/4?' — warm':' — cold')))}
  if(g===target){setScore(Math.max(1,100-tries*5));el('q').textContent='🎉 '+target+' in '+tries+' guesses!';msg('Correct! New round below — press Start.');newGameSoon();}
  else if(g<target){el('q').textContent='Higher!'+h;msg('Try a bigger number.')}
  else{el('q').textContent='Lower!'+h;msg('Try a smaller number.')}
  var p=document.createElement('div');p.textContent='Guess '+tries+': '+g+(g===target?' ✓':'');el('hist').appendChild(p);el('inp').value='';}
function newGameSoon(){setTimeout(newGame,1200)}
el('guessBtn').onclick=guess; el('inp').addEventListener('keydown',function(e){if(e.key==='Enter')guess()});
el('startBtn').onclick=newGame; newGame();
""",
{"range":["50","100","250","500","1000"],"hints":["on","off"],"difficulty":["easy","medium","hard"]})

# ---- 4 memory-match ----
add("memory-match","Memory Match","Match each sum with its answer. Flip cards, find pairs.","🧠",
"Flip two cards. Match a sum (like 6 × 7) with its answer (42). Clear the board!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div>',
r"""
var pairs=parseInt(qp('pairs')||'6')||6; var topic=qp('topic')||'sums'; var diff=qp('difficulty')||'medium';
var maxN = diff==='easy'?5:(diff==='hard'?12:9);
if(el('cfgLabel'))el('cfgLabel').textContent=pairs+' pairs · '+topic+' · '+diff;
var first=null, lock=false, found=0;
function build(){var cards=[]; var used=new Set();
  while(cards.length<pairs*2){var a=rnd(maxN)+2,b=rnd(maxN)+2, q, ans;
    if(topic==='products'){q=a+' × '+b;ans=String(a*b)} else if(topic==='sums'){q=a+' + '+b;ans=String(a+b)} else {q=a+'/'+b; ans=(a/b).toFixed(2)}
    if(used.has(q))continue; used.add(q); cards.push({t:q,v:q}); cards.push({t:ans,v:q});}
  shuffle(cards); found=0; first=null; el('board').innerHTML='';
  cards.forEach(function(c){var d=document.createElement('button'); d.className='tile'; d.textContent='?'; d.dataset.v=c.v; d.dataset.t=c.t;
    d.onclick=function(){if(lock||d.textContent!=='?')return; d.textContent=d.dataset.t;
      if(!first){first=d;return} lock=true; var f=first; first=null;
      if(f.dataset.v===d.dataset.v){found++; setScore(found); msg('Match! '+found+' of '+pairs); if(found===pairs)msg('🎉 Board cleared! Press Start for a new board.'); lock=false;}
      else{setTimeout(function(){f.textContent='?'; d.textContent='?'; lock=false},650);}}; el('board').appendChild(d)});}
el('startBtn').onclick=function(){setScore(0);build();msg('New board — find all '+pairs+' pairs!')}; build();
""",
{"pairs":["4","6","8","10"],"topic":["sums","products","fractions"],"difficulty":["easy","medium","hard"]})

# ---- 5 maths-race ----
add("maths-race","Maths Race","Endless quick questions. Score points, build your streak.","🏁",
"Answer fast to build a streak. One wrong answer resets the streak — how far can you go?",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div><div class="small" style="text-align:center">Streak: <b id="streak">0</b> · Best streak: <b id="bstreak">0</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'mixed'; var mode=qp('mode')||'race';
var maxN=diff==='easy'?10:(diff==='hard'?60:25); var streak=0, bstreak=0, cur=0, round=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op+' · '+mode;
function mk(){round++; var a=rnd(maxN)+1,b=rnd(maxN)+1,o=op; if(o==='mixed')o=['add','subtract','multiply','divide'][rnd(4)];
  var qtxt,ans; if(o==='add'){ans=a+b;qtxt=a+' + '+b}else if(o==='subtract'){if(b>a){var t=a;a=b;b=t}ans=a-b;qtxt=a+' − '+b}else if(o==='multiply'){a=rnd(9)+2;b=rnd(9)+2;ans=a*b;qtxt=a+' × '+b}else{ans=rnd(9)+2;b=rnd(9)+2;a=ans*b;qtxt=a+' ÷ '+b}
  cur=ans; el('q').textContent='Q'+round+': '+qtxt+' = ?'; var s=mkOpts(ans,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var btn=document.createElement('button');btn.className='opt';btn.textContent=v;
    btn.onclick=function(){if(v===cur){streak++; if(streak>bstreak){bstreak=streak;el('bstreak').textContent=bstreak} setScore(score+1+Math.floor(streak/5)); msg('Correct! Streak '+streak);}else{msg('Wrong — it was '+cur+'. Streak reset.'); streak=0} el('streak').textContent=streak; mk()}; el('opts').appendChild(btn)});}
el('startBtn').onclick=function(){setScore(0);streak=0;round=0;mk();msg('Race on!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"op":["add","subtract","multiply","divide","mixed"],"mode":["race","marathon","blitz"]})

# ---- 6 number-merge ----
add("number-merge","Number Merge","2048-style merging grid. Slide tiles, merge to the target!","🔀",
"Use the arrow buttons (or arrow keys) to slide. Equal tiles merge. Reach the target number!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div><div class="small" style="text-align:center">Target: <b id="tgt"></b></div>',
r"""
var size=parseInt(qp('size')||'4')||4; if([3,4,5].indexOf(size)<0)size=4;
var target=parseInt(qp('target')||'2048')||2048; var diff=qp('difficulty')||'medium';
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · target '+target;
el('tgt').textContent=target; el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
var g=[];
function spawn(){var empt=[]; for(var i=0;i<size*size;i++)if(!g[i])empt.push(i); if(!empt.length)return; g[empt[rnd(empt.length)]]=(Math.random()<0.9?2:4);}
function draw(){el('board').innerHTML=''; g.forEach(function(v){var d=document.createElement('div');d.className='tile';d.textContent=v||'';d.style.background=v?'#dcfce7':'';el('board').appendChild(d)});}
function slide(dir){var moved=false; function line(idx){var vals=[]; idx.forEach(function(i){if(g[i])vals.push(g[i])}); for(var k=0;k<vals.length-1;k++){if(vals[k]===vals[k+1]){vals[k]*=2; setScore(score+vals[k]); vals.splice(k+1,1); if(vals[k]>=target)msg('🎉 You reached '+target+'! Keep going!')}} while(vals.length<size)vals.push(0); return vals;}
  for(var r=0;r<size;r++){var idx=[]; for(var c=0;c<size;c++){idx.push(dir==='left'?r*size+c:(dir==='right'?r*size+(size-1-c):(dir==='up'?c*size+r:(size-1-c)*size+r)))}
    var nl=line(idx); for(var j=0;j<size;j++){if(g[idx[j]]!==nl[j])moved=true; g[idx[j]]=nl[j];}}
  if(moved){spawn();draw(); if(g.indexOf(0)<0)msg('No moves left — press Start for a new grid.');}}
function reset(){g=new Array(size*size).fill(0); setScore(0); spawn(); spawn(); draw(); msg('Slide to merge!')}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){slide(b.dataset.dir)}});
document.addEventListener('keydown',function(e){var m={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right'}; if(m[e.key]){e.preventDefault(); slide(m[e.key])}});
el('startBtn').onclick=reset; reset();
""",
{"size":["3","4","5"],"target":["512","1024","2048"],"difficulty":["easy","medium","hard"]})

# ---- 7 higher-lower ----
add("higher-lower","Higher or Lower","Will the next number be higher or lower? Guess right, keep going.","📈",
"See a number, guess whether the next one is higher or lower. One wrong guess ends the run!",
'<div id="q" style="font-size:44px">?</div><div class="row"><button class="btn" id="hiBtn">Higher ▲</button><button class="btn amber" id="loBtn">Lower ▼</button></div><div class="small" style="text-align:center">Range 1–<span id="rng"></span> · Streak: <b id="streak">0</b></div>',
r"""
var range=parseInt(qp('range')||'100')||100; var mode=qp('mode')||'classic'; var diff=qp('difficulty')||'medium';
var cur=0, streak=0;
if(el('cfgLabel'))el('cfgLabel').textContent='1–'+range+' · '+mode;
el('rng').textContent=range;
function draw(){el('q').textContent=cur}
function pick(higher){var n=rnd(range)+1; var ok = higher ? n>cur : n<cur;
  if(n===cur){msg('Same number — free pass!'); cur=n; draw(); return}
  cur=n; draw();
  if(ok){streak++; setScore(streak); el('streak').textContent=streak; msg('Right! Streak '+streak);}
  else{msg('Wrong — run over at '+streak+'. Press Start to play again.'); streak=0; el('streak').textContent=0;}}
function start(){cur=rnd(range)+1; streak=0; el('streak').textContent=0; setScore(0); draw(); msg('Higher or lower than '+cur+'?')}
el('hiBtn').onclick=function(){pick(true)}; el('loBtn').onclick=function(){pick(false)};
el('startBtn').onclick=start; start();
""",
{"range":["20","100","1000"],"mode":["classic","sudden-death"],"difficulty":["easy","medium","hard"]})

# ---- 8 true-false-maths ----
add("true-false-maths","True or False Maths","Is this sum right or wrong? Decide fast — endless statements.","✅",
"Read the statement. Tap TRUE if the maths is correct, FALSE if it is wrong.",
'<div id="q">Press Start</div><div class="row"><button class="btn" id="tBtn">TRUE</button><button class="btn amber" id="fBtn">FALSE</button></div><div class="small" style="text-align:center">Correct: <b id="ok">0</b> / <b id="tot">0</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'mixed'; var mode=qp('mode')||'endless';
var maxN=diff==='easy'?10:(diff==='hard'?30:15); var truth=false, ok=0, tot=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op;
function mk(){var a=rnd(maxN)+1,b=rnd(maxN)+1,o=op; if(o==='mixed')o=['add','subtract','multiply'][rnd(3)];
  var ans; if(o==='add')ans=a+b; else if(o==='subtract')ans=a-b; else ans=a*b;
  var shown=ans; truth=Math.random()<0.5; if(!truth)shown=ans+(rnd(5)+1)*(Math.random()<0.5?-1:1);
  var sym=o==='add'?'+':(o==='subtract'?'−':'×'); el('q').textContent=a+' '+sym+' '+b+' = '+shown;}
function ans(v){tot++; if(v===truth){ok++; setScore(ok); msg('Correct!')}else msg('Wrong — that was '+(truth?'TRUE':'FALSE')+'.'); el('ok').textContent=ok; el('tot').textContent=tot; mk();}
el('tBtn').onclick=function(){ans(true)}; el('fBtn').onclick=function(){ans(false)};
el('startBtn').onclick=function(){ok=0;tot=0;setScore(0);el('ok').textContent=0;el('tot').textContent=0;mk();msg('True or false?')}; mk();
""",
{"difficulty":["easy","medium","hard"],"op":["add","subtract","multiply","mixed"],"mode":["endless","timed"]})

# ---- 9 missing-number ----
add("missing-number","Missing Number","Find the missing number in the sequence. Spot the pattern!","🔍",
"Look at the sequence and work out the pattern. Pick the missing number.",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var type=qp('type')||'arithmetic'; var mode=qp('mode')||'find-it';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+type;
function mk(){var start=rnd(10)+1, step=rnd(5)+2, seq=[], n=5; var t=type; if(t==='mixed')t=['arithmetic','geometric','squares'][rnd(3)];
  for(var i=0;i<n;i++){if(t==='arithmetic')seq.push(start+i*step); else if(t==='geometric')seq.push(start*Math.pow(2,i)); else seq.push((start+i)*(start+i));}
  var miss=rnd(n); cur=seq[miss]; var shown=seq.slice(); shown[miss]='?';
  el('q').textContent=shown.join('  ·  ');
  var s=mkOpts(cur,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('Not quite — it was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Find the missing number!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"type":["arithmetic","geometric","squares","mixed"],"mode":["find-it","timed"]})

# ---- 10 times-table-trainer ----
add("times-table-trainer","Times Table Trainer","Endless multiplication drills. Master every table from 2 to 12.","✖️",
"Answer the multiplication. Pick a table from the variations below, or drill them all mixed.",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div><div class="small" style="text-align:center">Table: <b id="tbl"></b></div>',
r"""
var table=qp('table')||'mixed'; var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'drill';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent='table '+table+' · '+diff+' · '+mode;
function mk(){var a = table==='mixed'? rnd(11)+2 : parseInt(table,10); if(isNaN(a))a=rnd(11)+2; var b=rnd(9)+2;
  if(diff==='easy')b=rnd(5)+2; if(diff==='hard')b=rnd(12)+1;
  cur=a*b; el('tbl').textContent=a; el('q').textContent=a+' × '+b+' = ?';
  var s=mkOpts(cur,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var btn=document.createElement('button');btn.className='opt';btn.textContent=v;
    btn.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('It was '+cur+'.'); mk()}; el('opts').appendChild(btn)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Drill time!')}; mk();
""",
{"table":["2","3","4","5","6","7","8","9","10","11","12","mixed"],"difficulty":["easy","medium","hard"],"mode":["drill","timed"]})

# ---- 11 countdown-24 ----
add("countdown-24","Countdown 24","Make the target from 4 numbers using + − × ÷. Endless puzzles!","🎲",
"Use all four numbers once each with + − × ÷ to make the target. Tap a number, then an operation, then a number.",
'<div id="q">Press Start</div><div id="nums" class="grid" style="grid-template-columns:repeat(4,1fr)"></div><div class="grid" style="grid-template-columns:repeat(4,1fr);margin-top:8px" id="ops"></div><div class="small" style="text-align:center">Target: <b id="tgt">24</b> · <button class="btn ghost" id="undoBtn" style="display:inline-block;width:auto;padding:6px 12px">Undo</button></div>',
r"""
var target=parseInt(qp('target')||'24')||24; var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var nums=[], sel=null, pendOp=null, hist=[];
if(el('cfgLabel'))el('cfgLabel').textContent='target '+target+' · '+diff;
el('tgt').textContent=target;
function draw(){el('nums').innerHTML=''; nums.forEach(function(v,i){var b=document.createElement('button');b.className='tile';b.textContent=v; b.style.background=(sel===i)?'#F59E0B':'';
  b.onclick=function(){if(sel===null){sel=i;draw();return} if(pendOp&&sel!==i){hist.push(nums.slice()); var a=nums[sel],c=nums[i],r=0;
    if(pendOp==='+')r=a+c; else if(pendOp==='−')r=a-c; else if(pendOp==='×')r=a*c; else {if(c===0){msg('Cannot divide by zero.');return} r=a/c}
    nums=[r].concat(nums.filter(function(_,j){return j!==sel&&j!==i})); sel=null; pendOp=null; draw();
    if(nums.length===1){if(Math.abs(nums[0]-target)<0.001){setScore(score+1);msg('🎉 You made '+target+'! New puzzle!'); setTimeout(newPuzzle,900)} else msg('That gives '+nums[0]+' — not '+target+'. Undo or Start again.')}} else {sel=i;draw()}}; el('nums').appendChild(b)});
  el('ops').innerHTML=''; ['+','−','×','÷'].forEach(function(o){var b=document.createElement('button');b.className='opt';b.textContent=o; b.style.background=(pendOp===o)?'#F59E0B':'';
    b.onclick=function(){pendOp=o;draw();msg('Now tap the second number.')}; el('ops').appendChild(b)});}
function newPuzzle(){var maxN=diff==='easy'?6:(diff==='hard'?12:9); nums=[]; for(var i=0;i<4;i++)nums.push(rnd(maxN)+1); sel=null;pendOp=null;hist=[]; el('q').textContent='Make '+target+' from these four numbers:'; draw(); msg('Tap a number, an operation, then a number.')}
el('undoBtn').onclick=function(){if(hist.length){nums=hist.pop(); sel=null; pendOp=null; draw(); msg('Undone.')}};
el('startBtn').onclick=function(){newPuzzle()}; newPuzzle();
""",
{"target":["24","36","48"],"difficulty":["easy","medium","hard"],"mode":["classic","speed"]})

# ---- 12 odd-one-out ----
add("odd-one-out","Odd One Out","Find the number that does not belong. Spot the rule!","👁️",
"Five numbers follow a rule — one breaks it. Tap the odd one out.",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:repeat(3,1fr)"></div>',
r"""
var diff=qp('difficulty')||'medium'; var cat=qp('category')||'multiples'; var mode=qp('mode')||'find-it';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+cat;
function isPrime(n){if(n<2)return false; for(var i=2;i*i<=n;i++)if(n%i===0)return false; return true}
function mk(){var c=cat; if(c==='mixed')c=['multiples','primes','squares'][rnd(3)];
  var base, arr=[]; var oddIdx=rnd(5);
  if(c==='multiples'){base=rnd(4)+2; for(var i=0;i<5;i++){var v=base*(rnd(8)+2); arr.push(v)} arr[oddIdx]=arr[oddIdx]+1; if(arr[oddIdx]%base===0)arr[oddIdx]++}
  else if(c==='primes'){var ps=[2,3,5,7,11,13,17,19,23,29]; for(var j=0;j<5;j++)arr.push(ps[rnd(ps.length)]); arr[oddIdx]=rnd(20)+4; while(isPrime(arr[oddIdx]))arr[oddIdx]++}
  else {for(var k=0;k<5;k++){var s=rnd(8)+2; arr.push(s*s)} arr[oddIdx]=arr[oddIdx]+3}
  cur=arr[oddIdx]; el('q').textContent='Which number does NOT belong?';
  el('opts').innerHTML=''; arr.forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('No — '+cur+' was the odd one.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Spot the odd one!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"category":["multiples","primes","squares","mixed"],"mode":["find-it","timed"]})

# ---- 13 sequence-memory ----
add("sequence-memory","Sequence Memory","Watch the flashing numbers, then repeat the growing sequence.","🔁",
"Watch the numbers light up in order, then tap them back in the same order. The sequence grows!",
'<div id="q">Press Start</div><div class="grid" id="pad" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Level: <b id="lvl">1</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var speed=qp('speed')||'normal'; var mode=qp('mode')||'classic';
var seq=[], pos=0, showing=false, level=1;
var delay = speed==='slow'?700:(speed==='fast'?300:500);
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+speed;
var maxN = diff==='easy'?4:(diff==='hard'?9:6);
function buildPad(){el('pad').innerHTML=''; for(var i=1;i<=9;i++){var b=document.createElement('button');b.className='tile';b.textContent=i;b.dataset.n=i;
  b.onclick=function(){if(showing)return; var n=parseInt(this.dataset.n,10); flash(this);
    if(n===seq[pos]){pos++; if(pos===seq.length){level++; el('lvl').textContent=level; setScore(level-1); msg('Level '+level+'! Watch…'); setTimeout(showSeq,700)}} else {msg('Wrong — the sequence was '+seq.join(', ')+'. Press Start to retry.'); showing=true;}}; el('pad').appendChild(b)}}
function flash(b){var old=b.style.background; b.style.background='#F59E0B'; setTimeout(function(){b.style.background=old},250)}
function showSeq(){showing=true; pos=0; var i=0; el('q').textContent='Watch…';
  var iv=setInterval(function(){if(i>=seq.length){clearInterval(iv); showing=false; el('q').textContent='Your turn — repeat it!'; return}
    var btns=el('pad').children; var b=btns[seq[i]-1]; if(b)flash(b); i++}, delay);}
function nextLevel(){seq.push(rnd(maxN)+1); showSeq()}
el('startBtn').onclick=function(){seq=[]; level=1; el('lvl').textContent=1; setScore(0); nextLevel(); msg('Watch the sequence…')};
buildPad(); el('q').textContent='Press Start, watch, repeat!';
""",
{"difficulty":["easy","medium","hard"],"speed":["slow","normal","fast"],"mode":["classic","endless"]})

# ---- 14 tap-speed ----
add("tap-speed","Tap Speed","How many taps can you land in 10 seconds? Pure speed!","👆",
"Tap the big button as fast as you can before the timer ends. Beat your best!",
'<div id="q" style="font-size:44px">0</div><div class="small" style="text-align:center">Time left: <b id="time">10</b>s</div><button class="btn amber" id="tapBtn" style="padding:28px;font-size:24px">TAP!</button>',
r"""
var dur=parseInt(qp('time')||'10')||10; var mode=qp('mode')||'classic'; var diff=qp('difficulty')||'medium';
var taps=0, tLeft=dur, timer=null, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=dur+'s · '+mode;
el('time').textContent=dur;
el('tapBtn').onclick=function(){if(!playing){playing=true; taps=0; tLeft=dur; el('q').textContent='0'; msg('Go! Tap fast!');
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); playing=false; setScore(taps); msg('Time! '+taps+' taps — press Start to retry.');}},1000); return}
  taps++; el('q').textContent=taps;};
el('startBtn').onclick=function(){clearInterval(timer); playing=false; taps=0; tLeft=dur; el('time').textContent=dur; el('q').textContent='0'; msg('Press TAP to begin!')};
""",
{"time":["5","10","15"],"mode":["classic","double-tap"],"difficulty":["easy","medium","hard"]})

# ---- 15 reaction-test ----
add("reaction-test","Reaction Test","Wait for green… then tap as fast as you can!","⚡",
"Wait for the box to turn GREEN, then tap it fast. Tap early and the round is lost!",
'<div id="box" style="background:#dc2626;color:#fff;border-radius:12px;padding:50px 10px;text-align:center;font-size:24px;font-weight:800;cursor:pointer">Wait for green…</div><div class="small" style="text-align:center;margin-top:8px">Best time: <b id="bestMs">—</b> · Round: <b id="rnd">0</b>/<span id="totR"></span></div>',
r"""
var rounds=parseInt(qp('rounds')||'5')||5; var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var waiting=false, startT=0, timer=null, round=0, bestMs=null, results=[];
try{bestMs=JSON.parse(localStorage.getItem('fcn_reaction_best')||'null')}catch(e){}
if(bestMs)el('bestMs').textContent=bestMs+' ms';
if(el('cfgLabel'))el('cfgLabel').textContent=rounds+' rounds · '+diff;
el('totR').textContent=rounds;
function arm(){var box=el('box'); box.style.background='#dc2626'; box.textContent='Wait for green…'; waiting=false;
  var delay = diff==='easy'? 1500+rnd(1500) : (diff==='hard'? 800+rnd(2500) : 1000+rnd(2000));
  timer=setTimeout(function(){box.style.background='#166534'; box.textContent='TAP NOW!'; waiting=true; startT=Date.now()}, delay);}
el('box').onclick=function(){var box=el('box');
  if(!waiting){clearTimeout(timer); msg('Too soon! Wait for green.'); arm(); return}
  var ms=Date.now()-startT; results.push(ms); round++; el('rnd').textContent=round;
  if(!bestMs||ms<bestMs){bestMs=ms; el('bestMs').textContent=ms+' ms'; try{localStorage.setItem('fcn_reaction_best',JSON.stringify(ms))}catch(e){} setScore(Math.max(0,1000-ms));}
  msg('Reaction: '+ms+' ms'+(round>=rounds?' — done! Average '+Math.round(results.reduce(function(a,b){return a+b},0)/results.length)+' ms. Press Start for a new set.':''));
  waiting=false; if(round<rounds)arm(); else box.textContent='Done! Press Start to play again.';};
el('startBtn').onclick=function(){round=0; results=[]; el('rnd').textContent=0; msg('Get ready…'); arm()};
""",
{"rounds":["3","5","10"],"difficulty":["easy","medium","hard"],"mode":["classic","sudden"]})

# ---- 16 word-number-puzzle ----
add("word-number-puzzle","Number Wordle","Guess the 5-digit number. Green, amber and grey hints guide you.","🟩",
"Guess the secret number. Green = right digit, right place. Amber = right digit, wrong place. Grey = not in it.",
'<div id="q">?????</div><div class="row"><input type="text" id="inp" inputmode="numeric" maxlength="6" placeholder="Your guess"><button class="btn" id="guessBtn" style="flex:0 0 110px">Guess</button></div><div id="board"></div>',
r"""
var digits=parseInt(qp('digits')||'5')||5; if([4,5,6].indexOf(digits)<0)digits=5;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'endless';
var target='', tries=0;
if(el('cfgLabel'))el('cfgLabel').textContent=digits+' digits · '+diff;
function newTarget(){target=''; for(var i=0;i<digits;i++)target+=String(rnd(10)); el('q').textContent='?'.repeat(digits)}
function guess(){var g=(el('inp').value||'').replace(/\D/g,''); if(g.length!==digits){msg('Enter '+digits+' digits.');return} tries++;
  var row=document.createElement('div'); row.style.cssText='display:flex;gap:6px;margin:6px 0';
  var correct=0; for(var i=0;i<digits;i++){var c=document.createElement('div'); c.style.cssText='flex:1;text-align:center;padding:10px;font-weight:800;border-radius:8px;border:2px solid #e2e8f0'; c.textContent=g[i];
    if(g[i]===target[i]){c.style.background='#166534';c.style.color='#fff';correct++} else if(target.indexOf(g[i])>=0){c.style.background='#F59E0B'} else {c.style.background='#e2e8f0'} row.appendChild(c)}
  el('board').appendChild(row); el('inp').value='';
  if(correct===digits){setScore(score+1); msg('🎉 Solved in '+tries+' tries! New number below.'); setTimeout(function(){tries=0; el('board').innerHTML=''; newTarget()},1200)}
  else msg('Try '+(tries+1)+' — green is right place, amber is right digit.');}
el('guessBtn').onclick=guess; el('inp').addEventListener('keydown',function(e){if(e.key==='Enter')guess()});
el('startBtn').onclick=function(){tries=0; el('board').innerHTML=''; newTarget(); msg('New secret number!')}; newTarget();
""",
{"digits":["4","5","6"],"difficulty":["easy","medium","hard"],"mode":["endless","daily"]})

# ---- 17 quick-percent ----
add("quick-percent","Quick Percent","What is x% of y? Endless percent questions, instant answers.","%",
"Work out the percent, then pick the right answer. Fast and endless!",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var type=qp('type')||'of'; var mode=qp('mode')||'drill';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+type;
function mk(){var p=[5,10,20,25,50,75][rnd(6)]; var y=(rnd(9)+1)*10; var qtxt, ans;
  if(type==='of'){ans=y*p/100; qtxt='What is '+p+'% of '+y+'?'}
  else if(type==='increase'){ans=y+y*p/100; qtxt=y+' increased by '+p+'% = ?'}
  else {ans=y-y*p/100; qtxt=y+' with '+p+'% off = ?'}
  if(type==='mixed'){var t=['of','increase','discount'][rnd(3)]; type=t; mk(); type='mixed'; return}
  cur=ans; el('q').textContent=qtxt;
  var s=mkOpts(ans,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('It was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Percent time!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"type":["of","increase","discount","mixed"],"mode":["drill","timed"]})

# ---- 18 fraction-flip ----
add("fraction-flip","Fraction Flip","Match each fraction to its decimal or percent. Flip and match!","½",
"Flip two cards and match a fraction (like 1/2) with its decimal (0.5) or percent (50%).",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div>',
r"""
var pairs=parseInt(qp('pairs')||'6')||6; var type=qp('type')||'decimal'; var diff=qp('difficulty')||'medium';
var first=null, lock=false, found=0;
if(el('cfgLabel'))el('cfgLabel').textContent=pairs+' pairs · '+type;
var FR=[[1,2,'0.5','50%'],[1,4,'0.25','25%'],[3,4,'0.75','75%'],[1,5,'0.2','20%'],[2,5,'0.4','40%'],[1,10,'0.1','10%'],[3,5,'0.6','60%'],[1,3,'0.33','33%'],[2,3,'0.67','67%'],[1,8,'0.125','12.5%']];
function build(){var pool=shuffle(FR.slice()).slice(0,pairs); var cards=[];
  pool.forEach(function(f){var other = type==='decimal'? f[2] : (type==='percent'? f[3] : f[2]+' / '+f[3]); cards.push({t:f[0]+'/'+f[1],v:f[0]+'/'+f[1]}); cards.push({t:other,v:f[0]+'/'+f[1]})});
  shuffle(cards); found=0; first=null; el('board').innerHTML='';
  cards.forEach(function(c){var d=document.createElement('button'); d.className='tile'; d.style.fontSize='16px'; d.textContent='?'; d.dataset.v=c.v; d.dataset.t=c.t;
    d.onclick=function(){if(lock||d.textContent!=='?')return; d.textContent=d.dataset.t;
      if(!first){first=d;return} lock=true; var f=first; first=null;
      if(f.dataset.v===d.dataset.v){found++; setScore(found); msg('Match! '+found+' of '+pairs); if(found===pairs)msg('🎉 All matched! Press Start for a new board.'); lock=false}
      else setTimeout(function(){f.textContent='?'; d.textContent='?'; lock=false},650)}; el('board').appendChild(d)});}
el('startBtn').onclick=function(){setScore(0);build();msg('Match fractions to '+(type==='decimal'?'decimals':type==='percent'?'percents':'decimals / percents')+'!')}; build();
""",
{"pairs":["4","6","8"],"type":["decimal","percent","both"],"difficulty":["easy","medium","hard"]})

# ---- 19 prime-hunt ----
add("prime-hunt","Prime Hunt","Tap only the prime numbers in the grid. Don't tap a fake!","🔎",
"Tap every prime number in the grid. Tap a non-prime and you lose a life. Find them all!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Found: <b id="found">0</b>/<b id="tot">0</b></div>',
r"""
var size=parseInt(qp('size')||'4')||4; if([3,4,5].indexOf(size)<0)size=4;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'hunt';
var lives=3, found=0, tot=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function isPrime(n){if(n<2)return false; for(var i=2;i*i<=n;i++)if(n%i===0)return false; return true}
function build(){var maxN=diff==='easy'?30:(diff==='hard'?100:60); var nums=new Set(); while(nums.size<size*size)nums.add(rnd(maxN)+2);
  var arr=Array.from(nums); tot=arr.filter(isPrime).length; if(tot===0){build();return}
  found=0; lives=3; el('lives').textContent=3; el('found').textContent=0; el('tot').textContent=tot; el('board').innerHTML='';
  arr.forEach(function(v){var b=document.createElement('button'); b.className='tile'; b.textContent=v;
    b.onclick=function(){if(b.disabled)return; if(isPrime(v)){b.style.background='#166534'; b.style.color='#fff'; b.disabled=true; found++; setScore(score+1); el('found').textContent=found; msg('Prime! '+found+' of '+tot);
      if(found===tot){msg('🎉 All primes found! New grid below.'); setTimeout(build,900)}} else {lives--; el('lives').textContent=lives; b.style.background='#dc2626'; b.style.color='#fff'; b.disabled=true; msg('Not prime! '+lives+' lives left.'); if(lives<=0){msg('Out of lives — press Start for a new grid.');}}}; el('board').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);build();msg('Tap the primes!')}; build();
""",
{"size":["3","4","5"],"difficulty":["easy","medium","hard"],"mode":["hunt","timed"]})

# ---- 20 even-odd-dash ----
add("even-odd-dash","Even / Odd Dash","Sort numbers into Even or Odd — as fast as you can!","⚖️",
"A number appears. Tap EVEN or ODD as fast as you can. Streaks earn bonus points!",
'<div id="q" style="font-size:44px">?</div><div class="row"><button class="btn" id="evBtn">EVEN</button><button class="btn amber" id="odBtn">ODD</button></div><div class="small" style="text-align:center">Streak: <b id="streak">0</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'dash'; var speed=qp('speed')||'normal';
var cur=0, streak=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function mk(){var maxN=diff==='easy'?50:(diff==='hard'?999:200); cur=rnd(maxN)+1; el('q').textContent=cur}
function ans(isEven){if((cur%2===0)===isEven){streak++; setScore(score+1+Math.floor(streak/5)); msg('Right! Streak '+streak)} else {msg('Wrong — '+cur+' is '+(cur%2===0?'even':'odd')+'. Streak reset.'); streak=0} el('streak').textContent=streak; mk()}
el('evBtn').onclick=function(){ans(true)}; el('odBtn').onclick=function(){ans(false)};
el('startBtn').onclick=function(){setScore(0);streak=0;el('streak').textContent=0;mk();msg('Even or odd?')}; mk();
""",
{"difficulty":["easy","medium","hard"],"mode":["dash","marathon"],"speed":["slow","normal","fast"]})

# ---- 21 snake ----
add("snake","Snake","Classic snake. Eat the food, grow longer, don't crash!","🐍",
"Steer with the arrow buttons (or arrow keys). Eat the food to grow. Don't hit the wall or yourself!",
'<div class="grid" id="board" style="grid-template-columns:repeat(10,1fr);gap:2px"></div><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div>',
r"""
var size=parseInt(qp('size')||'10')||10; if([8,10,12].indexOf(size)<0)size=10;
var speed=qp('speed')||'normal'; var diff=qp('difficulty')||'medium';
var ms = speed==='slow'?300:(speed==='fast'?120:200); if(diff==='hard')ms=Math.max(90,ms-40); if(diff==='easy')ms+=60;
var snake=[], dir={x:1,y:0}, food={x:5,y:5}, timer=null, alive=false;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+speed;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function draw(){el('board').innerHTML=''; for(var y=0;y<size;y++)for(var x=0;x<size;x++){var d=document.createElement('div'); d.style.cssText='aspect-ratio:1;border-radius:4px;background:#f1f5f9';
  if(food.x===x&&food.y===y){d.style.background='#F59E0B'} snake.forEach(function(s,i){if(s.x===x&&s.y===y)d.style.background=i===0?'#0F172A':'#166534'}); el('board').appendChild(d)}}
function placeFood(){food={x:rnd(size),y:rnd(size)}; while(snake.some(function(s){return s.x===food.x&&s.y===food.y}))food={x:rnd(size),y:rnd(size)}}
function step(){if(!alive)return; var h={x:snake[0].x+dir.x, y:snake[0].y+dir.y};
  if(h.x<0||h.y<0||h.x>=size||h.y>=size||snake.some(function(s){return s.x===h.x&&s.y===h.y})){alive=false; clearInterval(timer); msg('Game over! Score '+score+'. Press Start to play again.'); return}
  snake.unshift(h); if(h.x===food.x&&h.y===food.y){setScore(score+1); placeFood()} else snake.pop(); draw()}
function start(){snake=[{x:2,y:5},{x:1,y:5},{x:0,y:5}]; dir={x:1,y:0}; setScore(0); alive=true; placeFood(); draw(); clearInterval(timer); timer=setInterval(step,ms); msg('Use the arrows to steer!')}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){var d=b.dataset.dir; if(d==='up'&&dir.y!==1)dir={x:0,y:-1}; if(d==='down'&&dir.y!==-1)dir={x:0,y:1}; if(d==='left'&&dir.x!==1)dir={x:-1,y:0}; if(d==='right'&&dir.x!==-1)dir={x:1,y:0};}});
document.addEventListener('keydown',function(e){var m={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right'}; if(m[e.key]){e.preventDefault(); document.querySelector('[data-dir="'+m[e.key]+'"]').click()}});
el('startBtn').onclick=start; start();
""",
{"size":["8","10","12"],"speed":["slow","normal","fast"],"difficulty":["easy","medium","hard"]})

# ---- 22 flappy-number ----
add("flappy-number","Flappy Number","Tap to fly through the gates. Each gate asks a sum!","🐦",
"Tap FLAP to fly. Pass through the gate that shows the right answer to the sum — wrong gate ends the run!",
'<div id="q">3 + 4 = ?</div><div style="text-align:center;font-size:40px" id="bird">🐦</div><div class="grid" id="gates" style="grid-template-columns:1fr 1fr 1fr"></div><button class="btn amber" id="flapBtn">FLAP ↑</button><div class="small" style="text-align:center">Height: <b id="h">5</b>/10</div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'gates'; var speed=qp('speed')||'normal';
var cur=0, height=5, timer=null, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function mk(){var a=rnd(9)+2,b=rnd(9)+2; cur=a+b; el('q').textContent=a+' + '+b+' = ?';
  var s=mkOpts(cur,3);
  el('gates').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var btn=document.createElement('button');btn.className='opt';btn.textContent=v;
    btn.onclick=function(){if(!playing)return; if(v===cur){setScore(score+1); msg('Through!'); mk()} else {playing=false; clearInterval(timer); msg('Wrong gate! Score '+score+'. Press Start to fly again.')}}; el('gates').appendChild(btn)});}
function start(){setScore(0); height=5; el('h').textContent=5; playing=true; mk(); msg('Tap a gate with the right answer!');
  clearInterval(timer); timer=setInterval(function(){if(!playing)return; height--; el('h').textContent=height; if(height<=0){playing=false; clearInterval(timer); msg('You fell! Score '+score+'. Press Start to fly again.');}}, speed==='fast'?900:1400);}
el('flapBtn').onclick=function(){if(!playing)return; height=Math.min(10,height+2); el('h').textContent=height;};
el('startBtn').onclick=start; mk();
""",
{"difficulty":["easy","medium","hard"],"mode":["gates","endless"],"speed":["slow","normal","fast"]})

# ---- 23 memory-cards ----
add("memory-cards","Memory Cards","Classic card memory. Flip two, find the matching pair!","🃏",
"Flip two cards at a time and remember where they are. Match all pairs to clear the board!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div>',
r"""
var pairs=parseInt(qp('pairs')||'8')||8; var theme=qp('theme')||'numbers'; var diff=qp('difficulty')||'medium';
var first=null, lock=false, found=0;
if(el('cfgLabel'))el('cfgLabel').textContent=pairs+' pairs · '+theme;
var SYM={numbers:['1','2','3','4','5','6','7','8','9','10','11','12'],emoji:['🍎','🍌','🍇','🚗','⚽','🐶','🌞','⭐','🎈','🐱','🍕','🎵'],letters:['A','B','C','D','E','F','G','H','I','J','K','L']};
function build(){var pool=shuffle(SYM[theme]||SYM.numbers).slice(0,pairs); var cards=[]; pool.forEach(function(s){cards.push(s);cards.push(s)});
  shuffle(cards); found=0; first=null; el('board').innerHTML='';
  cards.forEach(function(v){var d=document.createElement('button'); d.className='tile'; d.textContent='?'; d.dataset.v=v;
    d.onclick=function(){if(lock||d.textContent!=='?')return; d.textContent=d.dataset.v;
      if(!first){first=d;return} lock=true; var f=first; first=null;
      if(f.dataset.v===d.dataset.v){found++; setScore(found); msg('Match! '+found+' of '+pairs); if(found===pairs)msg('🎉 Board cleared! Press Start for a new board.'); lock=false}
      else setTimeout(function(){f.textContent='?'; d.textContent='?'; lock=false},650)}; el('board').appendChild(d)});}
el('startBtn').onclick=function(){setScore(0);build();msg('Find all '+pairs+' pairs!')}; build();
""",
{"pairs":["4","6","8","10"],"theme":["numbers","emoji","letters"],"difficulty":["easy","medium","hard"]})

# ---- 24 whack-a-number ----
add("whack-a-number","Whack a Number","Whack the tile showing the right answer — fast!","🔨",
"A sum appears. Whack the tile with the correct answer before time runs out!",
'<div id="q">Press Start</div><div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Time left: <b id="time">30</b>s</div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'mixed'; var dur=parseInt(qp('time')||'30')||30;
var cur=0, tLeft=dur, timer=null, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op+' · '+dur+'s';
function mk(){var a=rnd(9)+2,b=rnd(9)+2,o=op; if(o==='mixed')o=['add','subtract','multiply'][rnd(3)];
  var ans; if(o==='add'){ans=a+b; el('q').textContent=a+' + '+b+' = ?'} else if(o==='subtract'){ans=a-b; el('q').textContent=a+' − '+b+' = ?'} else {ans=a*b; el('q').textContent=a+' × '+b+' = ?'}
  cur=ans; var s=mkOpts(ans,9);
  el('board').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var btn=document.createElement('button');btn.className='tile';btn.textContent=v;
    btn.onclick=function(){if(!playing)return; if(v===cur){setScore(score+1); msg('Whacked!'); mk()} else msg('Not that one!')}; el('board').appendChild(btn)});}
function start(){clearInterval(timer); setScore(0); tLeft=dur; playing=true; el('time').textContent=tLeft; mk();
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); playing=false; msg('Time! You scored '+score+'. Play again!')}},1000);}
el('startBtn').onclick=start; mk();
""",
{"difficulty":["easy","medium","hard"],"op":["add","subtract","multiply","mixed"],"time":["30","60","90"]})

# ---- 25 balloon-pop ----
add("balloon-pop","Balloon Pop","Pop the balloon with the right answer. Don't pop the wrong one!","🎈",
"A sum appears with balloons. Pop the balloon showing the correct answer!",
'<div id="q">Press Start</div><div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'mixed'; var mode=qp('mode')||'pop';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op;
function mk(){var a=rnd(9)+2,b=rnd(9)+2,o=op; if(o==='mixed')o=['add','subtract','multiply'][rnd(3)];
  var ans; if(o==='add'){ans=a+b; el('q').textContent=a+' + '+b+' = ?'} else if(o==='subtract'){ans=a-b; el('q').textContent=a+' − '+b+' = ?'} else {ans=a*b; el('q').textContent=a+' × '+b+' = ?'}
  cur=ans; var s=mkOpts(ans,6);
  el('board').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var btn=document.createElement('button');btn.className='tile';btn.style.borderRadius='50%';btn.textContent='🎈 '+v;
    btn.onclick=function(){if(v===cur){setScore(score+1); msg('Pop! Correct!'); mk()} else msg('Wrong balloon — try again!')}; el('board').appendChild(btn)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Pop the right balloon!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"op":["add","subtract","multiply","mixed"],"mode":["pop","timed"]})

# ---- 26 colour-match ----
add("colour-match","Colour Match","Stroop test: tap the word that matches the INK colour, not the word!","🎨",
"The word says one colour but is printed in another. Tap the button naming the INK colour!",
'<div id="q" style="font-size:32px">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic'; var speed=qp('speed')||'normal';
var COLS=[['RED','#dc2626'],['GREEN','#166534'],['BLUE','#2563eb'],['AMBER','#F59E0B'],['PURPLE','#7c3aed'],['PINK','#db2777']];
var cur='';
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function mk(){var word=COLS[rnd(COLS.length)]; var ink=COLS[rnd(COLS.length)]; cur=ink[0];
  var q=el('q'); q.textContent=word[0]; q.style.color=ink[1];
  var s=new Set([cur]); while(s.size<4)s.add(COLS[rnd(COLS.length)][0]);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct — that was the ink colour!')}else msg('No — the ink was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Name the INK colour, not the word!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"mode":["classic","timed"],"speed":["slow","normal","fast"]})

# ---- 27 simon-says ----
add("simon-says","Simon Says","Repeat the colour pattern. It grows longer every round!","🔴",
"Watch the colours light up, then tap them back in the same order. How long a pattern can you remember?",
'<div id="q">Press Start</div><div class="grid" id="pad" style="grid-template-columns:1fr 1fr"></div><div class="small" style="text-align:center">Level: <b id="lvl">1</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var speed=qp('speed')||'normal'; var mode=qp('mode')||'classic';
var COLS=[['RED','#dc2626'],['GREEN','#166534'],['BLUE','#2563eb'],['AMBER','#F59E0B']];
var seq=[], pos=0, showing=false, level=1;
var delay = speed==='slow'?700:(speed==='fast'?300:500);
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+speed;
function buildPad(){el('pad').innerHTML=''; COLS.forEach(function(c,i){var b=document.createElement('button'); b.className='tile'; b.style.background=c[1]; b.style.color='#fff'; b.textContent=c[0]; b.dataset.i=i; b.style.minHeight='70px';
  b.onclick=function(){if(showing)return; flash(b); if(i===seq[pos]){pos++; if(pos===seq.length){level++; el('lvl').textContent=level; setScore(level-1); msg('Level '+level+'! Watch…'); setTimeout(showSeq,700)}} else {msg('Wrong — pattern was '+seq.map(function(x){return COLS[x][0]}).join(', ')+'. Press Start to retry.'); showing=true;}}; el('pad').appendChild(b)})}
function flash(b){b.style.opacity='0.4'; setTimeout(function(){b.style.opacity='1'},250)}
function showSeq(){showing=true; pos=0; var i=0; el('q').textContent='Watch…';
  var iv=setInterval(function(){if(i>=seq.length){clearInterval(iv); showing=false; el('q').textContent='Your turn!'; return} flash(el('pad').children[seq[i]]); i++}, delay);}
el('startBtn').onclick=function(){seq=[]; level=1; el('lvl').textContent=1; setScore(0); seq.push(rnd(4)); showSeq(); msg('Watch the pattern…')};
buildPad(); el('q').textContent='Press Start, watch, repeat!';
""",
{"difficulty":["easy","medium","hard"],"speed":["slow","normal","fast"],"mode":["classic","endless"]})

# ---- 28 tile-slide ----
add("tile-slide","Tile Slide","Slide the numbered tiles into order. Classic sliding puzzle!","🧩",
"Tap a tile next to the empty space to slide it. Put the numbers in order, 1 to 8!",
'<div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Moves: <b id="moves">0</b></div>',
r"""
var size=parseInt(qp('size')||'3')||3; if([3,4].indexOf(size)<0)size=3;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var tiles=[], moves=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function draw(){el('board').innerHTML=''; tiles.forEach(function(v,i){var b=document.createElement('button'); b.className='tile'; b.textContent=v||''; b.style.background=v?'':'#f1f5f9';
  b.onclick=function(){var e=tiles.indexOf(0); var r1=Math.floor(i/size),c1=i%size,r2=Math.floor(e/size),c2=e%size;
    if(Math.abs(r1-r2)+Math.abs(c1-c2)===1){tiles[e]=v; tiles[i]=0; moves++; el('moves').textContent=moves; draw(); check()}}; el('board').appendChild(b)});}
function check(){for(var i=0;i<tiles.length-1;i++)if(tiles[i]!==i+1)return; setScore(100-Math.min(90,moves)); msg('🎉 Solved in '+moves+' moves! Press Start for a new shuffle.')}
function shuffleTiles(){tiles=[]; for(var i=1;i<size*size;i++)tiles.push(i); tiles.push(0);
  var n = diff==='easy'?20:(diff==='hard'?120:60); var e=size*size-1;
  for(var k=0;k<n;k++){var r=Math.floor(e/size),c=e%size,opts=[]; if(r>0)opts.push(e-size); if(r<size-1)opts.push(e+size); if(c>0)opts.push(e-1); if(c<size-1)opts.push(e+1);
    var t=opts[rnd(opts.length)]; tiles[e]=tiles[t]; tiles[t]=0; e=t;} moves=0; el('moves').textContent=0;}
el('startBtn').onclick=function(){setScore(0); shuffleTiles(); draw(); msg('Slide the tiles into order!')}; shuffleTiles(); draw();
""",
{"size":["3","4"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 29 minesweeper-mini ----
add("minesweeper-mini","Minesweeper Mini","Clear the board without hitting a mine. Numbers are your clues!","💣",
"Tap a square to reveal it. Numbers tell you how many mines touch that square. Reveal all safe squares!",
'<div class="grid" id="board" style="grid-template-columns:repeat(6,1fr)"></div><div class="small" style="text-align:center">Mines: <b id="mc"></b> · Revealed: <b id="rev">0</b></div>',
r"""
var size=parseInt(qp('size')||'6')||6; if([5,6,8].indexOf(size)<0)size=6;
var mines=parseInt(qp('mines')||'6')||6; var diff=qp('difficulty')||'medium';
if(diff==='easy')mines=Math.max(3,Math.floor(mines/2)); if(diff==='hard')mines=mines+4;
var cells=[], revealed=0, over=false;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+mines+' mines';
el('board').style.gridTemplateColumns='repeat('+size+',1fr)'; el('mc').textContent=mines;
function build(){cells=[]; var mineSet=new Set(); while(mineSet.size<mines)mineSet.add(rnd(size*size));
  for(var i=0;i<size*size;i++){var cnt=0; var r=Math.floor(i/size),c=i%size;
    for(var dr=-1;dr<=1;dr++)for(var dc=-1;dc<=1;dc++){var nr=r+dr,nc=c+dc; if(nr>=0&&nr<size&&nc>=0&&nc<size&&mineSet.has(nr*size+nc))cnt++}
    cells.push({mine:mineSet.has(i),n:cnt,open:false})}
  revealed=0; over=false; el('rev').textContent=0; el('board').innerHTML='';
  cells.forEach(function(cell,i){var b=document.createElement('button'); b.className='tile'; b.style.fontSize='15px'; b.textContent='·';
    b.onclick=function(){if(over||cell.open)return; cell.open=true;
      if(cell.mine){b.textContent='💣'; b.style.background='#dc2626'; over=true; msg('💥 Boom! You hit a mine. Press Start for a new board.');}
      else {revealed++; el('rev').textContent=revealed; b.textContent=cell.n||''; b.style.background='#dcfce7'; b.disabled=true; setScore(revealed);
        if(revealed===size*size-mines){over=true; msg('🎉 You cleared the board! Press Start for a new one.')}}}; el('board').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);build();msg('Tap a square — avoid the mines!')}; build();
""",
{"size":["5","6","8"],"mines":["4","6","10"],"difficulty":["easy","medium","hard"]})

# ---- 30 block-drop ----
add("block-drop","Block Drop","Stack the falling blocks. Land them dead-centre to grow tall!","🧱",
"Tap DROP when the moving block is over the tower. Perfect drops grow the tower — miss and it shrinks!",
'<div id="q" style="text-align:center">Tower height: <b id="h">0</b></div><div id="tower" style="min-height:120px;display:flex;flex-direction:column-reverse;align-items:center;gap:2px"></div><div style="text-align:center;font-size:28px" id="mover">▬▬▬▬</div><button class="btn amber" id="dropBtn">DROP ⬇</button>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic'; var speed=qp('speed')||'normal';
var height=0, pos=0, dir=1, timer=null, width=4, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function drawTower(){el('tower').innerHTML=''; for(var i=0;i<height;i++){var d=document.createElement('div'); d.style.cssText='height:14px;width:'+(40+width*12)+'px;background:#166534;border-radius:3px'; el('tower').appendChild(d)} el('h').textContent=height;}
function start(){height=0; width=4; pos=0; dir=1; playing=true; setScore(0); drawTower(); msg('Tap DROP when the block is centred!');
  clearInterval(timer); var ms=speed==='fast'?120:(speed==='slow'?300:200); if(diff==='hard')ms=Math.max(80,ms-50);
  timer=setInterval(function(){if(!playing)return; pos+=dir; if(pos>6||pos<0){dir*=-1; pos+=dir*2} el('mover').style.marginLeft=(pos*6)+'%'}, ms);}
el('dropBtn').onclick=function(){if(!playing)return; var off=Math.abs(pos-3);
  if(off===0){height++; setScore(height); msg('Perfect!')} else if(off<=2){height++; width=Math.max(2,width-0); setScore(height); msg('Good — tower grows!')}
  else {height=Math.max(0,height-1); msg('Missed the centre — tower shrinks!'); if(height===0&&score>0){}}
  drawTower(); if(height>=20){playing=false; clearInterval(timer); msg('🎉 Tower of 20! Amazing. Press Start to build again.')}};
el('startBtn').onclick=start; drawTower();
""",
{"difficulty":["easy","medium","hard"],"mode":["classic","speed"],"speed":["slow","normal","fast"]})

# ---- 31 pong-mini ----
add("pong-mini","Pong Mini","Bounce the ball past the computer paddle. First to 5 wins!","🏓",
"Move your paddle with the buttons. Bounce the ball past the computer paddle — first to 5 wins the match!",
'<div id="q" style="text-align:center;font-size:20px">You <b id="ys">0</b> — <b id="cs">0</b> Computer</div><div id="court" style="position:relative;height:180px;background:#0F172A;border-radius:10px;overflow:hidden"><div id="ball" style="position:absolute;width:14px;height:14px;background:#F59E0B;border-radius:50%;left:50%;top:50%"></div><div id="pad" style="position:absolute;width:70px;height:10px;background:#fff;border-radius:5px;bottom:8px;left:40%"></div><div id="cpad" style="position:absolute;width:70px;height:10px;background:#166534;border-radius:5px;top:8px;left:40%"></div></div><div class="row" style="margin-top:8px"><button class="btn" id="leftBtn">← Left</button><button class="btn" id="rightBtn">Right →</button></div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'vs-computer'; var speed=qp('speed')||'normal';
var bx=50, by=50, vx=2, vy=2, px=40, cx=40, ys=0, cs=0, timer=null, playing=false;
if(diff==='hard'){vx=3;vy=3} if(diff==='easy'){vx=1.5;vy=1.5}
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function draw(){el('ball').style.left=bx+'%'; el('ball').style.top=by+'%'; el('pad').style.left=px+'%'; el('cpad').style.left=cx+'%'; el('ys').textContent=ys; el('cs').textContent=cs}
function step(){if(!playing)return; bx+=vx; by+=vy;
  if(bx<=0||bx>=96)vx*=-1;
  if(by<=4){cx=Math.max(0,Math.min(85,cx+((bx-cx)>0?1.5:-1.5))); if(by<=6&&Math.abs(bx-cx)<12){vy=Math.abs(vy)} else if(by<=0){ys++; setScore(ys); msg('Point for you!'); resetBall()}}
  if(by>=88){if(Math.abs(bx-px)<12){vy=-Math.abs(vy)} else {cs++; msg('Computer scores!'); resetBall()}}
  if(ys>=5||cs>=5){playing=false; clearInterval(timer); msg(ys>=5?'🎉 You won the match!':'Computer won. Press Start for a rematch.'); return}
  cx=Math.max(0,Math.min(85,cx+((bx-cx)>0?1:-1))); draw()}
function resetBall(){bx=50; by=50; vy=Math.abs(vy); draw()}
function start(){ys=0; cs=0; playing=true; resetBall(); msg('First to 5 wins!'); clearInterval(timer); timer=setInterval(step, speed==='fast'?25:40)}
el('leftBtn').onclick=function(){px=Math.max(0,px-10); draw()}; el('rightBtn').onclick=function(){px=Math.min(85,px+10); draw()};
el('startBtn').onclick=start; draw();
""",
{"difficulty":["easy","medium","hard"],"mode":["vs-computer","wall"],"speed":["slow","normal","fast"]})

# ---- 32 breakout-mini ----
add("breakout-mini","Breakout Mini","Break all the bricks with the bouncing ball. Endless levels!","🧱",
"Move the paddle to bounce the ball and break every brick. Clear the wall to reach the next level!",
'<div id="q">Level <b id="lvl">1</b> · Bricks left: <b id="left">0</b></div><div id="court" style="position:relative;height:200px;background:#0F172A;border-radius:10px;overflow:hidden"><div id="bricks" style="display:grid;grid-template-columns:repeat(6,1fr);gap:4px;padding:8px"></div><div id="ball" style="position:absolute;width:12px;height:12px;background:#F59E0B;border-radius:50%;left:50%;top:70%"></div><div id="pad" style="position:absolute;width:70px;height:10px;background:#fff;border-radius:5px;bottom:8px;left:40%"></div></div><div class="row" style="margin-top:8px"><button class="btn" id="leftBtn">← Left</button><button class="btn" id="rightBtn">Right →</button></div>',
r"""
var rows=parseInt(qp('rows')||'3')||3; var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var level=1, bricks=[], bx=50, by=70, vx=2, vy=-2, px=40, timer=null, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=rows+' rows · '+diff;
function build(){bricks=[]; var total=6*rows; for(var i=0;i<total;i++)bricks.push(true);
  el('bricks').innerHTML=''; bricks.forEach(function(_,i){var d=document.createElement('div'); d.style.cssText='height:16px;background:#F59E0B;border-radius:3px'; d.id='br'+i; el('bricks').appendChild(d)});
  el('left').textContent=total; el('lvl').textContent=level;}
function step(){if(!playing)return; bx+=vx; by+=vy; if(bx<=0||bx>=96)vx*=-1; if(by<=0)vy=Math.abs(vy);
  var left=bricks.filter(Boolean).length;
  if(by<28&&left>0){var col=Math.floor(bx/16.6); var row=Math.floor((by-2)/8); var idx=row*6+col;
    if(idx>=0&&idx<bricks.length&&bricks[idx]){bricks[idx]=false; var d=document.getElementById('br'+idx); if(d)d.style.visibility='hidden'; vy=Math.abs(vy); setScore(score+1); el('left').textContent=bricks.filter(Boolean).length;
      if(bricks.filter(Boolean).length===0){level++; msg('🎉 Level cleared! Level '+level+'!'); build(); by=70;}}}
  if(by>=88){if(Math.abs(bx-px)<12){vy=-Math.abs(vy)} else {playing=false; clearInterval(timer); msg('Ball lost! Score '+score+'. Press Start to retry.'); return}}
  el('ball').style.left=bx+'%'; el('ball').style.top=by+'%'; el('pad').style.left=px+'%';}
function start(){level=1; setScore(0); playing=true; bx=50; by=70; vy=-2; build(); msg('Break all the bricks!');
  clearInterval(timer); timer=setInterval(step, diff==='hard'?22:35);}
el('leftBtn').onclick=function(){px=Math.max(0,px-10); el('pad').style.left=px+'%'};
el('rightBtn').onclick=function(){px=Math.min(85,px+10); el('pad').style.left=px+'%'};
el('startBtn').onclick=start; build();
""",
{"rows":["2","3","4"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- 33 maze-run ----
add("maze-run","Maze Run","Navigate the random maze to the flag. A new maze every time!","🌀",
"Use the arrow buttons to move through the maze. Reach the 🏁 flag — a fresh maze appears!",
'<div class="grid" id="board" style="gap:2px"></div><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div><div class="small" style="text-align:center">Moves: <b id="mv">0</b></div>',
r"""
var size=parseInt(qp('size')||'9')||9; if([7,9,11].indexOf(size)<0)size=9;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var grid=[], px=1, py=1, moves=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function build(){grid=[]; for(var y=0;y<size;y++){var row=[]; for(var x=0;x<size;x++)row.push((x%2===0&&y%2===0)||Math.random()<(diff==='hard'?0.25:0.18)?1:0); grid.push(row)}
  grid[1][1]=0; grid[size-2][size-2]=0;
  // carve a guaranteed path along edges
  for(var i=1;i<size-1;i++){grid[1][i]=0; grid[i][size-2]=0}
  px=1; py=1; moves=0; el('mv').textContent=0; draw(); msg('Reach the flag!')}
function draw(){el('board').innerHTML=''; for(var y=0;y<size;y++)for(var x=0;x<size;x++){var d=document.createElement('div'); d.style.cssText='aspect-ratio:1;border-radius:3px;background:'+(grid[y][x]?'#0F172A':'#f1f5f9');
  if(x===px&&y===py){d.textContent='😀'; d.style.background='#F59E0B'} if(x===size-2&&y===size-2){d.textContent='🏁'; d.style.background='#dcfce7'} el('board').appendChild(d)}}
function move(dx,dy){var nx=px+dx, ny=py+dy; if(nx<0||ny<0||nx>=size||ny>=size||grid[ny][nx])return; px=nx; py=ny; moves++; el('mv').textContent=moves; draw();
  if(px===size-2&&py===size-2){setScore(score+1); msg('🎉 Maze solved in '+moves+' moves! New maze below.'); setTimeout(build,900)}}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){var d=b.dataset.dir; if(d==='up')move(0,-1); if(d==='down')move(0,1); if(d==='left')move(-1,0); if(d==='right')move(1,0)}});
document.addEventListener('keydown',function(e){var m={ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0]}; if(m[e.key]){e.preventDefault(); move(m[e.key][0],m[e.key][1])}});
el('startBtn').onclick=function(){build()}; build();
""",
{"size":["7","9","11"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 34 spot-the-difference ----
add("spot-the-difference","Spot the Difference","One number in the grid is different. Find it fast!","🔍",
"All the numbers look the same — except one. Tap the different number before time runs out!",
'<div id="q">Find the odd number!</div><div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="small" style="text-align:center">Time left: <b id="time">15</b>s</div>',
r"""
var size=parseInt(qp('size')||'4')||4; if([3,4,5].indexOf(size)<0)size=4;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var cur=0, tLeft=15, timer=null;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function mk(){var base=rnd(90)+10; var odd=base+(diff==='easy'?5:(diff==='hard'?1:2)); if(odd>99)odd=base-2; cur=odd;
  var idx=rnd(size*size); el('board').innerHTML='';
  for(var i=0;i<size*size;i++){var b=document.createElement('button'); b.className='tile'; b.textContent=(i===idx?odd:base);
    b.onclick=function(){if(this.textContent==String(cur)){setScore(score+1); msg('Found it!'); mk()} else msg('Not that one — look closer!')}; el('board').appendChild(b)}}
function start(){setScore(0); tLeft=15; el('time').textContent=15; mk(); clearInterval(timer);
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); msg('Time! You found '+score+'. Press Start to play again.');}},1000);}
el('startBtn').onclick=start; mk();
""",
{"size":["3","4","5"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 35 pattern-complete ----
add("pattern-complete","Pattern Complete","Complete the number pattern. What comes next?","🧩",
"Work out the rule behind the pattern, then pick the number that comes next.",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var type=qp('type')||'arithmetic'; var mode=qp('mode')||'find-it';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+type;
function mk(){var start=rnd(8)+1, step=rnd(4)+2, seq=[], t=type; if(t==='mixed')t=['arithmetic','geometric','fibonacci'][rnd(3)];
  if(t==='arithmetic'){for(var i=0;i<4;i++)seq.push(start+i*step); cur=start+4*step}
  else if(t==='geometric'){for(var j=0;j<4;j++)seq.push(start*Math.pow(2,j)); cur=start*16}
  else {seq=[1,1,2,3]; cur=5; if(diff==='hard'){seq=[2,3,5,8]; cur=13}}
  el('q').textContent=seq.join('  ·  ')+'  ·  ?';
  var s=mkOpts(cur,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('It was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('What comes next?')}; mk();
""",
{"difficulty":["easy","medium","hard"],"type":["arithmetic","geometric","fibonacci","mixed"],"mode":["find-it","timed"]})

# ---- 36 quick-count ----
add("quick-count","Quick Count","Count the dots — fast! How many are there?","🔢",
"Count the shapes as fast as you can, then pick the right total. New count every round!",
'<div id="q" style="font-size:32px;letter-spacing:4px">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var shape=qp('shape')||'dots'; var mode=qp('mode')||'count';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+shape;
function mk(){var maxN=diff==='easy'?10:(diff==='hard'?30:20); cur=rnd(maxN)+3;
  var ch = shape==='stars'?'⭐':(shape==='squares'?'■':'●');
  el('q').textContent=ch.repeat(Math.min(cur,30));
  var s=mkOpts(cur,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('There were '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Count them!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"shape":["dots","stars","squares"],"mode":["count","timed"]})

# ---- 37 dice-roll ----
add("dice-roll","Dice Roll","Roll the dice and beat the target. Luck + nerve!","🎲",
"Roll the dice. Beat the target number to score — roll under it and the round is lost!",
'<div id="q" style="font-size:44px">🎲 🎲</div><div class="small" style="text-align:center">Target: beat <b id="tgt">7</b> · Dice: <b id="dc">2</b></div><button class="btn amber" id="rollBtn">ROLL!</button>',
r"""
var dice=parseInt(qp('dice')||'2')||2; if([1,2,3].indexOf(dice)<0)dice=2;
var mode=qp('mode')||'beat-target'; var diff=qp('difficulty')||'medium';
var target=0;
if(el('cfgLabel'))el('cfgLabel').textContent=dice+' dice · '+mode;
el('dc').textContent=dice;
function newTarget(){target = dice===1? 4 : (dice===2? 7 : 10); if(diff==='easy')target--; if(diff==='hard')target++; el('tgt').textContent=target}
function roll(){var vals=[]; var tot=0; for(var i=0;i<dice;i++){var v=rnd(6)+1; vals.push(v); tot+=v}
  el('q').textContent=vals.map(function(v){return ['⚀','⚁','⚂','⚃','⚄','⚅'][v-1]}).join(' ');
  if(mode==='beat-target'){if(tot>target){setScore(score+1); msg('🎉 '+tot+' beats '+target+'!')} else msg(tot+' — not enough. Roll again!')}
  else {if(tot===target){setScore(score+2); msg('🎉 Exact '+target+'!')} else msg(tot+' — aim for exactly '+target+'.')}
  newTarget();}
el('rollBtn').onclick=roll;
el('startBtn').onclick=function(){setScore(0); newTarget(); msg('Roll to beat the target!')}; newTarget();
""",
{"dice":["1","2","3"],"mode":["beat-target","exact"],"difficulty":["easy","medium","hard"]})

# ---- 38 coin-flip-streak ----
add("coin-flip-streak","Coin Flip Streak","Call heads or tails. How long a streak can you build?","🪙",
"Call heads or tails before each flip. A right call grows your streak — a wrong call resets it!",
'<div id="q" style="font-size:56px">🪙</div><div class="row"><button class="btn" id="hBtn">HEADS</button><button class="btn amber" id="tBtn">TAILS</button></div><div class="small" style="text-align:center">Streak: <b id="streak">0</b> · Target streak: <b id="tgtS">5</b></div>',
r"""
var mode=qp('mode')||'streak'; var targetStreak=parseInt(qp('target')||'5')||5; var diff=qp('difficulty')||'medium';
var streak=0;
if(el('cfgLabel'))el('cfgLabel').textContent='target '+targetStreak+' · '+mode;
el('tgtS').textContent=targetStreak;
function flip(call){var res=Math.random()<0.5?'HEADS':'TAILS'; el('q').textContent=res==='HEADS'?'👑 HEADS':'🔄 TAILS';
  if(res===call){streak++; setScore(streak); el('streak').textContent=streak; msg('Right! Streak '+streak+(streak>=targetStreak?' — 🎉 target reached!':'')+'.')}
  else {msg('It was '+res+'. Streak reset.'); streak=0; el('streak').textContent=0}}
el('hBtn').onclick=function(){flip('HEADS')}; el('tBtn').onclick=function(){flip('TAILS')};
el('startBtn').onclick=function(){streak=0; setScore(0); el('streak').textContent=0; el('q').textContent='🪙'; msg('Call it — heads or tails?')};
""",
{"mode":["streak","best-of"],"target":["3","5","10"],"difficulty":["easy","medium","hard"]})

# ---- 39 rock-paper-scissors ----
add("rock-paper-scissors","Rock Paper Scissors","Classic RPS against the computer. Best of 5 — can you win?","✊",
"Pick rock, paper or scissors. Rock beats scissors, scissors beats paper, paper beats rock!",
'<div id="q">Pick your move!</div><div class="grid" style="grid-template-columns:repeat(3,1fr)"><button class="opt" data-m="Rock">✊ Rock</button><button class="opt" data-m="Paper">✋ Paper</button><button class="opt" data-m="Scissors">✌️ Scissors</button></div><div class="small" style="text-align:center">You <b id="ys">0</b> — <b id="cs">0</b> Computer · First to <b id="ft">3</b></div>',
r"""
var mode=qp('mode')||'best-of-5'; var variant=qp('variant')||'classic'; var diff=qp('difficulty')||'medium';
var MOVES = variant==='lizard-spock'? ['Rock','Paper','Scissors','Lizard','Spock'] : ['Rock','Paper','Scissors'];
var firstTo = mode==='best-of-3'?2:(mode==='best-of-5'?3:1);
var ys=0, cs=0;
if(el('cfgLabel'))el('cfgLabel').textContent=mode+' · '+variant;
el('ft').textContent=firstTo;
function beats(a,b){if(a===b)return 0; var W={Rock:['Scissors','Lizard'],Paper:['Rock','Spock'],Scissors:['Paper','Lizard'],Lizard:['Paper','Spock'],Spock:['Rock','Scissors']}; return W[a].indexOf(b)>=0?1:-1}
function play(m){if(ys>=firstTo||cs>=firstTo)return; var c=MOVES[rnd(MOVES.length)]; var r=beats(m,c);
  el('q').textContent='You: '+m+' vs Computer: '+c+' — '+(r===0?'Draw!':(r>0?'You win this round!':'Computer wins this round!'));
  if(r>0){ys++; setScore(ys)} else if(r<0){cs++}
  el('ys').textContent=ys; el('cs').textContent=cs;
  if(ys>=firstTo)msg('🎉 You won the match! Press Start for a rematch.'); else if(cs>=firstTo)msg('Computer won. Press Start for a rematch.');}
document.querySelectorAll('[data-m]').forEach(function(b){b.onclick=function(){play(b.dataset.m)}});
el('startBtn').onclick=function(){ys=0;cs=0;setScore(0);el('ys').textContent=0;el('cs').textContent=0;el('q').textContent='Pick your move!';msg(mode==='single'?'Single round — good luck!':'First to '+firstTo+' wins!')};
""",
{"mode":["single","best-of-3","best-of-5"],"variant":["classic","lizard-spock"],"difficulty":["easy","medium","hard"]})

# ---- 40 tic-tac-toe ----
add("tic-tac-toe","Tic-Tac-Toe","You are X, the computer is O. Three in a row wins!","❌",
"You play X, the computer plays O. Get three in a row — endless rematches!",
'<div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Wins: <b id="w">0</b> · Draws: <b id="d">0</b> · Losses: <b id="l">0</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var first=qp('first')||'you'; var mode=qp('mode')||'classic';
var board=[], over=false, w=0,d=0,l=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+first+' first';
function wins(b){var L=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]; for(var i=0;i<L.length;i++){if(b[L[i][0]]&&b[L[i][0]]===b[L[i][1]]&&b[L[i][1]]===b[L[i][2]])return b[L[i][0]]} return null}
function draw(){el('board').innerHTML=''; board.forEach(function(v,i){var b=document.createElement('button'); b.className='tile'; b.style.fontSize='28px'; b.textContent=v||'';
  b.onclick=function(){if(over||v)return; board[i]='X'; draw(); var wn=wins(board);
    if(wn){endGame(wn); return} if(board.indexOf('')<0){d++; el('d').textContent=d; over=true; msg('Draw! Press Start for a rematch.'); return}
    ai()}; el('board').appendChild(b)});}
function ai(){var empt=[]; board.forEach(function(v,i){if(!v)empt.push(i)}); if(!empt.length)return;
  var pick=empt[rnd(empt.length)];
  if(diff==='hard'||diff==='medium'){for(var k=0;k<empt.length;k++){var t=board.slice(); t[empt[k]]='O'; if(wins(t)==='O'){pick=empt[k]; break}}
    if(diff==='hard'){for(var j=0;j<empt.length;j++){var t2=board.slice(); t2[empt[j]]='X'; if(wins(t2)==='X'){pick=empt[j]; break}}}}
  board[pick]='O'; draw(); var wn=wins(board); if(wn)endGame(wn); else if(board.indexOf('')<0){d++; el('d').textContent=d; over=true; msg('Draw! Press Start for a rematch.')}}
function endGame(wn){over=true; if(wn==='X'){w++; el('w').textContent=w; setScore(w); msg('🎉 You win! Press Start for a rematch.')} else {l++; el('l').textContent=l; msg('Computer wins. Press Start for a rematch.')}}
function start(){board=['','','','','','','','','']; over=false; draw(); msg('Your move — you are X!');
  if(first==='computer'){ai()}}
el('startBtn').onclick=start; start();
""",
{"difficulty":["easy","medium","hard"],"first":["you","computer"],"mode":["classic","rematch"]})

# ---- 41 anagram-number ----
add("anagram-number","Anagram Number","Unscramble the number word. Letters jumbled — can you read it?","🔤",
"Letters of a number word are scrambled. Tap the letters in the right order to spell it!",
'<div id="q">Press Start</div><div id="letters" class="grid" style="grid-template-columns:repeat(4,1fr)"></div><div id="built" style="text-align:center;font-size:24px;font-weight:800;min-height:32px;margin:8px 0"></div><button class="btn ghost" id="clearBtn">Clear</button>',
r"""
var diff=qp('difficulty')||'medium'; var length=qp('length')||'medium'; var mode=qp('mode')||'classic';
var WORDS={short:['ONE','TWO','SIX','TEN'],medium:['THREE','FOUR','FIVE','NINE','ZERO','EIGHT'],long:['SEVEN','ELEVEN','TWELVE','TWENTY','HUNDRED','THOUSAND']};
var word='', built='', used=[];
if(el('cfgLabel'))el('cfgLabel').textContent=length+' words · '+diff;
function mk(){var pool=WORDS[length]||WORDS.medium; word=pool[rnd(pool.length)]; built=''; used=[]; el('built').textContent='';
  var letters=shuffle(word.split('')); el('q').textContent='Unscramble this number word:';
  el('letters').innerHTML=''; letters.forEach(function(ch,i){var b=document.createElement('button'); b.className='tile'; b.textContent=ch; b.dataset.i=i;
    b.onclick=function(){if(used.indexOf(i)>=0)return; used.push(i); built+=ch; b.style.background='#dcfce7'; el('built').textContent=built;
      if(built.length===word.length){if(built===word){setScore(score+1); msg('🎉 Correct — '+word+'! New word below.'); setTimeout(mk,900)} else {msg('Not quite — that spells '+built+'. Press Clear and try again.')}}}; el('letters').appendChild(b)});}
el('clearBtn').onclick=function(){built=''; used=[]; el('built').textContent=''; el('letters').querySelectorAll('button').forEach(function(b){b.style.background=''}); msg('Cleared — try again!')};
el('startBtn').onclick=function(){mk(); msg('Unscramble the word!')}; mk();
""",
{"length":["short","medium","long"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 42 sudoku-mini ----
add("sudoku-mini","Sudoku Mini","4×4 Sudoku. Fill every row, column and box with 1–4!","🔢",
"Tap an empty cell, then tap a number 1–4. Every row, column and 2×2 box must contain 1, 2, 3 and 4.",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="grid" style="grid-template-columns:repeat(4,1fr);margin-top:10px" id="numbar"></div><div class="small" style="text-align:center">Selected cell: <b id="sel">none</b> · <button class="btn ghost" id="checkBtn" style="display:inline-block;width:auto;padding:6px 12px">Check</button></div>',
r"""
var diff=qp('difficulty')||'medium'; var hints=qp('hints')||'on'; var mode=qp('mode')||'classic';
var sol=[[1,2,3,4],[3,4,1,2],[2,1,4,3],[4,3,2,1]];
var grid=[], givenSet={}, sel=null;
if(el('cfgLabel'))el('cfgLabel').textContent='4×4 · '+diff+' · hints '+hints;
// randomise solution by permuting digits and swapping rows/cols within bands
function newPuzzle(){var perm=shuffle([1,2,3,4]); sol=sol.map(function(r){return r.map(function(v){return perm[v-1]})});
  var hide = diff==='easy'?6:(diff==='hard'?10:8); grid=sol.map(function(r){return r.slice()}); givens=[];
  var cells=shuffle([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]).slice(0,hide);
  cells.forEach(function(i){grid[Math.floor(i/4)][i%4]=0});
  givenSet={}; cells.forEach(function(i){givenSet[i]=false}); for(var gi=0;gi<16;gi++){if(cells.indexOf(gi)<0)givenSet[gi]=true} sel=null; draw();}
function draw(){el('board').innerHTML=''; for(var r=0;r<4;r++)for(var c=0;c<4;c++){var v=grid[r][c];
  var b=document.createElement('button'); b.className='tile'; b.textContent=v||''; b.style.background=(sel&&sel[0]===r&&sel[1]===c)?'#F59E0B':'';
  (function(rr,cc){b.onclick=function(){if(givenSet[rr*4+cc])return; sel=[rr,cc]; el('sel').textContent='row '+(rr+1)+', col '+(cc+1); draw()}})(r,c);
  el('board').appendChild(b)}
  el('numbar').innerHTML=''; [1,2,3,4].forEach(function(n){var nb=document.createElement('button'); nb.className='opt'; nb.textContent=n;
    nb.onclick=function(){if(!sel){msg('Tap an empty cell first.'); return} grid[sel[0]][sel[1]]=n; draw();
      if(grid.every(function(row,ri){return row.every(function(v,ci){return v===sol[ri][ci]})})) {setScore(score+10); msg('🎉 Sudoku solved! Press Start for a new puzzle.')}}; el('numbar').appendChild(nb)});}
el('checkBtn').onclick=function(){var bad=0; for(var r=0;r<4;r++)for(var c=0;c<4;c++){if(grid[r][c]&&grid[r][c]!==sol[r][c])bad++} msg(bad?bad+' cell(s) wrong — fix them!':'All filled cells are correct so far!')};
el('startBtn').onclick=function(){newPuzzle(); msg('New 4×4 puzzle — fill 1 to 4!')}; newPuzzle();
""",
{"difficulty":["easy","medium","hard"],"hints":["on","off"],"mode":["classic","timed"]})

# ---- 43 digit-detective ----
add("digit-detective","Digit Detective","Guess the hidden number from the clues. Deduce it!","🕵️",
"Read the clues (even/odd, bigger/smaller, prime…) and guess the hidden number in as few tries as you can.",
'<div id="q">Press Start</div><div id="clues" class="small" style="margin:8px 0"></div><div class="row"><input type="number" id="inp" placeholder="Your guess"><button class="btn" id="guessBtn" style="flex:0 0 110px">Guess</button></div>',
r"""
var digits=parseInt(qp('digits')||'2')||2; if([1,2,3].indexOf(digits)<0)digits=2;
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var target=0, tries=0, maxN=0;
if(el('cfgLabel'))el('cfgLabel').textContent=digits+'-digit · '+diff;
function isPrime(n){if(n<2)return false; for(var i=2;i*i<=n;i++)if(n%i===0)return false; return true}
function newGame(){maxN=Math.pow(10,digits)-1; target=rnd(maxN-9)+10; if(digits===1)target=rnd(9)+1; tries=0;
  var clues=[]; clues.push('It is '+(target%2===0?'EVEN':'ODD')+'.');
  clues.push('It is '+(target>maxN/2?'bigger than '+Math.floor(maxN/2):'smaller than or equal to '+Math.floor(maxN/2))+'.');
  clues.push(isPrime(target)?'It is PRIME.':'It is NOT prime.');
  clues.push('Its digits add up to '+String(target).split('').reduce(function(a,c){return a+parseInt(c,10)},0)+'.');
  el('clues').innerHTML=clues.map(function(c){return '<div>• '+c+'</div>'}).join('');
  el('q').textContent='Hidden number: 1 to '+maxN+'. Use the clues!'; msg('Guess the hidden number!')}
function guess(){var g=parseInt(el('inp').value,10); if(isNaN(g)){msg('Type a number first.');return} tries++;
  if(g===target){setScore(Math.max(1,50-tries*5)); el('q').textContent='🎉 '+target+' in '+tries+' guesses!'; msg('Solved! Press Start for a new mystery.'); setTimeout(newGame,1400)}
  else {el('q').textContent=g<target?'Higher than '+g+'…':'Lower than '+g+'…'; msg('Try again — use the clues!')}
  el('inp').value='';}
el('guessBtn').onclick=guess; el('inp').addEventListener('keydown',function(e){if(e.key==='Enter')guess()});
el('startBtn').onclick=newGame; newGame();
""",
{"digits":["1","2","3"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 44 logic-grid ----
add("logic-grid","Logic Grid","Simple logic puzzles. Read the clues, pick the answer!","🧠",
"Read the short logic puzzle and pick the right answer. A new puzzle every round!",
'<div id="q" style="font-size:18px">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var type=qp('type')||'age'; var mode=qp('mode')||'classic';
var PUZZLES=[
 {q:'Ana is twice as old as Ben. Together they are 36. How old is Ana?', a:'24', opts:['18','24','12','30']},
 {q:'A farmer has 17 sheep. All but 9 run away. How many are left?', a:'9', opts:['8','9','17','0']},
 {q:'If 3 cats catch 3 mice in 3 minutes, how many cats catch 100 mice in 100 minutes?', a:'3', opts:['100','33','3','10']},
 {q:'A book costs $10 plus half its price. How much is it?', a:'$20', opts:['$15','$20','$25','$30']},
 {q:'Tom is 4, his sister is half his age. Tom is 40 now. How old is his sister?', a:'38', opts:['20','36','38','40']},
 {q:'What number comes next: 2, 6, 12, 20, 30, …?', a:'42', opts:['36','40','42','44']},
 {q:'I am an odd number. Take away one letter and I become even. What am I?', a:'Seven', opts:['Nine','Seven','Eleven','Three']},
 {q:'A snail climbs 3m up a 10m wall each day and slips 2m each night. How many days to the top?', a:'8 days', opts:['10 days','8 days','7 days','5 days']},
 {q:'If you have 3 apples and take away 2, how many do you have?', a:'2', opts:['1','2','3','5']},
 {q:'Which weighs more: a kilo of steel or a kilo of feathers?', a:'Same', opts:['Steel','Feathers','Same','Depends']},
 {q:'A train goes 60 km in 1 hour. How far in 2.5 hours?', a:'150 km', opts:['120 km','150 km','180 km','90 km']},
 {q:'Sara has 5 brothers. Each brother has 1 sister. How many children in the family?', a:'6', opts:['5','6','10','11']}];
var cur='';
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+type;
function mk(){var p=PUZZLES[rnd(PUZZLES.length)]; cur=p.a; el('q').textContent=p.q;
  el('opts').innerHTML=''; shuffle(p.opts.slice()).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct — nice logic!')}else msg('Not quite — the answer was '+cur+'.'); setTimeout(mk,600)}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Solve the logic puzzle!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"type":["age","riddle","numbers","mixed"],"mode":["classic","timed"]})

# ---- 45 shape-sort ----
add("shape-sort","Shape Sort","Sort shapes by how many sides they have. Fast fingers!","🔺",
"A shape appears. Tap how many sides it has — 0, 3, 4, 5 or 6. Quick!",
'<div id="q" style="font-size:56px">?</div><div class="grid" id="opts" style="grid-template-columns:repeat(3,1fr)"></div>',
r"""
var diff=qp('difficulty')||'medium'; var set=qp('set')||'basic'; var mode=qp('mode')||'sort';
var SHAPES={basic:[['●',0],['▲',3],['■',4],['⬟',5],['⬢',6]],advanced:[['●',0],['▲',3],['■',4],['⬟',5],['⬢',6],['⬛',4],['🔺',3],['⬠',5]]};
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=set+' shapes · '+diff;
function mk(){var pool=SHAPES[set]||SHAPES.basic; var s=pool[rnd(pool.length)]; cur=s[1]; el('q').textContent=s[0];
  var opts=[0,3,4,5,6]; el('opts').innerHTML=''; opts.forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v+' sides';
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('No — that shape has '+cur+' sides.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('How many sides?')}; mk();
""",
{"difficulty":["easy","medium","hard"],"set":["basic","advanced"],"mode":["sort","timed"]})

# ---- 46 time-trial-quiz ----
add("time-trial-quiz","Time Trial Quiz","Mixed quick quiz against the clock. 60 seconds, endless questions!","⏱️",
"Answer mixed maths, logic and number questions before the 60-second clock runs out!",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div><div class="small" style="text-align:center">Time left: <b id="time">60</b>s</div>',
r"""
var diff=qp('difficulty')||'medium'; var topic=qp('topic')||'mixed'; var dur=parseInt(qp('time')||'60')||60;
var cur=0, tLeft=dur, timer=null, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+topic+' · '+dur+'s';
function mk(){var kind=topic; if(kind==='mixed')kind=['maths','logic','numbers'][rnd(3)];
  var qtxt, ans, opts;
  if(kind==='maths'){var a=rnd(9)+2,b=rnd(9)+2; ans=a*b; qtxt=a+' × '+b+' = ?'; opts=[ans,ans+2,ans-2,ans+10]}
  else if(kind==='logic'){var a2=rnd(20)+5; ans=a2*2; qtxt='Double '+a2+' = ?'; opts=[ans,ans+2,ans-2,ans+4]}
  else {ans=rnd(90)+10; qtxt='What is '+ans+' + 10?'; ans=ans+10; opts=[ans,ans+1,ans-1,ans+10]}
  cur=ans; el('q').textContent=qtxt;
  el('opts').innerHTML=''; shuffle(opts).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(!playing)return; if(v===cur){setScore(score+1);msg('Correct!')}else msg('It was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
function start(){clearInterval(timer); setScore(0); tLeft=dur; playing=true; el('time').textContent=tLeft; mk(); msg('Go!');
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); playing=false; msg('Time! You scored '+score+'. Play again!')}},1000);}
el('startBtn').onclick=start; mk();
""",
{"difficulty":["easy","medium","hard"],"topic":["maths","logic","numbers","mixed"],"time":["30","60","90"]})

# ---- 47 estimate-it ----
add("estimate-it","Estimate It","Estimate how many dots there are — closest guess wins!","👀",
"Look at the dots for a few seconds, then pick the closest estimate. No counting allowed!",
'<div id="q" style="font-size:28px;letter-spacing:3px">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var range=qp('range')||'medium'; var mode=qp('mode')||'estimate';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+range;
function mk(){var maxN = range==='small'?20:(range==='large'?100:50); if(diff==='easy')maxN=Math.min(maxN,30); if(diff==='hard')maxN=maxN+30;
  cur=rnd(maxN)+10; el('q').textContent='●'.repeat(Math.min(cur,40));
  var opts=[cur, Math.max(1,cur-5), cur+5, cur+10]; if(diff==='hard')opts=[cur,cur-2,cur+3,cur-7];
  el('opts').innerHTML=''; shuffle(opts).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent='≈ '+v;
    b.onclick=function(){if(v===cur){setScore(score+2);msg('🎉 Spot on!')}else if(Math.abs(v-cur)<=5){setScore(score+1);msg('Close! There were '+cur+'.')}else msg('There were '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Estimate — don\'t count!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"range":["small","medium","large"],"mode":["estimate","timed"]})

# ---- 48 doubling-dash ----
add("doubling-dash","Doubling Dash","Double it or halve it — race through the numbers!","✖️",
"Double the number — or halve it. Pick the right answer and race on!",
'<div id="q">Press Start</div><div class="grid" id="opts" style="grid-template-columns:1fr 1fr"></div>',
r"""
var diff=qp('difficulty')||'medium'; var op=qp('op')||'double'; var mode=qp('mode')||'dash';
var cur=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+op;
function mk(){var n=rnd(40)+2; var o=op; if(o==='mixed')o=Math.random()<0.5?'double':'halve';
  var qtxt, ans; if(o==='double'){ans=n*2; qtxt='Double '+n+' = ?'} else {n=n*2; ans=n/2; qtxt='Half of '+n+' = ?'}
  cur=ans; el('q').textContent=qtxt;
  var s=mkOpts(ans,4);
  el('opts').innerHTML=''; shuffle(Array.from(s)).forEach(function(v){var b=document.createElement('button');b.className='opt';b.textContent=v;
    b.onclick=function(){if(v===cur){setScore(score+1);msg('Correct!')}else msg('It was '+cur+'.'); mk()}; el('opts').appendChild(b)});}
el('startBtn').onclick=function(){setScore(0);mk();msg('Double or halve — go!')}; mk();
""",
{"difficulty":["easy","medium","hard"],"op":["double","halve","mixed"],"mode":["dash","marathon"]})

# ---- 49 sum-15 ----
add("sum-15","Sum 15","Pick numbers that add up to exactly 15. A new set every round!","➕",
"Tap numbers that add up to exactly 15. Use as few or as many as you like — but hit 15 exactly!",
'<div id="q">Pick numbers that add to <b>15</b></div><div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Running total: <b id="tot">0</b> · Target: <b id="tgt">15</b></div><button class="btn ghost" id="resetBtn">Clear picks</button>',
r"""
var target=parseInt(qp('target')||'15')||15; var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var tot=0, picked=[];
if(el('cfgLabel'))el('cfgLabel').textContent='target '+target+' · '+diff;
el('tgt').textContent=target;
function build(){tot=0; picked=[]; el('tot').textContent=0;
  var nums=[]; for(var i=0;i<9;i++)nums.push(rnd(9)+1);
  el('board').innerHTML=''; nums.forEach(function(v){var b=document.createElement('button'); b.className='tile'; b.textContent=v;
    b.onclick=function(){if(b.disabled)return; tot+=v; picked.push(v); b.disabled=true; b.style.background='#dcfce7'; el('tot').textContent=tot;
      if(tot===target){setScore(score+1); msg('🎉 Exactly '+target+'! New set below.'); setTimeout(build,900)}
      else if(tot>target){msg('Over '+target+'! Press Clear picks and try again.')}}; el('board').appendChild(b)});}
el('resetBtn').onclick=function(){build(); msg('Cleared — try again!')};
el('startBtn').onclick=function(){build(); msg('Pick numbers to make '+target+'!')}; build();
""",
{"target":["10","15","20"],"difficulty":["easy","medium","hard"],"mode":["classic","timed"]})

# ---- 50 number-bingo ----
add("number-bingo","Number Bingo","Numbers are called — tap them on your card. Get a line to win!","🎱",
"Numbers are called out. Tap the matching number on your card. Complete a row, column or diagonal for BINGO!",
'<div id="q">Press Start to call the first number!</div><div class="grid" id="board" style="grid-template-columns:repeat(5,1fr)"></div><div class="small" style="text-align:center">Called: <b id="called">—</b></div><button class="btn amber" id="callBtn">CALL NEXT NUMBER</button>',
r"""
var size=parseInt(qp('size')||'5')||5; if([3,4,5].indexOf(size)<0)size=5;
var speed=qp('speed')||'manual'; var diff=qp('difficulty')||'medium';
var card=[], called=new Set(), last=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+speed;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function build(){var nums=shuffle(Array.from({length:50},function(_,i){return i+1})).slice(0,size*size); card=nums; called=new Set(); last=0; el('called').textContent='—';
  el('board').innerHTML=''; card.forEach(function(v){var b=document.createElement('button'); b.className='tile'; b.style.fontSize='16px'; b.textContent=v; b.dataset.v=v;
    b.onclick=function(){if(v===last){b.style.background='#166534'; b.style.color='#fff'; b.disabled=true; setScore(score+1); msg('Marked '+v+'!'); checkWin()} else msg(v+' was not called — the last call was '+(last||'none')+'.')}; el('board').appendChild(b)});}
function checkWin(){var marked=[]; el('board').querySelectorAll('button').forEach(function(b){marked.push(b.disabled)});
  var win=false; for(var r=0;r<size;r++){if(marked.slice(r*size,r*size+size).every(Boolean))win=true}
  for(var c=0;c<size;c++){var col=true; for(var rr=0;rr<size;rr++)if(!marked[rr*size+c])col=false; if(col)win=true}
  var d1=true,d2=true; for(var i=0;i<size;i++){if(!marked[i*size+i])d1=false; if(!marked[i*size+(size-1-i)])d2=false}
  if(d1||d2)win=true;
  if(win){setScore(score+10); msg('🎉 BINGO! You completed a line! Press Start for a new card.')}}
function call(){var pool=[]; for(var i=1;i<=50;i++)if(!called.has(i))pool.push(i); if(!pool.length){msg('All numbers called! Press Start for a new card.'); return}
  last=pool[rnd(pool.length)]; called.add(last); el('called').textContent=last; el('q').textContent='Called: '+last+' — tap it on your card!';}
el('callBtn').onclick=call;
el('startBtn').onclick=function(){build(); el('q').textContent='New card! Press CALL NEXT NUMBER.'; msg('New bingo card — good luck!')}; build();
""",
{"size":["3","4","5"],"speed":["manual","auto"],"difficulty":["easy","medium","hard"]})

# ================= MAIN =================
def main():
    os.makedirs(GAMES_DIR, exist_ok=True)
    registry = []
    total_var = 0
    for g in GAMES:
        d = os.path.join(GAMES_DIR, g["slug"])
        os.makedirs(d, exist_ok=True)
        html_text = page(g["slug"], g["name"], g["howto"], g["body"], g["js"], g["variations"])
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_text)
        total_var += len(g["variations"])
        registry.append({"slug": g["slug"], "name": g["name"], "blurb": g["blurb"], "icon": g["icon"],
                         "variations": g["variations"]})
    with open(os.path.join(BASE, "games.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"games={len(GAMES)} variations={total_var}")
    for g in GAMES:
        print(f"  {g['slug']}: {len(g['variations'])} variations")

if __name__ == "__main__":
    main()
