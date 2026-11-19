/* FreeCalcNow favourites — heart button on every tool + game page, and the
   /favourites/ page. localStorage only (fcn-favs-v1). No server, no sign-up. */
(function(){
  var KEY='fcn-favs-v1';
  function list(){ try{ return JSON.parse(localStorage.getItem(KEY)||'[]')||[]; }catch(e){ return []; } }
  function save(l){ try{ localStorage.setItem(KEY, JSON.stringify(l)); }catch(e){} }
  function isFav(slug){ var l=list(); for(var i=0;i<l.length;i++) if(l[i].slug===slug) return true; return false; }
  function toggle(item){ var l=list(); for(var i=0;i<l.length;i++) if(l[i].slug===item.slug){ l.splice(i,1); save(l); return false; }
    l.push(item); save(l); return true; }
  function remove(slug){ var l=list(), out=[]; for(var i=0;i<l.length;i++) if(l[i].slug!==slug) out.push(l[i]); save(out); }
  function pageItem(){
    var p=location.pathname;
    var m=p.match(/^\/games\/([^\/]+)\/$/);
    if(m){ var h1=document.querySelector('h1');
      return { type:'game', slug:'games/'+m[1], name:(h1?h1.textContent:'Game').trim(), url:p }; }
    if(document.querySelector('.share-row')){
      var h=document.querySelector('h1'); var slug=p.replace(/^\/|\/$/g,'');
      if(!slug) return null;
      return { type:'tool', slug:slug, name:(h?h.textContent:'Calculator').trim(), url:p };
    }
    return null;
  }
  function renderFavsPage(){
    var host=document.getElementById('fav-list'); if(!host) return;
    var l=list();
    var cnt=document.getElementById('fav-count');
    if(cnt) cnt.textContent=l.length? (l.length+' saved') : '';
    var empty=document.getElementById('fav-empty');
    if(!l.length){ host.innerHTML=''; if(empty) empty.hidden=false; return; }
    if(empty) empty.hidden=true;
    var html='';
    l.forEach(function(f){
      html+='<div class="rel-card" style="display:flex;gap:10px;align-items:center">'
        +'<span style="font-size:22px">'+(f.type==='game'?'🎮':'🧮')+'</span>'
        +'<div style="flex:1;min-width:0"><a href="'+f.url+'" style="font-weight:800">'+escapeHtml(f.name)+'</a>'
        +'<p class="small muted" style="margin:2px 0 0">'+(f.type==='game'?'Game':'Calculator')+' · '+escapeHtml(f.url)+'</p></div>'
        +'<button type="button" class="btn btn-ghost fav-remove" data-slug="'+escapeHtml(f.slug)+'">Remove</button></div>';
    });
    host.innerHTML=html;
    host.querySelectorAll('.fav-remove').forEach(function(b){
      b.addEventListener('click', function(){ remove(b.getAttribute('data-slug')); renderFavsPage(); });
    });
  }
  function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function inject(){
    var item=pageItem();
    if(item){
      var btn=document.createElement('button');
      btn.type='button'; btn.className='fav-btn';
      btn.style.cssText='padding:10px 14px;font-size:15px;font-weight:800;border:2px solid #e2e8f0;border-radius:10px;background:#fff;cursor:pointer;color:#0F172A';
      function paint(){ var f=isFav(item.slug);
        var lab=function(k,fb){ return (window.FCN_I18N?FCN_I18N.t(k):fb); };
        btn.innerHTML=(f?'♥ ':'♡ ')+(f?lab('btn.favourited','Favourited'):lab('btn.favourite','Favourite'));
        btn.style.borderColor=f?'#dc2626':'#e2e8f0';
        btn.style.color=f?'#dc2626':'#0F172A';
        btn.setAttribute('aria-pressed', f?'true':'false'); }
      paint();
      btn.addEventListener('click', function(){
        var now=toggle(item); paint();
        if(now){ var old=btn.innerHTML; btn.innerHTML='♥ Saved — see <a href="/favourites/" style="color:#dc2626">Favourites</a>';
          setTimeout(paint, 2200); }
      });
      var sr=document.querySelector('.share-row');
      if(sr){ sr.appendChild(btn); }
      else { var hd=document.querySelector('header');
        if(hd){ btn.style.marginLeft='8px'; btn.style.padding='6px 10px'; btn.style.fontSize='14px'; hd.appendChild(btn); } }
    }
    renderFavsPage();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', inject);
  else inject();
  window.FCN_FAVS={ list:list, isFav:isFav, toggle:toggle, remove:remove, render:renderFavsPage };
})();
