# ArBot Regex ULTRA-PROPRE - Référence Officielle
# Version: 1.0.0 - 2025-10-23

import re

# Pattern validé sur 94 images réelles
FILENAME_PATTERN = re.compile(
    r'^(?P<file_ID>\d{4})_(?P<detail>[A-Z0-9À-ÖØ-Ý-]+)_(?P<viewtype>[A-Z]{3})(?:_(?P<date>\d{8}))?\.(?P<ext>jpg|jpeg|png|webp|tiff)$',
    re.IGNORECASE
)

# Exemples validés
EXAMPLES_VALID = [
    "0001_SDB_GEN_20250818.jpg",
    "0002_SDB_GEN_20250818.jpg",
    "0003_SALON-PROTECTION_GEN_20250818.jpg",
    "0005_WC_GEN_20250818.jpg",
    "2101_CARRELAGE_GEN.jpg",
    "3601_JOINT_DET_20250819.jpg"
]

# Utilisation
def validate_filename(filename):
    """Valide un nom de fichier selon convention ArBot"""
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None

    return {
        'file_ID': int(match.group("file_ID")),
        'detail': match.group("detail"),
        'viewtype': match.group("viewtype"),
        'date': match.group("date"),
        'ext': match.group("ext")
    }

# Test
if __name__ == '__main__':
    print("Test regex ultra-propre:\n")
    for filename in EXAMPLES_VALID:
        result = validate_filename(filename)
        if result:
            print(f"✅ {filename}")
            print(f"   ID={result['file_ID']}, detail={result['detail']}, view={result['viewtype']}, date={result['date']}")
        else:
            print(f"❌ {filename}")
