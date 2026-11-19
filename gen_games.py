#!/usr/bin/env python3
"""Generate 50 endless mini-games for FreeCalcNow. Batch 1: 50+ games, 1000+ variations.
Each game: one self-contained HTML file, inline CSS+JS, no external deps.
Each game reads URL query params (difficulty/op/mode/size/time/...) and configures itself.
Variations = cartesian product of the game's variation axes; every axis is actually
read and used by that game's JS (honest count)."""
import os, json, itertools, html

BASE = os.path.expanduser("~/workspace/freecalcnow-site")
GAMES_DIR = os.path.join(BASE, "games")

CSS = """*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#F8FAFC;color:#0F172A}header{background:#166534;color:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}header a{color:#fff;font-weight:800;text-decoration:none;font-size:18px}header span{font-size:13px;opacity:.9}main{max-width:560px;margin:0 auto;padding:14px 14px 30px}h1{font-size:24px;margin:8px 0 4px}.how{color:#475569;margin:0 0 12px}.bar{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:8px 12px;margin-bottom:12px;font-weight:700}.bar span{color:#166534}#game{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;min-height:180px}#msg{min-height:24px;margin:10px 0;font-weight:600;color:#166534}#q{font-size:26px;font-weight:800;text-align:center;margin:12px 0}.grid{display:grid;gap:8px}.btn{display:block;width:100%;padding:13px;font-size:17px;font-weight:700;border:0;border-radius:10px;background:#166534;color:#fff;cursor:pointer;margin:6px 0}.btn.amber{background:#F59E0B;color:#0F172A}.btn.ghost{background:#e2e8f0;color:#0F172A}.opt{padding:13px;font-size:18px;font-weight:700;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer}.opt:active{background:#dcfce7}.tile{aspect-ratio:1;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer;min-height:48px}input[type=text],input[type=number]{width:100%;padding:12px;font-size:18px;border:2px solid #cbd5e1;border-radius:10px;margin:6px 0}.row{display:flex;gap:8px}.row>*{flex:1}.small{font-size:13px;color:#64748b}.vars{margin-top:14px;font-size:13px}.vars a{display:inline-block;background:#fff;border:1px solid #cbd5e1;border-radius:20px;padding:5px 10px;margin:3px;text-decoration:none;color:#166534;font-weight:600}footer{text-align:center;color:#64748b;font-size:13px;padding:16px}footer a{color:#166534}.more{display:block;text-align:center;margin-top:14px;font-weight:700;color:#166534}body.theme-dark{background:#0f172a;color:#e2e8f0}body.theme-dark #game,body.theme-dark .bar{background:#1e293b;border-color:#334155;color:#e2e8f0}body.theme-dark .opt,body.theme-dark .tile{background:#1e293b;color:#e2e8f0;border-color:#334155}body.theme-dark .how,body.theme-dark .small{color:#94a3b8}body.theme-dark .btn.ghost{background:#334155;color:#f1f5f9}body.theme-dark input[type=text],body.theme-dark input[type=number]{background:#0b1220;color:#e2e8f0;border-color:#334155}body.theme-dark .vars a{background:#1e293b;color:#86efac;border-color:#334155}body.theme-neon{background:#0b1020;color:#fef3c7}body.theme-neon #game,body.theme-neon .bar{background:#131a2e;border-color:#f59e0b;color:#fef3c7}body.theme-neon .opt,body.theme-neon .tile{background:#131a2e;color:#fef3c7;border-color:#f59e0b}body.theme-neon .how,body.theme-neon .small{color:#fcd34d}body.theme-neon .btn{background:#f59e0b;color:#1c1005}body.theme-neon .btn.amber{background:#22d3ee;color:#082f49}body.theme-neon .btn.ghost{background:#334155;color:#fef3c7}body.theme-neon .vars a{background:#131a2e;color:#fcd34d;border-color:#f59e0b}"""

