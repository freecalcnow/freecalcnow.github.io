/* FreeCalcNow service worker — cache-first shell for instant repeat loads.
   Caches the homepage shell + shared assets on first visit; tool and game
   pages are cached as they are visited (network-first, so answers are never
   stale). No push, no background sync, no tracking. */
var VERSION = "fcn-v9.1";
var SHELL = [
  "/",
  "/assets/style.css",
  "/assets/engine.js",
  "/assets/site.js",
  "/assets/assistant.js",
  "/assets/i18n.js",
  "/assets/bots.js",
  "/assets/games-v8.css",
  "/assets/daily.js",
  "/assets/logo-144.png",
  "/icon-192-v8.1.png",
  "/icon-192.png",
  "/icon-512-v8.1.png",
  "/icon-512.png",
  "/apple-touch-icon-v8.1.png",
  "/favicon-v8.1.ico",
  "/favicon.ico",
  "/og-image.png",
  "/manifest.json",
  "/assets/manifest-data.json"
];
/* v8: fully automatic updates (owner correction 20 Nov 2026) — NO banner,
   NO tap, NO reload. skipWaiting() in install + clients.claim() on activate
   make the new version take over on the next launch/navigation, without ever
   interrupting the open page mid-game or mid-calculation. */
self.addEventListener("install", function(e){
  e.waitUntil(
    caches.open(VERSION).then(function(c){ return c.addAll(SHELL); }).catch(function(){})
  );
  self.skipWaiting();
});
self.addEventListener("activate", function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.filter(function(k){ return k !== VERSION; }).map(function(k){ return caches.delete(k); }));
    })
  );
  self.clients.claim();
});
self.addEventListener("fetch", function(e){
  if(e.request.method !== "GET") return;
  var url = new URL(e.request.url);
  if(url.origin !== location.origin) return; /* never cache third-party (rates API etc.) */
  if(url.pathname === "/" || url.pathname.indexOf("/assets/") === 0){
    e.respondWith(
      caches.match(e.request).then(function(hit){
        return hit || fetch(e.request).then(function(res){
          var copy = res.clone();
          caches.open(VERSION).then(function(c){ c.put(e.request, copy); }).catch(function(){});
          return res;
        });
      })
    );
  } else {
    e.respondWith(
      fetch(e.request).then(function(res){
        if(res && res.ok){
          var copy = res.clone();
          caches.open(VERSION).then(function(c){ c.put(e.request, copy); }).catch(function(){});
        }
        return res;
      }).catch(function(){ return caches.match(e.request); })
    );
  }
});

self.addEventListener("notificationclick", function(e){
  e.notification.close();
  var url = (e.notification.data && e.notification.data.url) || "/games/daily-number/";
  e.waitUntil(clients.matchAll({type:"window", includeUncontrolled:true}).then(function(list){
    for(var i=0;i<list.length;i++){ if("focus" in list[i]) return list[i].focus(); }
    if(clients.openWindow) return clients.openWindow(url);
  }));
});
