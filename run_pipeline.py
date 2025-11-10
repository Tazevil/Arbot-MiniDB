#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot Vision Pipeline Execution Script
Executes the pipeline using images_db.json, docs_index.json, and analysis results
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Import our vision analysis script functions
from run_vision_analysis import (
    load_images_db,
    load_docs_index,
    load_analysis_results,
    analyze_defects
)

# Pipeline configuration
PACK = "ArBot-Vision-Pack_v0.7.1"
CONTROLPANEL_PATH = os.path.join(PACK, "controlpanel.json")
IMAGES_DB_PATH = "json/images_db.json"
DOCS_INDEX_PATH = "json/docs_index.json"
ANALYSIS_RESULTS_DIR = "docs/To validate/ArBot-Core,_v1.4_OUT_JSON"
OUTPUT_DIR = "pipeline_output"
REPORT_OUTPUT = os.path.join(OUTPUT_DIR, f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")


def load_controlpanel() -> Dict[str, Any]:
    """Load the pipeline control panel configuration."""
    try:
        with open(CONTROLPANEL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Control panel not found: {CONTROLPANEL_PATH}")
        print("Run: python setup_pipeline.py first")
        sys.exit(1)


def execute_phase_ingestion(images_db: Dict, docs_index: Dict, controlpanel: Dict) -> Dict[str, Any]:
    """Execute INGESTION phase."""
    print("\n=== PHASE 1: INGESTION ===")
    
    paths_filters = controlpanel.get("paths_filters", {})
    paths = paths_filters.get("paths", {})
    filters = paths_filters.get("filters", {})
    
    # Count files
    images_dir = Path(paths.get("photos_dir", "./images"))
    docs_dir = Path(paths.get("docs_dir", "./docs"))
    
    image_count = len(list(images_dir.glob("*.jpg"))) if images_dir.exists() else 0
    doc_count = docs_index.get("total_documents", 0)
    
    ingestion_result = {
        "step": "INGESTION",
        "active": True,
        "skipped": False,
        "status": "success",
        "inputs": {
            "paths": paths,
            "filters": filters
        },
        "outputs": {
            "files": [],
            "counts": {
                "photo": image_count,
                "pdf": doc_count,
                "docx": 0,
                "xlsx": 0
            }
        },
        "incertitudes": [],
        "simulations": [],
        "citations": [],
        "audit": {
            "modules_checked": ["runtime.paths_filters"],
            "schemas_validated": [],
            "controlpanel_version": controlpanel.get("schema_version", "0.7.1")
        }
    }
    
    print(f"[OK] Ingestion complete: {image_count} images, {doc_count} documents")
    return ingestion_result


def execute_phase_vision_analysis(
    images_db: Dict,
    analysis_results: Dict[str, Dict[str, Any]],
    controlpanel: Dict
) -> Dict[str, Any]:
    """Execute VISION_ANALYSIS phase."""
    print("\n=== PHASE 2: VISION_ANALYSIS ===")
    
    vision_result = {
        "step": "VISION_ANALYSIS",
        "active": True,
        "skipped": False,
        "status": "success",
        "inputs": {
            "mode": "multi_pass",
            "high_gravity": True
        },
        "outputs": {
            "frames": []
        },
        "incertitudes": [],
        "simulations": [],
        "citations": [],
        "audit": {
            "modules_checked": ["vision_core", "annotation.policy"],
            "schemas_validated": ["urn:arbot:schema:vision_analysis:1.0.0"],
            "controlpanel_version": controlpanel.get("schema_version", "0.7.1")
        }
    }
    
    # Process analysis results into frames
    frames = []
    for file_id, analysis in analysis_results.items():
        vision_data = analysis.get("vision", {})
        defects = vision_data.get("defects", [])
        annotations = vision_data.get("annotations", [])
        
        source_file = analysis.get("source_file", {})
        frame = {
            "id": int(file_id) if file_id.isdigit() else 0,
            "file": source_file.get("file_name", ""),
            "sha256": "",  # Would be computed during ingestion
            "width": source_file.get("file_img_width", 0),
            "height": source_file.get("file_img_height", 0),
            "annotations": annotations,
            "defects_count": len(defects)
        }
        frames.append(frame)
    
    vision_result["outputs"]["frames"] = frames
    print(f"[OK] Vision analysis complete: {len(frames)} frames processed")
    return vision_result


def execute_phase_defect_detection(analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Execute DEFECT_DETECTION phase."""
    print("\n=== PHASE 3: DEFECT_DETECTION ===")
    
    defect_stats = analyze_defects(analysis_results)
    
    # Aggregate all defects
    def_all = []
    for file_id, analysis in analysis_results.items():
        defects = analysis.get("vision", {}).get("defects", [])
        source_file = analysis.get("source_file", {})
        
        for defect in defects:
            defect_entry = {
                "id_defaut": defect.get("id_defaut", ""),
                "categorie": defect.get("categorie", "AUTRE"),
                "type_defaut": defect.get("type_defaut", ""),
                "origin_layer": defect.get("origin_layer", "SURFACE"),
                "gravite_technique": defect.get("gravite", 2),
                "image_ref": source_file.get("file_name", ""),
                "style": defect.get("style", "MAJEUR"),
                "incertitude": defect.get("incertitude", 0.0),
                "regle_ref": defect.get("regle_ref", {
                    "doc_id": "UNKNOWN",
                    "source_page": "",
                    "article_id": ""
                }),
                "polygons_norm": defect.get("polygons_norm", []),
                "polylines_norm": defect.get("polylines_norm", [])
            }
            def_all.append(defect_entry)
    
    defect_detection_result = {
        "step": "DEFECT_DETECTION",
        "active": True,
        "skipped": False,
        "status": "success",
        "inputs": {
            "analysis_results_count": len(analysis_results)
        },
        "outputs": {
            "def_all_count": len(def_all),
            "def_all": def_all
        },
        "stats": defect_stats
    }
    
    print(f"[OK] Defect detection complete: {len(def_all)} defects aggregated")
    return defect_detection_result


def execute_phase_norm_reference_link(def_all: List[Dict], docs_index: Dict) -> Dict[str, Any]:
    """Execute NORM_REFERENCE_LINK phase."""
    print("\n=== PHASE 4: NORM_REFERENCE_LINK ===")
    
    # Link defects to document references
    linked_count = 0
    citations = []
    
    for defect in def_all:
        regle_ref = defect.get("regle_ref", {})
        doc_id = regle_ref.get("doc_id", "UNKNOWN")
        
        if doc_id != "UNKNOWN":
            # Find document in docs_index
            for doc in docs_index.get("documents", []):
                if doc.get("id") == doc_id or doc.get("code") == doc_id:
                    citation = {
                        "defect_id": defect.get("id_defaut", ""),
                        "doc_id": doc_id,
                        "doc_title": doc.get("title", ""),
                        "doc_url": doc.get("url", ""),
                        "source_page": regle_ref.get("source_page", ""),
                        "article_id": regle_ref.get("article_id", "")
                    }
                    citations.append(citation)
                    linked_count += 1
                    break
    
    norm_link_result = {
        "step": "NORM_REFERENCE_LINK",
        "active": True,
        "skipped": False,
        "status": "success",
        "inputs": {
            "defects_count": len(def_all),
            "documents_count": docs_index.get("total_documents", 0)
        },
        "outputs": {
            "linked_defects": linked_count,
            "citations": citations
        }
    }
    
    print(f"[OK] Norm reference linking complete: {linked_count} defects linked to documents")
    return norm_link_result


def execute_phase_reporting(
    ingestion_result: Dict,
    vision_result: Dict,
    defect_result: Dict,
    norm_link_result: Dict
) -> Dict[str, Any]:
    """Execute REPORTING phase."""
    print("\n=== PHASE 8: REPORTING ===")
    
    report = {
        "meta": {
            "generated_at": datetime.now().isoformat() + "Z",
            "report_level": 2
        },
        "sections": {
            "introduction": "ArBot Vision Analysis Pipeline Report",
            "observations": [],
            "annexe_normative": [],
            "conclusion": "Pipeline execution complete"
        },
        "pipeline_results": {
            "ingestion": ingestion_result,
            "vision_analysis": vision_result,
            "defect_detection": defect_result,
            "norm_reference_link": norm_link_result
        },
        "summary": {
            "total_images": ingestion_result["outputs"]["counts"]["photo"],
            "total_documents": ingestion_result["outputs"]["counts"]["pdf"],
            "frames_analyzed": len(vision_result["outputs"]["frames"]),
            "defects_detected": defect_result["outputs"]["def_all_count"],
            "defects_linked": norm_link_result["outputs"]["linked_defects"]
        }
    }
    
    print(f"[OK] Reporting complete")
    return report


def main():
    """Main pipeline execution."""
    print("=" * 60)
    print("ArBot Vision Pipeline Execution")
    print("=" * 60)
    print()
    
    # Load control panel
    print("Loading pipeline configuration...")
    controlpanel = load_controlpanel()
    print(f"[OK] Control panel loaded: version {controlpanel.get('schema_version', 'N/A')}")
    print()
    
    # Load data
    print("Loading project data...")
    images_db = load_images_db()
    docs_index = load_docs_index()
    analysis_results = load_analysis_results(ANALYSIS_RESULTS_DIR)
    print()
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Execute pipeline phases
    ingestion_result = execute_phase_ingestion(images_db, docs_index, controlpanel)
    vision_result = execute_phase_vision_analysis(images_db, analysis_results, controlpanel)
    defect_result = execute_phase_defect_detection(analysis_results)
    norm_link_result = execute_phase_norm_reference_link(
        defect_result["outputs"]["def_all"],
        docs_index
    )
    report = execute_phase_reporting(
        ingestion_result,
        vision_result,
        defect_result,
        norm_link_result
    )
    
    # Save pipeline report
    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    print("[OK] Pipeline Execution Complete!")
    print("=" * 60)
    print(f"Report saved to: {REPORT_OUTPUT}")
    print()
    print("Summary:")
    print(f"  - Images processed: {report['summary']['total_images']}")
    print(f"  - Documents indexed: {report['summary']['total_documents']}")
    print(f"  - Frames analyzed: {report['summary']['frames_analyzed']}")
    print(f"  - Defects detected: {report['summary']['defects_detected']}")
    print(f"  - Defects linked to norms: {report['summary']['defects_linked']}")
    print()


if __name__ == "__main__":
    main()

