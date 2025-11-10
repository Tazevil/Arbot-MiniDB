# PARAMÈTRES
IMAGES_INDEX_URL = https://tazevil.github.io/Arbot-MiniDB/json/images_db.json
LOT_SIZE         = 20
START_INDEX      = 0
TEMPERATURE      = 0

# OBJECTIF
Pré-cartographier chaque image sans juger la conformité.
Produire un CSV court pour guider la passe d’analyse.

# DONNÉES À LIRE
1) Ouvre IMAGES_INDEX_URL (JSON). Utilise items[] dans l’ordre d’index.
2) Pour chaque item: privilégie url_preview si présent. Sinon url.

# RÈGLES DE CLASSIFICATION (nommage)
- "chantier" si le nom contient une date AAAAMMJJ juste avant l’extension (Cas A).
- Sinon "sinistre".
- Ambigu → "UNKNOWN".

# VALEURS ATTENDUES
- id_file = 4 premiers chiffres du nom, sinon "UNKNOWN".
- vue ∈ {GEN, DET, UNKNOWN}.
- angle ∈ {face, profil, plongée, contre-plongée, UNKNOWN}.
- zone ∈ {SDB, WC, PLAN, CHANTIER, UNKNOWN}.
- objets_clef: 1–3 mots séparés par “;”.

# SORTIE (CSV STRICT, ENTÊTE RÉPÉTÉE À CHAQUE LOT)
id_file,filename,classification,vue,objets_clef,angle,zone,notes

# CONTRAINTES
- Analyse VISION RÉELLE de l’image ouverte via l’URL. Décrire ce qui est VISIBLE.
- Pas de phrases longues. 1–3 mots par champ hors filename.
- Si incertain: "UNKNOWN". Zéro spéculation.
- Traite items[START_INDEX : START_INDEX+LOT_SIZE-1] uniquement.
- N’écris RIEN d’autre que le CSV.

# ITÉRATION
Rends le CSV puis STOP. J’enverrai "SUIVANT" pour le lot suivant (START_INDEX += LOT_SIZE).
