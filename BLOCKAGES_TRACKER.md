# ArBot-MiniDB - Blockages and Issues Tracker

**Last Updated:** November 10, 2025
**Total Issues:** 14 (4 Critical, 5 Medium, 5 Low/Optional)
**Resolved:** 5
**Status:** 62% operational, 38% blocked

---

## Critical Blockages (Prevent Core Functionality)

### B-01: Missing Preview Generator Script

**Priority:** 🔴 CRITICAL
**Status:** ❌ UNRESOLVED
**Blocking:** Steps 2, 6, 11

**Issue:**
- Script `make_previews_and_augment_json.py` does not exist
- No WebP preview generation capability
- Cannot create optimized images for web and AI analysis

**Impact:**
- AI vision workflow completely blocked
- No `json/images_db.json` database
- ROI cropping cannot be implemented
- GitHub Pages performance suboptimal (serving full JPGs)

**Requirements:**
```python
# make_previews_and_augment_json.py
# Dependencies: pip install pillow
# Input: images/*.jpg
# Output:
#   - images/preview/*.webp (1280-2048px long edge)
#   - json/images_db.json with structure:
#     {
#       "images": [
#         {
#           "id": 1,
#           "file": "2001_SDB_GEN.jpg",
#           "sha256": "abc123...",
#           "width": 3024,
#           "height": 4032,
#           "url_original": "https://raw.githubusercontent.com/.../images/2001_SDB_GEN.jpg",
#           "url_preview": "https://raw.githubusercontent.com/.../images/preview/2001_SDB_GEN.webp",
#           "roi_hints": {"x": 0.5, "y": 0.5, "w": 0.3, "h": 0.3},
#           "phase": "sinistre",
#           "zone_id": 2,
#           "category_id": 0
#         }
#       ]
#     }
```

**Solution:**
Create Python script with:
- Pillow for image processing
- EXIF rotation correction
- WebP compression (quality 85-90)
- SHA-256 calculation
- GitHub RAW URL generation
- ROI default hints (centered 30% box)

**Estimated Effort:** 4-6 hours

**Dependencies:**
- Python 3.11+
- Pillow library
- GitHub repository URL pattern

**Verification:**
```bash
python make_previews_and_augment_json.py \
  --images ./images \
  --out_json ./json/images_db.json \
  --owner Tazevil \
  --repo ArBot-MiniDB \
  --branch main

# Verify outputs:
ls images/preview/*.webp  # Should have 94 files
cat json/images_db.json   # Should have 94 entries
```

---

### B-02: Missing Image Database JSON

**Priority:** 🔴 CRITICAL
**Status:** ❌ UNRESOLVED
**Blocking:** Steps 2, 3, 6, 11

**Issue:**
- File `json/images_db.json` does not exist
- No centralized image metadata
- AI vision prompts cannot load image URLs

**Impact:**
- Step 2 (previews) cannot output metadata
- Step 3 (validation) missing JSON merge
- Step 6 (crops) has no ROI coordinates
- Step 11 (AI vision) completely blocked

**Root Cause:**
- Depends on B-01 (preview generator script)
- Script must create this file as output

**Solution:**
Implement B-01 (preview generator) which will create this file

**Estimated Effort:** Included in B-01 (4-6 hours)

**Verification:**
```bash
# Check JSON structure
cat json/images_db.json | jq '.images | length'
# Should output: 94

# Verify required fields
cat json/images_db.json | jq '.images[0] | keys'
# Should include: id, file, sha256, width, height, url_original, url_preview, roi_hints, phase
```

---

### B-03: Missing Document Indexer Script

**Priority:** 🔴 CRITICAL
**Status:** ❌ UNRESOLVED
**Blocking:** Step 4, 11

**Issue:**
- Script `scripts/generate_docs_index.py` does not exist
- Cannot index PDF documentation for citations
- DTU standards not searchable

**Impact:**
- AI vision cannot cite technical standards
- Manual document lookup required
- No automated compliance checking
- Step 11 prompts cannot reference DTU articles

**Requirements:**
```python
# scripts/generate_docs_index.py
# Input: docs/Normes/**/*.pdf
# Output: json/docs_index.json with structure:
# {
#   "version": "1.0",
#   "generated_at": "2025-11-10T...",
#   "documents": [
#     {
#       "doc_id": "DTU_25.41_1993",
#       "title": "DTU 25.41 - Ouvrages d'étanchéité des façades",
#       "type": "DTU",
#       "category": "Waterproofing",
#       "url": "https://raw.githubusercontent.com/.../docs/Normes/DTU/DTU_25.41_1993.pdf",
#       "pages": 150,
#       "year": 1993
#     }
#   ]
# }
```

