#!/usr/bin/env python3
"""Assemble les pages du site Séfar Système.

Chaque page est écrite dans src/<nom>.html : la première ligne est un
commentaire de métadonnées, le reste est le contenu de la page (<main>).
L'en-tête et le pied de page sont communs à toutes les pages et définis ici.

Usage : python3 build.py   (génère <nom>.html à la racine du site)
"""
import datetime
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SITE = "https://sefar-systeme.dz"

# Données structurées (schema.org) : aident Google à comprendre qui est l'entreprise
ORG_JSONLD = {
    "@context": "https://schema.org",
    "@type": ["Organization", "LocalBusiness", "ElectricalContractor"],
    "@id": SITE + "/#entreprise",
    "name": "Séfar Système",
    "legalName": "SARL Séfar Système",
    "alternateName": ["Sefar Systeme", "Séfar Système SARL"],
    "slogan": "Reliable energy infrastructure",
    "description": "Intégrateur algérien de systèmes électriques et numériques : contrôle-commande numérique des postes HT/MT, intégration IEC 61850, protections et rétrofit Sepam, tableaux MT/BT, supervision SCADA, télécoms industrielles, génie civil et énergies renouvelables.",
    "url": SITE + "/",
    "logo": SITE + "/images/logo-sefar-couleur-v2.png",
    "image": SITE + "/images/slide-infrastructures.jpg",
    "foundingDate": "2019",
    "telephone": "+213 28 10 31 32",
    "email": "contact@sefar-systeme.dz",
    "faxNumber": "+213 28 10 31 32",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "7 rue Ahmed Kara, Djenane El Malik",
        "addressLocality": "Hydra",
        "addressRegion": "Alger",
        "addressCountry": "DZ",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 36.7464287, "longitude": 3.0266527},
    "hasMap": "https://maps.app.goo.gl/rWyvqBvA1b9t3pJk7",
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
        "opens": "08:30", "closes": "17:00",
    }],
    "areaServed": {"@type": "Country", "name": "Algérie"},
    "knowsAbout": ["Contrôle-commande numérique", "IEC 61850", "Postes électriques HT/MT",
                   "Relais de protection Sepam", "SCADA", "Téléconduite IEC 60870-5-104",
                   "Tableaux moyenne tension", "Énergies renouvelables"],
    "hasCredential": ["ISO 9001:2015", "ISO 14001:2015", "ISO 45001:2018",
                      "Qualification BTP catégorie VI",
                      "Schneider Electric EcoXpert Power Automation"],
}
SRC = ROOT / "src"

# ---------------------------------------------------------------------------
# Langues : le français est à la racine, l'anglais dans /en/, l'arabe dans /ar/.
# Les pages sources sont dans src/ (fr), src/en/ et src/ar/ ; mêmes noms de fichiers.
# ---------------------------------------------------------------------------
LANGS = {
    "fr": {
        "prefix": "", "dir": "ltr", "locale": "fr_DZ",
        "nav": [("home", "", "Home"), ("apropos", "a-propos.html", "À propos"),
                ("solutions", "solutions.html", "Solutions"), ("references", "references.html", "Références"),
                ("support", "support.html", "Support"), ("actualites", "actualites.html", "Actualités")],
        "contact": "Contact", "home_crumb": "Accueil", "home_aria": "Séfar Système, accueil",
        "menu": "Ouvrir le menu", "nav_aria": "Navigation principale",
        "f_intro": "Intégrateur de systèmes électriques et numériques.",
        "f_company": "Entreprise", "f_about": "À propos", "f_refs": "Références", "f_news": "Actualités",
        "f_solutions": "Solutions", "f_infra": "Infrastructures électriques", "f_futur": "Énergies du futur",
        "f_digital": "Digital Energy", "f_contact": "Contact",
        "f_addr": "7 rue Ahmed Kara, Djenane El Malik<br>Hydra, Alger, Algérie",
        "f_tel": "Tél. / Fax", "f_mail": "E-mail", "f_rights": "Séfar Système. Tous droits réservés.",
        "f_legal_aria": "Liens légaux", "f_legal": "Mentions légales", "f_privacy": "Politique de confidentialité",
    },
    "en": {
        "prefix": "/en", "dir": "ltr", "locale": "en_US",
        "nav": [("home", "", "Home"), ("apropos", "a-propos.html", "About us"),
                ("solutions", "solutions.html", "Solutions"), ("references", "references.html", "References"),
                ("support", "support.html", "Support"), ("actualites", "actualites.html", "News")],
        "contact": "Contact", "home_crumb": "Home", "home_aria": "Séfar Système, home",
        "menu": "Open the menu", "nav_aria": "Main navigation",
        "f_intro": "Electrical and digital systems integrator.",
        "f_company": "Company", "f_about": "About us", "f_refs": "References", "f_news": "News",
        "f_solutions": "Solutions", "f_infra": "Electrical infrastructure", "f_futur": "Future energies",
        "f_digital": "Digital Energy", "f_contact": "Contact",
        "f_addr": "7 rue Ahmed Kara, Djenane El Malik<br>Hydra, Algiers, Algeria",
        "f_tel": "Tel. / Fax", "f_mail": "Email", "f_rights": "Séfar Système. All rights reserved.",
        "f_legal_aria": "Legal links", "f_legal": "Legal notice", "f_privacy": "Privacy policy",
    },
    "ar": {
        "prefix": "/ar", "dir": "rtl", "locale": "ar_DZ",
        "nav": [("home", "", "الرئيسية"), ("apropos", "a-propos.html", "من نحن"),
                ("solutions", "solutions.html", "الحلول"), ("references", "references.html", "المراجع"),
                ("support", "support.html", "الدعم"), ("actualites", "actualites.html", "الأخبار")],
        "contact": "اتصل بنا", "home_crumb": "الرئيسية", "home_aria": "صفار سيستام، الصفحة الرئيسية",
        "menu": "فتح القائمة", "nav_aria": "القائمة الرئيسية",
        "f_intro": "مُدمج أنظمة كهربائية ورقمية.",
        "f_company": "الشركة", "f_about": "من نحن", "f_refs": "المراجع", "f_news": "الأخبار",
        "f_solutions": "الحلول", "f_infra": "بنى تحتية كهربائية", "f_futur": "طاقات المستقبل",
        "f_digital": "الطاقة الرقمية", "f_contact": "اتصل بنا",
        "f_addr": "7 شارع أحمد قارة، جنان المالك<br>حيدرة، الجزائر العاصمة، الجزائر",
        "f_tel": "الهاتف / الفاكس", "f_mail": "البريد الإلكتروني", "f_rights": "صفار سيستام. جميع الحقوق محفوظة.",
        "f_legal_aria": "روابط قانونية", "f_legal": "الإشعار القانوني", "f_privacy": "سياسة الخصوصية",
    },
}

