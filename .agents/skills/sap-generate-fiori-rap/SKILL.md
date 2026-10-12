---
name: sap-generate-fiori-rap
description: Automated SOP to transform any Z Table into a Web-based Fiori Application using RAP (SOP otomatis mengubah Tabel Z menjadi Aplikasi Fiori Web berbasis API OData).
---

# 🇬🇧 English
**Objective:** Guide the AI to generate a complete RESTful ABAP Programming (RAP) stack (CDS, BDEF, SRVD, SRVB) from a database table to expose an OData API for SAP Fiori.

## Workflow:
1. **List Generators:** Call `abap_generators-list_generators` (from `sap_adt_mcp`) to identify the available RAP generators (e.g., `x-ui-service` for full RAP + Fiori UI, or `webapi-service`). Ask the user which one they prefer.
2. **Get Schema:** Call `abap_generators-get_schema` for the chosen generator type to understand the required JSON payload format.
3. **Draft Payload:** Read the target database table structure using `GetTable`. Draft the JSON payload containing the required parameters (package name, transport request if not $TMP, table name, and desired CDS/Behavior names). Show the drafted JSON to the user for confirmation.
4. **Generate Objects:** Once confirmed, execute `abap_generators-generate_objects` using the drafted JSON payload to generate the RAP artifacts in the SAP backend.
5. **Final Instructions:** Guide the user to refresh Eclipse, verify the generated CDS views and Service Binding, publish the Service Binding locally, and preview the Fiori app.

---

# 🇮🇩 Bahasa Indonesia
**Tujuan:** Memandu AI men-generate stack RAP (CDS, BDEF, SRVD, SRVB) dari tabel database untuk mengekspos OData API untuk SAP Fiori.

## Langkah Kerja:
1. **Cek Generator:** Panggil `abap_generators-list_generators` (dari `sap_adt_mcp`) untuk melihat generator RAP yang tersedia (misal: `x-ui-service` untuk Fiori UI lengkap). Tanyakan ke user ingin menggunakan yang mana.
2. **Ambil Skema:** Panggil `abap_generators-get_schema` untuk tipe generator yang dipilih agar AI tahu format JSON yang dibutuhkan.
3. **Rancang Payload:** Baca struktur tabel menggunakan `GetTable`. Buat draft payload JSON berisi parameter yang dibutuhkan (nama package, TR jika bukan $TMP, nama tabel, dan nama CDS). Tunjukkan draft JSON ke user untuk disetujui.
4. **Generate Objek:** Setelah disetujui, eksekusi `abap_generators-generate_objects` menggunakan JSON tersebut untuk memproduksi ratusan baris kode RAP di backend SAP.
5. **Instruksi Akhir:** Pandu user untuk me-refresh Eclipse, mengecek CDS dan Service Binding, mem-publish Service Binding, dan melakukan preview aplikasi Fiori.