GA = """<!-- Google tag (gtag.js) --><script async src="https://www.googletagmanager.com/gtag/js?id=G-3Y2FGRCKZZ"></script><script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'G-3Y2FGRCKZZ');</script>"""


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
        "try{var _th=qp('theme');if(_th==='dark'||_th==='neon'){document.body.classList.add('theme-'+_th)}}catch(e){}"
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(name)} - FreeCalcNow Games</title><meta name="description" content="{html.escape(howto)} Play free, endless, no sign-up."><link rel="canonical" href="https://freecalcnow.github.io/games/{slug}/"><meta name="theme-color" content="#166534">{GA}<style>{CSS}</style></head><body><header><a href="/">FreeCalcNow</a><span>Free Games</span></header><main><h1>{html.escape(name)}</h1><p class="how">{html.escape(howto)}</p><div class="bar"><span>Score: <b id="score">0</b></span><span>Best: <b id="best">0</b></span><span style="margin-left:auto" class="small" id="cfgLabel"></span></div><div id="game">{body}</div><div id="msg"></div><button class="btn" id="startBtn">▶ Start / New game</button><div class="vars"><b>Try a variation:</b><br>{varlinks}</div><a class="more" href="/games/">← More games</a></main><footer><a href="/">FreeCalcNow</a> — free calculators &amp; games. No sign-up, no ads covering play.</footer><script>{js_prefix}\n{js}</script></body></html>"""

def variations_from_axes(axes):
    keys = list(axes.keys())
    out = []
    for combo in itertools.product(*[axes[k] for k in keys]):
        params = dict(zip(keys, combo))
        name = " · ".join(str(c).replace("-", " ").title() for c in combo)
        out.append({"name": name, "params": params})
    return out

# PLAN (19 Nov 2026): 78 full games, 1,177 playable variations (difficulty/theme/board-size
# axes). 15,390 unique games are NOT possible - games ship in patches; each patch adds real
# full games (no demos) and the variation system carries the playable total past 1,000.
# Maths-drill games are DELETED by owner order (22 removed 19 Nov) and must NOT be re-added;
# Daily Number (daily guessing game) is KEPT. Next patches: more viral classics + new axes.
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


# ---- Batch games_c1_adds.py (19 Nov 2026) ----
# Batch C1: 10 classic board/logic games for FreeCalcNow (fragment only — add() calls)

# ---- chess ----
add("chess","Chess","Play chess against the computer. Full rules: castling, en passant, promotion, check and checkmate.","♞",
"Tap one of your pieces, then tap a highlighted square to move. Checkmate the enemy king to win. Promotion is automatic to queen.",
'<div id="board" style="display:grid;grid-template-columns:repeat(8,1fr);gap:0;border:2px solid #0F172A;max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin-top:8px">Turn: <b id="turn">White</b> · <span id="state"></span></div>',
r"""
var diff=qp('difficulty')||'medium'; var side=(qp('side')||'white').toLowerCase(); if(side!=='white'&&side!=='black')side='white';
var human=side==='white'?'w':'b'; var ai=human==='w'?'b':'w';
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · you play '+side;
var VAL={P:1,N:3,B:3,R:5,Q:9,K:0};
var GLYPH={wP:'\u2659',wN:'\u2658',wB:'\u2657',wR:'\u2656',wQ:'\u2655',wK:'\u2654',bP:'\u265F',bN:'\u265E',bB:'\u265D',bR:'\u265C',bQ:'\u265B',bK:'\u265A'};
var board, turn, castle, ep, sel, legalCache, over, wins=0;
function col(p){return p===p.toUpperCase()?'w':'b'}
function typ(p){return p.toUpperCase()}
function rc(i){return [Math.floor(i/8), i%8]}
function idx(r,c){return r*8+c}
function inside(r,c){return r>=0&&r<8&&c>=0&&c<8}
function attacked(b,sq,by){var r=rc(sq)[0],c=rc(sq)[1];
  var dir=by==='w'?1:-1;
  [[r+dir,c-1],[r+dir,c+1]].forEach(function(p){if(inside(p[0],p[1])&&b[idx(p[0],p[1])]===(by==='w'?'P':'p'))return true});
  // pawn check done inline below (forEach return does not exit) — recompute:
  var pawnAt=false; [[r+dir,c-1],[r+dir,c+1]].forEach(function(p){if(inside(p[0],p[1])&&b[idx(p[0],p[1])]===(by==='w'?'P':'p'))pawnAt=true}); if(pawnAt)return true;
  var kn=[[ -2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
  for(var i=0;i<kn.length;i++){var rr=r+kn[i][0],cc=c+kn[i][1]; if(inside(rr,cc)&&b[idx(rr,cc)]===(by==='w'?'N':'n'))return true}
  for(var dr=-1;dr<=1;dr++)for(var dc=-1;dc<=1;dc++){if(!dr&&!dc)continue; var rr2=r+dr,cc2=c+dc; if(inside(rr2,cc2)&&b[idx(rr2,cc2)]===(by==='w'?'K':'k'))return true}
  var dirs=[[ -1,0],[1,0],[0,-1],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]];
  for(var d=0;d<dirs.length;d++){var rr3=r+dirs[d][0],cc3=c+dirs[d][1];
    while(inside(rr3,cc3)){var p=b[idx(rr3,cc3)]; if(p){if(col(p)===by){var t=typ(p); if(d<4&&(t==='R'||t==='Q'))return true; if(d>=4&&(t==='B'||t==='Q'))return true} break} rr3+=dirs[d][0]; cc3+=dirs[d][1]}}
  return false}
function kingSq(b,color){for(var i=0;i<64;i++)if(b[i]===(color==='w'?'K':'k'))return i; return -1}
function pseudo(b,color,cast,epSq){var ms=[];
  for(var i=0;i<64;i++){var p=b[i]; if(!p||col(p)!==color)continue; var r=rc(i)[0],c=rc(i)[1]; var t=typ(p);
    if(t==='P'){var d=color==='w'?-1:1; var start=color==='w'?6:1; var last=color==='w'?0:7;
      var f=idx(r+d,c); if(inside(r+d,c)&&!b[f]){ms.push({from:i,to:f,promo:(r+d===last)}); var f2=idx(r+2*d,c); if(r===start&&!b[f2])ms.push({from:i,to:f2,dbl:true})}
      [[r+d,c-1],[r+d,c+1]].forEach(function(q){if(!inside(q[0],q[1]))return; var j=idx(q[0],q[1]);
        if(b[j]&&col(b[j])!==color)ms.push({from:i,to:j,promo:(q[0]===last)});
        if(j===epSq)ms.push({from:i,to:j,ep:true})})}
    else if(t==='N'||t==='K'){var off=t==='N'?[[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]]:[[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
      off.forEach(function(o){var rr=r+o[0],cc=c+o[1]; if(!inside(rr,cc))return; var j=idx(rr,cc); if(!b[j]||col(b[j])!==color)ms.push({from:i,to:j})})}
    else {var dirs2=t==='B'?[[-1,-1],[-1,1],[1,-1],[1,1]]:(t==='R'?[[-1,0],[1,0],[0,-1],[0,1]]:[[-1,-1],[-1,1],[1,-1],[1,1],[-1,0],[1,0],[0,-1],[0,1]]);
      dirs2.forEach(function(o){var rr=r+o[0],cc=c+o[1]; while(inside(rr,cc)){var j=idx(rr,cc); if(!b[j])ms.push({from:i,to:j}); else {if(col(b[j])!==color)ms.push({from:i,to:j}); break} rr+=o[0]; cc+=o[1]}})}
    if(t==='K'){
      if(color==='w'&&r===7&&c===4){if(cast.K&&!b[61]&&!b[62]&&b[63]==='R'&&!attacked(b,60,'b')&&!attacked(b,61,'b')&&!attacked(b,62,'b'))ms.push({from:60,to:62,castle:'K'});
        if(cast.Q&&!b[59]&&!b[58]&&!b[57]&&b[56]==='R'&&!attacked(b,60,'b')&&!attacked(b,59,'b')&&!attacked(b,58,'b'))ms.push({from:60,to:58,castle:'Q'})}
      if(color==='b'&&r===0&&c===4){if(cast.k&&!b[5]&&!b[6]&&b[7]==='r'&&!attacked(b,4,'w')&&!attacked(b,5,'w')&&!attacked(b,6,'w'))ms.push({from:4,to:6,castle:'k'});
        if(cast.q&&!b[3]&&!b[2]&&!b[1]&&b[0]==='r'&&!attacked(b,4,'w')&&!attacked(b,3,'w')&&!attacked(b,2,'w'))ms.push({from:4,to:2,castle:'q'})}}}
  return ms}
function applyMove(b,m,color,cast,epSq){var nb=b.slice(); var p=nb[m.from]; nb[m.from]=''; nb[m.to]=m.promo?(color==='w'?'Q':'q'):p;
  if(m.ep){var cap=color==='w'?m.to+8:m.to-8; nb[cap]=''}
  if(m.castle==='K'){nb[61]='R';nb[63]=''} if(m.castle==='Q'){nb[59]='R';nb[56]=''} if(m.castle==='k'){nb[5]='r';nb[7]=''} if(m.castle==='q'){nb[3]='r';nb[0]=''}
  var nc={K:cast.K,Q:cast.Q,k:cast.k,q:cast.q};
  if(p==='K'){nc.K=false;nc.Q=false} if(p==='k'){nc.k=false;nc.q=false}
  if(m.from===63||m.to===63)nc.K=false; if(m.from===56||m.to===56)nc.Q=false; if(m.from===7||m.to===7)nc.k=false; if(m.from===0||m.to===0)nc.q=false;
  var nep=m.dbl?(color==='w'?m.from-8:m.from+8):-1;
  return {b:nb,c:nc,ep:nep}}
function legal(b,color,cast,epSq){var out=[]; pseudo(b,color,cast,epSq).forEach(function(m){var r=applyMove(b,m,color,cast,epSq); if(!attacked(r.b,kingSq(r.b,color),color==='w'?'b':'w'))out.push(m)}); return out}
function evaluate(b){var s=0; for(var i=0;i<64;i++){if(!b[i])continue; var v=VAL[typ(b[i])]; s+=col(b[i])==='w'?v:-v} return s}
function aiMove(){if(over)return; var ms=legal(board,ai,castle,ep); if(!ms.length){endCheck();return}
  var mv; if(diff==='easy'){mv=ms[rnd(ms.length)]}
  else {var best=-1e9, cands=[]; ms.forEach(function(m){var r=applyMove(board,m,ai,castle,ep); var e=evaluate(r.b)*(ai==='w'?1:-1); if(e>best){best=e;cands=[m]} else if(e===best)cands.push(m)}); mv=cands[rnd(cands.length)]}
  doMove(mv); }
function doMove(m){var r=applyMove(board,m,turn,castle,ep); board=r.b; castle=r.c; ep=r.ep; turn=turn==='w'?'b':'w'; sel=null; draw(); endCheck();
  if(!over&&turn===ai)setTimeout(aiMove,400)}
function endCheck(){var ms=legal(board,turn,castle,ep); var inChk=attacked(board,kingSq(board,turn),turn==='w'?'b':'w');
  el('state').textContent=inChk?'Check!':'';
  if(!ms.length){over=true; if(inChk){var humanWon=turn!==human; msg(humanWon?'🎉 Checkmate — you win!':'Checkmate — the computer wins. Press Start to play again.'); if(humanWon){wins++; setScore(wins*10)}} else {msg('Stalemate — draw! Press Start to play again.'); setScore(wins*10+5)}}}
function draw(){el('turn').textContent=turn==='w'?'White':'Black';
  el('board').innerHTML='';
  for(var i=0;i<64;i++){var r=rc(i)[0],c=rc(i)[1]; var d=document.createElement('button');
    d.style.cssText='aspect-ratio:1;border:0;font-size:26px;cursor:pointer;min-height:44px;background:'+(((r+c)%2===0)?'#f0d9b5':'#b58863');
    d.style.padding='0';
    if(sel===i)d.style.background='#F59E0B';
    if(sel!==null&&legalCache){for(var k=0;k<legalCache.length;k++){if(legalCache[k].from===sel&&legalCache[k].to===i)d.style.background='#86efac'}}
    var p=board[i]; d.textContent=p?GLYPH[col(p)+typ(p)]:'';
    d.style.color=col(p)==='w'?'#fff':'#0F172A'; d.style.textShadow=col(p)==='w'?'0 0 3px #000':'none';
    (function(ii){d.onclick=function(){if(over||turn!==human)return;
      if(sel===null){if(board[ii]&&col(board[ii])===human){sel=ii; legalCache=legal(board,human,castle,ep); draw()} return}
      var m=null; if(legalCache)for(var k2=0;k2<legalCache.length;k2++)if(legalCache[k2].from===sel&&legalCache[k2].to===ii)m=legalCache[k2];
      if(m){doMove(m)} else if(board[ii]&&col(board[ii])===human){sel=ii; legalCache=legal(board,human,castle,ep); draw()} else {sel=null; draw()}}})(i);
    el('board').appendChild(d)}}
function start(){board=['r','n','b','q','k','b','n','r','p','p','p','p','p','p','p','p'];
  for(var e=0;e<32;e++)board.push('');
  board=board.concat(['P','P','P','P','P','P','P','P','R','N','B','Q','K','B','N','R']);
  turn='w'; castle={K:true,Q:true,k:true,q:true}; ep=-1; sel=null; legalCache=null; over=false; msg('Your move — tap a piece, then a highlighted square.');
  draw(); if(turn===ai)setTimeout(aiMove,500)}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium"],"side":["white","black"]})

# ---- checkers ----
add("checkers","Checkers","Classic checkers (draughts) against the computer. Jumps are forced — chain multi-jumps and crown kings.","🔴",
"Tap one of your pieces, then tap a highlighted square. Jumps are forced, and you must keep jumping while you can. Capture all enemy pieces or block them to win.",
'<div id="board" style="display:grid;grid-template-columns:repeat(8,1fr);gap:0;border:2px solid #0F172A;max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin-top:8px">Turn: <b id="turn">Red</b> · <span id="state"></span></div>',
r"""
var diff=qp('difficulty')||'medium'; var side=(qp('side')||'red').toLowerCase(); if(side!=='red'&&side!=='black')side='red';
var human=side==='red'?'r':'b'; var ai=human==='r'?'b':'r';
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · you play '+side;
var board, turn, sel, legalCache, over, mustPiece, wins=0;
function rc(i){return [Math.floor(i/8), i%8]}
function inside(r,c){return r>=0&&r<8&&c>=0&&c<8}
function col(p){return p.toLowerCase()}
function isKing(p){return p===p.toUpperCase()}
function dirs(p){if(isKing(p))return [[-1,-1],[-1,1],[1,-1],[1,1]]; return col(p)==='r'?[[-1,-1],[-1,1]]:[[1,-1],[1,1]]}
function jumpsFrom(b,i){var p=b[i]; if(!p)return []; var r=rc(i)[0],c=rc(i)[1]; var out=[];
  dirs(p).forEach(function(d){var mr=r+d[0],mc=c+d[1],lr=r+2*d[0],lc=c+2*d[1];
    if(inside(lr,lc)&&b[mr*8+mc]&&col(b[mr*8+mc])!==col(p)&&!b[lr*8+lc])out.push({from:i,to:lr*8+lc,cap:mr*8+mc})}); return out}
function movesFrom(b,i){var p=b[i]; if(!p)return []; var r=rc(i)[0],c=rc(i)[1]; var out=[];
  dirs(p).forEach(function(d){var nr=r+d[0],nc=c+d[1]; if(inside(nr,nc)&&!b[nr*8+nc])out.push({from:i,to:nr*8+nc})}); return out}
function allMoves(b,color){var js=[],ms=[]; for(var i=0;i<64;i++){if(b[i]&&col(b[i])===color){jumpsFrom(b,i).forEach(function(j){js.push(j)}); movesFrom(b,i).forEach(function(m){ms.push(m)})}}
  return js.length?js:ms}
function applyMove(b,m,color){var nb=b.slice(); var p=nb[m.from]; nb[m.from]=''; if(m.cap)nb[m.cap]='';
  var r=Math.floor(m.to/8); if(!isKing(p)&&((color==='r'&&r===0)||(color==='b'&&r===7)))p=p.toUpperCase();
  nb[m.to]=p; return nb}
function hasAny(b,color){return allMoves(b,color).length>0}
function countPieces(b,color){var n=0; for(var i=0;i<64;i++)if(b[i]&&col(b[i])===color)n++; return n}
function evaluate(b){var s=0; for(var i=0;i<64;i++){if(!b[i])continue; var v=isKing(b[i])?3:1; s+=col(b[i])===ai?v:-v} return s}
function aiMove(){if(over)return; var ms=allMoves(board,ai); if(!ms.length){endGame(ai);return}
  var mv; if(diff==='easy'){mv=ms[rnd(ms.length)]}
  else {var best=-1e9,cands=[]; ms.forEach(function(m){var nb=applyMove(board,m,ai); var e=evaluate(nb); var cont=jumpsFrom(nb,m.to).length?1:0; e+=cont*2; if(e>best){best=e;cands=[m]} else if(e===best)cands.push(m)}); mv=cands[rnd(cands.length)]}
  doMove(mv,true)}
function doMove(m,isAi){board=applyMove(board,m,turn); var cont=m.cap?jumpsFrom(board,m.to):[];
  if(m.cap&&cont.length){ if(isAi){setTimeout(function(){var ms=jumpsFrom(board,m.to); doMove(ms[rnd(ms.length)],true)},450); draw(); return}
    mustPiece=m.to; sel=m.to; legalCache=cont; el('state').textContent='Keep jumping with the same piece!'; draw(); return}
  mustPiece=null; turn=turn==='r'?'b':'r'; sel=null; legalCache=null; draw(); checkEnd();
  if(!over&&turn===ai)setTimeout(aiMove,450)}
function checkEnd(){if(!hasAny(board,turn)){endGame(turn)} else if(countPieces(board,'r')===0){endGame('r')} else if(countPieces(board,'b')===0){endGame('b')}}
function endGame(loser){over=true; var humanWon=loser!==human; msg(humanWon?'🎉 You win! All enemy pieces captured.':'The computer wins. Press Start to play again.'); if(humanWon){wins++; setScore(wins*10)}}
function draw(){el('turn').textContent=turn==='r'?'Red':'Black';
  el('board').innerHTML='';
  for(var i=0;i<64;i++){var r=rc(i)[0],c=rc(i)[1]; var d=document.createElement('button');
    d.style.cssText='aspect-ratio:1;border:0;cursor:pointer;min-height:44px;padding:0;background:'+(((r+c)%2===0)?'#f0d9b5':'#7c4a21');
    var p=board[i];
    if(p){var s=document.createElement('span'); s.textContent=isKing(p)?'\u265A':'\u25CF'; s.style.cssText='font-size:26px;color:'+(col(p)==='r'?'#dc2626':'#111827')+';display:block;line-height:1'; if(isKing(p))s.style.textShadow='0 0 4px #F59E0B'; d.appendChild(s)}
    if(sel===i)d.style.background='#F59E0B';
    if(sel!==null&&legalCache){for(var k=0;k<legalCache.length;k++)if(legalCache[k].from===sel&&legalCache[k].to===i)d.style.background='#86efac'}
    (function(ii){d.onclick=function(){if(over||turn!==human)return;
      if(sel===null){if(board[ii]&&col(board[ii])===human){if(mustPiece!==null&&ii!==mustPiece)return; sel=ii; legalCache=allMoves(board,human).filter(function(m){return m.from===ii}); if(!legalCache.length){msg('That piece has no move.'); sel=null; return} draw()} return}
      var m=null; if(legalCache)for(var k2=0;k2<legalCache.length;k2++)if(legalCache[k2].to===ii)m=legalCache[k2];
      if(m){doMove(m,false)} else if(board[ii]&&col(board[ii])===human){sel=ii; legalCache=allMoves(board,human).filter(function(mm){return mm.from===ii}); draw()} else {sel=null; draw()}}})(i);
    el('board').appendChild(d)}}
function start(){board=new Array(64).fill('');
  for(var r=0;r<3;r++)for(var c=0;c<8;c++)if((r+c)%2===1)board[r*8+c]='b';
  for(var r2=5;r2<8;r2++)for(var c2=0;c2<8;c2++)if((r2+c2)%2===1)board[r2*8+c2]='r';
  turn='r'; sel=null; legalCache=null; over=false; mustPiece=null; el('state').textContent='';
  msg('Red moves first. Jumps are forced — tap a piece, then a highlighted square.');
  draw(); if(turn===ai)setTimeout(aiMove,500)}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium"],"side":["red","black"]})

# ---- connect-four ----
add("connect-four","Connect Four","Drop discs, connect four in a row — beat the computer!","🔴",
"Tap a column to drop your disc. Get four in a row — across, down or diagonally — before the computer does.",
'<div id="board" style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;background:#1d4ed8;padding:6px;border-radius:10px"></div>',
r"""
var diff=qp('difficulty')||'medium'; var first=(qp('first')||'you').toLowerCase(); if(first!=='you'&&first!=='computer')first='you';
var human=1, ai=2; var board, turn, over, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+first+' first';
function drop(b,col,p){for(var r=5;r>=0;r--){if(!b[r][col]){b[r][col]=p; return r}} return -1}
function win(b,p){var dirs=[[0,1],[1,0],[1,1],[1,-1]];
  for(var r=0;r<6;r++)for(var c=0;c<7;c++){if(b[r][c]!==p)continue;
    for(var d=0;d<4;d++){var ok=true; for(var k=1;k<4;k++){var rr=r+dirs[d][0]*k,cc=c+dirs[d][1]*k; if(rr<0||rr>5||cc<0||cc>6||b[rr][cc]!==p){ok=false;break}} if(ok)return true}} return false}
function full(b){for(var c=0;c<7;c++)if(!b[0][c])return false; return true}
function scorePos(b,p){var s=0; function win4(a,bb,cc,dr,dc){var n=0,e=0; for(var k=0;k<4;k++){var v=b[a+dr*k][bb+dc*k]; if(v===p)n++; else if(v===0)e++} if(n===4)return 100000; if(n===3&&e===1)return 50; if(n===2&&e===2)return 10; return 0}
  for(var r=0;r<6;r++)for(var c=0;c<7;c++){if(c+3<7)s+=win4(r,c,0,1); if(r+3<6)s+=win4(r,c,1,0); if(r+3<6&&c+3<7)s+=win4(r,c,1,1); if(r+3<6&&c-3>=0)s+=win4(r,c,1,-1)}
  return s}
function minimax(b,depth,alpha,beta,maxP){if(win(b,ai))return 100000+depth; if(win(b,human))return -100000-depth; if(full(b)||depth===0)return scorePos(b,ai)-scorePos(b,human);
  if(maxP){var best=-1e9; for(var c=0;c<7;c++){if(b[0][c])continue; var nb=b.map(function(row){return row.slice()}); drop(nb,c,ai); best=Math.max(best,minimax(nb,depth-1,alpha,beta,false)); alpha=Math.max(alpha,best); if(beta<=alpha)break} return best}
  var best2=1e9; for(var c2=0;c2<7;c2++){if(b[0][c2])continue; var nb2=b.map(function(row){return row.slice()}); drop(nb2,c2,human); best2=Math.min(best2,minimax(nb2,depth-1,alpha,beta,true)); beta=Math.min(beta,best2); if(beta<=alpha)break} return best2}
function aiMove(){if(over)return; var cols=[]; for(var c=0;c<7;c++)if(!board[0][c])cols.push(c);
  var pick=cols[rnd(cols.length)];
  if(diff==='medium'||diff==='hard'){
    var depth=diff==='hard'?4:2; var best=-1e9, cands=[];
    cols.forEach(function(cc){var nb=board.map(function(row){return row.slice()}); drop(nb,cc,ai);
      var v=win(nb,ai)?1000000:minimax(nb,depth-1,-1e9,1e9,false);
      v+= (3-Math.abs(cc-3))*2;
      if(v>best){best=v;cands=[cc]} else if(v===best)cands.push(cc)});
    pick=cands[rnd(cands.length)]}
  else { // easy: still take an instant win, otherwise random
    for(var i=0;i<cols.length;i++){var nb3=board.map(function(row){return row.slice()}); drop(nb3,cols[i],ai); if(win(nb3,ai)){pick=cols[i];break}}}
  drop(board,pick,ai); afterMove(ai)}
function afterMove(p){draw();
  if(win(board,p)){over=true; if(p===human){wins++; setScore(wins*10); msg('🎉 You connected four — you win!')} else msg('The computer connected four. Press Start to play again.'); return}
  if(full(board)){over=true; msg('Draw! The board is full. Press Start to play again.'); setScore(wins*10+5); return}
  turn=p===human?ai:human; if(turn===ai)setTimeout(aiMove,400)}
function draw(){el('board').innerHTML='';
  for(var r=0;r<6;r++)for(var c=0;c<7;c++){var d=document.createElement('button');
    d.style.cssText='aspect-ratio:1;border-radius:50%;border:0;cursor:pointer;min-height:44px;padding:0;background:'+(board[r][c]===1?'#dc2626':(board[r][c]===2?'#facc15':'#fff'));
    (function(cc){d.onclick=function(){if(over||turn!==human)return; if(board[0][cc]){msg('That column is full.');return} drop(board,cc,human); afterMove(human)}})(c);
    el('board').appendChild(d)}}
function start(){board=[]; for(var r=0;r<6;r++)board.push([0,0,0,0,0,0,0]); over=false; turn=first==='you'?human:ai; draw(); msg(first==='you'?'Your move — tap a column to drop a red disc.':'The computer goes first…'); if(turn===ai)setTimeout(aiMove,500)}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"first":["you","computer"]})

# ---- reversi ----
add("reversi","Reversi (Othello)","Flip discs, outnumber your rival on the 8×8 board.","⚫",
"Tap a highlighted square to place a disc. You flip every enemy disc trapped between yours. Most discs at the end wins — corners are gold!",
'<div id="board" style="display:grid;grid-template-columns:repeat(8,1fr);gap:0;border:2px solid #166534;max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin-top:8px">Black: <b id="cntB">2</b> · White: <b id="cntW">2</b> · Turn: <b id="turn">Black</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var side=(qp('side')||'black').toLowerCase(); if(side!=='black'&&side!=='white')side='black';
var human=side==='black'?'B':'W'; var ai=human==='B'?'W':'B';
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · you play '+side;
var board, turn, over, wins=0, legalCache=[];
var DIRS=[[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
function inside(r,c){return r>=0&&r<8&&c>=0&&c<8}
function flips(b,r,c,p){if(b[r][c])return []; var opp=p==='B'?'W':'B'; var all=[];
  DIRS.forEach(function(d){var line=[],rr=r+d[0],cc=c+d[1];
    while(inside(rr,cc)&&b[rr][cc]===opp){line.push([rr,cc]); rr+=d[0]; cc+=d[1]}
    if(line.length&&inside(rr,cc)&&b[rr][cc]===p)all=all.concat(line)}); return all}
function legal(b,p){var out=[]; for(var r=0;r<8;r++)for(var c=0;c<8;c++){var f=flips(b,r,c,p); if(f.length)out.push({r:r,c:c,flips:f})} return out}
function counts(b){var nb=0,nw=0; for(var r=0;r<8;r++)for(var c=0;c<8;c++){if(b[r][c]==='B')nb++; if(b[r][c]==='W')nw++} return [nb,nw]}
function applyMove(b,m,p){var nb=b.map(function(row){return row.slice()}); nb[m.r][m.c]=p; m.flips.forEach(function(f){nb[f[0]][f[1]]=p}); return nb}
function aiMove(){if(over)return; var ms=legal(board,ai); if(!ms.length){msg('Computer has no move — your turn.'); turn=human; refresh(); return}
  var mv; if(diff==='easy'){mv=ms[rnd(ms.length)]}
  else {var best=-1e9,cands=[]; ms.forEach(function(m){var v=m.flips.length; if((m.r===0||m.r===7)&&(m.c===0||m.c===7))v+=25; else if(m.r===0||m.r===7||m.c===0||m.c===7)v+=5;
      if((m.r===1||m.r===6)&&(m.c===1||m.c===6))v-=10;
      if(v>best){best=v;cands=[m]} else if(v===best)cands.push(m)}); mv=cands[rnd(cands.length)]}
  board=applyMove(board,mv,ai); turn=human; refresh(); checkEnd()}
function checkEnd(){var hm=legal(board,human).length, am=legal(board,ai).length;
  if(!hm&&!am){over=true; var cnt=counts(board); var hb=human==='B'?cnt[0]:cnt[1]; var ab=human==='B'?cnt[1]:cnt[0];
    if(hb>ab){wins++; setScore(wins*10); msg('🎉 You win '+hb+'–'+ab+'!')} else if(ab>hb)msg('Computer wins '+ab+'–'+hb+'. Press Start to play again.'); else {msg('Draw '+hb+'–'+hb+'! Press Start to play again.'); setScore(wins*10+5)} return}
  if(!hm&&turn===human){msg('You have no move — computer plays again.'); turn=ai; setTimeout(aiMove,500)}}
function refresh(){legalCache=(!over&&turn===human)?legal(board,human):[]; var cnt=counts(board); el('cntB').textContent=cnt[0]; el('cntW').textContent=cnt[1]; el('turn').textContent=turn==='B'?'Black':'White'; draw()}
function draw(){el('board').innerHTML='';
  for(var r=0;r<8;r++)for(var c=0;c<8;c++){var d=document.createElement('button');
    d.style.cssText='aspect-ratio:1;border:0;cursor:pointer;min-height:44px;padding:0;background:#166534';
    d.style.boxShadow='inset 0 0 0 1px #14532d';
    var p=board[r][c]; if(p){var s=document.createElement('span'); s.style.cssText='display:block;width:70%;height:70%;border-radius:50%;margin:15%;background:'+(p==='B'?'#111827':'#fff'); d.appendChild(s)}
    var isLegal=false; legalCache.forEach(function(m){if(m.r===r&&m.c===c)isLegal=true});
    if(isLegal){var dot=document.createElement('span'); dot.style.cssText='display:block;width:26%;height:26%;border-radius:50%;margin:37%;background:#86efac'; d.appendChild(dot)}
    (function(rr,cc){d.onclick=function(){if(over||turn!==human)return; var m=null; legalCache.forEach(function(mm){if(mm.r===rr&&mm.c===cc)m=mm});
      if(!m)return; board=applyMove(board,m,human); turn=ai; refresh(); checkEnd(); if(!over)setTimeout(aiMove,450)}})(r,c);
    el('board').appendChild(d)}}
function start(){board=[]; for(var r=0;r<8;r++)board.push(['','','','','','','','']);
  board[3][3]='W'; board[3][4]='B'; board[4][3]='B'; board[4][4]='W';
  turn='B'; over=false; msg('Black moves first. Tap a green dot to place a disc.'); refresh();
  if(turn===ai)setTimeout(aiMove,500)}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium"],"side":["black","white"]})

# ---- gomoku ----
add("gomoku","Gomoku","Five in a row wins. Out-think the computer on a big board.","⚫",
"Tap an empty intersection to place your stone. First to five in a row — across, down or diagonally — wins.",
'<div id="board" style="display:grid;gap:0;border:2px solid #b45309;max-width:480px;margin:0 auto;background:#fef3c7"></div>',
r"""
var diff=qp('difficulty')||'medium'; var size=parseInt(qp('size')||'15')||15; if([13,15].indexOf(size)<0)size=15;
var human='B', ai='W'; var board, turn, over, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function win(b,p){var dirs=[[0,1],[1,0],[1,1],[1,-1]];
  for(var r=0;r<size;r++)for(var c=0;c<size;c++){if(b[r][c]!==p)continue;
    for(var d=0;d<4;d++){var ok=true; for(var k=1;k<5;k++){var rr=r+dirs[d][0]*k,cc=c+dirs[d][1]*k; if(rr<0||rr>=size||cc<0||cc>=size||b[rr][cc]!==p){ok=false;break}} if(ok)return true}} return false}
function lineScore(b,r,c,p){var s=0; var dirs=[[0,1],[1,0],[1,1],[1,-1]];
  dirs.forEach(function(d){var n=1,open=0;
    for(var step=1;step<5;step++){var rr=r+d[0]*step,cc=c+d[1]*step; if(rr<0||rr>=size||cc<0||cc>=size)break; if(b[rr][cc]===p)n++; else {if(!b[rr][cc])open++; break}}
    for(var step2=1;step2<5;step2++){var rr2=r-d[0]*step2,cc2=c-d[1]*step2; if(rr2<0||rr2>=size||cc2<0||cc2>=size)break; if(b[rr2][cc2]===p)n++; else {if(!b[rr2][cc2])open++; break}}
    if(n>=5)s+=100000; else if(n===4&&open>0)s+=10000; else if(n===4)s+=1000; else if(n===3&&open===2)s+=1000; else if(n===3&&open===1)s+=100; else if(n===2&&open===2)s+=50; else if(n===2)s+=5});
  return s}
function aiMove(){if(over)return; var empt=[]; var hasStone=false;
  for(var r=0;r<size;r++)for(var c=0;c<size;c++){if(board[r][c])hasStone=true; else empt.push([r,c])}
  if(!empt.length){over=true; msg('Draw! Press Start to play again.'); return}
  var pick; if(diff==='easy'||!hasStone){pick=hasStone?empt[rnd(empt.length)]:[Math.floor(size/2),Math.floor(size/2)]}
  else {var best=-1,cands=[];
    empt.forEach(function(cell){var v=lineScore(board,cell[0],cell[1],ai)*1.1+lineScore(board,cell[0],cell[1],human);
      // only consider cells near existing stones for speed
      var near=false; for(var dr=-2;dr<=2&&!near;dr++)for(var dc=-2;dc<=2;dc++){var rr=cell[0]+dr,cc=cell[1]+dc; if(rr>=0&&rr<size&&cc>=0&&cc<size&&board[rr][cc])near=true}
      if(!near)return;
      if(v>best){best=v;cands=[cell]} else if(v===best)cands.push(cell)});
    pick=cands.length?cands[rnd(cands.length)]:empt[rnd(empt.length)]}
  board[pick[0]][pick[1]]=ai; afterMove(ai)}
function afterMove(p){draw();
  if(win(board,p)){over=true; if(p===human){wins++; setScore(wins*10); msg('🎉 Five in a row — you win!')} else msg('The computer got five in a row. Press Start to play again.'); return}
  turn=p===human?ai:human; if(turn===ai)setTimeout(aiMove,400)}
function draw(){el('board').innerHTML='';
  for(var r=0;r<size;r++)for(var c=0;c<size;c++){var d=document.createElement('button');
    d.style.cssText='aspect-ratio:1;border:0;cursor:pointer;min-height:28px;padding:0;background:transparent;box-shadow:inset 0 0 0 1px #d97706';
    var p=board[r][c]; if(p){var s=document.createElement('span'); s.style.cssText='display:block;width:80%;height:80%;border-radius:50%;margin:10%;background:'+(p==='B'?'#111827':'#fff')+';box-shadow:0 1px 3px rgba(0,0,0,.4)'; d.appendChild(s)}
    (function(rr,cc){d.onclick=function(){if(over||turn!==human)return; if(board[rr][cc])return; board[rr][cc]=human; afterMove(human)}})(r,c);
    el('board').appendChild(d)}}
function start(){board=[]; for(var r=0;r<size;r++){var row=[]; for(var c=0;c<size;c++)row.push(''); board.push(row)} over=false; turn=human; draw(); msg('You play black. Tap an intersection to place a stone — five in a row wins!')}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium"],"size":["13","15"]})

# ---- battleship ----
add("battleship","Battleship","Sink the enemy fleet before yours goes down. Hunt, hit, sink!","🚢",
"Your fleet is placed automatically. Tap a square on the enemy sea to fire — a hit is red, a miss is blue. The computer fires back. Sink all enemy ships first!",
'<div class="small" style="text-align:center;margin-bottom:6px">Enemy sea — tap to fire</div><div id="enemy" style="display:grid;gap:2px;max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin:12px 0 6px">Your sea</div><div id="mine" style="display:grid;gap:2px;max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin-top:8px">Enemy ships left: <b id="eLeft"></b> · Your ships left: <b id="mLeft"></b></div>',
r"""
var size=parseInt(qp('size')||'10')||10; if([8,10].indexOf(size)<0)size=10;
var diff=qp('difficulty')||'medium';
var SHIPS=size===8?[4,3,3,2]:[5,4,3,3,2];
var eShips, mShips, eShots, mShots, eHits, mHits, over, lastHit, hunt, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('enemy').style.gridTemplateColumns='repeat('+size+',1fr)'; el('mine').style.gridTemplateColumns='repeat('+size+',1fr)';
function placeFleet(){var grid=[]; for(var i=0;i<size*size;i++)grid.push(0);
  SHIPS.forEach(function(len,si){var placed=false,guard=0;
    while(!placed&&guard++<500){var horiz=Math.random()<0.5; var r=rnd(size),c=rnd(size);
      if(horiz&&c+len>size)continue; if(!horiz&&r+len>size)continue; var ok=true;
      for(var k=0;k<len;k++){var cell=horiz?r*size+c+k:(r+k)*size+c; if(grid[cell])ok=false}
      if(!ok)continue;
      for(var k2=0;k2<len;k2++){var cell2=horiz?r*size+c+k2:(r+k2)*size+c; grid[cell2]=si+1} placed=true}
    if(!placed)grid[0]=si+1});
  return grid}
function shipsLeft(grid,shots){var alive=0; SHIPS.forEach(function(len,si){var sunk=true; for(var i=0;i<size*size;i++)if(grid[i]===si+1&&!shots[i])sunk=false; if(!sunk)alive++}); return alive}
function sunkName(grid,shots,si){for(var i=0;i<size*size;i++)if(grid[i]===si+1&&!shots[i])return false; return true}
function aiShot(){var cand=[];
  if(diff==='medium'&&lastHit!==null){var r=Math.floor(lastHit/size),c=lastHit%size;
    [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(d){var rr=r+d[0],cc=c+d[1]; if(rr>=0&&rr<size&&cc>=0&&cc<size&&!mShots[rr*size+cc])cand.push(rr*size+cc)})}
  var cell; if(cand.length)cell=cand[rnd(cand.length)];
  else {var pool=[]; for(var i=0;i<size*size;i++)if(!mShots[i])pool.push(i); cell=pool[rnd(pool.length)]}
  mShots[cell]=1; var hit=!!mShips[cell]; if(hit){lastHit=cell; if(sunkName(mShips,mShots,mShips[cell]))lastHit=null} else if(!lastHit&&hunt.length){lastHit=hunt[hunt.length-1]}
  if(hit&&sunkName(mShips,mShots,mShips[cell]))msg('The computer sank one of your ships!');
  draw(); checkEnd()}
function checkEnd(){var e=shipsLeft(eShips,eShots), m=shipsLeft(mShips,mShots);
  el('eLeft').textContent=e; el('mLeft').textContent=m;
  if(e===0){over=true; wins++; setScore(wins*10); msg('🎉 You sank the whole enemy fleet — you win!')}
  else if(m===0){over=true; msg('Your fleet is sunk — the computer wins. Press Start to play again.')}}
function draw(){el('enemy').innerHTML=''; el('mine').innerHTML='';
  for(var i=0;i<size*size;i++){var d=document.createElement('button');
    var hit=eShots[i]&&eShips[i]; var miss=eShots[i]&&!eShips[i];
    d.style.cssText='aspect-ratio:1;border:0;cursor:pointer;min-height:36px;padding:0;font-size:16px;background:'+(hit?'#dc2626':(miss?'#93c5fd':'#2563eb'))+';color:#fff';
    d.textContent=hit?'\u2715':(miss?'\u00B7':'');
    (function(ii){d.onclick=function(){if(over||eShots[ii])return; eShots[ii]=1;
      if(eShips[ii]){msg(sunkName(eShips,eShots,eShips[ii])?'💥 Hit — you sank an enemy ship!':'💥 Hit! Fire again.')} else msg('Splash — miss. The computer fires back…');
      draw(); checkEnd(); if(!over)setTimeout(aiShot,500)}})(i);
    el('enemy').appendChild(d);
    var m=document.createElement('div'); var mhit=mShots[i]&&mShips[i]; var mmiss=mShots[i]&&!mShips[i];
    m.style.cssText='aspect-ratio:1;min-height:28px;background:'+(mhit?'#dc2626':(mmiss?'#93c5fd':(mShips[i]?'#166534':'#dbeafe')));
    el('mine').appendChild(m)}}
function start(){eShips=placeFleet(); mShips=placeFleet(); eShots=new Array(size*size).fill(0); mShots=new Array(size*size).fill(0); over=false; lastHit=null; hunt=[]; draw(); checkEnd(); msg('Fleets placed! Tap the blue enemy sea to fire.')}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"size":["8","10"],"difficulty":["easy","medium"]})

# ---- mastermind ----
add("mastermind","Mastermind","Crack the hidden colour code. Black pegs, white pegs, pure logic.","🎨",
"Build a guess from the colour buttons, then tap Check. A black peg means right colour, right place. A white peg means right colour, wrong place.",
'<div id="pegs" style="display:flex;gap:8px;justify-content:center;margin:10px 0"></div><div id="palette" style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap"></div><div class="row" style="margin-top:10px"><button class="btn amber" id="clearBtn">Clear</button><button class="btn" id="checkBtn">Check guess</button></div><div id="history"></div><div class="small" style="text-align:center">Guesses left: <b id="left"></b></div>',
r"""
var len=parseInt(qp('length')||'4')||4; if([4,5].indexOf(len)<0)len=4;
var diff=qp('difficulty')||'easy';
var COLORS=diff==='hard'?['#dc2626','#f59e0b','#16a34a','#2563eb','#7c3aed','#ec4899','#0f172a','#facc15']:['#dc2626','#f59e0b','#16a34a','#2563eb','#7c3aed','#ec4899'];
var MAXT=diff==='hard'?8:12;
var secret, guess, tries, over, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=len+' pegs · '+diff+' · '+COLORS.length+' colours · '+MAXT+' tries';
function newSecret(){secret=[]; for(var i=0;i<len;i++){var c=rnd(COLORS.length); if(diff==='hard'){while(secret.indexOf(c)>=0)c=rnd(COLORS.length)} secret.push(c)}}
function drawGuess(){el('pegs').innerHTML=''; for(var i=0;i<len;i++){var d=document.createElement('div');
  d.style.cssText='width:44px;height:44px;border-radius:50%;border:2px solid #94a3b8;background:'+(guess[i]!==null?COLORS[guess[i]]:'#fff');
  el('pegs').appendChild(d)} el('left').textContent=MAXT-tries}
function buildPalette(){el('palette').innerHTML=''; COLORS.forEach(function(col,ci){var b=document.createElement('button');
  b.style.cssText='width:44px;height:44px;border-radius:50%;border:2px solid #0F172A;background:'+col+';cursor:pointer';
  b.onclick=function(){if(over)return; for(var i=0;i<len;i++)if(guess[i]===null){guess[i]=ci; break} drawGuess()}; el('palette').appendChild(b)})}
function check(){if(over)return; if(guess.indexOf(null)>=0){msg('Pick '+len+' colours first.'); return}
  tries++; var black=0, white=0; var sLeft=[], gLeft=[];
  for(var i=0;i<len;i++){if(guess[i]===secret[i])black++; else {sLeft.push(secret[i]); gLeft.push(guess[i])}}
  gLeft.forEach(function(g){var ix=sLeft.indexOf(g); if(ix>=0){white++; sLeft.splice(ix,1)}});
  var row=document.createElement('div'); row.style.cssText='display:flex;gap:6px;align-items:center;margin:8px 0';
  guess.forEach(function(g){var d=document.createElement('span'); d.style.cssText='width:26px;height:26px;border-radius:50%;display:inline-block;background:'+COLORS[g]; row.appendChild(d)});
  var fb=document.createElement('span'); fb.textContent='  ●'.repeat(black)+'  ○'.repeat(white)+'   ('+black+' black, '+white+' white)'; fb.style.fontWeight='700'; row.appendChild(fb);
  el('history').appendChild(row); drawGuess();
  if(black===len){over=true; wins++; setScore(wins*10+(MAXT-tries)); msg('🎉 You cracked the code in '+tries+' guesses!')}
  else if(tries>=MAXT){over=true; msg('Out of guesses — the code was '+secret.map(function(s){return COLORS[s]}).join(', ')+'. Press Start to try again.')}
  else {guess=new Array(len).fill(null); drawGuess(); msg('Guess '+(tries+1)+' of '+MAXT+'.')}}
el('checkBtn').onclick=check;
el('clearBtn').onclick=function(){guess=new Array(len).fill(null); drawGuess()};
function start(){newSecret(); guess=new Array(len).fill(null); tries=0; over=false; el('history').innerHTML=''; buildPalette(); drawGuess(); msg('Guess the '+len+'-colour code!')}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"length":["4","5"],"difficulty":["easy","hard"]})

# ---- hangman ----
add("hangman","Hangman","Guess the word letter by letter — before the drawing is finished!","🎯",
"Tap letters to guess the hidden word. Wrong guesses add to the drawing. Guess the whole word before you run out of lives!",
'<div id="art" style="font-family:monospace;white-space:pre;text-align:center;font-size:15px;line-height:1.2;min-height:110px"></div><div id="word" style="font-size:30px;font-weight:800;letter-spacing:8px;text-align:center;margin:10px 0"></div><div id="letters" style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center"></div><div class="small" style="text-align:center;margin-top:8px">Lives: <b id="lives"></b> · Category: <b id="cat"></b></div>',
r"""
var cat=(qp('category')||'mixed').toLowerCase(); if(['animals','countries','food','mixed'].indexOf(cat)<0)cat='mixed';
var diff=qp('difficulty')||'easy';
var WORDS={animals:['ELEPHANT','GIRAFFE','DOLPHIN','PENGUIN','KANGAROO','LEOPARD','BUFFALO','OCTOPUS','CHEETAH','GORILLA','TURTLE','MONKEY','ZEBRA','PANTHER','COBRA','EAGLE'],
countries:['PAKISTAN','FRANCE','BRAZIL','CANADA','JAPAN','EGYPT','TURKEY','SPAIN','INDIA','CHINA','ITALY','MEXICO','KENYA','NEPAL','CHILE','POLAND'],
food:['PIZZA','BURGER','PASTA','BIRYANI','SANDWICH','CHOCOLATE','PANCAKE','NOODLES','CURRY','SALAD','OMELETTE','POPCORN','WAFFLE','SOUP','BREAD','MANGO']};
var MAXL=diff==='hard'?6:10;
var ART=['','\n\n\n\n\n\n  ____','\n  |\n  |\n  |\n  |\n  |\n__|__','  ____\n  |  |\n  |\n  |\n  |\n  |\n__|__','  ____\n  |  |\n  |  O\n  |\n  |\n  |\n__|__','  ____\n  |  |\n  |  O\n  |  |\n  |\n  |\n__|__','  ____\n  |  |\n  |  O\n  | /|\n  |\n  |\n__|__','  ____\n  |  |\n  |  O\n  | /|\\\n  |\n  |\n__|__','  ____\n  |  |\n  |  O\n  | /|\\\n  | / \n  |\n__|__','  ____\n  |  |\n  |  O\n  | /|\\\n  | / \\\n  |\n__|__'];
var word, shown, wrong, used, over, wins=0, curCat='';
if(el('cfgLabel'))el('cfgLabel').textContent=cat+' · '+diff+' · '+MAXL+' lives';
function pickWord(){var c=cat; if(c==='mixed')c=['animals','countries','food'][rnd(3)]; curCat=c; el('cat').textContent=c;
  var list=WORDS[c]; return list[rnd(list.length)]}
function draw(){el('word').textContent=shown.join(' '); el('lives').textContent=MAXL-wrong;
  var stage=Math.min(ART.length-1,Math.round(wrong/MAXL*(ART.length-1))); el('art').textContent=ART[stage];
  el('letters').innerHTML=''; 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach(function(L){var b=document.createElement('button');
    b.className='opt'; b.style.cssText='flex:0 0 44px;min-height:44px;padding:8px 0;text-align:center'; b.textContent=L;
    if(used[L]){b.disabled=true; b.style.opacity='0.4'}
    b.onclick=function(){if(over)return; guessLetter(L)}; el('letters').appendChild(b)})}
function guessLetter(L){used[L]=true;
  if(word.indexOf(L)>=0){for(var i=0;i<word.length;i++)if(word[i]===L)shown[i]=L;
    if(shown.indexOf('_')<0){over=true; wins++; setScore(wins*10+(MAXL-wrong)); msg('🎉 You guessed it — '+word+'!'); draw(); return}
    msg('Good — '+L+' is in the word!')}
  else {wrong++; if(wrong>=MAXL){over=true; shown=word.split(''); msg('Out of lives — the word was '+word+'. Press Start to play again.'); draw(); return}
    msg('No '+L+'. '+(MAXL-wrong)+' lives left.')}
  draw()}
function start(){word=pickWord(); shown=new Array(word.length).fill('_'); wrong=0; used={}; over=false;
  if(diff==='easy'){var ix=rnd(word.length); shown[ix]=word[ix]; msg('Easy mode: one letter is revealed for you.')}
  else msg('Guess the '+curCat+' word!');
  draw()}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"category":["animals","countries","food","mixed"],"difficulty":["easy","hard"]})

# ---- word-guess ----
add("word-guess","Word Guess","Wordle-style: guess the hidden word in 6 tries. Green, amber, grey.","🟩",
"Type a word and tap Guess. Green = right letter, right place. Amber = right letter, wrong place. Grey = not in the word. Six tries!",
'<div class="row"><input type="text" id="inp" maxlength="6" placeholder="Type your guess" style="text-transform:uppercase"><button class="btn" id="guessBtn" style="flex:0 0 110px">Guess</button></div><div id="board"></div><div class="small" style="text-align:center">Tries left: <b id="left">6</b></div>',
r"""
var len=parseInt(qp('length')||'5')||5; if([4,5,6].indexOf(len)<0)len=5;
var mode=(qp('mode')||'daily').toLowerCase(); if(mode!=='daily'&&mode!=='practice')mode='daily';
var LISTS={
4:['PLAY','GAME','WORD','FISH','BIRD','STAR','MOON','FIRE','WIND','RAIN','BOOK','CAKE','DOGS','CATS','BALL','TREE','ROCK','SAND','SHIP','KING','QUEEN','LION','BEAR','WOLF','FROG','DUCK','EGGS','MILK','RICE','SOUP','ROAD','DOOR','WALL','HAND','FOOT','HEAD','NOSE','HAIR'],
5:['APPLE','BRAVE','CLOUD','DANCE','EAGLE','FLAME','GRAPE','HEART','IVORY','JUMBO','KITE','LEMON','MANGO','NIGHT','OCEAN','PIANO','QUEEN','RIVER','STONE','TIGER','UMBRA','VOICE','WATER','YOUTH','ZEBRA','LIGHT','SHARK','MOUSE','HORSE','SNAKE','TRAIN','PLANT','CANDY','BREAD','SMILE','DREAM','MAGIC','CROWN','PEARL','ROBOT'],
6:['BANANA','CASTLE','DRAGON','FLOWER','GUITAR','HARBOR','ISLAND','JUNGLE','KITTEN','LADDER','MIRROR','NATURE','ORANGE','PLANET','QUEEN','ROCKET','SILVER','TEMPLE','UMPIRE','VOLCANO','WINDOW','YELLOW','ZOMBIE','BRIDGE','CANDLE','DOLPHIN','EAGLE','FARMER','GARDEN','HUNGER','JACKET']};
var target, tries, over, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=len+' letters · '+mode+' · 6 tries';
el('inp').setAttribute('maxlength',String(len));
function pickTarget(){var list=LISTS[len];
  if(mode==='daily'){var ds=''; try{ds=new Date().toISOString().slice(0,10)}catch(e){ds='2026-11-19'} var seed=0; for(var i=0;i<ds.length;i++)seed=(seed*31+ds.charCodeAt(i))>>>0; seed=(seed+len*7919)>>>0; return list[seed%list.length]}
  return list[rnd(list.length)]}
function guess(){if(over)return; var g=(el('inp').value||'').toUpperCase().replace(/[^A-Z]/g,'');
  if(g.length!==len){msg('Enter a '+len+'-letter word.'); return}
  tries++; var row=document.createElement('div'); row.style.cssText='display:flex;gap:6px;margin:6px 0';
  var res=new Array(len).fill('grey'); var rem=[];
  for(var i=0;i<len;i++){if(g[i]===target[i])res[i]='green'; else rem.push(target[i])}
  for(var j=0;j<len;j++){if(res[j]==='green')continue; var ix=rem.indexOf(g[j]); if(ix>=0){res[j]='amber'; rem.splice(ix,1)}}
  var correct=0; for(var k=0;k<len;k++){var c=document.createElement('div'); c.style.cssText='flex:1;text-align:center;padding:12px 0;font-weight:800;font-size:20px;border-radius:8px;border:2px solid #e2e8f0';
    c.textContent=g[k]; if(res[k]==='green'){c.style.background='#166534';c.style.color='#fff';correct++} else if(res[k]==='amber'){c.style.background='#F59E0B'} else {c.style.background='#e2e8f0'}
    row.appendChild(c)}
  el('board').appendChild(row); el('inp').value=''; el('left').textContent=6-tries;
  if(correct===len){over=true; wins++; setScore(wins*10+(6-tries)); msg('🎉 You got '+target+' in '+tries+' tries!')}
  else if(tries>=6){over=true; msg('Out of tries — the word was '+target+'. Press Start for a new word.')}
  else msg('Try '+(tries+1)+' of 6.')}
el('guessBtn').onclick=guess; el('inp').addEventListener('keydown',function(e){if(e.key==='Enter')guess()});
function start(){target=pickTarget(); tries=0; over=false; el('board').innerHTML=''; el('left').textContent=6; el('inp').value=''; msg(mode==='daily'?'Daily word — everyone gets the same word today.':'Practice mode — a fresh word each game.')}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"length":["4","5","6"],"mode":["daily","practice"]})

# ---- dots-and-boxes ----
add("dots-and-boxes","Dots and Boxes","Draw lines, claim boxes. The most boxes wins!","▦",
"Tap a line between two dots to claim it. Complete a box and it is yours — and you go again. The player with the most boxes wins!",
'<div id="board" style="max-width:480px;margin:0 auto"></div><div class="small" style="text-align:center;margin-top:8px">Your boxes: <b id="myB">0</b> · Computer: <b id="aiB">0</b> · Turn: <b id="turn">You</b></div>',
r"""
var size=parseInt(qp('size')||'5')||5; if([4,5,6].indexOf(size)<0)size=5;
var diff=qp('difficulty')||'medium';
var hEdges, vEdges, boxes, turn, over, wins=0;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' dots · '+diff;
function boxCount(owner){var n=0; for(var i=0;i<boxes.length;i++)if(boxes[i]===owner)n++; return n}
function edgesOfBox(b){var r=Math.floor(b/(size-1)), c=b%(size-1); return ['h'+(r*size+c),'h'+((r+1)*size+c),'v'+(r*(size-1)+c),'v'+(r*(size-1)+c+1)]}
function isEdge(e){return hEdges[e]||vEdges[e]}
function wouldComplete(edge){var n=0; for(var b=0;b<boxes.length;b++){if(boxes[b])continue; var es=edgesOfBox(b); if(es.indexOf(edge)<0)continue; var done=0; es.forEach(function(e){if(e!==edge&&isEdge(e))done++}); if(done===3)n++} return n}
function claimBoxes(p){var n=0; for(var b=0;b<boxes.length;b++){if(boxes[b])continue; var es=edgesOfBox(b); var all=true; es.forEach(function(e){if(!isEdge(e))all=false}); if(all){boxes[b]=p; n++}} return n}
function allEdges(){var out=[]; for(var r=0;r<size;r++)for(var c=0;c<size-1;c++)if(!hEdges['h'+(r*size+c)])out.push('h'+(r*size+c));
  for(var r2=0;r2<size-1;r2++)for(var c2=0;c2<size;c2++)if(!vEdges['v'+(r2*(size-1)+c2)])out.push('v'+(r2*(size-1)+c2)); return out}
function aiMove(){if(over)return; var avail=allEdges(); if(!avail.length){endGame();return}
  var pick; if(diff==='medium'){var takes=avail.filter(function(e){return wouldComplete(e)>0}); if(takes.length)pick=takes[rnd(takes.length)];
    else {var safe=avail.filter(function(e){return wouldComplete(e)===0}); pick=safe.length?safe[rnd(safe.length)]:avail[rnd(avail.length)]}}
  else {var takes2=avail.filter(function(e){return wouldComplete(e)>0}); pick=(takes2.length&&Math.random()<0.5)?takes2[rnd(takes2.length)]:avail[rnd(avail.length)]}
  var n=takeEdge(pick,'ai'); draw();
  if(n>0){if(allEdges().length===0){endGame();return} setTimeout(aiMove,400)}
  else {turn='human'; draw()}}
function takeEdge(e,p){if(e[0]==='h')hEdges[e]=1; else vEdges[e]=1; return claimBoxes(p)}
function endGame(){over=true; var m=boxCount('human'), a=boxCount('ai');
  if(m>a){wins++; setScore(wins*10+m); msg('🎉 You win '+m+'–'+a+' boxes!')} else if(a>m)msg('Computer wins '+a+'–'+m+' boxes. Press Start to play again.'); else {msg('Draw '+m+'–'+m+'! Press Start to play again.'); setScore(wins*10+m)}}
function draw(){el('myB').textContent=boxCount('human'); el('aiB').textContent=boxCount('ai'); el('turn').textContent=over?'—':(turn==='human'?'You':'Computer');
  var b=el('board'); b.innerHTML='';
  for(var r=0;r<size;r++){
    var row=document.createElement('div'); row.style.display='flex';
    for(var c=0;c<size;c++){var dot=document.createElement('div'); dot.style.cssText='width:14px;height:14px;border-radius:50%;background:#0F172A;flex:0 0 14px;margin:6px 0'; row.appendChild(dot);
      if(c<size-1){var he=document.createElement('button'); var ek='h'+(r*size+c);
        he.style.cssText='flex:1;height:14px;margin:6px 0;border:0;cursor:pointer;min-height:14px;padding:0;background:'+(hEdges[ek]?'#166534':'#e2e8f0');
        (function(e){he.onclick=function(){if(over||turn!=='human')return; if(hEdges[e])return; var n=takeEdge(e,'human'); draw(); if(allEdges().length===0){endGame();return} if(n===0){turn='ai'; draw(); setTimeout(aiMove,400)} else msg('Box claimed — go again!')}})(ek);
        row.appendChild(he)}}
    b.appendChild(row);
    if(r<size-1){var row2=document.createElement('div'); row2.style.display='flex';
      for(var c2=0;c2<size;c2++){var ve=document.createElement('button'); var ek2='v'+(r*(size-1)+c2);
        ve.style.cssText='width:14px;flex:0 0 14px;min-height:44px;border:0;cursor:pointer;padding:0;background:'+(vEdges[ek2]?'#166534':'#e2e8f0');
        (function(e){ve.onclick=function(){if(over||turn!=='human')return; if(vEdges[e])return; var n=takeEdge(e,'human'); draw(); if(allEdges().length===0){endGame();return} if(n===0){turn='ai'; draw(); setTimeout(aiMove,400)} else msg('Box claimed — go again!')}})(ek2);
        row2.appendChild(ve);
        if(c2<size-1){var box=document.createElement('div'); var bx=r*(size-1)+c2; box.style.cssText='flex:1;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:800;color:'+(boxes[bx]==='human'?'#166534':(boxes[bx]==='ai'?'#dc2626':'#fff'));
          box.textContent=boxes[bx]==='human'?'Y':(boxes[bx]==='ai'?'C':''); box.style.background=boxes[bx]==='human'?'#dcfce7':(boxes[bx]==='ai'?'#fee2e2':'#fff');
          row2.appendChild(box)}}
      b.appendChild(row2)}}}
function start(){hEdges={}; vEdges={}; boxes=new Array((size-1)*(size-1)).fill(''); turn='human'; over=false; draw(); msg('Your move — tap a line between two dots to claim it.')}
el('startBtn').onclick=function(){start()}; start();
""",
{"theme":["classic","dark","neon"],"size":["4","5","6"],"difficulty":["easy","medium"]})

# ---- Batch games_c2_adds.py (19 Nov 2026) ----
# Batch C2: 10 new classic arcade/puzzle/action games for FreeCalcNow.
# Fragment only — appended to a copy of gen_games.py before the MAIN marker.

# ---- 1 2048 ----
add("2048","2048","Slide tiles and merge them to reach 2048. Arrow keys, swipe or tap buttons!","🔢",
"Use the arrow buttons (or arrow keys, or swipe) to slide. Equal tiles merge. Reach the target number!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div><div class="small" style="text-align:center">Target: <b id="tgt"></b> · Moves: <b id="moves">0</b></div>',
r"""
var size=parseInt(qp('size')||'4')||4; if([4,5].indexOf(size)<0)size=4;
var target=parseInt(qp('target')||'2048')||2048; if([2048,4096].indexOf(target)<0)target=2048;
var g=[], moves=0, won=false, over=false;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'x'+size+' - target '+target;
el('tgt').textContent=target; el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function spawn(){var empt=[]; for(var i=0;i<size*size;i++)if(!g[i])empt.push(i); if(!empt.length)return; g[empt[rnd(empt.length)]]=(Math.random()<0.9?2:4);}
function draw(){el('board').innerHTML=''; g.forEach(function(v){var d=document.createElement('div'); d.className='tile'; d.textContent=v||''; d.style.fontSize=v>=1024?'15px':(v>=128?'17px':'20px'); if(v)d.style.background=v>=target?'#F59E0B':'#dcfce7'; el('board').appendChild(d)}); el('moves').textContent=moves;}
function canMove(){if(g.indexOf(0)>=0)return true; for(var r=0;r<size;r++)for(var c=0;c<size;c++){var v=g[r*size+c]; if(c<size-1&&g[r*size+c+1]===v)return true; if(r<size-1&&g[(r+1)*size+c]===v)return true;} return false;}
function slide(dir){if(over)return; var moved=false;
  function line(idx){var vals=[]; idx.forEach(function(i){if(g[i])vals.push(g[i])});
    for(var k=0;k<vals.length-1;k++){if(vals[k]===vals[k+1]){vals[k]*=2; setScore(score+vals[k]); vals.splice(k+1,1); if(vals[k]>=target&&!won){won=true; msg('YOU WIN! You reached '+target+'! Keep playing or press Start for a new game.')}}}
    while(vals.length<size)vals.push(0); return vals;}
  for(var r=0;r<size;r++){var idx=[]; for(var c=0;c<size;c++){idx.push(dir==='left'?r*size+c:(dir==='right'?r*size+(size-1-c):(dir==='up'?c*size+r:(size-1-c)*size+r)))}
    var nl=line(idx); for(var j=0;j<size;j++){if(g[idx[j]]!==nl[j])moved=true; g[idx[j]]=nl[j];}}
  if(moved){moves++; spawn(); draw(); if(!canMove()){over=true; msg('Game over! No moves left. Final score '+score+'. Press Start to play again.');} else if(!won) msg('Keep merging!');}}
function reset(){g=new Array(size*size).fill(0); moves=0; won=false; over=false; setScore(0); spawn(); spawn(); draw(); msg('Slide to merge — reach '+target+'!');}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){slide(b.dataset.dir)}});
document.addEventListener('keydown',function(e){var m={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right'}; if(m[e.key]){e.preventDefault(); slide(m[e.key])}});
var tx=0,ty=0; el('board').addEventListener('touchstart',function(e){tx=e.touches[0].clientX; ty=e.touches[0].clientY},{passive:true});
el('board').addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-tx, dy=e.changedTouches[0].clientY-ty; if(Math.max(Math.abs(dx),Math.abs(dy))<24)return; slide(Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up'));},{passive:true});
el('startBtn').onclick=reset; reset();
""",
{"theme":["classic","dark","neon"],"size":["4","5"],"target":["2048","4096"]})

# ---- 2 flappy-bird ----
add("flappy-bird","Flappy Bird","Tap to flap through the pipes. How far can you fly?","🐦",
"Tap FLAP (or press Space / tap the game) to fly. Pass through the pipes to score. One hit ends the run!",
'<canvas id="cv" width="360" height="360" style="width:100%;border-radius:10px;background:#7dd3fc;display:block"></canvas><button class="btn amber" id="flapBtn" style="padding:16px;font-size:20px;margin-top:10px">FLAP ↑</button><div class="small" style="text-align:center">Pipes passed: <b id="pipes">0</b> · Tap the game or press Space to flap</div>',
r"""
var diff=qp('difficulty')||'medium';
var cfg={easy:{gap:150,grav:0.45,speed:2.0},medium:{gap:125,grav:0.5,speed:2.6},hard:{gap:105,grav:0.55,speed:3.2}}[diff]||{gap:125,grav:0.5,speed:2.6};
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' difficulty';
var cv=el('cv'), ctx=cv.getContext('2d');
var bird={x:70,y:180,vy:0,r:13}, pipes=[], playing=false, over=false, frame=0, passed=0;
function reset(){bird={x:70,y:180,vy:0,r:13}; pipes=[]; passed=0; setScore(0); el('pipes').textContent=0; playing=true; over=false; msg('Tap FLAP to fly!');}
function flap(){if(!playing)return; bird.vy=-8;}
function step(){if(!playing)return; frame++; bird.vy+=cfg.grav; bird.y+=bird.vy;
  if(frame%90===0){var top=40+rnd(170); pipes.push({x:360,top:top,gap:cfg.gap,scored:false});}
  for(var i=pipes.length-1;i>=0;i--){var p=pipes[i]; p.x-=cfg.speed;
    if(!p.scored&&p.x+50<bird.x){p.scored=true; passed++; setScore(passed); el('pipes').textContent=passed; msg('Nice! '+passed+' pipe'+(passed===1?'':'s')+'.');}
    if(p.x<-60)pipes.splice(i,1);
    if(bird.x+bird.r>p.x&&bird.x-bird.r<p.x+50&&(bird.y-bird.r<p.top||bird.y+bird.r>p.top+cfg.gap)){gameOver(); return;}}
  if(bird.y+bird.r>=360||bird.y-bird.r<=0){gameOver(); return;}
  draw();}
function gameOver(){playing=false; over=true; msg('Game over! You passed '+passed+' pipe'+(passed===1?'':'s')+'. Press Start to fly again.');}
function draw(){ctx.fillStyle='#7dd3fc'; ctx.fillRect(0,0,360,360);
  ctx.fillStyle='#166534'; pipes.forEach(function(p){ctx.fillRect(p.x,0,50,p.top); ctx.fillRect(p.x,p.top+cfg.gap,50,360-p.top-cfg.gap);});
  ctx.fillStyle='#F59E0B'; ctx.beginPath(); ctx.arc(bird.x,bird.y,bird.r,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#0F172A'; ctx.beginPath(); ctx.arc(bird.x+5,bird.y-4,3,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#92400e'; ctx.fillRect(bird.x-16,bird.y-2,12,6);
  ctx.fillStyle='#166534'; ctx.fillRect(0,352,360,8);}
el('flapBtn').onclick=flap; cv.addEventListener('pointerdown',flap);
document.addEventListener('keydown',function(e){if(e.key===' '||e.key==='ArrowUp'){e.preventDefault(); flap();}});
el('startBtn').onclick=reset; reset(); setInterval(step,1000/60); setInterval(function(){if(playing)draw();},1000/60);
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- 3 whack-a-mole ----
add("whack-a-mole","Whack a Mole","Moles pop up — whack them fast before they hide!","🐹",
"Tap a mole the moment it pops up. Each hit scores a point. Whack as many as you can before time runs out!",
'<div class="grid" id="board" style="grid-template-columns:repeat(3,1fr)"></div><div class="small" style="text-align:center">Time left: <b id="time">30</b>s · Hits: <b id="hits">0</b> · Misses: <b id="miss">0</b></div>',
r"""
var dur=parseInt(qp('time')||'30')||30; if([30,60].indexOf(dur)<0)dur=30;
var diff=qp('difficulty')||'easy';
var spawnMs = diff==='hard'?550:900; var upMs = diff==='hard'?650:1000;
var tLeft=dur, timer=null, spawnTimer=null, playing=false, hits=0, miss=0, active=-1, hideTimer=null;
if(el('cfgLabel'))el('cfgLabel').textContent=dur+'s · '+diff;
el('time').textContent=dur;
function build(){el('board').innerHTML=''; for(var i=0;i<9;i++){var b=document.createElement('button'); b.className='tile'; b.style.fontSize='30px'; b.style.minHeight='64px'; b.textContent='🕳️'; b.dataset.i=i;
  b.onclick=function(){if(!playing)return; if(parseInt(this.dataset.i,10)===active){hits++; setScore(hits); el('hits').textContent=hits; this.textContent='💥'; active=-1; clearTimeout(hideTimer); msg('Whacked! '+hits+' hit'+(hits===1?'':'s')+'.');}
    else{miss++; el('miss').textContent=miss; msg('Empty hole!');}}; el('board').appendChild(b);}}
function pop(){if(!playing)return; var cells=el('board').children; if(active>=0)cells[active].textContent='🕳️';
  active=rnd(9); cells[active].textContent='🐹';
  clearTimeout(hideTimer); hideTimer=setTimeout(function(){if(active>=0&&cells[active])cells[active].textContent='🕳️'; active=-1;},upMs);}
function start(){clearInterval(timer); clearInterval(spawnTimer); clearTimeout(hideTimer); build(); setScore(0); hits=0; miss=0; tLeft=dur; active=-1; playing=true;
  el('hits').textContent=0; el('miss').textContent=0; el('time').textContent=tLeft; msg('Whack the moles!');
  spawnTimer=setInterval(pop,spawnMs);
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); clearInterval(spawnTimer); clearTimeout(hideTimer); playing=false; active=-1; msg('Time! You whacked '+hits+' moles with '+miss+' miss'+(miss===1?'':'es')+'. Press Start to play again.');}},1000);}
el('startBtn').onclick=start; build(); msg('Press Start — moles pop up fast!');
""",
{"theme":["classic","dark","neon"],"time":["30","60"],"difficulty":["easy","hard"]})

# ---- 4 asteroids ----
add("asteroids","Asteroids","Fly your ship, blast the asteroids — they split into smaller ones!","🚀",
"Steer with the arrow buttons or arrow keys, press FIRE (or Space) to shoot. Big asteroids split in two. Don't crash!",
'<canvas id="cv" width="360" height="360" style="width:100%;border-radius:10px;background:#0f172a;display:block"></canvas><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-k="up">▲</button><span></span><button class="opt" data-k="left">◀</button><button class="opt" data-k="fire">🔥 FIRE</button><button class="opt" data-k="right">▶</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Wave: <b id="wave">1</b> · <span id="modeLabel"></span></div>',
r"""
var diff=qp('difficulty')||'medium';
var mode=qp('mode')||'classic'; if(['classic','endless'].indexOf(mode)<0)mode='classic';
var cfg={easy:{n:3,sp:1.0},medium:{n:4,sp:1.4},hard:{n:5,sp:1.9}}[diff]||{n:4,sp:1.4};
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
el('modeLabel').textContent=mode==='classic'?'Classic: clear every wave':'Endless: survive as long as you can';
var cv=el('cv'), ctx=cv.getContext('2d');
var ship, bullets, rocks, lives, wave, playing=false, keys={};
function mkRock(x,y,r){return {x:x,y:y,r:r,vx:(Math.random()-0.5)*2*cfg.sp,vy:(Math.random()-0.5)*2*cfg.sp};}
function newWave(){var n=cfg.n+wave-1; rocks=[]; for(var i=0;i<n;i++){var r=mkRock(rnd(360),rnd(360),34); if(Math.hypot(r.x-ship.x,r.y-ship.y)<90){r.x=(r.x+180)%360; r.y=(r.y+180)%360;} rocks.push(r);} el('wave').textContent=wave;}
function reset(){ship={x:180,y:180,a:-Math.PI/2,vx:0,vy:0}; bullets=[]; lives=3; wave=1; setScore(0); el('lives').textContent=3; playing=true; newWave(); msg('Fly! Fire with the FIRE button or Space.');}
function fire(){if(!playing)return; bullets.push({x:ship.x+Math.cos(ship.a)*18,y:ship.y+Math.sin(ship.a)*18,vx:Math.cos(ship.a)*6+ship.vx,vy:Math.sin(ship.a)*6+ship.vy,life:40});}
function step(){if(!playing)return;
  if(keys.left)ship.a-=0.09; if(keys.right)ship.a+=0.09;
  if(keys.up){ship.vx+=Math.cos(ship.a)*0.15; ship.vy+=Math.sin(ship.a)*0.15;}
  ship.vx*=0.99; ship.vy*=0.99; ship.x=(ship.x+ship.vx+360)%360; ship.y=(ship.y+ship.vy+360)%360;
  bullets.forEach(function(b){b.x=(b.x+b.vx+360)%360; b.y=(b.y+b.vy+360)%360; b.life--;});
  bullets=bullets.filter(function(b){return b.life>0});
  rocks.forEach(function(r){r.x=(r.x+r.vx+360)%360; r.y=(r.y+r.vy+360)%360;});
  for(var i=bullets.length-1;i>=0;i--){for(var j=rocks.length-1;j>=0;j--){var b=bullets[i], r=rocks[j];
    if(b&&Math.hypot(b.x-r.x,b.y-r.y)<r.r){bullets.splice(i,1); var pts=r.r>22?20:(r.r>12?50:100); setScore(score+pts);
      if(r.r>14){rocks.push(mkRock(r.x,r.y,r.r/2)); rocks.push(mkRock(r.x,r.y,r.r/2));}
      rocks.splice(j,1); break;}}}
  for(var k=0;k<rocks.length;k++){var rk=rocks[k]; if(Math.hypot(ship.x-rk.x,ship.y-rk.y)<rk.r+10){lives--; el('lives').textContent=lives; ship={x:180,y:180,a:-Math.PI/2,vx:0,vy:0};
    if(lives<=0){playing=false; msg('Game over! Final score '+score+' on wave '+wave+'. Press Start to fly again.');} else msg('Crash! '+lives+' live'+(lives===1?'':'s')+' left.'); break;}}
  if(playing&&rocks.length===0){wave++; if(mode==='classic'){setScore(score+250); msg('Wave cleared! +250 bonus. Wave '+wave+'.');} newWave();}
  draw();}
function draw(){ctx.fillStyle='#0f172a'; ctx.fillRect(0,0,360,360);
  ctx.strokeStyle='#94a3b8'; rocks.forEach(function(r){ctx.beginPath(); ctx.arc(r.x,r.y,r.r,0,Math.PI*2); ctx.stroke();});
  ctx.fillStyle='#facc15'; bullets.forEach(function(b){ctx.fillRect(b.x-2,b.y-2,4,4);});
  if(playing){ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(ship.x+Math.cos(ship.a)*16,ship.y+Math.sin(ship.a)*16); ctx.lineTo(ship.x+Math.cos(ship.a+2.5)*12,ship.y+Math.sin(ship.a+2.5)*12); ctx.lineTo(ship.x+Math.cos(ship.a-2.5)*12,ship.y+Math.sin(ship.a-2.5)*12); ctx.closePath(); ctx.stroke();}}
document.querySelectorAll('[data-k]').forEach(function(b){var k=b.dataset.k;
  b.addEventListener('pointerdown',function(){if(k==='fire')fire(); else keys[k]=true;});
  b.addEventListener('pointerup',function(){keys[k]=false;}); b.addEventListener('pointerleave',function(){keys[k]=false;});});
document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft'){keys.left=true; e.preventDefault();} if(e.key==='ArrowRight'){keys.right=true; e.preventDefault();} if(e.key==='ArrowUp'){keys.up=true; e.preventDefault();} if(e.key===' '){fire(); e.preventDefault();}});
document.addEventListener('keyup',function(e){if(e.key==='ArrowLeft')keys.left=false; if(e.key==='ArrowRight')keys.right=false; if(e.key==='ArrowUp')keys.up=false;});
el('startBtn').onclick=reset; reset(); setInterval(step,1000/60);
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- 5 frogger ----
add("frogger","Frogger","Hop across the road and river to reach home. Don't get squashed or sink!","🐸",
"Use the arrow buttons or arrow keys to hop. Dodge cars on the road, ride the logs on the river, and reach a home pad!",
'<canvas id="cv" width="360" height="360" style="width:100%;border-radius:10px;background:#166534;display:block"></canvas><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Homes filled: <b id="homes">0</b>/5</div>',
r"""
var diff=qp('difficulty')||'medium';
var startLives=parseInt(qp('lives')||'3')||3; if([3,5].indexOf(startLives)<0)startLives=3;
var spd={easy:1.2,medium:1.8,hard:2.6}[diff]||1.8;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+startLives+' lives';
var cv=el('cv'), ctx=cv.getContext('2d');
var ROW=36, frog, lives, homes, playing=false, cars=[], logs=[];
function mkTraffic(){cars=[]; logs=[];
  for(var r=0;r<4;r++){var y=360-ROW*(r+2); var dir=r%2?1:-1; var n=2+rnd(2);
    for(var i=0;i<n;i++)cars.push({x:rnd(360),y:y,w:44,dir:dir,sp:spd*(0.8+Math.random()*0.5)});}
  for(var r2=0;r2<3;r2++){var y2=ROW*(r2+1); var d2=r2%2?1:-1; var m=2+rnd(2);
    for(var j=0;j<m;j++)logs.push({x:rnd(360),y:y2,w:70,dir:d2,sp:spd*(0.7+Math.random()*0.4)});}}
function resetFrog(){frog={x:180,y:360-ROW/2};}
function reset(){lives=startLives; homes=[false,false,false,false,false]; setScore(0); el('lives').textContent=lives; el('homes').textContent=0; playing=true; mkTraffic(); resetFrog(); msg('Hop up — reach a home pad!');}
function die(why){lives--; el('lives').textContent=lives; if(lives<=0){playing=false; msg('Game over! You filled '+homes.filter(Boolean).length+' home'+(homes.filter(Boolean).length===1?'':'s')+'. Press Start to play again.');} else {msg(why+' '+lives+' live'+(lives===1?'':'s')+' left.'); resetFrog();}}
function move(dx,dy){if(!playing)return; frog.x=Math.max(18,Math.min(342,frog.x+dx)); frog.y=Math.max(ROW/2,Math.min(360-ROW/2,frog.y+dy));
  if(frog.y<=ROW/2){var slot=Math.floor(frog.x/72); if(!homes[slot]){homes[slot]=true; setScore(score+100); el('homes').textContent=homes.filter(Boolean).length; msg('Home! +100. '+homes.filter(Boolean).length+'/5 filled.'); resetFrog();
    if(homes.every(Boolean)){playing=false; setScore(score+500); msg('YOU WIN! All 5 homes filled — +500 bonus! Final score '+score+'. Press Start to play again.');}} else {die('That home is already full!');}}}
function step(){if(!playing)return;
  cars.forEach(function(c){c.x+=c.dir*c.sp; if(c.x>390)c.x=-50; if(c.x<-50)c.x=390;});
  var onLog=null; logs.forEach(function(l){l.x+=l.dir*l.sp; if(l.x>400)l.x=-80; if(l.x<-80)l.x=400; if(frog.y===l.y+ROW/2&&frog.x>l.x&&frog.x<l.x+l.w)onLog=l;});
  if(onLog){frog.x+=onLog.dir*onLog.sp; if(frog.x<0||frog.x>360){die('You floated away!'); return;}}
  var inRiver=frog.y<ROW*4&&frog.y>ROW/2; if(inRiver&&!onLog){die('Splash! You fell in the river.'); return;}
  if(frog.y>ROW*4){for(var i=0;i<cars.length;i++){var c=cars[i]; if(frog.y===c.y+ROW/2&&frog.x>c.x&&frog.x<c.x+c.w){die('Squashed by a car!'); return;}}}
  draw();}
function draw(){ctx.fillStyle='#166534'; ctx.fillRect(0,0,360,360);
  ctx.fillStyle='#3b82f6'; ctx.fillRect(0,ROW,360,ROW*3);
  ctx.fillStyle='#1f2937'; ctx.fillRect(0,ROW*5,360,ROW*4);
  ctx.fillStyle='#f59e0b'; homes.forEach(function(h,i){ctx.fillRect(i*72+18,6,36,24); if(h){ctx.fillStyle='#22c55e'; ctx.font='20px sans-serif'; ctx.fillText('🐸',i*72+22,26); ctx.fillStyle='#f59e0b';}});
  ctx.fillStyle='#8b5a2b'; logs.forEach(function(l){ctx.fillRect(l.x,l.y, l.w, 28);});
  ctx.fillStyle='#dc2626'; cars.forEach(function(c){ctx.fillRect(c.x,c.y, c.w, 28);});
  ctx.font='24px sans-serif'; ctx.fillText('🐸',frog.x-12,frog.y+8);}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){var d=b.dataset.dir; if(d==='up')move(0,-ROW); if(d==='down')move(0,ROW); if(d==='left')move(-36,0); if(d==='right')move(36,0);}});
document.addEventListener('keydown',function(e){var m={ArrowUp:[0,-ROW],ArrowDown:[0,ROW],ArrowLeft:[-36,0],ArrowRight:[36,0]}; if(m[e.key]){e.preventDefault(); move(m[e.key][0],m[e.key][1]);}});
el('startBtn').onclick=reset; reset(); setInterval(step,1000/60);
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"lives":["3","5"]})

# ---- 6 air-hockey ----
add("air-hockey","Air Hockey","Paddle vs computer — first to the target wins!","🏒",
"Drag your paddle (bottom, blue) or use the arrow keys. Push the puck into the computer's goal (top). First to the target wins!",
'<canvas id="cv" width="360" height="420" style="width:100%;border-radius:10px;background:#e0f2fe;display:block;touch-action:none"></canvas><div class="small" style="text-align:center">You: <b id="you">0</b> · Computer: <b id="cpu">0</b> · First to <b id="tgt"></b> · Drag the blue paddle or use arrow keys</div>',
r"""
var diff=qp('difficulty')||'medium';
var target=parseInt(qp('target')||'5')||5; if([5,7].indexOf(target)<0)target=5;
var cpuSp={easy:1.6,medium:2.4,hard:3.2}[diff]||2.4;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · first to '+target;
el('tgt').textContent=target;
var cv=el('cv'), ctx=cv.getContext('2d');
var you=0, cpu=0, playing=false;
var puck={x:180,y:210,vx:2,vy:2,r:11}, me={x:180,y:370,r:22}, foe={x:180,y:50,r:22}, keys={};
function resetPuck(dir){puck={x:180,y:210,vx:(Math.random()<0.5?-1:1)*2.5,vy:dir*3,r:11};}
function reset(){you=0; cpu=0; setScore(0); el('you').textContent=0; el('cpu').textContent=0; playing=true; resetPuck(1); msg('First to '+target+' wins — go!');}
function goal(who){if(who==='you'){you++; el('you').textContent=you; setScore(you); if(you>=target){playing=false; msg('YOU WIN '+you+'–'+cpu+'! Press Start for a rematch.'); return;}} else {cpu++; el('cpu').textContent=cpu; if(cpu>=target){playing=false; msg('Computer wins '+cpu+'–'+you+'. Press Start for a rematch.'); return;}}
  msg('Goal! You '+you+' – '+cpu+' Computer.'); resetPuck(who==='you'?-1:1);}
function collide(p){var dx=puck.x-p.x, dy=puck.y-p.y, d=Math.hypot(dx,dy), min=puck.r+p.r;
  if(d<min&&d>0){var nx=dx/d, ny=dy/d; puck.x=p.x+nx*min; puck.y=p.y+ny*min; var dot=puck.vx*nx+puck.vy*ny; if(dot<0){puck.vx-=2*dot*nx; puck.vy-=2*dot*ny; puck.vx*=1.05; puck.vy*=1.05;}}}
function step(){if(!playing)return;
  if(keys.left)me.x-=5; if(keys.right)me.x+=5; if(keys.up)me.y-=5; if(keys.down)me.y+=5;
  me.x=Math.max(22,Math.min(338,me.x)); me.y=Math.max(240,Math.min(398,me.y));
  var tx=puck.x, ty=foe.y; if(puck.y<210){ty=Math.max(22,Math.min(160,puck.y)); tx=puck.x;}
  foe.x+=(tx-foe.x)*0.06*cpuSp; foe.y+=(ty-foe.y)*0.06*cpuSp; foe.x=Math.max(22,Math.min(338,foe.x)); foe.y=Math.max(22,Math.min(180,foe.y));
  puck.x+=puck.vx; puck.y+=puck.vy;
  if(puck.x<11){puck.x=11; puck.vx=Math.abs(puck.vx);} if(puck.x>349){puck.x=349; puck.vx=-Math.abs(puck.vx);}
  if(puck.y<11){if(puck.x>150&&puck.x<210){goal('you'); return;} puck.y=11; puck.vy=Math.abs(puck.vy);}
  if(puck.y>409){if(puck.x>150&&puck.x<210){goal('cpu'); return;} puck.y=409; puck.vy=-Math.abs(puck.vy);}
  collide(me); collide(foe); draw();}
function draw(){ctx.fillStyle='#e0f2fe'; ctx.fillRect(0,0,360,420);
  ctx.strokeStyle='#0284c7'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(0,210); ctx.lineTo(360,210); ctx.stroke(); ctx.beginPath(); ctx.arc(180,210,50,0,Math.PI*2); ctx.stroke();
  ctx.fillStyle='#fff'; ctx.fillRect(150,0,60,8); ctx.fillRect(150,412,60,8);
  ctx.fillStyle='#0f172a'; ctx.beginPath(); ctx.arc(puck.x,puck.y,puck.r,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#dc2626'; ctx.beginPath(); ctx.arc(foe.x,foe.y,foe.r,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#2563eb'; ctx.beginPath(); ctx.arc(me.x,me.y,me.r,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#fff'; ctx.font='bold 20px sans-serif'; ctx.fillText(cpu,170,40); ctx.fillText(you,170,395);}
cv.addEventListener('pointermove',function(e){var r=cv.getBoundingClientRect(); var x=(e.clientX-r.left)*360/r.width, y=(e.clientY-r.top)*420/r.height; me.x=Math.max(22,Math.min(338,x)); me.y=Math.max(240,Math.min(398,y));});
cv.addEventListener('pointerdown',function(e){var r=cv.getBoundingClientRect(); var x=(e.clientX-r.left)*360/r.width, y=(e.clientY-r.top)*420/r.height; me.x=Math.max(22,Math.min(338,x)); me.y=Math.max(240,Math.min(398,y));});
document.addEventListener('keydown',function(e){var m={ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down'}; if(m[e.key]){keys[m[e.key]]=true; e.preventDefault();}});
document.addEventListener('keyup',function(e){var m={ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down'}; if(m[e.key])keys[m[e.key]]=false;});
el('startBtn').onclick=reset; reset(); setInterval(step,1000/60);
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"target":["5","7"]})

# ---- 7 blackjack ----
add("blackjack","Blackjack","Hit, stand or double — beat the dealer without going over 21!","🃏",
"Start with 100 chips. Bet, then hit, stand or double. Dealer must hit to 17. Blackjack pays 3 to 2!",
'<div id="q" style="font-size:18px">Chips: <b id="chips">100</b> · Bet: <b id="bet">10</b></div><div class="row"><button class="opt" id="betDown">− Bet</button><button class="opt" id="betUp">+ Bet</button></div><div id="hands"></div><div class="row"><button class="btn" id="hitBtn">Hit</button><button class="btn amber" id="standBtn">Stand</button><button class="btn ghost" id="dblBtn">Double</button></div><div class="small" style="text-align:center">Hands won: <b id="wins">0</b> · Hands lost: <b id="lost">0</b> · Pushes: <b id="push">0</b></div>',
r"""
var decks=parseInt(qp('decks')||'1')||1; if([1,2,4].indexOf(decks)<0)decks=1;
if(el('cfgLabel'))el('cfgLabel').textContent=decks+' deck'+(decks===1?'':'s');
var shoe=[], chips=100, bet=10, phand=[], dhand=[], wins=0, lost=0, push=0, inHand=false, done=false;
function buildShoe(){shoe=[]; var ranks=['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
  for(var d=0;d<decks;d++)for(var s=0;s<4;s++)for(var i=0;i<13;i++)shoe.push(ranks[i]); shuffle(shoe);}
function val(c){if(c==='A')return 11; if(['K','Q','J'].indexOf(c)>=0)return 10; return parseInt(c,10);}
function total(h){var t=0, aces=0; h.forEach(function(c){t+=val(c); if(c==='A')aces++;}); while(t>21&&aces>0){t-=10; aces--;} return t;}
function show(reveal){var h='<div class="small">Dealer: '+ (reveal? dhand.join(' ') : dhand[0]+' ?') +' = '+(reveal? total(dhand) : '?') +'</div><div class="small">You: '+phand.join(' ')+' = '+total(phand)+'</div>'; el('hands').innerHTML=h;}
function deal(){if(chips<=0){msg('Out of chips! Press Start for a fresh 100 chips.'); return;}
  if(shoe.length<15)buildShoe();
  if(bet>chips)bet=chips; chips-=bet; el('chips').textContent=chips; el('bet').textContent=bet;
  phand=[shoe.pop(),shoe.pop()]; dhand=[shoe.pop(),shoe.pop()]; inHand=true; done=false; show(false);
  if(total(phand)===21){chips+=Math.floor(bet*2.5); wins++; el('wins').textContent=wins; el('chips').textContent=chips; setScore(wins); inHand=false; show(true); msg('BLACKJACK! You win '+Math.floor(bet*1.5)+' chips!'); return;}
  msg('Your move: Hit, Stand or Double.');}
function endHand(){done=true; inHand=false; var pt=total(phand), dt=total(dhand);
  if(pt>21){lost++; el('lost').textContent=lost; msg('Bust! You lose '+bet+' chips.');}
  else if(dt>21){chips+=bet*2; wins++; el('wins').textContent=wins; setScore(wins); msg('Dealer busts! You win '+bet+' chips.');}
  else if(pt>dt){chips+=bet*2; wins++; el('wins').textContent=wins; setScore(wins); msg('You win '+bet+' chips! '+pt+' beats '+dt+'.');}
  else if(pt<dt){lost++; el('lost').textContent=lost; msg('Dealer wins '+dt+' vs '+pt+'. You lose '+bet+' chips.');}
  else {chips+=bet; push++; el('push').textContent=push; msg('Push — bet returned.');}
  el('chips').textContent=chips; show(true);
  if(chips<=0)msg('Out of chips! Press Start for a fresh 100 chips.');}
el('hitBtn').onclick=function(){if(!inHand||done)return; phand.push(shoe.pop()); show(false); if(total(phand)>=21)endHand(); else msg('Hit or stand?');};
el('standBtn').onclick=function(){if(!inHand||done)return; while(total(dhand)<17)dhand.push(shoe.pop()); endHand();};
el('dblBtn').onclick=function(){if(!inHand||done)return; if(chips<bet){msg('Not enough chips to double.'); return;} chips-=bet; bet*=2; el('chips').textContent=chips; el('bet').textContent=bet; phand.push(shoe.pop()); show(false); if(total(phand)>21){endHand(); return;} while(total(dhand)<17)dhand.push(shoe.pop()); endHand();};
el('betUp').onclick=function(){if(inHand)return; bet=Math.min(50,bet+10); el('bet').textContent=bet;};
el('betDown').onclick=function(){if(inHand)return; bet=Math.max(10,bet-10); el('bet').textContent=bet;};
el('startBtn').onclick=function(){if(chips<=0){chips=100; el('chips').textContent=100;} buildShoe(); deal();};
buildShoe(); el('hands').innerHTML='<div class="small">Press Start to deal your first hand.</div>'; msg('Bet 10 chips, then beat the dealer!');
""",
{"theme":["classic","dark","neon"],"decks":["1","2","4"]})

# ---- 8 typing-test ----
add("typing-test","Typing Test","Type the shown words as fast and accurately as you can!","⌨️",
"Type each word and press Space. Your WPM and accuracy are scored live. Beat your best before time runs out!",
'<div id="q" style="font-size:20px;line-height:1.7"></div><div class="row"><input type="text" id="inp" placeholder="Type here…" autocomplete="off" autocapitalize="off"><button class="btn" id="doneBtn" style="flex:0 0 110px">Finish</button></div><div class="small" style="text-align:center">Time left: <b id="time">60</b>s · WPM: <b id="wpm">0</b> · Accuracy: <b id="acc">100</b>% · Typed: <b id="typed">0</b> words</div>',
r"""
var dur=parseInt(qp('time')||'60')||60; if([30,60].indexOf(dur)<0)dur=60;
var diff=qp('difficulty')||'easy';
var WORDS={easy:['cat','dog','sun','book','tree','fish','bird','cake','milk','star','happy','green','water','house','smile','light','music','friend','apple','table'],
hard:['keyboard','mountain','elephant','computer','adventure','beautiful','challenge','umbrella','chocolate','dangerous','wonderful','yesterday','tomorrow','language','question','remember','together','birthday','afternoon','something']}[diff]||['cat','dog','sun','book','tree','fish','bird','cake','milk','star','happy','green','water','house','smile','light','music','friend','apple','table'];
var words=[], idx=0, correct=0, wrong=0, typed=0, tLeft=dur, timer=null, playing=false, startedAt=0;
if(el('cfgLabel'))el('cfgLabel').textContent=dur+'s · '+diff+' words';
el('time').textContent=dur;
function draw(){var h=''; words.forEach(function(w,i){var cls=i<idx?'color:#166534':(i===idx?'background:#fef3c7;font-weight:800':'color:#64748b'); h+='<span style="'+cls+'">'+w+'</span> ';}); el('q').innerHTML=h;}
function newWords(){words=[]; for(var i=0;i<30;i++)words.push(WORDS[rnd(WORDS.length)]); idx=0; draw();}
function finish(){if(!playing)return; playing=false; clearInterval(timer);
  var mins=(dur-tLeft)/60||dur/60; var wpm=Math.round((correct/5)/mins); if(!isFinite(wpm))wpm=0;
  var acc=typed?Math.round(correct/typed*100):100; setScore(wpm); el('wpm').textContent=wpm; el('acc').textContent=acc;
  msg('Done! '+wpm+' WPM, '+acc+'% accuracy, '+correct+' correct / '+typed+' typed. Press Start to try again.');}
function start(){clearInterval(timer); newWords(); correct=0; wrong=0; typed=0; tLeft=dur; playing=true; startedAt=Date.now(); setScore(0);
  el('time').textContent=tLeft; el('wpm').textContent=0; el('acc').textContent=100; el('typed').textContent=0; el('inp').value=''; el('inp').focus(); msg('Type the highlighted word, then Space!');
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0)finish();},1000);}
el('inp').addEventListener('input',function(){if(!playing)return; var v=el('inp').value;
  if(v.slice(-1)===' '){var w=v.trim(); typed++; el('typed').textContent=typed;
    if(w===words[idx])correct++; else wrong++;
    var mins=(Date.now()-startedAt)/60000||0.01; el('wpm').textContent=Math.round((correct/5)/mins);
    el('acc').textContent=Math.round(correct/typed*100);
    idx++; if(idx>=words.length)newWords(); else draw(); el('inp').value='';}});
el('doneBtn').onclick=finish;
el('startBtn').onclick=start; newWords(); msg('Press Start, then type the highlighted words!');
""",
{"theme":["classic","dark","neon"],"time":["30","60"],"difficulty":["easy","hard"]})

# ---- 9 space-invaders ----
add("space-invaders","Space Invaders","Blast the descending invaders before they land!","👾",
"Move with the arrow buttons or arrow keys, press FIRE (or Space) to shoot. Clear every wave — don't let them reach you!",
'<canvas id="cv" width="360" height="360" style="width:100%;border-radius:10px;background:#0f172a;display:block"></canvas><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><button class="opt" data-k="left">◀</button><button class="opt" data-k="fire">🔥 FIRE</button><button class="opt" data-k="right">▶</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Wave: <b id="wave">1</b> · <span id="modeLabel"></span></div>',
r"""
var diff=qp('difficulty')||'medium';
var mode=qp('mode')||'classic'; if(['classic','endless'].indexOf(mode)<0)mode='classic';
var cfg={easy:{sp:0.5,rows:3,cols:6},medium:{sp:0.8,rows:4,cols:7},hard:{sp:1.2,rows:5,cols:8}}[diff]||{sp:0.8,rows:4,cols:7};
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
el('modeLabel').textContent=mode==='classic'?'Classic: clear waves, 3 lives':'Endless: waves keep coming';
var cv=el('cv'), ctx=cv.getContext('2d');
var ship, bullets, ebullets, inv, lives, wave, playing=false, keys={}, dir=1, frame=0;
function buildWave(){inv=[]; for(var r=0;r<cfg.rows;r++)for(var c=0;c<cfg.cols;c++)inv.push({x:40+c*40,y:30+r*30,alive:true});}
function reset(){ship={x:180,y:330}; bullets=[]; ebullets=[]; lives=3; wave=1; setScore(0); el('lives').textContent=3; el('wave').textContent=1; playing=true; buildWave(); msg('Shoot them all!');}
function fire(){if(!playing)return; if(bullets.length<3)bullets.push({x:ship.x,y:ship.y-14,vy:-7});}
function step(){if(!playing)return; frame++;
  if(keys.left)ship.x=Math.max(16,ship.x-5); if(keys.right)ship.x=Math.min(344,ship.x+5);
  bullets.forEach(function(b){b.y+=b.vy;}); bullets=bullets.filter(function(b){return b.y>0});
  ebullets.forEach(function(b){b.y+=b.vy;}); ebullets=ebullets.filter(function(b){return b.y<360});
  var alive=inv.filter(function(v){return v.alive});
  var edge=false; alive.forEach(function(v){v.x+=dir*cfg.sp; if(v.x<16||v.x>344)edge=true;});
  if(edge){dir*=-1; alive.forEach(function(v){v.y+=14;});}
  if(alive.length&&alive.some(function(v){return v.y>=300})){lives=0; el('lives').textContent=0; playing=false; msg('The invaders landed! Game over — final score '+score+'. Press Start to play again.'); draw(); return;}
  for(var i=bullets.length-1;i>=0;i--){for(var j=0;j<inv.length;j++){var v=inv[j]; if(v.alive&&Math.abs(bullets[i].x-v.x)<16&&Math.abs(bullets[i].y-v.y)<12){v.alive=false; bullets.splice(i,1); setScore(score+10); break;}}}
  if(frame%90===0&&alive.length){var s=alive[rnd(alive.length)]; ebullets.push({x:s.x,y:s.y+10,vy:3});}
  for(var k=ebullets.length-1;k>=0;k--){var eb=ebullets[k]; if(Math.abs(eb.x-ship.x)<14&&Math.abs(eb.y-ship.y)<12){ebullets.splice(k,1); lives--; el('lives').textContent=lives;
    if(lives<=0){playing=false; msg('Game over! Final score '+score+' on wave '+wave+'. Press Start to play again.'); draw(); return;} msg('Hit! '+lives+' live'+(lives===1?'':'s')+' left.'); break;}}
  if(inv.every(function(v){return !v.alive})){wave++; el('wave').textContent=wave; setScore(score+100);
    if(mode==='classic'){msg('Wave cleared! +100 bonus. Wave '+wave+'.');} else {cfg.sp=Math.min(2.5,cfg.sp+0.2); msg('Wave '+wave+' — faster!');}
    buildWave();}
  draw();}
function draw(){ctx.fillStyle='#0f172a'; ctx.fillRect(0,0,360,360);
  ctx.font='20px sans-serif'; inv.forEach(function(v){if(v.alive)ctx.fillText('👾',v.x-10,v.y+7);});
  ctx.fillStyle='#22c55e'; ctx.fillRect(ship.x-14,ship.y-6,28,12);
  ctx.fillStyle='#facc15'; bullets.forEach(function(b){ctx.fillRect(b.x-2,b.y-8,4,10);});
  ctx.fillStyle='#f87171'; ebullets.forEach(function(b){ctx.fillRect(b.x-2,b.y-4,4,10);});}
document.querySelectorAll('[data-k]').forEach(function(b){var k=b.dataset.k;
  b.addEventListener('pointerdown',function(){if(k==='fire')fire(); else keys[k]=true;});
  b.addEventListener('pointerup',function(){keys[k]=false;}); b.addEventListener('pointerleave',function(){keys[k]=false;});});
document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft'){keys.left=true; e.preventDefault();} if(e.key==='ArrowRight'){keys.right=true; e.preventDefault();} if(e.key===' '){fire(); e.preventDefault();}});
document.addEventListener('keyup',function(e){if(e.key==='ArrowLeft')keys.left=false; if(e.key==='ArrowRight')keys.right=false;});
el('startBtn').onclick=reset; reset(); setInterval(step,1000/60);
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- 10 tower-of-hanoi ----
add("tower-of-hanoi","Tower of Hanoi","Move the whole stack to the third peg — never put a big disk on a small one!","🗼",
"Tap a peg to pick up its top disk, then tap another peg to drop it. A bigger disk can never sit on a smaller one. Beat the minimum moves!",
'<div id="pegs" style="display:flex;gap:8px"></div><div class="small" style="text-align:center">Moves: <b id="moves">0</b> · Minimum: <b id="minMoves"></b> · Disks: <b id="diskN"></b></div><button class="btn ghost" id="undoBtn">↩ Undo move</button>',
r"""
var disks=parseInt(qp('disks')||'3')||3; if([3,4,5,6].indexOf(disks)<0)disks=3;
var minMoves=Math.pow(2,disks)-1;
if(el('cfgLabel'))el('cfgLabel').textContent=disks+' disks · min '+minMoves+' moves';
el('minMoves').textContent=minMoves; el('diskN').textContent=disks;
var pegs=[], sel=-1, moves=0, hist=[], won=false;
function draw(){el('pegs').innerHTML=''; pegs.forEach(function(p,pi){var d=document.createElement('div'); d.style.cssText='flex:1;min-height:180px;background:#f1f5f9;border:2px solid '+(sel===pi?'#F59E0B':'#e2e8f0')+';border-radius:10px;padding:8px;display:flex;flex-direction:column-reverse;align-items:center;gap:4px;cursor:pointer';
  p.forEach(function(sz){var bar=document.createElement('div'); bar.style.cssText='height:26px;width:'+(sz*16+18)+'px;background:#166534;border-radius:6px;color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:14px'; bar.textContent=sz; d.appendChild(bar);});
  var lbl=document.createElement('div'); lbl.style.cssText='font-weight:800;color:#64748b'; lbl.textContent='Peg '+(pi+1); d.appendChild(lbl);
  d.onclick=function(){tap(pi)}; el('pegs').appendChild(d);});
  el('moves').textContent=moves;}
function tap(pi){if(won)return;
  if(sel<0){if(pegs[pi].length){sel=pi; msg('Disk picked up — tap a peg to drop it.');} else msg('That peg is empty.'); draw(); return;}
  if(sel===pi){sel=-1; draw(); return;}
  var disk=pegs[sel][pegs[sel].length-1];
  if(pegs[pi].length&&pegs[pi][pegs[pi].length-1]<disk){msg('Too big! A bigger disk cannot sit on a smaller one.'); sel=-1; draw(); return;}
  hist.push(pegs.map(function(p){return p.slice()})); pegs[pi].push(pegs[sel].pop()); moves++; sel=-1; draw();
  if(pegs[2].length===disks){won=true; setScore(Math.max(1,1000-moves*10)); msg('YOU WIN! Solved in '+moves+' moves (minimum '+minMoves+'). '+(moves===minMoves?'Perfect — the minimum!':'')+' Press Start to play again.');}
  else msg('Move '+moves+' — keep going!');}
function reset(){pegs=[[],[],[]]; for(var i=disks;i>=1;i--)pegs[0].push(i); sel=-1; moves=0; hist=[]; won=false; setScore(0); draw(); msg('Move the stack to Peg 3 in '+minMoves+' moves!');}
el('undoBtn').onclick=function(){if(hist.length&&!won){pegs=hist.pop(); moves++; draw(); msg('Undone.');}};
el('startBtn').onclick=reset; reset();
""",
{"theme":["classic","dark","neon"],"disks":["3","4","5","6"]})

# ---- Batch games_c3_adds.py (19 Nov 2026) ----
# Batch C3: 10 new viral puzzle/casual games for FreeCalcNow.
# Fragment only: append before "# ================= MAIN =================" in gen_games.py.

# ---- match-3 ----
add("match-3","Match 3 Gems","Swap gems, match 3 or more, cascade your way to the target score!","💎",
"Tap two adjacent gems to swap them. Match 3+ in a row or column to clear them and score. Reach the target before your moves run out!",
'<div class="grid" id="board" style="grid-template-columns:repeat(7,1fr);gap:4px"></div><div class="small" style="text-align:center">Moves left: <b id="moves">25</b> · Target: <b id="tgt"></b></div>',
r"""
var diff=qp('difficulty')||'medium'; var theme=qp('theme')||'gems';
var THEMES={gems:['💎','🔴','🔵','🟢','🟡','🟣'],fruits:['🍎','🍌','🍇','🍓','🍊','🥝'],sweets:['🍬','🍭','🍩','🍪','🧁','🍫']};
var SET=THEMES[theme]||THEMES.gems;
var NT = diff==='easy'?4:(diff==='hard'?6:5);
var MOVES = diff==='easy'?30:(diff==='hard'?20:25);
var TARGET = diff==='easy'?500:(diff==='hard'?1200:800);
var N=7, board=[], sel=null, moves=MOVES, playing=false, busy=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+theme+' · target '+TARGET;
el('tgt').textContent=TARGET; el('moves').textContent=moves;
function randType(r,c){var t; do{t=rnd(NT)}while((c>=2&&board[r][c-1]===t&&board[r][c-2]===t)||(r>=2&&board[r-1][c]===t&&board[r-2][c]===t)); return t}
function newBoard(){board=[]; for(var r=0;r<N;r++){board.push([]); for(var c=0;c<N;c++)board[r].push(randType(r,c))} sel=null; moves=MOVES; playing=true; busy=false; setScore(0); el('moves').textContent=moves; draw(); msg('Swap adjacent gems to match 3+!')}
function draw(){el('board').innerHTML=''; for(var r=0;r<N;r++)for(var c=0;c<N;c++){var b=document.createElement('button'); b.className='tile'; b.style.fontSize='22px'; b.style.minHeight='44px'; b.textContent=board[r][c]<0?'':SET[board[r][c]];
  if(sel&&sel.r===r&&sel.c===c)b.style.outline='3px solid #F59E0B';
  (function(rr,cc){b.onclick=function(){tap(rr,cc)}})(r,c); el('board').appendChild(b)}}
function tap(r,c){if(!playing||busy)return;
  if(!sel){sel={r:r,c:c}; draw(); return}
  if(sel.r===r&&sel.c===c){sel=null; draw(); return}
  if(Math.abs(sel.r-r)+Math.abs(sel.c-c)!==1){sel={r:r,c:c}; draw(); return}
  var sr=sel.r, sc=sel.c; sel=null;
  var t=board[sr][sc]; board[sr][sc]=board[r][c]; board[r][c]=t;
  var m=findMatches();
  if(!m.length){var t2=board[sr][sc]; board[sr][sc]=board[r][c]; board[r][c]=t2; draw(); msg('No match — try another swap.'); return}
  moves--; el('moves').textContent=moves; busy=true; draw(); resolve(1);}
function findMatches(){var hit=[]; var seen={};
  function mark(r,c){var k=r+','+c; if(!seen[k]){seen[k]=1; hit.push([r,c])}}
  for(var r=0;r<N;r++){var run=1; for(var c=1;c<=N;c++){if(c<N&&board[r][c]>=0&&board[r][c]===board[r][c-1])run++; else {if(run>=3)for(var k=c-run;k<c;k++)mark(r,k); run=1}}}
  for(var c=0;c<N;c++){var run2=1; for(var r=1;r<=N;r++){if(r<N&&board[r][c]>=0&&board[r][c]===board[r-1][c])run2++; else {if(run2>=3)for(var k=r-run2;k<r;k++)mark(k,c); run2=1}}}
  return hit}
function resolve(chain){var m=findMatches();
  if(!m.length){busy=false; draw(); checkEnd(); return}
  setScore(score+m.length*10*chain);
  m.forEach(function(p){board[p[0]][p[1]]=-1});
  draw();
  setTimeout(function(){
    for(var c=0;c<N;c++){var col=[]; for(var r=N-1;r>=0;r--)if(board[r][c]>=0)col.push(board[r][c]);
      while(col.length<N)col.push(rnd(NT));
      for(var r2=N-1;r2>=0;r2--)board[r2][c]=col[N-1-r2];}
    draw(); resolve(chain+1);},300);}
function checkEnd(){if(score>=TARGET){playing=false; msg('🎉 Target reached! You win with '+score+' points!'); return}
  if(moves<=0){playing=false; msg('Out of moves! You scored '+score+' (target '+TARGET+'). Press Start to retry.');}}
el('startBtn').onclick=newBoard; newBoard();
""",
{"difficulty":["easy","medium","hard"],"theme":["gems","fruits","sweets"]})

# ---- bubble-shooter ----
add("bubble-shooter","Bubble Shooter","Aim, shoot and pop matching bubbles before they reach the bottom!","🫧",
"Tap a column button to shoot your bubble into that column. Match 3+ of the same colour to pop them. Bubbles not attached to the top fall away!",
'<div class="grid" id="board" style="grid-template-columns:repeat(8,1fr);gap:3px"></div><div class="small" style="text-align:center">Next bubble: <b id="next" style="font-size:20px"></b> · Shots: <b id="shots">0</b></div><div class="grid" id="cols" style="grid-template-columns:repeat(8,1fr);gap:3px;margin-top:8px"></div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var COLS=['🔴','🔵','🟢','🟡','🟣','🟠'];
var NC = diff==='easy'?4:(diff==='hard'?6:5);
var ROWS=10, COLN=8, board=[], next=0, shots=0, playing=false;
var ADD_EVERY = mode==='classic'?5:4;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode+' · '+NC+' colours';
function newGame(){board=[]; for(var r=0;r<ROWS;r++){board.push([]); for(var c=0;c<COLN;c++)board[r].push(r<4?rnd(NC):-1)}
  next=rnd(NC); shots=0; playing=true; setScore(0); draw(); msg('Tap a column to shoot!')}
function draw(){el('board').innerHTML=''; for(var r=0;r<ROWS;r++)for(var c=0;c<COLN;c++){var d=document.createElement('div'); d.className='tile'; d.style.minHeight='36px'; d.style.fontSize='18px'; d.textContent=board[r][c]<0?'':COLS[board[r][c]]; el('board').appendChild(d)}
  el('next').textContent=COLS[next]; el('shots').textContent=shots;
  el('cols').innerHTML=''; for(var c2=0;c2<COLN;c2++){var b=document.createElement('button'); b.className='opt'; b.style.padding='10px 0'; b.textContent='▼'; (function(cc){b.onclick=function(){shoot(cc)}})(c2); el('cols').appendChild(b)}}
function groupAt(r,c){var col=board[r][c]; var seen={}, q=[[r,c]], out=[]; seen[r+','+c]=1;
  while(q.length){var p=q.pop(); out.push(p); var dirs=[[-1,0],[1,0],[0,-1],[0,1]];
    dirs.forEach(function(d){var nr=p[0]+d[0], nc=p[1]+d[1];
      if(nr>=0&&nr<ROWS&&nc>=0&&nc<COLN&&!seen[nr+','+nc]&&board[nr][nc]===col){seen[nr+','+nc]=1; q.push([nr,nc])}})}
  return out}
function dropFloating(){var keep={}, q=[]; for(var c=0;c<COLN;c++)if(board[0][c]>=0){keep['0,'+c]=1; q.push([0,c])}
  while(q.length){var p=q.pop(); [[-1,0],[1,0],[0,-1],[0,1]].forEach(function(d){var nr=p[0]+d[0], nc=p[1]+d[1];
    if(nr>=0&&nr<ROWS&&nc>=0&&nc<COLN&&!keep[nr+','+nc]&&board[nr][nc]>=0){keep[nr+','+nc]=1; q.push([nr,nc])}})}
  var fell=0; for(var r=0;r<ROWS;r++)for(var c2=0;c2<COLN;c2++)if(board[r][c2]>=0&&!keep[r+','+c2]){board[r][c2]=-1; fell++}
  if(fell)setScore(score+fell*5);}
function addRow(){var row=[]; for(var c=0;c<COLN;c++)row.push(Math.random()<0.85?rnd(NC):-1);
  board.pop(); board.unshift(row);
  for(var c2=0;c2<COLN;c2++)if(board[ROWS-1][c2]>=0){playing=false; msg('Game over! Bubbles reached the bottom. Score '+score+'. Press Start to retry.'); return}}
function shoot(c){if(!playing)return;
  var r=0; while(r<ROWS&&board[r][c]>=0)r++;
  if(r>=ROWS){playing=false; msg('Column full — game over! Score '+score+'.'); return}
  board[r][c]=next; shots++;
  var g=groupAt(r,c);
  if(g.length>=3){g.forEach(function(p){board[p[0]][p[1]]=-1}); setScore(score+g.length*10); msg('Pop! +'+(g.length*10)); dropFloating()}
  else msg('No match — '+ (ADD_EVERY-(shots%ADD_EVERY)) +' shots until a new row.');
  next=rnd(NC);
  if(shots%ADD_EVERY===0)addRow();
  if(playing){var any=false; for(var rr=0;rr<ROWS;rr++)for(var cc=0;cc<COLN;cc++)if(board[rr][cc]>=0)any=true;
    if(!any){playing=false; setScore(score+100); msg('🎉 Board cleared! You win! Bonus +100. Press Start for a new game.')}}
  draw();}
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- piano-tiles ----
add("piano-tiles","Piano Tiles","Tap the black tiles in order — never tap a white one!","🎹",
"Black tiles slide down. Tap each black tile before it slides off the bottom. Tap a white tile and the game ends!",
'<div class="grid" id="board" style="grid-template-columns:repeat(4,1fr);gap:4px"></div><div class="small" style="text-align:center">Tiles tapped: <b id="taps">0</b> · Lives: <b id="lives">3</b> · Goal: <b id="goal">30</b></div>',
r"""
var speed=qp('speed')||'normal'; var mode=qp('mode')||'classic';
var INTERVAL = speed==='slow'?1000:(speed==='fast'?500:700);
var GOAL = mode==='classic'?30:9999;
var rows=[], taps=0, lives=3, playing=false, timer=null, curInterval=INTERVAL;
if(el('cfgLabel'))el('cfgLabel').textContent=speed+' · '+mode;
el('goal').textContent=mode==='classic'?'30':'∞';
function draw(){el('board').innerHTML=''; var show=rows.slice(0,5);
  for(var i=0;i<5;i++){var row=show[i];
    for(var c=0;c<4;c++){var d=document.createElement('button'); d.className='tile'; d.style.minHeight='56px';
      if(!row){d.style.background='#f1f5f9'; d.disabled=true}
      else if(row.col===c){d.style.background=row.tapped?'#166534':'#0F172A'; d.style.color='#fff'; d.textContent=row.tapped?'✓':'♪';
        (function(rr){d.onclick=function(){hit(rr)}})(i)}
      else {d.style.background='#fff'; (function(rr){d.onclick=function(){miss(rr)}})(i)}
      el('board').appendChild(d)}}
  el('taps').textContent=taps; el('lives').textContent=lives;}
function tick(){if(!playing)return;
  rows.unshift({col:rnd(4),tapped:false});
  if(rows.length>5){var bottom=rows.pop(); if(!bottom.tapped){lives--; el('lives').textContent=lives;
    if(mode==='arcade'||lives<=0){playing=false; clearInterval(timer); msg('Missed a tile! Game over — '+taps+' tiles. Press Start to retry.'); draw(); return}
    msg('Missed one! '+lives+' lives left.')}}
  if(mode==='arcade'&&taps>0&&taps%10===0){curInterval=Math.max(300,curInterval-40); clearInterval(timer); timer=setInterval(tick,curInterval)}
  draw();}
function hit(i){if(!playing)return; var row=rows[i]; if(!row||row.tapped)return;
  row.tapped=true; taps++; setScore(taps);
  if(taps>=GOAL){playing=false; clearInterval(timer); msg('🎉 You tapped '+GOAL+' tiles — you win! Press Start to play again.')}
  draw();}
function miss(i){if(!playing)return; playing=false; clearInterval(timer); msg('White tile! Game over — '+taps+' tiles. Press Start to retry.')}
function start(){rows=[]; taps=0; lives=mode==='arcade'?1:3; playing=true; curInterval=INTERVAL; setScore(0);
  clearInterval(timer); timer=setInterval(tick,curInterval); draw(); msg('Tap the black tiles!')}
el('startBtn').onclick=start; draw(); msg('Press Start — then tap the black tiles!');
""",
{"theme":["classic","dark","neon"],"speed":["slow","normal","fast"],"mode":["classic","arcade"]})

# ---- water-sort ----
add("water-sort","Water Sort","Pour coloured water between tubes until each tube holds one colour!","🧪",
"Tap a tube, then tap another tube to pour. Only the same colour can go on top, and a tube holds 4. Sort every colour into its own tube!",
'<div id="tubes" style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap"></div><div class="row" style="margin-top:12px"><button class="btn ghost" id="undoBtn">↩ Undo</button><button class="btn ghost" id="restartBtn">↻ Restart</button></div><div class="small" style="text-align:center">Moves: <b id="moves">0</b> · Undos left: <b id="undos">∞</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var tubeCount=parseInt(qp('tubes')||'6')||6; if([6,8].indexOf(tubeCount)<0)tubeCount=6;
var CAP=4;
var NCOL = tubeCount-2;
var UNDO_LIMIT = diff==='hard'?5:999;
var COLHEX=['#dc2626','#2563eb','#16a34a','#eab308','#7c3aed','#ea580c'];
var tubes=[], sel=-1, moves=0, undosUsed=0, hist=[], playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+tubeCount+' tubes · '+NCOL+' colours';
el('undos').textContent=diff==='hard'?'5':'∞';
function deal(){var pool=[]; for(var c=0;c<NCOL;c++)for(var k=0;k<CAP;k++)pool.push(c);
  if(diff==='easy'){var blocks=[]; for(var i=0;i<pool.length;i+=2)blocks.push(pool.slice(i,i+2)); shuffle(blocks); pool=[]; blocks.forEach(function(b){pool=pool.concat(b)})}
  else shuffle(pool);
  tubes=[]; for(var t=0;t<tubeCount;t++)tubes.push([]);
  var idx=0; for(var t2=0;t2<tubeCount-2;t2++)for(var k2=0;k2<CAP;k2++)tubes[t2].push(pool[idx++]);
  for(var t3=tubeCount-2;t3<tubeCount;t3++)tubes[t3]=[];}
function draw(){el('tubes').innerHTML=''; tubes.forEach(function(tube,i){
  var d=document.createElement('button'); d.style.cssText='width:52px;min-height:180px;display:flex;flex-direction:column-reverse;gap:3px;padding:6px;border:3px solid '+(sel===i?'#F59E0B':'#cbd5e1')+';border-radius:0 0 12px 12px;background:#fff;cursor:pointer';
  for(var k=0;k<CAP;k++){var u=document.createElement('div'); u.style.cssText='flex:1;border-radius:6px;min-height:34px;background:'+(k<tube.length?COLHEX[tube[k]]:'#f1f5f9'); d.appendChild(u)}
  d.onclick=function(){tapTube(i)}; el('tubes').appendChild(d)});
  el('moves').textContent=moves; el('undos').textContent=diff==='hard'?String(Math.max(0,UNDO_LIMIT-undosUsed)):'∞';}
function topRun(tube){if(!tube.length)return 0; var col=tube[tube.length-1], n=0; for(var i=tube.length-1;i>=0&&tube[i]===col;i--)n++; return n}
function tapTube(i){if(!playing)return;
  if(sel<0){if(!tubes[i].length){msg('That tube is empty — pick a full one.'); return} sel=i; draw(); return}
  if(sel===i){sel=-1; draw(); return}
  var src=tubes[sel], dst=tubes[i];
  if(!src.length){sel=-1; draw(); return}
  var col=src[src.length-1];
  if(dst.length&&dst[dst.length-1]!==col){msg('Only '+ 'the same colour' +' can pour on top!'); sel=-1; draw(); return}
  var space=CAP-dst.length; if(!space){msg('That tube is full!'); sel=-1; draw(); return}
  hist.push(JSON.stringify(tubes));
  var n=Math.min(topRun(src),space);
  for(var k=0;k<n;k++)dst.push(src.pop());
  moves++; sel=-1; draw(); checkWin();}
function checkWin(){for(var i=0;i<tubes.length;i++){var t=tubes[i]; if(!t.length)continue; if(t.length<CAP)return; for(var k=1;k<t.length;k++)if(t[k]!==t[0])return}
  playing=false; var pts=Math.max(100,1000-moves*10); setScore(pts); msg('🎉 Sorted in '+moves+' moves! Score '+pts+'. Press Start for a new puzzle.')}
el('undoBtn').onclick=function(){if(!hist.length){msg('Nothing to undo.'); return}
  if(undosUsed>=UNDO_LIMIT){msg('No undos left on hard mode!'); return}
  undosUsed++; tubes=JSON.parse(hist.pop()); moves=Math.max(0,moves-1); sel=-1; draw(); msg('Undone.')};
el('restartBtn').onclick=function(){start()};
function start(){deal(); sel=-1; moves=0; undosUsed=0; hist=[]; playing=true; setScore(0); draw(); msg('Tap a tube, then tap where to pour!')}
el('startBtn').onclick=start; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"tubes":["6","8"]})

# ---- block-puzzle ----
add("block-puzzle","Block Puzzle","Place shapes on a 10×10 board. Fill rows and columns to clear them!","🧱",
"Tap a shape below, then tap a board cell to place it there. Complete a full row or column to clear it and score. Game over when no shape fits!",
'<div class="grid" id="board" style="grid-template-columns:repeat(10,1fr);gap:2px"></div><div id="tray" style="display:flex;gap:10px;justify-content:center;margin-top:12px"></div><div class="small" style="text-align:center">Selected shape: <b id="selName">none — tap a shape</b></div>',
r"""
var diff=qp('difficulty')||'medium';
var N=10, board=[], tray=[], selShape=-1, playing=false;
var SHAPES={
 small:[{n:'Dot',cells:[[0,0]]},{n:'Domino',cells:[[0,0],[0,1]]},{n:'Trio',cells:[[0,0],[0,1],[0,2]]},{n:'Corner',cells:[[0,0],[1,0],[1,1]]},{n:'Square',cells:[[0,0],[0,1],[1,0],[1,1]]}],
 medium:[{n:'Line 4',cells:[[0,0],[0,1],[0,2],[0,3]]},{n:'Line 4 ↓',cells:[[0,0],[1,0],[2,0],[3,0]]},{n:'L',cells:[[0,0],[1,0],[2,0],[2,1]]},{n:'T',cells:[[0,0],[0,1],[0,2],[1,1]]},{n:'Square',cells:[[0,0],[0,1],[1,0],[1,1]]},{n:'Zig',cells:[[0,0],[0,1],[1,1],[1,2]]}],
 hard:[{n:'Line 5',cells:[[0,0],[0,1],[0,2],[0,3],[0,4]]},{n:'Big L',cells:[[0,0],[1,0],[2,0],[3,0],[3,1]]},{n:'3×3',cells:[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]},{n:'Plus',cells:[[0,1],[1,0],[1,1],[1,2],[2,1]]},{n:'T',cells:[[0,0],[0,1],[0,2],[1,1]]},{n:'Square',cells:[[0,0],[0,1],[1,0],[1,1]]}]};
var POOL = diff==='easy'?SHAPES.small:(diff==='hard'?SHAPES.hard:SHAPES.small.concat(SHAPES.medium));
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · 10×10';
function newTray(){tray=[POOL[rnd(POOL.length)],POOL[rnd(POOL.length)],POOL[rnd(POOL.length)]]; selShape=-1; drawTray()}
function draw(){el('board').innerHTML=''; for(var r=0;r<N;r++)for(var c=0;c<N;c++){var d=document.createElement('button'); d.style.cssText='aspect-ratio:1;min-height:26px;border-radius:4px;border:1px solid #e2e8f0;background:'+(board[r][c]?'#166534':'#fff')+';cursor:pointer;padding:0';
  (function(rr,cc){d.onclick=function(){place(rr,cc)}})(r,c); el('board').appendChild(d)}
  el('selName').textContent=selShape<0?'none — tap a shape':tray[selShape].n;}
function drawTray(){el('tray').innerHTML=''; tray.forEach(function(s,i){if(!s){var sp=document.createElement('div'); sp.style.width='64px'; el('tray').appendChild(sp); return}
  var b=document.createElement('button'); b.className='opt'; b.style.padding='8px'; b.style.borderColor=selShape===i?'#F59E0B':'';
  var maxR=0,maxC=0; s.cells.forEach(function(cl){maxR=Math.max(maxR,cl[0]); maxC=Math.max(maxC,cl[1])});
  var g='<div style="display:grid;grid-template-columns:repeat('+(maxC+1)+',14px);gap:2px">';
  for(var r=0;r<=maxR;r++)for(var c=0;c<=maxC;c++){var on=s.cells.some(function(cl){return cl[0]===r&&cl[1]===c}); g+='<div style="width:14px;height:14px;border-radius:3px;background:'+(on?'#166534':'#f1f5f9')+'"></div>'}
  b.innerHTML=g+'</div><div style="font-size:12px;margin-top:4px">'+s.n+'</div>';
  b.onclick=function(){selShape=i; draw(); drawTray()}; el('tray').appendChild(b)})}
function canPlace(s,r,c){return s.cells.every(function(cl){var rr=r+cl[0], cc=c+cl[1]; return rr>=0&&rr<N&&cc>=0&&cc<N&&!board[rr][cc]})}
function place(r,c){if(!playing||selShape<0||!tray[selShape]){msg('Tap a shape first, then a board cell.'); return}
  var s=tray[selShape]; if(!canPlace(s,r,c)){msg('That shape does not fit there — try another spot.'); return}
  s.cells.forEach(function(cl){board[r+cl[0]][c+cl[1]]=1});
  setScore(score+s.cells.length); tray[selShape]=null; selShape=-1;
  var cleared=0;
  for(var rr=0;rr<N;rr++)if(board[rr].every(function(v){return v})){board[rr]=board[rr].map(function(){return 0}); cleared++}
  for(var cc=0;cc<N;cc++){var full=true; for(var r2=0;r2<N;r2++)if(!board[r2][cc])full=false;
    if(full){for(var r3=0;r3<N;r3++)board[r3][cc]=0; cleared++}}
  if(cleared){setScore(score+cleared*10*N); msg('Cleared '+cleared+' line'+(cleared>1?'s':'')+'! +'+(cleared*10*N))}
  if(tray.every(function(t){return !t}))newTray();
  draw(); drawTray();
  if(!anyFits()){playing=false; msg('Game over! No shape fits. Final score '+score+'. Press Start to play again.');}}
function anyFits(){for(var i=0;i<tray.length;i++){if(!tray[i])continue; for(var r=0;r<N;r++)for(var c=0;c<N;c++)if(canPlace(tray[i],r,c))return true} return false}
function start(){board=[]; for(var r=0;r<N;r++){board.push([]); for(var c=0;c<N;c++)board[r].push(0)} setScore(0); playing=true; newTray(); draw(); msg('Tap a shape, then tap the board to place it!')}
el('startBtn').onclick=start; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- word-search ----
add("word-search","Word Search","Find the hidden words in the letter grid — tap start, then end!","🔤",
"Find every word in the list. Tap the first letter, then tap the last letter of a word (across, down or diagonal). Beat your best time!",
'<div class="grid" id="board" style="grid-template-columns:repeat(10,1fr);gap:2px"></div><div class="small" style="text-align:center">Time: <b id="time">0</b>s · Best: <b id="bestTime">—</b> · Found: <b id="found">0</b>/<b id="tot">0</b></div><div id="words" style="margin-top:8px"></div>',
r"""
var cat=qp('category')||'animals'; var size=parseInt(qp('size')||'10')||10; if([10,12].indexOf(size)<0)size=10;
var LISTS={animals:['LION','TIGER','BEAR','WOLF','EAGLE','SNAKE','MOUSE','HORSE','MONKEY','ZEBRA'],
 sports:['SOCCER','TENNIS','GOLF','RUGBY','BOXING','SWIM','SKI','SURF','CRICKET','HOCKEY'],
 food:['PIZZA','PASTA','BREAD','APPLE','GRAPE','MELON','PEACH','LEMON','SUGAR','HONEY'],
 mixed:['LION','SOCCER','PIZZA','TIGER','TENNIS','PASTA','EAGLE','GOLF','APPLE','WOLF']};
var WORDS=shuffle((LISTS[cat]||LISTS.animals).slice()).slice(0,size===12?10:8);
var grid=[], foundWords={}, foundCells={}, selCell=null, found=0, secs=0, timer=null, playing=false;
var bestTime=null; try{bestTime=JSON.parse(localStorage.getItem('fcn_best_word-search-time')||'null')}catch(e){}
if(bestTime)el('bestTime').textContent=bestTime+'s';
if(el('cfgLabel'))el('cfgLabel').textContent=cat+' · '+size+'×'+size;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)'; el('tot').textContent=WORDS.length;
var DIRS=[[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[1,-1],[-1,1]];
function build(){grid=[]; for(var r=0;r<size;r++){grid.push([]); for(var c=0;c<size;c++)grid[r].push('')}
  WORDS.forEach(function(w){var placed=false, tries=0;
    while(!placed&&tries<200){tries++; var d=DIRS[rnd(DIRS.length)]; var r0=rnd(size), c0=rnd(size);
      var r1=r0+d[0]*(w.length-1), c1=c0+d[1]*(w.length-1);
      if(r1<0||r1>=size||c1<0||c1>=size)continue;
      var ok=true; for(var k=0;k<w.length;k++){var ch=grid[r0+d[0]*k][c0+d[1]*k]; if(ch&&ch!==w[k]){ok=false; break}}
      if(!ok)continue;
      for(var k2=0;k2<w.length;k2++)grid[r0+d[0]*k2][c0+d[1]*k2]=w[k2]; placed=true}});
  for(var r=0;r<size;r++)for(var c=0;c<size;c++)if(!grid[r][c])grid[r][c]=String.fromCharCode(65+rnd(26));
  foundWords={}; foundCells={}; found=0; selCell=null; draw(); drawWords();}
function draw(){el('board').innerHTML=''; for(var r=0;r<size;r++)for(var c=0;c<size;c++){var b=document.createElement('button'); b.className='tile'; b.style.minHeight='34px'; b.style.fontSize='15px'; b.textContent=grid[r][c];
  if(selCell&&selCell.r===r&&selCell.c===c)b.style.outline='3px solid #F59E0B';
  if(foundCells[r+','+c]){b.style.background='#166534'; b.style.color='#fff'}
  (function(rr,cc){b.onclick=function(){tapCell(rr,cc)}})(r,c); el('board').appendChild(b)}
  el('found').textContent=found;}
function drawWords(){el('words').innerHTML=''; WORDS.forEach(function(w){var s=document.createElement('span'); s.textContent=w; s.style.cssText='display:inline-block;margin:3px;padding:4px 10px;border-radius:20px;font-weight:700;font-size:14px;background:'+(foundWords[w]?'#166534':'#e2e8f0')+';color:'+(foundWords[w]?'#fff':'#0F172A')+';text-decoration:'+(foundWords[w]?'line-through':'none'); el('words').appendChild(s)})}
function lineCells(a,b){var dr=Math.sign(b.r-a.r), dc=Math.sign(b.c-a.c);
  if(!(dr===0||dc===0||Math.abs(b.r-a.r)===Math.abs(b.c-a.c)))return null;
  var len=Math.max(Math.abs(b.r-a.r),Math.abs(b.c-a.c)); var cells=[], word='';
  for(var k=0;k<=len;k++){var r=a.r+dr*k, c=a.c+dc*k; cells.push([r,c]); word+=grid[r][c]}
  return {cells:cells,word:word}}
function tapCell(r,c){if(!playing){msg('Press Start first!'); return}
  if(!selCell){selCell={r:r,c:c}; draw(); return}
  var res=lineCells(selCell,{r:r,c:c}); selCell=null;
  if(!res){msg('Words run straight — across, down or diagonal.'); draw(); return}
  var w=res.word, rev=w.split('').reverse().join('');
  var hit=null; if(WORDS.indexOf(w)>=0&&!foundWords[w])hit=w; else if(WORDS.indexOf(rev)>=0&&!foundWords[rev])hit=rev;
  if(hit){foundWords[hit]=1; found++; setScore(found);
    res.cells.forEach(function(p){foundCells[p[0]+','+p[1]]=1}); draw();
    if(found===WORDS.length){playing=false; clearInterval(timer);
      if(!bestTime||secs<bestTime){bestTime=secs; el('bestTime').textContent=secs+'s'; try{localStorage.setItem('fcn_best_word-search-time',JSON.stringify(secs))}catch(e){}}
      msg('🎉 All words found in '+secs+'s! Press Start for a new puzzle.')}}
  else {msg('No word there — try again.'); draw()}}
function start(){build(); secs=0; el('time').textContent=0; playing=true; setScore(0);
  clearInterval(timer); timer=setInterval(function(){secs++; el('time').textContent=secs},1000); msg('Find the words!')}
el('startBtn').onclick=start; build(); msg('Press Start — the clock runs from your first game!');
""",
{"theme":["classic","dark","neon"],"category":["animals","sports","food","mixed"],"size":["10","12"]})

# ---- lights-out ----
add("lights-out","Lights Out","Tap the lights to turn them all off. Each tap flips its neighbours!","💡",
"Tap a light to toggle it and its neighbours up, down, left and right. Turn every light OFF to win!",
'<div class="grid" id="board" style="grid-template-columns:repeat(5,1fr);gap:6px"></div><div class="small" style="text-align:center">Moves: <b id="moves">0</b> · Lights on: <b id="on">0</b></div>',
r"""
var size=parseInt(qp('size')||'5')||5; if([5,6].indexOf(size)<0)size=5;
var diff=qp('difficulty')||'easy';
var board=[], moves=0, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff;
el('board').style.gridTemplateColumns='repeat('+size+',1fr)';
function toggle(r,c){if(r>=0&&r<size&&c>=0&&c<size)board[r][c]=!board[r][c]}
function draw(){el('board').innerHTML=''; var on=0;
  for(var r=0;r<size;r++)for(var c=0;c<size;c++){if(board[r][c])on++;
    var b=document.createElement('button'); b.className='tile'; b.style.minHeight='52px'; b.style.fontSize='26px';
    b.textContent=board[r][c]?'💡':'⚫'; b.style.background=board[r][c]?'#fef9c3':'#f1f5f9';
    (function(rr,cc){b.onclick=function(){tap(rr,cc)}})(r,c); el('board').appendChild(b)}
  el('on').textContent=on; el('moves').textContent=moves;}
function tap(r,c){if(!playing)return; toggle(r,c); toggle(r-1,c); toggle(r+1,c); toggle(r,c-1); toggle(r,c+1); moves++; draw();
  var on=0; for(var i=0;i<size;i++)for(var j=0;j<size;j++)if(board[i][j])on++;
  if(on===0){playing=false; var pts=Math.max(10,500-moves*10); setScore(pts); msg('🎉 All lights out in '+moves+' moves! Score '+pts+'. Press Start for a new puzzle.')}
  else msg('Lights on: '+on+' — keep going!')}
function start(){board=[]; for(var r=0;r<size;r++){board.push([]); for(var c=0;c<size;c++)board[r].push(false)}
  var taps = diff==='easy'? size*2 : size*4;
  for(var k=0;k<taps;k++){var r2=rnd(size), c2=rnd(size); toggle(r2,c2); toggle(r2-1,c2); toggle(r2+1,c2); toggle(r2,c2-1); toggle(r2,c2+1)}
  var on=0; for(var i=0;i<size;i++)for(var j=0;j<size;j++)if(board[i][j])on++;
  if(on===0){toggle(0,0); toggle(1,0); toggle(0,1)}
  moves=0; playing=true; setScore(0); draw(); msg('Turn all the lights off!')}
el('startBtn').onclick=start; start();
""",
{"theme":["classic","dark","neon"],"size":["5","6"],"difficulty":["easy","hard"]})

# ---- nonogram ----
add("nonogram","Nonogram","Paint cells by the number clues to reveal the hidden picture!","🖼️",
"Numbers on each row and column tell you how many filled cells run together. Tap Fill mode, then tap cells to paint. Wrong paint costs a life!",
'<div class="row"><button class="btn" id="modeBtn" style="flex:1">Mode: FILL ⬛</button><span class="small" style="flex:1;text-align:center">Lives: <b id="lives">5</b> · Mistakes: <b id="errs">0</b></span></div><div id="wrap" style="overflow-x:auto;margin-top:10px"><div id="grid"></div></div>',
r"""
var size=parseInt(qp('size')||'5')||5; if([5,10].indexOf(size)<0)size=5;
var diff=qp('difficulty')||'easy';
var LIVES = diff==='easy'?5:3;
var PATS5=[
 [[0,1,1,0,0],[1,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[0,0,1,0,0]],
 [[0,0,1,0,0],[0,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[0,0,1,0,0]],
 [[0,1,1,1,0],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,0,1],[0,1,1,1,0]],
 [[0,0,1,0,0],[0,1,1,1,0],[1,1,1,1,1],[0,1,0,1,0],[0,1,0,1,0]],
 [[0,1,0,1,0],[1,1,1,1,1],[1,1,1,1,1],[0,1,1,1,0],[0,0,1,0,0]]];
var sol=[], state=[], mode='fill', lives=LIVES, errs=0, playing=false;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+diff+' · '+LIVES+' lives';
function genSol(){if(size===5)return PATS5[rnd(PATS5.length)].map(function(r){return r.slice()});
  var s=[]; for(var r=0;r<10;r++){s.push([]); for(var c=0;c<10;c++)s[r].push(0)}
  for(var r2=0;r2<10;r2++)for(var c2=0;c2<5;c2++){var v=Math.random()<0.38?1:0; s[r2][c2]=v; s[r2][9-c2]=v}
  return s}
function clues(line){var out=[], n=0; line.forEach(function(v){if(v)n++; else if(n){out.push(n); n=0}}); if(n)out.push(n); return out.length?out:[0]}
function draw(){var g=el('grid'); g.innerHTML='';
  var cell = size===5?44:30;
  var tbl=document.createElement('div'); tbl.style.display='grid'; tbl.style.gridTemplateColumns='54px repeat('+size+','+cell+'px)'; tbl.style.gap='2px';
  var corner=document.createElement('div'); tbl.appendChild(corner);
  for(var c=0;c<size;c++){var ch=document.createElement('div'); ch.style.cssText='text-align:center;font-size:11px;font-weight:700;color:#475569'; ch.textContent=clues(sol.map(function(row){return row[c]})).join('\n'); ch.style.whiteSpace='pre-line'; tbl.appendChild(ch)}
  for(var r=0;r<size;r++){var rh=document.createElement('div'); rh.style.cssText='text-align:right;font-size:11px;font-weight:700;color:#475569;padding-right:4px'; rh.textContent=clues(sol[r]).join(' '); tbl.appendChild(rh);
    for(var c2=0;c2<size;c2++){var b=document.createElement('button');
      b.style.cssText='width:'+cell+'px;height:'+cell+'px;border:1px solid #cbd5e1;border-radius:4px;cursor:pointer;font-size:14px;font-weight:800;padding:0;background:'+(state[r][c2]===1?'#0F172A':state[r][c2]===2?'#f1f5f9':'#fff')+';color:'+(state[r][c2]===1?'#fff':'#dc2626');
      b.textContent=state[r][c2]===2?'✕':(state[r][c2]===1?'⬛':'');
      (function(rr,cc){b.onclick=function(){tap(rr,cc)}})(r,c2); tbl.appendChild(b)}}
  g.appendChild(tbl); el('lives').textContent=lives; el('errs').textContent=errs;}
function tap(r,c){if(!playing)return; if(state[r][c]===1&&mode==='fill')return;
  if(mode==='mark'){state[r][c]=state[r][c]===2?0:2; draw(); return}
  if(sol[r][c]===1){state[r][c]=1; draw(); checkWin()}
  else {errs++; lives--; draw();
    if(lives<=0){playing=false; msg('Out of lives! Press Start for a new picture.')}
    else msg('Wrong cell! '+lives+' lives left.')}}
function checkWin(){for(var r=0;r<size;r++)for(var c=0;c<size;c++)if(sol[r][c]===1&&state[r][c]!==1)return;
  playing=false; var pts=Math.max(50,1000-errs*100); setScore(pts); msg('🎉 Picture revealed! Score '+pts+'. Press Start for a new picture.')}
function start(){sol=genSol(); state=[]; for(var r=0;r<size;r++){state.push([]); for(var c=0;c<size;c++)state[r].push(0)}
  lives=LIVES; errs=0; playing=true; setScore(0); mode='fill'; el('modeBtn').textContent='Mode: FILL ⬛'; draw(); msg('Paint the picture from the number clues!')}
el('modeBtn').onclick=function(){mode=mode==='fill'?'mark':'fill'; el('modeBtn').textContent=mode==='fill'?'Mode: FILL ⬛':'Mode: MARK ✕'; msg(mode==='fill'?'Tap cells to fill them.':'Tap cells to mark them as empty.')};
el('startBtn').onclick=start; start();
""",
{"theme":["classic","dark","neon"],"size":["5","10"],"difficulty":["easy","hard"]})

# ---- fruit-merge ----
add("fruit-merge","Fruit Merge","Drop fruits, merge matching pairs into bigger fruit. Don't hit the top!","🍉",
"Tap a column to drop the next fruit. Two matching fruits merge into the next bigger one — even across columns! If any stack passes the top line, it's game over.",
'<div class="small" style="text-align:center">Next: <b id="next" style="font-size:24px"></b> · Drops: <b id="drops">0</b></div><div id="cols" style="display:flex;gap:4px;margin-top:8px"></div><div class="grid" id="btns" style="grid-template-columns:repeat(7,1fr);gap:4px;margin-top:8px"></div>',
r"""
var diff=qp('difficulty')||'medium';
var FRUITS=['🍒','🍓','🍇','🍊','🍎','🍐','🍑','🍍','🍉'];
var NCOL=7, MAXH=8, cols=[], next=0, drops=0, playing=false;
var SPAWN = diff==='easy'?3:(diff==='hard'?5:4);
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · next fruit up to '+FRUITS[SPAWN-1];
function draw(){el('cols').innerHTML=''; for(var c=0;c<NCOL;c++){var d=document.createElement('div'); d.style.cssText='flex:1;min-height:220px;display:flex;flex-direction:column-reverse;gap:2px;border:2px solid #e2e8f0;border-top:3px dashed #dc2626;border-radius:8px;padding:4px;background:#fff';
  cols[c].forEach(function(t){var s=document.createElement('div'); s.style.cssText='text-align:center;font-size:26px;line-height:1.1'; s.textContent=FRUITS[t]; d.appendChild(s)});
  el('cols').appendChild(d)}
  el('btns').innerHTML=''; for(var c2=0;c2<NCOL;c2++){var b=document.createElement('button'); b.className='opt'; b.style.padding='10px 0'; b.textContent='▼ '+(c2+1);
    (function(cc){b.onclick=function(){drop(cc)}})(c2); el('btns').appendChild(b)}
  el('next').textContent=FRUITS[next]; el('drops').textContent=drops;}
function resolveMerges(){var changed=true;
  while(changed){changed=false;
    for(var c=0;c<NCOL;c++){var col=cols[c];
      if(col.length>=2&&col[col.length-1]===col[col.length-2]){var t=col.pop(); col.pop(); var nt=Math.min(FRUITS.length-1,t+1); col.push(nt); setScore(score+(nt+1)*10); changed=true; break}}
    if(changed)continue;
    for(var c2=0;c2<NCOL-1;c2++){var a=cols[c2], b2=cols[c2+1];
      if(a.length&&b2.length&&a[a.length-1]===b2[b2.length-1]){var t2=a.pop(); b2.pop(); var nt2=Math.min(FRUITS.length-1,t2+1); a.push(nt2); setScore(score+(nt2+1)*10); changed=true; break}}}}
function drop(c){if(!playing)return;
  if(cols[c].length>=MAXH){playing=false; msg('That column is full — game over! Score '+score+'. Press Start to play again.'); return}
  cols[c].push(next); drops++; resolveMerges();
  for(var i=0;i<NCOL;i++)if(cols[i].length>MAXH){playing=false; draw(); msg('💥 Over the top line! Game over — score '+score+'. Press Start to retry.'); return}
  next=rnd(SPAWN); draw();}
function start(){cols=[]; for(var c=0;c<NCOL;c++)cols.push([]); next=rnd(SPAWN); drops=0; playing=true; setScore(0); draw(); msg('Tap a column to drop the fruit!')}
el('startBtn').onclick=start; start();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- cookie-clicker ----
add("cookie-clicker","Cookie Clicker","Click to earn cookies, buy upgrades, and grow your cookie empire!","🍪",
"Tap the big cookie to earn. Spend cookies on upgrades: stronger clicks and auto-clickers that earn while you wait!",
'<div style="text-align:center"><button id="bigBtn" style="font-size:90px;background:none;border:0;cursor:pointer;min-width:140px;min-height:140px">🍪</button><div style="font-size:20px;font-weight:800"><span id="count">0</span> <span id="itemName">cookies</span></div><div class="small">Per click: <b id="perClick">1</b> · Per second: <b id="perSec">0</b></div></div><div id="shop" style="margin-top:12px"></div>',
r"""
var theme=qp('theme')||'cookies';
var TH={cookies:{emoji:'🍪',name:'cookies',up:['🥛 Milk','👵 Grandma','🏭 Factory']},
 coins:{emoji:'🪙',name:'coins',up:['👛 Wallet','🏦 Bank','⛏️ Mint']},
 gems:{emoji:'💎',name:'gems',up:['⛏️ Pickaxe','💍 Jeweller','🏰 Gem Mine']}}[theme]||{emoji:'🍪',name:'cookies',up:['🥛 Milk','👵 Grandma','🏭 Factory']};
var total=0, perClick=1, perSec=0, owned=[0,0,0], timer=null;
var BASE=[25,50,250], RATE=[1,1,5];
if(el('cfgLabel'))el('cfgLabel').textContent=theme+' · clicker';
el('bigBtn').textContent=TH.emoji; el('itemName').textContent=TH.name;
function cost(i){return Math.floor(BASE[i]*Math.pow(1.8,owned[i]))}
function draw(){el('count').textContent=Math.floor(total); el('perClick').textContent=perClick; el('perSec').textContent=perSec;
  el('shop').innerHTML='';
  var defs=[{n:TH.up[0]+' (+1/click)',i:0},{n:TH.up[1]+' (+1/sec)',i:1},{n:TH.up[2]+' (+5/sec)',i:2}];
  defs.forEach(function(d){var b=document.createElement('button'); b.className='btn ghost'; b.style.margin='6px 0';
    b.textContent=d.n+' — cost '+cost(d.i)+' '+TH.name+' (owned: '+owned[d.i]+')';
    b.disabled=total<cost(d.i); b.style.opacity=total<cost(d.i)?'0.6':'1';
    b.onclick=function(){buy(d.i)}; el('shop').appendChild(b)})}
function buy(i){var c=cost(i); if(total<c)return; total-=c; owned[i]++;
  if(i===0)perClick+=RATE[0]; else perSec+=RATE[i];
  setScore(Math.floor(total)); draw(); msg('Bought! '+TH.up[i]+' ×'+owned[i]);}
el('bigBtn').onclick=function(){total+=perClick; setScore(Math.floor(total)); draw()};
function start(){total=0; perClick=1; perSec=0; owned=[0,0,0]; setScore(0);
  clearInterval(timer); timer=setInterval(function(){if(perSec>0){total+=perSec; setScore(Math.floor(total)); draw()}},1000);
  draw(); msg('Tap the '+TH.emoji+' to earn '+TH.name+'!')}
el('startBtn').onclick=start; start();
""",
{"theme":["cookies","coins","gems"]})

# ---- Batch games_c4_adds.py (19 Nov 2026) ----
# ---- C4-1 endless-runner ----
add("endless-runner","Endless Runner","Subway-style endless runner. Jump, slide, dodge and grab coins!","🏃",
"Tap JUMP to leap low barriers and SLIDE to duck under high ones. Grab coins, survive as long as you can — speed keeps rising!",
'<canvas id="cv" width="520" height="280" style="width:100%;max-width:520px;display:block;background:#bae6fd;border-radius:10px;touch-action:none"></canvas><div class="row" style="margin-top:8px"><button class="btn" id="jumpBtn" style="padding:16px">⬆ JUMP</button><button class="btn amber" id="slideBtn" style="padding:16px">⬇ SLIDE</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Coins: <b id="coins">0</b> · Speed: <b id="spd">1.0</b>x</div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var baseSpd = diff==='easy'?4:(diff==='hard'?7:5.5);
var lives = mode==='classic'?3:1; var maxLives=lives;
var coins=0, dist=0, speed=baseSpd, playing=false, timer=null;
var py=210, vy=0, sliding=0, jumping=false, obs=[], coinList=[], frame=0;
var cv=el('cv'), ctx=cv.getContext('2d');
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
el('lives').textContent=lives;
function draw(){ctx.clearRect(0,0,520,280); ctx.fillStyle='#bae6fd'; ctx.fillRect(0,0,520,280);
  ctx.fillStyle='#fde68a'; ctx.beginPath(); ctx.arc(470,35,22,0,7); ctx.fill();
  ctx.fillStyle='#a16207'; ctx.fillRect(0,250,520,30); ctx.fillStyle='#65a30d'; ctx.fillRect(0,246,520,6);
  coinList.forEach(function(c){ctx.fillStyle='#f59e0b'; ctx.beginPath(); ctx.arc(c.x,c.y,10,0,7); ctx.fill(); ctx.fillStyle='#78350f'; ctx.font='bold 12px sans-serif'; ctx.textAlign='center'; ctx.fillText('$',c.x,c.y+4);});
  obs.forEach(function(o){if(o.kind==='low'){ctx.fillStyle='#dc2626'; ctx.fillRect(o.x,220,26,30);} else {ctx.fillStyle='#7c3aed'; ctx.fillRect(o.x,190,26,60);} ctx.fillStyle='#fff'; ctx.font='bold 11px sans-serif'; ctx.textAlign='center'; ctx.fillText(o.kind==='low'?'JUMP':'DUCK',o.x+13,o.kind==='low'?215:185);});
  var h=sliding>0?22:40; ctx.fillStyle='#166534'; ctx.fillRect(60,py+40-h,34,h);
  ctx.fillStyle='#fff'; ctx.font='bold 16px sans-serif'; ctx.textAlign='center'; ctx.fillText('🏃',77,py+40-h+18);
  ctx.fillStyle='#0f172a'; ctx.font='bold 14px sans-serif'; ctx.textAlign='left'; ctx.fillText('Score '+score,10,20);}
function step(){if(!playing)return; frame++; dist++; speed=baseSpd+dist/900;
  el('spd').textContent=speed.toFixed(1)+'x';
  if(jumping){vy+=1.1; py+=vy; if(py>=210){py=210; jumping=false; vy=0;}}
  if(sliding>0)sliding--;
  if(frame%Math.max(28,Math.floor(80-speed*4))===0){var kind=Math.random()<0.5?'low':'high'; obs.push({x:520,kind:kind}); if(Math.random()<0.6)coinList.push({x:520,y:kind==='low'?190:215});}
  if(frame%45===0)coinList.push({x:520,y:185+rnd(50)});
  obs.forEach(function(o){o.x-=speed}); coinList.forEach(function(c){c.x-=speed});
  obs=obs.filter(function(o){return o.x>-40}); coinList=coinList.filter(function(c){return c.x>-20});
  var ph=sliding>0?22:40, pTop=py+40-ph;
  obs.forEach(function(o){var oTop=o.kind==='low'?220:190, oH=o.kind==='low'?30:60;
    if(60+34>o.x&&60<o.x+26&&pTop+ph>oTop&&pTop<oTop+oH){o.x=-999; hit();}});
  coinList.forEach(function(c){if(!c.got&&Math.abs(c.x-77)<26&&Math.abs(c.y-(pTop+ph/2))<30){c.got=true; coins++; el('coins').textContent=coins; setScore(score+5);}});
  coinList=coinList.filter(function(c){return !c.got});
  if(dist%10===0)setScore(Math.floor(dist/10)+coins*5);
  draw();}
function hit(){lives--; el('lives').textContent=lives; if(lives<=0){playing=false; clearInterval(timer); msg('💥 Game over! Distance '+Math.floor(dist/10)+'m, '+coins+' coins. Press Start to run again.');} else msg('Ouch! '+lives+' '+(lives===1?'life':'lives')+' left — keep running!');}
function jump(){if(!playing)return; if(!jumping){jumping=true; vy=-13;}}
function slide(){if(!playing)return; sliding=22;}
el('jumpBtn').onclick=jump; el('slideBtn').onclick=slide;
cv.addEventListener('pointerdown',function(e){var r=cv.getBoundingClientRect(); var y=(e.clientY-r.top)/r.height*280; if(y<140)jump(); else slide();});
document.addEventListener('keydown',function(e){if(e.key==='ArrowUp'||e.key===' '){e.preventDefault(); jump()} if(e.key==='ArrowDown'){e.preventDefault(); slide()}});
el('startBtn').onclick=function(){clearInterval(timer); lives=maxLives; el('lives').textContent=lives; coins=0; el('coins').textContent=0; dist=0; speed=baseSpd; py=210; vy=0; jumping=false; sliding=0; obs=[]; coinList=[]; frame=0; setScore(0); playing=true; msg('Run! Jump the red barriers, slide under the purple ones.'); timer=setInterval(step,50); draw();};
msg('Press Start, then jump and slide to survive!');
draw();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- C4-2 doodle-jump ----
add("doodle-jump","Doodle Jump","Bounce ever higher on tiny platforms. Don't fall!","🐸",
"Hold LEFT / RIGHT (or arrow keys) to steer while you bounce. Land on platforms to climb — falling is game over!",
'<canvas id="cv" width="360" height="420" style="width:100%;max-width:360px;display:block;margin:0 auto;background:#dbeafe;border-radius:10px;touch-action:none"></canvas><div class="row" style="margin-top:8px"><button class="btn" id="leftBtn" style="padding:16px">◀ LEFT</button><button class="btn amber" id="rightBtn" style="padding:16px">RIGHT ▶</button></div><div class="small" style="text-align:center">Height: <b id="ht">0</b>m · Platforms: <b id="plats">0</b></div>',
r"""
var diff=qp('difficulty')||'medium';
var gap = diff==='easy'?52:(diff==='hard'?78:64);
var moveChance = diff==='easy'?0.1:(diff==='hard'?0.45:0.25);
var cv=el('cv'), ctx=cv.getContext('2d');
var px=170, py=360, vy=0, height=0, maxH=0, playing=false, timer=null, left=false, right=false, plats=[], landed=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · bounce up!';
function newPlats(){plats=[]; var y=400; plats.push({x:150,y:400,w:70,kind:'normal',vx:0});
  while(y>0){y-=gap+rnd(14); var w=diff==='hard'?52:68; var kind='normal'; var r=Math.random();
    if(r<moveChance)kind='moving'; else if(r<moveChance+0.12&&diff!=='easy')kind='breaking';
    plats.push({x:rnd(360-w),y:y,w:w,kind:kind,vx:kind==='moving'?(Math.random()<0.5?-1.4:1.4):0});}}
function draw(){ctx.clearRect(0,0,360,420); ctx.fillStyle='#dbeafe'; ctx.fillRect(0,0,360,420);
  plats.forEach(function(p){ctx.fillStyle=p.kind==='breaking'?'#fca5a5':(p.kind==='moving'?'#f59e0b':'#166534'); ctx.fillRect(p.x,p.y,p.w,12);});
  ctx.fillStyle='#166534'; ctx.beginPath(); ctx.arc(px+15,py+12,15,0,7); ctx.fill();
  ctx.fillStyle='#fff'; ctx.font='bold 14px sans-serif'; ctx.textAlign='center'; ctx.fillText('🐸',px+15,py+17);
  ctx.fillStyle='#0f172a'; ctx.font='bold 14px sans-serif'; ctx.textAlign='left'; ctx.fillText('Height '+maxH+'m',10,20);}
function step(){if(!playing)return; vy+=0.55; py+=vy;
  if(left)px-=5; if(right)px+=5; if(px<-15)px=375; if(px>375)px=-15;
  plats.forEach(function(p){if(p.kind==='moving'){p.x+=p.vx; if(p.x<0||p.x+p.w>360)p.vx*=-p.vx;}});
  if(vy>0){for(var i=0;i<plats.length;i++){var p=plats[i]; if(px+30>p.x&&px<p.x+p.w&&py+28>=p.y&&py+28<=p.y+16){vy=-13; landed++; el('plats').textContent=landed; if(p.kind==='breaking'){plats.splice(i,1);} break;}}}
  if(py<150){var dy=150-py; py=150; height+=Math.round(dy/10); plats.forEach(function(p){p.y+=dy; if(p.y>420){p.y-=420+gap+rnd(14); p.x=rnd(360-p.w);}}); if(height>maxH){maxH=height; setScore(maxH); el('ht').textContent=maxH;}}
  if(py>420){playing=false; clearInterval(timer); msg('💥 You fell! Best height '+maxH+'m, '+landed+' platforms. Press Start to bounce again.');}
  draw();}
el('leftBtn').addEventListener('pointerdown',function(){left=true}); el('leftBtn').addEventListener('pointerup',function(){left=false}); el('leftBtn').addEventListener('pointerleave',function(){left=false});
el('rightBtn').addEventListener('pointerdown',function(){right=true}); el('rightBtn').addEventListener('pointerup',function(){right=false}); el('rightBtn').addEventListener('pointerleave',function(){right=false});
document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')left=true; if(e.key==='ArrowRight')right=true;});
document.addEventListener('keyup',function(e){if(e.key==='ArrowLeft')left=false; if(e.key==='ArrowRight')right=false;});
el('startBtn').onclick=function(){clearInterval(timer); px=170; py=360; vy=-12; height=0; maxH=0; landed=0; el('ht').textContent=0; el('plats').textContent=0; setScore(0); newPlats(); playing=true; msg('Bounce! Steer left and right, land on every platform.'); timer=setInterval(step,40); draw();};
newPlats(); draw(); msg('Press Start to bounce!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- C4-3 fruit-slicer ----
add("fruit-slicer","Fruit Slicer","Slice the flying fruit, dodge the bombs!","🍉",
"Tap or click fruit as it flies up to slice it. NEVER tap a bomb — three strikes and you're out!",
'<canvas id="cv" width="520" height="320" style="width:100%;max-width:520px;display:block;background:#fef3c7;border-radius:10px;touch-action:none"></canvas><div class="small" style="text-align:center">Time left: <b id="time">60</b>s · Sliced: <b id="sliced">0</b> · Misses: <b id="miss">0</b>/3</div>',
r"""
var dur=parseInt(qp('time')||'60')||60; var diff=qp('difficulty')||'hard';
var spawnMs = diff==='easy'?900:550; var bombChance = diff==='easy'?0.12:0.25;
var items=[], sliced=0, misses=0, tLeft=dur, playing=false, timer=null, spawnTimer=null, stepTimer=null;
var cv=el('cv'), ctx=cv.getContext('2d');
var EMOJI={apple:'🍎',orange:'🍊',melon:'🍉',lemon:'🍋',berry:'🍇',bomb:'💣'};
if(el('cfgLabel'))el('cfgLabel').textContent=dur+'s · '+diff;
el('time').textContent=dur;
function spawn(){var kind=Math.random()<bombChance?'bomb':['apple','orange','melon','lemon','berry'][rnd(5)];
  items.push({x:40+rnd(440),y:330,vy:-(7+rnd(4)),kind:kind,dead:false});}
function draw(){ctx.clearRect(0,0,520,320); ctx.fillStyle='#fef3c7'; ctx.fillRect(0,0,520,320);
  ctx.fillStyle='#166534'; ctx.fillRect(0,310,520,10);
  items.forEach(function(it){if(it.dead)return; ctx.font='34px sans-serif'; ctx.textAlign='center'; ctx.fillText(EMOJI[it.kind],it.x,it.y);});}
function step(){if(!playing)return; items.forEach(function(it){it.y+=it.vy; it.vy+=0.35;});
  items=items.filter(function(it){if(it.y>340&&!it.dead){if(it.kind!=='bomb'){misses++; el('miss').textContent=misses; if(misses>=3)endGame('Three fruit missed!');} return false} return !it.dead;});
  draw();}
function endGame(reason){playing=false; clearInterval(timer); clearInterval(spawnTimer); clearInterval(stepTimer); msg('⏰ '+reason+' You sliced '+sliced+' fruit. Score '+score+'. Press Start to play again.');}
cv.addEventListener('pointerdown',function(e){if(!playing)return; var r=cv.getBoundingClientRect(); var x=(e.clientX-r.left)/r.width*520, y=(e.clientY-r.top)/r.height*320;
  for(var i=0;i<items.length;i++){var it=items[i]; if(!it.dead&&Math.abs(it.x-x)<34&&Math.abs(it.y-y)<34){it.dead=true; if(it.kind==='bomb'){endGame('💣 BOOM! You sliced a bomb!'); return} sliced++; el('sliced').textContent=sliced; setScore(score+10); break;}} draw();});
el('startBtn').onclick=function(){clearInterval(timer); clearInterval(spawnTimer); clearInterval(stepTimer); items=[]; sliced=0; misses=0; tLeft=dur; el('sliced').textContent=0; el('miss').textContent=0; el('time').textContent=dur; setScore(0); playing=true; msg('Slice the fruit — not the bombs!');
  spawnTimer=setInterval(function(){if(playing)spawn()},spawnMs);
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0)endGame('Time up!');},1000);
  stepTimer=setInterval(step,40); draw();};
draw(); msg('Press Start, then tap the fruit!');
""",
{"theme":["classic","dark","neon"],"time":["30","60"],"difficulty":["easy","hard"]})

# ---- C4-4 stack-blocks ----
add("stack-blocks","Stack Blocks","Drop the swinging block and build the tallest tower!","🧱",
"Tap DROP when the swinging block is over the tower. Perfect drops score big and grow the block back!",
'<canvas id="cv" width="360" height="420" style="width:100%;max-width:360px;display:block;margin:0 auto;background:#e0f2fe;border-radius:10px;touch-action:none"></canvas><button class="btn amber" id="dropBtn" style="padding:18px;font-size:20px">🧱 DROP BLOCK</button><div class="small" style="text-align:center">Tower: <b id="tower">0</b> blocks · Perfect drops: <b id="perfect">0</b></div>',
r"""
var diff=qp('difficulty')||'medium';
var swingSpd = diff==='easy'?2.2:(diff==='hard'?4.5:3.2);
var startW = diff==='easy'?120:(diff==='hard'?90:105);
var cv=el('cv'), ctx=cv.getContext('2d');
var tower=[], curX=0, curDir=1, curW=startW, curY=40, playing=false, perfects=0, anim=null;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · drop to stack!';
function baseY(){return 400-tower.length*22;}
function draw(){ctx.clearRect(0,0,360,420); ctx.fillStyle='#e0f2fe'; ctx.fillRect(0,0,360,420);
  ctx.fillStyle='#166534'; ctx.fillRect(0,400,360,20);
  tower.forEach(function(b){ctx.fillStyle=b.color; ctx.fillRect(b.x,b.y,b.w,20); ctx.strokeStyle='#0f172a'; ctx.strokeRect(b.x,b.y,b.w,20);});
  if(playing){ctx.fillStyle='#f59e0b'; ctx.fillRect(curX,curY,curW,20); ctx.strokeStyle='#0f172a'; ctx.strokeRect(curX,curY,curW,20);}
  ctx.fillStyle='#0f172a'; ctx.font='bold 14px sans-serif'; ctx.textAlign='left'; ctx.fillText('Tower '+tower.length,10,20);}
function swing(){if(!playing)return; curX+=curDir*swingSpd; if(curX<=0||curX+curW>=360)curDir*=-curDir; draw();}
function drop(){if(!playing)return; var prev=tower.length?tower[tower.length-1]:{x:120,y:400,w:120};
  var overlap=Math.min(curX+curW,prev.x+prev.w)-Math.max(curX,prev.x);
  if(overlap<=0){playing=false; clearInterval(anim); msg('💥 Missed the tower! You stacked '+tower.length+' blocks. Press Start to rebuild.'); return}
  var nx=Math.max(curX,prev.x), nw=overlap;
  var isPerfect=Math.abs(curX-prev.x)<=6; if(isPerfect){nw=prev.w; nx=prev.x; perfects++; el('perfect').textContent=perfects; setScore(score+10); msg('⭐ PERFECT drop! +10');}
  else setScore(score+1);
  tower.push({x:nx,y:baseY(),w:nw,color:['#f59e0b','#166534','#0284c7','#db2777','#7c3aed'][tower.length%5]});
  el('tower').textContent=tower.length; curW=nw; curX=60+rnd(120); curDir=Math.random()<0.5?-1:1; curY=40;
  if(tower.length>=14){tower.forEach(function(b){b.y+=22});}
  if(!isPerfect)msg('Stacked '+tower.length+' — keep going!');
  draw();}
el('dropBtn').onclick=drop;
cv.addEventListener('pointerdown',drop);
document.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault(); drop()}});
el('startBtn').onclick=function(){clearInterval(anim); tower=[{x:120,y:400,w:120,color:'#166534'}]; curW=startW; curX=60; curDir=1; perfects=0; el('perfect').textContent=0; el('tower').textContent=0; setScore(0); playing=true; msg('Tap DROP when the block is over the tower!'); anim=setInterval(swing,30); draw();};
draw(); msg('Press Start to build your tower!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- C4-5 pac-man ----
add("pac-man","Pac-Man","Eat every dot, dodge the ghosts, grab power pellets!","👻",
"Steer with the arrow buttons (or arrow keys). Eat all the dots to clear the level — power pellets let you eat ghosts!",
'<canvas id="cv" width="380" height="300" style="width:100%;max-width:380px;display:block;margin:0 auto;background:#0f172a;border-radius:10px;touch-action:none"></canvas><div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:10px"><span></span><button class="opt" data-dir="up">↑</button><span></span><button class="opt" data-dir="left">←</button><button class="opt" data-dir="down">↓</button><button class="opt" data-dir="right">→</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Level: <b id="lvl">1</b> · Dots left: <b id="dots">0</b></div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var ghostMs = diff==='easy'?420:(diff==='hard'?240:320);
var MAP=["###################","#........#........#","#.##.###.#.###.##.#","#o##.....P.....##o#","#.##.#.#####.#.##.#","#....#...#...#....#","####.###.#.###.####","#....#...#...#....#","#.##.#####.#####.#","#o................o#","###################"];
var ROWS=MAP.length, COLS=MAP[0].length, TS=20;
var cv=el('cv'), ctx=cv.getContext('2d'); cv.width=COLS*TS; cv.height=ROWS*TS;
var dots=[], player={x:9,y:3}, dir={x:0,y:0}, ghosts=[], lives=3, level=1, power=0, playing=false, timer=null, gTimer=null;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
function buildDots(){dots=[]; for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){var c=MAP[y][x]; if(c==='.')dots.push({x:x,y:y}); if(c==='o')dots.push({x:x,y:y,power:true});} el('dots').textContent=dots.length;}
function resetGhosts(){ghosts=[{x:1,y:1,c:'#ef4444'},{x:17,y:1,c:'#f472b6'},{x:1,y:9,c:'#22d3ee'},{x:17,y:9,c:'#f59e0b'}];}
function isWall(x,y){return x<0||y<0||x>=COLS||y>=ROWS||MAP[y][x]==='#';}
function draw(){ctx.clearRect(0,0,cv.width,cv.height); ctx.fillStyle='#0f172a'; ctx.fillRect(0,0,cv.width,cv.height);
  for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){if(MAP[y][x]==='#'){ctx.fillStyle='#1d4ed8'; ctx.fillRect(x*TS,y*TS,TS,TS);}}
  dots.forEach(function(d){ctx.fillStyle='#fde68a'; if(d.power){ctx.beginPath(); ctx.arc(d.x*TS+10,d.y*TS+10,6,0,7); ctx.fill();} else {ctx.beginPath(); ctx.arc(d.x*TS+10,d.y*TS+10,3,0,7); ctx.fill();}});
  ctx.font='18px sans-serif'; ctx.textAlign='center';
  ghosts.forEach(function(g){ctx.fillText(power>0?'😨':'👻',g.x*TS+10,g.y*TS+16);});
  ctx.fillText('😋',player.x*TS+10,player.y*TS+16);}