HEAD = """<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Séfar Système">
<meta property="og:locale" content="{locale}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{site}/images/slide-infrastructures.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/images/favicon-v2.png">
<link rel="apple-touch-icon" href="/images/favicon-v2.png">{jsonld}{fonts}
<link rel="stylesheet" href="/styles.css">
</head>
<body>
"""

AR_FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;700&display=swap">"""

HEADER = """<header class="header">
  <div class="wrap">
    <a class="brand" href="{home}" aria-label="{home_aria}">
      <img src="/images/logo-sefar-couleur-v2.png" alt="Séfar Système" width="208" height="92">
      <span class="tagline" lang="en">Reliable energy<br>infrastructure</span>
    </a>
    <button class="burger" aria-label="{menu}" aria-expanded="false" aria-controls="menu">
      <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="1.8" fill="none"/></svg>
    </button>
    <nav class="nav" id="menu" aria-label="{nav_aria}">
{links}
      <a class="nav-cta{cta_on}" href="{prefix}/contact.html">{contact}</a>
      <span class="lang">
        <a{on_fr} href="{url_fr}" lang="fr" hreflang="fr">FR</a>
        <a{on_en} href="{url_en}" lang="en" hreflang="en">EN</a>
        <a class="ar{on_ar_cls}" href="{url_ar}" lang="ar" hreflang="ar">العربية</a>
      </span>
    </nav>
  </div>
</header>
"""

FOOTER = """<footer class="footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="/images/logo-sefar-couleur-v2.png" alt="Séfar Système" width="230" height="101">
        <span class="motto" lang="en">Reliable energy<br>infrastructure</span>
        <p>{f_intro}</p>
        <div class="norms" dir="ltr"><span>IEC 61850</span><span>IEC 60870-5-104</span><span>MODBUS</span></div>
      </div>
      <div class="footer-cols">
        <div><strong>{f_company}</strong><a href="{prefix}/a-propos.html">{f_about}</a><a href="{prefix}/references.html">{f_refs}</a><a href="{prefix}/actualites.html">{f_news}</a></div>
        <div><strong>{f_solutions}</strong><a href="{prefix}/infrastructures-electriques.html">{f_infra}</a><a href="{prefix}/energies-du-futur.html">{f_futur}</a><a href="{prefix}/digital-energy.html">{f_digital}</a></div>
        <div class="footer-contact"><strong>{f_contact}</strong>
          <span>Séfar Système SARL</span>
          <span>{f_addr}</span>
          <span>{f_tel} : <a href="tel:+21328103132" dir="ltr">028 10 31 32</a></span>
          <span>{f_mail} : <a href="mailto:contact@sefar-systeme.dz">contact@sefar-systeme.dz</a></span>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> {f_rights}</span>
      <nav aria-label="{f_legal_aria}"><a href="{prefix}/mentions-legales.html">{f_legal}</a><a href="{prefix}/mentions-legales.html#confidentialite">{f_privacy}</a></nav>
    </div>
  </div>
</footer>

<script src="/main.js" defer></script>
</body>
</html>
"""