**Solution:**
Create Python script with:
- Recursive scan of `docs/Normes/` directory
- PDF metadata extraction (PyPDF2 or pdfplumber)
- Filename parsing for doc_id
- URL generation for GitHub RAW access
- Optional: OCR detection for scanned PDFs

**Estimated Effort:** 3-4 hours

**Dependencies:**
- Python 3.11+
- PyPDF2 or pdfplumber library
- Directory structure: `docs/Normes/{DTU,FT,CR}/*.pdf`

**Verification:**
```bash
python scripts/generate_docs_index.py

# Verify output
cat json/docs_index.json | jq '.documents | length'
# Should output: 40+ (number of PDF files)

# Check structure
cat json/docs_index.json | jq '.documents[0]'
# Should have doc_id, title, type, url fields
```

---

### B-04: Missing Document Index JSON

**Priority:** 🔴 CRITICAL
**Status:** ❌ UNRESOLVED
**Blocking:** Steps 4, 11

**Issue:**
- File `json/docs_index.json` does not exist
- No document citation capability
- AI vision cannot reference standards

**Impact:**
- Same as B-03
- Blocks automated compliance verification
- Manual citation process required

**Root Cause:**
- Depends on B-03 (document indexer script)
- Script must create this file as output

**Solution:**
Implement B-03 (document indexer) which will create this file

**Estimated Effort:** Included in B-03 (3-4 hours)

**Verification:**
Same as B-03

---

## Medium Priority Issues (Reduce Functionality)

### B-05: Missing Sidecar CSV

**Priority:** 🟡 MEDIUM
**Status:** ❓ UNKNOWN (May exist)
**Blocking:** Step 3

**Issue:**
- File `json/images_sidecar.csv` may not exist
- Metadata not available in CSV format
- Human-readable format missing

**Impact:**
- Cannot easily review image metadata in spreadsheet
- No CSV import for other tools
- Validation output incomplete

**Solution:**
Run existing validation script:
```bash
cd C:\Dev\personal\ArBot-MiniDB
python scripts\validate_pack.py \
  --images .\images \
  --out .\json \
  --owner Tazevil \
  --repo ArBot-MiniDB \
  --branch main
```

**Estimated Effort:** 30 minutes (just run script)

**Verification:**
```bash
# Check if file exists
ls json/images_sidecar.csv

# If exists, verify contents
head json/images_sidecar.csv
# Should have headers: file_ID, detail, viewtype, zone, category, classification, url
```

---

### B-07: Missing Checksum Batch Script

**Priority:** 🟡 MEDIUM
**Status:** ❌ UNRESOLVED
**Blocking:** Step 8

**Issue:**
- Script `scripts/generate_checksum.bat` does not exist
- Cannot automate checksum generation on Windows
- Manual hash calculation required

**Impact:**
- Data integrity verification not automated
- No `checksums_sha256.txt` file
- Cannot detect file tampering easily

**Solution:**
Create Windows batch script:
```batch
@echo off
REM scripts\generate_checksum.bat
echo Generating SHA-256 checksums...

REM Hash all images
for %%f in (images\*.jpg) do (
  certutil -hashfile "%%f" SHA256 | findstr /v ":" >> checksums_sha256.txt
)

REM Hash all PDFs
for /r docs %%f in (*.pdf) do (
  certutil -hashfile "%%f" SHA256 | findstr /v ":" >> checksums_sha256.txt
)

echo Done. Output: checksums_sha256.txt
```

**Alternative (Cross-platform):**
Create Python script:
```python
# scripts/generate_checksum.py
import hashlib
from pathlib import Path

def hash_file(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

# Hash all files
with open('checksums_sha256.txt', 'w') as out:
    for img in Path('images').glob('*.jpg'):
        out.write(f"{hash_file(img)}  {img}\n")
    for pdf in Path('docs').rglob('*.pdf'):
        out.write(f"{hash_file(pdf)}  {pdf}\n")
```

**Estimated Effort:** 1-2 hours

---

### B-08: SHA-256 Missing from Manifest

**Priority:** 🟡 MEDIUM
**Status:** ⚠️ PARTIAL
**Blocking:** Step 8

**Issue:**
- `manifest.json` exists but lacks `global_sha256` field
- No cryptographic signature for project state
- Cannot verify manifest integrity

**Impact:**
- Incomplete integrity verification
- Cannot detect manifest tampering
- Audit trail incomplete

