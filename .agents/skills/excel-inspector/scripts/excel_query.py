#!/usr/bin/env python3
"""
excel_query.py - Zero-dependency High-Performance Excel (.xlsx) Inspector & Query Engine.
Designed for Agentic Second Brain / SAP RAG architecture.
Uses Python Standard Library ONLY (zipfile, xml.etree.ElementTree).

Features:
1. --digest: Generate a compact companion Markdown file (<filename>_digest.md) containing
   sheet inventory, headers, row counts, and distinct values of categorical columns.
2. --query: Selectively filter and extract rows matching criteria with column projection.
3. --preview: Quick snapshot of first N rows.
4. --sheets: List sheets in the workbook.
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

# Force UTF-8 encoding for standard outputs on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

NS_MAIN = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
NS_REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'
NS_OFFICE_REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def col_to_idx(col_str):
    """Convert column letters (e.g. 'A', 'Z', 'AA') to 0-based index."""
    num = 0
    for c in col_str.upper():
        if 'A' <= c <= 'Z':
            num = num * 26 + (ord(c) - ord('A')) + 1
    return max(0, num - 1)

def parse_cell_ref(ref):
    """Parse 'AA4' -> (26, 4)."""
    m = re.match(r'([A-Za-z]+)([0-9]+)', ref)
    if m:
        return col_to_idx(m.group(1)), int(m.group(2))
    return 0, 0

class ExcelWorkbook:
    def __init__(self, filepath):
        self.filepath = Path(filepath).resolve()
        if not self.filepath.exists():
            raise FileNotFoundError(f"Excel file not found: {self.filepath}")
        
        self.zip_file = zipfile.ZipFile(self.filepath, 'r')
        self.shared_strings = self._load_shared_strings()
        self.sheets = self._load_sheets()

    def _load_shared_strings(self):
        strings = []
        if 'xl/sharedStrings.xml' in self.zip_file.namelist():
            try:
                tree = ET.fromstring(self.zip_file.read('xl/sharedStrings.xml'))
                for si in tree.iter(f'{NS_MAIN}si'):
                    strings.append(''.join(si.itertext()))
            except Exception:
                pass
        return strings

    def _load_sheets(self):
        """Map sheet names to internal target xml paths."""
        rels = {}
        if 'xl/_rels/workbook.xml.rels' in self.zip_file.namelist():
            try:
                tree = ET.fromstring(self.zip_file.read('xl/_rels/workbook.xml.rels'))
                for rel in tree:
                    r_id = rel.attrib.get('Id')
                    target = rel.attrib.get('Target', '')
                    if not target.startswith('xl/'):
                        if target.startswith('/xl/'):
                            target = target[1:]
                        else:
                            target = 'xl/' + target.lstrip('/')
                    rels[r_id] = target
            except Exception:
                pass

        sheets = []
        if 'xl/workbook.xml' in self.zip_file.namelist():
            tree = ET.fromstring(self.zip_file.read('xl/workbook.xml'))
            for s in tree.iter(f'{NS_MAIN}sheet'):
                name = s.attrib.get('name')
                sheet_id = s.attrib.get('sheetId')
                r_id = s.attrib.get(f'{NS_OFFICE_REL}id') or s.attrib.get('r:id')
                target = rels.get(r_id)
                if not target:
                    # Fallback pattern
                    target = f"xl/worksheets/sheet{sheet_id}.xml"
                sheets.append({'name': name, 'id': sheet_id, 'target': target})
        return sheets

    def get_sheet_names(self):
        return [s['name'] for s in self.sheets]

    def read_sheet(self, sheet_name=None):
        """Read rows of a sheet as 2D list of strings with coordinate preservation."""
        target = None
        matched_name = sheet_name
        if not sheet_name:
            if self.sheets:
                target = self.sheets[0]['target']
                matched_name = self.sheets[0]['name']
        else:
            sheet_name_clean = sheet_name.strip().lower()
            for s in self.sheets:
                if s['name'].strip().lower() == sheet_name_clean:
                    target = s['target']
                    matched_name = s['name']
                    break
            # Partial match if not exact
            if not target:
                for s in self.sheets:
                    if sheet_name_clean in s['name'].strip().lower():
                        target = s['target']
                        matched_name = s['name']
                        break

        if not target or target not in self.zip_file.namelist():
            raise ValueError(f"Sheet '{sheet_name}' not found. Available: {self.get_sheet_names()}")

        xml_content = self.zip_file.read(target)
        tree = ET.fromstring(xml_content)

        raw_rows = []
        for r in tree.iter(f'{NS_MAIN}row'):
            row_idx = int(r.attrib.get('r', len(raw_rows) + 1))
            cells = {}
            for c in r.iter(f'{NS_MAIN}c'):
                ref = c.attrib.get('r')
                col_i = 0
                if ref:
                    col_i, _ = parse_cell_ref(ref)
                
                cell_type = c.attrib.get('t')
                val = ""
                if cell_type == 's':
                    v_elem = c.find(f'{NS_MAIN}v')
                    if v_elem is not None and v_elem.text:
                        try:
                            s_idx = int(v_elem.text.strip())
                            if s_idx < len(self.shared_strings):
                                val = self.shared_strings[s_idx]
                        except ValueError:
                            val = v_elem.text.strip()
                elif cell_type == 'inlineStr':
                    val = ''.join(c.itertext()).strip()
                elif cell_type == 'b':
                    v_elem = c.find(f'{NS_MAIN}v')
                    val = "TRUE" if v_elem is not None and v_elem.text == '1' else "FALSE"
                else:
                    v_elem = c.find(f'{NS_MAIN}v')
                    if v_elem is not None and v_elem.text:
                        val = v_elem.text.strip()

                cells[col_i] = val.strip()

            if cells:
                max_c = max(cells.keys())
                row_arr = [cells.get(i, "") for i in range(max_c + 1)]
                raw_rows.append((row_idx, row_arr))

        return matched_name, raw_rows

    def close(self):
        self.zip_file.close()


def detect_header_and_data(raw_rows):
    """
    Auto-detect header row and separate data rows.
    Heuristic: The first row that has >= 2 non-empty text cells and is not just a title banner.
    """
    if not raw_rows:
        return 0, [], []

    header_row_idx = None
    headers = []

    for idx, (r_num, row) in enumerate(raw_rows):
        non_empty = [c for c in row if c]
        # Skip single-cell banner rows
        if len(non_empty) >= 2:
            header_row_idx = idx
            headers = [c if c else f"Col_{i+1}" for i, c in enumerate(row)]
            break

    if header_row_idx is None:
        # Fallback to first row
        header_row_idx = 0
        headers = [c if c else f"Col_{i+1}" for i, c in enumerate(raw_rows[0][1])]

    # Normalize headers
    clean_headers = []
    seen = {}
    for i, h in enumerate(headers):
        clean_h = re.sub(r'[\r\n]+', ' ', h).strip()
        if not clean_h:
            clean_h = f"Col_{i+1}"
        if clean_h in seen:
            seen[clean_h] += 1
            clean_h = f"{clean_h}_{seen[clean_h]}"
        else:
            seen[clean_h] = 1
        clean_headers.append(clean_h)

    # Collect data rows
    data_rows = []
    num_cols = len(clean_headers)
    for r_num, row in raw_rows[header_row_idx + 1:]:
        # Pad or trim row to match headers length
        padded = (row + [""] * num_cols)[:num_cols]
        # Ignore completely empty rows
        if any(padded):
            data_rows.append(padded)

    return header_row_idx, clean_headers, data_rows


def generate_digest(excel_path, output_md_path=None):
    """Generate a high-density, token-efficient companion Markdown digest."""
    wb = ExcelWorkbook(excel_path)
    sheet_names = wb.get_sheet_names()
    file_size_kb = os.path.getsize(excel_path) / 1024

    md_lines = []
    md_lines.append(f"# Excel Companion Digest: `{Path(excel_path).name}`")
    md_lines.append("")
    md_lines.append(f"- **Source File:** `{Path(excel_path).name}`")
    md_lines.append(f"- **File Size:** {file_size_kb:.1f} KB")
    md_lines.append(f"- **Total Sheets:** {len(sheet_names)}")
    md_lines.append(f"- **Sheets:** " + ", ".join([f"`{s}`" for s in sheet_names]))
    md_lines.append("")
    md_lines.append("> [!NOTE]")
    md_lines.append("> **Agentic Usage Guide:** File ini adalah ringkasan skema & kamus nilai untuk menghemat token.")
    md_lines.append("> Gunakan script `python excel_query.py --file <file> --sheet <sheet> --filter \"<col>=<val>\"` untuk mengambil baris spesifik.")
    md_lines.append("")

    for s_name in sheet_names:
        try:
            matched_name, raw_rows = wb.read_sheet(s_name)
            _, headers, data = detect_header_and_data(raw_rows)
            md_lines.append(f"## Sheet: `{matched_name}`")
            md_lines.append(f"- **Total Records:** {len(data)} rows")
            md_lines.append(f"- **Total Columns:** {len(headers)}")
            md_lines.append(f"- **Columns:** {', '.join([f'`{h}`' for h in headers])}")
            md_lines.append("")

            # Find categorical columns (columns with <= 15 unique values and non-trivial counts)
            cat_summaries = []
            for col_i, header_name in enumerate(headers):
                vals = [row[col_i] for row in data if row[col_i]]
                if not vals:
                    continue
                distinct_vals = {}
                for v in vals:
                    distinct_vals[v] = distinct_vals.get(v, 0) + 1
                
                # If unique count is between 2 and 15 and row count > 3
                if 1 < len(distinct_vals) <= 15 and len(vals) >= 3:
                    top_vals = [f"`{k}` ({count})" for k, count in sorted(distinct_vals.items(), key=lambda x: -x[1])[:8]]
                    cat_summaries.append((header_name, len(distinct_vals), ", ".join(top_vals)))

            if cat_summaries:
                md_lines.append("### Key Categorical Columns (Filters)")
                md_lines.append("| Column | Unique Count | Distinct Values (Top) |")
                md_lines.append("|---|:---:|---|")
                for col_name, u_cnt, top_str in cat_summaries:
                    md_lines.append(f"| `{col_name}` | {u_cnt} | {top_str} |")
                md_lines.append("")

            # 2-Row Sample Preview
            if data:
                md_lines.append("### Sample Preview (First 2 Rows)")
                # Truncate to first 8 columns for compact display
                preview_cols = headers[:8]
                md_lines.append("| " + " | ".join(preview_cols) + " |")
                md_lines.append("|" + "|".join([":---" for _ in preview_cols]) + "|")
                for row in data[:2]:
                    preview_vals = [re.sub(r'[\r\n]+', ' ', str(row[i]))[:50] for i in range(len(preview_cols))]
                    md_lines.append("| " + " | ".join(preview_vals) + " |")
                md_lines.append("")

        except Exception as e:
            md_lines.append(f"## Sheet: `{s_name}` (Error parsing: {e})")
            md_lines.append("")

    wb.close()

    content = "\n".join(md_lines)
    if output_md_path:
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Digest successfully created: {output_md_path}")
    else:
        print(content)


def query_data(excel_path, sheet_name=None, filters=None, columns=None, limit=20, offset=0, out_format='markdown'):
    """Query data from a sheet with filtering and column selection."""
    wb = ExcelWorkbook(excel_path)
    matched_name, raw_rows = wb.read_sheet(sheet_name)
    _, headers, data = detect_header_and_data(raw_rows)
    wb.close()

    header_lower_map = {h.lower(): i for i, h in enumerate(headers)}

    # Parse filters: List of tuples (col_idx, operator, target_val_lower)
    parsed_filters = []
    if filters:
        for f in filters:
            if '=' in f:
                col_key, target_val = f.split('=', 1)
                op = '='
            elif '~' in f:
                col_key, target_val = f.split('~', 1)
                op = '~'
            else:
                continue

            col_key_clean = col_key.strip().lower()
            # Match column name
            matched_col_idx = None
            for h_low, idx in header_lower_map.items():
                if h_low == col_key_clean or col_key_clean in h_low:
                    matched_col_idx = idx
                    break
            
            if matched_col_idx is not None:
                parsed_filters.append((matched_col_idx, op, target_val.strip().lower()))
            else:
                print(f"[Warning] Filter column '{col_key}' not found in sheet '{matched_name}'. Available: {headers}", file=sys.stderr)

    # Filter rows
    matched_rows = []
    for row in data:
        keep = True
        for col_idx, op, target_val in parsed_filters:
            cell_val = str(row[col_idx]).strip().lower()
            if op == '=' and cell_val != target_val:
                keep = False
                break
            elif op == '~' and target_val not in cell_val:
                keep = False
                break
        if keep:
            matched_rows.append(row)

    # Select columns
    if columns:
        col_indices = []
        selected_headers = []
        for req_col in [c.strip() for c in columns.split(',') if c.strip()]:
            req_low = req_col.lower()
            found = False
            for h_low, idx in header_lower_map.items():
                if h_low == req_low or req_low in h_low:
                    col_indices.append(idx)
                    selected_headers.append(headers[idx])
                    found = True
                    break
            if not found:
                print(f"[Warning] Column '{req_col}' not found. Skipping.", file=sys.stderr)
        if not col_indices:
            col_indices = list(range(len(headers)))
            selected_headers = headers
    else:
        col_indices = list(range(len(headers)))
        selected_headers = headers

    # Apply offset & limit
    total_matches = len(matched_rows)
    paged_rows = matched_rows[offset:]
    if limit > 0:
        paged_rows = paged_rows[:limit]

    # Format output
    if out_format == 'json':
        records = []
        for row in paged_rows:
            record = {selected_headers[i]: row[col_indices[i]] for i in range(len(selected_headers))}
            records.append(record)
        print(json.dumps({'total': total_matches, 'returned': len(records), 'data': records}, indent=2, ensure_ascii=False))

    elif out_format == 'csv':
        import csv
        writer = csv.writer(sys.stdout)
        writer.writerow(selected_headers)
        for row in paged_rows:
            writer.writerow([row[i] for i in col_indices])

    else:
        # Markdown table
        print(f"**Query Results from `{matched_name}`** ({len(paged_rows)} of {total_matches} matches)")
        print()
        if not paged_rows:
            print("_No matching records found._")
            return

        header_line = "| " + " | ".join(selected_headers) + " |"
        sep_line = "|" + "|".join([":---" for _ in selected_headers]) + "|"
        print(header_line)
        print(sep_line)
        for row in paged_rows:
            row_vals = [re.sub(r'[\r\n]+', ' ', str(row[i])) for i in col_indices]
            print("| " + " | ".join(row_vals) + " |")



def process_batch(target_dir, recursive=False):
    """Process all .xlsx files in directory in batch mode (0 Gemini tokens)."""
    root = Path(target_dir).resolve()
    pattern = "**/*.xlsx" if recursive else "*.xlsx"
    excel_files = [f for f in root.glob(pattern) if not f.name.startswith('~$') and f.is_file()]

    print("=" * 80)
    print(f"🚀 EXCEL BATCH INSPECTION ENGINE: {len(excel_files)} files in '{root.name}'")
    print(f"Mode: Local Zero-Dependency Python (0 Gemini API Tokens Used)")
    print("=" * 80)

    summary_rows = []
    t_start = time.time()

    for idx, f in enumerate(excel_files, 1):
        t0 = time.time()
        try:
            wb = ExcelWorkbook(f)
            sheet_names = wb.get_sheet_names()
            total_rows = 0
            total_cols = 0
            for s in sheet_names:
                _, raw_rows = wb.read_sheet(s)
                _, headers, data = detect_header_and_data(raw_rows)
                total_rows += len(data)
                total_cols = max(total_cols, len(headers))
            wb.close()

            # Generate companion digest
            digest_path = f.parent / f"{f.stem}_digest.md"
            generate_digest(str(f), str(digest_path))
            elapsed = time.time() - t0

            summary_rows.append({
                'num': idx,
                'name': f.name,
                'parent': f.parent.name,
                'size_kb': f"{f.stat().st_size / 1024:.1f} KB",
                'sheets': len(sheet_names),
                'sheet_names': ", ".join([f"`{s}`" for s in sheet_names[:3]]) + (f" (+{len(sheet_names)-3} more)" if len(sheet_names) > 3 else ""),
                'rows': total_rows,
                'cols': total_cols,
                'status': 'OK',
                'time': f"{elapsed:.2f}s"
            })
            print(f"[{idx:2d}/{len(excel_files)}] ✔ {f.name[:45]:<45} | {len(sheet_names):2d} sheets | {total_rows:3d} rows | {total_cols:2d} cols | {elapsed:.2f}s")
        except Exception as e:
            summary_rows.append({
                'num': idx,
                'name': f.name,
                'parent': f.parent.name,
                'size_kb': f"{f.stat().st_size / 1024:.1f} KB",
                'sheets': 0,
                'sheet_names': "-",
                'rows': 0,
                'cols': 0,
                'status': f"ERR: {str(e)[:20]}",
                'time': "0s"
            })
            print(f"[{idx:2d}/{len(excel_files)}] ❌ {f.name[:45]:<45} | ERROR: {e}")

    total_time = time.time() - t_start
    total_sheets = sum(r['sheets'] for r in summary_rows)
    total_rows_all = sum(r['rows'] for r in summary_rows)

    print("=" * 80)
    print(f"🎉 Batch Finished in {total_time:.2f} seconds!")
    print(f"📊 Total Workbooks Processed: {len(excel_files)}")
    print(f"📊 Total Sheets Cataloged:    {total_sheets}")
    print(f"📊 Total Data Rows Mapped:    {total_rows_all}")
    print(f"🪙 Gemini API Quota Consumed: 0 TOKENS (100% Local Execution)")
    print("=" * 80)

    # Generate 00_XLSX_INVENTORY.md
    inv_md = root / "00_XLSX_INVENTORY.md"
    with open(inv_md, 'w', encoding='utf-8') as inv_f:
        inv_f.write(f"# Master Excel Inventory: `{root.name}`\n\n")
        inv_f.write(f"- **Generated:** Local Batch Excel Inspector Engine\n")
        inv_f.write(f"- **Total Workbooks:** {len(excel_files)}\n")
        inv_f.write(f"- **Total Sheets:** {total_sheets}\n")
        inv_f.write(f"- **Total Rows Mapped:** {total_rows_all}\n")
        inv_f.write(f"- **Gemini API Token Consumption:** 0 Tokens (100% Local Execution)\n\n")
        inv_f.write("| # | Spreadsheet File | Subfolder | Size | Sheets | Total Rows | Primary Sheets | Digest Link |\n")
        inv_f.write("|:---:|---|---|:---:|:---:|:---:|---|---|\n")
        for r in summary_rows:
            stem = Path(r['name']).stem
            inv_f.write(f"| {r['num']} | `{r['name']}` | `{r['parent']}` | {r['size_kb']} | {r['sheets']} | {r['rows']} | {r['sheet_names']} | [[{stem}_digest.md]] |\n")
    print(f"Inventory saved: {inv_md}")


def main():
    parser = argparse.ArgumentParser(description="Zero-dependency High-Performance Excel Query Engine for Second Brain.")
    parser.add_argument("--dir", "-d", help="Directory path to run batch inspection on all .xlsx files")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan subdirectories recursively")
    parser.add_argument("--file", "-f", help="Path to .xlsx file")
    parser.add_argument("--sheet", "-s", help="Sheet name (exact or partial)")
    parser.add_argument("--digest", action="store_true", help="Generate companion Markdown digest")
    parser.add_argument("--digest-out", help="Path to save digest (default: <file>_digest.md)")
    parser.add_argument("--filter", action="append", help="Filter criteria: Col=Val or Col~Substring (can specify multiple)")
    parser.add_argument("--columns", "-c", help="Comma-separated column names to project")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max rows to return (default 20, 0 for all)")
    parser.add_argument("--offset", type=int, default=0, help="Row offset for pagination")
    parser.add_argument("--format", choices=['markdown', 'json', 'csv'], default='markdown', help="Output format")
    parser.add_argument("--sheets", action="store_true", help="List all sheets in the workbook")
    parser.add_argument("--preview", "-p", type=int, help="Quick preview of first N rows")
    parser.add_argument("--extract-images", "-x", action="store_true", help="Extract embedded screenshots/diagrams from workbook")
    parser.add_argument("--image-output", help="Custom folder for extracted images (default: <file>_assets/)")

    args = parser.parse_args()

    if args.dir:
        process_batch(args.dir, recursive=args.recursive)
        return

    if not args.file:
        parser.print_help()
        return

    if args.extract_images:
        import importlib.util
        extractor_path = Path(__file__).parent / "extract_excel_images.py"
        spec = importlib.util.spec_from_file_location("extract_excel_images", extractor_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        res = mod.extract_images_from_xlsx(args.file, output_dir=args.image_output)
        print(f"Extracted {len(res)} images from {Path(args.file).name}")
        return

    if args.sheets:
        wb = ExcelWorkbook(args.file)
        print(f"Sheets in {Path(args.file).name}:")
        for i, s in enumerate(wb.sheets, 1):
            print(f"  {i}. {s['name']}")
        wb.close()
        return

    if args.digest:
        out_path = args.digest_out
        if not out_path:
            p = Path(args.file)
            out_path = p.parent / f"{p.stem}_digest.md"
        generate_digest(args.file, str(out_path))
        return

    if args.preview:
        query_data(args.file, sheet_name=args.sheet, limit=args.preview, out_format=args.format)
        return

    # Default query
    query_data(
        excel_path=args.file,
        sheet_name=args.sheet,
        filters=args.filter,
        columns=args.columns,
        limit=args.limit,
        offset=args.offset,
        out_format=args.format
    )

if __name__ == "__main__":
    main()