def page_path(lang, name):
    """Chemin public d'une page (ex. /en/solutions.html, / pour l'accueil français)."""
    pre = LANGS[lang]["prefix"]
    return (pre + "/") if name == "index.html" else f"{pre}/{name}"


def build():
    sitemap = []
    for lang, L in LANGS.items():
        src_dir = SRC if lang == "fr" else SRC / lang
        if not src_dir.is_dir():
            continue
        out_dir = ROOT if lang == "fr" else ROOT / lang
        out_dir.mkdir(exist_ok=True)
        for src in sorted(src_dir.glob("*.html")):
            text = src.read_text(encoding="utf-8")
            m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
            if not m:
                raise SystemExit(f"{src} : métadonnées manquantes en première ligne")
            meta = json.loads(m.group(1))
            body = text[m.end():]

            # Blocs réutilisables : <!--#nom#--> -> partials/<langue>/nom.html (ou partials/nom.html)
            def partial(k):
                n = k.group(1).lower() + ".html"
                f = ROOT / "partials" / lang / n
                if lang == "fr" or not f.exists():
                    f = ROOT / "partials" / n
                return f.read_text(encoding="utf-8").rstrip()
            body = re.sub(r"<!--#(\w+)#-->", partial, body)

            active = meta.get("nav", "")
            on = ' class="on" aria-current="page"'
            links = "\n".join(
                f'      <a href="{L["prefix"]}/{href}"{on if key == active else ""}>{label}</a>'
                for key, href, label in L["nav"]
            )
            path = page_path(lang, src.name)
            url = SITE + path
            # Versions linguistiques existantes de cette page
            versions = {lg: page_path(lg, src.name) for lg in LANGS
                        if ((SRC if lg == "fr" else SRC / lg) / src.name).exists()}
            alternates = "\n".join(f'<link rel="alternate" hreflang="{lg}" href="{SITE}{p}">' for lg, p in versions.items())
            if "fr" in versions:
                alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{versions["fr"]}">'
            noindex = meta.get("noindex", False)
            jsonld = ""
            if src.name == "index.html":
                org = dict(ORG_JSONLD, url=url)
                jsonld = '\n<script type="application/ld+json">' + json.dumps(org, ensure_ascii=False) + "</script>"
            elif not noindex:
                crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": L["home_crumb"], "item": SITE + page_path(lang, "index.html")},
                    {"@type": "ListItem", "position": 2, "name": meta["title"].split(" — ")[0], "item": url}]}
                jsonld = '\n<script type="application/ld+json">' + json.dumps(crumbs, ensure_ascii=False) + "</script>"
            if not noindex:
                sitemap.append((url, 1.0 if src.name == "index.html" else 0.8))
            fallback = page_path
            html = (
                HEAD.format(lang=lang, dir=L["dir"], locale=L["locale"], title=meta["title"],
                            description=meta["description"], url=url, site=SITE, alternates=alternates,
                            robots="noindex, follow" if noindex else "index, follow, max-image-preview:large",
                            jsonld=jsonld, fonts=AR_FONTS if lang == "ar" else "")
                + HEADER.format(links=links, cta_on=" on" if active == "contact" else "",
                                home=page_path(lang, "index.html"), prefix=L["prefix"],
                                on_fr=' class="on"' if lang == "fr" else "",
                                on_en=' class="on"' if lang == "en" else "",
                                on_ar_cls=" on" if lang == "ar" else "",
                                url_fr=versions.get("fr", fallback("fr", "index.html")),
                                url_en=versions.get("en", fallback("en", "index.html")),
                                url_ar=versions.get("ar", fallback("ar", "index.html")),
                                **{k: v for k, v in L.items() if k in ("home_aria", "menu", "nav_aria", "contact")})
                + body.rstrip() + "\n\n"
                + FOOTER.format(prefix=L["prefix"], **{k: v for k, v in L.items() if k.startswith("f_")})
            )
            out = out_dir / src.name
            out.write_text(html, encoding="utf-8")
            print("généré :", out.relative_to(ROOT))

    # Plan du site pour les moteurs de recherche
    today = datetime.date.today().isoformat()
    sitemap.sort(key=lambda u: (-u[1], u[0]))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, prio in sitemap:
        xml.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>")
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print("généré : sitemap.xml (", len(sitemap), "pages )")


if __name__ == "__main__":
    build()
