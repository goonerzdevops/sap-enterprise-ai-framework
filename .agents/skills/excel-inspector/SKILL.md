---
name: excel-inspector
description: SOP & Zero-Dependency Engine untuk membaca, mengindeks, dan menanyakan data spreadsheet Excel (.xlsx) enterprise secara presisi tanpa memboroskan token context window melalui pola Companion Digest (.md) dan On-Demand Query CLI.
---

# 📊 SOP: Universal Excel (.xlsx) Inspector & Companion Digest Engine

Skill ini menyediakan metodologi standar untuk menangani dokumen spreadsheet Excel (`.xlsx`) seperti **Requirement Tracker**, **Configuration Matrix**, **Authorization Matrix**, dan **Data Migration Mapping** di dalam Universal Agentic Second Brain / RAG architecture.

---

## 💡 Filosofi & Masalah Utama: "Token Explosion Anti-Pattern"

> [!WARNING]
> **ANTI-PATTERN:** Mengonversi file Excel utuh (misal: 30 kolom x 500 baris) langsung menjadi tabel Markdown raksasa.
> - **Akibat:** Membakar puluhan ribu token context window sekaligus.
> - **Dampak Negatif:** AI mengalami *context dilution / attention drift*, data penting terlewat, dan biaya/latensi melonjak drastis.

### 🌟 Solusi: Pola Two-Tier Hybrid Architecture

```mermaid
flowchart TD
    A["File Mentah: file.xlsx\n(Misal: Config/Req Tracker)"] --> B["Tier 1: Companion Digest (.md)\npython excel_query.py --digest"]
    B --> C["file_digest.md\n(~100-200 Token)\n- List Sheet\n- Schema Kolom\n- Nilai Unik Kategori\n- 2-Baris Sampel"]
    C --> D{"AI Agent Membaca Digest"}
    D -->|Mengetahui Skema & Nilai Filter| E["Tier 2: On-Demand Query CLI\npython excel_query.py --filter Kategori=Prod --columns 'ID,Nama'"]
    E --> F["Tabel Terstruktur Ringkas (5-10 Baris)\n(~40 Token - Presisi 100%)"]

    style A fill:#374151,stroke:#9ca3af,stroke-width:2px,color:#fff
    style B fill:#1e3a5f,stroke:#3b82f6,stroke-width:2px,color:#fff
    style C fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    style D fill:#d97706,stroke:#fbbf24,stroke-width:2px,color:#fff
    style E fill:#1e3a5f,stroke:#3b82f6,stroke-width:2px,color:#fff
    style F fill:#065f46,stroke:#34d399,stroke-width:2px,color:#fff
```

1. **Tier 1 — Companion Digest (`<file>_digest.md`):**
   - Disimpan berdampingan dengan file `.xlsx`.
   - Hanya menghabiskan ~150 token.
   - Memuat: inventaris sheet, daftar nama kolom, jumlah baris, dan **kamus nilai kategori unik** (misal: Kategori apa saja yang ada, status apa saja yang ada).
   - Memberikan 100% gambaran menyeluruh tanpa memuat seluruh baris data.

2. **Tier 2 — Selective On-Demand Query (`excel_query.py`):**
   - Dijalankan via terminal Python bawaan (**0 dependensi pip, murni `zipfile` + `xml.etree`**).
   - Menarik hanya baris dan kolom yang spesifik ditanyakan oleh user/tugas.
   - Mengembalikan luaran terstruktur mini (hanya ~30–50 token).

---

## 🛠️ Panduan Perintah CLI (`excel_query.py`)

Lokasi Script:
`c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\excel_query.py`

### 1. Membuat Companion Digest (`--digest`)
Buat ringkasan skema dan profil kolom:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\excel_query.py" --file "path\to\tracker.xlsx" --digest
```
*Output otomatis disimpan ke `path\to\tracker_digest.md`.*

---

### 2. Melihat Daftar Sheet (`--sheets`)
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\excel_query.py" --file "path\to\tracker.xlsx" --sheets
```

---

### 3. Filter Spesifik & Proyeksi Kolom (`--query`)
Ambil data kategori tertentu, dan hanya kolom yang dibutuhkan:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --sheet "Sheet1" `
  --filter "Status=Active" `
  --columns "ID,Nama,Status,Deskripsi" `
  --format kv
```

#### Filter Operator:
- `=` : Pencocokan eksak (case-insensitive), misal `--filter "Status=Active"`
- `~` : Pencocokan substring (case-insensitive), misal `--filter "Kategori~Phase 1"`
- Filter Jamak: Dapat menggunakan beberapa flag `--filter` sekaligus, misal:
  `--filter "Status=Active" --filter "Tipe=Critical"`

---

### 4. Batasan & Format Output
- `--limit 10`: Batasi maksimal baris (default 20, isi `0` untuk semua).
- `--offset 10`: Pagination untuk data banyak.
- `--format kv`: (Rekomendasi Utama AI Reasoning) Format vertikal key-value bebas geser kolom.
- `--format json`: Menghasilkan struktur JSON untuk kebutuhan script/DDL.
- `--format markdown`: Menghasilkan tabel Markdown untuk preview visual manusia.
- `--preview 5`: Snapshot cepat 5 baris pertama dari sebuah sheet.

---

### 5. Ekstraksi Gambar & Diagram Tersemat (`--extract-images` / `-x`)
Mengekstrak seluruh screenshot, arsitektur, atau bukti UAT yang ditempel di lembar kerja Excel secara berurutan:
```powershell
# Ekstrak otomatis ke folder <file>_assets/
python "c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --extract-images

# Atau jalankan script dedicated:
python "c:\D\FIleSharing\SAP\.agents\skills\excel-inspector\scripts\extract_excel_images.py" `
  --file "path\to\tracker.xlsx" `
  --output "path\to\custom_assets"
```
*Fitur ini 100% Zero-Dependency (Python Standard Library: zipfile + xml.etree.ElementTree), mengekstrak gambar terurut dari baris atas ke bawah.*

---

## 📋 SOP Eksekusi bagi AI Agent

Saat user mengajukan pertanyaan seputar data Excel (misal: *"Tampilkan daftar item aktif yang masuk prioritas tinggi"*):

1. **Cek Digest Terlebih Dahulu:**
   - Cek apakah file `<nama_file>_digest.md` sudah ada di folder terkait.
   - Jika belum ada, jalankan `--digest` terlebih dahulu via `excel_query.py`.
   - Baca file digest menggunakan `view_file` untuk memahami nama sheet, nama kolom, dan nilai kategorinya.

2. **Jalankan Query Selektif:**
   - Gunakan nama kolom yang tepat dari digest untuk menyusun perintah `python excel_query.py --filter ... --columns ... --format kv`.
   - Ambil hanya kolom yang relevan dengan pertanyaan user.

3. **Sajikan Hasil ke User:**
   - Sajikan tabel/ringkasan hasil eksekusi query.
   - Jelaskan insight-nya tanpa membebani context window dengan data kolom yang tidak relevan.

