/* FreeCalcNow games — bots + how-to (v8).
   Bots fill every game so matches never feel empty. They have player-like
   names and avatars and play alongside you. There is NO fake "real users
   online" number anywhere: real online multiplayer needs a server, which
   the free static site does not have yet. The panel says so plainly.
   How-to rule (owner, 20 Nov 2026): the how-to panel shows ONLY the first
   time a game is played on this device (localStorage fcn-howto-seen-<slug>).
   Later visits show only a small "How to play" button to reopen it. */
(function () {
  "use strict";
  var NAMES = ["Ayesha", "Bilal", "Zara", "Omar", "Liam", "Sofia", "Arslan", "Mina",
    "Hassan", "Noor", "Ethan", "Mia", "Ali", "Sara", "Danish", "Hina", "Lucas",
    "Emma", "Usman", "Amina", "Noah", "Ava", "Hamza", "Fatima", "Leo", "Ivy",
    "Kabir", "Anaya", "Rayan", "Meera", "Felix", "Nina", "Yusuf", "Layla",
    "Owen", "Ruby", "Imran", "Tara", "Jay", "Elena", "Ravi", "Dina"];
  var COLORS = ["#dc2626", "#ea580c", "#d97706", "#92400E", "#0B1F3A", "#0369A1",
    "#0891b2", "#2563eb", "#4f46e5", "#7c3aed", "#db2777", "#be185d", "#b45309", "#4338ca"];

  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) >>> 0; } return h; }
  function rng(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  function initials(name) { var p = name.split(/[\s-]+/); return (p[0][0] + (p[1] ? p[1][0] : "")).toUpperCase(); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  function makeBots(slug, count) {
    var r = rng(hash(slug) * 2654435761 + 97);
    var used = {}, bots = [], i = 0, guard = 0;
    while (bots.length < count && guard++ < 500) {
      var name = NAMES[Math.floor(r() * NAMES.length)];
      if (used[name]) continue;
      used[name] = 1;
      bots.push({ name: name, color: COLORS[Math.floor(r() * COLORS.length)],
        score: Math.floor(r() * 60) + 5, games: Math.floor(r() * 40) + 1 });
      i++;
    }
    return bots;
  }

  function avatar(b, size) {
    return '<span class="fcn-av" style="background:' + b.color + ';width:' + size + 'px;height:' + size + 'px;line-height:' + size + 'px">' + initials(b.name) + '</span>';
  }

  /* Players panel: "You" + 15 bots, scores tick live. mountEl gets the panel. */
  function renderPlayers(mountEl, slug, yourScore) {
    if (!mountEl) return;
    var bots = makeBots(slug, 15);
    var you = { name: "You", color: "#0B1F3A", score: yourScore || 0, games: 1 };
    var all = bots.concat([you]);
    function row(p, rank) {
      return '<li class="fcn-pl-row' + (p.name === "You" ? " fcn-you" : "") + '">' +
        '<span class="fcn-pl-rank">' + rank + '</span>' + avatar(p, 30) +
        '<span class="fcn-pl-name">' + p.name + (p.name === "You" ? " (you)" : "") + '</span>' +
        '<span class="fcn-pl-games">' + p.games + ' games</span>' +
        '<b class="fcn-pl-score">' + p.score + '</b></li>';
    }
    function draw() {
      var sorted = all.slice().sort(function (a, b) { return b.score - a.score; });
      var top = sorted.slice(0, 5);
      var youIdx = sorted.findIndex(function (p) { return p.name === "You"; });
      if (youIdx >= 5) top.push(sorted[youIdx]);
      mountEl.innerHTML =
        '<div class="fcn-pl-head"><b>Players in this match</b><span class="fcn-pl-note">16 players · bots play alongside you</span></div>' +
        '<ul class="fcn-pl-list">' + top.map(function (p) { return row(p, sorted.indexOf(p) + 1); }).join("") + '</ul>' +
        '<p class="fcn-pl-foot">Bot players keep every game lively. Real online multiplayer (playing live with real people) needs a server — it arrives when the site grows.</p>';
    }
    draw();
    var tick = 0;
    setInterval(function () {
      tick++;
      var b = bots[Math.floor(Math.random() * bots.length)];
      b.score += 1 + Math.floor(Math.random() * 3);
      if (tick % 4 === 0) { var b2 = bots[Math.floor(Math.random() * bots.length)]; b2.games += 1; }
      draw();
    }, 2800);
  }

  /* Top-players strip for featured games: top 3 bot names + scores. */
  function renderTopPlayers(mountEl, slug) {
    if (!mountEl) return;
    var bots = makeBots(slug, 15).sort(function (a, b) { return b.score - a.score; }).slice(0, 3);
    mountEl.innerHTML = '<span class="fcn-tp-label">Top players:</span> ' + bots.map(function (b, i) {
      return '<span class="fcn-tp">' + (i + 1) + '. ' + avatar(b, 22) + ' ' + b.name + ' · <b>' + b.score + '</b></span>';
    }).join("");
  }

  /* How-to: show ONLY the first time per game per device. */
  function initHowTo(slug) {
    var key = "fcn-howto-seen-" + slug;
    var panel = document.getElementById("fcn-howto");
    var btn = document.getElementById("fcn-howto-btn");
    if (!panel || !btn) return;
    var seen = read(key);
    if (!seen) {
      panel.hidden = false;
      btn.hidden = true;
      store(key, "1");
    } else {
      panel.hidden = true;
      btn.hidden = false;
    }
    btn.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      btn.textContent = panel.hidden ? "How to play" : "Hide how to play";
    });
  }

  window.FCNBots = { renderPlayers: renderPlayers, renderTopPlayers: renderTopPlayers, initHowTo: initHowTo };

  document.addEventListener("DOMContentLoaded", function () {
    var tops = document.querySelectorAll("[data-fcn-topplayers]");
    for (var i = 0; i < tops.length; i++) renderTopPlayers(tops[i], tops[i].getAttribute("data-fcn-topplayers"));
    var slug = (document.body && document.body.getAttribute("data-fcn-game")) || "";
    if (!slug) return;
    var mount = document.querySelector("[data-fcn-players]");
    if (mount) {
      var best = 0;
      try { best = parseInt(read("fcn_best_" + slug) || "0") || 0; } catch (e) {}
      renderPlayers(mount, slug, best);
    }
    initHowTo(slug);
  });
})();

