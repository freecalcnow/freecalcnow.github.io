/* FreeCalcNow service worker — cache-first shell for instant repeat loads.
   Caches the homepage shell + shared assets on first visit; tool and game
   pages are cached as they are visited (network-first, so answers are never
   stale). No push, no background sync, no tracking. */
var VERSION = "fcn-v7.3";
var SHELL = [
  "/",
  "/assets/style.css",
  "/assets/engine.js",
  "/assets/site.js",
  "/assets/assistant.js",
  "/assets/daily.js",
  "/icon-192.png",
  "/icon-512.png",
  "/og-image.png",
  "/manifest.json"
];
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