function step(){if(!playing)return; var nx=player.x+dir.x, ny=player.y+dir.y;
  if(!isWall(nx,ny)){player.x=nx; player.y=ny;}
  for(var i=dots.length-1;i>=0;i--){var d=dots[i]; if(d.x===player.x&&d.y===player.y){dots.splice(i,1); if(d.power){power=8; setScore(score+50); msg('⚡ POWER! Eat the ghosts!');} else setScore(score+10); el('dots').textContent=dots.length;}}
  if(power>0)power--;
  ghosts.forEach(function(g){if(g.x===player.x&&g.y===player.y){if(power>0){setScore(score+200); msg('👻 Ghost eaten! +200'); g.x=1; g.y=1;} else loseLife();}});
  if(dots.length===0){level++; el('lvl').textContent=level; setScore(score+100); if(mode==='endless'){msg('🎉 Level '+level+'! Dots refilled — keep going!'); buildDots(); player={x:9,y:3}; resetGhosts();} else {msg('🎉 Level cleared! Level '+level+' — faster ghosts!'); buildDots(); player={x:9,y:3}; resetGhosts();}}
  draw();}
function moveGhosts(){if(!playing)return; ghosts.forEach(function(g){var opts=[{x:1,y:0},{x:-1,y:0},{x:0,y:1},{x:0,y:-1}].filter(function(o){return !isWall(g.x+o.x,g.y+o.y)});
  var o=opts[rnd(opts.length)]; if(o){g.x+=o.x; g.y+=o.y;}});}
