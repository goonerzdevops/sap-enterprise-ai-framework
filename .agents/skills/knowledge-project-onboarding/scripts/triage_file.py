#!/usr/bin/env python3
"""
Universal File Triage & Destination Router (0 LLM Token)
Bagian dari skill: knowledge-project-onboarding

Menganalisis file mentah (teks, markdown, pdf, docx, xlsx) dan merekomendasikan:
1. Target Folder & Subfolder di Knowledge Base
2. Nama Standar Bersih (lower_snake_case)
3. Alasan Kategorisasi & Action Plan
"""

import os
import sys
import argparse
import re
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Keyword Heuristic Rules & Scoring Matrix
ROUTING_RULES = [
    {
        "target": "40_Projects_and_Specs",
        "subfolders": ["Client_<NamaKlien>/Specs_FS_TS", "Client_<NamaKlien>/ABAP_Source_Code"],
        "description": "Spesifikasi Proyek Klien Nyata / Dokumen FSD/TSD Resmi / RICEF Deliverable",
        "keywords": [
            "functional specification", "technical specification", "fsd", "tsd", "ricef",
            "client", "klien", "motul", "zuellig", "garuda", "user story", "change request", "cr-",
            "acceptance criteria", "deliverable", "sign-off", "mockup form", "spec", "specs"
        ],
        "weight": 3.0
    },
    {
        "target": "30_Playbooks_and_SOP",
        "subfolders": ["Code_Templates", "Search_and_Diagnostics", "Error_Resolutions"],
        "description": "Boilerplate Siap Pakai, Template Koding, SOP Pemecahan Error ST22, Troubleshooting",
        "keywords": [
            "template", "boilerplate", "sop", "troubleshooting", "playbook", "st22", "dump",
            "syntax error", "short dump", "how to solve", "langkah perbaikan", "step by step fix",
            "diagnostics", "xml adt filtering", "query program", "seeder", "contoh kode"
        ],
        "weight": 2.5
    },
    {
        "target": "20_Technical_Core",
        "subfolders": ["ABAP_Foundations", "Dictionary_Tables", "Interfaces_BAPI", "ADT_MCP_Integration", "OpenSource_and_Repos"],
        "description": "Fondasi Koding ABAP, Sintaks 7.4/7.5+, Kamus Tabel DDIC SE11, BAPI, Eclipse ADT, Arsitektur S/4HANA",
        "keywords": [
            "abap", "open sql", "select", "internal table", "work area", "cl_salv_table",
            "alv", "smartforms", "adobe forms", "sfp", "eclipse adt", "project explorer",
            "shortcut adt", "transport request", "se11", "se38", "se80", "se16n", "st05",
            "cds view", "amdp", "rap", "restful application programming", "odata", "gateway",
            "bapi", "clean core", "acdoca", "matdoc", "prcd_elements", "sandbox cal", "roadmap",
            "karir", "career", "skill", "tiket", "s4hana", "s/4hana", "ecc", "developer", "programmer", "transisi"
        ],
        "weight": 2.0
    },
    {
        "target": "10_Domains",
        "subfolders": ["Overview", "MM_Procurement", "SD_OrderToCash", "FI_Financials"],
        "description": "Domain Proses Bisnis Murni (P2P, O2C, GL, Billing, Rekonsiliasi, Akuntansi) tanpa Koding",
        "keywords": [
            "procure to pay", "p2p", "order to cash", "o2c", "purchase requisition", "purchase order",
            "goods receipt", "invoice verification", "sales order", "delivery order", "billing document",
            "general ledger", "reconciliation", "chart of accounts", "plant", "storage location",
            "purchasing organization", "sales organization", "company code", "bisnis proses", "rantai pasok",
            "modul besar", "fungsional", "bispro"
        ],
        "weight": 1.5
    },
    {
        "target": "90_Legacy_Archive",
        "subfolders": ["Legacy_ECC_Code", "Deprecated"],
        "description": "Sintaks Usang Pre-7.40, Procedural Pool/Cluster Kuno, Obsolete statements",
        "keywords": [
            "obsolete", "deprecated", "abap pool table", "cluster table", "pre-7.40", "dialog programming",
            "screen painter dynpro kuno", "legacy archive"
        ],
        "weight": 3.0
    }
]

def extract_snippet(file_path):
    """Membaca teks dari berkas lokal tanpa dependensi berat (max 2000 karakter)."""
    p = Path(file_path)
    if not p.exists():
        return ""
    
    ext = p.suffix.lower()
    
    # Text / Markdown / Code / TXT
    if ext in ['.md', '.txt', '.py', '.abap', '.sql', '.json', '.xml', '.csv']:
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline() for _ in range(60)]
                return " ".join(lines).lower()
        except Exception:
            return ""
            
    # Binary / PDF / Office (Deteksi nama file + scan string ascii mentah cepat)
    content = p.stem.replace('_', ' ').replace('-', ' ').lower() + " "
    try:
        with open(p, 'rb') as f:
            raw_bytes = f.read(8192) # Baca 8 KB awal
            ascii_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', raw_bytes.decode('ascii', errors='ignore'))
            content += " " + ascii_text.lower()
    except Exception:
        pass
        
    return content

def normalize_suggested_name(filename):
    """Mengubah nama file acak menjadi clean lower_snake_case tanpa karakter aneh."""
    p = Path(filename)
    stem = p.stem.lower()
    ext = p.suffix.lower()
    
    # Hapus karakter aneh
    clean = re.sub(r'[^a-z0-9]+', '_', stem)
    clean = re.sub(r'_+', '_', clean).strip('_')
    
    # Buang awalan umum yang tidak rapi
    clean = re.sub(r'^(download|file|document|copy_of|salinan)_', '', clean)
    
    if not clean:
        clean = "dokumen_tanpa_nama"
        
    return clean + ext

