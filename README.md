---
title: "SAP Enterprise Second Brain & Knowledge Base"
author: "Dwi Septian Nugroho"
version: "2.0.0"
last_updated: "2026-10-12"
tags: [SAP, S4HANA, ABAP, CleanCore, SecondBrain, Obsidian, AgenticAI]
---

# 🧠 SAP Enterprise Second Brain & Knowledge Base

Selamat datang di repositori **SAP Enterprise Second Brain** — pusat dokumentasi terpadu, repositori pengetahuan teknis, dan arsip spesifikasi implementasi SAP S/4HANA & ECC.

Repositori ini dirancang khusus dengan arsitektur **Hybrid Human & Agentic AI**, yang dapat digunakan sebagai **Obsidian Vault lokal** sekaligus **Knowledge Base presisi tinggi** untuk AI coding assistant (Antigravity IDE, Cline, Claude, dll.) tanpa risiko *hallucination* atau pemborosan token.

---

## 🗺️ Gambaran Arsitektur Folder

```text
📁 SAP/
│
├── 📄 README.md                            <-- [File Ini] Dokumentasi ringkas & overview repositori
├── 📄 00_MAP_OF_CONTENT.md                 <-- Peta Jalan Navigasi Utama (Single Source of Truth)
├── 📄 AGENTS.md                            <-- Konstitusi & Guardrails Aturan Pengembangan AI (Clean Core)
├── 📄 KNOWLEDGE_BASE_ARCHITECTURE.md        <-- Blueprint Desain Arsitektur Knowledge Base
│
├── 📁 _assets/                             <-- Media Statis & Gambar Pendukung (Tidak di-parse sebagai teks)
│   └── 📁 images/
│       ├── 📁 abapgit/                     <-- Screenshot tutorial abapGit (abapgit_1.jpg s/d abapgit_21.jpg)
│       └── 📁 eclipse/                     <-- Diagram perspektif Eclipse ADT (adt_eclipse_perspective.png)
│
├── 📁 10_Domains/                          <-- Inti Pengetahuan Modul & Proses Bisnis SAP (Reusable)
│   ├── 📁 Overview/                        <-- Peta modul besar ERP & diagram arsitektur
│   ├── 📁 MM_Procurement/                  <-- Siklus Procure-to-Pay (P2P), MIGO, MIRO, EKKO/EKPO
│   ├── 📁 SD_OrderToCash/                  <-- Alur Order-to-Cash (OTC), Delivery, Billing VBRK/VBRP
│   └── 📁 FI_Financials/                   <-- General Ledger, House Bank T012/T012K
│
├── 📁 20_Technical_Core/                   <-- Kamus Teknis ABAP, Kamus Data (DDIC), BAPI, & ADT MCP (Reusable)
│   ├── 📁 ABAP_Foundations/                <-- Panduan Lengkap Part 01 s/d Part 06, sintaks modern 7.5+
│   ├── 📁 Dictionary_Tables/               <-- DDL tabel kustom (ZEMP_DWI) & requirement database
│   ├── 📁 Interfaces_BAPI/                 <-- Signature & analisis Function Module (BAPI_USER_GET_DETAIL)
│   ├── 📁 ADT_MCP_Integration/             <-- Panduan server ADT MCP, tools, & troubleshooting
│   └── 📁 OpenSource_and_Repos/            <-- Kurasi library ABAP & repositori open-source GitHub
│
├── 📁 30_Playbooks_and_SOP/                <-- Template Kode Siap Pakai & Teknik Troubleshooting (Reusable)
│   ├── 📁 Code_Templates/                  <-- Template Report ALV ZMM_REPORT_PO (INNER JOIN aman)
│   ├── 📁 Search_and_Diagnostics/          <-- Teknik AI filtering respons XML ADT & query Z*
│   └── 📄 todo_5_pilar_teknis_abap.txt     <-- Agenda topik tingkat lanjut (BAdI, Lock Objects, Dumps)
│
├── 📁 40_Projects_and_Specs/               <-- Spesifikasi Fungsional & Teknis Terisolasi per Klien
│   ├── 📄 00_PROJECTS_INDEX.md             <-- [Master Sub-MOC] Registry seluruh proyek & klien
│   ├── 📁 Client_EnterpriseSample/         <-- [Contoh Wadah Proyek Klien]
│   │   ├── 📄 CLIENT_CONTEXT.md            <-- Profil arsitektur sistem, profil klien & index spesifikasi
│   │   ├── 📁 Specs_FS_TS/                 <-- Klaster Docx_Specs, Excel_Trackers, Markdown_Specs
│   │   ├── 📁 ABAP_Source_Code/            <-- [Murni ABAP] Class, Driver, Include, Test Runner
│   │   ├── 📁 Document_Tooling/            <-- [Perkakas Dokumen] Skrip AST Python & builder lokal
│   │   └── 📁 Outputs_and_Logs/            <-- Log eksekusi, digest ringkas, manifes silsilah data
│   └── 📁 _Template_Client/                <-- Template bersih siap pakai untuk klien baru di masa depan
│
├── 📁 50_Learning_Apps/                    <-- Aplikasi Edukasi & Latihan Interaktif
│   └── 📁 AppsSoalSAP/                     <-- Web app kuis/simulasi ujian sertifikasi SAP (HTML/JS/CSS)
│
└── 📁 90_Legacy_Archive/                   <-- Arsip Proyek Lama / Kode Usang
    └── 📄 .aiignore                        <-- Melindungi AI agar tidak membaca sintaks lama/obsolete
```