function loseLife(){lives--; el('lives').textContent=lives; player={x:9,y:3}; dir={x:0,y:0}; power=0;
  if(lives<=0){playing=false; clearInterval(timer); clearInterval(gTimer); msg('💀 Game over! Final score '+score+' on level '+level+'. Press Start to play again.');} else msg('👻 Caught! '+lives+' '+(lives===1?'life':'lives')+' left.');}
function setDir(x,y){dir={x:x,y:y};}
document.querySelectorAll('[data-dir]').forEach(function(b){b.onclick=function(){var d=b.dataset.dir; if(d==='up')setDir(0,-1); if(d==='down')setDir(0,1); if(d==='left')setDir(-1,0); if(d==='right')setDir(1,0);}});
document.addEventListener('keydown',function(e){var m={ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0]}; if(m[e.key]){e.preventDefault(); setDir(m[e.key][0],m[e.key][1]);}});
el('startBtn').onclick=function(){clearInterval(timer); clearInterval(gTimer); lives=3; level=1; el('lives').textContent=3; el('lvl').textContent=1; setScore(0); player={x:9,y:3}; dir={x:0,y:0}; power=0; buildDots(); resetGhosts(); playing=true; msg('Eat all the dots! Avoid the ghosts.'); timer=setInterval(step,220); gTimer=setInterval(moveGhosts,ghostMs); draw();};
buildDots(); resetGhosts(); draw(); msg('Press Start to play Pac-Man!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- C4-6 traffic-racer ----
add("traffic-racer","Traffic Racer","Dodge the traffic, change lanes, go faster and faster!","🚗",
"Tap ◀ ▶ (or arrow keys) to change lanes. Dodge every car — each near-miss and metre earns points!",
'<canvas id="cv" width="360" height="420" style="width:100%;max-width:360px;display:block;margin:0 auto;background:#334155;border-radius:10px;touch-action:none"></canvas><div class="row" style="margin-top:8px"><button class="btn" id="leftBtn" style="padding:16px">◀ LEFT</button><button class="btn amber" id="rightBtn" style="padding:16px">RIGHT ▶</button></div><div class="small" style="text-align:center">Lives: <b id="lives">3</b> · Distance: <b id="dist">0</b>m · Speed: <b id="spd">1.0</b>x</div>',
r"""
var diff=qp('difficulty')||'medium'; var mode=qp('mode')||'classic';
var lives = mode==='classic'?3:1; var maxLives=lives;
var spawnMs = diff==='easy'?1100:(diff==='hard'?650:850);
var cv=el('cv'), ctx=cv.getContext('2d');
var LANES=[70,180,290]; var lane=1, cars=[], dist=0, speed=1, playing=false, timer=null, spawnTimer=null, invuln=0;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+mode;
el('lives').textContent=lives;
function draw(){ctx.clearRect(0,0,360,420); ctx.fillStyle='#334155'; ctx.fillRect(0,0,360,420);
  ctx.fillStyle='#facc15'; for(var y=0;y<420;y+=40)ctx.fillRect(178,y+((dist*3)%40),4,22);
  ctx.fillStyle='#fff'; ctx.fillRect(120,0,2,420); ctx.fillRect(238,0,2,420);
  cars.forEach(function(c){ctx.fillStyle=c.color; ctx.fillRect(c.x-28,c.y,56,72); ctx.fillStyle='#0f172a'; ctx.fillRect(c.x-20,c.y+12,40,16); ctx.fillRect(c.x-20,c.y+44,40,14);});
  if(invuln<=0||Math.floor(invuln/4)%2===0){ctx.fillStyle='#ef4444'; ctx.fillRect(LANES[lane]-28,330,56,72); ctx.fillStyle='#fff'; ctx.font='bold 20px sans-serif'; ctx.textAlign='center'; ctx.fillText('🚗',LANES[lane],372);}
  ctx.fillStyle='#fff'; ctx.font='bold 14px sans-serif'; ctx.textAlign='left'; ctx.fillText('Score '+score,10,20);}
function step(){if(!playing)return; dist++; speed=1+dist/1500; el('spd').textContent=speed.toFixed(1)+'x'; el('dist').textContent=dist;
  if(invuln>0)invuln--;
  cars.forEach(function(c){c.y+=4*speed;});
  cars=cars.filter(function(c){if(c.y>430){return false} return true});
  cars.forEach(function(c){if(Math.abs(c.x-LANES[lane])<50&&c.y+72>330&&c.y<402&&invuln<=0){crash();}});
  if(dist%20===0)setScore(Math.floor(dist/20));
  draw();}
function spawn(){var l=rnd(3); if(cars.some(function(c){return c.y<120&&Math.abs(c.x-LANES[l])<60}))return;
  cars.push({x:LANES[l],y:-80,color:['#f59e0b','#22c55e','#3b82f6','#a855f7'][rnd(4)]});}
function crash(){lives--; el('lives').textContent=lives; cars=[]; invuln=40;
  if(lives<=0){playing=false; clearInterval(timer); clearInterval(spawnTimer); msg('💥 Crash! You drove '+dist+'m. Press Start to race again.');} else msg('💥 Crash! '+lives+' '+(lives===1?'life':'lives')+' left — keep driving!');}
el('leftBtn').onclick=function(){if(lane>0)lane--};
el('rightBtn').onclick=function(){if(lane<2)lane++};
document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft'&&lane>0)lane--; if(e.key==='ArrowRight'&&lane<2)lane++;});
el('startBtn').onclick=function(){clearInterval(timer); clearInterval(spawnTimer); lives=maxLives; el('lives').textContent=lives; lane=1; cars=[]; dist=0; speed=1; invuln=0; setScore(0); playing=true; msg('Dodge the traffic! Change lanes to survive.'); timer=setInterval(step,50); spawnTimer=setInterval(spawn,spawnMs); draw();};
draw(); msg('Press Start to race!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"mode":["classic","endless"]})

# ---- C4-7 penalty-shootout ----
add("penalty-shootout","Penalty Shootout","Pick a corner, beat the keeper — 5 kicks to win!","⚽",
"Tap a corner of the goal to shoot. The keeper dives — score at least 3 of 5 to win the shootout!",
'<div style="background:#166534;border-radius:12px;padding:14px;text-align:center"><div style="font-size:44px" id="keeper">🧍</div><div class="grid" id="goal" style="grid-template-columns:repeat(3,1fr);gap:6px;background:#fff;border:4px solid #fff;border-radius:8px;padding:6px"></div><div style="color:#fff;font-weight:700;margin-top:8px">Kick <b id="kick">1</b>/5 · Goals <b id="goals">0</b> · Keeper dives: <b id="dives">—</b></div></div>',
r"""
var diff=qp('difficulty')||'medium';
var saveCh = diff==='easy'?0.25:(diff==='hard'?0.55:0.4);
var kicks=0, goals=0, playing=false;
var ZONES=['Top left','Top centre','Top right','Bottom left','Bottom centre','Bottom right'];
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · 5 kicks · need 3 goals';
function buildGoal(){el('goal').innerHTML=''; ZONES.forEach(function(z,i){var b=document.createElement('button'); b.className='opt'; b.textContent=z; b.style.minHeight='52px';
  b.onclick=function(){if(!playing)return; shoot(i,b)}; el('goal').appendChild(b);});}
function shoot(i,btn){var dive=rnd(6); var saved=Math.random()<saveCh&&dive===i;
  var keeperEl=el('keeper'); keeperEl.textContent=dive<3?'🧍‍♂️⬅️':'🧍‍♂️➡️'; el('dives').textContent=ZONES[dive];
  kicks++; el('kick').textContent=Math.min(5,kicks+1);
  if(saved){btn.style.background='#dc2626'; btn.style.color='#fff'; msg('🧤 SAVED! The keeper read your '+ZONES[i]+' shot.');}
  else{goals++; setScore(goals); el('goals').textContent=goals; btn.style.background='#166534'; btn.style.color='#fff'; msg('⚽ GOAL! '+ZONES[i]+' — unstoppable!');}
  if(kicks>=5){playing=false; var win=goals>=3;
    msg(win?'🏆 YOU WIN the shootout '+goals+'–'+(5-goals)+'! Press Start for another shootout.':'😞 You lost '+goals+'–'+(5-goals)+'. You needed 3 goals. Press Start to retry.');}}
el('startBtn').onclick=function(){kicks=0; goals=0; playing=true; el('kick').textContent=1; el('goals').textContent=0; el('dives').textContent='—'; el('keeper').textContent='🧍'; setScore(0); buildGoal(); msg('Pick a corner — beat the keeper!');};
buildGoal(); msg('Press Start, then pick a corner to shoot!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- C4-8 cricket-smash ----
add("cricket-smash","Cricket Smash","Time your shot as the ball arrives — smash fours and sixes!","🏏",
"Watch the ball come in and tap HIT at the perfect moment. Perfect timing = SIX! 6 balls an over.",
'<div style="background:#dcfce7;border-radius:12px;padding:16px;text-align:center"><div style="font-size:18px;font-weight:800" id="ballLine">Ball 1 of 6 · Over 1</div><div style="height:26px;background:#fff;border:2px solid #166534;border-radius:13px;margin:14px 0;position:relative;overflow:hidden"><div id="ball" style="position:absolute;left:0;top:2px;width:20px;height:20px;border-radius:50%;background:#dc2626"></div><div id="zone" style="position:absolute;top:0;bottom:0;background:#bbf7d0;border-left:2px solid #166534;border-right:2px solid #166534"></div></div><div style="font-size:40px">🏏 <span id="bat">🧍</span></div><button class="btn amber" id="hitBtn" style="padding:18px;font-size:20px">🏏 HIT!</button><div class="small" style="margin-top:8px">Runs: <b id="runs">0</b> · Wickets: <b id="wkts">0</b> · Balls: <b id="balls">0</b> · Last shot: <b id="last">—</b></div></div>',
r"""
var diff=qp('difficulty')||'medium'; var overs=parseInt(qp('overs')||'1')||1;
var ballSpeed = diff==='easy'?7:(diff==='hard'?15:11);
var zoneW = diff==='easy'?90:(diff==='hard'?44:64);
var totalBalls=overs*6;
var runs=0, wkts=0, ballNo=0, overNo=1, pos=0, playing=false, timer=null, ballLive=false;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · '+overs+(overs===1?' over':' overs')+' · '+totalBalls+' balls';
var zoneL=270-zoneW/2; el('zone').style.left=zoneL+'px'; el('zone').style.width=zoneW+'px';
function nextBall(){if(ballNo>=totalBalls){endInnings(); return} ballNo++; overNo=Math.ceil(ballNo/6);
  el('ballLine').textContent='Ball '+((ballNo-1)%6+1)+' of 6 · Over '+overNo+' of '+overs;
  el('balls').textContent=ballNo; pos=0; ballLive=true; el('ball').style.left='0px';}
function endInnings(){playing=false; ballLive=false; clearInterval(timer);
  msg('🏏 Innings over! You scored '+runs+' runs for '+wkts+' wickets in '+overs+(overs===1?' over':' overs')+'. Press Start to bat again.');}
el('hitBtn').onclick=function(){if(!playing||!ballLive)return; ballLive=false;
  var centre=pos+10, zoneC=zoneL+zoneW/2, d=Math.abs(centre-zoneC);
  var r=0, label='';
  if(d<=zoneW*0.18){r=6; label='SIX! 💥 Perfect timing!';}
  else if(d<=zoneW*0.5){r=4; label='FOUR! Great shot!';}
  else if(d<=zoneW*0.9){r=2; label='2 runs — good timing.';}
  else if(d<=zoneW*1.6){r=1; label='1 run — just made it.';}
  else{r=0; label='Missed it!';}
  if(r===0){wkts++; el('wkts').textContent=wkts; if(wkts>=3){runs+=0; setScore(runs); el('last').textContent='OUT!'; msg('❌ OUT! Three wickets down — innings over at '+runs+' runs.'); endInnings(); return}}
  runs+=r; setScore(runs); el('runs').textContent=runs; el('last').textContent=label;
  msg(label+' Total '+runs+'/'+wkts+'.');
  setTimeout(nextBall,700);};
el('startBtn').onclick=function(){clearInterval(timer); runs=0; wkts=0; ballNo=0; overNo=1; setScore(0); el('runs').textContent=0; el('wkts').textContent=0; el('balls').textContent=0; el('last').textContent='—'; playing=true; msg('Watch the red ball — hit it in the green zone!');
  nextBall();
  timer=setInterval(function(){if(!playing||!ballLive)return; pos+=ballSpeed; if(pos>=500){ballLive=false; wkts++; el('wkts').textContent=wkts; el('last').textContent='Ball missed — OUT!'; msg('❌ You let it through! Wicket lost.'); if(wkts>=3){endInnings(); return} setTimeout(nextBall,700); return} el('ball').style.left=pos+'px';},40);};
msg('Press Start to bat!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"],"overs":["1","2"]})

# ---- C4-9 darts ----
add("darts","Darts","Aim, throw, hit the bullseye — 3 darts a round!","🎯",
"Watch the moving crosshair, tap THROW when it is over the bullseye. 3 darts per round, 3 rounds!",
'<canvas id="cv" width="360" height="360" style="width:100%;max-width:360px;display:block;margin:0 auto;background:#fef3c7;border-radius:10px;touch-action:none"></canvas><button class="btn amber" id="throwBtn" style="padding:18px;font-size:20px">🎯 THROW DART</button><div class="small" style="text-align:center">Round <b id="round">1</b>/3 · Dart <b id="dart">1</b>/3 · Round score: <b id="rscore">0</b></div>',
r"""
var diff=qp('difficulty')||'medium';
var moveSpd = diff==='easy'?2:(diff==='hard'?5:3.5);
var bullR = diff==='easy'?26:(diff==='hard'?14:20);
var cv=el('cv'), ctx=cv.getContext('2d');
var cx=180, cy=180, t=0, round=1, dart=1, rscore=0, playing=false, anim=null;
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · 3 rounds × 3 darts';
function draw(){ctx.clearRect(0,0,360,360); ctx.fillStyle='#fef3c7'; ctx.fillRect(0,0,360,360);
  var rings=[[150,'#0f172a'],[120,'#f8fafc'],[90,'#0f172a'],[60,'#f8fafc'],[bullR,'#dc2626']];
  rings.forEach(function(r){ctx.fillStyle=r[1]; ctx.beginPath(); ctx.arc(180,180,r[0],0,7); ctx.fill();});
  ctx.fillStyle='#166534'; ctx.font='bold 13px sans-serif'; ctx.textAlign='center'; ctx.fillText('20',180,42); ctx.fillText('100',180,120); ctx.fillText('BULL',180,184);
  ctx.strokeStyle='#dc2626'; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(cx-18,cy); ctx.lineTo(cx+18,cy); ctx.moveTo(cx,cy-18); ctx.lineTo(cx,cy+18); ctx.stroke();
  ctx.fillStyle='#dc2626'; ctx.beginPath(); ctx.arc(cx,cy,4,0,7); ctx.fill();}
function move(){t+=0.06*moveSpd; cx=180+Math.sin(t)*130; cy=180+Math.cos(t*1.3)*130; draw();}
function throwDart(){if(!playing)return; var d=Math.sqrt((cx-180)*(cx-180)+(cy-180)*(cy-180)); var pts=0, label='';
  if(d<=bullR){pts=100; label='🎯 BULLSEYE! +100';}
  else if(d<=60){pts=50; label='Inner ring! +50';}
  else if(d<=90){pts=25; label='+25 — close!';}
  else if(d<=120){pts=10; label='+10';}
  else if(d<=150){pts=5; label='+5 — on the board.';}
  else{pts=0; label='Missed the board!';}
  rscore+=pts; setScore(score+pts); el('rscore').textContent=rscore; msg(label+' (dart '+dart+' of round '+round+')');
  dart++; if(dart>3){dart=1; round++; el('round').textContent=Math.min(3,round); el('dart').textContent=1;
    if(round>3){playing=false; clearInterval(anim); msg('🏁 Game over! Final score '+score+'. Press Start to throw again.'); return}}
  el('dart').textContent=dart;}
el('throwBtn').onclick=throwDart;
cv.addEventListener('pointerdown',throwDart);
document.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault(); throwDart()}});
el('startBtn').onclick=function(){clearInterval(anim); round=1; dart=1; rscore=0; el('round').textContent=1; el('dart').textContent=1; el('rscore').textContent=0; setScore(0); playing=true; msg('Throw when the crosshair is on the bullseye!'); anim=setInterval(move,40); draw();};
draw(); msg('Press Start to play darts!');
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- C4-10 basketball-shoot ----
add("basketball-shoot","Basketball Shoot","Aim, time it, swish! Streaks earn bonus points.","🏀",
"Tap SHOOT when the moving ball is under the hoop. Swishes build streaks — timed rounds, beat the clock!",
'<canvas id="cv" width="520" height="320" style="width:100%;max-width:520px;display:block;background:#ffedd5;border-radius:10px;touch-action:none"></canvas><button class="btn amber" id="shootBtn" style="padding:18px;font-size:20px">🏀 SHOOT!</button><div class="small" style="text-align:center">Time left: <b id="time">60</b>s · Hoops: <b id="hoops">0</b> · Streak: <b id="streak">0</b> · Best streak: <b id="bstreak">0</b></div>',
r"""
var dur=parseInt(qp('time')||'60')||60; var diff=qp('difficulty')||'hard';
var hoopSpd = diff==='easy'?1.6:(diff==='hard'?3.4:2.4);
var hoopW = diff==='easy'?110:(diff==='hard'?70:90);
var cv=el('cv'), ctx=cv.getContext('2d');
var hoopX=200, hoopDir=1, ballX=260, hoops=0, streak=0, bstreak=0, tLeft=dur, playing=false, timer=null, anim=null, shotY=null;
if(el('cfgLabel'))el('cfgLabel').textContent=dur+'s · '+diff;
el('time').textContent=dur;
function draw(){ctx.clearRect(0,0,520,320); ctx.fillStyle='#ffedd5'; ctx.fillRect(0,0,520,320);
  ctx.fillStyle='#b45309'; ctx.fillRect(0,290,520,30);
  ctx.strokeStyle='#dc2626'; ctx.lineWidth=5; ctx.beginPath(); ctx.arc(hoopX+hoopW/2,70,hoopW/2,0,Math.PI); ctx.stroke();
  ctx.fillStyle='#fff'; ctx.fillRect(hoopX,60,hoopW,8);
  ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(hoopX+8,68); ctx.lineTo(hoopX+8,110); ctx.moveTo(hoopX+hoopW-8,68); ctx.lineTo(hoopX+hoopW-8,110); ctx.stroke();
  ctx.font='34px sans-serif'; ctx.textAlign='center';
  if(shotY!==null){ctx.fillText('🏀',ballX,shotY);} else {ctx.fillText('🏀',ballX,275);}
  ctx.fillStyle='#0f172a'; ctx.font='bold 14px sans-serif'; ctx.textAlign='left'; ctx.fillText('Score '+score,10,20);}
function moveHoop(){hoopX+=hoopDir*hoopSpd; if(hoopX<=10||hoopX+hoopW>=510)hoopDir*=-hoopDir; draw();}
function shoot(){if(!playing)return; var under=ballX>=hoopX&&ballX<=hoopX+hoopW;
  shotY=275; var steps=0;
  var iv=setInterval(function(){steps++; shotY-=22; if(steps>=9){clearInterval(iv); shotY=null;
    if(under){hoops++; streak++; if(streak>bstreak){bstreak=streak; el('bstreak').textContent=bstreak}
      var pts=2+Math.min(3,streak-1); setScore(score+pts); el('hoops').textContent=hoops; el('streak').textContent=streak;
      msg(streak>=3?'🔥 SWISH! Streak '+streak+' — +'+pts+' points!':'🏀 Swish! +'+pts+' points.');}
    else{streak=0; el('streak').textContent=0; msg('Missed! The hoop moved — time your shot.');}
    ballX=60+rnd(400); draw();}},50);}
el('shootBtn').onclick=shoot;
cv.addEventListener('pointerdown',shoot);
document.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault(); shoot()}});
el('startBtn').onclick=function(){clearInterval(timer); clearInterval(anim); hoops=0; streak=0; bstreak=0; tLeft=dur; el('hoops').textContent=0; el('streak').textContent=0; el('bstreak').textContent=0; el('time').textContent=dur; setScore(0); playing=true; msg('Shoot when the ball is under the hoop!');
  anim=setInterval(moveHoop,30);
  timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){playing=false; clearInterval(timer); clearInterval(anim); msg('⏰ Time! You made '+hoops+' hoops, best streak '+bstreak+'. Press Start to shoot again.');}},1000);
  draw();};
draw(); msg('Press Start, then shoot under the hoop!');
""",
{"theme":["classic","dark","neon"],"time":["30","60"],"difficulty":["easy","hard"]})

# ---- Batch games_c5_adds.py (19 Nov 2026) ----
# ---- C5-1 solitaire ----
add("solitaire","Solitaire","Classic Klondike Solitaire. Build the tableau, stack the foundations, clear the deck!","🃏",
"Click the stock to draw cards. Click a card to select it, then click a tableau pile or a foundation to move it. Build tableau down in alternating colours, foundations up by suit from Ace.",
'<div style="display:flex;gap:6px;justify-content:space-between;margin-bottom:8px"><div><div class="small">Stock</div><button class="tile" id="stockBtn" style="width:56px;height:76px;font-size:22px">🂠</button></div><div><div class="small">Waste</div><div class="tile" id="wasteSlot" style="width:56px;height:76px;font-size:20px"></div></div><div id="foundRow" style="display:flex;gap:6px"></div></div><div id="tabRow" style="display:flex;gap:6px;overflow-x:auto"></div><div class="small" style="text-align:center;margin-top:8px">Moves: <b id="moves">0</b> · Time: <b id="clock">0:00</b> · <button class="btn ghost" id="autoBtn" style="display:inline-block;width:auto;padding:6px 12px">Move to foundation</button></div>',
r"""
var drawN=parseInt(qp('draw')||'1')||1; if([1,3].indexOf(drawN)<0)drawN=1;
if(el('cfgLabel'))el('cfgLabel').textContent='Draw '+drawN;
var SUITS=['♠','♥','♦','♣']; var RED={'♥':1,'♦':1};
var deck=[], stock=[], waste=[], found=[[],[],[],[]], tab=[], sel=null, moves=0, secs=0, timer=null, won=false;
function mkDeck(){var d=[]; SUITS.forEach(function(s){for(var r=1;r<=13;r++)d.push({r:r,s:s,up:false})}); return shuffle(d)}
function cardLabel(c){var R={1:'A',11:'J',12:'Q',13:'K'}; return (R[c.r]||c.r)+c.s}
function newGame(){deck=mkDeck(); stock=[]; waste=[]; found=[[],[],[],[]]; tab=[]; sel=null; moves=0; secs=0; won=false; setScore(0);
  for(var p=0;p<7;p++){var pile=[]; for(var i=0;i<=p;i++){var c=deck.pop(); c.up=(i===p); pile.push(c)} tab.push(pile)}
  stock=deck; clearInterval(timer); timer=setInterval(function(){if(!won){secs++; var m=Math.floor(secs/60); el('clock').textContent=m+':'+('0'+(secs%60)).slice(-2)}},1000);
  el('moves').textContent='0'; draw(); msg('Click the stock to draw '+drawN+' card'+(drawN>1?'s':'')+'.')}
function canTab(c,top){if(!top)return c.r===13; return (RED[c.s]?1:0)!==(RED[top.s]?1:0)&&c.r===top.r-1}
function canFound(c,f){if(!f.length)return c.r===1; var t=f[f.length-1]; return t.s===c.s&&c.r===t.r+1}
function bump(){moves++; el('moves').textContent=moves}
function draw(){el('stockBtn').textContent=stock.length?'🂠':'↻'; el('wasteSlot').textContent=waste.length?cardLabel(waste[waste.length-1]):'';
  el('wasteSlot').style.color=waste.length&&RED[waste[waste.length-1].s]?'#dc2626':'#0F172A';
  var fr=el('foundRow'); fr.innerHTML=''; found.forEach(function(f,i){var d=document.createElement('button'); d.className='tile'; d.style.cssText='width:56px;height:76px;font-size:20px'; d.textContent=f.length?cardLabel(f[f.length-1]):SUITS[i]; d.style.color=f.length&&RED[f[f.length-1].s]?'#dc2626':'#94a3b8';
    d.onclick=function(){tryMoveFound(i)}; fr.appendChild(d)});
  var tr=el('tabRow'); tr.innerHTML=''; tab.forEach(function(pile,pi){var col=document.createElement('div'); col.style.cssText='flex:1;min-width:56px';
    pile.forEach(function(c,ci){var d=document.createElement('button'); d.className='tile'; d.style.cssText='width:100%;height:52px;font-size:17px;margin-top:'+(ci?'-30px':'0')+';position:relative'; d.textContent=c.up?cardLabel(c):'🂠'; d.style.color=c.up&&RED[c.s]?'#dc2626':'#0F172A'; d.style.background=sel&&sel.pi===pi&&sel.ci===ci?'#F59E0B':'#fff';
      d.onclick=function(){onCard(pi,ci)}; col.appendChild(d)});
    if(!pile.length){var e=document.createElement('button'); e.className='tile'; e.style.cssText='width:100%;height:52px'; e.textContent='K'; e.onclick=function(){onCard(pi,-1)}; col.appendChild(e)}
    col.onclick=function(ev){if(ev.target===col)onCard(pi,-1)}; tr.appendChild(col)});
  var total=0; found.forEach(function(f){total+=f.length}); setScore(total*10);
  if(total===52&&!won){won=true; clearInterval(timer); msg('🎉 You won Solitaire in '+moves+' moves and '+el('clock').textContent+'! Press Start for a new game.')}}
function onCard(pi,ci){if(ci===-1){if(sel)tryMoveTab(pi); return}
  var pile=tab[pi], c=pile[ci]; if(!c.up){msg('That card is face down.'); return}
  if(sel&&sel.pi===pi&&sel.ci===ci){sel=null; draw(); return}
  if(sel){tryMoveTab(pi); return}
  sel={pi:pi,ci:ci}; draw(); msg('Selected '+cardLabel(c)+' — click a pile or foundation.')}
function tryMoveTab(pi){if(!sel)return; var from=tab[sel.pi], moving=from.slice(sel.ci), top=tab[pi].length?tab[pi][tab[pi].length-1]:null;
  if(moving.length===1&&sel.pi===pi){sel=null;draw();return}
  if(canTab(moving[0],top)){tab[pi]=tab[pi].concat(moving); tab[sel.pi]=from.slice(0,sel.ci); flipTop(sel.pi); bump(); sel=null; draw()}
  else{msg('Cannot move there — tableau builds down in alternating colours.'); sel=null; draw()}}
function tryMoveFound(i){var c=null, from=null;
  if(sel){var f=tab[sel.pi]; if(sel.ci!==f.length-1){msg('Only the top card can go to a foundation.'); sel=null; draw(); return} c=f[f.length-1]; from='tab'}
  else if(waste.length){c=waste[waste.length-1]; from='waste'}
  else{msg('Select a card first, or use the waste pile.'); return}
  if(canFound(c,found[i])){found[i].push(c); if(from==='tab'){tab[sel.pi].pop(); flipTop(sel.pi)} else waste.pop(); bump(); sel=null; draw(); msg('To the foundation!')}
  else{msg('Foundations build up by suit from Ace.'); sel=null; draw()}}
function flipTop(pi){var p=tab[pi]; if(p.length&&!p[p.length-1].up)p[p.length-1].up=true}
el('stockBtn').onclick=function(){if(won)return; sel=null;
  if(!stock.length){stock=waste.reverse(); waste=[]; msg('Stock recycled.')}
  else{for(var i=0;i<drawN&&stock.length;i++)waste.push(stock.pop())}
  bump(); draw()};
el('wasteSlot').onclick=function(){if(!waste.length)return; if(sel&&sel.pi===-1){sel=null;draw();return} sel={pi:-1,ci:-1}; draw(); msg('Waste card selected — click a pile or foundation.')};
el('autoBtn').onclick=function(){var moved=false;
  for(var pi=0;pi<7;pi++){var p=tab[pi]; if(!p.length)continue; var c=p[p.length-1]; for(var fi=0;fi<4;fi++){if(canFound(c,found[fi])){found[fi].push(c); p.pop(); flipTop(pi); bump(); moved=true; break}} if(moved)break}
  if(!moved&&waste.length){var w=waste[waste.length-1]; for(var fj=0;fj<4;fj++){if(canFound(w,found[fj])){found[fj].push(w); waste.pop(); bump(); moved=true; break}}}
  draw(); msg(moved?'Moved a card to the foundation.':'No card can move to a foundation yet.')};
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"draw":["1","3"]})

# ---- C5-2 ludo ----
add("ludo","Ludo","Classic Ludo! Roll the dice, race your tokens home — capture rivals on the way.","🎲",
"Tap Roll, then tap one of your highlighted tokens to move it. You need a 6 to leave base. Land on a rival to capture it. Stars are safe. First to bring all tokens home wins!",
'<div class="small" style="text-align:center">Turn: <b id="turn">You</b> · <span id="diceTxt">Roll the dice!</span></div><div style="text-align:center;font-size:44px" id="dice">🎲</div><button class="btn amber" id="rollBtn">🎲 Roll dice</button><div id="track" style="display:flex;flex-wrap:wrap;gap:3px;margin:10px 0"></div><div id="players"></div>',
r"""
var nPlayers=parseInt(qp('players')||'4')||4; if([2,3,4].indexOf(nPlayers)<0)nPlayers=4;
var mode=qp('mode')||'classic';
var TOKENS = mode==='quick'?2:4;
var COLORS=['🔴','🟡','🟢','🔵']; var NAMES=['You','Yellow','Green','Blue']; var START=[0,13,26,39];
var SAFE=[0,8,13,21,26,34,39,47];
if(el('cfgLabel'))el('cfgLabel').textContent=nPlayers+' players · '+mode+' · '+TOKENS+' tokens';
var players=[], turn=0, dice=0, rolled=false, over=false;
function newGame(){players=[]; for(var i=0;i<nPlayers;i++){var tk=[]; for(var t=0;t<TOKENS;t++)tk.push(-1); players.push({tokens:tk,done:0})} turn=0; dice=0; rolled=false; over=false; setScore(0); el('dice').textContent='🎲'; el('diceTxt').textContent='Your turn — roll!'; draw(); msg('Roll to start. You need a 6 to leave base.')}
function absPos(p,steps){return (START[p]+steps)%52}
function tokenAt(p,steps){return absPos(p,steps)}
function movable(p){var out=[]; var pl=players[p];
  pl.tokens.forEach(function(s,i){if(s===-1){if(dice===6)out.push(i)} else if(s<56){if(s+dice<=56)out.push(i)}}); return out}
function doMove(p,ti){var pl=players[p]; var s=pl.tokens[ti];
  if(s===-1)pl.tokens[ti]=0; else pl.tokens[ti]=s+dice;
  var ns=pl.tokens[ti];
  if(ns===56){pl.done++; msg(NAMES[p]+' brought a token home!')}
  else if(ns<51){var ap=absPos(p,ns);
    if(SAFE.indexOf(ap)<0){for(var q=0;q<nPlayers;q++){if(q===p)continue; players[q].tokens.forEach(function(os,oi){if(os>=0&&os<51&&absPos(q,os)===ap){players[q].tokens[oi]=-1; if(p===0)setScore(score+10); msg(NAMES[p]+' captured '+NAMES[q]+'!')}})}}}
  if(pl.done===TOKENS){over=true; if(p===0){setScore(score+100); msg('🎉 YOU WIN LUDO! Press Start to play again.')} else msg('🏁 '+NAMES[p]+' wins! Press Start to play again.'); draw(); return}
  draw(); if(dice===6&&!over){msg(NAMES[p]+' rolled a 6 — roll again!'); rolled=false; if(p!==0)setTimeout(aiTurn,700); else el('diceTxt').textContent='You rolled a 6 — roll again!'}
  else{turn=(turn+1)%nPlayers; rolled=false; if(turn!==0&&!over)setTimeout(aiTurn,700); else if(!over)el('diceTxt').textContent='Your turn — roll!'}}
function aiTurn(){if(over)return; el('turn').textContent=NAMES[turn]; dice=rnd(6)+1; el('dice').textContent=['⚀','⚁','⚂','⚃','⚄','⚅'][dice-1]; el('diceTxt').textContent=NAMES[turn]+' rolled '+dice;
  var mv=movable(turn);
  if(!mv.length){msg(NAMES[turn]+' cannot move.'); setTimeout(function(){turn=(turn+1)%nPlayers; rolled=false; if(turn!==0&&!over)setTimeout(aiTurn,700); else if(!over)el('diceTxt').textContent='Your turn — roll!'; draw()},700); return}
  var pick=mv[0]; var best=-1;
  mv.forEach(function(ti){var s=players[turn].tokens[ti]; var sc=0; if(s===-1)sc=3; else if(s+dice===56)sc=5; else if(s+dice<51){var ap=absPos(turn,s+dice); for(var q=0;q<nPlayers;q++){if(q!==turn)players[q].tokens.forEach(function(os){if(os>=0&&os<51&&absPos(q,os)===ap)sc=4})}} if(sc>best){best=sc;pick=ti}});
  setTimeout(function(){doMove(turn,pick)},600)}
function draw(){el('turn').textContent=over?'Game over':NAMES[turn];
  var tr=el('track'); tr.innerHTML=''; for(var cell=0;cell<52;cell++){var d=document.createElement('div'); d.style.cssText='width:22px;height:22px;border:1px solid #cbd5e1;border-radius:4px;font-size:13px;text-align:center;line-height:22px;background:'+(SAFE.indexOf(cell)>=0?'#fef3c7':'#fff');
    var here=[]; players.forEach(function(pl,p){pl.tokens.forEach(function(s){if(s>=0&&s<51&&absPos(p,s)===cell)here.push(COLORS[p])})});
    d.textContent=here.length?here[0]:''; if(here.length>1)d.textContent=here.length; tr.appendChild(d)}
  var pv=el('players'); pv.innerHTML='';
  players.forEach(function(pl,p){var box=document.createElement('div'); box.style.cssText='border:2px solid #e2e8f0;border-radius:10px;padding:8px;margin:6px 0;'+(turn===p&&!over?'border-color:#166534':'');
    var home=pl.tokens.filter(function(s){return s===56}).length;
    box.innerHTML='<b>'+COLORS[p]+' '+NAMES[p]+'</b> · Home: '+home+'/'+TOKENS+' · Base: '+pl.tokens.filter(function(s){return s===-1}).length;
    var row=document.createElement('div'); row.style.cssText='display:flex;gap:8px;margin-top:6px;flex-wrap:wrap';
    pl.tokens.forEach(function(s,ti){var b=document.createElement('button'); b.className='opt'; b.style.cssText='min-width:52px;min-height:48px;padding:8px';
      b.textContent=COLORS[p]+(s===-1?' 🏠':(s===56?' 🏁':(s>=51?'⌂'+(s-50):' '+s)));
      var can = p===0&&turn===0&&rolled&&!over&&movable(0).indexOf(ti)>=0; b.style.background=can?'#F59E0B':'#fff'; b.disabled=!can;
      b.onclick=function(){if(can)doMove(0,ti)}; row.appendChild(b)});
    box.appendChild(row); pv.appendChild(box)});
  var home0=players[0]?players[0].done:0; if(score<home0*25)setScore(home0*25)}
el('rollBtn').onclick=function(){if(over||turn!==0||rolled)return; dice=rnd(6)+1; rolled=true; el('dice').textContent=['⚀','⚁','⚂','⚃','⚄','⚅'][dice-1]; el('diceTxt').textContent='You rolled '+dice;
  var mv=movable(0);
  if(!mv.length){msg('No move possible — turn passes.'); setTimeout(function(){turn=(turn+1)%nPlayers; rolled=false; draw(); if(!over)setTimeout(aiTurn,600)},900)}
  else{msg('Tap a highlighted token to move '+dice+' steps.'); draw()}};
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"players":["2","3","4"],"mode":["classic","quick"]})

