/* FreeCalcNow install — captures the browser's install prompt
   (beforeinstallprompt) so the Download page can start a REAL PWA install.
   No fake downloads: if the browser offers no prompt (iOS, already installed),
   the Download page shows the honest manual steps instead. */
(function(){
  var deferred=null, installed=false;
  window.addEventListener('beforeinstallprompt', function(e){
    e.preventDefault();
    deferred=e;
    try{ document.documentElement.classList.add('fcn-installable'); }catch(err){}
    document.querySelectorAll('[data-install-btn]').forEach(function(x){ x.disabled=false; });
  });
  window.addEventListener('appinstalled', function(){ installed=true; deferred=null; });
  function canPrompt(){ return !!deferred && !installed; }
  function isIOS(){ return /iphone|ipad|ipod/i.test(navigator.userAgent||'') && !window.MSStream; }
  function isStandalone(){
    try{ if(window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) return true; }catch(e){}
    return window.navigator.standalone===true;
  }
  function promptInstall(cb){
    if(!deferred){ if(cb) cb({ ok:false, reason: isStandalone()?'installed':(isIOS()?'ios':'unavailable') }); return; }
    var p=deferred; deferred=null;
    try{
      var pr=p.prompt();
      if(pr && pr.then) pr.then(function(choice){ if(cb) cb({ ok:true, outcome:(choice&&choice.outcome)||'unknown' }); });
      else if(cb) cb({ ok:true, outcome:'unknown' });
    }catch(e){ if(cb) cb({ ok:false, reason:'error' }); }
  }
  window.FCN_INSTALL={ canPrompt:canPrompt, promptInstall:promptInstall, isIOS:isIOS, isStandalone:isStandalone };
})();
