---
name: knowledge-file-curator
description: SOP & Zero-Dependency Engine untuk mengaudit kesehatan direktori knowledge base, standardisasi tata nama file (01_... s/d 07_...), penegakan ambang batas baris (150-400 baris), penyusunan Daftar Isi (TOC) klikabel, dan otomasi 00_FOLDER_INDEX.md untuk efisiensi token AI Agent.
---

# Knowledge File Curator Skill

## 1. Overview & Filosofi Arsitektur
Skill ini dirancang untuk memastikan setiap direktori pembelajaran dan basis pengetahuan (*Second Brain*) di repositori memenuhi standar **Agentic AI & Human Readability**:
* **Zero-Token Ambiguity:** Agen AI tidak boleh bingung memilih file karena nama yang acak atau tumpang tindih.
* **Token Economy Standard:** File tidak boleh terlalu pendek (<100 baris, memicu fragmentasi konteks) atau terlalu panjang (>600 baris, memicu *lost-in-the-middle* dan pemborosan kuota token).
* **Sweet Spot Zone:** Setiap berkas pembelajaran berada pada kisaran **150 – 400 baris** (~1.500 – 3.500 tokens).
* **Library Card Catalog (`00_FOLDER_INDEX.md`):** Setiap folder pengetahuan wajib memiliki satu gerbang indeks yang memetakan kata kunci kueri AI (*trigger queries*) ke berkas target secara presisi.
* **Mandatory Table of Contents (TOC):** Setiap berkas Markdown wajib memuat `## 📌 Daftar Isi` dengan tautan *anchor* Markdown yang valid.

---

## 2. Aturan Baku Kurasi Dokumen (The 5 Golden Rules)

### Aturan 1: Standardisasi Tata Nama (Hierarchical Numeric Prefix)
Seluruh berkas pembelajaran dalam satu folder wajib menggunakan penomoran sekuensial hierarkis:
```text
00_FOLDER_INDEX.md                      <-- Master Router & Katalog Perpustakaan
01_<topik_fondasi_awal>.md              <-- Modul 1
02_<topik_lanjutan_spesifik>.md         <-- Modul 2
...
NN_<topik_penutup_atau_spesialisasi>.md <-- Modul Terakhir
```

### Aturan 2: Ambang Batas Baris & Tindakan Rekayasa
| Rentang Baris | Klasifikasi Status | Tindakan Kurasi yang Wajib Diambil |
| :---: | :---: | :--- |
| **< 100 baris** | ⚠️ Terlalu Kurus | **Merge & Enrich:** Gabungkan ke modul induk yang relevan ATAU perkaya (*enrich*) dengan diagram, tabel, dan contoh kode nyata hingga mencapai batas ideal. |
| **150 – 400 baris** | 🟢 **Zona Ideal (*Sweet Spot*)** | Pertahankan. Optimal untuk pembacaan bedah (*surgical reading*) LLM dan sesi baca manusia. |
| **> 600 baris** | ⚠️ Terlalu Gemuk | **Split & Modularize:** Pecah menjadi 2 sub-modul logis (misal `02a_...` dan `02b_...`) untuk mencegah context window explosion. |

### Aturan 3: Kewajiban YAML Frontmatter Baku
Setiap file `.md` wajib diawali dengan:
```yaml
---
title: "Judul Modul Lengkap"
doc_id: "<DOMAIN>-<SUBDOMAIN>-<NOMOR>"
domain: "<Nama_Folder>"
type: "concept" # Pilihan: concept | playbook | technical_spec | inventory
status: "approved"
upstream_sources:
  - "[[path/ke/dokumen_sumber.md]]"
downstream_artifacts:
  - "[[path/ke/dokumen_terkait.md]]"
tags: [Tag1, Tag2, Tag3]
last_verified: "YYYY-MM-DD"
---
```

### Aturan 4: Kewajiban Daftar Isi (Clickable TOC)
Setelah judul utama (`# ...`) dan catatan singkat (*callout block*), wajib menyertakan:
```markdown
## 📌 Daftar Isi
1. [Judul Bab 1](#1-judul-bab-1)
2. [Judul Bab 2](#2-judul-bab-2)
   - [Sub-Bab 2.1](#sub-bab-21)
```

### Aturan 5: Sinkronisasi Katalog (`00_FOLDER_INDEX.md`) & Master MOC
Setiap penambahan, penggabungan, atau penggantian nama file wajib memperbarui:
1. `00_FOLDER_INDEX.md` lokal (memperbarui nama file, ukuran baris, dan trigger queries).
2. `00_MAP_OF_CONTENT.md` root repositori (memperbarui WikiLinks).

---

## 3. CLI Helper Script (`scripts/curate_knowledge.py`)

Gunakan script bawaan Python Standard Library untuk mengaudit kepatuhan folder secara deterministik (0 token LLM):

```powershell
# Audit kesehatan folder (cek baris, TOC, dan frontmatter):
python ".agents/skills/knowledge-file-curator/scripts/curate_knowledge.py" --dir "<path_to_folder>"

# Audit dan hasilkan draf 00_FOLDER_INDEX.md otomatis:
python ".agents/skills/knowledge-file-curator/scripts/curate_knowledge.py" --dir "<path_to_folder>" --generate-index
```
