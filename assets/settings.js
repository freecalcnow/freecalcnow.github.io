/* FreeCalcNow settings — themes, accent colour, light/dark, font size and
   background picture. Everything is saved in the USER'S OWN browser
   (localStorage for choices, IndexedDB for the uploaded picture). No server,
   no sign-up, nothing is uploaded anywhere. */
(function(){
  var KEY='fcn-settings-v1';
  var DEFAULTS={ theme:'default', accent:'#166534', mode:'auto', font:'medium', bg:'none' };
  function load(){ try{ var s=JSON.parse(localStorage.getItem(KEY)||'{}')||{};
      var out={}; for(var k in DEFAULTS) out[k]=(s[k]!==undefined&&s[k]!==null)?s[k]:DEFAULTS[k]; return out; }
    catch(e){ var o={}; for(var k2 in DEFAULTS) o[k2]=DEFAULTS[k2]; return o; } }
  function save(s){ try{ localStorage.setItem(KEY, JSON.stringify(s)); }catch(e){} }
  function apply(s){
    s=s||load();
    var h=document.documentElement;
    h.setAttribute('data-fcn-theme', s.theme||'default');
    h.setAttribute('data-fcn-mode', s.mode||'auto');
    h.setAttribute('data-fcn-font', s.font||'medium');
    h.setAttribute('data-fcn-bg', s.bg||'none');
    try{ h.style.setProperty('--accent', s.accent||'#166534'); }catch(e){}
    var tc=document.querySelector('meta[name="theme-color"]');
    if(tc) tc.setAttribute('content', s.accent||'#166534');
    loadBgImage();
  }
  /* --- Custom background picture in IndexedDB (data URL, downscaled) --- */
  var DB='fcn-settings', STORE='kv';
  function openDb(ok, fail){
    try{
      var req=indexedDB.open(DB, 1);
      req.onupgradeneeded=function(){ try{ req.result.createObjectStore(STORE); }catch(e){} };
      req.onsuccess=function(){ ok(req.result); };
      req.onerror=function(){ if(fail) fail(); };
    }catch(e){ if(fail) fail(); }
  }
  function loadBgImage(){
    openDb(function(db){
      try{
        var tx=db.transaction(STORE, 'readonly');
        var req=tx.objectStore(STORE).get('bg-image');
        req.onsuccess=function(){
          var url=req.result;
          if(url){ document.body.classList.add('fcn-custom-bg');
            document.body.style.backgroundImage='url('+url+')'; }
        };
      }catch(e){}
    });
  }
  function saveBgImage(dataUrl, cb){
    openDb(function(db){
      try{
        var tx=db.transaction(STORE, 'readwrite');
        tx.objectStore(STORE).put(dataUrl, 'bg-image');
        tx.oncomplete=function(){ if(cb) cb(true); };
        tx.onerror=function(){ if(cb) cb(false); };
      }catch(e){ if(cb) cb(false); }
    }, function(){ if(cb) cb(false); });
  }
  function clearBgImage(cb){
    openDb(function(db){
      try{
        var tx=db.transaction(STORE, 'readwrite');
        tx.objectStore(STORE).delete('bg-image');
        tx.oncomplete=function(){ document.body.classList.remove('fcn-custom-bg');
          document.body.style.backgroundImage=''; if(cb) cb(true); };
        tx.onerror=function(){ if(cb) cb(false); };
      }catch(e){ if(cb) cb(false); }
    }, function(){ if(cb) cb(false); });
  }
  window.FCN_SETTINGS={ load:load, save:save, apply:apply, DEFAULTS:DEFAULTS,
    saveBgImage:saveBgImage, clearBgImage:clearBgImage };
  apply();
})();
