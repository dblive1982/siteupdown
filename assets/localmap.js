/* Local outage reports map: loads Leaflet + street tiles only when the visitor opens it. */
(function () {
  'use strict';
  var go = document.getElementById('lm-go'); if (!go) return;
  var el = document.getElementById('lm-map'), note = document.getElementById('lm-note'), me = document.getElementById('lm-me');
  var map = null, cells = [], heat = null, started = false;
  var CDN = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/';

  function say(t) { note.textContent = t; }
  function loadLeaflet(done, fail) {
    if (window.L) return done();
    var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = CDN + 'leaflet.min.css'; document.head.appendChild(l);
    var s = document.createElement('script'); s.src = CDN + 'leaflet.min.js'; s.onload = done; s.onerror = fail; document.head.appendChild(s);
  }
  function makeHeat() {
    return L.Layer.extend({
      onAdd: function (m) {
        this._m = m; var c = this._cv = L.DomUtil.create('canvas', 'lm-heat');
        c.style.position = 'absolute'; c.style.pointerEvents = 'none'; m.getPanes().overlayPane.appendChild(c);
        m.on('move zoom resize', this._draw, this); this._draw();
      },
      onRemove: function (m) { m.off('move zoom resize', this._draw, this); L.DomUtil.remove(this._cv); },
      _draw: function () {
        var m = this._m, c = this._cv, s = m.getSize();
        L.DomUtil.setPosition(c, m.containerPointToLayerPoint([0, 0]));
        c.width = s.x; c.height = s.y;
        var x = c.getContext('2d'), pxDeg = 256 * Math.pow(2, m.getZoom()) / 360;
        var maxN = cells.reduce(function (a, k) { return Math.max(a, k.n); }, 1);
        cells.forEach(function (k) {
          var p = m.latLngToContainerPoint([k.lat, k.lon]);
          var r = Math.max(16, Math.min(110, k.cell * pxDeg * 1.1));
          var a = 0.35 + 0.6 * Math.min(1, k.n / Math.max(3, maxN));
          var g = x.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
          g.addColorStop(0, 'rgba(232,58,58,' + a + ')'); g.addColorStop(0.45, 'rgba(255,150,30,' + (a * 0.7) + ')'); g.addColorStop(1, 'rgba(255,200,40,0)');
          x.fillStyle = g; x.beginPath(); x.arc(p.x, p.y, r, 0, 6.2832); x.fill();
        });
      }
    });
  }
  function popup(latlng) {
    var m = map, best = null, bd = 1e9, pxDeg = 256 * Math.pow(2, m.getZoom()) / 360, cp = m.latLngToContainerPoint(latlng);
    cells.forEach(function (k) {
      var p = m.latLngToContainerPoint([k.lat, k.lon]), d = Math.hypot(p.x - cp.x, p.y - cp.y);
      if (d < bd && d < Math.max(24, k.cell * pxDeg)) { bd = d; best = k; }
    });
    if (!best) return;
    var d = document.createElement('div'), b = document.createElement('b');
    b.textContent = best.n + (best.n === 1 ? ' report' : ' reports') + ' here, last 24 hours'; d.appendChild(b);
    (best.sites || []).forEach(function (s) { var r = document.createElement('div'); r.textContent = s.name + ' (' + s.n + ')'; d.appendChild(r); });
    L.popup({ closeButton: false }).setLatLng([best.lat, best.lon]).setContent(d).openOn(m);
  }
  function show(j) {
    cells = (j && j.cells) || [];
    if (heat) heat._draw();
    if (!cells.length) { say('No local reports in the last 24 hours yet. When someone reports a problem and adds their area, it shows up here.'); return; }
    say(j.total + (j.total === 1 ? ' report' : ' reports') + ' from ' + cells.length + (cells.length === 1 ? ' area' : ' areas') + ' in the last 24 hours. Tap a glow for details.');
    map.fitBounds(cells.map(function (k) { return [k.lat, k.lon]; }), { padding: [40, 40], maxZoom: 7 });
  }
  function start() {
    el.hidden = false;
    map = L.map(el, { minZoom: 2, worldCopyJump: true, attributionControl: true }).setView([30, 10], 2);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
    var H = makeHeat(); heat = new H(); heat.addTo(map);
    map.on('click', function (e) { popup(e.latlng); });
    fetch('/api/outage-local.php?hours=24', { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.json() : null; }).then(show)
      .catch(function () { say('Local reports could not be loaded just now.'); });
    if (navigator.geolocation) me.hidden = false;
    setTimeout(function () { map.invalidateSize(); }, 200);
  }
  go.addEventListener('click', function () {
    if (started) return; started = true; go.disabled = true; say('Loading the map…');
    loadLeaflet(start, function () { started = false; go.disabled = false; say('The map could not be loaded. Please try again later.'); });
  });
  me.addEventListener('click', function () {
    if (!map || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(function (p) { map.setView([p.coords.latitude, p.coords.longitude], 9); },
      function () { say('We could not get your location. You can still pan and zoom the map yourself.'); }, { timeout: 9000 });
  });
})();
