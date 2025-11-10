#!/usr/bin/env python3
# make_previews_and_augment_json.py
# Previews WebP + orientation EXIF + url_preview + roi_hints

from pathlib import Path
import argparse, json, re
from datetime import datetime, timezone
from PIL import Image, ImageOps  # pip install pillow

EXTS = {".jpg",".jpeg",".png",".webp",".tiff"}

RX_A = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_([A-Z0-9]{2,6})_(\d{8})\.(jpg|jpeg|png|webp|tiff)$', re.I)
RX_B = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_(\d{4})\.(jpg|jpeg|png|webp|tiff)$', re.I)
RX_C = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_([A-Z0-9]{2,6})\.(jpg|jpeg|png|webp|tiff)$', re.I)

def parse_spec_and_phase(fname:str):
    up = fname.upper()
    if RX_A.match(up):
        return RX_A.match(up).group(3), "chantier"
    if RX_B.match(up):
        return RX_B.match(up).group(3), "sinistre"
    m = RX_C.match(up)
    if m:
        return m.group(3), "sinistre"
    return "UNKNOWN", "UNKNOWN"

def first4_id(fname:str):
    m = re.match(r'^(\d{4})_', fname)
    return m.group(1) if m else "UNKNOWN"

def build_raw(owner, repo, branch, relposix:str):
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{relposix}"

def ensure_dir(p:Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def gen_preview(src:Path, dst:Path, max_side:int=1280, quality:int=85):
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        scale = max_side / max(w, h)
        if scale < 1.0:
            im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        ensure_dir(dst)
        im.save(dst, "WEBP", quality=quality, method=6)

def default_roi(spec:str):
    s = 0.30
    if spec == "GEN":
        s = 0.35
    elif spec == "DET":
        s = 0.22
    x0 = round((1.0 - s)/2, 3)
    y0 = round((1.0 - s)/2, 3)
    return [{"x": x0, "y": y0, "w": round(s,3), "h": round(s,3)}]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default="images")
    ap.add_argument("--out_json", default="json/images_db.json")
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", default="main")
    ap.add_argument("--preview_dir", default="images/preview")
    ap.add_argument("--max_side", type=int, default=1280)
    ap.add_argument("--quality", type=int, default=85)
    args = ap.parse_args()

    images_root = Path(args.images)
    preview_root = Path(args.preview_dir)
    out_json = Path(args.out_json)

    # Charger JSON existant si présent
    items = []
    by_basename = {}
    if out_json.exists():
        try:
            data = json.loads(out_json.read_text(encoding="utf-8"))
            items = data.get("items", [])
            for it in items:
                if "url" in it:
                    base = it["url"].split("/")[-1]
                    by_basename[base] = it
        except Exception:
            items = []

    updated = set()
    count_previews = 0

    for p in sorted(images_root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue

        rel_from_repo = p.relative_to(Path(".")).as_posix()       # images/xxx.jpg
        basename = p.name

        # Générer preview
        preview_rel = Path(args.preview_dir) / p.relative_to(images_root)
        preview_rel = preview_rel.with_suffix(".webp")
        gen_preview(p, preview_rel, max_side=args.max_side, quality=args.quality)
        count_previews += 1

        # URLs
        url_orig = build_raw(args.owner, args.repo, args.branch, rel_from_repo)
        url_prev = build_raw(args.owner, args.repo, args.branch, preview_rel.as_posix())

        # Spec + phase + roi
        spec, phase = parse_spec_and_phase(basename)
        roi = default_roi(spec)

        if basename in by_basename:
            it = by_basename[basename]
            it["url_preview"] = url_prev
            it["roi_hints"] = roi
            if "phase" not in it or it.get("phase") in ("", "UNKNOWN"):
                it["phase"] = phase
        else:
            # Ce cas ne devrait pas arriver si Étape 2 est exécutée avant
            it = {
                "id": first4_id(basename),
                "title": basename,
                "url": url_orig,
                "url_preview": url_prev,
                "phase": phase,
                "roi_hints": roi,
                "created_at": datetime.now(timezone.utc).date().isoformat(),
                "tags": []
            }
            items.append(it)
            by_basename[basename] = it

        updated.add(basename)

    payload = {
        "db_name": "ArbotMiniDB_Augmented",
        "created_at": datetime.now(timezone.utc).date().isoformat(),
        "count": len(items),
        "items": items
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] previews: {count_previews} -> {preview_root}")
    print(f"[OK] JSON: {out_json} (items={len(items)})")

if __name__ == "__main__":
    main()