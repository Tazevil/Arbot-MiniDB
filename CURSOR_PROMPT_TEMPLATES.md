# Cursor AI Prompt Templates for ArBot-MiniDB

Copy and paste these prompts directly into Cursor AI for specific tasks.

---

## Template 1: Implement ROI Cropping (Step 6)

```
I need help implementing ROI cropping for the ArBot-MiniDB project.

Context:
- I have 94 images in the `images/` folder
- Each image has ROI (Region of Interest) hints in `json/images_db.json`
- ROI hints are stored as: {"x": 0.325, "y": 0.325, "w": 0.35, "h": 0.35} (normalized coordinates 0-1)

Task:
Create a Python script `scripts/crop_roi.py` that:
1. Reads json/images_db.json
2. For each image, extracts the ROI region using the normalized coordinates
3. Saves cropped images to `images/crops/` maintaining the original filename
4. Handles edge cases (coordinates outside image bounds, invalid values)
5. Prints progress and summary statistics

Requirements:
- Use PIL (Pillow) for image processing
- Support jpg, jpeg, png, webp, tiff formats
- Create output directory if it doesn't exist
- Handle errors gracefully
- Add command-line arguments: --images, --crops_output, --verbose

The script should produce output like:
  [OK] Cropped 94 images to images/crops/
  [OK] ROI statistics:
    - Average crop size: 35% of original
    - Min/Max coordinates verified

After implementation, verify pipeline integrity:
  python verify_pipeline_integrity.py
```

---

## Template 2: Implement Image Tiling (Step 7)

```
I need help implementing image tiling for the ArBot-MiniDB project.

Context:
- I have 94 images in the `images/` folder with various sizes
- I need to create overlapping 1024px patches for regional analysis
- Tile size should be 1024x1024 pixels
- Overlap should be 256 pixels (25% overlap)

Task:
Create a Python script `scripts/tile_images.py` that:
1. Reads images from `images/` folder
2. For each image, generates overlapping 1024px square tiles
3. Saves tiles to `images/tiles/` with naming: {image_id}_{tile_row}_{tile_col}.webp
4. Creates a tile metadata file `json/tiles_index.json`
5. Skips images smaller than 1024px or handles appropriately

Requirements:
- Use PIL for image processing
- Generate tiles in WebP format (quality 85)
- Create tile index with: image_id, tile_count, tile_positions
- Support command-line arguments: --images, --tile_size, --overlap, --tiles_output
- Print statistics: total tiles generated, coverage analysis

The script should produce:
  [OK] Generated tiles for 94 images
  [OK] Total tiles: XXX
  [OK] Tile index: json/tiles_index.json

After implementation, verify pipeline integrity.
```

---

## Template 3: Generate SHA-256 Manifest (Step 8)

```
I need help implementing SHA-256 cryptographic verification for the ArBot-MiniDB project.

Context:
- I need to verify integrity of 94 images and 16 documents
- Images are in `images/` (original files)
- Documents are in `docs/Normes/`
- I want to create a verification manifest

Task:
Create a Python script `scripts/generate_manifest_sha256.py` that:
1. Scans all images in `images/` folder (not previews)
2. Scans all PDFs in `docs/Normes/` folder recursively
3. Calculates SHA-256 hash for each file
4. Creates `json/manifest_sha256.json` with:
   - file_path
   - file_size
   - sha256_hash
   - last_modified
5. Creates a verification script to check integrity

Requirements:
- Use hashlib.sha256() for hashing
- Process files in chunks (don't load entire file in memory)
- Format hashes as hex strings
- Add command-line arguments: --scan_dirs, --output_json, --verify

The manifest structure should be:
{
  "generated_at": "2025-11-10T...",
  "total_files": 110,
  "files": [
    {
      "path": "images/0001_SDB_GEN_20250818.jpg",
      "size_bytes": 2456800,
      "sha256": "abc123...",
      "type": "image"
    }
  ]
}

Output should show:
  [OK] Scanned 94 images: SHA-256 calculated
  [OK] Scanned 16 documents: SHA-256 calculated
  [OK] Manifest: json/manifest_sha256.json
```

---

## Template 4: Setup GitHub Actions (Step 10)

