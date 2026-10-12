# 🚀 Panduan Penggunaan: `excel_query.py` (Hybrid Developer & AI)

File ini adalah panduan praktis siap pakai untuk menjalankan script **`excel_query.py`**.  
Script ini berjalan **100% offline secara lokal di CPU menggunakan Python standard library bawaan** (`zipfile` + `xml.etree`).  
**Konsumsi Token Gemini API: 0 TOKENS.**

## 💻 1. Cara Menjalankan Mode Batch (Banyak File Sekaligus)

Gunakan perintah ini saat ada folder proyek klien mentah baru yang berisi banyak file spreadsheet `.xlsx`.

### A. Pindai 1 Folder Spesifik (misal folder Spesifikasi Teknis):
Buka **PowerShell** dan jalankan:
```powershell
python ".agents\skills\excel-inspector\scripts\excel_query.py" `
  --dir "40_Projects_and_Specs\Client_Sample\Specs_FS_TS"
```

### B. Pindai Seluruh Folder Mentah & Subfolder Secara Rekursif:
```powershell
python ".agents\skills\excel-inspector\scripts\excel_query.py" `
  --dir "40_Projects_and_Specs\Client_Sample" --recursive
```

### ✨ Apa yang Dihasilkan Mode Batch Excel?
1. **`00_XLSX_INVENTORY.md`**: Master tabel inventaris yang merangkum seluruh file spreadsheet, jumlah sheet, total baris, dan link digest.
2. **`<nama_file>_digest.md`**: File ringkasan pendamping (~150 token) berisi skema kolom dan nilai kategori unik untuk setiap workbook.

---

## 📊 2. Cara Menghasilkan Companion Digest untuk 1 File Saja (`--digest`)

Gunakan perintah ini untuk membuat ringkasan skema dan kamus nilai kategori unik (~150 token):
```powershell
python ".agents\skills\excel-inspector\scripts\excel_query.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\ricef_tracker_sample.xlsx" `
  --digest
```
*Otomatis menghasilkan file `<nama_file>_digest.md` berdampingan dengan file Excel.*

---

## 📑 2. Cara Melihat Daftar Sheet (`--sheets`)
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\sap-excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --sheets
```

---

## 🎯 3. Cara Melakukan Query Selektif On-Demand (Hemat Token)

Tarik baris spesifik dan pilih kolom yang diinginkan saja:

### A. Filter Modul Tertentu:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\sap-excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --sheet "2 RICEF Tracker" `
  --filter "Modul=MM" `
  --columns "Req ID,Modul,Tipe,Judul,Kategori,Usulan nama objek"
```

### B. Filter Pencocokan Parsial/Substring (`~`):
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\sap-excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --sheet "2 RICEF Tracker" `
  --filter "Kategori~Phase 1" `
  --columns "Req ID,Modul,Judul,Kategori,Status"
```

### C. Output dalam Format JSON:
Tambahkan flag `--format json`:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\sap-excel-inspector\scripts\excel_query.py" `
  --file "path\to\tracker.xlsx" `
  --sheet "2 RICEF Tracker" `
  --filter "Modul=MM" `
  --columns "Req ID,Judul" `
  --format json
```

---

## 📌 Rangkuman Argumen CLI Flag

| Flag | Deskripsi | Contoh |
|---|---|---|
| `--file`, `-f` | Path ke file `.xlsx` | `--file "path\to\file.xlsx"` |
| `--digest`, `-d` | Buat file pendamping `<file>_digest.md` | `--digest` |
| `--sheet`, `-s` | Nama sheet target | `--sheet "2 RICEF Tracker"` |
| `--filter` | Filter kriteria kolom (`=` atau `~`) | `--filter "Modul=MM"` |
| `--columns`, `-c` | Daftar kolom yang ingin ditampilkan | `--columns "Req ID,Judul,Status"` |
| `--limit`, `-l` | Maksimal baris output (default 20, 0 = semua) | `--limit 10` |
| `--format` | Format output (`markdown`, `json`, `csv`) | `--format markdown` |
| `--preview`, `-p` | Snapshot cepat N baris pertama | `--preview 5` |
| `--sheets` | Tampilkan daftar seluruh sheet di workbook | `--sheets` |
