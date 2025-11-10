#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot Vision Pipeline Setup Script
Adapts the pipeline-all-in-one configuration to match current project structure
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Pipeline configuration
PACK = "ArBot-Vision-Pack_v0.7.1"
ROOT = PACK
MOD = os.path.join(ROOT, "modules")
SCHEMAS = os.path.join(ROOT, "schemas")
PROMPTS = os.path.join(ROOT, "prompts")

# Create directories
os.makedirs(MOD, exist_ok=True)
os.makedirs(SCHEMAS, exist_ok=True)
os.makedirs(PROMPTS, exist_ok=True)

print(f"Setting up ArBot Vision Pipeline: {PACK}")
print(f"Directories: {MOD}, {SCHEMAS}, {PROMPTS}")

# Load existing project data to adapt paths
try:
    with open("json/images_db.json", "r", encoding="utf-8") as f:
        images_db = json.load(f)
    print(f"[OK] Loaded images_db.json: {images_db.get('count', 0)} images")
except FileNotFoundError:
    print("[WARNING] images_db.json not found, using defaults")
    images_db = {"count": 94}

try:
    with open("json/docs_index.json", "r", encoding="utf-8") as f:
        docs_index = json.load(f)
    print(f"[OK] Loaded docs_index.json: {docs_index.get('total_documents', 0)} documents")
except FileNotFoundError:
    print("[WARNING] docs_index.json not found, using defaults")
    docs_index = {"total_documents": 16}

# Check knowledge base files
kb_files = {
    "articles_validated": "json/articles_validated.jsonl",
    "clauses_validated_exhaustive": "json/clauses_validated.jsonl",
    "clauses_full": "json/clauses_full.jsonl",
    "index_keywords": "json/index_keywords.jsonl",
    "defaut_auto_map": None,  # Will be generated
    "ontology_enriched": "json/ontology.enriched.json",
    "ontology_validated": "json/ontology.validated.json"
}

print("\n=== Creating Pipeline Configuration ===")

# ==================== SCHEMAS ====================

# Schema: annotations 1.1.1
annotations_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:arbot:schema:annotations:1.1.1",
    "$anchor": "annotation",
    "title": "ArBot Annotations Schema",
    "version": "1.1.1",
    "type": "object",
    "required": ["id_defaut", "categorie", "type_defaut", "origin_layer", "gravite_technique", "polygons_norm"],
    "additionalProperties": False,
    "properties": {
        "id_defaut": {
            "type": "string",
            "pattern": "^[A-Za-z0-9_-]+_[A-Za-z0-9_-]+_D\\d{2}$"
        },
        "categorie": {
            "type": "string",
            "enum": ["ETANCHEITE", "PLOMBERIE", "CARRELAGE", "STRUCTURE", "MENUISERIE", "CVC", "ELECTRICITE", "AUTRE"]
        },
        "type_defaut": {"type": "string"},
        "origin_layer": {
            "type": "string",
            "enum": ["SURFACE", "SUPPORT", "STRUCTUREL", "INFRA"]
        },
        "gravite_technique": {"type": "integer", "enum": [1, 2, 3]},
        "polygons_norm": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "array",
                "minItems": 6,
                "maxItems": 30,
                "items": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": [
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001},
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001}
                    ]
                }
            },
            "description": "Polygones fermes prioritaires."
        },
        "polylines_norm": {
            "type": "array",
            "items": {
                "type": "array",
                "minItems": 6,
                "maxItems": 30,
                "items": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": [
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001},
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001}
                    ]
                }
            },
            "description": "Fallback optionnel si polygons_norm < 2."
        },
        "mask_polygon_norm": {
            "type": "array",
            "items": {
                "type": "array",
                "minItems": 6,
                "maxItems": 100,
                "items": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": [
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001},
                        {"type": "number", "minimum": 0.0, "maximum": 1.0, "multipleOf": 0.0001}
                    ]
                }
            }
        },
        "style": {"type": "string", "enum": ["CRITIQUE", "MAJEUR", "MINEUR", "INFO"]},
        "incertitude": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "regle_ref": {
            "type": "object",
            "required": ["doc_id", "source_page", "article_id"],
            "properties": {
                "doc_id": {"type": "string"},
                "source_page": {"type": "string"},
                "article_id": {"type": "string"}
            },
            "additionalProperties": False
        },
        "x_extensions": {"type": "object"}
    }
}

with open(os.path.join(SCHEMAS, "annotations.schema.json"), "w", encoding="utf-8") as f:
    json.dump(annotations_schema, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {SCHEMAS}/annotations.schema.json")

# Schema: vision_analysis 1.0.0 (simplified)
vision_analysis_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:arbot:schema:vision_analysis:1.0.0",
    "$anchor": "visionAnalysis",
    "title": "ArBot Vision Analysis",
    "type": "object",
    "required": ["step", "active", "skipped", "status", "inputs", "outputs"],
    "additionalProperties": False,
    "properties": {
        "step": {"type": "string", "const": "VISION_ANALYSIS"},
        "active": {"type": "boolean"},
        "skipped": {"type": "boolean"},
        "status": {"type": "string", "enum": ["success", "error"]},
        "inputs": {"type": "object"},
        "outputs": {"type": "object"}
    }
}

