#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot Vision Analysis and Report Generator
Loads image database and document index, processes vision analysis, and generates assessment reports.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse

# File paths
IMAGES_DB_PATH = "json/images_db.json"
DOCS_INDEX_PATH = "json/docs_index.json"
ANALYSIS_RESULTS_DIR = "docs/To validate/ArBot-Core,_v1.4_OUT_JSON"
OUTPUT_REPORT_DIR = "reports"
OUTPUT_REPORT_PATH = f"{OUTPUT_REPORT_DIR}/assessment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[OK] Loaded {file_path}: {len(data.get('items', data.get('documents', [])))} items")
        return data
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {file_path}: {e}")
        raise


def load_images_db() -> Dict[str, Any]:
    """Load the images database."""
    return load_json_file(IMAGES_DB_PATH)


def load_docs_index() -> Dict[str, Any]:
    """Load the documents index."""
    return load_json_file(DOCS_INDEX_PATH)


def load_analysis_results(analysis_dir: str = ANALYSIS_RESULTS_DIR) -> Dict[str, Dict[str, Any]]:
    """Load all analysis result JSON files."""
    analysis_results = {}
    analysis_path = Path(analysis_dir)
    
    if not analysis_path.exists():
        print(f"[WARNING] Analysis directory not found: {analysis_dir}")
        return analysis_results
    
    # Load all JSON files except DEF_ALL.json and other aggregate files
    json_files = list(analysis_path.glob("*_analysis.json"))
    json_files = [f for f in json_files if f.name not in ["DEF_ALL.json", "IMG_GEN_analysis.json"]]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract file ID from filename or from data
                file_id = json_file.stem.replace('_analysis', '').split('_')[0]
                analysis_results[file_id] = data
        except Exception as e:
            print(f"[WARNING] Could not load {json_file.name}: {e}")
    
    print(f"[OK] Loaded {len(analysis_results)} analysis results from {analysis_dir}")
    return analysis_results