def triage_file(file_path):
    p = Path(file_path)
    if not p.exists():
        print(f"❌ Error: File '{file_path}' tidak ditemukan.")
        sys.exit(1)
        
    snippet = extract_snippet(p)
    filename_text = p.name.lower().replace('_', ' ').replace('-', ' ')
    combined_corpus = filename_text + " " + filename_text + " " + snippet # Bobot ganda untuk nama file
    
    scores = {}
    matched_kw = {}
    
    for rule in ROUTING_RULES:
        target = rule["target"]
        score = 0
        hits = []
        for kw in rule["keywords"]:
            # Cocokkan kata kunci
            matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', combined_corpus))
            if matches > 0:
                score += matches * rule["weight"]
                hits.append(kw)
        scores[target] = score
        matched_kw[target] = hits

    # Extra boost jika kata kunci muncul langsung di nama file (stem)
    stem_tokens = set(re.split(r'[^a-z0-9]+', p.stem.lower()))
    for rule in ROUTING_RULES:
        target = rule["target"]
        for kw in rule["keywords"]:
            kw_words = set(re.split(r'[^a-z0-9]+', kw.lower()))
            if kw_words.issubset(stem_tokens):
                scores[target] += 15.0 # High boost untuk match di nama file
                matched_kw[target].append(f"[FILENAME] {kw}")

    # Sort berdasarkan skor tertinggi
    sorted_targets = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner_target, top_score = sorted_targets[0]
    
    # Jika skor 0 atau sangat rendah, default ke 10_Domains/Overview atau butuh konfirmasi
    if top_score == 0:
        winner_target = "10_Domains"
        subfolder = "Overview"
        confidence = "RENDAH (Perlu Review Manusia)"
    else:
        confidence = "TINGGI" if top_score >= 10 else "SEDANG"
        # Tentukan subfolder spesifik
        if winner_target == "20_Technical_Core":
            if any(k in matched_kw[winner_target] for k in ["abap", "open sql", "alv", "eclipse adt", "shortcut adt", "roadmap karir", "acdoca"]):
                subfolder = "ABAP_Foundations"
            elif any(k in matched_kw[winner_target] for k in ["se11", "dictionary", "tabel"]):
                subfolder = "Dictionary_Tables"
            elif any(k in matched_kw[winner_target] for k in ["bapi", "interfaces"]):
                subfolder = "Interfaces_BAPI"
            else:
                subfolder = "ABAP_Foundations"
        elif winner_target == "10_Domains":
            if any(k in matched_kw[winner_target] for k in ["procure to pay", "p2p", "purchase order", "goods receipt"]):
                subfolder = "MM_Procurement"
            elif any(k in matched_kw[winner_target] for k in ["order to cash", "o2c", "sales order", "delivery order"]):
                subfolder = "SD_OrderToCash"
            elif any(k in matched_kw[winner_target] for k in ["general ledger", "reconciliation", "akuntansi"]):
                subfolder = "FI_Financials"
            else:
                subfolder = "Overview"
        elif winner_target == "30_Playbooks_and_SOP":
            if any(k in matched_kw[winner_target] for k in ["template", "boilerplate"]):
                subfolder = "Code_Templates"
            else:
                subfolder = "Search_and_Diagnostics"
        elif winner_target == "40_Projects_and_Specs":
            subfolder = "Client_New/Specs_FS_TS"
        else:
            subfolder = "Legacy_ECC_Code"

    clean_name = normalize_suggested_name(p.name)

    print("=" * 65)
    print(f" 🎯 HASIL TRIAGE & DESTINATION ROUTING: {p.name}")
    print("=" * 65)
    print(f"📁 Target Pilar Utama : {winner_target}")
    print(f"📂 Rekomendasi Folder : {winner_target}/{subfolder}")
    print(f"🏷️  Saran Nama Bersih  : {clean_name}")
    print(f"📊 Tingkat Keyakinan  : {confidence} (Score: {top_score:.1f})")
    print(f"🔑 Kata Kunci Terdeteksi:")
    for tgt, hits in matched_kw.items():
        if hits:
            print(f"   • {tgt}: {', '.join(hits[:5])}")
    print("-" * 65)
    print("📋 REKOMENDASI TINDAKAN (ACTION PLAN):")
    if p.suffix.lower() in ['.pdf', '.docx', '.xlsx']:
        print("1. Simpan berkas biner asli di folder target sebagai upstream reference.")
        print("2. Buat companion markdown (_digest.md atau naskah sintesis .md) berstandar:")
        print("   - YAML Frontmatter lengkap.")
        print("   - Clickable Table of Contents (TOC).")
        print("   - Volume baris ideal: 150 - 400 baris.")
    else:
        print("1. Pindahkan dan rename file ke folder target menggunakan format numerik sekuensial.")
        print("2. Jalankan audit kesehatan file via:")
        print(f"   python .agents/skills/knowledge-file-curator/scripts/curate_knowledge.py --dir {winner_target}/{subfolder}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Universal Triage & Router File Mentah ke Knowledge Base")
    parser.add_argument("--file", required=True, help="Path ke file mentah yang ingin di-triage")
    args = parser.parse_args()
    
    triage_file(args.file)

if __name__ == "__main__":
    main()