/* v9.8 — left side panel (owner 21 Nov 2026): the hamburger opens a left
   drawer, not a full-screen menu. Games section (own icon), Tools section
   (own icon), EVERY category with its own icon + honest count from the
   manifest. Built at runtime so the 15,555 v9.4-tree HTML files are never
   edited; the panel is idempotent (data-fcn-panel marker). */
(function(){
  "use strict";
  var ICONS = {
  'home': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/></svg>',
  'calculator': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h2M13 11h2M9 15h2M13 15h2"/></svg>',
  'gamepad': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 7h10a5 5 0 0 1 5 5v2a3 3 0 0 1-5.4 1.8L15 15H9l-1.6 1.8A3 3 0 0 1 2 14v-2a5 5 0 0 1 5-5Z"/><path d="M8 11v3M6.5 12.5h3"/><path d="M16 11h.01M17.5 13h.01"/></svg>',
  'dice': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="8.5" cy="8.5" r="1" fill="currentColor" stroke="none"/><circle cx="15.5" cy="15.5" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="15.5" cy="8.5" r="1" fill="currentColor" stroke="none"/><circle cx="8.5" cy="15.5" r="1" fill="currentColor" stroke="none"/></svg>',
  'calendar': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  'chat': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4V5Z"/><path d="M8 9h8M8 13h5"/></svg>',
  'info': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>',
  'heart': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.3-7-9.5A4 4 0 0 1 12 7a4 4 0 0 1 7 3.5C19 15.7 12 20 12 20Z"/></svg>',
  'gear': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/></svg>',
  'dollar': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 6.5c0-1.9-2.2-3-5-3s-5 1.1-5 3 1.8 2.6 5 3.2 5 1.4 5 3.3-2.2 3-5 3-5-1.1-5-3"/></svg>',
  'activity': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  'sigma': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 5H7l6 7-6 7h10"/></svg>',
  'ruler': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17L17 3l4 4L7 21l-4-4Z"/><path d="M8 16l1.5 1.5M11 13l1.5 1.5M14 10l1.5 1.5"/></svg>',
  'clock': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  'trophy': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4h8v5a4 4 0 0 1-8 0V4Z"/><path d="M8 5H4a4 4 0 0 0 4 5M16 5h4a4 4 0 0 1-4 5M12 13v4M8 21h8M10 17h4"/></svg>',
  'chart': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M8 17v-5M12 17V7M16 17v-3"/></svg>',
  'atom': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2" fill="currentColor" stroke="none"/><ellipse cx="12" cy="12" rx="9" ry="3.5"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(120 12 12)"/></svg>',
  'flask': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6M10 3v6L4.5 18a2 2 0 0 0 1.8 3h11.4a2 2 0 0 0 1.8-3L14 9V3"/><path d="M7.5 14h9"/></svg>',
  'leaf': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19c0-9 5-14 14-14-1 8-5 13-14 14Z"/><path d="M5 19c3-5 7-9 11-11"/></svg>',
  'apple': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7c-1-2-3-3-5-2-2.5 1.2-3.5 4.5-2.5 8 .8 2.8 3 5 7.5 5s6.7-2.2 7.5-5c1-3.5 0-6.8-2.5-8-2-1-4 0-5 2Z"/><path d="M12 7c0-2 1-3.5 3-4"/></svg>',
  'globe': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z"/></svg>',
  'swap': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 4v13M7 4L3 8M7 4l4 4"/><path d="M17 20V7M17 20l4-4M17 20l-4-4"/></svg>',
  'grid': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/></svg>'
  };
  var CATS = [
  ['biology','Biology',53,'leaf'],
  ['chemistry','Chemistry',63,'flask'],
  ['construction','Construction',128,'ruler'],
  ['conversion','Conversion',13789,'swap'],
  ['ecology','Ecology',41,'globe'],
  ['everyday','Everyday life',149,'clock'],
  ['finance','Finance',332,'dollar'],
  ['food','Food',79,'apple'],
  ['health','Health',159,'activity'],
  ['math','Math',149,'sigma'],
  ['other','Other',107,'grid'],
  ['physics','Physics',140,'atom'],
  ['sports','Sports',104,'trophy'],
  ['statistics','Statistics',83,'chart']
  ];
  var NAV_ICONS = {'/':'home','/tools/':'calculator','/games/':'gamepad',
    '/ask/':'chat','/about/':'info','/favourites/':'heart','/settings/':'gear'};
  function svg(k){ return ICONS[k] || ''; }
  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function item(href, icon, label, small){
    return '<a class="nav-item" href="'+href+'"><span class="nav-ico" aria-hidden="true">'+svg(icon)+'</span><span>'+esc(label)+'</span>'+(small?'<small>'+esc(small)+'</small>':'')+'</a>';
  }
  function buildCats(cats){
    var rows = cats.map(function(c){
      return item('/category/'+c[0]+'/', c[3], c[1],
        Number(c[2]).toLocaleString('en-US') + (c[2]===1?' tool':' tools'));
    }).join('');
    return '<div class="nav-sec nav-panel-only"><p class="nav-head"><span class="nav-ico" aria-hidden="true">'+svg('calculator')+'</span>Tools</p>'
      + item('/tools/','calculator','All tools', '15,376 tools') + rows + '</div>';
  }
  function buildGames(){
    return '<div class="nav-sec nav-panel-only"><p class="nav-head"><span class="nav-ico" aria-hidden="true">'+svg('gamepad')+'</span>Games</p>'
      + item('/games/','gamepad','Games','164 games')
      + item('/games/world/','dice','Games World','100 arcade games')
      + item('/daily-number/','calendar','Daily Number','New puzzle daily') + '</div>';
  }
  function enhance(headerSel){
    var header = document.querySelector(headerSel);
    if(!header) return false;
    var nav = header.querySelector('#site-nav');
    if(!nav || nav.getAttribute('data-fcn-panel')) return false;
    nav.setAttribute('data-fcn-panel','1');
    var links = nav.querySelectorAll(':scope > a[href]');
    for(var i=0;i<links.length;i++){
      var a = links[i];
      if(a.classList.contains('nav-dl')) continue;
      var key = NAV_ICONS[a.getAttribute('href')];
      if(!key || a.querySelector('.nav-ico')) continue;
      var sp = document.createElement('span');
      sp.className = 'nav-ico'; sp.setAttribute('aria-hidden','true');
      sp.innerHTML = svg(key);
      a.insertBefore(sp, a.firstChild);
    }
    var dl = nav.querySelector('a.nav-dl');
    var frag = document.createElement('div');
    frag.innerHTML = buildGames() + buildCats(CATS);
    while(frag.firstChild) nav.insertBefore(frag.firstChild, dl);
    if(window.fetch){
      fetch('/assets/manifest-data.json').then(function(r){ return r.json(); }).then(function(m){
        try{
          var byId = {}; (m.categories||[]).forEach(function(c){ byId[c.id]=c.count; });
          var changed = false;
          CATS.forEach(function(c){ if(byId[c[0]]!=null && byId[c[0]]!==c[2]){ c[2]=byId[c[0]]; changed=true; } });
          if(!changed) return;
          var secs = nav.querySelectorAll('.nav-sec');
          var toolsSec = null;
          for(var j=0;j<secs.length;j++){ if(secs[j].textContent.indexOf('All tools')>=0) toolsSec = secs[j]; }
          if(!toolsSec) return;
          var tmp = document.createElement('div');
          tmp.innerHTML = buildCats(CATS);
          toolsSec.parentNode.replaceChild(tmp.firstChild, toolsSec);
        }catch(e){}
      }).catch(function(){});
    }
    var bd = document.createElement('div');
    bd.className = 'menu-backdrop'; bd.setAttribute('aria-hidden','true');
    bd.addEventListener('click', function(){
      header.classList.remove('menu-open');
      document.body.classList.remove('menu-open');
      var btn = header.querySelector('.menu-btn');
      if(btn) btn.setAttribute('aria-expanded','false');
    });
    header.appendChild(bd);
    return true;
  }
  function ready(fn){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fn); else fn(); }
  ready(function(){ enhance('.game-head'); });
})();

/* v9.8 — "Download" label on game-head pages: the game pages do not load
   i18n.js, so the Download buttons are rewritten here at runtime (the two
   spans in the header + in the nav), from the static old label text. */
(function(){
  "use strict";
  function ready(fn){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fn); else fn(); }
  ready(function(){
    var header = document.querySelector('.game-head');
    if(!header) return;
    header.querySelectorAll('.dl-btn').forEach(function(btn){
      var spans = btn.querySelectorAll('span');
      var last = spans[spans.length-1];
      if(last) last.textContent = 'Download';
    });
  });
})();
