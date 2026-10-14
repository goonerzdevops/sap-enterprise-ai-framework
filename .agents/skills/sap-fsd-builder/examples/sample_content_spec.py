# -*- coding: utf-8 -*-
"""Contoh Format Modul Konten FSD untuk sap-fsd-builder.
Gunakan file ini sebagai pola untuk menyusun spesifikasi fungsional baru (FSD) RICEF.
"""

# Mapping file gambar/diagram
IMG = {
    1: "img01.png",
    2: "img02.png"
}

# Metadata Dokumen
META = {
    "cover_module": "SD – Sales & Distribution / Order to Cash",
    "cover_title": "F-SD-99 (REQ-099) – Form Custom Delivery Slip",
    "header_new": "F-SD-99 Form Custom Delivery",
    "client_name": "PT Enterprise Global",
    "project_name": "SAP S/4HANA Implementation",
    "date": "12/10/2026",
    "doc_title": "FS F-SD-99 REQ-099 Custom Delivery Slip Form - V.0.1",
    "versions": [
        ("0.1", "12/10/2026", "AI Consultant", "Draf awal spesifikasi kebutuhan dan mapping field."),
    ],
}

# Lebar Kolom Semantik Terstandarisasi (Total halaman: 9921 dxa):
W_WIN  = [1500, 3450, 3450, 1400]  # Tabel Window Form (Kolom 1: 2,65 cm)
W_TECH = [1800, 2600, 2800, 2600]  # Tabel Komponen Teknis (Kolom 1: 3,17 cm)
W_OBJ  = [2400, 1600, 1600, 4200]  # Tabel Objek ABAP (Kolom 1: 4,23 cm)
W_ID   = [700, 3300, 3800, 2000]   # Tabel ID / Matrix Uji (Kolom 1: 1,23 cm)

# Struktur Elemen Dokumen (AST)
# Tag yang didukung:
#   ('h1', 'Judul Bab H1')
#   ('h2', 'Sub-bab H2')
#   ('h3', 'Sub-bab H3')
#   ('p',  'Paragraf teks. Gunakan **teks tebal** bila diperlukan.')
#   ('b',  'Item bullet point')
#   ('tbl', [header1, header2], [[row1_col1, row1_col2]], [width1, width2])
#   ('fig', img_num, 'Caption Judul', 'Penjelasan detail gambar')
C = [
    ('h1', 'Context'),
    ('h2', 'Latar Belakang Bisnis'),
    ('p', 'Klien membutuhkan pencetakan formulir **Custom Delivery Slip** untuk pengiriman barang gudang.'),
    
    ('h2', 'Mengapa standar SAP tidak sesuai atau tidak cukup?'),
    ('p', 'Form standar SAP tidak memuat barcode batch dan syarat retur lokal Indonesia.'),
    
    ('h1', 'Solution Design'),
    ('h2', 'Model Data'),
    ('p', 'Data ditarik dari tabel standar pengiriman SAP (LIKP dan LIPS):'),
    ('tbl',
     ['Field Sumber', 'Field Target', 'Tipe Data', 'Keterangan'],
     [
         ['LIKP-VBELN', 'Delivery No', 'CHAR 10', 'Nomor dokumen pengiriman'],
         ['LIPS-POSNR', 'Item No', 'NUMC 6', 'Nomor posisi item'],
         ['LIPS-MATNR', 'Material No', 'CHAR 18', 'Kode produk material'],
         ['LIPS-LFIMG', 'Delivery Qty', 'QUAN 13,3', 'Kuantitas fisik kirim']
     ],
     [2200, 2200, 1800, 3100]
    ),
    
    ('h2', 'Application Logic'),
    ('b', 'Driver membaca tabel LIKP berdasarkan nomor dokumen VBELN.'),
    ('b', 'Item barang dibaca dari LIPS dengan filter kuantitas LFIMG > 0.'),
    ('b', 'Alamat pengiriman diambil dari tabel ADRC melalui relasi partner VBPA-ADRNR (Partner WE).'),
    
    ('h1', 'Cara Pengujian'),
    ('p', 'Jalankan test runner di SE38 dengan memasukkan nomor dokumen delivery uji.'),
]