**Current State:**
```json
// manifest.json
{
  "version": "1.0.0",
  "checksum_sha256": "UNKNOWN",  // ← Should be calculated
  // ...
}
```

**Solution:**
Update `scripts/build_manifest_strict.py`:
```python
import hashlib
import json

# Calculate hash of all files
def calculate_global_hash(manifest_data):
    # Serialize manifest without checksum field
    temp_manifest = {k: v for k, v in manifest_data.items() if k != 'checksum_sha256'}
    manifest_str = json.dumps(temp_manifest, sort_keys=True)
    return hashlib.sha256(manifest_str.encode()).hexdigest()

# Add to manifest
manifest['checksum_sha256'] = calculate_global_hash(manifest)
```

**Estimated Effort:** 1-2 hours

---

### B-09: GitHub Actions Workflow Not Verified

**Priority:** 🟡 MEDIUM
**Status:** ⚠️ EXISTS BUT UNVERIFIED
**Blocking:** Step 10

**Issue:**
- File `.github/workflows/build-index.yml` exists
- Contents not verified against runbook requirements
- May not match Step 10 specifications

**Impact:**
- Automation may be incomplete
- Triggers may not fire correctly
- Generated files may not auto-commit

**Required Workflow (per Runbook):**
```yaml
name: Build All
on:
  push:
    paths:
      - 'images/**'
      - 'scripts/**'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pillow

      - name: Generate previews
        run: python make_previews_and_augment_json.py --images ./images --out_json ./json/images_db.json

      - name: Validate images
        run: python scripts/validate_pack.py --images ./images --out ./json

      - name: Generate gallery
        run: python generate_index_html.py --images ./images --out ./index.html

      - name: Commit changes
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git add images/preview/ json/ index.html
          git commit -m "Auto-update: previews, JSON, gallery" || echo "No changes"
          git push
```

**Solution:**
1. Read `.github/workflows/build-index.yml`
2. Compare with required workflow above
3. Update if needed
4. Test workflow on sample push

**Estimated Effort:** 1-2 hours

**Verification:**
```bash
# Push a test change
echo "test" > test_trigger.txt
git add test_trigger.txt
git commit -m "Test workflow trigger"
git push

# Check Actions tab on GitHub
# Verify workflow runs and commits changes
```

---

### B-10: AI Vision Configuration Missing

**Priority:** 🟡 MEDIUM
**Status:** ❌ NOT CONFIGURED
**Blocking:** Step 11

**Issue:**
- No OpenAI API configuration
- Vision prompts defined in pipeline but not implemented
- No integration with GPT-4o

**Impact:**
- Cannot run automated defect detection
- No AI-powered analysis
- Manual review required

**Requirements (from Runbook Step 11):**
- OpenAI API key
- GPT-4o model access
- Temperature ≤ 0.2
- Prompts for:
  - Pass 0: CSV pre-analysis
  - Pass 1: JSON structured output with citations
  - Pass 2: SVG overlay annotations

