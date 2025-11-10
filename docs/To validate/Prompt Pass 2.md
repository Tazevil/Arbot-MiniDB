# PARAMÈTRES
IMAGES_INDEX_URL = https://tazevil.github.io/Arbot-MiniDB/json/images_db.json
ANALYSES_JSONL   = <<COLLER ICI LES OBJETS JSON PRODUITS PAR LA PASS 1 POUR CE LOT>>
LOT_SIZE         = 5
START_INDEX      = 0
TEMPERATURE      = 0

# OBJECTIF
Générer, pour chaque image du lot, un overlay vectoriel <svg> autonome
avec polylignes fermées qui annotent les défauts détectés.

# DONNÉES À LIRE
1) Ouvre IMAGES_INDEX_URL. Pour items[START_INDEX : START_INDEX+LOT_SIZE-1], récupère filename et URL.
2) Lis ANALYSES_JSONL pour connaître la liste des défauts par image.
3) Si l’index contient roi_hints, privilégie ces zones pour placer les polylignes.

# RÈGLES SVG
- Système de coordonnées normalisé [0..1]. Convertis en base 1000 pour le SVG.
  Ex.: point (x=0.32,y=0.47) → (320,470).
- Un <svg> autonome par image, de la forme:
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"> ... </svg>
- Polylignes fermées: 4–25 points. style: stroke="#FF0000"; fill="#FF0000"; fill-opacity="0.15"; stroke-width="3".
- Pas de texte ni d’élément non vectoriel.
- Regions = tableau parallèle à la liste des défauts (même ordre si possible), sinon indiquer "label_fr".

# FORMAT SORTIE (STRICT, UN OBJET PAR IMAGE, PAS D’AUTRE TEXTE)
{
  "id_file": "<####>",
  "filename": "<basename>",
  "svg": "<svg ...> ... </svg>",
  "regions": [
    {
      "label_fr": "<rappel du défaut>",
      "polyline": [[x1,y1],[x2,y2],...[xN,yN]]   // coords normalisées [0..1], polyligne fermée
    }
  ]
}

# CONTRÔLES
- Chaque "polyline" est FERMÉE (dernier point = premier point) ou le moteur la ferme explicitement.
- 4 ≤ N ≤ 25 par polyligne.
- Zéro texte hors JSON.

# ITÉRATION
Rends exactement LOT_SIZE objets JSON, puis STOP.