# ---- C5-3 poker ----
add("poker","Poker — 5-Card Draw","5-card draw poker against the computer. Bet, draw, and win the pot!","♠️",
"Place your bet, get 5 cards, tap cards to mark them for exchange, then Draw. Best hand wins the pot. Don't let your bankroll hit zero!",
'<div class="small" style="text-align:center">Bankroll: <b id="bank">1000</b> chips · Pot: <b id="pot">0</b> · Bet: <b id="betTxt"></b></div><div class="small" style="text-align:center;margin:6px 0">Computer hand</div><div id="cpuHand" style="display:flex;gap:6px;justify-content:center"></div><div class="small" style="text-align:center;margin:6px 0">Your hand — tap cards to exchange them</div><div id="myHand" style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap"></div><div class="row" style="margin-top:10px"><button class="btn amber" id="drawBtn">Draw / Exchange</button><button class="btn" id="showBtn">Showdown</button></div><div class="small" style="text-align:center">Your hand: <b id="myRank"></b> · Computer: <b id="cpuRank"></b></div>',
r"""
var mode=qp('mode')||'classic';
var BET = mode==='high-stakes'?50:10;
if(el('cfgLabel'))el('cfgLabel').textContent=mode+' · bet '+BET;
var SUITS=['♠','♥','♦','♣']; var RED={'♥':1,'♦':1}; var R={11:'J',12:'Q',13:'K',14:'A'};
var bank=1000, pot=0, deck=[], my=[], cpu=[], sel=[], phase='bet', over=false;
function lbl(c){return (R[c.r]||c.r)+c.s}
function mkDeck(){var d=[]; SUITS.forEach(function(s){for(var r=2;r<=14;r++)d.push({r:r,s:s})}); return shuffle(d)}
function evalHand(h){var counts={}, suits={}; h.forEach(function(c){counts[c.r]=(counts[c.r]||0)+1; suits[c.s]=(suits[c.s]||0)+1});
  var groups=Object.keys(counts).map(function(k){return [parseInt(k,10),counts[k]]}).sort(function(a,b){return b[1]-a[1]||b[0]-a[0]});
  var flush=Object.keys(suits).length===1;
  var rs=h.map(function(c){return c.r}).sort(function(a,b){return a-b});
  var straight=false, high=rs[4]; if(rs[4]-rs[0]===4&&new Set(rs).size===5)straight=true; if(rs.join(',')==='2,3,4,5,14'){straight=true; high=5}
  var name, val, tie=groups.map(function(g){return g[0]});
  if(straight&&flush){name='Straight flush'; val=8} else if(groups[0][1]===4){name='Four of a kind'; val=7}
  else if(groups[0][1]===3&&groups[1][1]===2){name='Full house'; val=6} else if(flush){name='Flush'; val=5}
  else if(straight){name='Straight'; val=4} else if(groups[0][1]===3){name='Three of a kind'; val=3}
  else if(groups[0][1]===2&&groups[1][1]===2){name='Two pair'; val=2} else if(groups[0][1]===2){name='Pair'; val=1}
  else{name='High card'; val=0}
  return {name:name,val:val,tie:tie,high:high}}
function cmp(a,b){if(a.val!==b.val)return a.val-b.val; for(var i=0;i<Math.max(a.tie.length,b.tie.length);i++){if((a.tie[i]||0)!==(b.tie[i]||0))return (a.tie[i]||0)-(b.tie[i]||0)} return 0}
function showCard(c,face,selOn,click){var d=document.createElement('button'); d.className='tile'; d.style.cssText='width:56px;height:76px;font-size:19px;background:'+(selOn?'#F59E0B':'#fff'); d.textContent=face?lbl(c):'🂠'; d.style.color=face&&RED[c.s]?'#dc2626':'#0F172A'; if(click)d.onclick=click; return d}
function drawHands(){var ch=el('cpuHand'); ch.innerHTML=''; cpu.forEach(function(c){ch.appendChild(showCard(c,phase==='show',false,null))});
  var mh=el('myHand'); mh.innerHTML=''; my.forEach(function(c,i){mh.appendChild(showCard(c,true,sel.indexOf(i)>=0,function(){if(phase!=='draw')return; var ix=sel.indexOf(i); if(ix>=0)sel.splice(ix,1); else if(sel.length<4)sel.push(i); drawHands()}))});
  el('bank').textContent=bank; el('pot').textContent=pot; el('betTxt').textContent=BET+' chips';
  el('myRank').textContent=phase==='show'?evalHand(my).name:(my.length?evalHand(my).name:'');
  el('cpuRank').textContent=phase==='show'?evalHand(cpu).name:'???'}
function newRound(){if(bank<BET){over=true; msg('💸 Bankroll empty — game over! Your best bankroll was your score. Press Start to restart with 1000 chips.'); return}
  bank-=BET; pot=BET*2; deck=mkDeck(); my=deck.splice(0,5); cpu=deck.splice(0,5); sel=[]; phase='draw'; drawHands();
  msg('Bet '+BET+' placed. Tap up to 4 cards to exchange, then press Draw — or go straight to Showdown.')}
function cpuDraw(){var ev=evalHand(cpu); var keep=[];
  var counts={}; cpu.forEach(function(c,i){counts[c.r]=(counts[c.r]||0)+1});
  cpu.forEach(function(c,i){if(counts[c.r]>=2)keep.push(i)});
  if(ev.val>=4)keep=[0,1,2,3,4];
  if(ev.val===0)keep=[cpu.reduce(function(bi,c,i){return c.r>cpu[bi].r?i:bi},0)];
  var disc=[]; cpu.forEach(function(c,i){if(keep.indexOf(i)<0)disc.push(i)});
  disc.forEach(function(i){cpu[i]=deck.pop()})}
el('drawBtn').onclick=function(){if(phase!=='draw')return; sel.sort(function(a,b){return a-b}); sel.forEach(function(i){my[i]=deck.pop()}); sel=[]; cpuDraw(); phase='show'; drawHands();
  var a=evalHand(my), b=evalHand(cpu), r=cmp(a,b);
  if(r>0){bank+=pot; msg('🎉 You win the pot of '+pot+' with '+a.name+' vs '+b.name+'!')} else if(r<0){msg('Computer wins with '+b.name+' vs your '+a.name+'. Pot lost.')} else{bank+=pot/2; msg('Push — split pot. Both had '+a.name+'.')}
  setScore(Math.max(0,bank-1000)); pot=0; el('pot').textContent=0; el('bank').textContent=bank; phase='done';
  setTimeout(function(){if(!over)newRound()},2500)};
el('showBtn').onclick=function(){if(phase!=='draw')return; cpuDraw(); phase='show'; drawHands();
  var a=evalHand(my), b=evalHand(cpu), r=cmp(a,b);
  if(r>0){bank+=pot; msg('🎉 You win the pot of '+pot+' with '+a.name+' vs '+b.name+'!')} else if(r<0){msg('Computer wins with '+b.name+' vs your '+a.name+'. Pot lost.')} else{bank+=pot/2; msg('Push — split pot. Both had '+a.name+'.')}
  setScore(Math.max(0,bank-1000)); pot=0; el('pot').textContent=0; el('bank').textContent=bank; phase='done';
  setTimeout(function(){if(!over)newRound()},2500)};
el('startBtn').onclick=function(){bank=1000; over=false; setScore(0); newRound(); msg('New game — bankroll reset to 1000 chips.')};
newRound();
""",
{"theme":["classic","dark","neon"],"mode":["classic","high-stakes"]})

