---
name: docx-inspector
description: SOP & Zero-Dependency Batch Engine untuk memproses dan mengindeks seluruh file dokumen Word (.docx) secara lokal (0 LLM API tokens). Mengekstrak outline hierarkis, inventaris tabel, dan seluruh aset diagram/UML/flowchart ke disk lokal untuk inspeksi deterministik multimodal.
---

# 📑 SOP: Universal Word (.docx) Inspector & Batch Engine

Skill ini menyediakan engine dan metodologi standar untuk memproses puluhan hingga ratusan dokumen Word (`.docx`) dalam proyek klien enterprise (seperti **Functional Specs**, **Technical Specs**, **Architecture Blueprints**, **Contract Agreements**, dan **Minutes of Meeting**) secara **Hybrid (bisa dieksekusi oleh Pengembang langsung di terminal maupun oleh AI Agent)**.

---

## ⚡ Mengapa Perlu Batch Local Script? (0 LLM API Tokens)

> [!IMPORTANT]
> **Zero API Token Consumption:**
> Jika AI Agent membaca berkas `.docx` puluhan megabyte langsung ke context window prompt LLM, kuota token akan langsung meledak (*context window explosion / quota exhaustion*).
> 
> Engine ini berjalan **100% secara lokal di CPU** menggunakan Python standard library (`zipfile` + `xml.etree`):
> - **Kecepatan:** Memproses 10 file `.docx` hanya dalam **~0.2 detik**.
> - **Biaya Token:** **0 TOKENS**.
> - **Hasil:** Seluruh diagram, UML, flowchart, dan screenshot otomatis diekstrak ke disk lokal, teks caption diinjeksi ke digest, siap diinspeksi secara visual maupun tekstual.

---

## 🛠️ Panduan Perintah CLI (`docx_inspector.py`)

Lokasi Script:
`c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py`

### 1. Mode Batch Folder (Bisa Dijalankan Pengembang / AI)
Memproses seluruh file `.docx` dalam sebuah folder secara serentak:
```powershell
# Jalankan pada folder spesifikasi
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --dir "path\to\Docx_Specs"
```

**Apa yang terjadi dalam 1 kali eksekusi?**
1. Setiap file `.docx` otomatis dibuatkan file pendamping `<nama_file>_digest.md` (~200 token).
2. Seluruh gambar diagram, flowchart alur proses, dan screen mockup substantif diekstrak ke folder `<nama_file>_assets/`.
3. Seluruh teks keterangan (*caption*) di sekitar gambar otomatis di-inject ke tabel katalog visual digest.
4. Otomatis dibuatkan file master ringkasan: `00_DOCX_INVENTORY.md`.

#### Ingin Memproses Seluruh Subfolder Sekaligus?
Gunakan flag `--recursive` / `-r`:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --dir "path\to\root_folder" --recursive
```

---

### 2. Mode Single File On-Demand (Hemat Token & Presisi Tinggi)
Ketika AI atau pengembang ingin menanyakan bagian spesifik tanpa membaca seluruh dokumen:

#### A. Ambil Potongan Bab Tertentu Saja:
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "path\to\document.docx" `
  --section "Diagram Alur"
```
*Output hanya ~50-100 token berisi langkah-langkah alur proses spesifik.*

#### B. Ambil Tabel Tertentu Saja (Key-Value / JSON / Markdown):
```powershell
# Format Key-Value (Sangat direkomendasikan untuk reasoning AI bebas geser kolom)
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "path\to\document.docx" `
  --table 3 --format kv

# Format JSON (Deterministik untuk skrip dan DDL)
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "path\to\document.docx" `
  --table 3 --format json
```

#### C. Lihat Outline Daftar Isi (TOC):
```powershell
python "c:\D\FIleSharing\SAP\.agents\skills\docx-inspector\scripts\docx_inspector.py" `
  --file "path\to\document.docx" `
  --outline
```

---

## 🖼️ Alur Kerja Dual-Track AI (Multimodal Vision vs Text-Only)

1. Saat batch selesai, diagram dan gambar substantif tersimpan di:
   `<file>_assets/image1.png`, `image2.png`, dst.
2. AI Agent membaca tabel di `<file>_digest.md` pada bagian:
   `## 🖼️ Embedded Diagrams & Visual Assets Catalog`
3. **Model Text-Only (DeepSeek V4 Pro API):**
   Cukup membaca kolom metadata *Caption / Context Description* pada digest untuk memahami relasi diagram tanpa perlu memanggil image processor.
4. **Model Multimodal Vision (Gemini / Claude Sonnet / GPT-4o):**
   Membaca metadata konteks terlebih dahulu, lalu membuka berkas fisik menggunakan tool `view_file` untuk inspeksi visual mendalam:
   ```text
   view_file AbsolutePath="path\to\<file>_assets\image2.png"
   ```

---

## ⚖️ Sinergi: `docx-inspector` vs `docx-mcp`

| Kebutuhan Pekerjaan | Tool Pilihan | Alasan |
|---|---|---|
| **Batch Onboarding / Staging** | 🌟 `docx-inspector` | Super cepat (<0.3s), 0 token, ekstrak gambar & buat digest. |
| **Pencarian Bab / Tabel Spesifik** | 🌟 `docx-inspector` | On-demand slicing hemat 95%+ token. |
| **Inspeksi Flowchart / Mockup** | 👁️ `view_file` pada `_assets/` | Multimodal visual inspection langsung pada gambar hasil dump. |
| **Membuat Dokumen TSD / Word Baru** | 🛠️ `docx-mcp` | Membangun dokumen Word resmi berformat rapi dari Markdown. |
| **Review & Track Changes (Redlining)** | 🛠️ `docx-mcp` | Menyisipkan markup revisi resmi yang kompatibel dengan MS Word. |

