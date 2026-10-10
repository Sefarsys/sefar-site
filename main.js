// Séfar Système — carrousel, menu mobile et veille
(function () {
  'use strict';

  // ---- Menu mobile ----
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
    });
  }

  // ---- Carrousel ----
  var DUREE = 7000;
  var slides = document.querySelectorAll('.slide');
  var tabs = document.querySelectorAll('.tab');
  var hero = document.querySelector('.hero');
  var current = 0, elapsed = 0, paused = false, last = null;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function show(n) {
    current = (n + slides.length) % slides.length;
    elapsed = 0;
    slides.forEach(function (s, k) {
      s.classList.toggle('active', k === current);
      s.setAttribute('aria-hidden', k === current ? 'false' : 'true');
    });
    tabs.forEach(function (t, k) {
      t.classList.toggle('active', k === current);
      t.setAttribute('aria-current', k === current ? 'true' : 'false');
      t.querySelector('.tab-fill').style.width = k < current ? '100%' : '0%';
    });
  }

  function tick(ts) {
    if (last === null) last = ts;
    var dt = ts - last; last = ts;
    if (!paused && !reduceMotion) {
      elapsed += dt;
      if (elapsed >= DUREE) show(current + 1);
      var fill = tabs[current] && tabs[current].querySelector('.tab-fill');
      if (fill) fill.style.width = Math.min(100, elapsed / DUREE * 100) + '%';
    }
    requestAnimationFrame(tick);
  }

  if (slides.length) {
    tabs.forEach(function (t) { t.addEventListener('click', function () { show(+t.dataset.i); }); });
    document.querySelector('.hero .prev').addEventListener('click', function () { show(current - 1); });
    document.querySelector('.hero .next').addEventListener('click', function () { show(current + 1); });
    hero.addEventListener('mouseenter', function () { paused = true; });
    hero.addEventListener('mouseleave', function () { paused = false; });
    hero.addEventListener('focusin', function () { paused = true; });
    hero.addEventListener('focusout', function () { paused = false; });
    document.addEventListener('visibilitychange', function () { last = null; });
    show(0);
    requestAnimationFrame(tick);
  }

  // ---- Veille (lue depuis data/veille.json) ----
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }

  var grid = document.getElementById('veille-grid');
  if (grid) {
    fetch('/data/veille.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var fiches = (data && data.fiches) || [];
        if (!fiches.length) { grid.appendChild(el('p', 'note', 'La prochaine sélection arrive bientôt.')); return; }
        fiches.slice(0, 4).forEach(function (f) {
          var a = el('a', 'fiche');
          if (/^https?:\/\//.test(f.lien || '')) a.href = f.lien;
          a.target = '_blank';
          a.rel = 'noopener';
          a.appendChild(el('span', 'meta', (f.date || '') + ' · ' + (f.source || '')));
          a.appendChild(el('h3', '', f.titre || ''));
          a.appendChild(el('p', '', f.resume || ''));
          a.appendChild(el('span', 'go', 'Lire sur la source ↗'));
          grid.appendChild(a);
        });
      })
      .catch(function () { grid.appendChild(el('p', 'note', 'La veille est momentanément indisponible.')); });
  }

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
