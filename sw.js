/* Service worker: shows the notifications people asked for, and shows a friendly page when you are offline. It never serves cached copies of pages, so results are always live. */
var OFFLINE = '/offline.html', CK = 'sud-offline-v1';
self.addEventListener('install', function (e) { e.waitUntil(caches.open(CK).then(function (c) { return c.add(OFFLINE); }).catch(function () {})); self.skipWaiting(); });
self.addEventListener('fetch', function (e) {
  if (e.request.mode !== 'navigate') return;
  e.respondWith(fetch(e.request).catch(function () { return caches.match(OFFLINE).then(function (r) { return r || Response.error(); }); }));
});
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('push', function (e) {
  var d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) {}
  e.waitUntil(self.registration.showNotification(d.title || 'siteupdown.com', {
    body: d.body || '', icon: '/favicon-192.png', badge: '/favicon-64.png', tag: d.url || 'siteupdown', data: { url: d.url || '/' }
  }));
});
self.addEventListener('notificationclick', function (e) {
  e.notification.close();
  var u = (e.notification.data && e.notification.data.url) || '/';
  try { if (new URL(u, self.location.origin).origin !== self.location.origin) u = '/'; } catch (x) { u = '/'; }
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) if (list[i].url.indexOf(u) > -1 && 'focus' in list[i]) return list[i].focus();
    return self.clients.openWindow(u);
  }));
});