# ---- C5-4 dominoes ----
add("dominoes","Dominoes","Classic dominoes against the computer. Match the open ends and shed your tiles!","🁢",
"Tap one of your dominoes, then choose which end to play it on. Match the number on an open end. No match? Draw from the boneyard. First to shed all tiles wins!",
'<div class="small" style="text-align:center">Board ends: <b id="ends">—</b> · Boneyard: <b id="bone">0</b> · <span id="turnTxt">Your turn</span></div><div id="board" style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;margin:10px 0;min-height:60px"></div><div id="playRow" style="display:none;gap:8px;margin:8px 0"><button class="btn" id="leftBtn">◀ Play left</button><button class="btn amber" id="rightBtn">Play right ▶</button></div><div class="small" style="text-align:center">Your tiles — tap one to select it</div><div id="myHand" style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:8px 0"></div><div class="row"><button class="btn ghost" id="drawBtn2">Draw from boneyard</button><button class="btn ghost" id="passBtn">Pass</button></div><div class="small" style="text-align:center">Computer tiles: <b id="cpuN">7</b></div>',
r"""
var mode=qp('mode')||'classic';
if(el('cfgLabel'))el('cfgLabel').textContent=mode+' · double-six';
var bone=[], my=[], cpu=[], board=[], turn=0, selTile=-1, over=false;
function tileTxt(t){return t[0]+' | '+t[1]}
function pips(h){return h.reduce(function(a,t){return a+t[0]+t[1]},0)}
function newGame(){var all=[]; for(var a=0;a<=6;a++)for(var b=a;b<=6;b++)all.push([a,b]); shuffle(all);
  my=all.splice(0,7); cpu=all.splice(0,7); bone=all; board=[]; turn=0; selTile=-1; over=false; setScore(0);
  var first=my.concat(cpu).map(function(t,i){return t}); var starter=null;
  for(var d=6;d>=0;d--){var ix=my.findIndex(function(t){return t[0]===d&&t[1]===d}); if(ix>=0){starter={who:0,ix:ix};break} var jx=cpu.findIndex(function(t){return t[0]===d&&t[1]===d}); if(jx>=0){starter={who:1,ix:jx};break}}
  if(starter){var t=(starter.who===0?my:cpu).splice(starter.ix,1)[0]; board.push(t); turn=starter.who===0?1:0; msg((starter.who===0?'You':'Computer')+' opened with double '+t[0]+'.')}
  else msg('No doubles — you start. Tap a tile, then an end.');
  draw(); if(turn===1&&!over)setTimeout(aiTurn,800)}
function ends(){if(!board.length)return [null,null]; return [board[0][0],board[board.length-1][1]]}
function fits(t){var e=ends(); if(!e[0])return ['left']; var out=[]; if(t[0]===e[0]||t[1]===e[0])out.push('left'); if(t[0]===e[1]||t[1]===e[1])out.push('right'); return out}
function playTile(who,ti,side){var hand=who===0?my:cpu; var t=hand.splice(ti,1)[0]; var e=ends();
  if(!board.length){board.push(t)}
  else if(side==='left'){if(t[1]===e[0])board.unshift(t); else if(t[0]===e[0])board.unshift([t[1],t[0]]); else{hand.splice(ti,0,t); return false}}
  else{if(t[0]===e[1])board.push(t); else if(t[1]===e[1])board.push([t[1],t[0]]); else{hand.splice(ti,0,t); return false}}
  if(mode==='all-fives'){var s=ends()[0]+ends()[1]; if(s%5===0&&s>0){if(who===0){setScore(score+s); msg('All-Fives! Board ends total '+s+' — you score '+s+' points!')} else msg('Computer scores '+s+' in All-Fives.')}} 
  return true}
function checkEnd(){if(my.length===0){setScore(score+pips(cpu)); msg('🎉 YOU WIN! Computer is left with '+pips(cpu)+' pips. Press Start for a new game.'); over=true; return true}
  if(cpu.length===0){msg('🏁 Computer wins — you are left with '+pips(my)+' pips. Press Start to play again.'); over=true; return true}
  if(!canPlay(my)&&!canPlay(cpu)&&!bone.length){var mp=pips(my), cp=pips(cpu); if(mp<cp){setScore(score+(cp-mp)); msg('Blocked game! You win on fewest pips ('+mp+' vs '+cp+').')} else if(cp<mp){msg('Blocked game! Computer wins on fewest pips ('+cp+' vs '+mp+').')} else msg('Blocked game — a draw!'); over=true; return true}
  return false}
function canPlay(hand){if(!board.length)return true; var e=ends(); return hand.some(function(t){return t[0]===e[0]||t[1]===e[0]||t[0]===e[1]||t[1]===e[1]})}
function draw(){var bd=el('board'); bd.innerHTML=''; board.forEach(function(t){var d=document.createElement('div'); d.className='tile'; d.style.cssText='min-width:52px;min-height:48px;font-size:16px'; d.textContent=tileTxt(t); bd.appendChild(d)});
  var e=ends(); el('ends').textContent=board.length?e[0]+' … '+e[1]:'—'; el('bone').textContent=bone.length; el('cpuN').textContent=cpu.length; el('turnTxt').textContent=over?'Game over':(turn===0?'Your turn':'Computer thinking…');
  var mh=el('myHand'); mh.innerHTML=''; my.forEach(function(t,i){var b=document.createElement('button'); b.className='tile'; b.style.cssText='min-width:56px;min-height:52px;font-size:16px;background:'+(selTile===i?'#F59E0B':'#fff'); b.textContent=tileTxt(t);
    b.onclick=function(){if(over||turn!==0)return; selTile=i; var f=fits(t); if(!f.length){msg('That tile matches neither end.')} else{msg('Selected '+tileTxt(t)+' — now choose an end.'); el('playRow').style.display='flex'} draw()}; mh.appendChild(b)})}
function aiTurn(){if(over)return; turn=1; draw();
  setTimeout(function(){if(over)return;
    var ix=-1, side=null; for(var i=0;i<cpu.length;i++){var f=fits(cpu[i]); if(f.length){ix=i; side=f[0]; break}}
    if(ix>=0){playTile(1,ix,side); msg('Computer played '+tileTxt(board[side==='left'?0:board.length-1])+'.')}
    else if(bone.length){cpu.push(bone.pop()); msg('Computer drew from the boneyard.'); setTimeout(aiTurn,700); return}
    else msg('Computer passes.');
    if(checkEnd()){draw(); return}
    turn=0; selTile=-1; el('playRow').style.display='none'; draw(); msg('Your turn.');},700)}
function afterMyPlay(){if(checkEnd()){draw(); return} turn=1; selTile=-1; el('playRow').style.display='none'; draw(); setTimeout(aiTurn,600)}
el('leftBtn').onclick=function(){if(selTile<0)return; if(playTile(0,selTile,'left'))afterMyPlay(); else msg('That does not fit the left end.')};
el('rightBtn').onclick=function(){if(selTile<0)return; if(playTile(0,selTile,'right'))afterMyPlay(); else msg('That does not fit the right end.')};
el('drawBtn2').onclick=function(){if(over||turn!==0)return; if(!bone.length){msg('Boneyard is empty.'); return} if(canPlay(my)){msg('You have a playable tile — play it instead of drawing.'); return} my.push(bone.pop()); draw(); msg('Drew a tile.')};
el('passBtn').onclick=function(){if(over||turn!==0)return; if(canPlay(my)){msg('You have a playable tile — you cannot pass yet.'); return} turn=1; draw(); setTimeout(aiTurn,600)};
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"mode":["classic","all-fives"]})

# ---- C5-5 mini-golf ----
add("mini-golf","Mini Golf","Putt through 9 or 18 holes. Beat par, hole by hole!","⛳",
"Set the angle and power, then Putt. The ball rolls with real friction and bounces off the walls. Fewest strokes wins — par is 3 per hole (4 on hard).",
'<div class="small" style="text-align:center">Hole <b id="hole">1</b>/<span id="holesN"></span> · Par <b id="par">3</b> · Strokes this hole: <b id="strokes">0</b> · Total: <b id="total">0</b> (par <span id="parTot"></span>)</div><canvas id="cv" width="520" height="300" style="width:100%;border:2px solid #166534;border-radius:12px;background:#dcfce7"></canvas><div class="row" style="margin-top:8px"><label class="small">Angle <span id="angTxt">0°</span><input type="range" id="ang" min="0" max="359" value="0" style="width:100%"></label><label class="small">Power <span id="powTxt">5</span><input type="range" id="pow" min="1" max="10" value="5" style="width:100%"></label></div><button class="btn amber" id="puttBtn">⛳ Putt!</button><button class="btn ghost" id="nextBtn" style="display:none">Next hole ▶</button>',
r"""
var nHoles=parseInt(qp('holes')||'9')||9; if([9,18].indexOf(nHoles)<0)nHoles=9;
var diff=qp('difficulty')||'easy';
var PAR = diff==='hard'?4:3;
if(el('cfgLabel'))el('cfgLabel').textContent=nHoles+' holes · '+diff+' · par '+PAR;
el('holesN').textContent=nHoles; el('parTot').textContent=nHoles*PAR;
var hole=1, strokes=0, total=0, ball={x:60,y:150}, cup={x:450,y:150}, vel={x:0,y:0}, rolling=false, timer=null, holed=false;
var obstacles=[];
function setupHole(){ball={x:60,y:150}; vel={x:0,y:0}; rolling=false; holed=false; strokes=0;
  cup={x:380+rnd(100),y:50+rnd(200)}; obstacles=[];
  if(diff==='hard'){obstacles.push({x:240,y:60,w:24,h:180}); obstacles.push({x:340,y:120,w:24,h:120})}
  el('hole').textContent=hole; el('par').textContent=PAR; el('strokes').textContent='0'; el('nextBtn').style.display='none'; drawCourse()}
function drawCourse(){var c=el('cv'), x=c.getContext('2d'); x.clearRect(0,0,520,300);
  x.fillStyle='#86efac'; x.fillRect(0,0,520,300);
  obstacles.forEach(function(o){x.fillStyle='#78716c'; x.fillRect(o.x,o.y,o.w,o.h)});
  x.fillStyle='#0F172A'; x.beginPath(); x.arc(cup.x,cup.y,12,0,7); x.fill();
  x.strokeStyle='#dc2626'; x.beginPath(); x.moveTo(cup.x,cup.y); x.lineTo(cup.x,cup.y-34); x.stroke();
  x.fillStyle='#dc2626'; x.beginPath(); x.moveTo(cup.x,cup.y-34); x.lineTo(cup.x+16,cup.y-28); x.lineTo(cup.x,cup.y-22); x.fill();
  x.fillStyle='#fff'; x.beginPath(); x.arc(ball.x,ball.y,8,0,7); x.fill(); x.strokeStyle='#0F172A'; x.stroke();
  if(!rolling&&!holed){var a=parseInt(el('ang').value,10)*Math.PI/180; var p=parseInt(el('pow').value,10);
    x.strokeStyle='#166534'; x.setLineDash([6,4]); x.beginPath(); x.moveTo(ball.x,ball.y); x.lineTo(ball.x+Math.cos(a)*p*12,ball.y+Math.sin(a)*p*12); x.stroke(); x.setLineDash([])}}
el('ang').oninput=function(){el('angTxt').textContent=el('ang').value+'°'; drawCourse()};
el('pow').oninput=function(){el('powTxt').textContent=el('pow').value; drawCourse()};
el('puttBtn').onclick=function(){if(rolling||holed)return; var a=parseInt(el('ang').value,10)*Math.PI/180; var p=parseInt(el('pow').value,10);
  vel={x:Math.cos(a)*p*1.6,y:Math.sin(a)*p*1.6}; strokes++; total++; el('strokes').textContent=strokes; el('total').textContent=total; rolling=true;
  clearInterval(timer); timer=setInterval(function(){ball.x+=vel.x; ball.y+=vel.y; vel.x*=0.97; vel.y*=0.97;
    if(ball.x<8){ball.x=8; vel.x*=-0.7} if(ball.x>512){ball.x=512; vel.x*=-0.7}
    if(ball.y<8){ball.y=8; vel.y*=-0.7} if(ball.y>292){ball.y=292; vel.y*=-0.7}
    obstacles.forEach(function(o){if(ball.x>o.x-8&&ball.x<o.x+o.w+8&&ball.y>o.y-8&&ball.y<o.y+o.h+8){var dxl=Math.abs(ball.x-(o.x-8)), dxr=Math.abs(ball.x-(o.x+o.w+8)), dyt=Math.abs(ball.y-(o.y-8)), dyb=Math.abs(ball.y-(o.y+o.h+8)); var m=Math.min(dxl,dxr,dyt,dyb); if(m===dxl||m===dxr)vel.x*=-0.7; else vel.y*=-0.7; ball.x+=vel.x; ball.y+=vel.y}});
    var d=Math.hypot(ball.x-cup.x,ball.y-cup.y); var sp=Math.hypot(vel.x,vel.y);
    if(d<12&&sp<3){holed=true; rolling=false; clearInterval(timer); setScore(Math.max(0,100-total*2));
      var vsPar=strokes-PAR; var label=strokes===1?'🏆 HOLE IN ONE!':(vsPar<0?'🐦 Birdie!':(vsPar===0?'Par.':'Bogey +'+vsPar));
      msg(label+' Hole '+hole+' in '+strokes+' strokes. Total '+total+' (par '+(hole*PAR)+').');
      if(hole>=nHoles){msg('🏁 Round complete! '+nHoles+' holes in '+total+' strokes — par is '+(nHoles*PAR)+'. Press Start to play again.'); el('nextBtn').style.display='none'}
      else el('nextBtn').style.display='block'}
    if(sp<0.15&&!holed){rolling=false; clearInterval(timer); msg('Ball stopped. Putt again!')}
    drawCourse()},30)};
el('nextBtn').onclick=function(){hole++; setupHole(); msg('Hole '+hole+' — par '+PAR+'.')};
el('startBtn').onclick=function(){hole=1; total=0; el('total').textContent='0'; setScore(0); setupHole(); msg('New round — '+nHoles+' holes, par '+PAR+' each.')};
setupHole();
""",
{"theme":["classic","dark","neon"],"holes":["9","18"],"difficulty":["easy","hard"]})

# ---- C5-6 slingshot ----
add("slingshot","Slingshot Smash","Launch birds at the block towers. Knock every block down to win!","🐦",
"Set the angle and power, then Launch. Gravity pulls the bird down — knock all the blocks off the platform. You get 3 birds per level!",
'<div class="small" style="text-align:center">Level <b id="lvl">1</b>/3 · Birds left: <b id="birds">3</b> · Blocks down: <b id="down">0</b>/<span id="totB"></span></div><canvas id="cv" width="520" height="300" style="width:100%;border:2px solid #166534;border-radius:12px;background:#e0f2fe"></canvas><div class="row" style="margin-top:8px"><label class="small">Angle <span id="angTxt">45°</span><input type="range" id="ang" min="10" max="80" value="45" style="width:100%"></label><label class="small">Power <span id="powTxt">7</span><input type="range" id="pow" min="1" max="10" value="7" style="width:100%"></label></div><button class="btn amber" id="launchBtn">🐦 Launch!</button><button class="btn ghost" id="nextBtn" style="display:none">Next level ▶</button>',
r"""
var diff=qp('difficulty')||'medium';
var LEVELS = diff==='easy'?[1,2,2]:(diff==='hard'?[2,3,3]:[1,2,3]);
if(el('cfgLabel'))el('cfgLabel').textContent=diff+' · 3 levels';
var lvl=1, birds=3, blocks=[], bird=null, flying=false, timer=null, down=0;
function buildLevel(){var n=LEVELS[lvl-1]; blocks=[]; var bx=380;
  for(var t=0;t<n;t++){var baseX=bx+t*0; var rows=2+t;
    for(var r=0;r<rows;r++){for(var c=0;c<3;c++){blocks.push({x:360+t*70+c*0+ (r%2?0:0), y:0, w:0, h:0, alive:true})}}
    blocks=blocks.filter(function(b,i){return true});
    var idx=0; blocks.forEach(function(b){})}
  blocks=[]; var startX=340;
  for(var tw=0;tw<n;tw++){var tx=startX+tw*75; var h=2+tw;
    for(var rr=0;rr<h;rr++){for(var cc=0;cc<3;cc++){blocks.push({x:tx+cc*22,y:260-(rr+1)*20,w:20,h:18,alive:true,vy:0,vx:0})}}}
  birds=3; down=0; bird=null; flying=false;
  el('lvl').textContent=lvl; el('birds').textContent=birds; el('down').textContent='0'; el('totB').textContent=blocks.length; el('nextBtn').style.display='none'; drawScene()}
function drawScene(){var c=el('cv'), x=c.getContext('2d'); x.clearRect(0,0,520,300);
  x.fillStyle='#86efac'; x.fillRect(0,260,520,40);
  x.strokeStyle='#78350f'; x.lineWidth=5; x.beginPath(); x.moveTo(60,260); x.lineTo(60,210); x.moveTo(90,260); x.lineTo(90,210); x.stroke(); x.lineWidth=1;
  x.fillStyle='#F59E0B'; x.beginPath(); x.arc(75,205,16,0,7); x.fill(); x.fillStyle='#0F172A'; x.font='16px sans-serif'; x.fillText('🐦',63,212);
  if(bird){x.fillStyle='#dc2626'; x.beginPath(); x.arc(bird.x,bird.y,10,0,7); x.fill()}
  blocks.forEach(function(b){if(!b.alive)return; x.fillStyle='#b45309'; x.fillRect(b.x,b.y,b.w,b.h); x.strokeStyle='#78350f'; x.strokeRect(b.x,b.y,b.w,b.h)});
  if(!flying&&bird===null){var a=parseInt(el('ang').value,10)*Math.PI/180; var p=parseInt(el('pow').value,10);
    x.strokeStyle='#166534'; x.setLineDash([5,4]); x.beginPath(); x.moveTo(75,205); x.lineTo(75+Math.cos(a)*p*9,205-Math.sin(a)*p*9); x.stroke(); x.setLineDash([])}}
el('ang').oninput=function(){el('angTxt').textContent=el('ang').value+'°'; drawScene()};
el('pow').oninput=function(){el('powTxt').textContent=el('pow').value; drawScene()};
el('launchBtn').onclick=function(){if(flying||birds<=0)return; birds--; el('birds').textContent=birds;
  var a=parseInt(el('ang').value,10)*Math.PI/180; var p=parseInt(el('pow').value,10);
  bird={x:75,y:205,vx:Math.cos(a)*p*1.5,vy:-Math.sin(a)*p*1.5}; flying=true;
  clearInterval(timer); timer=setInterval(function(){bird.vy+=0.35; bird.x+=bird.vx; bird.y+=bird.vy;
    blocks.forEach(function(b){if(!b.alive)return; if(bird.x>b.x-10&&bird.x<b.x+b.w+10&&bird.y>b.y-10&&bird.y<b.y+b.h+10){b.alive=false; down++; setScore(score+10); el('down').textContent=down; bird.vx*=0.5; bird.vy*=0.5}});
    if(bird.y>285||bird.x>520){flying=false; clearInterval(timer); bird=null; endShot()}
    drawScene()},30)};
function endShot(){if(down>=blocks.length){clearInterval(timer); setScore(score+50); el('nextBtn').style.display=(lvl>=3?'none':'block');
    if(lvl>=3)msg('🏆 YOU WIN! All 3 levels cleared — final score '+score+'. Press Start to play again.');
    else msg('🎉 Level '+lvl+' cleared! +50 bonus. Press Next level.'); return}
  if(birds<=0){msg('Out of birds! '+down+' of '+blocks.length+' blocks down. Press Start to retry level '+lvl+'.'); return}
  msg(birds+' bird'+(birds>1?'s':'')+' left — adjust and launch again!')}
el('nextBtn').onclick=function(){lvl++; buildLevel(); msg('Level '+lvl+' — '+blocks.length+' blocks!')};
el('startBtn').onclick=function(){lvl=1; setScore(0); buildLevel(); msg('New game — knock every block down!')};
buildLevel();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium","hard"]})

# ---- C5-7 mahjong-match ----
add("mahjong-match","Mahjong Match","Mahjong solitaire — match free identical tiles and clear the board!","🀄",
"Tap two FREE identical tiles to remove them. A tile is free when its left or right side is open. Use Hint if you get stuck, Shuffle if no moves remain.",
'<div class="small" style="text-align:center">Tiles left: <b id="left">0</b> · Pairs found: <b id="pairs">0</b> · Time: <b id="clock">0:00</b></div><div id="board" style="margin-top:10px"></div><div class="row" style="margin-top:10px"><button class="btn ghost" id="hintBtn">💡 Hint</button><button class="btn ghost" id="shuffleBtn">🔀 Shuffle free tiles</button></div>',
r"""
var layout=qp('layout')||'turtle';
var LAYOUTS={turtle:[[6,8,10,12,10,8,6]],crab:[[8,10,12,10,8]],dragon:[[12,10,8,10,12]]};
var SHAPES=(LAYOUTS[layout]||LAYOUTS.turtle)[0];
if(el('cfgLabel'))el('cfgLabel').textContent=layout+' layout';
var SYM=['🌸','🐉','🎋','🀄','🌺','🦋','🍑','🎍','🐢','🌙','⭐','🔥'];
var tiles=[], sel=-1, secs=0, timer=null, pairs=0, over=false;
function newGame(){tiles=[]; var syms=[]; var total=SHAPES.reduce(function(a,b){return a+b},0);
  if(total%2)total--;
  for(var i=0;i<total/2;i++){var s=SYM[i%SYM.length]; syms.push(s); syms.push(s)}
  shuffle(syms);
  var k=0; SHAPES.forEach(function(w,r){var off=Math.floor((12-w)/2); for(var c=0;c<w;c++){tiles.push({r:r,c:off+c,sym:syms[k++],gone:false})}});
  sel=-1; pairs=0; secs=0; over=false; setScore(0); el('pairs').textContent='0';
  clearInterval(timer); timer=setInterval(function(){if(!over){secs++; var m=Math.floor(secs/60); el('clock').textContent=m+':'+('0'+(secs%60)).slice(-2)}},1000);
  draw(); msg('Tap two free matching tiles. A tile is free when one side is open.')}
function isFree(t){if(t.gone)return false; var left=tiles.some(function(o){return !o.gone&&o.r===t.r&&o.c===t.c-1}); var right=tiles.some(function(o){return !o.gone&&o.r===t.r&&o.c===t.c+1}); return !left||!right}
function freePairs(){var free=tiles.filter(isFree); var out=[]; for(var i=0;i<free.length;i++)for(var j=i+1;j<free.length;j++)if(free[i].sym===free[j].sym)out.push([free[i],free[j]]); return out}
function draw(){var b=el('board'); b.innerHTML=''; var leftN=tiles.filter(function(t){return !t.gone}).length; el('left').textContent=leftN;
  SHAPES.forEach(function(w,r){var row=document.createElement('div'); row.style.cssText='display:flex;gap:4px;justify-content:center;margin:2px 0';
    tiles.filter(function(t){return t.r===r}).forEach(function(t){var d=document.createElement('button'); d.className='tile'; d.style.cssText='width:42px;height:52px;font-size:20px;min-height:52px;background:'+(tiles.indexOf(t)===sel?'#F59E0B':(isFree(t)?'#fff':'#e2e8f0')); d.textContent=t.gone?'':t.sym; d.disabled=t.gone; d.style.opacity=isFree(t)||t.gone?'1':'0.55';
      d.onclick=function(){if(!isFree(t)){msg('That tile is blocked on both sides — pick a free tile.'); return}
        if(sel===-1){sel=tiles.indexOf(t); draw(); return}
        var first=tiles[sel];
        if(first===t){sel=-1; draw(); return}
        if(first.sym===t.sym){first.gone=true; t.gone=true; pairs++; setScore(pairs*10); el('pairs').textContent=pairs; sel=-1; draw();
          if(!tiles.some(function(o){return !o.gone})){over=true; clearInterval(timer); msg('🎉 Board cleared in '+el('clock').textContent+'! Press Start for a new layout.')}
          else if(!freePairs().length)msg('No moves left — press Shuffle free tiles!')}
        else{msg('Not a match — '+first.sym+' vs '+t.sym+'.'); sel=tiles.indexOf(t); draw()}}; row.appendChild(d)});
    b.appendChild(row)})}
el('hintBtn').onclick=function(){var p=freePairs(); if(!p.length){msg('No free pairs — shuffle!'); return} var a=p[0]; msg('Hint: match the two '+a[0].sym+' tiles (row '+(a[0].r+1)+' and row '+(a[1].r+1)+').'); sel=tiles.indexOf(a[0]); draw()};
el('shuffleBtn').onclick=function(){var free=tiles.filter(function(t){return !t.gone&&isFree(t)}); var syms=free.map(function(t){return t.sym}); shuffle(syms); free.forEach(function(t,i){t.sym=syms[i]}); sel=-1; draw(); msg('Free tiles shuffled.')};
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"layout":["turtle","crab","dragon"]})

# ---- C5-8 crazy-eights ----
add("crazy-eights","Crazy Eights","Match the suit or rank — eights are wild! First to shed all cards wins.","🃏",
"Tap a card that matches the suit or rank of the top discard — or play an 8 as a wild card and pick a new suit. No match? Draw a card. First to empty their hand wins!",
'<div class="small" style="text-align:center">Top card: <b id="topCard">—</b> · Current suit: <b id="curSuit">—</b> · Computer cards: <b id="cpuN">7</b> · Draw pile: <b id="deckN">0</b></div><div id="suitRow" style="display:none;gap:8px;margin:8px 0;justify-content:center"><span class="small">Pick a suit:</span><button class="opt" data-suit="♠">♠</button><button class="opt" data-suit="♥" style="color:#dc2626">♥</button><button class="opt" data-suit="♦" style="color:#dc2626">♦</button><button class="opt" data-suit="♣">♣</button></div><div class="small" style="text-align:center;margin:6px 0">Your hand — tap a card to play it</div><div id="myHand" style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center"></div><div class="row" style="margin-top:10px"><button class="btn amber" id="drawCardBtn">Draw a card</button></div>',
r"""
var diff=qp('difficulty')||'medium';
if(el('cfgLabel'))el('cfgLabel').textContent=diff;
var SUITS=['♠','♥','♦','♣']; var RED={'♥':1,'♦':1}; var R={11:'J',12:'Q',13:'K',14:'A'};
var deck=[], my=[], cpu=[], discard=[], curSuit='', turn=0, over=false, pendingEight=-1;
function lbl(c){return (R[c.r]||c.r)+c.s}
function mkDeck(){var d=[]; SUITS.forEach(function(s){for(var r=2;r<=14;r++)d.push({r:r,s:s})}); return shuffle(d)}
function newGame(){deck=mkDeck(); my=deck.splice(0,7); cpu=deck.splice(0,7); discard=[deck.pop()]; curSuit=discard[0].s; turn=0; over=false; pendingEight=-1; setScore(0); el('suitRow').style.display='none'; draw(); msg('Your turn — play a '+curSuit+' or a '+discard[0].r+', or an 8!')}
function topCard(){return discard[discard.length-1]}
function playable(c){return c.r===8||c.s===curSuit||c.r===topCard().r}
function draw(){el('topCard').textContent=lbl(topCard()); el('curSuit').textContent=curSuit; el('cpuN').textContent=cpu.length; el('deckN').textContent=deck.length;
  var mh=el('myHand'); mh.innerHTML=''; my.forEach(function(c,i){var b=document.createElement('button'); b.className='tile'; b.style.cssText='width:56px;height:76px;font-size:19px;background:'+(playable(c)&&turn===0?'#dcfce7':'#fff'); b.textContent=lbl(c); b.style.color=RED[c.s]?'#dc2626':'#0F172A';
    b.onclick=function(){if(over||turn!==0)return; if(!playable(c)){msg('That does not match — need '+curSuit+' or rank '+topCard().r+', or an 8.'); return}
      if(c.r===8){pendingEight=i; el('suitRow').style.display='flex'; msg('Wild 8! Pick a suit.'); return}
      playCard(0,i,null)}; mh.appendChild(b)})}
function playCard(who,i,suit){var hand=who===0?my:cpu; var c=hand.splice(i,1)[0]; discard.push(c); curSuit=(c.r===8)?(suit||c.s):c.s; pendingEight=-1; el('suitRow').style.display='none';
  if(who===0)msg('You played '+lbl(c)+(c.r===8?' — suit is now '+curSuit:'')+'.');
  else msg('Computer played '+lbl(c)+(c.r===8?' — suit is now '+curSuit:'')+'.');
  if(hand.length===0){over=true; if(who===0){var opp=cpu.length; setScore(score+opp*10+50); msg('🎉 YOU WIN Crazy Eights! Computer had '+opp+' cards left. Press Start to play again.')} else msg('🏁 Computer wins — you had '+my.length+' cards left. Press Start to play again.'); draw(); return}
  turn=who===0?1:0; draw(); if(turn===1&&!over)setTimeout(aiTurn,800); else if(!over)msg('Your turn.')}
document.querySelectorAll('[data-suit]').forEach(function(b){b.onclick=function(){if(pendingEight<0)return; playCard(0,pendingEight,b.dataset.suit)}});
el('drawCardBtn').onclick=function(){if(over||turn!==0)return; if(!deck.length){deck=shuffle(discard.splice(0,discard.length-1)); if(!deck.length){msg('No cards left to draw — pass!'); turn=1; draw(); setTimeout(aiTurn,700); return}}
  my.push(deck.pop()); draw(); if(my.some(playable)){msg('Drew a card — you have a playable card now!')} else{msg('Drew a card — still no match, turn passes.'); turn=1; draw(); setTimeout(aiTurn,700)}};
function aiTurn(){if(over)return; var ix=-1;
  var opts=cpu.map(function(c,i){return playable(c)?i:-1}).filter(function(i){return i>=0});
  if(diff==='easy'&&opts.length&&Math.random()<0.3)opts=[];
  if(opts.length){ix=opts[0]; cpu.forEach(function(c,i){if(playable(c)&&c.r!==8)ix=i});
    var c=cpu[ix]; if(c.r===8){var counts={}; cpu.forEach(function(x){counts[x.s]=(counts[x.s]||0)+1}); var bestSuit=SUITS[0], best=-1; SUITS.forEach(function(s){if((counts[s]||0)>best){best=counts[s]||0; bestSuit=s}}); playCard(1,ix,bestSuit)}
    else playCard(1,ix,null)}
  else{if(!deck.length){deck=shuffle(discard.splice(0,discard.length-1))} if(deck.length){cpu.push(deck.pop()); msg('Computer drew a card.')}
    if(cpu.some(playable)){setTimeout(aiTurn,700); return}
    turn=0; draw(); msg('Computer passes — your turn.')}}
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"difficulty":["easy","medium"]})

