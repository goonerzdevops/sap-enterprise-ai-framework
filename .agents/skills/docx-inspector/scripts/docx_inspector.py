#!/usr/bin/env python3
"""
docx_inspector.py - Zero-Dependency High-Performance Word (.docx) Inspector & Batch Engine.
Designed for Agentic Second Brain / SAP RAG architecture.
Uses Python Standard Library ONLY (zipfile, xml.etree.ElementTree).

Capabilities:
1. Batch Mode: Scan a folder of 50+ .docx files in seconds with ZERO Gemini API tokens.
2. Companion Digest: Generate compact <file>_digest.md with TOC outline, table inventory, and diagram list.
3. Asset Extraction: Extract embedded diagrams, UML, flowcharts, and mockups into <file>_assets/ folder.
4. On-Demand Slicing: Extract specific section (--section) or table (--table) in clean Markdown.
"""

import sys
import os
import re
import time
import json
import argparse
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Force UTF-8 encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A_NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
WP_NS = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
V_NS = 'urn:schemas-microsoft-com:vml'

class DocxDocument:
    def __init__(self, filepath):
        self.filepath = Path(filepath).resolve()
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        self.zip_file = zipfile.ZipFile(self.filepath, 'r')
        self.image_rels = self._load_image_relationships()
        self._parse_document()

    def _load_image_relationships(self):
        """Map rId to image target path in word/."""
        rels = {}
        rels_path = 'word/_rels/document.xml.rels'
        if rels_path in self.zip_file.namelist():
            try:
                tree = ET.fromstring(self.zip_file.read(rels_path))
                for r in tree:
                    target = r.attrib.get('Target', '')
                    r_type = r.attrib.get('Type', '')
                    r_id = r.attrib.get('Id')
                    if 'image' in r_type.lower() or target.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.emf', '.wmf')):
                        if not target.startswith('word/'):
                            if target.startswith('/'):
                                target = target.lstrip('/')
                            else:
                                target = 'word/' + target.lstrip('/')
                        rels[r_id] = target
            except Exception:
                pass
        return rels

    def _parse_document(self):
        """Parse headings, paragraphs, tables, and images in linear order."""
        self.sections = [] # list of dict: {title, level, paragraphs: [], tables: [], images: []}
        self.all_tables = []
        self.all_images = []

        if 'word/document.xml' not in self.zip_file.namelist():
            return

        tree = ET.fromstring(self.zip_file.read('word/document.xml'))
        body = tree.find(f'{W_NS}body')
        if body is None:
            return

        current_sec = {
            'title': 'Document Header / Meta',
            'level': 0,
            'paragraphs': [],
            'tables': [],
            'images': []
        }
        self.sections.append(current_sec)

        elements = list(body)
        for i, elem in enumerate(elements):
            if elem.tag == f'{W_NS}p':
                # Paragraph
                pStyle = elem.find(f'.//{W_NS}pStyle')
                style_val = pStyle.attrib.get(f'{W_NS}val', '') if pStyle is not None else ''
                text = ' '.join(''.join(elem.itertext()).split()).strip()

                # Check if Heading
                is_heading = False
                h_level = 1
                if 'heading' in style_val.lower() or style_val in ['1', '2', '3', 'Title', 'Judul']:
                    is_heading = True
                    m = re.search(r'\d+', style_val)
                    if m:
                        h_level = int(m.group(0))
                    elif 'title' in style_val.lower():
                        h_level = 1

                # Detect embedded images inside paragraph
                p_images = []
                for blip in elem.iter(f'{A_NS}blip'):
                    embed_id = blip.attrib.get(f'{R_NS}embed')
                    if embed_id and embed_id in self.image_rels:
                        img_path = self.image_rels[embed_id]
                        img_name = Path(img_path).name
                        p_images.append(img_path)

                        # Extract surrounding caption / context text
                        docPr = elem.find(f'.//{WP_NS}docPr')
                        doc_descr = docPr.attrib.get('descr', '').strip() if docPr is not None else ''
                        doc_name = docPr.attrib.get('name', '').strip() if docPr is not None else ''

                        next_p = ''
                        if i + 1 < len(elements) and elements[i+1].tag == f'{W_NS}p':
                            next_p = ' '.join(''.join(elements[i+1].itertext()).split()).strip()
                        prev_p = ''
                        if i > 0 and elements[i-1].tag == f'{W_NS}p':
                            prev_p = ' '.join(''.join(elements[i-1].itertext()).split()).strip()

                        caption = ''
                        if text:
                            caption = text
                        elif doc_descr:
                            caption = doc_descr
                        elif next_p and (any(k in next_p.lower()[:30] for k in ['gbr', 'gambar', 'fig', 'figure', 'screen', 'bagan', 'tangkapan', 'tabel', 'alur', 'flow']) or len(next_p) <= 140):
                            caption = next_p
                        elif prev_p and (any(k in prev_p.lower()[:30] for k in ['gbr', 'gambar', 'fig', 'figure', 'screen', 'bagan', 'tangkapan', 'tabel', 'alur', 'flow']) or len(prev_p) <= 140):
                            caption = prev_p
                        elif doc_name and not doc_name.lower().startswith('image ') and not doc_name.lower().startswith('picture '):
                            caption = doc_name
                        else:
                            caption = next_p[:120] if next_p else f"Visual diagram in {current_sec['title']}"

                        caption_clean = re.sub(r'[\r\n\t]+', ' ', caption).replace('|', '/').strip()
                        if not caption_clean:
                            caption_clean = f"Visual diagram in {current_sec['title']}"

                        self.all_images.append({
                            'path': img_path,
                            'name': img_name,
                            'section': current_sec['title'],
                            'caption': caption_clean[:140]
                        })

                if is_heading and text:
                    # Start new section
                    current_sec = {
                        'title': text,
                        'level': h_level,
                        'paragraphs': [],
                        'tables': [],
                        'images': list(p_images)
                    }
                    self.sections.append(current_sec)
                else:
                    if text:
                        current_sec['paragraphs'].append(text)
                    if p_images:
                        current_sec['images'].extend(p_images)

            elif elem.tag == f'{W_NS}tbl':
                # Table
                table_data = []
                for row_elem in elem.findall(f'{W_NS}tr'):
                    row = []
                    for cell_elem in row_elem.findall(f'{W_NS}tc'):
                        cell_text = ' '.join(''.join(cell_elem.itertext()).split()).strip()
                        row.append(cell_text)
                    if row:
                        table_data.append(row)

                if table_data:
                    tbl_info = {
                        'index': len(self.all_tables) + 1,
                        'section': current_sec['title'],
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0,
                        'headers': table_data[0] if table_data else [],
                        'data': table_data
                    }
                    self.all_tables.append(tbl_info)
                    current_sec['tables'].append(tbl_info)

    def _is_substantive_asset(self, zip_path, img_meta=None):
        """Filter out non-substantive assets like company logos, signatures, and tiny icons."""
        try:
            info = self.zip_file.getinfo(zip_path)
            # 1. Skip tiny files (< 3.5 KB) which are bullet icons, line dividers, spacers
            if info.file_size < 3500:
                return False
        except Exception:
            info = None

        if img_meta:
            cap_lower = img_meta.get('caption', '').lower()
            name_lower = img_meta.get('name', '').lower()
            sec_lower = img_meta.get('section', '').lower()
            combined = f"{name_lower} {cap_lower} {sec_lower}"

            # If it's located in document header/meta and has generic caption, it's typically a company logo/banner
            if 'document header' in sec_lower and (info and info.file_size < 20000) and not any(k in cap_lower for k in ['diagram', 'flow', 'arsitektur', 'tabel', 'screen']):
                return False

            # Noise keywords
            noise_kw = ['tanda tangan', 'paraf', 'signature', 'stempel', 'company logo', 'logo perusahaan', 'kop surat', 'watermark']
            # Substantive bypass keywords
            substantive_kw = ['screen', 'tampilan', 'form', 'alv', 'tabel', 'alur', 'flow', 'diagram', 'arsitektur', 'erd', 'uml', 'preview', 'smartform', 'gbr', 'gambar', 'fig']

            if any(n in combined for n in noise_kw) and not any(s in combined for s in substantive_kw):
                return False

        return True

    def extract_assets(self, output_dir, filter_noise=True):
        """Extract substantive media files from docx into output_dir (filters noise like logos/signatures)."""
        out_path = Path(output_dir)
        extracted = []
        media_files = [f for f in self.zip_file.namelist() if f.startswith('word/media/')]
        if not media_files:
            return extracted

        meta_by_name = {img['name']: img for img in self.all_images}

        out_path.mkdir(parents=True, exist_ok=True)
        for m in media_files:
            filename = Path(m).name
            img_meta = meta_by_name.get(filename)

            if filter_noise and not self._is_substantive_asset(m, img_meta):
                continue

            target_file = out_path / filename
            with self.zip_file.open(m) as src, open(target_file, 'wb') as dst:
                dst.write(src.read())
            extracted.append(target_file)
        return extracted

    def generate_digest(self, output_md_path=None, asset_folder_rel=None):
        """Generate high-density token-efficient Companion Digest."""
        lines = []
        file_size_kb = os.path.getsize(self.filepath) / 1024
        doc_name = self.filepath.name

        lines.append(f"# Word Document Digest: `{doc_name}`")
        lines.append("")
        lines.append(f"- **Source File:** `{doc_name}`")
        lines.append(f"- **File Size:** {file_size_kb:.1f} KB")
        lines.append(f"- **Total Sections/Headings:** {len(self.sections)}")
        lines.append(f"- **Total Tables:** {len(self.all_tables)}")
        lines.append(f"- **Total Embedded Images/Diagrams:** {len(self.all_images)}")
        if asset_folder_rel:
            lines.append(f"- **Extracted Assets Folder:** `{asset_folder_rel}`")
        lines.append("")

        script_path = Path(__file__).resolve()
        abs_doc_path = self.filepath.resolve()

        lines.append("> [!NOTE]")
        lines.append("> **Agentic Usage Guide (Siap Eksekusi):**")
        lines.append(f"> - Ekstrak Isi Bab Spesifik: `python \"{script_path}\" --file \"{abs_doc_path}\" --section \"<Judul_Bab>\"`")
        lines.append(f"> - Ekstrak Tabel Spesifik:  `python \"{script_path}\" --file \"{abs_doc_path}\" --table <nomor_tabel> --format kv`")
        lines.append("> *(Opsi format tabel: `--format kv` untuk Key-Value anti-halusinasi, `--format json` untuk output JSON terstruktur, `--format markdown` untuk tabel pipa)*")
        lines.append("")

        # 1. Heading Outline (TOC)
        lines.append("## 📑 Table of Contents (Outline)")
        lines.append("| Level | Section Title | Paragraphs | Tables | Diagrams/Images |")
        lines.append("|:---:|---|:---:|:---:|---|")
        for s in self.sections:
            if s['title'] == 'Document Header / Meta' and not s['paragraphs'] and not s['tables']:
                continue
            lvl_indent = "—" * max(0, s['level'] - 1) + (" " if s['level'] > 1 else "")
            title_display = f"{lvl_indent}**{s['title']}**" if s['level'] <= 1 else f"{lvl_indent}{s['title']}"
            img_badge = f"`{len(s['images'])} images`" if s['images'] else "-"
            tbl_badge = f"`{len(s['tables'])} tables`" if s['tables'] else "-"
            lines.append(f"| H{s['level']} | {title_display} | {len(s['paragraphs'])} | {tbl_badge} | {img_badge} |")
        lines.append("")

        # 2. Table Inventory
        if self.all_tables:
            lines.append("## 📊 Table Inventory")
            lines.append("| Table # | Section | Dimensions | Column Headers Preview |")
            lines.append("|:---:|---|:---:|---|")
            for t in self.all_tables:
                hdr_preview = ", ".join([f"`{h}`" for h in t['headers'][:6]])
                if len(t['headers']) > 6:
                    hdr_preview += f" ... (+{len(t['headers'])-6} more)"
                lines.append(f"| **T{t['index']}** | {t['section']} | {t['rows']} rows x {t['cols']} cols | {hdr_preview} |")
            lines.append("")

        # 3. Visual Assets / Diagram Catalog (Substantive Only)
        substantive_images = [img for img in self.all_images if self._is_substantive_asset(img['path'], img)]
        if substantive_images:
            lines.append("## 🖼️ Embedded Diagrams & Visual Assets Catalog")
            lines.append("> [!TIP]")
            lines.append("> **Petunjuk AI/LLM Tanpa Vision (Text-Only / DeepSeek API):**")
            lines.append("> Kolom **Caption / Context Description** di bawah menyajikan teks judul gambar, keterangan bagan, atau paragraf kontekstual yang diekstrak langsung dari sekeliling gambar di dokumen asli. Anda dapat memahami fungsi diagram arsitektur, flowchart alur proses, struktur tabel, atau mockup SAP tanpa perlu menginspeksi file gambar fisik!")
            lines.append("> *(Aset non-substantif seperti logo perusahaan, scan tanda tangan/paraf, dan icon dekorasi telah difilter otomatis)*")
            lines.append("")
            lines.append("| Asset Name | Belongs to Section | Caption / Context Description | Local Asset Path |")
            lines.append("|---|---|---|---|")
            seen_imgs = set()
            for img in substantive_images:
                name = img['name']
                if name in seen_imgs:
                    continue
                seen_imgs.add(name)
                rel_link = f"`{asset_folder_rel}/{name}`" if asset_folder_rel else f"`word/media/{name}`"
                lines.append(f"| `{name}` | {img['section']} | {img['caption']} | {rel_link} |")
            lines.append("")

        content = "\n".join(lines)
        if output_md_path:
            with open(output_md_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def get_section_content(self, section_query, out_format='markdown'):
        """Extract content of a specific section matching query."""
        q = section_query.strip().lower()
        matched = []
        for s in self.sections:
            if q in s['title'].strip().lower():
                matched.append(s)

        if not matched:
            avail = [s['title'] for s in self.sections if s['title']]
            return f"Section matching '{section_query}' not found. Available sections: {avail}"

        out = []
        for s in matched:
            out.append(f"## {s['title']}")
            if s['images']:
                out.append(f"_Embedded Images in this section:_ " + ", ".join([f"`{Path(p).name}`" for p in s['images']]))
                out.append("")
            for p in s['paragraphs']:
                out.append(p)
                out.append("")
            for t in s['tables']:
                out.append(f"### Table {t['index']} ({t['rows']} rows x {t['cols']} cols)")
                if out_format in ['kv', 'json']:
                    out.append(self.get_table_data(t['index'], out_format=out_format))
                else:
                    if t['data']:
                        out.append("| " + " | ".join(t['data'][0]) + " |")
                        out.append("|" + "|".join([":---" for _ in t['data'][0]]) + "|")
                        for row in t['data'][1:]:
                            out.append("| " + " | ".join(row) + " |")
                out.append("")
        return "\n".join(out)

    def get_table_data(self, table_idx, out_format='markdown'):
        """Extract and format a specific table as Markdown, JSON, or Key-Value pairs."""
        if not (1 <= table_idx <= len(self.all_tables)):
            return f"Table #{table_idx} not found. Total tables: {len(self.all_tables)}"
        t = self.all_tables[table_idx - 1]

        if out_format == 'json':
            headers = [h if h else f"Col_{c_idx+1}" for c_idx, h in enumerate(t['headers'])]
            records = []
            for row in t['data'][1:]:
                rec = {}
                for c_idx, val in enumerate(row):
                    h_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx+1}"
                    rec[h_name] = val
                records.append(rec)
            return json.dumps(records, indent=2, ensure_ascii=False)

        elif out_format == 'kv':
            headers = [h if h else f"Col_{c_idx+1}" for c_idx, h in enumerate(t['headers'])]
            lines = [f"=== TABLE {t['index']}: {t['section']} ({t['rows']} rows x {t['cols']} cols) ==="]
            for r_idx, row in enumerate(t['data'][1:], 1):
                lines.append(f"--- Row {r_idx} ---")
                for c_idx, val in enumerate(row):
                    h_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx+1}"
                    lines.append(f"  {h_name}: {val}")
            return "\n".join(lines)

        else: # markdown
            out = [f"**Table {t['index']}** in `{t['section']}` ({t['rows']} rows x {t['cols']} cols)", ""]
            if t['data']:
                out.append("| " + " | ".join(t['data'][0]) + " |")
                out.append("|" + "|".join([":---" for _ in t['data'][0]]) + "|")
                for row in t['data'][1:]:
                    out.append("| " + " | ".join(row) + " |")
            return "\n".join(out)

    def close(self):
        self.zip_file.close()


