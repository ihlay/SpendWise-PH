var CACHE_NAME = 'spendwise-static-v2';

var STATIC_ASSETS = [
    '/static/css/spendwise.css',
];

self.addEventListener('install', function (e) {
    e.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', function (e) {
    e.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys
                    .filter(function (k) { return k !== CACHE_NAME; })
                    .map(function (k) { return caches.delete(k); })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', function (e) {
    var req = e.request;

    // HTML pages always go to the network — never cache authenticated pages
    if (req.mode === 'navigate') {
        e.respondWith(fetch(req));
        return;
    }

    if (req.method !== 'GET' || !req.url.startsWith('http')) {
        return;
    }

    e.respondWith(
        caches.match(req).then(function (cached) {
            return cached || fetch(req);
        })
    );
});