with open(os.path.join(SCHEMAS, "vision_analysis.schema.json"), "w", encoding="utf-8") as f:
    json.dump(vision_analysis_schema, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {SCHEMAS}/vision_analysis.schema.json")

# ==================== MODULES ====================

# Module: runtime.paths_filters (ADAPTED to current project structure)
runtime_paths_filters = {
    "module": "runtime.paths_filters",
    "version": "1.0.0",
    "paths": {
        "root": ".",
        "photos_dir": "./images",  # ADAPTED: was ./photos
        "docs_dir": "./docs/Normes",  # ADAPTED: was ./docs
        "tables_dir": "./docs/Context/ARCHIVE",  # ADAPTED: was ./tables
        "kb_root": "./json"  # ADAPTED: was ./kb
    },
    "filters": {
        "images_ext": [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic", ".heif"],
        "docs_ext": [".pdf", ".docx"],
        "tables_ext": [".xlsx", ".csv"]
    }
}

with open(os.path.join(MOD, "runtime.paths_filters.json"), "w", encoding="utf-8") as f:
    json.dump(runtime_paths_filters, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {MOD}/runtime.paths_filters.json")

# Module: kb.map (ADAPTED to json/ directory)
kb_map = {
    "module": "kb.map",
    "version": "1.0.0",
    "articles_validated": "./json/articles_validated.jsonl",
    "clauses_validated_exhaustive": "./json/clauses_validated.jsonl",
    "clauses_full": "./json/clauses_full.jsonl",
    "index_keywords": "./json/index_keywords.jsonl",
    "defaut_auto_map": "./json/defaut_auto_map.jsonl",
    "ontology_enriched": "./json/ontology.enriched.json",
    "ontology_validated": "./json/ontology.validated.json"
}

with open(os.path.join(MOD, "kb.map.json"), "w", encoding="utf-8") as f:
    json.dump(kb_map, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {MOD}/kb.map.json")

# Module: pipeline.sequence
pipeline_sequence = {
    "module": "pipeline.sequence",
    "version": "1.0.0",
    "sequence": ["BOOT", "INGESTION", "VISION_ANALYSIS", "DEFECT_DETECTION", "NORM_REFERENCE_LINK", "CONTEXT_INTEGRATION", "HYPER_GRAVITY", "CAUSALITY_INFERENCE", "JSON_VALIDATION", "REPORTING"],
    "defaults_active": {
        "BOOT": True,
        "INGESTION": True,
        "VISION_ANALYSIS": True,
        "DEFECT_DETECTION": True,
        "NORM_REFERENCE_LINK": True,
        "CONTEXT_INTEGRATION": False,
        "HYPER_GRAVITY": True,
        "CAUSALITY_INFERENCE": False,
        "JSON_VALIDATION": True,
        "REPORTING": False
    }
}

with open(os.path.join(MOD, "pipeline.sequence.json"), "w", encoding="utf-8") as f:
    json.dump(pipeline_sequence, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {MOD}/pipeline.sequence.json")

# ==================== CONTROL PANEL ====================

controlpanel = {
    "schema_version": "0.7.1",
    "generated_at": datetime.now().isoformat() + "Z",
    "modules": {
        "runtime_paths_filters": "./modules/runtime.paths_filters.json",
        "kb_map": "./modules/kb.map.json",
        "pipeline_sequence": "./modules/pipeline.sequence.json"
    },
    "paths_filters": runtime_paths_filters,
    "kb": kb_map,
    "pipeline": pipeline_sequence,
    "project_stats": {
        "images_count": images_db.get("count", 0),
        "documents_count": docs_index.get("total_documents", 0),
        "analysis_results": "docs/To validate/ArBot-Core,_v1.4_OUT_JSON"
    }
}

with open(os.path.join(ROOT, "controlpanel.json"), "w", encoding="utf-8") as f:
    json.dump(controlpanel, f, indent=2, ensure_ascii=False)
print(f"[OK] Created {ROOT}/controlpanel.json")

# ==================== PROMPTS ====================

prompts = {
    "phase1_ingestion_prompt.txt": "INGESTION\nChecklist: chemins, filtres, inventaire, compteurs, schemas.\nSortie: urn:arbot:schema:ingestion_step:1.0.0",
    "phase2_vision_analysis_prompt.txt": "VISION_ANALYSIS\nChecklist: core actif, mode, high_gravity, annotations conformes, frames exhaustifs.\nSortie: urn:arbot:schema:vision_analysis:1.0.0",
    "phase3_defect_detection_prompt.txt": "DEFECT_DETECTION\nChecklist: aggregation detections->defauts, id_defaut, categorie, origin_layer, gravite. Fallback polylines si <2 polygones.\nSortie: structure pour DEF_ALL",
    "phase4_norm_reference_link_prompt.txt": "NORM_REFERENCE_LINK\nChecklist: defaut_auto_map, citations completes {doc_id,source_file,source_page,article_id}.\nSortie: liens norme par defaut",
    "phase8_reporting_prompt.txt": "REPORTING\nChecklist: miroir, coherence DEF_ALL, annexe normative.\nSortie: urn:arbot:schema:report_mirror:1.0.0"
}

for prompt_file, content in prompts.items():
    with open(os.path.join(PROMPTS, prompt_file), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Created {PROMPTS}/{prompt_file}")

print("\n=== Pipeline Setup Complete ===")
print(f"Pipeline pack created in: {ROOT}/")
print(f"Control panel: {ROOT}/controlpanel.json")
print(f"\nNext steps:")
print(f"  1. Run: python run_pipeline.py")
print(f"  2. Review: {ROOT}/controlpanel.json")