def process_batch(target_dir, recursive=False, extract_assets=True):
    """Process all .docx files in directory in batch mode (0 Gemini tokens)."""
    root = Path(target_dir).resolve()
    pattern = "**/*.docx" if recursive else "*.docx"
    docx_files = [f for f in root.glob(pattern) if not f.name.startswith('~$')]

    print("=" * 80)
    print(f"🚀 DOCX BATCH INSPECTION ENGINE: {len(docx_files)} files in '{root.name}'")
    print(f"Mode: Local Zero-Dependency Python (0 Gemini API Tokens Used)")
    print("=" * 80)

    summary_rows = []
    t_start = time.time()

    for idx, f in enumerate(docx_files, 1):
        t0 = time.time()
        try:
            doc = DocxDocument(f)
            asset_rel = None
            extracted_cnt = 0

            # Extract assets if file has media
            if extract_assets and doc.image_rels:
                asset_dir = f.parent / f"{f.stem}_assets"
                extracted = doc.extract_assets(asset_dir)
                extracted_cnt = len(extracted)
                asset_rel = f"{f.stem}_assets"

            # Generate digest
            digest_path = f.parent / f"{f.stem}_digest.md"
            doc.generate_digest(str(digest_path), asset_folder_rel=asset_rel)
            elapsed = time.time() - t0

            summary_rows.append({
                'num': idx,
                'name': f.name,
                'parent': f.parent.name,
                'sections': len(doc.sections),
                'tables': len(doc.all_tables),
                'images': extracted_cnt,
                'status': 'OK',
                'time': f"{elapsed:.2f}s"
            })
            print(f"[{idx:2d}/{len(docx_files)}] ✔ {f.name[:45]:<45} | {len(doc.sections):2d} secs | {len(doc.all_tables):2d} tbls | {extracted_cnt:2d} imgs | {elapsed:.2f}s")
            doc.close()
        except Exception as e:
            summary_rows.append({
                'num': idx,
                'name': f.name,
                'parent': f.parent.name,
                'sections': 0,
                'tables': 0,
                'images': 0,
                'status': f'ERR: {str(e)[:20]}',
                'time': "0s"
            })
            print(f"[{idx:2d}/{len(docx_files)}] ❌ {f.name[:45]:<45} | ERROR: {e}")

    total_time = time.time() - t_start
    total_imgs = sum(r['images'] for r in summary_rows)
    total_tbls = sum(r['tables'] for r in summary_rows)

    print("=" * 80)
    print(f"🎉 Batch Finished in {total_time:.2f} seconds!")
    print(f"📊 Total Documents Processed: {len(docx_files)}")
    print(f"📊 Total Tables Cataloged:    {total_tbls}")
    print(f"🖼️ Total Diagrams/Images:    {total_imgs} extracted to local assets")
    print(f"🪙 Gemini API Quota Consumed: 0 TOKENS (100% Local Execution)")
    print("=" * 80)

    # Generate master inventory file
    inv_md = root / "00_DOCX_INVENTORY.md"
    with open(inv_md, 'w', encoding='utf-8') as inv_f:
        inv_f.write(f"# Master Docx Inventory: `{root.name}`\n\n")
        inv_f.write(f"- **Generated:** Local Batch Inspector Engine\n")
        inv_f.write(f"- **Total Documents:** {len(docx_files)}\n")
        inv_f.write(f"- **Total Tables:** {total_tbls}\n")
        inv_f.write(f"- **Total Diagrams/Images Extracted:** {total_imgs}\n\n")
        inv_f.write("| # | Document File | Subfolder | Sections | Tables | Diagrams/Images | Digest Link |\n")
        inv_f.write("|:---:|---|---|:---:|:---:|:---:|---|\n")
        for r in summary_rows:
            stem = Path(r['name']).stem
            inv_f.write(f"| {r['num']} | `{r['name']}` | `{r['parent']}` | {r['sections']} | {r['tables']} | {r['images']} | [[{stem}_digest.md]] |\n")
    print(f"Inventory saved: {inv_md}")