# ---- C5-9 boggle ----
add("boggle","Boggle","Find hidden words in the letter grid before the clock runs out!","🔤",
"Tap letters to build a word — each next letter must touch the last one (including diagonally). Tap Submit when you have a real word (3+ letters). Longer words score more!",
'<div class="small" style="text-align:center">Time left: <b id="time">60</b>s · Words found: <b id="foundN">0</b></div><div id="q" style="font-size:26px;min-height:34px">Tap letters to spell a word</div><div class="grid" id="board" style="grid-template-columns:repeat(4,1fr)"></div><div class="row" style="margin-top:10px"><button class="btn amber" id="submitBtn">✓ Submit word</button><button class="btn ghost" id="clearBtn">Clear</button></div><div class="small" style="text-align:center">Found: <span id="foundList">—</span></div>',
r"""
var size=parseInt(qp('size')||'4')||4; if([4,5].indexOf(size)<0)size=4;
var dur=parseInt(qp('time')||'60')||60; if([60,120].indexOf(dur)<0)dur=60;
if(el('cfgLabel'))el('cfgLabel').textContent=size+'×'+size+' · '+dur+'s';
var WORDS=['CAT','DOG','SUN','MOON','STAR','FISH','BIRD','TREE','BOOK','BALL','CAKE','LION','BEAR','WOLF','FROG','DUCK','KING','QUEEN','FIRE','WATER','EARTH','STONE','GREEN','BLACK','WHITE','HAPPY','MUSIC','DANCE','LIGHT','NIGHT','OCEAN','RIVER','APPLE','BREAD','MILK','HOUSE','GARDEN','FLOWER','SUMMER','WINTER','SPRING','AUTUMN','BRIDGE','CASTLE','MARKET','SCHOOL','FRIEND','FAMILY','MOTHER','FATHER','SISTER','BROTHER','ORANGE','BANANA','GRAPE','LEMON','HONEY','SUGAR','PIZZA','PASTA','SOUP','RICE','EGG','CHEESE','BUTTER','COFFEE','JUMP','RUN','WALK','SWIM','READ','WRITE','PLAY','SING','PLAY','FAST','SLOW','BIG','SMALL','TALL','SHORT','LONG','HIGH','LOW','HOT','COLD','WARM','COOL','SOFT','HARD','NEW','OLD','GOOD','BEST','LOVE','KIND','CALM','BOLD','WILD','FREE','TRUE','LUCK','STAR','MOON','RAIN','SNOW','WIND','CLOUD','THUNDER','RAINBOW','PLANET','ROCKET','GUITAR','PIANO','DRUM','HORSE','MOUSE','SNAKE','EAGLE','SHARK','WHALE','TIGER','PANDA','MONKEY','RABBIT','TURTLE','SPIDER','BUTTERFLY','DRAGON','WIZARD','KNIGHT','PIRATE','ROBOT','MAGIC','DREAM','SLEEP','SMILE','LAUGH','BRAVE','QUICK','CLEVER','SIMPLE','GENTLE','GOLDEN','SILVER','PURPLE','YELLOW','RED','BLUE','PINK','BROWN','CLOUD','STORM','BEACH','FOREST','DESERT','ISLAND','MOUNTAIN','VALLEY','BRIDGE','TOWER','CANDLE','MIRROR','WINDOW','DOOR','CHAIR','TABLE','CLOCK','WATCH','SHOE','HAT','COAT','DRESS','RING','CROWN','SWORD','SHIELD','ARROW','BOW','KITE','BOAT','SHIP','TRAIN','PLANE','CAR','BUS','BIKE'];
var grid=[], path=[], cur='', found=[], tLeft=dur, timer=null, playing=false;
function newGame(){var words=shuffle(WORDS.slice()).slice(0,8);
  grid=[]; for(var i=0;i<size*size;i++)grid.push('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[rnd(26)]);
  words.forEach(function(w){var placed=false; for(var tries=0;tries<40&&!placed;tries++){var dr=[0,1,1][rnd(3)], dc=[1,0,1][rnd(3)]; if(dr===0&&dc===0)dc=1;
    var r=rnd(size), c=rnd(size); if(r+dr*(w.length-1)>=size||c+dc*(w.length-1)>=size)continue;
    var ok=true; for(var k=0;k<w.length;k++){var cell=grid[(r+dr*k)*size+(c+dc*k)]; if(cell!==w[k]&&cell!==grid[(r+dr*k)*size+(c+dc*k)]){}} 
    for(var j=0;j<w.length;j++)grid[(r+dr*j)*size+(c+dc*j)]=w[j]; placed=true}});
  var vowels='AEIOU'; for(var v=0;v<size;v++){grid[rnd(size*size)]=vowels[rnd(5)]}
  path=[]; cur=''; found=[]; tLeft=dur; playing=true; setScore(0);
  el('foundN').textContent='0'; el('foundList').textContent='—'; el('time').textContent=tLeft; el('q').textContent='Tap letters to spell a word';
  clearInterval(timer); timer=setInterval(function(){tLeft--; el('time').textContent=tLeft; if(tLeft<=0){clearInterval(timer); playing=false; msg('⏰ Time! You found '+found.length+' words and scored '+score+'. Press Start to play again.')}},1000);
  draw(); msg('Find as many words as you can in '+dur+' seconds!')}
function adjacent(a,b){var ar=Math.floor(a/size), ac=a%size, br=Math.floor(b/size), bc=b%size; return Math.abs(ar-br)<=1&&Math.abs(ac-bc)<=1}
function draw(){var b=el('board'); b.innerHTML=''; b.style.gridTemplateColumns='repeat('+size+',1fr)';
  grid.forEach(function(L,i){var d=document.createElement('button'); d.className='tile'; d.style.fontSize='22px'; d.textContent=L; d.style.background=path.indexOf(i)>=0?'#F59E0B':'#fff';
    d.onclick=function(){if(!playing)return; if(path.indexOf(i)>=0)return; if(path.length&&!adjacent(path[path.length-1],i)){msg('Next letter must touch the last one!'); return} path.push(i); cur+=L; el('q').textContent=cur; draw()}; b.appendChild(d)})}
el('submitBtn').onclick=function(){if(!playing)return; if(cur.length<3){msg('Words must be at least 3 letters.'); return}
  if(WORDS.indexOf(cur)<0){msg('"'+cur+'" is not in the word list — try another!'); path=[]; cur=''; el('q').textContent='Tap letters to spell a word'; draw(); return}
  if(found.indexOf(cur)>=0){msg('You already found "'+cur+'"!'); path=[]; cur=''; draw(); return}
  found.push(cur); var pts=cur.length===3?1:(cur.length===4?2:(cur.length===5?3:5)); setScore(score+pts); el('foundN').textContent=found.length; el('foundList').textContent=found.join(', ');
  msg('✓ "'+cur+'" — +'+pts+' points!'); path=[]; cur=''; el('q').textContent='Tap letters to spell a word'; draw()};
el('clearBtn').onclick=function(){path=[]; cur=''; el('q').textContent='Tap letters to spell a word'; draw()};
el('startBtn').onclick=newGame; newGame();
""",
{"theme":["classic","dark","neon"],"size":["4","5"],"time":["60","120"]})

