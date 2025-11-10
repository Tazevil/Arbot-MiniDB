#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_evidence_spreadsheet.py
Creates comprehensive Excel spreadsheet organizing legal evidence
for construction company dispute case 25-001508-RLY-M1
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re

def parse_master_csv():
    """Parse #MASTER.csv into People Info dataframe"""
    master_file = Path("ARCHIVE/#MASTER.csv")
    df = pd.read_csv(master_file, encoding='utf-8')

    # Select key columns for People Info
    columns_to_keep = [
        'ActeurID', 'Nom_Complet', 'Type_Acteur', 'Fonction_Role_Principal',
        'Entreprise_Rattachement', 'Telephone_Principal', 'Email_Principal',
        'Statut_Litige', 'Reputation_Score_Global', 'Nb_Communications_Total',
        'Nb_Anomalies_Imputees', 'Gravite_Anomalies_Max', 'Notes_Contextuelles'
    ]

    df_people = df[columns_to_keep].copy()
    df_people.columns = [
        'ID', 'Nom Complet', 'Type', 'Rôle Principal', 'Entreprise',
        'Téléphone', 'Email', 'Statut Litige', 'Réputation',
        'Nb Communications', 'Nb Anomalies', 'Gravité Max', 'Notes'
    ]

    return df_people

