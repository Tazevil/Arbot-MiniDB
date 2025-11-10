# PARAMÈTRES
IMAGES_INDEX_URL = https://tazevil.github.io/Arbot-MiniDB/json/images_db.json
DOCS_INDEX_URL   = https://tazevil.github.io/Arbot-MiniDB/json/docs_index.json
PREPASS_CSV      = <<COLLER ICI LE CSV DU LOT COURANT PROVENANT DE LA PASS 0>>
LOT_SIZE         = 5
START_INDEX      = 0
MAX_DEFAUTS      = 6
TEMPERATURE      = 0

# OBJECTIF
Pour chaque image: décrire factuellement, détecter les défauts visibles,
lier chaque défaut à 0–n citations {doc_id, page} issues de DOCS_INDEX_URL.

# DONNÉES À LIRE
1) Ouvre IMAGES_INDEX_URL et DOCS_INDEX_URL.
2) Pour items[START_INDEX : START_INDEX+LOT_SIZE-1], ouvre l’image (url_preview si présent, sinon url).
3) Utilise PREPASS_CSV uniquement comme contexte léger (si contradiction, l’image prévaut).

# RÈGLES
- VISION RÉELLE: décrire uniquement ce qui est visible. Aucune inférence cachée.
- Classification: "chantier" si date AAAAMMJJ en fin de nom; sinon "sinistre"; sinon "UNKNOWN".
- Citations: doc_id ∈ ids de DOCS_INDEX_URL. page = numéro si repérable, sinon "UNKNOWN".
- Limiter à MAX_DEFAUTS par image.
- Ajouter "confidence" ∈ [0,1] par défaut.
- Si information manquante → "UNKNOWN" et expliquer brièvement dans "incertitude".

# FEW-SHOT DE GARDE (à respecter)
[Mauvais]: « probable fuite derrière le mur »  ← spéculation non visible
[Bon]: « absence visible de mastic en pied de paroi côté baignoire »

# FORMAT SORTIE (STRICT, UN OBJET PAR IMAGE, PAS D’AUTRE TEXTE)
{
  "id_file": "<####|UNKNOWN>",
  "filename": "<basename>",
  "image_url": "<url réellement utilisée>",
  "classification": "<chantier|sinistre|UNKNOWN>",
  "description_fr": "2 à 4 phrases factuelles, seulement ce qui est visible.",
  "defauts": [
    {
      "label_fr": "<défaut concis>",
      "justification": "<indice(s) visuel(s) objectifs>",
      "confidence": 0.0,
      "citations": [
        {"doc_id":"<ID dans docs_index.json>", "page": <num|UNKNOWN>}
      ]
    }
  ],
  "incertitude": "<raison si page/doc absents ou vision insuffisante, sinon ''>"
}

# CONTRÔLES À FAIRE AVANT RENDU
- JSON valide. Pas de texte hors JSON.
- "defauts" ≤ MAX_DEFAUTS. "confidence" présent pour chaque défaut.
- Si page exacte introuvable → page=UNKNOWN + incertitude non vide.

# ITÉRATION
Rends exactement LOT_SIZE objets JSON puis STOP.
J’enverrai "SUIVANT" pour le lot suivant (START_INDEX += LOT_SIZE).
