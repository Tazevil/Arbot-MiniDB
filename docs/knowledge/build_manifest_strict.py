#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan récursif, respect STRICT NameGen v1.5 :
<file_ID:4d>_<DETAIL UPPERCASE & - only>_<VIEWTYPE:3A>[_YYYYMMDD].<ext>
ext ∈ {jpg,jpeg,png,webp,tiff} ; date optionnelle ; extension OBLIGATOIRE.
Sorties :
- manifest_images.json (complet)
- manifest_images_parsed.json (ingestion)
- manifest_report.json
- unparsed_filenames.txt (si besoin)
"""

import os, re, json, argparse, hashlib
from datetime import datetime
from PIL import Image, ExifTags

# --------- Convention (STRICT) ----------
NAME_PATTERN = re.compile(
    r'^(?P<file_ID>\d{4})_'
    r'(?P<detail>[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*)_'
    r'(?P<viewtype>[A-Z]{3})'
    r'(?:_(?P<date>\d{8}))?'
    r'\.(?P<ext>jpg|jpeg|png|webp|tiff)$',
    re.UNICODE
)
DETAIL_CHARS = re.compile(r'^[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*$')

ZONE = {0:"CHANTIER",1:"PLAN",2:"SDB",3:"WC"}
CAT  = {0:"VUE GENERALE",1:"PLOMBERIE",2:"BAIGNOIRE",3:"CARRELAGE",4:"FENETRE",5:"PLAFOND",6:"PLATRERIE",7:"SANITAIRE",8:"PLACARD",9:"EXISTANT"}
VIEW = {"PAN":"VUE PANORAMIQUE","GEN":"VUE GENERALE","DET":"VUE PROCHE","MAC":"VUE MACRO","MGM":"INTERACTION MUR-MUR","MGS":"INTERACTION MUR-SOL","MGP":"INTERACTION MUR-PLAFOND","MGB":"INTERACTION MUR-BAIGNOIRE","DEG":"DEGAT SUR EXISTANT"}

# EXIF orientation tag id
EXIF_ORIENT_TAG = next((k for k,v in ExifTags.TAGS.items() if v == 'Orientation'), 274)

def sha256_file(p, bs=1<<20):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(bs), b''):
            h.update(b)
    return h.hexdigest()

def image_meta(p):
    """retourne (w,h,exif_orientation:int|None,orientation:str)"""
    try:
        with Image.open(p) as im:
            w, h = im.size
            exif_o = None
            try:
                exif = im.getexif()
                if exif:
                    exif_o = int(exif.get(EXIF_ORIENT_TAG)) if exif.get(EXIF_ORIENT_TAG) else None
            except Exception:
                exif_o = None
    except Exception:
        return (0,0,None,"UNKNOWN")
    if w==h: orient = "square"
    elif w>h: orient = "landscape"
    else: orient = "portrait"
    return (int(w), int(h), exif_o, orient)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Racine à scanner")
    ap.add_argument("--out-dir", default=".", help="Dossier de sortie")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    path_manifest = os.path.join(out_dir, "manifest_images.json")
    path_parsed   = os.path.join(out_dir, "manifest_images_parsed.json")
    path_report   = os.path.join(out_dir, "manifest_report.json")
    path_unparsed = os.path.join(out_dir, "unparsed_filenames.txt")

    records = []
    unparsed = []

    total_seen = 0
    for r, _, files in os.walk(root):
        for fn in files:
            total_seen += 1
            m = NAME_PATTERN.match(fn)
            if not m:
                # Ignorer tout fichier hors convention stricte
                continue

            gd = m.groupdict()
            file_ID = int(gd["file_ID"])
            file_ID_str = gd["file_ID"]  # garde le padding "0001"
            detail = gd["detail"]
            viewtype = gd["viewtype"]
            date_raw = gd.get("date") or ""
            ext = gd["ext"].lower()

            # validations strictes
            if not DETAIL_CHARS.match(detail):
                unparsed.append(os.path.relpath(os.path.join(r, fn), root).replace("\\","/"))
                continue
            if viewtype not in VIEW:
                unparsed.append(os.path.relpath(os.path.join(r, fn), root).replace("\\","/"))
                continue

            # derive IDs
            zone_ID = file_ID // 1000
            cat_ID = (file_ID % 1000) // 100
            cat_img_ID = file_ID % 100

            id_ok = (file_ID == zone_ID*1000 + cat_ID*100 + cat_img_ID*10)

            # names
            zone_name = ZONE.get(zone_ID, "UNKNOWN")
            cat_name  = CAT.get(cat_ID, "UNKNOWN")
            viewtype_name = VIEW[viewtype]

            # date normalize
            date_iso = ""
            if date_raw:
                date_iso = f"{date_raw[0:4]}-{date_raw[4:6]}-{date_raw[6:8]}"

            full = os.path.join(r, fn)
            rel = os.path.relpath(full, root).replace("\\","/")
            w, h, exif_o, orient = image_meta(full)
            file_hash = sha256_file(full)

            rec = {
                "rel_path": rel,
                "sha256": file_hash,
                "file_name": fn,
                "file_ID": file_ID,
                "file_ID_str": file_ID_str,   # toujours 4 chiffres "0001"
                "zone_ID": zone_ID,
                "zone_name": zone_name,
                "cat_ID": cat_ID,
                "cat_name": cat_name,
                "cat_img_ID": cat_img_ID,
                "detail": detail,
                "viewtype_ID": viewtype,
                "viewtype_name": viewtype_name,
                "ext": ext,
                "date": date_iso,
                "image_width_px": w,
                "image_height_px": h,
                "orientation": orient,
                "exif_orientation": exif_o,
                "validations": {
                    "regex_match": True,
                    "detail_charset": True,
                    "id_consistency": bool(id_ok),
                    "viewtype_enum": True
                }
            }
            records.append(rec)

    # manifest complet
    with open(path_manifest, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # manifest ingestion minimal + dimensions/orientation
    parsed = []
    for r in records:
        parsed.append({
            "rel_path": r["rel_path"],
            "file_name": r["file_name"],
            "file_ID": r["file_ID"],             # valeur entière
            "file_ID_str": r["file_ID_str"],     # padding "0000"
            "zone_ID": r["zone_ID"],
            "cat_ID": r["cat_ID"],
            "cat_img_ID": r["cat_img_ID"],
            "viewtype_ID": r["viewtype_ID"],
            "date": r["date"],
            "sha256": r["sha256"],
            "image_width_px": r["image_width_px"],
            "image_height_px": r["image_height_px"],
            "orientation": r["orientation"],
            "exif_orientation": r["exif_orientation"]
        })
    with open(path_parsed, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    # report
    report = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds")+"Z",
        "scanned_root": root,
        "total_seen": total_seen,
        "parsed": len(records),
        "ignored_non_conform": total_seen - len(records),
        "unparsed_listed": len(unparsed),  # devrait rester 0 en mode strict
        "pattern_strict": NAME_PATTERN.pattern
    }
    with open(path_report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if unparsed:
        with open(path_unparsed, "w", encoding="utf-8") as f:
            f.write("\n".join(unparsed))

if __name__ == "__main__":
    main()