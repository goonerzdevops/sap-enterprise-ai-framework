---
name: notion-workspace
description: SOP and tools guide for interacting with Notion workspace via Remote OAuth Proxy, matching Cline's workflow with zero manual page sharing.
---

# Notion Workspace Skill & Proxy Architecture

Skill ini mengatur tata cara berkomunikasi dengan Notion workspace pengguna menggunakan **Notion Remote MCP OAuth Proxy**, sehingga AI dapat membaca, mencari, membuat, dan memperbarui dokumen Notion secara otomatis dan mulus.

---

## 1. Arsitektur & Komponen

| Komponen | Lokasi / Target | Keterangan |
|---|---|---|
| **MCP Config** | `c:\Users\LENOVO\.gemini\config\mcp_config.json` | Dikonfigurasi menggunakan `node` menjalankan `notion-proxy.js`. |
| **Proxy Script** | `C:\D\Software\MCP\notion-remote-proxy\notion-proxy.js` | Jembatan Stdio ke Remote Notion MCP (`https://mcp.notion.com/mcp`). |
| **Token Cache** | `C:\D\Software\MCP\notion-remote-proxy\notion_tokens.json` | Menyimpan `access_token` dan `refresh_token` OAuth Google/Notion. |

### Mekanisme Auto-Refresh Token
- Remote Notion OAuth token memiliki masa aktif 8 jam (`expires_in: 28800`).
- Script `notion-proxy.js` secara otomatis mendeteksi jika token kedaluwarsa atau menerima respons HTTP `401 Unauthorized`.
- Proxy akan otomatis memanggil `https://mcp.notion.com/token` dengan `grant_type: refresh_token`, memperbarui token di `notion_tokens.json`, dan mengulang permintaan tanpa interupsi.

---

## 2. Daftar Tool Utama (Notion Remote MCP)

1. **`notion-search`**:
   - Mencari halaman atau database berdasarkan kata kunci atau judul.
   - Contoh query: `"SAP Latest Insights"`, `"BAdI Guide"`, dsb.
2. **`notion-fetch`**:
   - Menarik seluruh isi teks/blok Markdown dari halaman berdasarkan URL atau Page ID.
3. **`notion-create-pages`**:
   - Membuat halaman baru.
   - Gunakan parameter `creation_mode: "draft"` untuk membuat halaman langsung di area privat pengguna tanpa memerlukan parent ID.
4. **`notion-update-page`**:
   - Memperbarui isi halaman dengan opsi perintah:
     - `insert_content`: Menyisipkan teks tambahan di awal atau akhir halaman.
     - `update_content`: Mencari dan mengganti (*search and replace*) teks tertentu.
     - `replace_content`: Menimpa seluruh isi halaman dengan konten baru.

---

## 3. Best Practices Penggunaan

- **Membaca Dokumen:** Selalu gunakan `notion-search` terlebih dahulu untuk menemukan Page ID dokumen yang dimaksud, lalu panggil `notion-fetch` untuk membaca isinya.
- **Membuat Catatan/Report Baru:** Gunakan `notion-create-pages` dengan judul yang deskriptif dan struktur Markdown standar.
- **Konsistensi dengan Cline:** Karena menggunakan akun OAuth yang sama persis, semua halaman yang dibuat di Antigravity langsung terlihat di Cline dan di aplikasi Notion pengguna.
