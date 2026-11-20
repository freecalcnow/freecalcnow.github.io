/* FreeCalcNow settings — themes, accent colour, light/dark, font size and
   background picture. Everything is saved in the USER'S OWN browser
   (localStorage for choices, IndexedDB for the uploaded picture). No server,
   no sign-up, nothing is uploaded anywhere. */
(function(){
  var KEY='fcn-settings-v1';
  var DEFAULTS={ theme:'default', accent:'#0B1F3A', mode:'auto', font:'medium', bg:'none' };
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
    try{ h.style.setProperty('--accent', s.accent||'#0B1F3A'); }catch(e){}
    var tc=document.querySelector('meta[name="theme-color"]');
    if(tc) tc.setAttribute('content', s.accent||'#0B1F3A');
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
  /* --- Bring-your-own-key: Gemini API key (v9.1) ---
     The key lives ONLY in this browser (localStorage, separate key from the
     theme settings) and is sent ONLY to Google's Gemini API, from the
     browser, when the assistant answers. It is never sent anywhere else,
     never written into the page, never logged, and never shown in full —
     the status line shows only the last 4 characters. A key that does not
     look like a Gemini key (must start with "AIza") is never saved.
     Migration (no-green rule, v9.1): a saved "forest" theme or a green
     accent from before is reset to the default, since green is gone. */
  var KEY_STORE='fcn-gemini-key-v1';
  function keyStatusText(){
    try{
      var k=localStorage.getItem(KEY_STORE)||"";
      if(k) return "Key saved (ends with …"+k.slice(-4)+") — the assistant will answer with AI.";
    }catch(e){}
    return "No key saved.";
  }
  function wireKeyField(){
    var input=document.getElementById('set-key');
    var saveBtn=document.getElementById('set-key-save');
    var removeBtn=document.getElementById('set-key-remove');
    var status=document.getElementById('set-key-status');
    if(!input || !saveBtn || !removeBtn) return;
    function showStatus(t){ if(status) status.textContent=t; }
    showStatus(keyStatusText());
    saveBtn.addEventListener('click', function(){
      var v=(input.value||"").trim();
      if(!/^AIza[0-9A-Za-z_\-]{10,}$/.test(v)){ showStatus("That doesn't look like a Gemini key — it should start with “AIza”. Nothing was saved."); return; }
      try{ localStorage.setItem(KEY_STORE, v); }catch(e){}
      input.value="";
      showStatus("Key saved — the assistant will now answer with AI.");
    });
    removeBtn.addEventListener('click', function(){
      try{ localStorage.removeItem(KEY_STORE); }catch(e){}
      input.value="";
      showStatus("Key removed — the assistant is back to offline mode.");
    });
  }
  function migrateNoGreen(s){
    /* A saved forest theme or green accent predates the no-green rule:
       reset it to the default instead of showing a theme that no longer
       exists. */
    if(s.theme==='forest'){ s.theme='default'; }
    if(typeof s.accent==='string' && /^#(166534|16a34a|059669|15803d|22c55e|10b981)/i.test(s.accent.replace(/\s/g,''))){ s.accent='#0B1F3A'; }
    return s;
  }
  window.FCN_SETTINGS={ load:load, save:save, apply:apply, DEFAULTS:DEFAULTS,
    saveBgImage:saveBgImage, clearBgImage:clearBgImage };
  apply();
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", wireKeyField); else wireKeyField();
  /* Migrate a saved forest/green choice once, then save the cleaned set. */
  try{ var _s=load(); var _ot=_s.theme, _oa=_s.accent; migrateNoGreen(_s); if(_s.theme!==_ot || _s.accent!==_oa){ save(_s); apply(_s); } }catch(e){}
})();