**Solution:**
1. Create `.env` file:
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.2
```

2. Create prompt files or scripts
3. Implement batching with SUIVANT/STOP commands

**Estimated Effort:** 3-4 hours (after B-01, B-02, B-03, B-04 resolved)

**Dependencies:**
- B-01, B-02: Images database
- B-03, B-04: Documents index
- OpenAI API account

---

## Low Priority Issues (Optional Features)

### B-11: Missing ROI Crop Generator (OPTIONAL)

**Priority:** 🟢 LOW (Optional)
**Status:** ❌ NOT IMPLEMENTED
**Blocking:** Step 6 (optional)

**Issue:**
- Script `make_crops_from_roi.py` does not exist
- No zoomed defect images
- Cannot generate detail crops

**Impact:**
- No automated ROI cropping
- Must manually crop defect areas if needed
- Slightly reduced AI analysis precision

**Use Case:**
Generate tight crops around defects for high-resolution analysis

**Solution (if needed):**
```python
# make_crops_from_roi.py
# Read ROI coordinates from json/images_db.json
# For each image with ROI:
#   - Load original image
#   - Crop to ROI box
#   - Save to images/crop/{filename}_crop.jpg
#   - Add url_crop to JSON
```

**Estimated Effort:** 3-4 hours

**Decision:** Implement only if needed for detailed defect analysis

---

### B-12: Missing Image Tiling Script (OPTIONAL)

**Priority:** 🟢 LOW (Optional)
**Status:** ❌ NOT IMPLEMENTED
**Blocking:** Step 7 (optional)

**Issue:**
- Script `tile_1024_overlap.py` does not exist
- No patch-based image analysis
- Cannot tile large images

**Impact:**
- Cannot detect small defects in very large images
- Must analyze full-size images (slower)

**Use Case:**
Tile 4K+ images into 1024x1024 patches with 10% overlap for small defect detection

**Solution (if needed):**
```python
# tile_1024_overlap.py
# For each image:
#   - Calculate grid (1024x1024 tiles, 10% overlap)
#   - Generate patches
#   - Save to tiles/ directory
#   - Create tiles_map.json linking patches to originals
```

**Estimated Effort:** 4-5 hours

**Decision:** Implement only if analyzing very large images (>4K resolution)

---

### B-13: HTML Gallery Generator Missing

**Priority:** 🟢 LOW (Alternative Exists)
**Status:** ⚠️ WORKAROUND EXISTS
**Blocking:** Step 5

**Issue:**
- Script `generate_index_html.py` does not exist at root
- Runbook expects this script

**Impact:**
- None - `index.html` already exists
- May have been generated manually or by different script

**Current Workaround:**
`index.html` exists and appears functional

**Solution:**
- Option 1: Create script to match runbook (for future regeneration)
- Option 2: Document that HTML is manually maintained
- Option 3: Accept current state (lowest priority)

**Estimated Effort:** 2-3 hours (if standardization needed)

---

## Resolved Issues

### R-01: File ID Formula Error ✅

**Status:** ✅ RESOLVED (2025-11-10)
**Issue:** Formula incorrectly documented as `zone*1000 + cat*100 + img*10`
**Resolution:** Corrected to `zone*1000 + cat*100 + img` in all files
**Fixed In:**
- `json/name_convention.json`
- `scripts/build_manifest_strict.py`
- `scripts/REGEX_REFERENCE.py`
- Documentation

---

### R-02: Category 9 "EXISTANT" Missing ✅

**Status:** ✅ RESOLVED (2025-11-10)
**Issue:** Category 9 not defined in validation scripts
**Resolution:** Added to all category dictionaries
**Fixed In:**
- `scripts/validate_pack.py`
- `validate_images.py`

---

### R-03: Typo in Category Name ✅

**Status:** ✅ RESOLVED (2025-11-10)
**Issue:** "PLATERIE" instead of "PLATRERIE"
**Resolution:** Corrected spelling in all files
**Fixed In:**
- `scripts/validate_pack.py`
- Documentation

---

### R-04: Hyphen Support in Regex ✅

**Status:** ✅ RESOLVED (2025-11-10)
**Issue:** Regex pattern didn't support hyphens in DETAIL field
**Resolution:** Updated pattern to `[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*`
**Fixed In:**
- `scripts/REGEX_REFERENCE.py`

---

### R-05: Case Enforcement Missing ✅

**Status:** ✅ RESOLVED (2025-11-10)
**Issue:** `re.IGNORECASE` flag allowed lowercase (convention requires UPPERCASE)
**Resolution:** Removed flag from regex compilation
**Fixed In:**
- `scripts/REGEX_REFERENCE.py`

---

## Priority Action Plan

### Immediate (This Week)
1. ✅ Review runbook and identify gaps → **COMPLETE**
2. 🔴 Implement B-01: Preview generator → **8-12 hours**
3. 🔴 Implement B-03: Document indexer → **6-8 hours**
4. 🟡 Generate B-05: CSV sidecar → **30 minutes**

### Short-term (Next 2 Weeks)
5. 🟡 Fix B-07: Checksum script → **2 hours**
6. 🟡 Fix B-08: Manifest SHA-256 → **2 hours**
7. 🟡 Verify B-09: GitHub Actions → **2 hours**

### Medium-term (Next Month)
8. 🟡 Configure B-10: AI vision integration → **4 hours**
9. 🟢 Optional: B-11 ROI crops (if needed)
10. 🟢 Optional: B-12 Image tiling (if needed)

---

## Success Metrics

### Critical Path Complete
- [ ] All 4 critical blockages (B-01 to B-04) resolved
- [ ] `json/images_db.json` generated with 94 entries
- [ ] `json/docs_index.json` generated with 40+ entries
- [ ] AI vision workflow testable

### Full Compliance
- [ ] All medium priority issues resolved
- [ ] SHA-256 integrity checks operational
- [ ] GitHub Actions workflow verified
- [ ] Optional features decided (implement or document skip)

---

**Last Updated:** November 10, 2025
**Next Review:** After Phase 1 completion (B-01, B-03 resolved)