---

## ⚡ 3 Pilar Utama Sistem

### 1. Reusable Knowledge Assets (Folder `10`, `20`, `30`)
* Berisi fondasi modul (MM, SD, FI), standar ABAP Clean Core (7.4+/7.5+), kamus data, dan template ALV.
* **Bersifat Universal:** Aset ini dapat digunakan kembali (*reusable*) untuk proyek klien mana pun tanpa perlu menulis ulang panduan.

### 2. Multi-Client Isolation (Folder `40_Projects_and_Specs`)
* Menggunakan pendekatan **Hierarchical Sub-MOC**:
  * Root `00_MAP_OF_CONTENT.md` tetap bersih dan tidak berubah setiap ada proyek baru.
  * Setiap klien memiliki wadah terisolasi (`Client_<NamaKlien>/`) lengkap dengan file `CLIENT_CONTEXT.md` agar aturan unik dan spesifikasi rahasia (*NDA*) tidak saling tercampur.

### 3. Machine-Friendly & Obsidian-Ready
* **Standar Penamaan:** Menggunakan format `lower_snake_case` ringkas tanpa karakter rawan (kurung `()`, spasi ganda, koma).
* **Metadata Instan:** Dilengkapi **YAML Frontmatter** di awal setiap file Markdown untuk pemfilteran cepat oleh AI.
* **Jaringan Tautan:** Menggunakan format **WikiLinks (`[[path/to/file.md]]`)** untuk visualisasi *Graph View* di Obsidian.

### 4. Token-Efficient Document Engines (Excel & Word Companion Digest)
* **Anti-Token-Explosion:** Mencegah konversi membabi-buta dokumen besar (Excel ribuan sel, Word puluhan halaman) menjadi teks mentah raksasa yang membakar puluhan ribu token.
* **Pola Companion Digest (`<file>_digest.md`):** Menyimpan ringkasan metadata, TOC outline bab, inventaris tabel, dan kamus nilai kategori unik (~150-200 token).
* **Ekstraksi Diagram & UML Lokal (`_assets/`):** Seluruh flowchart, arsitektur sistem, dan screen mockup dari file Word otomatis diekstrak ke disk lokal untuk inspeksi visual multimodal tanpa memakan kuota LLM.
* **Zero-Dependency Local Batch Engine:** Berjalan 100% lokal di CPU menggunakan Python standard library murni (`zipfile` + `xml.etree`). Memproses 60+ file dalam <1 detik dengan **0 kuota token Gemini API**.

---

## 🚀 Panduan Penggunaan

### A. Untuk Manusia (Membuka via Obsidian)
1. Buka aplikasi **Obsidian**.
2. Pilih **"Open folder as vault"**.
3. Arahkan ke direktori `c:\D\FIleSharing\SAP`.
4. Buka file `00_MAP_OF_CONTENT.md` atau aktifkan **Graph View** untuk menjelajahi peta konsep secara visual interaktif.

### B. Untuk AI Agent (Antigravity IDE / Cline)
Alur berpikir AI saat mengeksekusi instruksi:
```text
User Prompt ➔ 1. AGENTS.md (Filter Aturan) ➔ 2. 00_MAP_OF_CONTENT.md (Peta Navigasi) ➔ 3. Target File ➔ Eksekusi
```
AI dilarang melakukan pencarian acak (*random crawling*) dan wajib membaca peta indeks terlebih dahulu.

### C. SOP Menambahkan Proyek Klien Baru (Hanya 1 Menit)
1. Salin folder `40_Projects_and_Specs/_Template_Client` ➔ beri nama `Client_<NamaKlien>`.
2. Rename dan sesuaikan file `CLIENT_CONTEXT_TEMPLATE.md` menjadi `CLIENT_CONTEXT.md`.
3. Masukkan berkas FS/TS dari klien ke folder `Specs_FS_TS/`.
4. Daftarkan 1 baris nama klien baru di tabel `40_Projects_and_Specs/00_PROJECTS_INDEX.md`.

---

## 🛡️ Standar Koding & Clean Core
Pengembangan kode kustom wajib mematuhi panduan di [AGENTS.md](file:///c:/D/FIleSharing/SAP/AGENTS.md):
- Menggunakan arsitektur modern **ABAP Cloud / RAP (RESTful Application Programming)**.
- Menghindari modifikasi langsung pada sistem standar SAP (gunakan BAdI / Enhancement Spots).
- Menggunakan namespace kustom **`Z*`** atau **`Y*`**.