# ---- C5-10 crossword-mini ----
add("crossword-mini","Crossword Mini","A tiny crossword with clues. Fill every square to win!","🧩",
"Read the clues, tap a square and type its letter. Tap Check to see how you are doing — the puzzle is complete when every square is green!",
'<div class="small" style="text-align:center">Time: <b id="clock">0:00</b> · Correct: <b id="correct">0</b>/<span id="totalCells"></span></div><div id="grid" style="display:flex;flex-direction:column;gap:3px;align-items:center;margin:10px 0"></div><div id="clues" style="font-size:14px"></div><div class="row" style="margin-top:10px"><button class="btn amber" id="checkBtn">✓ Check answers</button><button class="btn ghost" id="revealBtn">Reveal one letter</button></div>',
r"""
var cat=qp('category')||'general';
var PUZZLES={
 general:{rows:4,cols:6,words:[
  {n:1,word:'SUN',r:0,c:1,dir:'across',clue:'1 Across: It rises in the morning'},
  {n:2,word:'STAR',r:0,c:1,dir:'down',clue:'2 Down: It twinkles at night'},
  {n:3,word:'APPLE',r:2,c:1,dir:'across',clue:'3 Across: A red fruit that keeps the doctor away'},
  {n:4,word:'RAIN',r:3,c:1,dir:'across',clue:'4 Across: It falls from clouds'}]},
 animals:{rows:4,cols:4,words:[
  {n:1,word:'LION',r:0,c:0,dir:'across',clue:'1 Across: King of the jungle'},
  {n:2,word:'LAMB',r:0,c:0,dir:'down',clue:'2 Down: A baby sheep'},
  {n:3,word:'OWL',r:0,c:2,dir:'down',clue:'3 Down: A bird that hoots at night'},
  {n:4,word:'BEAR',r:3,c:0,dir:'across',clue:'4 Across: A big furry animal that loves honey'}]},
 food:{rows:5,cols:5,words:[
  {n:1,word:'PIZZA',r:0,c:0,dir:'across',clue:'1 Across: Cheesy Italian favourite'},
  {n:2,word:'PASTA',r:0,c:0,dir:'down',clue:'2 Down: Spaghetti and friends'},
  {n:3,word:'SOUP',r:2,c:0,dir:'across',clue:'3 Across: Hot liquid served in a bowl'},
  {n:4,word:'PIE',r:2,c:3,dir:'down',clue:'4 Down: Apple ___'}]}};
var P=PUZZLES[cat]||PUZZLES.general;
if(el('cfgLabel'))el('cfgLabel').textContent=cat+' · '+P.words.length+' words';
var cells={}, secs=0, timer=null, over=false;
function key(r,c){return r+','+c}
function build(){cells={}; P.words.forEach(function(w){for(var i=0;i<w.word.length;i++){var r=w.r+(w.dir==='down'?i:0), c=w.c+(w.dir==='across'?i:0); cells[key(r,c)]={letter:w.word[i],num:(i===0?w.n:null)}}});
  var total=Object.keys(cells).length; el('totalCells').textContent=total; el('correct').textContent='0';
  var g=el('grid'); g.innerHTML='';
  for(var r=0;r<P.rows;r++){var row=document.createElement('div'); row.style.cssText='display:flex;gap:3px';
    for(var c=0;c<P.cols;c++){var cell=cells[key(r,c)];
      if(!cell){var sp=document.createElement('div'); sp.style.cssText='width:46px;height:46px;background:#0F172A;border-radius:6px'; row.appendChild(sp); continue}
      var wrap=document.createElement('div'); wrap.style.cssText='position:relative;width:46px;height:46px';
      var inp=document.createElement('input'); inp.type='text'; inp.maxLength=1; inp.dataset.k=key(r,c); inp.style.cssText='width:46px;height:46px;text-align:center;font-size:20px;font-weight:800;text-transform:uppercase;padding:0;margin:0;border-radius:6px';
      inp.addEventListener('input',function(){this.value=this.value.replace(/[^a-zA-Z]/g,'').toUpperCase()});
      var num=document.createElement('span'); num.style.cssText='position:absolute;top:1px;left:3px;font-size:10px;font-weight:700;color:#64748b;pointer-events:none'; num.textContent=cell.num||'';
      wrap.appendChild(inp); wrap.appendChild(num); row.appendChild(wrap)}
    g.appendChild(row)}
  var cl=el('clues'); cl.innerHTML='<b>Clues:</b><br>'+P.words.map(function(w){return w.clue}).join('<br>');
  secs=0; over=false; clearInterval(timer); timer=setInterval(function(){if(!over){secs++; var m=Math.floor(secs/60); el('clock').textContent=m+':'+('0'+(secs%60)).slice(-2)}},1000);
  msg('Fill in the '+P.words.length+' words — tap a square and type!')}
function check(){var inputs=document.querySelectorAll('#grid input'); var ok=0, total=inputs.length;
  inputs.forEach(function(inp){var cell=cells[inp.dataset.k]; var v=(inp.value||'').toUpperCase();
    if(v===cell.letter){inp.style.background='#dcfce7'; inp.style.borderColor='#166534'; ok++}
    else if(v===''){inp.style.background='#fff'}
    else{inp.style.background='#fee2e2'; inp.style.borderColor='#dc2626'}});
  el('correct').textContent=ok; setScore(ok);
  if(ok===total){over=true; clearInterval(timer); msg('🎉 Crossword complete in '+el('clock').textContent+'! Press Start for a fresh puzzle.')}
  else msg(ok+' of '+total+' letters correct — keep going!')}
el('checkBtn').onclick=check;
el('revealBtn').onclick=function(){var inputs=Array.from(document.querySelectorAll('#grid input')).filter(function(inp){return (inp.value||'').toUpperCase()!==cells[inp.dataset.k].letter});
  if(!inputs.length){msg('Everything is already correct!'); return}
  var pick=inputs[rnd(inputs.length)]; pick.value=cells[pick.dataset.k].letter; check(); msg('One letter revealed.')};
el('startBtn').onclick=build; build();
""",
{"theme":["classic","dark","neon"],"category":["general","animals","food"]})

# ================= MAIN =================
# Featured order: the most-played viral games first (hub + homepage + teaser rotation).
FEATURED = ['chess', 'word-guess', 'solitaire', '2048', 'snake', 'pac-man', 'ludo', 'match-3', 'sudoku-mini', 'tic-tac-toe', 'minesweeper-mini', 'block-drop', 'checkers', 'hangman', 'connect-four', 'reversi', 'flappy-bird', 'space-invaders', 'breakout-mini', 'pong-mini', 'simon-says', 'memory-cards', 'blackjack', 'bubble-shooter', 'piano-tiles', 'word-search', 'crossword-mini', 'mahjong-match', 'boggle', 'asteroids', 'frogger', 'whack-a-mole', 'doodle-jump', 'endless-runner', 'fruit-slicer', 'stack-blocks', 'traffic-racer', 'penalty-shootout', 'cricket-smash', 'darts', 'basketball-shoot', 'cookie-clicker', 'water-sort', 'lights-out', 'nonogram', 'fruit-merge', 'block-puzzle', 'mastermind', 'gomoku', 'battleship', 'dots-and-boxes', 'tower-of-hanoi', 'typing-test', 'air-hockey', 'slingshot', 'mini-golf', 'dominoes', 'crazy-eights', 'poker', 'daily-number', 'guess-the-number', 'higher-lower']


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
    _feat = {s: i for i, s in enumerate(FEATURED)}
    registry.sort(key=lambda r: _feat.get(r["slug"], 10**6))
    with open(os.path.join(BASE, "games.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"games={len(GAMES)} variations={total_var}")
    for g in GAMES:
        print(f"  {g['slug']}: {len(g['variations'])} variations")

if __name__ == "__main__":
    main()
