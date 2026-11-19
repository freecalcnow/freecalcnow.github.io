/* FreeCalcNow daily.js — ONE shared streak for all daily games.
   Daily Number, Word Guess (daily) and Sudoku Mini (daily) all record here,
   so one streak covers every daily puzzle. No account, localStorage only.
   Key: fcn_daily_streak_v2 = {n, last:"YYYY-MM-DD", days:{gameId:"YYYY-MM-DD"}} */
(function(){
  "use strict";
  var KEY = "fcn_daily_streak_v2";
  function todayStr(){
    try{ return new Date().toISOString().slice(0,10); }catch(e){ return "2026-11-19"; }
  }
  function load(){
    try{
      var s = JSON.parse(localStorage.getItem(KEY) || "null");
      if(s && typeof s.n === "number"){ s.days = s.days || {}; return s; }
    }catch(e){}
    /* Migrate the old Daily Number-only streak ({n}) once. */
    try{
      var old = JSON.parse(localStorage.getItem("fcn_daily_streak") || "null");
      if(old && typeof old.n === "number" && old.n > 0){
        return {n: old.n, last: todayStr(), days: {"daily-number": todayStr()}};
      }
    }catch(e){}
    return {n: 0, last: null, days: {}};
  }
  function save(st){
    try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){}
  }
  function yesterdayStr(){
    try{
      var d = new Date(); d.setUTCDate(d.getUTCDate() - 1);
      return d.toISOString().slice(0,10);
    }catch(e){ return ""; }
  }
  /* Record that this game was completed today. Counts once per game per day.
     Returns the streak count after recording. */
  function record(gameId){
    var st = load(), t = todayStr();
    if(st.days[gameId] === t) return st.n; /* already counted today */
    if(st.last === yesterdayStr()) st.n += 1;
    else if(st.last !== t) st.n = 1;
    st.days[gameId] = t;
    st.last = t;
    save(st);
    return st.n;
  }
  function get(){
    var st = load();
    return {n: st.n, last: st.last};
  }
  function emojiRows(rows){
    /* rows: arrays of "g" (green), "a" (amber), "x" (grey) */
    var map = {g: "\u{1F7E9}", a: "\u{1F7E8}", x: "\u2B1C"};
    return rows.map(function(r){
      return r.map(function(c){ return map[c] || map.x; }).join("");
    }).join("\n");
  }
  function shareText(opts){
    /* opts: {game, date, rows, tries, maxTries, won, streak} */
    var lines = [];
    lines.push("FreeCalcNow " + opts.game + " — " + (opts.date || todayStr()));
    if(opts.rows && opts.rows.length) lines.push(emojiRows(opts.rows));
    if(opts.won) lines.push("Solved in " + opts.tries + "/" + opts.maxTries + " tries");
    else lines.push("Played today — try it yourself");
    if(opts.streak) lines.push("\u{1F525} " + opts.streak + "-day streak");
    lines.push("Play: " + opts.url);
    return lines.join("\n");
  }
  function copyText(text, done){
    function fallback(){
      try{
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        document.execCommand("copy"); document.body.removeChild(ta);
        if(done) done(true);
      }catch(e){ if(done) done(false); }
    }
    if(navigator.share){
      navigator.share({text: text}).then(function(){ if(done) done(true); }).catch(function(){ fallback(); });
    } else if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(function(){ if(done) done(true); }).catch(function(){ fallback(); });
    } else fallback();
  }
  window.FCN_DAILY = {
    todayStr: todayStr,
    record: record,
    get: get,
    emojiRows: emojiRows,
    shareText: shareText,
    copyText: copyText
  };
})();
