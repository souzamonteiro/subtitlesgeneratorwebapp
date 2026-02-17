const CACHE_NAME = 'subtitlesgeneratorwebapp-v1';
const urlsToCache = [
  './',
  './css',
  './css/fontawesome.min.css',
  './icons',
  './icons/apple-touch-icon.png',
  './icons/favicon-16.png',
  './icons/favicon-32.png',
  './icons/favicon.ico',
  './icons/icon-128x128.png',
  './iconsicon-144x144.png',
  './icons/icon-152x152.png',
  './icons/icon-16x16.png',
  './icons/icon-180x180.png',
  './icons/icon-192x192.png',
  './icons/icon-32x32.png',
  './icons/icon-384x384.png',
  './icons/icon-512x512.png',
  './icons/icon-72x72.png',
  './icons/icon-96x96.png',
  './icons/icon.svg',
  './index.html',
  './manifest.json',
  './webfonts',
  './webfonts/fa-brands-400.eot',
  './webfonts/fa-brands-400.svg',
  './webfonts/fa-brands-400.ttf',
  './webfonts/fa-brands-400.woff',
  './webfonts/fa-brands-400.woff2',
  './webfonts/fa-regular-400.eot',
  './webfonts/fa-regular-400.svg',
  './webfonts/fa-regular-400.ttf',
  './webfonts/fa-regular-400.woff',
  './webfonts/fa-regular-400.woff2',
  './webfonts/fa-solid-900.eot',
  './webfonts/fa-solid-900.svg',
  './webfonts/fa-solid-900.ttf',
  './webfonts/fa-solid-900.woff',
  './webfonts/fa-solid-900.woff2',
  './Vosklet.js',
  './Vosklet.wasm',
  './Wrapper.js',
  './vosk-model-small-en-us-0.15.tar.gz',
  './vosk-model-small-pt-0.3.tar.gz',
  './vosk-model-small-es-0.42.tar.gz'
];

// Installation - cache all resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache).catch(err => {
          console.warn('Some resources could not be cached:', err);
        });
      })
  );
  // Forces the immediate activation of the new service worker
  self.skipWaiting();
});

// Activation - clears old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME) // Keep only the current cache
          .map(cacheName => {
            console.log('Removing old cache:', cacheName);
            return caches.delete(cacheName); // Remove old caches
          })
      );
    })
  );
  return self.clients.claim();
});

// Fetch - estratégia Cache First com fallback para rede
self.addEventListener('fetch', event => {
  // Ignores non-GET requests and Chrome extensions.
  if (event.request.method !== 'GET' || 
      event.request.url.startsWith('chrome-extension://')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // If found in the cache, return it
        if (cachedResponse) {
          return cachedResponse;
        }

        // If you can't find it, search online
        return fetch(event.request)
          .then(response => {
            // Check if the answer is valid.
            if (!response || response.status !== 200 || response.type === 'opaque') {
              return response;
            }

            // Clone the response for caching and use.
            const responseToCache = response.clone();

            // Adds to cache for future use.
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(error => {
            // If the network fails and it's an HTML page, it returns the offline page
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('./index.html');
            }
            // For other resources, you can return a fallback
            console.log('Fetch failed; returning offline page instead.', error);
          });
      })
  );
});