def parse_mail_chronologie():
    """Parse Mail Chronologie.txt into Timeline dataframe"""
    chrono_file = Path("ARCHIVE/Mail Chronologie.txt")
    content = chrono_file.read_text(encoding='utf-8')

    # Parse markdown table
    lines = content.strip().split('\n')
    data = []

    for line in lines[4:]:  # Skip header rows
        if line.strip() and '|' in line and not line.startswith('| **'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 6 and parts[0] and parts[0] != 'Date':
                data.append(parts)

    df_timeline = pd.DataFrame(data, columns=[
        'Date', 'Expéditeur', 'Destinataires', 'Objet',
        'Pièces jointes', 'Synthèse'
    ])

    return df_timeline

def parse_call_history():
    """Parse Call History cleaned.txt into Calls dataframe"""
    calls_file = Path("ARCHIVE/Call History cleaned.txt")
    content = calls_file.read_text(encoding='utf-8')

    lines = content.strip().split('\n')
    data = []
    current_date = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if it's a date line
        if re.match(r'^\w+ \d+ \w+', line):
            current_date = line
            continue

        # Parse call entry
        if ';' in line:
            parts = line.split(';')
            time = parts[0]
            contact = parts[1] if len(parts) > 1 else "Inconnu"
            phone = parts[2] if len(parts) > 2 else ""

            data.append({
                'Date': current_date,
                'Heure': time,
                'Contact': contact,
                'Numéro': phone,
                'Type': 'Entrant'  # All appear to be incoming
            })

    df_calls = pd.DataFrame(data)
    return df_calls

def parse_context_json():
    """Parse arbotvision_context.json for key events"""
    json_file = Path("arbotvision_context.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = []
    for event in data.get('chronologie', []):
        events.append({
            'Date': event.get('date', ''),
            'Type': event.get('type', ''),
            'Description': event.get('description', ''),
            'Responsable': '',  # To be filled from context
            'Impact': '',
            'Gravité': ''
        })

    df_events = pd.DataFrame(events)
    return df_events

def create_documents_index():
    """Create index of all evidence files"""
    context_dir = Path(".")
    archive_dir = Path("ARCHIVE")
    raw_dir = Path("RAW")

    files_data = []

    # Scan all directories
    for directory in [context_dir, archive_dir, raw_dir]:
        if not directory.exists():
            continue

        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix not in ['.pyc', '.tmp']:
                try:
                    size = file_path.stat().st_size
                    size_kb = round(size / 1024, 1)

                    # Categorize file type
                    if file_path.suffix in ['.csv']:
                        category = 'Data - CSV'
                    elif file_path.suffix in ['.xlsx', '.xls']:
                        category = 'Data - Excel'
                    elif file_path.suffix == '.json':
                        category = 'Data - JSON'
                    elif file_path.suffix in ['.txt']:
                        category = 'Text - Logs'
                    elif file_path.suffix in ['.pdf']:
                        category = 'Document - PDF'
                    elif file_path.suffix in ['.docx', '.doc']:
                        category = 'Document - Word'
                    elif file_path.suffix in ['.jpg', '.jpeg', '.png']:
                        category = 'Image - Photo'
                    elif file_path.suffix == '.zip':
                        category = 'Archive - ZIP'
                    else:
                        category = 'Other'

                    files_data.append({
                        'Nom fichier': file_path.name,
                        'Type': file_path.suffix[1:].upper() if file_path.suffix else 'N/A',
                        'Taille (KB)': size_kb,
                        'Emplacement': str(file_path.parent),
                        'Catégorie': category,
                        'Chemin complet': str(file_path)
                    })
                except:
                    pass

    df_docs = pd.DataFrame(files_data)
    df_docs = df_docs.sort_values(['Catégorie', 'Nom fichier'])
    return df_docs

def create_defects_log():
    """Create defects log from known issues"""
    defects = [
        {
            'ID': 'D-001',
            'Date constatée': '2025-08-29',
            'Localisation': 'Salle de bain - Sol',
            'Description': 'Carrelage sol désaligné, différences de niveau',
            'Gravité': 'Élevée',
            'Statut': 'Non corrigé',
            'Responsable': 'Rhône Bâtiment',
            'Photo': 'Voir dossier Google Drive'
        },
        {
            'ID': 'D-002',
            'Date constatée': '2025-08-29',
            'Localisation': 'Salle de bain - Murs',
            'Description': 'Peinture défectueuse, traces et bavures',
            'Gravité': 'Moyenne',
            'Statut': 'Non corrigé',
            'Responsable': 'Rhône Bâtiment',
            'Photo': 'Voir dossier Google Drive'
        },
        {
            'ID': 'D-003',
            'Date constatée': '2025-09-08',
            'Localisation': 'Salle de bain - Baignoire',
            'Description': 'Installation pieds baignoire non conforme',
            'Gravité': 'Critique',
            'Statut': 'En discussion',
            'Responsable': 'Rhône Bâtiment',
            'Photo': 'Photos envoyées 08/09'
        },
        {
            'ID': 'D-004',
            'Date constatée': '2025-09-08',
            'Localisation': 'Salle de bain - Cloison',
            'Description': 'Espace suspect entre BA13 et mur extérieur',
            'Gravité': 'Élevée',
            'Statut': 'Question posée',
            'Responsable': 'Rhône Bâtiment',
            'Photo': 'Photos envoyées 08/09'
        },
        {
            'ID': 'D-005',
            'Date constatée': '2025-08-29',
            'Localisation': 'Salle de bain - Finitions',
            'Description': 'Joints silicone mal finis',
            'Gravité': 'Moyenne',
            'Statut': 'Non corrigé',
            'Responsable': 'Rhône Bâtiment',
            'Photo': 'Voir dossier Google Drive'
        }
    ]

    df_defects = pd.DataFrame(defects)
    return df_defects

def create_delays_log():
    """Create delays and communication failures log"""
    delays = [
        {
            'Date incident': '2025-04-22 to 2025-06-11',
            'Type': 'Silence radio',
            'Responsable': 'Mustafa Dogan',
            'Durée': '49 jours',
            'Impact': 'Blocage total chantier',
            'Gravité': 'Critique',
            'Notes': 'Aucune réponse pendant 7 semaines consécutives'
        },
        {
            'Date incident': '2025-07-07',
            'Type': 'Report chantier',
            'Responsable': 'Mustafa Dogan',
            'Durée': '1 semaine',
            'Impact': 'Retard planification',
            'Gravité': 'Élevée',
            'Notes': 'Report de 16/07 à 30/07'
        },
        {
            'Date incident': '2025-07-29',
            'Type': 'Annulation veille',
            'Responsable': 'Mustafa Dogan',
            'Durée': 'N/A',
            'Impact': 'Changement prestataire',
            'Gravité': 'Critique',
            'Notes': 'Annulation 24h avant début - prestataire remplacé'
        },
        {
            'Date incident': '2025-08-18',
            'Type': 'Défausse fourniture',
            'Responsable': 'GEOP/Rogliardo',
            'Durée': 'N/A',
            'Impact': 'Blocage chantier 6 jours',
            'Gravité': 'Critique',
            'Notes': 'Demande assuré commander baignoire lui-même'
        },
        {
            'Date incident': '2025-06-17 to 2025-07-01',
            'Type': 'Non-réponse',
            'Responsable': 'GEOP/Pagez',
            'Durée': '14 jours',
            'Impact': 'Incertitude budget',
            'Gravité': 'Moyenne',
            'Notes': 'Contradiction budget baignoire 450€ vs 600€'
        },
        {
            'Date incident': '2025-09-03',
            'Type': 'Clôture abusive',
            'Responsable': 'GEOP/Lalande',
            'Durée': 'N/A',
            'Impact': 'Procédure administrative',
            'Gravité': 'Critique',
            'Notes': 'Clôture sans visite réception ni PV'
        },
        {
            'Date incident': '2025-09-10',
            'Type': 'Non-réponse',
            'Responsable': 'GEOP',
            'Durée': '2+ jours',
            'Impact': 'Incertitude reprise',
            'Gravité': 'Moyenne',
            'Notes': 'Silence après envoi photos malfaçons'
        },
        {
            'Date incident': '2025-09-11',
            'Type': 'Coordination défaillante',
            'Responsable': 'Rhône Bâtiment/GEOP',
            'Durée': 'N/A',
            'Impact': 'Confusion planning',
            'Gravité': 'Élevée',
            'Notes': 'Proposition RDV sans plan action validé'
        }
    ]

    df_delays = pd.DataFrame(delays)
    return df_delays

def main():
    """Generate comprehensive evidence spreadsheet"""
    print("[*] Generating Evidence Master Spreadsheet...")
    print()

    # Change to context directory
    import os
    os.chdir(Path(__file__).parent)

    # Create Excel writer
    output_file = "EVIDENCE_MASTER.xlsx"
    writer = pd.ExcelWriter(output_file, engine='openpyxl')

    # TAB 1: PEOPLE_INFO
    print("[1/8] Creating PEOPLE_INFO tab...")
    df_people = parse_master_csv()
    df_people.to_excel(writer, sheet_name='PEOPLE_INFO', index=False)

    # TAB 2: TIMELINE
    print("[2/8] Creating TIMELINE tab...")
    df_timeline = parse_mail_chronologie()
    df_timeline.to_excel(writer, sheet_name='TIMELINE', index=False)

    # TAB 3: CALLS
    print("[3/8] Creating CALLS tab...")
    df_calls = parse_call_history()
    df_calls.to_excel(writer, sheet_name='CALLS', index=False)

    # TAB 4: EVENTS_TIMING
    print("[4/8] Creating EVENTS_TIMING tab...")
    df_events = parse_context_json()
    df_events.to_excel(writer, sheet_name='EVENTS_TIMING', index=False)

    # TAB 5: DOCUMENTS
    print("[5/8] Creating DOCUMENTS tab...")
    df_docs = create_documents_index()
    df_docs.to_excel(writer, sheet_name='DOCUMENTS', index=False)

    # TAB 6: DEFECTS_LOG
    print("[6/8] Creating DEFECTS_LOG tab...")
    df_defects = create_defects_log()
    df_defects.to_excel(writer, sheet_name='DEFECTS_LOG', index=False)

    # TAB 7: DELAYS_LOG
    print("[7/8] Creating DELAYS_LOG tab...")
    df_delays = create_delays_log()
    df_delays.to_excel(writer, sheet_name='DELAYS_LOG', index=False)

    # TAB 8: SUMMARY
    print("[8/8] Creating SUMMARY tab...")
    summary_data = {
        'Métrique': [
            'Dossier référence',
            'Lieu sinistre',
            'Date sinistre',
            'Date début travaux',
            'Date fin travaux',
            'Durée totale affaire',
            'Nombre total de parties',
            'Nombre communications',
            'Nombre d\'appels',
            'Nombre de défauts constatés',
            'Nombre de retards majeurs',
            'Budget total travaux',
            'Gravité globale'
        ],
        'Valeur': [
            '25-001508-RLY-M1',
            '123 rue Château Gaillard, 69100 Villeurbanne',
            '2024-07-21',
            '2025-08-18',
            '2025-08-29',
            '13 mois (393 jours)',
            str(len(df_people)),
            str(len(df_timeline)),
            str(len(df_calls)),
            str(len(df_defects)),
            str(len(df_delays)),
            '4 831,84 € TTC',
            'CRITIQUE'
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(writer, sheet_name='SUMMARY', index=False)

    # Save Excel file
    writer.close()

    print()
    print("="*70)
    print("SUCCESS: Evidence spreadsheet generated")
    print("="*70)
    print(f"File: {output_file}")
    print(f"Location: {Path.cwd()}")
    print()
    print("Tabs created:")
    print("  1. PEOPLE_INFO     - 17 parties with contact info")
    print(f"  2. TIMELINE        - {len(df_timeline)} chronological events")
    print(f"  3. CALLS           - {len(df_calls)} call records")
    print(f"  4. EVENTS_TIMING   - Key events timeline")
    print(f"  5. DOCUMENTS       - {len(df_docs)} evidence files indexed")
    print(f"  6. DEFECTS_LOG     - {len(df_defects)} construction defects")
    print(f"  7. DELAYS_LOG      - {len(df_delays)} delays & failures")
    print("  8. SUMMARY         - Case overview metrics")
    print()
    print("[OK] Ready for legal analysis")

if __name__ == "__main__":
    main()
