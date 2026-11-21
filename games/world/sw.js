const CACHE = 'freecalcnow-games-world-v2';
const GAME_ART = Array.from({length:100}, (_,i) => `./assets/games/${String(i+1).padStart(3,'0')}.svg`);
const FILES = ['./','./index.html','./styles.css','./app.js','./manifest.webmanifest','./assets/favicon.svg',...GAME_ART];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())));
// v9.7: activate() deletes ONLY old Games-World caches. The original
// deleted EVERY origin cache key except its own — that would have wiped
// the main site's fcn-v9.6 cache the first time a visitor opened the hub.
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE && key.startsWith('freecalcnow-games-')).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok && new URL(event.request.url).origin === self.location.origin) {
      const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(event.request, copy));
    }
    return response;
  }).catch(() => event.request.mode === 'navigate' ? caches.match('./index.html') : Promise.reject(new Error('offline')))));
});