def main():
    parser = argparse.ArgumentParser(description="Zero-Dependency Docx Inspector & Batch Engine for Second Brain.")
    parser.add_argument("--dir", "-d", help="Directory path to run batch inspection on all .docx files")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan subdirectories recursively")
    parser.add_argument("--file", "-f", help="Single .docx file path")
    parser.add_argument("--digest", action="store_true", help="Generate companion digest")
    parser.add_argument("--extract-assets", action="store_true", default=True, help="Extract embedded diagrams & images")
    parser.add_argument("--section", "-s", help="Extract specific section text and tables")
    parser.add_argument("--table", "-t", type=int, help="Extract specific table # as Markdown, JSON, or KV")
    parser.add_argument("--format", choices=['markdown', 'json', 'kv'], default='markdown', help="Output format for tables (markdown, json, kv)")
    parser.add_argument("--outline", "-o", action="store_true", help="Display TOC outline")

    args = parser.parse_args()

    if args.dir:
        process_batch(args.dir, recursive=args.recursive, extract_assets=args.extract_assets)
        return

    if args.file:
        doc = DocxDocument(args.file)
        if args.outline:
            print(f"Outline of {Path(args.file).name}:")
            for s in doc.sections:
                indent = "  " * s['level']
                print(f"{indent}- H{s['level']} {s['title']} ({len(s['paragraphs'])} paras, {len(s['tables'])} tables, {len(s['images'])} imgs)")
            doc.close()
            return

        if args.table:
            print(doc.get_table_data(args.table, out_format=args.format))
            doc.close()
            return

        if args.section:
            print(doc.get_section_content(args.section, out_format=args.format))
            doc.close()
            return

        if args.digest:
            p = Path(args.file)
            asset_dir = p.parent / f"{p.stem}_assets"
            asset_rel = None
            if args.extract_assets and doc.image_rels:
                doc.extract_assets(asset_dir)
                asset_rel = f"{p.stem}_assets"
            out_digest = p.parent / f"{p.stem}_digest.md"
            doc.generate_digest(str(out_digest), asset_folder_rel=asset_rel)
            print(f"Digest created: {out_digest}")
            doc.close()
            return

        # Default action for single file: print digest to stdout
        print(doc.generate_digest())
        doc.close()
        return

    parser.print_help()

if __name__ == "__main__":
    main()
