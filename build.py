#!/usr/bin/env python3
"""Assemble les pages du site Séfar Système.

Chaque page est écrite dans src/<nom>.html : la première ligne est un
commentaire de métadonnées, le reste est le contenu de la page (<main>).
L'en-tête et le pied de page sont communs à toutes les pages et définis ici.

Usage : python3 build.py   (génère <nom>.html à la racine du site)
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"

NAV = [
    ("home", "/", "Home"),
    ("solutions", "/solutions.html", "Solutions"),
    ("domaines", "/domaines-application.html", "Domaines d'application"),
    ("references", "/references.html", "Références"),
    ("support", "/support.html", "Support"),
    ("apropos", "/a-propos.html", "À propos"),
]

HEAD = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="/images/slide-infrastructures.jpg">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
"""

HEADER = """<header class="header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Séfar Système, accueil">
      <img src="/images/logo-sefar-couleur.png" alt="Séfar Système" width="208" height="92">
      <span class="tagline">Reliable energy<br>infrastructure</span>
    </a>
    <button class="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="menu">
      <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="1.8" fill="none"/></svg>
    </button>
    <nav class="nav" id="menu" aria-label="Navigation principale">
{links}
      <a class="nav-cta{cta_on}" href="/contact.html">Contact</a>
      <span class="lang">
        <a class="on" href="/" lang="fr">FR</a>
        <a href="/" lang="en">EN</a>
        <a class="ar" href="/" lang="ar">العربية</a>
      </span>
    </nav>
  </div>
</header>
"""

FOOTER = """<footer class="footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="/images/logo-sefar-couleur.png" alt="Séfar Système" width="230" height="101">
        <span class="motto">Reliable energy<br>infrastructure</span>
        <p>Intégrateur de systèmes électriques et numériques.</p>
        <div class="norms"><span>IEC 61850</span><span>IEC 60870-5-104</span><span>MODBUS</span></div>
      </div>
      <div class="footer-cols">
        <div><strong>Entreprise</strong><a href="/a-propos.html">À propos</a><a href="/references.html">Références</a><a href="/contact.html">Carrières</a></div>
        <div><strong>Solutions</strong><a href="/infrastructures-electriques.html">Infrastructures électriques</a><a href="/energies-du-futur.html">Énergies du futur</a><a href="/digital-energy.html">Digital Energy</a></div>
        <div class="footer-contact"><strong>Contact</strong>
          <span>Séfar Système SARL</span>
          <span>7 rue Ahmed Kara, Djenane El Malik<br>Hydra, Alger, Algérie</span>
          <span>Tél. / Fax : <a href="tel:+21328103132">028 10 31 32</a></span>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> Séfar Système. Tous droits réservés.</span>
      <nav aria-label="Liens légaux"><a href="/mentions-legales.html">Mentions légales</a><a href="/mentions-legales.html#confidentialite">Politique de confidentialité</a></nav>
    </div>
  </div>
</footer>

<script src="/main.js" defer></script>
</body>
</html>
"""


def build():
    pages = sorted(SRC.glob("*.html"))
    for src in pages:
        text = src.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
        if not m:
            raise SystemExit(f"{src.name} : métadonnées manquantes en première ligne")
        meta = json.loads(m.group(1))
        body = text[m.end():]
        # Blocs réutilisables : <!--#nom#--> est remplacé par partials/nom.html
        body = re.sub(
            r"<!--#(\w+)#-->",
            lambda k: (ROOT / "partials" / f"{k.group(1).lower()}.html").read_text(encoding="utf-8").rstrip(),
            body,
        )
        active = meta.get("nav", "")
        on = ' class="on" aria-current="page"'
        links = "\n".join(
            f'      <a href="{href}"{on if key == active else ""}>{label}</a>'
            for key, href, label in NAV
        )
        html = (
            HEAD.format(title=meta["title"], description=meta["description"])
            + HEADER.format(links=links, cta_on=" on" if active == "contact" else "")
            + body.rstrip() + "\n\n"
            + FOOTER
        )
        out = ROOT / src.name
        out.write_text(html, encoding="utf-8")
        print("généré :", out.name)


if __name__ == "__main__":
    build()