```
I need help setting up GitHub Actions automation for the ArBot-MiniDB project.

Context:
- Repository: https://github.com/Tazevil/ArBot-MiniDB
- Branch: main
- The project has image validation and database generation scripts
- I want to automate: validation, preview generation, database updates

Task:
Create a GitHub Actions workflow file `.github/workflows/update-databases.yml` that:

1. Triggers on:
   - Push to main branch (only images/ or docs/Normes/ changes)
   - Manual workflow dispatch

2. Jobs:
   a. Validate Images
      - Run: scripts/validate_images.py
      - Generate: json/validation_report.json
      - Fail if validation has critical errors

   b. Generate Previews
      - Run: scripts/make_previews_and_augment_json.py
      - Generate: images/preview/ and json/images_db.json
      - Skip if no image changes

   c. Index Documents
      - Run: scripts/generate_docs_index.py
      - Generate: json/docs_index.json
      - Skip if no doc changes

   d. Verify Pipeline
      - Run: verify_pipeline_integrity.py
      - Fail if critical errors found

   e. Commit & Push
      - Commit updated JSON and previews
      - Push back to main branch

Requirements:
- Use Python 3.11
- Install dependencies: pillow, requests
- Run on ubuntu-latest
- Use actions/checkout@v3 and actions/setup-python@v4
- Handle git credentials for push-back

The workflow should produce:
  ✓ Images validated
  ✓ Previews generated (94)
  ✓ Database updated
  ✓ Integrity verified
  ✓ Changes committed and pushed

Provide the complete .yml file ready to commit.
```

---

## Template 5: Quick Status Check

```
Summarize the current status of the ArBot-MiniDB project:

1. List all JSON databases and their item counts
2. Verify all 94 images are present in images/
3. Verify all 94 WebP previews exist in images/preview/
4. Check pipeline integrity status
5. List any missing or broken files
6. Show next available tasks

Format as:
  DATABASE STATUS
  IMAGE STATUS
  DOCUMENT STATUS
  PIPELINE STATUS
  ISSUES (if any)
  NEXT STEPS
```

---

## Template 6: Fix a Specific Issue

```
I encountered this issue in the ArBot-MiniDB project:

[ISSUE DESCRIPTION]

Context:
- Project location: C:\Dev\personal\ArBot-MiniDB
- Related files: [list files affected]
- Error message (if any): [error]

Please help me:
1. Identify the root cause
2. Propose a solution
3. Implement the fix
4. Verify the fix doesn't break other things
5. Update documentation if needed

After fixing, run:
  python verify_pipeline_integrity.py
```

---

## Template 7: Batch Rename Documentation Files

```
I need to batch rename files in docs/Normes/ that have naming inconsistencies:

Pattern to fix: Files with double extensions (.docx.pdf) or extra spaces

Current issues:
- Some files have spaces in filenames
- Some have double extensions
- Some have trailing spaces in code fields

Task:
1. Scan docs/Normes/ recursively
2. Identify all files with:
   - Double extensions (.docx.pdf, ..pdf)
   - Leading/trailing spaces in filename
   - Invalid character sequences
3. Rename them to follow standard pattern: [TYPE]_[CODE]_[DESCRIPTION].pdf
4. Update json/docs_index.json accordingly
5. Verify all files still accessible
6. Run pipeline integrity check

Show me:
- List of files to be renamed (before/after)
- Confirmation before executing
- Summary of changes made
- Verification results
```

---

## Template 8: Create Data Analysis Report

```
Generate a comprehensive analysis of the ArBot-MiniDB datasets:

1. IMAGE STATISTICS
   - Count by zone (0=chantier, 1=plan, etc.)
   - Count by category
   - Count by viewtype
   - Date range distribution
   - Average image size

2. DOCUMENT STATISTICS
   - Count by type (DTU, FT, CR, NOTICE, OTHER)
   - Size range and total size
   - Standards coverage

3. COVERAGE ANALYSIS
   - Which image zones are well-represented
   - Which document types are available
   - Gaps in coverage

4. DATA QUALITY
   - Check for orphaned images/docs
   - Verify all URLs are valid format
   - Check for missing metadata

5. READINESS FOR AI
   - Can GPT-4o Vision access all images via URLs
   - Are ROI hints present for all images
   - Are reference documents indexed

Output should be: ANALYSIS_REPORT.md

Include:
- Statistics tables
- Charts (ASCII-based)
- Recommendations for improvement
- Ready/not-ready assessment for each component
```

---

## How to Use These Templates

1. Copy the template text
2. Paste into Cursor AI or Claude
3. Replace bracketed sections [LIKE THIS] with your details
4. Press Enter and let Cursor implement
5. Review the output
6. Ask for adjustments if needed

---

## Key Commands to Remember

```bash
# Verify everything is working
python verify_pipeline_integrity.py

# Fix issues automatically
python fix_pipeline_issues.py

# Validate images
python scripts/validate_images.py

# Generate docs index
python scripts/generate_docs_index.py

# Generate previews
python scripts/make_previews_and_augment_json.py \
  --images images \
  --out_json json/images_db.json \
  --owner Tazevil \
  --repo ArBot-MiniDB \
  --branch main
```

---

**Last Updated:** November 10, 2025
**Status:** All templates verified and ready to use
