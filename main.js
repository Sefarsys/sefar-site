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
  // Défilement automatique toutes les 3 secondes, sans pause au survol
  var DUREE = 3000;
  var slides = document.querySelectorAll('.slide');
  var tabs = document.querySelectorAll('.tab');
  var current = 0, elapsed = 0, last = null;

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
    elapsed += Math.min(dt, 250);
    if (elapsed >= DUREE) show(current + 1);
    var fill = tabs[current] && tabs[current].querySelector('.tab-fill');
    if (fill) fill.style.width = Math.min(100, elapsed / DUREE * 100) + '%';
    requestAnimationFrame(tick);
  }

  if (slides.length) {
    tabs.forEach(function (t) { t.addEventListener('click', function () { show(+t.dataset.i); }); });
    document.querySelector('.hero .prev').addEventListener('click', function () { show(current - 1); });
    document.querySelector('.hero .next').addEventListener('click', function () { show(current + 1); });
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
        // Règle d'affichage : articles des 2 derniers mois, salons jusqu'à leur dernier jour
        var today = new Date(); today.setHours(0, 0, 0, 0);
        var limite = new Date(today); limite.setDate(limite.getDate() - 61);
        function parse(d) {
          var m = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(d || '');
          return m ? new Date(+m[3], +m[2] - 1, +m[1]) : null;
        }
        var fiches = ((data && data.fiches) || []).filter(function (f) {
          if (f.type === 'salon') { var fin = parse(f.dateFin || f.date); return !fin || fin >= today; }
          var d = parse(f.date); return !d || d >= limite;
        });
        if (!fiches.length) { grid.appendChild(el('p', 'note', 'La prochaine sélection arrive bientôt.')); return; }
        fiches.slice(0, 4).forEach(function (f) {
          var a = el('a', 'fiche' + (f.type === 'salon' ? ' salon' : ''));
          if (/^https?:\/\//.test(f.lien || '')) a.href = f.lien;
          a.target = '_blank';
          a.rel = 'noopener';
          if (f.type === 'salon') {
            var debut = parse(f.date);
            a.appendChild(el('span', 'badge', debut && debut > today ? 'Salon à venir' : 'Salon en cours'));
          }
          var quand = f.type === 'salon' && f.dateFin ? 'Du ' + f.date + ' au ' + f.dateFin : (f.date || '');
          a.appendChild(el('span', 'meta', quand + ' · ' + (f.source || '')));
          a.appendChild(el('h3', '', f.titre || ''));
          a.appendChild(el('p', '', f.resume || ''));
          a.appendChild(el('span', 'go', 'Lire sur la source ↗'));
          grid.appendChild(a);
        });
      })
      .catch(function () { grid.appendChild(el('p', 'note', 'La veille est momentanément indisponible.')); });
  }


  // ---- Visionneuse des qualifications ----
  var lb = document.getElementById('lightbox');
  if (lb) {
    var media = lb.querySelector('.lb-media');
    document.querySelectorAll('.qbtn').forEach(function (b) {
      b.addEventListener('click', function () {
        media.innerHTML = '';
        if (b.dataset.img) {
          var im = document.createElement('img');
          im.src = b.dataset.img; im.alt = b.dataset.title;
          media.appendChild(im);
        } else {
          var ic = document.createElement('div'); ic.className = 'lb-icon';
          var svg = b.querySelector('svg'); if (svg) ic.appendChild(svg.cloneNode(true));
          media.appendChild(ic);
        }
        lb.querySelector('h3').textContent = b.dataset.title;
        lb.querySelector('.lb-desc').textContent = b.dataset.desc + (b.dataset.img ? '' : ' Document disponible sur demande.');
        if (lb.showModal) lb.showModal(); else lb.setAttribute('open', '');
      });
    });
    lb.querySelector('.lb-close').addEventListener('click', function () { lb.close(); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
  }

  // ---- Graphique du chiffre d'affaires (data/chiffres.json) ----
  var caBox = document.getElementById('ca-chart');
  if (caBox) {
    fetch('/data/chiffres.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var rows = (d && d.ca) || [];
        if (!rows.length) return;
        document.getElementById('chiffres').hidden = false;
        document.getElementById('ca-note').textContent = (d.note || '') + ' En ' + (d.unite || '') + '.';
        var W = 720, H = 320, padL = 16, padB = 36, padT = 28;
        var max = Math.max.apply(null, rows.map(function (r) { return r.valeur; })) * 1.15;
        var bw = (W - padL * 2) / rows.length;
        var ns = 'http://www.w3.org/2000/svg';
        var svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', rows.map(function (r) { return r.annee + ' : ' + r.valeur + ' ' + (d.unite || ''); }).join(', '));
        var base = H - padB;
        var line = document.createElementNS(ns, 'path');
        line.setAttribute('d', 'M' + padL + ' ' + base + ' H' + (W - padL));
        line.setAttribute('stroke', '#C9D0D4'); line.setAttribute('stroke-width', '1');
        svg.appendChild(line);
        var pts = [];
        rows.forEach(function (r, i) {
          var h = (r.valeur / max) * (base - padT);
          var x = padL + i * bw + bw * 0.22, w = bw * 0.56, y = base - h;
          var rect = document.createElementNS(ns, 'rect');
          rect.setAttribute('x', x); rect.setAttribute('y', y); rect.setAttribute('width', w); rect.setAttribute('height', h);
          rect.setAttribute('rx', 3); rect.setAttribute('fill', i === rows.length - 1 ? '#F07A2B' : '#F6B48A');
          svg.appendChild(rect);
          pts.push((x + w / 2) + ' ' + (y - 2));
          var t = document.createElementNS(ns, 'text');
          t.setAttribute('x', x + w / 2); t.setAttribute('y', y - 10); t.setAttribute('text-anchor', 'middle');
          t.setAttribute('font-size', '14'); t.setAttribute('font-weight', '700'); t.setAttribute('fill', '#1A2024');
          t.textContent = r.libelle || r.valeur; svg.appendChild(t);
          var a = document.createElementNS(ns, 'text');
          a.setAttribute('x', x + w / 2); a.setAttribute('y', base + 22); a.setAttribute('text-anchor', 'middle');
          a.setAttribute('font-size', '13'); a.setAttribute('fill', '#6B757A'); a.textContent = r.annee; svg.appendChild(a);
        });
        caBox.appendChild(svg);
      })
      .catch(function () {});
  }

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
