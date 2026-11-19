/* FreeCalcNow daily games — date-seeded random.
   Every daily puzzle uses the SAME seed for everyone on the same day:
   the local date (YYYY-MM-DD) hashed to a 32-bit seed, fed into mulberry32.
   So today's puzzle is identical for all players, and tomorrow's is new.
   No server, no sign-up — the seed is the date itself. */
(function(){
  function todayStr(d){
    d = d || new Date();
    var m = d.getMonth()+1, day = d.getDate();
    return d.getFullYear() + "-" + (m<10?"0":"") + m + "-" + (day<10?"0":"") + day;
  }
  function hash(str){
    var h = 2166136261;
    for (var i=0;i<str.length;i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function mulberry32(a){
    return function(){
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function rngFor(dateStr){
    return mulberry32(hash(dateStr || todayStr()));
  }
  function pick(rng, arr){ return arr[Math.floor(rng()*arr.length)]; }
  function shuffle(rng, arr){
    var a = arr.slice();
    for (var i=a.length-1;i>0;i--){ var j=Math.floor(rng()*(i+1)); var t=a[i]; a[i]=a[j]; a[j]=t; }
    return a;
  }
  function int(rng, min, max){ return min + Math.floor(rng()*(max-min+1)); }
  window.FCN_SEED = { todayStr: todayStr, hash: hash, rngFor: rngFor, pick: pick, shuffle: shuffle, int: int };
})();
