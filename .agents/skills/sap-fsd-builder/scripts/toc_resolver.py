# -*- coding: utf-8 -*-
"""TOC Resolver: Deteksi nomor halaman heading dari PDF hasil render Word untuk pass ke-2.

Penggunaan:
    python toc_resolver.py <fsd.pdf> <toc.json>
"""
import sys
import json
import os

import importlib

# Dynamic import untuk mencegah static lint error (reportMissingImports) di IDE
pymupdf = None
for mod_name in ("pymupdf", "fitz"):
    try:
        pymupdf = importlib.import_module(mod_name)
        break
    except ImportError:
        pass

if pymupdf is None:
    print("[WARN] Modul 'pymupdf' / 'fitz' belum terpasang di environment Python.")
    print("       Jalankan: pip install pymupdf (hanya jika ingin mengaktifkan pass ke-2 nomor halaman TOC).")
    sys.exit(0)

if len(sys.argv) < 3:
    print("Penggunaan: python toc_resolver.py <input.pdf> <output_toc.json>")
    sys.exit(1)

PDF_IN, JSON_OUT = sys.argv[1], sys.argv[2]

DEFAULT_HEADINGS = [
    "Context", "Latar Belakang Bisnis", "Mengapa standar SAP tidak sesuai atau tidak cukup?",
    "Alternatif yang Dipertimbangkan", "Di Luar Lingkup", "Asumsi", "Dependensi", "Tautan",
    "Solution Design", "Model Data", "Antarmuka Pengguna", "Enhancement Logic", "Application Logic",
    "Diagram Alur", "Validasi dan Penanganan Error", "Otorisasi",
    "Perluasan Objek Terkait untuk Interface, Migrasi Data dan Pelaporan", "IDOC",
    "API: mis. BAPI, RFC atau Web Service", "LSMW", "Model Data Analitik (HANA Live atau CDS View)",
    "Cara Pengujian"
]

if not os.path.exists(PDF_IN):
    print(f"[ERR] File PDF tidak ditemukan: {PDF_IN}")
    sys.exit(1)

doc = pymupdf.open(PDF_IN)
page_numbers = []

for h in DEFAULT_HEADINGS:
    found_page = None
    for i in range(2, len(doc)):  # lewati cover dan daftar isi
        page_text = [line.strip() for line in doc[i].get_text().split('\n')]
        if h in page_text:
            found_page = i + 1
            break
    page_numbers.append(found_page)

with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(page_numbers, f)

print(f"[OK] TOC nomor halaman tersimpan ke {JSON_OUT}: {page_numbers}")
