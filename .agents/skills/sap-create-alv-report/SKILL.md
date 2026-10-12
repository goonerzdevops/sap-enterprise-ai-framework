---
name: sap-create-alv-report
description: Automated SOP to create a complete ALV Report and its Data Seeder program (SOP Pembuatan Laporan ALV lengkap beserta Seeder-nya).
---

# 🇬🇧 English
**Objective:** Guide the AI to create an end-to-end ABAP ALV report, including a separate seeder program to inject dummy data, using MCP tools.

## Workflow:
1. **Analyze Table:** Ask the user for the custom table name (e.g., Z* table). Use `GetTable` (from `sap-abap-adt`) to read its structure and fields.
2. **Create Seeder (ZINSERT):** Use `abap_creation-create_object` (from `sap_adt_mcp`) to create a Program named `ZINSERT_<tablename>` (e.g., ZINSERT_EMP_DWI) in the `$TMP` package (or user-specified package). Do not require TR for `$TMP`. Provide the ABAP code using Open SQL `INSERT` to the user to copy-paste.
3. **Create Report (ZREPORT):** Use `abap_creation-create_object` to create another Program named `ZREPORT_<tablename>`. Provide the ABAP code using `SELECT` and `cl_demo_output=>display` to the user to copy-paste.
4. **Final Instructions:** Guide the user to refresh their Eclipse Project Explorer, paste the provided codes into the respective programs, save (`Ctrl+S`), activate (`Ctrl+F3`), and execute (`F8`).

---

# 🇮🇩 Bahasa Indonesia
**Tujuan:** Memandu AI untuk membuat laporan ALV ABAP end-to-end, termasuk program seeder terpisah untuk menyuntikkan data dummy, menggunakan tools MCP.

## Langkah Kerja:
1. **Analisa Tabel:** Minta nama tabel custom dari user (misal tabel Z*). Gunakan `GetTable` (dari `sap-abap-adt`) untuk membaca struktur dan field-nya.
2. **Buat Seeder (ZINSERT):** Gunakan `abap_creation-create_object` (dari `sap_adt_mcp`) untuk membuat Program bernama `ZINSERT_<namatabel>` di package `$TMP` (atau package dari user). Tidak perlu TR untuk `$TMP`. Berikan kode ABAP Open SQL `INSERT` kepada user untuk di-copy-paste.
3. **Buat Report (ZREPORT):** Gunakan `abap_creation-create_object` untuk membuat Program kedua bernama `ZREPORT_<namatabel>`. Berikan kode ABAP berisi `SELECT` dan `cl_demo_output=>display` kepada user untuk di-copy-paste.
4. **Instruksi Akhir:** Pandu user untuk me-refresh Project Explorer di Eclipse, mem-paste kode ke masing-masing program, menyimpan (`Ctrl+S`), mengaktifkan (`Ctrl+F3`), dan mengeksekusi (`F8`).
