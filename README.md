# Site Séfar Système

Site statique (HTML, CSS, JavaScript) hébergé sur Netlify. Devise : *Reliable energy infrastructure*.

## Contenu

- `index.html` : page d'accueil
- `styles.css` : mise en forme
- `main.js` : carrousel, menu mobile, affichage de la veille
- `images/` : logo, favicon et photos du carrousel
- `data/veille.json` : fiches du bloc « Actualités du secteur »
- `netlify.toml` : réglages Netlify

## Mise en ligne

Chaque modification poussée sur la branche `main` est publiée automatiquement par Netlify (environ une minute).

## Veille hebdomadaire

Le bloc « Actualités du secteur » affiche les 4 premières fiches de `data/veille.json`.
L'agent de veille met à jour **uniquement ce fichier**, après validation. Format d'une fiche :

```json
{
  "date": "JJ.MM.AAAA",
  "source": "Nom du média",
  "titre": "Titre reformulé en français",
  "resume": "Deux phrases maximum, reformulées.",
  "lien": "https://…"
}
```

Les fiches sont rangées de la plus récente à la plus ancienne. Le champ `miseAJour` indique la date de la dernière sélection (AAAA-MM-JJ).

## Contenus à compléter

- Adresse, téléphone et e-mail dans le pied de page
- Photo et détails de la référence Sonelgaz
- Pages Mentions légales et Politique de confidentialité
