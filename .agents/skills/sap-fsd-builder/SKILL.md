---
name: sap-fsd-builder
description: SOP & Generator Otomatis Dokumen FSD (Functional Specification Document) SAP Enterprise berbasis Template Word (.docx) dan Markdown (.md) menggunakan OOXML cloning tanpa merusak styling korporat.
---

# 📑 SOP & Engine: SAP Enterprise FSD Builder (`sap-fsd-builder`)

Skill ini menyediakan engine kompilasi otomatis dan metodologi terstandarisasi untuk merakit dokumen **Functional Specification Document (FSD / FS)** tingkat enterprise untuk kebutuhan kustomisasi RICEF SAP (Reports, Interfaces, Conversions, Enhancements, Forms).

---

## 🎯 Masalah yang Diselesaikan

Membuat dokumen FSD Word dari awal (*from scratch*) sering menimbulkan masalah:
1. **Styling Hancur:** Font, warna heading, margin tabel, kop surat, dan nomor halaman sering berantakan jika dibuat ad-hoc.
2. **Format Ganda:** Klien membutuhkan Word (`.docx`) formal untuk approval/sign-off, sementara tim developer membutuhkan Markdown (`.md`) untuk pelacakan Git dan review cepat.
3. **Token Inefficiency:** Menulis naskah Word 30+ halaman via LLM bolak-balik membakar kuota token.

### 🌟 Solusi: AST Template-Cloning Architecture
Skill ini menggunakan arsitektur **Abstract Syntax Tree (AST)** di mana naskah spesifikasi ditulis dalam modul Python terstruktur (`content_*.py`), lalu compiler mengkloning prototipe elemen dari template resmi (`fsd_master_template.docx`) dan menghasilkan `.docx` + `.md` secara simultan dalam waktu < 1 detik.

---

## 🛠️ Komponen Engine & Direktori

```text
📁 .agents/skills/sap-fsd-builder/
├── 📄 SKILL.md                          <-- Panduan operasional (file ini)
├── 📁 scripts/
│   ├── 🐍 build_fsd.py                  <-- Compiler utama (.docx & .md)
│   └── 🐍 toc_resolver.py               <-- Resolver nomor halaman daftar isi (pass ke-2 via PDF)
├── 📁 templates/
│   └── 📄 fsd_master_template.docx      <-- Template Word resmi korporat (independen & self-contained)
└── 📁 examples/
    └── 🐍 sample_content_spec.py        <-- Boilerplate modul konten untuk spesifikasi baru
```

---

## 🚀 Panduan Eksekusi CLI

### 1. Merakit Dokumen FSD Baru
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\sap-fsd-builder\scripts\build_fsd.py" `
  "<path_ke_content_spec.py>" `
  "<path_ke_output.docx>" `
  "<path_ke_output.md>"
```

### 2. Opsional: Custom Template & Folder Media Gambar
Secara default, engine menggunakan template bawaan di `templates/fsd_master_template.docx`. Anda dapat menentukan template atau folder gambar kustom melalui variabel lingkungan (*environment variables*):
```powershell
$env:FSD_TPL = "path\to\custom_template.docx"
$env:FSD_MEDIA = "path\to\images_folder"
python "c:\D\FIleSharing\SAP\.agents\skills\sap-fsd-builder\scripts\build_fsd.py" content.py out.docx out.md
```

### 3. Opsional: Penyelesaian Nomor Halaman Daftar Isi (Pass ke-2)
Jika dokumen sudah pernah diekspor ke PDF:
```powershell
# 1. Ekstrak nomor halaman heading:
python "c:\D\FIleSharing\SAP\.agents\skills\sap-fsd-builder\scripts\toc_resolver.py" "out.pdf" "toc.json"

# 2. Re-compile FSD dengan menyuntikkan toc.json:
$env:TOCPAGES = "toc.json"
python "c:\D\FIleSharing\SAP\.agents\skills\sap-fsd-builder\scripts\build_fsd.py" content.py out.docx out.md
```

---

## 📝 Format Struktur Data Modul Konten (`content_*.py`)

Modul konten mendefinisikan tiga variabel utama:
1. **`META` (Dictionary):**
   * `cover_module`: Nama modul (misal: `"SD – Order to Cash"` atau `"MM – Procure to Pay"`).
   * `cover_title`: Judul dokumen (misal: `"F-SD-03 (REQ-005) – Form Sales Invoice"`).
   * `header_new`: Running header di bagian atas tiap halaman.
   * `date`: Tanggal penyusunan (`"DD/MM/YYYY"`).
   * `doc_title`: Nama file dokumen lengkap.
   * `versions`: List tuple riwayat revisi `[("0.1", "12/10/2026", "Author", "Alasan")]`.
2. **`IMG` (Dictionary):**
   * Pemetaan ID gambar ke file fisik: `{1: "img01.png", 2: "img02.png"}`.
3. **`C` (List of AST Elements):**
   * `('h1', 'Judul Bab H1')`
   * `('h2', 'Sub-bab H2')`
   * `('h3', 'Sub-sub-bab H3')`
   * `('p', 'Teks paragraf dengan dukungan inline **bold**')`
   * `('b', 'Bullet point item')`
   * `('tbl', [headers], [[rows]], [widths_in_dxa])`
   * `('fig', img_id, 'Caption Gambar', 'Penjelasan detail')`

---

## 📋 SOP bagi AI Agent Saat Diminta Membuat FSD Baru

1. **Sintesis Forensik Konten & Provenance (Skill: `sap-fsd-synthesizer`):**
   * Gunakan [[.agents/skills/sap-fsd-synthesizer/SKILL.md]] untuk memindai korpus dokumen mentah klien (Excel, MoM, email, query live SAP) dengan 4 algoritma forensik.
   * Dapatkan modul AST `content_<req>.py` dan manifes ketertelusuran `<req>_provenance.md`.
2. **Kompilasi Dokumen (Skill: `sap-fsd-builder`):**
   * Jalankan compiler `build_fsd.py` untuk memproduksi berkas resmi `.docx` di folder `Docx_Specs` dan `.md` di `Markdown_Specs`.
3. **Penyelesaian Nomor Halaman Daftar Isi (Pass ke-2):**
   * Jika diperlukan nomor halaman statis TOC yang presisi, jalankan `toc_resolver.py` pada berkas PDF hasil render Word.
4. **Buat Companion Digest & Ko-lokasi Provenance:**
   * Jalankan `docx-inspector` untuk menghasilkan file digest pendamping (`<file>_digest.md`).
   * Pastikan berkas `<req>_provenance.md` disimpan berdampingan (*co-located*) sebagai dokumen audit resmi.
