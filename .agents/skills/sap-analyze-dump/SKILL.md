---
name: sap-analyze-dump
description: SOP to analyze ST22 ABAP Dumps or runtime errors and provide Clean Core recommendations (SOP mencari penyebab error/dump dan solusinya).
---

# 🇬🇧 English
**Objective:** Guide the AI to systematically troubleshoot and analyze ABAP runtime errors (dumps) reported by the user.

## Workflow:
1. **Identify the Issue:** Ask the user for the T-Code, Program name, or the exact error dump message (e.g., from ST22).
2. **Locate the Code:** Use `SearchObject` or `GetTransaction` (from `sap-abap-adt`) to find the exact location (URI) of the failing program, class, or include.
3. **Extract Source Code:** Use `GetProgram`, `GetClass`, or `GetFunction` to read the ABAP source code into the AI's context. Pay special attention to the lines around the reported error.
4. **Analyze & Recommend:** Analyze the code for common issues (e.g., `CX_SY_OPEN_SQL_DB`, `GETWA_NOT_ASSIGNED`, obsolete syntax). Provide a detailed explanation of why it failed and write the corrected code block using modern ABAP (7.4+) and Clean Core principles.

---

# 🇮🇩 Bahasa Indonesia
**Tujuan:** Memandu AI untuk mencari penyebab error secara sistematis (runtime errors/dumps) dan memberikan solusi berstandar Clean Core.

## Langkah Kerja:
1. **Identifikasi Masalah:** Minta T-Code, nama Program, atau pesan error dump (misal dari ST22) dari user.
2. **Lacak Kode:** Gunakan `SearchObject` atau `GetTransaction` (dari `sap-abap-adt`) untuk mencari lokasi pasti (URI) dari program, class, atau fungsi yang error.
3. **Sedot Source Code:** Gunakan `GetProgram`, `GetClass`, atau `GetFunction` untuk membaca source code ABAP. Fokus pada baris kode yang menyebabkan error.
4. **Analisa & Solusi:** Analisa kode tersebut untuk mencari masalah umum (misal: variabel belum di-assign, syntax lama yang tidak disupport S/4HANA). Jelaskan kenapa error itu terjadi dan berikan kode perbaikannya menggunakan standar ABAP Modern (7.4+ / Clean Core).
