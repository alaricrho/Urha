const CACHE_NAME = 'urha25-cache-v1';
const URLS_TO_CACHE = [
  '/',
  '/static/icon.png',
  '/static/manifest.json',
  '/static/service-worker.js',
  
  '/quizzes',
  '/login',
  '/admin'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(URLS_TO_CACHE);
    })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
    if (event.request.url.includes('/quizzes')) {
      event.respondWith(
        fetch(event.request)
          .then(response => {
            const clonedResponse = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clonedResponse));
            return response;
          })
          .catch(() => caches.match(event.request))
      );
    } else {
      event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
      );
    }
  });
  

// Activate event
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(
        keyList.map(key => {
          if (!cacheWhitelist.includes(key)) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});