def analyze_defects(analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze defects from vision analysis results."""
    defect_stats = {
        'total_images_analyzed': len(analysis_results),
        'total_defects': 0,
        'defects_by_category': defaultdict(int),
        'defects_by_severity': defaultdict(int),
        'defects_by_zone': defaultdict(int),
        'images_with_defects': 0,
        'images_without_defects': 0,
    }
    
    for file_id, analysis in analysis_results.items():
        defects = analysis.get('vision', {}).get('defects', [])
        if defects:
            defect_stats['images_with_defects'] += 1
            defect_stats['total_defects'] += len(defects)
            
            # Get zone from source_file
            zone_name = analysis.get('source_file', {}).get('zone_name', 'UNKNOWN')
            defect_stats['defects_by_zone'][zone_name] += len(defects)
            
            for defect in defects:
                category = defect.get('categorie', 'UNKNOWN')
                severity = defect.get('gravite', 'UNKNOWN')
                defect_stats['defects_by_category'][category] += 1
                defect_stats['defects_by_severity'][str(severity)] += 1
        else:
            defect_stats['images_without_defects'] += 1
    
    return defect_stats


def generate_assessment_report(
    images_db: Dict[str, Any],
    docs_index: Dict[str, Any],
    analysis_results: Dict[str, Dict[str, Any]],
    output_path: str = OUTPUT_REPORT_PATH
) -> str:
    """Generate a comprehensive assessment report."""
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Analyze defects
    defect_stats = analyze_defects(analysis_results)
    
    # Generate report
    report_lines = []
    report_lines.append("# ArBot Vision Analysis - Assessment Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Analysis Version:** ArBot-Core v1.4")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append(f"- **Total Images in Database:** {images_db.get('count', 0)}")
    report_lines.append(f"- **Total Documents Indexed:** {docs_index.get('total_documents', 0)}")
    report_lines.append(f"- **Images Analyzed:** {defect_stats['total_images_analyzed']}")
    report_lines.append(f"- **Total Defects Detected:** {defect_stats['total_defects']}")
    report_lines.append(f"- **Images with Defects:** {defect_stats['images_with_defects']}")
    report_lines.append(f"- **Images without Defects:** {defect_stats['images_without_defects']}")
    report_lines.append("")
    
    # Defect Statistics
    report_lines.append("## Defect Statistics")
    report_lines.append("")
    
    # Defects by Category
    report_lines.append("### Defects by Category")
    report_lines.append("")
    report_lines.append("| Category | Count |")
    report_lines.append("|----------|-------|")
    for category, count in sorted(defect_stats['defects_by_category'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"| {category} | {count} |")
    report_lines.append("")
    
    # Defects by Severity
    report_lines.append("### Defects by Severity")
    report_lines.append("")
    report_lines.append("| Severity | Count |")
    report_lines.append("|----------|-------|")
    severity_labels = {'1': 'Critical', '2': 'Major', '3': 'Minor'}
    for severity, count in sorted(defect_stats['defects_by_severity'].items(), key=lambda x: int(x[0])):
        label = severity_labels.get(severity, f'Level {severity}')
        report_lines.append(f"| {label} | {count} |")
    report_lines.append("")
    
    # Defects by Zone
    report_lines.append("### Defects by Zone")
    report_lines.append("")
    report_lines.append("| Zone | Defect Count |")
    report_lines.append("|------|--------------|")
    for zone, count in sorted(defect_stats['defects_by_zone'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"| {zone} | {count} |")
    report_lines.append("")
    
    # Image Database Summary
    report_lines.append("## Image Database Summary")
    report_lines.append("")
    report_lines.append(f"- **Database Name:** {images_db.get('db_name', 'N/A')}")
    report_lines.append(f"- **Total Images:** {images_db.get('count', 0)}")
    report_lines.append(f"- **Created At:** {images_db.get('created_at', 'N/A')}")
    report_lines.append("")
    
    # Document Index Summary
    report_lines.append("## Document Index Summary")
    report_lines.append("")
    report_lines.append(f"- **Database Name:** {docs_index.get('db_name', 'N/A')}")
    report_lines.append(f"- **Total Documents:** {docs_index.get('total_documents', 0)}")
    report_lines.append(f"- **Version:** {docs_index.get('version', 'N/A')}")
    report_lines.append("")
    
    # Document Categories
    doc_categories = defaultdict(int)
    for doc in docs_index.get('documents', []):
        category = doc.get('category', 'UNKNOWN')
        doc_categories[category] += 1
    
    report_lines.append("### Documents by Category")
    report_lines.append("")
    report_lines.append("| Category | Count |")
    report_lines.append("|----------|-------|")
    for category, count in sorted(doc_categories.items()):
        report_lines.append(f"| {category} | {count} |")
    report_lines.append("")
    
    # Top Defects
    report_lines.append("## Top Defects by Image")
    report_lines.append("")
    report_lines.append("| Image ID | File Name | Defect Count | Categories |")
    report_lines.append("|----------|-----------|--------------|------------|")
    
    # Sort images by defect count
    image_defect_counts = []
    for file_id, analysis in analysis_results.items():
        defects = analysis.get('vision', {}).get('defects', [])
        if defects:
            categories = set(d.get('categorie', 'UNKNOWN') for d in defects)
            file_name = analysis.get('source_file', {}).get('file_name', 'N/A')
            image_defect_counts.append((file_id, file_name, len(defects), categories))
    
    image_defect_counts.sort(key=lambda x: x[2], reverse=True)
    
    for file_id, file_name, defect_count, categories in image_defect_counts[:20]:  # Top 20
        categories_str = ', '.join(sorted(categories))
        report_lines.append(f"| {file_id} | {file_name} | {defect_count} | {categories_str} |")
    
    report_lines.append("")
    
    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    if defect_stats['total_defects'] > 0:
        report_lines.append("### Critical Issues")
        report_lines.append("- Review all critical severity defects (Level 1)")
        report_lines.append("- Prioritize defects in high-risk zones (SDB, WC)")
        report_lines.append("")
        report_lines.append("### Next Steps")
        report_lines.append("1. Review detailed analysis results for each image")
        report_lines.append("2. Cross-reference defects with technical standards (DTU, FT)")
        report_lines.append("3. Generate repair recommendations based on defect severity")
        report_lines.append("4. Create work orders for critical defects")
    else:
        report_lines.append("No defects detected in analyzed images.")
    report_lines.append("")
    
    # Write report
    report_content = '\n'.join(report_lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"[OK] Assessment report generated: {output_path}")
    return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Run ArBot Vision Analysis and Generate Reports')
    parser.add_argument('--images-db', default=IMAGES_DB_PATH, help='Path to images_db.json')
    parser.add_argument('--docs-index', default=DOCS_INDEX_PATH, help='Path to docs_index.json')
    parser.add_argument('--analysis-dir', default=ANALYSIS_RESULTS_DIR, help='Directory containing analysis results')
    parser.add_argument('--output', default=OUTPUT_REPORT_PATH, help='Output report path')
    parser.add_argument('--skip-analysis', action='store_true', help='Skip loading analysis results')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ArBot Vision Analysis and Report Generator")
    print("=" * 60)
    print()
    
    # Step 1: Load images database
    print("Step 1: Loading images database...")
    images_db = load_images_db()
    print()
    
    # Step 2: Load documents index
    print("Step 2: Loading documents index...")
    docs_index = load_docs_index()
    print()
    
    # Step 3: Load analysis results
    analysis_results = {}
    if not args.skip_analysis:
        print("Step 3: Loading vision analysis results...")
        analysis_results = load_analysis_results(args.analysis_dir)
        print()
    else:
        print("Step 3: Skipping analysis results (--skip-analysis)")
        print()
    
    # Step 4: Generate assessment report
    print("Step 4: Generating assessment report...")
    report_path = generate_assessment_report(
        images_db=images_db,
        docs_index=docs_index,
        analysis_results=analysis_results,
        output_path=args.output
    )
    print()
    
    print("=" * 60)
    print("[OK] Analysis Complete!")
    print("=" * 60)
    print(f"Report saved to: {report_path}")
    print()
    print("Summary:")
    print(f"  - Images in database: {images_db.get('count', 0)}")
    print(f"  - Documents indexed: {docs_index.get('total_documents', 0)}")
    print(f"  - Analysis results loaded: {len(analysis_results)}")
    print()


if __name__ == "__main__":
    main()

