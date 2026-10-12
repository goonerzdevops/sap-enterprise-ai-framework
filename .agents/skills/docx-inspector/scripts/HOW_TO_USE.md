# 🚀 Panduan Penggunaan: `docx_inspector.py` (Hybrid Developer & AI)

File ini adalah panduan praktis siap pakai untuk menjalankan script **`docx_inspector.py`**.  
Script ini berjalan **100% offline secara lokal di CPU menggunakan Python standard library bawaan** (`zipfile` + `xml.etree`).  
**Konsumsi Token Gemini API: 0 TOKENS.**

---

## 💻 1. Cara Menjalankan Mode Batch (Banyak File Sekaligus)

Gunakan perintah ini saat ada folder proyek klien mentah baru yang berisi puluhan file `.docx`.

### A. Pindai 1 Folder Spesifik (misal folder Spesifikasi Teknis):
Buka **PowerShell** dan jalankan:
```powershell
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --dir "40_Projects_and_Specs\Client_Sample\Specs_FS_TS"
```

### B. Pindai Seluruh Folder Mentah & Subfolder Secara Rekursif:
```powershell
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --dir "40_Projects_and_Specs\Client_Sample" --recursive
```

### ✨ Apa yang Dihasilkan Mode Batch?
1. **`00_DOCX_INVENTORY.md`**: Master tabel inventaris yang merangkum seluruh file, jumlah bab, jumlah tabel, dan jumlah gambar.
2. **`<nama_file>_digest.md`**: File ringkasan pendamping (~150-200 token) berisi Outline Bab (TOC) dan peta tabel.
3. **Folder `<nama_file>_assets/`**: Berisi seluruh file gambar diagram, flowchart alur proses, dan screen mockup yang diekstrak dari Word (`.png` / `.jpg`).

---

## 🎯 2. Cara Menjalankan Mode Single File On-Demand (Hemat Token)

Gunakan perintah ini ketika Anda atau AI Agent ingin mengambil potongan data spesifik dari sebuah dokumen Word tanpa membaca seluruh isinya:

### A. Buat Digest & Ekstrak Gambar untuk 1 File Tertentu:
```powershell
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\sample_spec_doc.docx" `
  --digest
```

### B. Ambil Isi Bab Tertentu Saja (Hanya Menghasilkan ~50 Token):
```powershell
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\sample_spec_doc.docx" `
  --section "Diagram Alur"
```

### C. Ambil Tabel Tertentu (Pilihan Format: KV, JSON, Markdown):
```powershell
# Format Key-Value (Paling Presisi untuk LLM/AI, Bebas Delimiter Pipe Table):
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\Docx_Specs\sample_spec_doc.docx" `
  --table 2 --format kv

# Format JSON (Sangat Cocok untuk Model Penalaran seperti DeepSeek V4 Pro):
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\Docx_Specs\sample_spec_doc.docx" `
  --table 2 --format json

# Format Standar Markdown:
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\Docx_Specs\sample_spec_doc.docx" `
  --table 2 --format markdown
```

### D. Lihat Struktur Outline Bab (TOC) Cepat:
```powershell
python ".agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "40_Projects_and_Specs\Client_Sample\Specs_FS_TS\Docx_Specs\sample_spec_doc.docx" `
  --outline
```

---

## 🖼️ 3. Cara Memahami Diagram & Screenshot (Untuk AI Text-Only & Manusia)

1. Buka file `<nama_file>_digest.md`.
2. Cari bagian tabel `## 🖼️ Embedded Diagrams & Visual Assets Catalog`.
3. **Untuk Model AI Text-Only (DeepSeek API):**
   - Kolom **Caption / Context Description** sudah merangkum judul bagan, nomor gambar (misal `Gbr. A1 – Output type...`), dan konteks paragraf terdekat. AI dapat memahami fungsi alur bisnis, objek teknis (seperti `TNAPR`, `Smartform`), atau mockup tanpa memerlukan kapabilitas visi komputer.
4. **Untuk Model Multimodal / Pengembang:**
   - Seluruh gambar fisik tersimpan di `<nama_file>_assets/`. Cukup buka file gambarnya langsung jika ingin melihat tampilan visual aslinya.

---

## 📌 Rangkuman Argumen CLI Flag

| Flag | Deskripsi | Contoh |
|---|---|---|
| `--dir`, `-d` | Jalankan batch scan pada sebuah direktori | `--dir "path\to\folder"` |
| `--recursive`, `-r` | Pindai subfolder secara mendalam (rekursif) | `--recursive` |
| `--file`, `-f` | Targetkan 1 file dokumen `.docx` spesifik | `--file "path\to\file.docx"` |
| `--digest` | Hasilkan file pendamping `<file>_digest.md` | `--digest` |
| `--section`, `-s` | Ambil teks & tabel dari bab tertentu | `--section "Model Data"` |
| `--table`, `-t` | Ambil tabel berdasarkan nomor indeksnya | `--table 2` |
| `--format` | Pilihan format tabel: `kv`, `json`, atau `markdown` | `--format kv` |
| `--outline`, `-o` | Tampilkan hirarki heading (TOC) di terminal | `--outline` |
