const CACHE_NAME = "sistema-peticoes-static-v1";
const STATIC_ASSETS = [
  "/",
  "/static/styles.css",
  "/static/app.js",
  "/static/api.js",
  "/static/ui.js",
  "/static/render.js",
  "/static/state/store.js",
];

function isSensitiveRequest(request) {
  const url = new URL(request.url);
  return (
    request.method !== "GET" ||
    url.pathname.startsWith("/api/v1") ||
    url.pathname.includes("/documents/") ||
    url.pathname.includes("/reports/")
  );
}

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (isSensitiveRequest(event.request)) return;

  const url = new URL(event.request.url);
  if (url.pathname === "/") {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request)),
    );
    return;
  }

  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
  }
});
