/* Service worker: shows the notifications people asked for. It does not cache pages or run in the background for anything else. */
self.addEventListener('install', function () { self.skipWaiting(); });
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
